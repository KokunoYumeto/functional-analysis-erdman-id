#!/usr/bin/env python3
"""Run the locked word-box audit against the Chapters 1--10 reader."""

from __future__ import annotations

from pathlib import Path

import audit_ch08_bbox as audit


ROOT = Path(__file__).resolve().parents[1]
audit.ROOT = ROOT
audit.PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf"
audit.BBOX = ROOT / "qa" / "renders" / "ch10-final" / "functional-analysis-id-through-ch10-bbox.html"
audit.EXPECTED_PAGES = 153
audit.EXPECTED_PDF_BYTES = 1_796_056
audit.EXPECTED_PDF_SHA256 = "1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc"


if __name__ == "__main__":
    audit.main()
