"""Integration-style test for repository fixtures and CI safety controls."""

from __future__ import annotations

from scripts.validate_repository import PROJECT_ROOT, validate_repository


def test_repository_contract_is_consistent() -> None:
    report = validate_repository(PROJECT_ROOT)

    assert report.errors == ()
    assert report.customers == 5
    assert report.accounts == 7
    assert report.unique_events == 5
    assert report.invalid_events == 3


def test_replay_fixture_is_byte_identical() -> None:
    event_root = PROJECT_ROOT / "data" / "fixtures" / "events"

    assert (event_root / "transactions_batch_001.jsonl").read_bytes() == (
        event_root / "transactions_batch_001_replay.jsonl"
    ).read_bytes()
