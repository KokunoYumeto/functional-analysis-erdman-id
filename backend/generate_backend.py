#!/usr/bin/env python3
"""Regenerate the current backend from its frozen Chapter 1--8 byte prefix."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BACKEND = Path(__file__).resolve().parent
ROOT = BACKEND.parent


def run_generator(name: str) -> None:
    result = subprocess.run(
        [sys.executable, str(BACKEND / name)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stderr:
        sys.stderr.write(result.stderr)
    print(result.stdout.strip())


def main() -> None:
    # Earlier chapter projections are immutable inputs to the append-only
    # Chapter 9 generator. Replaying their historical checkers would wrongly
    # revalidate obsolete whole-ledger hashes after later chapter appends.
    run_generator("generate_ch09_backend.py")


if __name__ == "__main__":
    main()
