# Data Warehouse Dimensional con DuckDB

Proyecto práctico de Ingeniería de Datos enfocado en diseñar e implementar un Data Warehouse dimensional con modelo estrella usando datos transaccionales de e-commerce.

## Problema del proyecto

Los datos originales vienen desde un modelo operacional de e-commerce, separado en archivos como órdenes, items de órdenes, clientes, productos y categorías.

Ese modelo sirve para registrar transacciones, pero no es ideal para análisis. Para responder preguntas de negocio como ventas por mes, ventas por producto o ventas por segmento, conviene transformar esos datos en un modelo analítico.

## Qué construí

Construí un Data Warehouse local en DuckDB usando un modelo estrella.

El modelo final tiene:

```text
Dimensiones:
- dim_date
- dim_customers
- dim_products

Tabla de hechos:
- fact_order_items
```

El grano de la tabla de hechos es:

```text
1 fila = 1 producto vendido dentro de una orden
```

Elegí `order_item` como grano porque permite analizar ventas a nivel de producto, cantidad, precio y subtotal. Si la fact estuviera solo a nivel de orden, se perdería el detalle de productos vendidos.

## Flujo del pipeline

El proyecto sigue este flujo:

```text
CSV transaccionales
        ↓
Tablas raw en DuckDB
        ↓
Tablas staging deduplicadas
        ↓
Dimensiones
        ↓
Tabla de hechos
        ↓
Validaciones del modelo
```

## Capas del modelo

### 1. Raw

Carga directa de los CSV originales:

```text
raw_orders
raw_order_items
raw_customers
raw_products
raw_categories
```

Esta capa conserva los datos como vienen desde el origen.

### 2. Staging

Capa intermedia para deduplicar datos antes de construir el modelo dimensional:

```text
stg_orders
stg_order_items
stg_customers
stg_products
stg_categories
```

Esta capa fue necesaria porque los datos originales tenían duplicados. Sin staging, los JOINs podían multiplicar filas en la tabla de hechos e inflar las métricas.

### 3. Modelo dimensional

Desde staging se construyen las dimensiones y la fact table:

```text
dim_date
dim_customers
dim_products
fact_order_items
```

## Diseño del modelo estrella

### `dim_date`

Dimensión de fechas para análisis temporal.

Incluye:

```text
date_key
full_date
year
quarter
month
month_name
day
day_of_week
is_weekend
```

### `dim_customers`

Dimensión de clientes.

Incluye:

```text
customer_key
customer_id
first_name
last_name
email
city
country
segment
registration_date
is_verified
accepts_marketing
```

### `dim_products`

Dimensión de productos.

Incluye información del producto y su categoría.

```text
product_key
product_id
sku
product_name
category_name
price
cost
is_active
created_at
updated_at
```

### `fact_order_items`

Tabla central del modelo.

Incluye claves hacia dimensiones y métricas numéricas:

```text
order_item_key
order_item_id
order_id
customer_key
product_key
date_key
quantity
unit_price
item_subtotal
discount_percent
shipping_cost
tax_amount
total_amount
```

`order_id` se mantiene como identificador de trazabilidad de la orden original.

## Validaciones del modelo

La validación principal fue asegurar que la fact table no duplicara filas.

| Tabla              | Total filas | IDs únicos |
| ------------------ | ----------: | ---------: |
| `stg_order_items`  |         310 |        310 |
| `fact_order_items` |         310 |        310 |
| `dim_date`         |          92 |         92 |
| `dim_customers`    |          34 |         34 |
| `dim_products`     |          20 |         20 |

Resultado clave:

```text
fact_order_items = 310 filas
distinct order_item_id = 310
```

Esto confirma que el modelo respeta el grano definido:

```text
1 fila = 1 order_item único
```

## Hallazgos de calidad

Además de construir el modelo, ejecuté validaciones para detectar filas de la fact table sin match contra sus dimensiones.

| Validación                  | Resultado |
| --------------------------- | --------: |
| Filas sin fecha asociada    |        68 |
| Filas sin cliente asociado  |        71 |
| Filas sin producto asociado |        33 |

