# ETL Simple con Python

Proyecto práctico de ingeniería de datos enfocado en construir un pipeline ETL simple usando Python y Pandas.

El objetivo es extraer datos desde un archivo CSV, explorar su calidad, limpiar valores nulos y duplicados, corregir tipos de datos, calcular métricas de negocio y guardar resultados en formatos CSV y Parquet.

## Objetivo del proyecto

Construir un pipeline ETL que permita:

- Cargar datos desde un archivo CSV.
- Explorar estructura, nulos, duplicados y tipos de datos.
- Limpiar valores faltantes.
- Eliminar registros duplicados.
- Convertir fechas a formato correcto.
- Calcular métricas de negocio.
- Guardar outputs en CSV y Parquet.

## Caso de negocio

Este proyecto simula un escenario simple de e-commerce donde se procesan órdenes de compra para generar información útil para análisis comercial.

A partir de los datos de órdenes, se responden preguntas como:

- ¿Cuáles son los clientes con mayor gasto?
- ¿Cuáles son los productos más vendidos?
- ¿Cómo evolucionan las ventas por mes?

## Stack utilizado

- Python
- Pandas
- CSV
- Parquet
- Git / GitHub
- GitHub Codespaces

````markdown
## Estructura del proyecto

```text
07-etl-simple-python/
├── data/
│   └── raw/
│       └── ecommerce_orders.csv
├── output/
│   ├── clean_orders.csv
│   ├── clean_orders.parquet
│   ├── sales_by_month.csv
│   ├── top_customers.csv
│   └── top_products.csv
├── src/
│   └── etl.py
├── README.md
└── requirements.txt
