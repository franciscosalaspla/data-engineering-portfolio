# AWS Architecture Mapping

Este proyecto simula localmente una arquitectura de Data Lake bancaria estilo AWS. No crea recursos cloud, no usa credenciales y no ejecuta servicios reales de AWS.

## Mapeo local vs AWS

| Componente local | Equivalente AWS | Responsabilidad | Migracion real |
| --- | --- | --- | --- |
| `data_lake/landing/` | S3 landing/raw prefix | Recibir CSV crudos desde sistemas origen | Crear bucket o prefix S3 para archivos raw, con versionado y lifecycle policy |
| `app/generate_banking_landing_data.py` | Sistema core bancario / batch export | Simular extractos operacionales crudos | Reemplazar por transferencia controlada desde core banking, SFTP, DMS o jobs batch |
| `data_lake/bronze/` | S3 bronze prefix | Persistir datos cercanos al raw en Parquet | Escribir Parquet en S3 con compresion y metadata de ingestion |
| `app/build_data_lake.py` | Glue Job / Lambda transform | Normalizar, limpiar, validar y enriquecer datos | Ejecutar como Glue Spark Job, Glue Python Shell o Lambda para volumen bajo |
| `data_lake/silver/` | S3 silver prefix | Guardar datos limpios y enriquecidos | Particionar por `year/month` en S3 y registrar schema en Glue Data Catalog |
| `data_lake/gold/` | S3 gold analytics prefix | Publicar metricas analiticas | Crear tablas externas para consumo de Athena, QuickSight o downstream jobs |
| `queries/athena_like_queries.sql` | Athena SQL | Consultar datos analiticos en Parquet | Crear workgroup Athena, tablas externas y queries controladas |
| `app/run_athena_like_queries.py` | Athena query execution | Ejecutar SQL local con DuckDB | Orquestar queries via Athena Workgroup, Step Functions o Airflow |
| `output/pipeline_summary.json` | CloudWatch-style logs | Registrar estado, conteos, rutas y checks | Enviar logs a CloudWatch Logs y metricas a CloudWatch Metrics |
| `output/cost_estimation.json` | Cost Explorer / billing controls conceptuales | Estimar bytes locales y controles de scan | Activar budgets, billing alerts y tags de costos |
| `docs/iam_least_privilege.md` | IAM policy design | Definir permisos minimos conceptuales | Crear roles separados por ingestion, transformacion y consulta |

## Flujo conceptual

```text
S3 landing/raw
    -> Glue/Lambda transform
    -> S3 bronze
    -> S3 silver particionado
    -> S3 gold analytics
    -> Athena queries
    -> CloudWatch-style summary
```

## Responsabilidades por capa

### Landing

Conserva datos crudos generados localmente en CSV. En AWS seria el punto de entrada de archivos batch, normalmente protegido contra modificaciones manuales.

### Bronze

Convierte el landing a Parquet manteniendo una estructura cercana al raw. Agrega metadata tecnica como archivo fuente y timestamp de carga.

### Silver

Aplica reglas de calidad:

- normalizacion de tipos de transaccion y canales;
- parseo de fechas y montos;
- remocion de duplicados;
- cuarentena de registros invalidos criticos;
- enriquecimiento de transacciones con cuentas, clientes y sucursales;
- particionamiento por `year/month`.

### Gold

Materializa datasets analiticos preparados para consultas:

- transacciones por canal;
- transacciones por tipo;
- monto total por mes;
- top clientes por monto transaccional;
- sucursales con mayor volumen.

## Como migrarlo a AWS real

1. Crear bucket S3 con prefixes `landing/`, `bronze/`, `silver/` y `gold/`.
2. Reemplazar `data_lake/landing/` por una carga real a S3.
3. Ejecutar la transformacion como Glue Job o Lambda, segun volumen y duracion.
4. Registrar schemas con Glue Data Catalog.
5. Crear tablas externas en Athena apuntando a silver/gold.
6. Configurar un Athena Workgroup con limites de bytes escaneados.
7. Enviar logs y metricas a CloudWatch.
8. Configurar IAM least privilege, budgets y billing alerts.

## Limites de esta simulacion

- No despliega Glue, Lambda, S3, Athena ni CloudWatch reales.
- No usa `boto3`.
- No usa credenciales AWS.
- No genera costos cloud.
- No prueba performance de volumen real en S3.
