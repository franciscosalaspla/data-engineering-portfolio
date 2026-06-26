# Proyecto 17 - dbt Professional Ecommerce

## 1. Valor del proyecto

Este proyecto demuestra como construir un flujo profesional de Analytics Engineering con dbt y DuckDB para transformar datos crudos de e-commerce en modelos confiables para reporting.

El valor de negocio esta en convertir archivos transaccionales simples en una capa analitica documentada, testeada y mantenible. Este tipo de proyecto permite responder preguntas como:

```text
Cuanto revenue genera cada cliente?
Que productos tienen mayor margen?
Que ordenes estan completas, pendientes, canceladas o devueltas?
Como mantener historial de cambios de clientes?
Como cargar una fact table de forma incremental?
```

## 2. Resumen ejecutivo

Se construyo un proyecto dbt completo usando DuckDB como motor local.

El flujo implementa:

```text
seeds raw
   -> staging
   -> intermediate
   -> marts
   -> snapshots
   -> tests y documentacion
```

El proyecto incluye datos seed, modelos SQL con `ref()`, logica Jinja, tests de calidad, documentacion en `schema.yml`, snapshot SCD Type 2 y una fact table incremental.

## 3. Caso de negocio

La empresa simulada es un e-commerce que vende productos de tecnologia, hogar, accesorios y muebles.

Los datos operacionales llegan en tres archivos:

```text
raw_orders.csv
raw_customers.csv
raw_products.csv
```

Estos datos sirven para registrar operaciones, pero no estan listos para analisis. El proyecto crea una capa analitica que permite medir revenue, costo, margen, comportamiento de clientes y ventas por producto.

## 4. Arquitectura dbt

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

DuckDB permite ejecutar el proyecto localmente sin depender de un warehouse cloud. dbt aporta estructura, dependencias entre modelos, testing y documentacion automatica.

## 5. Flujo staging -> intermediate -> marts

### Staging

La capa staging es 1:1 con los seeds. Solo realiza limpieza basica:

```text
cast de tipos
trim de textos
lowercase para emails y status
estandarizacion de nombres
```

Modelos:

```text
stg_orders
stg_customers
stg_products
```

### Intermediate

La capa intermediate concentra joins y logica de negocio.

Modelos:

```text
int_orders_enriched
int_customer_order_history
```

Aqui se calculan:

```text
revenue = quantity * unit_price
cost = quantity * unit_cost
margin = revenue - cost
normalized_order_status
historial agregado por cliente
```

### Marts

La capa marts expone modelos finales para consumo analitico:

```text
fct_orders
dim_customers
dim_products
```

Estos modelos estan listos para BI, reporting o analisis exploratorio.

## 6. Seeds utilizados

Los seeds simulan tablas crudas de e-commerce:

| Seed | Descripcion |
| --- | --- |
| `raw_orders.csv` | Ordenes transaccionales con cliente, producto, fecha, cantidad, precio, status y updated_at |
| `raw_customers.csv` | Clientes con pais, segmento y timestamp de actualizacion |
| `raw_products.csv` | Catalogo de productos con categoria, costo unitario y flag activo |

Los seeds se cargan con:

```bash
dbt seed --profiles-dir .
```

## 7. Modelos creados

| Capa | Modelo | Proposito |
| --- | --- | --- |
| staging | `stg_orders` | Limpieza y tipado de ordenes |
| staging | `stg_customers` | Limpieza y tipado de clientes |
| staging | `stg_products` | Limpieza y tipado de productos |
| intermediate | `int_orders_enriched` | Join de ordenes, clientes y productos con metricas |
| intermediate | `int_customer_order_history` | Agregados historicos por cliente |
| marts | `fct_orders` | Fact table incremental de ordenes |
| marts | `dim_customers` | Dimension de clientes para analisis |
| marts | `dim_products` | Dimension de productos para analisis |

## 8. Tests de calidad de datos

El proyecto incluye tests en `schema.yml` para validar:

```text
unique y not_null en primary keys
relationships en foreign keys
accepted_values en status, customer_segment y active_flag
not_null en campos criticos como order_date, quantity, unit_price y revenue
```

Ejemplos de reglas:

```text
fct_orders.order_id debe ser unico y no nulo
fct_orders.customer_id debe existir en dim_customers
fct_orders.product_id debe existir en dim_products
stg_orders.status solo acepta completed, pending, cancelled o returned
dim_customers.customer_segment solo acepta consumer, corporate, enterprise o small_business
```

## 9. Snapshot SCD Type 2

El snapshot `customers_snapshot` mantiene historial de cambios de clientes.

Configuracion principal:

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

En un escenario real, esto ayuda a responder preguntas historicas sin sobrescribir informacion anterior.

## 10. Modelo incremental

`fct_orders` esta configurado como modelo incremental:

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

Esto evita reprocesar toda la fact table cuando solo llegan ordenes nuevas o actualizadas.

## 11. Como ejecutar el proyecto

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

Si se ejecuta sin `--profiles-dir .`, copiar o adaptar `profiles.yml` al directorio dbt local del usuario.

## 12. Outputs esperados

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

La documentacion se genera en:

```text
target/
```

`target/` y la base `.duckdb` son artefactos generados y no deberian versionarse.

## 13. Decisiones tecnicas

| Decision | Motivo |
| --- | --- |
| DuckDB como adapter | Permite ejecutar dbt localmente sin infraestructura cloud |
| Seeds como fuente | Facilita reproducibilidad en GitHub y entrevistas |
| Staging 1:1 | Mantiene separacion clara entre limpieza tecnica y logica de negocio |
| Intermediate para joins | Evita duplicar logica compleja en marts |
| Marts como tablas finales | Entrega modelos listos para consumo analitico |
| Snapshot SCD2 | Demuestra manejo de historicos de dimensiones |
| Fact incremental | Demuestra patron comun de carga eficiente |
| Tests en schema.yml | Documenta reglas de calidad junto al modelo |

## 14. Como explicarlo en entrevista

Construiria la explicacion asi:

```text
Implemente un proyecto dbt profesional para un caso de e-commerce usando DuckDB.
Parti desde seeds que simulan datos raw de ordenes, clientes y productos.
Separe el flujo en staging, intermediate y marts para mantener una arquitectura clara.
En staging hice limpieza liviana y casteo de tipos.
En intermediate agregue joins y logica de negocio para calcular revenue, cost y margin.
En marts cree una fact table incremental y dimensiones listas para reporting.
Tambien agregue tests de calidad, documentacion automatica y un snapshot SCD Type 2 para historizar cambios de clientes.
```

Puntos tecnicos defendibles:

```text
Por que staging debe ser 1:1 con la fuente.
Por que la logica de negocio vive en intermediate.
Como funciona ref() para dependencias entre modelos.
Como dbt test protege la calidad de datos.
Como updated_at permite carga incremental.
Como un snapshot SCD2 conserva historia de cambios.
```

## 15. Mejoras futuras

Posibles extensiones:

```text
Agregar sources.yml si los datos vienen desde un warehouse real.
Separar ambientes dev/prod en profiles.yml.
Agregar exposures para dashboards BI.
Agregar macros reutilizables para normalizacion de status.
Agregar tests custom para revenue, cost y margin positivos.
Agregar CI con dbt build en GitHub Actions.
Migrar el proyecto a BigQuery, Snowflake o Databricks.
Agregar freshness checks para fuentes reales.
```
