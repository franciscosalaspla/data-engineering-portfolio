-- name: optimized_endpoint_errors
SELECT
    log_id,
    transaction_id,
    customer_id,
    account_id,
    branch_id,
    endpoint,
    status_code,
    response_time_ms,
    created_at
FROM transaction_logs
WHERE endpoint IN ('/api/wire-transfer', '/api/international-transfer')
  AND status_code >= 400
ORDER BY created_at DESC;

-- name: optimized_correlated_avg_response_time
WITH endpoint_response_time AS (
    SELECT
        endpoint,
        AVG(response_time_ms) AS endpoint_avg_response_time_ms
    FROM transaction_logs
    GROUP BY endpoint
),
filtered_logs AS (
    SELECT
        log_id,
        endpoint,
        channel,
        status_code,
        response_time_ms
    FROM transaction_logs
    WHERE status_code = 500
      AND endpoint IN ('/api/wire-transfer', '/api/international-transfer')
)
SELECT
    filtered_logs.log_id,
    filtered_logs.endpoint,
    filtered_logs.channel,
    filtered_logs.status_code,
    filtered_logs.response_time_ms,
    endpoint_response_time.endpoint_avg_response_time_ms
FROM filtered_logs
JOIN endpoint_response_time
    ON filtered_logs.endpoint = endpoint_response_time.endpoint
ORDER BY filtered_logs.response_time_ms DESC;

-- name: optimized_channel_metrics_preaggregated
SELECT
    channel,
    transaction_type,
    total_logs,
    error_logs,
    avg_response_time_ms,
    net_transaction_amount
FROM channel_transaction_metrics
ORDER BY total_logs DESC;

-- name: optimized_customer_error_lookup
WITH filtered_errors AS (
    SELECT
        customer_id,
        account_id,
        branch_id,
        response_time_ms,
        created_at
    FROM transaction_logs
    WHERE endpoint = '/api/wire-transfer'
      AND status_code >= 400
      AND created_at >= TIMESTAMP '2026-01-01 00:00:00'
)
SELECT
    customers.customer_id,
    customers.customer_name,
    customers.customer_segment,
    branches.city,
    accounts.account_type,
    COUNT(*) AS error_events,
    AVG(filtered_errors.response_time_ms) AS avg_error_response_time_ms,
    MAX(filtered_errors.created_at) AS last_error_at
FROM filtered_errors
JOIN accounts
    ON filtered_errors.account_id = accounts.account_id
JOIN customers
    ON filtered_errors.customer_id = customers.customer_id
JOIN branches
    ON filtered_errors.branch_id = branches.branch_id
GROUP BY
    customers.customer_id,
    customers.customer_name,
    customers.customer_segment,
    branches.city,
    accounts.account_type
ORDER BY error_events DESC, avg_error_response_time_ms DESC
LIMIT 25;
