"""Run deterministic, cloud-independent repository checks for Project 24."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent
SOURCE_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from banking_streaming.contracts import ContractError, parse_event  # noqa: E402
from banking_streaming.idempotency import process_batch  # noqa: E402

FORBIDDEN_PII_FIELDS = frozenset({"address", "email", "full_name", "name", "phone", "rut", "ssn"})
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SCANNED_SUFFIXES = frozenset(
    {".bicep", ".bicepparam", ".env", ".json", ".jsonl", ".py", ".sh", ".toml", ".yaml", ".yml"}
)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Aggregated result that is straightforward to assert in tests and CI."""

    errors: tuple[str, ...]
    customers: int
    accounts: int
    unique_events: int
    invalid_events: int

    @property
    def passed(self) -> bool:
        return not self.errors


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load one JSON object per non-empty line."""

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {error.msg}") from error
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number}: each JSONL line must be an object")
        records.append(record)
    return records


def validate_repository(project_root: Path = PROJECT_ROOT) -> ValidationReport:
    """Validate fixtures, local links, workflow safety, and obvious secret patterns."""

    fixture_root = project_root / "data" / "fixtures"
    event_root = fixture_root / "events"
    errors: list[str] = []

    customers = _load_json_array(fixture_root / "reference" / "customers.json", errors)
    accounts = _load_json_array(fixture_root / "reference" / "accounts.json", errors)
    batch_001 = _load_jsonl_safely(event_root / "transactions_batch_001.jsonl", errors)
    batch_002 = _load_jsonl_safely(event_root / "transactions_batch_002.jsonl", errors)
    replay = _load_jsonl_safely(event_root / "transactions_batch_001_replay.jsonl", errors)
    invalid = _load_jsonl_safely(event_root / "transactions_invalid.jsonl", errors)

    if len(customers) != 5:
        errors.append(f"expected 5 synthetic customers, found {len(customers)}")
    if len(accounts) != 7:
        errors.append(f"expected 7 synthetic accounts, found {len(accounts)}")
    if len(invalid) != 3:
        errors.append(f"expected 3 invalid events, found {len(invalid)}")

    _validate_no_pii([*customers, *accounts, *batch_001, *batch_002, *replay, *invalid], errors)
    _validate_references(customers, accounts, [*batch_001, *batch_002], errors)
    _validate_contracts(batch_001, batch_002, replay, invalid, errors)
    _validate_replay_bytes(event_root, errors)
    unique_events = _validate_idempotency(batch_001, batch_002, replay, errors)
    _validate_json_files(project_root, errors)
    _validate_markdown_links(project_root, errors)
    _validate_infrastructure(project_root / "infra", errors)
    workflow_root = REPOSITORY_ROOT / ".github" / "workflows"
    _validate_ci_workflow(workflow_root / "p24-ci.yml", errors)
    _validate_cd_workflow(workflow_root / "p24-cd.yml", errors)
    _scan_for_secrets(project_root, errors)

    return ValidationReport(
        errors=tuple(errors),
        customers=len(customers),
        accounts=len(accounts),
        unique_events=unique_events,
        invalid_events=len(invalid),
    )


def _load_json_array(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"cannot load {path.relative_to(REPOSITORY_ROOT)}: {error}")
        return []
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        errors.append(f"{path.relative_to(REPOSITORY_ROOT)} must contain an array of objects")
        return []
    return value


def _load_jsonl_safely(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    try:
        return load_jsonl(path)
    except (OSError, ValueError) as error:
        errors.append(str(error))
        return []


def _validate_no_pii(records: Iterable[dict[str, Any]], errors: list[str]) -> None:
    for index, record in enumerate(records):
        forbidden = sorted(set(record) & FORBIDDEN_PII_FIELDS)
        if forbidden:
            errors.append(f"record {index} contains forbidden PII fields: {', '.join(forbidden)}")


def _validate_references(
    customers: list[dict[str, Any]],
    accounts: list[dict[str, Any]],
    events: list[dict[str, Any]],
    errors: list[str],
) -> None:
    customer_ids = {item.get("customer_id") for item in customers}
    account_ids = {item.get("account_id") for item in accounts}
    if len(customer_ids) != len(customers):
        errors.append("customer_id values must be unique")
    if len(account_ids) != len(accounts):
        errors.append("account_id values must be unique")
    for account in accounts:
        if account.get("customer_id") not in customer_ids:
            errors.append(f"account {account.get('account_id')} references an unknown customer")
    for event in events:
        if event.get("account_id") not in account_ids:
            errors.append(f"event {event.get('event_id')} references an unknown account")


def _validate_contracts(
    batch_001: list[dict[str, Any]],
    batch_002: list[dict[str, Any]],
    replay: list[dict[str, Any]],
    invalid: list[dict[str, Any]],
    errors: list[str],
) -> None:
    for label, records in (
        ("batch_001", batch_001),
        ("batch_002", batch_002),
        ("batch_001_replay", replay),
    ):
        for index, record in enumerate(records):
            try:
                parse_event(record)
            except ContractError as error:
                errors.append(f"{label}[{index}] should be valid: {error}")

    for index, record in enumerate(invalid):
        try:
            parse_event(record)
        except ContractError:
            continue
        errors.append(f"transactions_invalid[{index}] unexpectedly satisfies the contract")


def _validate_replay_bytes(event_root: Path, errors: list[str]) -> None:
    original = event_root / "transactions_batch_001.jsonl"
    replay = event_root / "transactions_batch_001_replay.jsonl"
    if original.exists() and replay.exists() and original.read_bytes() != replay.read_bytes():
        errors.append("transactions_batch_001 replay must be byte-for-byte identical")


def _validate_idempotency(
    batch_001: list[dict[str, Any]],
    batch_002: list[dict[str, Any]],
    replay: list[dict[str, Any]],
    errors: list[str],
) -> int:
    first = process_batch(batch_001)
    second = process_batch(batch_002, first.seen_event_ids)
    replayed = process_batch(replay, second.seen_event_ids)

    if (len(first.accepted), len(first.duplicate_event_ids), len(first.rejected)) != (3, 0, 0):
        errors.append("batch_001 expected 3 accepted, 0 duplicate, and 0 rejected events")
    if (len(second.accepted), len(second.duplicate_event_ids), len(second.rejected)) != (2, 1, 0):
        errors.append("batch_002 expected 2 accepted, 1 duplicate, and 0 rejected events")
    if replayed.accepted or len(replayed.duplicate_event_ids) != 3 or replayed.rejected:
        errors.append("replay expected 0 accepted, 3 duplicate, and 0 rejected events")
    return len(replayed.seen_event_ids)


def _validate_json_files(project_root: Path, errors: list[str]) -> None:
    for path in sorted(project_root.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid JSON in {path.relative_to(REPOSITORY_ROOT)}: {error}")


def _validate_markdown_links(project_root: Path, errors: list[str]) -> None:
    for path in sorted(project_root.rglob("*.md")):
        for target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
            target = target.split(maxsplit=1)[0].strip("<>")
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            local_target = target.split("#", maxsplit=1)[0]
            if local_target and not (path.parent / local_target).resolve().exists():
                errors.append(f"broken local link in {path.relative_to(REPOSITORY_ROOT)}: {target}")


def _validate_ci_workflow(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append("missing .github/workflows/p24-ci.yml")
        return
    content = path.read_text(encoding="utf-8")
    required_fragments = (
        "24-azure-banking-streaming-platform/**",
        '".github/workflows/p24-cd.yml"',
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "BICEP_VERSION:",
        "sha256sum --check --strict",
        "scripts/validate_bicep.sh",
    )
    for fragment in required_fragments:
        if fragment not in content:
            errors.append(f"workflow is missing required safety fragment: {fragment!r}")
    forbidden_fragments = (
        "azure/login",
        "az deployment",
        "bicep deploy",
        "bicep what-if",
        "id-token: write",
        "secrets.",
    )
    for fragment in forbidden_fragments:
        if fragment in content:
            errors.append(f"workflow contains forbidden pre-deployment fragment: {fragment!r}")


def _validate_cd_workflow(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append("missing .github/workflows/p24-cd.yml")
        return
    content = path.read_text(encoding="utf-8")
    required_fragments = (
        "workflow_dispatch:",
        "permissions:\n  contents: read\n  id-token: write",
        "cancel-in-progress: false",
        "environment: dev",
        "persist-credentials: false",
        "azure/login@7ddb5af1ef8758cf1353cf3b42f940aee27ba21c",
        "az deployment group what-if",
        "--validation-level Provider",
        "--mode Incremental",
        "az deployment group create",
        "inputs.confirmation == 'DEPLOY-P24-DEV'",
        "inputs.approved_what_if_run_id != ''",
        "vars.AZURE_CLIENT_ID",
        "vars.AZURE_TENANT_ID",
        "vars.AZURE_SUBSCRIPTION_ID",
    )
    for fragment in required_fragments:
        if fragment not in content:
            errors.append(f"CD workflow is missing required safety fragment: {fragment!r}")

    forbidden_fragments = (
        "\n  push:",
        "\n  pull_request:",
        "\n  schedule:",
        "secrets.",
        "client-secret",
        "az group create",
        "az group delete",
        "az ad ",
        "az role assignment",
        "federated-credential",
        "--mode Complete",
    )
    for fragment in forbidden_fragments:
        if fragment in content:
            errors.append(f"CD workflow contains forbidden fragment: {fragment!r}")


def _validate_infrastructure(infra_root: Path, errors: list[str]) -> None:
    required_files = (
        infra_root / "bicepconfig.json",
        infra_root / "main.bicep",
        infra_root / "environments" / "dev.bicepparam",
        infra_root / "modules" / "data-factory.bicep",
        infra_root / "modules" / "databricks.bicep",
        infra_root / "modules" / "event-hubs.bicep",
        infra_root / "modules" / "key-vault.bicep",
        infra_root / "modules" / "monitoring.bicep",
        infra_root / "modules" / "sql.bicep",
        infra_root / "modules" / "storage.bicep",
    )
    for path in required_files:
        if not path.exists():
            errors.append(f"missing infrastructure file: {path.relative_to(REPOSITORY_ROOT)}")

    parameter_file = infra_root / "environments" / "dev.bicepparam"
    if parameter_file.exists():
        content = parameter_file.read_text(encoding="utf-8")
        required_fragments = (
            "using '../main.bicep'",
            "param environment = 'dev'",
            "replace-in-hito-3",
        )
        for fragment in required_fragments:
            if fragment not in content:
                errors.append(f"dev parameters are missing required marker: {fragment!r}")

    main_template = infra_root / "main.bicep"
    if main_template.exists():
        content = main_template.read_text(encoding="utf-8")
        required_modules = (
            "./modules/data-factory.bicep",
            "./modules/databricks.bicep",
            "./modules/event-hubs.bicep",
            "./modules/key-vault.bicep",
            "./modules/monitoring.bicep",
            "./modules/sql.bicep",
            "./modules/storage.bicep",
        )
        for module in required_modules:
            if module not in content:
                errors.append(f"main Bicep template is missing module: {module}")


def _scan_for_secrets(project_root: Path, errors: list[str]) -> None:
    patterns = (
        re.compile("BEGIN " + "PRIVATE KEY"),
        re.compile("Account" + r"Key\s*="),
        re.compile("SharedAccess" + r"Key\s*="),
        re.compile("gh" + r"p_[A-Za-z0-9]{30,}"),
    )
    candidates = [
        path
        for path in project_root.rglob("*")
        if path.is_file()
        and (path.suffix in SCANNED_SUFFIXES or path.name.startswith(".env"))
        and path.resolve() != Path(__file__).resolve()
    ]
    candidates.extend(
        (
            REPOSITORY_ROOT / ".github" / "workflows" / "p24-ci.yml",
            REPOSITORY_ROOT / ".github" / "workflows" / "p24-cd.yml",
        )
    )
    for path in sorted(set(candidates)):
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if any(pattern.search(content) for pattern in patterns):
            errors.append(f"possible credential material in {path.relative_to(REPOSITORY_ROOT)}")


def main() -> int:
    report = validate_repository()
    if not report.passed:
        for error in report.errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASSED: "
        f"customers={report.customers}, accounts={report.accounts}, "
        f"unique_events={report.unique_events}, invalid_events={report.invalid_events}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
