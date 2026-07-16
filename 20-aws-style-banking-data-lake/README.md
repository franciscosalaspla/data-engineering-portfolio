# 20 - AWS-style Banking Data Lake

## 1. Objetivo

Implementar una simulacion local de un Data Lake tipo AWS para datos bancarios, usando Python, DuckDB y Parquet.

El proyecto representa una arquitectura cloud end-to-end sin usar AWS real, sin credenciales, sin `boto3` y sin generar costos. El foco es demostrar diseno de capas, transformacion de datos, trazabilidad, consultas analiticas y criterios basicos de seguridad/costos en un entorno reproducible.

## 2. Valor de negocio

Un banco necesita convertir datos operacionales crudos en informacion confiable para analisis de clientes, canales, sucursales y volumen transaccional.

Este proyecto importa porque permite:

- organizar datos crudos, limpios y analiticos en capas separadas;
- mejorar trazabilidad entre archivos de entrada, transformaciones y resultados;
- separar registros invalidos en cuarentena sin ocultarlos;
- preparar consultas analiticas sobre datos en formato Parquet;
- considerar costos, permisos y arquitectura cloud desde el diseno;
- demostrar una arquitectura tipo AWS sin depender de infraestructura real.

## 3. Arquitectura tipo AWS

El flujo local simula una arquitectura con S3, Glue/Lambda, Athena y logs estilo CloudWatch:

```mermaid
flowchart LR
    A["landing<br/>CSV crudo<br/>S3 landing/raw"] --> B["bronze<br/>Parquet normalizado<br/>S3 bronze"]
    B --> C["silver<br/>limpieza + validacion + enriquecimiento<br/>Glue/Lambda transform"]
    C --> D["gold<br/>metricas analiticas<br/>S3 gold"]
    D --> E["Athena-like queries<br/>DuckDB sobre Parquet"]
    E --> F["outputs<br/>query results + summaries JSON<br/>CloudWatch-style logs"]
```

La implementacion corre completamente en carpetas locales bajo `data_lake/`, pero conserva los conceptos principales de un Data Lake cloud: zona de ingesta, capas medallion, transformaciones reproducibles, consultas SQL y artefactos de monitoreo.

## 4. Equivalencia local vs AWS

| Componente local | Equivalente AWS | Rol |
| --- | --- | --- |
| `data_lake/landing/` | S3 landing/raw | Zona de ingesta cruda en CSV |
| `data_lake/bronze/` | S3 bronze | Datos normalizados en Parquet, cercanos al raw |
| `data_lake/silver/` | S3 silver + Glue/Lambda | Datos limpios, validados, enriquecidos y particionados |
| `data_lake/gold/` | S3 gold | Metricas analiticas listas para consumo |
| `DuckDB` | Athena | Consultas SQL sobre archivos Parquet |
| `output/pipeline_summary.json` | CloudWatch-style log | Trazabilidad de ejecucion, conteos y checks |
| `docs/iam_least_privilege.md` | IAM design | Diseno conceptual de permisos minimos |
| `docs/cost_control.md` | AWS cost controls | Buenas practicas de particionamiento, compresion y control de escaneo |

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
- `docs/`: documentacion de arquitectura AWS equivalente, costos e IAM.
- `queries/`: SQL usado por DuckDB para simular consultas Athena-like.
- `output/`: summaries y resultados generados en ejecucion local, ignorados por Git.

## 6. Flujo del pipeline

1. Generacion de datos landing: crea CSV bancarios crudos con duplicados, nulos, fechas invalidas, montos faltantes, tipos inconsistentes y referencias invalidas.
2. Conversion a bronze Parquet: normaliza columnas, conserva una estructura cercana al raw y agrega metadata tecnica de carga.
3. Limpieza, validacion y enriquecimiento en silver: castea fechas/montos, remueve duplicados, normaliza tipos de transaccion/canales y une transacciones con cuentas, clientes y sucursales.
4. Separacion de registros invalidos en cuarentena: guarda transacciones criticas invalidas en `silver/quarantined_transactions`.
5. Generacion de metricas gold: produce datasets analiticos por canal, tipo de transaccion, mes, cliente y sucursal.
6. Ejecucion de consultas Athena-like con DuckDB: consulta Parquet desde `queries/athena_like_queries.sql` sin usar Athena real.
7. Generacion de summaries: escribe resultados y trazabilidad en JSON/CSV locales, incluyendo estado final, conteos, checks de calidad y estimacion conceptual de costos.

Los outputs generados durante la ejecucion incluyen CSV de landing, Parquet en bronze/silver/gold, resultados de queries y summaries JSON. Todos esos artefactos generados estan ignorados por Git para evitar subir datos locales.

## 7. Componentes principales

- `generate_banking_landing_data.py`: genera datos bancarios de ejemplo en la capa landing, con errores controlados para probar calidad de datos.
- `build_data_lake.py`: componente central del proyecto. Cumple el rol tipo Glue/Lambda porque construye bronze, silver y gold, aplica validaciones, enriquece datos, particiona Parquet y genera estimacion conceptual de costos.
- `run_athena_like_queries.py`: ejecuta consultas SQL con DuckDB sobre los Parquet generados, simulando Athena.
- `run_pipeline.py`: orquesta el flujo completo y consolida el resumen final en `output/pipeline_summary.json`.

## 8. Resultados de la implementacion

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
- fechas invalidas;
- montos faltantes;
- referencias invalidas de cuenta;
- tipos de transaccion desconocidos;
- registros criticos enviados a cuarentena.

Estos resultados corresponden a la ejecucion local del proyecto. No implican uso real de AWS, procesamiento de grandes volumenes ni costos reales de nube.

## 9. Como migrarlo a AWS real

Una migracion real podria seguir estos pasos:

1. Crear un bucket S3 con prefixes `landing/`, `bronze/`, `silver/` y `gold/`.
2. Subir CSV reales o archivos batch al prefix `landing/`.
3. Usar Glue Crawler para catalogar schemas en Glue Data Catalog.
4. Usar Glue Job o Lambda para transformar datos desde landing/bronze hacia silver/gold.
5. Guardar Parquet particionado en silver y gold, idealmente por columnas usadas en filtros frecuentes como `year/month`.
6. Consultar datos con Athena usando tablas externas y evitando `SELECT *` en datasets grandes.
7. Configurar IAM least privilege para ingestion, transformacion, catalogacion y consulta.
8. Configurar billing alerts, Athena workgroups con limites de escaneo y lifecycle policies para controlar costos.

La documentacion complementaria esta en:

- `docs/aws_architecture_mapping.md`
- `docs/cost_control.md`
- `docs/iam_least_privilege.md`

## 10. Explicacion profesional del proyecto

Este proyecto demuestra como disenar un Data Lake bancario estilo AWS sin depender de infraestructura cloud real. La solucion organiza datos crudos en landing, convierte informacion a Parquet en bronze, limpia y enriquece transacciones en silver, separa registros invalidos en cuarentena y publica metricas analiticas en gold.

Sobre esa base, DuckDB ejecuta consultas SQL tipo Athena y el pipeline genera summaries que permiten revisar estado final, conteos, calidad de datos, rutas generadas y consideraciones de costos. Es un proyecto pensado para explicar arquitectura, trazabilidad, calidad, particionamiento, Parquet, consultas analiticas y gobierno basico sin afirmar despliegue real en AWS.
