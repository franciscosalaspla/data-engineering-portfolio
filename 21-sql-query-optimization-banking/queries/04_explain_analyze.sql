-- Baseline plan example.
EXPLAIN
SELECT *
FROM transaction_logs
WHERE status_code >= 400
  AND endpoint IN ('/api/wire-transfer', '/api/international-transfer')
ORDER BY created_at DESC;

-- Baseline execution profile example.
EXPLAIN ANALYZE
SELECT *
FROM transaction_logs
WHERE status_code >= 400
  AND endpoint IN ('/api/wire-transfer', '/api/international-transfer')
ORDER BY created_at DESC;

-- Optimized plan example.
EXPLAIN
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

-- Optimized execution profile example.
EXPLAIN ANALYZE
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
