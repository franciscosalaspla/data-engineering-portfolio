# Arquitectura del Proyecto 23

## Estado verificable

Los Hitos 1–4 están implementados localmente. La ejecución comprobable llega a un modelo estrella Gold Delta y un snapshot Parquet mediante PySpark. Los artefactos ADF y notebooks Databricks están versionados, pero no se han importado ni ejecutado en Azure Data Factory, Databricks Free Edition o Azure Databricks.

## Flujo actual

```mermaid
flowchart LR
    S["CSV + JSON + ECB mock"] --> I["Ingesta metadata-driven"]
    I --> L["Landing inmutable"]
    L --> B["Bronze JSONL"]
    B --> P["PySpark con schemas explícitos"]
    P --> Q{"Quality gates Silver"}
    Q -->|Aceptado| M["Delta MERGE"]
    Q -->|Rechazado| X["Delta quarantine"]
    M --> C["4 tablas Silver"]
    C --> G["6 dimensiones + fact_transactions"]
    G --> R["Reconciliación + snapshot Parquet"]
    M --> A["Audit + Delta history"]
    X --> A
```

ADF está representado por artefactos Azure-style parametrizados. Localmente, `scripts/run_ingestion.py` cumple el mismo límite Landing/Bronze sin afirmar una ejecución cloud.

## Capas implementadas

### Landing

- copia byte a byte del archivo recibido;
- partición por fuente, entidad, fecha y run;
- SHA-256 y metadata adyacente;
- sin correcciones de negocio.

### Bronze

- JSONL por entidad y checksum del archivo;
- campos originales válidos;
- metadata de origen, archivo, fecha, ejecución, registro y Landing;
- idempotencia de archivo antes de Silver.

### Silver

- lectura recursiva de Bronze con `StructType` explícito;
- normalización PySpark de strings, fechas, timestamps y decimales;
- reglas contractuales y referencias cuenta-cliente/transacción-cuenta;
- deduplicación determinística por clave de negocio;
- tablas Delta path-based sin particionamiento para el volumen pequeño actual;
- `MERGE` por clave y `_record_checksum`;
- cuarentena Delta idempotente y auditoría JSONL.

Las rutas locales son:

```text
data/output/silver/silver_customers
data/output/silver/silver_accounts
data/output/silver/silver_fx_rates
data/output/silver/silver_transactions
data/output/silver_quarantine
data/output/audit/silver_audit.jsonl
```

No se particionan las tablas Silver porque solo contienen 22 filas y una partición física añadiría archivos pequeños sin beneficio. El diseño permite cambiar las rutas a Unity Catalog Volumes antes de aumentar el volumen.

### Gold

- seis dimensiones Type 1 con claves sustitutas determinísticas;
- hecho `fact_transactions` con grano de una fila por `transaction_id`;
- conversión EUR por fecha y moneda usando decimales;
- cuarentena para FX o referencias faltantes y duplicados;
- `MERGE` Delta por clave natural y checksum de contenido;
- controles de claves, huérfanos, conteos e importes;
- snapshot Parquet desnormalizado para consumo analítico.

```text
data/output/gold/dim_date
data/output/gold/dim_customer
data/output/gold/dim_account
data/output/gold/dim_merchant
data/output/gold/dim_channel
data/output/gold/dim_currency
data/output/gold/fact_transactions
data/output/gold_quarantine
data/output/serving/transactions_analytics
data/output/audit/gold_audit.jsonl
```

El modelo tampoco se particiona con ocho hechos: esa decisión evita archivos pequeños y queda abierta a revisión cuando exista volumen representativo.

