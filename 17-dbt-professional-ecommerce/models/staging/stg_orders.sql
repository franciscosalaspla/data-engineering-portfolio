{{ config(materialized='view') }}

select
    cast(order_id as varchar) as order_id,
    cast(customer_id as varchar) as customer_id,
    cast(product_id as varchar) as product_id,
    cast(order_date as date) as order_date,
    cast(quantity as integer) as quantity,
    cast(unit_price as decimal(12, 2)) as unit_price,
    lower(trim(status)) as status,
    cast(updated_at as timestamp) as updated_at
from {{ ref('raw_orders') }}
