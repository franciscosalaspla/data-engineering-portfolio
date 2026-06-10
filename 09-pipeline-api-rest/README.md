# Pipeline con API REST

Proyecto práctico de ingeniería de datos enfocado en consumir datos desde una API REST pública, guardar la respuesta cruda en JSON, transformar datos anidados en una tabla limpia y generar outputs analíticos en CSV y Parquet.

## Objetivo del proyecto

Construir un pipeline de datos que permita:

* Consumir una API REST pública.
* Manejar respuestas en formato JSON.
* Guardar la respuesta cruda en `data/raw`.
* Transformar JSON anidado en una tabla analítica.
* Validar calidad de datos.
* Generar outputs en CSV y Parquet.
* Crear métricas agregadas para análisis.

## Caso de negocio

Este proyecto simula un flujo de ingesta de datos desde una API externa.
Una empresa necesita consumir información de países, transformar estructuras JSON anidadas y dejar los datos disponibles para análisis posterior.

El pipeline responde preguntas como:

* ¿Cuántos países existen por región?
* ¿Cuáles son los países con mayor población?
* ¿Cuáles son los países con mayor superficie?
* ¿Existen datos nulos o duplicados?
* ¿Cómo transformar datos JSON anidados en una tabla limpia?

## Stack utilizado

* Python
* Requests
* Pandas
* JSON
* CSV
* Parquet
* PyArrow
* Git / GitHub
* GitHub Codespaces

## Estructura del proyecto

```text
09-pipeline-api-rest/
├── data/
│   └── raw/
│       └── countries_raw.json
├── output/
│   ├── countries_clean.csv
│   ├── countries_clean.parquet
│   ├── countries_by_region.csv
│   ├── top_countries_by_area.csv
│   └── top_countries_by_population.csv
├── src/
│   └── main.py
├── README.md
└── requirements.txt
```

## Fuente de datos

Se utilizó la API pública REST Countries:

```text
https://restcountries.com/v3.1/all
```

Para evitar traer datos innecesarios, se solicitaron campos específicos mediante el parámetro `fields`:

```text
name, capital, region, subregion, population, area, languages, currencies, cca3
```

## Proceso del pipeline

### 1. Extract

Se consume la API REST usando `requests`.

```python
response = requests.get(API_URL, timeout=30)
response.raise_for_status()
data = response.json()
```

Se utiliza:

* `timeout`: para evitar que el pipeline quede esperando indefinidamente.
* `raise_for_status()`: para detectar errores HTTP antes de procesar datos inválidos.

### 2. Raw Load

La respuesta original de la API se guarda en formato JSON dentro de:

```text
data/raw/countries_raw.json
```

Esto permite conservar una copia cruda de los datos antes de cualquier transformación.

### 3. Transform

El JSON original contiene estructuras anidadas, por ejemplo:

```text
name.common
capital[0]
languages.{codigo}
currencies.{codigo}.name
```

Estas estructuras se transforman en columnas simples:

| Columna         | Descripción           |
| --------------- | --------------------- |
| `country_name`  | Nombre común del país |
| `official_name` | Nombre oficial        |
| `capital`       | Capital principal     |
| `region`        | Región                |
| `subregion`     | Subregión             |
| `population`    | Población             |
| `area`          | Superficie            |
| `main_language` | Idioma principal      |
| `main_currency` | Moneda principal      |
| `country_code`  | Código del país       |

### 4. Validate

Se ejecutan validaciones básicas de calidad:

* Cantidad de filas y columnas.
* Valores nulos por columna.
* Duplicados por `country_code`.
* Cantidad de países por región.

Resultados principales:

```text
Filas transformadas: 250
Columnas: 10
Duplicados por country_code: 0
```

Valores nulos detectados:

```text
capital: 4
main_language: 1
main_currency: 3
```

Estos registros se conservaron porque los nulos son pocos y no afectan la unicidad ni la estructura principal del dataset.

### 5. Load

El dataset limpio se guarda en:

```text
output/countries_clean.csv
output/countries_clean.parquet
```

### 6. Analytics Outputs

También se generan archivos analíticos:

| Archivo                           | Descripción                                    |
| --------------------------------- | ---------------------------------------------- |
| `countries_by_region.csv`         | Resumen de países, población y área por región |
| `top_countries_by_population.csv` | Top 10 países por población                    |
| `top_countries_by_area.csv`       | Top 10 países por superficie                   |

## Resultados principales

### Países por región

```text
Africa: 59
Americas: 56
Europe: 53
Asia: 50
Oceania: 27
Antarctic: 5
```

### Top países por población

```text
India
China
United States
Indonesia
Pakistan
Nigeria
Brazil
Bangladesh
Russia
Mexico
```

### Top países por área

```text
Russia
Antarctica
Canada
China
United States
Brazil
Australia
India
Argentina
Kazakhstan
```

## Manejo de errores

El pipeline incluye manejo básico de errores para:

* Timeout de la API.
* Errores HTTP como 400, 404 o 500.
* Errores generales de conexión.

Esto evita que el pipeline procese datos incompletos o respuestas inválidas.

## Cómo ejecutar el proyecto

Desde la carpeta del proyecto:

```bash
cd 09-pipeline-api-rest
pip install -r requirements.txt
python src/main.py
```

## Outputs esperados

Después de ejecutar el pipeline, se generan los siguientes archivos:

```text
data/raw/countries_raw.json
output/countries_clean.csv
output/countries_clean.parquet
output/countries_by_region.csv
output/top_countries_by_population.csv
output/top_countries_by_area.csv
```

## Aprendizajes

* Consumir datos desde una API REST usando Python.
* Manejar respuestas JSON.
* Guardar datos crudos antes de transformar.
* Aplanar estructuras JSON anidadas.
* Validar calidad de datos.
* Exportar datos limpios en CSV y Parquet.
* Crear outputs analíticos reutilizables.
* Manejar errores básicos de API.

## Explicación para entrevista

Construí un pipeline que consume una API REST pública, guarda la respuesta cruda en JSON, transforma estructuras anidadas en una tabla limpia y genera outputs en CSV y Parquet. Además, agregué validaciones de calidad, manejo de errores y métricas analíticas como países por región, top países por población y top países por área.
