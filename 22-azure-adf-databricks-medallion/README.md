# Proyecto 22 — Azure ADF + Databricks Medallion (local)

## 1. Valor del proyecto

Laboratorio reproducible y sin costo que demuestra cómo diseñaría un pipeline Azure de punta a punta: orquestación tipo Azure Data Factory, almacenamiento tipo ADLS, transformaciones tipo Databricks y capas Medallion. No usa Azure real, credenciales ni secretos.

## 2. Resumen ejecutivo

Genera datos sintéticos de clientes, pólizas, siniestros y pagos; los ingiere en Landing/Bronze, limpia en Silver, construye cinco datamarts Gold y ejecuta ocho controles de calidad. Se inspira conceptualmente en `Azure-Samples/data-factory-to-databricks`, sin copiar código ni recursos del sample.

## 3. Arquitectura

`Fuentes sintéticas → Landing → ADF-style orchestration → Bronze → Databricks-style transformations → Silver → Gold → Quality evidence`

| Local | Equivalente Azure |
|---|---|
| `adf_orchestrator.py` | Azure Data Factory pipeline |
| `data/landing|bronze|silver|gold` | ADLS Gen2 containers/zones |
| módulos pandas + Parquet | Databricks notebooks + Delta Lake |
| JSON de ejecución | ADF Monitor / Log Analytics |

## 4. Flujo técnico

Las actividades registran dependencias, duración, estado y error. Bronze agrega trazabilidad; Silver normaliza y deduplica; Gold publica `dim_customer`, `fact_policy`, `claims_by_product`, `premium_by_segment` y `payment_risk`.

## 5. Ejecución local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m py_compile app/*.py
python app/run_pipeline.py
```

Resultado esperado: `Pipeline PASSED: 8/8 checks, 5 Gold datamarts`.

## 6. Evidencia y calidad

La ejecución genera `output/pipeline_summary.json`, `output/data_quality_summary.json` y `output/data_quality_results.csv`. Los ocho checks validan unicidad, integridad referencial, disponibilidad y cantidad de datamarts. Datos y outputs se regeneran y están ignorados por Git.

## 7. Evolución segura a Azure

La migración futura usaría ADF, ADLS Gen2, Azure Databricks, Delta Lake, Key Vault, managed identities, Purview y presupuestos/alertas. Antes de desplegar: confirmar crédito gratuito, región, límites, auto-termination del clúster y eliminación completa de recursos. Ver `docs/`.
