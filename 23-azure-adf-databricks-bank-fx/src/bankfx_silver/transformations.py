"""Entity normalization, quality rules and deterministic deduplication."""

from __future__ import annotations

from datetime import datetime
from typing import Callable

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType


ALLOWED_CURRENCIES = ["EUR", "USD", "GBP"]

QUALITY_REASONS = {
    "BRONZE_CORRUPT_RECORD": "The Bronze JSON line could not be parsed with the explicit schema.",
    "BRONZE_CHECKSUM_REQUIRED": "Bronze record checksum is required for traceability.",
    "CUSTOMER_ID_REQUIRED": "customer_id is required.",
    "CUSTOMER_ID_FORMAT": "customer_id must match CUS-NNN.",
    "CUSTOMER_COUNTRY_FORMAT": "country_code must contain two uppercase letters.",
    "CUSTOMER_SEGMENT_DOMAIN": "segment is outside the contract domain.",
    "CUSTOMER_ONBOARDING_DATE": "onboarding_date is missing or invalid.",
    "CUSTOMER_STATUS_DOMAIN": "customer status is outside the contract domain.",
    "CUSTOMER_RISK_DOMAIN": "risk_rating is outside the contract domain.",
    "ACCOUNT_ID_REQUIRED": "account_id is required.",
    "ACCOUNT_ID_FORMAT": "account_id must match ACC-NNN.",
    "ACCOUNT_CUSTOMER_ID_FORMAT": "customer_id must match CUS-NNN.",
    "ACCOUNT_TYPE_DOMAIN": "account_type is outside the contract domain.",
    "ACCOUNT_CURRENCY_DOMAIN": "base_currency must be EUR, USD or GBP.",
    "ACCOUNT_OPENED_DATE": "opened_date is missing or invalid.",
    "ACCOUNT_STATUS_DOMAIN": "account status is outside the contract domain.",
    "ACCOUNT_CUSTOMER_REFERENCE": "customer_id is not present in valid Silver customers.",
    "FX_EFFECTIVE_DATE": "effective_date is missing or invalid.",
    "FX_BASE_CURRENCY": "FX base currency must be EUR.",
    "FX_EUR_RATE": "EUR rate must equal 1.0.",
    "FX_USD_RATE": "USD rate must be positive.",
    "FX_GBP_RATE": "GBP rate must be positive.",
    "TRANSACTION_ID_REQUIRED": "transaction_id is required.",
    "TRANSACTION_ID_FORMAT": "transaction_id must match TXN-NNNN.",
    "TRANSACTION_ACCOUNT_ID_FORMAT": "account_id must match ACC-NNN.",
    "TRANSACTION_TIMESTAMP": "transaction_timestamp is missing or invalid.",
    "TRANSACTION_AMOUNT": "amount must be a positive decimal with at most two decimals.",
    "TRANSACTION_CURRENCY_DOMAIN": "currency must be EUR, USD or GBP.",
    "TRANSACTION_TYPE_DOMAIN": "transaction_type is outside the contract domain.",
    "TRANSACTION_MERCHANT_ID_FORMAT": "merchant_id must match MER-NNN.",
    "TRANSACTION_MERCHANT_NAME": "merchant_name is required.",
    "TRANSACTION_MERCHANT_CATEGORY": "merchant_category is outside the contract domain.",
    "TRANSACTION_CHANNEL_DOMAIN": "channel is outside the contract domain.",
    "TRANSACTION_STATUS_DOMAIN": "transaction status is outside the contract domain.",
    "TRANSACTION_BATCH_DOMAIN": "source_batch_id is outside the contract domain.",
    "TRANSACTION_ACCOUNT_REFERENCE": "account_id is not present in valid Silver accounts.",
    "DUPLICATE_BUSINESS_KEY": "A deterministic winner already exists for this business key in the input.",
}


