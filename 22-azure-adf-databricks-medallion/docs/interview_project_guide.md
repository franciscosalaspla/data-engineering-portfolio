# Cómo presentar el Proyecto 22 en una entrevista

## Hook

Construí un pipeline local estilo Azure Data Engineering que transforma datos de seguros en datamarts confiables, con arquitectura Medallion, orquestación ADF-style, trazabilidad y controles de calidad.

## Presentación de 1 minuto

El proyecto resuelve un problema típico de Data Engineering: no basta con mover archivos de clientes, pólizas, siniestros y pagos; esos datos deben organizarse por capas, tener trazabilidad y pasar controles antes de convertirse en información para análisis.

Mi objetivo fue construir un pipeline end-to-end, reproducible y fácil de explicar, implementando localmente patrones de Azure Data Engineering sin desplegar Azure real. Para eso separé el flujo en Landing, Bronze, Silver y Gold. Landing recibe los CSV, Bronze los convierte a Parquet y agrega metadata técnica, Silver elimina duplicados y normaliza texto, y Gold genera cinco datamarts orientados al consumo.

La ejecución se coordina con un orquestador ADF-style que registra dependencias, estado, duración y errores. El pipeline se ejecutó correctamente, procesó 1.000 registros, aprobó 8 de 8 controles de calidad y generó 5 datamarts en Gold.

La implementación real usa Python, pandas, Parquet, CSV y JSON. El aprendizaje principal fue separar orquestación, transformación, calidad y consumo analítico, manteniendo una base clara para evolucionar el diseño hacia Azure Data Factory, ADLS Gen2 y Databricks en un escenario productivo.

## 3 preguntas de entrevista con respuestas

| Pregunta | Respuesta |
|---|---|
| ¿Qué problema resuelve este proyecto? | Resuelve cómo transformar datos operacionales de seguros en datasets confiables para análisis, separando datos crudos, datos trazables, datos limpios y datamarts finales. Está implementado localmente, pero representa un patrón real de Data Engineering que podría llevarse a Azure. |
| ¿Qué significa orquestar un pipeline y cómo se representa aquí? | Orquestar significa coordinar qué actividad se ejecuta, en qué orden, con qué dependencias y con qué estado final. Aquí lo representa un orquestador ADF-style en Python que registra duración, errores y estado; en Azure real ese rol lo cumpliría Azure Data Factory. |
| ¿Qué cambiarías para llevar esta solución a Azure real? | Mantendría la arquitectura Medallion, pero reemplazaría carpetas locales por ADLS Gen2, scripts pandas por jobs o notebooks en Databricks, y el orquestador local por Azure Data Factory. También agregaría Key Vault, monitoreo, reintentos, cargas incrementales, CI/CD y control de costos. |
