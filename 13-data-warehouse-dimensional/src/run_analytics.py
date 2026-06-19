import duckdb
from pathlib import Path

DB_PATH = "output/ecommerce_warehouse.duckdb"
OUTPUT_PATH = Path("output")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB_PATH)

queries = {
    "sales_by_month": """
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(f.order_item_id) AS total_items,
            ROUND(SUM(f.item_subtotal), 2) AS total_sales
        FROM fact_order_items f
        LEFT JOIN dim_date d
            ON f.date_key = d.date_key
        GROUP BY
            d.year,
            d.month,
            d.month_name
        ORDER BY
            d.year,
            d.month
    """,

    "top_products_by_sales": """
        SELECT
            p.product_name,
            p.category_name,
            COUNT(f.order_item_id) AS total_items_sold,
            ROUND(SUM(f.item_subtotal), 2) AS total_sales
        FROM fact_order_items f
        LEFT JOIN dim_products p
            ON f.product_key = p.product_key
        GROUP BY
            p.product_name,
            p.category_name
        ORDER BY
            total_sales DESC
        LIMIT 10
    """,

    "weekend_vs_weekday_sales": """
        SELECT
            CASE
                WHEN d.is_weekend = TRUE THEN 'weekend'
                ELSE 'weekday'
            END AS day_type,
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(f.order_item_id) AS total_items,
            ROUND(SUM(f.item_subtotal), 2) AS total_sales
        FROM fact_order_items f
        LEFT JOIN dim_date d
            ON f.date_key = d.date_key
        GROUP BY
            day_type
        ORDER BY
            total_sales DESC
    """,

    "sales_by_customer_segment": """
        SELECT
            c.segment,
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(f.order_item_id) AS total_items,
            ROUND(SUM(f.item_subtotal), 2) AS total_sales
        FROM fact_order_items f
        LEFT JOIN dim_customers c
            ON f.customer_key = c.customer_key
        GROUP BY
            c.segment
        ORDER BY
            total_sales DESC
    """
}

print("Ejecutando queries analíticas...")

for name, query in queries.items():
    result = con.execute(query).fetchdf()
    output_file = OUTPUT_PATH / f"{name}.csv"
    result.to_csv(output_file, index=False)

    print(f"\nArchivo generado: {output_file}")
    print(result)

con.close()
