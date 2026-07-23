# Convenciones Azure de nombres y etiquetas

## Región acordada

| Uso | Valor |
|---|---|
| Nombre Azure | `chilecentral` |
| Nombre visible | `Chile Central` |
| Abreviación | `clc` |

La disponibilidad, cuota y precio de cada servicio deberán verificarse en la suscripción antes de desplegar. Este documento no confirma que los recursos ya existan.

## Patrón general

```text
<resource-type>-p23-bankfx-<environment>-<region>-<suffix>
```

El sufijo global será calculado posteriormente por Bicep para los recursos que requieran nombres únicos. No se genera en el Hito 1.

## Nombres base

| Recurso | Nombre previsto |
|---|---|
| Resource Group | `rg-p23-bankfx-dev-clc` |
| Data Factory | `adf-p23-bankfx-dev-clc-{suffix}` |
| Storage Account | `stp23bankfxdev{suffix}` |
| Key Vault reservado | `kv-p23-bankfx-dev-{suffix}` |
| Databricks Workspace | `dbw-p23-bankfx-dev-clc-{suffix}` |
| Azure SQL Server | `sql-p23-bankfx-dev-clc-{suffix}` |
| Azure SQL Database | `sqldb-p23-bankfx-dev` |

Key Vault no se desplegará en el MVP mientras no existan secretos reales. Su nombre se reserva para mantener coherencia si un hito futuro justifica su uso.

## Nombres de datos y orquestación

| Artefacto | Convención | Ejemplo |
|---|---|---|
| ADF pipeline | `pl_<action>_<domain>` | `pl_ingest_bankfx_sources` |
| Linked service | `ls_<technology>_<purpose>` | `ls_adls_bankfx` |
| Dataset | `ds_<format>_<entity>` | `ds_csv_transactions` |
| Notebook driver | `nb_<layer>_<purpose>` | `nb_run_bankfx_medallion` |
| Delta table | `<layer>.<entity>` | `silver.transactions` |
| SQL table | `<schema>.<entity>` | `mart.fact_transactions` |

## Etiquetas obligatorias

```text
project=p23-bankfx
environment=dev
workload=data-engineering
managed-by=bicep
cost-control=training
data-classification=synthetic
```

Etiquetas futuras recomendadas:

- `owner-role=data-engineer` sin correos personales;
- `expires-on=<YYYY-MM-DD>` para la ventana temporal;
- `repository=data-engineering-portfolio`;
- `region-code=clc`.

## Reglas

- Usar minúsculas y guiones donde el servicio lo permita.
- No incluir correos, nombres personales, tenant IDs o subscription IDs.
- No guardar sufijos calculados como constantes en el código de transformación.
- Pasar nombres, catálogos, schemas y paths mediante parámetros de entorno.
- Mantener las etiquetas en un único objeto Bicep reutilizable durante el Hito 2.
