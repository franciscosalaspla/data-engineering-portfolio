"""Tests for initial at-least-once and replay controls."""

from __future__ import annotations

from collections.abc import Callable

from banking_streaming.idempotency import process_batch

EventLoader = Callable[[str], list[dict[str, object]]]


def test_duplicate_inside_later_microbatch_is_neutralized(event_loader: EventLoader) -> None:
    first = process_batch(event_loader("transactions_batch_001.jsonl"))
    second = process_batch(event_loader("transactions_batch_002.jsonl"), first.seen_event_ids)

    assert len(first.accepted) == 3
    assert len(second.accepted) == 2
    assert second.duplicate_event_ids == ("EVT-0002",)
    assert len(second.seen_event_ids) == 5


def test_exact_replay_becomes_no_op(event_loader: EventLoader) -> None:
    original = process_batch(event_loader("transactions_batch_001.jsonl"))
    replay = process_batch(
        event_loader("transactions_batch_001_replay.jsonl"), original.seen_event_ids
    )

    assert replay.accepted == ()
    assert replay.duplicate_event_ids == ("EVT-0001", "EVT-0002", "EVT-0003")
    assert replay.seen_event_ids == original.seen_event_ids


def test_invalid_events_are_quarantined_without_raw_payload(event_loader: EventLoader) -> None:
    result = process_batch(event_loader("transactions_invalid.jsonl"))

    assert result.accepted == ()
    assert len(result.rejected) == 3
    assert result.rejected[0].event_id is None
    assert result.rejected[1].event_id == "EVT-9002"
    assert all(rejection.reasons for rejection in result.rejected)
