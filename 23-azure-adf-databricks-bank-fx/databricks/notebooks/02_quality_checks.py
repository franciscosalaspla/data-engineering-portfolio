# Databricks notebook source
# MAGIC %md
# MAGIC # Project 23 — Silver quality controls

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

from pyspark.sql import functions as F

expected_keys = {
    "silver_customers": "customer_id",
    "silver_accounts": "account_id",
    "silver_fx_rates": "effective_date",
    "silver_transactions": "transaction_id",
}

results = []
for table_name, key in expected_keys.items():
    path = f"{SILVER_ROOT.rstrip('/')}/{table_name}"
    frame = spark.read.format("delta").load(path)
    results.append(
        {
            "table_name": table_name,
            "row_count": frame.count(),
            "null_key_count": frame.filter(F.col(key).isNull()).count(),
            "duplicate_key_count": frame.groupBy(key).count().filter("count > 1").count(),
        }
    )

quality_results = spark.createDataFrame(results)
display(quality_results)
assert quality_results.filter("null_key_count > 0 OR duplicate_key_count > 0").count() == 0
