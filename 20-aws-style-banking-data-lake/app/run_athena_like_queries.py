import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUERY_FILE = PROJECT_ROOT / "queries" / "athena_like_queries.sql"
OUTPUT_DIR = PROJECT_ROOT / "output"
QUERY_RESULTS_FILE = OUTPUT_DIR / "athena_like_query_results.csv"
QUERY_SUMMARY_FILE = OUTPUT_DIR / "query_summary.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_named_queries(sql_text: str) -> list[tuple[str, str]]:
    queries = []
    current_name = None
    current_lines = []

    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- name:"):
            if current_name and current_lines:
                queries.append((current_name, "\n".join(current_lines).strip().rstrip(";")))
            current_name = stripped.replace("-- name:", "", 1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_name and current_lines:
        queries.append((current_name, "\n".join(current_lines).strip().rstrip(";")))

    if not queries:
        raise ValueError(f"No named queries found in {QUERY_FILE}")
    return queries


def run_queries() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sql_text = QUERY_FILE.read_text(encoding="utf-8").replace(
        "{{PROJECT_ROOT}}", PROJECT_ROOT.as_posix()
    )
    named_queries = parse_named_queries(sql_text)

    combined_results = []
    query_summaries = []
    started_at = utc_now()

    with duckdb.connect(database=":memory:") as connection:
        for query_name, query_sql in named_queries:
            dataframe = connection.execute(query_sql).fetchdf()
            dataframe.insert(0, "query_name", query_name)
            combined_results.append(dataframe)
            query_summaries.append(
                {
                    "query_name": query_name,
                    "row_count": len(dataframe),
                    "status": "PASSED",
                }
            )

    if combined_results:
        result_frame = pd.concat(combined_results, ignore_index=True, sort=False)
    else:
        result_frame = pd.DataFrame()

    result_frame.to_csv(QUERY_RESULTS_FILE, index=False)
    finished_at = utc_now()

    summary = {
        "final_status": "PASSED",
        "started_at": started_at,
        "finished_at": finished_at,
        "query_count": len(named_queries),
        "queries": query_summaries,
        "generated_paths": {
            "query_results": str(QUERY_RESULTS_FILE),
            "query_summary": str(QUERY_SUMMARY_FILE),
        },
        "engine": "DuckDB local Athena-like simulation",
    }
    QUERY_SUMMARY_FILE.write_text(json.dumps(summary, indent=4), encoding="utf-8")
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    summary = run_queries()
    logging.info("Athena-like queries finished: %s", summary["queries"])


if __name__ == "__main__":
    main()
