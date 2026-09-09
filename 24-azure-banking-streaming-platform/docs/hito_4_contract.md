# Contrato del Hito 4 — Ingesta de eventos

## Objetivo

Definir y probar la ingesta de transacciones bancarias completamente sintéticas. La fase local
valida el contrato, la serialización, la partición y los conteos sin conectarse a Azure.

## Alcance local

- JSON Schema `transaction-event-v1`;
- productor determinista que publica solo eventos válidos;
- clave de partición `account_id`;
- Event Hub simulado en memoria;
- consumidor que decodifica y vuelve a validar cada mensaje;
- evidencia de rechazos sin conservar el payload original;
- reconciliación de eventos publicados, recibidos y aceptados.

## Decisiones

| ID | Decisión | Motivo |
|---|---|---|
| H4-D01 | Fijar `event_version` en `1` | Permite evolucionar el contrato sin cambios silenciosos |
| H4-D02 | Usar `account_id` como clave de partición | Conserva el orden relativo de una cuenta |
| H4-D03 | Serializar JSON canónico | Hace reproducibles las pruebas y comparaciones |
| H4-D04 | Validar antes de publicar y después de consumir | Protege ambos límites de la ingesta |
| H4-D05 | No deduplicar en el productor | Mantiene explícita la entrega al menos una vez; Hito 5 deduplicará |
| H4-D06 | Simular el transporte durante la fase local | Evita credenciales, costos y afirmaciones cloud sin evidencia |
| H4-D07 | No guardar payloads rechazados en logs | Reduce exposición accidental de datos |

## Criterios locales de aceptación

- [x] El esquema v1 exige los nueve campos y rechaza campos adicionales.
- [x] Los eventos válidos se serializan de forma determinista.
- [x] La clave de partición coincide con `account_id`.
- [x] Los tres eventos inválidos no se publican.
- [x] Tres eventos válidos producen tres publicados, recibidos y aceptados.
- [x] El validador confirma cinco eventos únicos en los fixtures de replay.
- [x] Las pruebas y el lint se ejecutan sin Azure.
- [x] El Proyecto 23 y los cambios ajenos permanecen intactos.

## Pendiente cloud

- desplegar el Event Hub ya representado en Bicep;
- configurar identidades separadas de envío y lectura;
- conectar el productor y un consumidor real;
- reconciliar los conteos de extremo a extremo;
- recopilar evidencia sanitizada y ejecutar teardown.

Estas acciones requieren autorización expresa. Este hito local no configura OIDC, RBAC, identidades
ni recursos Azure.

## Definición de terminado local

El Hito 4 queda listo para revisión cuando el código, los fixtures, el contrato y la documentación
superan la suite local. Commit, push y PR requieren una aprobación posterior; la validación cloud
continúa pendiente.
