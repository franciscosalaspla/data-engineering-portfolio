"""Generate deterministic, synthetic fixtures for Project 23."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SEED = 2301
SCHEMA_VERSION = "1.0.0"
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


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    path.write_text(content, encoding="utf-8")


def _csv_bytes(rows: Iterable[Dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _transaction(
    transaction_id: str,
    account_id: str,
    timestamp: str,
    amount: str,
    currency: str,
    transaction_type: str,
    merchant_id: str,
    merchant_name: str,
    merchant_category: str,
    channel: str,
    status: str,
    batch_id: str,
) -> Dict[str, str]:
    return dict(
        zip(
            CSV_COLUMNS,
            [
                transaction_id,
                account_id,
                timestamp,
                amount,
                currency,
                transaction_type,
                merchant_id,
                merchant_name,
                merchant_category,
                channel,
                status,
                batch_id,
            ],
        )
    )


def _build_payloads() -> Dict[str, Any]:
    customers = {
        "fixture_metadata": {"is_synthetic": True, "schema_version": SCHEMA_VERSION},
        "customers": [
            {
                "customer_id": "CUS-001",
                "country_code": "CL",
                "segment": "RETAIL",
                "onboarding_date": "2024-01-15",
                "status": "ACTIVE",
                "risk_rating": "LOW",
            },
            {
                "customer_id": "CUS-002",
                "country_code": "GB",
                "segment": "PREMIUM",
                "onboarding_date": "2024-03-10",
                "status": "ACTIVE",
                "risk_rating": "MEDIUM",
            },
            {
                "customer_id": "CUS-003",
                "country_code": "DE",
                "segment": "SME",
                "onboarding_date": "2024-05-22",
                "status": "ACTIVE",
                "risk_rating": "LOW",
            },
            {
                "customer_id": "CUS-004",
                "country_code": "CL",
                "segment": "RETAIL",
                "onboarding_date": "2024-08-01",
                "status": "SUSPENDED",
                "risk_rating": "HIGH",
            },
            {
                "customer_id": "CUS-005",
                "country_code": "ES",
                "segment": "PREMIUM",
                "onboarding_date": "2025-01-18",
                "status": "ACTIVE",
                "risk_rating": "MEDIUM",
            },
        ],
    }

    accounts = {
        "fixture_metadata": {"is_synthetic": True, "schema_version": SCHEMA_VERSION},
        "accounts": [
            {"account_id": "ACC-001", "customer_id": "CUS-001", "account_type": "CHECKING", "base_currency": "EUR", "opened_date": "2024-01-16", "status": "ACTIVE"},
            {"account_id": "ACC-002", "customer_id": "CUS-001", "account_type": "SAVINGS", "base_currency": "USD", "opened_date": "2024-02-01", "status": "ACTIVE"},
            {"account_id": "ACC-003", "customer_id": "CUS-002", "account_type": "CREDIT", "base_currency": "GBP", "opened_date": "2024-03-12", "status": "ACTIVE"},
            {"account_id": "ACC-004", "customer_id": "CUS-003", "account_type": "BUSINESS", "base_currency": "EUR", "opened_date": "2024-05-25", "status": "ACTIVE"},
            {"account_id": "ACC-005", "customer_id": "CUS-004", "account_type": "CHECKING", "base_currency": "USD", "opened_date": "2024-08-02", "status": "SUSPENDED"},
            {"account_id": "ACC-006", "customer_id": "CUS-005", "account_type": "SAVINGS", "base_currency": "GBP", "opened_date": "2025-01-20", "status": "ACTIVE"},
            {"account_id": "ACC-007", "customer_id": "CUS-005", "account_type": "CHECKING", "base_currency": "EUR", "opened_date": "2025-02-01", "status": "ACTIVE"},
        ],
    }

    fx_rates = {
        "fixture_metadata": {
            "is_synthetic": True,
            "source": "ECB_API_MOCK",
            "schema_version": SCHEMA_VERSION,
        },
        "base": "EUR",
        "rates_by_date": [
            {"effective_date": "2026-07-20", "rates": {"EUR": 1.0, "USD": 1.15, "GBP": 0.87}},
            {"effective_date": "2026-07-21", "rates": {"EUR": 1.0, "USD": 1.14, "GBP": 0.86}},
        ],
    }

    batch_001: List[Dict[str, str]] = [
        _transaction("TXN-0001", "ACC-001", "2026-07-20T09:15:00Z", "100.00", "EUR", "PURCHASE", "MER-001", "Synthetic Market", "GROCERIES", "CARD", "APPROVED", "BATCH-001"),
        _transaction("TXN-0002", "ACC-002", "2026-07-20T10:30:00Z", "250.00", "USD", "TRANSFER", "MER-002", "Synthetic Transfer Hub", "TRANSFER", "ONLINE", "APPROVED", "BATCH-001"),
        _transaction("TXN-0003", "ACC-003", "2026-07-20T12:05:00Z", "75.50", "GBP", "PURCHASE", "MER-003", "Synthetic Rail", "TRANSPORT", "MOBILE", "APPROVED", "BATCH-001"),
        _transaction("TXN-0004", "ACC-004", "2026-07-20T15:45:00Z", "500.00", "EUR", "PAYMENT", "MER-004", "Synthetic Cloud Services", "BUSINESS_SERVICES", "ONLINE", "PENDING", "BATCH-001"),
    ]

    batch_002: List[Dict[str, str]] = [
        _transaction("TXN-0005", "ACC-006", "2026-07-21T08:20:00Z", "45.25", "GBP", "PURCHASE", "MER-005", "Synthetic Travel Desk", "TRAVEL", "CARD", "APPROVED", "BATCH-002"),
        _transaction("TXN-0006", "ACC-007", "2026-07-21T11:10:00Z", "80.00", "EUR", "WITHDRAWAL", "MER-006", "Synthetic Cash Point", "CASH_WITHDRAWAL", "ATM", "APPROVED", "BATCH-002"),
        _transaction("TXN-0007", "ACC-002", "2026-07-21T14:35:00Z", "120.00", "USD", "PURCHASE", "MER-007", "Synthetic Tech Store", "ELECTRONICS", "CARD", "DECLINED", "BATCH-002"),
        _transaction("TXN-0008", "ACC-001", "2026-07-21T17:25:00Z", "60.00", "EUR", "TRANSFER", "MER-002", "Synthetic Transfer Hub", "TRANSFER", "MOBILE", "APPROVED", "BATCH-002"),
    ]

    invalid_transactions = [
        _transaction("TXN-9001", "ACC-999", "2026-07-21T18:00:00Z", "50.00", "USD", "PURCHASE", "MER-001", "Synthetic Market", "GROCERIES", "CARD", "APPROVED", "BATCH-002"),
        _transaction("TXN-9002", "ACC-001", "2026-07-21T18:05:00Z", "-20.00", "EUR", "PURCHASE", "MER-001", "Synthetic Market", "GROCERIES", "CARD", "APPROVED", "BATCH-002"),
        _transaction("TXN-9003", "ACC-002", "2026-07-21T18:10:00Z", "100.00", "CHF", "PURCHASE", "MER-007", "Synthetic Tech Store", "ELECTRONICS", "ONLINE", "APPROVED", "BATCH-002"),
    ]

    rng = random.Random(FIXTURE_SEED)
    rng.shuffle(batch_001)
    rng.shuffle(batch_002)

    return {
        "customers": customers,
        "accounts": accounts,
        "fx_rates": fx_rates,
        "batch_001": batch_001,
        "batch_002": batch_002,
        "invalid_transactions": invalid_transactions,
    }


def generate_fixtures(project_root: Path = PROJECT_ROOT) -> Dict[str, Any]:
    """Write all fixtures and return the generated manifest."""
    valid_dir = project_root / "data" / "fixtures" / "valid"
    invalid_dir = project_root / "data" / "fixtures" / "invalid"
    manifest_dir = project_root / "manifest"
    valid_dir.mkdir(parents=True, exist_ok=True)
    invalid_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(parents=True, exist_ok=True)

    payloads = _build_payloads()
    _write_json(valid_dir / "customers.json", payloads["customers"])
    _write_json(valid_dir / "accounts.json", payloads["accounts"])
    _write_json(valid_dir / "fx_rates.json", payloads["fx_rates"])

    batch_001_bytes = _csv_bytes(payloads["batch_001"])
    (valid_dir / "transactions_batch_001.csv").write_bytes(batch_001_bytes)
    (valid_dir / "transactions_batch_001_replay.csv").write_bytes(batch_001_bytes)
    (valid_dir / "transactions_batch_002.csv").write_bytes(_csv_bytes(payloads["batch_002"]))
    (invalid_dir / "transactions_invalid.csv").write_bytes(_csv_bytes(payloads["invalid_transactions"]))

    fixture_paths = sorted(
        [path for path in valid_dir.iterdir() if path.is_file()]
        + [path for path in invalid_dir.iterdir() if path.is_file()]
    )
    relative_paths = [path.relative_to(project_root).as_posix() for path in fixture_paths]
    manifest: Dict[str, Any] = {
        "manifest_version": "1.0.0",
        "fixture_seed": FIXTURE_SEED,
        "is_synthetic": True,
        "logical_generation_timestamp_utc": "2026-07-22T00:00:00Z",
        "expected_files": relative_paths,
        "expected_counts": {
            "customers": 5,
            "accounts": 7,
            "valid_batch_001": 4,
            "valid_batch_001_replay": 4,
            "valid_batch_002": 4,
            "valid_transactions_total_excluding_replay": 8,
            "invalid_transactions": 3,
        },
        "required_coverage": {
            "currencies": ["EUR", "USD", "GBP"],
            "channels": ["ATM", "CARD", "MOBILE", "ONLINE"],
            "logical_dates": ["2026-07-20", "2026-07-21"],
        },
        "replay": {
            "original": "data/fixtures/valid/transactions_batch_001.csv",
            "replay": "data/fixtures/valid/transactions_batch_001_replay.csv",
            "must_match_bytes": True,
        },
        "expected_invalid_records": {
            "TXN-9001": ["account_id.unknown"],
            "TXN-9002": ["amount.not_positive"],
            "TXN-9003": ["currency.invalid"],
        },
        "expected_sha256": {
            relative: _sha256(project_root / relative) for relative in relative_paths
        },
    }
    _write_json(manifest_dir / "expected_results.json", manifest)
    return manifest


def main() -> int:
    manifest = generate_fixtures()
    counts = manifest["expected_counts"]
    print(
        "Generated deterministic fixtures: "
        f"{counts['valid_transactions_total_excluding_replay']} valid transactions, "
        f"{counts['invalid_transactions']} expected invalid transactions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
