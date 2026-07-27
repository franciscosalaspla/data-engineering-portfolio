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
- `gold_root`;
- `gold_quarantine_path`;
- `serving_root`;
- `catalog`;
- `schema`.

Se deben reemplazar todos los valores `REPLACE_*`. Los paths no dependen del almacenamiento predeterminado de Free Edition.

## Orden de ejecución

1. `01_bronze_to_silver.py` ejecuta el driver Bronze→Silver.
2. `02_quality_checks.py` valida nulos y duplicados Silver.
3. `03_validate_results.py` compara los conteos Silver.
4. `04_silver_to_gold.py` ejecuta dimensiones, hecho, calidad, reconciliación y snapshot.
5. Repetir únicamente el driver Gold con otro `run_id` para validar idempotencia.
6. `05_validate_gold.py` verifica los conteos Gold y el snapshot.

Las evidencias deben mostrar los parámetros no sensibles, conteos, sumas reconciliadas, auditoría, versiones Delta y nombre del entorno **Databricks Free Edition**. No deben presentarse como ejecución de Azure Databricks.
