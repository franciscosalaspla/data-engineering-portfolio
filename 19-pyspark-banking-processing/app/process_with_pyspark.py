import shutil
from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ANALYTICS_DIR = PROJECT_ROOT / "data" / "analytics"

SPARK_APP_NAME = "pyspark_banking_processing"


TRANSACTIONS_SCHEMA = StructType(
    [
        StructField("transaction_id", StringType(), True),
        StructField("account_id", StringType(), True),
        StructField("transaction_type", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("balance_after", DoubleType(), True),
        StructField("transaction_date", StringType(), True),
        StructField("description", StringType(), True),
        StructField("reference_number", StringType(), True),
        StructField("channel", StringType(), True),
        StructField("status", StringType(), True),
    ]
)

ACCOUNTS_SCHEMA = StructType(
    [
        StructField("account_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("account_type_id", StringType(), True),
        StructField("account_number", StringType(), True),
        StructField("cbu", StringType(), True),
        StructField("balance", DoubleType(), True),
        StructField("opened_date", StringType(), True),
        StructField("status", StringType(), True),
        StructField("last_activity_date", StringType(), True),
    ]
)

CUSTOMERS_SCHEMA = StructType(
    [
        StructField("customer_id", StringType(), True),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("dni", StringType(), True),
        StructField("email", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("address", StringType(), True),
        StructField("city", StringType(), True),
        StructField("birth_date", StringType(), True),
        StructField("registration_date", StringType(), True),
        StructField("credit_score", DoubleType(), True),
        StructField("is_vip", StringType(), True),
        StructField("preferred_branch_id", StringType(), True),
    ]
)

BRANCHES_SCHEMA = StructType(
    [
        StructField("branch_id", StringType(), True),
        StructField("branch_name", StringType(), True),
        StructField("city", StringType(), True),
        StructField("address", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("manager_id", StringType(), True),
        StructField("opened_date", StringType(), True),
        StructField("is_active", StringType(), True),
    ]
)


def create_spark_session() -> SparkSession:
    spark = (
        SparkSession.builder.appName(SPARK_APP_NAME)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_csv_with_schema(spark: SparkSession, path: Path, schema: StructType) -> DataFrame:
    return (
        spark.read.option("header", True)
        .option("mode", "PERMISSIVE")
        .schema(schema)
        .csv(str(path))
    )


def clean_text(column_name: str) -> F.Column:
    return F.lower(F.trim(F.col(column_name)))


def null_if_empty(column_name: str) -> F.Column:
    return F.when(F.trim(F.col(column_name)) == "", None).otherwise(F.trim(F.col(column_name)))


def remove_output_path(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def parquet_exists(path: Path) -> bool:
    return path.exists() and any(path.rglob("*.parquet"))


def count_duplicates(df: DataFrame, subset: list[str]) -> int:
    total_rows = df.count()
    unique_rows = df.dropDuplicates(subset).count()
    return total_rows - unique_rows


def clean_transactions(df: DataFrame) -> DataFrame:
    parsed_timestamp = F.coalesce(
        F.to_timestamp("transaction_date_raw", "yyyy-MM-dd HH:mm:ss"),
        F.to_timestamp("transaction_date_raw", "yyyy-MM-dd"),
        F.to_timestamp("transaction_date_raw", "yyyy-MM-dd'T'HH:mm:ss"),
        F.to_timestamp("transaction_date_raw", "dd/MM/yyyy HH:mm:ss"),
        F.to_timestamp("transaction_date_raw", "dd/MM/yyyy"),
        F.to_timestamp("transaction_date_raw", "MM/dd/yyyy HH:mm:ss"),
        F.to_timestamp("transaction_date_raw", "MM/dd/yyyy"),
        F.to_timestamp("transaction_date_raw"),
    )

    return (
        df.select(
            null_if_empty("transaction_id").alias("transaction_id"),
            null_if_empty("account_id").alias("account_id"),
            null_if_empty("transaction_date").alias("transaction_date_raw"),
            clean_text("transaction_type").alias("transaction_type"),
            clean_text("channel").alias("channel"),
            F.col("amount").cast(DoubleType()).alias("amount"),
            F.col("balance_after").cast(DoubleType()).alias("balance_after"),
            clean_text("status").alias("status"),
            F.trim(F.col("description")).alias("description"),
            null_if_empty("reference_number").alias("reference_number"),
        )
        .withColumn("transaction_ts", parsed_timestamp)
        .withColumn("transaction_date", F.to_date(F.col("transaction_ts")))
        .filter(F.col("transaction_id").isNotNull())
        .filter(F.col("account_id").isNotNull())
        .filter(F.col("amount").isNotNull())
        .filter(F.col("transaction_date").isNotNull())
        .dropDuplicates(["transaction_id"])
        .withColumn("amount_abs", F.abs(F.col("amount")))
        .withColumn("year", F.year(F.col("transaction_date")))
        .withColumn("month", F.month(F.col("transaction_date")))
        .withColumn(
            "risk_flag",
            F.when(F.col("amount_abs") >= F.lit(5_000_000), F.lit(True))
            .when(F.col("status").isin("failed", "reversed"), F.lit(True))
            .when(F.col("channel").isin("unknown_channel"), F.lit(True))
            .otherwise(F.lit(False)),
        )
        .select(
            "transaction_id",
            "account_id",
            "transaction_ts",
            "transaction_date",
            "year",
            "month",
            "transaction_type",
            "channel",
            "amount",
            "amount_abs",
            "balance_after",
            "status",
            "risk_flag",
            "description",
            "reference_number",
        )
    )


def clean_accounts(df: DataFrame) -> DataFrame:
    return (
        df.select(
            null_if_empty("account_id").alias("account_id"),
            null_if_empty("customer_id").alias("customer_id"),
            null_if_empty("account_type_id").alias("account_type_id"),
            null_if_empty("account_number").alias("account_number"),
            null_if_empty("cbu").alias("cbu"),
            F.to_date("opened_date", "yyyy-MM-dd").alias("opened_date"),
            F.col("balance").cast(DoubleType()).alias("balance"),
            clean_text("status").alias("account_status"),
            F.to_date("last_activity_date", "yyyy-MM-dd").alias("last_activity_date"),
        )
        .filter(F.col("account_id").isNotNull())
        .filter(F.col("customer_id").isNotNull())
        .dropDuplicates(["account_id"])
        .fillna({"account_type_id": "unknown", "account_status": "unknown"})
    )


def clean_customers(df: DataFrame) -> DataFrame:
    is_vip_normalized = clean_text("is_vip")

    return (
        df.select(
            null_if_empty("customer_id").alias("customer_id"),
            F.trim(F.concat_ws(" ", null_if_empty("first_name"), null_if_empty("last_name"))).alias(
                "customer_name"
            ),
            clean_text("email").alias("email"),
            clean_text("city").alias("customer_city"),
            F.col("credit_score").cast(DoubleType()).alias("credit_score"),
            is_vip_normalized.alias("is_vip"),
            null_if_empty("preferred_branch_id").alias("preferred_branch_id"),
            F.when(is_vip_normalized.isin("true", "1", "yes"), F.lit("vip"))
            .when(is_vip_normalized.isin("false", "0", "no"), F.lit("standard"))
            .otherwise(F.lit("unknown"))
            .alias("customer_segment"),
        )
        .filter(F.col("customer_id").isNotNull())
        .dropDuplicates(["customer_id"])
        .fillna(
            {
                "customer_name": "Unknown Customer",
                "email": "unknown",
                "customer_city": "unknown",
                "customer_segment": "unknown",
            }
        )
    )


def clean_branches(df: DataFrame) -> DataFrame:
    return (
        df.select(
            null_if_empty("branch_id").alias("branch_id"),
            F.trim(F.col("branch_name")).alias("branch_name"),
            clean_text("city").alias("branch_city"),
            F.trim(F.col("address")).alias("branch_address"),
            clean_text("is_active").alias("is_active"),
        )
        .filter(F.col("branch_id").isNotNull())
        .dropDuplicates(["branch_id"])
        .fillna(
            {
                "branch_name": "Unknown Branch",
                "branch_city": "unknown",
                "branch_address": "unknown",
                "is_active": "unknown",
            }
        )
    )


def build_enriched_transactions(
    transactions: DataFrame,
    accounts: DataFrame,
    customers: DataFrame,
    branches: DataFrame,
) -> DataFrame:
    accounts_selected = accounts.select(
        "account_id",
        "customer_id",
        "account_type_id",
        "account_status",
        "balance",
    )
    customers_selected = customers.select(
        "customer_id",
        "customer_name",
        "customer_segment",
        "customer_city",
        "preferred_branch_id",
    )
    branches_selected = branches.select(
        "branch_id",
        "branch_name",
        "branch_city",
        "is_active",
    )

    account_window = (
        Window.partitionBy("account_id")
        .orderBy(F.col("transaction_ts"), F.col("transaction_id"))
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    return (
        transactions.join(accounts_selected, on="account_id", how="left")
        .join(customers_selected, on="customer_id", how="left")
        .withColumn("branch_id", F.col("preferred_branch_id"))
        .join(branches_selected, on="branch_id", how="left")
        .withColumn("account_running_amount", F.sum("amount").over(account_window))
        .select(
            "transaction_id",
            "transaction_date",
            "year",
            "month",
            "account_id",
            "customer_id",
            "customer_name",
            "customer_segment",
            "branch_id",
            "branch_name",
            "branch_city",
            "account_type_id",
            "transaction_type",
            "channel",
            "amount",
            "amount_abs",
            "balance_after",
            "status",
            "risk_flag",
            "account_running_amount",
        )
    )


def build_monthly_branch_metrics(enriched: DataFrame) -> DataFrame:
    return (
        enriched.groupBy("year", "month", "branch_id", "branch_name", "branch_city")
        .agg(
            F.count("*").alias("transaction_count"),
            F.round(F.sum("amount"), 2).alias("net_amount"),
            F.round(F.sum("amount_abs"), 2).alias("total_amount_abs"),
            F.round(F.avg("amount_abs"), 2).alias("avg_amount_abs"),
            F.sum(F.when(F.col("risk_flag"), 1).otherwise(0)).alias("risk_transaction_count"),
        )
        .filter(F.col("branch_id").isNotNull())
        .orderBy("year", "month", F.desc("total_amount_abs"))
    )


def build_customer_ranking(enriched: DataFrame) -> DataFrame:
    customer_metrics = (
        enriched.groupBy("customer_id", "customer_name", "customer_segment")
        .agg(
            F.count("*").alias("transaction_count"),
            F.round(F.sum("amount_abs"), 2).alias("total_amount_abs"),
            F.round(F.avg("amount_abs"), 2).alias("avg_amount_abs"),
            F.sum(F.when(F.col("risk_flag"), 1).otherwise(0)).alias("risk_transaction_count"),
        )
        .filter(F.col("customer_id").isNotNull())
    )

    ranking_window = Window.partitionBy("customer_segment").orderBy(
        F.desc("total_amount_abs"),
        F.desc("transaction_count"),
        F.asc("customer_id"),
    )

    return customer_metrics.withColumn(
        "customer_rank", F.dense_rank().over(ranking_window)
    ).orderBy(
        "customer_segment",
        "customer_rank",
    )


def collect_main_metrics(
    transactions_clean: DataFrame,
    enriched: DataFrame,
    monthly_branch_metrics: DataFrame,
    customer_ranking: DataFrame,
) -> dict[str, Any]:
    transaction_metrics = transactions_clean.agg(
        F.round(F.sum("amount"), 2).alias("net_amount"),
        F.round(F.sum("amount_abs"), 2).alias("total_amount_abs"),
        F.round(F.avg("amount_abs"), 2).alias("avg_amount_abs"),
        F.sum(F.when(F.col("risk_flag"), 1).otherwise(0)).alias("risk_transaction_count"),
    ).first()

    channel_metrics = (
        transactions_clean.groupBy("channel")
        .agg(
            F.count("*").alias("transaction_count"),
            F.round(F.avg("amount_abs"), 2).alias("avg_amount_abs"),
        )
        .orderBy(F.desc("transaction_count"))
        .limit(5)
        .collect()
    )

    transaction_type_metrics = (
        transactions_clean.groupBy("transaction_type")
        .agg(F.count("*").alias("transaction_count"))
        .orderBy(F.desc("transaction_count"))
        .collect()
    )

    top_customer = customer_ranking.limit(1).collect()
    top_branch = monthly_branch_metrics.orderBy(F.desc("total_amount_abs")).limit(1).collect()

    return {
        "transaction_totals": transaction_metrics.asDict() if transaction_metrics else {},
        "top_channels_by_transaction_count": [row.asDict() for row in channel_metrics],
        "transactions_by_type": [row.asDict() for row in transaction_type_metrics],
        "top_customer_by_amount_abs": top_customer[0].asDict() if top_customer else {},
        "top_monthly_branch_by_amount_abs": top_branch[0].asDict() if top_branch else {},
        "enriched_rows_without_customer": enriched.filter(F.col("customer_id").isNull()).count(),
        "enriched_rows_without_branch": enriched.filter(F.col("branch_id").isNull()).count(),
    }


def write_outputs(
    transactions_clean: DataFrame,
    accounts_clean: DataFrame,
    customers_clean: DataFrame,
    enriched_transactions: DataFrame,
    monthly_branch_metrics: DataFrame,
    customer_ranking: DataFrame,
) -> dict[str, str]:
    output_paths = {
        "transactions_clean": PROCESSED_DIR / "transactions_clean",
        "accounts_clean": PROCESSED_DIR / "accounts_clean",
        "customers_clean": PROCESSED_DIR / "customers_clean",
        "enriched_transactions": ANALYTICS_DIR / "enriched_transactions",
        "monthly_branch_metrics": ANALYTICS_DIR / "monthly_branch_metrics",
        "customer_transaction_ranking": ANALYTICS_DIR / "customer_transaction_ranking",
    }

    for path in output_paths.values():
        remove_output_path(path)

    transactions_clean.write.mode("overwrite").parquet(str(output_paths["transactions_clean"]))
    accounts_clean.write.mode("overwrite").parquet(str(output_paths["accounts_clean"]))
    customers_clean.write.mode("overwrite").parquet(str(output_paths["customers_clean"]))
    enriched_transactions.write.mode("overwrite").partitionBy("year", "month").parquet(
        str(output_paths["enriched_transactions"])
    )
    monthly_branch_metrics.write.mode("overwrite").parquet(str(output_paths["monthly_branch_metrics"]))
    customer_ranking.write.mode("overwrite").parquet(str(output_paths["customer_transaction_ranking"]))

    return {name: str(path) for name, path in output_paths.items()}


def process_banking_data() -> dict[str, Any]:
    spark = create_spark_session()

    try:
        raw_transactions = read_csv_with_schema(
            spark,
            RAW_DIR / "finanzas_transactions.csv",
            TRANSACTIONS_SCHEMA,
        )
        raw_accounts = read_csv_with_schema(
            spark,
            RAW_DIR / "finanzas_accounts.csv",
            ACCOUNTS_SCHEMA,
        )
        raw_customers = read_csv_with_schema(
            spark,
            RAW_DIR / "finanzas_customers.csv",
            CUSTOMERS_SCHEMA,
        )
        raw_branches = read_csv_with_schema(
            spark,
            RAW_DIR / "finanzas_branches.csv",
            BRANCHES_SCHEMA,
        )

        input_counts = {
            "transactions": raw_transactions.count(),
            "accounts": raw_accounts.count(),
            "customers": raw_customers.count(),
            "branches": raw_branches.count(),
        }

        parsed_transaction_date = F.coalesce(
            F.to_timestamp("transaction_date", "yyyy-MM-dd HH:mm:ss"),
            F.to_timestamp("transaction_date", "yyyy-MM-dd"),
            F.to_timestamp("transaction_date", "yyyy-MM-dd'T'HH:mm:ss"),
            F.to_timestamp("transaction_date", "dd/MM/yyyy HH:mm:ss"),
            F.to_timestamp("transaction_date", "dd/MM/yyyy"),
            F.to_timestamp("transaction_date", "MM/dd/yyyy HH:mm:ss"),
            F.to_timestamp("transaction_date", "MM/dd/yyyy"),
            F.to_timestamp("transaction_date"),
        )

        validations = {
            "input_row_counts": input_counts,
            "raw_duplicate_transactions_removed": count_duplicates(
                raw_transactions,
                ["transaction_id"],
            ),
            "raw_duplicate_accounts_removed": count_duplicates(raw_accounts, ["account_id"]),
            "raw_duplicate_customers_removed": count_duplicates(raw_customers, ["customer_id"]),
            "raw_duplicate_branches_removed": count_duplicates(raw_branches, ["branch_id"]),
            "transactions_with_null_account_id": raw_transactions.filter(
                null_if_empty("account_id").isNull()
            ).count(),
            "transactions_with_null_amount": raw_transactions.filter(F.col("amount").isNull()).count(),
            "transactions_with_invalid_date": raw_transactions.withColumn(
                "parsed_transaction_ts",
                parsed_transaction_date,
            )
            .filter(F.col("parsed_transaction_ts").isNull())
            .count(),
        }

        transactions_clean = clean_transactions(raw_transactions)
        accounts_clean = clean_accounts(raw_accounts)
        customers_clean = clean_customers(raw_customers)
        branches_clean = clean_branches(raw_branches)

        enriched_transactions = build_enriched_transactions(
            transactions_clean,
            accounts_clean,
            customers_clean,
            branches_clean,
        )
        monthly_branch_metrics = build_monthly_branch_metrics(enriched_transactions)
        customer_ranking = build_customer_ranking(enriched_transactions)

        output_counts = {
            "transactions_clean": transactions_clean.count(),
            "accounts_clean": accounts_clean.count(),
            "customers_clean": customers_clean.count(),
            "branches_clean": branches_clean.count(),
            "enriched_transactions": enriched_transactions.count(),
            "monthly_branch_metrics": monthly_branch_metrics.count(),
            "customer_transaction_ranking": customer_ranking.count(),
        }

        validations.update(
            {
                "clean_row_counts": {
                    "transactions_clean": output_counts["transactions_clean"],
                    "accounts_clean": output_counts["accounts_clean"],
                    "customers_clean": output_counts["customers_clean"],
                    "branches_clean": output_counts["branches_clean"],
                },
                "risk_flag_transactions": transactions_clean.filter(F.col("risk_flag")).count(),
            }
        )

        generated_paths = write_outputs(
            transactions_clean,
            accounts_clean,
            customers_clean,
            enriched_transactions,
            monthly_branch_metrics,
            customer_ranking,
        )

        parquet_validations = {
            name: parquet_exists(Path(path)) for name, path in generated_paths.items()
        }
        validations["parquet_outputs_exist"] = parquet_validations

        main_metrics = collect_main_metrics(
            transactions_clean,
            enriched_transactions,
            monthly_branch_metrics,
            customer_ranking,
        )

        return {
            "spark_app_name": SPARK_APP_NAME,
            "input_counts": input_counts,
            "output_counts": output_counts,
            "generated_paths": generated_paths,
            "main_metrics": main_metrics,
            "validations": validations,
        }
    finally:
        spark.stop()


if __name__ == "__main__":
    result = process_banking_data()
    print(result)
