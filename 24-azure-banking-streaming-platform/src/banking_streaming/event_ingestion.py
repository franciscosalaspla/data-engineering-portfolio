"""Deterministic event production and local consumption for Hito 4."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC
from typing import Any, Protocol

from banking_streaming.contracts import ContractError, TransactionEvent, parse_event

PARTITION_KEY_FIELD = "account_id"


@dataclass(frozen=True, slots=True)
class EventMessage:
    """Serialized event and routing metadata accepted by an event transport."""

    event_id: str
    partition_key: str
    body: bytes


class EventSink(Protocol):
    """Small transport boundary implemented locally and by Event Hubs in a future cloud run."""

    def send(self, message: EventMessage) -> None:
        """Send one validated event message."""


@dataclass(slots=True)
class InMemoryEventHub:
    """Local test double that stores messages without network or Azure credentials."""

    _messages: list[EventMessage] = field(default_factory=list)

    def send(self, message: EventMessage) -> None:
        self._messages.append(message)

    def receive(self) -> tuple[EventMessage, ...]:
        return tuple(self._messages)


@dataclass(frozen=True, slots=True)
class RejectedPublication:
    """Sanitized producer rejection that never retains the raw payload."""

    index: int
    event_id: str | None
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PublishReport:
    """Counts and safe evidence returned by the producer."""

    attempted: int
    published_event_ids: tuple[str, ...]
    rejected: tuple[RejectedPublication, ...]

    @property
    def published(self) -> int:
        return len(self.published_event_ids)


@dataclass(frozen=True, slots=True)
class ConsumeReport:
    """Validated messages observed by the local consumer."""

    received: int
    accepted_event_ids: tuple[str, ...]
    rejected_event_ids: tuple[str | None, ...]

    @property
    def accepted(self) -> int:
        return len(self.accepted_event_ids)


@dataclass(frozen=True, slots=True)
class IngestionReport:
    """Producer-to-consumer reconciliation for one local run."""

    producer: PublishReport
    consumer: ConsumeReport

    @property
    def reconciled(self) -> bool:
        return (
            self.producer.published == self.consumer.received == self.consumer.accepted
            and self.producer.published_event_ids == self.consumer.accepted_event_ids
        )


def build_message(payload: Mapping[str, Any]) -> EventMessage:
    """Validate and serialize one event using stable JSON and ``account_id`` partitioning."""

    event = parse_event(payload)
    canonical_payload = _canonical_payload(event)
    body = json.dumps(
        canonical_payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return EventMessage(event.event_id, event.account_id, body)


def publish_events(payloads: Iterable[Mapping[str, Any]], sink: EventSink) -> PublishReport:
    """Publish valid events and record invalid inputs without raw data."""

    published: list[str] = []
    rejected: list[RejectedPublication] = []
    attempted = 0

    for index, payload in enumerate(payloads):
        attempted += 1
        try:
            message = build_message(payload)
        except ContractError as error:
            raw_event_id = payload.get("event_id")
            event_id = raw_event_id if isinstance(raw_event_id, str) else None
            rejected.append(RejectedPublication(index, event_id, error.reasons))
            continue
        sink.send(message)
        published.append(message.event_id)

    return PublishReport(attempted, tuple(published), tuple(rejected))


def consume_events(messages: Iterable[EventMessage]) -> ConsumeReport:
    """Decode and validate locally received messages."""

    accepted: list[str] = []
    rejected: list[str | None] = []
    received = 0

    for message in messages:
        received += 1
        try:
            payload = json.loads(message.body)
            event = parse_event(payload)
            if message.partition_key != event.account_id:
                raise ContractError([f"partition key must equal {PARTITION_KEY_FIELD}"])
        except (ContractError, UnicodeDecodeError, json.JSONDecodeError):
            rejected.append(message.event_id or None)
            continue
        accepted.append(event.event_id)

    return ConsumeReport(received, tuple(accepted), tuple(rejected))


def run_local_ingestion(payloads: Iterable[Mapping[str, Any]]) -> IngestionReport:
    """Execute the producer and consumer against an in-memory transport."""

    hub = InMemoryEventHub()
    producer = publish_events(payloads, hub)
    consumer = consume_events(hub.receive())
    return IngestionReport(producer, consumer)


def _canonical_payload(event: TransactionEvent) -> dict[str, object]:
    event_time = event.event_time.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return {
        "event_id": event.event_id,
        "event_time": event_time,
        "event_version": event.event_version,
        "transaction_id": event.transaction_id,
        "account_id": event.account_id,
        "amount": format(event.amount, "f"),
        "currency": event.currency,
        "transaction_type": event.transaction_type,
        "channel": event.channel,
    }
