import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import duckdb

from run_explain_analysis import parse_named_queries


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "db" / "optimization_lab.duckdb"
QUERY_DIR = PROJECT_ROOT / "queries"
OUTPUT_DIR = PROJECT_ROOT / "output"
BENCHMARK_RESULTS_FILE = OUTPUT_DIR / "query_benchmark_results.csv"
BENCHMARK_SUMMARY_FILE = OUTPUT_DIR / "query_benchmark_summary.json"
ITERATIONS = 3

QUERY_PAIR_KEYS = {
    "slow_endpoint_errors": "endpoint_errors",
    "optimized_endpoint_errors": "endpoint_errors",
    "slow_correlated_avg_response_time": "correlated_avg_response_time",
    "optimized_correlated_avg_response_time": "correlated_avg_response_time",
    "slow_channel_metrics_full_scan": "channel_metrics",
    "optimized_channel_metrics_preaggregated": "channel_metrics",
    "slow_customer_error_lookup": "customer_error_lookup",
    "optimized_customer_error_lookup": "customer_error_lookup",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_query_file(path: Path) -> list[tuple[str, str]]:
    return parse_named_queries(path.read_text(encoding="utf-8"))


def apply_indexes(connection: duckdb.DuckDBPyConnection) -> None:
    index_sql = (QUERY_DIR / "02_indexes.sql").read_text(encoding="utf-8")
    connection.execute(index_sql)


def run_single_query(
    connection: duckdb.DuckDBPyConnection,
    query_name: str,
    query_type: str,
    query_sql: str,
) -> dict:
    durations = []
    row_count = 0
    status = "PASSED"
    error_message = None

    try:
        for _ in range(ITERATIONS):
            started = perf_counter()
            rows = connection.execute(query_sql).fetchall()
            durations.append(perf_counter() - started)
            row_count = len(rows)
    except Exception as exc:
        status = "FAILED"
        error_message = str(exc)

    average_duration = sum(durations) / len(durations) if durations else None
    return {
        "query_name": query_name,
        "query_type": query_type,
        "pair_key": QUERY_PAIR_KEYS.get(query_name, query_name),
        "duration_seconds": round(average_duration, 6) if average_duration is not None else None,
        "row_count": row_count,
        "iterations": len(durations),
        "status": status,
        "error_message": error_message,
    }


def calculate_improvements(results: list[dict]) -> list[dict]:
    grouped = {}
    for result in results:
        grouped.setdefault(result["pair_key"], {})[result["query_type"]] = result

    improvements = []
    for pair_key, values in grouped.items():
        baseline = values.get("baseline")
        optimized = values.get("optimized")
        improvement_factor = None
        improved = None

        if (
            baseline
            and optimized
            and baseline["duration_seconds"]
            and optimized["duration_seconds"]
            and optimized["duration_seconds"] > 0
        ):
            improvement_factor = round(
                baseline["duration_seconds"] / optimized["duration_seconds"], 3
            )
            improved = improvement_factor > 1

        improvements.append(
            {
                "pair_key": pair_key,
                "baseline_query": baseline["query_name"] if baseline else None,
                "optimized_query": optimized["query_name"] if optimized else None,
                "baseline_duration_seconds": baseline["duration_seconds"] if baseline else None,
                "optimized_duration_seconds": optimized["duration_seconds"] if optimized else None,
                "improvement_factor": improvement_factor,
                "improved": improved,
                "note": (
                    "Measured locally. Small datasets and DuckDB optimizations can make differences small or noisy."
                    if improvement_factor is not None
                    else "Improvement could not be calculated."
                ),
            }
        )
    return improvements


def write_results_csv(results: list[dict]) -> None:
    fieldnames = [
        "query_name",
        "query_type",
        "pair_key",
        "duration_seconds",
        "row_count",
        "iterations",
        "status",
        "error_message",
    ]
    with BENCHMARK_RESULTS_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def run_benchmark() -> dict:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DATABASE_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    baseline_queries = read_query_file(QUERY_DIR / "01_slow_queries.sql")
    optimized_queries = read_query_file(QUERY_DIR / "03_optimized_queries.sql")
    started_at = utc_now()
    benchmark_results = []

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        for query_name, query_sql in baseline_queries:
            benchmark_results.append(
                run_single_query(connection, query_name, "baseline", query_sql)
            )

        apply_indexes(connection)

        for query_name, query_sql in optimized_queries:
            benchmark_results.append(
                run_single_query(connection, query_name, "optimized", query_sql)
            )

    improvements = calculate_improvements(benchmark_results)
    passed_queries = sum(1 for result in benchmark_results if result["status"] == "PASSED")
    failed_queries = sum(1 for result in benchmark_results if result["status"] == "FAILED")
    best_improvement = max(
        (
            item["improvement_factor"]
            for item in improvements
            if item["improvement_factor"] is not None
        ),
        default=None,
    )

    write_results_csv(benchmark_results)
    summary = {
        "final_status": "PASSED" if failed_queries == 0 else "FAILED",
        "started_at": started_at,
        "finished_at": utc_now(),
        "iterations_per_query": ITERATIONS,
        "baseline_query_count": len(baseline_queries),
        "optimized_query_count": len(optimized_queries),
        "passed_query_count": passed_queries,
        "failed_query_count": failed_queries,
        "best_improvement_factor": best_improvement,
        "improvements": improvements,
        "generated_paths": {
            "benchmark_results": str(BENCHMARK_RESULTS_FILE),
            "benchmark_summary": str(BENCHMARK_SUMMARY_FILE),
        },
    }
    BENCHMARK_SUMMARY_FILE.write_text(json.dumps(summary, indent=4), encoding="utf-8")
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    summary = run_benchmark()
    logging.info("Benchmark finished: %s", summary["final_status"])


if __name__ == "__main__":
    main()
