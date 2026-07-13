{{ config(materialized='view') }}

select
    cast(customer_id as varchar) as customer_id,
    trim(customer_name) as customer_name,
    lower(trim(email)) as email,
    trim(country) as country,
    lower(trim(customer_segment)) as customer_segment,
    cast(updated_at as timestamp) as updated_at
from {{ ref('raw_customers') }}
