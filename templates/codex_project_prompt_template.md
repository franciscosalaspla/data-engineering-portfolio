# Codex Project Prompt Template

Plantilla reutilizable para crear nuevos proyectos del portfolio `data-engineering-portfolio` usando Codex.

Esta plantilla debe completarse antes de iniciar un nuevo proyecto. El objetivo es mantener consistencia entre proyectos, evitar cambios accidentales en proyectos anteriores y asegurar que cada entrega tenga código reproducible, README profesional, outputs ignorados y aprendizajes técnicos documentados.

---

## Prompt base

```text
Quiero crear el Proyecto [NÚMERO] de mi portfolio de Ingeniería de Datos.

Repositorio:
data-engineering-portfolio

Crear una nueva rama desde main actualizado:
codex/[numero-nombre-del-proyecto]

Nombre del proyecto:
[numero-nombre-del-proyecto]

Card / ejercicio asociado:
[Pegar aquí la card completa o descripción del ejercicio]

Objetivo:
Construir un proyecto práctico de Ingeniería de Datos alineado con la card entregada, manteniendo una estructura profesional, reproducible y defendible técnicamente.

Contexto del portfolio:
Este proyecto debe seguir el estándar aplicado en proyectos anteriores:
- README profesional y concreto.
- Código modular.
- Pipeline reproducible.
- Outputs ignorados por Git.
- Sección de aprendizajes técnicos.
- Sin métricas falsas.
- Sin afirmar uso de herramientas reales si solo se simulan.
- Sin subir CSV, Parquet, JSON generados ni archivos pesados.

Restricciones:
- No usar servicios cloud reales salvo que la card lo pida explícitamente y se confirme.
- No usar credenciales.
- No subir datos generados.
- No modificar proyectos anteriores.
- No modificar README principal salvo agregar una línea breve del nuevo proyecto si corresponde.
- No hacer merge.

Estructura esperada del proyecto:
Definir una estructura adecuada según la card, usando este patrón como base:

[numero-nombre-del-proyecto]/
├── app/
├── data/
│   ├── raw/.gitkeep
│   ├── processed/.gitkeep
│   └── analytics/.gitkeep
├── queries/            # si aplica
├── docs/               # si aplica
├── output/.gitkeep
├── README.md
├── requirements.txt
└── .gitignore

Requisitos del README:
Debe seguir esta estructura, adaptada al proyecto:

# [NÚMERO] - [Nombre del proyecto]

## [Subtítulo asociado a la card]

## 1. Valor del proyecto
Explicar por qué este proyecto importa desde el punto de vista de Ingeniería de Datos y negocio.

## 2. Problema y enfoque
Explicar de forma narrativa:
- qué problema aborda;
- por qué no basta con una solución simple;
- qué enfoque técnico se usó.

## 3. Objetivo
Explicar qué se construyó, con qué herramientas y qué limitaciones tiene.

## 4. Arquitectura del proyecto
Incluir diagrama Mermaid si aplica.

## 5. Estructura del proyecto
Incluir árbol de carpetas y componentes principales.

## 6. Flujo del pipeline
Explicar el flujo paso a paso, idealmente con un flujo visual en texto.

## 7. Resultados de la implementación
Usar formato:
- Situación
- Tarea
- Acciones
- Resultados validados

No inventar resultados. Usar solo resultados generados por el pipeline.

## 8. Conceptos técnicos aplicados
Tabla con conceptos técnicos relevantes del proyecto.

## 9. Aprendizajes técnicos del proyecto
Usar la plantilla:
templates/project_readme_learning_section.md

Adaptarla al proyecto:
- conceptos clave;
- archivos más importantes;
- funciones destacables;
- qué debo saber explicar técnicamente;
- aprendizaje principal;
- resumen técnico corto.

Código:
- Crear scripts modulares.
- Incluir función main() cuando corresponda.
- Usar logging.
- Generar output/pipeline_summary.json o equivalente.
- Manejar errores si aplica.
- Separar lógica de generación, transformación, validación y ejecución.

Validaciones:
Ejecutar:
python3 -m py_compile [scripts principales]

Crear entorno:
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

Ejecutar pipeline o script principal:
python3 app/run_pipeline.py

Validar:
cat output/pipeline_summary.json
git status --short

Criterios de aceptación:
- Pipeline ejecuta correctamente.
- README claro y profesional.
- Outputs generados ignorados por Git.
- No datos pesados versionados.
- No métricas falsas.
- Sección de aprendizajes incluida.
- Proyecto alineado con la card.
- PR draft creado.
- No hacer merge.

Commit:
Add project [NÚMERO]: [nombre del proyecto]

Crear PR draft.
No hacer merge.
```
