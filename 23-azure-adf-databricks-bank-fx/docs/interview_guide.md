# Anexo — Cómo contar este proyecto en una entrevista

## Hook — 10 segundos

> “Construí una plataforma bancaria multimoneda end-to-end en Azure, orquestada con Data Factory y procesada en Databricks bajo arquitectura Medallion, con calidad, idempotencia y serving analítico.”

## Situación y tarea

| Situación | Tarea |
|---|---|
| Había datos bancarios en CSV, JSON y una API externa, con estructuras distintas y riesgo de duplicados o relaciones inválidas. | Diseñar un pipeline cloud confiable que integrara las fuentes, controlara la calidad y publicara un modelo listo para Power BI. |

## Acciones

- Diseñé capas Landing, Bronze, Silver y Gold en ADLS y Databricks.
- Implementé transformaciones con PySpark y Delta Lake, incluyendo cuarentena y quality gates.
- Orquesté tres notebooks secuenciales con Azure Data Factory.
- Construí un modelo estrella multimoneda y lo publiqué en Azure SQL.
- Aseguré la reejecución con claves, checksums, `MERGE` y comportamiento `NO_OP`.
- Protegí secretos con Key Vault y Secret Scope, y configuré controles de costos.

## Resultados

- Pipeline ADF completo en **10 min 17 s**, con **3/3 notebooks correctos**.
- **7 tablas y 953 filas** publicadas en Azure SQL.
- **PK/FK 7/7**, cero huérfanos y reconciliación aprobada.
- Segunda ejecución **`NO_OP`**, sin duplicar ni reescribir datos.
- Modelo Power BI con **7 tablas, 6 relaciones activas** y KPIs validados.
- Costo observado de **USD 0,04**.

## Lecciones aprendidas

- ADF funciona mejor como capa de orquestación y Databricks como motor de transformación.
- La arquitectura Medallion permite aislar errores y aplicar calidad antes de publicar datos.
- Idempotencia, observabilidad y control de costos deben diseñarse desde el inicio.

## Preguntas que pueden hacerte

### ¿Por qué usaste ADF y Databricks en conjunto?

ADF administra dependencias, ejecución y monitorización; Databricks concentra las transformaciones con PySpark, Delta Lake y controles de calidad. Así cada servicio cumple una responsabilidad clara.

### ¿Cómo garantizaste la idempotencia?

Usé claves de negocio, checksums de contenido y `MERGE` en Delta. Si un lote no cambia, se omite la escritura. La segunda publicación en Azure SQL terminó `NO_OP`, con 953 filas antes y después.

### ¿Por qué elegiste arquitectura Medallion?

Porque separa fidelidad del origen, limpieza y reglas de negocio. Bronze conserva, Silver valida y Gold publica; esto facilita auditoría, reprocesamiento y prevención de errores aguas abajo.

## Cierre memorable

> “El valor del proyecto no fue mover archivos: fue convertir tres fuentes distintas en una cadena de datos confiable, auditable y lista para decisiones.”
