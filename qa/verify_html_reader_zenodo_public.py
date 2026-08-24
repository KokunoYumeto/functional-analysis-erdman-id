#!/usr/bin/env python3
"""Anonymously verify the public O008 semantic-HTML Zenodo checkpoint."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import requests


def load_package_contract():
    path = Path(__file__).with_name("package_html_reader_release.py")
    spec = importlib.util.spec_from_file_location("o008_html_package_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the HTML package contract")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKAGE = load_package_contract()


ROOT = Path(__file__).resolve().parents[1]
CONCEPT_ID = "22059739"
VERSION = "2026.08.24-html-reader"
TITLE = "Analisis Fungsional dan Aljabar Operator: Suatu Pengantar — Edisi Bahasa Indonesia"
PUBLICATION_DATE = "2026-08-24"
PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf"
ZIP_NAME = "functional-analysis-erdman-id-2026.08.24-html-reader-source-backend.zip"
SUMS_NAME = "SHA256SUMS.txt"
PREFIX = "functional-analysis-erdman-id-2026.08.24-html-reader"
EXPECTED_PDF_SHA256 = (
    "efa2358b3c3e6e8c47e0caee9a02f6afe78d15bea1b0f1822ea8449d801b2b10"
)
FORBIDDEN_COMPONENTS = {"TABLE.TEX", "by-sa.eps", "by-sa.pdf", "Wiener_quote.tex"}
FORBIDDEN_COMPONENTS_LOWER = {name.lower() for name in FORBIDDEN_COMPONENTS}
DESCRIPTION_MARKERS = (
    "Status keseluruhan: edisi masih dalam pengerjaan",
    "terjemahan teks sumber dan reader HTML semantik telah lengkap",
    "CC BY-SA 4.0",
    "Tidak ada dukungan atau persetujuan tersirat",
    "OpenAI Codex gpt-5.6-sol, Ultra",
    "PDF 238 halaman",
    "tetap belum bertag",
    "22 rute",
    "80 diagram SVG",
)
RELATED_IDENTIFIERS = {
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
FILES = {
    PDF_NAME: ROOT / "output" / "pdf" / PDF_NAME,
    ZIP_NAME: ROOT / "qa" / "release-html-reader" / ZIP_NAME,
    SUMS_NAME: ROOT / "qa" / "release-html-reader" / SUMS_NAME,
}
RECEIPT = ROOT / "provenance" / "ZENODO_PUBLICATION_RECEIPT_HTML_READER.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def license_id(metadata: dict[str, object]) -> str:
    value = metadata.get("license", "")
    if isinstance(value, dict):
        return str(value.get("id", ""))
    return str(value)


def local_release_metadata() -> dict[str, object]:
    zip_path = FILES[ZIP_NAME]
    with zipfile.ZipFile(zip_path, "r") as archive:
        if archive.testzip() is not None:
            raise SystemExit("local release ZIP failed integrity replay")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise SystemExit("local release ZIP contains duplicate entry names")
        metadata_name = f"{PREFIX}/RELEASE_METADATA.json"
        manifest_name = f"{PREFIX}/RELEASE_MANIFEST.csv"
        if metadata_name not in archive.namelist() or manifest_name not in archive.namelist():
            raise SystemExit("local release ZIP lacks its exact metadata/manifest pair")
        metadata = json.loads(archive.read(metadata_name))
        rows = list(
            csv.DictReader(
                io.StringIO(archive.read(manifest_name).decode("utf-8-sig"))
            )
        )
        paths: set[str] = set()
        payload: dict[str, bytes] = {}
        private_markers = (
            b"C:/Users/",
            b"c:/users/",
            b"C:\\Users\\",
            b"c:\\users\\",
            b"C:\\\\Users\\\\",
            b"c:\\\\users\\\\",
            b"file:///C:/Users/",
            b"/home/",
        )
        for row in rows:
            path = row.get("path", "")
            if path in paths or path.startswith("/") or ".." in PurePosixPath(path).parts:
                raise SystemExit("local release manifest has a duplicate or unsafe path")
            data = archive.read(f"{PREFIX}/{path}")
            if int(row["bytes"]) != len(data) or row["sha256"] != sha256(data):
                raise SystemExit(f"local release manifest identity differs: {path}")
            if PurePosixPath(path.lower()).name in FORBIDDEN_COMPONENTS_LOWER:
                raise SystemExit(f"forbidden component entered local release: {path}")
            if any(marker in data for marker in private_markers):
                raise SystemExit(f"private absolute path entered local release: {path}")
            paths.add(path)
            payload[path] = data
        expected_names = {
            f"{PREFIX}/{path}" for path in paths
        } | {metadata_name, manifest_name}
        if set(archive.namelist()) != expected_names:
            raise SystemExit("local ZIP inventory differs from its release manifest")
        try:
            backend_paths, backend_rows = PACKAGE.backend_inventory(
                payload[PACKAGE.BACKEND_MANIFEST_PATH]
            )
            PACKAGE.verify_backend_manifest(payload, backend_rows)
            PACKAGE.verify_site_manifest(payload)
        except (KeyError, SystemExit) as exc:
            raise SystemExit(f"local packaged manifest replay failed: {exc}") from exc
        html_manifest_rows = list(
            csv.DictReader(
                io.StringIO(payload["output/html/MANIFEST.csv"].decode("utf-8-sig"))
            )
        )
        html_paths = {"output/html/MANIFEST.csv"} | {
            f"output/html/{row['path']}" for row in html_manifest_rows
        }
        canonical_payload = set(PACKAGE.REQUIRED_EXACT) | backend_paths | html_paths
        if set(payload) != canonical_payload:
            raise SystemExit("local ZIP payload differs from the canonical package inventory")
        if any(PACKAGE.unsafe(path) for path in payload):
            raise SystemExit("local ZIP contains a forbidden or transient path")
    commit = str(metadata.get("git_commit", ""))
    tree = str(metadata.get("git_tree", ""))
    if (
        metadata.get("schema_version") != "o008.release-html-reader.v1"
        or metadata.get("release") != VERSION
        or metadata.get("overall_status") != "in_progress"
        or metadata.get("source_text_status") != "complete"
        or metadata.get("semantic_html_status") != "complete"
        or not re.fullmatch(r"[0-9a-f]{40}", commit)
        or not re.fullmatch(r"[0-9a-f]{40}", tree)
    ):
        raise SystemExit("local release metadata identity differs")
    pdf_data = FILES[PDF_NAME].read_bytes()
    if sha256(pdf_data) != EXPECTED_PDF_SHA256:
        raise SystemExit("local PDF is not the admitted unchanged complete-source reader")
    expected_sums = {
        PDF_NAME: sha256(pdf_data),
        ZIP_NAME: sha256(FILES[ZIP_NAME].read_bytes()),
    }
    parsed_sums: dict[str, str] = {}
    for line in FILES[SUMS_NAME].read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match or match.group(2) in parsed_sums:
            raise SystemExit("local SHA256SUMS.txt is malformed or duplicated")
        parsed_sums[match.group(2)] = match.group(1)
    if parsed_sums != expected_sums:
        raise SystemExit("local SHA256SUMS.txt does not bind exactly the PDF and ZIP")
    if len(pdf_data) + FILES[ZIP_NAME].stat().st_size > PACKAGE.MAX_RELEASE_BYTES:
        raise SystemExit("local release exceeds the 500,000,000-byte cap")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--doi", required=True)
    args = parser.parse_args()
    if not args.record_id.isdigit():
        raise SystemExit("record ID must be numeric")
    expected_doi = f"10.5281/zenodo.{args.record_id}"
    if args.doi != expected_doi:
        raise SystemExit("record ID and DOI differ")
    if not all(path.is_file() for path in FILES.values()):
        raise SystemExit("one or more local release files are missing")
    release_metadata = local_release_metadata()
    github_commit = str(release_metadata["git_commit"])

    session = requests.Session()
    session.trust_env = False
    response = session.get(f"https://zenodo.org/api/records/{args.record_id}", timeout=30)
    if response.status_code != 200:
        raise SystemExit(f"anonymous Zenodo metadata returned {response.status_code}")
    record = response.json()
    metadata = record.get("metadata", {})
    description = str(metadata.get("description", ""))
    creators = metadata.get("creators", [])
    contributors = metadata.get("contributors", [])
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
        or {
            str(item.get("name", ""))
            for item in creators
            if isinstance(item, dict)
        }
        != {"Erdman, John M."}
        or {
            (str(item.get("name", "")), str(item.get("type", "")))
            for item in contributors
            if isinstance(item, dict)
        }
        != {("Codex", "Other")}
        or set(metadata.get("keywords", [])) != EXPECTED_KEYWORDS
        or not all(marker in description for marker in DESCRIPTION_MARKERS)
        or github_commit not in description
        or related != RELATED_IDENTIFIERS
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
        raise SystemExit("published HTML checkpoint is not the latest O008 version")

    versions_response = session.get(
        f"https://zenodo.org/api/records/{args.record_id}/versions", timeout=30
    )
    if versions_response.status_code != 200:
        raise SystemExit("anonymous version-lineage readback failed")
    versions = versions_response.json().get("hits", {}).get("hits", [])
    matching_versions = [
        item for item in versions if item.get("metadata", {}).get("version") == VERSION
    ]
    if len(matching_versions) != 1 or str(matching_versions[0].get("id")) != args.record_id:
        raise SystemExit("O008 lineage does not contain one exact HTML-reader version")

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
    public_files = {item["key"]: item for item in file_items}
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
            or str(item.get("checksum", "")) != f"md5:{hashlib.md5(local).hexdigest()}"
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
        "receipt_id": "FAOA-2015-HTML-READER-ZENODO-PUBLICATION",
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
        "overall_status": "in_progress",
        "source_text_status": "complete",
        "semantic_html_status": "complete",
        "github_commit": github_commit,
        "github_tree": release_metadata["git_tree"],
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
