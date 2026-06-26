{{ config(materialized='table') }}

select
    product_id,
    product_name,
    category,
    unit_cost,
    active_flag
from {{ ref('stg_products') }}
