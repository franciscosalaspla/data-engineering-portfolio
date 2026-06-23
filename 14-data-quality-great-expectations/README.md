# Data Quality con Great Expectations

Proyecto práctico para implementar una capa de validación de datos sobre archivos de e-commerce antes de cargarlos a un Data Warehouse o usarlos en reportes.

## Cómo contar este proyecto en una entrevista

### Hook

Implementé un pipeline de validación de datos que detectó fallas críticas antes de que los datos llegaran a un modelo analítico.

### Situación

Los datos de e-commerce venían desde archivos CSV con problemas típicos de datos crudos: duplicados, claves nulas, montos inválidos y registros incompletos.

Si estos datos se cargaban directamente a un Data Warehouse, podían generar reportes incorrectos, ventas duplicadas o relaciones incompletas entre órdenes, clientes y productos.

### Tarea

Diseñar una capa de Data Quality que validara automáticamente los datos antes de cargarlos a una etapa analítica.

El objetivo era responder:

```text
¿Los datos están suficientemente buenos para pasar al siguiente paso del pipeline?
```

### Acciones

Implementé validaciones sobre cuatro tablas principales:

```text
customers
orders
order_items
products
```

Definí dos tipos de reglas:

```text
critical → si falla, el pipeline queda FAILED
warning  → alerta, pero no bloquea necesariamente la carga
```

Las validaciones revisan:

* IDs nulos.
* IDs duplicados.
* Campos críticos vacíos.
* Montos inválidos.
* Cantidades inválidas.
* Productos u órdenes sin relación.

### Resultados

El pipeline ejecutó 16 validaciones.

| Métrica               | Resultado |
| --------------------- | --------: |
| Pipeline status       |    FAILED |
| Total validaciones    |        16 |
| Validaciones exitosas |         4 |
| Validaciones fallidas |        12 |
| Fallas críticas       |        10 |
| Warnings              |         2 |
| Success rate          |     25.0% |

El resultado `FAILED` indica que los datos no deberían cargarse directamente a un Data Warehouse sin revisión previa.

## Principales hallazgos

| Tabla       | Problema                       | Registros afectados |
| ----------- | ------------------------------ | ------------------: |
| customers   | `customer_id` duplicado        |                   1 |
| customers   | `email` nulo                   |                   3 |
| orders      | `order_id` duplicado           |                   3 |
| orders      | `customer_id` nulo             |                   6 |
| orders      | `total_amount` inválido o nulo |                  10 |
| order_items | `order_item_id` duplicado      |                   9 |
| order_items | `order_id` nulo                |                  33 |
| order_items | `product_id` nulo              |                  16 |
| order_items | `quantity` inválido o nulo     |                  28 |
| order_items | `subtotal` inválido o nulo     |                  29 |
| products    | `product_id` duplicado         |                   1 |
| products    | `product_name` nulo            |                   1 |

## Por qué importa

Una capa de calidad evita que datos defectuosos lleguen a reportes, dashboards o modelos dimensionales.

Ejemplos de impacto:

```text
order_id duplicado        → riesgo de ventas duplicadas
customer_id nulo          → órdenes sin cliente
product_id nulo           → ventas sin producto asociado
subtotal inválido         → métricas financieras poco confiables
quantity inválida         → unidades vendidas incorrectas
```

## Reglas implementadas

### Customers

| Regla                          | Severidad |
| ------------------------------ | --------- |
| `customer_id` no debe ser nulo | critical  |
| `customer_id` debe ser único   | critical  |
| `email` no debe ser nulo       | warning   |

### Orders

| Regla                                     | Severidad |
| ----------------------------------------- | --------- |
| `order_id` no debe ser nulo               | critical  |
| `order_id` debe ser único                 | critical  |
| `customer_id` no debe ser nulo            | critical  |
| `total_amount` debe ser mayor o igual a 0 | critical  |

### Order Items

| Regla                                 | Severidad |
| ------------------------------------- | --------- |
| `order_item_id` no debe ser nulo      | critical  |
| `order_item_id` debe ser único        | critical  |
| `order_id` no debe ser nulo           | critical  |
| `product_id` no debe ser nulo         | critical  |
| `quantity` debe ser mayor o igual a 1 | critical  |
| `subtotal` debe ser mayor o igual a 0 | critical  |

### Products

| Regla                           | Severidad |
| ------------------------------- | --------- |
| `product_id` no debe ser nulo   | critical  |
| `product_id` debe ser único     | critical  |
| `product_name` no debe ser nulo | warning   |

## Outputs generados

```text
output/validation_results.csv
output/validation_summary.json
```

### `validation_results.csv`

Contiene el detalle de cada validación:

```text
table
expectation
column
severity
success
unexpected_count
unexpected_percent
```

### `validation_summary.json`

Contiene el resumen global del pipeline:

```text
pipeline_status
total_expectations
passed_expectations
failed_expectations
critical_failures
warning_failures
success_rate
```

## Stack utilizado

```text
Python
pandas
Great Expectations
CSV
Git / GitHub
```

Nota: el proyecto usa Great Expectations como dependencia y referencia conceptual para estructurar expectations. Por compatibilidad con la versión instalada, las reglas se ejecutan con pandas de forma simple y reproducible.

## Aprendizajes

* Data Quality debe ejecutarse antes de cargar datos a modelos analíticos.
* No todas las reglas tienen la misma severidad.
* Las reglas críticas deben bloquear el pipeline.
* Los warnings permiten alertar sin detener necesariamente el proceso.
* Validar claves, duplicados y métricas evita reportes incorrectos.
* Un pipeline no solo debe transformar datos; también debe proteger la confiabilidad del dato.

## Cómo ejecutar

```bash
cd 14-data-quality-great-expectations
pip install -r requirements.txt
python src/run_quality_checks.py
```

## Estructura del proyecto

```text
14-data-quality-great-expectations/
├── data/
│   └── raw/
│       ├── ecommerce_customers.csv
│       ├── ecommerce_orders.csv
│       ├── ecommerce_order_items.csv
│       └── ecommerce_products.csv
├── output/
│   ├── validation_results.csv
│   └── validation_summary.json
├── src/
│   └── run_quality_checks.py
├── docs/
├── README.md
└── requirements.txt
```
