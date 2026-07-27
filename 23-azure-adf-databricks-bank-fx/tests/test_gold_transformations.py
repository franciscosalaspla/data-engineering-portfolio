"""Focused unit tests for Gold FX conversion, dimensions and quarantine."""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "tests"))
for java_home in (
    Path("/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
    Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
):
    if java_home.exists() and not os.environ.get("JAVA_HOME"):
        os.environ["JAVA_HOME"] = str(java_home)
os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")

from pyspark.sql import functions as F  # noqa: E402
from pyspark.sql.types import DecimalType, LongType  # noqa: E402

from bankfx_gold.transformations import build_dimensions, build_fact_transactions  # noqa: E402
from bankfx_silver.spark import build_spark_session  # noqa: E402
from gold_test_data import silver_frames  # noqa: E402


class GoldTransformationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spark = build_spark_session("project23-gold-unit-tests")
        cls.spark.sparkContext.setLogLevel("ERROR")
        cls.frames = silver_frames(cls.spark)
        cls.processed_at = datetime(2026, 7, 23, tzinfo=timezone.utc)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.spark.stop()

    def test_known_fx_values_use_division_by_units_per_eur(self) -> None:
        fact, rejected, quarantine = build_fact_transactions(
            **self.frames, run_id="gold-unit", processed_at=self.processed_at
        )
        actual = {
            row["transaction_id"]: (row["fx_rate_to_eur"], row["amount_eur"])
            for row in fact.select("transaction_id", "fx_rate_to_eur", "amount_eur").collect()
        }
        self.assertEqual((Decimal("1.00000000"), Decimal("100.00")), actual["TXN-0001"])
        self.assertEqual((Decimal("1.15000000"), Decimal("217.39")), actual["TXN-0002"])
        self.assertEqual((Decimal("0.87000000"), Decimal("86.78")), actual["TXN-0003"])
        self.assertEqual(0, rejected.count())
        self.assertEqual(0, quarantine.count())

    def test_money_and_rates_remain_decimal(self) -> None:
        fact, _rejected, _quarantine = build_fact_transactions(
            **self.frames, run_id="gold-types", processed_at=self.processed_at
        )
        self.assertEqual(DecimalType(18, 2), fact.schema["amount_original"].dataType)
        self.assertEqual(DecimalType(18, 8), fact.schema["fx_rate_to_eur"].dataType)
        self.assertEqual(DecimalType(18, 2), fact.schema["amount_eur"].dataType)

    def test_missing_fx_is_quarantined_with_explanation(self) -> None:
        missing_date = self.frames["transactions"].limit(1).withColumn(
            "transaction_timestamp", F.to_timestamp(F.lit("2026-07-22 09:00:00"))
        )
        fact, rejected, quarantine = build_fact_transactions(
            missing_date,
            self.frames["accounts"],
            self.frames["customers"],
            self.frames["fx_rates"],
            "gold-missing-fx",
            self.processed_at,
        )
        self.assertEqual(0, fact.count())
        self.assertEqual(1, rejected.count())
        self.assertEqual("FX_RATE_MISSING", quarantine.select("rule_name").first()[0])
        self.assertIn("No positive FX rate", quarantine.select("rejection_reason").first()[0])

    def test_six_dimensions_have_stable_long_keys(self) -> None:
        first = build_dimensions(
            self.frames["customers"], self.frames["accounts"], self.frames["transactions"],
            "gold-first", self.processed_at,
        )
        second = build_dimensions(
            self.frames["customers"], self.frames["accounts"], self.frames["transactions"],
            "gold-second", datetime(2026, 7, 24, tzinfo=timezone.utc),
        )
        expected = {"dim_date": 2, "dim_customer": 5, "dim_account": 7, "dim_merchant": 7, "dim_channel": 4, "dim_currency": 3}
        key_names = {"dim_date": "date_key", "dim_customer": "customer_key", "dim_account": "account_key", "dim_merchant": "merchant_key", "dim_channel": "channel_key", "dim_currency": "currency_key"}
        self.assertEqual(expected, {name: frame.count() for name, frame in first.items()})
        for name, key in key_names.items():
            self.assertIsInstance(first[name].schema[key].dataType, LongType)
            first_keys = sorted(row[0] for row in first[name].select(key).collect())
            second_keys = sorted(row[0] for row in second[name].select(key).collect())
            self.assertEqual(first_keys, second_keys)


if __name__ == "__main__":
    unittest.main()
