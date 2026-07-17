# EXPLAIN Reading Guide

## Que es EXPLAIN

`EXPLAIN` muestra el plan que el motor SQL espera ejecutar para una consulta. No devuelve los datos finales de la query; devuelve una representacion del trabajo interno que el motor planea hacer.

En este proyecto se usa para revisar si una consulta necesita leer una tabla completa, aplicar filtros, ordenar, agregar, unir tablas o usar una estructura auxiliar.

## Que es EXPLAIN ANALYZE

`EXPLAIN ANALYZE` ejecuta la consulta y muestra informacion del plan junto con datos de ejecucion. Es mas util para validar comportamiento real porque incluye el costo observado durante la ejecucion local.

La diferencia practica es:

| Comando | Ejecuta la query | Para que sirve |
| --- | --- | --- |
| `EXPLAIN` | No necesariamente | Entender el plan estimado. |
| `EXPLAIN ANALYZE` | Si | Revisar el plan con evidencia de ejecucion. |

## Como interpretar operaciones comunes

| Operacion | Significado | Lectura practica |
| --- | --- | --- |
| Seq Scan | Lectura secuencial de una tabla o fragmento de tabla. | Puede estar bien en analitica, pero debe revisarse si el filtro es muy selectivo. |
| Index Scan | Lectura usando un indice. | Suele ayudar cuando se busca una pequena parte de la tabla. |
| Hash Join | Join por igualdad usando una tabla hash. | Comun y eficiente para joins analiticos si las claves son razonables. |
| Nested Loop | Join que itera una entrada contra otra. | Puede ser costoso con muchas filas; requiere revisar cardinalidad. |
| Aggregate | Agrupacion o calculo agregado. | El costo depende de filas leidas, columnas usadas y cardinalidad del group by. |
| Filter | Aplicacion de condiciones `WHERE`. | Conviene que reduzca filas temprano cuando sea posible. |

## Cuando un plan puede ser bueno o malo

Un plan no es bueno o malo por una sola palabra. Un `Seq Scan` puede ser correcto si la query necesita leer casi toda la tabla, como una agregacion global. Un `Index Scan` puede no aportar si el filtro no es selectivo o si el motor analitico resuelve mejor con lectura columnar.

Un plan merece revision cuando:

- lee muchas mas filas de las necesarias;
- filtra tarde despues de joins grandes;
- repite agregaciones que podrian preagregarse;
- usa joins costosos sin necesidad;
- selecciona columnas innecesarias;
- ejecuta subqueries correlacionadas que pueden reescribirse como agregaciones y joins.

## Por que no se optimiza a ciegas

Optimizar sin medir puede llevar a cambios que no mejoran nada o incluso empeoran la query. Por eso este proyecto compara baseline vs optimizado con:

- queries antes y despues;
- `EXPLAIN ANALYZE`;
- benchmark con varias iteraciones;
- resumen JSON con mejoras medidas.

La regla principal es simple: primero entender el plan, despues cambiar la query, y finalmente medir.
