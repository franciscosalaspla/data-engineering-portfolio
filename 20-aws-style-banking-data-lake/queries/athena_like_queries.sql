-- name: transactions_by_channel
SELECT
    channel,
    transaction_count,
    ROUND(total_amount, 2) AS total_amount,
    ROUND(average_amount, 2) AS average_amount,
    failed_or_reversed_count,
    risk_transaction_count
FROM read_parquet('{{PROJECT_ROOT}}/data_lake/gold/channel_metrics/*.parquet')
ORDER BY transaction_count DESC;

-- name: monthly_total_amount
SELECT
    year,
    month,
    transaction_count,
    ROUND(total_amount, 2) AS total_amount,
    ROUND(total_amount_abs, 2) AS total_amount_abs,
    risk_transaction_count
FROM read_parquet('{{PROJECT_ROOT}}/data_lake/gold/monthly_amount/*.parquet')
ORDER BY year, month;

-- name: transaction_type_metrics
SELECT
    transaction_type,
    transaction_count,
    ROUND(total_amount, 2) AS total_amount,
    ROUND(average_amount, 2) AS average_amount,
    risk_transaction_count
FROM read_parquet('{{PROJECT_ROOT}}/data_lake/gold/transaction_type_metrics/*.parquet')
ORDER BY transaction_count DESC;

-- name: top_customers_by_amount
SELECT
    customer_id,
    customer_name,
    customer_segment,
    transaction_count,
    ROUND(total_transaction_amount, 2) AS total_transaction_amount,
    risk_transaction_count
FROM read_parquet('{{PROJECT_ROOT}}/data_lake/gold/top_customers/*.parquet')
ORDER BY total_transaction_amount DESC
LIMIT 10;

-- name: partition_pruning_year_month
SELECT
    year,
    month,
    channel,
    COUNT(transaction_id) AS transaction_count,
    ROUND(SUM(amount_abs), 2) AS total_amount_abs
FROM read_parquet(
    '{{PROJECT_ROOT}}/data_lake/silver/enriched_transactions/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2025
  AND month BETWEEN 1 AND 3
GROUP BY year, month, channel
ORDER BY year, month, transaction_count DESC;
