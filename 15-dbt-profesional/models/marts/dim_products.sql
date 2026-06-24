select
    product_id,
    sku,
    product_name,
    category_id,
    price,
    cost,
    is_active
from {{ ref('stg_products') }}
where product_id is not null
qualify row_number() over (
    partition by product_id
    order by product_id
) = 1
