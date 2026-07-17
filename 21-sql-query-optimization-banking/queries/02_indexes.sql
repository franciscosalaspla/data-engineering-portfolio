-- Strategic indexes for selective filters and joins.
-- Indexes can help when a query filters a small portion of a large table.
-- They do not automatically improve full table aggregations.
-- In analytical engines such as DuckDB, table design, columnar execution and
-- pre-aggregation can be more important than indexing every column.

CREATE INDEX IF NOT EXISTS idx_transaction_logs_endpoint
ON transaction_logs(endpoint);

CREATE INDEX IF NOT EXISTS idx_transaction_logs_status_code
ON transaction_logs(status_code);

CREATE INDEX IF NOT EXISTS idx_transaction_logs_created_at
ON transaction_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_transaction_logs_customer_id
ON transaction_logs(customer_id);

CREATE INDEX IF NOT EXISTS idx_transaction_logs_account_id
ON transaction_logs(account_id);

CREATE INDEX IF NOT EXISTS idx_transaction_logs_branch_id
ON transaction_logs(branch_id);

CREATE INDEX IF NOT EXISTS idx_transaction_logs_endpoint_status
ON transaction_logs(endpoint, status_code);

CREATE INDEX IF NOT EXISTS idx_transaction_logs_created_endpoint
ON transaction_logs(created_at, endpoint);