## Modelo estrella Gold

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_TRANSACTIONS : date_key
    DIM_CUSTOMER ||--o{ FACT_TRANSACTIONS : customer_key
    DIM_ACCOUNT ||--o{ FACT_TRANSACTIONS : account_key
    DIM_MERCHANT ||--o{ FACT_TRANSACTIONS : merchant_key
    DIM_CHANNEL ||--o{ FACT_TRANSACTIONS : channel_key
    DIM_CURRENCY ||--o{ FACT_TRANSACTIONS : currency_key
```

`dim_customer` y `dim_account` se construyen desde sus tablas Silver completas; fecha, comercio, canal y moneda se derivan de transacciones Silver. Las claves hash incorporan un namespace de entidad y se validan contra colisiones dentro de cada dimensión. `date_key` usa el formato estable `yyyyMMdd`.

Las tasas ECB representan unidades de moneda cotizada por `1 EUR`. La fórmula es:

```text
amount_eur = amount_original / fx_rate_to_eur
```

`amount_original` y `amount_eur` son `decimal(18,2)`; `fx_rate_to_eur` es `decimal(18,8)`. EUR utiliza tasa `1.00000000`.

## Calidad y dependencias

El driver procesa en este orden:

```mermaid
flowchart LR
    C["customers"] --> A["accounts + FK customer"]
    A --> T["transactions + FK account"]
    F["fx_rates"] --> T
```

`fx_rates` se procesa antes de transacciones para dejar disponible el conjunto completo de Silver, aunque la conversión monetaria se reserva para Gold. Los registros con reglas incumplidas se separan antes del `MERGE`; una fila puede aportar varias evidencias de regla en cuarentena.

## Idempotencia Delta

Cada entidad declara su clave de negocio en `config/silver_pipeline.json`. La comparación con la tabla existente utiliza `_record_checksum`:

1. una clave nueva se inserta;
2. una clave con contenido cambiado se actualiza;
3. una clave con el mismo checksum se omite;
4. duplicados dentro del input conservan una ganadora ordenada por timestamp, checksum y ruta Bronze.

Cuando todas las filas coinciden, el pipeline devuelve `SKIPPED` y evita un `MERGE` físico. Una prueba específica modifica un checksum, ejecuta un `MERGE` Delta real y verifica `numTargetRowsUpdated=1` en el historial.

## Idempotencia Gold

Cada dimensión usa su clave natural y el hecho usa `transaction_id`. `_gold_record_checksum` solo incluye contenido analítico, no run ID ni timestamps de proceso:

1. una clave nueva se inserta;
2. un cambio real de contenido se actualiza como Type 1;
3. una reejecución idéntica se omite sin `MERGE` físico;
4. el snapshot se reescribe únicamente cuando cambió alguna tabla Gold.

La reconciliación posterior verifica grano, claves no nulas, huérfanos, unicidad de claves sustitutas, conteos y suma de importes originales. La suma EUR se publica como métrica, pero no se compara directamente con la suma original porque mezcla monedas antes de la conversión.

## Diseño para Databricks Free Edition

Los notebooks en `databricks/notebooks/` exponen widgets para entorno, run ID, proyecto, Bronze, Silver, Gold, ambas cuarentenas, auditoría, serving, catálogo y schema. Los drivers importan los módulos del repositorio; las reglas no están duplicadas en celdas.

En Free Edition se usarán rutas `/Volumes/...` y el runtime proporcionará Spark/Delta. Esa fase sigue pendiente: la evidencia actual debe llamarse **PySpark/Delta local**, no Databricks Free Edition ni Azure Databricks.

## Arquitectura objetivo posterior

```mermaid
flowchart LR
    S["ECB API / CSV / JSON"] --> ADF["Azure Data Factory"]
    ADF --> ADLS["ADLS Gen2 Landing"]
    ADLS --> D["Databricks driver"]
    D --> SI["Bronze + Silver Delta"]
    SI --> G["Gold star model"]
    G --> SQL["Azure SQL"]
    SQL --> BI["Power BI"]
```

El Hito 5 incorporará la ingesta real API + CSV + JSON mediante ADF y ADLS. Azure SQL, Power BI y la ventana temporal de Azure Databricks permanecen en hitos posteriores.
