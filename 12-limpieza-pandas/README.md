# Limpieza de Datos E-commerce con Pandas

Proyecto práctico de limpieza de datos usando Python y pandas sobre un dataset de e-commerce generado desde la plataforma de práctica.

## Valor del proyecto

Este proyecto demuestra una habilidad base en Data Engineering: preparar datos crudos antes de usarlos en análisis, reporting o pipelines posteriores. Se trabajó con tablas reales de un modelo e-commerce, aplicando limpieza de texto, conversión de fechas, corrección de tipos numéricos, manejo de nulos y eliminación de duplicados.

## Objetivo

Limpiar las principales tablas de un dataset de e-commerce y generar archivos procesados listos para análisis.

Tablas trabajadas:

* `ecommerce_customers.csv`
* `ecommerce_orders.csv`
* `ecommerce_reviews.csv`

## Stack

* Python
* pandas
* CSV
* Git / GitHub
* GitHub Codespaces

## Estructura

```text
12-limpieza-pandas/
├── data/
│   ├── raw/
│   │   ├── ecommerce_customers.csv
│   │   ├── ecommerce_orders.csv
│   │   └── ecommerce_reviews.csv
│   └── processed/
│       ├── clean_customers.csv
│       ├── clean_orders.csv
│       └── clean_reviews.csv
├── output/
│   └── cleaning_summary.csv
├── src/
│   └── clean_ecommerce_data.py
├── README.md
└── requirements.txt
```

## Proceso de limpieza

### Customers

Se aplicaron las siguientes reglas:

* Normalización de texto en nombres, email, ciudad, país y segmento.
* Conversión de fechas con `pd.to_datetime`.
* Eliminación de duplicados por `customer_id`.
* Eliminación de registros sin `customer_id`.

### Orders

Se aplicaron las siguientes reglas:

* Normalización de texto en estado de orden, método de pago y método de envío.
* Conversión de `order_date` a formato fecha.
* Conversión de columnas monetarias a formato numérico.
* Relleno de nulos en montos con `0`.
* Eliminación de duplicados por `order_id`.
* Eliminación de registros sin `order_id`.

### Reviews

Se aplicaron las siguientes reglas:

* Limpieza de espacios en comentarios.
* Conversión de `rating` a formato numérico.
* Conversión de `created_at` a formato fecha.
* Relleno de comentarios vacíos con `no comment`.
* Eliminación de duplicados por `review_id`.
* Eliminación de registros sin `review_id`.

## Resultados

Resumen de limpieza generado en `output/cleaning_summary.csv`:

| Tabla     | Filas iniciales | Filas finales | Filas eliminadas |
| --------- | --------------: | ------------: | ---------------: |
| customers |              35 |            34 |                1 |
| orders    |             103 |           100 |                3 |
| reviews   |             103 |           100 |                3 |

## Outputs generados

```text
data/processed/clean_customers.csv
data/processed/clean_orders.csv
data/processed/clean_reviews.csv
output/cleaning_summary.csv
```

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
cd 12-limpieza-pandas
pip install -r requirements.txt
python src/clean_ecommerce_data.py
```

## Aprendizajes

* Cómo limpiar datos crudos con pandas.
* Cómo normalizar columnas de texto.
* Cómo convertir fechas y columnas numéricas.
* Cómo manejar valores nulos.
* Cómo eliminar duplicados usando claves de negocio.
* Cómo generar datasets procesados y un resumen de calidad.

## Explicación para entrevista

Tomé un dataset de e-commerce generado desde una plataforma de práctica y limpié tres tablas principales: clientes, órdenes y reviews. El pipeline normaliza texto, convierte fechas, corrige tipos numéricos, maneja nulos y elimina duplicados. Como resultado, generé archivos limpios listos para análisis y un resumen de limpieza que muestra cuántas filas fueron procesadas y eliminadas por tabla.
