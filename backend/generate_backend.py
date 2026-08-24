#!/usr/bin/env python3
"""Regenerate the latest admitted backend, including the semantic HTML layer."""

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
    # The complete source-text backend is an immutable byte prefix. The latest
    # generator appends only the admitted semantic-HTML surface, assets,
    # artifacts, QA events, and relations, then refreshes the exact manifest.
    run_generator("generate_html_backend.py")


if __name__ == "__main__":
    main()
