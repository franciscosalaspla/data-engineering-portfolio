"""Gold-only integration tests using small temporary Silver Delta tables."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
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

from bankfx_gold import GoldPipeline  # noqa: E402
from bankfx_gold.config import load_gold_config  # noqa: E402
from bankfx_silver.spark import build_spark_session  # noqa: E402
from bankfx_silver.storage import DeltaTableStore  # noqa: E402
from gold_test_data import silver_frames, write_silver_delta  # noqa: E402


class GoldPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary_directory = tempfile.TemporaryDirectory()
        cls.project_root = Path(cls.temporary_directory.name) / "project"
        (cls.project_root / "config").mkdir(parents=True)
        shutil.copy2(PROJECT_ROOT / "config" / "gold_pipeline.json", cls.project_root / "config")
        cls.spark = build_spark_session("project23-gold-integration-tests")
        cls.spark.sparkContext.setLogLevel("ERROR")
        frames = silver_frames(cls.spark)
        write_silver_delta(frames, str(cls.project_root / "data" / "output" / "silver"))
        cls.first_summary = GoldPipeline(cls.spark, cls.project_root).run("gold-test-001")
        cls.second_summary = GoldPipeline(cls.spark, cls.project_root).run("gold-test-002")
        cls.config = load_gold_config(cls.project_root / "config" / "gold_pipeline.json")
        cls.gold_root = cls.project_root / cls.config.gold_root
        cls.store = DeltaTableStore(cls.spark)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.spark.stop()
        cls.temporary_directory.cleanup()

    def test_first_run_builds_complete_star_schema(self) -> None:
        self.assertEqual("SUCCESS", self.first_summary.status)
        expected = {"dim_date": 2, "dim_customer": 5, "dim_account": 7, "dim_merchant": 7, "dim_channel": 4, "dim_currency": 3, "fact_transactions": 8}
        actual = {
            table: self.store.read(str(self.gold_root / table)).count()
            for table in expected
        }
        self.assertEqual(expected, actual)
        self.assertEqual(36, sum(table["inserted_row_count"] for table in self.first_summary.tables))

    def test_fact_grain_foreign_keys_and_reconciliation_pass(self) -> None:
        reconciliation = self.first_summary.reconciliation
        self.assertEqual("PASSED", reconciliation["status"])
        self.assertEqual(8, reconciliation["source_transaction_count"])
        self.assertEqual(8, reconciliation["fact_transaction_count"])
        self.assertEqual("1230.75", reconciliation["source_original_amount_sum"])
        self.assertEqual("1230.75", reconciliation["fact_original_amount_sum"])
        self.assertEqual("1202.05", reconciliation["fact_eur_amount_sum"])
        self.assertTrue(all(value == 0 for value in reconciliation["orphan_counts"].values()))
        self.assertTrue(all(value == 0 for value in reconciliation["dimension_surrogate_duplicate_counts"].values()))

    def test_second_run_is_idempotent_without_physical_merge(self) -> None:
        self.assertEqual("SKIPPED", self.second_summary.status)
        self.assertEqual(0, sum(table["inserted_row_count"] for table in self.second_summary.tables))
        self.assertEqual(0, sum(table["updated_row_count"] for table in self.second_summary.tables))
        self.assertEqual(36, sum(table["skipped_row_count"] for table in self.second_summary.tables))
        self.assertEqual("SKIPPED", self.second_summary.snapshot_status)

    def test_content_change_produces_true_delta_update(self) -> None:
        probe_path = str(self.project_root / "data" / "output" / "gold_merge_probe")
        source = self.store.read(str(self.gold_root / "fact_transactions")).limit(1)
        initial = self.store.merge(source, probe_path, ("transaction_id",), "_gold_record_checksum")
        changed = source.withColumn("amount_eur", F.lit(Decimal("999.99")).cast("decimal(18,2)")).withColumn(
            "_gold_record_checksum", F.lit("changed-checksum")
        )
        updated = self.store.merge(changed, probe_path, ("transaction_id",), "_gold_record_checksum")
        self.assertEqual(1, initial.inserted)
        self.assertEqual(1, updated.updated)
        self.assertEqual("MERGE", updated.delta_operation)
        self.assertEqual(Decimal("999.99"), self.store.read(probe_path).select("amount_eur").first()[0])

    def test_snapshot_and_audit_are_traceable(self) -> None:
        snapshot_path = self.project_root / "data" / "output" / "serving" / "transactions_analytics"
        self.assertEqual(8, self.spark.read.parquet(str(snapshot_path)).count())
        self.assertEqual("WRITTEN", self.first_summary.snapshot_status)
        audit_path = self.project_root / "data" / "output" / "audit" / "gold_audit.jsonl"
        audits = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(14, len(audits))
        self.assertEqual(7, sum(item["run_id"] == "gold-test-001" for item in audits))
        self.assertTrue((self.project_root / "data" / "output" / "audit" / "gold_run_summary_gold-test-002.json").exists())


if __name__ == "__main__":
    unittest.main()
