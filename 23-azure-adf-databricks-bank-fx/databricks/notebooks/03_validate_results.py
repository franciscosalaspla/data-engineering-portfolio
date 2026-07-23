# Databricks notebook source
# MAGIC %md
# MAGIC # Project 23 — Silver result validation
# MAGIC Fixture-scale expectations are local development evidence, not production thresholds.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

expected_counts = {
    "silver_customers": 5,
    "silver_accounts": 7,
    "silver_fx_rates": 2,
    "silver_transactions": 8,
}

actual_counts = {
    table_name: spark.read.format("delta").load(f"{SILVER_ROOT.rstrip('/')}/{table_name}").count()
    for table_name in expected_counts
}

display(spark.createDataFrame([{"table_name": key, "expected": expected_counts[key], "actual": value} for key, value in actual_counts.items()]))
assert actual_counts == expected_counts, {"expected": expected_counts, "actual": actual_counts}
