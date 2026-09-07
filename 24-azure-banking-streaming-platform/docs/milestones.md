# Plan de hitos y criterios de salida

## Regla general

Cada hito se desarrolla en una rama y un PR independientes. Un hito no comienza hasta que el anterior tenga una condición de salida verificable o una excepción documentada.

## Hito 0 — Baseline y arquitectura

**Objetivo:** delimitar el MVP y evitar decisiones cloud implícitas.

**Entregables:** README inicial, contrato, arquitectura, roadmap, restricciones de seguridad y costos.

**Salida:** documentos validados, cero recursos creados y aprobación de las decisiones D01–D10.

## Hito 1 — Integración continua

**Objetivo:** crear una puerta de calidad reproducible sin depender de Azure.

**Entregables:** estructura Python, fixtures, configuración de lint/tests y workflow CI limitado al Proyecto 24.

**Salida:** CI verde en PR, sin credenciales, con pruebas de contrato, transformación e idempotencia inicial.

## Hito 2 — Infraestructura como código

**Objetivo:** representar la infraestructura `dev` mediante Bicep modular.

**Entregables:** módulos, parámetros seguros, naming, tags, outputs no sensibles, compilación y lint local.

**Salida:** plantillas compilables y validadas estáticamente, sin iniciar sesión en Azure ni desplegar recursos.

## Hito 3 — Despliegue seguro

**Objetivo:** desplegar de forma manual y auditable sin client secrets persistentes.

**Entregables:** workflow `workflow_dispatch`, OIDC, GitHub Environment `dev`, roles mínimos, Key Vault y validación `what-if`.

**Salida:** autenticación federada validada, `what-if` revisado, despliegue manual controlado y logs sin secretos.

## Hito 4 — Ingesta de eventos

**Objetivo:** publicar y consumir transacciones bancarias sintéticas con un contrato versionado.

**Entregables:** JSON Schema v1, productor reproducible, Event Hub, partición definida, fixtures válidos e inválidos.

**Salida:** conteos reconciliados productor → Event Hubs → consumidor y cero PII.

## Hito 5 — Procesamiento streaming

**Objetivo:** materializar Bronze y Silver con calidad y tolerancia a reintentos.

**Entregables:** readStream, checkpoint, watermark, deduplicación, cuarentena, auditoría y replay.

**Salida:** duplicados neutralizados, eventos tardíos tratados según contrato y reinicio desde checkpoint validado.

## Hito 6 — Gold y serving

**Objetivo:** producir métricas incrementales y disponibilizarlas para consumo.

**Entregables:** modelo Gold, reconciliación, microbatch hacia Azure SQL y consultas de validación.

**Salida:** PK/FK válidas, cero huérfanos, conteos conciliados y segunda publicación `NO_OP`.

## Hito 7 — Observabilidad

**Objetivo:** hacer visible la salud técnica y de datos del pipeline.

**Entregables:** métricas de throughput, lag, rechazados, duplicados, duración, fallos y costo; alertas mínimas.

**Salida:** un fallo controlado genera evidencia diagnóstica y una ejecución correcta deja métricas reconciliables.

## Hito 8 — Validación y cierre

**Objetivo:** demostrar operación end-to-end, recuperación y cierre seguro.

**Entregables:** prueba integral, replay, runbook, catálogo de evidencias, README final, guía de entrevista y teardown.

**Salida:** suite local y validaciones cloud aprobadas, evidencia sanitizada, recursos detenidos o eliminados y PR final revisado.

## Matriz de aprobación

| Punto de control | Responsable | Acción permitida después |
|---|---|---|
| Contrato del hito aprobado | Usuario | Implementación local completa |
| Diff y pruebas locales aprobados | Usuario | Commit, push y PR en borrador |
| Estimación y teardown cloud aprobados | Usuario | Despliegue temporal en Azure |
| Evidencia cloud revisada | Usuario + Codex | Cierre documental del hito |
| PR listo y revisado | Usuario | Merge manual |

## Evidencia mínima por hito

Cada PR debe registrar:

- objetivo y criterios de aceptación;
- archivos agregados o modificados;
- comandos de validación y resultados;
- decisiones y desviaciones;
- riesgos pendientes;
- clasificación de cada afirmación: local, cloud, simulada o futura;
- estado final de cualquier recurso con costo.
