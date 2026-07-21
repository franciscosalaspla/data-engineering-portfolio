import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def run_quality_checks():
    s = ROOT / "data/silver"
    c, p = pd.read_parquet(s / "customers.parquet"), pd.read_parquet(s / "policies.parquet")
    cl, pay = pd.read_parquet(s / "claims.parquet"), pd.read_parquet(s / "payments.parquet")
    gold_files = list((ROOT / "data/gold").glob("*.parquet"))
    checks = {
        "customers_not_empty": len(c) > 0,
        "customer_id_unique": c.customer_id.is_unique,
        "policy_id_unique": p.policy_id.is_unique,
        "claim_id_unique": cl.claim_id.is_unique,
        "payment_id_unique": pay.payment_id.is_unique,
        "policies_have_customers": p.customer_id.isin(c.customer_id).all(),
        "claims_have_policies": cl.policy_id.isin(p.policy_id).all(),
        "five_gold_datamarts": len(gold_files) == 5,
    }
    results = [{"check": name, "status": "PASSED" if ok else "FAILED"} for name, ok in checks.items()]
    passed = int(sum(bool(value) for value in checks.values()))
    summary = {"total_checks": 8, "passed_checks": passed, "failed_checks": 8 - passed, "final_status": "PASSED" if all(checks.values()) else "FAILED", "checks": results}
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    (out / "data_quality_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(results).to_csv(out / "data_quality_results.csv", index=False)
    if not all(checks.values()):
        raise ValueError("Data quality checks failed")
    return summary
