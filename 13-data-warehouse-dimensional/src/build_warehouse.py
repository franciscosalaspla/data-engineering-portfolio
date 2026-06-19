import duckdb
from pathlib import Path

OUTPUT_PATH = Path("output")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

DB_PATH = "output/ecommerce_warehouse.duckdb"

con = duckdb.connect(DB_PATH)

print("Creando Data Warehouse dimensional...")

# =========================
# 1. Cargar tablas raw
# =========================

con.execute("""
CREATE OR REPLACE TABLE raw_orders AS
SELECT *
FROM read_csv_auto('data/raw/ecommerce_orders.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE raw_order_items AS
SELECT *
FROM read_csv_auto('data/raw/ecommerce_order_items.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE raw_customers AS
SELECT *
FROM read_csv_auto('data/raw/ecommerce_customers.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE raw_products AS
SELECT *
FROM read_csv_auto('data/raw/ecommerce_products.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE raw_categories AS
SELECT *
FROM read_csv_auto('data/raw/ecommerce_categories.csv');
""")

print("Tablas raw cargadas.")

# =========================
# 1.1 Crear tablas staging deduplicadas
# =========================

con.execute("""
CREATE OR REPLACE TABLE stg_orders AS
SELECT *
FROM raw_orders
WHERE order_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY order_id
) = 1;
""")

con.execute("""
CREATE OR REPLACE TABLE stg_order_items AS
SELECT *
FROM raw_order_items
WHERE order_item_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_item_id
    ORDER BY order_item_id
) = 1;
""")

con.execute("""
CREATE OR REPLACE TABLE stg_customers AS
SELECT *
FROM stg_customers
WHERE customer_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY customer_id
) = 1;
""")

con.execute("""
CREATE OR REPLACE TABLE stg_products AS
SELECT *
FROM raw_products
WHERE product_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY product_id
    ORDER BY product_id
) = 1;
""")

con.execute("""
CREATE OR REPLACE TABLE stg_categories AS
SELECT *
FROM raw_categories
WHERE category_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY category_id
    ORDER BY category_id
) = 1;
""")

print("Tablas staging deduplicadas creadas.")

# =========================
# 2. Crear dim_date
# =========================

con.execute("""
CREATE OR REPLACE TABLE dim_date AS
WITH parsed_dates AS (
    SELECT DISTINCT
        COALESCE(
            TRY_CAST(order_date AS DATE),
            CAST(TRY_STRPTIME(order_date, '%m/%d/%Y') AS DATE),
            CAST(TRY_STRPTIME(order_date, '%d-%m-%Y') AS DATE),
            CAST(TRY_STRPTIME(order_date, '%Y/%m/%d') AS DATE)
        ) AS full_date
    FROM stg_orders
    WHERE order_date IS NOT NULL
),

unique_dates AS (
    SELECT DISTINCT
        full_date
    FROM parsed_dates
    WHERE full_date IS NOT NULL
)

SELECT
    CAST(STRFTIME(full_date, '%Y%m%d') AS INTEGER) AS date_key,
    full_date,
    EXTRACT(YEAR FROM full_date) AS year,
    EXTRACT(QUARTER FROM full_date) AS quarter,
    EXTRACT(MONTH FROM full_date) AS month,
    STRFTIME(full_date, '%B') AS month_name,
    EXTRACT(DAY FROM full_date) AS day,
    EXTRACT(DOW FROM full_date) AS day_of_week,
    CASE
        WHEN EXTRACT(DOW FROM full_date) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM unique_dates;
""")

print("dim_date creada.")

# =========================
# 3. Crear dim_customers
# =========================

con.execute("""
CREATE OR REPLACE TABLE dim_customers AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    LOWER(TRIM(first_name)) AS first_name,
    LOWER(TRIM(last_name)) AS last_name,
    LOWER(TRIM(email)) AS email,
    LOWER(TRIM(city)) AS city,
    LOWER(TRIM(country)) AS country,
    LOWER(TRIM(segment)) AS segment,
    COALESCE(
        TRY_CAST(registration_date AS DATE),
        CAST(TRY_STRPTIME(registration_date, '%m/%d/%Y') AS DATE),
        CAST(TRY_STRPTIME(registration_date, '%d-%m-%Y') AS DATE),
        CAST(TRY_STRPTIME(registration_date, '%Y/%m/%d') AS DATE)
    ) AS registration_date,
    is_verified,
    accepts_marketing
FROM stg_customers
WHERE customer_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY customer_id
) = 1;
""")

