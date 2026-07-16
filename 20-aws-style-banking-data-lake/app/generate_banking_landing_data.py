import csv
import logging
import random
from datetime import date, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LANDING_DIR = PROJECT_ROOT / "data_lake" / "landing"
RANDOM_SEED = 20260720


def reset_landing_csvs() -> None:
    LANDING_DIR.mkdir(parents=True, exist_ok=True)
    for path in LANDING_DIR.glob("*.csv"):
        path.unlink()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows provided for {path.name}")

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def random_date(start: date, days: int) -> str:
    return (start + timedelta(days=random.randint(0, days))).isoformat()


def build_branches() -> list[dict]:
    cities = [
        ("BR001", "Santiago Centro", "Santiago", "Metropolitana"),
        ("BR002", "Providencia", "Santiago", "Metropolitana"),
        ("BR003", "Valparaiso Puerto", "Valparaiso", "Valparaiso"),
        ("BR004", "Concepcion Norte", "Concepcion", "Biobio"),
        ("BR005", "La Serena", "La Serena", "Coquimbo"),
        ("BR006", "Antofagasta", "Antofagasta", "Antofagasta"),
        ("BR007", "Temuco", "Temuco", "Araucania"),
        ("BR008", "Puerto Montt", "Puerto Montt", "Los Lagos"),
    ]
    return [
        {
            "branch_id": branch_id,
            "branch_name": branch_name,
            "city": city,
            "region": region,
        }
        for branch_id, branch_name, city, region in cities
    ]


def build_customers(branches: list[dict], total_customers: int = 180) -> list[dict]:
    first_names = [
        "Sofia",
        "Mateo",
        "Valentina",
        "Agustin",
        "Isidora",
        "Benjamin",
        "Camila",
        "Lucas",
        "Martina",
        "Tomas",
    ]
    last_names = [
        "Gonzalez",
        "Munoz",
        "Rojas",
        "Diaz",
        "Perez",
        "Soto",
        "Contreras",
        "Silva",
        "Martinez",
        "Sepulveda",
    ]
    segments = ["mass", "affluent", "sme", "private"]
    customers = []
    for index in range(1, total_customers + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        customer_id = f"C{index:05d}"
        customers.append(
            {
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "segment": random.choice(segments),
                "signup_date": random_date(date(2021, 1, 1), 1100),
                "preferred_branch_id": random.choice(branches)["branch_id"],
                "email": f"{first_name}.{last_name}.{index}@examplebank.local".lower(),
            }
        )

    customers.append({**customers[5], "email": "duplicate.customer@examplebank.local"})
    customers.append({**customers[20], "customer_id": "", "email": ""})
    return customers


def build_accounts(customers: list[dict], total_accounts: int = 240) -> list[dict]:
    valid_customer_ids = [row["customer_id"] for row in customers if row["customer_id"]]
    accounts = []
    for index in range(1, total_accounts + 1):
        accounts.append(
            {
                "account_id": f"A{index:06d}",
                "customer_id": random.choice(valid_customer_ids),
                "account_type": random.choice(["checking", "savings", "credit_card"]),
                "opened_date": random_date(date(2021, 1, 1), 1250),
                "account_status": random.choice(["active", "active", "active", "inactive"]),
            }
        )

    accounts.append({**accounts[10]})
    accounts.append(
        {
            "account_id": "A999999",
            "customer_id": "C99999",
            "account_type": "checking",
            "opened_date": "2026-02-31",
            "account_status": "active",
        }
    )
    return accounts


def build_transactions(
    accounts: list[dict], branches: list[dict], total_transactions: int = 1250
) -> list[dict]:
    valid_account_ids = [row["account_id"] for row in accounts if row["account_id"] != "A999999"]
    transaction_types = [
        "deposit",
        " Deposit ",
        "DEP",
        "withdrawal",
        "WD",
        "transfer",
        "xfer",
        "payment",
        "card_payment",
        "fee",
        "unknown_type",
    ]
    channels = ["mobile", "mobile_app", "web", "atm", "branch", "call_center", "unknown"]
    statuses = ["completed", "success", "failed", "declined", "reversed", "pending"]
    merchant_categories = ["groceries", "utilities", "travel", "salary", "loan", "services"]

    transactions = []
    for index in range(1, total_transactions + 1):
        amount = round(random.uniform(-2500, 6500), 2)
        if random.random() < 0.04:
            amount = round(random.uniform(8000, 18000), 2)
        transactions.append(
            {
                "transaction_id": f"T{index:07d}",
                "account_id": random.choice(valid_account_ids),
                "transaction_date": random_date(date(2025, 1, 1), 455),
                "transaction_type": random.choice(transaction_types),
                "channel": random.choice(channels),
                "amount": amount,
                "currency": "CLP",
                "status": random.choice(statuses),
                "merchant_category": random.choice(merchant_categories),
                "branch_id": random.choice(branches)["branch_id"],
            }
        )

    messy_rows = [
        {**transactions[25]},
        {**transactions[100], "transaction_id": transactions[100]["transaction_id"]},
        {
            **transactions[150],
            "transaction_id": "T_BAD_DATE",
            "transaction_date": "2026-02-31",
        },
        {
            **transactions[175],
            "transaction_id": "T_NULL_AMOUNT",
            "amount": "",
        },
        {
            **transactions[210],
            "transaction_id": "T_BAD_ACCOUNT",
            "account_id": "A000000",
        },
        {
            **transactions[240],
            "transaction_id": "T_BAD_TYPE",
            "transaction_type": "not_a_real_type",
        },
        {
            **transactions[275],
            "transaction_id": "",
            "amount": "12000.00",
        },
    ]
    transactions.extend(messy_rows)
    return transactions


def generate_landing_data() -> dict:
    random.seed(RANDOM_SEED)
    reset_landing_csvs()

    branches = build_branches()
    customers = build_customers(branches)
    accounts = build_accounts(customers)
    transactions = build_transactions(accounts, branches)

    datasets = {
        "branches": branches,
        "customers": customers,
        "accounts": accounts,
        "transactions": transactions,
    }
    generated_paths = {}
    counts = {}
    for dataset_name, rows in datasets.items():
        path = LANDING_DIR / f"{dataset_name}.csv"
        write_csv(path, rows)
        generated_paths[dataset_name] = str(path)
        counts[dataset_name] = len(rows)

    return {
        "landing_counts": counts,
        "generated_paths": generated_paths,
        "messy_data_profile": {
            "duplicates": "customer, account and transaction duplicates are intentionally generated",
            "nulls": "blank customer_id, transaction_id and amount values are included",
            "invalid_dates": "invalid transaction and account dates are included",
            "inconsistent_types": "transaction_type and channel include inconsistent labels",
        },
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    result = generate_landing_data()
    logging.info("Landing banking data generated: %s", result["landing_counts"])


if __name__ == "__main__":
    main()
