# Implementación cloud — Hitos 4 a 7

## Propósito

Este documento registra qué se implementó y validó realmente en Azure después de cerrar la base local del Proyecto 23. Las capturas originales respaldan la evidencia operativa, pero se conservan fuera del repositorio público; no sustituyen la suite automatizada local ni se presentan como exportaciones reproducibles de los servicios.

## Inventario

| Categoría | Nombre confirmado | Tipo | Propósito | Estado observado al cierre |
|---|---|---|---|---|
| Grupo | `rg-project23-dev` | Resource Group | Agrupar recursos y costos | Activo |
| Storage | `stproject23dev2026` | ADLS Gen2 | Landing, Bronze, Silver y Gold | Activo |
| Orquestación | `adf-project23-dev-2026` | Data Factory V2 | Ejecutar notebooks secuenciales | Publicado |
| Pipeline | `pl_project23_medallion_orchestration` | ADF pipeline | Landing → Bronze → Silver → Gold | Ejecución correcta |
| Procesamiento | `dbw-project23-dev-2026` | Databricks Workspace | PySpark y Delta | Activo |
| Compute | `compute-project23-dev-2026` | Single-node compute | Ejecutar notebooks | Detenido |
| Catálogo | `dbw_project23_dev_2026` | Unity Catalog | Organizar tablas por capa | Utilizado |
| Secretos | `kv-project23-dev-2026` | Key Vault | Credenciales SQL | Utilizado |
| Secret Scope | `project23-serving-dev` | Databricks Secret Scope | Acceso a dos secretos | Validado |
| SQL Server | `sqlsrv-project23-serving-dev-2026` | Logical SQL Server | Host de serving | Activo |
| Base | `sqldb-project23-serving-dev-2026` | Azure SQL Database | Modelo estrella serving | `Paused` |
| Consumo | `My Workspace` | Power BI workspace | Publicar informe | Publicado |

No se incluyen IDs, endpoints, cuentas ni valores de secretos.

## Hito 4 — Azure Data Factory

### Objetivo

Orquestar las tres capas de Azure Databricks desde ADF y comprobar una ejecución completa desde Landing hasta Gold.

### Configuración confirmada

- Data Factory: `adf-project23-dev-2026`.
- Workspace: `dbw-project23-dev-2026`.
- Integración mediante Linked Service de Azure Databricks con prueba de conexión correcta.
- Pipeline: `pl_project23_medallion_orchestration`.
- Publicación: validada y publicada.
- Patrón: ejecución secuencial con dependencia de éxito.

Orden de actividades:

| Orden | Actividad | Resultado | Duración |
|---:|---|---|---:|
| 1 | `nb_01_landing_to_bronze` | Correcto | 2 min 37 s |
| 2 | `nb_02_bronze_to_silver` | Correcto | 3 min 6 s |
| 3 | `nb_03_silver_to_gold` | Correcto | 4 min 22 s |
|  | **Pipeline completo** | **Correcto** | **10 min 17 s** |

La diferencia entre la suma de actividades y la duración total corresponde al tiempo de orquestación y transición.

### Incidente

ADF Monitor conserva al menos una ejecución fallida anterior a la ejecución correcta. La causa y la corrección exactas no quedaron respaldadas por un artefacto recuperable; por ello no se atribuye una causa por inferencia.

### Evidencia

- E04-01 — pipeline correcto y ejecución anterior fallida.
- E04-02 — tres notebooks y duraciones.

Los archivos bajo `adf/` pertenecen a la ingesta local inicial y conservan su condición `DESIGN_ONLY`/`NOT_DEPLOYED`. El pipeline ejecutado no fue exportado al repositorio.

## Hito 5 — Azure SQL

### Objetivo

Publicar el modelo Gold como capa de serving relacional y validar conteos, integridad, reconciliación e idempotencia.

### Seguridad y conexión

- SQL Server: `sqlsrv-project23-serving-dev-2026`.
- Base: `sqldb-project23-serving-dev-2026`.
- Región: Central US.
- Plan: uso general serverless con oferta gratuita.
- Facturación sobre el límite gratuito: deshabilitada.
- Key Vault: `kv-project23-dev-2026`.
- Secret Scope: `project23-serving-dev`.
- Secretos: dos, destinados a usuario y contraseña SQL.
- Notebook cloud: `04_gold_to_azure_sql`.
- Conexión: JDBC con secretos fuera del código.

El notebook cloud no fue exportado y no se reconstruye en este repositorio.

### Publicación

| Tabla `serving` | Filas |
|---|---:|
| `dim_date` | 919 |
| `dim_customer` | 5 |
| `dim_account` | 7 |
| `dim_merchant` | 7 |
| `dim_channel` | 4 |
| `dim_currency` | 3 |
| `fact_transaction` | 8 |
| **Total** | **953** |

### Validaciones

| Control | Resultado |
|---|---|
| Preflight Gold | 7 tablas y 953 filas esperadas; `PASSED` |
| Publicación | 7 tablas y 953 filas; `LOADED` |
| Claves primarias y foráneas | 7/7 aprobadas |
| Registros huérfanos | 0 |
| Reconciliación Gold → SQL | `PASSED` |
| Segunda ejecución | `NO_OP` |
| Filas antes/después | 953 → 953 |
| Escrituras segunda ejecución | 0 |
| Quality Gate final | `PASSED` |

