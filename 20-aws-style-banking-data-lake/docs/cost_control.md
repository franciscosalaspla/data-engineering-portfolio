# Cost Control

Este documento explica el control conceptual de costos para migrar este proyecto a AWS. La ejecucion actual es local y no genera costos cloud.

## Por que Parquet reduce datos escaneados

Parquet es un formato columnar. En motores como Athena, una consulta que selecciona pocas columnas puede leer solo una parte del dataset en vez de escanear filas completas como ocurriria con CSV.

Beneficios principales:

- lectura columnar;
- compresion eficiente;
- metadata de tipos;
- mejor compatibilidad con particionamiento analitico.

En datasets muy pequenos, Parquet puede ocupar mas bytes que CSV por overhead de metadata. El beneficio aparece con volumen, seleccion de columnas y queries repetidas.

## Por que particionar por fecha reduce costos

La capa silver guarda transacciones particionadas por:

```text
year/month
```

Si una consulta filtra por `year` y `month`, Athena puede aplicar partition pruning y evitar escanear meses que no corresponden.

Ejemplo conceptual:

```sql
WHERE year = 2025
  AND month BETWEEN 1 AND 3
```

Esto reduce bytes escaneados si las tablas estan bien registradas en Glue Data Catalog y las particiones estan disponibles para Athena.

## Como cobra Athena

Athena cobra por datos escaneados por consulta. Por eso importan:

- formato de archivo;
- compresion;
- columnas seleccionadas;
- filtros de particion;
- cantidad de archivos pequenos;
- uso de `SELECT *`.

Este proyecto no calcula una factura real. `output/cost_estimation.json` solo mide bytes locales de CSV y Parquet para explicar el concepto.

## Riesgos de costos

- Ejecutar queries amplias sin filtros.
- Usar CSV en vez de Parquet para consultas frecuentes.
- No particionar datasets historicos grandes.
- Mantener demasiados archivos pequenos.
- Permitir `SELECT *` en tablas grandes.
- No configurar budgets ni alertas.
- Dejar datos temporales o duplicados sin lifecycle policies.

## Buenas practicas

### Particionar

Usar particiones alineadas con los filtros mas frecuentes. En datos bancarios historicos, `year/month` suele ser un punto de partida simple.

### Comprimir

Usar Parquet con compresion como Snappy para balancear rendimiento y tamano.

### Evitar `SELECT *`

Seleccionar solo columnas necesarias. Las queries finales de este proyecto evitan `SELECT *`.

### Limitar queries

Configurar Athena Workgroups con limites de bytes escaneados y separar workloads de desarrollo, QA y produccion.

### Lifecycle policies

Mover o expirar datos temporales, raw antiguo o artefactos intermedios que ya no se consultan.

### Billing alerts

Configurar AWS Budgets y alertas tempranas para detectar consumo no esperado antes de una entrevista o demo.
