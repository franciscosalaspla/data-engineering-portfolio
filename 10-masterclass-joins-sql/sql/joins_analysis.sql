-- =====================================================
-- Proyecto 10: Masterclass de JOINS SQL
-- Archivo: joins_analysis.sql
-- Objetivo: Practicar diferentes tipos de JOIN
-- =====================================================

-- 1. INNER JOIN: empleados con departamento válido
SELECT
    e.employee_id,
    e.employee_name,
    e.department_id,
    d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;


-- 2. LEFT JOIN: todos los empleados, aunque no tengan departamento válido
SELECT
    e.employee_id,
    e.employee_name,
    e.department_id,
    d.department_name
FROM employees e
LEFT JOIN departments d
    ON e.department_id = d.department_id;


-- 3. LEFT JOIN para detectar empleados sin departamento válido
SELECT
    e.employee_id,
    e.employee_name,
    e.department_id,
    d.department_name
FROM employees e
LEFT JOIN departments d
    ON e.department_id = d.department_id
WHERE d.department_id IS NULL;


-- 4. LEFT JOIN desde departments para detectar departamentos sin empleados
SELECT
    d.department_id,
    d.department_name,
    e.employee_id,
    e.employee_name
FROM departments d
LEFT JOIN employees e
    ON d.department_id = e.department_id
WHERE e.employee_id IS NULL;


-- 5. JOIN de 3 tablas: empleados con departamento y sueldo
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
    ON e.employee_id = s.employee_id;


-- 6. Empleados sin salario registrado
SELECT
    e.employee_id,
    e.employee_name,
    s.salary
FROM employees e
LEFT JOIN salaries s
    ON e.employee_id = s.employee_id
WHERE s.employee_id IS NULL;


-- 7. SELF JOIN: empleado con su manager
SELECT
    e.employee_id,
    e.employee_name AS employee_name,
    e.manager_id,
    m.employee_name AS manager_name
FROM employees e
LEFT JOIN employees m
    ON e.manager_id = m.employee_id;


-- 8. CTE: salario promedio por departamento
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
ORDER BY avg_salary DESC;