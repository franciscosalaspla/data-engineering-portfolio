# Proyecto 16 - Orquestación con Apache Airflow

## Objetivo

Este proyecto implementa una orquestación de datos con Apache Airflow para coordinar un pipeline de e-commerce compuesto por validación de archivos raw, controles de calidad, ejecución de modelos dbt y generación de un resumen final del pipeline.

El objetivo no es ocultar errores, sino exponerlos de forma controlada para dejar trazabilidad del estado real del proceso.

---

## Componentes del pipeline

El DAG principal se llama:

```text
ecommerce_orchestration_pipeline
```

La orquestación ejecuta las siguientes tareas:

| Tarea                       | Descripción                                                      | Resultado esperado    |
| --------------------------- | ---------------------------------------------------------------- | --------------------- |
| `validate_raw_files`        | Valida existencia, estructura y columnas mínimas de archivos raw | PASSED                |
| `run_data_quality_checks`   | Ejecuta controles de calidad del Proyecto 14                     | Puede detectar fallas |
| `run_dbt_run`               | Ejecuta los modelos dbt del Proyecto 15                          | PASSED                |
| `run_dbt_test`              | Ejecuta tests dbt sobre staging y marts                          | FAILED esperado       |
| `generate_pipeline_summary` | Consolida el resultado final del pipeline                        | PASSED como ejecución |

---

## Arquitectura

```text
Raw CSV files
   ↓
Raw file validation
   ↓
Data quality checks
   ↓
dbt run
   ↓
dbt test
   ↓
Pipeline summary
```

---

## Tecnologías utilizadas

* Apache Airflow
* Docker Compose
* Python
* pandas
* dbt-core
* dbt-duckdb
* DuckDB
* Great Expectations
* JSON como salida de trazabilidad

---

## Estructura del proyecto

```text
16-orquestacion-airflow/
├── dags/
│   └── ecommerce_orchestration_dag.py
├── scripts/
│   ├── validate_raw_files.py
│   ├── run_dbt_command.py
│   └── generate_pipeline_summary.py
├── output/
│   ├── raw_files_validation.json
│   ├── dbt_run_result.json
│   ├── dbt_test_result.json
│   └── pipeline_summary.json
├── docker-compose.yaml
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Ejecución local de scripts

Desde la raíz del repositorio:

```bash
python 16-orquestacion-airflow/scripts/validate_raw_files.py
python 16-orquestacion-airflow/scripts/run_dbt_command.py run
python 16-orquestacion-airflow/scripts/run_dbt_command.py test
python 16-orquestacion-airflow/scripts/generate_pipeline_summary.py
```

---

## Ejecución con Airflow

Desde la carpeta del proyecto:

```bash
cd 16-orquestacion-airflow
docker compose up airflow-init
docker compose up
```

Luego abrir Airflow en el puerto 8080.

Credenciales:

```text
usuario: airflow
password: airflow
```

---

## Resultado final del pipeline

El pipeline finaliza con estado:

```text
FAILED
```

Este resultado es intencional y controlado, porque los tests de calidad detectan problemas reales en los datos.

Resumen generado:

```json
{
    "pipeline_status": "FAILED",
    "steps": {
        "validate_raw_files": "PASSED",
        "run_data_quality_checks": "FAILED",
        "dbt_run": "PASSED",
        "dbt_test": "FAILED"
    },
    "failed_steps": [
        "run_data_quality_checks",
        "dbt_test"
    ]
}
```

---

## Hallazgos principales

Los controles de calidad detectan errores en los datos crudos y en los modelos staging de dbt.

Principales fallas conocidas:

```text
stg_order_items.order_id tiene 33 valores nulos
stg_order_items.product_id tiene 16 valores nulos
stg_orders.customer_id tiene 6 valores nulos
```

Esto permite demostrar que el pipeline no solo ejecuta procesos, sino que también identifica problemas de calidad antes de considerar los datos como confiables.

---

## Cómo contar este proyecto en entrevista

### Hook

Construí una orquestación con Apache Airflow para coordinar un pipeline de datos de e-commerce, integrando validaciones raw, controles de calidad, ejecución de dbt y generación de un resumen final trazable.

### Situación

El proyecto parte desde datos raw con problemas reales de calidad. En vez de asumir que los datos están correctos, implementé una orquestación que valida cada etapa y deja evidencia del estado final del pipeline.

### Tarea

Diseñar un flujo orquestado que pudiera ejecutar validaciones, transformaciones y tests, permitiendo identificar fallas de calidad sin perder trazabilidad del proceso.

### Acciones

* Creé un DAG en Airflow con tareas encadenadas.
* Validé archivos raw antes de ejecutar transformaciones.
* Integré controles de calidad del proyecto anterior.
* Ejecuté `dbt run` para construir modelos analíticos.
* Ejecuté `dbt test` para detectar errores en staging y marts.
* Generé un archivo `pipeline_summary.json` con el estado final del pipeline.

### Resultado

El pipeline ejecuta correctamente la orquestación completa y deja evidencia de los pasos exitosos y fallidos. El resultado final queda como `FAILED` de forma controlada, porque los tests detectan problemas reales de calidad en los datos.

---

## Frase corta para entrevista

Orquesté un pipeline de datos con Apache Airflow integrando validaciones raw, controles de calidad, ejecución de dbt y generación de un resumen final. El pipeline detecta errores reales en los datos y deja trazabilidad clara del estado de cada etapa.

