"""Deterministic surrogate keys and content checksums."""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


MAX_SIGNED_LONG = 9_223_372_036_854_775_807


def surrogate_key(namespace: str, *columns: str) -> Column:
    """Return a stable positive LongType key derived from a namespace and natural key."""
    values = [F.lit(namespace)] + [F.coalesce(F.col(name).cast("string"), F.lit("<null>")) for name in columns]
    return F.pmod(F.xxhash64(*values), F.lit(MAX_SIGNED_LONG)).cast("long")


def with_content_checksum(frame: DataFrame, columns: list[str]) -> DataFrame:
    values = [F.coalesce(F.col(name).cast("string"), F.lit("<null>")) for name in columns]
    return frame.withColumn("_gold_record_checksum", F.sha2(F.concat_ws("||", *values), 256))
