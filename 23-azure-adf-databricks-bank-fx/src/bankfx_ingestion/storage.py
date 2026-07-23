"""Filesystem operations for immutable Landing and partitioned Bronze outputs."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Iterable


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_checksum(record: dict[str, Any]) -> str:
    encoded = json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def copy_to_landing(
    source_path: Path,
    output_root: Path,
    source_name: str,
    entity_name: str,
    ingestion_date: str,
    run_id: str,
    checksum: str,
    ingested_at: str,
) -> tuple[Path, Path]:
    target_dir = (
        output_root
        / "landing"
        / source_name
        / entity_name
        / f"ingestion_date={ingestion_date}"
        / f"run_id={run_id}"
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source_path.name
    if target.exists():
        if sha256_file(target) != checksum:
            raise FileExistsError(f"Immutable Landing target already exists with different content: {target}")
    else:
        shutil.copyfile(source_path, target)

    metadata_path = target.with_name(f"{target.name}.metadata.json")
    metadata = {
        "run_id": run_id,
        "source_name": source_name,
        "entity_name": entity_name,
        "source_file": source_path.name,
        "landing_file": target.as_posix(),
        "sha256": checksum,
        "ingested_at": ingested_at,
        "ingestion_date": ingestion_date,
    }
    write_json_once(metadata_path, metadata)
    return target, metadata_path


def write_jsonl_once(path: Path, records: Iterable[dict[str, Any]]) -> None:
    if path.exists():
        raise FileExistsError(f"Immutable output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def write_json_once(path: Path, payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != serialized:
            raise FileExistsError(f"Immutable metadata already exists with different content: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)


def relative_to_project(path: Path, project_root: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()
