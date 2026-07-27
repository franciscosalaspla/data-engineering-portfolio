"""Build the six dimensions, reconciled EUR fact and explainable quarantine."""

from __future__ import annotations

from datetime import datetime

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType

from .keys import surrogate_key, with_content_checksum


AMOUNT_TYPE = DecimalType(18, 2)
FX_RATE_TYPE = DecimalType(18, 8)
QUALITY_REASONS = {
    "DUPLICATE_TRANSACTION_ID": "More than one Silver row exists for transaction_id.",
    "ACCOUNT_REFERENCE_MISSING": "The transaction account does not exist in Silver accounts.",
    "CUSTOMER_REFERENCE_MISSING": "The account customer does not exist in Silver customers.",
    "FX_RATE_MISSING": "No positive FX rate exists for the transaction currency and UTC date.",
}


def build_dimensions(
    customers: DataFrame,
    accounts: DataFrame,
    transactions: DataFrame,
    run_id: str,
    processed_at: datetime,
) -> dict[str, DataFrame]:
    """Create Type 1 dimensions using stable keys and content-only checksums."""
    dates = (
        transactions.select(
            F.to_date("transaction_timestamp").alias("full_date"),
            "_silver_run_id",
        )
        .filter(F.col("full_date").isNotNull())
        .groupBy("full_date")
        .agg(F.min("_silver_run_id").alias("_silver_run_id"))
        .withColumn("date_key", F.date_format("full_date", "yyyyMMdd").cast("long"))
        .withColumn("calendar_year", F.year("full_date"))
        .withColumn("calendar_quarter", F.quarter("full_date"))
        .withColumn("calendar_month", F.month("full_date"))
        .withColumn("day_of_month", F.dayofmonth("full_date"))
        .withColumn("iso_week", F.weekofyear("full_date"))
        .withColumn("day_of_week", F.date_format("full_date", "EEEE"))
    )
    dates = _finish_dimension(
        dates,
        run_id,
        processed_at,
        ["full_date", "date_key", "calendar_year", "calendar_quarter", "calendar_month", "day_of_month", "iso_week", "day_of_week"],
        "silver_transactions",
    )

    customer_columns = [
        "customer_id",
        "country_code",
        "segment",
        "onboarding_date",
        "status",
        "risk_rating",
        "_silver_run_id",
    ]
    dim_customer = customers.select(*customer_columns).withColumn(
        "customer_key", surrogate_key("customer", "customer_id")
    )
    dim_customer = _finish_dimension(
        dim_customer,
        run_id,
        processed_at,
        ["customer_id", "customer_key", "country_code", "segment", "onboarding_date", "status", "risk_rating"],
        "silver_customers",
    )

    account_columns = [
        "account_id",
        "customer_id",
        "account_type",
        "base_currency",
        "opened_date",
        "status",
        "_silver_run_id",
    ]
    dim_account = (
        accounts.select(*account_columns)
        .withColumn("account_key", surrogate_key("account", "account_id"))
        .withColumn("customer_key", surrogate_key("customer", "customer_id"))
    )
    dim_account = _finish_dimension(
        dim_account,
        run_id,
        processed_at,
        ["account_id", "account_key", "customer_id", "customer_key", "account_type", "base_currency", "opened_date", "status"],
        "silver_accounts",
    )

    merchant_window = Window.partitionBy("merchant_id").orderBy(
        F.col("transaction_timestamp").desc(), F.col("transaction_id").asc()
    )
    dim_merchant = (
        transactions.select(
            "merchant_id",
            "merchant_name",
            "merchant_category",
            "transaction_timestamp",
            "transaction_id",
            "_silver_run_id",
        )
        .withColumn("_rank", F.row_number().over(merchant_window))
        .filter(F.col("_rank") == 1)
        .drop("_rank", "transaction_timestamp", "transaction_id")
        .withColumn("merchant_key", surrogate_key("merchant", "merchant_id"))
    )
    dim_merchant = _finish_dimension(
        dim_merchant,
        run_id,
        processed_at,
        ["merchant_id", "merchant_key", "merchant_name", "merchant_category"],
        "silver_transactions",
    )

    dim_channel = (
        transactions.select(F.col("channel").alias("channel_code"), "_silver_run_id")
        .groupBy("channel_code")
        .agg(F.min("_silver_run_id").alias("_silver_run_id"))
        .withColumn("channel_key", surrogate_key("channel", "channel_code"))
    )
    dim_channel = _finish_dimension(
        dim_channel,
        run_id,
        processed_at,
        ["channel_code", "channel_key"],
        "silver_transactions",
    )

    dim_currency = (
        transactions.select(F.col("currency").alias("currency_code"), "_silver_run_id")
        .groupBy("currency_code")
        .agg(F.min("_silver_run_id").alias("_silver_run_id"))
        .withColumn("currency_key", surrogate_key("currency", "currency_code"))
    )
    dim_currency = _finish_dimension(
        dim_currency,
        run_id,
        processed_at,
        ["currency_code", "currency_key"],
        "silver_transactions",
    )

    return {
        "dim_date": dates,
        "dim_customer": dim_customer,
        "dim_account": dim_account,
        "dim_merchant": dim_merchant,
        "dim_channel": dim_channel,
        "dim_currency": dim_currency,
    }


