# Cómo presentar el Proyecto 22 en una entrevista

## 1. Respuesta breve de 30 segundos

Construí un laboratorio local que representa un pipeline Azure Data Engineering end-to-end para datos de seguros. El proyecto genera datos sintéticos, los ingiere en una capa landing, los mueve a Bronze con trazabilidad, los limpia en Silver, construye cinco datamarts Gold y ejecuta ocho controles de calidad. La orquestación está implementada con un patrón ADF-style y las transformaciones representan notebooks Databricks-style, pero todo corre localmente con Python, pandas y Parquet, sin Azure real, sin credenciales, sin secretos y sin costos cloud.

## 2. Explicación de 2 minutos

El proyecto nace de un problema común en datos: no basta con copiar archivos desde una fuente hacia una carpeta final. Si esos datos alimentan reporting o análisis de negocio, necesitan trazabilidad, validaciones y capas con responsabilidades claras.

Para resolverlo diseñé una arquitectura Medallion local inspirada en Azure. Primero genero datos sintéticos de clientes, pólizas, siniestros y pagos. Esos CSV quedan en landing, que representa la llegada inicial de datos. Luego `landing_to_bronze.py` los convierte a Parquet en Bronze y agrega metadata técnica como `ingestion_timestamp`, `source_file` y `pipeline_run_id`.

Después `bronze_to_silver.py` aplica limpieza básica: elimina duplicados y normaliza texto. Sobre esa capa Silver, `silver_to_gold.py` construye cinco datamarts orientados a consumo: clientes, pólizas, siniestros por producto, primas por segmento y riesgo de pago. Finalmente, `quality_checks.py` valida unicidad, integridad referencial y existencia de los cinco datamarts Gold.

Todo lo coordina `run_pipeline.py` usando `ADFStyleOrchestrator`, que registra actividades, dependencias, estado, duración y errores. En una ejecución limpia el pipeline termina `PASSED`, con 8/8 controles exitosos y 5 datamarts Gold. El aprendizaje principal fue separar claramente orquestación, transformación, calidad y evidencia, manteniendo un diseño que se puede explicar como base para una futura implementación real en Azure.

## 3. Explicación técnica de 5 minutos

La separación landing, Bronze, Silver y Gold existe para evitar mezclar responsabilidades. Landing conserva los CSV generados como llegada inicial. Bronze toma esos archivos y los guarda en Parquet con metadata de ingesta, por lo que ya existe trazabilidad técnica. Silver aplica limpieza básica y deja datasets más confiables para validación y consumo. Gold contiene salidas analíticas orientadas a negocio, no datos crudos.

`run_pipeline.py` es el entrypoint del flujo. Crea una instancia de `ADFStyleOrchestrator` y ejecuta cada etapa como una actividad con dependencias explícitas. Esa clase está en `adf_orchestrator.py` y controla el `pipeline_run_id`, la duración de cada actividad, el estado `SUCCEEDED` o `FAILED` y el mensaje de error si ocurre una excepción. Al final escribe `output/pipeline_summary.json`.

La primera actividad llama a `generate_source_data.py`, que crea datos sintéticos de seguros: 100 clientes, 200 pólizas, 300 siniestros y 400 pagos. Después `landing_to_bronze.py` lee los CSV, agrega columnas de trazabilidad y escribe Parquet en Bronze. Luego `bronze_to_silver.py` elimina duplicados y recorta espacios en columnas texto. No implementa reglas avanzadas de schema enforcement ni cargas incrementales; esa sería una mejora para una versión con Delta Lake.

La etapa Gold está en `silver_to_gold.py`. Allí se cruzan pólizas con clientes y se construyen cinco datamarts: `dim_customer`, `fact_policy`, `claims_by_product`, `premium_by_segment` y `payment_risk`. Después se ejecuta `quality_checks.py`, que valida que los datasets no estén vacíos, que los identificadores principales sean únicos, que las pólizas referencien clientes existentes, que los siniestros referencien pólizas existentes y que existan exactamente cinco archivos Gold.

Conceptualmente, `ADFStyleOrchestrator` representa Azure Data Factory, las carpetas `data/landing`, `data/bronze`, `data/silver` y `data/gold` representan zonas en ADLS Gen2, y los scripts de transformación representan notebooks o jobs en Azure Databricks. La implementación real en Azure necesitaría linked services, managed identities, Key Vault para secretos, Databricks Jobs, Delta Lake, monitoreo con ADF Monitor o Log Analytics, y despliegue por ambientes. Este proyecto no implementa esos servicios; los documenta como equivalencias o mejoras futuras.

