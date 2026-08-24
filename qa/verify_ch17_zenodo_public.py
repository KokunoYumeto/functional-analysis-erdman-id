#!/usr/bin/env python3
"""Anonymously verify the public Chapter 17 Zenodo record and file bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
CONCEPT_ID = "22059739"
VERSION = "2026.08.24-ch17"
FILES = {
    "analisis-fungsional-dan-aljabar-operator-id-bab-1-17.pdf": ROOT
    / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-17.pdf",
    "functional-analysis-erdman-id-2026.08.24-ch17-source-backend.zip": ROOT
    / "qa" / "release-ch17"
    / "functional-analysis-erdman-id-2026.08.24-ch17-source-backend.zip",
    "SHA256SUMS.txt": ROOT / "qa" / "release-ch17" / "SHA256SUMS.txt",
}
RECEIPT = ROOT / "provenance" / "ZENODO_PUBLICATION_RECEIPT_CH17.json"


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
    if (
        str(record.get("id")) != args.record_id
        or str(record.get("conceptrecid")) != CONCEPT_ID
        or metadata.get("version") != VERSION
        or metadata.get("doi") != args.doi
        or metadata.get("license", {}).get("id") != "cc-by-sa-4.0"
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
        receipts.append({"filename": name, "bytes": len(local), "sha256": sha256(local),
                         "matches_local_bytes": True})

    result = {
        "schema_version": "1.0.0", "receipt_id": "FAOA-2015-CH17-ZENODO-PUBLICATION",
        "verified_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "conceptrecid": CONCEPT_ID, "record_id": args.record_id, "doi": args.doi,
        "record_url": f"https://zenodo.org/records/{args.record_id}", "version": VERSION,
        "license": "CC BY-SA 4.0", "status": "published",
        "anonymous_metadata_readback": True, "anonymous_file_byte_readback": True,
        "files": receipts, "credential_material_recorded": False, "result": "pass",
    }
    RECEIPT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
