from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from bronze_ingestion import SOURCE_FILES, SOURCE_DIR, run_bronze_ingestion
from gold_datamart import build_gold_datamarts
from quality_checks import run_quality_checks
from silver_transformations import run_silver_transformations


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
PIPELINE_NAME = "azure_adf_medallion_pipeline_local"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _source_row_count() -> int:
    total_rows = 0
    for file_name in SOURCE_FILES:
        path = SOURCE_DIR / file_name
        if not path.exists():
            raise FileNotFoundError(f"Missing source file: {path}")
        total_rows += len(pd.read_csv(path))
    return total_rows


def _sum_metric_rows(metrics: dict[str, dict[str, int]], key: str) -> int:
    return int(sum(dataset_metrics.get(key, 0) for dataset_metrics in metrics.values()))


def _activity(
    *,
    activity_name: str,
    dependencies: list[str],
    runner,
    row_mapper,
) -> tuple[dict[str, object], object]:
    started = time.perf_counter()
    result = runner()
    duration = round(time.perf_counter() - started, 4)
    input_rows, output_rows = row_mapper(result)
    return (
        {
            "activity_name": activity_name,
            "status": "PASSED",
            "input_rows": int(input_rows),
            "output_rows": int(output_rows),
            "duration_seconds": duration,
            "dependencies": dependencies,
        },
        result,
    )


def run_adf_orchestrator() -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pipeline_run_id = str(uuid4())
    started_at = _now()
    activities: list[dict[str, object]] = []
    failed_activity = None

    try:
        activity, _ = _activity(
            activity_name="Extract source files",
            dependencies=[],
            runner=_source_row_count,
            row_mapper=lambda row_count: (row_count, row_count),
        )
        activities.append(activity)

        activity, bronze_metrics = _activity(
            activity_name="Bronze ingestion",
            dependencies=["Extract source files"],
            runner=lambda: run_bronze_ingestion(pipeline_run_id),
            row_mapper=lambda metrics: (_sum_metric_rows(metrics, "input_rows"), _sum_metric_rows(metrics, "output_rows")),
        )
        activities.append(activity)

        activity, silver_metrics = _activity(
            activity_name="Silver transformations",
            dependencies=["Bronze ingestion"],
            runner=run_silver_transformations,
            row_mapper=lambda metrics: (_sum_metric_rows(metrics, "input_rows"), _sum_metric_rows(metrics, "output_rows")),
        )
        activities.append(activity)

        activity, quality_summary = _activity(
            activity_name="Data quality checks",
            dependencies=["Silver transformations"],
            runner=run_quality_checks,
            row_mapper=lambda summary: (summary["total_checks"], summary["passed_checks"]),
        )
        activities.append(activity)
        if quality_summary["final_status"] != "PASSED":
            raise ValueError("Data quality checks failed")

        activity, gold_metrics = _activity(
            activity_name="Gold datamart build",
            dependencies=["Data quality checks"],
            runner=build_gold_datamarts,
            row_mapper=lambda metrics: (_sum_metric_rows(metrics, "input_rows"), _sum_metric_rows(metrics, "output_rows")),
        )
        activities.append(activity)

        activity, _ = _activity(
            activity_name="Pipeline summary",
            dependencies=["Gold datamart build"],
            runner=lambda: {
                "bronze_datasets": len(bronze_metrics),
                "silver_datasets": len(silver_metrics),
                "gold_datamarts": len(gold_metrics),
                "quality_checks": quality_summary["total_checks"],
            },
            row_mapper=lambda summary: (
                summary["bronze_datasets"] + summary["silver_datasets"] + summary["gold_datamarts"],
                summary["quality_checks"],
            ),
        )
        activities.append(activity)
        final_status = "PASSED"
    except Exception as exc:
        final_status = "FAILED"
        failed_activity = {
            "activity_name": activities[-1]["activity_name"] if activities else "Pipeline startup",
            "error": str(exc),
        }

    summary = {
        "pipeline_name": PIPELINE_NAME,
        "pipeline_run_id": pipeline_run_id,
        "started_at": started_at,
        "finished_at": _now(),
        "final_status": final_status,
        "activities": activities,
        "failed_activity": failed_activity,
    }

    with (OUTPUT_DIR / "adf_pipeline_run_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    return summary


if __name__ == "__main__":
    print(json.dumps(run_adf_orchestrator(), indent=2))