## 4. Historia del pipeline paso a paso

| Orden | Archivo | Responsabilidad | Entrada | Salida | Equivalencia Azure |
|---:|---|---|---|---|---|
| 1 | `app/run_pipeline.py` | Inicia el pipeline, crea el orquestador y llama las actividades en orden | Ejecución local del script | Flujo completo y mensaje final | Pipeline trigger o ejecución manual |
| 2 | `app/adf_orchestrator.py` | Registra `pipeline_run_id`, dependencias, estado, duración y errores | Funciones de cada etapa | `output/pipeline_summary.json` | Azure Data Factory pipeline y monitor |
| 3 | `app/generate_source_data.py` | Genera datos sintéticos de clientes, pólizas, siniestros y pagos | Código determinístico con pandas | CSV en `data/landing/` | Extracción o Copy Activity hacia landing |
| 4 | `app/landing_to_bronze.py` | Convierte CSV a Parquet y agrega metadata de ingesta | `data/landing/*.csv` | Parquet en `data/bronze/` | Ingesta hacia Bronze en ADLS |
| 5 | `app/bronze_to_silver.py` | Elimina duplicados y normaliza texto | Parquet en `data/bronze/` | Parquet en `data/silver/` | Notebook Databricks de limpieza |
| 6 | `app/silver_to_gold.py` | Construye cinco datamarts analíticos | Parquet en `data/silver/` | Parquet en `data/gold/` | Notebook Databricks de publicación Gold |
| 7 | `app/quality_checks.py` | Ejecuta ocho controles de calidad y falla si alguno no pasa | Silver y Gold | JSON/CSV de calidad en `output/` | Data quality gate o validación ADF/Databricks |

## 5. Decisiones técnicas

Se eligió una arquitectura Medallion porque permite explicar la madurez progresiva del dato: landing recibe datos, Bronze agrega trazabilidad, Silver limpia y Gold publica salidas orientadas a consumo. Esa separación ayuda a evitar que un error de origen llegue directamente a una métrica de negocio.

La capa landing existe separada de Bronze porque landing representa el punto de llegada. Bronze ya incorpora una acción de ingeniería: lectura, conversión a Parquet y metadata técnica. Esa diferencia es relevante en entrevistas porque muestra que no todo archivo recibido debería tratarse como dato confiable.

Los quality checks se ejecutan después de Gold en el código actual porque una de las reglas valida que existan exactamente cinco datamarts. En una implementación productiva se podrían agregar checks antes de Gold para bloquear datos inválidos y checks después de Gold para validar publicación.

Gold contiene datamarts porque representa la capa de consumo. En vez de exponer tablas crudas, entrega datasets agregados o modelados para análisis: dimensión de clientes, hecho de pólizas, siniestros por producto, primas por segmento y riesgo de pago.

Las dependencias y estados se manejan con `ADFStyleOrchestrator.activity()`. Cada actividad recibe una lista `depends_on`, se mide con `time.perf_counter()` y queda registrada como `SUCCEEDED` o `FAILED`. Si una función falla, el pipeline escribe summary con estado `FAILED` y propaga la excepción.

En Azure real cambiaría el motor y la operación: ADF coordinaría actividades, ADLS Gen2 almacenaría las zonas, Databricks ejecutaría notebooks o jobs con Spark, Delta Lake permitiría cargas incrementales e idempotentes, Key Vault gestionaría secretos, y CI/CD desplegaría el pipeline por ambientes.

## 6. Preguntas probables de entrevista

