# 20 - AWS-style Banking Data Lake

## Pipeline End-to-End en AWS

<p align="center">
  <img src="./assets/aws-cloud-development-services-by-vizsphere.jpeg" alt="AWS-style Banking Data Lake" width="650">
</p>

> Imagen referencial utilizada para representar una arquitectura cloud AWS-style.

## 1. Objetivo

Implementar una simulación local de un Data Lake tipo AWS para datos bancarios, usando Python, DuckDB y Parquet.

El proyecto representa una arquitectura cloud end-to-end sin usar AWS real, sin credenciales, sin `boto3` y sin generar costos. El foco es demostrar diseño de capas, transformación de datos, trazabilidad, consultas analíticas y criterios básicos de seguridad/costos en un entorno reproducible.

## 2. Valor de negocio

Un banco necesita convertir datos operacionales crudos en información confiable para análisis de clientes, canales, sucursales y volumen transaccional.

Este proyecto importa porque permite:

- organizar datos crudos, limpios y analíticos en capas separadas;
- mejorar trazabilidad entre archivos de entrada, transformaciones y resultados;
- separar registros inválidos en cuarentena sin ocultarlos;
- preparar consultas analíticas sobre datos en formato Parquet;
- considerar costos, permisos y arquitectura cloud desde el diseño;
- demostrar una arquitectura tipo AWS sin depender de infraestructura real.

## 3. Arquitectura tipo AWS

El flujo local simula una arquitectura con S3, Glue/Lambda, Athena y logs estilo CloudWatch:

```mermaid
flowchart LR
    A["landing<br/>CSV crudo<br/>S3 landing/raw"] --> B["bronze<br/>Parquet normalizado<br/>S3 bronze"]
    B --> C["silver<br/>limpieza + validación + enriquecimiento<br/>Glue/Lambda transform"]
    C --> D["gold<br/>métricas analíticas<br/>S3 gold"]
    D --> E["Athena-like queries<br/>DuckDB sobre Parquet"]
    E --> F["outputs<br/>query results + summaries JSON<br/>CloudWatch-style logs"]
```

La implementación corre completamente en carpetas locales bajo `data_lake/`, pero conserva los conceptos principales de un Data Lake cloud: zona de ingesta, capas medallion, transformaciones reproducibles, consultas SQL y artefactos de monitoreo.

## 4. Equivalencia local vs AWS

| Componente local | Equivalente AWS | Rol |
| --- | --- | --- |
| `data_lake/landing/` | S3 landing/raw | Zona de ingesta cruda en CSV |
| `data_lake/bronze/` | S3 bronze | Datos normalizados en Parquet, cercanos al raw |
| `data_lake/silver/` | S3 silver + Glue/Lambda | Datos limpios, validados, enriquecidos y particionados |
| `data_lake/gold/` | S3 gold | Métricas analíticas listas para consumo |
| `DuckDB` | Athena | Consultas SQL sobre archivos Parquet |
| `output/pipeline_summary.json` | CloudWatch-style log | Trazabilidad de ejecución, conteos y checks |
| `docs/iam_least_privilege.md` | IAM design | Diseño conceptual de permisos mínimos |
| `docs/cost_control.md` | AWS cost controls | Buenas prácticas de particionamiento, compresión y control de escaneo |

## 5. Estructura del proyecto

```text
20-aws-style-banking-data-lake/
|-- app/
|   |-- generate_banking_landing_data.py
|   |-- build_data_lake.py
|   |-- run_athena_like_queries.py
|   `-- run_pipeline.py
|-- data_lake/
|   |-- landing/
|   |-- bronze/
|   |-- silver/
|   `-- gold/
|-- docs/
|   |-- aws_architecture_mapping.md
|   |-- cost_control.md
|   `-- iam_least_privilege.md
|-- queries/
|   `-- athena_like_queries.sql
|-- output/
|   `-- .gitkeep
|-- README.md
|-- requirements.txt
`-- .gitignore
```

Carpetas principales:

- `app/`: scripts Python del pipeline.
- `data_lake/`: capas locales que simulan S3 landing, bronze, silver y gold.
- `docs/`: documentación de arquitectura AWS equivalente, costos e IAM.
- `queries/`: SQL usado por DuckDB para simular consultas Athena-like.
- `output/`: summaries y resultados generados en ejecución local, ignorados por Git.

