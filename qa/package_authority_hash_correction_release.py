#!/usr/bin/env python3
"""Build the deterministic O008 authority-hash-correction release bundle."""

from __future__ import annotations

import package_final_integrated_release as _base


RELEASE = "2026.08.25-authority-hash-correction-r2"
PREFIX = f"functional-analysis-erdman-id-{RELEASE}"
PDF_NAME = _base.PDF_NAME
ZIP_NAME = f"{PREFIX}-source-backend-html.zip"
SUMS_NAME = _base.SUMS_NAME
ROOT = _base.ROOT
OUTPUT_DIR = ROOT / "qa" / "release-authority-hash-correction-r2"
MAX_RELEASE_BYTES = _base.MAX_RELEASE_BYTES
ZIP_TIMESTAMP = (2026, 8, 25, 1, 30, 0)

CORRECTION_SCRIPTS = {
    "qa/package_authority_hash_correction_release.py",
    "qa/publish_authority_hash_correction_zenodo.py",
    "qa/verify_authority_hash_correction_github_public.py",
    "qa/verify_authority_hash_correction_r2_github_public.py",
    "qa/verify_authority_hash_correction_zenodo_public.py",
}
CORRECTION_PROVENANCE = {
    "provenance/AUTHORITY_HASH_CORRECTION_20260825.md",
}


def configure() -> None:
    _base.RELEASE = RELEASE
    _base.PREFIX = PREFIX
    _base.PDF_NAME = PDF_NAME
    _base.ZIP_NAME = ZIP_NAME
    _base.SUMS_NAME = SUMS_NAME
    _base.OUTPUT_DIR = OUTPUT_DIR
    _base.ZIP_TIMESTAMP = ZIP_TIMESTAMP
    _base.RESUMABLE_FILES = set(_base.RESUMABLE_FILES) | CORRECTION_SCRIPTS
    _base.PROVENANCE_FILES = set(_base.PROVENANCE_FILES) | CORRECTION_PROVENANCE
    _base.STATIC_REQUIRED = (
        set(_base.BASE_PACKAGE.REQUIRED_EXACT)
        | _base.FINAL_QA_FILES
        | _base.RESUMABLE_FILES
        | _base.PROVENANCE_FILES
        | {
            _base.BASE_HTML_MANIFEST,
            _base.COMPANION_BACKEND_MANIFEST,
            _base.COMPANION_HTML_MANIFEST,
        }
    )


configure()

# Re-export the tested implementation after configuring its release globals.
sha256 = _base.sha256
read_release_archive = _base.read_release_archive
verify_payload = _base.verify_payload


def main() -> None:
    configure()
    _base.main()


if __name__ == "__main__":
    main()
