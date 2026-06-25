from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule


REPO_ROOT = "/opt/airflow/repo"

DEFAULT_ARGS = {
    "owner": "francisco",
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
    "execution_timeout": timedelta(minutes=10),
}


with DAG(
    dag_id="ecommerce_orchestration_pipeline",
    description="Orquesta validación de archivos raw, dbt run, dbt test y resumen final.",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["data-engineering", "airflow", "dbt", "duckdb"],
) as dag:

    validate_raw_files = BashOperator(
        task_id="validate_raw_files",
        bash_command=(
            f"cd {REPO_ROOT} && "
            "python 16-orquestacion-airflow/scripts/validate_raw_files.py"
        ),
    )

    run_data_quality_checks = BashOperator(
        task_id="run_data_quality_checks",
        bash_command=(
            f"cd {REPO_ROOT}/14-data-quality-great-expectations && "
            "python src/run_quality_checks.py"
        ),
    )

    run_dbt_run = BashOperator(
        task_id="run_dbt_run",
        bash_command=(
            f"cd {REPO_ROOT} && "
            "python 16-orquestacion-airflow/scripts/run_dbt_command.py run"
        ),
    )

    run_dbt_test = BashOperator(
        task_id="run_dbt_test",
        bash_command=(
            f"cd {REPO_ROOT} && "
            "python 16-orquestacion-airflow/scripts/run_dbt_command.py test"
        ),
    )

    generate_pipeline_summary = BashOperator(
        task_id="generate_pipeline_summary",
        bash_command=(
            f"cd {REPO_ROOT} && "
            "python 16-orquestacion-airflow/scripts/generate_pipeline_summary.py"
        ),
        trigger_rule=TriggerRule.ALL_DONE,
    )

    (
        validate_raw_files
        >> run_data_quality_checks
        >> run_dbt_run
        >> run_dbt_test
        >> generate_pipeline_summary
    )
