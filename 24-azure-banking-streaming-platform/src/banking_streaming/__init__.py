"""Local, cloud-independent foundations for Project 24."""

from banking_streaming.contracts import ContractError, TransactionEvent, parse_event
from banking_streaming.idempotency import BatchResult, process_batch
from banking_streaming.transformations import normalize_event

__all__ = [
    "BatchResult",
    "ContractError",
    "TransactionEvent",
    "normalize_event",
    "parse_event",
    "process_batch",
]