Impacto en ventas:

| Métrica                      |     Monto |
| ---------------------------- | --------: |
| Ventas sin fecha asociada    | 719717.22 |
| Ventas sin cliente asociado  | 719087.41 |
| Ventas sin producto asociado |  17834.00 |

Este hallazgo muestra que un Data Warehouse no solo debe construir tablas, también debe validar la integridad de las relaciones antes de confiar en los reportes.

## Problemas detectados y solución

### Fechas con formatos mixtos

Los datos venían con formatos distintos:

```text
YYYY-MM-DD
MM/DD/YYYY
DD-MM-YYYY
YYYY/MM/DD
```

Se resolvió usando conversiones robustas con `TRY_CAST`, `TRY_STRPTIME` y `COALESCE`.

### Duplicados en tablas origen

Se detectaron duplicados en tablas transaccionales. Para evitar duplicación de métricas, se creó una capa staging deduplicada antes de construir dimensiones y fact table.

### Registros sin match contra dimensiones

Algunas filas de la fact no tenían relación válida con fecha, cliente o producto. En vez de ocultarlo, se generaron controles de calidad para medir el impacto.

## Queries de validación analítica

Las queries analíticas se usaron para comprobar que el modelo permite responder preguntas de negocio.

Se generaron outputs como:

```text
sales_by_month.csv
top_products_by_sales.csv
weekend_vs_weekday_sales.csv
sales_by_customer_segment.csv
```

Estas queries no son el foco principal del proyecto; su rol es validar que el modelo dimensional permite análisis sobre tiempo, productos y clientes.

## Stack utilizado

```text
Python
DuckDB
SQL
pandas
CSV
Git / GitHub
GitHub Codespaces
```

## Cómo ejecutar

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Construir el Data Warehouse:

```bash
python src/build_warehouse.py
```

Ejecutar queries analíticas:

```bash
python src/run_analytics.py
```

Ejecutar validaciones de calidad:

```bash
python src/run_quality_checks.py
```

## Aprendizajes

* Diseñar un modelo estrella.
* Definir correctamente el grano de una fact table.
* Separar datos raw, staging y modelo dimensional.
* Usar surrogate keys y business keys.
* Evitar duplicación de métricas en JOINs.
* Crear una dimensión de fecha útil para análisis.
* Validar integridad referencial entre fact y dimensiones.
* Usar DuckDB como motor analítico local para prototipar un Data Warehouse.

## Explicación para entrevista

Construí un Data Warehouse dimensional en DuckDB usando datos transaccionales de e-commerce. Definí el grano de la fact table a nivel de `order_item`, creé dimensiones de fecha, clientes y productos, y cargué una tabla de hechos con métricas de ventas.

Durante el desarrollo detecté duplicados y fechas con formatos mixtos, por lo que agregué una capa staging para preparar los datos antes de construir el modelo. También validé que la fact table no duplicara registros y agregué controles de calidad para detectar ventas sin match contra dimensiones.

El foco del proyecto fue demostrar el diseño e implementación de un modelo estrella, no solo ejecutar queries.

## Estructura del proyecto

```text
13-data-warehouse-dimensional/
├── data/
│   └── raw/
│       ├── ecommerce_categories.csv
│       ├── ecommerce_customers.csv
│       ├── ecommerce_order_items.csv
│       ├── ecommerce_orders.csv
│       └── ecommerce_products.csv
├── output/
│   ├── ecommerce_warehouse.duckdb
│   ├── sales_by_month.csv
│   ├── top_products_by_sales.csv
│   ├── weekend_vs_weekday_sales.csv
│   ├── sales_by_customer_segment.csv
│   ├── fact_row_validation.csv
│   ├── missing_dimension_keys.csv
│   └── sales_without_dimensions.csv
├── sql/
│   ├── create_star_schema.sql
│   ├── analytics_queries.sql
│   └── data_quality_checks.sql
├── src/
│   ├── build_warehouse.py
│   ├── run_analytics.py
│   └── run_quality_checks.py
├── docs/
├── README.md
└── requirements.txt
```
