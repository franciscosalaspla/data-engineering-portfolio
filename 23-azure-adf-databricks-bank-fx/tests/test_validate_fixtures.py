"""Unit tests for the deterministic fixtures and local validator."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_fixtures import generate_fixtures  # noqa: E402
from validate_fixtures import validate_project  # noqa: E402


class FixtureValidationTests(unittest.TestCase):
    def test_repository_fixtures_pass(self) -> None:
        result = validate_project(PROJECT_ROOT)

        self.assertEqual("PASSED", result["status"], result["errors"])
        self.assertEqual(0, result["checks_failed"])

    def test_replay_byte_change_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            copied_project = Path(temporary_directory) / "project"
            shutil.copytree(PROJECT_ROOT, copied_project)
            replay = copied_project / "data" / "fixtures" / "valid" / "transactions_batch_001_replay.csv"
            replay.write_bytes(replay.read_bytes() + b"\n")

            result = validate_project(copied_project)
            error_codes = {error["code"] for error in result["errors"]}

            self.assertEqual("FAILED", result["status"])
            self.assertIn("transactions.replay_exact", error_codes)
            self.assertIn("manifest.checksums", error_codes)

    def test_missing_expected_invalid_issue_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            copied_project = Path(temporary_directory) / "project"
            shutil.copytree(PROJECT_ROOT, copied_project)
            invalid_file = copied_project / "data" / "fixtures" / "invalid" / "transactions_invalid.csv"
            invalid_file.write_text(
                invalid_file.read_text(encoding="utf-8").replace("-20.00", "20.00"),
                encoding="utf-8",
            )

            result = validate_project(copied_project)
            error_codes = {error["code"] for error in result["errors"]}

            self.assertEqual("FAILED", result["status"])
            self.assertIn("invalid_transactions.expected_issues", error_codes)

    def test_generator_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            first_root = Path(temporary_directory) / "first"
            second_root = Path(temporary_directory) / "second"
            generate_fixtures(first_root)
            generate_fixtures(second_root)

            first_files = sorted(
                path.relative_to(first_root)
                for path in first_root.rglob("*")
                if path.is_file()
            )
            second_files = sorted(
                path.relative_to(second_root)
                for path in second_root.rglob("*")
                if path.is_file()
            )

            self.assertEqual(first_files, second_files)
            for relative_path in first_files:
                self.assertEqual(
                    (first_root / relative_path).read_bytes(),
                    (second_root / relative_path).read_bytes(),
                    str(relative_path),
                )


if __name__ == "__main__":
    unittest.main()
