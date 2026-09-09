# Diseño de despliegue seguro

## Fronteras de confianza

| Componente | Puede hacer | No puede hacer |
|---|---|---|
| CI del Proyecto 24 | Lint, tests, Bicep offline y controles estáticos | Solicitar token OIDC o contactar Azure |
| Workflow CD | `what-if` y despliegue incremental manual en el resource group `dev` | Asignar RBAC; no contiene comandos de teardown |
| Administrador de bootstrap | Crear resource group, identidad, federación y roles | Participar en ejecuciones ordinarias |
| Identidades de workload | Leer o escribir solo los datos necesarios | Modificar infraestructura o RBAC |
| Operador de teardown | Eliminar el ambiente después de aprobación | Actuar desde el workflow de CD |

## Contrato OIDC

Se propone una app de Microsoft Entra con service principal dedicado a Project 24. No tendrá client
secret. Su credencial federada debe aceptar exclusivamente:

| Campo | Valor esperado |
|---|---|
| Issuer | `https://token.actions.githubusercontent.com` |
| Audience | `api://AzureADTokenExchange` |
| Subject | `repo:franciscosalaspla/data-engineering-portfolio:environment:dev` |

El Environment de GitHub `dev` debe permitir despliegues solo desde `main` y tener protección por
revisor antes de habilitar la operación `deploy`. La persona que configure Azure registrará estos
identificadores no sensibles como variables del Environment:

- `AZURE_CLIENT_ID`;
- `AZURE_TENANT_ID`;
- `AZURE_SUBSCRIPTION_ID`;
- `AZURE_RESOURCE_GROUP`;
- `SQL_ENTRA_ADMIN_LOGIN`;
- `SQL_ENTRA_ADMIN_OBJECT_ID`.

Los IDs no son contraseñas, pero se mantienen fuera del repositorio para evitar acoplarlo a una
suscripción. No se crearán `AZURE_CREDENTIALS`, client secrets ni service principal passwords.

## Matriz RBAC propuesta

Las asignaciones se harán únicamente después de aprobación y nunca desde la identidad de CD.

| Principal | Rol | Scope mínimo | Momento |
|---|---|---|---|
| Identidad OIDC de GitHub | `Contributor` | Solo resource group `dev` | Bootstrap de Hito 3 |
| Data Factory managed identity | `Storage Blob Data Contributor` | Storage account de Project 24 | Hito 4 |
| Identidad de procesamiento | `Storage Blob Data Contributor` | Storage account de Project 24 | Hito 5 |
| Productor sintético | `Azure Event Hubs Data Sender` | Event Hub `transactions-v1` | Hito 4 |
| Identidad de procesamiento | `Azure Event Hubs Data Receiver` | Event Hub `transactions-v1` | Hito 5 |
| Identidad que necesite un secreto | `Key Vault Secrets User` | Key Vault de Project 24 | Solo si aparece el caso de uso |
| Persona o grupo SQL administrador | Administración Microsoft Entra | Servidor SQL de Project 24 | Bootstrap de Hito 3 |

IDs estables de los roles de datos:

| Rol | Role definition ID |
|---|---|
| Contributor | `b24988ac-6180-42a0-ab88-20f7382dd24c` |
| Storage Blob Data Contributor | `ba92f5b4-2d11-453d-a403-e96b0029c9fe` |
| Azure Event Hubs Data Sender | `2b629674-e913-4c01-ae53-ef4638d8f975` |
| Azure Event Hubs Data Receiver | `a638d3c7-ab3a-418d-83e6-5f17a39d4fde` |
| Key Vault Secrets User | `4633458b-17de-408a-b874-0445c86b69e6` |

`Contributor` permite administrar y borrar recursos dentro del scope, aunque no asignar roles ni
leer automáticamente el data plane. El MVP reduce ese riesgo con scope exclusivo, Environment
protegido, workflow sin comandos de borrado y teardown humano. Antes de producción se reemplazaría
por un rol personalizado limitado a los resource providers realmente usados.

## Operación del workflow

### 1. Plan

Ejecutar `Project 24 CD` con `operation=what-if`. El job comprueba variables, versión de Azure CLI,
existencia del resource group y permisos de proveedor. `what-if` no modifica recursos.

La revisión humana debe confirmar:

- suscripción y resource group correctos;
- solo recursos y nombres de Project 24;
- ningún cambio `Delete` inesperado;
- SKU, región y tags esperados;
- parámetros SQL correspondientes a una identidad verificada;
- estimación de costos aún vigente.

### 2. Despliegue

Después de la aprobación Azure independiente, ejecutar de nuevo el workflow con:

- `operation=deploy`;
- `approved_what_if_run_id=<ID numérico del run revisado>`;
- `confirmation=DEPLOY-P24-DEV`.

El job `plan` vuelve a calcular `what-if` para detectar deriva. El job `deploy` solo comienza si el
plan termina correctamente y las dos confirmaciones coinciden. El modo `Incremental` no elimina
recursos omitidos de la plantilla.

## Bootstrap futuro, no ejecutado

Cuando exista autorización, un administrador deberá:

1. comprobar suscripción, región, cuotas y nombres;
2. crear el resource group `dev` con tags de Project 24;
3. crear la app/service principal sin secreto y su credencial federada exacta;
4. asignar `Contributor` únicamente al resource group;
5. crear y proteger el Environment `dev`, limitado a `main`;
6. registrar las seis variables no sensibles;
7. ejecutar solo `what-if` y devolver su evidencia para revisión.

Estas instrucciones describen el orden; no conceden autorización para ejecutarlo.

## Referencias oficiales

- [Azure Login con OIDC](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect)
- [Desplegar Bicep con GitHub Actions](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/deploy-github-actions)
- [Endurecer despliegues OIDC en Azure](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure)
- [Roles integrados de Azure](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles)
- [Acceso a blobs mediante Azure RBAC](https://learn.microsoft.com/en-us/azure/storage/blobs/assign-azure-role-data-access)
