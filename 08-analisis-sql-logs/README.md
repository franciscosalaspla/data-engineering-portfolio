# Análisis SQL de Logs de Servidor

Proyecto práctico de ingeniería de datos enfocado en analizar logs de servidor utilizando SQL y DuckDB.

El objetivo es cargar datos desde un archivo CSV, consultarlos como una tabla SQL, analizar tráfico, errores, tiempos de respuesta y generar outputs reutilizables para análisis técnico y de negocio.

## Objetivo del proyecto

Construir un flujo de análisis SQL que permita:

* Cargar logs desde un archivo CSV.
* Consultar los datos usando DuckDB.
* Analizar volumen de requests.
* Identificar endpoints más utilizados.
* Detectar errores por endpoint.
* Medir performance por tiempo de respuesta.
* Analizar tendencia horaria.
* Aplicar CTEs y Window Functions.
* Guardar resultados en archivos CSV.

## Caso de negocio

Este proyecto simula el análisis de logs de una aplicación web.

El equipo técnico necesita entender qué endpoints reciben más tráfico, cuáles presentan errores y cuáles tienen peor tiempo de respuesta, para priorizar mejoras de performance y experiencia de usuario.

Preguntas respondidas:

* ¿Cuántos requests hubo?
* ¿Cuántos usuarios únicos participaron?
* ¿Cuáles fueron los endpoints más usados?
* ¿Qué endpoints concentraron más errores?
* ¿Qué endpoints fueron más lentos?
* ¿En qué horarios hubo mayor tráfico?
* ¿Qué endpoints deberían priorizarse para optimización?

## Stack utilizado

* SQL
* DuckDB
* Python
* CSV
* Git / GitHub
* GitHub Codespaces

## Estructura del proyecto

```text
08-analisis-sql-logs/
├── data/
│   └── raw/
│       └── server_logs.csv
├── output/
│   ├── endpoints_mas_usados.csv
│   ├── errores_por_endpoint.csv
│   ├── performance_endpoint.csv
│   ├── ranking_performance.csv
│   ├── summary.csv
│   └── tendencia_horaria.csv
├── sql/
│   └── analysis.sql
├── src/
│   └── run_analysis.py
├── README.md
└── requirements.txt
```

## Dataset

El archivo original se encuentra en:

```text
data/raw/server_logs.csv
```

Columnas principales:

| Columna            | Descripción                         |
| ------------------ | ----------------------------------- |
| `timestamp`        | Fecha y hora del request            |
| `endpoint`         | Ruta o servicio consultado          |
| `method`           | Método HTTP utilizado               |
| `status_code`      | Código de respuesta del servidor    |
| `response_time_ms` | Tiempo de respuesta en milisegundos |
| `user_id`          | Identificador del usuario           |
| `ip_address`       | Dirección IP del request            |

## Proceso de análisis

### 1. Carga de datos

Se utiliza DuckDB para leer el archivo CSV y convertirlo en una tabla SQL llamada `logs`.

```sql
CREATE OR REPLACE TABLE logs AS
SELECT *
FROM read_csv_auto('data/raw/server_logs.csv');
```

### 2. Exploración general

Se calcula:

* Total de requests.
* Usuarios únicos.
* Endpoints únicos.
* Primera fecha registrada.
* Última fecha registrada.

Resultado principal:

```text
total_requests: 20
unique_users: 18
unique_endpoints: 9
```

### 3. Análisis de métodos HTTP

Se identificó que la mayoría del tráfico corresponde a requests `GET`.

```text
GET  → 13 requests
POST → 7 requests
```

Interpretación:

* `GET`: navegación o consulta de información.
* `POST`: acciones del usuario, como login, carrito o checkout.

### 4. Análisis de errores

Se analizaron los endpoints con códigos de error `>= 400`.

Resultado:

```text
/api/search    → 2 errores
/api/checkout  → 1 error
/api/reports   → 1 error
/api/export    → 1 error
```

Interpretación:

`/api/search` es el endpoint con mayor cantidad de errores y también el más utilizado, por lo que debería ser priorizado para revisión técnica.

### 5. Análisis de performance

Se calcularon tiempos promedio y máximos de respuesta por endpoint.

Endpoints más lentos:

```text
/api/export    → 2500 ms promedio
/api/reports   → 1975 ms promedio
/api/checkout  → 1350 ms promedio
/api/search    → 1143.33 ms promedio
```

Interpretación:

Aunque `/api/export` aparece como el más lento, tiene solo 1 request. En cambio, `/api/search` combina alto tráfico, errores y latencia, por lo que representa una prioridad más relevante.

### 6. Tendencia horaria

Se agrupó el tráfico por hora para identificar volumen y performance.

Hallazgos:

```text
08:00 → mayor volumen de requests
10:00 → alto tiempo promedio de respuesta
11:00 → alto tiempo promedio de respuesta
15:00 → request puntual muy lento
```

### 7. Window Functions

Se utilizó `RANK()` para ordenar endpoints según tiempo promedio de respuesta.

```sql
RANK() OVER (ORDER BY avg_response_time_ms DESC) AS performance_rank
```

También se utilizó `LAG()` para comparar cada endpoint contra el anterior en el ranking.

```sql
LAG(avg_response_time_ms) OVER (ORDER BY performance_rank)
```

Esto permite analizar diferencias relativas entre endpoints y detectar brechas importantes de performance.

## Outputs generados

Los resultados se guardan en la carpeta `output/`.

| Archivo                    | Descripción                                   |
| -------------------------- | --------------------------------------------- |
| `summary.csv`              | Resumen general del dataset                   |
| `endpoints_mas_usados.csv` | Ranking de endpoints por cantidad de requests |
| `errores_por_endpoint.csv` | Errores agrupados por endpoint                |
| `performance_endpoint.csv` | Tiempo promedio y máximo por endpoint         |
| `tendencia_horaria.csv`    | Requests y tiempo promedio por hora           |
| `ranking_performance.csv`  | Ranking de endpoints por performance          |

## Cómo ejecutar el proyecto

Desde la carpeta del proyecto:

```bash
cd 08-analisis-sql-logs
pip install -r requirements.txt
python src/run_analysis.py
```

## Principales hallazgos

* El dataset contiene 20 requests, 18 usuarios únicos y 9 endpoints.
* `/api/search` fue el endpoint más utilizado.
* `/api/search` también concentró la mayor cantidad de errores.
* `/api/export`, `/api/reports`, `/api/checkout` y `/api/search` fueron los endpoints con peor performance.
* `/api/search` debería ser priorizado porque combina alto uso, errores y latencia.
* `/api/checkout` también es crítico porque impacta directamente en conversión.
* La mayor actividad ocurrió a las 08:00.
* Los peores tiempos promedio se observaron a las 10:00, 11:00 y 15:00.

## Recomendaciones

1. Priorizar la revisión técnica de `/api/search`, ya que concentra alto tráfico, errores y lentitud.
2. Revisar `/api/checkout`, porque cualquier error o demora puede afectar directamente la conversión.
3. Analizar `/api/reports` y `/api/export`, ya que presentan altos tiempos de respuesta.
4. Monitorear horarios con mayor latencia para detectar posibles problemas de carga o endpoints pesados.

## Aprendizajes

* DuckDB permite ejecutar SQL directamente sobre archivos CSV.
* Separar SQL y Python mejora la organización del proyecto.
* Los logs permiten analizar comportamiento técnico y experiencia de usuario.
* No basta con mirar el endpoint más lento; también hay que considerar volumen, errores e impacto de negocio.
* Las Window Functions como `RANK()` y `LAG()` ayudan a construir análisis más avanzados.
