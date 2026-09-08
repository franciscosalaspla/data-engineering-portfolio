"""Tests for deterministic normalization before streaming is introduced."""

from __future__ import annotations

from banking_streaming.transformations import normalize_event


def test_debit_amount_is_signed_negative(valid_event: dict[str, object]) -> None:
    record = normalize_event(valid_event)

    assert record["amount"] == "15990.00"
    assert record["signed_amount"] == "-15990.00"
    assert record["event_date"] == "2026-09-08"


def test_domains_and_offset_timestamp_are_normalized(valid_event: dict[str, object]) -> None:
    payload = {
        **valid_event,
        "event_time": "2026-09-08T12:01:05-03:00",
        "currency": "eur",
        "transaction_type": "credit",
        "channel": "online",
    }

    record = normalize_event(payload)

    assert record["event_time"] == "2026-09-08T15:01:05Z"
    assert record["currency"] == "EUR"
    assert record["transaction_type"] == "CREDIT"
    assert record["channel"] == "ONLINE"
    assert record["signed_amount"] == "15990.00"


def test_normalization_is_deterministic(valid_event: dict[str, object]) -> None:
    assert normalize_event(valid_event) == normalize_event(valid_event)
