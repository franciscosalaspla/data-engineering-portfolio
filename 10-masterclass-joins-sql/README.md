# Masterclass de JOINS SQL

Proyecto práctico para entender y aplicar distintos tipos de `JOIN` usando SQL, DuckDB y un caso simple de Recursos Humanos.

## Objetivo

Practicar consultas SQL para unir tablas, detectar registros sin match y generar outputs analíticos.

Se trabajan:

* `INNER JOIN`
* `LEFT JOIN`
* `LEFT JOIN + IS NULL`
* `SELF JOIN`
* JOIN de 3 tablas
* CTEs
* Exportación de resultados a CSV

## Caso de negocio

El proyecto simula un modelo simple de RRHH con tres tablas:

* `employees`: empleados.
* `departments`: departamentos.
* `salaries`: sueldos.

Preguntas que responde:

* ¿Qué empleados tienen departamento válido?
* ¿Qué empleados no tienen departamento asignado o válido?
* ¿Qué departamentos no tienen empleados?
* ¿Qué empleados no tienen salario registrado?
* ¿Quién es el manager de cada empleado?
* ¿Cuál es el salario promedio por departamento?

## Stack

* SQL
* DuckDB
* Python
* CSV
* pandas
* Git / GitHub

## Estructura

```text
10-masterclass-joins-sql/
├── data/
│   └── raw/
│       ├── employees.csv
│       ├── departments.csv
│       └── salaries.csv
├── output/
│   ├── avg_salary_by_department.csv
│   ├── departments_without_employees.csv
│   ├── employees_departments_salaries.csv
│   ├── employees_with_manager.csv
│   ├── employees_without_salary.csv
│   ├── employees_without_valid_department.csv
│   ├── inner_join_employees_departments.csv
│   └── left_join_all_employees.csv
├── sql/
│   └── joins_analysis.sql
├── src/
│   └── run_joins.py
├── README.md
└── requirements.txt
```

## Casos incluidos en los datos

El dataset contiene casos intencionales para practicar joins:

```text
Carlos Díaz  → no tiene department_id
Diego Muñoz  → tiene department_id 50, pero no existe en departments
Marketing    → existe como departamento, pero no tiene empleados
Diego Muñoz  → no tiene salario registrado
Laura Torres → no tiene manager
```

## Consultas principales

| Consulta                      | Objetivo                                             |
| ----------------------------- | ---------------------------------------------------- |
| `INNER JOIN`                  | Obtener empleados con departamento válido            |
| `LEFT JOIN`                   | Mantener todos los empleados, aunque no tengan match |
| `LEFT JOIN + IS NULL`         | Detectar empleados sin departamento válido           |
| `LEFT JOIN desde departments` | Detectar departamentos sin empleados                 |
| JOIN de 3 tablas              | Unir empleados, departamentos y salarios             |
| `SELF JOIN`                   | Relacionar empleados con sus managers                |
| CTE                           | Calcular salario promedio por departamento           |

## Resultados principales

* Empleados sin departamento válido: `Carlos Díaz`, `Diego Muñoz`.
* Departamento sin empleados: `Marketing`.
* Empleado sin salario registrado: `Diego Muñoz`.
* Laura Torres no tiene manager registrado.
* HR tiene el salario promedio más alto del dataset.

## Outputs generados

Los resultados se guardan en `output/`:

```text
inner_join_employees_departments.csv
left_join_all_employees.csv
employees_without_valid_department.csv
departments_without_employees.csv
employees_departments_salaries.csv
employees_without_salary.csv
employees_with_manager.csv
avg_salary_by_department.csv
```

## Cómo ejecutar

```bash
cd 10-masterclass-joins-sql
pip install -r requirements.txt
python src/run_joins.py
```

## Aprendizajes

* `INNER JOIN` elimina registros sin match.
* `LEFT JOIN` conserva todos los registros de la tabla izquierda.
* `LEFT JOIN + IS NULL` permite detectar problemas de calidad.
* `SELF JOIN` sirve para relaciones jerárquicas, como empleado-manager.
* Las CTEs ayudan a ordenar consultas antes de agregar resultados.

## Explicación para entrevista

Construí un caso práctico de RRHH con tres tablas: empleados, departamentos y salarios. Practiqué `INNER JOIN`, `LEFT JOIN`, detección de registros sin match, `SELF JOIN` para relacionar empleados con managers y CTEs para calcular salario promedio por departamento. El proyecto muestra problemas típicos de calidad de datos, como empleados sin departamento válido, departamentos sin empleados y empleados sin salario registrado.
