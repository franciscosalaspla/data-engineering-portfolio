# Databricks notebook source
# MAGIC %md
# MAGIC # Project 23 — Medallion configuration
# MAGIC All paths and namespaces are parameters; no secret is stored in this notebook.

# COMMAND ----------

dbutils.widgets.text("project_root", "/Workspace/Repos/REPLACE_WITH_REPO/23-azure-adf-databricks-bank-fx")
dbutils.widgets.text("environment", "free-edition")
dbutils.widgets.text("run_id", "manual-silver-run")
dbutils.widgets.text("bronze_root", "/Volumes/REPLACE_CATALOG/REPLACE_SCHEMA/bankfx/bronze")
dbutils.widgets.text("silver_root", "/Volumes/REPLACE_CATALOG/REPLACE_SCHEMA/bankfx/silver")
dbutils.widgets.text("quarantine_path", "/Volumes/REPLACE_CATALOG/REPLACE_SCHEMA/bankfx/silver_quarantine")
dbutils.widgets.text("audit_root", "/Volumes/REPLACE_CATALOG/REPLACE_SCHEMA/bankfx/audit")
dbutils.widgets.text("gold_root", "/Volumes/REPLACE_CATALOG/REPLACE_SCHEMA/bankfx/gold")
dbutils.widgets.text("gold_quarantine_path", "/Volumes/REPLACE_CATALOG/REPLACE_SCHEMA/bankfx/gold_quarantine")
dbutils.widgets.text("serving_root", "/Volumes/REPLACE_CATALOG/REPLACE_SCHEMA/bankfx/serving")
dbutils.widgets.text("catalog", "REPLACE_CATALOG")
dbutils.widgets.text("schema", "REPLACE_SCHEMA")

PROJECT_ROOT = dbutils.widgets.get("project_root")
ENVIRONMENT = dbutils.widgets.get("environment")
RUN_ID = dbutils.widgets.get("run_id")
BRONZE_ROOT = dbutils.widgets.get("bronze_root")
SILVER_ROOT = dbutils.widgets.get("silver_root")
QUARANTINE_PATH = dbutils.widgets.get("quarantine_path")
AUDIT_ROOT = dbutils.widgets.get("audit_root")
GOLD_ROOT = dbutils.widgets.get("gold_root")
GOLD_QUARANTINE_PATH = dbutils.widgets.get("gold_quarantine_path")
SERVING_ROOT = dbutils.widgets.get("serving_root")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
