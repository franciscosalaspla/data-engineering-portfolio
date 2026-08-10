# Implementación end-to-end

## Propósito

Este documento registra, en el orden de los Hitos 1–7, qué se construyó y cómo se validó. La suite automatizada corresponde al código versionado; ADF, Azure SQL, Power BI y costos se validaron directamente en Azure.

## 1. Landing → Bronze

### Construcción

- Se definieron contratos y schemas para clientes, cuentas, transacciones y tasas FX.
- Se integraron transacciones CSV, clientes/cuentas JSON y la API histórica del ECB.
- ADLS Gen2 conserva los archivos en Landing y Databricks crea Bronze con metadata técnica.
- El checksum permite reconocer archivos ya procesados y mantener trazabilidad por lote.

### Validación

- Fixtures sintéticos determinísticos: **42/42 controles aprobados**.
- Datos válidos, inválidos y reejecución incluidos en la cobertura.
- La ejecución cloud dejó las entidades Bronze creadas y validadas.

## 2. Bronze → Silver

### Construcción

- PySpark aplica schemas explícitos y normaliza tipos, fechas, dominios e identificadores.
- Se controlan nulos, duplicados y relaciones cuenta → cliente y transacción → cuenta.
- Los registros que no cumplen el contrato se separan en cuarentena con causa identificable.
- Delta `MERGE` actualiza por clave de negocio sin duplicar registros.

### Validación

- Quality gates de clientes, cuentas, transacciones y tasas FX: **`PASSED`**.
- Conteos, claves, dominios y cuarentena reconciliados antes de avanzar.
- Segunda ejecución sin cambios comprobada como idempotente.

## 3. Silver → Gold

### Construcción

- Se convirtieron importes de EUR, USD y GBP a EUR usando la tasa de la fecha.
- Se generaron claves sustitutas determinísticas.
- Se construyeron seis dimensiones Type 1 y una tabla de hechos.
- El grano quedó definido como una fila por `transaction_id`.

### Validación

- Grano, claves, huérfanos, importes y reconciliación: **`PASSED`**.
- La suite local completa de ingesta, Silver y Gold terminó **37/37**.
- Un contenido sin cambios evita un nuevo snapshot o `MERGE` innecesario.

## 4. Orquestación con Azure Data Factory

### Construcción

ADF ejecuta tres notebooks de Databricks con dependencia de éxito:

| Orden | Actividad | Resultado | Duración |
|---:|---|---|---:|
| 1 | `nb_01_landing_to_bronze` | Correcto | 2 min 37 s |
| 2 | `nb_02_bronze_to_silver` | Correcto | 3 min 6 s |
| 3 | `nb_03_silver_to_gold` | Correcto | 4 min 22 s |
|  | **Pipeline completo** | **Correcto** | **10 min 17 s** |

### Validación

- Linked Service de Azure Databricks: conexión correcta.
- Pipeline validado, publicado y ejecutado.
- ADF Monitor: **3/3 actividades correctas**.

Existe una ejecución fallida anterior en el historial, pero no se conserva evidencia suficiente para atribuirle una causa. La documentación no la infiere.

## 5. Serving en Azure SQL

### Construcción

- El modelo Gold se publicó mediante JDBC en el esquema `serving`.
- Key Vault y Databricks Secret Scope mantienen usuario y contraseña fuera del código.
- Azure SQL se configuró en modalidad serverless con exceso sobre el límite gratuito deshabilitado.

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

### Validación

| Control | Resultado |
|---|---|
| Preflight y publicación | 7 tablas, 953 filas y `LOADED` |
| PK/FK | 7/7 aprobadas |
| Registros huérfanos | 0 |
| Reconciliación Gold → SQL | `PASSED` |
| Segunda publicación | `NO_OP` |
| Filas antes/después | 953 → 953 |
| Escrituras en segunda ejecución | 0 |

Durante la implementación se corrigieron consultas con `ORDER BY`, se reintentó la disponibilidad JDBC y se restablecieron credenciales SQL. La publicación final quedó validada.

## 6. Consumo en Power BI

### Construcción

- Se cargaron las siete tablas de `serving`.
- Se configuraron seis relaciones activas, una por dimensión hacia `fact_transaction`.
- Se creó y publicó una página ejecutiva mínima para mantener el foco en Data Engineering.
- DirectQuery fue probado; el modo final publicado no se afirma sin el PBIX.

### Validación

| Indicador | Resultado |
|---|---:|
| Transacciones | 8 |
| Clientes únicos con transacciones | 4 |
| Cuentas únicas con transacciones | 6 |
| Canales | Card 3 · Mobile 2 · Online 2 · ATM 1 |

`dim_customer` contiene cinco clientes; cuatro aparecen en la tabla de hechos.

## 7. Monitorización, costos y cierre

### Controles aplicados

| Control | Resultado al cierre |
|---|---|
| ADF Monitor | Pipeline correcto; 3/3 actividades correctas |
| Databricks compute | Detenido; autoapagado de 10 minutos |
| Azure SQL | `Paused` |
| Exceso del plan gratuito | Deshabilitado |
| Costo observado | USD 0,04 |
| Proyección observada | USD 0,29 |
| Presupuesto | USD 2 mensual |
| Alerta | 50 %, equivalente a USD 1 |

El [runbook operativo](operations_and_cost_runbook.md) define el preflight, la ejecución y el cierre de recursos.

## Resumen de validación

| Alcance | Tipo | Resultado |
|---|---|---|
| Fixtures | Automatizada local | 42/42 |
| Ingesta, Silver y Gold | Automatizada local | 37/37 |
| Capas Medallion | Ejecución Databricks | Quality gates `PASSED` |
| Orquestación | Validación cloud | 3/3 actividades correctas |
| Azure SQL | Validación cloud | 7 tablas, 953 filas, integridad e idempotencia aprobadas |
| Power BI | Validación cloud | Modelo y KPI publicados |
| Operación y costos | Validación cloud | Recursos cerrados y controles activos |

## Alcance de los artefactos

No están versionados el pipeline ADF definitivo, el notebook `04_gold_to_azure_sql`, el PBIX, las fórmulas DAX ni las capturas. Estas ausencias se declaran como límites y no se completan con artefactos reconstruidos. El detalle está en [Catálogo de evidencias](evidence_catalog.md).
