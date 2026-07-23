"""Explicit Bronze schemas used by every production read."""

from __future__ import annotations

from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)


TECHNICAL_FIELDS = [
    StructField("_run_id", StringType(), True),
    StructField("_ingested_at", StringType(), True),
    StructField("_source_name", StringType(), True),
    StructField("_source_file", StringType(), True),
    StructField("_record_checksum", StringType(), True),
    StructField("_ingestion_date", StringType(), True),
    StructField("_landing_path", StringType(), True),
    StructField("_corrupt_record", StringType(), True),
]


BRONZE_SCHEMAS: dict[str, StructType] = {
    "customers": StructType(
        [
            StructField("customer_id", StringType(), True),
            StructField("country_code", StringType(), True),
            StructField("segment", StringType(), True),
            StructField("onboarding_date", StringType(), True),
            StructField("status", StringType(), True),
            StructField("risk_rating", StringType(), True),
            *TECHNICAL_FIELDS,
        ]
    ),
    "accounts": StructType(
        [
            StructField("account_id", StringType(), True),
            StructField("customer_id", StringType(), True),
            StructField("account_type", StringType(), True),
            StructField("base_currency", StringType(), True),
            StructField("opened_date", StringType(), True),
            StructField("status", StringType(), True),
            *TECHNICAL_FIELDS,
        ]
    ),
    "transactions": StructType(
        [
            StructField("transaction_id", StringType(), True),
            StructField("account_id", StringType(), True),
            StructField("transaction_timestamp", StringType(), True),
            StructField("amount", StringType(), True),
            StructField("currency", StringType(), True),
            StructField("transaction_type", StringType(), True),
            StructField("merchant_id", StringType(), True),
            StructField("merchant_name", StringType(), True),
            StructField("merchant_category", StringType(), True),
            StructField("channel", StringType(), True),
            StructField("status", StringType(), True),
            StructField("source_batch_id", StringType(), True),
            *TECHNICAL_FIELDS,
        ]
    ),
    "fx_rates": StructType(
        [
            StructField("base", StringType(), True),
            StructField("effective_date", StringType(), True),
            StructField(
                "rates",
                StructType(
                    [
                        StructField("EUR", DoubleType(), True),
                        StructField("USD", DoubleType(), True),
                        StructField("GBP", DoubleType(), True),
                    ]
                ),
                True,
            ),
            *TECHNICAL_FIELDS,
        ]
    ),
}


def bronze_schema(entity_name: str) -> StructType:
    try:
        return BRONZE_SCHEMAS[entity_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported Bronze entity: {entity_name}") from exc
