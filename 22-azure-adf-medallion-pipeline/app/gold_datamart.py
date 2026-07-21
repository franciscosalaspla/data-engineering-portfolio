from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"


def _read_silver(dataset_name: str) -> pd.DataFrame:
    path = SILVER_DIR / f"{dataset_name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing Silver dataset: {path}")
    return pd.read_parquet(path)


def _write_gold(df: pd.DataFrame, dataset_name: str) -> int:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GOLD_DIR / f"{dataset_name}.parquet"
    df.to_parquet(output_path, index=False)
    return len(df)


def build_gold_datamarts() -> dict[str, dict[str, int]]:
    customers = _read_silver("silver_customers")
    policies = _read_silver("silver_policies")
    claims = _read_silver("silver_claims")
    payments = _read_silver("silver_payments")

    policy_metrics = (
        policies.groupby("customer_id", as_index=False)
        .agg(
            policy_count=("policy_id", "nunique"),
            active_policy_count=("policy_status", lambda values: (values == "active").sum()),
            total_premium_amount=("premium_amount", "sum"),
        )
    )
    claim_metrics = (
        claims.merge(policies[["policy_id", "customer_id"]], on="policy_id", how="left")
        .groupby("customer_id", as_index=False)
        .agg(
            claim_count=("claim_id", "nunique"),
            total_claim_amount=("claim_amount", "sum"),
            avg_claim_amount=("claim_amount", "mean"),
        )
    )
    payment_metrics = (
        payments.merge(policies[["policy_id", "customer_id"]], on="policy_id", how="left")
        .groupby("customer_id", as_index=False)
        .agg(
            payment_count=("payment_id", "nunique"),
            total_payment_amount=("payment_amount", "sum"),
            failed_payment_count=("payment_status", lambda values: (values == "failed").sum()),
            late_payment_count=("payment_status", lambda values: (values == "late").sum()),
        )
    )

    customer_360 = (
        customers[["customer_id", "region", "segment", "risk_score"]]
        .merge(policy_metrics, on="customer_id", how="left")
        .merge(claim_metrics, on="customer_id", how="left")
        .merge(payment_metrics, on="customer_id", how="left")
        .fillna(
            {
                "policy_count": 0,
                "active_policy_count": 0,
                "total_premium_amount": 0,
                "claim_count": 0,
                "total_claim_amount": 0,
                "avg_claim_amount": 0,
                "payment_count": 0,
                "total_payment_amount": 0,
                "failed_payment_count": 0,
                "late_payment_count": 0,
            }
        )
    )

    claims_for_summary = claims.copy()
    claims_for_summary["claim_month"] = pd.to_datetime(claims_for_summary["claim_date"]).dt.to_period("M").astype(str)
    claims_monthly_summary = (
        claims_for_summary.groupby(["claim_month", "claim_status", "claim_type"], as_index=False)
        .agg(
            claims_count=("claim_id", "nunique"),
            total_claim_amount=("claim_amount", "sum"),
            avg_claim_amount=("claim_amount", "mean"),
        )
        .sort_values(["claim_month", "claim_status", "claim_type"])
    )

    claims_by_policy = (
        claims.groupby("policy_id", as_index=False)
        .agg(
            claim_count=("claim_id", "nunique"),
            total_claim_amount=("claim_amount", "sum"),
        )
    )
    payments_by_policy = (
        payments.groupby("policy_id", as_index=False)
        .agg(
            payment_count=("payment_id", "nunique"),
            total_payment_amount=("payment_amount", "sum"),
            failed_payment_count=("payment_status", lambda values: (values == "failed").sum()),
        )
    )
    policy_performance = (
        policies.merge(claims_by_policy, on="policy_id", how="left")
        .merge(payments_by_policy, on="policy_id", how="left")
        .fillna(
            {
                "claim_count": 0,
                "total_claim_amount": 0,
                "payment_count": 0,
                "total_payment_amount": 0,
                "failed_payment_count": 0,
            }
        )
    )
    policy_performance["loss_ratio"] = (
        policy_performance["total_claim_amount"] / policy_performance["premium_amount"]
    ).round(4)

    payment_risk_summary = (
        payments.merge(policies[["policy_id", "policy_type", "customer_id"]], on="policy_id", how="left")
        .groupby(["policy_type", "payment_status"], as_index=False)
        .agg(
            payment_count=("payment_id", "nunique"),
            total_payment_amount=("payment_amount", "sum"),
            affected_customers=("customer_id", "nunique"),
        )
        .sort_values(["policy_type", "payment_status"])
    )

    return {
        "gold_customer_360": {
            "input_rows": len(customers),
            "output_rows": _write_gold(customer_360, "gold_customer_360"),
        },
        "gold_claims_monthly_summary": {
            "input_rows": len(claims),
            "output_rows": _write_gold(claims_monthly_summary, "gold_claims_monthly_summary"),
        },
        "gold_policy_performance": {
            "input_rows": len(policies),
            "output_rows": _write_gold(policy_performance, "gold_policy_performance"),
        },
        "gold_payment_risk_summary": {
            "input_rows": len(payments),
            "output_rows": _write_gold(payment_risk_summary, "gold_payment_risk_summary"),
        },
    }


if __name__ == "__main__":
    print(build_gold_datamarts())
