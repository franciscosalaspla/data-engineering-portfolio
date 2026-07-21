from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def generate_source_data():
    out = ROOT / "data/landing"
    out.mkdir(parents=True, exist_ok=True)
    customers = pd.DataFrame({
        "customer_id": range(1, 101),
        "customer_name": [f"Cliente {i:03d}" for i in range(1, 101)],
        "segment": ["Retail", "Premium", "Pyme", "Retail"] * 25,
        "region": ["Valparaiso", "Metropolitana", "Biobio", "Los Lagos"] * 25,
    })
    policies = pd.DataFrame({
        "policy_id": range(1001, 1201),
        "customer_id": [(i % 100) + 1 for i in range(200)],
        "product": ["Vida", "Salud", "Auto", "Hogar"] * 50,
        "premium": [22000 + (i % 20) * 1500 for i in range(200)],
        "status": ["ACTIVE" if i % 8 else "INACTIVE" for i in range(200)],
    })
    claims = pd.DataFrame({
        "claim_id": range(5001, 5301),
        "policy_id": [1001 + (i % 200) for i in range(300)],
        "claim_date": pd.date_range("2025-01-01", periods=300, freq="D"),
        "claim_amount": [15000 + (i % 35) * 3500 for i in range(300)],
        "claim_status": ["APPROVED", "PENDING", "REJECTED"] * 100,
    })
    payments = pd.DataFrame({
        "payment_id": range(9001, 9401),
        "policy_id": [1001 + (i % 200) for i in range(400)],
        "payment_date": pd.date_range("2025-01-01", periods=400, freq="D"),
        "amount": [18000 + (i % 25) * 1200 for i in range(400)],
        "payment_status": ["PAID" if i % 7 else "OVERDUE" for i in range(400)],
    })
    datasets = {"customers": customers, "policies": policies, "claims": claims, "payments": payments}
    for name, frame in datasets.items():
        frame.to_csv(out / f"{name}.csv", index=False)
    return {name: len(frame) for name, frame in datasets.items()}

if __name__ == "__main__":
    print(generate_source_data())
