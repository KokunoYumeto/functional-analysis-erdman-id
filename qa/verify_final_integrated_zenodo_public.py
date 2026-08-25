#!/usr/bin/env python3
"""Anonymously verify the public complete integrated O008 Zenodo release."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

import package_final_integrated_release as package
import publish_final_integrated_zenodo as publish


ROOT = Path(__file__).resolve().parents[1]
CONCEPT_ID = publish.EXPECTED_CONCEPTRECID
VERSION = publish.VERSION
TITLE = publish.TITLE
PUBLICATION_DATE = publish.PUBLICATION_DATE
PDF_NAME = package.PDF_NAME
ZIP_NAME = package.ZIP_NAME
SUMS_NAME = package.SUMS_NAME
FILES = {
    PDF_NAME: ROOT / "output" / "pdf" / PDF_NAME,
    ZIP_NAME: package.OUTPUT_DIR / ZIP_NAME,
    SUMS_NAME: package.OUTPUT_DIR / SUMS_NAME,
}
RECEIPT = ROOT / "provenance" / "ZENODO_PUBLICATION_RECEIPT_FINAL_INTEGRATED.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def license_id(metadata: dict[str, object]) -> str:
    value = metadata.get("license", "")
    if isinstance(value, dict):
        return str(value.get("id", ""))
    return str(value)


def local_release() -> tuple[dict[str, object], list[dict[str, object]]]:
    if not all(path.is_file() for path in FILES.values()):
        raise SystemExit("one or more local final-integrated release files are missing")
    archive_metadata, _, _ = package.read_release_archive(FILES[ZIP_NAME])
    commit = str(archive_metadata.get("git_commit", ""))
    receipts, validated_metadata = publish.validate_payload(
        FILES[PDF_NAME], FILES[ZIP_NAME], FILES[SUMS_NAME], commit
    )
    if validated_metadata != archive_metadata:
        raise SystemExit("local release metadata replay differs")
    return archive_metadata, receipts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--doi", required=True)
    args = parser.parse_args()
    if not args.record_id.isdigit():
        raise SystemExit("record ID must be numeric")
    expected_doi = f"10.5281/zenodo.{args.record_id}"
    if args.doi != expected_doi:
        raise SystemExit("record ID and DOI differ")

    release_metadata, _ = local_release()
    github_commit = str(release_metadata["git_commit"])
    github_tree = str(release_metadata["git_tree"])

    session = requests.Session()
    session.trust_env = False
    response = session.get(f"https://zenodo.org/api/records/{args.record_id}", timeout=30)
    if response.status_code != 200:
        raise SystemExit(f"anonymous Zenodo metadata returned {response.status_code}")
    record = response.json()
    metadata = record.get("metadata", {})
    description = str(metadata.get("description", ""))
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
    resource_type = metadata.get("resource_type", {})
    if (
        record.get("status") != "published"
        or str(record.get("id")) != args.record_id
        or str(record.get("conceptrecid")) != CONCEPT_ID
        or metadata.get("version") != VERSION
        or metadata.get("doi") != args.doi
        or license_id(metadata) != "cc-by-sa-4.0"
        or metadata.get("title") != TITLE
        or metadata.get("publication_date") != PUBLICATION_DATE
        or metadata.get("language") != "ind"
        or metadata.get("access_right") != "open"
        or not isinstance(resource_type, dict)
        or resource_type.get("type") != "publication"
        or resource_type.get("subtype") != "book"
        or creators != publish.EXPECTED_CREATORS
        or contributors != publish.EXPECTED_CONTRIBUTORS
        or set(metadata.get("keywords", [])) != publish.EXPECTED_KEYWORDS
        or related != publish.EXPECTED_RELATED
        or github_commit not in description
        or not all(marker in description for marker in publish.DESCRIPTION_MARKERS)
    ):
        raise SystemExit("public Zenodo metadata identity differs")

    latest_response = session.get(
        f"https://zenodo.org/api/records/{args.record_id}/versions/latest", timeout=30
    )
    if latest_response.status_code != 200:
        raise SystemExit("anonymous latest-version readback failed")
    latest = latest_response.json()
    if (
        str(latest.get("id")) != args.record_id
        or str(latest.get("conceptrecid")) != CONCEPT_ID
        or latest.get("metadata", {}).get("version") != VERSION
    ):
        raise SystemExit("final integrated release is not the latest O008 version")

    versions_response = session.get(
        f"https://zenodo.org/api/records/{args.record_id}/versions", timeout=30
    )
    if versions_response.status_code != 200:
        raise SystemExit("anonymous version-lineage readback failed")
    versions = versions_response.json().get("hits", {}).get("hits", [])
    matching = [item for item in versions if item.get("metadata", {}).get("version") == VERSION]
    if len(matching) != 1 or str(matching[0].get("id")) != args.record_id:
        raise SystemExit("O008 lineage does not contain one exact final-integrated version")

    files_response = session.get(
        f"https://zenodo.org/api/records/{args.record_id}/files", timeout=30
    )
    if files_response.status_code != 200:
        raise SystemExit("anonymous public-file metadata readback failed")
    files_payload = files_response.json()
    file_items = files_payload.get("entries", [])
    public_pdf_names = [
        str(item.get("key", ""))
        for item in file_items
        if str(item.get("mimetype", "")) == "application/pdf"
        or str(item.get("key", "")).lower().endswith(".pdf")
    ]
    if public_pdf_names != [PDF_NAME]:
        raise SystemExit("public Zenodo payload lacks one exact primary PDF reader")
    default_preview = files_payload.get("default_preview")
    file_order = files_payload.get("order") or []
    if default_preview not in (None, PDF_NAME):
        raise SystemExit("Zenodo default preview points away from the PDF reader")
    if file_order and file_order[0] != PDF_NAME:
        raise SystemExit("Zenodo explicit file order points away from the PDF reader")
    public_files = {str(item.get("key", "")): item for item in file_items}
    if len(file_items) != len(public_files) or set(public_files) != set(FILES):
        raise SystemExit("public Zenodo file inventory differs")

    receipts: list[dict[str, object]] = []
    for name, local_path in FILES.items():
        local = local_path.read_bytes()
        item = public_files[name]
        if (
            item.get("status") != "completed"
            or item.get("access", {}).get("hidden") is not False
            or int(item.get("size", -1)) != len(local)
            or str(item.get("checksum", ""))
            != f"md5:{hashlib.md5(local).hexdigest()}"
        ):
            raise SystemExit(f"public Zenodo file metadata differs for {name}")
        file_response = session.get(item["links"]["content"], timeout=180)
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

    record_page = session.get(f"https://zenodo.org/records/{args.record_id}", timeout=30)
    if record_page.status_code != 200:
        raise SystemExit("anonymous Zenodo record page did not resolve")
    doi_response = session.get(f"https://doi.org/{args.doi}", timeout=30)
    if doi_response.status_code != 200 or "zenodo.org" not in doi_response.url:
        raise SystemExit("version DOI did not resolve anonymously to Zenodo")

    result = {
        "schema_version": "1.0.0",
        "receipt_id": "FAOA-2015-FINAL-INTEGRATED-ZENODO-PUBLICATION",
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
        "overall_status": "complete",
        "source_text_status": "complete",
        "semantic_html_status": "complete",
        "mastery_solution_status": "complete",
        "selected_reader_work_status": "complete",
        "compact_spectral_svd_bridge_status": "complete",
        "companion_html_status": "complete",
        "github_commit": github_commit,
        "github_tree": github_tree,
        "primary_reader_pages": 298,
        "source_exercise_solutions": 52,
        "selected_reader_work_solutions": 10,
        "compact_spectral_svd_bridge_units": 13,
        "source_author_credit_present": True,
        "scope_nonendorsement_component_model_metadata_present": True,
        "required_related_identifiers_present": True,
        "reader_first_surface": {
            "sole_primary_reader_pdf": PDF_NAME,
            "description_introduces_pdf_before_archive": True,
            "api_file_array_treated_as_unordered": True,
            "default_preview": default_preview,
            "explicit_file_order": file_order,
        },
        "status": "published",
        "latest_in_concept": True,
        "unique_version_in_lineage": True,
        "record_page_resolves": True,
        "doi_resolves": True,
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
