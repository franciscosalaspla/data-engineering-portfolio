# Contrato del Hito 3 — Despliegue seguro

## Objetivo

Preparar un despliegue manual, auditable y sin secretos persistentes para el ambiente efímero
`dev`. La preparación local cubre OIDC, mínimo privilegio, `what-if`, costos y teardown; no crea
identidades, no asigna roles y no ejecuta operaciones contra Azure.

## Flujo aprobado para diseño

1. Una persona con privilegios crea previamente el resource group y la identidad federada.
2. GitHub obtiene un token OIDC de corta duración para el Environment `dev`.
3. Una ejecución manual `what-if` valida permisos y muestra el cambio propuesto sin modificar
   recursos.
4. Una persona revisa el log, registra el run ID y solicita una aprobación Azure independiente.
5. Otra ejecución manual puede desplegar únicamente con el run ID revisado y la confirmación
   exacta `DEPLOY-P24-DEV`.
6. La misma sesión recoge evidencia y ejecuta el teardown aprobado por un operador humano.

El paso 5 no está autorizado en esta fase. El workflow se valida solo como código local.

## Decisiones

| ID | Decisión | Justificación |
|---|---|---|
| H3-D01 | Usar `workflow_dispatch` sin disparadores automáticos | Evita desplegar por `push` o por un PR |
| H3-D02 | Federar únicamente el subject del Environment `dev` | Vincula el token al repositorio y entorno esperados |
| H3-D03 | Guardar IDs no sensibles como variables del Environment | No se crean client secrets ni credenciales de larga duración |
| H3-D04 | Ejecutar `what-if` con validación `Provider` | Comprueba configuración y permisos reales antes del despliegue |
| H3-D05 | Usar modo ARM `Incremental` | Evita eliminaciones implícitas por recursos ausentes de la plantilla |
| H3-D06 | Separar el run revisado del run de despliegue | Deja una referencia de aprobación legible en el historial |
| H3-D07 | Limitar la identidad de CD al resource group `dev` | Reduce el radio de impacto y excluye asignaciones RBAC |
| H3-D08 | Mantener RBAC de datos fuera de la identidad de CD | Separa control plane, acceso a datos y bootstrap privilegiado |
| H3-D09 | Fijar las acciones de terceros por SHA completo | Reduce el riesgo de ejecutar una etiqueta mutable |
| H3-D10 | Dejar el borrado fuera del workflow | El teardown exige una aprobación y un operador humano independientes |

## Criterios de aceptación de la preparación local

- [x] El workflow solo expone `workflow_dispatch`.
- [x] Solicita únicamente `contents: read` e `id-token: write`.
- [x] `actions/checkout` y `azure/login` están fijadas por SHA completo.
- [x] El Environment es `dev` y el despliegue exige dos confirmaciones explícitas.
- [x] `what-if` usa `Provider`, modo `Incremental` y Azure CLI 2.76.0 o superior.
- [x] No se usan `secrets.*`, contraseñas, connection strings ni shared keys.
- [x] El workflow no crea resource groups, federaciones, roles ni secretos y no contiene comandos
  de borrado.
- [x] La matriz RBAC separa bootstrap, despliegue y data plane.
- [x] El costo se estima para una ventana limitada y el teardown incluye verificaciones posteriores.
- [x] CI sigue funcionando sin credenciales Azure y revisa también el workflow de CD.
- [x] El Proyecto 23 y los cambios ajenos permanecen intactos.

## Evidencia y límites

| Evidencia | Clasificación | Estado |
|---|---|---|
| Ruff, yamllint, pytest y validadores | Local | Requerida antes de publicar |
| Bicep lint y compilación | Local sin Azure | Requerida antes de publicar |
| Sintaxis y controles del workflow CD | Local estática | Cubierta por el validador del repositorio |
| GitHub Environment e identidad federada | Cloud | No configurados ni autorizados |
| `what-if` real | Cloud sin cambios de recursos | No ejecutado ni autorizado todavía |
| Despliegue y teardown | Cloud con costo | No ejecutados ni autorizados todavía |

## Definición de terminado

La fase local queda lista para publicación cuando las validaciones son verdes y el usuario aprueba
por separado commit, push y PR. Completar el Hito 3 en cloud requerirá después dos aprobaciones:
primero para configurar OIDC/RBAC y ejecutar `what-if`; luego para desplegar temporalmente según la
estimación y el teardown revisados. No habrá merge automático.
