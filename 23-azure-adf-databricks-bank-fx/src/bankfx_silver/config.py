"""Configuration models for the parametrized Silver pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class EntityConfig:
    entity_name: str
    table_name: str
    business_key: tuple[str, ...]


@dataclass(frozen=True)
class SilverConfig:
    environment: str
    catalog: str
    schema: str
    bronze_root: str
    silver_root: str
    quarantine_path: str
    audit_root: str
    storage_format: str
    entities: tuple[EntityConfig, ...]

    def with_overrides(self, **overrides: str | None) -> "SilverConfig":
        provided = {name: value for name, value in overrides.items() if value is not None}
        return replace(self, **provided)

    def resolved_path(self, project_root: Path, value: str) -> str:
        if "://" in value or value.startswith("dbfs:/") or value.startswith("/Volumes/"):
            return value.rstrip("/")
        path = (project_root / value).resolve()
        root = project_root.resolve()
        if path != root and root not in path.parents:
            raise ValueError(f"Configured path escapes project root: {value}")
        return str(path)


def load_silver_config(path: Path) -> SilverConfig:
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)

    required = {
        "environment",
        "catalog",
        "schema",
        "bronze_root",
        "silver_root",
        "quarantine_path",
        "audit_root",
        "storage_format",
        "entities",
    }
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Silver configuration is missing: {sorted(missing)}")
    if raw["storage_format"] != "delta":
        raise ValueError("Hito 3 requires storage_format=delta")

    entities: list[EntityConfig] = []
    seen: set[str] = set()
    for item in raw["entities"]:
        name = item["entity_name"]
        if name in seen:
            raise ValueError(f"Duplicate Silver entity: {name}")
        if not item.get("business_key"):
            raise ValueError(f"Missing business_key for Silver entity: {name}")
        entities.append(
            EntityConfig(
                entity_name=name,
                table_name=item["table_name"],
                business_key=tuple(item["business_key"]),
            )
        )
        seen.add(name)

    expected_order = ["customers", "accounts", "fx_rates", "transactions"]
    if [item.entity_name for item in entities] != expected_order:
        raise ValueError(f"Silver entities must follow dependency order: {expected_order}")

    return SilverConfig(
        environment=raw["environment"],
        catalog=raw["catalog"],
        schema=raw["schema"],
        bronze_root=raw["bronze_root"],
        silver_root=raw["silver_root"],
        quarantine_path=raw["quarantine_path"],
        audit_root=raw["audit_root"],
        storage_format=raw["storage_format"],
        entities=tuple(entities),
    )
