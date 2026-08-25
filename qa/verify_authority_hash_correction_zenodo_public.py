#!/usr/bin/env python3
"""Anonymously verify the corrected O008 Zenodo release and every file byte."""

from __future__ import annotations

import contextlib
import io
import json
import sys

import package_authority_hash_correction_release as package
import publish_authority_hash_correction_zenodo as publish
import verify_final_integrated_zenodo_public as _base


ROOT = package.ROOT
RECEIPT = (
    ROOT
    / "provenance"
    / "ZENODO_PUBLICATION_RECEIPT_AUTHORITY_HASH_CORRECTION.json"
)
CORRECT_HASH = b"0c667cfa7420b61dda8f8cb4ed9d619db8abbd1b53d17eafe7d4a2e153342e53"
INCORRECT_HASH = b"0c667cfa7420b61dda8f8cb4ed9d619db8abd1b53d17eafe7d4a2e153342e53"


def configure() -> None:
    publish.configure()
    _base.package = package
    _base.publish = publish
    _base.CONCEPT_ID = publish.EXPECTED_CONCEPTRECID
    _base.VERSION = publish.VERSION
    _base.TITLE = publish.TITLE
    _base.PUBLICATION_DATE = publish.PUBLICATION_DATE
    _base.PDF_NAME = package.PDF_NAME
    _base.ZIP_NAME = package.ZIP_NAME
    _base.SUMS_NAME = package.SUMS_NAME
    _base.FILES = {
        package.PDF_NAME: ROOT / "output" / "pdf" / package.PDF_NAME,
        package.ZIP_NAME: package.OUTPUT_DIR / package.ZIP_NAME,
        package.SUMS_NAME: package.OUTPUT_DIR / package.SUMS_NAME,
    }
    _base.RECEIPT = RECEIPT


def main() -> None:
    configure()
    if any(argument in {"-h", "--help"} for argument in sys.argv[1:]):
        _base.main()
        return
    zip_path = package.OUTPUT_DIR / package.ZIP_NAME
    _, payload, _ = package.read_release_archive(zip_path)
    contaminated = sorted(path for path, data in payload.items() if INCORRECT_HASH in data)
    if contaminated:
        raise SystemExit(f"invalid 63-character authority hash remains: {contaminated}")
    required = {
        "provenance/SOURCE_AUTHORITY.md",
        "provenance/FINAL_EDITION_BUILD_AND_QA_RECEIPT.md",
        "provenance/AUTHORITY_HASH_CORRECTION_20260825.md",
    }
    missing_correct = sorted(path for path in required if CORRECT_HASH not in payload[path])
    if missing_correct:
        raise SystemExit(f"correct authority hash missing from: {missing_correct}")

    with contextlib.redirect_stdout(io.StringIO()):
        _base.main()
    result = json.loads(RECEIPT.read_text(encoding="utf-8"))
    result["receipt_id"] = "FAOA-2015-ID-ZENODO-AUTHORITY-HASH-CORRECTION"
    result["prior_record_id"] = publish.EXPECTED_PREVIOUS_RECORD_ID
    result["prior_version"] = publish.EXPECTED_PREVIOUS_VERSION
    result["authority_hash_correction"] = {
        "official_source_zip_bytes": 262556,
        "correct_sha256": CORRECT_HASH.decode("ascii"),
        "incorrect_63_character_value_absent_from_release_archive": True,
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
