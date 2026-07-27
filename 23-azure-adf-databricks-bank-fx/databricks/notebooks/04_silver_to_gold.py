# Databricks notebook source
# MAGIC %md
# MAGIC # Project 23 — Silver to Gold driver
# MAGIC Reuses repository modules with catalog, schema, paths and environment supplied by widgets.
# MAGIC Evidence from this notebook must be labelled **Databricks Free Edition** until Azure Databricks is actually used.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

import sys
from pathlib import Path

sys.path.insert(0, str(Path(PROJECT_ROOT) / "src"))

from bankfx_gold import GoldPipeline
from bankfx_gold.config import load_gold_config

config = load_gold_config(Path(PROJECT_ROOT) / "config" / "gold_pipeline.json").with_overrides(
    environment=ENVIRONMENT,
    silver_root=SILVER_ROOT,
    gold_root=GOLD_ROOT,
    quarantine_path=GOLD_QUARANTINE_PATH,
    audit_root=AUDIT_ROOT,
    serving_root=SERVING_ROOT,
    catalog=CATALOG,
    schema=SCHEMA,
)
summary = GoldPipeline(spark, Path(PROJECT_ROOT), config=config).run(RUN_ID)
display(spark.createDataFrame(summary.tables))
print(summary.to_dict())

if summary.status == "FAILED":
    raise RuntimeError("Gold pipeline failed; inspect the run summary and audit records")
