#!/usr/bin/env python3
"""Print compact Gold audit and reconciliation evidence."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = PROJECT_ROOT / "data" / "output" / "audit"


def main() -> int:
    summaries = sorted(AUDIT_ROOT.glob("gold_run_summary_*.json"))
    if not summaries:
        print("No Gold run summaries found.")
        return 1
    for path in summaries:
        summary = json.loads(path.read_text(encoding="utf-8"))
        totals = {
            name: sum(table[f"{name}_row_count"] for table in summary["tables"])
            for name in ("inserted", "updated", "skipped")
        }
        print(
            json.dumps(
                {
                    "run_id": summary["run_id"],
                    "status": summary["status"],
                    "table_count": len(summary["tables"]),
                    **totals,
                    "quarantine_rule_count": summary["quarantine_rule_count"],
                    "snapshot_status": summary["snapshot_status"],
                    "reconciliation": summary["reconciliation"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
