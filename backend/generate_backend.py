#!/usr/bin/env python3
"""Generate all deterministic backend projections in chapter order."""

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
    run_generator("generate_ch01_backend.py")
    run_generator("generate_ch02_backend.py")
    run_generator("generate_ch03_backend.py")
    run_generator("generate_ch04_backend.py")
    run_generator("generate_ch05_backend.py")
    run_generator("generate_ch06_backend.py")
    run_generator("generate_ch07_backend.py")


if __name__ == "__main__":
    main()
