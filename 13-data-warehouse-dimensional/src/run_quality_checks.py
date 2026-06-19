import duckdb
from pathlib import Path

DB_PATH = "output/ecommerce_warehouse.duckdb"
OUTPUT_PATH = Path("output")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB_PATH)

queries = {
    "fact_row_validation": """
        SELECT
            COUNT(*) AS total_fact_rows,
            COUNT(DISTINCT order_item_id) AS distinct_order_items
        FROM fact_order_items
    """,

    "missing_dimension_keys": """
        SELECT
            COUNT(*) AS total_fact_rows,
            SUM(CASE WHEN date_key IS NULL THEN 1 ELSE 0 END) AS rows_without_date,
            SUM(CASE WHEN customer_key IS NULL THEN 1 ELSE 0 END) AS rows_without_customer,
            SUM(CASE WHEN product_key IS NULL THEN 1 ELSE 0 END) AS rows_without_product
        FROM fact_order_items
    """,

    "sales_without_dimensions": """
        SELECT
            ROUND(SUM(CASE WHEN date_key IS NULL THEN item_subtotal ELSE 0 END), 2) AS sales_without_date,
            ROUND(SUM(CASE WHEN customer_key IS NULL THEN item_subtotal ELSE 0 END), 2) AS sales_without_customer,
            ROUND(SUM(CASE WHEN product_key IS NULL THEN item_subtotal ELSE 0 END), 2) AS sales_without_product
        FROM fact_order_items
    """
}

print("Ejecutando validaciones de calidad...")

for name, query in queries.items():
    result = con.execute(query).fetchdf()
    output_file = OUTPUT_PATH / f"{name}.csv"
    result.to_csv(output_file, index=False)

    print(f"\nArchivo generado: {output_file}")
    print(result)

con.close()