## 6. Flujo del pipeline

1. Generación de datos landing: crea CSV bancarios crudos con duplicados, nulos, fechas inválidas, montos faltantes, tipos inconsistentes y referencias inválidas.
2. Conversión a bronze Parquet: normaliza columnas, conserva una estructura cercana al raw y agrega metadata técnica de carga.
3. Limpieza, validación y enriquecimiento en silver: castea fechas/montos, remueve duplicados, normaliza tipos de transacción/canales y une transacciones con cuentas, clientes y sucursales.
4. Separación de registros inválidos en cuarentena: guarda transacciones críticas inválidas en `silver/quarantined_transactions`.
5. Generación de métricas gold: produce datasets analíticos por canal, tipo de transacción, mes, cliente y sucursal.
6. Ejecución de consultas Athena-like con DuckDB: consulta Parquet desde `queries/athena_like_queries.sql` sin usar Athena real.
7. Generación de summaries: escribe resultados y trazabilidad en JSON/CSV locales, incluyendo estado final, conteos, checks de calidad y estimación conceptual de costos.

Los outputs generados durante la ejecución incluyen CSV de landing, Parquet en bronze/silver/gold, resultados de queries y summaries JSON. Todos esos artefactos generados están ignorados por Git para evitar subir datos locales.

## 7. Componentes principales

- `generate_banking_landing_data.py`: genera datos bancarios de ejemplo en la capa landing, con errores controlados para probar calidad de datos.
- `build_data_lake.py`: componente central del proyecto. Cumple el rol tipo Glue/Lambda porque construye bronze, silver y gold, aplica validaciones, enriquece datos, particiona Parquet y genera estimación conceptual de costos.
- `run_athena_like_queries.py`: ejecuta consultas SQL con DuckDB sobre los Parquet generados, simulando Athena.
- `run_pipeline.py`: orquesta el flujo completo y consolida el resumen final en `output/pipeline_summary.json`.

## 8. Resultados de la implementación

Validado localmente en Codespaces:

| Resultado | Valor |
| --- | --- |
| `final_status` | `PASSED` |
| Transacciones en landing | 1257 |
| `enriched_transactions` en silver | 1135 |
| Registros en cuarentena | 120 |
| Datasets gold generados | 5 |
| Queries Athena-like ejecutadas | 5 PASSED |

Checks de calidad registrados:

- duplicados removidos;
- `transaction_id` faltante;
- fechas inválidas;
- montos faltantes;
- referencias inválidas de cuenta;
- tipos de transacción desconocidos;
- registros críticos enviados a cuarentena.

Estos resultados corresponden a la ejecución local del proyecto. No implican uso real de AWS, procesamiento de grandes volúmenes ni costos reales de nube.

## 9. Cómo migrarlo a AWS real

Una migración real podría seguir estos pasos:

1. Crear un bucket S3 con prefixes `landing/`, `bronze/`, `silver/` y `gold/`.
2. Subir CSV reales o archivos batch al prefix `landing/`.
3. Usar Glue Crawler para catalogar schemas en Glue Data Catalog.
4. Usar Glue Job o Lambda para transformar datos desde landing/bronze hacia silver/gold.
5. Guardar Parquet particionado en silver y gold, idealmente por columnas usadas en filtros frecuentes como `year/month`.
6. Consultar datos con Athena usando tablas externas y evitando `SELECT *` en datasets grandes.
7. Configurar IAM least privilege para ingestión, transformación, catalogación y consulta.
8. Configurar billing alerts, Athena workgroups con límites de escaneo y lifecycle policies para controlar costos.

La documentación complementaria está en:

- `docs/aws_architecture_mapping.md`
- `docs/cost_control.md`
- `docs/iam_least_privilege.md`

## 10. Explicación profesional del proyecto

Este proyecto demuestra cómo diseñar un Data Lake bancario estilo AWS sin depender de infraestructura cloud real. La solución organiza datos crudos en landing, convierte información a Parquet en bronze, limpia y enriquece transacciones en silver, separa registros inválidos en cuarentena y publica métricas analíticas en gold.

