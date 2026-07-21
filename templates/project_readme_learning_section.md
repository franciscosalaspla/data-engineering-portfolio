## X. Documentación de aprendizaje y entrevista

Esta plantilla ya no está pensada para copiar una sección larga dentro de cada README. El README debe funcionar como presentación ejecutiva y técnica del proyecto; el material formativo detallado debe quedar en `docs/` para no sobrecargar la lectura principal.

Usa esta guía cuando un proyecto necesite documentación adicional para estudio, defensa técnica o preparación de entrevistas.

### X.1 README

El README debe:

- explicar el valor profesional del proyecto;
- mostrar arquitectura, problema, objetivo, implementación y resultados reales;
- usar métricas verificables;
- mantener una lectura breve y orientada a reclutadores o entrevistas;
- enlazar documentación complementaria cuando exista.

El README no debe:

- duplicar definiciones extensas;
- incluir respuestas largas de entrevista;
- mezclar implementación real con mejoras futuras sin aclararlo;
- afirmar uso cloud real si el proyecto es local o cloud-style.

### X.2 docs/interview_project_guide.md

Crear este documento cuando el proyecto tenga suficiente contenido para ser defendido en entrevista.

Debe incluir, adaptado al proyecto:

- respuesta breve de 30 segundos;
- explicación de 2 minutos;
- explicación técnica de 5 minutos;
- historia del pipeline o flujo paso a paso;
- decisiones técnicas;
- preguntas probables de entrevista con respuestas modelo;
- errores comunes que se deben evitar;
- cierre conectado al objetivo profesional.

Las respuestas deben distinguir entre:

- lo implementado realmente;
- lo representado conceptualmente;
- lo que sería una mejora futura.

### X.3 docs/learnings_and_concepts.md

Crear este documento cuando el proyecto requiera material de estudio técnico.

Debe incluir, adaptado al proyecto:

- aprendizajes principales por tema;
- diccionario de conceptos aplicado al proyecto;
- mapa de archivos principales;
- flujo completo confirmado desde el código;
- comparación entre implementación local y una versión cloud o productiva, si aplica.

Para cada archivo importante, documentar:

- propósito;
- funciones o clases principales;
- entradas;
- transformaciones o acciones;
- salidas;
- validaciones;
- relación con otros archivos;
- concepto de Data Engineering representado;
- posible equivalente cloud o productivo;
- ejemplo de cómo explicarlo en entrevista.

### X.4 Reglas de calidad documental

- Leer el código antes de documentar.
- Usar resultados reales desde outputs, summaries o una ejecución controlada.
- No inventar métricas.
- No copiar contenido de otros proyectos.
- No convertir todos los proyectos en documentos idénticos.
- Mantener enlaces relativos desde el README hacia `docs/`.
- Evitar duplicación entre README y documentación complementaria.
- Si una tecnología no está implementada, marcarla como concepto relacionado o mejora futura.

### X.5 Enlace recomendado desde README

Cuando existan documentos complementarios, agregar una sección breve como:

```markdown
## Documentación complementaria

- [Cómo presentar el proyecto en una entrevista](docs/interview_project_guide.md)
- [Aprendizajes, conceptos y definiciones](docs/learnings_and_concepts.md)
```
