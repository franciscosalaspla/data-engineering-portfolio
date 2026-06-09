import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "ecommerce_orders.csv"


def extract_data(file_path):
    """
    Extract data from a CSV file.
    """
    df = pd.read_csv(file_path)
    return df


def explore_data(df):
    """
    Explore the initial structure and quality of the dataset.
    """

    print("Archivo cargado correctamente:")
    print("- ecommerce_orders.csv")

    print("\nResumen inicial:")
    print(f"Filas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")

    print("\nColumnas:")
    for column in df.columns:
        print(f"- {column}")

    print("\nValores nulos:")
    print(df.isnull().sum())

    print("\nDuplicados:")
    print(f"{df.duplicated().sum()} fila duplicada encontrada")


def main():
    """
    Run the first stage of the ETL pipeline.
    """
    df = extract_data(RAW_DATA_PATH)
    explore_data(df)


if __name__ == "__main__":
    main()
