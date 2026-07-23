"""Integration-style unit tests for the local Landing/Bronze pipeline."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from bankfx_ingestion import IngestionPipeline  # noqa: E402
from bankfx_ingestion.config import load_source_config  # noqa: E402
from bankfx_ingestion.storage import record_checksum  # noqa: E402


class IngestionPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temporary_directory.name) / "project"
        self.project_root.mkdir()
        for name in ("adf", "config", "schemas"):
            shutil.copytree(PROJECT_ROOT / name, self.project_root / name)
        shutil.copytree(PROJECT_ROOT / "data" / "fixtures", self.project_root / "data" / "fixtures")
        (self.project_root / "data" / "output").mkdir(parents=True)
        self.pipeline = IngestionPipeline(self.project_root)
        self.summary = self.pipeline.run("test-run-001", "2026-07-22")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_configuration_is_metadata_driven(self) -> None:
        sources = load_source_config(self.project_root / "config" / "sources.json")

        self.assertEqual(7, len(sources))
        self.assertTrue(all(source.enabled for source in sources))
        self.assertEqual({"csv", "json"}, {source.file_format for source in sources})
        self.assertTrue(all(source.business_key for source in sources))

    def test_csv_sources_create_eight_valid_bronze_rows(self) -> None:
        rows = self._bronze_rows("transactions")

        self.assertEqual(8, len(rows))
        self.assertEqual(8, len({row["transaction_id"] for row in rows}))

    def test_json_sources_are_ingested(self) -> None:
        self.assertEqual(5, len(self._bronze_rows("customers")))
        self.assertEqual(7, len(self._bronze_rows("accounts")))
        self.assertEqual(2, len(self._bronze_rows("fx_rates")))

    def test_landing_preserves_original_bytes_and_sha256(self) -> None:
        successful = [
            source for source in self.summary.sources if source["status"] in {"SUCCESS", "PARTIAL"}
        ]
        self.assertEqual(6, len(successful))
        for audit in successful:
            source = self.project_root / audit["source_path"]
            landing = self.project_root / audit["landing_path"]
            metadata = json.loads(
                landing.with_name(f"{landing.name}.metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(source.read_bytes(), landing.read_bytes())
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), metadata["sha256"])
            self.assertEqual(audit["checksum"], metadata["sha256"])

    def test_bronze_contains_required_technical_metadata(self) -> None:
        required = {
            "_run_id",
            "_ingested_at",
            "_source_name",
            "_source_file",
            "_record_checksum",
            "_ingestion_date",
            "_landing_path",
        }
        for row in self._all_bronze_rows():
            self.assertTrue(required.issubset(row))
            original = {key: value for key, value in row.items() if not key.startswith("_")}
            self.assertEqual(record_checksum(original), row["_record_checksum"])

    def test_replay_is_skipped_during_first_run(self) -> None:
        replay = next(
            source
            for source in self.summary.sources
            if source["source_path"].endswith("transactions_batch_001_replay.csv")
        )

        self.assertEqual("SKIPPED", replay["status"])
        self.assertEqual(4, replay["duplicate_row_count"])
        self.assertEqual(0, replay["accepted_row_count"])

    def test_second_run_is_idempotent(self) -> None:
        paths_before = {
            path.relative_to(self.project_root): path.read_bytes()
            for path in (self.project_root / "data" / "output" / "bronze").rglob("*.jsonl")
        }
        second = IngestionPipeline(self.project_root).run("test-run-002", "2026-07-22")
        paths_after = {
            path.relative_to(self.project_root): path.read_bytes()
            for path in (self.project_root / "data" / "output" / "bronze").rglob("*.jsonl")
        }

        self.assertEqual("SUCCESS", second.status)
        self.assertTrue(all(source["status"] == "SKIPPED" for source in second.sources))
        self.assertEqual(paths_before, paths_after)
        self.assertEqual(29, sum(source["duplicate_row_count"] for source in second.sources))

    def test_audit_has_required_fields_and_reconciled_counts(self) -> None:
        audit_path = self.project_root / "data" / "output" / "audit" / "ingestion_audit.jsonl"
        audit_rows = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
        required = {
            "run_id",
            "source_name",
            "entity_name",
            "source_path",
            "landing_path",
            "bronze_path",
            "source_row_count",
            "accepted_row_count",
            "rejected_row_count",
            "duplicate_row_count",
            "checksum",
            "started_at",
            "finished_at",
            "duration_ms",
            "status",
            "error_message",
        }

        self.assertEqual(7, len(audit_rows))
        self.assertTrue(all(required.issubset(row) for row in audit_rows))
        for row in audit_rows:
            if row["status"] != "SKIPPED":
                self.assertEqual(
                    row["source_row_count"],
                    row["accepted_row_count"] + row["rejected_row_count"],
                )

    def test_invalid_rows_are_quarantined_with_reasons(self) -> None:
        quarantine_files = list(
            (self.project_root / "data" / "output" / "quarantine").rglob("*.jsonl")
        )
        self.assertEqual(1, len(quarantine_files))
        rejected = [json.loads(line) for line in quarantine_files[0].read_text(encoding="utf-8").splitlines()]

        self.assertEqual(3, len(rejected))
        self.assertTrue(all(row["_error_type"] == "DATA_QUALITY" for row in rejected))
        self.assertTrue(all(row["_rejection_reasons"] for row in rejected))
        self.assertEqual(
            {"TXN-9001", "TXN-9002", "TXN-9003"},
            {row["original_record"]["transaction_id"] for row in rejected},
        )

    def test_data_rejections_do_not_remove_valid_bronze(self) -> None:
        self.assertEqual("PARTIAL", self.summary.status)
        self.assertEqual(22, len(self._all_bronze_rows()))
        self.assertEqual(8, len(self._bronze_rows("transactions")))

    def test_technical_failure_is_distinguished_and_other_sources_continue(self) -> None:
        config_path = self.project_root / "config" / "sources.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["sources"][2]["source_path"] = "data/fixtures/valid/missing_fx.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        shutil.rmtree(self.project_root / "data" / "output")
        (self.project_root / "data" / "output").mkdir()

        summary = IngestionPipeline(self.project_root).run("technical-failure", "2026-07-22")
        failed = [source for source in summary.sources if source["status"] == "FAILED"]

        self.assertEqual("FAILED", summary.status)
        self.assertEqual(1, len(failed))
        self.assertEqual("TECHNICAL", failed[0]["error_type"])
        self.assertEqual(8, len(self._bronze_rows("transactions")))

    def _bronze_rows(self, entity_name: str) -> list[dict[str, object]]:
        root = self.project_root / "data" / "output" / "bronze" / entity_name
        rows: list[dict[str, object]] = []
        for path in sorted(root.rglob("records.jsonl")):
            rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
        return rows

    def _all_bronze_rows(self) -> list[dict[str, object]]:
        root = self.project_root / "data" / "output" / "bronze"
        rows: list[dict[str, object]] = []
        for path in sorted(root.rglob("records.jsonl")):
            rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
        return rows


class AdfArtifactTests(unittest.TestCase):
    def test_adf_json_is_valid_and_contains_required_activities(self) -> None:
        artifacts = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in (PROJECT_ROOT / "adf").rglob("*.json")
        }
        master_types = {
            activity["type"]
            for activity in artifacts["pl_master_metadata_ingestion.json"]["properties"]["activities"]
        }
        reusable = artifacts["pl_ingest_source.json"]["properties"]
        switch = next(activity for activity in reusable["activities"] if activity["type"] == "Switch")
        nested_types = {
            activity["type"]
            for case in switch["typeProperties"]["cases"]
            for activity in case["activities"]
        }

        self.assertGreaterEqual(len(artifacts), 9)
        self.assertTrue({"Lookup", "ForEach"}.issubset(master_types))
        self.assertIn("Copy", nested_types)
        self.assertEqual(
            "Stopped",
            artifacts["tr_example_schedule_disabled.json"]["properties"]["runtimeState"],
        )

    def test_adf_artifacts_do_not_contain_secret_values(self) -> None:
        forbidden_keys = {
            "accountkey",
            "clientsecret",
            "connectionstring",
            "password",
            "sasuri",
            "token",
        }
        findings: list[str] = []

        def inspect(value: object, path: str) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    normalized = key.lower().replace("_", "")
                    if normalized in forbidden_keys:
                        findings.append(f"{path}.{key}")
                    inspect(child, f"{path}.{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    inspect(child, f"{path}[{index}]")

        for artifact in (PROJECT_ROOT / "adf").rglob("*.json"):
            inspect(json.loads(artifact.read_text(encoding="utf-8")), artifact.name)

        self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main()
