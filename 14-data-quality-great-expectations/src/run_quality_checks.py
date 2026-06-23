import json
from pathlib import Path

import pandas as pd
import great_expectations as gx


RAW_PATH = Path("data/raw")
OUTPUT_PATH = Path("output")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def add_result(
    results,
    table,
    expectation,
    column,
    success,
    unexpected_count,
    total_rows,
    severity
):
    unexpected_percent = round((unexpected_count / total_rows) * 100, 2) if total_rows > 0 else 0

    results.append({
        "table": table,
        "expectation": expectation,
        "column": column,
        "severity": severity,
        "success": success,
        "unexpected_count": int(unexpected_count),
        "unexpected_percent": unexpected_percent
    })


def expect_not_null(df, table, column, results, severity="warning"):
    total_rows = len(df)
    unexpected_count = df[column].isna().sum()
    success = unexpected_count == 0

    add_result(
        results,
        table,
        "expect_column_values_to_not_be_null",
        column,
        success,
        unexpected_count,
        total_rows,
        severity
    )


def expect_unique(df, table, column, results, severity="warning"):
    total_rows = len(df)
    unexpected_count = df[column].duplicated().sum()
    success = unexpected_count == 0

    add_result(
        results,
        table,
        "expect_column_values_to_be_unique",
        column,
        success,
        unexpected_count,
        total_rows,
        severity
    )


def expect_between(df, table, column, min_value, results, severity="warning"):
    total_rows = len(df)
    values = pd.to_numeric(df[column], errors="coerce")

    unexpected_count = ((values < min_value) | values.isna()).sum()
    success = unexpected_count == 0

    add_result(
        results,
        table,
        "expect_column_values_to_be_between",
        column,
        success,
        unexpected_count,
        total_rows,
        severity
    )


def main():
    print("Ejecutando validaciones de calidad...")
    print(f"Great Expectations instalado: {gx.__version__}")

    customers = pd.read_csv(RAW_PATH / "ecommerce_customers.csv")
    orders = pd.read_csv(RAW_PATH / "ecommerce_orders.csv")
    order_items = pd.read_csv(RAW_PATH / "ecommerce_order_items.csv")
    products = pd.read_csv(RAW_PATH / "ecommerce_products.csv")

    results = []

    # Customers
    expect_not_null(customers, "customers", "customer_id", results, severity="critical")
    expect_unique(customers, "customers", "customer_id", results, severity="critical")
    expect_not_null(customers, "customers", "email", results, severity="warning")

    # Orders
    expect_not_null(orders, "orders", "order_id", results, severity="critical")
    expect_unique(orders, "orders", "order_id", results, severity="critical")
    expect_not_null(orders, "orders", "customer_id", results, severity="critical")
    expect_between(orders, "orders", "total_amount", 0, results, severity="critical")

    # Order items
    expect_not_null(order_items, "order_items", "order_item_id", results, severity="critical")
    expect_unique(order_items, "order_items", "order_item_id", results, severity="critical")
    expect_not_null(order_items, "order_items", "order_id", results, severity="critical")
    expect_not_null(order_items, "order_items", "product_id", results, severity="critical")
    expect_between(order_items, "order_items", "quantity", 1, results, severity="critical")
    expect_between(order_items, "order_items", "subtotal", 0, results, severity="critical")

    # Products
    expect_not_null(products, "products", "product_id", results, severity="critical")
    expect_unique(products, "products", "product_id", results, severity="critical")
    expect_not_null(products, "products", "product_name", results, severity="warning")

    results_df = pd.DataFrame(results)

    total_expectations = len(results_df)
    passed_expectations = int(results_df["success"].sum())
    failed_expectations = total_expectations - passed_expectations

    critical_failures = len(
        results_df[
            (results_df["severity"] == "critical") &
            (results_df["success"] == False)
        ]
    )

    warning_failures = len(
        results_df[
            (results_df["severity"] == "warning") &
            (results_df["success"] == False)
        ]
    )

    success_rate = round((passed_expectations / total_expectations) * 100, 2)

    pipeline_status = "PASSED" if critical_failures == 0 else "FAILED"

    summary = {
        "pipeline_status": pipeline_status,
        "total_expectations": total_expectations,
        "passed_expectations": passed_expectations,
        "failed_expectations": failed_expectations,
        "critical_failures": critical_failures,
        "warning_failures": warning_failures,
        "success_rate": success_rate
    }

    results_df.to_csv(OUTPUT_PATH / "validation_results.csv", index=False)

    with open(OUTPUT_PATH / "validation_summary.json", "w") as file:
        json.dump(summary, file, indent=4)

    print("\nResumen de validación:")
    print(summary)

    print("\nDetalle de validaciones:")
    print(results_df)

    print("\nArchivos generados:")
    print("output/validation_results.csv")
    print("output/validation_summary.json")

    if pipeline_status == "FAILED":
        print("\nPipeline status: FAILED")
        print("Existen validaciones críticas fallidas. Los datos no deberían cargarse a un modelo analítico sin revisión.")
    else:
        print("\nPipeline status: PASSED")
        print("No existen validaciones críticas fallidas.")


if __name__ == "__main__":
    main()
