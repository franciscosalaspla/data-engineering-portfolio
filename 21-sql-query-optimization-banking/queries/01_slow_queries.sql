-- name: slow_endpoint_errors
SELECT *
FROM transaction_logs
WHERE status_code >= 400
  AND endpoint IN ('/api/wire-transfer', '/api/international-transfer')
ORDER BY created_at DESC;

-- name: slow_correlated_avg_response_time
SELECT
    logs.log_id,
    logs.endpoint,
    logs.channel,
    logs.status_code,
    logs.response_time_ms,
    (
        SELECT AVG(compare_logs.response_time_ms)
        FROM transaction_logs AS compare_logs
        WHERE compare_logs.endpoint = logs.endpoint
    ) AS endpoint_avg_response_time_ms
FROM transaction_logs AS logs
WHERE logs.status_code = 500
  AND logs.endpoint IN ('/api/wire-transfer', '/api/international-transfer')
ORDER BY logs.response_time_ms DESC;

-- name: slow_channel_metrics_full_scan
SELECT
    channel,
    transaction_type,
    COUNT(*) AS total_logs,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) AS error_logs,
    AVG(response_time_ms) AS avg_response_time_ms,
    SUM(transaction_amount) AS net_transaction_amount
FROM transaction_logs
GROUP BY channel, transaction_type
ORDER BY total_logs DESC;

-- name: slow_customer_error_lookup
SELECT
    customers.customer_id,
    customers.customer_name,
    customers.customer_segment,
    branches.city,
    accounts.account_type,
    COUNT(*) AS error_events,
    AVG(transaction_logs.response_time_ms) AS avg_error_response_time_ms,
    MAX(transaction_logs.created_at) AS last_error_at
FROM transaction_logs
JOIN accounts
    ON transaction_logs.account_id = accounts.account_id
JOIN customers
    ON accounts.customer_id = customers.customer_id
JOIN branches
    ON transaction_logs.branch_id = branches.branch_id
WHERE transaction_logs.status_code >= 400
  AND transaction_logs.endpoint = '/api/wire-transfer'
  AND transaction_logs.created_at >= TIMESTAMP '2026-01-01 00:00:00'
GROUP BY
    customers.customer_id,
    customers.customer_name,
    customers.customer_segment,
    branches.city,
    accounts.account_type
HAVING COUNT(*) > 0
ORDER BY error_events DESC, avg_error_response_time_ms DESC
LIMIT 25;
