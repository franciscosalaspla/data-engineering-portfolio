from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
OUTPUT_DIR = PROJECT_ROOT / "output"


def _read_silver(dataset_name: str) -> pd.DataFrame:
    path = SILVER_DIR / f"{dataset_name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing Silver dataset: {path}")
    return pd.read_parquet(path)


def _result(check_name: str, failed_rows: int, details: str) -> dict[str, object]:
    return {
        "check_name": check_name,
        "status": "PASSED" if failed_rows == 0 else "FAILED",
        "failed_rows": int(failed_rows),
        "details": details,
    }


def run_quality_checks() -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    customers = _read_silver("silver_customers")
    policies = _read_silver("silver_policies")
    claims = _read_silver("silver_claims")
    payments = _read_silver("silver_payments")

    results = [
        _result(
            "customers_without_null_customer_id",
            customers["customer_id"].isna().sum(),
            "customers must have a non-null customer_id",
        ),
        _result(
            "policies_unique_policy_id",
            policies["policy_id"].duplicated().sum(),
            "policy_id must be unique",
        ),
        _result(
            "claims_non_negative_amount",
            (claims["claim_amount"] < 0).sum(),
            "claim_amount must be greater than or equal to zero",
        ),
        _result(
            "payments_non_negative_amount",
            (payments["payment_amount"] < 0).sum(),
            "payment_amount must be greater than or equal to zero",
        ),
        _result(
            "valid_customer_dates",
            customers[["birth_date", "signup_date"]].isna().any(axis=1).sum(),
            "customer date fields must be parseable",
        ),
        _result(
            "valid_policy_dates",
            policies[["start_date", "end_date"]].isna().any(axis=1).sum(),
            "policy date fields must be parseable",
        ),
        _result(
            "valid_claim_dates",
            claims["claim_date"].isna().sum(),
            "claim_date must be parseable",
        ),
        _result(
            "valid_payment_dates",
            payments["payment_date"].isna().sum(),
            "payment_date must be parseable",
        ),
        _result(
            "claims_reference_existing_policies",
            (~claims["policy_id"].isin(set(policies["policy_id"]))).sum(),
            "claims must reference existing policies",
        ),
        _result(
            "policies_reference_existing_customers",
            (~policies["customer_id"].isin(set(customers["customer_id"]))).sum(),
            "policies must reference existing customers",
        ),
    ]

    results_df = pd.DataFrame(results)
    summary = {
        "final_status": "PASSED" if (results_df["status"] == "PASSED").all() else "FAILED",
        "total_checks": int(len(results_df)),
        "passed_checks": int((results_df["status"] == "PASSED").sum()),
        "failed_checks": int((results_df["status"] == "FAILED").sum()),
        "results": results,
    }

    results_df.to_csv(OUTPUT_DIR / "data_quality_results.csv", index=False)
    with (OUTPUT_DIR / "data_quality_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    return summary


if __name__ == "__main__":
    print(json.dumps(run_quality_checks(), indent=2))
