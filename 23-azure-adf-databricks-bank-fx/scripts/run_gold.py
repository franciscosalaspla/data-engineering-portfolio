#!/usr/bin/env python3
"""Run the local PySpark Silver-to-Gold dimensional pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _configure_local_java() -> None:
    if not os.environ.get("JAVA_HOME"):
        for candidate in (
            Path("/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
            Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
        ):
            if candidate.exists():
                os.environ["JAVA_HOME"] = str(candidate)
                break
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Optional deterministic run identifier")
    parser.add_argument("--environment", help="Override environment")
    parser.add_argument("--silver-root", help="Override Silver root path")
    parser.add_argument("--gold-root", help="Override Gold root path")
    parser.add_argument("--quarantine-path", help="Override Gold quarantine path")
    parser.add_argument("--audit-root", help="Override audit output path")
    parser.add_argument("--serving-root", help="Override serving output path")
    parser.add_argument("--catalog", help="Optional Databricks catalog")
    parser.add_argument("--schema", help="Optional Databricks schema")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _configure_local_java()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    from bankfx_gold import GoldPipeline
    from bankfx_gold.config import load_gold_config
    from bankfx_silver.spark import build_spark_session

    config = load_gold_config(PROJECT_ROOT / "config" / "gold_pipeline.json").with_overrides(
        environment=args.environment,
        silver_root=args.silver_root,
        gold_root=args.gold_root,
        quarantine_path=args.quarantine_path,
        audit_root=args.audit_root,
        serving_root=args.serving_root,
        catalog=args.catalog,
        schema=args.schema,
    )
    spark = build_spark_session("project23-silver-to-gold")
    try:
        summary = GoldPipeline(spark, PROJECT_ROOT, config=config).run(args.run_id)
        print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
        return 1 if summary.status == "FAILED" else 0
    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main())
