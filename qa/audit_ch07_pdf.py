#!/usr/bin/env python3
"""Bounded link, navigation, and PDF-safety audit for Chapters 1--7."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from audit_ch05_pdf import main


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "qa" / "build-through-ch07-a" / "functional-analysis-id-through-ch07.pdf"
EXPECTED_BYTES = 1_530_677
EXPECTED_SHA256 = "a7ddaef324bd356d258cb47195f524e027ba54a696cb8d38a8358bb8d0a2d7ff"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    if PDF.stat().st_size != EXPECTED_BYTES or sha256(PDF) != EXPECTED_SHA256:
        raise SystemExit("Chapter 7 PDF identity does not match the frozen audit target")
    sys.argv = [sys.argv[0], str(PDF)]
    main()
