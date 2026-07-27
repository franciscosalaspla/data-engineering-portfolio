"""Configuration models for the parametrized Gold pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class GoldTableConfig:
    table_name: str
    business_key: tuple[str, ...]


@dataclass(frozen=True)
class GoldConfig:
    environment: str
    catalog: str
    schema: str
    silver_root: str
    gold_root: str
    quarantine_path: str
    audit_root: str
    serving_root: str
    storage_format: str
    tables: tuple[GoldTableConfig, ...]

    def with_overrides(self, **overrides: str | None) -> "GoldConfig":
        provided = {name: value for name, value in overrides.items() if value is not None}
        return replace(self, **provided)

    def resolved_path(self, project_root: Path, value: str) -> str:
        if "://" in value or value.startswith(("dbfs:/", "/Volumes/")):
            return value.rstrip("/")
        path = (project_root / value).resolve()
        root = project_root.resolve()
        if path != root and root not in path.parents:
            raise ValueError(f"Configured path escapes project root: {value}")
        return str(path)

    def table(self, table_name: str) -> GoldTableConfig:
        for table in self.tables:
            if table.table_name == table_name:
                return table
        raise ValueError(f"Unknown Gold table: {table_name}")


def load_gold_config(path: Path) -> GoldConfig:
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)

    required = {
        "environment",
        "catalog",
        "schema",
        "silver_root",
        "gold_root",
        "quarantine_path",
        "audit_root",
        "serving_root",
        "storage_format",
        "tables",
    }
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Gold configuration is missing: {sorted(missing)}")
    if raw["storage_format"] != "delta":
        raise ValueError("Hito 4 requires storage_format=delta")

    tables = tuple(
        GoldTableConfig(item["table_name"], tuple(item["business_key"]))
        for item in raw["tables"]
    )
    expected = [
        "dim_date",
        "dim_customer",
        "dim_account",
        "dim_merchant",
        "dim_channel",
        "dim_currency",
        "fact_transactions",
    ]
    names = [table.table_name for table in tables]
    if names != expected:
        raise ValueError(f"Gold tables must follow dependency order: {expected}")
    if len(names) != len(set(names)) or any(not table.business_key for table in tables):
        raise ValueError("Gold tables require unique names and non-empty business keys")

    return GoldConfig(
        environment=raw["environment"],
        catalog=raw["catalog"],
        schema=raw["schema"],
        silver_root=raw["silver_root"],
        gold_root=raw["gold_root"],
        quarantine_path=raw["quarantine_path"],
        audit_root=raw["audit_root"],
        serving_root=raw["serving_root"],
        storage_format=raw["storage_format"],
        tables=tables,
    )
