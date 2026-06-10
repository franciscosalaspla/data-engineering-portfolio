import duckdb
import os

# Crear carpeta output si no existe
os.makedirs("output", exist_ok=True)

# Crear conexión local en memoria
con = duckdb.connect()

# Cargar CSV como tabla DuckDB
con.execute("""
CREATE OR REPLACE TABLE logs AS
SELECT *
FROM read_csv_auto('data/raw/server_logs.csv');
""")

# Consultas principales para guardar como outputs
queries = {
    "summary": """
        SELECT
            COUNT(*) AS total_requests,
            COUNT(DISTINCT user_id) AS unique_users,
            COUNT(DISTINCT endpoint) AS unique_endpoints,
            MIN(timestamp) AS first_request,
            MAX(timestamp) AS last_request
        FROM logs
    """,

    "endpoints_mas_usados": """
        SELECT
            endpoint,
            COUNT(*) AS total_requests
        FROM logs
        GROUP BY endpoint
        ORDER BY total_requests DESC
    """,

    "errores_por_endpoint": """
        SELECT
            endpoint,
            COUNT(*) AS total_errors
        FROM logs
        WHERE status_code >= 400
        GROUP BY endpoint
        ORDER BY total_errors DESC
    """,

    "performance_endpoint": """
        SELECT
            endpoint,
            COUNT(*) AS total_requests,
            ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
            MAX(response_time_ms) AS max_response_time_ms
        FROM logs
        GROUP BY endpoint
        ORDER BY avg_response_time_ms DESC
    """,

    "tendencia_horaria": """
        SELECT
            EXTRACT(HOUR FROM timestamp) AS request_hour,
            COUNT(*) AS total_requests,
            ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms
        FROM logs
        GROUP BY request_hour
        ORDER BY request_hour
    """,

    "ranking_performance": """
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
        ORDER BY performance_rank
    """
}

# Ejecutar y guardar cada resultado
for name, query in queries.items():
    result = con.execute(query).fetchdf()
    output_path = f"output/{name}.csv"
    result.to_csv(output_path, index=False)

    print(f"\nArchivo generado: {output_path}")
    print(result)