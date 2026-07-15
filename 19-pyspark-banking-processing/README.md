# Proyecto 19 - Procesamiento Bancario con PySpark

## Objetivo

Construir un pipeline de procesamiento de datos bancarios usando PySpark, simulando un escenario donde los datos empiezan a superar la comodidad de un flujo local con pandas y requieren un motor preparado para transformaciones distribuidas.

El proyecto procesa archivos CSV crudos de un sistema bancario, aplica limpieza y normalización, ejecuta validaciones básicas de calidad, genera agregaciones analíticas, usa Window Functions y guarda salidas en formato Parquet.

## Card asociada

```text
Procesamiento con PySpark
```

## Fuente de datos

La fuente esperada es un dataset bancario generado desde la sección Datasets & APIs de la plataforma:

```text
Sistema Bancario
5.000 filas
CSV
Realista / messy
```

El dataset real incluye 12 archivos, pero esta primera versión procesa principalmente:

```text
finanzas_transactions.csv
finanzas_accounts.csv
finanzas_customers.csv
finanzas_branches.csv
```

Los CSV reales deben copiarse en:

```text
19-pyspark-banking-processing/data/raw/
```

Si esos archivos no existen, el pipeline ejecuta automáticamente `app/generate_sample_data.py` y genera datos bancarios de ejemplo para que el proyecto pueda correr sin depender todavía del dataset real.

## Valor de negocio

Un banco necesita transformar transacciones operacionales en datos confiables para análisis de volumen, canales, sucursales, clientes y señales simples de riesgo.

Este proyecto demuestra cómo construir una base analítica reproducible a partir de CSV crudos:

```text
datos bancarios raw
    -> limpieza y normalización
    -> validación de calidad
    -> enriquecimiento con cuentas, clientes y sucursales
    -> métricas por mes, canal, tipo y sucursal
    -> rankings de clientes
    -> Parquet listo para consumo analítico
```

## Arquitectura

```text
CSV raw bancario
    -> SparkSession
    -> lectura con schema explícito
    -> limpieza de whitespace, nulos y duplicados
    -> casteo de fechas y columnas numéricas
    -> columnas derivadas
    -> joins entre transactions, accounts, customers y branches
    -> validaciones básicas de calidad
    -> agregaciones analíticas
    -> Window Functions
    -> Parquet particionado por year y month
    -> output/pipeline_summary.json
```

## Estructura

```text
19-pyspark-banking-processing/
|-- app/
|   |-- generate_sample_data.py
|   |-- process_with_pyspark.py
|   `-- run_pipeline.py
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- analytics/
|-- output/
|   `-- .gitkeep
|-- README.md
|-- requirements.txt
`-- .gitignore
```

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
cd 19-pyspark-banking-processing
pip install -r requirements.txt
python3 app/run_pipeline.py
```

PySpark requiere Java. Antes de ejecutar, valida que exista un runtime Java disponible:

```bash
java -version
```

En Codespaces normalmente se puede instalar Java con paquetes del sistema si la imagen base no lo trae disponible.

Validaciones recomendadas:

```bash
python3 -m py_compile app/generate_sample_data.py app/process_with_pyspark.py app/run_pipeline.py
python3 -c "from pyspark.sql import SparkSession; print('pyspark ok')"
python3 app/run_pipeline.py
cat output/pipeline_summary.json
find data/analytics -type f
```

## SparkSession

`SparkSession` es el punto de entrada principal para trabajar con Spark desde PySpark. En este proyecto se usa para:

```text
crear la aplicación Spark local
leer CSV con schemas explícitos
construir DataFrames
ejecutar transformaciones
guardar outputs en Parquet
```

El pipeline usa modo local con `local[*]`. No afirma correr en cluster, Databricks ni producción.

## Transformations vs Actions

El proyecto usa transformations como:

```text
select
filter
withColumn
join
groupBy
agg
```

Estas operaciones construyen un plan lógico. Spark no ejecuta el trabajo inmediatamente.

El proyecto usa actions como:

```text
count
write
collect
```

Estas operaciones disparan la ejecución real del plan.

## Lazy Evaluation

Spark aplica lazy evaluation: las transformaciones se acumulan hasta que una action obliga a ejecutar el pipeline.

Esto permite que Spark optimice el plan antes de leer, transformar y escribir datos. En este proyecto, los `count()` se usan para registrar conteos y validaciones, mientras que los `write()` materializan los Parquet finales.

## Limpieza y columnas derivadas

El procesamiento principal aplica:

```text
trim de strings
normalización a minúsculas
deduplicación por claves
filtrado de claves críticas nulas
casteo de fechas
casteo de montos
```

Columnas derivadas:

```text
transaction_date
year
month
amount_abs
risk_flag
```

