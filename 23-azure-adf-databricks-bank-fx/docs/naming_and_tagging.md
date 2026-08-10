# Convenciones de nombres, regiones y etiquetas

## Propósito

Centralizar los nombres utilizados en el despliegue y las reglas necesarias para recrear recursos sin mezclarlos con credenciales o identificadores sensibles.

## Nombres confirmados

| Componente | Nombre | Función |
|---|---|---|
| Resource Group | `rg-project23-dev` | Agrupar recursos y costos |
| Storage Account | `stproject23dev2026` | Contenedores Landing, Bronze, Silver y Gold |
| Data Factory | `adf-project23-dev-2026` | Orquestar Databricks |
| Pipeline ADF | `pl_project23_medallion_orchestration` | Ejecutar el flujo Medallion |
| Databricks Workspace | `dbw-project23-dev-2026` | Procesamiento PySpark y Delta |
| Databricks compute | `compute-project23-dev-2026` | Cómputo single node |
| Unity Catalog | `dbw_project23_dev_2026` | Organizar esquemas y tablas |
| Key Vault | `kv-project23-dev-2026` | Custodiar credenciales SQL |
| Secret Scope | `project23-serving-dev` | Entregar secretos a Databricks |
| SQL Server | `sqlsrv-project23-serving-dev-2026` | Servidor lógico de serving |
| Azure SQL Database | `sqldb-project23-serving-dev-2026` | Modelo estrella relacional |

No se documentan IDs, endpoints, cuentas ni valores de secretos.

## Nombres dentro del flujo

| # | Etapa | Artefacto principal |
|---:|---|---|
| 1 | Landing → Bronze | `nb_01_landing_to_bronze` |
| 2 | Bronze → Silver | `nb_02_bronze_to_silver` |
| 3 | Silver → Gold | `nb_03_silver_to_gold` |
| 4 | Orquestación | `pl_project23_medallion_orchestration` |
| 5 | Azure SQL | `04_gold_to_azure_sql` y esquema `serving` |
| 6 | Power BI | `project23-banking-report.pbix` |
| 7 | Costos | Presupuesto aplicado al Resource Group |

## Datos y tablas

| Elemento | Nombre |
|---|---|
| Esquemas Lakehouse | `bronze`, `silver`, `gold` |
| Esquema Azure SQL | `serving` |
| Hecho Delta local | `fact_transactions` |
| Hecho Azure SQL/Power BI | `fact_transaction` |
| Dimensiones | `dim_date`, `dim_customer`, `dim_account`, `dim_merchant`, `dim_channel`, `dim_currency` |

Los nombres de los Linked Services del despliegue final no fueron recuperados. Los JSON bajo `adf/linkedService/` pertenecen al diseño inicial y no se presentan como exportación cloud.

## Regiones confirmadas

| Elemento | Región observada | Alcance de la afirmación |
|---|---|---|
| Azure SQL Server y Database | Central US | Confirmada en la evidencia de SQL |
| ADF Integration Runtime | East US 2 | Runtime observado durante la ejecución |
| Resto de recursos | No recuperada | No se completa por inferencia |

La región del Integration Runtime no demuestra la región de Data Factory ni de los demás recursos.

## Etiquetas

Confirmadas en Azure SQL:

```text
Project=project23
Environment=dev
```

Recomendadas para una futura recreación:

```text
Workload=data-engineering
CostControl=training
DataClassification=synthetic
Repository=data-engineering-portfolio
```

Las etiquetas recomendadas no se presentan como aplicadas actualmente.

## Reglas

- Usar minúsculas y guiones cuando el servicio lo permita.
- Incluir proyecto, entorno y propósito sin nombres personales.
- Mantener catálogos, esquemas, rutas y destinos como parámetros.
- Guardar credenciales en Key Vault y Secret Scope.
- No incluir correos, tenant IDs, subscription IDs, tokens ni contraseñas.
- Verificar disponibilidad, precio y región antes de recrear un recurso.
- Documentar el nombre real ejecutado; no reemplazarlo por una convención histórica.

El diseño inicial proponía nombres con sufijo regional. El despliegue real priorizó nombres más legibles; no se renombran retrospectivamente porque forman parte de la trazabilidad del proyecto.
