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
