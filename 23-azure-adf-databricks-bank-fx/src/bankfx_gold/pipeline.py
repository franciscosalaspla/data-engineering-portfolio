"""Orchestrate Silver-to-Gold dimensions, fact, quality, audit and serving snapshot."""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from pyspark import StorageLevel
from pyspark.sql import DataFrame, SparkSession

from bankfx_silver.storage import DeltaTableStore

from .audit import GoldAuditStore, GoldRunSummary, GoldTableAudit
from .config import GoldConfig, load_gold_config
from .reconciliation import reconcile_gold
from .transformations import build_dimensions, build_fact_transactions


LOGGER = logging.getLogger("bankfx_gold")


class GoldPipeline:
    """Build a Type 1 star schema and a denormalized analytical snapshot."""

    def __init__(
        self,
        spark: SparkSession,
        project_root: Path,
        config_path: Path | None = None,
        config: GoldConfig | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.spark = spark
        self.project_root = project_root.resolve()
        self.config = config or load_gold_config(
            config_path or self.project_root / "config" / "gold_pipeline.json"
        )
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.silver_root = self.config.resolved_path(self.project_root, self.config.silver_root)
        self.gold_root = self.config.resolved_path(self.project_root, self.config.gold_root)
        self.quarantine_path = self.config.resolved_path(
            self.project_root, self.config.quarantine_path
        )
        self.serving_root = self.config.resolved_path(self.project_root, self.config.serving_root)
        audit_root = self.config.resolved_path(self.project_root, self.config.audit_root)
        self.audit_store = GoldAuditStore(audit_root)
        self.delta_store = DeltaTableStore(self.spark)

    def run(self, run_id: str | None = None) -> GoldRunSummary:
        run_id = run_id or str(uuid.uuid4())
        _validate_run_id(run_id)
        started = self.now()
        timer = time.monotonic_ns()
        summary = GoldRunSummary(
            run_id=run_id,
            environment=self.config.environment,
            started_at=_iso_utc(started),
        )
        cached: list[DataFrame] = []
        LOGGER.info("gold_run_started run_id=%s environment=%s", run_id, self.config.environment)
        try:
            silver = self._read_silver()
            dimensions = build_dimensions(
                silver["customers"], silver["accounts"], silver["transactions"], run_id, started
            )
            dimensions = {
                name: frame.persist(StorageLevel.MEMORY_AND_DISK)
                for name, frame in dimensions.items()
            }
            cached.extend(dimensions.values())
            fact, rejected, quarantine = build_fact_transactions(
                silver["transactions"],
                silver["accounts"],
                silver["customers"],
                silver["fx_rates"],
                run_id,
                started,
            )
            fact = fact.persist(StorageLevel.MEMORY_AND_DISK)
            rejected = rejected.persist(StorageLevel.MEMORY_AND_DISK)
            quarantine = quarantine.persist(StorageLevel.MEMORY_AND_DISK)
            cached.extend([fact, rejected, quarantine])

            frames = {**dimensions, "fact_transactions": fact}
            rejected_count = rejected.select("transaction_id").distinct().count()
            for table_config in self.config.tables:
                frame = frames[table_config.table_name]
                path = f"{self.gold_root}/{table_config.table_name}"
                metrics = self.delta_store.merge(
                    frame,
                    path,
                    table_config.business_key,
                    checksum_column="_gold_record_checksum",
                )
                incoming_count = metrics.inserted + metrics.updated + metrics.skipped
                audit = GoldTableAudit(
                    run_id=run_id,
                    table_name=table_config.table_name,
                    gold_path=path,
                    source_row_count=(
                        incoming_count + rejected_count
                        if table_config.table_name == "fact_transactions"
                        else incoming_count
                    ),
                    valid_row_count=incoming_count,
                    rejected_row_count=(
                        rejected_count if table_config.table_name == "fact_transactions" else 0
                    ),
                    inserted_row_count=metrics.inserted,
                    updated_row_count=metrics.updated,
                    skipped_row_count=metrics.skipped,
                    status=(
                        "PARTIAL"
                        if table_config.table_name == "fact_transactions" and rejected_count
                        else "SKIPPED"
                        if metrics.inserted == 0 and metrics.updated == 0
                        else "SUCCESS"
                    ),
                    delta_version=metrics.delta_version,
                    delta_operation=metrics.delta_operation,
                    delta_operation_metrics=metrics.delta_operation_metrics,
                    delta_timestamp=metrics.delta_timestamp,
                )
                self.audit_store.append(audit)
                summary.tables.append(audit.to_dict())

            summary.quarantine_rule_count = quarantine.count()
            inserted, skipped = self.delta_store.merge_quarantine(
                quarantine, self.quarantine_path
            )
            summary.quarantine_inserted_count = inserted
            summary.quarantine_skipped_count = skipped

            persisted_dimensions = {
                name: self.delta_store.read(f"{self.gold_root}/{name}")
                for name in dimensions
            }
            persisted_fact = self.delta_store.read(f"{self.gold_root}/fact_transactions")
            summary.reconciliation = reconcile_gold(
                silver["transactions"], rejected, persisted_fact, persisted_dimensions
            )

            changed = any(
                table["inserted_row_count"] or table["updated_row_count"]
                for table in summary.tables
            )
            snapshot = self._build_snapshot(persisted_fact, persisted_dimensions)
            summary.snapshot_row_count = snapshot.count()
            snapshot_path = f"{self.serving_root}/transactions_analytics"
            if changed or not self._parquet_exists(snapshot_path):
                snapshot.write.mode("overwrite").parquet(snapshot_path)
                summary.snapshot_status = "WRITTEN"
            else:
                summary.snapshot_status = "SKIPPED"

            if summary.reconciliation["status"] == "FAILED":
                summary.status = "FAILED"
            elif rejected_count:
                summary.status = "PARTIAL"
            elif all(table["status"] == "SKIPPED" for table in summary.tables):
                summary.status = "SKIPPED"
            else:
                summary.status = "SUCCESS"
        except Exception:
            summary.status = "FAILED"
            LOGGER.exception("gold_run_failed run_id=%s", run_id)
            raise
        finally:
            for frame in cached:
                frame.unpersist(blocking=False)
            finished = self.now()
            summary.finished_at = _iso_utc(finished)
            summary.duration_ms = max(0, (time.monotonic_ns() - timer) // 1_000_000)
            self.audit_store.write_summary(summary)
        LOGGER.info("gold_run_finished run_id=%s status=%s", run_id, summary.status)
        return summary

    def _read_silver(self) -> dict[str, DataFrame]:
        names = {
            "customers": "silver_customers",
            "accounts": "silver_accounts",
            "fx_rates": "silver_fx_rates",
            "transactions": "silver_transactions",
        }
        return {
            entity: self.delta_store.read(f"{self.silver_root}/{table}")
            for entity, table in names.items()
        }

    def _build_snapshot(
        self, fact: DataFrame, dimensions: dict[str, DataFrame]
    ) -> DataFrame:
        customer = dimensions["dim_customer"].select(
            "customer_key", "country_code", "segment", "risk_rating"
        )
        account = dimensions["dim_account"].select(
            "account_key", "account_type", "base_currency"
        )
        merchant = dimensions["dim_merchant"].select(
            "merchant_key", "merchant_name", "merchant_category"
        )
        date = dimensions["dim_date"].select(
            "date_key", "calendar_year", "calendar_quarter", "calendar_month", "day_of_month"
        )
        return (
            fact.join(customer, "customer_key")
            .join(account, "account_key")
            .join(merchant, "merchant_key")
            .join(date, "date_key")
            .select(
                "transaction_id", "transaction_timestamp", "transaction_date",
                "customer_id", "country_code", "segment", "risk_rating",
                "account_id", "account_type", "base_currency",
                "merchant_id", "merchant_name", "merchant_category",
                "channel_code", "currency_code", "transaction_type", "status",
                "source_batch_id", "amount_original", "fx_rate_to_eur", "fx_rate_date",
                "amount_eur", "calendar_year", "calendar_quarter", "calendar_month", "day_of_month",
                "_source_silver_run_id", "_gold_run_id",
            )
        )

    def _parquet_exists(self, path: str) -> bool:
        try:
            self.spark.read.parquet(path)
        except Exception:  # noqa: BLE001 - filesystem schemes differ locally and in Databricks
            return False
        return True


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_run_id(run_id: str) -> None:
    if not run_id or any(
        character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        for character in run_id
    ):
        raise ValueError("run_id contains unsupported path characters")