def normalize_entity(
    entity_name: str,
    frame: DataFrame,
    silver_run_id: str,
    processed_at: datetime,
    reference_frame: DataFrame | None = None,
) -> DataFrame:
    handlers: dict[str, Callable[[DataFrame], DataFrame]] = {
        "customers": normalize_customers,
        "accounts": normalize_accounts,
        "fx_rates": normalize_fx_rates,
        "transactions": normalize_transactions,
    }
    try:
        prepared = _with_silver_metadata(frame, silver_run_id, processed_at)
        normalized = handlers[entity_name](prepared)
    except KeyError as exc:
        raise ValueError(f"Unsupported Silver entity: {entity_name}") from exc

    if entity_name == "accounts":
        if reference_frame is None:
            raise ValueError("Silver customers are required to validate accounts")
        normalized = _add_reference_rule(
            normalized,
            reference_frame,
            local_key="customer_id",
            reference_key="customer_id",
            rule_name="ACCOUNT_CUSTOMER_REFERENCE",
        )
    elif entity_name == "transactions":
        if reference_frame is None:
            raise ValueError("Silver accounts are required to validate transactions")
        normalized = _add_reference_rule(
            normalized,
            reference_frame,
            local_key="account_id",
            reference_key="account_id",
            rule_name="TRANSACTION_ACCOUNT_REFERENCE",
        )
    return normalized


def normalize_customers(frame: DataFrame) -> DataFrame:
    normalized = (
        frame.withColumn("customer_id", F.upper(F.trim("customer_id")))
        .withColumn("country_code", F.upper(F.trim("country_code")))
        .withColumn("segment", F.upper(F.trim("segment")))
        .withColumn("onboarding_date", F.to_date("onboarding_date"))
        .withColumn("status", F.upper(F.trim("status")))
        .withColumn("risk_rating", F.upper(F.trim("risk_rating")))
    )
    return _initialize_quality(
        normalized,
        [
            (F.col("customer_id").isNotNull(), "CUSTOMER_ID_REQUIRED"),
            (F.col("customer_id").rlike(r"^CUS-[0-9]{3}$"), "CUSTOMER_ID_FORMAT"),
            (F.col("country_code").rlike(r"^[A-Z]{2}$"), "CUSTOMER_COUNTRY_FORMAT"),
            (F.col("segment").isin("RETAIL", "PREMIUM", "SME"), "CUSTOMER_SEGMENT_DOMAIN"),
            (F.col("onboarding_date").isNotNull(), "CUSTOMER_ONBOARDING_DATE"),
            (F.col("status").isin("ACTIVE", "SUSPENDED", "CLOSED"), "CUSTOMER_STATUS_DOMAIN"),
            (F.col("risk_rating").isin("LOW", "MEDIUM", "HIGH"), "CUSTOMER_RISK_DOMAIN"),
        ],
    )


def normalize_accounts(frame: DataFrame) -> DataFrame:
    normalized = (
        frame.withColumn("account_id", F.upper(F.trim("account_id")))
        .withColumn("customer_id", F.upper(F.trim("customer_id")))
        .withColumn("account_type", F.upper(F.trim("account_type")))
        .withColumn("base_currency", F.upper(F.trim("base_currency")))
        .withColumn("opened_date", F.to_date("opened_date"))
        .withColumn("status", F.upper(F.trim("status")))
    )
    return _initialize_quality(
        normalized,
        [
            (F.col("account_id").isNotNull(), "ACCOUNT_ID_REQUIRED"),
            (F.col("account_id").rlike(r"^ACC-[0-9]{3}$"), "ACCOUNT_ID_FORMAT"),
            (F.col("customer_id").rlike(r"^CUS-[0-9]{3}$"), "ACCOUNT_CUSTOMER_ID_FORMAT"),
            (
                F.col("account_type").isin("CHECKING", "SAVINGS", "CREDIT", "BUSINESS"),
                "ACCOUNT_TYPE_DOMAIN",
            ),
            (F.col("base_currency").isin(*ALLOWED_CURRENCIES), "ACCOUNT_CURRENCY_DOMAIN"),
            (F.col("opened_date").isNotNull(), "ACCOUNT_OPENED_DATE"),
            (F.col("status").isin("ACTIVE", "SUSPENDED", "CLOSED"), "ACCOUNT_STATUS_DOMAIN"),
        ],
    )


