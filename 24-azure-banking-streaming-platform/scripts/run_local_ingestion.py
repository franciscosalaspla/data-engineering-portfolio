"""Run the Hito 4 producer and consumer without Azure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from banking_streaming.event_ingestion import run_local_ingestion  # noqa: E402


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="Local JSONL fixture to process")
    args = parser.parse_args()

    report = run_local_ingestion(_load_jsonl(args.fixture))
    summary = {
        "accepted": report.consumer.accepted,
        "attempted": report.producer.attempted,
        "consumer_rejected": len(report.consumer.rejected_event_ids),
        "producer_rejected": len(report.producer.rejected),
        "published": report.producer.published,
        "received": report.consumer.received,
        "reconciled": report.reconciled,
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if report.reconciled else 1


if __name__ == "__main__":
    raise SystemExit(main())
