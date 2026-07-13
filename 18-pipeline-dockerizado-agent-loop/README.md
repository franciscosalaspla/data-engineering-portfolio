# Proyecto 18 - Pipeline Dockerizado con Agent Loop

## Objetivo

Este proyecto dockeriza el pipeline dbt del proyecto `17-dbt-professional-ecommerce` para ejecutarlo de forma reproducible con Docker y Docker Compose.

El foco no está en crear nuevos modelos dbt. El foco está en construir una capa operativa profesional alrededor del proyecto 17:

```text
health check
ejecución dbt reproducible
registro JSON
condición de parada
revisión humana
```

## Valor de negocio

Un pipeline analítico no solo debe transformar datos correctamente. También debe poder ejecutarse en un ambiente controlado, dejar evidencia del resultado y permitir diagnosticar fallas.

Este proyecto demuestra cómo pasar de un proyecto dbt local a un flujo más cercano a operación real:

```text
menos dependencia de la máquina del desarrollador
configuración por variables de entorno
ejecución con un solo comando
logs y resumen trazable
artefactos dbt generados de forma reproducible
```

## Diferencia entre proyecto 17 y proyecto 18

| Proyecto | Rol | Qué demuestra |
| --- | --- | --- |
| `17-dbt-professional-ecommerce` | Proyecto analítico dbt | Modelado staging, intermediate, marts, snapshots, tests y documentación |
| `18-pipeline-dockerizado-agent-loop` | Wrapper operativo | Docker, Docker Compose, health checks, ejecución reproducible y Loop Engineering |

El proyecto 18 usa el proyecto 17 como base. No duplica sus modelos, seeds ni snapshots.

## Arquitectura

```text
data-engineering-portfolio/
|-- 17-dbt-professional-ecommerce/
|   |-- dbt_project.yml
|   |-- profiles.yml
|   |-- seeds/
|   |-- models/
|   `-- snapshots/
`-- 18-pipeline-dockerizado-agent-loop/
    |-- app/
    |   |-- health_check.py
    |   `-- run_pipeline.py
    |-- docs/
    |   `-- LOOP_ENGINEERING.md
    |-- output/
    |   `-- .gitkeep
    |-- Dockerfile
    |-- docker-compose.yaml
    |-- requirements.txt
    |-- .dockerignore
    |-- .gitignore
    |-- .env.example
    `-- README.md
```

## Flujo del pipeline

El contenedor ejecuta:

```text
health_check.py
    -> dbt debug
    -> dbt seed --full-refresh
    -> dbt build
    -> dbt docs generate
    -> output/pipeline_run_summary.json
```

## Variables de entorno

Las variables se definen en `.env.example`:

| Variable | Descripción |
| --- | --- |
| `PIPELINE_NAME` | Nombre lógico del pipeline |
| `ENVIRONMENT` | Ambiente de ejecución |
| `DBT_PROJECT_DIR` | Ruta del proyecto dbt 17 dentro del contenedor |
| `DBT_PROFILES_DIR` | Ruta donde vive `profiles.yml` |
| `OUTPUT_DIR` | Ruta donde se escribe el resumen JSON |
| `FAIL_FAST` | Detiene el loop ante la primera falla crítica |
| `LOG_LEVEL` | Nivel de logging |

## Cómo ejecutar con Docker

Desde la carpeta del proyecto:

```bash
cd 18-pipeline-dockerizado-agent-loop
docker compose up --build
```

El resumen final se genera en:

```text
output/pipeline_run_summary.json
```

## Cómo validar

Validar configuración de Docker Compose:

```bash
docker compose config
```

Ejecutar solo el health check:

```bash
docker compose run --rm pipeline python app/health_check.py
```

Ejecutar el pipeline completo:

```bash
docker compose up --build
```

Revisar el resumen:

```bash
cat output/pipeline_run_summary.json
```

Validar scripts Python localmente:

```bash
python3 -m py_compile app/health_check.py app/run_pipeline.py
```

## Output generado

`output/pipeline_run_summary.json` contiene:

```text
pipeline_name
environment
started_at
finished_at
final_status
steps
return_code por paso
duración por paso
stop_condition
outputs_generated
next_actions
```

## Loop Engineering aplicado

El loop queda documentado en:

```text
docs/LOOP_ENGINEERING.md
```

Resumen del loop:

```text
Objetivo
    Ejecutar de forma reproducible el proyecto dbt 17.

Activación
    docker compose up --build

Ejecución
    dbt debug, dbt seed, dbt build y dbt docs generate.

Verificación
    health check, return codes, artefactos dbt y resumen JSON.

Condición de parada
    todos los pasos pasan o falla un paso crítico.

Registro
    output/pipeline_run_summary.json

Revisión humana
    análisis del estado final, errores, artefactos y next_actions.
```

## Cómo contar este proyecto en entrevista

### Hook

Dockericé un proyecto dbt profesional de e-commerce para ejecutarlo de forma reproducible con Docker Compose, agregando health check, variables de entorno y un resumen JSON trazable.

### Situación

El proyecto 17 ya resolvía la parte analítica con dbt: seeds, staging, intermediate, marts, snapshots y tests. El siguiente problema era operacional: cómo ejecutar ese pipeline de forma consistente fuera de mi máquina.

### Tarea

Crear una capa de ejecución reproducible que pudiera levantar el ambiente, validar configuración, ejecutar dbt y dejar evidencia del resultado.

### Acciones

* Creé un `Dockerfile` con imagen Python slim.
* Configuré `docker-compose.yaml` para ejecutar el pipeline con un solo comando.
* Implementé `health_check.py` para validar ambiente, rutas, dbt y permisos de escritura.
* Implementé `run_pipeline.py` para ejecutar `dbt debug`, `dbt seed --full-refresh`, `dbt build` y `dbt docs generate`.
* Generé `pipeline_run_summary.json` con estados, return codes, duración por paso, outputs y recomendaciones.
* Documenté el loop de ejecución, verificación, parada, registro y revisión humana.

### Resultado

El proyecto permite ejecutar el pipeline dbt del proyecto 17 dentro de Docker, con trazabilidad clara del estado final. Esto demuestra una evolución desde Analytics Engineering hacia operación reproducible de pipelines de datos.

## Decisiones técnicas

| Decisión | Motivo |
| --- | --- |
| Wrapper sobre proyecto 17 | Evita duplicar modelos dbt y mantiene separación de responsabilidades |
| Docker con Python slim | Imagen simple y liviana para ejecutar dbt |
| `docker compose up --build` | Comando estándar y fácil de reproducir |
| Variables de entorno | Permiten ajustar rutas y comportamiento sin cambiar código |
| Health check explícito | Detecta problemas de ambiente antes de ejecutar dbt |
| JSON como registro | Facilita auditoría, debugging y evidencia para entrevistas |
| `FAIL_FAST` configurable | Permite elegir entre detener ante falla o recolectar más evidencia |

## Posibles mejoras

* Publicar la imagen en GitHub Container Registry.
* Agregar CI con GitHub Actions para ejecutar `docker compose up --build`.
* Persistir artefactos dbt como evidencia de ejecución.
* Agregar alertas si `final_status` termina en `FAILED`.
* Separar ambientes `dev`, `qa` y `prod`.
* Integrar este contenedor como tarea en Airflow.
