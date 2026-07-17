import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from generate_banking_logs import generate_banking_logs
from run_benchmark import run_benchmark
from run_explain_analysis import run_explain_analysis
from setup_database import setup_database


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


def failed_summary(started_at: str, start_time: float, error: Exception) -> dict:
    return {
        "final_status": "FAILED",
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(perf_counter() - start_time, 3),
        "input_counts": {},
        "database_path": str(PROJECT_ROOT / "db" / "optimization_lab.duckdb"),
        "explain_summary": {},
        "benchmark_summary": {},
        "generated_paths": {
            "pipeline_summary": str(PIPELINE_SUMMARY_FILE),
        },
        "error": {
            "error_type": type(error).__name__,
            "error_message": str(error),
        },
    }


def main() -> None:
    configure_logging()
    started_at = utc_now()
    start_time = perf_counter()

    logging.info("Starting SQL query optimization banking pipeline")
    logging.info("Project root: %s", PROJECT_ROOT)

    try:
        generation_result = generate_banking_logs()
        logging.info("Raw banking data generated: %s", generation_result["row_counts"])

        database_result = setup_database()
        logging.info("DuckDB tables created: %s", database_result["table_counts"])

        explain_summary = run_explain_analysis()
        logging.info("EXPLAIN analysis generated")

        benchmark_summary = run_benchmark()
        logging.info("Benchmark generated: %s", benchmark_summary["final_status"])

        final_status = (
            "PASSED"
            if explain_summary["final_status"] == "PASSED"
            and benchmark_summary["final_status"] == "PASSED"
            else "FAILED"
        )
        summary = {
            "final_status": final_status,
            "started_at": started_at,
            "finished_at": utc_now(),
            "duration_seconds": round(perf_counter() - start_time, 3),
            "input_counts": generation_result["row_counts"],
            "database_path": database_result["database_path"],
            "table_counts": database_result["table_counts"],
            "explain_summary": {
                "baseline_query_count": explain_summary["baseline_query_count"],
                "optimized_query_count": explain_summary["optimized_query_count"],
                "generated_paths": explain_summary["generated_paths"],
            },
            "benchmark_summary": {
                "baseline_query_count": benchmark_summary["baseline_query_count"],
                "optimized_query_count": benchmark_summary["optimized_query_count"],
                "passed_query_count": benchmark_summary["passed_query_count"],
                "failed_query_count": benchmark_summary["failed_query_count"],
                "best_improvement_factor": benchmark_summary["best_improvement_factor"],
                "generated_paths": benchmark_summary["generated_paths"],
            },
            "generated_paths": {
                "raw_data": generation_result["generated_paths"],
                "database": database_result["generated_paths"]["database"],
                "explain_analysis": explain_summary["generated_paths"]["explain_analysis"],
                "benchmark_results": benchmark_summary["generated_paths"]["benchmark_results"],
                "benchmark_summary": benchmark_summary["generated_paths"]["benchmark_summary"],
                "pipeline_summary": str(PIPELINE_SUMMARY_FILE),
            },
            "notes": [
                "This project runs locally with DuckDB and generated synthetic banking data.",
                "No cloud services, credentials or boto3 are used.",
                "Performance improvements are measured from local benchmark results and are not estimated manually.",
            ],
        }
        write_summary(summary)
        logging.info("Pipeline summary written to %s", PIPELINE_SUMMARY_FILE)

        if final_status != "PASSED":
            raise SystemExit(1)
    except Exception as exc:
        logging.exception("Pipeline failed")
        write_summary(failed_summary(started_at, start_time, exc))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
