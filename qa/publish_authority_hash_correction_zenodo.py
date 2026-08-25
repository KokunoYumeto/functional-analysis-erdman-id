#!/usr/bin/env python3
"""Publish the corrected O008 authority metadata in the existing Zenodo concept."""

from __future__ import annotations

import package_authority_hash_correction_release as package
import publish_final_integrated_zenodo as _prior


EXPECTED_CONCEPTRECID = _prior.EXPECTED_CONCEPTRECID
EXPECTED_PREVIOUS_RECORD_ID = "22088619"
EXPECTED_PREVIOUS_VERSION = "2026.08.25-authority-hash-correction"
VERSION = package.RELEASE
PUBLICATION_DATE = _prior.PUBLICATION_DATE
TITLE = _prior.TITLE
PDF_NAME = package.PDF_NAME
ZIP_NAME = package.ZIP_NAME
SUMS_NAME = package.SUMS_NAME
PREFIX = package.PREFIX
EXPECTED_KEYWORDS = _prior.EXPECTED_KEYWORDS
EXPECTED_CREATORS = _prior.EXPECTED_CREATORS
EXPECTED_CONTRIBUTORS = _prior.EXPECTED_CONTRIBUTORS
EXPECTED_RELATED = _prior.EXPECTED_RELATED
CORRECTION_MARKER = "Koreksi metadata otoritas sumber"
DESCRIPTION_MARKERS = _prior.DESCRIPTION_MARKERS + (CORRECTION_MARKER,)
_base_description = _prior.description


def description(github_commit: str) -> str:
    return _base_description(github_commit) + (
        "<p><strong>Koreksi metadata otoritas sumber:</strong> versi ini "
        "memperbaiki satu nilai SHA-256 arsip sumber resmi yang sebelumnya "
        "kehilangan satu karakter <code>b</code>. PDF 298 halaman, matematika, "
        "terjemahan, solusi, reader HTML, dan lisensi tidak berubah. Nilai yang "
        "benar diverifikasi ulang langsung dari 262.556 byte ZIP resmi dan 27 "
        "anggota manifes. Revisi r2 juga memuat verifier anonim yang telah "
        "diperbaiki agar catatan penjelas koreksi tidak dianggap sebagai "
        "kontaminasi metadata.</p>"
    )


def configure() -> None:
    _prior.package = package
    _prior.EXPECTED_CONCEPTRECID = EXPECTED_CONCEPTRECID
    _prior.EXPECTED_PREVIOUS_RECORD_ID = EXPECTED_PREVIOUS_RECORD_ID
    _prior.EXPECTED_PREVIOUS_VERSION = EXPECTED_PREVIOUS_VERSION
    _prior.VERSION = VERSION
    _prior.PUBLICATION_DATE = PUBLICATION_DATE
    _prior.TITLE = TITLE
    _prior.PDF_NAME = PDF_NAME
    _prior.ZIP_NAME = ZIP_NAME
    _prior.SUMS_NAME = SUMS_NAME
    _prior.PREFIX = PREFIX
    _prior.DESCRIPTION_MARKERS = DESCRIPTION_MARKERS
    _prior.description = description

    transaction = _prior.release
    transaction.PACKAGE = package
    transaction.EXPECTED_CONCEPTRECID = EXPECTED_CONCEPTRECID
    transaction.EXPECTED_PREVIOUS_RECORD_ID = EXPECTED_PREVIOUS_RECORD_ID
    transaction.EXPECTED_PREVIOUS_VERSION = EXPECTED_PREVIOUS_VERSION
    transaction.VERSION = VERSION
    transaction.TITLE = TITLE
    transaction.PDF_NAME = PDF_NAME
    transaction.ZIP_NAME = ZIP_NAME
    transaction.SUMS_NAME = SUMS_NAME
    transaction.PREFIX = PREFIX
    transaction.EXPECTED_KEYWORDS = EXPECTED_KEYWORDS
    transaction.EXPECTED_CREATORS = EXPECTED_CREATORS
    transaction.EXPECTED_CONTRIBUTORS = EXPECTED_CONTRIBUTORS
    transaction.EXPECTED_RELATED = EXPECTED_RELATED
    transaction.DESCRIPTION_MARKERS = DESCRIPTION_MARKERS
    transaction.validate_payload = _prior.validate_payload
    transaction.description = description
    transaction.writable_metadata = _prior.writable_metadata
    transaction.assert_release_metadata = _prior.assert_release_metadata


configure()

validate_payload = _prior.validate_payload
assert_release_metadata = _prior.assert_release_metadata
writable_metadata = _prior.writable_metadata


def main() -> None:
    configure()
    _prior.release.main()


if __name__ == "__main__":
    main()
