"""Tests for the preliminary, cloud-independent transaction contract."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal

import pytest

from banking_streaming.contracts import ContractError, parse_event


def test_valid_event_is_typed(valid_event: dict[str, object]) -> None:
    event = parse_event(valid_event)

    assert event.event_id == "EVT-0001"
    assert event.amount == Decimal("15990.00")
    assert event.currency == "CLP"
    assert event.event_time.utcoffset() is not None


def test_missing_event_id_is_rejected(valid_event: dict[str, object]) -> None:
    payload = deepcopy(valid_event)
    payload.pop("event_id")

    with pytest.raises(ContractError, match="event_id must be a non-empty string"):
        parse_event(payload)


@pytest.mark.parametrize("amount", [0, "-1.00", "1.001", "not-a-number", True])
def test_invalid_amount_is_rejected(valid_event: dict[str, object], amount: object) -> None:
    payload = {**valid_event, "amount": amount}

    with pytest.raises(ContractError):
        parse_event(payload)


def test_timestamp_without_timezone_is_rejected(valid_event: dict[str, object]) -> None:
    payload = {**valid_event, "event_time": "2026-09-08T12:00:00"}

    with pytest.raises(ContractError, match="event_time must include a timezone"):
        parse_event(payload)


def test_unknown_fields_are_rejected(valid_event: dict[str, object]) -> None:
    payload = {**valid_event, "unexpected": "value"}

    with pytest.raises(ContractError, match="unknown fields: unexpected"):
        parse_event(payload)
