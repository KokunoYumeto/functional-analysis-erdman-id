#!/usr/bin/env python3
"""Anonymously verify the public complete-source Zenodo record and file bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
CONCEPT_ID = "22059739"
VERSION = "2026.08.24-source-text"
TITLE = "Analisis Fungsional dan Aljabar Operator: Suatu Pengantar — Edisi Bahasa Indonesia"
PUBLICATION_DATE = "2026-08-24"
DESCRIPTION_MARKERS = (
    "terjemahan teks sumber lengkap",
    "CC BY-SA 4.0",
    "Tidak ada dukungan atau persetujuan tersirat",
    "OpenAI Codex gpt-5.6-sol, Ultra",
    "PDF 238 halaman",
    "belum bertag",
)
RELATED_IDENTIFIERS = {
    "https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_pdf.pdf",
    "https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_web.zip",
    "https://github.com/KokunoYumeto/functional-analysis-erdman-id",
}
FILES = {
    "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf": ROOT
    / "output" / "pdf"
    / "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf",
    "functional-analysis-erdman-id-2026.08.24-source-text-source-backend.zip": ROOT
    / "qa" / "release-complete-source"
    / "functional-analysis-erdman-id-2026.08.24-source-text-source-backend.zip",
    "SHA256SUMS.txt": ROOT / "qa" / "release-complete-source" / "SHA256SUMS.txt",
}
RECEIPT = ROOT / "provenance" / "ZENODO_PUBLICATION_RECEIPT_COMPLETE_SOURCE.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--doi", required=True)
    args = parser.parse_args()
    expected_doi = f"10.5281/zenodo.{args.record_id}"
    if args.doi != expected_doi:
        raise SystemExit("record ID and DOI differ")

    session = requests.Session()
    response = session.get(f"https://zenodo.org/api/records/{args.record_id}", timeout=30)
    if response.status_code != 200:
        raise SystemExit(f"anonymous Zenodo metadata returned {response.status_code}")
    record = response.json()
    metadata = record.get("metadata", {})
    description = str(metadata.get("description", ""))
    creators = metadata.get("creators", [])
    related = {
        str(item.get("identifier", ""))
        for item in metadata.get("related_identifiers", [])
        if isinstance(item, dict)
    }
    if (
        str(record.get("id")) != args.record_id
        or str(record.get("conceptrecid")) != CONCEPT_ID
        or metadata.get("version") != VERSION
        or metadata.get("doi") != args.doi
        or metadata.get("license", {}).get("id") != "cc-by-sa-4.0"
        or metadata.get("title") != TITLE
        or metadata.get("publication_date") != PUBLICATION_DATE
        or metadata.get("language") != "ind"
        or not any(
            isinstance(item, dict) and "Erdman" in str(item.get("name", ""))
            for item in creators
        )
        or not all(marker in description for marker in DESCRIPTION_MARKERS)
        or not RELATED_IDENTIFIERS <= related
    ):
        raise SystemExit("public Zenodo metadata identity differs")

    public_files = {item["key"]: item for item in record.get("files", [])}
    if set(public_files) != set(FILES):
        raise SystemExit("public Zenodo file inventory differs")
    receipts: list[dict[str, object]] = []
    for name, local_path in FILES.items():
        local = local_path.read_bytes()
        file_response = session.get(public_files[name]["links"]["self"], timeout=120)
        if file_response.status_code != 200 or file_response.content != local:
            raise SystemExit(f"anonymous Zenodo file readback differs for {name}")
        receipts.append(
            {
                "filename": name,
                "bytes": len(local),
                "sha256": sha256(local),
                "matches_local_bytes": True,
            }
        )

    result = {
        "schema_version": "1.0.0",
        "receipt_id": "FAOA-2015-COMPLETE-SOURCE-ZENODO-PUBLICATION",
        "verified_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "conceptrecid": CONCEPT_ID,
        "record_id": args.record_id,
        "doi": args.doi,
        "record_url": f"https://zenodo.org/records/{args.record_id}",
        "version": VERSION,
        "license": "CC BY-SA 4.0",
        "title": metadata["title"],
        "publication_date": metadata["publication_date"],
        "language": metadata["language"],
        "source_author_credit_present": True,
        "scope_nonendorsement_component_model_metadata_present": True,
        "required_related_identifiers_present": True,
        "status": "published",
        "anonymous_metadata_readback": True,
        "anonymous_file_byte_readback": True,
        "files": receipts,
        "credential_material_recorded": False,
        "result": "pass",
    }
    RECEIPT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
