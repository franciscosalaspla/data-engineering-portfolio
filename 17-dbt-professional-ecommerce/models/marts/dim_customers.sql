{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('stg_customers') }}
),

history as (
    select * from {{ ref('int_customer_order_history') }}
)

select
    customers.customer_id,
    customers.customer_name,
    customers.email,
    customers.country,
    customers.customer_segment,
    coalesce(history.total_orders, 0) as total_orders,
    coalesce(history.completed_orders, 0) as completed_orders,
    coalesce(history.completed_revenue, 0) as completed_revenue,
    history.first_order_date,
    history.most_recent_order_date,
    customers.updated_at
from customers
left join history
    on customers.customer_id = history.customer_id
