# Runbook de teardown del ambiente `dev`

## Autorización y responsabilidad

Este runbook es un diseño. No autoriza ejecutar comandos. El teardown se realiza fuera de GitHub
Actions por un operador humano, después de confirmar el resource group exacto y recibir aprobación
explícita. Borrar un resource group es destructivo e irreversible para la mayoría de sus recursos.

## Datos que deben registrarse antes del despliegue

| Campo | Valor requerido |
|---|---|
| Subscription ID | ID verificado, no alias ambiguo |
| Resource group | Nombre exacto dedicado solo a Project 24 `dev` |
| Databricks managed resource group | Nombre derivado por el módulo Bicep |
| Inicio de ventana | Fecha y hora UTC |
| Fin máximo | Inicio + 2 horas |
| Operador | Persona responsable de ejecutar y verificar el borrado |
| Evidencia a conservar | Run IDs, deployment name, outputs no sensibles y conteos |

## Checklist previo al borrado

- detener cualquier cluster, warehouse, job o stream de Databricks;
- detener productores y consumidores de Event Hubs;
- exportar solo evidencia sanitizada, nunca tokens ni valores de secretos;
- comprobar que el resource group contiene exclusivamente recursos del Proyecto 24;
- identificar locks y asignaciones que puedan impedir el borrado;
- confirmar una vez más subscription ID y resource group exactos.

## Comandos propuestos

Las variables deben establecerse con valores explícitos y revisados. No usar `~`, `$HOME`, globs ni
nombres inferidos para una operación destructiva.

```bash
az account show --query '{subscription:id,tenant:tenantId,user:user.name}' --output table
az resource list --resource-group '<RESOURCE_GROUP_EXACTO>' \
  --query '[].{name:name,type:type,location:location}' --output table

az group delete --name '<RESOURCE_GROUP_EXACTO>' --yes --no-wait
```

El borrado se envía solo después de leer el inventario. `--no-wait` exige continuar con la
verificación; no significa que los recursos hayan desaparecido.

## Verificación posterior

```bash
az group wait --name '<RESOURCE_GROUP_EXACTO>' --deleted --interval 20 --timeout 1800
az group exists --name '<RESOURCE_GROUP_EXACTO>'
az group exists --name '<DATABRICKS_MANAGED_RESOURCE_GROUP_EXACTO>'
```

Los dos últimos comandos deben devolver `false`. También se revisarán en el portal:

- `Cost analysis` filtrado por tag `project=24`;
- `All resources` sin recursos del prefijo `p24`;
- clusters y SQL warehouses de Databricks sin actividad;
- namespaces de Event Hubs inexistentes;
- alertas de costo sin incremento inesperado durante las 24 horas siguientes.

Key Vault tiene soft delete y purge protection. Después de borrar el resource group puede quedar
como vault eliminado recuperable durante su retención: no debe purgarse para acelerar la
reutilización del nombre. Se documentará ese estado, pero no se considerará un recurso activo.

## Fallos y escalamiento

| Situación | Acción segura |
|---|---|
| Hay recursos ajenos en el grupo | Detenerse; no borrar y pedir revisión |
| Existe un lock | Identificar propietario; no quitarlo sin autorización |
| El grupo sigue en `Deleting` después de 30 min | Consultar operaciones fallidas y soporte; no recrear recursos |
| El managed resource group de Databricks persiste | Verificar estado del workspace y escalar; no forzar borrado ciego |
| El costo continúa creciendo | Localizar el recurso por tag/prefijo y solicitar acción inmediata |

## Evidencia de cierre

Registrar fecha UTC, operador, salida sanitizada de las verificaciones, costo observado y estado de
Key Vault. El Hito 3 no puede declararse cerrado en cloud mientras exista un recurso facturable o
una eliminación sin verificar.
