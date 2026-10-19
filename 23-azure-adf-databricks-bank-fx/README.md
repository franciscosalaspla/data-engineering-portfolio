![Del doble conteo a cifras confiables: problema, solución y resultados del pipeline bancario en Azure.](./docs/images/pipeline-azure-aprobada.png)

**Cuando las cifras no cuadran, el negocio termina esperando.**

En un cierre de gestión, el equipo necesita entender cuánto dinero se movió, por qué canales y en qué monedas. Si los reportes entregan cifras distintas, la conversación termina girando alrededor de cuál está bien.

Una operación de 100 € que aparece dos veces puede convertirse en 200 €. Una cuenta inexistente puede dejar movimientos fuera del análisis. Y comparar monedas sin una conversión consistente puede llevar a conclusiones equivocadas.

Resolver esas diferencias obliga a revisar archivos y reconstruir cálculos. El análisis del negocio queda esperando.

**La solución: resolver las diferencias antes del reporte**

Con ese escenario como punto de partida, construí un pipeline bancario en Azure con Databricks que conecta las fuentes y revisa la información antes de publicarla.

El proceso conserva los datos originales, comprueba duplicados y relaciones, y convierte los montos a una moneda común. Los registros que necesitan atención quedan separados, con su motivo identificado.

Así, el equipo cuenta con un recorrido para investigar una diferencia y una base común para analizar movimientos, clientes y canales.

También incorporé una condición práctica: repetir una carga con los mismos datos debe conservar el resultado.

**Los resultados y su valor para el negocio**

La publicación dejó **siete tablas y 953 filas totales**, con sus relaciones validadas y **cero registros huérfanos**.

Al publicar nuevamente, se mantuvieron **953 filas y hubo cero escrituras nuevas**. Repetir el proceso conservó las cifras.

Los tres notebooks coordinados completaron su ejecución en **10 min 17 s**.

Estos controles permiten concentrar la revisión en los casos identificados, explicar el origen de una cifra y repetir una publicación sin duplicar operaciones.

Para el negocio, el aporte está en disponer de información consistente para comparar canales y montos. Para el equipo, en tener un camino claro para responder cuando alguien pregunta de dónde salió un resultado.

Proyecto validado con datos sintéticos y volumen controlado.

## Arquitectura

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./docs/images/arquitectura-azure-dark.png">
  <img src="./docs/images/arquitectura-azure-light.png" alt="Azure Cloud: arquitectura vertical con control lateral, iconos de las tecnologías y marca personal de alien abajo a la derecha." width="736">
</picture>

## Implementación

<details>
<summary><strong>Cómo lo llevé a la práctica</strong></summary>

Primero conecté las fuentes y conservé una copia de los datos originales para poder revisar cualquier transformación. Después separé el procesamiento en tres capas: recibir los datos, validarlos y preparar el modelo de análisis.

El paso clave fue decidir qué podía avanzar. Los registros con errores quedaron en cuarentena con su motivo; los válidos continuaron hacia la conversión de monedas y el modelo estrella.

Con las capas funcionando, coordiné los tres notebooks desde Data Factory y publiqué el resultado en Azure SQL para consumirlo en Power BI. Antes de cerrar, comprobé las relaciones y contrasté las cifras entre Gold y SQL.

La última prueba fue volver a publicar los mismos datos: el proceso reconoció que no había cambios y evitó nuevas escrituras.

</details>

[Volver al portafolio](../README.md)
