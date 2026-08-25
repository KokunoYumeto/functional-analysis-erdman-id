#!/usr/bin/env python3
"""Anonymously verify the final O008 authority-correction closeout commit."""

from __future__ import annotations

import contextlib
import io
import json
import sys

import verify_authority_hash_correction_github_public as _base


RECEIPT = (
    _base.ROOT
    / "provenance"
    / "GITHUB_PUBLICATION_RECEIPT_AUTHORITY_HASH_CORRECTION_FINAL_CLOSEOUT.json"
)
EXPECTED_PATHS = {
    "README.md",
    "provenance/AUTHORITY_HASH_CORRECTION_R2_RELEASE_PACKAGE_RECEIPT.json",
    "provenance/GITHUB_PUBLICATION_RECEIPT_AUTHORITY_HASH_CORRECTION.json",
    "provenance/GITHUB_PUBLICATION_RECEIPT_AUTHORITY_HASH_CORRECTION_R2.json",
    "provenance/GITHUB_REPOSITORY_METADATA_AUTHORITY_HASH_CORRECTION_R2.json",
    "provenance/O008_COORDINATOR_HANDOFF_FINAL.json",
    "provenance/ZENODO_PUBLICATION_RECEIPT_AUTHORITY_HASH_CORRECTION.json",
    "qa/verify_authority_hash_correction_final_closeout_github_public.py",
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
    result["receipt_id"] = (
        "FAOA-2015-ID-GITHUB-AUTHORITY-HASH-CORRECTION-FINAL-CLOSEOUT"
    )
    result["zenodo_latest"] = {
        "concept_doi": "10.5281/zenodo.22059739",
        "record_id": "22088677",
        "version_doi": "10.5281/zenodo.22088677",
        "version": "2026.08.25-authority-hash-correction-r2",
        "anonymous_metadata_and_file_readback": True,
    }
    result["substantive_pdf_changed"] = False
    RECEIPT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
