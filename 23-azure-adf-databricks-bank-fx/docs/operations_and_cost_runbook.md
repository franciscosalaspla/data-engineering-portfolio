# Runbook operativo y de costos

Guía breve para **validar la arquitectura Medallion, ejecutar la orquestación y cerrar los recursos** sin dejar consumo variable activo. No contiene credenciales ni crea o elimina infraestructura.

## Hitos 1–3 — Validar antes de orquestar

### 1.1 Contratos y fuentes

Confirmar que los contratos, schemas y fixtures estén versionados y que Landing contenga las fuentes esperadas.

### 2.1 Calidad Silver

Confirmar tipificación, dominios, relaciones, deduplicación y cuarentena antes de promover datos.

### 3.1 Quality Gate Gold

Confirmar el modelo estrella, la conversión FX, el grano y la reconciliación antes de ejecutar la publicación cloud.

## Recursos que se deben controlar

| Hito | Componente | Referencia | Riesgo principal |
|---:|---|---|---|
| 4 | Data Factory | Instancia del proyecto | Ejecución accidental o repetida |
| 4 | Pipeline | `pl_project23_medallion_orchestration` | Reprocesamiento no planificado |
| 4 | Databricks compute | Compute de desarrollo | DBU activo sin trabajo |
| 5 | Azure SQL | Base de serving | Base online por conexiones activas |
| 7 | Cost Management | Grupo de recursos del proyecto | Desviación del presupuesto |

## Hito 4 — Ejecutar la arquitectura Medallion

### 4.1 Preflight

Antes de iniciar:

1. Confirmar que la ejecución es necesaria y que no existe otra en curso.
2. Revisar en el grupo de recursos del proyecto el costo, la proyección y la alerta.
3. Verificar que los triggers ADF estén desactivados.
4. Encender el compute de Databricks solo al comenzar.
5. No copiar usuarios, contraseñas, tokens, endpoints o IDs a notebooks o capturas.

El trigger local desactivado no demuestra el estado cloud actual; este debe comprobarse en ADF.

### 4.2 Ejecución

1. Abrir `pl_project23_medallion_orchestration`.
2. Iniciar una sola ejecución manual.
3. Supervisar este orden:
   - `nb_01_landing_to_bronze`;
   - `nb_02_bronze_to_silver`;
   - `nb_03_silver_to_gold`.
4. No iniciar otra ejecución mientras la primera esté activa.

### 4.3 Si una actividad falla

1. Registrar el nombre de la actividad, la hora y el mensaje sanitizado.
2. Revisar la causa antes de reintentar.
3. Reejecutar desde el punto soportado por ADF.
4. No publicar capturas con run IDs u otros identificadores.

### 4.4 Validación

| Control | Criterio de aprobación |
|---|---|
| ADF pipeline | Estado `Correcto` |
| Actividades | 3/3 correctas |
| Orden | Bronze → Silver → Gold |
| Databricks | Quality gates y reconciliación aprobados |

## Hito 5 — Publicar Gold en Azure SQL

### 5.1 Preflight

1. Confirmar que Azure SQL mantiene el plan serverless gratuito.
2. Confirmar que la facturación sobre el límite está deshabilitada.
3. Ejecutar el preflight Gold antes de abrir la conexión JDBC.
4. Verificar que el dataset actual espera siete tablas y 953 filas.
5. Mantener las credenciales en Key Vault y Secret Scope.

### 5.2 Publicación

1. Ejecutar `04_gold_to_azure_sql`.
2. Confirmar `LOADED` en una carga nueva o `NO_OP` si no existen cambios.
3. No reemplazar los secretos por credenciales escritas en el notebook.

### 5.3 Quality gates

| Gate | Criterio de aprobación |
|---|---|
| Serving | 7 tablas; 953 filas para el fixture actual |
| Integridad | PK/FK 7/7 |
| Huérfanos | 0 |
| Reconciliación | Gold → SQL `PASSED` |
| Idempotencia | Segunda ejecución `NO_OP` |
| Conteos | 953 → 953 |
| Escrituras | 0 en la segunda ejecución |

Si cambia el contrato de datos, los conteos deben actualizarse mediante un cambio versionado; no deben ignorarse como una falsa alarma.

## Hito 6 — Validar Power BI

### 6.1 Modelo

1. Confirmar siete tablas.
2. Confirmar seis relaciones activas hacia `fact_transaction`.
3. Verificar que no exista una segunda tabla de hechos.

### 6.2 Resultados

| Indicador | Valor esperado para el fixture actual |
|---|---:|
| Transacciones | 8 |
| Clientes únicos | 4 |
| Cuentas únicas | 6 |
| Canales Card/Mobile/Online/ATM | 3/2/2/1 |

### 6.3 Seguridad

Antes de publicar o documentar, comprobar que el informe no exponga usuarios, endpoints, IDs ni credenciales.

## Hito 7 — Cerrar y controlar costos

### 7.1 Cierre técnico

1. Verificar en ADF Monitor que no existan ejecuciones pendientes o en reintento.
2. Terminar el compute de Databricks.
3. Confirmar memoria, núcleos y DBU activos en `-`.
4. Cerrar conexiones que mantengan Azure SQL activa.
5. Esperar la pausa automática y comprobar `Paused`.
6. Revisar nuevamente los triggers ADF.

### 7.2 Controles permanentes

| Control | Configuración confirmada | Acción |
|---|---|---|
| Databricks | Autoapagado de 10 minutos | Detener manualmente al finalizar |
| Azure SQL | Serverless gratuito | Verificar `Paused` |
| Exceso SQL | Deshabilitado | No habilitar sin decisión explícita |
| Presupuesto | USD 2 mensual | Mantener activo |
| Alerta | 50 % / USD 1 | Investigar antes de otra ejecución |
| Triggers ADF | Ejemplo local desactivado | Verificar el estado cloud |

Valores históricos del cierre:

- costo observado: USD 0,04;
- proyección observada: USD 0,29.

Estos valores son una fotografía del proyecto, no una garantía de precio futuro.

### 7.3 Respuesta ante una alerta

1. No iniciar nuevas ejecuciones.
2. Confirmar que Databricks esté detenido.
3. Confirmar que Azure SQL esté pausada.
4. Revisar ejecuciones y triggers de ADF.
5. Agrupar costos por servicio dentro del grupo de recursos del proyecto.
6. Identificar el recurso responsable.
7. Reanudar solo cuando la causa esté explicada.

### 7.4 Estado final esperado

| Recurso | Estado esperado |
|---|---|
| ADF pipeline | Finalizado; sin ejecución pendiente |
| ADF triggers | Desactivados salvo prueba planificada |
| Databricks compute | `Terminated` |
| Azure SQL | `Paused` |
| Facturación SQL excedente | Deshabilitada |
| Presupuesto y alerta | Activos |

## Regla para evidencias públicas

Mantener los originales fuera del repositorio. Antes de publicar una copia, eliminar subscription ID, tenant ID, run IDs, resource IDs, client/object IDs, correos, usuarios, contraseñas, tokens y endpoints completos. Validar visualmente y mediante OCR, registrar el resultado en [evidence_catalog.md](evidence_catalog.md) y nunca reconstruir una evidencia ausente.
