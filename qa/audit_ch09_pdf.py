#!/usr/bin/env python3
"""Bounded link, navigation, and PDF-safety audit for Chapters 1--9."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from audit_ch05_pdf import main


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf"
EXPECTED_BYTES = 1_686_477
EXPECTED_SHA256 = "99215ff5987f720600152da902cec8f521329692931a0dbf89e82ef2d4ff6076"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    if PDF.stat().st_size != EXPECTED_BYTES or sha256(PDF) != EXPECTED_SHA256:
        raise SystemExit("Chapter 9 PDF identity does not match the frozen audit target")
    sys.argv = [sys.argv[0], str(PDF)]
    main()
