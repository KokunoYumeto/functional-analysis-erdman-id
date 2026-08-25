#!/usr/bin/env python3
"""Anonymously verify the O008 correction-r2 GitHub commit."""

from __future__ import annotations

import contextlib
import io
import json
import sys

import verify_authority_hash_correction_github_public as _base


RECEIPT = (
    _base.ROOT
    / "provenance"
    / "GITHUB_PUBLICATION_RECEIPT_AUTHORITY_HASH_CORRECTION_R2.json"
)
EXPECTED_PATHS = {
    "provenance/AUTHORITY_HASH_CORRECTION_20260825.md",
    "qa/package_authority_hash_correction_release.py",
    "qa/publish_authority_hash_correction_zenodo.py",
    "qa/verify_authority_hash_correction_r2_github_public.py",
    "qa/verify_authority_hash_correction_zenodo_public.py",
}


def main() -> None:
    _base.EXPECTED_PATHS = EXPECTED_PATHS
    _base.RECEIPT = RECEIPT
    if any(argument in {"-h", "--help"} for argument in sys.argv[1:]):
        _base.main()
        return
    with contextlib.redirect_stdout(io.StringIO()):
        _base.main()
    result = json.loads(RECEIPT.read_text(encoding="utf-8"))
    result["receipt_id"] = "FAOA-2015-ID-GITHUB-AUTHORITY-HASH-CORRECTION-R2"
    result["packaged_verifier_fix"] = {
        "prior_zenodo_record_id": "22088619",
        "prior_version": "2026.08.25-authority-hash-correction",
        "false_positive_on_explanatory_occurrences_fixed": True,
        "substantive_pdf_changed": False,
    }
    RECEIPT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
