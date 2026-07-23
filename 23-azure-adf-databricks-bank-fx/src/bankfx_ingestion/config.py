"""Read and validate the central source configuration."""

from __future__ import annotations

import json
from pathlib import Path

from .models import SourceConfig


REQUIRED_FIELDS = {
    "source_id",
    "source_name",
    "entity_name",
    "source_type",
    "source_path",
    "file_format",
    "schema_path",
    "enabled",
    "load_type",
    "destination_path",
    "business_key",
}


def load_source_config(config_path: Path) -> list[SourceConfig]:
    """Return validated source definitions in declared processing order."""
    with config_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload.get("sources"), list):
        raise ValueError("Configuration must contain a sources array")

    sources: list[SourceConfig] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(payload["sources"]):
        missing = REQUIRED_FIELDS - raw.keys()
        if missing:
            raise ValueError(f"Source {index} is missing: {sorted(missing)}")
        if raw["source_id"] in seen_ids:
            raise ValueError(f"Duplicate source_id: {raw['source_id']}")
        if raw["file_format"] not in {"csv", "json"}:
            raise ValueError(f"Unsupported file_format: {raw['file_format']}")
        if raw["load_type"] not in {"full", "incremental"}:
            raise ValueError(f"Unsupported load_type: {raw['load_type']}")
        if not isinstance(raw["enabled"], bool):
            raise ValueError(f"enabled must be boolean for {raw['source_id']}")
        if not raw["business_key"] or not all(
            isinstance(key, str) for key in raw["business_key"]
        ):
            raise ValueError(f"business_key must be a non-empty string array for {raw['source_id']}")

        sources.append(
            SourceConfig(
                source_id=raw["source_id"],
                source_name=raw["source_name"],
                entity_name=raw["entity_name"],
                source_type=raw["source_type"],
                source_path=raw["source_path"],
                file_format=raw["file_format"],
                schema_path=raw["schema_path"],
                enabled=raw["enabled"],
                load_type=raw["load_type"],
                destination_path=raw["destination_path"],
                business_key=tuple(raw["business_key"]),
                record_collection=raw.get("record_collection"),
            )
        )
        seen_ids.add(raw["source_id"])

    return sources
