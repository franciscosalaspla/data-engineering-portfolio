# Technical Notes - Proyecto 21

## Conceptos tecnicos aplicados

| Concepto | Aplicacion en el proyecto |
| --- | --- |
| `EXPLAIN` | Permite revisar el plan estimado o la representacion del trabajo de una query. |
| `EXPLAIN ANALYZE` | Ejecuta la query y devuelve evidencia del plan con informacion de ejecucion. |
| Seq Scan | Lectura secuencial que puede aparecer en queries analiticas o filtros no resueltos por indice. |
| Index Scan | Acceso por indice cuando el optimizador lo considera conveniente. |
| Hash Join | Estrategia comun para joins por igualdad. |
| Nested Loop | Operacion que debe revisarse cuando hay muchas filas involucradas. |
| Indexing | Creacion de indices sobre columnas usadas en filtros y joins selectivos. |
| Correlated subquery | Patron baseline que se reescribe como agregacion + join. |
| Query rewrite | Cambio de estructura SQL para reducir trabajo o mejorar mantenibilidad. |
| Pre-aggregation | Uso de tablas resumidas para evitar recalcular metricas desde logs completos. |
| Benchmark | Medicion con `perf_counter()` y varias iteraciones por query. |
| DuckDB | Motor SQL local usado para tablas, indices, planes y analitica. |

## Aprendizajes tecnicos del proyecto

Este proyecto funciona como practica de optimizacion SQL aplicada. El foco no es memorizar que una tecnica siempre mejora una query, sino aprender a observar el plan, cambiar una cosa concreta y medir el impacto.

### Conceptos clave

| Concepto | Que significa en este proyecto |
| --- | --- |
| Baseline query | Consulta funcional, pero escrita de forma menos eficiente o menos mantenible. |
| Optimized query | Version reescrita para seleccionar menos columnas, filtrar mejor o usar preagregaciones. |
| `EXPLAIN ANALYZE` | Evidencia del plan de ejecucion usada para documentar operaciones reales mostradas por DuckDB. |
| Indice selectivo | Indice creado sobre columnas usadas en filtros o joins frecuentes. |
| Preagregacion | Tabla analitica que evita recalcular metricas desde `transaction_logs` en cada consulta. |
| Benchmark local | Medicion reproducible, no promesa teorica de mejora. |

### Archivos mas importantes

| Archivo | Rol principal | Que debo saber explicar |
| --- | --- | --- |
| `generate_banking_logs.py` | Genera datos bancarios independientes y reproducibles. | Por que un laboratorio de performance necesita volumen suficiente y datos controlados. |
| `setup_database.py` | Crea tablas DuckDB y preagregaciones. | Por que se separa carga, modelo y optimizacion. |
| `run_explain_analysis.py` | Genera `output/explain_analysis.md`. | Como se documentan planes sin inventar operaciones. |
| `run_benchmark.py` | Mide baseline vs optimized. | Como se calculan mejoras desde tiempos reales. |
| `queries/01_slow_queries.sql` | Contiene queries baseline. | Que patrones son menos eficientes: `SELECT *`, subquery correlacionada, full scan agregado y filtros tardios. |
| `queries/02_indexes.sql` | Declara indices estrategicos. | Por que los indices son visibles y no estan escondidos en el setup. |
| `queries/03_optimized_queries.sql` | Contiene queries optimizadas. | Que cambio se compara contra cada baseline. |

### Funciones destacables

| Funcion o bloque | Archivo | Por que importa |
| --- | --- | --- |
| `generate_banking_logs()` | `generate_banking_logs.py` | Orquesta la generacion de entidades bancarias y logs transaccionales. |
| `build_transaction_logs()` | `generate_banking_logs.py` | Crea el dataset principal con endpoints, estados, canales, tipos, montos y fechas realistas. |
| `setup_database()` | `setup_database.py` | Crea la base DuckDB y materializa tablas del laboratorio. |
| `parse_named_queries()` | `run_explain_analysis.py` | Permite separar SQL del codigo Python usando comentarios `-- name:`. |
| `detected_operations()` | `run_explain_analysis.py` | Extrae operaciones relevantes solo si aparecen en el plan. |
| `run_single_query()` | `run_benchmark.py` | Ejecuta cada query varias veces y calcula duracion promedio. |
| `calculate_improvements()` | `run_benchmark.py` | Calcula factores de mejora solo desde tiempos medidos. |

## Que debo saber explicar tecnicamente

- Por que el proyecto genera sus propios datos y no depende de outputs ignorados de proyectos anteriores.
- Por que `SELECT *` puede aumentar trabajo innecesario.
- Como leer operaciones basicas en un plan de DuckDB.
- Cuando un `Seq Scan` puede ser aceptable en un motor analitico.
- Cuando un indice puede ayudar y cuando una agregacion full scan puede no beneficiarse.
- Por que una subquery correlacionada puede reescribirse como CTE + join.
- Por que una tabla preagregada puede mejorar consultas repetitivas de metricas.
- Por que `customer_error_lookup` no mejoro en la ejecucion validada y por que eso no invalida el proyecto.
- Por que las mejoras del README deben venir de benchmarks reales.

## Resumen tecnico corto

```text
generate_banking_logs.py genera datos bancarios reproducibles.
setup_database.py carga CSV en DuckDB y crea preagregaciones.
queries/01_slow_queries.sql define consultas baseline.
queries/02_indexes.sql declara indices estrategicos.
queries/03_optimized_queries.sql define consultas optimizadas comparables.
run_explain_analysis.py documenta planes con EXPLAIN ANALYZE.
run_benchmark.py mide tiempos reales y calcula mejoras.
run_pipeline.py orquesta todo y escribe pipeline_summary.json.
```

## Preguntas de entrevista

| Pregunta | Respuesta breve |
| --- | --- |
| Que problema resuelve este proyecto? | Muestra como pasar de SQL que solo funciona a SQL medido, documentado y mas mantenible. |
| Por que usaste DuckDB? | Porque permite ejecutar analitica SQL local, crear tablas, indices, `EXPLAIN ANALYZE` y benchmarks sin infraestructura cloud. |
| Cuando usarias un indice? | Cuando un filtro o join busca una parte selectiva de una tabla. |
| Cuando no sirve tanto un indice? | Cuando la query necesita leer gran parte de la tabla o hacer una agregacion full scan. |
| Que es `EXPLAIN`? | Una forma de ver el plan de ejecucion estimado de una query. |
| Que es `EXPLAIN ANALYZE`? | Ejecuta la query y muestra informacion del plan con evidencia de ejecucion. |
| Que es una subquery correlacionada? | Una subquery que depende de cada fila de la consulta externa. Puede ser expresiva, pero a veces se reescribe mejor como agregacion y join. |
| Que optimizacion fue mas efectiva? | La preagregacion de `channel_metrics`, con una mejora medida de 6.317x. |
| Todas las optimizaciones mejoraron? | No. `customer_error_lookup` no mejoro en la ejecucion local; por eso se documento como resultado real. |
| Esto equivale a PostgreSQL? | No exactamente. DuckDB y PostgreSQL tienen optimizadores y almacenamiento distintos, pero los conceptos de planes, filtros, joins, indices y medicion son transferibles. |

## Aprendizaje principal

Un Data Engineer no solo escribe SQL que funciona. Tambien debe saber leer planes de ejecucion, detectar cuellos de botella, optimizar queries, medir resultados y documentar decisiones sin exagerar los numeros.
