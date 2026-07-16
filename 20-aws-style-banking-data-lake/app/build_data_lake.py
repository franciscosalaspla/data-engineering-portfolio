import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_LAKE_DIR = PROJECT_ROOT / "data_lake"
LANDING_DIR = DATA_LAKE_DIR / "landing"
BRONZE_DIR = DATA_LAKE_DIR / "bronze"
SILVER_DIR = DATA_LAKE_DIR / "silver"
GOLD_DIR = DATA_LAKE_DIR / "gold"
OUTPUT_DIR = PROJECT_ROOT / "output"
COST_ESTIMATION_FILE = OUTPUT_DIR / "cost_estimation.json"

REQUIRED_LANDING_FILES = {
    "branches": LANDING_DIR / "branches.csv",
    "customers": LANDING_DIR / "customers.csv",
    "accounts": LANDING_DIR / "accounts.csv",
    "transactions": LANDING_DIR / "transactions.csv",
}

TRANSACTION_TYPE_MAP = {
    "deposit": "deposit",
    "dep": "deposit",
    "withdrawal": "withdrawal",
    "wd": "withdrawal",
    "transfer": "transfer",
    "xfer": "transfer",
    "payment": "payment",
    "card_payment": "payment",
    "fee": "fee",
}

CHANNEL_MAP = {
    "mobile": "mobile",
    "mobile_app": "mobile",
    "web": "web",
    "atm": "atm",
    "branch": "branch",
    "call_center": "call_center",
    "unknown": "unknown",
}

