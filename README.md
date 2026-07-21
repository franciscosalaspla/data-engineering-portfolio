# Portafolio de Ingeniería de Datos

Portfolio práctico de Ingeniería de Datos construido desde mi experiencia conectando cliente, datos, integración y negocio. He trabajado en proyectos relacionados con telemedicina, encuestas de satisfacción, biometría facial, transacciones digitales, venta de productos y pólizas, integrando información desde APIs, JSON, SFTP, SQL, Power BI y servicios cloud.

Este trabajo me ha permitido desarrollar criterio para entender el viaje del cliente, transformar datos operacionales en información analítica, validar calidad, documentar procesos y colaborar con equipos de negocio, producto, BI y desarrollo. Actualmente estoy consolidando ese perfil hacia Ingeniería de Datos mediante proyectos prácticos de pipelines, PySpark, SQL, Data Lake, calidad de datos y arquitecturas cloud-style.

## Contacto

* LinkedIn: [https://bit.ly/4u9E6eU](https://bit.ly/4u9E6eU)
* GitHub: [https://bit.ly/4vouAFH](http://bit.ly/4vouAFH)
* Email: [franciscosalaspla@gmail.com](mailto:franciscosalaspla@gmail.com)
* CV: [Descargar CV](./CV_Francisco_Salas.pdf)

## Perfil

Soy Ingeniero Civil Industrial con experiencia en analítica digital, integración de datos, SQL, APIs/JSON, validación QA/producción, Power BI, Databricks SQL y documentación técnica. Este repositorio consolida mi transición hacia roles de Data Engineer mediante proyectos prácticos, reproducibles y orientados a problemas reales de datos.

Actualmente estoy reforzando proyectos asociados a entornos Azure, pipelines ETL/ELT, PySpark, Databricks, arquitectura Medallion, optimización SQL y calidad de datos.

## Top 3 proyectos destacados

Estos son los tres proyectos que recomiendo revisar primero. Están seleccionados porque muestran arquitectura de datos, procesamiento distribuido y optimización SQL: habilidades relevantes para posiciones Data Engineer en entornos cloud.

| Prioridad | Proyecto | Foco técnico | Qué demuestra |
|---:|---|---|---|
| 1 | [20 - Data Lake Bancario estilo AWS](./20-aws-style-banking-data-lake) | Data Lake, Parquet, capas landing/bronze/silver/gold, DuckDB | Diseño de arquitectura cloud-style, separación por capas, transformación de datos, consultas analíticas y documentación de gobierno básico como IAM least privilege y control de costos |
| 2 | [19 - Procesamiento Bancario con PySpark](./19-pyspark-banking-processing) | PySpark, Spark SQL, limpieza, enriquecimiento y métricas bancarias | Procesamiento distribuido, transformación de datos, validaciones, joins y generación de datasets analíticos aplicables a entornos tipo Databricks |
| 3 | [21 - Optimización de Queries SQL](./21-sql-query-optimization-banking) | SQL, EXPLAIN ANALYZE, benchmark, reescritura de queries, preagregación | Capacidad para medir performance, leer planes de ejecución, detectar cuellos de botella y optimizar consultas con evidencia |

## Proyectos principales

### 20 - Data Lake Bancario estilo AWS

Proyecto principal de arquitectura de datos. Simula localmente un Data Lake bancario con capas landing, bronze, silver y gold. El flujo genera datos bancarios, transforma información cruda en datasets analíticos, escribe salidas en Parquet y permite consultas tipo Athena usando DuckDB.

**Habilidades demostradas:**

* diseño de arquitectura Data Lake;
* separación por capas landing, bronze, silver y gold;
* transformación de datos con Python;
* almacenamiento analítico en Parquet;
* consultas analíticas con DuckDB;
* documentación de equivalencias con servicios AWS;
* criterios de gobierno básico como IAM least privilege y control de costos.

---

### 19 - Procesamiento Bancario con PySpark

Proyecto enfocado en procesamiento distribuido. Procesa datos bancarios en CSV usando PySpark, limpia registros problemáticos, normaliza entidades, cruza transacciones con cuentas, clientes y sucursales, y genera salidas analíticas.

**Habilidades demostradas:**

* procesamiento con PySpark;
* uso de Spark SQL/DataFrames;
* limpieza y normalización de datos;
* validación de nulos, duplicados y fechas;
* joins entre entidades bancarias;
* generación de métricas por cliente, sucursal y periodo;
* base técnica aplicable a Databricks y pipelines distribuidos.

---

### 21 - Optimización de Queries SQL

Proyecto enfocado en performance SQL. Construye un laboratorio local con logs transaccionales bancarios, ejecuta queries baseline y optimizadas, analiza planes con EXPLAIN ANALYZE y mide mejoras con benchmark reproducible.

**Habilidades demostradas:**

* SQL analítico;
* lectura de EXPLAIN ANALYZE;
* identificación de cuellos de botella;
* reescritura de queries;
* uso de preagregaciones;
* uso de índices con criterio;
* medición de performance con benchmark.

## Otros proyectos

| Proyecto | Descripción | Herramientas |
|---|---|---|
| [14 - Data Quality con Great Expectations](./14-data-quality-great-expectations) | Validaciones de calidad, revisión de errores y reportes de control sobre datos tabulares | Great Expectations, Python |
| [18 - Pipeline Dockerizado Agent Loop](./18-pipeline-dockerizado-agent-loop) | Pipeline dbt dockerizado con validación reproducible y flujo tipo agent loop | Docker, dbt, DuckDB |
| [17 - dbt Profesional E-commerce](./17-dbt-professional-ecommerce) | Proyecto dbt con staging, intermediate, marts, tests, snapshot SCD Type 2 y modelo incremental | dbt, DuckDB, SQL |
| [16 - Orquestación Airflow](./16-orquestacion-airflow) | Orquestación de pipelines y validaciones con DAGs | Airflow, Python |
| [15 - dbt Profesional](./15-dbt-profesional) | Transformaciones SQL modulares con dbt, modelos, tests y documentación | dbt, DuckDB, SQL |
| [13 - Data Warehouse Dimensional](./13-data-warehouse-dimensional) | Modelo dimensional con dimensiones, tabla de hechos y análisis SQL | DuckDB, SQL |
| [09 - Pipeline con API REST](./09-pipeline-api-rest) | Consumo de API REST, transformación de JSON y generación de outputs analíticos | Python, requests, pandas |
| [08 - Análisis SQL de Logs](./08-analisis-sql-logs) | Análisis SQL de logs, errores, tráfico y tiempos de respuesta | DuckDB, SQL |
| [07 - ETL Simple con Python](./07-etl-simple-python) | Pipeline ETL básico con limpieza, transformación y exportación | Python, pandas |

## Habilidades aplicadas

* Diseño de pipelines ETL/ELT.
* Arquitectura Data Lake y enfoque Medallion.
* Capas landing, bronze, silver y gold.
* Procesamiento con Python, SQL, DuckDB y PySpark.
* Base técnica aplicable a Databricks y Spark SQL.
* Almacenamiento analítico en Parquet.
* Optimización SQL con EXPLAIN ANALYZE.
* Validaciones de calidad de datos.
* Revisión de errores y trazabilidad.
* Modelado dimensional y transformaciones dbt.
* Orquestación con Airflow.
* Dockerización y flujos reproducibles.
* Git, ramas, pull requests y documentación técnica.
