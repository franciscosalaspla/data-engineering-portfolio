from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "data" / "source"
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SOURCE_FILES = ["customers.csv", "policies.csv", "claims.csv", "payments.csv", "interactions.csv"]


def run_bronze_ingestion(pipeline_run_id: str) -> dict[str, dict[str, int]]:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    ingestion_timestamp = datetime.now(timezone.utc).isoformat()
    metrics: dict[str, dict[str, int]] = {}

    for file_name in SOURCE_FILES:
        source_path = SOURCE_DIR / file_name
        dataset_name = source_path.stem
        if not source_path.exists():
            raise FileNotFoundError(f"Missing source file: {source_path}")

        df = pd.read_csv(source_path)
        input_rows = len(df)
        df["ingestion_timestamp"] = ingestion_timestamp
        df["source_file"] = file_name
        df["pipeline_run_id"] = pipeline_run_id

        output_path = BRONZE_DIR / f"bronze_{dataset_name}.parquet"
        df.to_parquet(output_path, index=False)

        metrics[dataset_name] = {
            "input_rows": input_rows,
            "output_rows": len(df),
        }

    return metrics


if __name__ == "__main__":
    print(run_bronze_ingestion("manual-run"))
