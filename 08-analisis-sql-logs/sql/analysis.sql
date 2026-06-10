-- =====================================================
-- Proyecto 08: Análisis SQL de Logs de Servidor
-- Archivo: analysis.sql
-- Objetivo: Analizar tráfico, errores y performance
-- =====================================================

-- 1. Exploración general del dataset
SELECT
    COUNT(*) AS total_requests,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(DISTINCT endpoint) AS unique_endpoints,
    MIN(timestamp) AS first_request,
    MAX(timestamp) AS last_request
FROM logs;


-- 2. Requests por método HTTP
SELECT
    method,
    COUNT(*) AS total_requests
FROM logs
GROUP BY method
ORDER BY total_requests DESC;


-- 3. Requests por status code
SELECT
    status_code,
    COUNT(*) AS total_requests
FROM logs
GROUP BY status_code
ORDER BY total_requests DESC;


-- 4. Endpoints más usados
SELECT
    endpoint,
    COUNT(*) AS total_requests
FROM logs
GROUP BY endpoint
ORDER BY total_requests DESC;


-- 5. Errores por endpoint
SELECT
    endpoint,
    COUNT(*) AS total_errors
FROM logs
WHERE status_code >= 400
GROUP BY endpoint
ORDER BY total_errors DESC;


-- 6. Performance por endpoint
SELECT
    endpoint,
    COUNT(*) AS total_requests,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
    MAX(response_time_ms) AS max_response_time_ms
FROM logs
GROUP BY endpoint
ORDER BY avg_response_time_ms DESC;


-- 7. Tendencia horaria de requests
SELECT
    EXTRACT(HOUR FROM timestamp) AS request_hour,
    COUNT(*) AS total_requests,
    ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms
FROM logs
GROUP BY request_hour
ORDER BY request_hour;


-- 8. Ranking de endpoints por tiempo promedio de respuesta
WITH endpoint_performance AS (
    SELECT
        endpoint,
        COUNT(*) AS total_requests,
        ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
        MAX(response_time_ms) AS max_response_time_ms
    FROM logs
    GROUP BY endpoint
)

SELECT
    endpoint,
    total_requests,
    avg_response_time_ms,
    max_response_time_ms,
    RANK() OVER (ORDER BY avg_response_time_ms DESC) AS performance_rank
FROM endpoint_performance
ORDER BY performance_rank;


-- 9. Comparación contra endpoint anterior usando LAG
WITH endpoint_performance AS (
    SELECT
        endpoint,
        COUNT(*) AS total_requests,
        ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms
    FROM logs
    GROUP BY endpoint
),

ranked_endpoints AS (
    SELECT
        endpoint,
        total_requests,
        avg_response_time_ms,
        RANK() OVER (ORDER BY avg_response_time_ms DESC) AS performance_rank
    FROM endpoint_performance
)

SELECT
    endpoint,
    total_requests,
    avg_response_time_ms,
    performance_rank,
    LAG(avg_response_time_ms) OVER (ORDER BY performance_rank) AS previous_avg_response_time,
    avg_response_time_ms - LAG(avg_response_time_ms) OVER (ORDER BY performance_rank) AS difference_vs_previous
FROM ranked_endpoints
ORDER BY performance_rank;