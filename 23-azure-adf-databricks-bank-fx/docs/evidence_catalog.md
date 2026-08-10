# Catálogo de evidencias cloud

## Política

Este catálogo registra capturas originales seguras o copias sanitizadas mecánicamente. Por decisión de publicación, ningún archivo de imagen se incluye en el repositorio público. No se generaron ni reconstruyeron imágenes con IA.

Datos excluidos:

- subscription ID y tenant ID;
- run IDs y resource IDs;
- client/object IDs;
- correos y usuarios;
- contraseñas y tokens;
- endpoints completos.

Las copias sanitizadas se revisaron visualmente y mediante OCR para detectar UUID, correos y endpoints. Se conservan fuera del repositorio junto con los originales.

## Inventario

| ID | Hito | Nombre recomendado | Qué demuestra | Tratamiento aplicado |
|---|---:|---|---|---|
| E04-01 | 4 | `h04-adf-pipeline-success.png` | Pipeline correcto en 10 min 17 s y una ejecución anterior fallida | Recorte de columna con run IDs y de filas no necesarias |
| E04-02 | 4 | `h04-adf-three-notebooks-success.png` | Tres notebooks correctos; 2:37, 3:06 y 4:22 | Run ID ocultado y columna de activity IDs recortada |
| E05-01 | 5 | `h05-gold-preflight-953-rows.png` | Preflight Gold: siete tablas, 953 filas y `PASSED` | Original seguro, sin modificación de píxeles |
| E05-02 | 5 | `h05-azure-sql-publication-953-rows.png` | Siete tablas publicadas, conteos 919/5/7/7/4/3/8, total 953 y `LOADED` | Original seguro, sin modificación de píxeles |
| E05-03 | 5 | `h05-azure-sql-seven-serving-tables.png` | Existencia de siete tablas en el esquema `serving` | Original seguro; nombre de base truncado por la interfaz |
| E05-04 | 5/7 | `h07-azure-sql-paused-serverless.png` | Azure SQL `Paused`, Central US, plan gratuito serverless y exceso deshabilitado | Subscription ID y endpoint ocultados; panel inferior recortado |
| E06-01 | 6 | `h06-power-bi-star-schema.png` | Modelo estrella con siete tablas y seis relaciones activas | Original seguro, sin modificación de píxeles |
| E06-02 | 6 | `h06-power-bi-kpi-cards.png` | KPI: 4 clientes, 8 transacciones y 6 cuentas | Original seguro, sin modificación de píxeles |
| E06-03 | 6 | `h06-power-bi-service-published-dashboard.png` | Dashboard 8/4/6, canales 3/2/2/1 y operación de publicación correcta | Original seguro; no muestra cuenta de usuario |
| E07-01 | 7 | `h07-azure-cost-analysis.png` | Costo USD 0,04, proyección USD 0,29 y desglose por servicio | Original seguro, sin modificación de píxeles |
| E07-02 | 7 | `h07-budget-alert-50-percent.png` | Alerta al 50 %, equivalente a USD 1 | Sección de destinatarios y correos recortada |
| E07-03 | 7 | `h07-databricks-compute-terminated.png` | Compute sin memoria, núcleos ni DBU activos | Columna `Creador` y usuario recortados |

## Lectura correcta de las evidencias

### E04 — ADF

E04-01 y E04-02 corresponden a capturas recuperadas el 9 de agosto de 2026 sobre una ejecución del 5 de agosto de 2026. Demuestran el resultado y las duraciones, pero no la causa del intento fallido. Los nombres del pipeline y las actividades sí son visibles:

- `pl_project23_medallion_orchestration`;
- `nb_01_landing_to_bronze`;
- `nb_02_bronze_to_silver`;
- `nb_03_silver_to_gold`.

### E05 — Azure SQL

E05-01 demuestra que el preflight no realizó conexiones ni escrituras. E05-02 demuestra la carga real. E05-03 demuestra las siete tablas, pero no los conteos de filas. E05-04 es una fotografía del estado operativo final, no una prueba de que la base permanezca pausada indefinidamente.

### E06 — Power BI

E06-01 confirma la topología del modelo. E06-02 confirma los KPI. E06-03 confirma la publicación y la distribución por canal. Ninguna captura permite verificar el modo final Import/DirectQuery ni reconstruir las fórmulas DAX.

### E07 — Costos

E07-01 muestra `PRESUPUESTO: NINGUNO` porque fue capturada antes de la creación posterior. E07-02 demuestra la configuración del umbral de alerta. La creación del presupuesto mensual de USD 2 está confirmada por el historial, pero no existe una captura final recuperada que muestre el presupuesto ya asociado.

## Validaciones confirmadas sin captura recuperada

| Hito | Validación | Resultado confirmado | Cómo se documenta |
|---:|---|---|---|
| 1–3 | Catálogo Bronze, Silver y Gold | Capas creadas y validadas | Confirmación textual; sin archivo inventado |
| 5 | PK/FK | 7/7 `PASSED` | Validación cloud manual |
| 5 | Huérfanos | 0 | Validación cloud manual |
| 5 | Reconciliación | `PASSED` | Validación cloud manual |
| 5 | Idempotencia | `NO_OP`; 953 → 953; 0 escrituras | Validación cloud manual |
| 7 | Presupuesto creado | USD 2 mensual | Confirmación textual; E07-02 solo cubre el umbral |

No se asigna una imagen a estas validaciones porque eso produciría una trazabilidad falsa.

## Artefactos no disponibles

- Captura del catálogo completo con Bronze, Silver y Gold.
- Capturas específicas de PK/FK, huérfanos, reconciliación y `NO_OP`.
- Captura final del presupuesto de USD 2 ya creado.
- PBIX original y exportación del modelo semántico.
- Exportación del pipeline ADF cloud.

La ausencia de esos binarios no requiere volver a ejecutar Azure. El estado se registra con el nivel de evidencia realmente disponible.
