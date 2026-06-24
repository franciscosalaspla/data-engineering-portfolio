select
    try_cast(customer_id as integer) as customer_id,
    lower(trim(first_name)) as first_name,
    lower(trim(last_name)) as last_name,
    lower(trim(email)) as email,
    lower(trim(city)) as city,
    lower(trim(country)) as country,
    lower(trim(segment)) as segment,
    try_cast(is_verified as boolean) as is_verified,
    try_cast(accepts_marketing as boolean) as accepts_marketing
from {{ source('raw_ecommerce', 'ecommerce_customers') }}
