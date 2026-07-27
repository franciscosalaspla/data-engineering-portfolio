-- Project 23: portable analytical examples over the Gold star schema.
-- Table qualification is intentionally left to the target catalog/schema.

-- Daily EUR transaction value by currency.
SELECT
    d.full_date,
    c.currency_code,
    COUNT(*) AS transaction_count,
    SUM(f.amount_original) AS amount_original,
    SUM(f.amount_eur) AS amount_eur
FROM fact_transactions AS f
JOIN dim_date AS d ON d.date_key = f.date_key
JOIN dim_currency AS c ON c.currency_key = f.currency_key
GROUP BY d.full_date, c.currency_code
ORDER BY d.full_date, c.currency_code;

-- Customer-segment and channel performance in the common EUR measure.
SELECT
    cu.segment,
    ch.channel_code,
    COUNT(*) AS transaction_count,
    SUM(f.amount_eur) AS amount_eur
FROM fact_transactions AS f
JOIN dim_customer AS cu ON cu.customer_key = f.customer_key
JOIN dim_channel AS ch ON ch.channel_key = f.channel_key
GROUP BY cu.segment, ch.channel_code
ORDER BY amount_eur DESC;
