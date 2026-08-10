# Runbook operativo y de costos

## Objetivo

Ejecutar el Proyecto 23 de forma controlada, preservar evidencia útil y cerrar los recursos con consumo variable. Este runbook no contiene credenciales ni automatiza la creación o eliminación de infraestructura.

## Recursos críticos

| Componente | Nombre | Riesgo operativo principal |
|---|---|---|
| Data Factory | `adf-project23-dev-2026` | Ejecución accidental o repetida |
| Pipeline | `pl_project23_medallion_orchestration` | Reprocesamiento no planificado |
| Databricks | `compute-project23-dev-2026` | DBU/compute activo sin trabajo |
| Azure SQL | `sqldb-project23-serving-dev-2026` | Permanecer online por conexiones activas |
| Cost Management | Alcance `rg-project23-dev` | Desviación del presupuesto |

## Antes de ejecutar

1. Confirmar que la ejecución es necesaria y que existe una ventana de trabajo.
2. Revisar Cost Management en `rg-project23-dev`:
   - costo acumulado;
   - proyección;
   - estado del presupuesto mensual de USD 2;
   - alerta al 50 %.
3. Confirmar que no hay un pipeline ADF en curso.
4. Verificar que los triggers estén desactivados. El JSON local de ejemplo está desactivado, pero no demuestra el estado cloud actual.
5. Confirmar que Azure SQL mantiene:
   - plan serverless gratuito;
   - facturación por encima del límite deshabilitada.
6. Encender `compute-project23-dev-2026` solo al comenzar la ejecución.
7. No copiar usuarios, contraseñas, tokens, endpoints completos o IDs a notebooks, logs o capturas.

## Ejecución controlada

1. Abrir ADF y seleccionar `pl_project23_medallion_orchestration`.
2. Ejecutar manualmente una sola vez.
3. Supervisar el orden:
   - `nb_01_landing_to_bronze`;
   - `nb_02_bronze_to_silver`;
   - `nb_03_silver_to_gold`.
4. No iniciar una segunda ejecución mientras la primera esté activa.
5. Si falla una actividad:
   - conservar el nombre de la actividad, timestamp y mensaje técnico sanitizado;
   - revisar la causa antes de reintentar;
   - preferir la reejecución desde el punto soportado por ADF;
   - no publicar capturas con run IDs.
6. Para Gold → Azure SQL:
   - comprobar el preflight antes de conectar;
   - verificar que se esperan siete tablas y 953 filas para los fixtures actuales;
   - confirmar el resultado `LOADED` o `NO_OP`;
   - no sustituir valores de Key Vault por credenciales hardcodeadas.

## Quality gates de cierre

| Gate | Criterio de aprobación |
|---|---|
| ADF | Pipeline `Correcto`; 3/3 actividades correctas |
| Gold | Quality gates y reconciliación aprobados |
| Azure SQL | 7 tablas; 953 filas para el dataset actual |
| Integridad | PK/FK 7/7; 0 huérfanos |
| Idempotencia | Segunda ejecución `NO_OP`; conteos sin cambios |
| Power BI | 8 transacciones; 4 clientes; 6 cuentas; canales 3/2/2/1 |
| Seguridad | Sin secretos o IDs sensibles en artefactos públicos |

Los conteos son expectativas del fixture actual. Si cambia el contrato de datos, deben actualizarse mediante un cambio versionado y no ignorarse como una falsa alarma.

## Cierre obligatorio

1. Verificar en ADF Monitor el estado final de cada actividad.
2. Confirmar que no quedan ejecuciones en curso o en reintento.
3. Terminar `compute-project23-dev-2026`.
4. Confirmar en la lista de cómputo:
   - memoria activa: `-`;
   - núcleos activos: `-`;
   - DBU/h activo: `-`.
5. Cerrar conexiones que mantengan Azure SQL activa.
6. Esperar la pausa automática serverless y comprobar el estado `Paused`.
7. Volver a revisar Cost Management dentro de la ventana de actualización del servicio.
8. Registrar solo métricas y evidencia sanitizada.

## Controles de costo

| Control | Configuración confirmada | Acción operativa |
|---|---|---|
| Autoapagado Databricks | 10 minutos | Mantener habilitado; detener manualmente al finalizar |
| Azure SQL | Serverless gratuito | Verificar `Paused` después de cada uso |
| Exceso SQL | Deshabilitado | No habilitar sin decisión explícita |
| Presupuesto | USD 2 mensual | Mantener activo |
| Alerta | 50 % / USD 1 | Investigar antes de otra ejecución |
| Triggers ADF | Ejemplo local desactivado | Verificar estado cloud antes y después |

Valores de referencia del cierre:

- costo observado: USD 0,04;
- proyección observada: USD 0,29.

Son una fotografía histórica, no una garantía de precio futuro.

## Respuesta ante alerta

Si el gasto alcanza el 50 % del presupuesto:

1. No iniciar nuevas ejecuciones.
2. Confirmar que Databricks está detenido.
3. Confirmar que Azure SQL está pausada.
4. Revisar ejecuciones ADF y triggers.
5. Agrupar costos por servicio y recurso dentro de `rg-project23-dev`.
6. Determinar si el consumo corresponde a Storage, ADF, Key Vault, SQL u otro recurso.
7. Reanudar solo cuando la causa esté explicada y el impacto sea aceptable.

## Evidencia pública

Antes de incorporar una captura:

- mantener el original fuera del repositorio público;
- trabajar sobre una copia cuando requiera recorte u ocultamiento;
- eliminar subscription ID, tenant ID, run IDs, resource IDs, client/object IDs, correos, usuarios, contraseñas, tokens y endpoints completos;
- comprobar el resultado visualmente y mediante OCR;
- registrar el archivo en [evidence_catalog.md](evidence_catalog.md);
- no reconstruir una evidencia ausente.

## Estado esperado después del cierre

| Recurso | Estado esperado |
|---|---|
| ADF pipeline | Finalizado; sin ejecución pendiente |
| ADF triggers | Desactivados salvo prueba planificada |
| Databricks compute | Detenido / `Terminated` |
| Azure SQL | `Paused` |
| Facturación SQL excedente | Deshabilitada |
| Presupuesto y alerta | Activos |
