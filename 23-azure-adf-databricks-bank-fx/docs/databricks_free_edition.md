# Runbook alternativo para Databricks Free Edition

## Estado

Este runbook conserva la ruta portable diseñada durante la fase local. El Proyecto 23 también fue ejecutado y validado en **Azure Databricks**, como se documenta en [implementation_by_milestone.md](implementation_by_milestone.md).

Los notebooks de esta carpeta siguen siendo una alternativa reproducible para Free Edition, pero no son la exportación de los notebooks cloud `nb_01_landing_to_bronze`, `nb_02_bronze_to_silver` y `nb_03_silver_to_gold`. Una eventual ejecución en Free Edition debe registrarse como evidencia independiente.

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

Las evidencias deben mostrar los parámetros no sensibles, conteos, sumas reconciliadas, auditoría, versiones Delta y nombre del entorno **Databricks Free Edition**. Deben mantenerse separadas de las evidencias de Azure Databricks registradas en `docs/evidence_catalog.md` y conservadas fuera del repositorio público.
