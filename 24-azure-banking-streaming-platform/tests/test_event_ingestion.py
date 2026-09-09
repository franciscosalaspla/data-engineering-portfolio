"""Tests for the cloud-independent Hito 4 event path."""

from __future__ import annotations

import json
from collections.abc import Callable

from banking_streaming.event_ingestion import (
    EventMessage,
    InMemoryEventHub,
    build_message,
    consume_events,
    publish_events,
    run_local_ingestion,
)

EventLoader = Callable[[str], list[dict[str, object]]]


def test_valid_batch_is_reconciled(event_loader: EventLoader) -> None:
    report = run_local_ingestion(event_loader("transactions_batch_001.jsonl"))

    assert report.producer.attempted == 3
    assert report.producer.published == 3
    assert report.consumer.received == 3
    assert report.consumer.accepted == 3
    assert report.reconciled


def test_partition_key_is_account_id(valid_event: dict[str, object]) -> None:
    message = build_message(valid_event)

    assert message.partition_key == valid_event["account_id"]


def test_serialization_is_deterministic_and_canonical(valid_event: dict[str, object]) -> None:
    first = build_message(valid_event)
    second = build_message(valid_event)
    payload = json.loads(first.body)

    assert first == second
    assert payload["amount"] == "15990.00"
    assert payload["event_time"] == "2026-09-08T12:00:00Z"


def test_invalid_events_are_not_published(event_loader: EventLoader) -> None:
    hub = InMemoryEventHub()
    report = publish_events(event_loader("transactions_invalid.jsonl"), hub)

    assert report.attempted == 3
    assert report.published == 0
    assert len(report.rejected) == 3
    assert hub.receive() == ()


def test_consumer_rejects_wrong_partition_key(valid_event: dict[str, object]) -> None:
    valid_message = build_message(valid_event)
    wrong_partition = EventMessage(valid_message.event_id, "ACC-WRONG", valid_message.body)

    report = consume_events([wrong_partition])

    assert report.received == 1
    assert report.accepted == 0
    assert report.rejected_event_ids == ("EVT-0001",)


def test_consumer_rejects_malformed_json() -> None:
    message = EventMessage("EVT-BROKEN", "ACC-001", b"not-json")

    report = consume_events([message])

    assert report.received == 1
    assert report.accepted == 0
    assert report.rejected_event_ids == ("EVT-BROKEN",)


def test_rejection_evidence_does_not_retain_payload(event_loader: EventLoader) -> None:
    hub = InMemoryEventHub()
    report = publish_events(event_loader("transactions_invalid.jsonl"), hub)

    assert all(not hasattr(item, "payload") for item in report.rejected)
