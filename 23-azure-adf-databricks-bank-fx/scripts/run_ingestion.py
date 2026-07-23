#!/usr/bin/env python3
"""Run the complete local metadata-driven Landing/Bronze ingestion."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from bankfx_ingestion import IngestionPipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Optional deterministic run identifier")
    parser.add_argument("--ingestion-date", help="Partition date in YYYY-MM-DD format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    summary = IngestionPipeline(PROJECT_ROOT).run(
        run_id=args.run_id,
        ingestion_date=args.ingestion_date,
    )
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
    return 1 if summary.status == "FAILED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
