-- =====================================================
-- Proyecto 11: Window Functions SQL
-- Archivo: window_functions_analysis.sql
-- Objetivo: Practicar funciones de ventana en SQL
-- =====================================================

-- 1. ROW_NUMBER: número de compra por cliente
SELECT
    customer_id,
    customer_name,
    order_id,
    order_date,
    product,
    sales,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS purchase_number
FROM orders
ORDER BY customer_id, order_date;


-- 2. RANK: ranking de clientes por venta total
WITH customer_sales AS (
    SELECT
        customer_id,
        customer_name,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id, customer_name
)

SELECT
    customer_id,
    customer_name,
    total_sales,
    RANK() OVER (
        ORDER BY total_sales DESC
    ) AS sales_rank
FROM customer_sales
ORDER BY sales_rank;


-- 3. DENSE_RANK: ranking de productos por categoría
SELECT
    category,
    product,
    sales,
    DENSE_RANK() OVER (
        PARTITION BY category
        ORDER BY sales DESC
    ) AS product_rank_in_category
FROM orders
ORDER BY category, product_rank_in_category;


-- 4. LAG: comparar venta actual con la compra anterior del cliente
SELECT
    customer_id,
    customer_name,
    order_id,
    order_date,
    product,
    sales,
    LAG(sales) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS previous_sales,
    sales - LAG(sales) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS sales_difference
FROM orders
ORDER BY customer_id, order_date;


-- 5. LEAD: ver la siguiente compra del cliente
SELECT
    customer_id,
    customer_name,
    order_id,
    order_date,
    product,
    sales,
    LEAD(order_date) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS next_order_date,
    LEAD(product) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS next_product
FROM orders
ORDER BY customer_id, order_date;


-- 6. SUM OVER: venta acumulada por cliente
SELECT
    customer_id,
    customer_name,
    order_id,
    order_date,
    product,
    sales,
    SUM(sales) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_sales
FROM orders
ORDER BY customer_id, order_date;


-- 7. AVG OVER: comparar venta contra promedio de su categoría
SELECT
    order_id,
    category,
    product,
    sales,
    ROUND(AVG(sales) OVER (
        PARTITION BY category
    ), 2) AS avg_sales_category,
    ROUND(
        sales - AVG(sales) OVER (
            PARTITION BY category
        ), 2
    ) AS difference_vs_category_avg
FROM orders
ORDER BY category, sales DESC;


-- 8. Ventas mensuales y comparación contra mes anterior
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) AS sales_month,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
)

SELECT
    sales_month,
    total_sales,
    LAG(total_sales) OVER (
        ORDER BY sales_month
    ) AS previous_month_sales,
    total_sales - LAG(total_sales) OVER (
        ORDER BY sales_month
    ) AS monthly_sales_difference
FROM monthly_sales
ORDER BY sales_month;
