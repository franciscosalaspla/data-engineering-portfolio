# Contrato del Hito 0 — Baseline y arquitectura

## Propósito

Establecer una base verificable para el Proyecto 24 antes de escribir pipelines o desplegar Azure. El hito transforma la idea de “agregar streaming y CI/CD” en decisiones, límites y criterios de aceptación concretos.

## Baseline confirmado

El Proyecto 23 ya implementó y validó:

- ADLS Gen2 con Landing, Bronze, Silver y Gold;
- procesamiento PySpark y Delta Lake en Azure Databricks;
- ADF con tres notebooks secuenciales;
- calidad, cuarentena, reconciliación e idempotencia;
- siete tablas y 953 filas en Azure SQL;
- PK/FK correctas, cero huérfanos y segunda publicación `NO_OP`;
- modelo estrella y dashboard mínimo viable en Power BI;
- Key Vault y Databricks Secret Scope para credenciales SQL;
- control operativo con compute detenido, SQL pausado y presupuesto.

El Proyecto 24 reutiliza los patrones y el dominio sintético, pero no modifica ni reconstruye la implementación histórica del Proyecto 23.

## Pregunta de arquitectura

¿Cómo extender el flujo batch existente para procesar transacciones bancarias sintéticas con baja latencia, preservando calidad, replay, trazabilidad, seguridad y un serving analítico estable?

## Decisiones aprobables en este hito

| ID | Decisión | Justificación |
|---|---|---|
| D01 | Crear el Proyecto 24 como carpeta independiente | Conserva el Proyecto 23 como evidencia batch terminada |
| D02 | Mantener ADF para batch y backfill | El streaming no reemplaza la recuperación histórica |
| D03 | Usar Event Hubs mediante su endpoint compatible con Kafka | Permite consumir eventos con el conector Kafka incluido en Databricks Runtime |
| D04 | Implementar Structured Streaming directamente | Expone checkpoints, offsets, watermarks y estado de forma versionable y demostrable |
| D05 | Persistir cada etapa en Delta Lake | Facilita replay, auditoría y procesamiento incremental |
| D06 | Usar entrega al menos una vez más idempotencia | Evita prometer exactly-once end-to-end sin evidencia suficiente |
| D07 | Publicar Azure SQL por microbatch | Aísla el serving relacional de la presión evento a evento |
| D08 | Definir CI sin Azure y CD manual con OIDC | Las pruebas no requieren credenciales y el despliegue evita secretos de larga duración |
| D09 | Utilizar solo información sintética | Elimina PII y reduce el riesgo de exposición pública |
| D10 | Limitar el MVP a un ambiente efímero `dev` | Reduce costo y complejidad sin simular una plataforma productiva |

Lakeflow Declarative Pipelines se documentará como alternativa administrada. No se incorpora al MVP para conservar visibilidad sobre los fundamentos de Structured Streaming y facilitar pruebas locales.

## Criterios de aceptación

- [ ] La relación entre los proyectos 23 y 24 está explicada sin duplicar implementaciones.
- [ ] Existe una arquitectura batch + streaming con responsabilidades separadas.
- [ ] Los hitos 0–8 tienen objetivo, evidencia y condición de salida.
- [ ] El alcance diferencia MVP, evolución futura y exclusiones.
- [ ] La estrategia de seguridad prohíbe credenciales persistentes en código y workflows.
- [ ] La estrategia de costos exige aprobación antes de desplegar y teardown posterior.
- [ ] No se crean recursos Azure durante el Hito 0.
- [ ] No se afirma que Event Hubs, CI/CD o streaming ya estén implementados.
- [ ] Los enlaces Markdown y el diff de Git pasan validación local.
- [ ] El cambio se limita a la carpeta `24-azure-banking-streaming-platform/`.

## Evidencia del hito

| Evidencia | Estado esperado |
|---|---|
| Rama aislada desde el último `origin/main` | Verificada |
| Árbol de archivos del Proyecto 24 | Verificado |
| `git diff --check` | Sin errores |
| Validador de enlaces Markdown locales | Sin enlaces rotos |
| Recursos Azure creados | Ninguno |
| Credenciales o identificadores sensibles | Ninguno |

## Stop conditions

Codex debe detenerse y solicitar autorización antes de:

- crear o reactivar recursos Azure;
- configurar identidades, roles, OIDC o secretos;
- introducir un servicio con costo no estimado;
- realizar commit, push, abrir un PR o hacer merge;
- ampliar el alcance hacia producción, datos reales o múltiples ambientes.

## Definición de terminado

El Hito 0 se considera cerrado cuando los documentos pasan las validaciones locales, el usuario aprueba las decisiones D01–D10 y el cambio se publica mediante un PR independiente. El merge permanece bajo decisión humana.
