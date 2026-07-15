import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from process_with_pyspark import process_banking_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "output"
SUMMARY_FILE = OUTPUT_DIR / "pipeline_summary.json"

REQUIRED_RAW_FILES = [
    RAW_DIR / "finanzas_transactions.csv",
    RAW_DIR / "finanzas_accounts.csv",
    RAW_DIR / "finanzas_customers.csv",
    RAW_DIR / "finanzas_branches.csv",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def missing_required_files() -> list[Path]:
    return [path for path in REQUIRED_RAW_FILES if not path.exists()]


def run_sample_data_generator() -> None:
    generator_script = PROJECT_ROOT / "app" / "generate_sample_data.py"
    logging.info("Running fallback sample data generator: %s", generator_script)
    subprocess.run(
        [sys.executable, str(generator_script)],
        cwd=PROJECT_ROOT,
        check=True,
    )


def validate_java_runtime() -> None:
    if not shutil.which("java"):
        raise RuntimeError(
            "Java Runtime is required to run PySpark, but the 'java' executable was not found. "
            "Install Java 11 or 17 and run the pipeline again."
        )
    java_check = subprocess.run(
        ["java", "-version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if java_check.returncode != 0:
        java_error = (java_check.stderr or java_check.stdout).strip()
        raise RuntimeError(
            "Java Runtime is required to run PySpark, but 'java -version' failed. "
            f"Install Java 11 or 17 and run the pipeline again. Details: {java_error}"
        )


def write_summary(summary: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(
        json.dumps(summary, indent=4, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def build_failed_summary(
    started_at: str,
    start_time: float,
    fallback_data_generated: bool,
    error: Exception,
) -> dict:
    finished_at = utc_now()
    return {
        "final_status": "FAILED",
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": round(perf_counter() - start_time, 3),
        "fallback_data_generated": fallback_data_generated,
        "spark_app_name": "pyspark_banking_processing",
        "input_counts": {},
        "output_counts": {},
        "generated_paths": {"pipeline_summary": str(SUMMARY_FILE)},
        "main_metrics": {},
        "validations": {
            "error_type": type(error).__name__,
            "error_message": str(error),
        },
    }


def main() -> None:
    configure_logging()
    started_at = utc_now()
    start_time = perf_counter()
    fallback_data_generated = False

    logging.info("Starting PySpark banking pipeline")
    logging.info("Project root: %s", PROJECT_ROOT)

    try:
        missing_files = missing_required_files()
        if missing_files:
            fallback_data_generated = True
            logging.info(
                "Missing required raw files: %s",
                ", ".join(path.name for path in missing_files),
            )
            run_sample_data_generator()
        else:
            logging.info("All required raw files found in data/raw")

        validate_java_runtime()
        processing_result = process_banking_data()
        finished_at = utc_now()

        summary = {
            "final_status": "PASSED",
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_seconds": round(perf_counter() - start_time, 3),
            "fallback_data_generated": fallback_data_generated,
            "spark_app_name": processing_result["spark_app_name"],
            "input_counts": processing_result["input_counts"],
            "output_counts": processing_result["output_counts"],
            "generated_paths": {
                **processing_result["generated_paths"],
                "pipeline_summary": str(SUMMARY_FILE),
            },
            "main_metrics": processing_result["main_metrics"],
            "validations": processing_result["validations"],
        }
        write_summary(summary)
        logging.info("Pipeline finished successfully")
        logging.info("Pipeline summary written to %s", SUMMARY_FILE)
    except Exception as exc:
        logging.exception("Pipeline failed")
        summary = build_failed_summary(started_at, start_time, fallback_data_generated, exc)
        write_summary(summary)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
