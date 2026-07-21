from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "data" / "source"
RANDOM_SEED = 42

CUSTOMERS_COUNT = 5_000
POLICIES_COUNT = 8_000
CLAIMS_COUNT = 20_000
PAYMENTS_COUNT = 40_000
INTERACTIONS_COUNT = 30_000


def _random_date(start: date, end: date) -> str:
    delta_days = (end - start).days
    return (start + timedelta(days=random.randint(0, delta_days))).isoformat()


def _write_csv(df: pd.DataFrame, file_name: str) -> int:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SOURCE_DIR / file_name
    df.to_csv(output_path, index=False)
    return len(df)


def generate_source_data() -> dict[str, int]:
    random.seed(RANDOM_SEED)

    regions = ["north", "south", "east", "west", "central"]
    segments = ["retail", "premium", "sme", "corporate"]
    policy_types = ["auto", "home", "life", "health", "business"]
    policy_statuses = ["active", "expired", "cancelled"]
    claim_statuses = ["open", "approved", "rejected", "paid"]
    claim_types = ["accident", "theft", "medical", "property", "liability"]
    payment_statuses = ["paid", "late", "failed", "pending"]
    payment_methods = ["card", "bank_transfer", "direct_debit", "cash"]
    interaction_channels = ["email", "phone", "branch", "chat", "app"]
    interaction_reasons = ["claim_update", "policy_question", "payment_issue", "renewal", "complaint"]

    customers = []
    for idx in range(1, CUSTOMERS_COUNT + 1):
        customers.append(
            {
                "customer_id": f"C{idx:06d}",
                "full_name": f"Customer {idx:06d}",
                "birth_date": _random_date(date(1950, 1, 1), date(2004, 12, 31)),
                "region": random.choice(regions),
                "segment": random.choice(segments),
                "signup_date": _random_date(date(2018, 1, 1), date(2025, 12, 31)),
                "risk_score": random.randint(250, 850),
            }
        )
    customers_df = pd.DataFrame(customers)

    customer_ids = customers_df["customer_id"].tolist()
    policies = []
    for idx in range(1, POLICIES_COUNT + 1):
        start_date = date.fromisoformat(_random_date(date(2020, 1, 1), date(2025, 12, 31)))
        end_date = start_date + timedelta(days=random.choice([180, 365, 730]))
        policies.append(
            {
                "policy_id": f"P{idx:07d}",
                "customer_id": random.choice(customer_ids),
                "policy_type": random.choice(policy_types),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "premium_amount": round(random.uniform(120.0, 5_500.0), 2),
                "policy_status": random.choices(policy_statuses, weights=[0.72, 0.2, 0.08], k=1)[0],
            }
        )
    policies_df = pd.DataFrame(policies)

    policy_ids = policies_df["policy_id"].tolist()
    claims = []
    for idx in range(1, CLAIMS_COUNT + 1):
        claims.append(
            {
                "claim_id": f"CL{idx:08d}",
                "policy_id": random.choice(policy_ids),
                "claim_date": _random_date(date(2021, 1, 1), date(2026, 6, 30)),
                "claim_amount": round(random.uniform(50.0, 25_000.0), 2),
                "claim_status": random.choices(claim_statuses, weights=[0.18, 0.38, 0.16, 0.28], k=1)[0],
                "claim_type": random.choice(claim_types),
            }
        )
    claims_df = pd.DataFrame(claims)

    payments = []
    for idx in range(1, PAYMENTS_COUNT + 1):
        payments.append(
            {
                "payment_id": f"PM{idx:08d}",
                "policy_id": random.choice(policy_ids),
                "payment_date": _random_date(date(2021, 1, 1), date(2026, 6, 30)),
                "payment_amount": round(random.uniform(20.0, 2_000.0), 2),
                "payment_status": random.choices(payment_statuses, weights=[0.78, 0.12, 0.05, 0.05], k=1)[0],
                "payment_method": random.choice(payment_methods),
            }
        )
    payments_df = pd.DataFrame(payments)

    interactions = []
    for idx in range(1, INTERACTIONS_COUNT + 1):
        interactions.append(
            {
                "interaction_id": f"IN{idx:08d}",
                "customer_id": random.choice(customer_ids),
                "interaction_date": _random_date(date(2021, 1, 1), date(2026, 6, 30)),
                "channel": random.choice(interaction_channels),
                "reason": random.choice(interaction_reasons),
                "satisfaction_score": random.randint(1, 5),
            }
        )
    interactions_df = pd.DataFrame(interactions)

    return {
        "customers": _write_csv(customers_df, "customers.csv"),
        "policies": _write_csv(policies_df, "policies.csv"),
        "claims": _write_csv(claims_df, "claims.csv"),
        "payments": _write_csv(payments_df, "payments.csv"),
        "interactions": _write_csv(interactions_df, "interactions.csv"),
    }


if __name__ == "__main__":
    metrics = generate_source_data()
    for dataset, rows in metrics.items():
        print(f"{dataset}: {rows} rows generated")
