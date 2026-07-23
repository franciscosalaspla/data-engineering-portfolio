"""Spark session factory shared by local execution and Databricks drivers."""

from __future__ import annotations

from pyspark.sql import SparkSession


def build_spark_session(app_name: str = "project23-bronze-to-silver") -> SparkSession:
    """Create a small local Delta-enabled session unless one already exists."""
    active = SparkSession.getActiveSession()
    if active is not None:
        active.conf.set("spark.sql.session.timeZone", "UTC")
        active.conf.set("spark.sql.jsonGenerator.ignoreNullFields", "false")
        return active

    from delta import configure_spark_with_delta_pip

    builder = (
        SparkSession.builder.master("local[2]")
        .appName(app_name)
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.default.parallelism", "2")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.jsonGenerator.ignoreNullFields", "false")
        .config("spark.databricks.delta.snapshotPartitions", "2")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    )
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
