# Interview Guide

## Como contar este proyecto

Este proyecto es un laboratorio local de optimizacion SQL para datos bancarios. Genere datos sinteticos reproducibles de sucursales, clientes, cuentas y logs transaccionales. Luego cargue esos datos en DuckDB, escribi queries baseline intencionalmente menos eficientes, revise sus planes con `EXPLAIN ANALYZE`, cree indices visibles en SQL, reescribi consultas y compare tiempos con benchmarks reproducibles.

El foco no fue construir un pipeline cloud, sino demostrar criterio de performance SQL: leer planes, detectar cuellos de botella, aplicar filtros antes de joins, evitar `SELECT *`, reemplazar subqueries correlacionadas y usar preagregaciones cuando corresponde.

## Preguntas posibles y respuestas breves

| Pregunta | Respuesta breve |
| --- | --- |
| Por que usaste DuckDB? | Porque permite ejecutar analitica SQL local, crear tablas, indices, `EXPLAIN ANALYZE` y benchmarks sin infraestructura cloud. |
| Que problema resuelve este proyecto? | Muestra como pasar de SQL que solo funciona a SQL medido, documentado y mas mantenible. |
| Cuando usarias un indice? | Cuando filtro o busco una parte selectiva de una tabla, especialmente por columnas usadas en `WHERE` o joins frecuentes. |
| Cuando no sirve tanto un indice? | En agregaciones full scan o cuando la query necesita leer una gran parte de los datos. En esos casos puede ser mejor preagregar o redisenar la tabla. |
| Que es EXPLAIN? | Es una forma de ver el plan de ejecucion estimado de una query. |
| Que es EXPLAIN ANALYZE? | Ejecuta la query y devuelve informacion del plan con evidencia de ejecucion. |
| Que es una subquery correlacionada? | Una subquery que depende de cada fila de la consulta externa. Puede ser expresiva, pero a veces se reescribe mejor como agregacion y join. |
| Que optimizacion aplicaste a la subquery correlacionada? | Calcule el promedio por endpoint en una CTE y luego lo uni con los logs filtrados. |
| Por que creaste tablas preagregadas? | Para comparar una agregacion directa sobre logs completos contra una tabla ya resumida, que es un patron comun para dashboards. |
| Esto equivale a PostgreSQL? | No exactamente. DuckDB y PostgreSQL tienen optimizadores y almacenamiento distintos, pero los conceptos de plan, filtros, joins, indices y medicion son transferibles. |

## Decisiones defendibles

- Los datos se generan localmente para que el proyecto sea reproducible y no dependa de archivos ignorados de proyectos anteriores.
- Los indices viven en `queries/02_indexes.sql` para que la decision de optimizacion sea visible.
- Las queries baseline y optimizadas estan separadas para facilitar comparacion.
- Los benchmarks ejecutan varias iteraciones y reportan promedios.
- Las mejoras se documentan solo cuando fueron medidas.

## Cierre profesional

La idea principal para entrevista es que un Data Engineer debe poder explicar no solo que una query devuelve el resultado correcto, sino tambien como se ejecuta, que tradeoffs tiene y como validar si una optimizacion realmente mejora el comportamiento.
