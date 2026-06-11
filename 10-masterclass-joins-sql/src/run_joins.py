import duckdb
import os

# Crear carpeta output si no existe
os.makedirs("output", exist_ok=True)

# Crear conexión local en memoria
con = duckdb.connect()

# Crear tablas desde CSV
con.execute("""
CREATE OR REPLACE TABLE employees AS
SELECT *
FROM read_csv_auto('data/raw/employees.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE departments AS
SELECT *
FROM read_csv_auto('data/raw/departments.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE salaries AS
SELECT *
FROM read_csv_auto('data/raw/salaries.csv');
""")

# Consultas principales del proyecto
queries = {
    "inner_join_employees_departments": """
        SELECT
            e.employee_id,
            e.employee_name,
            e.department_id,
            d.department_name
        FROM employees e
        INNER JOIN departments d
            ON e.department_id = d.department_id
    """,

    "left_join_all_employees": """
        SELECT
            e.employee_id,
            e.employee_name,
            e.department_id,
            d.department_name
        FROM employees e
        LEFT JOIN departments d
            ON e.department_id = d.department_id
    """,

    "employees_without_valid_department": """
        SELECT
            e.employee_id,
            e.employee_name,
            e.department_id,
            d.department_name
        FROM employees e
        LEFT JOIN departments d
            ON e.department_id = d.department_id
        WHERE d.department_id IS NULL
    """,

    "departments_without_employees": """
        SELECT
            d.department_id,
            d.department_name,
            e.employee_id,
            e.employee_name
        FROM departments d
        LEFT JOIN employees e
            ON d.department_id = e.department_id
        WHERE e.employee_id IS NULL
    """,

    "employees_departments_salaries": """
        SELECT
            e.employee_id,
            e.employee_name,
            d.department_name,
            s.salary,
            s.effective_date
        FROM employees e
        LEFT JOIN departments d
            ON e.department_id = d.department_id
        LEFT JOIN salaries s
            ON e.employee_id = s.employee_id
    """,

    "employees_without_salary": """
        SELECT
            e.employee_id,
            e.employee_name,
            s.salary
        FROM employees e
        LEFT JOIN salaries s
            ON e.employee_id = s.employee_id
        WHERE s.employee_id IS NULL
    """,

    "employees_with_manager": """
        SELECT
            e.employee_id,
            e.employee_name AS employee_name,
            e.manager_id,
            m.employee_name AS manager_name
        FROM employees e
        LEFT JOIN employees m
            ON e.manager_id = m.employee_id
    """,

    "avg_salary_by_department": """
        WITH employee_department_salary AS (
            SELECT
                e.employee_id,
                e.employee_name,
                d.department_name,
                s.salary
            FROM employees e
            LEFT JOIN departments d
                ON e.department_id = d.department_id
            LEFT JOIN salaries s
                ON e.employee_id = s.employee_id
        )

        SELECT
            department_name,
            COUNT(employee_id) AS total_employees,
            ROUND(AVG(salary), 2) AS avg_salary
        FROM employee_department_salary
        GROUP BY department_name
        ORDER BY avg_salary DESC
    """
}

# Ejecutar cada consulta y guardar resultado en CSV
for name, query in queries.items():
    result = con.execute(query).fetchdf()
    output_path = f"output/{name}.csv"

    result.to_csv(output_path, index=False)

    print(f"\nArchivo generado: {output_path}")
    print(result)