{{ config(materialized='view') }}

with orders as (
    select * from {{ ref('int_orders_enriched') }}
)

select
    customer_id,
    max(customer_name) as customer_name,
    max(country) as country,
    max(customer_segment) as customer_segment,
    count(order_id) as total_orders,
    sum(case when normalized_order_status = 'completed' then 1 else 0 end) as completed_orders,
    sum(case when normalized_order_status = 'completed' then revenue else 0 end) as completed_revenue,
    min(order_date) as first_order_date,
    max(order_date) as most_recent_order_date
from orders
group by customer_id
