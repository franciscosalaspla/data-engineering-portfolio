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
        ("BR001", "Sucursal Centro", "Santiago", "Av. Principal 100", "true"),
        ("BR002", "Sucursal Providencia", "Santiago", "Av. Providencia 2200", "true"),
        ("BR003", "Sucursal Valparaiso", "Valparaiso", "Calle Puerto 455", "true"),
        ("BR004", "Sucursal Concepcion", "Concepcion", "Av. Bio Bio 810", "true"),
        ("BR005", "Sucursal La Serena", "La Serena", "Ruta Norte 300", "false"),
        ("BR006", "Sucursal Antofagasta", "Antofagasta", "Av. Minera 710", "true"),
    ]
    rows = []
    for index, (branch_id, name, city, address, is_active) in enumerate(branches, start=1):
        rows.append(
            {
                "branch_id": branch_id,
                "branch_name": maybe_messy_text(name, index),
                "city": maybe_messy_text(city, index),
                "address": maybe_messy_text(address, index),
                "phone": f"+5622300{index:04d}",
                "manager_id": f"E{index:05d}",
                "opened_date": f"201{index}-01-15",
                "is_active": is_active,
            }
        )

    rows.append(rows[1].copy())
    return rows


def build_customers(row_count: int = 120) -> list[dict]:
    first_names = ["Ana", "Luis", "Camila", "Jorge", "Valentina", "Diego", "Paula"]
    last_names = ["Rojas", "Perez", "Gonzalez", "Silva", "Munoz", "Contreras"]
    cities = ["Santiago", "Valparaiso", "Concepcion", "La Serena", "Antofagasta"]

    rows = []
    for customer_number in range(1, row_count + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        customer_id = f"C{customer_number:05d}"
        registered_at = datetime(2021, 1, 1) + timedelta(days=random.randint(0, 1200))
        born_at = datetime(1965, 1, 1) + timedelta(days=random.randint(0, 12000))
        row = {
            "customer_id": customer_id,
            "first_name": maybe_messy_text(first_name, customer_number),
            "last_name": maybe_messy_text(last_name, customer_number),
            "dni": f"{random.randint(8_000_000, 25_000_000)}-{random.randint(0, 9)}",
            "email": f"{first_name.lower()}.{last_name.lower()}{customer_number}@example.com",
            "phone": f"+569{random.randint(10000000, 99999999)}",
            "address": f"Calle {random.randint(100, 9999)}",
            "city": maybe_messy_text(random.choice(cities), customer_number),
            "birth_date": born_at.strftime("%Y-%m-%d"),
            "registration_date": registered_at.strftime("%Y-%m-%d"),
            "credit_score": random.randint(300, 850),
            "is_vip": random.choice(["true", "false", "1", "0", "yes", "no", ""]),
            "preferred_branch_id": f"BR{random.randint(1, 6):03d}",
        }
        if customer_number % 41 == 0:
            row["email"] = ""
        if customer_number % 59 == 0:
            row["is_vip"] = ""
        if customer_number % 61 == 0:
            row["preferred_branch_id"] = ""
        rows.append(row)

    rows.append(rows[10].copy())
    return rows


def build_accounts(row_count: int = 180) -> list[dict]:
    account_types = ["AT001", "AT002", "AT003", "AT004"]
    account_statuses = ["active", "active", "active", "inactive", "frozen"]
    rows = []

    for account_number in range(1, row_count + 1):
        opened_at = datetime(2021, 1, 1) + timedelta(days=random.randint(0, 1100))
        row = {
            "account_id": f"A{account_number:06d}",
            "customer_id": f"C{random.randint(1, 120):05d}",
            "account_type_id": maybe_messy_text(random.choice(account_types), account_number),
            "account_number": f"00{random.randint(10_000_000, 99_999_999)}",
            "cbu": f"{random.randint(10**21, 10**22 - 1)}",
            "balance": round(random.uniform(-50000, 25000000), 2),
            "opened_date": opened_at.strftime("%Y-%m-%d"),
            "status": random.choice(account_statuses),
            "last_activity_date": (opened_at + timedelta(days=random.randint(0, 900))).strftime(
                "%Y-%m-%d"
            ),
        }
        if account_number % 67 == 0:
            row["account_type_id"] = ""
        if account_number % 73 == 0:
            row["balance"] = ""
        rows.append(row)

    rows.append(rows[4].copy())
    return rows


def build_transactions(row_count: int = 1200) -> list[dict]:
    transaction_types = ["deposit", "withdrawal", "payment", "transfer", "fee", "ChargeBack"]
    channels = ["mobile_app", "web", "atm", "branch", "POS", "  call_center  "]
    statuses = ["completed", "completed", "completed", "pending", "failed", "REVERSED"]
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
            "transaction_type": maybe_messy_text(random.choice(transaction_types), transaction_number),
            "amount": amount,
            "balance_after": round(random.uniform(-100000, 30000000), 2),
            "transaction_date": transaction_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "description": random.choice(descriptions),
            "reference_number": f"REF{transaction_number:09d}",
            "channel": maybe_messy_text(random.choice(channels), transaction_number),
            "status": maybe_messy_text(random.choice(statuses), transaction_number),
        }

        if transaction_number % 89 == 0:
            row["account_id"] = ""
        if transaction_number % 101 == 0:
            row["amount"] = ""
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
            [
                "branch_id",
                "branch_name",
                "city",
                "address",
                "phone",
                "manager_id",
                "opened_date",
                "is_active",
            ],
            build_branches(),
        ),
        "customers": (
            CUSTOMERS_FILE,
            [
                "customer_id",
                "first_name",
                "last_name",
                "dni",
                "email",
                "phone",
                "address",
                "city",
                "birth_date",
                "registration_date",
                "credit_score",
                "is_vip",
                "preferred_branch_id",
            ],
            build_customers(),
        ),
        "accounts": (
            ACCOUNTS_FILE,
            [
                "account_id",
                "customer_id",
                "account_type_id",
                "account_number",
                "cbu",
                "balance",
                "opened_date",
                "status",
                "last_activity_date",
            ],
            build_accounts(),
        ),
        "transactions": (
            TRANSACTIONS_FILE,
            [
                "transaction_id",
                "account_id",
                "transaction_type",
                "amount",
                "balance_after",
                "transaction_date",
                "description",
                "reference_number",
                "channel",
                "status",
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
