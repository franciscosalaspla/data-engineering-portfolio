from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def silver_to_gold():
    src, out = ROOT / "data/silver", ROOT / "data/gold"
    out.mkdir(parents=True, exist_ok=True)
    c = pd.read_parquet(src / "customers.parquet")
    p = pd.read_parquet(src / "policies.parquet")
    cl = pd.read_parquet(src / "claims.parquet")
    pay = pd.read_parquet(src / "payments.parquet")
    enriched = p.merge(c, on="customer_id", validate="many_to_one")
    marts = {
        "dim_customer": c[["customer_id", "customer_name", "segment", "region"]],
        "fact_policy": enriched[["policy_id", "customer_id", "product", "premium", "status"]],
        "claims_by_product": cl.merge(p[["policy_id", "product"]], on="policy_id").groupby("product", as_index=False).agg(claim_count=("claim_id", "count"), claim_amount=("claim_amount", "sum")),
        "premium_by_segment": enriched.groupby("segment", as_index=False).agg(policy_count=("policy_id", "count"), premium_total=("premium", "sum")),
        "payment_risk": pay.groupby("payment_status", as_index=False).agg(payment_count=("payment_id", "count"), amount_total=("amount", "sum")),
    }
    for name, frame in marts.items():
        frame.to_parquet(out / f"{name}.parquet", index=False)
    return {name: len(frame) for name, frame in marts.items()}
