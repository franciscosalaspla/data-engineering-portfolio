# Estimación y controles de costo del ambiente `dev`

## Alcance de la estimación

Estimación de catálogo público en USD para `eastus2`, consultada el 9 de septiembre de 2026. No
incluye impuestos, contrato, créditos ni descuentos de la suscripción. Antes de cada despliegue se
debe actualizar con Azure Pricing Calculator y comprobar la oferta efectiva de la cuenta.

`what-if` no crea recursos y no inicia este consumo. La estimación empieza únicamente después de un
despliegue correcto.

## Drivers del Hito 3

| Recurso | Configuración | Driver de costo durante la prueba |
|---|---|---|
| Event Hubs | Standard, 1 TU, endpoint Kafka | USD 0.03/TU-h + USD 0.09/Kafka-h + USD 0.028/millón de eventos |
| Azure SQL | General Purpose serverless, máximo 1 vCore, autopausa 60 min | Hasta USD 0.521758/vCore-h mientras está activo; almacenamiento aparte |
| Databricks | Workspace Standard sin cluster | Sin DBU ni VM en Hito 3; el compute futuro se cobra por separado |
| ADLS Gen2 | Standard LRS, datos sintéticos mínimos | GB-mes, transacciones y recuperación, prorrateados |
| Data Factory | Factory sin pipelines ejecutados | Sin actividad facturable en Hito 3 |
| Log Analytics | Workspace, 30 días, sin diagnósticos conectados | Ingesta; los primeros 5 GB/mes por billing account pueden estar incluidos |
| Key Vault | Standard y vacío | Operaciones; no se crean secretos en Hito 3 |

La base SQL se configura para pausar después de 60 minutos sin actividad. Event Hubs no se pausa:
sigue cobrando por hora hasta eliminar el namespace, por lo que determina la urgencia del teardown.

## Ventana y reserva recomendadas

| Escenario | Supuesto | Reserva conservadora |
|---|---|---:|
| Solo `what-if` | Sin recursos creados | USD 0 de infraestructura nueva |
| Prueba Hito 3 | Desplegar, verificar y borrar en máximo 2 horas; sin cluster Databricks | USD 2 |
| Ambiente olvidado 24 horas | Event Hubs activo; SQL se autopausa; sin compute Databricks | USD 5 |

Las reservas son límites operativos redondeados, no cotizaciones. La prueba de dos horas considera
aproximadamente USD 0.24 de Event Hubs, hasta USD 1.04 de compute SQL y margen para almacenamiento,
backup y operaciones. Lo no consumido no se convierte en un cargo mínimo del proyecto.

## Controles previos obligatorios

- aprobación explícita del costo y del teardown en la misma conversación de trabajo;
- alerta presupuestaria de USD 5 para Project 24; una alerta avisa, no bloquea gasto;
- ventana máxima de dos horas registrada antes de desplegar;
- ninguna creación de cluster Databricks en el Hito 3;
- datos y logs sintéticos de tamaño mínimo;
- operador de teardown disponible antes de iniciar;
- revisión de `Cost analysis` y de los recursos existentes antes y después de la prueba.

## Fórmulas para recalcular

```text
Event Hubs = horas × (TU × tarifa_TU + tarifa_endpoint_Kafka)
             + millones_eventos × tarifa_ingreso

Azure SQL compute <= horas_activas × 1 vCore × tarifa_vCore_hora

Databricks futuro = horas × (DBU_hora × tarifa_DBU + tarifa_VM_hora)

Total = Event Hubs + SQL compute + SQL storage + ADLS + ADF + Monitor + Key Vault
```

## Fuentes oficiales

- [Azure Retail Prices API](https://prices.azure.com/api/retail/prices)
- [Precios de Event Hubs](https://azure.microsoft.com/en-us/pricing/details/event-hubs/)
- [Precios de Azure SQL Database](https://azure.microsoft.com/en-us/pricing/details/azure-sql-database/single/)
- [Precios de Azure Databricks](https://azure.microsoft.com/en-us/pricing/details/databricks/)
- [Precios de Azure Monitor](https://azure.microsoft.com/en-us/pricing/details/monitor/)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
