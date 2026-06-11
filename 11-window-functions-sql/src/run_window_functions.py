import duckdb
import os

# Crear carpeta output si no existe
os.makedirs("output", exist_ok=True)

# Crear conexión local en memoria
con = duckdb.connect()

# Crear tabla orders desde CSV
con.execute("""
CREATE OR REPLACE TABLE orders AS
SELECT *
FROM read_csv_auto('data/raw/orders.csv');
""")

# Queries con nombre de output
queries = {
    "purchase_number_by_customer": """
        SELECT
            customer_id,
            customer_name,
            order_id,
            order_date,
            product,
            sales,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS purchase_number
        FROM orders
        ORDER BY customer_id, order_date
    """,

    "customer_sales_ranking": """
        WITH customer_sales AS (
            SELECT
                customer_id,
                customer_name,
                SUM(sales) AS total_sales
            FROM orders
            GROUP BY customer_id, customer_name
        )

        SELECT
            customer_id,
            customer_name,
            total_sales,
            RANK() OVER (
                ORDER BY total_sales DESC
            ) AS sales_rank
        FROM customer_sales
        ORDER BY sales_rank
    """,

    "product_ranking_by_category": """
        SELECT
            category,
            product,
            sales,
            DENSE_RANK() OVER (
                PARTITION BY category
                ORDER BY sales DESC
            ) AS product_rank_in_category
        FROM orders
        ORDER BY category, product_rank_in_category
    """,

    "sales_vs_previous_purchase": """
        SELECT
            customer_id,
            customer_name,
            order_id,
            order_date,
            product,
            sales,
            LAG(sales) OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS previous_sales,
            sales - LAG(sales) OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS sales_difference
        FROM orders
        ORDER BY customer_id, order_date
    """,

    "next_purchase_by_customer": """
        SELECT
            customer_id,
            customer_name,
            order_id,
            order_date,
            product,
            sales,
            LEAD(order_date) OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS next_order_date,
            LEAD(product) OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS next_product
        FROM orders
        ORDER BY customer_id, order_date
    """,

    "running_total_sales_by_customer": """
        SELECT
            customer_id,
            customer_name,
            order_id,
            order_date,
            product,
            sales,
            SUM(sales) OVER (
                PARTITION BY customer_id
                ORDER BY order_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS running_total_sales
        FROM orders
        ORDER BY customer_id, order_date
    """,

    "sales_vs_category_average": """
        SELECT
            order_id,
            category,
            product,
            sales,
            ROUND(AVG(sales) OVER (
                PARTITION BY category
            ), 2) AS avg_sales_category,
            ROUND(
                sales - AVG(sales) OVER (
                    PARTITION BY category
                ), 2
            ) AS difference_vs_category_avg
        FROM orders
        ORDER BY category, sales DESC
    """,

    "monthly_sales_comparison": """
        WITH monthly_sales AS (
            SELECT
                DATE_TRUNC('month', order_date) AS sales_month,
                SUM(sales) AS total_sales
            FROM orders
            GROUP BY DATE_TRUNC('month', order_date)
        )

        SELECT
            sales_month,
            total_sales,
            LAG(total_sales) OVER (
                ORDER BY sales_month
            ) AS previous_month_sales,
            total_sales - LAG(total_sales) OVER (
                ORDER BY sales_month
            ) AS monthly_sales_difference
        FROM monthly_sales
        ORDER BY sales_month
    """
}

# Ejecutar queries y guardar resultados
for name, query in queries.items():
    result = con.execute(query).fetchdf()
    output_path = f"output/{name}.csv"

    result.to_csv(output_path, index=False)

    print(f"\nArchivo generado: {output_path}")
    print(result)