| Pregunta | Respuesta modelo |
|---|---|
| ¿Qué problema resuelve? | Resuelve cómo organizar un flujo de datos por capas, con trazabilidad, validaciones y salidas analíticas, sin mezclar datos crudos con datamarts de consumo. |
| ¿Qué significa orquestar? | Orquestar es coordinar actividades, dependencias, estado y orden de ejecución. En el proyecto lo hace `ADFStyleOrchestrator`; en Azure lo haría Data Factory. |
| ¿Qué hace ADF? | Azure Data Factory normalmente coordina pipelines, triggers y actividades. Aquí está representado conceptualmente por `adf_orchestrator.py`, no por un servicio real. |
| ¿Cuál es la diferencia entre ingesta y transformación? | Ingesta mueve o registra datos desde la fuente hacia una zona inicial. Transformación cambia estructura, tipos, limpieza o agregaciones. En el proyecto, landing-to-bronze ingiere y silver/gold transforman. |
| ¿Qué diferencia existe entre landing y Bronze? | Landing guarda CSV como llegada inicial. Bronze ya agrega metadata técnica y convierte a Parquet, por lo que tiene trazabilidad de ingesta. |
| ¿Qué diferencia existe entre Bronze, Silver y Gold? | Bronze conserva datos cercanos al origen, Silver aplica limpieza básica y Gold contiene datamarts orientados a análisis. |
| ¿Dónde usarías Databricks? | Lo usaría para ejecutar las transformaciones Bronze-to-Silver y Silver-to-Gold con Spark. En este proyecto se representa con scripts pandas, no con Databricks real. |
| ¿Por qué utilizar PySpark? | PySpark sería útil si el volumen creciera o se necesitara procesamiento distribuido. Este laboratorio no lo implementa porque pandas es suficiente para la escala local. |
| ¿Cómo garantizas calidad de datos? | Implementé ocho checks: unicidad de IDs, integridad referencial y verificación de cinco datamarts Gold. En producción agregaría más reglas y controles previos a Gold. |
| ¿Qué ocurre si falla una actividad? | `ADFStyleOrchestrator.activity()` marca la actividad como `FAILED`, registra el error y el pipeline escribe un summary final fallido antes de propagar la excepción. |
| ¿Cómo implementarías reintentos? | En Azure usaría retry policy de ADF o configuración del job. En el código local agregaría reintentos controlados por actividad, con límite y logging del último error. |
| ¿Cómo harías el pipeline incremental? | Usaría watermark por fecha o `pipeline_run_id`, particiones por periodo y Delta Lake `MERGE`. Actualmente el pipeline es batch local y no incremental. |
| ¿Cómo manejarías secretos? | No hay secretos en este proyecto. En Azure real usaría Key Vault y managed identities, nunca credenciales en el repositorio. |
| ¿Cómo monitorearías el pipeline? | Localmente se revisa `pipeline_summary.json` y los resultados de calidad. En Azure usaría ADF Monitor, Log Analytics y alertas. |
| ¿Cómo desplegarías DEV, QA y PROD? | Separaría parámetros, storage, pipelines y permisos por ambiente. Usaría CI/CD con validaciones antes de promover cambios. No está implementado en este laboratorio. |
| ¿Qué es idempotencia? | Es poder reejecutar una etapa sin duplicar o corromper resultados. Este proyecto es reproducible, pero no implementa idempotencia robusta como limpieza controlada o merges Delta. |
| ¿Qué partes son simuladas localmente? | ADF, ADLS, Databricks y Delta Lake son patrones conceptuales. Lo real implementado es Python, pandas, Parquet, carpetas locales y JSON/CSV de evidencia. |
| ¿Qué mejorarías para producción? | Agregaría schemas explícitos, particionamiento, cargas incrementales, Delta Lake, observabilidad, tests automatizados, retries, manejo de secretos y despliegue por ambientes. |

## 7. Errores que debo evitar al explicarlo

- Decir que se desplegó en Azure. El proyecto es local y representa patrones Azure.
- Afirmar que ADF transforma todos los datos directamente. ADF orquesta; las transformaciones las harían notebooks o jobs.
- Confundir orquestación con transformación.
- Decir que se usó Delta Lake real. El proyecto escribe Parquet; Delta Lake está documentado como mejora futura.
- Decir que se usó PySpark. El código usa pandas.
- Inventar métricas distintas a las validadas por el código vigente.
- No explicar por qué existen landing, Bronze, Silver y Gold.
- Presentarlo como una copia de CSV. El valor está en capas, trazabilidad, calidad, datamarts y evidencia.
- Omitir que no hay credenciales, secretos, recursos cloud ni costos.
- Confundir los datamarts reales: `dim_customer`, `fact_policy`, `claims_by_product`, `premium_by_segment` y `payment_risk`.

## 8. Cierre para entrevista

Este proyecto resume el tipo de criterio que quiero consolidar como Data Engineer Azure: diseñar pipelines reproducibles, separar responsabilidades por capas, orquestar procesos, validar calidad y publicar datos listos para consumo. Aunque corre localmente, está pensado para explicar cómo llevaría ese patrón a Azure con Data Factory, ADLS Gen2, Databricks, Delta Lake, monitoreo y control de costos.
