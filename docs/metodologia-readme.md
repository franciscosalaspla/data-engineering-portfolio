# Metodología de README para proyectos del portafolio

Estructura acordada el 20 de octubre de 2026. El caso de referencia es el [pipeline bancario en Azure](../23-azure-adf-databricks-bank-fx/README.md).

## Objetivo

Conectar problema, solución y resultados en un recorrido fácil de leer. La entrada debe ser comprensible para una persona de negocio o selección; las aperturas permiten profundizar y preparar la entrevista técnica.

## Orden principal

1. **Inicio:** una imagen de portada que presente el problema, la solución y los resultados principales.
2. **Narrativa:** problema de negocio → solución → resultados y su valor.
3. **Arquitectura:** diagrama compacto del recorrido real del dato.
4. **Implementación:** cuatro flechas desplegables, cerradas al abrir el README.

## 1. Inicio

- Una imagen principal, clara y legible.
- Las cifras y tecnologías deben coincidir con el proyecto y el texto.
- Identificar los datos sintéticos y el volumen controlado cuando corresponda.

## 2. Narrativa

Usar encabezados visibles y párrafos breves:

- **El problema de negocio:** una situación concreta y qué le cuesta al equipo trabajar con ella.
- **La solución:** qué se construyó, cómo resuelve el problema y qué permite hacer.
- **Los resultados y su valor para el negocio:** pocas cifras verificadas, acompañadas de una explicación sencilla de su aporte.

El tono debe ser amable, simple y cercano. Tomar la extensión del proyecto Azure como referencia; evitar un catálogo de herramientas o repetir toda la documentación técnica. Distinguir un resultado técnico medido del beneficio de negocio que el diseño permite.

## 3. Arquitectura

- Mostrar las fuentes, almacenamiento, procesamiento, orquestación, publicación y consumo que realmente existan.
- Preferir una disposición vertical compacta con iconos pequeños de las tecnologías.
- Usar el título del entorno dentro del gráfico; por ejemplo, Azure Cloud en el proyecto de referencia.
- Mantener la marca personal de alien pequeña, con fondo transparente, abajo a la derecha.
- No añadir una narrativa debajo del diagrama.
- Conservar una versión editable y comprobar la legibilidad en temas claro y oscuro.

## 4. Flechas desplegables, en este orden

### 1. De los archivos al análisis

Tabla breve de cinco etapas, adaptada al proyecto:

| Etapa y tecnología | Problema | Cómo lo resolví y qué aporta |
|---|---|---|
| Recepción y conservación del origen | Dificultad de entrada | Decisión y aporte |
| Preparación de los datos | Riesgo de calidad | Decisión y aporte |
| Coordinación del flujo | Dependencia entre etapas | Decisión y aporte |
| Publicación | Riesgo de inconsistencias | Decisión y aporte |
| Consumo | Necesidad de análisis | Decisión y aporte |

Usar iconos de 20–24 px junto a las tecnologías. Ajustar las etapas a lo que se implementó.

### 2. Cómo construí el proyecto, paso a paso

Tabla con alrededor de cinco a siete carpetas importantes y enlaces a sus rutas reales:

| Paso y carpeta | Tecnología | Problema → solución |
|---|---|---|
| Definir entradas | Herramienta | Necesidad → decisión |
| Preparar casos | Herramienta | Necesidad → decisión |
| Transformar | Herramienta | Necesidad → decisión |
| Ejecutar y coordinar | Herramienta | Necesidad → decisión |
| Comprobar y consultar | Herramienta | Necesidad → decisión |

Ordenar como un recorrido lógico de construcción; afirmar una cronología histórica solo cuando esté documentada. Explicar brevemente que las pruebas acompañan el desarrollo. Mostrar las carpetas esenciales, no el inventario completo. Identificar diseños locales y versiones portables para no confundirlos con exportaciones del entorno desplegado.

### 3. Las pruebas detrás de las cifras

Tabla concreta de controles, resultados y aporte:

| Control | Resultado | Qué aporta |
|---|---|---|
| Ejecución | Resultado medido | Lectura práctica |
| Publicación | Volumen comprobado | Lectura práctica |
| Integridad y reconciliación | Resultado comprobado | Lectura práctica |
| Repetición de cargas | Resultado comprobado | Lectura práctica |
| Pruebas automatizadas | Resultado y alcance | Lectura práctica |

Mantener unas cinco o seis filas. Separar pruebas locales automatizadas y comprobaciones cloud manuales. No presentar tiempos de una ejecución pequeña como rendimiento a escala ni resultados de prueba como impacto real en una empresa.

### 4. Cómo lo cuento en una entrevista técnica

Un relato breve de aproximadamente un minuto:

1. Problema y contexto del proyecto.
2. Solución y decisiones técnicas principales.
3. Una o dos validaciones o cifras clave.
4. Aporte al análisis o a la operación.

Debe ser natural para decirlo en voz alta, sin exigir que el entrevistador navegue por archivos.

## Enlaces y evidencias

- Enlazar las carpetas o archivos que existen y corresponden al contenido descrito.
- Evitar enlaces a portales privados, recursos eliminados o documentación extensa como requisito para entender el README.
- Incorporar capturas originales que muestren una comprobación concreta, cuando estén disponibles.
- Guardar las capturas al cerrar cada etapa y exportar los artefactos cloud antes de retirar recursos.
- Revisar los datos que se hacen públicos en las capturas y conservar copias de respaldo.
- No reconstruir pruebas visuales ni atribuir validaciones a archivos que no existen.

## Validación antes de publicar

- Comprobar el orden inicio → narrativa → arquitectura → cuatro flechas.
- Verificar rutas de enlaces e imágenes.
- Contrastar las cifras con sus registros y documentación.
- Usar los mismos nombres de tecnologías y etapas en todo el recorrido.
- Mantener claro el alcance de datos, pruebas, implementación local y ejecución cloud.
- Comprobar el despliegue de las cuatro aperturas y la legibilidad del contenido.
- Reutilizar la estructura en los próximos proyectos, adaptando etapas, tecnologías y resultados.