def normalize_transactions(frame: DataFrame) -> DataFrame:
    normalized = (
        frame.withColumn(
            "_amount_format_valid",
            F.col("amount").rlike(r"^[0-9]+(\.[0-9]{1,2})?$"),
        )
        .withColumn(
            "_timestamp_format_valid",
            F.col("transaction_timestamp").rlike(
                r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
            ),
        )
        .withColumn("transaction_id", F.upper(F.trim("transaction_id")))
        .withColumn("account_id", F.upper(F.trim("account_id")))
        .withColumn("transaction_timestamp", F.to_timestamp("transaction_timestamp"))
        .withColumn("amount", F.trim("amount").cast(DecimalType(18, 2)))
        .withColumn("currency", F.upper(F.trim("currency")))
        .withColumn("transaction_type", F.upper(F.trim("transaction_type")))
        .withColumn("merchant_id", F.upper(F.trim("merchant_id")))
        .withColumn("merchant_name", F.trim("merchant_name"))
        .withColumn("merchant_category", F.upper(F.trim("merchant_category")))
        .withColumn("channel", F.upper(F.trim("channel")))
        .withColumn("status", F.upper(F.trim("status")))
        .withColumn("source_batch_id", F.upper(F.trim("source_batch_id")))
    )
    return _initialize_quality(
        normalized,
        [
            (F.col("transaction_id").isNotNull(), "TRANSACTION_ID_REQUIRED"),
            (F.col("transaction_id").rlike(r"^TXN-[0-9]{4}$"), "TRANSACTION_ID_FORMAT"),
            (F.col("account_id").rlike(r"^ACC-[0-9]{3}$"), "TRANSACTION_ACCOUNT_ID_FORMAT"),
            (
                F.col("_timestamp_format_valid") & F.col("transaction_timestamp").isNotNull(),
                "TRANSACTION_TIMESTAMP",
            ),
            (
                F.col("_amount_format_valid")
                & F.col("amount").isNotNull()
                & (F.col("amount") > 0),
                "TRANSACTION_AMOUNT",
            ),
            (F.col("currency").isin(*ALLOWED_CURRENCIES), "TRANSACTION_CURRENCY_DOMAIN"),
            (
                F.col("transaction_type").isin("PURCHASE", "TRANSFER", "PAYMENT", "WITHDRAWAL"),
                "TRANSACTION_TYPE_DOMAIN",
            ),
            (F.col("merchant_id").rlike(r"^MER-[0-9]{3}$"), "TRANSACTION_MERCHANT_ID_FORMAT"),
            (F.length(F.col("merchant_name")) > 0, "TRANSACTION_MERCHANT_NAME"),
            (
                F.col("merchant_category").isin(
                    "GROCERIES",
                    "TRANSFER",
                    "TRANSPORT",
                    "BUSINESS_SERVICES",
                    "TRAVEL",
                    "CASH_WITHDRAWAL",
                    "ELECTRONICS",
                ),
                "TRANSACTION_MERCHANT_CATEGORY",
            ),
            (F.col("channel").isin("ATM", "CARD", "MOBILE", "ONLINE"), "TRANSACTION_CHANNEL_DOMAIN"),
            (F.col("status").isin("APPROVED", "DECLINED", "PENDING"), "TRANSACTION_STATUS_DOMAIN"),
            (F.col("source_batch_id").isin("BATCH-001", "BATCH-002"), "TRANSACTION_BATCH_DOMAIN"),
        ],
    )


def normalize_fx_rates(frame: DataFrame) -> DataFrame:
    normalized = (
        frame.withColumn("base", F.upper(F.trim("base")))
        .withColumn("effective_date", F.to_date("effective_date"))
        .withColumn("rate_eur", F.col("rates.EUR").cast("double"))
        .withColumn("rate_usd", F.col("rates.USD").cast("double"))
        .withColumn("rate_gbp", F.col("rates.GBP").cast("double"))
        .drop("rates")
    )
    return _initialize_quality(
        normalized,
        [
            (F.col("effective_date").isNotNull(), "FX_EFFECTIVE_DATE"),
            (F.col("base") == "EUR", "FX_BASE_CURRENCY"),
            (F.col("rate_eur") == 1.0, "FX_EUR_RATE"),
            (F.col("rate_usd").isNotNull() & (F.col("rate_usd") > 0), "FX_USD_RATE"),
            (F.col("rate_gbp").isNotNull() & (F.col("rate_gbp") > 0), "FX_GBP_RATE"),
        ],
    )


def deduplicate_input(frame: DataFrame, business_key: tuple[str, ...]) -> DataFrame:
    eligible = frame.filter(F.size("_quality_rules") == 0)
    already_invalid = frame.filter(F.size("_quality_rules") > 0)
    window = Window.partitionBy(*business_key).orderBy(
        F.col("_ingested_at").desc_nulls_last(),
        F.col("_record_checksum").asc_nulls_last(),
        F.col("_source_bronze_path").asc(),
    )
    ranked = eligible.withColumn("_duplicate_rank", F.row_number().over(window))
    ranked = _append_rule(
        ranked,
        F.col("_duplicate_rank") > 1,
        "DUPLICATE_BUSINESS_KEY",
    )
    return already_invalid.withColumn("_duplicate_rank", F.lit(None).cast("int")).unionByName(ranked)


