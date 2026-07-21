# Mapeo de arquitectura Azure

| Laboratorio local | Implementación futura |
|---|---|
| Orquestador Python | Azure Data Factory |
| Carpetas Medallion | ADLS Gen2 |
| pandas/Parquet | Azure Databricks + Delta Lake |
| JSON de evidencia | ADF Monitor + Log Analytics |
| Variables locales | Managed Identity + Key Vault |

El laboratorio demuestra responsabilidades y contratos de datos; no afirma un despliegue cloud real.
