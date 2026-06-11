# Portafolio de Ingeniería de Datos

Portfolio práctico de proyectos de Ingeniería de Datos enfocado en ETL, SQL, APIs, Python, limpieza de datos, validación de calidad y generación de outputs analíticos.

## Contacto

* LinkedIn: [https://bit.ly/4u9E6eU](https://bit.ly/4u9E6eU)
* GitHub: [https://bit.ly/4vouAFH](http://bit.ly/4vouAFH)
* Email: [franciscosalaspla@gmail.com](mailto:franciscosalaspla@gmail.com)
* CV: [Descargar CV](./CV_Francisco_Salas.pdf)

## Perfil

Soy Ingeniero Civil Industrial con experiencia en analítica digital, integración de eventos, JSON/APIs, validación QA/producción, Data Warehouse, SQL, Power BI y Databricks SQL.

Este repositorio consolida mi transición hacia roles de Data Engineer mediante proyectos prácticos, documentados y defendibles en entrevista.

## Top 3 proyectos recomendados

Estos son los proyectos principales que recomiendo revisar primero.

| Proyecto                                             | Foco técnico                                 | Qué demuestra                                                                      |
| ---------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------- |
| [09 - Pipeline con API REST](./09-pipeline-api-rest) | API REST, JSON, Python, pandas, CSV, Parquet | Consumo de API, transformación de JSON anidado, validación y generación de outputs |
| [08 - Análisis SQL de Logs](./08-analisis-sql-logs)  | DuckDB, SQL, CTEs, Window Functions          | Análisis de tráfico, errores, performance y priorización de endpoints              |
| [07 - ETL Simple con Python](./07-etl-simple-python) | Python, pandas, ETL, CSV, Parquet            | Limpieza, transformación, métricas de negocio y exportación de datos               |

## Proyectos destacados

### 09 - Pipeline con API REST

Pipeline que consume una API REST pública, guarda la respuesta cruda en JSON, transforma datos anidados en una tabla limpia, valida calidad de datos y genera outputs en CSV y Parquet.

**Habilidades aplicadas:**

* Consumo de APIs REST con `requests`.
* Manejo de JSON anidado.
* Transformación con pandas.
* Validación de nulos y duplicados.
* Exportación a CSV y Parquet.
* Manejo de errores con `timeout` y `raise_for_status()`.

**Explicación breve:**

> Construí un pipeline que extrae datos desde una API REST, conserva el JSON crudo, transforma estructuras anidadas en una tabla analítica y genera outputs reutilizables para análisis.

---

### 08 - Análisis SQL de Logs

Análisis de logs de servidor usando SQL y DuckDB. El proyecto identifica endpoints más usados, errores, tiempos de respuesta, tendencia horaria y ranking de performance.

**Habilidades aplicadas:**

* SQL analítico.
* DuckDB.
* CTEs.
* Window Functions: `RANK()` y `LAG()`.
* Análisis de errores y performance.
* Generación de outputs CSV.

**Explicación breve:**

> Analicé logs de servidor para detectar endpoints críticos combinando volumen de tráfico, errores y latencia. El principal hallazgo fue que `/api/search` debía priorizarse por alto uso, errores y tiempos elevados.

---

### 07 - ETL Simple con Python

Pipeline ETL simple para procesar datos de e-commerce. El proyecto carga datos desde CSV, explora calidad, limpia nulos y duplicados, corrige tipos de datos, calcula métricas de negocio y exporta resultados.

**Habilidades aplicadas:**

* ETL con Python y pandas.
* Limpieza de datos.
* Manejo de nulos y duplicados.
* Cálculo de métricas de negocio.
* Exportación a CSV y Parquet.
* Documentación técnica.

**Explicación breve:**

> Construí un flujo ETL completo para transformar datos crudos de e-commerce en datasets limpios y métricas de negocio listas para análisis.

## Otros proyectos

| Proyecto                                                            | Descripción                                                                                | Herramientas        |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------- |
| [01 - Experimentos de Suplementos](./01-experimentos-suplementos)   | Integración y limpieza de datos de salud, suplementos, experimentos y perfiles de usuarios | Python, pandas      |
| [02 - Limpieza de Datos en Python](./02-limpieza-datos-python)      | Limpieza, estandarización y preparación de datos para análisis                             | Python, pandas      |
| [03 - Pipeline de Datos Retail](./03-pipeline-datos-retail)         | Pipeline para procesar, limpiar, transformar y agregar datos de ventas retail              | Python, pandas, ETL |
| [04 - Limpieza de Campaña Bancaria](./04-limpieza-campana-bancaria) | Limpieza y transformación de datos de una campaña bancaria de marketing                    | Python, pandas      |
| [05 - Pipeline ETL de Energía](./05-pipeline-etl-energia)           | Pipeline ETL para extraer, transformar y cargar datos de energía                           | Python, pandas, ETL |
| [06 - Revisión de Código en Python](./06-revision-codigo-python)    | Evaluación y mejora de código Python aplicando buenas prácticas                            | Python, code review |

## Habilidades aplicadas

* Construcción de pipelines ETL.
* Consumo de APIs REST.
* Procesamiento de JSON.
* Limpieza y transformación de datos.
* Validación de calidad de datos.
* SQL analítico.
* CTEs y Window Functions.
* Manejo de CSV y Parquet.
* Organización de proyectos en GitHub.
* Documentación técnica orientada a entrevistas.

## Estructura del repositorio

```text
data-engineering-portfolio/
├── 01-experimentos-suplementos/
├── 02-limpieza-datos-python/
├── 03-pipeline-datos-retail/
├── 04-limpieza-campana-bancaria/
├── 05-pipeline-etl-energia/
├── 06-revision-codigo-python/
├── 07-etl-simple-python/
├── 08-analisis-sql-logs/
├── 09-pipeline-api-rest/
├── README.md
├── .gitignore
└── LICENSE
```

## Objetivo del portfolio

Este repositorio busca demostrar una progresión práctica hacia Ingeniería de Datos:

```text
datos crudos
    ↓
extracción desde CSV / JSON / APIs
    ↓
limpieza y transformación con Python / SQL
    ↓
validación de calidad
    ↓
outputs analíticos en CSV / Parquet
    ↓
documentación y versionamiento en GitHub
```

## Próximos pasos

La ruta continuará incorporando proyectos de mayor complejidad:

* JOINS SQL.
* Window Functions avanzadas.
* Data Warehouse con modelo dimensional.
* Data Quality.
* Orquestación con Apache Airflow.
* Procesamiento con PySpark.
* Databricks y Delta Lake.
* Data Lake con arquitectura Medallion.

├── README.md
├── .gitignore
└── LICENSE
