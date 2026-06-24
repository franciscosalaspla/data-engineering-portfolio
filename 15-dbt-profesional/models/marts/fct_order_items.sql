select
    oi.order_item_id,
    oi.order_id,
    o.customer_id,
    oi.product_id,
    o.order_date,
    o.status,
    oi.quantity,
    oi.unit_price,
    oi.item_subtotal,
    o.payment_method,
    o.shipping_method
from {{ ref('stg_order_items') }} oi
inner join {{ ref('stg_orders') }} o
    on oi.order_id = o.order_id
inner join {{ ref('dim_customers') }} c
    on o.customer_id = c.customer_id
inner join {{ ref('dim_products') }} p
    on oi.product_id = p.product_id
where oi.order_item_id is not null
  and oi.order_id is not null
  and oi.product_id is not null
  and oi.quantity >= 1
  and oi.item_subtotal >= 0
qualify row_number() over (
    partition by oi.order_item_id
    order by oi.order_item_id
) = 1
