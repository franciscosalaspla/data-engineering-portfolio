# Codex Project Prompt Template

Plantilla reutilizable para crear proyectos del portfolio `data-engineering-portfolio`. Usa el Proyecto 21 como referencia editorial y adapta el contenido al caso real.

## Prompt base

```text
Quiero crear el Proyecto [NÚMERO] de mi portfolio de Ingeniería de Datos.

Repositorio:
data-engineering-portfolio

Rama:
codex/[numero-nombre-del-proyecto]

Objetivo:
Construir un proyecto reproducible y defendible técnicamente, alineado con [CARD O DESCRIPCIÓN].

Reglas:
- Leer todo el código y los outputs antes de documentar.
- No modificar proyectos anteriores.
- No versionar datos u outputs generados.
- No inventar métricas, funciones ni tecnologías.
- Diferenciar implementación real, simulación local y mejora futura.
- No afirmar uso cloud real si el proyecto corre localmente.
- No hacer merge.

README:
Mantenerlo ejecutivo, concreto y basado en evidencia. Seguir la lógica del Proyecto 21, adaptándola cuando una sección no aporte valor:

1. Valor del proyecto.
2. Arquitectura y flujo.
3. Problema.
4. Objetivo.
5. Implementación.
6. Resultados verificables.
7. Estructura del proyecto.

El README debe explicar qué se construyó, qué capacidad demuestra, qué problema resuelve y qué resultados produjo. Usar Mermaid o tablas solo cuando mejoren la comprensión.

Documentación estándar:
Si el proyecto tiene suficiente profundidad técnica, crear únicamente:

docs/learnings_and_concepts.md
docs/interview_project_guide.md

No crear documentos adicionales salvo que tengan un propósito claramente distinto y el usuario los solicite.

Documento técnico — docs/learnings_and_concepts.md:
- Qué se construyó y resultado validado.
- Flujo real del pipeline.
- Mapa concreto de archivos, funciones o clases principales.
- Entradas, acciones, salidas y relaciones.
- Código o decisiones destacables.
- Conceptos y definiciones aplicados.
- Aprendizajes principales.
- Implementación local frente a equivalente cloud/productivo.
- Limitaciones y mejoras futuras.

Debe ser breve, amigable y útil para estudiar. No copiar todo el código.

Documento de entrevista — docs/interview_project_guide.md:
- Hook de una frase.
- Versión oral de 1 minuto.
- Exactamente 3 preguntas de entrevista con respuestas modelo.

La presentación de 1 minuto debe seguir esta secuencia:
valor/problema → objetivo → acciones o implementación → resultados → tecnologías y aprendizajes.

No incluir presentaciones de 3 o 5 minutos. La guía de entrevista debe ser breve, fácil de memorizar y útil para practicar una respuesta oral. Usar solamente métricas verificadas y distinguir lo implementado de lo conceptual.

Enlaces:
El README debe enlazar solamente los documentos que realmente existan.

Validaciones:
- Ejecutar el pipeline o usar evidencia vigente y confiable.
- Confirmar orden desde el entrypoint.
- Verificar métricas y enlaces.
- Confirmar que scripts, datos y outputs no cambiaron por documentación.
- Ejecutar git diff --check y revisar git status.
- Crear PR draft y no hacer merge.
```

## Criterio editorial

El README vende el valor del proyecto. El documento técnico ayuda a entenderlo. El documento de entrevista ayuda a contarlo. Evitar duplicación y archivos de documentación que no aporten una función distinta.
