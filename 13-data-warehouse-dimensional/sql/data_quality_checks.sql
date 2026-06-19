-- =====================================================
-- Proyecto 13: Validaciones de calidad del Data Warehouse
-- =====================================================

-- 1. Validar filas de la fact
SELECT
    COUNT(*) AS total_fact_rows,
    COUNT(DISTINCT order_item_id) AS distinct_order_items
FROM fact_order_items;


-- 2. Fact sin fecha asociada
SELECT
    COUNT(*) AS rows_without_date
FROM fact_order_items
WHERE date_key IS NULL;


-- 3. Fact sin cliente asociado
SELECT
    COUNT(*) AS rows_without_customer
FROM fact_order_items
WHERE customer_key IS NULL;


-- 4. Fact sin producto asociado
SELECT
    COUNT(*) AS rows_without_product
FROM fact_order_items
WHERE product_key IS NULL;


-- 5. Ventas con fecha nula
SELECT
    COUNT(DISTINCT order_id) AS orders_without_date,
    COUNT(order_item_id) AS items_without_date,
    ROUND(SUM(item_subtotal), 2) AS sales_without_date
FROM fact_order_items
WHERE date_key IS NULL;


-- 6. Ventas con producto no asociado
SELECT
    COUNT(order_item_id) AS items_without_product,
    ROUND(SUM(item_subtotal), 2) AS sales_without_product
FROM fact_order_items
WHERE product_key IS NULL;


-- 7. Ventas con cliente no asociado
SELECT
    COUNT(DISTINCT order_id) AS orders_without_customer,
    COUNT(order_item_id) AS items_without_customer,
    ROUND(SUM(item_subtotal), 2) AS sales_without_customer
FROM fact_order_items
WHERE customer_key IS NULL;
