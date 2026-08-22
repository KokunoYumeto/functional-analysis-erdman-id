#!/usr/bin/env python3
"""Run the locked text/font audit against the Chapters 1--9 reader."""

from __future__ import annotations

from pathlib import Path

import audit_ch08_text_fonts as audit


ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "qa" / "renders" / "ch09-final"
audit.ROOT = ROOT
audit.RENDER_DIR = RENDER_DIR
audit.PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf"
audit.TEXT = RENDER_DIR / "functional-analysis-id-through-ch09-layout.txt"
audit.FONTS = RENDER_DIR / "functional-analysis-id-through-ch09-fonts.txt"
audit.INFO = RENDER_DIR / "functional-analysis-id-through-ch09-pdfinfo.txt"
audit.EXPECTED_PAGES = 140
audit.EXPECTED_PDF_BYTES = 1_686_477
audit.EXPECTED_PDF_SHA256 = "99215ff5987f720600152da902cec8f521329692931a0dbf89e82ef2d4ff6076"


if __name__ == "__main__":
    audit.main()