def build_fact_transactions(
    transactions: DataFrame,
    accounts: DataFrame,
    customers: DataFrame,
    fx_rates: DataFrame,
    run_id: str,
    processed_at: datetime,
) -> tuple[DataFrame, DataFrame, DataFrame]:
    """Return valid fact rows, rejected source records and one quarantine row per rule."""
    duplicate_window = Window.partitionBy("transaction_id").orderBy(
        F.col("_silver_processed_at").desc_nulls_last(),
        F.col("_record_checksum").asc_nulls_last(),
    )
    source = (
        transactions.withColumn("_duplicate_rank", F.row_number().over(duplicate_window))
        .withColumn("_original_record", F.to_json(F.struct(*[F.col(name) for name in transactions.columns])))
        .alias("tx")
    )
    account_lookup = accounts.select(
        F.col("account_id").alias("lookup_account_id"),
        F.col("customer_id").alias("lookup_customer_id"),
    )
    customer_lookup = customers.select(F.col("customer_id").alias("valid_customer_id"))
    fx_long = _fx_rates_long(fx_rates)

    joined = (
        source.join(
            F.broadcast(account_lookup),
            F.col("tx.account_id") == F.col("lookup_account_id"),
            "left",
        )
        .join(
            F.broadcast(customer_lookup),
            F.col("lookup_customer_id") == F.col("valid_customer_id"),
            "left",
        )
        .withColumn("transaction_date", F.to_date("tx.transaction_timestamp"))
        .join(
            F.broadcast(fx_long),
            (F.col("transaction_date") == F.col("fx_rate_date"))
            & (F.col("tx.currency") == F.col("fx_currency")),
            "left",
        )
    )
    failures = [
        F.when(F.col("_duplicate_rank") > 1, F.lit("DUPLICATE_TRANSACTION_ID")),
        F.when(F.col("lookup_account_id").isNull(), F.lit("ACCOUNT_REFERENCE_MISSING")),
        F.when(F.col("valid_customer_id").isNull(), F.lit("CUSTOMER_REFERENCE_MISSING")),
        F.when(F.col("fx_rate_to_eur").isNull() | (F.col("fx_rate_to_eur") <= 0), F.lit("FX_RATE_MISSING")),
    ]
    quality = joined.withColumn(
        "_quality_rules",
        F.filter(F.array(*failures), lambda item: item.isNotNull()),
    )
    rejected = quality.filter(F.size("_quality_rules") > 0)
    valid = quality.filter(F.size("_quality_rules") == 0)

    fact = (
        valid.withColumn("fact_transaction_key", surrogate_key("transaction", "transaction_id"))
        .withColumn("date_key", F.date_format("transaction_date", "yyyyMMdd").cast("long"))
        .withColumn("customer_key", surrogate_key("customer", "lookup_customer_id"))
        .withColumn("account_key", surrogate_key("account", "account_id"))
        .withColumn("merchant_key", surrogate_key("merchant", "merchant_id"))
        .withColumn("channel_key", surrogate_key("channel", "channel"))
        .withColumn("currency_key", surrogate_key("currency", "currency"))
        .withColumn("amount_original", F.col("amount").cast(AMOUNT_TYPE))
        .withColumn("fx_rate_to_eur", F.col("fx_rate_to_eur").cast(FX_RATE_TYPE))
        .withColumn(
            "amount_eur",
            (F.col("amount_original") / F.col("fx_rate_to_eur")).cast(AMOUNT_TYPE),
        )
        .withColumn("_gold_processed_at", F.lit(processed_at).cast("timestamp"))
        .withColumn("_gold_run_id", F.lit(run_id))
        .withColumnRenamed("_silver_run_id", "_source_silver_run_id")
        .withColumn("_source_silver_path", F.lit("silver_transactions"))
        .select(
            "fact_transaction_key",
            "transaction_id",
            "date_key",
            "customer_key",
            "account_key",
            "merchant_key",
            "channel_key",
            "currency_key",
            "account_id",
            F.col("lookup_customer_id").alias("customer_id"),
            "merchant_id",
            F.col("channel").alias("channel_code"),
            F.col("currency").alias("currency_code"),
            "transaction_timestamp",
            "transaction_date",
            "transaction_type",
            "status",
            "source_batch_id",
            "amount_original",
            "fx_rate_to_eur",
            "fx_rate_date",
            "amount_eur",
            "_record_checksum",
            "_source_silver_run_id",
            "_source_silver_path",
            "_gold_processed_at",
            "_gold_run_id",
        )
    )
    fact = with_content_checksum(
        fact,
        [
            "transaction_id", "date_key", "customer_key", "account_key", "merchant_key",
            "channel_key", "currency_key", "transaction_timestamp", "transaction_type", "status",
            "source_batch_id", "amount_original", "fx_rate_to_eur", "fx_rate_date", "amount_eur",
        ],
    )

    reason_values = []
    for rule, reason in QUALITY_REASONS.items():
        reason_values.extend([F.lit(rule), F.lit(reason)])
    reason_map = F.create_map(*reason_values)
    quarantine = (
        rejected.withColumn("rule_name", F.explode("_quality_rules"))
        .withColumn("rejection_reason", reason_map[F.col("rule_name")])
        .withColumn("entity_name", F.lit("fact_transactions"))
        .withColumn("business_key", F.coalesce(F.col("transaction_id"), F.lit("<null>")))
        .withColumnRenamed("_original_record", "original_record")
        .withColumn("_gold_run_id", F.lit(run_id))
        .withColumn("_gold_processed_at", F.lit(processed_at).cast("timestamp"))
        .withColumn(
            "_quarantine_id",
            F.sha2(F.concat_ws("||", "entity_name", "business_key", "rule_name", "original_record"), 256),
        )
        .select(
            "_quarantine_id", "entity_name", "business_key", "rule_name", "rejection_reason",
            "original_record", "_gold_run_id", "_gold_processed_at",
            F.col("tx._silver_run_id").alias("_source_silver_run_id"),
        )
    )
    return fact, rejected, quarantine


def _fx_rates_long(fx_rates: DataFrame) -> DataFrame:
    frames = []
    for currency in ("EUR", "USD", "GBP"):
        frames.append(
            fx_rates.select(
                F.col("effective_date").alias("fx_rate_date"),
                F.lit(currency).alias("fx_currency"),
                F.col(f"rate_{currency.lower()}").cast(FX_RATE_TYPE).alias("fx_rate_to_eur"),
            )
        )
    result = frames[0]
    for frame in frames[1:]:
        result = result.unionByName(frame)
    return result


def _finish_dimension(
    frame: DataFrame,
    run_id: str,
    processed_at: datetime,
    checksum_columns: list[str],
    source_silver_path: str,
) -> DataFrame:
    return with_content_checksum(
        frame.withColumnRenamed("_silver_run_id", "_source_silver_run_id")
        .withColumn("_source_silver_path", F.lit(source_silver_path))
        .withColumn("_gold_processed_at", F.lit(processed_at).cast("timestamp"))
        .withColumn("_gold_run_id", F.lit(run_id)),
        checksum_columns,
    )
