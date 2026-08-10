# Implementación por hitos — 1 a 7

Este documento registra **qué se construyó, cómo se validó y qué resultado produjo cada hito**. La arquitectura y el runbook se mantienen separados para evitar repetir información.

## Mapa de implementación

| Hito | Tecnología principal | Entregable |
|---:|---|---|
| 1 | ADLS Gen2 + Databricks | Datos trazables en Bronze |
| 2 | PySpark + Delta Lake | Datos limpios en Silver |
| 3 | Databricks + Unity Catalog | Modelo estrella en Gold |
| 4 | Azure Data Factory | Pipeline Medallion orquestado |
| 5 | Key Vault + Azure SQL | Capa relacional de serving |
| 6 | Power BI | Modelo y dashboard publicados |
| 7 | Azure Monitor + Cost Management | Recursos cerrados y costos controlados |

## Hito 1 — Landing → Bronze

### 1.1 Construcción

- Ingesta de transacciones CSV, clientes y cuentas JSON, y tasas históricas del ECB.
- Conservación de archivos en ADLS Gen2 `landing`.
- Lectura con schemas explícitos, metadata técnica y persistencia Delta en `bronze`.
- Checksum y auditoría para mantener trazabilidad e idempotencia.

### 1.2 Validación y resultado

| Control | Resultado |
|---|---|
| Contratos y fixtures | 42/42 controles aprobados |
| Datos válidos | 5 clientes, 7 cuentas, 2 tasas FX y 8 transacciones |
| Registros inválidos | 3 transacciones enviadas a cuarentena |
| Replay | Omitido por checksum; sin duplicados |

## Hito 2 — Bronze → Silver

### 2.1 Construcción

- Limpieza y tipificación con PySpark.
- Normalización de IDs, fechas, dominios y decimales.
- Validación de relaciones cuenta → cliente y transacción → cuenta.
- Delta `MERGE` por clave de negocio y checksum.

### 2.2 Validación y resultado

| Tabla | Filas válidas |
|---|---:|
| `silver_customers` | 5 |
| `silver_accounts` | 7 |
| `silver_fx_rates` | 2 |
| `silver_transactions` | 8 |
| **Total** | **22** |

La segunda ejecución mantuvo los conteos y no generó duplicados.

## Hito 3 — Silver → Gold

### 3.1 Construcción

- Conversión de EUR, USD y GBP a EUR según fecha.
- Seis dimensiones Type 1 y una tabla de hechos.
- Claves sustitutas determinísticas y grano por `transaction_id`.
- Quality gates de claves, huérfanos, conteos, importes y reconciliación.

### 3.2 Validación y resultado

| Control | Resultado |
|---|---|
| Modelo Gold | 6 dimensiones y 1 tabla de hechos |
| Registros de hechos | 8 |
| Reconciliación | `PASSED` |
| Suite local completa | 37/37 pruebas aprobadas |

La implementación local conserva `fact_transactions`; el contrato de Azure SQL y Power BI usa `fact_transaction`.

## Hito 4 — Orquestación con Azure Data Factory

### 4.1 Construcción

`pl_project23_medallion_orchestration` ejecuta en orden:

1. `nb_01_landing_to_bronze`;
2. `nb_02_bronze_to_silver`;
3. `nb_03_silver_to_gold`.

Cada actividad comienza solo si la anterior termina correctamente. ADF controla la orquestación y Databricks concentra las transformaciones.

### 4.2 Validación y resultado

| Actividad | Estado | Duración |
|---|---|---:|
| Landing → Bronze | Correcto | 2 min 37 s |
| Bronze → Silver | Correcto | 3 min 6 s |
| Silver → Gold | Correcto | 4 min 22 s |
| **Pipeline completo** | **Correcto** | **10 min 17 s** |

El pipeline cloud fue validado y publicado, pero su exportación no está versionada. Los JSON bajo `adf/` corresponden al diseño inicial.

## Hito 5 — Serving en Azure SQL

### 5.1 Construcción y seguridad

- Publicación JDBC desde Gold al esquema `serving`.
- Credenciales almacenadas en Key Vault y Databricks Secret Scope.
- Azure SQL serverless con facturación sobre el límite gratuito deshabilitada.

### 5.2 Validación y resultado

| Tabla | Filas |
|---|---:|
| `dim_date` | 919 |
| `dim_customer` | 5 |
| `dim_account` | 7 |
| `dim_merchant` | 7 |
| `dim_channel` | 4 |
| `dim_currency` | 3 |
| `fact_transaction` | 8 |
| **Total** | **953** |

| Quality Gate | Resultado |
|---|---|
| PK/FK | 7/7 aprobadas |
| Registros huérfanos | 0 |
| Reconciliación Gold → SQL | `PASSED` |
| Segunda publicación | `NO_OP` |
| Filas antes/después | 953 → 953 |
| Escrituras en reejecución | 0 |

### 5.3 Incidentes resueltos

| Problema | Solución | Resultado |
|---|---|---|
| `ORDER BY` en consultas/vistas | Corrección de SQL | Flujo continuó |
| Disponibilidad temporal de JDBC | Reintentos controlados | Conexión validada |
| Credenciales no operativas | Restablecimiento seguro | Publicación correcta |

## Hito 6 — Consumo en Power BI

### 6.1 Construcción

- Consumo de las siete tablas del esquema `serving`.
- Seis relaciones activas desde dimensiones hacia `fact_transaction`.
- Dashboard mínimo para demostrar el flujo end-to-end.

### 6.2 Validación y resultado

| Indicador | Resultado |
|---|---:|
| Transacciones | 8 |
| Clientes únicos | 4 |
| Cuentas únicas | 6 |
| Canales Card/Mobile/Online/ATM | 3/2/2/1 |

DirectQuery fue probado, pero el modo final no se afirma porque el PBIX y el modelo semántico no están versionados.

## Hito 7 — Monitorización y costos

### 7.1 Cierre operativo

- Pipeline ADF finalizado sin actividades pendientes.
- Databricks compute detenido y autoapagado configurado en 10 minutos.
- Azure SQL en estado `Paused`.
- Facturación sobre el límite gratuito deshabilitada.

### 7.2 Validación y resultado

| Control | Resultado |
|---|---:|
| Costo observado | USD 0,04 |
| Proyección observada | USD 0,29 |
| Presupuesto mensual | USD 2 |
| Umbral de alerta | 50 % / USD 1 |

Los costos son una fotografía histórica del cierre, no una garantía de precio futuro.

## Resumen de validaciones

| Tipo | Alcance | Resultado |
|---|---|---|
| Automatizada local | Contratos y fixtures | 42/42 controles |
| Automatizada local | Ingesta, Silver y Gold | 37/37 pruebas |
| Manual cloud | Databricks y ADF | `PASSED` |
| Manual cloud | Azure SQL | `PASSED` |
| Manual cloud | Power BI | `PASSED` |
| Operativa | Recursos y costos | `PASSED` |

## Límites del repositorio

No están exportados el pipeline ADF definitivo, el notebook `04_gold_to_azure_sql`, el PBIX, las fórmulas DAX ni el modelo semántico. Las capturas se conservan fuera del repositorio público. Estas ausencias se declaran y no se completan mediante reconstrucciones.
