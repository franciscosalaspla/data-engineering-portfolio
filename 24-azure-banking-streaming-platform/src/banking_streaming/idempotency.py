"""Side-effect-free batch processing used to demonstrate initial replay behavior."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from banking_streaming.contracts import ContractError
from banking_streaming.transformations import normalize_event


@dataclass(frozen=True, slots=True)
class RejectedEvent:
    """Sanitized evidence for a contract rejection."""

    index: int
    event_id: str | None
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BatchResult:
    """Immutable result of processing one deterministic microbatch."""

    accepted: tuple[dict[str, object], ...]
    duplicate_event_ids: tuple[str, ...]
    rejected: tuple[RejectedEvent, ...]
    seen_event_ids: frozenset[str]


def process_batch(
    payloads: Iterable[Mapping[str, Any]],
    seen_event_ids: Iterable[str] = (),
) -> BatchResult:
    """Validate, normalize, and deduplicate a batch by ``event_id``.

    The returned state is explicit, so a replay can be tested without files,
    databases, checkpoints, or cloud credentials.
    """

    seen = set(seen_event_ids)
    accepted: list[dict[str, object]] = []
    duplicates: list[str] = []
    rejected: list[RejectedEvent] = []

    for index, payload in enumerate(payloads):
        try:
            record = normalize_event(payload)
        except ContractError as error:
            raw_event_id = payload.get("event_id")
            event_id = raw_event_id if isinstance(raw_event_id, str) else None
            rejected.append(RejectedEvent(index, event_id, error.reasons))
            continue

        event_id = str(record["event_id"])
        if event_id in seen:
            duplicates.append(event_id)
            continue

        seen.add(event_id)
        accepted.append(record)

    return BatchResult(
        accepted=tuple(accepted),
        duplicate_event_ids=tuple(duplicates),
        rejected=tuple(rejected),
        seen_event_ids=frozenset(seen),
    )
