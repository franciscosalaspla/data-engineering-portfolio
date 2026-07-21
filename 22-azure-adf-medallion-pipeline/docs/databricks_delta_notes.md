# Databricks and Delta Lake Notes

This project uses local Python and pandas to keep the implementation reproducible without cloud services. The design is intentionally Databricks-style, not a claim that the workload was deployed to Databricks.

## Spark and Databricks Conceptual Mapping

In a real Azure Data Engineering setup, the transformation steps in `app/silver_transformations.py` and `app/gold_datamart.py` could be implemented as Databricks notebooks or jobs using PySpark and Spark SQL.

Local equivalents in this project:

- pandas DataFrames represent tabular transformation logic;
- Parquet files represent analytics-oriented storage;
- the orchestrator represents a pipeline calling transformation jobs;
- Gold outputs represent curated datamarts for BI or analytics.

## Delta Lake Conceptual Mapping

Delta Lake would add transaction logs, schema enforcement, time travel, merge/upsert support, and stronger reliability guarantees on top of files in the lake.

This project writes Parquet because it is lightweight and local. Conceptually:

- Bronze Parquet files map to raw Delta tables;
- Silver Parquet files map to cleaned Delta tables;
- Gold Parquet files map to curated Delta tables or datamarts.

## Medallion Architecture

The medallion design separates responsibility by layer:

- Bronze: preserve source data with traceability.
- Silver: clean, type, deduplicate, validate, and enrich.
- Gold: aggregate and publish business-ready outputs.

This separation helps prevent source errors from flowing directly into analytical outputs.

## Local Batch vs Real Databricks Job

The local project runs as a batch Python process. A real Databricks implementation would likely use:

- notebooks or Python wheels;
- Databricks Jobs or Workflows;
- Spark clusters or serverless compute;
- Delta tables in ADLS;
- job parameters for processing dates and environments.
