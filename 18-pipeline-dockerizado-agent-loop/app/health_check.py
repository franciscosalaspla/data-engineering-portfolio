import json
import os
import shutil
from pathlib import Path


REQUIRED_ENV_VARS = [
    "PIPELINE_NAME",
    "ENVIRONMENT",
    "DBT_PROJECT_DIR",
    "DBT_PROFILES_DIR",
    "OUTPUT_DIR",
]


def check_required_env_vars() -> dict:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    return {
        "status": "PASSED" if not missing else "FAILED",
        "missing": missing,
    }


def check_path_exists(path: Path, path_type: str) -> dict:
    exists = path.exists()
    type_is_valid = path.is_dir() if path_type == "directory" else path.is_file()

    return {
        "status": "PASSED" if exists and type_is_valid else "FAILED",
        "path": str(path),
        "expected_type": path_type,
        "exists": exists,
    }


def check_output_writable(output_dir: Path) -> dict:
    test_file = output_dir / ".health_check.tmp"

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return {
            "status": "PASSED",
            "path": str(output_dir),
            "error": None,
        }
    except OSError as exc:
        return {
            "status": "FAILED",
            "path": str(output_dir),
            "error": str(exc),
        }


def build_health_report() -> dict:
    dbt_project_dir = Path(os.getenv("DBT_PROJECT_DIR", ""))
    dbt_profiles_dir = Path(os.getenv("DBT_PROFILES_DIR", ""))
    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))

    checks = {
        "required_environment_variables": check_required_env_vars(),
        "dbt_project_dir": check_path_exists(dbt_project_dir, "directory"),
        "dbt_project_yml": check_path_exists(dbt_project_dir / "dbt_project.yml", "file"),
        "profiles_yml": check_path_exists(dbt_profiles_dir / "profiles.yml", "file"),
        "seeds_directory": check_path_exists(dbt_project_dir / "seeds", "directory"),
        "dbt_executable": {
            "status": "PASSED" if shutil.which("dbt") else "FAILED",
            "path": shutil.which("dbt"),
        },
        "output_dir_writable": check_output_writable(output_dir),
    }

    failed_checks = [
        check_name
        for check_name, result in checks.items()
        if result["status"] != "PASSED"
    ]

    return {
        "status": "healthy" if not failed_checks else "unhealthy",
        "failed_checks": failed_checks,
        "checks": checks,
    }


def main() -> None:
    report = build_health_report()
    print(json.dumps(report, indent=4, ensure_ascii=False))

    if report["status"] != "healthy":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
