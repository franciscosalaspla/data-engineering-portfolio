"""Bronze reader with mandatory explicit PySpark schemas."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from .schemas import bronze_schema


def read_bronze(
    spark: SparkSession,
    bronze_root: str,
    entity_name: str,
) -> DataFrame:
    entity_path = f"{bronze_root.rstrip('/')}/{entity_name}"
    return (
        spark.read.schema(bronze_schema(entity_name))
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", "_corrupt_record")
        .option("recursiveFileLookup", "true")
        .option("pathGlobFilter", "records.jsonl")
        .json(entity_path)
        .withColumn("_source_bronze_path", F.input_file_name())
    )
