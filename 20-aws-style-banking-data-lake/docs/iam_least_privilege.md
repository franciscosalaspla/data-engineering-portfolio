# IAM Least Privilege

Este proyecto no usa credenciales reales. El objetivo de este documento es explicar el diseno conceptual de permisos minimos si la arquitectura se migrara a AWS.

## Principios

- No usar root para desarrollo ni pipelines.
- Crear usuarios o roles separados por responsabilidad.
- Otorgar permisos solo sobre buckets, prefixes, databases y workgroups necesarios.
- Separar lectura, escritura, transformacion y consulta.
- Rotar credenciales si se usan usuarios IAM, aunque para workloads se prefieren roles.
- No guardar access keys en el repositorio.

## Roles conceptuales

### Ingestion role

Responsabilidad:

- escribir archivos crudos en `s3://banking-data-lake/landing/`;
- leer solo lo necesario para validar llegada de archivos.

Permisos conceptuales:

- `s3:PutObject` sobre `landing/*`;
- `s3:GetObject` sobre `landing/*`;
- `s3:ListBucket` limitado al prefix `landing/`.

### Transformation role

Responsabilidad:

- leer landing y bronze;
- escribir bronze, silver y gold;
- actualizar catalogo si aplica.

Permisos conceptuales:

- `s3:GetObject` sobre `landing/*` y `bronze/*`;
- `s3:PutObject` sobre `bronze/*`, `silver/*` y `gold/*`;
- `glue:GetTable`, `glue:GetDatabase`, `glue:CreateTable`, `glue:UpdateTable` sobre la base del proyecto;
- permisos de logs para CloudWatch.

### Query role

Responsabilidad:

- consultar datos gold y, si es necesario, silver;
- escribir resultados de Athena en un prefix controlado.

Permisos conceptuales:

- `athena:StartQueryExecution`, `athena:GetQueryExecution`, `athena:GetQueryResults` sobre un workgroup especifico;
- `s3:GetObject` sobre `gold/*` y rutas silver autorizadas;
- `s3:PutObject` sobre `athena-results/*`;
- `glue:GetTable` y `glue:GetDatabase` sobre catalogo requerido.

### Glue crawler role

Responsabilidad:

- descubrir schemas solo en rutas requeridas.

Permisos conceptuales:

- lectura sobre `bronze/*`, `silver/*` y `gold/*`;
- escritura controlada en Glue Data Catalog;
- logs en CloudWatch.

## Restricciones recomendadas

- Bloquear buckets publicos.
- Usar encryption at rest con SSE-S3 o SSE-KMS.
- Usar condiciones por prefix cuando sea posible.
- Separar ambientes: dev, staging y prod.
- Activar CloudTrail para auditar acciones.

## Lo que no se debe hacer

- No usar root.
- No compartir access keys.
- No poner credenciales en `.env`, notebooks, commits o capturas.
- No dar `AdministratorAccess` a pipelines.
- No permitir lectura completa de todos los buckets si solo se requiere un prefix.
