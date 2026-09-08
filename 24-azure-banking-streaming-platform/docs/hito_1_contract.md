# Contrato del Hito 1 — Integración continua local

## Propósito

Crear una puerta de calidad reproducible para el Proyecto 24 sin iniciar sesión en Azure, usar
credenciales cloud ni desplegar recursos.

## Alcance implementado

- estructura Python `src/` con contrato preliminar, normalización y deduplicación pura;
- fixtures sintéticos determinísticos con 5 clientes, 7 cuentas y dos microbatches;
- replay byte a byte del primer microbatch y tres eventos inválidos;
- pruebas de contrato, transformación, referencias, rechazo e idempotencia inicial;
- lint y formato de Python con Ruff;
- lint del workflow con yamllint;
- validador de JSON, JSONL, enlaces Markdown, PII prohibida y patrones obvios de secretos;
- GitHub Actions limitado por rutas al Proyecto 24 y con `contents: read`.

## Límites

- El contrato de este hito es una interfaz local mínima, no el JSON Schema v1 definitivo.
- La deduplicación usa estado explícito en memoria, no checkpoints ni estado de Structured Streaming.
- No se implementan Event Hubs, PySpark, Delta Lake, Bicep, OIDC, Key Vault ni Azure SQL.
- La ejecución local no demuestra el comportamiento de servicios Azure.

El contrato JSON versionado se cierra en el Hito 4. Checkpoints, watermark, deduplicación distribuida
y cuarentena Delta se implementan en el Hito 5.

## Fixtures y resultados esperados

| Fixture | Filas | Resultado esperado |
|---|---:|---|
| `transactions_batch_001.jsonl` | 3 | 3 aceptadas |
| `transactions_batch_002.jsonl` | 3 | 2 aceptadas y `EVT-0002` duplicado |
| `transactions_batch_001_replay.jsonl` | 3 | 0 aceptadas y 3 duplicadas |
| `transactions_invalid.jsonl` | 3 | 3 rechazadas por contrato |

Después de los dos microbatches existen cinco `event_id` únicos. El replay no modifica ese estado.

## Puerta de CI

El workflow `.github/workflows/p24-ci.yml` se activa únicamente cuando cambia el Proyecto 24 o el
propio workflow. Sus pasos son:

1. checkout sin persistir credenciales;
2. Python 3.12 e instalación de dependencias fijadas;
3. lint y formato de Python;
4. lint de YAML;
5. pruebas automatizadas;
6. validación integrada de fixtures, enlaces y controles de seguridad.

El workflow no concede `id-token: write`, no referencia GitHub Secrets y no ejecuta `azure/login`.

## Ejecución local

Desde `24-azure-banking-streaming-platform/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement requirements-dev.txt
python -m ruff check src scripts tests
python -m ruff format --check src scripts tests
yamllint --config-file .yamllint.yml ../.github/workflows/p24-ci.yml
python -m pytest
python scripts/validate_repository.py
```

## Criterios de aceptación

- [x] La estructura y las pruebas se limitan al Proyecto 24.
- [x] Los fixtures son sintéticos, determinísticos y no contienen campos de PII.
- [x] Contrato, transformación y replay pueden probarse sin Azure.
- [x] La segunda aparición de un `event_id` no vuelve a aceptarse.
- [x] El replay exacto produce cero registros nuevos.
- [x] El workflow tiene permisos mínimos y no usa credenciales Azure.
- [x] Las dependencias directas de calidad están fijadas por versión.
- [ ] El workflow finaliza en verde dentro del PR del Hito 1.

## Evidencia y clasificación

| Evidencia | Clasificación | Estado antes del PR |
|---|---|---|
| Ruff, yamllint, pytest y validador integrado | Local | Verificado localmente |
| GitHub Actions | Remota sin Azure | Pendiente de publicación |
| Event Hubs y procesamiento streaming | Futuro | Hitos 4–5 |
| Recursos y credenciales Azure | Cloud | No creados ni utilizados |

## Stop conditions

Se requiere aprobación antes de realizar commit, push o abrir el PR. También se mantiene la
prohibición de desplegar Azure, configurar OIDC, crear secretos o ampliar el alcance del MVP sin
autorización explícita.

## Definición de terminado

El Hito 1 termina cuando todas las validaciones locales pasan, el workflow se ejecuta en verde en
un PR independiente y el usuario revisa la evidencia. El merge continúa siendo manual.
