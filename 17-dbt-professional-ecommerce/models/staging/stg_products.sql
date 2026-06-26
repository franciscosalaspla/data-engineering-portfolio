{{ config(materialized='view') }}

select
    cast(product_id as varchar) as product_id,
    trim(product_name) as product_name,
    trim(category) as category,
    cast(unit_cost as decimal(12, 2)) as unit_cost,
    cast(active_flag as boolean) as active_flag
from {{ ref('raw_products') }}
