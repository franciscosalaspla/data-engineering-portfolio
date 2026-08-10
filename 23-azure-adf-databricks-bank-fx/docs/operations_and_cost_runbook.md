# Runbook operativo y de costos

## Propósito

Ejecutar el pipeline de forma controlada, validar sus resultados y detener los recursos con consumo variable. No contiene credenciales ni automatiza la creación o eliminación de infraestructura.

## Cobertura

| Etapa | Control operativo |
|---|---|
| Landing → Bronze | Fuentes disponibles, checksum y trazabilidad |
| Bronze → Silver | Quality gates y cuarentena |
| Silver → Gold | Reconciliación, grano e idempotencia |
| ADF | Orden, dependencias y estado de actividades |
| Azure SQL | Conteos, integridad y segunda publicación `NO_OP` |
| Power BI | Relaciones y KPI esperados |
| Cierre | Cómputo detenido, SQL pausado y costos revisados |

## Antes de ejecutar

1. Confirmar que no exista otra ejecución ADF en curso.
2. Revisar que los triggers estén desactivados, salvo una prueba programada.
3. Consultar costo acumulado, proyección, presupuesto de USD 2 y alerta al 50 %.
4. Verificar que Azure SQL mantenga serverless y el exceso gratuito deshabilitado.
5. Encender Databricks compute solo al comenzar el trabajo.
6. Confirmar que no se copiarán credenciales, correos, IDs ni endpoints completos en notebooks, logs o capturas.

## Ejecución

### Pipeline Medallion

1. Abrir ADF y ejecutar una sola vez `pl_project23_medallion_orchestration`.
2. Supervisar el orden:
   - `nb_01_landing_to_bronze`;
   - `nb_02_bronze_to_silver`;
   - `nb_03_silver_to_gold`.
3. No iniciar otra ejecución mientras la primera esté activa.
4. Confirmar que cada quality gate apruebe antes de avanzar.

### Gold → Azure SQL

1. Ejecutar el preflight: siete tablas y 953 filas esperadas para el dataset actual.
2. Conectar mediante JDBC usando Key Vault y Secret Scope.
3. Confirmar `LOADED` en la primera publicación o `NO_OP` cuando no existan cambios.
4. Validar PK/FK, huérfanos, reconciliación y conteos.

### Power BI

1. Comprobar siete tablas y seis relaciones activas.
2. Validar 8 transacciones, 4 clientes y 6 cuentas con transacciones.
3. Confirmar la distribución Card 3, Mobile 2, Online 2 y ATM 1.

Los conteos corresponden al dataset actual. Si cambia el contrato, deben actualizarse mediante un cambio versionado.

## Quality gates de cierre

| Control | Criterio de aprobación |
|---|---|
| ADF | Pipeline `Correcto`; 3/3 actividades correctas |
| Gold | Grano, claves, FX y reconciliación aprobados |
| Azure SQL | 7 tablas y 953 filas |
| Integridad | PK/FK 7/7; 0 huérfanos |
| Idempotencia | Segunda publicación `NO_OP`; 953 → 953; 0 escrituras |
| Power BI | Modelo y KPI coinciden con el dataset |
| Seguridad | Sin secretos ni identificadores sensibles en artefactos públicos |

## Si una ejecución falla

1. Registrar actividad, timestamp y mensaje técnico sanitizado.
2. Identificar la causa antes de reintentar.
3. Reejecutar desde el punto soportado por ADF.
4. No publicar capturas con run IDs, cuentas o endpoints.
5. No sustituir Key Vault por credenciales escritas en el código.

## Cierre obligatorio

1. Confirmar en ADF Monitor que no queden actividades en curso o reintento.
2. Detener Databricks compute y verificar que no muestre memoria, núcleos ni DBU activos.
3. Cerrar las conexiones que mantengan Azure SQL activa.
4. Esperar y comprobar el estado `Paused` de Azure SQL.
5. Revisar Cost Management dentro de su ventana de actualización.
6. Registrar únicamente métricas y evidencias sanitizadas.

## Controles de costo

| Control | Configuración | Acción esperada |
|---|---|---|
| Databricks | Autoapagado de 10 minutos | Detener manualmente al finalizar |
| Azure SQL | Serverless gratuito | Comprobar `Paused` después del uso |
| Exceso SQL | Deshabilitado | No habilitar sin decisión explícita |
| Presupuesto | USD 2 mensual | Mantener activo |
| Alerta | 50 % / USD 1 | Investigar antes de otra ejecución |
| ADF triggers | Desactivados por defecto | Verificar antes y después |

Valores históricos del cierre: **USD 0,04 observados** y **USD 0,29 proyectados**. No representan una garantía de precio futuro.

## Respuesta ante una alerta

1. No iniciar nuevas ejecuciones.
2. Confirmar que Databricks esté detenido y Azure SQL pausada.
3. Revisar ejecuciones y triggers de ADF.
4. Agrupar costos por servicio y recurso.
5. Reanudar solo cuando la causa y el impacto estén explicados.

## Estado esperado

| Recurso | Estado después del cierre |
|---|---|
| ADF | Sin ejecuciones pendientes |
| Triggers | Desactivados salvo prueba planificada |
| Databricks compute | `Terminated` |
| Azure SQL | `Paused` |
| Exceso SQL | Deshabilitado |
| Presupuesto y alerta | Activos |
