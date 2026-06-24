select
    try_cast(order_id as integer) as order_id,
    try_cast(customer_id as integer) as customer_id,
    order_number,
    try_cast(order_date as date) as order_date,
    lower(trim(status)) as status,
    try_cast(subtotal as double) as subtotal,
    try_cast(discount_percent as double) as discount_percent,
    try_cast(shipping_cost as double) as shipping_cost,
    try_cast(tax_amount as double) as tax_amount,
    try_cast(total_amount as double) as total_amount,
    lower(trim(payment_method)) as payment_method,
    lower(trim(shipping_method)) as shipping_method
from {{ source('raw_ecommerce', 'ecommerce_orders') }}
