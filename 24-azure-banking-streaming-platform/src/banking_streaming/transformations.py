"""Deterministic local transformations for synthetic transaction events."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC
from decimal import Decimal
from typing import Any

from banking_streaming.contracts import parse_event


def normalize_event(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return a canonical record suitable for initial idempotency tests."""

    event = parse_event(payload)
    signed_amount = event.amount if event.transaction_type == "CREDIT" else -event.amount
    event_time_utc = event.event_time.astimezone(UTC)

    return {
        "event_id": event.event_id,
        "event_time": event_time_utc.isoformat().replace("+00:00", "Z"),
        "event_date": event_time_utc.date().isoformat(),
        "event_version": event.event_version,
        "transaction_id": event.transaction_id,
        "account_id": event.account_id,
        "amount": _decimal_text(event.amount),
        "signed_amount": _decimal_text(signed_amount),
        "currency": event.currency,
        "transaction_type": event.transaction_type,
        "channel": event.channel,
    }


def _decimal_text(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")
