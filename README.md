# Portafolio de Ingeniería de Datos

Portfolio práctico de Ingeniería de Datos enfocado en pipelines, SQL, calidad de datos, arquitectura Data Lake, procesamiento analítico y documentación técnica defendible en entrevistas.

## Contacto

* LinkedIn: [https://bit.ly/4u9E6eU](https://bit.ly/4u9E6eU)
* GitHub: [https://bit.ly/4vouAFH](http://bit.ly/4vouAFH)
* Email: [franciscosalaspla@gmail.com](mailto:franciscosalaspla@gmail.com)
* CV: [Descargar CV](./CV_Francisco_Salas.pdf)

## Perfil

Soy Ingeniero Civil Industrial con experiencia en analítica digital, integración de datos, SQL, APIs/JSON, validación QA/producción, Power BI, Databricks SQL y documentación técnica. Este repositorio consolida mi transición hacia roles de Data Engineer mediante proyectos prácticos.

## Top 3 proyectos para entrevistas técnicas

Estos son los tres proyectos que recomiendo revisar primero. Están seleccionados porque cubren arquitectura Data Lake en AWS, optimización SQL y calidad/control de datos: tres áreas críticas para roles de Ingeniería de Datos.

| Prioridad | Proyecto | Foco técnico | Por qué es defendible en entrevista |
|---:|---|---|---|
| 1 | [20 - AWS-Style Banking Data Lake](./20-aws-style-banking-data-lake) | AWS-style Data Lake, Parquet, capas landing/bronze/silver/gold, DuckDB | Permite explicar arquitectura tipo S3 + Glue/Lambda + Athena, separación por capas, transformación, consultas analíticas, IAM least privilege y control de costos |
| 2 | [21 - Optimizacion de Queries SQL](./21-sql-query-optimization-banking) | SQL, EXPLAIN ANALYZE, benchmark, reescritura de queries, preagregación | Permite demostrar que no solo escribo SQL, sino que mido performance, leo planes de ejecución y optimizo consultas con evidencia |
| 3 | [14 - Data Quality con Great Expectations](./14-data-quality-great-expectations) | Data Quality, validaciones, expectation-style checks, revisión de errores | Permite hablar de controles de calidad, validación automática, trazabilidad de errores y revisión de datos antes de disponibilizarlos |

## Proyectos destacados para defender

### 20 - AWS-Style Banking Data Lake

Proyecto principal para entrevistas con foco AWS. Construye una simulación local de un Data Lake bancario con capas landing, bronze, silver y gold. El flujo genera datos bancarios, transforma información cruda en datasets analíticos, escribe salidas en Parquet y permite consultas tipo Athena usando DuckDB.

**Qué demuestra:**

* diseño de arquitectura Data Lake estilo AWS;
* separación de datos por capas;
* transformación y enriquecimiento de datos;
* uso de Parquet para almacenamiento analítico;
* consultas analíticas tipo Athena con DuckDB;
* documentación de IAM least privilege y control de costos;
* criterio para hablar de S3, Glue/Lambda, Athena y gobierno básico de datos.

**Cómo lo explicaría en entrevista:**

> Construí una simulación local de un Data Lake bancario estilo AWS. Separé los datos en landing, bronze, silver y gold, transformé datos crudos en salidas analíticas en Parquet y ejecuté consultas tipo Athena con DuckDB. El proyecto también documenta equivalencias con servicios AWS, control de costos e IAM least privilege.

---

### 21 - Optimizacion de Queries SQL

Proyecto enfocado en performance SQL. Construye un laboratorio local con 150.000 logs transaccionales bancarios, ejecuta queries baseline y optimizadas, analiza planes con EXPLAIN ANALYZE y mide mejoras reales con benchmark reproducible.

**Qué demuestra:**

* SQL analítico;
* lectura de EXPLAIN ANALYZE;
* identificación de cuellos de botella;
* reescritura de queries;
* uso de preagregaciones;
* uso de índices con criterio;
* medición de performance con benchmark.

**Cómo lo explicaría en entrevista:**

> Construí un laboratorio de optimización SQL sobre datos bancarios. Ejecuté 4 queries baseline y 4 optimizadas, medí cada par con 3 iteraciones y documenté el impacto. El valor del proyecto es mostrar una metodología concreta: medir, leer el plan, optimizar y volver a medir.

---

### 14 - Data Quality con Great Expectations

Proyecto enfocado en calidad y control de datos. Implementa validaciones tipo expectation-based checks sobre datos tabulares, identifica errores, registra fallas y genera evidencia para revisar la calidad antes de usar los datos en procesos analíticos.

Este proyecto debe entenderse como un laboratorio local de calidad de datos inspirado en Great Expectations y en controles estilo expectations, no como un sistema productivo.

**Qué demuestra:**

* validaciones de calidad de datos;
* control de nulos, duplicados y reglas de negocio;
* revisión de registros problemáticos;
* generación de reportes de validación;
* trazabilidad de errores;
* criterio para detener o revisar datos antes de consumirlos.

**Cómo lo explicaría en entrevista:**

> Implementé un laboratorio local de calidad de datos con validaciones tipo expectations. El proyecto revisa reglas sobre datos tabulares, identifica fallas, genera reportes y deja evidencia de qué datos deben corregirse antes de alimentar procesos analíticos.

## Otros proyectos

| Proyecto | Descripción | Herramientas |
|---|---|---|
| [19 - PySpark Banking Processing](./19-pyspark-banking-processing) | Procesamiento bancario con PySpark, limpieza, enriquecimiento y métricas analíticas | PySpark, Python |
| [18 - Pipeline Dockerizado Agent Loop](./18-pipeline-dockerizado-agent-loop) | Pipeline dbt dockerizado con validación reproducible y flujo tipo agent loop | Docker, dbt, DuckDB |
| [17 - dbt Profesional E-commerce](./17-dbt-professional-ecommerce) | Proyecto dbt con staging, intermediate, marts, tests, snapshot SCD Type 2 y modelo incremental | dbt, DuckDB, SQL |
| [16 - Orquestación Airflow](./16-orquestacion-airflow) | Orquestación de pipelines y validaciones con DAGs | Airflow, Python |
| [15 - dbt Profesional](./15-dbt-profesional) | Transformaciones SQL modulares con dbt, modelos, tests y documentación | dbt, DuckDB, SQL |
| [13 - Data Warehouse Dimensional](./13-data-warehouse-dimensional) | Modelo dimensional con dimensiones, tabla de hechos y análisis SQL | DuckDB, SQL |
| [09 - Pipeline con API REST](./09-pipeline-api-rest) | Consumo de API REST, transformación de JSON y generación de outputs analíticos | Python, requests, pandas |
| [08 - Análisis SQL de Logs](./08-analisis-sql-logs) | Análisis SQL de logs, errores, tráfico y tiempos de respuesta | DuckDB, SQL |
| [07 - ETL Simple con Python](./07-etl-simple-python) | Pipeline ETL básico con limpieza, transformación y exportación | Python, pandas |
| [06 - Revisión de Código en Python](./06-revision-codigo-python) | Revisión y mejora de código Python aplicando buenas prácticas | Python, code review |

## Habilidades aplicadas

* Diseño de pipelines ETL/ELT.
* Arquitectura Data Lake estilo AWS.
* Separación por capas landing, bronze, silver y gold.
* Procesamiento con Python, SQL, DuckDB y PySpark.
* Almacenamiento analítico en Parquet.
* Optimizacion SQL con EXPLAIN ANALYZE.
* Validaciones de calidad de datos.
* Revisión de errores y trazabilidad.
* Modelado dimensional y transformaciones dbt.
* Orquestación con Airflow.
* Dockerización de pipelines.
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
├── 10-masterclass-joins-sql/
├── 11-window-functions-sql/
├── 12-limpieza-pandas/
├── 13-data-warehouse-dimensional/
├── 14-data-quality-great-expectations/
├── 15-dbt-profesional/
├── 16-orquestacion-airflow/
├── 17-dbt-professional-ecommerce/
├── 18-pipeline-dockerizado-agent-loop/
├── 19-pyspark-banking-processing/
├── 20-aws-style-banking-data-lake/
├── 21-sql-query-optimization-banking/
├── templates/
├── README.md
├── CV_Francisco_Salas.pdf
└── LICENSE
```

## Objetivo del portfolio

Este repositorio busca demostrar una progresión práctica hacia Ingeniería de Datos:

```text
datos crudos
    ↓
ingesta desde CSV / JSON / APIs
    ↓
limpieza, validación y control de calidad
    ↓
transformación con Python / SQL / dbt / PySpark
    ↓
almacenamiento analítico en Parquet y capas tipo Data Lake
    ↓
orquestación, optimización SQL y documentación técnica
    ↓
proyectos defendibles en entrevista
```

## Próximos pasos

La evolución natural del portfolio puede avanzar hacia:

* Integración con servicios cloud administrados.
* Databricks y Delta Lake.
* CI/CD para pipelines de datos.
* Monitoreo de calidad y costos.
* Casos incrementales con mayor volumen de datos.
