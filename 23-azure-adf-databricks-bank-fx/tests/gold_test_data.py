"""Small synthetic Silver frames shared by Gold-only tests."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from pyspark.sql import DataFrame, SparkSession


def silver_frames(spark: SparkSession) -> dict[str, DataFrame]:
    customers = spark.createDataFrame(
        [
            ("CUS-001", "ES", "RETAIL", date(2024, 1, 10), "ACTIVE", "LOW", "silver-source"),
            ("CUS-002", "DE", "PREMIUM", date(2023, 5, 20), "ACTIVE", "MEDIUM", "silver-source"),
            ("CUS-003", "GB", "RETAIL", date(2025, 2, 1), "ACTIVE", "LOW", "silver-source"),
            ("CUS-004", "FR", "SME", date(2022, 9, 15), "ACTIVE", "MEDIUM", "silver-source"),
            ("CUS-005", "PT", "RETAIL", date(2026, 1, 5), "ACTIVE", "HIGH", "silver-source"),
        ],
        "customer_id string, country_code string, segment string, onboarding_date date, status string, risk_rating string, _silver_run_id string",
    )
    accounts = spark.createDataFrame(
        [
            ("ACC-001", "CUS-001", "CHECKING", "EUR", date(2024, 1, 11), "ACTIVE", "silver-source"),
            ("ACC-002", "CUS-002", "SAVINGS", "USD", date(2023, 5, 21), "ACTIVE", "silver-source"),
            ("ACC-003", "CUS-003", "CHECKING", "GBP", date(2025, 2, 2), "ACTIVE", "silver-source"),
            ("ACC-004", "CUS-004", "BUSINESS", "EUR", date(2022, 9, 16), "ACTIVE", "silver-source"),
            ("ACC-005", "CUS-005", "SAVINGS", "EUR", date(2026, 1, 6), "ACTIVE", "silver-source"),
            ("ACC-006", "CUS-005", "CHECKING", "GBP", date(2026, 2, 1), "ACTIVE", "silver-source"),
            ("ACC-007", "CUS-001", "CREDIT", "EUR", date(2024, 3, 1), "ACTIVE", "silver-source"),
        ],
        "account_id string, customer_id string, account_type string, base_currency string, opened_date date, status string, _silver_run_id string",
    )
    fx_rates = spark.createDataFrame(
        [
            (date(2026, 7, 20), 1.0, 1.15, 0.87),
            (date(2026, 7, 21), 1.0, 1.14, 0.86),
        ],
        "effective_date date, rate_eur double, rate_usd double, rate_gbp double",
    )
    processed = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
    transaction_values = [
        ("TXN-0001", "ACC-001", datetime(2026, 7, 20, 9, 0), Decimal("100.00"), "EUR", "PURCHASE", "MER-001", "Market One", "GROCERIES", "CARD", "APPROVED", "BATCH-001"),
        ("TXN-0002", "ACC-002", datetime(2026, 7, 20, 10, 0), Decimal("250.00"), "USD", "TRANSFER", "MER-002", "Bank Transfer", "TRANSFER", "ONLINE", "APPROVED", "BATCH-001"),
        ("TXN-0003", "ACC-003", datetime(2026, 7, 20, 11, 0), Decimal("75.50"), "GBP", "PURCHASE", "MER-003", "City Transit", "TRANSPORT", "MOBILE", "APPROVED", "BATCH-001"),
        ("TXN-0004", "ACC-004", datetime(2026, 7, 20, 12, 0), Decimal("500.00"), "EUR", "PAYMENT", "MER-004", "Office Services", "BUSINESS_SERVICES", "ONLINE", "APPROVED", "BATCH-001"),
        ("TXN-0005", "ACC-006", datetime(2026, 7, 21, 9, 0), Decimal("45.25"), "GBP", "PURCHASE", "MER-005", "Travel Desk", "TRAVEL", "CARD", "APPROVED", "BATCH-002"),
        ("TXN-0006", "ACC-007", datetime(2026, 7, 21, 10, 0), Decimal("80.00"), "EUR", "WITHDRAWAL", "MER-006", "Cash Point", "CASH_WITHDRAWAL", "ATM", "APPROVED", "BATCH-002"),
        ("TXN-0007", "ACC-002", datetime(2026, 7, 21, 11, 0), Decimal("120.00"), "USD", "PURCHASE", "MER-007", "Tech Store", "ELECTRONICS", "CARD", "APPROVED", "BATCH-002"),
        ("TXN-0008", "ACC-001", datetime(2026, 7, 21, 12, 0), Decimal("60.00"), "EUR", "TRANSFER", "MER-002", "Bank Transfer", "TRANSFER", "MOBILE", "APPROVED", "BATCH-002"),
    ]
    transactions = spark.createDataFrame(
        [
            (*values, f"checksum-{index:02d}", processed, "silver-source")
            for index, values in enumerate(transaction_values, start=1)
        ],
        "transaction_id string, account_id string, transaction_timestamp timestamp, amount decimal(18,2), currency string, transaction_type string, merchant_id string, merchant_name string, merchant_category string, channel string, status string, source_batch_id string, _record_checksum string, _silver_processed_at timestamp, _silver_run_id string",
    )
    return {
        "customers": customers,
        "accounts": accounts,
        "fx_rates": fx_rates,
        "transactions": transactions,
    }


def write_silver_delta(frames: dict[str, DataFrame], silver_root: str) -> None:
    names = {
        "customers": "silver_customers",
        "accounts": "silver_accounts",
        "fx_rates": "silver_fx_rates",
        "transactions": "silver_transactions",
    }
    for entity, table_name in names.items():
        frames[entity].write.format("delta").mode("overwrite").save(f"{silver_root}/{table_name}")
