{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='delete+insert'
    )
}}

with orders as (
    select * from {{ ref('int_orders_enriched') }}
)

select
    order_id,
    customer_id,
    product_id,
    order_date,
    quantity,
    unit_price,
    unit_cost,
    normalized_order_status as status,
    revenue,
    cost,
    margin,
    updated_at
from orders

{% if is_incremental() %}
where updated_at > (select coalesce(max(updated_at), cast('1900-01-01' as timestamp)) from {{ this }})
{% endif %}
