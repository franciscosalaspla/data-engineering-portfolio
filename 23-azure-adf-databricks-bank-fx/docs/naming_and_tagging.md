# Convenciones Azure de nombres y etiquetas

## Estado del documento

El diseño inicial proponía Chile Central y un patrón con sufijo regional. El despliegue real utilizó nombres simplificados y disponibilidad regional distinta. Esta versión conserva ambos contextos: la convención prevista como antecedente y el inventario efectivamente validado.

## Inventario real confirmado

| Recurso o artefacto | Nombre confirmado | Región confirmada | Estado |
|---|---|---|---|
| Resource Group | `rg-project23-dev` | No aplica | Creado y utilizado |
| Storage Account | `stproject23dev2026` | No recuperada | Creado y utilizado |
| Data Factory | `adf-project23-dev-2026` | No recuperada | Publicado y ejecutado |
| Pipeline ADF | `pl_project23_medallion_orchestration` | No aplica | Ejecución correcta |
| Databricks Workspace | `dbw-project23-dev-2026` | No recuperada | Creado y utilizado |
| Databricks compute | `compute-project23-dev-2026` | Workspace | Detenido al cierre |
| Unity Catalog | `dbw_project23_dev_2026` | Workspace | Bronze, Silver y Gold |
| Key Vault | `kv-project23-dev-2026` | No recuperada | Creado y utilizado |
| Secret Scope | `project23-serving-dev` | Workspace | Dos secretos configurados |
| SQL Server | `sqlsrv-project23-serving-dev-2026` | Central US | Creado y utilizado |
| Azure SQL Database | `sqldb-project23-serving-dev-2026` | Central US | `Paused` al cierre |

La evidencia ADF muestra `AutoResolveIntegrationRuntime (East US 2)` durante las actividades. Eso identifica el runtime de integración observado, no demuestra por sí solo la región de todos los recursos. No se completan regiones faltantes por inferencia.

## Mapeo entre diseño inicial y despliegue

| Tipo | Nombre previsto históricamente | Nombre real |
|---|---|---|
| Resource Group | `rg-p23-bankfx-dev-clc` | `rg-project23-dev` |
| Data Factory | `adf-p23-bankfx-dev-clc-{suffix}` | `adf-project23-dev-2026` |
| Storage Account | `stp23bankfxdev{suffix}` | `stproject23dev2026` |
| Key Vault | `kv-p23-bankfx-dev-{suffix}` | `kv-project23-dev-2026` |
| Databricks Workspace | `dbw-p23-bankfx-dev-clc-{suffix}` | `dbw-project23-dev-2026` |
| Azure SQL Server | `sql-p23-bankfx-dev-clc-{suffix}` | `sqlsrv-project23-serving-dev-2026` |
| Azure SQL Database | `sqldb-p23-bankfx-dev` | `sqldb-project23-serving-dev-2026` |

La convención real prioriza legibilidad para un proyecto de entrenamiento. Los nombres no se cambian retrospectivamente porque ya identifican recursos ejecutados y evidencia histórica.

## Nombres de datos y orquestación

| Elemento | Valor cloud confirmado |
|---|---|
| Pipeline | `pl_project23_medallion_orchestration` |
| Actividad 1 | `nb_01_landing_to_bronze` |
| Actividad 2 | `nb_02_bronze_to_silver` |
| Actividad 3 | `nb_03_silver_to_gold` |
| Catálogo | `dbw_project23_dev_2026` |
| Esquemas Lakehouse | `bronze`, `silver`, `gold` |
| Esquema Azure SQL | `serving` |
| Hecho Delta local | `fact_transactions` |
| Hecho Azure SQL/Power BI | `fact_transaction` |

Los nombres de los Linked Services de la ejecución cloud no quedaron recuperados. Los archivos bajo `adf/linkedService/` pertenecen al diseño inicial y no deben presentarse como exportación del despliegue final.

## Etiquetas observadas y recomendadas

La evidencia de Azure SQL confirma al menos:

```text
Project=project23
Environment=dev
```

Para futuros despliegues se recomienda completar un conjunto consistente:

```text
Project=project23
Environment=dev
Workload=data-engineering
CostControl=training
DataClassification=synthetic
Repository=data-engineering-portfolio
```

No se afirma que todas esas etiquetas estén aplicadas actualmente.

## Reglas

- Usar minúsculas y guiones donde el servicio lo permita.
- Mantener el entorno (`dev`) y el propósito del recurso en el nombre.
- No incluir nombres personales, correos, tenant IDs, subscription IDs o credenciales.
- Pasar catálogos, esquemas, paths y nombres de destino mediante parámetros.
- Mantener secretos fuera del repositorio mediante Key Vault y Secret Scope.
- No reemplazar nombres reales por la convención histórica en documentación de evidencia.
- Verificar disponibilidad, precio y región antes de recrear un recurso; Central US solo está confirmado para Azure SQL.
