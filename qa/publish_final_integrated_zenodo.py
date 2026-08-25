#!/usr/bin/env python3
"""Publish the complete integrated O008 edition in its existing Zenodo concept.

Credential bytes are read only after all local and anonymous-public preflights
pass, and only by the inherited authenticated transaction routine.  They are
never printed, copied into receipts, or placed in request URLs.
"""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Any

import package_final_integrated_release as package
import publish_html_reader_zenodo as release


EXPECTED_CONCEPTRECID = "22059739"
EXPECTED_PREVIOUS_RECORD_ID = "22086801"
EXPECTED_PREVIOUS_VERSION = "2026.08.24-html-reader"
VERSION = package.RELEASE
PUBLICATION_DATE = "2026-08-25"
TITLE = "Analisis Fungsional dan Aljabar Operator: Suatu Pengantar — Edisi Bahasa Indonesia"
PDF_NAME = package.PDF_NAME
ZIP_NAME = package.ZIP_NAME
SUMS_NAME = package.SUMS_NAME
PREFIX = package.PREFIX

EXPECTED_KEYWORDS = {
    "functional analysis",
    "operator algebras",
    "Bahasa Indonesia",
    "open textbook",
    "CC BY-SA 4.0",
    "Banach space",
    "Hilbert space",
    "spectral theory",
    "machine-readable curriculum",
}
EXPECTED_CREATORS = {"Erdman, John M."}
EXPECTED_CONTRIBUTORS = {("Codex", "Other")}
EXPECTED_RELATED = {
    (
        "https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_pdf.pdf",
        "isDerivedFrom",
        "publication-book",
    ),
    (
        "https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_web.zip",
        "isDerivedFrom",
        "software",
    ),
    (
        "https://github.com/KokunoYumeto/functional-analysis-erdman-id",
        "isSupplementedBy",
        "software",
    ),
}
DESCRIPTION_MARKERS = (
    "Status keseluruhan: edisi lengkap",
    "PDF utama 298 halaman",
    "52 latihan sumber",
    "10 hasil kerja-pembaca terpilih",
    "13 unit jembatan spektral-kompak/SVD",
    "Dua reader HTML semantik",
    "CC BY-SA 4.0",
    "Tidak ada dukungan atau persetujuan tersirat",
    "OpenAI Codex gpt-5.6-sol, Ultra",
    "belum bertag",
)


def description(github_commit: str) -> str:
    return (
        "<p><strong>Status keseluruhan: edisi lengkap.</strong> PDF utama 298 halaman "
        "memuat prakata, seluruh 17 bab sumber, bibliografi, indeks terjemahan, "
        "solusi terpisah untuk seluruh 52 latihan sumber, solusi untuk 10 hasil "
        "kerja-pembaca terpilih, dan 13 unit jembatan spektral-kompak/SVD.</p>"
        "<p>Adaptasi dari John M. Erdman, <em>Functional Analysis and Operator "
        "Algebras: An Introduction</em>, versi 4 Oktober 2015. Karya sumber dan "
        "adaptasi ini berlisensi CC BY-SA 4.0. Komponen solusi O001, jembatan, "
        "backend, dan permukaan aksesibilitas diberi provenans terpisah dan "
        "lisensi kompatibel. Perubahan dicatat transparan. Tidak ada dukungan "
        "atau persetujuan tersirat dari John M. Erdman maupun Portland State "
        "University.</p>"
        "<p>Terjemahan, penyuntingan teknis, solusi, dan integrasi dibantu oleh "
        "<strong>OpenAI Codex gpt-5.6-sol, Ultra</strong>, atas arahan pengguna "
        "manusia. Kredit penulis sumber dan kontributor komponen tetap "
        "dipertahankan.</p>"
        "<p>PDF belum bertag dan tidak diklaim sebagai permukaan aksesibel. Dua "
        "reader HTML semantik/offline menyediakan MathML, reflow responsif, "
        "navigasi stabil, teks alternatif, dan transkrip diagram untuk teks sumber "
        "serta materi pendamping. Arsip ringkas memuat sumber yang dapat dilanjutkan, "
        "kedua reader HTML, backend modular, LICENSE, manifest, checksum, dan bukti "
        "QA; arsip mengikat commit publik GitHub "
        f"<code>{github_commit}</code>.</p>"
        "<p>Mirror GitHub dan unduhan HTML offline: "
        "<a href=\"https://github.com/KokunoYumeto/functional-analysis-erdman-id\">"
        "functional-analysis-erdman-id</a>.</p>"
    )


