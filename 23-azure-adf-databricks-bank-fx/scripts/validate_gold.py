#!/usr/bin/env python3
"""Validate Gold star-schema counts, keys, decimals, FX and reconciliation."""

from __future__ import annotations

import json
import os
import sys
from decimal import Decimal
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


def main() -> int:
    _configure_local_java()
    from pyspark.sql import functions as F
    from pyspark.sql.types import DecimalType

    from bankfx_gold.config import load_gold_config
    from bankfx_gold.reconciliation import DIMENSION_KEYS, reconcile_gold
    from bankfx_silver.spark import build_spark_session
    from bankfx_silver.storage import DeltaTableStore

    expected_counts = {
        "dim_date": 2,
        "dim_customer": 5,
        "dim_account": 7,
        "dim_merchant": 7,
        "dim_channel": 4,
        "dim_currency": 3,
        "fact_transactions": 8,
    }
    config = load_gold_config(PROJECT_ROOT / "config" / "gold_pipeline.json")
    silver_root = config.resolved_path(PROJECT_ROOT, config.silver_root)
    gold_root = config.resolved_path(PROJECT_ROOT, config.gold_root)
    spark = build_spark_session("project23-validate-gold")
    spark.sparkContext.setLogLevel("ERROR")
    store = DeltaTableStore(spark)
    try:
        dimensions = {
            name: store.read(f"{gold_root}/{name}") for name in DIMENSION_KEYS
        }
        fact = store.read(f"{gold_root}/fact_transactions")
        silver_transactions = store.read(f"{silver_root}/silver_transactions")
        empty_rejected = silver_transactions.limit(0)
        reconciliation = reconcile_gold(
            silver_transactions, empty_rejected, fact, dimensions
        )
        table_counts = {
            **{name: frame.count() for name, frame in dimensions.items()},
            "fact_transactions": fact.count(),
        }
        checks = {
            "expected_table_counts": table_counts == expected_counts,
            "reconciliation": reconciliation["status"] == "PASSED",
            "amount_original_decimal": fact.schema["amount_original"].dataType == DecimalType(18, 2),
            "amount_eur_decimal": fact.schema["amount_eur"].dataType == DecimalType(18, 2),
            "fx_rate_decimal": fact.schema["fx_rate_to_eur"].dataType == DecimalType(18, 8),
            "known_fx_values": fact.filter(
                ((F.col("currency_code") == "EUR") & (F.col("fx_rate_to_eur") != Decimal("1.00000000")))
                | F.col("fx_rate_to_eur").isNull()
                | (F.col("fx_rate_to_eur") <= 0)
            ).count() == 0,
            "eur_sum": reconciliation["fact_eur_amount_sum"] == "1202.05",
        }
        status = "PASSED" if all(checks.values()) else "FAILED"
        print(json.dumps({"status": status, "checks": checks, "table_counts": table_counts, "reconciliation": reconciliation}, indent=2, sort_keys=True))
        return 0 if status == "PASSED" else 1
    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main())
