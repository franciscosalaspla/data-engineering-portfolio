# Proyecto 17 - dbt Profesional para E-commerce

## Valor del proyecto

Este proyecto demuestra cómo construir un flujo profesional de Analytics Engineering con dbt y DuckDB para transformar datos crudos de e-commerce en modelos analíticos confiables.

El valor de negocio está en convertir archivos transaccionales simples en una capa de datos documentada, testeada y lista para reporting. Con este enfoque, un equipo puede responder preguntas como:

```text
¿Cuánto revenue genera cada cliente?
¿Qué productos tienen mayor margen?
¿Qué órdenes están completas, pendientes, canceladas o devueltas?
¿Cómo conservar el historial de cambios de clientes?
¿Cómo cargar una tabla de hechos de forma incremental?
```

Este tipo de arquitectura permite reducir errores en reportes, mejorar la trazabilidad de las transformaciones y separar claramente datos crudos, lógica de negocio y modelos finales de consumo.

## Resumen ejecutivo

Se construyó un proyecto dbt completo usando DuckDB como motor analítico local.

El flujo implementa la arquitectura:

```text
seeds raw
   -> staging
   -> intermediate
   -> marts
   -> snapshots
   -> tests y documentación
```

El proyecto incluye:

* Datos seed para simular fuentes crudas.
* Modelos SQL con `ref()` y configuración Jinja.
* Capa staging, intermediate y marts.
* Tests de calidad de datos en `schema.yml`.
* Documentación automática de modelos y columnas.
* Snapshot SCD Type 2 para clientes.
* Fact table incremental para órdenes.
* Ejecución validada con `dbt build` exitoso.

## Caso de negocio

La empresa simulada es un e-commerce que vende productos de tecnología, hogar, accesorios y muebles.

Los datos operacionales llegan en tres archivos CSV:

```text
raw_orders.csv
raw_customers.csv
raw_products.csv
```

Estos archivos registran órdenes, clientes y productos, pero no están listos para análisis directo. El proyecto transforma esas fuentes en modelos analíticos que permiten medir revenue, costo, margen, comportamiento de clientes y ventas por producto.

El objetivo es construir una base confiable para dashboards, reportes financieros y análisis de performance comercial.

## Arquitectura dbt

```text
17-dbt-professional-ecommerce/
|-- dbt_project.yml
|-- profiles.yml
|-- requirements.txt
|-- seeds/
|   |-- raw_orders.csv
|   |-- raw_customers.csv
|   `-- raw_products.csv
|-- models/
|   |-- staging/
|   |-- intermediate/
|   `-- marts/
|-- snapshots/
|   `-- customers_snapshot.sql
`-- README.md
```

DuckDB permite ejecutar el proyecto localmente sin depender de un Data Warehouse cloud. dbt aporta estructura, dependencias entre modelos, tests, documentación y una forma ordenada de transformar datos con SQL.

## Flujo staging → intermediate → marts

### Staging

La capa staging es 1:1 con los seeds. Su responsabilidad es mantener una representación limpia y tipada de la fuente, sin incorporar lógica de negocio pesada.

Transformaciones aplicadas:

```text
cast de tipos
trim de textos
lowercase para emails, segmentos y status
estandarización de nombres
```

Modelos:

```text
stg_orders
stg_customers
stg_products
```

### Intermediate

La capa intermediate concentra joins y lógica de negocio reutilizable.

Modelos:

```text
int_orders_enriched
int_customer_order_history
```

Aquí se calculan métricas y atributos preparados para marts:

```text
revenue = quantity * unit_price
cost = quantity * unit_cost
margin = revenue - cost
normalized_order_status
historial agregado por cliente
```

### Marts

La capa marts expone modelos finales para consumo analítico:

```text
fct_orders
dim_customers
dim_products
```

Estos modelos están listos para BI, reporting, análisis exploratorio o consumo por otros procesos analíticos.

## Seeds utilizados

Los seeds simulan tablas crudas de e-commerce:

| Seed | Descripción |
| --- | --- |
| `raw_orders.csv` | Órdenes transaccionales con cliente, producto, fecha, cantidad, precio, status y `updated_at` |
| `raw_customers.csv` | Clientes con país, segmento y timestamp de actualización |
| `raw_products.csv` | Catálogo de productos con categoría, costo unitario y flag activo |

Los seeds se cargan con:

```bash
dbt seed --profiles-dir .
```

## Modelos creados

| Capa | Modelo | Propósito |
| --- | --- | --- |
| staging | `stg_orders` | Limpieza y tipado de órdenes |
| staging | `stg_customers` | Limpieza y tipado de clientes |
| staging | `stg_products` | Limpieza y tipado de productos |
| intermediate | `int_orders_enriched` | Join de órdenes, clientes y productos con métricas de negocio |
| intermediate | `int_customer_order_history` | Agregados históricos por cliente |
| marts | `fct_orders` | Fact table incremental de órdenes |
| marts | `dim_customers` | Dimensión de clientes para análisis |
| marts | `dim_products` | Dimensión de productos para análisis |

