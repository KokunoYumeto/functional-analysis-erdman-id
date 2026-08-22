#!/usr/bin/env python3
"""Inventory and contact-sheet the frozen Chapters 1--9 render."""

from __future__ import annotations

from pathlib import Path

import audit_ch08_render as audit


ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "qa" / "renders" / "ch09-final"
audit.ROOT = ROOT
audit.PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf"
audit.RENDER_DIR = RENDER_DIR
audit.CONTACT_DIR = RENDER_DIR / "contact-sheets"
audit.MANIFEST_JSON = RENDER_DIR / "RENDER_MANIFEST.json"
audit.MANIFEST_CSV = RENDER_DIR / "RENDER_MANIFEST.csv"
audit.EXPECTED_PDF_BYTES = 1_686_477
audit.EXPECTED_PDF_SHA256 = "99215ff5987f720600152da902cec8f521329692931a0dbf89e82ef2d4ff6076"
audit.EXPECTED_PAGES = 140


if __name__ == "__main__":
    audit.main()
