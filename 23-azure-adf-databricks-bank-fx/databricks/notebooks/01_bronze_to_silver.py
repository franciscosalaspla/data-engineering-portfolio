# Databricks notebook source
# MAGIC %md
# MAGIC # Project 23 — Bronze to Silver driver
# MAGIC This notebook delegates all transformations and quality rules to reusable modules.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

import sys
from pathlib import Path

sys.path.insert(0, str(Path(PROJECT_ROOT) / "src"))

from bankfx_silver.config import load_silver_config
from bankfx_silver.pipeline import SilverPipeline

config = load_silver_config(Path(PROJECT_ROOT) / "config" / "silver_pipeline.json").with_overrides(
    environment=ENVIRONMENT,
    bronze_root=BRONZE_ROOT,
    silver_root=SILVER_ROOT,
    quarantine_path=QUARANTINE_PATH,
    audit_root=AUDIT_ROOT,
    catalog=CATALOG,
    schema=SCHEMA,
)

summary = SilverPipeline(spark, Path(PROJECT_ROOT), config=config).run(RUN_ID)
display(spark.createDataFrame(summary.entities))
assert summary.status != "FAILED", summary.to_dict()
