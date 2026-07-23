"""Metadata-driven local equivalent of the planned ADF ingestion pipeline."""

from __future__ import annotations

import csv
import json
import logging
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .audit import AuditStore, ProcessedFileStore
from .config import load_source_config
from .models import AuditRecord, RejectedRecord, RunSummary, SourceConfig
from .storage import (
    copy_to_landing,
    record_checksum,
    relative_to_project,
    sha256_file,
    write_jsonl_once,
)
from .validation import ContractValidator, validate_references


LOGGER = logging.getLogger("bankfx_ingestion")


class IngestionPipeline:
    """Ingest enabled file metadata entries into local Landing and Bronze."""

    def __init__(
        self,
        project_root: Path,
        config_path: Path | None = None,
        output_root: Path | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.project_root = project_root.resolve()
        self.config_path = config_path or self.project_root / "config" / "sources.json"
        self.output_root = output_root or self.project_root / "data" / "output"
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.sources = load_source_config(self.config_path)
        self.audit_store = AuditStore(self.output_root)
        self.processed_store = ProcessedFileStore(self.output_root)
        self.account_ids, self.customer_ids = self._load_reference_ids()

    def run(
        self,
        run_id: str | None = None,
        ingestion_date: str | None = None,
    ) -> RunSummary:
        run_id = run_id or str(uuid.uuid4())
        ingestion_date = ingestion_date or date.today().isoformat()
        _validate_partition_value(run_id, "run_id")
        _validate_ingestion_date(ingestion_date)

        started = self.now()
        summary = RunSummary(
            run_id=run_id,
            ingestion_date=ingestion_date,
            started_at=_iso_utc(started),
        )
        LOGGER.info("run_started run_id=%s ingestion_date=%s", run_id, ingestion_date)

        for source in (item for item in self.sources if item.enabled):
            audit = self._process_source(source, run_id, ingestion_date)
            self.audit_store.append(audit)
            summary.sources.append(audit.to_dict())
            LOGGER.info(
                "source_finished source_id=%s entity=%s status=%s accepted=%d rejected=%d duplicates=%d",
                source.source_id,
                source.entity_name,
                audit.status,
                audit.accepted_row_count,
                audit.rejected_row_count,
                audit.duplicate_row_count,
            )

        finished = self.now()
        summary.finished_at = _iso_utc(finished)
        summary.duration_ms = max(0, int((finished - started).total_seconds() * 1000))
        statuses = {source["status"] for source in summary.sources}
        if "FAILED" in statuses:
            summary.status = "FAILED"
        elif "PARTIAL" in statuses:
            summary.status = "PARTIAL"
        else:
            summary.status = "SUCCESS"
        self.audit_store.write_summary(summary)
        LOGGER.info("run_finished run_id=%s status=%s", run_id, summary.status)
        return summary

    def _process_source(
        self,
        source: SourceConfig,
        run_id: str,
        ingestion_date: str,
    ) -> AuditRecord:
        started = self.now()
        started_timer = time.monotonic_ns()
        audit = AuditRecord(
            run_id=run_id,
            source_name=source.source_name,
            entity_name=source.entity_name,
            source_path=source.source_path,
            started_at=_iso_utc(started),
        )
        try:
            source_path = source.resolved_source(self.project_root)
            schema_path = source.resolved_schema(self.project_root)
            checksum = sha256_file(source_path)
            audit.checksum = checksum
            processed = self.processed_store.get(source.source_name, source.entity_name, checksum)
            if processed:
                audit.landing_path = processed.get("landing_path", "")
                audit.bronze_path = processed.get("bronze_path", "")
                audit.quarantine_path = processed.get("quarantine_path", "")
                audit.source_row_count = processed["source_row_count"]
                audit.duplicate_row_count = processed["source_row_count"]
                audit.status = "SKIPPED"
                return self._finish_audit(audit, started_timer)

            ingested_at = _iso_utc(self.now())
            landing_path, _metadata_path = copy_to_landing(
                source_path=source_path,
                output_root=self.output_root,
                source_name=source.source_name,
                entity_name=source.entity_name,
                ingestion_date=ingestion_date,
                run_id=run_id,
                checksum=checksum,
                ingested_at=ingested_at,
            )
            audit.landing_path = relative_to_project(landing_path, self.project_root)

            records, rejected = self._read_and_validate(source, source_path, schema_path)
            audit.source_row_count = len(records) + len(rejected)
            accepted = self._to_bronze_records(
                records,
                source,
                run_id,
                ingestion_date,
                ingested_at,
                audit.landing_path,
            )
            audit.accepted_row_count = len(accepted)
            audit.rejected_row_count = len(rejected)

            checksum_partition = f"source_checksum={checksum[:16]}"
            if accepted:
                bronze_path = (
                    self.output_root
                    / "bronze"
                    / source.destination_path
                    / f"ingestion_date={ingestion_date}"
                    / checksum_partition
                    / "records.jsonl"
                )
                write_jsonl_once(bronze_path, accepted)
                audit.bronze_path = relative_to_project(bronze_path, self.project_root)

            if rejected:
                quarantine_path = (
                    self.output_root
                    / "quarantine"
                    / source.source_name
                    / source.entity_name
                    / f"ingestion_date={ingestion_date}"
                    / f"run_id={run_id}"
                    / f"{source_path.stem}.rejected.jsonl"
                )
                quarantine_records = [
                    {
                        "_run_id": run_id,
                        "_source_name": source.source_name,
                        "_source_file": source_path.name,
                        "_error_type": "DATA_QUALITY",
                        "_rejection_reasons": item.reasons,
                        "original_record": item.record,
                    }
                    for item in rejected
                ]
                write_jsonl_once(quarantine_path, quarantine_records)
                audit.quarantine_path = relative_to_project(quarantine_path, self.project_root)

            audit.status = "PARTIAL" if rejected else "SUCCESS"
            self.processed_store.add(
                source.source_name,
                source.entity_name,
                checksum,
                {
                    "processed_run_id": run_id,
                    "source_row_count": audit.source_row_count,
                    "accepted_row_count": audit.accepted_row_count,
                    "rejected_row_count": audit.rejected_row_count,
                    "landing_path": audit.landing_path,
                    "bronze_path": audit.bronze_path,
                    "quarantine_path": audit.quarantine_path,
                },
            )
        except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
            audit.status = "FAILED"
            audit.error_type = "TECHNICAL"
            audit.error_message = f"{type(exc).__name__}: {exc}"
            LOGGER.error(
                "source_failed source_id=%s error=%s",
                source.source_id,
                audit.error_message,
            )
        return self._finish_audit(audit, started_timer)

    def _read_and_validate(
        self,
        source: SourceConfig,
        source_path: Path,
        schema_path: Path,
    ) -> tuple[list[dict[str, Any]], list[RejectedRecord]]:
        with schema_path.open(encoding="utf-8") as handle:
            schema = json.load(handle)
        validator = ContractValidator(schema)

        if source.file_format == "csv":
            with source_path.open(encoding="utf-8", newline="") as handle:
                raw_records = list(csv.DictReader(handle))
            return self._partition_records(source, raw_records, validator)

        with source_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        document_errors = validator.validate(payload)
        if document_errors:
            return [], [RejectedRecord(record=payload, reasons=document_errors)]
        if not source.record_collection:
            raw_records = [payload]
        else:
            collection = payload.get(source.record_collection)
            if not isinstance(collection, list):
                raise ValueError(f"record_collection is not an array: {source.record_collection}")
            raw_records = collection
        if source.entity_name == "fx_rates":
            raw_records = [{"base": payload["base"], **record} for record in raw_records]

        accepted: list[dict[str, Any]] = []
        rejected: list[RejectedRecord] = []
        for record in raw_records:
            reference_errors = validate_references(
                source.entity_name,
                record,
                self.account_ids,
                self.customer_ids,
            )
            if reference_errors:
                rejected.append(RejectedRecord(record=record, reasons=reference_errors))
            else:
                accepted.append(record)
        return accepted, rejected

    def _partition_records(
        self,
        source: SourceConfig,
        records: list[dict[str, Any]],
        validator: ContractValidator,
    ) -> tuple[list[dict[str, Any]], list[RejectedRecord]]:
        accepted: list[dict[str, Any]] = []
        rejected: list[RejectedRecord] = []
        for record in records:
            errors = validator.validate(record)
            errors.extend(
                validate_references(
                    source.entity_name,
                    record,
                    self.account_ids,
                    self.customer_ids,
                )
            )
            if errors:
                rejected.append(RejectedRecord(record=record, reasons=errors))
            else:
                accepted.append(record)
        return accepted, rejected

    def _to_bronze_records(
        self,
        records: list[dict[str, Any]],
        source: SourceConfig,
        run_id: str,
        ingestion_date: str,
        ingested_at: str,
        landing_path: str,
    ) -> list[dict[str, Any]]:
        bronze_records: list[dict[str, Any]] = []
        for record in records:
            bronze_records.append(
                {
                    **record,
                    "_run_id": run_id,
                    "_ingested_at": ingested_at,
                    "_source_name": source.source_name,
                    "_source_file": Path(source.source_path).name,
                    "_record_checksum": record_checksum(record),
                    "_ingestion_date": ingestion_date,
                    "_landing_path": landing_path,
                }
            )
        return sorted(bronze_records, key=lambda row: tuple(str(row[key]) for key in source.business_key))

    def _load_reference_ids(self) -> tuple[set[str], set[str]]:
        account_ids: set[str] = set()
        customer_ids: set[str] = set()
        for source in self.sources:
            if source.entity_name not in {"accounts", "customers"}:
                continue
            with source.resolved_source(self.project_root).open(encoding="utf-8") as handle:
                payload = json.load(handle)
            collection = payload.get(source.record_collection or source.entity_name, [])
            if source.entity_name == "accounts":
                account_ids.update(item["account_id"] for item in collection)
            else:
                customer_ids.update(item["customer_id"] for item in collection)
        return account_ids, customer_ids

    def _finish_audit(self, audit: AuditRecord, started_timer: int) -> AuditRecord:
        audit.finished_at = _iso_utc(self.now())
        audit.duration_ms = max(0, (time.monotonic_ns() - started_timer) // 1_000_000)
        return audit


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_partition_value(value: str, field_name: str) -> None:
    if not value or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for character in value):
        raise ValueError(f"{field_name} contains unsupported path characters")


def _validate_ingestion_date(value: str) -> None:
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("ingestion_date must use YYYY-MM-DD")
