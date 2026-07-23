"""Small dependency-free validator for the JSON Schema subset used in Hito 1."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any


class ContractValidator:
    """Validate records against the local contracts without external packages."""

    def __init__(self, schema: dict[str, Any]) -> None:
        self.schema = schema

    def validate(self, value: Any) -> list[str]:
        errors: list[str] = []
        self._validate(value, self.schema, "$", errors)
        return errors

    def _validate(
        self,
        value: Any,
        rule: dict[str, Any],
        path: str,
        errors: list[str],
    ) -> None:
        if "$ref" in rule:
            rule = self._resolve_ref(rule["$ref"])

        expected_type = rule.get("type")
        if expected_type and not _matches_type(value, expected_type):
            errors.append(f"SCHEMA_TYPE: {path} must be {expected_type}")
            return

        if "const" in rule and value != rule["const"]:
            errors.append(f"SCHEMA_CONST: {path} must equal {rule['const']!r}")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"SCHEMA_ENUM: {path} must be one of {rule['enum']}")
        if isinstance(value, str):
            if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
                errors.append(f"SCHEMA_PATTERN: {path} has an invalid format")
            if len(value) < rule.get("minLength", 0):
                errors.append(f"SCHEMA_MIN_LENGTH: {path} is too short")
            if rule.get("format") and not _valid_format(value, rule["format"]):
                errors.append(f"SCHEMA_FORMAT: {path} is not a valid {rule['format']}")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "exclusiveMinimum" in rule and value <= rule["exclusiveMinimum"]:
                errors.append(f"SCHEMA_MINIMUM: {path} must be greater than {rule['exclusiveMinimum']}")
        if isinstance(value, list):
            if len(value) < rule.get("minItems", 0):
                errors.append(f"SCHEMA_MIN_ITEMS: {path} contains too few items")
            item_rule = rule.get("items")
            if item_rule:
                for index, item in enumerate(value):
                    self._validate(item, item_rule, f"{path}[{index}]", errors)
        if isinstance(value, dict):
            required = rule.get("required", [])
            for name in required:
                if name not in value:
                    errors.append(f"SCHEMA_REQUIRED: {path}.{name} is required")
            properties = rule.get("properties", {})
            if rule.get("additionalProperties") is False:
                for name in value.keys() - properties.keys():
                    errors.append(f"SCHEMA_ADDITIONAL_PROPERTY: {path}.{name} is not allowed")
            for name, child_rule in properties.items():
                if name in value:
                    self._validate(value[name], child_rule, f"{path}.{name}", errors)

    def _resolve_ref(self, reference: str) -> dict[str, Any]:
        if not reference.startswith("#/"):
            raise ValueError(f"Only local schema references are supported: {reference}")
        node: Any = self.schema
        for part in reference[2:].split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
        return node


def validate_references(
    entity_name: str,
    record: dict[str, Any],
    account_ids: set[str],
    customer_ids: set[str],
) -> list[str]:
    """Apply only cross-source contract checks required before Bronze."""
    errors: list[str] = []
    if entity_name == "transactions" and record.get("account_id") not in account_ids:
        errors.append("REFERENTIAL_INTEGRITY: account_id is not present in accounts")
    if entity_name == "accounts" and record.get("customer_id") not in customer_ids:
        errors.append("REFERENTIAL_INTEGRITY: customer_id is not present in customers")
    return errors


def _matches_type(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return checks.get(expected, lambda _item: False)(value)


def _valid_format(value: str, expected: str) -> bool:
    try:
        if expected == "date":
            date.fromisoformat(value)
        elif expected == "date-time":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            return True
    except ValueError:
        return False
    return True
