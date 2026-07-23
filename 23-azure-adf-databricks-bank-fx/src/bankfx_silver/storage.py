"""Delta Lake writes, idempotent MERGE operations and history evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


@dataclass(frozen=True)
class MergeMetrics:
    inserted: int
    updated: int
    skipped: int
    delta_version: int
    delta_operation: str
    delta_operation_metrics: dict[str, str]
    delta_timestamp: str


class DeltaTableStore:
    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def is_table(self, path: str) -> bool:
        return DeltaTable.isDeltaTable(self.spark, path)

    def read(self, path: str) -> DataFrame:
        return self.spark.read.format("delta").load(path)

    def merge(
        self,
        incoming: DataFrame,
        path: str,
        business_key: tuple[str, ...],
    ) -> MergeMetrics:
        incoming_count = incoming.count()
        if not self.is_table(path):
            incoming.write.format("delta").mode("overwrite").save(path)
            history = self.history(path)
            return MergeMetrics(
                inserted=incoming_count,
                updated=0,
                skipped=0,
                **history,
            )

        existing = self.read(path)
        join_condition = [
            F.col(f"source.`{key}`") == F.col(f"target.`{key}`")
            for key in business_key
        ]
        combined_condition = join_condition[0]
        for condition in join_condition[1:]:
            combined_condition = combined_condition & condition

        inserted = (
            incoming.alias("source")
            .join(existing.alias("target"), combined_condition, "left_anti")
            .count()
        )
        updated = (
            incoming.alias("source")
            .join(existing.alias("target"), combined_condition, "inner")
            .filter(~F.col("source._record_checksum").eqNullSafe(F.col("target._record_checksum")))
            .count()
        )
        skipped = incoming_count - inserted - updated

        if inserted == 0 and updated == 0:
            history = self.history(path)
            return MergeMetrics(
                inserted=0,
                updated=0,
                skipped=skipped,
                **history,
            )

        merge_condition = " AND ".join(
            f"target.`{key}` = source.`{key}`" for key in business_key
        )
        (
            DeltaTable.forPath(self.spark, path)
            .alias("target")
            .merge(incoming.alias("source"), merge_condition)
            .whenMatchedUpdateAll(
                condition="NOT (target._record_checksum <=> source._record_checksum)"
            )
            .whenNotMatchedInsertAll()
            .execute()
        )
        history = self.history(path)
        return MergeMetrics(
            inserted=inserted,
            updated=updated,
            skipped=skipped,
            **history,
        )

    def merge_quarantine(self, quarantine: DataFrame, path: str) -> tuple[int, int]:
        incoming_count = quarantine.count()
        if incoming_count == 0:
            return 0, 0
        if not self.is_table(path):
            quarantine.write.format("delta").mode("overwrite").save(path)
            return incoming_count, 0

        existing = self.read(path).select("_quarantine_id")
        inserted = quarantine.join(existing, "_quarantine_id", "left_anti").count()
        (
            DeltaTable.forPath(self.spark, path)
            .alias("target")
            .merge(
                quarantine.alias("source"),
                "target._quarantine_id = source._quarantine_id",
            )
            .whenNotMatchedInsertAll()
            .execute()
        )
        return inserted, incoming_count - inserted

    def history(self, path: str) -> dict[str, Any]:
        row = (
            DeltaTable.forPath(self.spark, path)
            .history(1)
            .select("version", "operation", "operationMetrics", "timestamp")
            .collect()[0]
        )
        timestamp = row["timestamp"]
        if isinstance(timestamp, datetime):
            timestamp_value = timestamp.isoformat()
        else:
            timestamp_value = str(timestamp)
        return {
            "delta_version": int(row["version"]),
            "delta_operation": str(row["operation"]),
            "delta_operation_metrics": {
                str(key): str(value) for key, value in (row["operationMetrics"] or {}).items()
            },
            "delta_timestamp": timestamp_value,
        }
