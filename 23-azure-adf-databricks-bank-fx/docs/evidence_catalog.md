# Catálogo de validaciones y evidencias

Este catálogo indica **cómo se respalda cada hito**. Los Hitos 1–3 tienen pruebas versionadas; los Hitos 4–7 se validaron manualmente en Azure. Por decisión de publicación, las imágenes se conservan fuera del repositorio público.

## Política de seguridad

Antes de considerar una evidencia publicable se excluyen:

- subscription ID, tenant ID, run IDs y resource IDs;
- client/object IDs, correos y usuarios;
- contraseñas, tokens y endpoints completos.

Las copias sanitizadas fueron revisadas visualmente y mediante OCR. No se generaron ni reconstruyeron imágenes con IA.

## Hito 1 — Landing → Bronze

### 1.1 Evidencia versionada

| Evidencia | Qué demuestra | Resultado |
|---|---|---|
| `manifest/expected_results.json` | Contratos, conteos, checksums y replay esperado | Fixture determinístico |
| `scripts/validate_fixtures.py` | Integridad de los datos de prueba | 42/42 controles aprobados |
| `tests/test_ingestion_pipeline.py` | Landing, Bronze, metadata, cuarentena e idempotencia | Pruebas automatizadas aprobadas |

## Hito 2 — Bronze → Silver

### 2.1 Evidencia versionada

| Evidencia | Qué demuestra | Resultado |
|---|---|---|
| `config/silver_pipeline.json` | Configuración y claves de negocio por entidad | 4 tablas Silver definidas |
| `tests/test_silver_pipeline.py` | Schemas, calidad, cuarentena, `MERGE` y auditoría | Pruebas automatizadas aprobadas |
| Salida esperada del fixture | 5 clientes, 7 cuentas, 2 tasas y 8 transacciones | 22 registros válidos |

## Hito 3 — Silver → Gold

### 3.1 Evidencia versionada

| Evidencia | Qué demuestra | Resultado |
|---|---|---|
| `config/gold_pipeline.json` | Contrato del modelo dimensional | 6 dimensiones y 1 hecho |
| `tests/test_gold_transformations.py` | Conversión FX, decimales, claves y cuarentena | Pruebas automatizadas aprobadas |
| `tests/test_gold_pipeline.py` | Grano, FK, reconciliación e idempotencia | Quality gates aprobados |

La suite local completa contiene 37 pruebas. Estas validaciones no sustituyen las comprobaciones manuales de los servicios Azure.

## Hito 4 — Azure Data Factory

### 4.1 Pipeline

| ID | Nombre recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E04-01 | `h04-adf-pipeline-success.png` | Pipeline correcto en 10 min 17 s y una ejecución anterior fallida | Recorte de run IDs y filas no necesarias |

### 4.2 Actividades

| ID | Nombre recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E04-02 | `h04-adf-three-notebooks-success.png` | Tres notebooks correctos; 2:37, 3:06 y 4:22 | Run ID ocultado y activity IDs recortados |

Las capturas fueron recuperadas el 9 de agosto de 2026 y corresponden a una ejecución del 5 de agosto de 2026. Confirman el pipeline `pl_project23_medallion_orchestration` y sus tres actividades, pero no la causa del intento fallido anterior.

## Hito 5 — Azure SQL

### 5.1 Preflight y publicación

| ID | Nombre recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E05-01 | `h05-gold-preflight-953-rows.png` | Preflight: 7 tablas, 953 filas y `PASSED` | Original seguro |
| E05-02 | `h05-azure-sql-publication-953-rows.png` | Carga 919/5/7/7/4/3/8; total 953 y `LOADED` | Original seguro |

### 5.2 Serving y cierre

| ID | Nombre recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E05-03 | `h05-azure-sql-seven-serving-tables.png` | Siete tablas en el esquema `serving` | Original seguro; nombre de base truncado por la interfaz |
| E05-04 | `h07-azure-sql-paused-serverless.png` | SQL `Paused`, Central US, serverless gratuito y exceso deshabilitado | Subscription ID y endpoint ocultados; panel recortado |

E05-01 demuestra que el preflight no realizó conexiones ni escrituras. E05-03 demuestra la existencia de las tablas, pero no sus conteos. E05-04 es una fotografía del cierre, no una garantía de que la base permanezca pausada.

## Hito 6 — Power BI

### 6.1 Modelo

| ID | Nombre recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E06-01 | `h06-power-bi-star-schema.png` | Siete tablas y seis relaciones activas | Original seguro |

### 6.2 Dashboard y publicación

| ID | Nombre recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E06-02 | `h06-power-bi-kpi-cards.png` | KPI: 4 clientes, 8 transacciones y 6 cuentas | Original seguro |
| E06-03 | `h06-power-bi-service-published-dashboard.png` | KPI 8/4/6, canales 3/2/2/1 y publicación correcta | Original seguro; no muestra la cuenta |

Estas evidencias no permiten verificar el modo final Import/DirectQuery ni reconstruir las fórmulas DAX.

## Hito 7 — Monitorización y costos

### 7.1 Costos y alerta

| ID | Nombre recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E07-01 | `h07-azure-cost-analysis.png` | Costo USD 0,04 y proyección USD 0,29 | Original seguro |
| E07-02 | `h07-budget-alert-50-percent.png` | Alerta al 50 %, equivalente a USD 1 | Destinatarios y correos recortados |

### 7.2 Recursos detenidos

| ID | Nombre recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E07-03 | `h07-databricks-compute-terminated.png` | Compute sin memoria, núcleos ni DBU activos | Usuario y columna `Creador` recortados |
| E05-04 | `h07-azure-sql-paused-serverless.png` | Azure SQL pausado | Sanitización descrita en Hito 5 |

E07-01 fue capturada antes de crear el presupuesto y muestra `PRESUPUESTO: NINGUNO`. E07-02 respalda el umbral; el presupuesto mensual de USD 2 está confirmado por el historial, pero no por una captura final recuperada.

## Validaciones cloud sin captura recuperada

| Hito | Validación | Resultado confirmado |
|---:|---|---|
| 5 | PK/FK | 7/7 `PASSED` |
| 5 | Registros huérfanos | 0 |
| 5 | Reconciliación | `PASSED` |
| 5 | Idempotencia | `NO_OP`; 953 → 953; 0 escrituras |
| 7 | Presupuesto mensual | USD 2 |

Estas validaciones se registran como confirmaciones cloud manuales. No se les asigna una imagen inexistente.

## Artefactos no disponibles

- captura del catálogo completo Bronze, Silver y Gold;
- capturas específicas de PK/FK, huérfanos, reconciliación y `NO_OP`;
- captura final del presupuesto ya creado;
- PBIX y modelo semántico;
- exportación del pipeline ADF cloud.

La ausencia de estos binarios no requiere volver a ejecutar Azure y no se completa mediante reconstrucciones.