STATUS_MAP = {
    "completed": "completed",
    "success": "completed",
    "succeeded": "completed",
    "failed": "failed",
    "declined": "failed",
    "reversed": "reversed",
    "pending": "pending",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clear_generated_children(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for child in directory.iterdir():
        if child.name == ".gitkeep":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_key(value: object) -> str:
    return normalize_text(value).upper()


def load_landing_csvs() -> dict[str, pd.DataFrame]:
    missing_files = [path for path in REQUIRED_LANDING_FILES.values() if not path.exists()]
    if missing_files:
        missing_names = ", ".join(path.name for path in missing_files)
        raise FileNotFoundError(f"Missing landing files: {missing_names}")

    return {
        name: pd.read_csv(path, dtype=str, keep_default_na=False)
        for name, path in REQUIRED_LANDING_FILES.items()
    }


def write_single_parquet(dataframe: pd.DataFrame, dataset_dir: Path, file_name: str) -> str:
    dataset_dir.mkdir(parents=True, exist_ok=True)
    path = dataset_dir / file_name
    dataframe.to_parquet(path, index=False, engine="pyarrow", compression="snappy")
    return str(path)


def write_partitioned_parquet(dataframe: pd.DataFrame, dataset_dir: Path) -> str:
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    dataframe.to_parquet(
        dataset_dir,
        index=False,
        engine="pyarrow",
        compression="snappy",
        partition_cols=["year", "month"],
    )
    return str(dataset_dir)


def build_bronze_layer(landing_frames: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], dict, dict]:
    clear_generated_children(BRONZE_DIR)
    bronze_frames = {}
    bronze_counts = {}
    bronze_paths = {}
    loaded_at = utc_now()

    for dataset_name, dataframe in landing_frames.items():
        bronze_df = dataframe.copy()
        bronze_df.columns = [column.strip().lower() for column in bronze_df.columns]
        bronze_df = bronze_df.map(lambda value: value.strip() if isinstance(value, str) else value)
        bronze_df["source_file"] = f"{dataset_name}.csv"
        bronze_df["bronze_loaded_at"] = loaded_at
        bronze_df["source_system"] = "local_s3_landing_simulation"

        dataset_dir = BRONZE_DIR / dataset_name
        bronze_paths[dataset_name] = write_single_parquet(
            bronze_df, dataset_dir, f"{dataset_name}.parquet"
        )
        bronze_counts[dataset_name] = len(bronze_df)
        bronze_frames[dataset_name] = bronze_df

    return bronze_frames, bronze_counts, bronze_paths


def clean_branches(branches: pd.DataFrame) -> pd.DataFrame:
    result = branches.copy()
    result["branch_id"] = result["branch_id"].map(normalize_key)
    result["branch_name"] = result["branch_name"].map(normalize_text)
    result["city"] = result["city"].map(normalize_text)
    result["region"] = result["region"].map(normalize_text)
    result = result[result["branch_id"] != ""]
    return result.drop_duplicates(subset=["branch_id"], keep="first")


def clean_customers(customers: pd.DataFrame, valid_branch_ids: set[str]) -> pd.DataFrame:
    result = customers.copy()
    result["customer_id"] = result["customer_id"].map(normalize_key)
    result["first_name"] = result["first_name"].map(normalize_text)
    result["last_name"] = result["last_name"].map(normalize_text)
    result["customer_name"] = (result["first_name"] + " " + result["last_name"]).str.strip()
    result["segment"] = result["segment"].map(lambda value: normalize_text(value).lower())
    result["preferred_branch_id"] = result["preferred_branch_id"].map(normalize_key)
    result["email"] = result["email"].map(lambda value: normalize_text(value).lower())
    result["signup_date"] = pd.to_datetime(result["signup_date"], errors="coerce")

    result = result[result["customer_id"] != ""]
    result = result[result["preferred_branch_id"].isin(valid_branch_ids)]
    result = result.dropna(subset=["signup_date"])
    return result.drop_duplicates(subset=["customer_id"], keep="first")


def clean_accounts(accounts: pd.DataFrame, valid_customer_ids: set[str]) -> pd.DataFrame:
    result = accounts.copy()
    result["account_id"] = result["account_id"].map(normalize_key)
    result["customer_id"] = result["customer_id"].map(normalize_key)
    result["account_type"] = result["account_type"].map(lambda value: normalize_text(value).lower())
    result["account_status"] = result["account_status"].map(lambda value: normalize_text(value).lower())
    result["opened_date"] = pd.to_datetime(result["opened_date"], errors="coerce")

    result = result[result["account_id"] != ""]
    result = result[result["customer_id"].isin(valid_customer_ids)]
    result = result.dropna(subset=["opened_date"])
    return result.drop_duplicates(subset=["account_id"], keep="first")


def normalize_transactions(transactions: pd.DataFrame, valid_account_ids: set[str]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    result = transactions.copy()
    result["transaction_id"] = result["transaction_id"].map(normalize_key)
    result["account_id"] = result["account_id"].map(normalize_key)
    result["branch_id"] = result["branch_id"].map(normalize_key)
    result["transaction_type_raw"] = result["transaction_type"].map(normalize_text)
    result["transaction_type"] = (
        result["transaction_type_raw"].str.strip().str.lower().map(TRANSACTION_TYPE_MAP).fillna("unknown")
    )
    result["channel"] = (
        result["channel"].map(normalize_text).str.lower().map(CHANNEL_MAP).fillna("unknown")
    )
    result["status"] = (
        result["status"].map(normalize_text).str.lower().map(STATUS_MAP).fillna("unknown")
    )
    result["merchant_category"] = result["merchant_category"].map(lambda value: normalize_text(value).lower())
    result["currency"] = result["currency"].map(normalize_key)
    result["transaction_date"] = pd.to_datetime(result["transaction_date"], errors="coerce")
    result["amount"] = pd.to_numeric(result["amount"], errors="coerce")

    duplicate_transaction_rows = int(result.duplicated(subset=["transaction_id"], keep="first").sum())
    result = result.drop_duplicates(subset=["transaction_id"], keep="first")

    result["invalid_reason"] = ""
    result.loc[result["transaction_id"] == "", "invalid_reason"] = "missing_transaction_id"
    result.loc[result["account_id"] == "", "invalid_reason"] = "missing_account_id"
    result.loc[result["transaction_date"].isna(), "invalid_reason"] = "invalid_transaction_date"
    result.loc[result["amount"].isna(), "invalid_reason"] = "missing_amount"
    result.loc[~result["account_id"].isin(valid_account_ids), "invalid_reason"] = "invalid_account_reference"
    result.loc[result["transaction_type"] == "unknown", "invalid_reason"] = "unknown_transaction_type"

    quarantine = result[result["invalid_reason"] != ""].copy()
    valid = result[result["invalid_reason"] == ""].copy()

    valid["year"] = valid["transaction_date"].dt.year.astype("int16")
    valid["month"] = valid["transaction_date"].dt.month.astype("int8")
    valid["amount_abs"] = valid["amount"].abs()
    valid["risk_flag"] = (
        (valid["amount_abs"] >= 8000)
        | (valid["status"].isin(["failed", "reversed"]))
        | (valid["channel"] == "unknown")
    )

    checks = {
        "duplicate_transaction_rows_removed": duplicate_transaction_rows,
        "missing_transaction_id_rows": int((transactions["transaction_id"].map(normalize_key) == "").sum()),
        "invalid_transaction_date_rows": int(result["transaction_date"].isna().sum()),
        "missing_amount_rows": int(result["amount"].isna().sum()),
        "invalid_account_reference_rows": int((~result["account_id"].isin(valid_account_ids)).sum()),
        "unknown_transaction_type_rows": int((result["transaction_type"] == "unknown").sum()),
        "critical_invalid_rows_quarantined": len(quarantine),
    }
    return valid, quarantine, checks


def build_silver_layer(bronze_frames: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], dict, dict, dict]:
    clear_generated_children(SILVER_DIR)

    branches = clean_branches(bronze_frames["branches"])
    customers = clean_customers(bronze_frames["customers"], set(branches["branch_id"]))
    accounts = clean_accounts(bronze_frames["accounts"], set(customers["customer_id"]))
    transactions, quarantine, transaction_checks = normalize_transactions(
        bronze_frames["transactions"], set(accounts["account_id"])
    )

    enriched = transactions.merge(
        accounts[["account_id", "customer_id", "account_type", "account_status", "opened_date"]],
        on="account_id",
        how="left",
    )
    enriched = enriched.merge(
        customers[["customer_id", "customer_name", "segment", "preferred_branch_id", "email"]],
        on="customer_id",
        how="left",
    )
    enriched = enriched.merge(
        branches[["branch_id", "branch_name", "city", "region"]],
        on="branch_id",
        how="left",
    )
    enriched = enriched.rename(columns={"segment": "customer_segment"})

    enriched_columns = [
        "transaction_id",
        "account_id",
        "customer_id",
        "customer_name",
        "customer_segment",
        "account_type",
        "account_status",
        "transaction_date",
        "year",
        "month",
        "transaction_type",
        "channel",
        "amount",
        "amount_abs",
        "currency",
        "status",
        "risk_flag",
        "merchant_category",
        "branch_id",
        "branch_name",
        "city",
        "region",
    ]
    enriched = enriched[enriched_columns].sort_values(["transaction_date", "transaction_id"])

    silver_paths = {
        "branches": write_single_parquet(branches, SILVER_DIR / "branches", "branches.parquet"),
        "customers": write_single_parquet(customers, SILVER_DIR / "customers", "customers.parquet"),
        "accounts": write_single_parquet(accounts, SILVER_DIR / "accounts", "accounts.parquet"),
        "enriched_transactions": write_partitioned_parquet(
            enriched, SILVER_DIR / "enriched_transactions"
        ),
        "quarantined_transactions": write_single_parquet(
            quarantine, SILVER_DIR / "quarantined_transactions", "quarantined_transactions.parquet"
        ),
    }

    silver_counts = {
        "branches": len(branches),
        "customers": len(customers),
        "accounts": len(accounts),
        "enriched_transactions": len(enriched),
        "quarantined_transactions": len(quarantine),
    }
    silver_frames = {
        "branches": branches,
        "customers": customers,
        "accounts": accounts,
        "enriched_transactions": enriched,
        "quarantined_transactions": quarantine,
    }
    return silver_frames, silver_counts, silver_paths, transaction_checks


def build_gold_layer(silver_frames: dict[str, pd.DataFrame]) -> tuple[dict, dict]:
    clear_generated_children(GOLD_DIR)
    transactions = silver_frames["enriched_transactions"].copy()

    channel_metrics = (
        transactions.groupby("channel", as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
            average_amount=("amount", "mean"),
            failed_or_reversed_count=("status", lambda values: values.isin(["failed", "reversed"]).sum()),
            risk_transaction_count=("risk_flag", "sum"),
        )
        .sort_values("transaction_count", ascending=False)
    )

    transaction_type_metrics = (
        transactions.groupby("transaction_type", as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
            average_amount=("amount", "mean"),
            risk_transaction_count=("risk_flag", "sum"),
        )
        .sort_values("transaction_count", ascending=False)
    )

    monthly_amount = (
        transactions.groupby(["year", "month"], as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
            total_amount_abs=("amount_abs", "sum"),
            risk_transaction_count=("risk_flag", "sum"),
        )
        .sort_values(["year", "month"])
    )

    top_customers = (
        transactions.groupby(["customer_id", "customer_name", "customer_segment"], as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_transaction_amount=("amount_abs", "sum"),
            risk_transaction_count=("risk_flag", "sum"),
        )
        .sort_values("total_transaction_amount", ascending=False)
        .head(20)
    )

    branch_volume = (
        transactions.groupby(["branch_id", "branch_name", "city", "region"], as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_transaction_amount=("amount_abs", "sum"),
            risk_transaction_count=("risk_flag", "sum"),
        )
        .sort_values("total_transaction_amount", ascending=False)
    )

    gold_frames = {
        "channel_metrics": channel_metrics,
        "transaction_type_metrics": transaction_type_metrics,
        "monthly_amount": monthly_amount,
        "top_customers": top_customers,
        "branch_volume": branch_volume,
    }
    gold_paths = {
        name: write_single_parquet(frame, GOLD_DIR / name, f"{name}.parquet")
        for name, frame in gold_frames.items()
    }
    gold_counts = {name: len(frame) for name, frame in gold_frames.items()}
    return gold_counts, gold_paths


def directory_size_bytes(directory: Path, pattern: str) -> int:
    return sum(path.stat().st_size for path in directory.rglob(pattern) if path.is_file())


def write_cost_estimation() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    landing_csv_bytes = directory_size_bytes(LANDING_DIR, "*.csv")
    silver_gold_parquet_bytes = directory_size_bytes(SILVER_DIR, "*.parquet") + directory_size_bytes(
        GOLD_DIR, "*.parquet"
    )
    bronze_parquet_bytes = directory_size_bytes(BRONZE_DIR, "*.parquet")

    if landing_csv_bytes > 0:
        scan_reduction_percent = round(
            max(0, 1 - (silver_gold_parquet_bytes / landing_csv_bytes)) * 100, 2
        )
    else:
        scan_reduction_percent = 0

    estimation = {
        "estimation_type": "local_simulation_not_aws_invoice",
        "generated_at": utc_now(),
        "landing_csv_bytes": landing_csv_bytes,
        "bronze_parquet_bytes": bronze_parquet_bytes,
        "silver_gold_parquet_bytes": silver_gold_parquet_bytes,
        "approximate_scan_reduction_percent": scan_reduction_percent,
        "notes": [
            "Athena charges are based on data scanned, so columnar Parquet and partition pruning reduce scanned bytes conceptually.",
            "This local dataset is intentionally small; Parquet metadata overhead can be larger than CSV for tiny files.",
            "No AWS services were called, no credentials were used, and this is not a real AWS bill.",
        ],
        "cost_controls_simulated": [
            "Parquet output with snappy compression",
            "Silver transactions partitioned by year and month",
            "Athena-like SQL avoids SELECT * in final queries",
            "Generated data remains local and ignored by Git",
        ],
    }
    COST_ESTIMATION_FILE.write_text(json.dumps(estimation, indent=4), encoding="utf-8")
    return estimation


def build_data_lake() -> dict:
    landing_frames = load_landing_csvs()
    input_counts = {name: len(frame) for name, frame in landing_frames.items()}

    bronze_frames, bronze_counts, bronze_paths = build_bronze_layer(landing_frames)
    silver_frames, silver_counts, silver_paths, data_quality_checks = build_silver_layer(bronze_frames)
    gold_counts, gold_paths = build_gold_layer(silver_frames)
    cost_estimation = write_cost_estimation()

    return {
        "input_counts": input_counts,
        "bronze_counts": bronze_counts,
        "silver_counts": silver_counts,
        "gold_counts": gold_counts,
        "data_quality_checks": data_quality_checks,
        "generated_paths": {
            "bronze": bronze_paths,
            "silver": silver_paths,
            "gold": gold_paths,
            "cost_estimation": str(COST_ESTIMATION_FILE),
        },
        "cost_estimation": cost_estimation,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    result = build_data_lake()
    logging.info("Data lake built successfully")
    logging.info("Counts: %s", {key: result[key] for key in ["input_counts", "silver_counts", "gold_counts"]})


if __name__ == "__main__":
    main()
