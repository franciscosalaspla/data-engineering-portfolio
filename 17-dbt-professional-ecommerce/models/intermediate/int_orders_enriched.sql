{{ config(materialized='view') }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

products as (
    select * from {{ ref('stg_products') }}
)

select
    orders.order_id,
    orders.customer_id,
    customers.customer_name,
    customers.country,
    customers.customer_segment,
    orders.product_id,
    products.product_name,
    products.category,
    products.active_flag,
    orders.order_date,
    orders.quantity,
    orders.unit_price,
    products.unit_cost,
    orders.status as order_status,
    case
        when orders.status in ('completed', 'pending', 'cancelled', 'returned') then orders.status
        else 'unknown'
    end as normalized_order_status,
    cast(orders.quantity * orders.unit_price as decimal(12, 2)) as revenue,
    cast(orders.quantity * products.unit_cost as decimal(12, 2)) as cost,
    cast((orders.quantity * orders.unit_price) - (orders.quantity * products.unit_cost) as decimal(12, 2)) as margin,
    orders.updated_at
from orders
left join customers
    on orders.customer_id = customers.customer_id
left join products
    on orders.product_id = products.product_id
