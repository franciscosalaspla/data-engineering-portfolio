"""PySpark and Delta Lake tests for the Project 23 Bronze-to-Silver pipeline."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

for java_home in (
    Path("/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
    Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
):
    if java_home.exists() and not os.environ.get("JAVA_HOME"):
        os.environ["JAVA_HOME"] = str(java_home)
os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")

from pyspark.sql import functions as F  # noqa: E402
from pyspark.sql.types import DateType, DecimalType, TimestampType  # noqa: E402

from bankfx_ingestion import IngestionPipeline  # noqa: E402
from bankfx_silver import SilverPipeline  # noqa: E402
from bankfx_silver.config import load_silver_config  # noqa: E402
from bankfx_silver.reader import read_bronze  # noqa: E402
from bankfx_silver.schemas import BRONZE_SCHEMAS, bronze_schema  # noqa: E402
from bankfx_silver.spark import build_spark_session  # noqa: E402
from bankfx_silver.storage import DeltaTableStore  # noqa: E402
from bankfx_silver.transformations import (  # noqa: E402
    deduplicate_input,
    normalize_entity,
    split_quality,
)


class SilverPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary_directory = tempfile.TemporaryDirectory()
        cls.project_root = Path(cls.temporary_directory.name) / "project"
        cls.project_root.mkdir()
        for name in ("config", "schemas"):
            shutil.copytree(PROJECT_ROOT / name, cls.project_root / name)
        shutil.copytree(PROJECT_ROOT / "data" / "fixtures", cls.project_root / "data" / "fixtures")
        (cls.project_root / "data" / "output").mkdir(parents=True)

        bronze_summary = IngestionPipeline(cls.project_root).run(
            "silver-test-bronze",
            "2026-07-22",
        )
        if bronze_summary.status != "PARTIAL":
            raise AssertionError(bronze_summary.to_dict())

        cls.spark = build_spark_session("project23-silver-tests")
        cls.spark.sparkContext.setLogLevel("ERROR")
        cls.first_summary = SilverPipeline(cls.spark, cls.project_root).run("silver-test-001")
        cls.second_summary = SilverPipeline(cls.spark, cls.project_root).run("silver-test-002")
        cls.config = load_silver_config(cls.project_root / "config" / "silver_pipeline.json")
        cls.silver_root = Path(cls.project_root / cls.config.silver_root)
        cls.delta_store = DeltaTableStore(cls.spark)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.spark.stop()
        cls.temporary_directory.cleanup()

    def test_configuration_is_parametrized_and_dependency_ordered(self) -> None:
        self.assertEqual("local", self.config.environment)
        self.assertEqual("delta", self.config.storage_format)
        self.assertEqual(
            ["customers", "accounts", "fx_rates", "transactions"],
            [entity.entity_name for entity in self.config.entities],
        )
        self.assertTrue(all(entity.business_key for entity in self.config.entities))

    def test_all_bronze_reads_use_explicit_schemas(self) -> None:
        self.assertEqual(
            {"customers", "accounts", "fx_rates", "transactions"},
            set(BRONZE_SCHEMAS),
        )
        for entity_name, schema in BRONZE_SCHEMAS.items():
            self.assertIs(schema, bronze_schema(entity_name))
            self.assertIn("_record_checksum", schema.fieldNames())
            self.assertIn("_corrupt_record", schema.fieldNames())

    def test_bronze_is_read_for_every_entity(self) -> None:
        expected = {"customers": 5, "accounts": 7, "fx_rates": 2, "transactions": 8}
        bronze_root = str(self.project_root / "data" / "output" / "bronze")

        actual = {
            entity: read_bronze(self.spark, bronze_root, entity).count()
            for entity in expected
        }
        self.assertEqual(expected, actual)

    def test_first_run_materializes_all_silver_delta_tables(self) -> None:
        self.assertEqual("SUCCESS", self.first_summary.status)
        expected = {
            "silver_customers": 5,
            "silver_accounts": 7,
            "silver_fx_rates": 2,
            "silver_transactions": 8,
        }
        actual = {
            table_name: self.delta_store.read(str(self.silver_root / table_name)).count()
            for table_name in expected
        }

        self.assertEqual(expected, actual)
        self.assertEqual(22, sum(entity["inserted_row_count"] for entity in self.first_summary.entities))

    def test_normalized_types_are_explicit(self) -> None:
        customers = self.delta_store.read(str(self.silver_root / "silver_customers"))
        accounts = self.delta_store.read(str(self.silver_root / "silver_accounts"))
        transactions = self.delta_store.read(str(self.silver_root / "silver_transactions"))
        fx_rates = self.delta_store.read(str(self.silver_root / "silver_fx_rates"))

        self.assertIsInstance(customers.schema["onboarding_date"].dataType, DateType)
        self.assertIsInstance(accounts.schema["opened_date"].dataType, DateType)
        self.assertIsInstance(transactions.schema["transaction_timestamp"].dataType, TimestampType)
        self.assertEqual(DecimalType(18, 2), transactions.schema["amount"].dataType)
        self.assertEqual("double", fx_rates.schema["rate_usd"].dataType.simpleString())
        self.assertNotIn("rates", fx_rates.columns)

    def test_silver_metadata_preserves_bronze_traceability(self) -> None:
        required = {
            "_run_id",
            "_ingested_at",
            "_source_name",
            "_source_file",
            "_record_checksum",
            "_ingestion_date",
            "_landing_path",
            "_silver_processed_at",
            "_silver_run_id",
            "_quality_status",
            "_source_bronze_path",
        }
        for table_name in (
            "silver_customers",
            "silver_accounts",
            "silver_fx_rates",
            "silver_transactions",
        ):
            frame = self.delta_store.read(str(self.silver_root / table_name))
            self.assertTrue(required.issubset(frame.columns))
            self.assertEqual(0, frame.filter(F.col("_source_bronze_path").isNull()).count())
            self.assertEqual({"PASSED"}, {row[0] for row in frame.select("_quality_status").distinct().collect()})

    def test_quality_and_referential_failures_are_quarantined(self) -> None:
        invalid = self._transaction_row()
        invalid.update(
            {
                "transaction_id": "TXN-9999",
                "account_id": "ACC-999",
                "amount": "-10.00",
                "_record_checksum": "9" * 64,
            }
        )
        frame = self.spark.createDataFrame([invalid], bronze_schema("transactions")).withColumn(
            "_source_bronze_path", F.lit("file:///test/invalid-transactions.jsonl")
        )
        accounts = self.delta_store.read(str(self.silver_root / "silver_accounts"))
        normalized = normalize_entity(
            "transactions",
            frame,
            "quality-test",
            datetime(2026, 7, 23, tzinfo=timezone.utc),
            accounts,
        )
        deduplicated = deduplicate_input(normalized, ("transaction_id",))
        valid, rejected, quarantine = split_quality(
            deduplicated,
            "transactions",
            ("transaction_id",),
        )

        self.assertEqual(0, valid.count())
        self.assertEqual(1, rejected.count())
        rules = {row[0] for row in quarantine.select("rule_name").collect()}
        self.assertEqual(
            {"TRANSACTION_AMOUNT", "TRANSACTION_ACCOUNT_REFERENCE"},
            rules,
        )
        original = json.loads(quarantine.select("original_record").first()[0])
        self.assertEqual("-10.00", original["amount"])
        self.assertEqual("ACC-999", original["account_id"])

        quarantine_path = str(self.project_root / "data" / "output" / "quality_test_quarantine")
        first_inserted, first_skipped = self.delta_store.merge_quarantine(
            quarantine,
            quarantine_path,
        )
        second_inserted, second_skipped = self.delta_store.merge_quarantine(
            quarantine,
            quarantine_path,
        )
        self.assertEqual((2, 0), (first_inserted, first_skipped))
        self.assertEqual((0, 2), (second_inserted, second_skipped))
        self.assertEqual(2, self.delta_store.read(quarantine_path).count())

    def test_duplicate_business_key_has_deterministic_winner(self) -> None:
        customer = self._customer_row()
        frame = self.spark.createDataFrame(
            [customer, customer],
            bronze_schema("customers"),
        ).withColumn("_source_bronze_path", F.lit("file:///test/duplicate-customers.jsonl"))
        normalized = normalize_entity(
            "customers",
            frame,
            "duplicate-test",
            datetime(2026, 7, 23, tzinfo=timezone.utc),
        )
        deduplicated = deduplicate_input(normalized, ("customer_id",))
        valid, rejected, _quarantine = split_quality(
            deduplicated,
            "customers",
            ("customer_id",),
        )

        self.assertEqual(1, valid.count())
        self.assertEqual(1, rejected.count())
        self.assertEqual(
            ["DUPLICATE_BUSINESS_KEY"],
            rejected.select("_quality_rules").first()[0],
        )

    def test_second_run_is_safe_and_idempotent(self) -> None:
        self.assertEqual("SKIPPED", self.second_summary.status)
        self.assertTrue(
            all(entity["status"] == "SKIPPED" for entity in self.second_summary.entities)
        )
        self.assertEqual(0, sum(entity["inserted_row_count"] for entity in self.second_summary.entities))
        self.assertEqual(0, sum(entity["updated_row_count"] for entity in self.second_summary.entities))
        self.assertEqual(22, sum(entity["skipped_row_count"] for entity in self.second_summary.entities))

    def test_delta_merge_update_and_history_execute_really(self) -> None:
        probe_path = str(self.project_root / "data" / "output" / "merge_probe")
        source = self.delta_store.read(str(self.silver_root / "silver_customers")).limit(1)
        initial = self.delta_store.merge(source, probe_path, ("customer_id",))
        changed = source.withColumn("country_code", F.lit("ZZ")).withColumn(
            "_record_checksum", F.lit("f" * 64)
        )
        updated = self.delta_store.merge(changed, probe_path, ("customer_id",))

        self.assertEqual(1, initial.inserted)
        self.assertEqual(1, updated.updated)
        self.assertEqual("MERGE", updated.delta_operation)
        self.assertEqual("1", updated.delta_operation_metrics["numTargetRowsUpdated"])
        self.assertEqual("ZZ", self.delta_store.read(probe_path).select("country_code").first()[0])

    def test_entity_audit_reconciles_every_count(self) -> None:
        audit_path = self.project_root / "data" / "output" / "audit" / "silver_audit.jsonl"
        rows = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(8, len(rows))
        for row in rows:
            self.assertEqual(
                row["source_row_count"],
                row["valid_row_count"] + row["rejected_row_count"],
            )
            self.assertIn(row["status"], {"SUCCESS", "SKIPPED"})
            self.assertIsNotNone(row["delta_version"])
            self.assertEqual("", row["error_message"])

    @staticmethod
    def _customer_row() -> dict[str, object]:
        return {
            "customer_id": "CUS-001",
            "country_code": "CL",
            "segment": "RETAIL",
            "onboarding_date": "2026-01-01",
            "status": "ACTIVE",
            "risk_rating": "LOW",
            "_run_id": "bronze-test",
            "_ingested_at": "2026-07-23T00:00:00Z",
            "_source_name": "test",
            "_source_file": "customers.json",
            "_record_checksum": "a" * 64,
            "_ingestion_date": "2026-07-22",
            "_landing_path": "data/output/landing/test/customers.json",
            "_corrupt_record": None,
        }

    @staticmethod
    def _transaction_row() -> dict[str, object]:
        return {
            "transaction_id": "TXN-0001",
            "account_id": "ACC-001",
            "transaction_timestamp": "2026-07-20T10:00:00Z",
            "amount": "10.00",
            "currency": "EUR",
            "transaction_type": "PURCHASE",
            "merchant_id": "MER-001",
            "merchant_name": "Synthetic Merchant",
            "merchant_category": "GROCERIES",
            "channel": "CARD",
            "status": "APPROVED",
            "source_batch_id": "BATCH-001",
            "_run_id": "bronze-test",
            "_ingested_at": "2026-07-23T00:00:00Z",
            "_source_name": "test",
            "_source_file": "transactions.csv",
            "_record_checksum": "b" * 64,
            "_ingestion_date": "2026-07-22",
            "_landing_path": "data/output/landing/test/transactions.csv",
            "_corrupt_record": None,
        }


if __name__ == "__main__":
    unittest.main()