def validate_payload(
    pdf_path: Path, zip_path: Path, sums_path: Path, github_commit: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    receipts = [release.digest(path) for path in (pdf_path, zip_path, sums_path)]
    expected_sums = {item["filename"]: item["sha256"] for item in receipts[:2]}
    parsed: dict[str, str] = {}
    for line in sums_path.read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match or match.group(2) in parsed:
            raise RuntimeError("SHA256SUMS.txt is malformed or duplicated")
        parsed[match.group(2)] = match.group(1)
    if parsed != expected_sums:
        raise RuntimeError("SHA256SUMS.txt does not bind exactly the PDF and ZIP")

    metadata, payload, _ = package.read_release_archive(zip_path)
    required = {
        "schema_version": "o008.release-final-integrated.v1",
        "release": VERSION,
        "overall_status": "complete",
        "source_text_status": "complete",
        "semantic_html_status": "complete",
        "mastery_solution_status": "complete",
        "selected_reader_work_status": "complete",
        "compact_spectral_svd_bridge_status": "complete",
        "companion_html_status": "complete",
        "remaining_components": [],
        "git_commit": github_commit,
        "license": "CC BY-SA 4.0",
        "primary_reader_uploaded_separately": PDF_NAME,
        "primary_reader_pages": 298,
        "source_exercise_solutions": 52,
        "selected_reader_work_solutions": 10,
        "compact_spectral_svd_bridge_units": 13,
    }
    if any(metadata.get(key) != value for key, value in required.items()):
        raise RuntimeError("source/backend/HTML ZIP metadata differs from this release")
    if not re.fullmatch(r"[0-9a-f]{40}", str(metadata.get("git_tree", ""))):
        raise RuntimeError("release archive has no exact Git tree identity")
    pdf_data = pdf_path.read_bytes()
    if (
        len(pdf_data) != int(metadata.get("primary_reader_bytes", -1))
        or package.sha256(pdf_data) != metadata.get("primary_reader_sha256")
    ):
        raise RuntimeError("PDF differs from the archive's exact final-reader identity")
    build = json.loads(payload["qa/FINAL_COMPANION_BUILD_RESULT.json"])
    if (
        build.get("result") != "pass"
        or int(build.get("pages", -1)) != 298
        or build.get("pdf", {}).get("sha256") != package.sha256(pdf_data)
    ):
        raise RuntimeError("PDF differs from the packaged final build receipt")
    if "LICENSE.md" not in payload:
        raise RuntimeError("release archive lacks the exact CC BY-SA license file")
    if len(pdf_data) + zip_path.stat().st_size > package.MAX_RELEASE_BYTES:
        raise RuntimeError("release payload exceeds the 500,000,000-byte cap")
    return receipts, metadata


_base_writable_metadata = release.writable_metadata


def writable_metadata(existing: dict[str, Any], github_commit: str) -> dict[str, Any]:
    metadata = _base_writable_metadata(existing, github_commit)
    metadata.update(
        {
            "title": TITLE,
            "description": description(github_commit),
            "publication_date": PUBLICATION_DATE,
            "version": VERSION,
        }
    )
    return metadata


def assert_release_metadata(metadata: dict[str, Any], github_commit: str) -> None:
    creators = {
        str(item.get("name", ""))
        for item in metadata.get("creators", [])
        if isinstance(item, dict)
    }
    contributors = {
        (str(item.get("name", "")), str(item.get("type", "")))
        for item in metadata.get("contributors", [])
        if isinstance(item, dict)
    }
    related = {
        (
            str(item.get("identifier", "")),
            str(item.get("relation", "")),
            str(item.get("resource_type", "")),
        )
        for item in metadata.get("related_identifiers", [])
        if isinstance(item, dict)
    }
    exact = {
        "title": TITLE,
        "publication_date": PUBLICATION_DATE,
        "version": VERSION,
        "language": "ind",
        "access_right": "open",
        "upload_type": "publication",
        "publication_type": "book",
    }
    if any(metadata.get(key) != value for key, value in exact.items()):
        raise RuntimeError("Zenodo draft metadata has an incorrect core field")
    if release.metadata_license_id(metadata) != "cc-by-sa-4.0":
        raise RuntimeError("Zenodo draft license is not CC BY-SA 4.0")
    if creators != EXPECTED_CREATORS or contributors != EXPECTED_CONTRIBUTORS:
        raise RuntimeError("Zenodo draft creator/contributor credit differs")
    if set(metadata.get("keywords", [])) != EXPECTED_KEYWORDS:
        raise RuntimeError("Zenodo draft keyword set differs")
    if related != EXPECTED_RELATED:
        raise RuntimeError("Zenodo draft related-identifier relations differ")
    description_text = str(metadata.get("description", ""))
    if github_commit not in description_text or not all(
        marker in description_text for marker in DESCRIPTION_MARKERS
    ):
        raise RuntimeError("Zenodo draft description lacks a required completion marker")


# Reuse the already-tested, existing-concept transaction machinery with this
# release's stricter local contract and metadata.  These assignments do not
# access credentials or mutate Zenodo.
release.PACKAGE = package
release.EXPECTED_CONCEPTRECID = EXPECTED_CONCEPTRECID
release.EXPECTED_PREVIOUS_RECORD_ID = EXPECTED_PREVIOUS_RECORD_ID
release.EXPECTED_PREVIOUS_VERSION = EXPECTED_PREVIOUS_VERSION
release.VERSION = VERSION
release.TITLE = TITLE
release.PDF_NAME = PDF_NAME
release.ZIP_NAME = ZIP_NAME
release.SUMS_NAME = SUMS_NAME
release.PREFIX = PREFIX
release.EXPECTED_KEYWORDS = EXPECTED_KEYWORDS
release.EXPECTED_CREATORS = EXPECTED_CREATORS
release.EXPECTED_CONTRIBUTORS = EXPECTED_CONTRIBUTORS
release.EXPECTED_RELATED = EXPECTED_RELATED
release.DESCRIPTION_MARKERS = DESCRIPTION_MARKERS
release.validate_payload = validate_payload
release.description = description
release.writable_metadata = writable_metadata
release.assert_release_metadata = assert_release_metadata


if __name__ == "__main__":
    release.main()