Las validaciones de integridad, reconciliación y `NO_OP` están confirmadas en el historial, pero sus capturas específicas no fueron recuperadas. Se registran como validaciones cloud manuales, no como tests automatizados versionados.

### Incidentes resueltos

| Problema | Acción confirmada | Resultado |
|---|---|---|
| Uso de `ORDER BY` en la definición SQL utilizada | Corrección de consultas/vistas | Flujo continuó |
| Disponibilidad temporal para JDBC | Reintentos de disponibilidad | Conexión validada |
| Credenciales SQL no operativas | Restablecimiento de credenciales | Publicación correcta |

No se conservan mensajes de error completos y no se agregan causas adicionales.

### Evidencia

- E05-01 — preflight Gold.
- E05-02 — publicación de 953 filas.
- E05-03 — siete tablas serving.
- E05-04 — SQL pausado y serverless.

## Hito 6 — Power BI

### Objetivo

Consumir Azure SQL, construir un modelo estrella mínimo viable y publicar una página ejecutiva. El alcance se mantuvo acotado para conservar el foco en Data Engineering.

### Modelo

- Siete tablas de `serving`.
- Seis relaciones activas, desde cada dimensión hacia `fact_transaction`.
- Cardinalidad esperada uno a muchos.
- Una tabla de hechos duplicada durante la preparación fue eliminada antes de recargar el modelo.
- Una relación automática incorrecta fue corregida manualmente; sus columnas exactas no quedaron registradas.

DirectQuery fue probado durante la conexión. El modo final del modelo publicado no está demostrado por el PBIX ni por una exportación del modelo semántico, por lo que no se afirma como Import o DirectQuery.

### Página ejecutiva

| Indicador | Resultado |
|---|---:|
| Total de transacciones | 8 |
| Clientes únicos con transacciones | 4 |
| Cuentas únicas con transacciones | 6 |

| Canal | Transacciones |
|---|---:|
| Card | 3 |
| Mobile | 2 |
| Online | 2 |
| ATM | 1 |

Los cuatro clientes son clientes presentes en la tabla de hechos; `dim_customer` contiene cinco registros.

Se crearon tres medidas, pero sus fórmulas DAX exactas no fueron recuperadas. El informe visible en Power BI Service se identifica como `project23-banking-report.pbix`; el PBIX original y la exportación del modelo semántico no están versionados.

### Evidencia

- E06-01 — modelo estrella.
- E06-02 — KPI 8/4/6.
- E06-03 — publicación completada.

## Hito 7 — Monitorización y costos

### Objetivo

Comprobar el resultado operativo, detener recursos de consumo variable y configurar un límite básico de gasto.

| Control | Resultado observado |
|---|---|
| ADF Monitor | Pipeline correcto; 3/3 actividades correctas |
| Databricks | `compute-project23-dev-2026` detenido |
| Recursos compute | Sin memoria, núcleos ni DBU activos |
| Autoapagado | 10 minutos |
| Azure SQL | `Paused` |
| Exceso plan gratuito | Deshabilitado |
| Costo acumulado | USD 0,04 |
| Proyección | USD 0,29 |
| Presupuesto | USD 2 mensual |
| Alerta | 50 %, equivalente a USD 1 |

La captura de costos fue tomada antes de que el presupuesto apareciera asociado en esa vista; la creación posterior del presupuesto y la alerta está confirmada por el historial. La captura E07-02 demuestra la configuración del umbral, no la pantalla final del presupuesto creado.

### Evidencia

- E07-01 — costo y proyección.
- E07-02 — alerta al 50 %.
- E07-03 — compute detenido.
- E05-04 — Azure SQL pausado.

El detalle de cada ID y la política de conservación fuera del repositorio está en [evidence_catalog.md](evidence_catalog.md).

## Matriz de validación

| Tipo | Alcance | Resultado | Evidencia |
|---|---|---|---|
| Automatizada local | Fixtures | 42/42 | Salida reproducible de `validate_fixtures.py` |
| Automatizada local | Ingesta, Silver y Gold | 37/37 | Suite `unittest` |
| Databricks | Quality gates de capas | `PASSED` | Confirmación de ejecución |
| ADF manual | Pipeline y actividades | `PASSED` | E04-01, E04-02 |
| Azure SQL manual | Conteos y publicación | `PASSED` | E05-01 a E05-03 |
| Azure SQL manual | Integridad e idempotencia | `PASSED` | Confirmación textual; sin captura recuperada |
| Power BI manual | Modelo, KPI y publicación | `PASSED` | E06-01 a E06-03 |
| Operativa | Recursos y costos | `PASSED` | E07-01 a E07-03, E05-04 |

## Artefactos no exportados

- Pipeline ADF cloud definitivo y sus Linked Services.
- Notebook `04_gold_to_azure_sql`.
- DDL final usado para materializar todas las tablas serving.
- PBIX original, fórmulas DAX y modelo semántico.
- Exportación del presupuesto.
- Capturas específicas de PK/FK, huérfanos, reconciliación y `NO_OP`.

Estas ausencias se documentan como límites. No se rellenan mediante código o capturas reconstruidas.