print("dim_customers creada.")

# =========================
# 4. Crear dim_products
# =========================

con.execute("""
CREATE OR REPLACE TABLE dim_products AS
SELECT
    ROW_NUMBER() OVER (ORDER BY p.product_id) AS product_key,
    p.product_id,
    p.sku,
    TRIM(p.product_name) AS product_name,
    TRIM(c.category_name) AS category_name,
    p.price,
    p.cost,
    p.is_active,
    COALESCE(
        TRY_CAST(p.created_at AS DATE),
        CAST(TRY_STRPTIME(p.created_at, '%m/%d/%Y') AS DATE),
        CAST(TRY_STRPTIME(p.created_at, '%d-%m-%Y') AS DATE),
        CAST(TRY_STRPTIME(p.created_at, '%Y/%m/%d') AS DATE)
    ) AS created_at,
    COALESCE(
        TRY_CAST(p.updated_at AS DATE),
        CAST(TRY_STRPTIME(p.updated_at, '%m/%d/%Y') AS DATE),
        CAST(TRY_STRPTIME(p.updated_at, '%d-%m-%Y') AS DATE),
        CAST(TRY_STRPTIME(p.updated_at, '%Y/%m/%d') AS DATE)
    ) AS updated_at
FROM stg_products p
LEFT JOIN stg_categories c
    ON p.category_id = c.category_id
WHERE p.product_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY p.product_id
    ORDER BY p.product_id
) = 1;
""")

print("dim_products creada.")

# =========================
# 5. Crear fact_order_items
# =========================

con.execute("""
CREATE OR REPLACE TABLE fact_order_items AS
SELECT
    ROW_NUMBER() OVER (ORDER BY oi.order_item_id) AS order_item_key,
    oi.order_item_id,
    oi.order_id,
    dc.customer_key,
    dp.product_key,
    dd.date_key,
    TRY_CAST(oi.quantity AS DOUBLE) AS quantity,
    TRY_CAST(oi.unit_price AS DOUBLE) AS unit_price,
    TRY_CAST(oi.subtotal AS DOUBLE) AS item_subtotal,
    TRY_CAST(o.discount_percent AS DOUBLE) AS discount_percent,
    TRY_CAST(o.shipping_cost AS DOUBLE) AS shipping_cost,
    TRY_CAST(o.tax_amount AS DOUBLE) AS tax_amount,
    TRY_CAST(o.total_amount AS DOUBLE) AS total_amount
FROM stg_order_items oi
LEFT JOIN stg_orders o
    ON oi.order_id = o.order_id
LEFT JOIN dim_customers dc
    ON o.customer_id = dc.customer_id
LEFT JOIN dim_products dp
    ON oi.product_id = dp.product_id
LEFT JOIN dim_date dd
    ON COALESCE(
        TRY_CAST(o.order_date AS DATE),
        CAST(TRY_STRPTIME(o.order_date, '%m/%d/%Y') AS DATE),
        CAST(TRY_STRPTIME(o.order_date, '%d-%m-%Y') AS DATE),
        CAST(TRY_STRPTIME(o.order_date, '%Y/%m/%d') AS DATE)
    ) = dd.full_date
WHERE oi.order_item_id IS NOT NULL;
""")

print("fact_order_items creada.")

# =========================
# 6. Validación de tablas
# =========================

tables = [
    "raw_orders",
    "raw_order_items",
    "raw_customers",
    "raw_products",
    "raw_categories",
    "dim_date",
    "dim_customers",
    "dim_products",
    "fact_order_items"
]

print("\nResumen de tablas:")
for table in tables:
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} filas")

print("\nData Warehouse creado correctamente en:")
print(DB_PATH)

con.close()
