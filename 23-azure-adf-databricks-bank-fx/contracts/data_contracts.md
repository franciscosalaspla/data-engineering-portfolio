# Contratos de datos

## Reglas comunes

- Todos los datos son sintéticos.
- Codificación UTF-8.
- Fechas calendario en ISO `YYYY-MM-DD`.
- Timestamps en ISO 8601 UTC con sufijo `Z`.
- Identificadores determinísticos, no reutilizados entre entidades.
- Monedas permitidas: `EUR`, `USD`, `GBP`.
- Los fixtures inválidos están separados y sus errores forman parte del manifiesto.

## Fuente 1: transacciones CSV

El encabezado debe respetar exactamente este orden:

```text
transaction_id,account_id,transaction_timestamp,amount,currency,transaction_type,merchant_id,merchant_name,merchant_category,channel,status,source_batch_id
```

| Campo | Tipo lógico | Obligatorio | Valores o regla |
|---|---|---:|---|
| `transaction_id` | string | Sí | Único, patrón `TXN-NNNN` |
| `account_id` | string | Sí | Debe existir en cuentas |
| `transaction_timestamp` | timestamp UTC | Sí | ISO 8601 parseable |
| `amount` | decimal | Sí | Mayor que cero, máximo dos decimales |
| `currency` | string | Sí | `EUR`, `USD`, `GBP` |
| `transaction_type` | string | Sí | `PURCHASE`, `TRANSFER`, `PAYMENT`, `WITHDRAWAL` |
| `merchant_id` | string | Sí | Patrón `MER-NNN` |
| `merchant_name` | string | Sí | Nombre sintético no vacío |
| `merchant_category` | string | Sí | Catálogo controlado |
| `channel` | string | Sí | `ATM`, `CARD`, `MOBILE`, `ONLINE` |
| `status` | string | Sí | `APPROVED`, `DECLINED`, `PENDING` |
| `source_batch_id` | string | Sí | `BATCH-001` o `BATCH-002` |

Categorías permitidas: `GROCERIES`, `TRANSFER`, `TRANSPORT`, `BUSINESS_SERVICES`, `TRAVEL`, `CASH_WITHDRAWAL`, `ELECTRONICS`.

## Fuente 2: clientes y cuentas JSON

### Clientes

| Campo | Tipo | Obligatorio | Valores o regla |
|---|---|---:|---|
| `customer_id` | string | Sí | Único, patrón `CUS-NNN` |
| `country_code` | string | Sí | ISO alpha-2 sintético |
| `segment` | string | Sí | `RETAIL`, `PREMIUM`, `SME` |
| `onboarding_date` | date | Sí | ISO parseable |
| `status` | string | Sí | `ACTIVE`, `SUSPENDED`, `CLOSED` |
| `risk_rating` | string | Sí | `LOW`, `MEDIUM`, `HIGH` |

No se permiten nombres, correos, teléfonos, documentos ni direcciones.

### Cuentas

| Campo | Tipo | Obligatorio | Valores o regla |
|---|---|---:|---|
| `account_id` | string | Sí | Único, patrón `ACC-NNN` |
| `customer_id` | string | Sí | Debe existir en clientes |
| `account_type` | string | Sí | `CHECKING`, `SAVINGS`, `CREDIT`, `BUSINESS` |
| `base_currency` | string | Sí | `EUR`, `USD`, `GBP` |
| `opened_date` | date | Sí | ISO parseable |
| `status` | string | Sí | `ACTIVE`, `SUSPENDED`, `CLOSED` |

Los envelopes JSON incluyen metadata que marca explícitamente el contenido como fixture sintético.

## Fuente 3: mock ECB JSON

La respuesta conceptual contiene:

- `fixture_metadata.is_synthetic=true`;
- `fixture_metadata.source=ECB_API_MOCK`;
- moneda base `EUR`;
- una entrada por fecha lógica;
- tasas positivas para EUR, USD y GBP;
- tasa EUR igual a `1`.

