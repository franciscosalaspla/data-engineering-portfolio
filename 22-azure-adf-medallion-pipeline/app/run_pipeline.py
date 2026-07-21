from __future__ import annotations

import json

from adf_orchestrator import run_adf_orchestrator
from generate_source_data import generate_source_data


def main() -> dict[str, object]:
    print("Starting Azure-style local medallion pipeline")
    print("Generating reproducible synthetic source data")
    source_metrics = generate_source_data()
    for dataset_name, rows in source_metrics.items():
        print(f"Generated {dataset_name}: {rows} rows")

    print("Running ADF-style orchestration")
    summary = run_adf_orchestrator()
    print(f"Pipeline final status: {summary['final_status']}")
    print(f"Pipeline run id: {summary['pipeline_run_id']}")
    print("Summary written to output/adf_pipeline_run_summary.json")
    print(json.dumps({"source_rows": source_metrics, "final_status": summary["final_status"]}, indent=2))
    return summary


if __name__ == "__main__":
    main()
