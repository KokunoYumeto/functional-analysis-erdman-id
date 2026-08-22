#!/usr/bin/env python3
"""Bounded link, navigation, and PDF-safety audit for Chapters 1--8."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from audit_ch05_pdf import main


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-8.pdf"
EXPECTED_BYTES = 1_593_249
EXPECTED_SHA256 = "fb6488691e2127bc0b8e3f94f38033eb3bdbe0c61efedc66c07de8f3b3444fbd"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    if PDF.stat().st_size != EXPECTED_BYTES or sha256(PDF) != EXPECTED_SHA256:
        raise SystemExit("Chapter 8 PDF identity does not match the frozen audit target")
    sys.argv = [sys.argv[0], str(PDF)]
    main()
