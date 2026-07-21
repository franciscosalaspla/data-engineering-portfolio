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
- Documentación enfocada en valor, arquitectura, implementación y resultados reales.
- Material de estudio detallado en `docs/`, no sobrecargado en el README.
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

Cuando el proyecto tenga suficiente profundidad técnica, evaluar crear también:

```text
docs/interview_project_guide.md
docs/learnings_and_concepts.md
```

Estos documentos deben adaptarse al proyecto. No son obligatorios si duplican contenido o vuelven la entrega innecesariamente pesada.

Requisitos del README:
Debe seguir el estándar editorial del Proyecto 21, adaptado al tipo de proyecto. No fuerces secciones si no aportan valor, pero conserva esta lógica narrativa:

# [NÚMERO] - [Nombre del proyecto]

## 1. Valor del proyecto
Abrir con un párrafo fuerte y concreto:
- qué se construyó;
- qué habilidad profesional demuestra;
- qué volumen, herramienta o evidencia real respalda el proyecto;
- qué limitaciones honestas existen, por ejemplo si es cloud-style local y no cloud real.

Evitar frases genéricas como "este proyecto ayuda a aprender". Conectar el proyecto con una capacidad defendible en entrevistas técnicas.

## 2. Arquitectura del proyecto y flujo del pipeline
Explicar la arquitectura de forma visual y breve:
- diagrama Mermaid si aporta claridad;
- flujo ejecutado paso a paso;
- componentes principales y su responsabilidad;
- equivalencias cloud solo cuando sean conceptuales y honestas.

## 3. Problema
Explicar en un párrafo:
- qué problema de datos resuelve;
- por qué no basta con mover archivos o ejecutar un script simple;
- qué riesgo evita el diseño técnico.

## 4. Objetivo
Usar una frase inicial y una lista corta con objetivos verificables:
- datasets o fuentes procesadas;
- capas construidas;
- validaciones ejecutadas;
- outputs o datamarts generados;
- evidencia reproducible.

## 5. Implementación
Usar una tabla clara:

| Etapa | Acción realizada | Evidencia |
| --- | --- | --- |

Cada evidencia debe apuntar a archivos, queries, tablas, summaries o outputs reales.

## 6. Resultados
Usar métricas reales generadas por el pipeline o comprobadas en outputs:
- estado final;
- filas procesadas;
- checks ejecutados;
- queries, modelos o datamarts generados;
- mejoras medidas, si aplica.

Incluir una tabla de métricas y, cuando aplique, una segunda tabla con resultados específicos. Agregar una interpretación breve de los resultados, sin inflar conclusiones.

## 7. Estructura del proyecto
Cerrar con árbol de carpetas y una nota sobre qué artefactos se versionan y cuáles se regeneran localmente.

Secciones opcionales:
- Conceptos técnicos aplicados, si el proyecto necesita material de estudio.
- Decisiones técnicas, si hubo tradeoffs relevantes.
- Guía de ejecución, si el proyecto no es evidente desde el README o si el usuario la pide.
- Documentación complementaria, con enlaces a guías en `docs/` cuando existan.
- Aprendizajes técnicos breves solo si aportan valor. El detalle debe quedar en `docs/learnings_and_concepts.md`.

Reglas editoriales:
- No convertir todos los READMEs en textos idénticos.
- No copiar métricas ni narrativa de otros proyectos.
- No inventar resultados ni afirmar mejoras no medidas.
- No decir que se usó AWS, Azure, GCP, Databricks, Airflow, dbt u otra herramienta real si solo se construyó una simulación local.
- Para proyectos cloud-style, declarar explícitamente si no se usaron credenciales, secretos, recursos cloud ni costos.
- Priorizar evidencia, arquitectura, decisiones técnicas e impacto profesional.
- Mantener redacción concreta, técnica y amigable.
- Mantener el README ejecutivo. Las explicaciones largas de entrevista, definiciones y aprendizaje van en `docs/`.

Requisitos para documentación complementaria:
- Leer realmente todos los archivos de `app/`, `src/`, `queries/` o equivalentes antes de documentar.
- Explicar la función de cada componente con base en el código real.
- Documentar el orden de ejecución confirmado desde el entrypoint del pipeline.
- Incluir resultados verificables desde summaries, outputs o una ejecución controlada del pipeline.
- Diferenciar con claridad entre implementación real, simulación conceptual y mejora futura.
- No afirmar uso cloud real cuando el proyecto corre localmente.
- No decir que se usó una tecnología como Delta Lake, PySpark, Key Vault, Purview o CI/CD si solo aparece como equivalencia o recomendación futura.

Si se crea `docs/interview_project_guide.md`, incluir:
- presentación de 30 segundos;
- explicación de 2 minutos;
- explicación técnica de 5 minutos;
- historia del pipeline paso a paso;
- decisiones técnicas;
- preguntas probables de entrevista con respuestas modelo;
- errores que conviene evitar al explicar el proyecto;
- cierre conectado al perfil Data Engineer.

Si se crea `docs/learnings_and_concepts.md`, incluir:
- aprendizajes principales por tema;
- diccionario de conceptos aplicado al proyecto;
- mapa de archivos principales;
- flujo completo real;
- comparación entre implementación local y posible versión cloud real.

El README debe enlazar estos documentos si existen, pero no duplicar su contenido.

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
- Resultados reales y comprobables.
- Arquitectura, implementación y resultados explicados con evidencia.
- Documentación complementaria creada cuando el proyecto lo justifique.
- README con enlaces a docs complementarios, sin duplicar material extenso.
- Proyecto alineado con la card.
- PR draft creado.
- No hacer merge.

Commit:
Add project [NÚMERO]: [nombre del proyecto]

Crear PR draft.
No hacer merge.
```
