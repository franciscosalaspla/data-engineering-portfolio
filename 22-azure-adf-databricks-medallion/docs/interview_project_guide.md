# Cómo contar el Proyecto 22 en una entrevista

## Hook

**Construí un pipeline end-to-end para seguros que convierte datos crudos en cinco datamarts confiables, con trazabilidad y ocho controles de calidad, siguiendo patrones de Azure Data Factory, Databricks y arquitectura Medallion.**

## Versión de 1 minuto

El problema era representar cómo una empresa de seguros puede transformar archivos de clientes, pólizas, siniestros y pagos en información confiable para análisis, sin mezclar datos crudos con resultados de negocio.

Mi objetivo fue construir un pipeline end-to-end, reproducible y fácil de auditar. Implementé cuatro capas: Landing recibe los CSV; Bronze los convierte a Parquet y agrega trazabilidad; Silver elimina duplicados y normaliza texto; y Gold crea cinco datamarts para clientes, pólizas, siniestros, primas y riesgo de pago.

Además, desarrollé un orquestador estilo Azure Data Factory que controla el orden, las dependencias, el estado, la duración y los errores de cada actividad. El resultado fue un pipeline local que procesó 1.000 registros, terminó en estado `PASSED`, aprobó 8 de 8 controles de calidad y generó cinco datamarts.

Lo importante es que el proyecto demuestra arquitectura, orquestación, transformación y calidad. Está implementado localmente con Python, pandas y Parquet; ADF, ADLS y Databricks son las equivalencias para llevarlo a Azure real.

## Versión de 3 minutos

**Valor y problema.** Construí este proyecto para demostrar que un pipeline de datos no consiste solamente en copiar CSV. En seguros, datos de clientes, pólizas, siniestros y pagos deben ser trazables, consistentes y estar preparados antes de llegar a un dashboard. Si se mezclan datos crudos y métricas finales, un error de origen puede terminar afectando decisiones de negocio.

**Objetivo.** Diseñé un pipeline batch end-to-end inspirado en Azure, pero ejecutado localmente para evitar credenciales y costos cloud. Quería separar responsabilidades, controlar la ejecución y producir salidas verificables.

**Acciones e implementación.** Primero, `generate_source_data.py` crea 1.000 registros sintéticos en cuatro CSV. Luego `landing_to_bronze.py` los convierte a Parquet y agrega `ingestion_timestamp`, `source_file` y `pipeline_run_id`. `bronze_to_silver.py` elimina duplicados y normaliza campos de texto. Después, `silver_to_gold.py` cruza y agrega la información para construir cinco datamarts: clientes, pólizas, siniestros por producto, primas por segmento y riesgo de pago.

El flujo completo parte en `run_pipeline.py`. Este usa `ADFStyleOrchestrator` para ejecutar las actividades en orden, registrar dependencias, medir duración y capturar estados o errores. Finalmente, `quality_checks.py` ejecuta ocho validaciones sobre unicidad, integridad referencial y publicación Gold. Los controles se ejecutan después de Gold porque una de las reglas verifica que existan exactamente los cinco datamarts.

**Resultados.** La ejecución validada procesó 100 clientes, 200 pólizas, 300 siniestros y 400 pagos. Terminó `PASSED`, con 8/8 controles exitosos y cinco datamarts Gold. Además, dejó evidencia en `pipeline_summary.json` y en los archivos de calidad.

**Tecnologías y aprendizaje.** La implementación real usa Python, pandas, Parquet, CSV y JSON. Conceptualmente, el orquestador representa ADF; las carpetas Medallion representan ADLS Gen2; y los scripts de transformación representan notebooks Databricks. Aprendí a diferenciar orquestación de transformación y a diseñar un pipeline por capas con trazabilidad y resultados orientados al negocio. Para producción agregaría Delta Lake, PySpark, cargas incrementales, reintentos, Key Vault, monitoreo y CI/CD.

## Cinco preguntas probables

| Pregunta | Respuesta amigable y concreta |
|---|---|
| ¿Qué valor entrega el proyecto? | Convierte cuatro fuentes de seguros en cinco datamarts listos para análisis, con trazabilidad y controles que reducen el riesgo de publicar datos inconsistentes. |
| ¿Qué significa orquestar y qué hace ADF? | Orquestar es coordinar qué actividad se ejecuta, en qué orden y con qué estado. En el proyecto lo hace `ADFStyleOrchestrator`; en Azure lo haría Data Factory. ADF coordina, mientras Databricks transformaría los datos. |
| ¿Por qué separaste Landing, Bronze, Silver y Gold? | Landing recibe los archivos; Bronze agrega formato y trazabilidad; Silver limpia; y Gold publica modelos de consumo. Así cada capa tiene una responsabilidad clara. |
| ¿Cómo aseguraste la calidad? | Implementé ocho controles de unicidad, integridad referencial y existencia de los cinco datamarts. Si una actividad falla, el orquestador registra el error y el pipeline termina como fallido. |
| ¿Qué es real y qué llevarías a Azure? | Lo implementado es Python, pandas, Parquet y ejecución local. En Azure usaría ADF, ADLS Gen2 y Databricks; para producción agregaría Delta Lake, PySpark, Key Vault, monitoreo, reintentos y CI/CD. |

## Cierre

Este proyecto demuestra el criterio que quiero aplicar como Data Engineer Azure: transformar necesidades de negocio en pipelines reproducibles, trazables y confiables, siendo preciso sobre lo que ya implementé y sobre cómo lo evolucionaría a producción.
