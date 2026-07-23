#!/usr/bin/env python3
"""Print a compact view of the local ingestion audit log."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = PROJECT_ROOT / "data" / "output" / "audit" / "ingestion_audit.jsonl"


def main() -> int:
    if not AUDIT_PATH.exists():
        print("No audit records found. Run scripts/run_ingestion.py first.")
        return 0

    print("run_id | source | entity | status | source/accepted/rejected/duplicates")
    with AUDIT_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            counts = "/".join(
                str(row[field])
                for field in (
                    "source_row_count",
                    "accepted_row_count",
                    "rejected_row_count",
                    "duplicate_row_count",
                )
            )
            print(
                f"{row['run_id']} | {row['source_name']} | {row['entity_name']} | "
                f"{row['status']} | {counts}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