Sobre esa base, DuckDB ejecuta consultas SQL tipo Athena y el pipeline genera summaries que permiten revisar estado final, conteos, calidad de datos, rutas generadas y consideraciones de costos. Es un proyecto pensado para explicar arquitectura, trazabilidad, calidad, particionamiento, Parquet, consultas analíticas y gobierno básico sin afirmar despliegue real en AWS.

## 11. Aprendizajes técnicos del proyecto

Esta sección resume los conceptos, archivos y decisiones técnicas que conviene saber defender al explicar el proyecto. No reemplaza la documentación de uso; funciona como material de estudio personal sobre arquitectura, calidad, costos y ejecución local.

### 11.1 Conceptos clave

| Concepto | Qué significa en este proyecto |
| --- | --- |
| Landing | Zona local donde se generan CSV crudos que simulan una ingesta bancaria inicial. |
| Bronze | Capa Parquet cercana al raw, con columnas normalizadas y metadata técnica de carga. |
| Silver | Capa limpia, validada, enriquecida y particionada para análisis confiable. |
| Gold | Capa analítica con métricas agregadas por canal, tipo, mes, cliente y sucursal. |
| Parquet | Formato columnar usado para reducir datos escaneados y mejorar consultas analíticas. |
| Particionamiento | Organización de transacciones silver por `year/month` para simular pruning por fecha. |
| Cuarentena | Separación de registros críticos inválidos para trazabilidad sin contaminar silver. |
| Data Quality Checks | Validaciones de duplicados, fechas, montos, IDs, cuentas y tipos de transacción. |
| Glue/Lambda equivalente | Rol conceptual implementado por `build_data_lake.py` para transformar capas. |
| Athena-like queries | Consultas SQL ejecutadas con DuckDB sobre archivos Parquet locales. |
| CloudWatch-style summary | JSON de ejecución con estado final, conteos, checks, rutas y notas de costos. |
| IAM least privilege | Diseño documental de permisos mínimos para una migración futura a AWS real. |
| Control de costos | Uso conceptual de Parquet, particiones, límites de escaneo y alertas de billing. |

### 11.2 Archivos más importantes

| Archivo | Rol principal | Qué aprendí |
| --- | --- | --- |
| `generate_banking_landing_data.py` | Genera datos bancarios crudos y controladamente imperfectos. | Diseñar datos de prueba realistas permite validar reglas de calidad antes de tener datos reales. |
| `build_data_lake.py` | Construye bronze, silver, gold, cuarentena y estimación de costos. | El componente central de un pipeline debe organizar transformaciones, calidad, particiones y evidencia. |
| `run_athena_like_queries.py` | Ejecuta consultas SQL con DuckDB sobre Parquet. | Separar SQL del código Python mejora mantenibilidad y simula mejor un patrón Athena. |
| `run_pipeline.py` | Orquesta el flujo completo y escribe el summary final. | Un pipeline profesional debe tener una entrada clara, logging, manejo de errores y salida trazable. |
| `athena_like_queries.sql` | Contiene las consultas analíticas finales. | Las queries deben responder preguntas de negocio sin depender de `SELECT *` ni de infraestructura cloud real. |

### 11.3 Funciones y códigos destacables

`generate_banking_landing_data.py`

| Función | Por qué importa |
| --- | --- |
| `reset_landing_csvs()` | Limpia CSV generados previamente para que cada ejecución sea reproducible. |
| `write_csv()` | Centraliza la escritura de archivos landing con estructura consistente. |
| `random_date()` | Genera fechas de ejemplo para simular actividad bancaria distribuida. |
| `build_branches()` | Crea sucursales base para enriquecer clientes y métricas posteriores. |
| `build_customers()` | Genera clientes asociados a sucursales, incluyendo variaciones controladas. |
| `build_accounts()` | Crea cuentas bancarias vinculadas a clientes. |
| `build_transactions()` | Es clave porque genera datos messy: duplicados, fechas inválidas, montos faltantes, cuentas inválidas, tipos inconsistentes e IDs vacíos. |
| `generate_landing_data()` | Coordina la generación de todos los CSV landing y devuelve conteos/rutas. |

`build_data_lake.py`

