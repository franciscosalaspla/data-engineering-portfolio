select
    customer_id,
    first_name,
    last_name,
    email,
    city,
    country,
    segment,
    is_verified,
    accepts_marketing
from {{ ref('stg_customers') }}
where customer_id is not null
qualify row_number() over (
    partition by customer_id
    order by customer_id
) = 1
