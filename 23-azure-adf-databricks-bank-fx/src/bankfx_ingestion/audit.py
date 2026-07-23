"""Structured audit and idempotency state stores."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AuditRecord, RunSummary


class AuditStore:
    def __init__(self, output_root: Path) -> None:
        self.audit_dir = output_root / "audit"
        self.audit_file = self.audit_dir / "ingestion_audit.jsonl"

    def append(self, record: AuditRecord) -> None:
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        with self.audit_file.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    def write_summary(self, summary: RunSummary) -> Path:
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        path = self.audit_dir / f"run_summary_{summary.run_id}.json"
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(summary.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        return path


class ProcessedFileStore:
    def __init__(self, output_root: Path) -> None:
        self.path = output_root / "control" / "processed_files.json"
        self.entries: dict[str, dict[str, Any]] = self._load()

    @staticmethod
    def key(source_name: str, entity_name: str, checksum: str) -> str:
        return f"{source_name}|{entity_name}|{checksum}"

    def get(self, source_name: str, entity_name: str, checksum: str) -> dict[str, Any] | None:
        return self.entries.get(self.key(source_name, entity_name, checksum))

    def add(
        self,
        source_name: str,
        entity_name: str,
        checksum: str,
        entry: dict[str, Any],
    ) -> None:
        self.entries[self.key(source_name, entity_name, checksum)] = entry
        self._save()

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        with self.path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError("Processed file state must be a JSON object")
        return payload

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(self.entries, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        temporary.replace(self.path)
