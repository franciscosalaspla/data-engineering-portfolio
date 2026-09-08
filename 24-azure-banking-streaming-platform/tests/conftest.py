"""Shared deterministic fixtures for Hito 1 tests."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVENT_FIXTURES = PROJECT_ROOT / "data" / "fixtures" / "events"


def load_jsonl(name: str) -> list[dict[str, object]]:
    path = EVENT_FIXTURES / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


@pytest.fixture
def event_loader() -> Callable[[str], list[dict[str, object]]]:
    return load_jsonl


@pytest.fixture
def valid_event() -> dict[str, object]:
    return load_jsonl("transactions_batch_001.jsonl")[0]
