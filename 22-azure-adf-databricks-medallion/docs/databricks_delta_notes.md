# Notas Databricks y Delta Lake

Parquet mantiene el laboratorio liviano. La versión real usaría tablas Delta, operaciones idempotentes, particionamiento por fecha cuando el volumen lo justifique, `MERGE` para cargas incrementales, constraints y optimización basada en métricas. Los módulos de transformación representan notebooks separados y orquestables.
