"""Structured Silver audit records and run summaries."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SilverAuditRecord:
    run_id: str
    entity_name: str
    bronze_path: str
    silver_path: str
    source_row_count: int = 0
    valid_row_count: int = 0
    rejected_row_count: int = 0
    duplicate_row_count: int = 0
    inserted_row_count: int = 0
    updated_row_count: int = 0
    skipped_row_count: int = 0
    quarantine_rule_count: int = 0
    started_at: str = ""
    finished_at: str = ""
    duration_ms: int = 0
    status: str = "FAILED"
    error_message: str = ""
    delta_version: int | None = None
    delta_operation: str = ""
    delta_operation_metrics: dict[str, str] = field(default_factory=dict)
    delta_timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SilverRunSummary:
    run_id: str
    environment: str
    started_at: str
    finished_at: str = ""
    duration_ms: int = 0
    status: str = "FAILED"
    entities: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SilverAuditStore:
    def __init__(self, audit_root: str) -> None:
        if "://" in audit_root or audit_root.startswith("dbfs:/"):
            raise ValueError("audit_root must be a local or /Volumes filesystem path")
        self.root = Path(audit_root)
        self.audit_path = self.root / "silver_audit.jsonl"

    def append(self, audit: SilverAuditRecord) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(audit.to_dict(), ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    def write_summary(self, summary: SilverRunSummary) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / f"silver_run_summary_{summary.run_id}.json"
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(summary.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        return path
