"""Typed models shared by the local ingestion components."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceConfig:
    source_id: str
    source_name: str
    entity_name: str
    source_type: str
    source_path: str
    file_format: str
    schema_path: str
    enabled: bool
    load_type: str
    destination_path: str
    business_key: tuple[str, ...]
    record_collection: str | None = None

    def resolved_source(self, project_root: Path) -> Path:
        return _safe_project_path(project_root, self.source_path)

    def resolved_schema(self, project_root: Path) -> Path:
        return _safe_project_path(project_root, self.schema_path)


@dataclass
class RejectedRecord:
    record: dict[str, Any]
    reasons: list[str]


@dataclass
class AuditRecord:
    run_id: str
    source_name: str
    entity_name: str
    source_path: str
    landing_path: str = ""
    bronze_path: str = ""
    quarantine_path: str = ""
    source_row_count: int = 0
    accepted_row_count: int = 0
    rejected_row_count: int = 0
    duplicate_row_count: int = 0
    checksum: str = ""
    started_at: str = ""
    finished_at: str = ""
    duration_ms: int = 0
    status: str = "FAILED"
    error_type: str = ""
    error_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunSummary:
    run_id: str
    ingestion_date: str
    started_at: str
    finished_at: str = ""
    duration_ms: int = 0
    status: str = "FAILED"
    sources: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_project_path(project_root: Path, relative_path: str) -> Path:
    candidate = (project_root / relative_path).resolve()
    root = project_root.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"Path escapes project root: {relative_path}")
    return candidate
