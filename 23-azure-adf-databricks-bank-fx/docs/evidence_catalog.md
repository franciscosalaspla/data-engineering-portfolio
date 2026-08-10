# Catálogo y alcance de evidencias

## Política

Las capturas originales y sus copias sanitizadas se conservan fuera del repositorio público. No se generaron ni reconstruyeron imágenes con IA.

Antes de conservar una evidencia se eliminaron o recortaron:

- IDs de suscripción, tenant, recurso, ejecución, cliente u objeto;
- correos, usuarios, contraseñas y tokens;
- endpoints completos.

Las copias se revisaron visualmente y mediante OCR.

## Cobertura de principio a fin

| # | Etapa | Evidencia disponible | Conclusión verificable |
|---:|---|---|---|
| 1 | Landing → Bronze | Código, fixtures, pruebas y confirmación de ejecución | Datos ingeridos con contrato y trazabilidad |
| 2 | Bronze → Silver | Código, pruebas y confirmación de quality gates | Limpieza, relaciones y cuarentena validadas |
| 3 | Silver → Gold | Código, pruebas y confirmación de quality gates | Modelo estrella, FX e idempotencia validados |
| 4 | ADF | E04-01 y E04-02 | Pipeline correcto; 3/3 actividades |
| 5 | Azure SQL | E05-01 a E05-04 y validaciones registradas | 7 tablas, 953 filas, integridad y `NO_OP` |
| 6 | Power BI | E06-01 a E06-03 | Modelo, KPI y publicación confirmados |
| 7 | Operación y costos | E07-01 a E07-03 y E05-04 | Recursos cerrados y controles de costo aplicados |

## Inventario visual

| ID | Archivo recomendado | Qué demuestra | Tratamiento |
|---|---|---|---|
| E04-01 | `h04-adf-pipeline-success.png` | Pipeline correcto en 10 min 17 s | Run IDs y filas no necesarias recortados |
| E04-02 | `h04-adf-three-notebooks-success.png` | Tres notebooks correctos y sus duraciones | Run ID ocultado y activity IDs recortados |
| E05-01 | `h05-gold-preflight-953-rows.png` | Preflight: 7 tablas, 953 filas y `PASSED` | Original seguro |
| E05-02 | `h05-azure-sql-publication-953-rows.png` | Publicación completa y `LOADED` | Original seguro |
| E05-03 | `h05-azure-sql-seven-serving-tables.png` | Siete tablas en el esquema `serving` | Original seguro |
| E05-04 | `h07-azure-sql-paused-serverless.png` | SQL `Paused`, serverless y exceso deshabilitado | ID, endpoint y panel inferior retirados |
| E06-01 | `h06-power-bi-star-schema.png` | Siete tablas y seis relaciones activas | Original seguro |
| E06-02 | `h06-power-bi-kpi-cards.png` | KPI: 8 transacciones, 4 clientes y 6 cuentas | Original seguro |
| E06-03 | `h06-power-bi-service-published-dashboard.png` | Dashboard publicado y canales 3/2/2/1 | Original seguro |
| E07-01 | `h07-azure-cost-analysis.png` | USD 0,04 observados y USD 0,29 proyectados | Original seguro |
| E07-02 | `h07-budget-alert-50-percent.png` | Alerta al 50 %, equivalente a USD 1 | Correos y destinatarios recortados |
| E07-03 | `h07-databricks-compute-terminated.png` | Compute sin memoria, núcleos ni DBU activos | Usuario y columna `Creador` recortados |

## Validaciones sin captura recuperada

| Etapa | Validación | Resultado | Tratamiento documental |
|---|---|---|---|
| 1–3 | Catálogo Bronze, Silver y Gold | Capas creadas y validadas | Código, pruebas y confirmación de ejecución |
| 5 | PK/FK | 7/7 `PASSED` | Validación cloud manual |
| 5 | Huérfanos | 0 | Validación cloud manual |
| 5 | Reconciliación | `PASSED` | Validación cloud manual |
| 5 | Idempotencia | `NO_OP`; 953 → 953; 0 escrituras | Validación cloud manual |
| 7 | Presupuesto | USD 2 mensual | Confirmación registrada; E07-02 cubre solo la alerta |

No se asigna una imagen a estas validaciones porque produciría una trazabilidad falsa.

## Límites de interpretación

- E04-01 muestra una ejecución fallida anterior, pero no demuestra su causa.
- E05-04 representa el estado de Azure SQL al cierre, no un estado permanente.
- E06 confirma modelo y KPI, pero no el modo final Import/DirectQuery ni las fórmulas DAX.
- E07-01 fue tomada antes de crear el presupuesto; E07-02 demuestra el umbral de alerta.
- El PBIX, la exportación del pipeline ADF y las capturas de PK/FK, reconciliación y `NO_OP` no están disponibles.

La falta de esos binarios no se completa mediante inferencias ni obliga a reejecutar Azure.