Las tasas significan unidades de moneda cotizada por `1 EUR`. Para convertir USD o GBP a EUR se utilizará el inverso de la tasa publicada.

## Reconciliación esperada del Hito 1

- Cada cuenta válida referencia un cliente existente.
- Cada transacción válida referencia una cuenta existente.
- Cada fecha y moneda transaccional tiene tasa disponible.
- El replay del lote 1 es idéntico al archivo original.
- Los registros inválidos producen exactamente los códigos de error declarados en el manifiesto.

## Contrato técnico Landing del Hito 2

Cada fuente habilitada y no procesada se copia sin alterar sus bytes a:

```text
data/output/landing/{source_name}/{entity_name}/ingestion_date=YYYY-MM-DD/run_id={run_id}/{source_file}
```

Un archivo adyacente `{source_file}.metadata.json` registra `run_id`, fuente, entidad, archivo, ruta Landing, checksum SHA-256, timestamp UTC y fecha de ingesta. Una ruta Landing existente solo se acepta si conserva exactamente el mismo checksum; nunca se sobrescribe con contenido diferente.

## Contrato técnico Bronze del Hito 2

Bronze materializa únicamente registros que cumplen el esquema de su fuente y las referencias necesarias para respetar los contratos del Hito 1. No convierte monedas, no deduplica por reglas Silver y no enriquece atributos de negocio.

Cada registro preserva sus campos de origen y agrega:

| Campo | Descripción |
|---|---|
| `_run_id` | Identificador de la ejecución que materializó el registro |
| `_ingested_at` | Timestamp UTC de ingesta |
| `_source_name` | Fuente lógica declarada en metadata |
| `_source_file` | Nombre del archivo original |
| `_record_checksum` | SHA-256 del registro original serializado de forma canónica |
| `_ingestion_date` | Fecha lógica de partición |
| `_landing_path` | Ruta relativa del archivo Landing trazable |

La ruta física agrega una partición por checksum del archivo:

```text
data/output/bronze/{destination_path}/ingestion_date=YYYY-MM-DD/source_checksum={sha256_prefix}/records.jsonl
```

## Cuarentena y auditoría del Hito 2

Los errores de datos producen registros JSONL en `data/output/quarantine/` con el registro original, tipo `DATA_QUALITY` y todos los motivos de rechazo. Los errores técnicos se registran con `error_type=TECHNICAL` y estado `FAILED`; no marcan el archivo como procesado.

La clave de idempotencia es `source_name + entity_name + file_sha256`. Un archivo ya completado queda `SKIPPED`, informa sus filas como duplicadas y no vuelve a escribir Landing, Bronze ni cuarentena. Cada intento conserva un registro estructurado con rutas, conteos, checksum, tiempos, estado y mensaje de error.

## Contrato Silver del Hito 3

Silver utiliza esquemas PySpark explícitos para cada lectura Bronze. No se permite inferencia de esquema en el flujo productivo. Las claves de negocio son:

| Entidad | Tabla Delta | Clave de negocio |
|---|---|---|
| Clientes | `silver_customers` | `customer_id` |
| Cuentas | `silver_accounts` | `account_id` |
| Tipos de cambio | `silver_fx_rates` | `effective_date` |
| Transacciones | `silver_transactions` | `transaction_id` |

Las transformaciones Silver normalizan espacios, mayúsculas, fechas, timestamps, decimales y dominios respaldados por los contratos de origen. `rates.EUR`, `rates.USD` y `rates.GBP` se materializan como `rate_eur`, `rate_usd` y `rate_gbp`; no se calcula todavía `amount_eur`.

Toda fila aceptada conserva la metadata Bronze y agrega:

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `_silver_processed_at` | timestamp UTC | Instante de la ejecución que insertó o actualizó la fila |
| `_silver_run_id` | string | Identificador de esa ejecución Silver |
| `_quality_status` | string | `PASSED` para filas publicadas |
| `_source_bronze_path` | string | Archivo JSONL Bronze leído por Spark |

