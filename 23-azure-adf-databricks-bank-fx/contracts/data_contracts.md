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
