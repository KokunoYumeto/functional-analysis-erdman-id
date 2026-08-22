#!/usr/bin/env python3
"""Inventory and contact-sheet the frozen Chapters 1--10 render."""

from __future__ import annotations

from pathlib import Path

import audit_ch08_render as audit


ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "qa" / "renders" / "ch10-final"
audit.ROOT = ROOT
audit.PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf"
audit.RENDER_DIR = RENDER_DIR
audit.CONTACT_DIR = RENDER_DIR / "contact-sheets"
audit.MANIFEST_JSON = RENDER_DIR / "RENDER_MANIFEST.json"
audit.MANIFEST_CSV = RENDER_DIR / "RENDER_MANIFEST.csv"
audit.EXPECTED_PDF_BYTES = 1_796_056
audit.EXPECTED_PDF_SHA256 = "1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc"
audit.EXPECTED_PAGES = 153


if __name__ == "__main__":
    audit.main()
