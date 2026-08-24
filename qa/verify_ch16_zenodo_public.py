#!/usr/bin/env python3
"""Anonymously verify the public Chapter 16 Zenodo record and file bytes."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
RECORD_ID = "22076176"
CONCEPT_ID = "22059739"
VERSION = "2026.08.24-ch16"
DOI = "10.5281/zenodo.22076176"
FILES = {
    "analisis-fungsional-dan-aljabar-operator-id-bab-1-16.pdf": ROOT
    / "output"
    / "pdf"
    / "analisis-fungsional-dan-aljabar-operator-id-bab-1-16.pdf",
    "functional-analysis-erdman-id-2026.08.24-ch16-source-backend.zip": ROOT
    / "qa"
    / "release-ch16"
    / "functional-analysis-erdman-id-2026.08.24-ch16-source-backend.zip",
    "SHA256SUMS.txt": ROOT / "qa" / "release-ch16" / "SHA256SUMS.txt",
}
RECEIPT = ROOT / "provenance" / "ZENODO_PUBLICATION_RECEIPT_CH16.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    session = requests.Session()
    metadata_response = session.get(
        f"https://zenodo.org/api/records/{RECORD_ID}", timeout=30
    )
    if metadata_response.status_code != 200:
        raise SystemExit(
            f"anonymous Zenodo metadata returned {metadata_response.status_code}"
        )
    record = metadata_response.json()
    metadata = record.get("metadata", {})
    if (
        str(record.get("id")) != RECORD_ID
        or str(record.get("conceptrecid")) != CONCEPT_ID
        or metadata.get("version") != VERSION
        or metadata.get("doi") != DOI
        or metadata.get("license", {}).get("id") != "cc-by-sa-4.0"
    ):
        raise SystemExit("public Zenodo metadata identity differs")

    public_files = {item["key"]: item for item in record.get("files", [])}
    if set(public_files) != set(FILES):
        raise SystemExit("public Zenodo file inventory differs")

    receipts: list[dict[str, object]] = []
    for name, local_path in FILES.items():
        local = local_path.read_bytes()
        item = public_files[name]
        response = session.get(item["links"]["self"], timeout=120)
        if response.status_code != 200:
            raise SystemExit(f"anonymous Zenodo file read failed for {name}")
        public = response.content
        match = public == local
        if not match:
            raise SystemExit(f"public Zenodo bytes differ for {name}")
        receipts.append(
            {
                "filename": name,
                "bytes": len(public),
                "sha256": sha256(public),
                "matches_local_bytes": True,
            }
        )

    result = {
        "schema_version": "1.0.0",
        "receipt_id": "FAOA-2015-CH16-ZENODO-PUBLICATION",
        "verified_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "conceptrecid": CONCEPT_ID,
        "record_id": RECORD_ID,
        "doi": DOI,
        "record_url": f"https://zenodo.org/records/{RECORD_ID}",
        "version": VERSION,
        "license": "CC BY-SA 4.0",
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
