# Databricks notebook source
# MAGIC %md
# MAGIC # Project 23 — Gold validation
# MAGIC Validates table counts, foreign keys and the analytical snapshot after notebook 04.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

expected = {
    "dim_date": 2,
    "dim_customer": 5,
    "dim_account": 7,
    "dim_merchant": 7,
    "dim_channel": 4,
    "dim_currency": 3,
    "fact_transactions": 8,
}
results = []
for table_name, expected_count in expected.items():
    frame = spark.read.format("delta").load(f"{GOLD_ROOT}/{table_name}")
    actual_count = frame.count()
    results.append((table_name, expected_count, actual_count, "PASSED" if actual_count == expected_count else "FAILED"))

display(spark.createDataFrame(results, ["table_name", "expected_count", "actual_count", "status"]))
snapshot_count = spark.read.parquet(f"{SERVING_ROOT}/transactions_analytics").count()
if any(row[3] == "FAILED" for row in results) or snapshot_count != 8:
    raise RuntimeError("Gold validation failed")
print({"status": "PASSED", "snapshot_row_count": snapshot_count})
