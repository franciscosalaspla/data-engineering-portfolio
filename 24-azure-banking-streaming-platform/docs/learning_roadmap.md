# Ruta de aprendizaje aplicada al Proyecto 24

## Principio de progresión

El aprendizaje para Data Engineering se organiza en tres capas: primero fundamentos, después
capacidad de producción y finalmente especialización. La intención no es acumular herramientas,
sino demostrar que un pipeline puede diseñarse, probarse, desplegarse y operarse con confianza.

## 1. Fundamentos imprescindibles

SQL, Python, ETL/ELT, modelado, Data Warehouse, Linux, Git, APIs y procesamiento batch forman la
base para mover, transformar, validar y disponibilizar datos. El Proyecto 23 consolidó este bloque
con un pipeline bancario batch end-to-end.

## 2. Estándar moderno de producción

Spark, Databricks, cloud, Lakehouse, Parquet, calidad de datos, CI/CD, contenedores,
infraestructura como código, monitoreo y orquestación convierten un pipeline funcional en una
plataforma operable:

> Código → pruebas → CI/CD → calidad → observabilidad → despliegue → operación

Para un perfil Azure + Databricks, Delta Lake se considera parte de este estándar moderno junto con
PySpark y la arquitectura Lakehouse, no una capacidad opcional o lejana.

## 3. Especialización diferenciadora

Streaming, CDC, arquitecturas event-driven, Kafka, Flink, Kubernetes, MLOps, Data Mesh y Platform
Engineering cobran importancia cuando el caso requiere baja latencia, mayor escala o una
plataforma compartida. No es necesario dominar todas estas áreas a la vez.

## Alineación con el portafolio

| Área | Evidencia o prioridad |
|---|---|
| SQL, Python, Git y APIs | Consolidados en proyectos anteriores |
| ETL/ELT, modelado y batch | Consolidados en el Proyecto 23 |
| Azure, ADF, PySpark y Databricks | Stack principal en consolidación |
| Delta Lake, Lakehouse y Data Quality | Estándar moderno del stack elegido |
| CI/CD | Implementado desde el Hito 1 del Proyecto 24 |
| Bicep e infraestructura como código | Introducidos en el Hito 2 |
| Key Vault y despliegue seguro | Planificados para el Hito 3 |
| Event Hubs y streaming | Planificados para los Hitos 4 y 5 |
| Monitoring | Planificado para el Hito 7 |
| CDC y Terraform | Evolución posterior al MVP |
| Kafka, Kubernetes y Flink | Prioridad condicionada por el puesto o la escala |
| MLOps y Data Mesh | Fuera del foco inmediato de Data Engineering Azure |

## Orden de prioridad

**Ahora:** SQL → Python → Azure → ADF → Databricks/PySpark → Delta Lake → Lakehouse → Data
Quality → CI/CD → Bicep.

**Después:** monitoreo → Key Vault → Terraform → Event Hubs → Structured Streaming → CDC.

**Cuando el contexto lo exija:** Kafka → Kubernetes → Flink → MLOps → Data Mesh.

## Posicionamiento buscado

El Proyecto 24 conecta el estándar moderno de producción con una especialización concreta:

> Azure Data Engineering + Databricks/Lakehouse + calidad y confiabilidad + streaming

La meta del portafolio es demostrar fundamentos sólidos, profundidad en un stack cloud, capacidad
de llevar pipelines a producción y una especialización coherente, no completar una checklist de
tecnologías.
