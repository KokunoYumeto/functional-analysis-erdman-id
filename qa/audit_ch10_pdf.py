#!/usr/bin/env python3
"""Bounded link, navigation, and PDF-safety audit for Chapters 1--10."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from audit_ch05_pdf import main


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf"
EXPECTED_BYTES = 1_796_056
EXPECTED_SHA256 = "1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    if PDF.stat().st_size != EXPECTED_BYTES or sha256(PDF) != EXPECTED_SHA256:
        raise SystemExit("Chapter 10 PDF identity does not match the frozen audit target")
    sys.argv = [sys.argv[0], str(PDF)]
    main()
