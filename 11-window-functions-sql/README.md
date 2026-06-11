# Window Functions SQL

Proyecto práctico de SQL avanzado enfocado en análisis de ventas usando Window Functions con DuckDB.

## Resumen ejecutivo

Analicé ventas de e-commerce usando funciones de ventana para identificar ranking de clientes, secuencia de compras, ventas acumuladas, comparación contra compras anteriores y variación mensual.

## Valor del proyecto

Este proyecto demuestra una habilidad clave para Data Engineering y Analytics: analizar datos manteniendo el detalle fila a fila, sin depender solo de agregaciones tradicionales como `GROUP BY`.

## Objetivo

Practicar funciones de ventana en SQL para resolver preguntas analíticas frecuentes:

* ¿Cuál es el ranking de clientes por ventas?
* ¿Cuál fue la compra anterior de cada cliente?
* ¿Cuál será la siguiente compra registrada?
* ¿Cuánto acumula cada cliente en ventas?
* ¿Qué productos lideran dentro de cada categoría?
* ¿Cómo cambian las ventas mes a mes?

## Stack

* SQL
* DuckDB
* Python
* pandas
* CSV
* Git / GitHub

## Estructura

```text
11-window-functions-sql/
├── data/
│   └── raw/
│       └── orders.csv
├── output/
│   ├── customer_sales_ranking.csv
│   ├── monthly_sales_comparison.csv
│   ├── next_purchase_by_customer.csv
│   ├── product_ranking_by_category.csv
│   ├── purchase_number_by_customer.csv
│   ├── running_total_sales_by_customer.csv
│   ├── sales_vs_category_average.csv
│   └── sales_vs_previous_purchase.csv
├── sql/
│   └── window_functions_analysis.sql
├── src/
│   └── run_window_functions.py
├── README.md
└── requirements.txt
```

## Dataset

El dataset simula órdenes de e-commerce.

Columnas principales:

| Columna         | Descripción               |
| --------------- | ------------------------- |
| `order_id`      | Identificador de la orden |
| `customer_id`   | Identificador del cliente |
| `customer_name` | Nombre del cliente        |
| `order_date`    | Fecha de compra           |
| `category`      | Categoría del producto    |
| `product`       | Producto comprado         |
| `sales`         | Monto de venta            |

## Consultas desarrolladas

| Función         | Objetivo                                           |
| --------------- | -------------------------------------------------- |
| `ROW_NUMBER()`  | Numerar compras por cliente                        |
| `RANK()`        | Crear ranking de clientes por venta total          |
| `DENSE_RANK()`  | Rankear productos dentro de cada categoría         |
| `LAG()`         | Comparar compra actual contra compra anterior      |
| `LEAD()`        | Identificar la siguiente compra del cliente        |
| `SUM() OVER()`  | Calcular ventas acumuladas por cliente             |
| `AVG() OVER()`  | Comparar ventas contra el promedio de su categoría |
| `LAG()` mensual | Comparar ventas mensuales contra el mes anterior   |

## Resultados principales

* Cliente con mayor venta total: `María García` con `2.950`.
* Segunda mayor venta total: `Carlos Díaz` con `1.850`.
* Categoría líder: `Electronics` con `5.250` en ventas.
* Producto líder en Electronics: `Laptop` con `1.200`.
* Abril fue el mes con mayor venta: `2.650`.
* Mayo muestra una baja frente a abril, pero el dataset llega solo hasta el 15 de mayo.

## Outputs generados

Los resultados se guardan en `output/`:

```text
customer_sales_ranking.csv
monthly_sales_comparison.csv
next_purchase_by_customer.csv
product_ranking_by_category.csv
purchase_number_by_customer.csv
running_total_sales_by_customer.csv
sales_vs_category_average.csv
sales_vs_previous_purchase.csv
```

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
cd 11-window-functions-sql
pip install -r requirements.txt
python src/run_window_functions.py
```

## Aprendizajes

* `ROW_NUMBER()` permite ordenar eventos por cliente.
* `RANK()` y `DENSE_RANK()` permiten construir rankings analíticos.
* `LAG()` permite comparar una fila con una anterior.
* `LEAD()` permite mirar el siguiente evento registrado.
* `SUM() OVER()` permite calcular acumulados sin perder detalle.
* `AVG() OVER()` permite comparar cada registro contra su grupo.
* Las Window Functions son clave para análisis temporal, comportamiento de clientes y métricas avanzadas.

## Explicación para entrevista

Construí un proyecto de SQL avanzado usando datos de ventas de e-commerce. Apliqué Window Functions como `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `SUM OVER` y `AVG OVER` para analizar ranking de clientes, secuencia de compras, ventas acumuladas y variación mensual. El proyecto demuestra cómo analizar comportamiento y evolución temporal sin perder el detalle de cada orden.
