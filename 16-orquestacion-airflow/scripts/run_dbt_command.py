from pathlib import Path
import argparse
import json
import subprocess
from datetime import datetime, timezone


BASE_PATH = Path(__file__).resolve().parents[2]
DBT_PROJECT_PATH = BASE_PATH / "15-dbt-profesional"
OUTPUT_PATH = BASE_PATH / "16-orquestacion-airflow" / "output"

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def run_dbt_command(command):
    if command not in ["run", "test"]:
        raise ValueError("Command must be 'run' or 'test'")

    started_at = datetime.now(timezone.utc).isoformat()

    cmd = ["dbt", command, "--profiles-dir", "."]

    print(f"Ejecutando comando dbt: {' '.join(cmd)}")
    print(f"Directorio dbt: {DBT_PROJECT_PATH}")

    process = subprocess.run(
        cmd,
        cwd=DBT_PROJECT_PATH,
        capture_output=True,
        text=True
    )

    finished_at = datetime.now(timezone.utc).isoformat()

    result = {
        "command": f"dbt {command}",
        "working_directory": str(DBT_PROJECT_PATH),
        "return_code": process.returncode,
        "status": "PASSED" if process.returncode == 0 else "FAILED",
        "started_at": started_at,
        "finished_at": finished_at,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }

    output_file = OUTPUT_PATH / f"dbt_{command}_result.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"Resultado guardado en: {output_file}")
    print(f"Estado dbt {command}: {result['status']}")

    print("\n--- STDOUT ---")
    print(process.stdout)

    if process.stderr:
        print("\n--- STDERR ---")
        print(process.stderr)

    if process.returncode != 0:
        raise SystemExit(process.returncode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["run", "test"],
        help="Comando dbt a ejecutar: run o test"
    )

    args = parser.parse_args()
    run_dbt_command(args.command)


if __name__ == "__main__":
    main()
