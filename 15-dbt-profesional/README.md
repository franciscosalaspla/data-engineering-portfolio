# Proyecto dbt Profesional con DuckDB

Proyecto práctico de Analytics Engineering para transformar datos crudos de e-commerce en modelos analíticos usando dbt y DuckDB.

## Cómo contar este proyecto en una entrevista

### Hook

Construí un proyecto dbt local que transforma archivos CSV crudos en modelos analíticos organizados, testeados y documentados.

### Situación

Los datos de e-commerce venían en archivos CSV separados: customers, orders, order_items y products.

Estos datos tenían problemas típicos de una fuente cruda: valores nulos, duplicados y campos que necesitaban limpieza antes de ser usados en análisis.

### Tarea

Diseñar una estructura dbt profesional con capas separadas:

* raw sources
* staging
* marts
* tests
* documentation

El objetivo fue dejar modelos analíticos listos para análisis, reporting o carga a un Data Warehouse.

### Acciones

Implementé un proyecto dbt usando DuckDB como motor local.

Se crearon 4 modelos staging:

* stg_customers
* stg_orders
* stg_order_items
* stg_products

Y 3 modelos marts:

* dim_customers
* dim_products
* fct_order_items

En staging se limpiaron y estandarizaron datos usando:

* lower(trim()) para limpiar texto.
* try_cast() para convertir tipos de forma segura.

En marts se construyeron modelos analíticos filtrando registros inválidos y manteniendo relaciones confiables entre clientes, productos y ventas.

### Resultados

El pipeline dbt construyó correctamente 7 modelos:

* dbt run: PASS=7, ERROR=0

También se ejecutaron 18 tests:

* dbt test: PASS=15, ERROR=3

Los 3 errores quedaron en staging y reflejan problemas reales de datos crudos:

| Modelo          | Columna     | Problema detectado |
| --------------- | ----------- | -----------------: |
| stg_order_items | order_id    |           33 nulos |
| stg_order_items | product_id  |           16 nulos |
| stg_orders      | customer_id |            6 nulos |

Los modelos finales marts pasaron correctamente sus tests, incluyendo unicidad, no nulos y relaciones.

## Modelo analítico construido

El proyecto construye los siguientes modelos finales:

* dim_customers
* dim_products
* fct_order_items

La tabla de hechos fct_order_items representa ventas a nivel de item de orden.

## Tests implementados

Se agregaron tests dbt para validar:

* not_null
* unique
* relationships

Ejemplos:

* customer_id no nulo.
* product_id único.
* order_item_id único.
* fct_order_items.customer_id relacionado con dim_customers.
* fct_order_items.product_id relacionado con dim_products.

## Documentación dbt

Se generó documentación automática con:

dbt docs generate --profiles-dir .

La carpeta target/ no se sube al repositorio porque es generada automáticamente por dbt.

## Stack utilizado

* dbt Core
* dbt-duckdb
* DuckDB
* SQL
* CSV
* Git / GitHub
* GitHub Codespaces

Versiones usadas:

* dbt-core: 1.11.11
* dbt-duckdb: 1.10.1

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
cd 15-dbt-profesional
pip install -r requirements.txt
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
```

## Aprendizajes

* Cómo estructurar un proyecto dbt profesional.
* Cómo separar modelos staging y marts.
* Cómo usar source() para leer datos crudos.
* Cómo usar ref() para conectar modelos.
* Cómo aplicar tests de calidad con dbt.
* Cómo documentar modelos automáticamente.
* Cómo usar DuckDB como motor local.
* Cómo transformar datos crudos en modelos confiables para reporting.

## Estructura del proyecto

```text
15-dbt-profesional/
├── data/raw/
├── models/
│   ├── staging/
│   ├── marts/
│   └── schema.yml
├── dbt_project.yml
├── profiles.yml
├── requirements.txt
├── .gitignore
└── README.md
```