`risk_flag` marca transacciones con monto absoluto alto, estados fallidos/reversados o canales desconocidos. Es una regla simple de calidad analítica, no un modelo de fraude.

## Agregaciones

El pipeline genera métricas bancarias con `groupBy` y `agg`, por ejemplo:

```text
monto total por mes y sucursal
cantidad de transacciones por mes y sucursal
monto promedio por canal
transacciones por tipo
cantidad de transacciones con risk_flag
```

La salida principal de agregaciones queda en:

```text
data/analytics/monthly_branch_metrics/
```

## Window Functions

El proyecto usa Window Functions para:

```text
ranking de clientes por monto transaccional absoluto
monto acumulado por cuenta en enriched_transactions
```

La salida del ranking queda en:

```text
data/analytics/customer_transaction_ranking/
```

## Particionamiento

La salida enriquecida de transacciones se guarda como Parquet particionado por:

```text
year
month
```

Ruta:

```text
data/analytics/enriched_transactions/
```

Este patrón permite organizar datos transaccionales por tiempo y facilita lecturas analíticas filtradas por periodo.

## Outputs generados

```text
data/processed/transactions_clean/
data/processed/accounts_clean/
data/processed/customers_clean/
data/analytics/enriched_transactions/
data/analytics/monthly_branch_metrics/
data/analytics/customer_transaction_ranking/
output/pipeline_summary.json
```

`pipeline_summary.json` incluye:

```text
final_status
started_at
finished_at
duration_seconds
fallback_data_generated
spark_app_name
input_counts
output_counts
generated_paths
main_metrics
validations
```

## Pandas vs PySpark

Pandas es muy útil para análisis local, exploración rápida y datasets que caben cómodamente en memoria.

PySpark se vuelve más relevante cuando el volumen crece, cuando las transformaciones se benefician de ejecución distribuida o cuando se necesita trabajar con formatos analíticos como Parquet de forma más cercana a plataformas de datos modernas.

Este proyecto no inventa métricas de performance. La comparación es conceptual: el pipeline corre localmente, pero usa APIs y patrones de Spark que escalan mejor que un flujo basado solo en pandas.

## Loop Engineering aplicado

```text
objetivo
    Procesar datos bancarios raw con PySpark.

plan
    Leer CSV con schema explícito, limpiar, validar, enriquecer, agregar y escribir Parquet.

implementación
    Scripts Python separados para fallback de datos, procesamiento Spark y orquestación.

ejecución
    python3 app/run_pipeline.py

observación
    Revisar logs, conteos, métricas y validaciones.

corrección
    Ajustar schemas, reglas de limpieza o archivos raw si hay errores.

validación
    Confirmar Parquet generado y revisar output/pipeline_summary.json.

registro
    Guardar evidencia de ejecución en pipeline_summary.json.

revisión humana
    Evaluar si las métricas y reglas de riesgo son consistentes con el caso bancario.
```

## Cómo contar este proyecto en entrevista

### Hook

Construí un pipeline bancario con PySpark que lee CSV crudos con schema explícito, limpia datos messy, valida calidad, enriquece transacciones con cuentas, clientes y sucursales, y genera salidas Parquet analíticas.

### Situación

El portfolio ya tenía proyectos con pandas, SQL y dbt. Faltaba demostrar procesamiento con Spark, especialmente transformations, actions, lazy evaluation, particionamiento y Window Functions.

### Tarea

Crear un proyecto reproducible que funcione incluso sin los CSV reales, pero que esté listo para recibir el dataset bancario descargado desde la plataforma.

### Acciones

* Definí schemas explícitos para las cuatro tablas principales.
* Implementé fallback de datos sample bancarios con condiciones messy controladas.
* Limpié whitespace, nulos, duplicados, fechas y montos.
* Generé columnas derivadas como `year`, `month`, `amount_abs` y `risk_flag`.
* Apliqué joins entre transacciones, cuentas, clientes y sucursales.
* Creé agregaciones bancarias y ranking de clientes con Window Functions.
* Guardé outputs en Parquet, incluyendo una salida particionada por `year` y `month`.
* Dejé evidencia de ejecución en `output/pipeline_summary.json`.

### Resultado

El proyecto demuestra procesamiento bancario con PySpark de punta a punta en entorno local, sin afirmar uso de cluster ni métricas de performance no medidas.

## Lecciones aprendidas

* Spark separa claramente transformations y actions.
* Definir schemas explícitos reduce ambigüedad al leer CSV messy.
* Parquet es más adecuado que CSV para outputs analíticos.
* El particionamiento debe responder a patrones de consulta, no aplicarse por costumbre.
* Window Functions permiten resolver rankings y acumulados sin convertir el proyecto en SQL.
* Un summary JSON ayuda a dejar trazabilidad técnica del pipeline.
