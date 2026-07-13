# Loop Engineering aplicado al pipeline dockerizado

## Objetivo

Ejecutar el proyecto `17-dbt-professional-ecommerce` dentro de un contenedor Docker para asegurar que el pipeline dbt pueda correr de forma reproducible, auditable y con una condición de parada clara.

El objetivo del loop no es reemplazar el proyecto 17. El objetivo es envolverlo con una capa operativa que permita:

```text
preparar ambiente
ejecutar dbt
verificar resultados
registrar evidencia
habilitar revisión humana
```

## Activación

El loop se activa con Docker Compose desde la carpeta del proyecto 18:

```bash
docker compose up --build
```

Docker construye una imagen Python slim que copia:

```text
17-dbt-professional-ecommerce
18-pipeline-dockerizado-agent-loop
```

Esto permite ejecutar el pipeline del proyecto 17 sin duplicar modelos dbt.

## Ejecución

La ejecución principal ocurre en:

```text
app/run_pipeline.py
```

El script ejecuta estos comandos sobre el proyecto 17:

```bash
dbt debug
dbt seed --full-refresh
dbt build
dbt docs generate
```

Cada paso registra:

```text
nombre del paso
comando ejecutado
started_at
finished_at
duración
return_code
status
stdout
stderr
```

## Verificación

La verificación ocurre en dos momentos.

Primero, `app/health_check.py` valida:

```text
variables de entorno requeridas
existencia de DBT_PROJECT_DIR
existencia de dbt_project.yml
existencia de profiles.yml
existencia de seeds/
existencia de dbt en el contenedor
permisos de escritura en OUTPUT_DIR
```

Luego, `app/run_pipeline.py` verifica el resultado de cada comando dbt usando su `return_code`.

También registra si existen artefactos esperados:

```text
ecommerce_analytics.duckdb
target/manifest.json
target/catalog.json
output/pipeline_run_summary.json
```

## Condición de parada

La condición de parada depende de `FAIL_FAST`.

Con `FAIL_FAST=true`, el loop se detiene cuando falla el primer paso crítico.

Con `FAIL_FAST=false`, el pipeline puede seguir ejecutando pasos posteriores aunque uno haya fallado, dejando evidencia completa para diagnóstico.

El estado final queda como:

```text
PASSED -> todos los pasos ejecutados terminaron con return_code 0
FAILED -> al menos un paso terminó con return_code distinto de 0
```

## Registro

El registro principal queda en:

```text
output/pipeline_run_summary.json
```

Ese archivo resume:

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

## Revisión humana

La revisión humana ocurre después de la ejecución. Una persona debe revisar:

```text
final_status
pasos fallidos
stdout/stderr del paso fallido
artefactos dbt generados
next_actions recomendadas
```

Esto evita tratar la automatización como una caja negra. El pipeline ejecuta y registra, pero la interpretación final de fallas, tests y próximos cambios sigue siendo responsabilidad humana.

## Rol de Codex, ChatGPT y Codespaces

Codex ayuda a construir, revisar y mantener el loop:

```text
crear estructura del proyecto
implementar scripts
revisar errores
proponer mejoras
generar documentación técnica
```

ChatGPT funciona como apoyo de razonamiento técnico:

```text
explicar decisiones
preparar respuestas para entrevistas
analizar trade-offs
convertir resultados técnicos en narrativa profesional
```

Codespaces funciona como ambiente reproducible de desarrollo:

```text
clonar el repositorio
ejecutar comandos Git
correr validaciones locales
probar Docker Compose si Docker está disponible
versionar cambios en una rama
abrir PR para revisión
```

El loop completo combina automatización y criterio humano:

```text
Codex implementa
Docker ejecuta
dbt valida
JSON registra
persona revisa
GitHub versiona
```
