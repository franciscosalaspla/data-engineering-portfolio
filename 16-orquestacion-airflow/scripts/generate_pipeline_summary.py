import json
from datetime import datetime, timezone
from pathlib import Path


BASE_PATH = Path(__file__).resolve().parents[2]
PROJECT_PATH = BASE_PATH / "16-orquestacion-airflow"
OUTPUT_PATH = PROJECT_PATH / "output"

QUALITY_OUTPUT_PATH = BASE_PATH / "14-data-quality-great-expectations" / "output" / "validation_summary.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {
            "status": "MISSING",
            "message": f"File not found: {path}"
        }

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_status(value: str) -> str:
    if value == "PASSED":
        return "PASSED"
    if value == "SUCCESS":
        return "PASSED"
    if value == "FAILED":
        return "FAILED"
    return value or "UNKNOWN"


def main() -> None:
    print("Generando resumen final del pipeline...")

    raw_validation = read_json(OUTPUT_PATH / "raw_files_validation.json")
    quality_summary = read_json(QUALITY_OUTPUT_PATH)
    dbt_run = read_json(OUTPUT_PATH / "dbt_run_result.json")
    dbt_test = read_json(OUTPUT_PATH / "dbt_test_result.json")

    data_quality_status = quality_summary.get("pipeline_status", quality_summary.get("status", "UNKNOWN"))

    steps = {
        "validate_raw_files": normalize_status(raw_validation.get("status")),
        "run_data_quality_checks": normalize_status(data_quality_status),
        "dbt_run": normalize_status(dbt_run.get("status")),
        "dbt_test": normalize_status(dbt_test.get("status")),
    }

    failed_steps = [
        step_name
        for step_name, status in steps.items()
        if status != "PASSED"
    ]

    pipeline_status = "PASSED" if not failed_steps else "FAILED"

    summary = {
        "pipeline_name": "ecommerce_orchestration_pipeline",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_status": pipeline_status,
        "steps": steps,
        "failed_steps": failed_steps,
        "notes": [
            "The pipeline is designed to expose data quality issues instead of hiding them.",
            "dbt test can fail because staging models expose real data quality issues.",
            "Known dbt test failure: stg_order_items.order_id has 33 nulls.",
            "Known dbt test failure: stg_order_items.product_id has 16 nulls.",
            "Known dbt test failure: stg_orders.customer_id has 6 nulls."
        ],
        "outputs": {
            "raw_files_validation": "output/raw_files_validation.json",
            "data_quality_summary": "../14-data-quality-great-expectations/output/validation_summary.json",
            "dbt_run_result": "output/dbt_run_result.json",
            "dbt_test_result": "output/dbt_test_result.json"
        }
    }

    output_file = OUTPUT_PATH / "pipeline_summary.json"
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    print(f"Resumen guardado en: {output_file}")
    print(f"Estado final del pipeline: {pipeline_status}")

    if failed_steps:
        print("Pasos con estado no exitoso:")
        for step in failed_steps:
            print(f"- {step}: {steps[step]}")


if __name__ == "__main__":
    main()
