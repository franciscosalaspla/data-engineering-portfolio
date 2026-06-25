from pathlib import Path
import json
import pandas as pd


BASE_PATH = Path(__file__).resolve().parents[2]
RAW_PATH = BASE_PATH / "15-dbt-profesional" / "data" / "raw"
OUTPUT_PATH = BASE_PATH / "16-orquestacion-airflow" / "output"

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

REQUIRED_FILES = {
    "ecommerce_customers.csv": ["customer_id"],
    "ecommerce_orders.csv": ["order_id", "customer_id"],
    "ecommerce_order_items.csv": ["order_item_id", "order_id", "product_id"],
    "ecommerce_products.csv": ["product_id"],
}


def validate_file(file_name, required_columns):
    file_path = RAW_PATH / file_name

    result = {
        "file": file_name,
        "path": str(file_path),
        "exists": file_path.exists(),
        "size_bytes": 0,
        "rows": 0,
        "columns": [],
        "missing_columns": [],
        "status": "FAILED",
    }

    if not file_path.exists():
        result["error"] = "File does not exist"
        return result

    result["size_bytes"] = file_path.stat().st_size

    if result["size_bytes"] == 0:
        result["error"] = "File is empty"
        return result

    df = pd.read_csv(file_path)

    result["rows"] = len(df)
    result["columns"] = list(df.columns)
    result["missing_columns"] = [
        col for col in required_columns if col not in df.columns
    ]

    if result["rows"] == 0:
        result["error"] = "CSV has no rows"
        return result

    if result["missing_columns"]:
        result["error"] = "Missing required columns"
        return result

    result["status"] = "PASSED"
    return result


def main():
    print("Validando archivos raw de e-commerce...")
    print(f"Ruta raw: {RAW_PATH}")

    results = []

    for file_name, required_columns in REQUIRED_FILES.items():
        result = validate_file(file_name, required_columns)
        results.append(result)

        print(
            f"{file_name}: {result['status']} | "
            f"rows={result['rows']} | "
            f"size={result['size_bytes']} bytes"
        )

    failed_files = [r for r in results if r["status"] == "FAILED"]

    summary = {
        "status": "PASSED" if not failed_files else "FAILED",
        "total_files": len(results),
        "passed_files": len(results) - len(failed_files),
        "failed_files": len(failed_files),
        "results": results,
    }

    output_file = OUTPUT_PATH / "raw_files_validation.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

    print(f"\nResultado guardado en: {output_file}")
    print(f"Estado final: {summary['status']}")

    if summary["status"] == "FAILED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
