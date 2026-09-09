"""Local, cloud-independent foundations for Project 24."""

from banking_streaming.contracts import ContractError, TransactionEvent, parse_event
from banking_streaming.event_ingestion import (
    ConsumeReport,
    EventMessage,
    IngestionReport,
    InMemoryEventHub,
    PublishReport,
    build_message,
    consume_events,
    publish_events,
    run_local_ingestion,
)
from banking_streaming.idempotency import BatchResult, process_batch
from banking_streaming.transformations import normalize_event

__all__ = [
    "BatchResult",
    "ConsumeReport",
    "ContractError",
    "EventMessage",
    "InMemoryEventHub",
    "IngestionReport",
    "PublishReport",
    "TransactionEvent",
    "build_message",
    "consume_events",
    "normalize_event",
    "parse_event",
    "process_batch",
    "publish_events",
    "run_local_ingestion",
]
