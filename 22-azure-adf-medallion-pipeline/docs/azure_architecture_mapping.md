# Azure Architecture Mapping

This project is a local, cost-free simulation of an Azure Data Engineering pipeline. It does not deploy resources to Azure, does not require credentials, and does not use secrets.

| Local component | Azure-style equivalent | Purpose |
|---|---|---|
| `app/adf_orchestrator.py` | Azure Data Factory pipeline | Coordinates activities, dependencies, monitoring fields, and final run status |
| `data/source/` | Source systems or landing inputs | Stores synthetic CSV files that represent operational business sources |
| `data/bronze/` | ADLS Bronze | Preserves raw-ish ingested data with traceability columns |
| `data/silver/` | ADLS Silver / Databricks transformations | Stores cleaned, typed, deduplicated, and enriched datasets |
| `data/gold/` | ADLS Gold / Datamarts | Stores analytics-ready datamarts for downstream reporting |
| `app/quality_checks.py` | Data Quality checks | Validates critical fields, referential integrity, duplicates, and business rules |
| `output/adf_pipeline_run_summary.json` | ADF monitor / run history | Provides execution evidence with activities, dependencies, rows, duration, and status |
| GitHub PR workflow | Collaboration and change control | Supports review, versioning, and controlled delivery of pipeline changes |

The design keeps the architecture honest: it uses Azure vocabulary and design patterns, but all processing runs locally with Python and Parquet files.
