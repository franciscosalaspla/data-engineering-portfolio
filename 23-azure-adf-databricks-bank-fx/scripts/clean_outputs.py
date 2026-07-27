#!/usr/bin/env python3
"""Remove only generated Project 23 outputs while preserving the output directory."""

from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "data" / "output"
GENERATED_NAMES = {
    "audit",
    "bronze",
    "control",
    "gold",
    "gold_quarantine",
    "landing",
    "quarantine",
    "silver",
    "silver_quarantine",
    "serving",
}


def main() -> int:
    output_root = OUTPUT_ROOT.resolve()
    expected = (PROJECT_ROOT / "data" / "output").resolve()
    if output_root != expected or output_root.parent != (PROJECT_ROOT / "data").resolve():
        raise RuntimeError("Refusing to clean an unexpected output path")

    for name in sorted(GENERATED_NAMES):
        target = output_root / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    print(f"Cleaned generated outputs under: {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
