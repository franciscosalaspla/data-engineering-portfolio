"""Validate Project 23 fixtures using only Python's standard library."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_COLUMNS = [
    "transaction_id",
    "account_id",
    "transaction_timestamp",
    "amount",
    "currency",
    "transaction_type",
    "merchant_id",
    "merchant_name",
    "merchant_category",
    "channel",
    "status",
    "source_batch_id",
]
ALLOWED_CURRENCIES = {"EUR", "USD", "GBP"}
ALLOWED_TRANSACTION_TYPES = {"PURCHASE", "TRANSFER", "PAYMENT", "WITHDRAWAL"}
ALLOWED_MERCHANT_CATEGORIES = {
    "GROCERIES",
    "TRANSFER",
    "TRANSPORT",
    "BUSINESS_SERVICES",
    "TRAVEL",
    "CASH_WITHDRAWAL",
    "ELECTRONICS",
}
ALLOWED_CHANNELS = {"ATM", "CARD", "MOBILE", "ONLINE"}
ALLOWED_TRANSACTION_STATUSES = {"APPROVED", "DECLINED", "PENDING"}
ALLOWED_CUSTOMER_SEGMENTS = {"RETAIL", "PREMIUM", "SME"}
ALLOWED_RISK_RATINGS = {"LOW", "MEDIUM", "HIGH"}
ALLOWED_ENTITY_STATUSES = {"ACTIVE", "SUSPENDED", "CLOSED"}
ALLOWED_ACCOUNT_TYPES = {"CHECKING", "SAVINGS", "CREDIT", "BUSINESS"}
REQUIRED_CUSTOMER_FIELDS = {
    "customer_id",
    "country_code",
    "segment",
    "onboarding_date",
    "status",
    "risk_rating",
}
REQUIRED_ACCOUNT_FIELDS = {
    "account_id",
    "customer_id",
    "account_type",
    "base_currency",
    "opened_date",
    "status",
}


class ValidationReport:
    """Collect named checks and unexpected validation failures."""

    def __init__(self) -> None:
        self.checks: List[str] = []
        self.errors: List[Dict[str, str]] = []
        self.counts: Dict[str, int] = {}

    def check(self, condition: bool, code: str, detail: str) -> bool:
        if condition:
            self.checks.append(code)
            return True
        self.errors.append({"code": code, "detail": detail})
        return False

    def error(self, code: str, detail: str) -> None:
        self.errors.append({"code": code, "detail": detail})

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": "PASSED" if not self.errors else "FAILED",
            "checks_passed": len(self.checks),
            "checks_failed": len(self.errors),
            "counts": self.counts,
            "errors": self.errors,
        }


def _load_json(path: Path, report: ValidationReport, code: str) -> Optional[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report.error(code, f"{path.name}: {exc}")
        return None
    if not isinstance(payload, dict):
        report.error(code, f"{path.name}: the root value must be an object")
        return None
    report.check(True, code, f"{path.name} is valid JSON")
    return payload


def _parse_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return True


def _parse_utc_timestamp(value: str) -> Optional[str]:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.date().isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_schema_documents(project_root: Path, report: ValidationReport) -> None:
    schema_dir = project_root / "schemas"
    expected = {
        "transactions.schema.json",
        "customers.schema.json",
        "accounts.schema.json",
        "fx_rates.schema.json",
    }
    actual = {path.name for path in schema_dir.glob("*.json")}
    report.check(actual == expected, "schemas.files", f"Expected {sorted(expected)}, found {sorted(actual)}")
    for name in sorted(expected & actual):
        payload = _load_json(schema_dir / name, report, f"schemas.json.{name}")
        if payload is None:
            continue
        report.check(
            payload.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
            f"schemas.draft.{name}",
            f"{name} must declare JSON Schema Draft 2020-12",
        )
        report.check(payload.get("type") == "object", f"schemas.root_type.{name}", f"{name} root type must be object")


def _validate_customers(payload: Dict[str, Any], report: ValidationReport) -> Set[str]:
    metadata = payload.get("fixture_metadata", {})
    report.check(metadata.get("is_synthetic") is True, "customers.synthetic", "Customers must be marked synthetic")
    customers = payload.get("customers")
    if not isinstance(customers, list):
        report.error("customers.collection", "customers must be an array")
        return set()

    ids: List[str] = []
    for index, customer in enumerate(customers, start=1):
        if not isinstance(customer, dict):
            report.error("customers.record", f"Customer {index} must be an object")
            continue
        missing = REQUIRED_CUSTOMER_FIELDS - set(customer)
        if missing:
            report.error("customers.required", f"Customer {index} missing {sorted(missing)}")
            continue
        customer_id = str(customer["customer_id"])
        ids.append(customer_id)
        rules = [
            (re.fullmatch(r"CUS-[0-9]{3}", customer_id) is not None, "customer_id.pattern"),
            (re.fullmatch(r"[A-Z]{2}", str(customer["country_code"])) is not None, "country_code.pattern"),
            (customer["segment"] in ALLOWED_CUSTOMER_SEGMENTS, "segment.invalid"),
            (_parse_date(str(customer["onboarding_date"])), "onboarding_date.invalid"),
            (customer["status"] in ALLOWED_ENTITY_STATUSES, "customer_status.invalid"),
            (customer["risk_rating"] in ALLOWED_RISK_RATINGS, "risk_rating.invalid"),
        ]
        for valid, rule in rules:
            if not valid:
                report.error(f"customers.{rule}", f"{customer_id}: {rule}")

    report.check(len(ids) == len(set(ids)), "customers.ids_unique", "customer_id values must be unique")
    report.check(bool(ids), "customers.not_empty", "At least one customer is required")
    report.counts["customers"] = len(ids)
    return set(ids)


def _validate_accounts(payload: Dict[str, Any], customer_ids: Set[str], report: ValidationReport) -> Set[str]:
    metadata = payload.get("fixture_metadata", {})
    report.check(metadata.get("is_synthetic") is True, "accounts.synthetic", "Accounts must be marked synthetic")
    accounts = payload.get("accounts")
    if not isinstance(accounts, list):
        report.error("accounts.collection", "accounts must be an array")
        return set()

    ids: List[str] = []
    for index, account in enumerate(accounts, start=1):
        if not isinstance(account, dict):
            report.error("accounts.record", f"Account {index} must be an object")
            continue
        missing = REQUIRED_ACCOUNT_FIELDS - set(account)
        if missing:
            report.error("accounts.required", f"Account {index} missing {sorted(missing)}")
            continue
        account_id = str(account["account_id"])
        ids.append(account_id)
        rules = [
            (re.fullmatch(r"ACC-[0-9]{3}", account_id) is not None, "account_id.pattern"),
            (account["customer_id"] in customer_ids, "customer_id.unknown"),
            (account["account_type"] in ALLOWED_ACCOUNT_TYPES, "account_type.invalid"),
            (account["base_currency"] in ALLOWED_CURRENCIES, "base_currency.invalid"),
            (_parse_date(str(account["opened_date"])), "opened_date.invalid"),
            (account["status"] in ALLOWED_ENTITY_STATUSES, "account_status.invalid"),
        ]
        for valid, rule in rules:
            if not valid:
                report.error(f"accounts.{rule}", f"{account_id}: {rule}")

    report.check(len(ids) == len(set(ids)), "accounts.ids_unique", "account_id values must be unique")
    report.check(bool(ids), "accounts.not_empty", "At least one account is required")
    report.counts["accounts"] = len(ids)
    return set(ids)


def _validate_fx_rates(payload: Dict[str, Any], report: ValidationReport) -> Set[Tuple[str, str]]:
    metadata = payload.get("fixture_metadata", {})
    report.check(metadata.get("is_synthetic") is True, "fx.synthetic", "FX rates must be marked synthetic")
    report.check(metadata.get("source") == "ECB_API_MOCK", "fx.mock_source", "FX source must be ECB_API_MOCK")
    report.check(payload.get("base") == "EUR", "fx.base", "FX base must be EUR")
    coverage: Set[Tuple[str, str]] = set()
    rate_dates: List[str] = []
    entries = payload.get("rates_by_date")
    if not isinstance(entries, list):
        report.error("fx.collection", "rates_by_date must be an array")
        return coverage
    for entry in entries:
        if not isinstance(entry, dict):
            report.error("fx.record", "Each FX entry must be an object")
            continue
        effective_date = str(entry.get("effective_date", ""))
        rates = entry.get("rates", {})
        if not _parse_date(effective_date):
            report.error("fx.date.invalid", f"Invalid FX date: {effective_date}")
            continue
        rate_dates.append(effective_date)
        if not isinstance(rates, dict) or set(rates) != ALLOWED_CURRENCIES:
            report.error("fx.currencies", f"{effective_date} must contain exactly EUR, USD and GBP")
            continue
        for currency, value in rates.items():
            if not isinstance(value, (int, float)) or value <= 0:
                report.error("fx.rate.not_positive", f"{effective_date}/{currency} must be positive")
                continue
            coverage.add((effective_date, currency))
        if rates.get("EUR") != 1.0:
            report.error("fx.eur_rate", f"{effective_date} EUR rate must equal 1.0")
    report.check(len(rate_dates) == len(set(rate_dates)), "fx.dates_unique", "FX dates must be unique")
    report.counts["fx_dates"] = len(rate_dates)
    return coverage


def _read_csv(path: Path, report: ValidationReport, code_prefix: str) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            if headers != CSV_COLUMNS:
                report.error(f"{code_prefix}.headers", f"{path.name} headers do not match the contract")
                return []
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        report.error(f"{code_prefix}.read", f"{path.name}: {exc}")
        return []
    report.check(True, f"{code_prefix}.headers", f"{path.name} headers match")
    return rows


def _transaction_issues(
    row: Dict[str, str],
    account_ids: Set[str],
    fx_coverage: Set[Tuple[str, str]],
) -> Set[str]:
    issues: Set[str] = set()
    for field in CSV_COLUMNS:
        if not str(row.get(field, "")).strip():
            issues.add(f"{field}.required")

    transaction_id = row.get("transaction_id", "")
    if transaction_id and re.fullmatch(r"TXN-[0-9]{4}", transaction_id) is None:
        issues.add("transaction_id.pattern")
    account_id = row.get("account_id", "")
    if account_id and account_id not in account_ids:
        issues.add("account_id.unknown")

    logical_date = _parse_utc_timestamp(row.get("transaction_timestamp", ""))
    if logical_date is None:
        issues.add("transaction_timestamp.invalid")

    try:
        amount = Decimal(row.get("amount", ""))
        if amount <= 0:
            issues.add("amount.not_positive")
        if amount.as_tuple().exponent < -2:
            issues.add("amount.scale")
    except (InvalidOperation, ValueError):
        issues.add("amount.invalid")

    currency = row.get("currency", "")
    if currency not in ALLOWED_CURRENCIES:
        issues.add("currency.invalid")
    elif logical_date is not None and (logical_date, currency) not in fx_coverage:
        issues.add("fx_rate.missing")

    if row.get("transaction_type") not in ALLOWED_TRANSACTION_TYPES:
        issues.add("transaction_type.invalid")
    if re.fullmatch(r"MER-[0-9]{3}", row.get("merchant_id", "")) is None:
        issues.add("merchant_id.pattern")
    if row.get("merchant_category") not in ALLOWED_MERCHANT_CATEGORIES:
        issues.add("merchant_category.invalid")
    if row.get("channel") not in ALLOWED_CHANNELS:
        issues.add("channel.invalid")
    if row.get("status") not in ALLOWED_TRANSACTION_STATUSES:
        issues.add("status.invalid")
    if row.get("source_batch_id") not in {"BATCH-001", "BATCH-002"}:
        issues.add("source_batch_id.invalid")
    return issues


def _validate_transactions(
    project_root: Path,
    manifest: Dict[str, Any],
    account_ids: Set[str],
    fx_coverage: Set[Tuple[str, str]],
    report: ValidationReport,
) -> None:
    valid_dir = project_root / "data" / "fixtures" / "valid"
    invalid_dir = project_root / "data" / "fixtures" / "invalid"
    batch_paths = {
        "valid_batch_001": valid_dir / "transactions_batch_001.csv",
        "valid_batch_001_replay": valid_dir / "transactions_batch_001_replay.csv",
        "valid_batch_002": valid_dir / "transactions_batch_002.csv",
    }
    batches: Dict[str, List[Dict[str, str]]] = {}
    for name, path in batch_paths.items():
        rows = _read_csv(path, report, name)
        batches[name] = rows
        for row in rows:
            issues = _transaction_issues(row, account_ids, fx_coverage)
            if issues:
                report.error(f"{name}.unexpected_invalid", f"{row.get('transaction_id')}: {sorted(issues)}")
        report.counts[name] = len(rows)

    original_rows = batches["valid_batch_001"]
    second_rows = batches["valid_batch_002"]
    non_replay_ids = [row.get("transaction_id", "") for row in original_rows + second_rows]
    report.check(
        len(non_replay_ids) == len(set(non_replay_ids)),
        "transactions.ids_unique",
        "Transaction IDs must be unique across original microlots",
    )
    report.counts["valid_transactions_total_excluding_replay"] = len(non_replay_ids)

    replay = manifest.get("replay", {})
    original_path = project_root / str(replay.get("original", ""))
    replay_path = project_root / str(replay.get("replay", ""))
    replay_matches = original_path.is_file() and replay_path.is_file() and original_path.read_bytes() == replay_path.read_bytes()
    report.check(replay_matches, "transactions.replay_exact", "Batch 001 replay must match the original byte for byte")

    valid_rows = original_rows + second_rows
    currency_coverage = {row["currency"] for row in valid_rows}
    channel_coverage = {row["channel"] for row in valid_rows}
    logical_dates = {
        logical_date
        for row in valid_rows
        if (logical_date := _parse_utc_timestamp(row["transaction_timestamp"])) is not None
    }
    required = manifest.get("required_coverage", {})
    report.check(currency_coverage == set(required.get("currencies", [])), "transactions.currency_coverage", "Currency coverage differs from manifest")
    report.check(channel_coverage == set(required.get("channels", [])), "transactions.channel_coverage", "Channel coverage differs from manifest")
    report.check(logical_dates == set(required.get("logical_dates", [])), "transactions.date_coverage", "Logical date coverage differs from manifest")

    invalid_rows = _read_csv(invalid_dir / "transactions_invalid.csv", report, "invalid_transactions")
    expected_invalid = {
        transaction_id: set(codes)
        for transaction_id, codes in manifest.get("expected_invalid_records", {}).items()
    }
    actual_invalid: Dict[str, Set[str]] = {}
    for row in invalid_rows:
        transaction_id = row.get("transaction_id", "")
        actual_invalid[transaction_id] = _transaction_issues(row, account_ids, fx_coverage)
    report.check(
        actual_invalid == expected_invalid,
        "invalid_transactions.expected_issues",
        f"Expected invalid issues {expected_invalid}, found {actual_invalid}",
    )
    report.counts["invalid_transactions"] = len(invalid_rows)


def _validate_manifest_files(project_root: Path, manifest: Dict[str, Any], report: ValidationReport) -> None:
    expected_files = manifest.get("expected_files", [])
    if not isinstance(expected_files, list):
        report.error("manifest.expected_files", "expected_files must be an array")
        return
    missing = [relative for relative in expected_files if not (project_root / relative).is_file()]
    report.check(not missing, "manifest.files_present", f"Missing expected files: {missing}")

    expected_hashes = manifest.get("expected_sha256", {})
    mismatches = []
    for relative, expected_hash in expected_hashes.items():
        path = project_root / relative
        if not path.is_file() or _sha256(path) != expected_hash:
            mismatches.append(relative)
    report.check(not mismatches, "manifest.checksums", f"Checksum mismatch: {mismatches}")


def _validate_expected_counts(manifest: Dict[str, Any], report: ValidationReport) -> None:
    expected_counts = manifest.get("expected_counts", {})
    mismatches = {
        name: {"expected": expected, "actual": report.counts.get(name)}
        for name, expected in expected_counts.items()
        if report.counts.get(name) != expected
    }
    report.check(not mismatches, "manifest.expected_counts", f"Count mismatches: {mismatches}")


def validate_project(project_root: Path = PROJECT_ROOT) -> Dict[str, Any]:
    """Validate all project contracts and return a serializable report."""
    report = ValidationReport()
    manifest = _load_json(project_root / "manifest" / "expected_results.json", report, "manifest.json")
    if manifest is None:
        return report.as_dict()
    report.check(manifest.get("is_synthetic") is True, "manifest.synthetic", "Manifest must mark fixtures as synthetic")
    report.check(manifest.get("fixture_seed") == 2301, "manifest.seed", "Fixture seed must be 2301")

    _validate_manifest_files(project_root, manifest, report)
    _validate_schema_documents(project_root, report)

    valid_dir = project_root / "data" / "fixtures" / "valid"
    customers = _load_json(valid_dir / "customers.json", report, "customers.json")
    accounts = _load_json(valid_dir / "accounts.json", report, "accounts.json")
    fx_rates = _load_json(valid_dir / "fx_rates.json", report, "fx.json")
    if customers is None or accounts is None or fx_rates is None:
        return report.as_dict()

    customer_ids = _validate_customers(customers, report)
    account_ids = _validate_accounts(accounts, customer_ids, report)
    fx_coverage = _validate_fx_rates(fx_rates, report)
    _validate_transactions(project_root, manifest, account_ids, fx_coverage, report)
    _validate_expected_counts(manifest, report)
    return report.as_dict()


def main() -> int:
    result = validate_project()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
