select
    try_cast(order_item_id as integer) as order_item_id,
    try_cast(order_id as integer) as order_id,
    try_cast(product_id as integer) as product_id,
    try_cast(quantity as integer) as quantity,
    try_cast(unit_price as double) as unit_price,
    try_cast(subtotal as double) as item_subtotal
from {{ source('raw_ecommerce', 'ecommerce_order_items') }}
