# Nombres, regiones y convenciones

Este documento define **cómo nombrar y organizar** los componentes del proyecto sin publicar identificadores reales de infraestructura.

## Hito 1 — Landing → Bronze

### 1.1 Recursos

| Componente | Patrón recomendado |
|---|---|
| Resource Group | `rg-<proyecto>-<entorno>` |
| Storage Account | `st<proyecto><entorno><sufijo>` |
| Contenedores | `landing`, `bronze`, `silver`, `gold` |
| Databricks Workspace | `dbw-<proyecto>-<entorno>` |
| Compute | `compute-<proyecto>-<entorno>` |
| Unity Catalog | `<proyecto>_<entorno>` |

### 1.2 Regla

Landing y Bronze deben conservar nombres simples, metadata técnica y separación por entorno.

## Hito 2 — Bronze → Silver

### 2.1 Tablas Silver

| Entidad | Nombre versionado |
|---|---|
| Clientes | `silver_customers` |
| Cuentas | `silver_accounts` |
| Tasas FX | `silver_fx_rates` |
| Transacciones | `silver_transactions` |

## Hito 3 — Silver → Gold

### 3.1 Dimensiones

`dim_date` · `dim_customer` · `dim_account` · `dim_merchant` · `dim_channel` · `dim_currency`

### 3.2 Tabla de hechos

| Capa | Nombre |
|---|---|
| Delta local | `fact_transactions` |
| Azure SQL y Power BI | `fact_transaction` |

El mapeo mantiene el historial de la implementación local y hace explícito el contrato de serving.

## Hito 4 — Orquestación con Azure Data Factory

### 4.1 Pipeline

| Elemento | Nombre lógico |
|---|---|
| Pipeline | `pl_project23_medallion_orchestration` |
| Actividad 1 | `nb_01_landing_to_bronze` |
| Actividad 2 | `nb_02_bronze_to_silver` |
| Actividad 3 | `nb_03_silver_to_gold` |

### 4.2 Linked Services

Los Linked Services siguen el patrón `ls-<servicio>-<propósito>`. Sus nombres desplegados, endpoints e identificadores no se publican.

## Hito 5 — Serving en Azure SQL

### 5.1 Seguridad

| Componente | Patrón recomendado |
|---|---|
| Key Vault | `kv-<proyecto>-<entorno>` |
| Secret Scope | `<proyecto>-serving-<entorno>` |
| SQL Server | `sql-<proyecto>-<entorno>` |
| SQL Database | `sqldb-<proyecto>-serving-<entorno>` |
| Esquema | `serving` |

Los nombres y valores de secretos nunca se versionan.

## Hito 6 — Consumo en Power BI

### 6.1 Artefactos

| Elemento | Convención |
|---|---|
| Workspace | Área personal o workspace del proyecto |
| Informe | `<proyecto>-banking-report.pbix` |
| Modelo | Mismos nombres de tablas que Azure SQL |

## Hito 7 — Monitorización y costos

### 7.1 Alcance

Cost Management debe operar sobre el grupo de recursos completo para reunir el costo de almacenamiento, orquestación, procesamiento, serving y seguridad.

### 7.2 Etiquetas

```text
Project=<proyecto>
Environment=<entorno>
Workload=data-engineering
CostControl=training
DataClassification=synthetic
Repository=data-engineering-portfolio
```

Las etiquetas `Project` y `Environment` fueron utilizadas. Las demás forman parte del estándar recomendado para una recreación futura.

## Estrategia de regiones

- seleccionar regiones según disponibilidad, precio y compatibilidad del servicio;
- mantener juntos los recursos con mayor transferencia de datos cuando sea posible;
- no inferir la región de un recurso desde el Integration Runtime de ADF;
- documentar excepciones cuando un servicio requiera otra región;
- verificar disponibilidad y precio antes de recrear la infraestructura.

## Reglas generales

- usar minúsculas y guiones donde Azure lo permita;
- incluir proyecto, propósito y entorno;
- evitar nombres personales, correos, tenant IDs, subscription IDs o endpoints;
- parametrizar catálogos, esquemas, rutas y destinos;
- mantener credenciales en Key Vault y Secret Scope;
- distinguir nombres lógicos versionados de nombres físicos desplegados.