| Función | Por qué importa |
| --- | --- |
| `load_landing_csvs()` | Lee los CSV crudos desde landing para iniciar el procesamiento. |
| `clear_generated_children()` | Limpia artefactos generados sin borrar archivos base como `.gitkeep`. |
| `normalize_text()` | Estandariza texto para reducir inconsistencias de formato. |
| `normalize_key()` | Normaliza claves de negocio usadas en joins y validaciones. |
| `write_single_parquet()` | Escribe datasets Parquet no particionados de forma controlada. |
| `write_partitioned_parquet()` | Escribe Parquet particionado, especialmente útil para silver por `year/month`. |
| `build_bronze_layer()` | Convierte landing a bronze manteniendo cercanía con el raw y agregando metadata. |
| `clean_branches()` | Limpia la dimensión de sucursales. |
| `clean_customers()` | Valida y normaliza clientes contra sucursales válidas. |
| `clean_accounts()` | Valida cuentas contra clientes válidos. |
| `normalize_transactions()` | Aplica reglas críticas de limpieza, normalización y cuarentena de transacciones. |
| `build_silver_layer()` | Construye datos limpios, enriquecidos y particionados para análisis. |
| `build_gold_layer()` | Genera agregados analíticos listos para consulta. |
| `write_cost_estimation()` | Calcula una estimación conceptual local de bytes y reducción por Parquet. |
| `build_data_lake()` | Orquesta bronze, silver, gold, quality checks, costos y rutas generadas. |

`build_data_lake.py` es el archivo central del proyecto porque cumple el rol tipo Glue/Lambda: transforma datos entre capas, aplica validaciones, produce datasets analíticos y genera evidencia técnica de ejecución.

`run_athena_like_queries.py`

| Función | Por qué importa |
| --- | --- |
| `parse_named_queries()` | Lee queries nombradas desde SQL para mantenerlas fuera del código Python. |
| `run_queries()` | Ejecuta las consultas con DuckDB sobre Parquet y guarda resultados/summaries. |
| `main()` | Permite ejecutar el módulo de consultas como script independiente. |

Este archivo separa SQL del código Python y ejecuta consultas DuckDB sobre Parquet, representando el rol conceptual de Athena sin usar AWS real.

`run_pipeline.py`

| Función | Por qué importa |
| --- | --- |
| `configure_logging()` | Configura logs básicos para seguir la ejecución. |
| `write_summary()` | Escribe el summary final de ejecución. |
| `aws_equivalent_services()` | Documenta la equivalencia conceptual entre componentes locales y servicios AWS. |
| `cost_control_notes()` | Resume decisiones de control de costos relevantes para una migración futura. |
| `failed_summary()` | Genera evidencia estructurada si el pipeline falla. |
| `main()` | Orquesta el flujo end-to-end del proyecto. |

`main()` orquesta el flujo completo:

```text
generate_landing_data()
-> build_data_lake()
-> run_queries()
-> write_summary()
```

### 11.4 Qué debo saber explicar técnicamente

- Por qué existen landing, bronze, silver y gold.
- Por qué uso Parquet en vez de dejar todo como CSV.
- Por qué particiono transacciones por `year/month`.
- Qué hace la cuarentena y por qué no conviene mezclar registros inválidos con silver.
- Qué representa DuckDB dentro de una simulación Athena-like.
- Qué representa `build_data_lake.py` como equivalente local de Glue/Lambda.
- Qué representa `run_pipeline.py` como orquestador end-to-end.
- Por qué `data_lake/` y `output/` aparecen casi vacíos en GitHub: los datos generados, Parquet y summaries se crean localmente y están ignorados por Git.

### 11.5 Aprendizaje principal

Un Data Engineer no solo construye pipelines que corren. También diseña arquitectura, capas de datos, reglas de calidad, control de costos, permisos mínimos y evidencia de ejecución para que el proceso sea entendible, auditable y defendible técnicamente.

### 11.6 Resumen técnico corto

```text
generate_banking_landing_data.py crea datos crudos.
build_data_lake.py transforma esos datos en capas bronze, silver y gold.
run_athena_like_queries.py consulta los Parquet con SQL usando DuckDB.
run_pipeline.py orquesta todo el flujo y genera evidencia de ejecución.
```
