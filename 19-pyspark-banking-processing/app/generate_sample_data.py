import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

BRANCHES_FILE = RAW_DIR / "finanzas_branches.csv"
CUSTOMERS_FILE = RAW_DIR / "finanzas_customers.csv"
ACCOUNTS_FILE = RAW_DIR / "finanzas_accounts.csv"
TRANSACTIONS_FILE = RAW_DIR / "finanzas_transactions.csv"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict], overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True


def maybe_messy_text(value: str, row_number: int) -> str:
    if row_number % 13 == 0:
        return f"  {value}  "
    if row_number % 17 == 0:
        return value.upper()
    return value


def build_branches() -> list[dict]:
    branches = [
        ("BR001", "Sucursal Centro", "Santiago", "Metropolitana", "active"),
        ("BR002", "Sucursal Providencia", "Santiago", "Metropolitana", "active"),
        ("BR003", "Sucursal Valparaiso", "Valparaiso", "Valparaiso", "active"),
        ("BR004", "Sucursal Concepcion", "Concepcion", "Biobio", "active"),
        ("BR005", "Sucursal La Serena", "La Serena", "Coquimbo", "inactive"),
        ("BR006", "Sucursal Antofagasta", "Antofagasta", "Antofagasta", "active"),
    ]
    rows = []
    for index, (branch_id, name, city, region, status) in enumerate(branches, start=1):
        rows.append(
            {
                "branch_id": branch_id,
                "branch_name": maybe_messy_text(name, index),
                "city": maybe_messy_text(city, index),
                "region": maybe_messy_text(region, index),
                "branch_status": status,
            }
        )

    rows.append(rows[1].copy())
    return rows


def build_customers(row_count: int = 120) -> list[dict]:
    first_names = ["Ana", "Luis", "Camila", "Jorge", "Valentina", "Diego", "Paula"]
    last_names = ["Rojas", "Perez", "Gonzalez", "Silva", "Munoz", "Contreras"]
    cities = ["Santiago", "Valparaiso", "Concepcion", "La Serena", "Antofagasta"]
    segments = ["retail", "premium", "sme", "corporate", "Preferente"]

    rows = []
    for customer_number in range(1, row_count + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        customer_id = f"C{customer_number:05d}"
        row = {
            "customer_id": customer_id,
            "customer_name": maybe_messy_text(f"{first_name} {last_name}", customer_number),
            "email": f"{first_name.lower()}.{last_name.lower()}{customer_number}@example.com",
            "city": maybe_messy_text(random.choice(cities), customer_number),
            "country": "Chile",
            "customer_segment": maybe_messy_text(random.choice(segments), customer_number),
            "customer_status": random.choice(["active", "active", "active", "inactive", "blocked"]),
        }
        if customer_number % 41 == 0:
            row["email"] = ""
        if customer_number % 59 == 0:
            row["customer_segment"] = "  unknown_segment  "
        rows.append(row)

    rows.append(rows[10].copy())
    return rows


def build_accounts(row_count: int = 180) -> list[dict]:
    account_types = ["checking", "savings", "credit", "investment"]
    account_statuses = ["active", "active", "active", "inactive", "frozen"]
    rows = []

    for account_number in range(1, row_count + 1):
        opened_at = datetime(2021, 1, 1) + timedelta(days=random.randint(0, 1100))
        row = {
            "account_id": f"A{account_number:06d}",
            "customer_id": f"C{random.randint(1, 120):05d}",
            "branch_id": f"BR{random.randint(1, 6):03d}",
            "account_type": maybe_messy_text(random.choice(account_types), account_number),
            "open_date": opened_at.strftime("%Y-%m-%d"),
            "balance": round(random.uniform(-50000, 25000000), 2),
            "account_status": random.choice(account_statuses),
        }
        if account_number % 67 == 0:
            row["branch_id"] = ""
        if account_number % 73 == 0:
            row["balance"] = ""
        rows.append(row)

    rows.append(rows[4].copy())
    return rows


def build_transactions(row_count: int = 1200) -> list[dict]:
    transaction_types = ["deposit", "withdrawal", "payment", "transfer", "fee", "ChargeBack"]
    channels = ["mobile_app", "web", "atm", "branch", "POS", "  call_center  "]
    statuses = ["completed", "completed", "completed", "pending", "failed", "REVERSED"]
    currencies = ["CLP", "USD"]
    descriptions = ["salary", "card payment", "atm cash", "wire transfer", "loan payment"]

    rows = []
    base_date = datetime(2024, 1, 1, 9, 0, 0)
    for transaction_number in range(1, row_count + 1):
        amount = round(random.uniform(-900000, 1500000), 2)
        if transaction_number % 97 == 0:
            amount = round(random.uniform(5000000, 12000000), 2)

        transaction_ts = base_date + timedelta(days=random.randint(0, 540), minutes=random.randint(0, 1440))
        row = {
            "transaction_id": f"T{transaction_number:08d}",
            "account_id": f"A{random.randint(1, 180):06d}",
            "transaction_timestamp": transaction_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_type": maybe_messy_text(random.choice(transaction_types), transaction_number),
            "channel": maybe_messy_text(random.choice(channels), transaction_number),
            "amount": amount,
            "currency": random.choice(currencies),
            "status": maybe_messy_text(random.choice(statuses), transaction_number),
            "description": random.choice(descriptions),
        }

        if transaction_number % 89 == 0:
            row["account_id"] = ""
        if transaction_number % 101 == 0:
            row["amount"] = ""
        if transaction_number % 113 == 0:
            row["transaction_timestamp"] = "invalid_date"
        if transaction_number % 127 == 0:
            row["channel"] = "  unknown_channel  "
        rows.append(row)

    rows.append(rows[20].copy())
    rows.append(rows[35].copy())
    return rows


def generate_sample_data(overwrite: bool = False) -> dict:
    random.seed(42)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    files = {
        "branches": (
            BRANCHES_FILE,
            ["branch_id", "branch_name", "city", "region", "branch_status"],
            build_branches(),
        ),
        "customers": (
            CUSTOMERS_FILE,
            [
                "customer_id",
                "customer_name",
                "email",
                "city",
                "country",
                "customer_segment",
                "customer_status",
            ],
            build_customers(),
        ),
        "accounts": (
            ACCOUNTS_FILE,
            [
                "account_id",
                "customer_id",
                "branch_id",
                "account_type",
                "open_date",
                "balance",
                "account_status",
            ],
            build_accounts(),
        ),
        "transactions": (
            TRANSACTIONS_FILE,
            [
                "transaction_id",
                "account_id",
                "transaction_timestamp",
                "transaction_type",
                "channel",
                "amount",
                "currency",
                "status",
                "description",
            ],
            build_transactions(),
        ),
    }

    result = {}
    for dataset_name, (path, fieldnames, rows) in files.items():
        written = write_csv(path, fieldnames, rows, overwrite)
        result[dataset_name] = {
            "path": str(path),
            "rows": len(rows),
            "written": written,
        }

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample banking CSV files.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing sample CSV files.",
    )
    args = parser.parse_args()

    result = generate_sample_data(overwrite=args.overwrite)
    for dataset_name, metadata in result.items():
        action = "created" if metadata["written"] else "kept"
        print(f"{dataset_name}: {action} {metadata['path']} ({metadata['rows']} rows prepared)")


if __name__ == "__main__":
    main()
