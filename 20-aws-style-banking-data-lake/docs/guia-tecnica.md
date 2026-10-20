# Guía técnica y ejecución local

Esta guía conserva el detalle técnico del proyecto. El recorrido de negocio está en el [README principal](../README.md#aws-inicio).

## 1. Ejecutar el recorrido

Desde la raíz de este proyecto, en un entorno Python compatible con las versiones de [requirements.txt](../requirements.txt):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app/run_pipeline.py
```

El proyecto usa Pandas, PyArrow y DuckDB. La ejecución genera archivos locales y no requiere una cuenta AWS.

El comando regenera los CSV de entrada con la semilla definida en el generador y reconstruye Bronze, Silver y Gold. Es una reconstrucción completa de datos de prueba. Las fechas de carga y ejecución cambian en cada corrida.

## 2. Qué revisar al terminar

| Salida generada | Qué contiene |
|---|---|
| `data_lake/landing/` | CSV sintéticos de entrada. |
| `data_lake/bronze/` | Parquet con datos cercanos al origen y metadatos de carga. |
| `data_lake/silver/` | Datos limpios, transacciones enriquecidas y registros en cuarentena. |
| `data_lake/gold/` | Cinco conjuntos analíticos. |
| `output/athena_like_query_results.csv` | Resultados de las consultas. |
| `output/query_summary.json` | Estado y número de filas de cada consulta. |
| `output/pipeline_summary.json` | Estado global, conteos, controles, duración y rutas. |
| `output/cost_estimation.json` | Tamaños de archivos y estimaciones conceptuales; no es una factura AWS. |

Estos archivos se generan al ejecutar el proyecto y están excluidos del repositorio por [.gitignore](../.gitignore). Por eso no se enlazan aquí como archivos publicados.

Para comprobar una nueva ejecución, revisar sus resúmenes y contrastar entrada, duplicados, cuarentena y transacciones preparadas. El estado `PASSED` de las consultas registra que el SQL terminó sin excepción; no comprueba por sí solo las cifras de negocio.

La carpeta Silver incluye una cuarentena de transacciones. Los clientes y las cuentas se limpian mediante filtros y deduplicación; sus registros descartados no tienen una cuarentena independiente. El campo `invalid_reason` conserva un motivo por transacción, según el orden de las reglas del código.

La [equivalencia con AWS](./aws_architecture_mapping.md), el [diseño de permisos](./iam_least_privilege.md) y el [control conceptual de costos](./cost_control.md) describen decisiones para una posible implementación cloud.

## 3. Conceptos y decisiones

Esta sección funciona como material de estudio personal para defender el proyecto técnicamente. Resume los conceptos, archivos y decisiones que conviene explicar con claridad.

### 3.1 Conceptos clave

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

### 3.2 Archivos más importantes

| Archivo | Rol principal | Qué aprendí |
| --- | --- | --- |
| `generate_banking_landing_data.py` | Genera datos bancarios crudos y controladamente imperfectos. | Diseñar datos de prueba realistas permite validar reglas de calidad antes de tener datos reales. |
| `build_data_lake.py` | Construye bronze, silver, gold, cuarentena y estimación de costos. | El componente central de un pipeline debe organizar transformaciones, calidad, particiones y evidencia. |
| `run_athena_like_queries.py` | Ejecuta consultas SQL con DuckDB sobre Parquet. | Separar SQL del código Python mejora mantenibilidad y simula mejor un patrón Athena. |
| `run_pipeline.py` | Orquesta el flujo completo y escribe el summary final. | Un pipeline profesional debe tener una entrada clara, logging, manejo de errores y salida trazable. |
| `athena_like_queries.sql` | Contiene las consultas analíticas finales. | Las queries deben responder preguntas de negocio sin depender de `SELECT *` ni de infraestructura cloud real. |

### 3.3 Funciones y códigos destacables

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

### 3.4 Qué debo saber explicar técnicamente

- Por qué existen landing, bronze, silver y gold.
- Por qué uso Parquet en vez de dejar todo como CSV.
- Por qué particiono transacciones por `year/month`.
- Qué hace la cuarentena y por qué no conviene mezclar registros inválidos con silver.
- Qué representa DuckDB dentro de una simulación Athena-like.
- Qué representa `build_data_lake.py` como equivalente local de Glue/Lambda.
- Qué representa `run_pipeline.py` como orquestador end-to-end.
- Por qué `data_lake/` y `output/` aparecen casi vacíos en GitHub: los datos generados, Parquet y summaries se crean localmente y están ignorados por Git.

### 3.5 Aprendizaje principal

Un Data Engineer no solo construye pipelines que corren. También diseña arquitectura, capas de datos, reglas de calidad, control de costos, permisos mínimos y evidencia de ejecución para que el proceso sea entendible, auditable y defendible técnicamente.


