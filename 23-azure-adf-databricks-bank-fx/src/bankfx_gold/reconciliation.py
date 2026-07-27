"""Post-write dimensional integrity and financial reconciliation checks."""

from __future__ import annotations

from decimal import Decimal

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


DIMENSION_KEYS = {
    "dim_date": "date_key",
    "dim_customer": "customer_key",
    "dim_account": "account_key",
    "dim_merchant": "merchant_key",
    "dim_channel": "channel_key",
    "dim_currency": "currency_key",
}


def reconcile_gold(
    source_transactions: DataFrame,
    rejected_records: DataFrame,
    fact: DataFrame,
    dimensions: dict[str, DataFrame],
) -> dict[str, object]:
    source_count = source_transactions.count()
    fact_count = fact.count()
    rejected_count = rejected_records.select("transaction_id").distinct().count()
    duplicate_fact_keys = fact.groupBy("transaction_id").count().filter("count > 1").count()
    null_foreign_keys = fact.filter(
        F.col("date_key").isNull()
        | F.col("customer_key").isNull()
        | F.col("account_key").isNull()
        | F.col("merchant_key").isNull()
        | F.col("channel_key").isNull()
        | F.col("currency_key").isNull()
    ).count()

    orphan_counts: dict[str, int] = {}
    surrogate_duplicates: dict[str, int] = {}
    for table_name, key in DIMENSION_KEYS.items():
        dimension = dimensions[table_name]
        orphan_counts[table_name] = fact.select(key).distinct().join(
            dimension.select(key).distinct(), key, "left_anti"
        ).count()
        surrogate_duplicates[table_name] = dimension.groupBy(key).count().filter("count > 1").count()

    source_amount = _decimal_sum(source_transactions, "amount")
    rejected_amount = _decimal_sum(
        rejected_records.dropDuplicates(["transaction_id"]), "amount"
    )
    accepted_source_amount = source_amount - rejected_amount
    fact_original_amount = _decimal_sum(fact, "amount_original")
    fact_eur_amount = _decimal_sum(fact, "amount_eur")
    checks = {
        "row_count_reconciled": source_count == fact_count + rejected_count,
        "original_amount_reconciled": accepted_source_amount == fact_original_amount,
        "fact_business_keys_unique": duplicate_fact_keys == 0,
        "fact_foreign_keys_not_null": null_foreign_keys == 0,
        "fact_foreign_keys_resolved": all(value == 0 for value in orphan_counts.values()),
        "dimension_surrogate_keys_unique": all(value == 0 for value in surrogate_duplicates.values()),
    }
    return {
        "status": "PASSED" if all(checks.values()) else "FAILED",
        "checks": checks,
        "source_transaction_count": source_count,
        "fact_transaction_count": fact_count,
        "rejected_transaction_count": rejected_count,
        "duplicate_fact_business_key_count": duplicate_fact_keys,
        "null_fact_foreign_key_count": null_foreign_keys,
        "orphan_counts": orphan_counts,
        "dimension_surrogate_duplicate_counts": surrogate_duplicates,
        "source_original_amount_sum": str(source_amount),
        "rejected_original_amount_sum": str(rejected_amount),
        "accepted_source_original_amount_sum": str(accepted_source_amount),
        "fact_original_amount_sum": str(fact_original_amount),
        "fact_eur_amount_sum": str(fact_eur_amount),
    }


def _decimal_sum(frame: DataFrame, column: str) -> Decimal:
    value = frame.agg(F.sum(column).alias("amount_sum")).first()["amount_sum"]
    return value if value is not None else Decimal("0.00")