## Quality gates Silver

- claves obligatorias y patrones de identificadores;
- fechas y timestamps parseables;
- importes positivos con escala decimal de dos posiciones;
- dominios de monedas, estados, tipos, segmentos, canales y categorías;
- referencia cuenta → cliente;
- referencia transacción → cuenta;
- tasas EUR, USD y GBP presentes y positivas, con EUR igual a `1.0`;
- una ganadora determinística por clave de negocio dentro del input.

Los registros rechazados no se escriben en las tablas Silver. La cuarentena Delta conserva `original_record`, entidad, clave, regla, motivo, run ID, timestamp Silver y ruta Bronze. Una fila con varias reglas genera una entrada por regla. `_quarantine_id` evita repetir la misma evidencia en una reejecución.

## MERGE e idempotencia Silver

El `MERGE` compara cada clave de negocio y `_record_checksum`:

- clave nueva: `INSERT`;
- clave existente con checksum diferente: `UPDATE`;
- clave existente con checksum idéntico: `SKIPPED`, sin ejecutar un `MERGE` físico innecesario;
- duplicado dentro del input: cuarentena con `DUPLICATE_BUSINESS_KEY`.

Las tablas mantienen el contenido válido de ejecuciones anteriores. La auditoría registra por entidad filas fuente, válidas, rechazadas, duplicadas, insertadas, actualizadas y omitidas, junto con la versión, operación y métricas disponibles en el historial Delta.

## Contrato dimensional Gold del Hito 4

El grano de `fact_transactions` es exactamente una fila por `transaction_id`. Sus claves foráneas no admiten nulos y deben resolver contra estas dimensiones Type 1:

| Tabla | Clave natural | Clave sustituta | Origen |
|---|---|---|---|
| `dim_date` | `full_date` | `date_key` | fecha UTC de transacción |
| `dim_customer` | `customer_id` | `customer_key` | Silver clientes completo |
| `dim_account` | `account_id` | `account_key` | Silver cuentas completo |
| `dim_merchant` | `merchant_id` | `merchant_key` | Silver transacciones |
| `dim_channel` | `channel_code` | `channel_key` | Silver transacciones |
| `dim_currency` | `currency_code` | `currency_key` | Silver transacciones |

Las claves sustitutas son `long` determinísticos. La fecha usa `yyyyMMdd`; las restantes incorporan un namespace de dimensión al hash. El pipeline comprueba claves sustitutas duplicadas antes de aprobar la reconciliación.

### Medidas monetarias y FX

| Campo | Tipo | Regla |
|---|---|---|
| `amount_original` | `decimal(18,2)` | importe Silver sin alterar |
| `currency_code` | string | EUR, USD o GBP |
| `fx_rate_to_eur` | `decimal(18,8)` | unidades de moneda por `1 EUR` |
| `fx_rate_date` | date | misma fecha UTC que la transacción |
| `amount_eur` | `decimal(18,2)` | `amount_original / fx_rate_to_eur` |

EUR requiere tasa `1.00000000`. Una tasa ausente, nula o no positiva impide publicar el hecho y produce `FX_RATE_MISSING` en la cuarentena Gold. También se explican duplicados de `transaction_id` y referencias faltantes a cuenta o cliente.

### Trazabilidad e idempotencia Gold

Cada fila conserva `_source_silver_run_id` y `_source_silver_path`, y agrega `_gold_run_id`, `_gold_processed_at` y `_gold_record_checksum`. El checksum excluye metadata volátil: solo un cambio de contenido provoca actualización Type 1. Una reejecución idéntica queda `SKIPPED`.

La auditoría reconcilia:

- transacciones Silver = hechos publicados + transacciones rechazadas;
- suma original aceptada = suma `amount_original` del hecho;
- cero claves de negocio duplicadas;
- cero claves foráneas nulas o huérfanas;
- cero claves sustitutas duplicadas por dimensión.
