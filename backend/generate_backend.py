#!/usr/bin/env python3
"""Regenerate the Chapter 1--10 backend and additive terminology-QA layer."""

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
    # Chapter 10 generator. Replaying their historical checkers would wrongly
    # revalidate obsolete whole-ledger hashes after later chapter appends.
    # The terminology-QA layer is an immutable additive Chapter 1--9 input.
    # Its historical generator intentionally requires the exact pre-Chapter-10
    # terminology file, so replaying it after this append would be invalid.
    # The full validator still checks its exact ordering, evidence, and IDs.
    run_generator("generate_ch10_backend.py")


if __name__ == "__main__":
    main()
