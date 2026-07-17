import logging
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_DIR = PROJECT_ROOT / "db"
DATABASE_PATH = DB_DIR / "optimization_lab.duckdb"


def validate_required_csvs() -> None:
    required_files = [
        RAW_DIR / "branches.csv",
        RAW_DIR / "customers.csv",
        RAW_DIR / "accounts.csv",
        RAW_DIR / "transaction_logs.csv",
    ]
    missing_files = [str(path) for path in required_files if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing raw CSV files: {missing_files}")


def setup_database() -> dict:
    validate_required_csvs()
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        connection.execute(
            f"""
            CREATE TABLE branches AS
            SELECT * FROM read_csv_auto('{(RAW_DIR / "branches.csv").as_posix()}');

            CREATE TABLE customers AS
            SELECT * FROM read_csv_auto('{(RAW_DIR / "customers.csv").as_posix()}');

            CREATE TABLE accounts AS
            SELECT * FROM read_csv_auto('{(RAW_DIR / "accounts.csv").as_posix()}');

            CREATE TABLE transaction_logs AS
            SELECT
                log_id,
                transaction_id,
                customer_id,
                account_id,
                branch_id,
                endpoint,
                CAST(status_code AS INTEGER) AS status_code,
                channel,
                transaction_type,
                CAST(response_time_ms AS INTEGER) AS response_time_ms,
                CAST(transaction_amount AS DOUBLE) AS transaction_amount,
                CAST(created_at AS TIMESTAMP) AS created_at
            FROM read_csv_auto('{(RAW_DIR / "transaction_logs.csv").as_posix()}');
            """
        )

        connection.execute(
            """
            CREATE TABLE endpoint_daily_metrics AS
            SELECT
                CAST(created_at AS DATE) AS event_date,
                endpoint,
                COUNT(*) AS total_logs,
                SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) AS error_logs,
                SUM(CASE WHEN status_code = 500 THEN 1 ELSE 0 END) AS server_error_logs,
                AVG(response_time_ms) AS avg_response_time_ms,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_response_time_ms
            FROM transaction_logs
            GROUP BY 1, 2;

            CREATE TABLE channel_transaction_metrics AS
            SELECT
                channel,
                transaction_type,
                COUNT(*) AS total_logs,
                SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) AS error_logs,
                AVG(response_time_ms) AS avg_response_time_ms,
                SUM(transaction_amount) AS net_transaction_amount
            FROM transaction_logs
            GROUP BY 1, 2;

            CREATE TABLE customer_error_metrics AS
            SELECT
                customer_id,
                COUNT(*) AS total_logs,
                SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) AS error_logs,
                SUM(CASE WHEN status_code = 500 THEN 1 ELSE 0 END) AS server_error_logs,
                MAX(created_at) AS last_event_at
            FROM transaction_logs
            GROUP BY 1;
            """
        )

        table_counts = {}
        for table_name in [
            "branches",
            "customers",
            "accounts",
            "transaction_logs",
            "endpoint_daily_metrics",
            "channel_transaction_metrics",
            "customer_error_metrics",
        ]:
            table_counts[table_name] = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

    return {
        "final_status": "PASSED",
        "database_path": str(DATABASE_PATH),
        "table_counts": table_counts,
        "generated_paths": {
            "database": str(DATABASE_PATH),
        },
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    result = setup_database()
    logging.info("DuckDB database created: %s", result["table_counts"])


if __name__ == "__main__":
    main()
