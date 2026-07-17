import logging
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RANDOM_SEED = 21021
LOG_COUNT = 150_000
BRANCH_COUNT = 12
CUSTOMER_COUNT = 5_000
ACCOUNT_COUNT = 7_500


def reset_raw_csvs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for csv_file in RAW_DIR.glob("*.csv"):
        csv_file.unlink()


def build_branches() -> pd.DataFrame:
    cities = [
        "Santiago",
        "Providencia",
        "Las Condes",
        "Valparaiso",
        "Concepcion",
        "Antofagasta",
        "La Serena",
        "Temuco",
        "Rancagua",
        "Puerto Montt",
        "Iquique",
        "Vina del Mar",
    ]
    rows = []
    for index in range(BRANCH_COUNT):
        branch_id = f"BR{index + 1:03d}"
        rows.append(
            {
                "branch_id": branch_id,
                "branch_name": f"Branch {cities[index]}",
                "city": cities[index],
                "region": "Metropolitana" if index < 3 else "Regional",
            }
        )
    return pd.DataFrame(rows)


def build_customers(branches: pd.DataFrame) -> pd.DataFrame:
    segments = ["standard", "premium", "business", "private"]
    segment_weights = [0.62, 0.23, 0.12, 0.03]
    branch_ids = branches["branch_id"].tolist()
    rows = []

    for index in range(CUSTOMER_COUNT):
        customer_id = f"C{index + 1:06d}"
        rows.append(
            {
                "customer_id": customer_id,
                "customer_name": f"Customer {index + 1:06d}",
                "customer_segment": random.choices(segments, weights=segment_weights, k=1)[0],
                "branch_id": random.choice(branch_ids),
                "created_at": (
                    datetime(2020, 1, 1) + timedelta(days=random.randint(0, 2000))
                ).date().isoformat(),
            }
        )
    return pd.DataFrame(rows)


def build_accounts(customers: pd.DataFrame) -> pd.DataFrame:
    customer_ids = customers["customer_id"].tolist()
    account_types = ["checking", "savings", "credit_card", "business"]
    rows = []

    for index in range(ACCOUNT_COUNT):
        account_id = f"A{index + 1:07d}"
        rows.append(
            {
                "account_id": account_id,
                "customer_id": random.choice(customer_ids),
                "account_type": random.choices(account_types, weights=[0.48, 0.32, 0.15, 0.05], k=1)[0],
                "opened_at": (
                    datetime(2020, 1, 1) + timedelta(days=random.randint(0, 2200))
                ).date().isoformat(),
                "account_status": random.choices(["active", "inactive"], weights=[0.96, 0.04], k=1)[0],
            }
        )
    return pd.DataFrame(rows)


def amount_for_type(transaction_type: str) -> float:
    base_amount = round(random.uniform(5.0, 2_500.0), 2)
    if transaction_type in {"withdrawal", "payment", "card_payment", "fee"}:
        return -base_amount
    if transaction_type == "transfer":
        return round(random.uniform(-2_000.0, 2_000.0), 2)
    return base_amount


def build_transaction_logs(customers: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    customer_to_accounts: dict[str, list[str]] = {}
    for row in accounts[["customer_id", "account_id"]].itertuples(index=False):
        customer_to_accounts.setdefault(row.customer_id, []).append(row.account_id)

    customer_to_branch = dict(zip(customers["customer_id"], customers["branch_id"]))
    customer_ids = customers["customer_id"].tolist()
    hot_customers = set(customer_ids[:150])
    customer_weights = [9 if customer_id in hot_customers else 1 for customer_id in customer_ids]

    endpoints = [
        "/api/balance",
        "/api/transactions",
        "/api/transfer",
        "/api/payment",
        "/api/card-payment",
        "/api/deposit",
        "/api/atm-withdrawal",
        "/api/wire-transfer",
        "/api/international-transfer",
        "/api/account-alerts",
    ]
    endpoint_weights = [28, 24, 16, 12, 8, 5, 3, 2, 1, 1]
    status_codes = [200, 400, 404, 500]
    status_weights = [91, 4, 3, 2]
    channels = ["mobile", "web", "atm", "branch"]
    channel_weights = [55, 28, 11, 6]
    transaction_types = ["deposit", "withdrawal", "transfer", "payment", "card_payment", "fee"]
    transaction_type_weights = [14, 18, 26, 19, 18, 5]
    start_datetime = datetime(2025, 1, 1, 0, 0, 0)
    total_minutes = int((datetime(2026, 6, 30, 23, 59, 59) - start_datetime).total_seconds() // 60)

    rows = []
    for index in range(LOG_COUNT):
        customer_id = random.choices(customer_ids, weights=customer_weights, k=1)[0]
        customer_accounts = customer_to_accounts.get(customer_id)
        if not customer_accounts:
            customer_id = random.choice(list(customer_to_accounts))
            customer_accounts = customer_to_accounts[customer_id]

        endpoint = random.choices(endpoints, weights=endpoint_weights, k=1)[0]
        status_code = random.choices(status_codes, weights=status_weights, k=1)[0]
        channel = random.choices(channels, weights=channel_weights, k=1)[0]
        transaction_type = random.choices(
            transaction_types, weights=transaction_type_weights, k=1
        )[0]
        response_base = {
            "/api/balance": 80,
            "/api/transactions": 140,
            "/api/transfer": 260,
            "/api/payment": 220,
            "/api/card-payment": 190,
            "/api/deposit": 160,
            "/api/atm-withdrawal": 210,
            "/api/wire-transfer": 520,
            "/api/international-transfer": 760,
            "/api/account-alerts": 120,
        }[endpoint]
        error_penalty = 180 if status_code >= 400 else 0
        response_time_ms = max(12, int(random.gauss(response_base + error_penalty, 45)))
        created_at = start_datetime + timedelta(minutes=random.randint(0, total_minutes))

        rows.append(
            {
                "log_id": f"L{index + 1:09d}",
                "transaction_id": f"T{index + 1:09d}",
                "customer_id": customer_id,
                "account_id": random.choice(customer_accounts),
                "branch_id": customer_to_branch[customer_id],
                "endpoint": endpoint,
                "status_code": status_code,
                "channel": channel,
                "transaction_type": transaction_type,
                "response_time_ms": response_time_ms,
                "transaction_amount": amount_for_type(transaction_type),
                "created_at": created_at.isoformat(sep=" "),
            }
        )

    return pd.DataFrame(rows)


def generate_banking_logs() -> dict:
    random.seed(RANDOM_SEED)
    reset_raw_csvs()

    branches = build_branches()
    customers = build_customers(branches)
    accounts = build_accounts(customers)
    transaction_logs = build_transaction_logs(customers, accounts)

    datasets = {
        "branches": branches,
        "customers": customers,
        "accounts": accounts,
        "transaction_logs": transaction_logs,
    }

    generated_paths = {}
    row_counts = {}
    for dataset_name, dataframe in datasets.items():
        path = RAW_DIR / f"{dataset_name}.csv"
        dataframe.to_csv(path, index=False)
        generated_paths[dataset_name] = str(path)
        row_counts[dataset_name] = int(len(dataframe))

    return {
        "final_status": "PASSED",
        "random_seed": RANDOM_SEED,
        "row_counts": row_counts,
        "generated_paths": generated_paths,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    result = generate_banking_logs()
    logging.info("Generated banking CSV files: %s", result["row_counts"])


if __name__ == "__main__":
    main()
