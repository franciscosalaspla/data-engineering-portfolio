import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")
OUTPUT_PATH = Path("output")

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def clean_text_column(series):
    return (
        series.astype("string")
        .str.strip()
        .str.lower()
    )


def clean_customers():
    df = pd.read_csv(RAW_PATH / "ecommerce_customers.csv")

    initial_rows = len(df)

    # Normalizar texto
    for col in ["first_name", "last_name", "email", "city", "country", "segment"]:
        if col in df.columns:
            df[col] = clean_text_column(df[col])

    # Convertir fecha
    if "birth_date" in df.columns:
        df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")

    # Eliminar duplicados por customer_id
    df = df.drop_duplicates(subset=["customer_id"], keep="first")

    # Eliminar clientes sin ID
    df = df.dropna(subset=["customer_id"])

    final_rows = len(df)

    df.to_csv(PROCESSED_PATH / "clean_customers.csv", index=False)

    return {
        "table": "customers",
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "removed_rows": initial_rows - final_rows
    }


def clean_orders():
    df = pd.read_csv(RAW_PATH / "ecommerce_orders.csv")

    initial_rows = len(df)

    # Normalizar texto
    for col in ["order_status", "payment_method", "shipping_method"]:
        if col in df.columns:
            df[col] = clean_text_column(df[col])

    # Convertir fechas
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Convertir montos
    money_cols = ["subtotal", "shipping_cost", "tax_amount", "total_amount"]
    for col in money_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Rellenar nulos en montos con 0
    for col in money_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Eliminar duplicados por order_id
    df = df.drop_duplicates(subset=["order_id"], keep="first")

    # Eliminar órdenes sin ID
    df = df.dropna(subset=["order_id"])

    final_rows = len(df)

    df.to_csv(PROCESSED_PATH / "clean_orders.csv", index=False)

    return {
        "table": "orders",
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "removed_rows": initial_rows - final_rows
    }


def clean_reviews():
    df = pd.read_csv(RAW_PATH / "ecommerce_reviews.csv")

    initial_rows = len(df)

    # Normalizar comentario
    if "comment" in df.columns:
        df["comment"] = df["comment"].astype("string").str.strip()

    # Convertir rating
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Convertir fecha
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    # Rellenar comentario vacío
    if "comment" in df.columns:
        df["comment"] = df["comment"].fillna("no comment")

    # Eliminar duplicados por review_id
    df = df.drop_duplicates(subset=["review_id"], keep="first")

    # Eliminar reviews sin ID
    df = df.dropna(subset=["review_id"])

    final_rows = len(df)

    df.to_csv(PROCESSED_PATH / "clean_reviews.csv", index=False)

    return {
        "table": "reviews",
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "removed_rows": initial_rows - final_rows
    }


def main():
    print("Iniciando limpieza de datos e-commerce...")

    summaries = [
        clean_customers(),
        clean_orders(),
        clean_reviews()
    ]

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(OUTPUT_PATH / "cleaning_summary.csv", index=False)

    print("\nResumen de limpieza:")
    print(summary_df)

    print("\nArchivos generados:")
    print("data/processed/clean_customers.csv")
    print("data/processed/clean_orders.csv")
    print("data/processed/clean_reviews.csv")
    print("output/cleaning_summary.csv")


if __name__ == "__main__":
    main()
