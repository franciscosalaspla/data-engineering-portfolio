# Resultados documentados y conciliación

## Origen de las cifras

Los conteos históricos proceden de la sección de resultados del [README anterior a esta reorganización](https://github.com/franciscosalaspla/data-engineering-portfolio/blob/580bf2d2b83c50af9f3e130a375c81511c0868cc/20-aws-style-banking-data-lake/README.md#7-resultados-de-la-implementación), que registra una ejecución local en Codespaces con datos sintéticos.

Los JSON y CSV de aquella ejecución no están versionados: el proyecto los excluye mediante [.gitignore](../.gitignore). La actualización de la presentación no equivale a una nueva ejecución del pipeline.

| Resultado histórico documentado | Valor |
|---|---|
| Registros de transacciones en Landing | 1.257 |
| Transacciones enriquecidas en Silver | 1.135 |
| Registros en cuarentena | 120 |
| Conjuntos Gold generados | 5 |
| Consultas SQL ejecutadas | 5 |
| Estado final | PASSED |

## Lo que permite contrastar el código

- El [generador](../app/generate_banking_landing_data.py) crea 1.250 transacciones y agrega siete casos: dos copias de transacciones existentes y cinco casos adicionales con errores.
- La [normalización](../app/build_data_lake.py) retira duplicados por `transaction_id` antes de separar transacciones válidas y cuarentena.
- La misma función guarda en `duplicate_transaction_rows_removed` el conteo de filas duplicadas retiradas. Los dos casos añadidos por el generador explican la diferencia entre entrada, cuarentena y Silver.
- El constructor define cinco salidas Gold: `channel_metrics`, `transaction_type_metrics`, `monthly_amount`, `top_customers` y `branch_volume`.
- El [archivo SQL](../queries/athena_like_queries.sql) contiene cinco consultas nombradas.

**Conciliación de la ejecución documentada: 1.257 = 2 duplicados + 120 en cuarentena + 1.135 preparadas.**

Los conteos de 120 y 1.135 son resultados históricos documentados; para confirmarlos en otro entorno hay que ejecutar nuevamente el proyecto y revisar sus resúmenes.

## Cómo interpretar las validaciones

- `PASSED` registra que el recorrido o la consulta terminó sin excepción.
- Las cinco consultas son ejecuciones SQL, no cinco pruebas con aserciones de resultados esperados.
- El proyecto reconstruye las capas en cada corrida. Estos resultados no describen un MERGE incremental ni una publicación sin escrituras nuevas.
- La ejecución es local. Las referencias a S3, Glue, Lambda, Athena o CloudWatch son equivalencias de arquitectura.

[Volver a los resultados del proyecto](../README.md#los-resultados-y-su-valor-para-el-negocio)
