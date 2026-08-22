#!/usr/bin/env python3
"""Run the locked text/font audit against the Chapters 1--10 reader."""

from __future__ import annotations

from pathlib import Path

import audit_ch08_text_fonts as audit


ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "qa" / "renders" / "ch10-final"
audit.ROOT = ROOT
audit.RENDER_DIR = RENDER_DIR
audit.PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf"
audit.TEXT = RENDER_DIR / "functional-analysis-id-through-ch10-layout.txt"
audit.FONTS = RENDER_DIR / "functional-analysis-id-through-ch10-fonts.txt"
audit.INFO = RENDER_DIR / "functional-analysis-id-through-ch10-pdfinfo.txt"
audit.EXPECTED_PAGES = 153
audit.EXPECTED_PDF_BYTES = 1_796_056
audit.EXPECTED_PDF_SHA256 = "1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc"


if __name__ == "__main__":
    audit.main()
