"""Runtime validation for the versioned transaction event v1 contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

ALLOWED_FIELDS = frozenset(
    {
        "event_id",
        "event_time",
        "event_version",
        "transaction_id",
        "account_id",
        "amount",
        "currency",
        "transaction_type",
        "channel",
    }
)
SUPPORTED_CURRENCIES = frozenset({"CLP", "EUR", "USD"})
SUPPORTED_TRANSACTION_TYPES = frozenset({"CREDIT", "DEBIT"})
SUPPORTED_CHANNELS = frozenset({"ATM", "CARD", "MOBILE", "ONLINE"})


class ContractError(ValueError):
    """Raised when an event does not satisfy the v1 contract."""

    def __init__(self, reasons: list[str] | tuple[str, ...]) -> None:
        self.reasons = tuple(reasons)
        super().__init__("; ".join(self.reasons))


@dataclass(frozen=True, slots=True)
class TransactionEvent:
    """Typed representation of a valid synthetic transaction event."""

    event_id: str
    event_time: datetime
    event_version: int
    transaction_id: str
    account_id: str
    amount: Decimal
    currency: str
    transaction_type: str
    channel: str


def parse_event(payload: Mapping[str, Any]) -> TransactionEvent:
    """Validate and type an event without contacting Azure or external services."""

    if not isinstance(payload, Mapping):
        raise ContractError(["payload must be a mapping"])

    reasons: list[str] = []
    unknown_fields = sorted(set(payload) - ALLOWED_FIELDS)
    if unknown_fields:
        reasons.append(f"unknown fields: {', '.join(unknown_fields)}")

    event_id = _required_text(payload, "event_id", reasons)
    transaction_id = _required_text(payload, "transaction_id", reasons)
    account_id = _required_text(payload, "account_id", reasons)
    event_time = _event_time(payload.get("event_time"), reasons)
    event_version = _event_version(payload.get("event_version"), reasons)
    amount = _amount(payload.get("amount"), reasons)
    currency = _domain_value(payload.get("currency"), "currency", SUPPORTED_CURRENCIES, reasons)
    transaction_type = _domain_value(
        payload.get("transaction_type"),
        "transaction_type",
        SUPPORTED_TRANSACTION_TYPES,
        reasons,
    )
    channel = _domain_value(payload.get("channel"), "channel", SUPPORTED_CHANNELS, reasons)

    if reasons:
        raise ContractError(reasons)

    assert event_time is not None
    assert event_version is not None
    assert amount is not None
    return TransactionEvent(
        event_id=event_id,
        event_time=event_time,
        event_version=event_version,
        transaction_id=transaction_id,
        account_id=account_id,
        amount=amount,
        currency=currency,
        transaction_type=transaction_type,
        channel=channel,
    )


def _required_text(payload: Mapping[str, Any], field: str, reasons: list[str]) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        reasons.append(f"{field} must be a non-empty string")
        return ""
    return value.strip()


def _event_time(value: Any, reasons: list[str]) -> datetime | None:
    if not isinstance(value, str):
        reasons.append("event_time must be an ISO-8601 string")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        reasons.append("event_time must be a valid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        reasons.append("event_time must include a timezone")
        return None
    return parsed


def _event_version(value: Any, reasons: list[str]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value != 1:
        reasons.append("event_version must equal 1")
        return None
    return value


def _amount(value: Any, reasons: list[str]) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        reasons.append("amount must be numeric")
        return None
    try:
        parsed = Decimal(str(value))
    except InvalidOperation:
        reasons.append("amount must be numeric")
        return None
    if not parsed.is_finite() or parsed <= 0:
        reasons.append("amount must be finite and greater than zero")
        return None
    if parsed.as_tuple().exponent < -2:
        reasons.append("amount must have at most two decimal places")
        return None
    return parsed.quantize(Decimal("0.01"))


def _domain_value(
    value: Any,
    field: str,
    supported: frozenset[str],
    reasons: list[str],
) -> str:
    if not isinstance(value, str) or not value.strip():
        reasons.append(f"{field} must be a non-empty string")
        return ""
    normalized = value.strip().upper()
    if normalized not in supported:
        reasons.append(f"{field} is not supported: {normalized}")
        return ""
    return normalized