def split_quality(
    frame: DataFrame,
    entity_name: str,
    business_key: tuple[str, ...],
) -> tuple[DataFrame, DataFrame, DataFrame]:
    rejected_records = frame.filter(F.size("_quality_rules") > 0)
    valid = (
        frame.filter(F.size("_quality_rules") == 0)
        .withColumn("_quality_status", F.lit("PASSED"))
        .drop(
            "_quality_rules",
            "_original_record",
            "_corrupt_record",
            "_duplicate_rank",
            "_amount_format_valid",
            "_timestamp_format_valid",
        )
    )

    mapping_values: list[Column] = []
    for rule_name, reason in QUALITY_REASONS.items():
        mapping_values.extend([F.lit(rule_name), F.lit(reason)])
    reason_map = F.create_map(*mapping_values)
    business_key_value = F.concat_ws("||", *[F.coalesce(F.col(key).cast("string"), F.lit("<null>")) for key in business_key])
    quarantine = (
        rejected_records.withColumn("rule_name", F.explode("_quality_rules"))
        .withColumn("entity_name", F.lit(entity_name))
        .withColumn("business_key", business_key_value)
        .withColumn("rejection_reason", reason_map[F.col("rule_name")])
        .withColumnRenamed("_original_record", "original_record")
        .withColumn(
            "_quarantine_record_id",
            F.sha2(
                F.concat_ws(
                    "||",
                    F.lit(entity_name),
                    F.col("business_key"),
                    F.col("original_record"),
                    F.col("_source_bronze_path"),
                ),
                256,
            ),
        )
        .withColumn(
            "_quarantine_id",
            F.sha2(F.concat_ws("||", "_quarantine_record_id", "rule_name"), 256),
        )
        .select(
            "_quarantine_id",
            "_quarantine_record_id",
            "entity_name",
            "business_key",
            "rule_name",
            "rejection_reason",
            "original_record",
            "_silver_run_id",
            "_silver_processed_at",
            "_source_bronze_path",
        )
    )
    return valid, rejected_records, quarantine


def _initialize_quality(
    frame: DataFrame,
    rules: list[tuple[Column, str]],
) -> DataFrame:
    common_rules = [
        (F.col("_corrupt_record").isNull(), "BRONZE_CORRUPT_RECORD"),
        (F.col("_record_checksum").isNotNull(), "BRONZE_CHECKSUM_REQUIRED"),
    ]
    failures = [
        F.when(~F.coalesce(condition, F.lit(False)), F.lit(rule_name))
        for condition, rule_name in [*common_rules, *rules]
    ]
    return frame.withColumn(
        "_quality_rules",
        F.filter(F.array(*failures), lambda item: item.isNotNull()),
    )


def _with_silver_metadata(
    frame: DataFrame,
    silver_run_id: str,
    processed_at: datetime,
) -> DataFrame:
    original_columns = [column for column in frame.columns if column != "_corrupt_record"]
    return (
        frame.withColumn(
            "_original_record",
            F.to_json(F.struct(*[F.col(column) for column in original_columns])),
        )
        .withColumn("_ingested_at", F.to_timestamp("_ingested_at"))
        .withColumn("_ingestion_date", F.to_date("_ingestion_date"))
        .withColumn("_silver_processed_at", F.lit(processed_at).cast("timestamp"))
        .withColumn("_silver_run_id", F.lit(silver_run_id))
    )


def _add_reference_rule(
    frame: DataFrame,
    reference_frame: DataFrame,
    local_key: str,
    reference_key: str,
    rule_name: str,
) -> DataFrame:
    marker = f"_valid_{reference_key}"
    references = reference_frame.select(F.col(reference_key).alias(marker)).distinct()
    joined = frame.join(F.broadcast(references), frame[local_key] == references[marker], "left")
    return _append_rule(joined, F.col(marker).isNull(), rule_name).drop(marker)


def _append_rule(frame: DataFrame, failed: Column, rule_name: str) -> DataFrame:
    return frame.withColumn(
        "_quality_rules",
        F.when(
            F.coalesce(failed, F.lit(True)),
            F.array_union("_quality_rules", F.array(F.lit(rule_name))),
        ).otherwise(F.col("_quality_rules")),
    )
