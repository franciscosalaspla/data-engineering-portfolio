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

## Implementación y evidencias

<details>
<summary><strong>Ver todas las métricas y el alcance de las validaciones</strong></summary>

| Métrica | Resultado |
|---|---:|
| Ejecución ADF | 3/3 notebooks correctos en 10 min 17 s |
| Publicación Azure SQL | 7 tablas y 953 filas |
| Integridad | PK/FK 7/7 y 0 registros huérfanos |
| Reconciliación | `PASSED` |
| Segunda publicación | `NO_OP`: 953 → 953 y 0 escrituras |
| Modelo Power BI | 7 tablas y 6 relaciones activas |
| KPI validados | 8 transacciones, 4 clientes y 6 cuentas |
| Distribución por canal | Card 3, Mobile 2, Online 2 y ATM 1 |
| Pruebas locales | 42/42 controles de fixtures y 37/37 pruebas |
| Costo observado | USD 0,04; proyección USD 0,29 |
| Control presupuestario | USD 2 mensuales y alerta al 50 % |

Los volúmenes son controlados y buscan demostrar diseño, calidad e idempotencia; no representan una prueba de rendimiento a escala.

</details>


<details>
<summary><strong>Ver etapas, decisiones técnicas, seguridad y control de costos</strong></summary>

| Etapa | Implementación | Decisión técnica |
|---|---|---|
| Ingesta | ECB API, transacciones CSV y clientes/cuentas JSON hacia ADLS | Separar origen y procesamiento para conservar trazabilidad |
| Bronze | Datos raw, schemas explícitos y metadata de auditoría | Preservar fidelidad del origen antes de transformar |
| Silver | Limpieza, tipificación, deduplicación, dominios y cuarentena | Evitar que datos inválidos lleguen al modelo analítico |
| Gold | Conversión a EUR, reconciliación y modelo estrella | Centralizar reglas de negocio y facilitar consumo |
| ADF | Pipeline `pl_project23_medallion_orchestration` con tres notebooks secuenciales | Separar orquestación de transformación distribuida |
| Azure SQL | Siete tablas en el esquema `serving` | Entregar una capa estable para herramientas BI |
| Seguridad | Azure Key Vault y Databricks Secret Scope | Mantener credenciales JDBC fuera del código |
| Operación | Autoapagado, SQL pausado, presupuesto y alerta | Controlar explícitamente el costo cloud |

Modelo de serving:

`dim_date` · `dim_customer` · `dim_account` · `dim_merchant` · `dim_channel` · `dim_currency` · `fact_transaction`

</details>

<details>
<summary><strong>Explorar la estructura del código</strong></summary>

```text
23-azure-adf-databricks-bank-fx/
├── adf/                         # Diseño ADF local versionado
├── config/                      # Configuración Silver y Gold
├── contracts/                   # Contratos de datos
├── data/fixtures/               # Datos sintéticos válidos e inválidos
├── databricks/notebooks/        # Notebooks portables por capa
├── docs/                        # Arquitectura, cloud, evidencias y operación
├── scripts/                     # Ejecución, auditoría y validación local
├── sql/                         # Consultas analíticas sobre Gold
├── src/                         # Ingesta, transformaciones Silver y Gold
├── tests/                       # Suite automatizada local
└── README.md
```

Los datos son sintéticos y el repositorio no contiene credenciales, correos, endpoints completos ni identificadores sensibles.

</details>

<details>
<summary><strong>Consultar la documentación y los anexos</strong></summary>

- [Arquitectura y decisiones técnicas](docs/architecture.md)
- [Implementación end-to-end](docs/cloud_implementation.md)
- [Runbook operativo y de costos](docs/operations_and_cost_runbook.md)
- [Catálogo y alcance de evidencias](docs/evidence_catalog.md)
- [Convenciones de nombres y regiones](docs/naming_and_tagging.md)
- [Anexo — Cómo contar este proyecto en una entrevista](docs/interview_guide.md)

Las pruebas automatizadas corresponden a la implementación local versionada. Las validaciones de ADF, Azure SQL, Power BI y costos fueron comprobaciones manuales cloud. Las capturas se mantienen fuera del repositorio público.

</details>

[Volver al portafolio](../README.md)
