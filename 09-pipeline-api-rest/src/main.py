import json
import requests
import pandas as pd
from pathlib import Path

# Rutas del proyecto
RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("output")

RAW_FILE = RAW_DIR / "countries_raw.json"
CSV_OUTPUT = OUTPUT_DIR / "countries_clean.csv"
PARQUET_OUTPUT = OUTPUT_DIR / "countries_clean.parquet"

REGION_SUMMARY_OUTPUT = OUTPUT_DIR / "countries_by_region.csv"
TOP_POPULATION_OUTPUT = OUTPUT_DIR / "top_countries_by_population.csv"
TOP_AREA_OUTPUT = OUTPUT_DIR / "top_countries_by_area.csv"

# URL de API pública sin token
API_URL = "https://restcountries.com/v3.1/all?fields=name,capital,region,subregion,population,area,languages,currencies,cca3"


def fetch_countries():
    """
    Consume la API REST de países y retorna la respuesta en formato JSON.
    Maneja errores de conexión, timeout y respuestas HTTP inválidas.
    """
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("Error: la API tardó demasiado en responder.")
        raise

    except requests.exceptions.HTTPError as error:
        print(f"Error HTTP al consumir la API: {error}")
        raise

    except requests.exceptions.RequestException as error:
        print(f"Error de conexión al consumir la API: {error}")
        raise


def save_raw_json(data):
    """
    Guarda la respuesta cruda de la API en data/raw.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with open(RAW_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_first_list_value(value):
    """
    Obtiene el primer elemento de una lista.
    Si no existe, retorna None.
    """
    if isinstance(value, list) and len(value) > 0:
        return value[0]
    return None


def get_first_dict_value(value):
    """
    Obtiene el primer valor de un diccionario.
    Sirve para campos como languages y currencies.
    """
    if isinstance(value, dict) and len(value) > 0:
        first_key = next(iter(value))
        first_value = value[first_key]

        if isinstance(first_value, dict) and "name" in first_value:
            return first_value["name"]

        return first_value

    return None


def transform_countries(data):
    """
    Transforma el JSON anidado en una tabla limpia.
    """
    records = []

    for country in data:
        record = {
            "country_name": country.get("name", {}).get("common"),
            "official_name": country.get("name", {}).get("official"),
            "capital": get_first_list_value(country.get("capital")),
            "region": country.get("region"),
            "subregion": country.get("subregion"),
            "population": country.get("population"),
            "area": country.get("area"),
            "main_language": get_first_dict_value(country.get("languages")),
            "main_currency": get_first_dict_value(country.get("currencies")),
            "country_code": country.get("cca3"),
        }

        records.append(record)

    return pd.DataFrame(records)


def save_outputs(df):
    """
    Guarda la tabla limpia en CSV y Parquet.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(CSV_OUTPUT, index=False)
    df.to_parquet(PARQUET_OUTPUT, index=False)


def validate_data(df):
    """
    Ejecuta validaciones básicas de calidad sobre el dataset limpio.
    """
    print("\nValidaciones de calidad:")

    print("\nCantidad de filas y columnas:")
    print(df.shape)

    print("\nValores nulos por columna:")
    print(df.isnull().sum())

    print("\nDuplicados por country_code:")
    print(df["country_code"].duplicated().sum())

    print("\nCantidad de países por región:")
    print(df["region"].value_counts())


def create_analytics_outputs(df):
    """
    Crea outputs analíticos a partir del dataset limpio.
    """
    countries_by_region = (
        df.groupby("region")
        .agg(
            total_countries=("country_code", "count"),
            total_population=("population", "sum"),
            avg_population=("population", "mean"),
            total_area=("area", "sum"),
        )
        .reset_index()
        .sort_values("total_countries", ascending=False)
    )

    top_countries_by_population = (
        df[["country_name", "region", "population"]]
        .sort_values("population", ascending=False)
        .head(10)
    )

    top_countries_by_area = (
        df[["country_name", "region", "area"]]
        .sort_values("area", ascending=False)
        .head(10)
    )

    countries_by_region.to_csv(REGION_SUMMARY_OUTPUT, index=False)
    top_countries_by_population.to_csv(TOP_POPULATION_OUTPUT, index=False)
    top_countries_by_area.to_csv(TOP_AREA_OUTPUT, index=False)

    print("\nOutputs analíticos generados:")
    print(f"- {REGION_SUMMARY_OUTPUT}")
    print(f"- {TOP_POPULATION_OUTPUT}")
    print(f"- {TOP_AREA_OUTPUT}")

    print("\nPaíses por región:")
    print(countries_by_region)

    print("\nTop 10 países por población:")
    print(top_countries_by_population)

    print("\nTop 10 países por área:")
    print(top_countries_by_area)


def main():
    print("Iniciando consumo de API REST...")

    data = fetch_countries()
    save_raw_json(data)

    df = transform_countries(data)
    validate_data(df)
    save_outputs(df)
    create_analytics_outputs(df)

    print(f"Registros obtenidos desde API: {len(data)}")
    print(f"Filas transformadas: {len(df)}")
    print(f"Archivo raw guardado: {RAW_FILE}")
    print(f"CSV limpio guardado: {CSV_OUTPUT}")
    print(f"Parquet limpio guardado: {PARQUET_OUTPUT}")

    print("\nVista previa del dataset limpio:")
    print(df.head())


if __name__ == "__main__":
    main()