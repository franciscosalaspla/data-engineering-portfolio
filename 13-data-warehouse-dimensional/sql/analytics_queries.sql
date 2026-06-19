-- =====================================================
-- Proyecto 13: Queries analíticas sobre modelo dimensional
-- Archivo: analytics_queries.sql
-- Objetivo: Validar el Data Warehouse con consultas de negocio
-- =====================================================

-- 1. Ventas por mes
-- Importante: usamos COUNT(DISTINCT order_id) porque la fact está a nivel order_item
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(f.order_item_id) AS total_items,
    ROUND(SUM(f.item_subtotal), 2) AS total_sales
FROM fact_order_items f
LEFT JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- 2. Top productos por ventas
SELECT
    p.product_name,
    p.category_name,
    COUNT(f.order_item_id) AS total_items_sold,
    ROUND(SUM(f.item_subtotal), 2) AS total_sales
FROM fact_order_items f
LEFT JOIN dim_products p
    ON f.product_key = p.product_key
GROUP BY
    p.product_name,
    p.category_name
ORDER BY
    total_sales DESC
LIMIT 10;


-- 3. Ventas fin de semana vs día laboral
SELECT
    CASE
        WHEN d.is_weekend = TRUE THEN 'weekend'
        ELSE 'weekday'
    END AS day_type,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(f.order_item_id) AS total_items,
    ROUND(SUM(f.item_subtotal), 2) AS total_sales
FROM fact_order_items f
LEFT JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    day_type
ORDER BY
    total_sales DESC;


-- 4. Ventas por segmento de cliente
SELECT
    c.segment,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(f.order_item_id) AS total_items,
    ROUND(SUM(f.item_subtotal), 2) AS total_sales
FROM fact_order_items f
LEFT JOIN dim_customers c
    ON f.customer_key = c.customer_key
GROUP BY
    c.segment
ORDER BY
    total_sales DESC;
