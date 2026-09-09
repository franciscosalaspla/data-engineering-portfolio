"""Integration-style test for repository fixtures and CI safety controls."""

from __future__ import annotations

from scripts.validate_repository import (
    PROJECT_ROOT,
    REPOSITORY_ROOT,
    _validate_cd_workflow,
    validate_repository,
)


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


def test_cd_workflow_rejects_github_secrets(tmp_path) -> None:
    workflow = REPOSITORY_ROOT / ".github" / "workflows" / "p24-cd.yml"
    unsafe_workflow = tmp_path / "p24-cd.yml"
    unsafe_workflow.write_text(
        workflow.read_text(encoding="utf-8").replace(
            "vars.AZURE_CLIENT_ID", "secrets.AZURE_CLIENT_SECRET", 1
        ),
        encoding="utf-8",
    )
    errors: list[str] = []

    _validate_cd_workflow(unsafe_workflow, errors)

    assert any("'secrets.'" in error for error in errors)


def test_cd_workflow_rejects_automatic_push_trigger(tmp_path) -> None:
    workflow = REPOSITORY_ROOT / ".github" / "workflows" / "p24-cd.yml"
    unsafe_workflow = tmp_path / "p24-cd.yml"
    unsafe_workflow.write_text(
        workflow.read_text(encoding="utf-8").replace(
            "  workflow_dispatch:", "  push:\n  workflow_dispatch:", 1
        ),
        encoding="utf-8",
    )
    errors: list[str] = []

    _validate_cd_workflow(unsafe_workflow, errors)

    assert any("'\\n  push:'" in error for error in errors)
