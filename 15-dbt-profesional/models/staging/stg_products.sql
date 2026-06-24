select
    try_cast(product_id as integer) as product_id,
    sku,
    lower(trim(product_name)) as product_name,
    try_cast(category_id as integer) as category_id,
    try_cast(price as double) as price,
    try_cast(cost as double) as cost,
    try_cast(is_active as boolean) as is_active
from {{ source('raw_ecommerce', 'ecommerce_products') }}
