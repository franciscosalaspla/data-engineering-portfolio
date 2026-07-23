# Ejecución prevista en Databricks Free Edition

## Estado

Este runbook es una guía de ejecución futura. Los notebooks todavía no se han ejecutado en Databricks Free Edition y no constituyen evidencia de Azure Databricks.

## Preparación

1. Importar o clonar el repositorio en el Workspace.
2. Crear o seleccionar un catálogo, schema y Volume permitido por Free Edition.
3. Copiar los JSONL Bronze generados por el Hito 2 bajo una ruta equivalente a `/Volumes/{catalog}/{schema}/bankfx/bronze/{entity}/`.
4. No copiar credenciales ni outputs locales anteriores como evidencia cloud.

Delta Lake y PySpark deben obtenerse del Databricks Runtime; no es necesario ejecutar `pip install` dentro del notebook salvo que el runtime futuro indique lo contrario.

## Parámetros

El notebook `00_configuration.py` define widgets para:

- `project_root`;
- `environment`;
- `run_id`;
- `bronze_root`;
- `silver_root`;
- `quarantine_path`;
- `audit_root`;
- `catalog`;
- `schema`.

Se deben reemplazar todos los valores `REPLACE_*`. Los paths no dependen del almacenamiento predeterminado de Free Edition.

## Orden de ejecución

1. `01_bronze_to_silver.py` ejecuta el driver completo.
2. Repetir el driver con otro `run_id` para validar idempotencia.
3. `02_quality_checks.py` valida nulos y duplicados de claves.
4. `03_validate_results.py` compara los conteos de los fixtures pequeños.

Las evidencias deben mostrar los parámetros no sensibles, conteos, auditoría, versiones Delta y nombre del entorno **Databricks Free Edition**. No deben presentarse como ejecución de Azure Databricks.
