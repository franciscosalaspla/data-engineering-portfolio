import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from build_data_lake import build_data_lake
from generate_banking_landing_data import generate_landing_data
from run_athena_like_queries import run_queries


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
PIPELINE_SUMMARY_FILE = OUTPUT_DIR / "pipeline_summary.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def write_summary(summary: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PIPELINE_SUMMARY_FILE.write_text(json.dumps(summary, indent=4), encoding="utf-8")


def aws_equivalent_services() -> dict:
    return {
        "data_lake/landing": "Amazon S3 landing/raw prefix",
        "data_lake/bronze": "Amazon S3 bronze prefix",
        "data_lake/silver": "Amazon S3 silver prefix",
        "data_lake/gold": "Amazon S3 gold analytics prefix",
        "app/build_data_lake.py": "AWS Glue Job or AWS Lambda transform",
        "queries/athena_like_queries.sql": "Amazon Athena SQL",
        "app/run_athena_like_queries.py": "Athena query execution simulated with DuckDB",
        "output/pipeline_summary.json": "CloudWatch-style execution summary",
        "docs/iam_least_privilege.md": "IAM least privilege design notes",
        "docs/cost_control.md": "Cost control and scan reduction notes",
    }


def cost_control_notes() -> list[str]:
    return [
        "This project does not create AWS resources and does not generate cloud costs.",
        "Cost estimation is based on local file sizes, not on an AWS invoice.",
        "Parquet and year/month partitioning are used to simulate lower data scanned by Athena.",
        "Final SQL examples avoid SELECT * to reinforce scan control.",
    ]


def failed_summary(started_at: str, start_time: float, error: Exception) -> dict:
    return {
        "final_status": "FAILED",
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(perf_counter() - start_time, 3),
        "input_counts": {},
        "bronze_counts": {},
        "silver_counts": {},
        "gold_counts": {},
        "data_quality_checks": {
            "error_type": type(error).__name__,
            "error_message": str(error),
        },
        "generated_paths": {
            "pipeline_summary": str(PIPELINE_SUMMARY_FILE),
        },
        "aws_equivalent_services": aws_equivalent_services(),
        "cost_control_notes": cost_control_notes(),
    }


def main() -> None:
    configure_logging()
    started_at = utc_now()
    start_time = perf_counter()

    logging.info("Starting local AWS-style banking data lake pipeline")
    logging.info("Project root: %s", PROJECT_ROOT)

    try:
        landing_result = generate_landing_data()
        logging.info("Landing generated: %s", landing_result["landing_counts"])

        data_lake_result = build_data_lake()
        logging.info("Data lake built: silver=%s", data_lake_result["silver_counts"])

        query_summary = run_queries()
        logging.info("Athena-like queries completed: %s queries", query_summary["query_count"])

        summary = {
            "final_status": "PASSED",
            "started_at": started_at,
            "finished_at": utc_now(),
            "duration_seconds": round(perf_counter() - start_time, 3),
            "input_counts": data_lake_result["input_counts"],
            "bronze_counts": data_lake_result["bronze_counts"],
            "silver_counts": data_lake_result["silver_counts"],
            "gold_counts": data_lake_result["gold_counts"],
            "data_quality_checks": data_lake_result["data_quality_checks"],
            "generated_paths": {
                "landing": landing_result["generated_paths"],
                **data_lake_result["generated_paths"],
                "athena_like_query_results": query_summary["generated_paths"]["query_results"],
                "query_summary": query_summary["generated_paths"]["query_summary"],
                "pipeline_summary": str(PIPELINE_SUMMARY_FILE),
            },
            "aws_equivalent_services": aws_equivalent_services(),
            "cost_control_notes": cost_control_notes(),
        }
        write_summary(summary)
        logging.info("Pipeline summary written to %s", PIPELINE_SUMMARY_FILE)
    except Exception as exc:
        logging.exception("Pipeline failed")
        write_summary(failed_summary(started_at, start_time, exc))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
