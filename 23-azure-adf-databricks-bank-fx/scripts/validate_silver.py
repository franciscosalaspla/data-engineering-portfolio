#!/usr/bin/env python3
"""Read back Silver Delta tables and validate fixture-scale quality expectations."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _configure_local_java() -> None:
    if os.environ.get("JAVA_HOME"):
        return
    for candidate in (
        Path("/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
        Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
    ):
        if candidate.exists():
            os.environ["JAVA_HOME"] = str(candidate)
            break
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")


def main() -> int:
    _configure_local_java()
    from pyspark.sql import functions as F

    from bankfx_silver.config import load_silver_config
    from bankfx_silver.spark import build_spark_session
    from bankfx_silver.storage import DeltaTableStore

    manifest = json.loads(
        (PROJECT_ROOT / "manifest" / "expected_results.json").read_text(encoding="utf-8")
    )
    expected_counts = {
        "silver_customers": manifest["expected_counts"]["customers"],
        "silver_accounts": manifest["expected_counts"]["accounts"],
        "silver_fx_rates": len(manifest["required_coverage"]["logical_dates"]),
        "silver_transactions": manifest["expected_counts"][
            "valid_transactions_total_excluding_replay"
        ],
    }
    business_keys = {
        "silver_customers": "customer_id",
        "silver_accounts": "account_id",
        "silver_fx_rates": "effective_date",
        "silver_transactions": "transaction_id",
    }
    config = load_silver_config(PROJECT_ROOT / "config" / "silver_pipeline.json")
    silver_root = config.resolved_path(PROJECT_ROOT, config.silver_root)
    spark = build_spark_session("project23-validate-silver")
    spark.sparkContext.setLogLevel("ERROR")
    store = DeltaTableStore(spark)
    results: list[dict[str, object]] = []
    try:
        for table_name, expected_count in expected_counts.items():
            path = f"{silver_root}/{table_name}"
            frame = store.read(path)
            key = business_keys[table_name]
            actual_count = frame.count()
            null_keys = frame.filter(F.col(key).isNull()).count()
            duplicate_keys = frame.groupBy(key).count().filter("count > 1").count()
            failed_quality = frame.filter(F.col("_quality_status") != "PASSED").count()
            history = store.history(path)
            results.append(
                {
                    "table_name": table_name,
                    "expected_count": expected_count,
                    "actual_count": actual_count,
                    "null_key_count": null_keys,
                    "duplicate_key_count": duplicate_keys,
                    "failed_quality_count": failed_quality,
                    "delta_version": history["delta_version"],
                    "delta_operation": history["delta_operation"],
                    "status": (
                        "PASSED"
                        if actual_count == expected_count
                        and null_keys == 0
                        and duplicate_keys == 0
                        and failed_quality == 0
                        else "FAILED"
                    ),
                }
            )
    finally:
        spark.stop()

    status = "PASSED" if all(item["status"] == "PASSED" for item in results) else "FAILED"
    print(json.dumps({"status": status, "tables": results}, indent=2, sort_keys=True))
    return 0 if status == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
