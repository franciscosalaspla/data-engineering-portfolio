import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_config() -> dict:
    return {
        "pipeline_name": os.getenv(
            "PIPELINE_NAME",
            "dbt_ecommerce_dockerized_agent_loop",
        ),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "dbt_project_dir": Path(
            os.getenv("DBT_PROJECT_DIR", "/workspace/17-dbt-professional-ecommerce")
        ),
        "dbt_profiles_dir": Path(
            os.getenv("DBT_PROFILES_DIR", "/workspace/17-dbt-professional-ecommerce")
        ),
        "output_dir": Path(
            os.getenv(
                "OUTPUT_DIR",
                "/workspace/18-pipeline-dockerizado-agent-loop/output",
            )
        ),
        "fail_fast": os.getenv("FAIL_FAST", "true").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def truncate_text(value: str, max_chars: int = 4000) -> str:
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + "\n...[truncated]"


def run_step(step_name: str, command: list[str], cwd: Path) -> dict:
    logging.info("Running step: %s", step_name)
    started_at = utc_now()
    start_time = perf_counter()

    process = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    duration_seconds = round(perf_counter() - start_time, 3)
    finished_at = utc_now()
    status = "PASSED" if process.returncode == 0 else "FAILED"

    logging.info(
        "Step finished: %s | status=%s | return_code=%s | duration=%ss",
        step_name,
        status,
        process.returncode,
        duration_seconds,
    )

    return {
        "step_name": step_name,
        "command": " ".join(command),
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "return_code": process.returncode,
        "status": status,
        "stdout": truncate_text(process.stdout),
        "stderr": truncate_text(process.stderr),
    }


def build_dbt_commands(config: dict) -> list[tuple[str, list[str]]]:
    base_args = [
        "--project-dir",
        str(config["dbt_project_dir"]),
        "--profiles-dir",
        str(config["dbt_profiles_dir"]),
    ]

    return [
        ("dbt_debug", ["dbt", "debug", *base_args]),
        ("dbt_seed_full_refresh", ["dbt", "seed", "--full-refresh", *base_args]),
        ("dbt_build", ["dbt", "build", *base_args]),
        ("dbt_docs_generate", ["dbt", "docs", "generate", *base_args]),
    ]


def detect_outputs(config: dict) -> dict:
    dbt_project_dir = config["dbt_project_dir"]
    output_dir = config["output_dir"]

    expected_outputs = {
        "duckdb_database": dbt_project_dir / "ecommerce_analytics.duckdb",
        "dbt_manifest": dbt_project_dir / "target" / "manifest.json",
        "dbt_catalog": dbt_project_dir / "target" / "catalog.json",
        "pipeline_summary": output_dir / "pipeline_run_summary.json",
    }

    return {
        output_name: {
            "path": str(path),
            "exists": path.exists(),
        }
        for output_name, path in expected_outputs.items()
    }


def build_next_actions(final_status: str, steps: list[dict]) -> list[str]:
    failed_steps = [step for step in steps if step["status"] != "PASSED"]

    if final_status == "PASSED":
        return [
            "Revisar target/catalog.json y target/manifest.json para validar documentación dbt.",
            "Abrir dbt docs localmente si se necesita inspeccionar lineage y contratos de modelos.",
            "Usar pipeline_run_summary.json como evidencia de ejecución reproducible.",
        ]

    return [
        f"Revisar stdout/stderr del paso {failed_steps[0]['step_name']}.",
        "Ejecutar docker compose run --rm pipeline python app/health_check.py para validar ambiente.",
        "Corregir configuración o tests dbt antes de repetir docker compose up --build.",
    ]


def write_summary(summary: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "pipeline_run_summary.json"
    output_file.write_text(
        json.dumps(summary, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_file


def main() -> None:
    config = get_config()
    configure_logging(config["log_level"])

    started_at = utc_now()
    steps = []
    stop_condition = "All dbt steps executed successfully."

    for step_name, command in build_dbt_commands(config):
        result = run_step(step_name, command, config["dbt_project_dir"])
        steps.append(result)

        if result["status"] != "PASSED" and config["fail_fast"]:
            stop_condition = f"Stopped after failed critical step: {step_name}."
            break

    final_status = "PASSED" if all(step["status"] == "PASSED" for step in steps) else "FAILED"
    if final_status == "FAILED" and stop_condition == "All dbt steps executed successfully.":
        stop_condition = "Completed configured steps with one or more failures."

    finished_at = utc_now()

    summary = {
        "pipeline_name": config["pipeline_name"],
        "environment": config["environment"],
        "started_at": started_at,
        "finished_at": finished_at,
        "final_status": final_status,
        "steps": steps,
        "stop_condition": stop_condition,
        "outputs_generated": {},
        "next_actions": build_next_actions(final_status, steps),
    }

    output_file = write_summary(summary, config["output_dir"])
    summary["outputs_generated"] = detect_outputs(config)
    write_summary(summary, config["output_dir"])

    logging.info("Pipeline summary written to %s", output_file)
    logging.info("Final status: %s", final_status)

    if final_status != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
