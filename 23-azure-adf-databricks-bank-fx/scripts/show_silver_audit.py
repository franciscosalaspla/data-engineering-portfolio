#!/usr/bin/env python3
"""Print the entity-level Silver audit in a compact format."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = PROJECT_ROOT / "data" / "output" / "audit" / "silver_audit.jsonl"


def main() -> int:
    if not AUDIT_PATH.exists():
        print("No Silver audit records found. Run scripts/run_silver.py first.")
        return 0

    print("run_id | entity | status | source/valid/rejected/duplicates | inserted/updated/skipped")
    with AUDIT_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            quality = "/".join(
                str(row[field])
                for field in (
                    "source_row_count",
                    "valid_row_count",
                    "rejected_row_count",
                    "duplicate_row_count",
                )
            )
            merge = "/".join(
                str(row[field])
                for field in (
                    "inserted_row_count",
                    "updated_row_count",
                    "skipped_row_count",
                )
            )
            print(
                f"{row['run_id']} | {row['entity_name']} | {row['status']} | "
                f"{quality} | {merge}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
