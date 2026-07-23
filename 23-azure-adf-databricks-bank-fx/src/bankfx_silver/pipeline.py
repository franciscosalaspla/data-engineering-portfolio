"""Orchestrate explicit-schema Bronze reads and idempotent Delta Silver MERGEs."""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from pyspark import StorageLevel
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from .audit import SilverAuditRecord, SilverAuditStore, SilverRunSummary
from .config import EntityConfig, SilverConfig, load_silver_config
from .reader import read_bronze
from .storage import DeltaTableStore
from .transformations import deduplicate_input, normalize_entity, split_quality


LOGGER = logging.getLogger("bankfx_silver")


class SilverPipeline:
    """Process customers, accounts, FX rates and transactions in dependency order."""

    def __init__(
        self,
        spark: SparkSession,
        project_root: Path,
        config_path: Path | None = None,
        config: SilverConfig | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.spark = spark
        self.project_root = project_root.resolve()
        self.config = config or load_silver_config(
            config_path or self.project_root / "config" / "silver_pipeline.json"
        )
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.bronze_root = self.config.resolved_path(self.project_root, self.config.bronze_root)
        self.silver_root = self.config.resolved_path(self.project_root, self.config.silver_root)
        self.quarantine_path = self.config.resolved_path(
            self.project_root, self.config.quarantine_path
        )
        audit_root = self.config.resolved_path(self.project_root, self.config.audit_root)
        self.audit_store = SilverAuditStore(audit_root)
        self.delta_store = DeltaTableStore(self.spark)

    def run(self, run_id: str | None = None) -> SilverRunSummary:
        run_id = run_id or str(uuid.uuid4())
        _validate_run_id(run_id)
        started = self.now()
        processed_at = started
        summary = SilverRunSummary(
            run_id=run_id,
            environment=self.config.environment,
            started_at=_iso_utc(started),
        )
        references: dict[str, DataFrame] = {}
        LOGGER.info("silver_run_started run_id=%s environment=%s", run_id, self.config.environment)

        for entity in self.config.entities:
            reference = None
            if entity.entity_name == "accounts":
                reference = references.get("customers")
            elif entity.entity_name == "transactions":
                reference = references.get("accounts")

            audit = self._process_entity(entity, run_id, processed_at, reference)
            self.audit_store.append(audit)
            summary.entities.append(audit.to_dict())
            if audit.status != "FAILED" and entity.entity_name in {"customers", "accounts"}:
                references[entity.entity_name] = self.delta_store.read(audit.silver_path)
            LOGGER.info(
                "silver_entity_finished entity=%s status=%s source=%d valid=%d rejected=%d "
                "inserted=%d updated=%d skipped=%d",
                entity.entity_name,
                audit.status,
                audit.source_row_count,
                audit.valid_row_count,
                audit.rejected_row_count,
                audit.inserted_row_count,
                audit.updated_row_count,
                audit.skipped_row_count,
            )

        finished = self.now()
        summary.finished_at = _iso_utc(finished)
        summary.duration_ms = max(0, int((finished - started).total_seconds() * 1000))
        statuses = [entity["status"] for entity in summary.entities]
        if "FAILED" in statuses:
            summary.status = "FAILED"
        elif "PARTIAL" in statuses:
            summary.status = "PARTIAL"
        elif statuses and all(status == "SKIPPED" for status in statuses):
            summary.status = "SKIPPED"
        else:
            summary.status = "SUCCESS"
        self.audit_store.write_summary(summary)
        LOGGER.info("silver_run_finished run_id=%s status=%s", run_id, summary.status)
        return summary

    def _process_entity(
        self,
        entity: EntityConfig,
        run_id: str,
        processed_at: datetime,
        reference_frame: DataFrame | None,
    ) -> SilverAuditRecord:
        started = self.now()
        timer = time.monotonic_ns()
        bronze_path = f"{self.bronze_root}/{entity.entity_name}"
        silver_path = f"{self.silver_root}/{entity.table_name}"
        audit = SilverAuditRecord(
            run_id=run_id,
            entity_name=entity.entity_name,
            bronze_path=bronze_path,
            silver_path=silver_path,
            started_at=_iso_utc(started),
        )
        cached_frames: list[DataFrame] = []
        try:
            bronze = read_bronze(self.spark, self.bronze_root, entity.entity_name)
            audit.source_row_count = bronze.count()
            transformed = normalize_entity(
                entity.entity_name,
                bronze,
                silver_run_id=run_id,
                processed_at=processed_at,
                reference_frame=reference_frame,
            )
            quality_frame = deduplicate_input(transformed, entity.business_key).persist(
                StorageLevel.MEMORY_AND_DISK
            )
            cached_frames.append(quality_frame)
            valid, rejected, quarantine = split_quality(
                quality_frame,
                entity.entity_name,
                entity.business_key,
            )
            valid = valid.persist(StorageLevel.MEMORY_AND_DISK)
            rejected = rejected.persist(StorageLevel.MEMORY_AND_DISK)
            quarantine = quarantine.persist(StorageLevel.MEMORY_AND_DISK)
            cached_frames.extend([valid, rejected, quarantine])

            audit.valid_row_count = valid.count()
            audit.rejected_row_count = rejected.count()
            audit.duplicate_row_count = rejected.filter(
                F.array_contains("_quality_rules", "DUPLICATE_BUSINESS_KEY")
            ).count()
            audit.quarantine_rule_count = quarantine.count()

            self.delta_store.merge_quarantine(quarantine, self.quarantine_path)
            metrics = self.delta_store.merge(valid, silver_path, entity.business_key)
            audit.inserted_row_count = metrics.inserted
            audit.updated_row_count = metrics.updated
            audit.skipped_row_count = metrics.skipped
            audit.delta_version = metrics.delta_version
            audit.delta_operation = metrics.delta_operation
            audit.delta_operation_metrics = metrics.delta_operation_metrics
            audit.delta_timestamp = metrics.delta_timestamp

            if audit.rejected_row_count:
                audit.status = "PARTIAL"
            elif audit.inserted_row_count == 0 and audit.updated_row_count == 0:
                audit.status = "SKIPPED"
            else:
                audit.status = "SUCCESS"
        except Exception as exc:  # noqa: BLE001 - entity boundary must be audited
            audit.status = "FAILED"
            audit.error_message = f"{type(exc).__name__}: {str(exc)[:1000]}"
            LOGGER.exception("silver_entity_failed entity=%s", entity.entity_name)
        finally:
            for frame in cached_frames:
                frame.unpersist(blocking=False)
        audit.finished_at = _iso_utc(self.now())
        audit.duration_ms = max(0, (time.monotonic_ns() - timer) // 1_000_000)
        return audit


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_run_id(run_id: str) -> None:
    if not run_id or any(
        character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        for character in run_id
    ):
        raise ValueError("run_id contains unsupported path characters")