## Tests de calidad de datos

El proyecto incluye tests en `schema.yml` para validar reglas críticas de calidad:

```text
unique y not_null en primary keys
relationships en foreign keys
accepted_values en status, customer_segment y active_flag
not_null en campos críticos como order_date, quantity, unit_price y revenue
```

Ejemplos de reglas implementadas:

```text
fct_orders.order_id debe ser único y no nulo
fct_orders.customer_id debe existir en dim_customers
fct_orders.product_id debe existir en dim_products
stg_orders.status solo acepta completed, pending, cancelled o returned
dim_customers.customer_segment solo acepta consumer, corporate, enterprise o small_business
```

Estas validaciones ayudan a detectar errores antes de que los modelos sean usados en reportes o análisis de negocio.

## Snapshot SCD Type 2

El snapshot `customers_snapshot` mantiene historial de cambios de clientes.

Configuración principal:

```text
unique_key = customer_id
strategy = timestamp
updated_at = updated_at
```

Esto permite capturar cambios en atributos como:

```text
customer_name
email
country
customer_segment
```

En un escenario real, este patrón permite analizar la evolución histórica de clientes sin sobrescribir información anterior.

## Modelo incremental

`fct_orders` está configurado como modelo incremental:

```sql
materialized='incremental'
unique_key='order_id'
incremental_strategy='delete+insert'
```

La carga incremental usa `updated_at`:

```sql
where updated_at > (
    select coalesce(max(updated_at), cast('1900-01-01' as timestamp))
    from {{ this }}
)
```

Esto evita reprocesar toda la fact table cuando solo llegan órdenes nuevas o actualizadas.

## Cómo ejecutar el proyecto

Desde la carpeta del proyecto:

```bash
cd 17-dbt-professional-ecommerce
pip install -r requirements.txt
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt build --profiles-dir .
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

Comandos esperados:

```bash
pip install -r requirements.txt
dbt seed
dbt run
dbt test
dbt build
dbt docs generate
```

Si se ejecuta sin `--profiles-dir .`, se debe copiar o adaptar `profiles.yml` al directorio local de perfiles de dbt.

## Outputs esperados

dbt genera una base local DuckDB:

```text
ecommerce_analytics.duckdb
```

Dentro de DuckDB se crean schemas similares a:

```text
raw
staging
intermediate
marts
snapshots
```

Modelos finales esperados:

```text
marts.fct_orders
marts.dim_customers
marts.dim_products
snapshots.customers_snapshot
```

La documentación se genera en:

```text
target/
```

`target/` y la base `.duckdb` son artefactos generados y no deberían versionarse.

## Decisiones técnicas

| Decisión | Motivo |
| --- | --- |
| DuckDB como adapter | Permite ejecutar dbt localmente sin infraestructura cloud |
| Seeds como fuente | Facilita reproducibilidad en GitHub y entrevistas técnicas |
| Staging 1:1 | Mantiene separación clara entre limpieza técnica y lógica de negocio |
| Intermediate para joins | Evita duplicar lógica compleja en marts |
| Marts como tablas finales | Entrega modelos listos para consumo analítico |
| Snapshot SCD Type 2 | Demuestra manejo de historial en dimensiones |
| Fact incremental | Demuestra un patrón común de carga eficiente |
| Tests en `schema.yml` | Documenta reglas de calidad junto al modelo |

## Cómo explicarlo en entrevista

Una forma clara de explicar el proyecto:

```text
Implementé un proyecto dbt profesional para un caso de e-commerce usando DuckDB.
Partí desde seeds que simulan datos raw de órdenes, clientes y productos.
Separé el flujo en staging, intermediate y marts para mantener una arquitectura clara.
En staging hice limpieza liviana y casteo de tipos.
En intermediate agregué joins y lógica de negocio para calcular revenue, cost y margin.
En marts creé una fact table incremental y dimensiones listas para reporting.
También agregué tests de calidad, documentación automática y un snapshot SCD Type 2 para historizar cambios de clientes.
```

Puntos técnicos defendibles:

```text
Por qué staging debe ser 1:1 con la fuente.
Por qué la lógica de negocio vive en intermediate.
Cómo funciona ref() para dependencias entre modelos.
Cómo dbt test protege la calidad de datos.
Cómo updated_at permite carga incremental.
Cómo un snapshot SCD Type 2 conserva historia de cambios.
```

## Mejoras futuras

Posibles extensiones:

```text
Agregar sources.yml si los datos vienen desde un warehouse real.
Separar ambientes dev/prod en profiles.yml.
Agregar exposures para dashboards BI.
Agregar macros reutilizables para normalización de status.
Agregar tests custom para validar revenue, cost y margin positivos.
Agregar CI con dbt build en GitHub Actions.
Migrar el proyecto a BigQuery, Snowflake o Databricks.
Agregar freshness checks para fuentes reales.
```
