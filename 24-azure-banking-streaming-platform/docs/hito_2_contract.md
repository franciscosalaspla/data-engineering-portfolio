# Contrato del Hito 2 — Infraestructura como código

## Objetivo

Representar el ambiente efímero `dev` del Proyecto 24 mediante Bicep modular, con nombres
deterministas, parámetros seguros y validación estática reproducible. Este hito no inicia sesión en
Azure ni despliega recursos.

## Inventario representado

| Módulo | Recurso principal | Configuración del MVP |
|---|---|---|
| `storage.bicep` | ADLS Gen2 | `Standard_LRS`, HNS, OAuth por defecto y seis contenedores privados |
| `event-hubs.bicep` | Event Hubs Standard | Un hub `transactions-v1`, dos particiones y consumer group de Databricks |
| `data-factory.bicep` | Azure Data Factory | Identidad administrada para batch y backfills futuros |
| `databricks.bicep` | Azure Databricks | SKU Standard y nodos sin IP pública |
| `sql.bicep` | Azure SQL | Base serverless, autopausa y administración exclusiva mediante Microsoft Entra |
| `key-vault.bicep` | Azure Key Vault | RBAC, soft delete y purge protection; no contiene secretos en este hito |
| `monitoring.bicep` | Log Analytics | Workspace base con 30 días de retención; alertas reservadas para el Hito 7 |

Power BI no forma parte del despliegue ARM. Los notebooks, pipelines, esquemas y objetos de datos
se incorporarán en sus hitos funcionales correspondientes.

## Decisiones del hito

| ID | Decisión | Justificación |
|---|---|---|
| H2-D01 | Mantener módulos locales bajo `infra/modules` | La compilación no depende de un registro ni de autenticación Azure |
| H2-D02 | Usar un único punto de entrada a nivel de resource group | Simplifica `what-if`, despliegue y teardown del ambiente `dev` |
| H2-D03 | Derivar un sufijo estable con `uniqueString` | Cumple unicidad global sin almacenar identificadores personales |
| H2-D04 | Exponer únicamente nombres e IDs de recursos | Los outputs son operativos y no contienen claves ni connection strings |
| H2-D05 | Preferir identidad y Microsoft Entra | Shared keys y autenticación SQL local permanecen deshabilitadas |
| H2-D06 | Mantener endpoints públicos en el MVP | La red privada empresarial está fuera de alcance; el acceso se cerrará con RBAC |
| H2-D07 | Tratar los IDs SQL del archivo `dev` como marcadores | Permiten compilación estática, pero bloquean un despliegue accidental válido |
| H2-D08 | Fijar Bicep CLI y verificar SHA-256 en CI | Evita descargar una versión mutable o ejecutar un binario sin verificar |
| H2-D09 | Ejecutar Bicep con `--no-restore` | Garantiza que lint y compilación no contacten Azure ni registros externos |

## Criterios de aceptación

- [x] `main.bicep` compila y resuelve los siete módulos locales.
- [x] `dev.bicepparam` compila contra el punto de entrada.
- [x] El linter configurado no produce advertencias ni errores.
- [x] El workflow fija Bicep 0.46.1 y el SHA-256 publicado para Linux x64.
- [x] CI conserva `contents: read`, no solicita `id-token: write` y no usa secretos.
- [x] No existen contraseñas, tokens, connection strings, claves compartidas ni PII.
- [x] Los nombres, tags, parámetros y outputs están documentados.
- [x] El Proyecto 23 y los demás proyectos permanecen intactos.
- [x] No se inicia sesión en Azure, no se ejecuta `what-if` y no se despliegan recursos.
- [ ] El workflow finaliza en verde dentro del PR del Hito 2.

## Evidencia y clasificación

| Evidencia | Clasificación | Estado antes del PR |
|---|---|---|
| Ruff, yamllint, pytest y validador integrado | Local | Verificado localmente |
| Bicep lint, build y build-params | Local sin Azure | Verificado con Bicep 0.46.1 |
| GitHub Actions | Remota sin Azure | Pendiente de publicación |
| `what-if`, OIDC y RBAC | Cloud | Reservado para el Hito 3 |
| Recursos Azure | Cloud | No creados ni reactivados |

## Exclusiones explícitas

- Creación del resource group o de recursos Azure.
- OIDC, GitHub Environment, identidades federadas y asignaciones RBAC.
- Valores reales de tenant, suscripción o identidades administrativas.
- Secretos, linked services, pipelines de ADF, clusters o jobs de Databricks.
- Diagnósticos por recurso, consultas, dashboards y alertas.
- Estimación final de costo y procedimiento ejecutado de teardown.

Los controles de identidad, `what-if`, costo y despliegue manual se cerrarán en el Hito 3 y
requerirán una aprobación independiente.

## Definición de terminado

El Hito 2 queda listo para publicación cuando todas las validaciones locales son verdes, el diff no
sale del Proyecto 24 salvo por su workflow dedicado, y el usuario aprueba expresamente el commit,
push y PR. El merge continúa siendo manual.
