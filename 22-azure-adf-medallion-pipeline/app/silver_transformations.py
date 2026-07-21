from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"


def _read_bronze(dataset_name: str) -> pd.DataFrame:
    path = BRONZE_DIR / f"bronze_{dataset_name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing Bronze dataset: {path}")
    df = pd.read_parquet(path)
    df.columns = [column.strip().lower() for column in df.columns]
    return df


def _write_silver(df: pd.DataFrame, dataset_name: str) -> int:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SILVER_DIR / f"{dataset_name}.parquet"
    df.to_parquet(output_path, index=False)
    return len(df)


def _parse_date_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        df[column] = pd.to_datetime(df[column], errors="coerce").dt.date
    return df


def run_silver_transformations() -> dict[str, dict[str, int]]:
    customers = _read_bronze("customers")
    policies = _read_bronze("policies")
    claims = _read_bronze("claims")
    payments = _read_bronze("payments")

    customers = customers.drop_duplicates(subset=["customer_id"]).copy()
    policies = policies.drop_duplicates(subset=["policy_id"]).copy()
    claims = claims.drop_duplicates(subset=["claim_id"]).copy()
    payments = payments.drop_duplicates(subset=["payment_id"]).copy()

    customers = _parse_date_columns(customers, ["birth_date", "signup_date"])
    policies = _parse_date_columns(policies, ["start_date", "end_date"])
    claims = _parse_date_columns(claims, ["claim_date"])
    payments = _parse_date_columns(payments, ["payment_date"])

    customers["risk_score"] = pd.to_numeric(customers["risk_score"], errors="coerce")
    policies["premium_amount"] = pd.to_numeric(policies["premium_amount"], errors="coerce")
    claims["claim_amount"] = pd.to_numeric(claims["claim_amount"], errors="coerce")
    payments["payment_amount"] = pd.to_numeric(payments["payment_amount"], errors="coerce")

    customer_policy_claims = (
        claims.merge(
            policies[
                [
                    "policy_id",
                    "customer_id",
                    "policy_type",
                    "policy_status",
                    "premium_amount",
                    "start_date",
                    "end_date",
                ]
            ],
            on="policy_id",
            how="left",
        )
        .merge(
            customers[["customer_id", "region", "segment", "risk_score"]],
            on="customer_id",
            how="left",
        )
        .copy()
    )

    return {
        "silver_customers": {
            "input_rows": len(customers),
            "output_rows": _write_silver(customers, "silver_customers"),
        },
        "silver_policies": {
            "input_rows": len(policies),
            "output_rows": _write_silver(policies, "silver_policies"),
        },
        "silver_claims": {
            "input_rows": len(claims),
            "output_rows": _write_silver(claims, "silver_claims"),
        },
        "silver_payments": {
            "input_rows": len(payments),
            "output_rows": _write_silver(payments, "silver_payments"),
        },
        "silver_customer_policy_claims": {
            "input_rows": len(claims),
            "output_rows": _write_silver(customer_policy_claims, "silver_customer_policy_claims"),
        },
    }


if __name__ == "__main__":
    print(run_silver_transformations())
