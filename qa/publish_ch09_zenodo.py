#!/usr/bin/env python3
"""Publish the admitted Chapter 9 checkpoint as a new Zenodo version."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import requests


BASE = "https://zenodo.org"
LATEST_DEPOSITION_ID = "22059740"
VERSION = "2026.08.22-ch09"
TITLE = "Analisis Fungsional dan Aljabar Operator: Suatu Pengantar — Edisi Bahasa Indonesia"
PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf"
ZIP_NAME = "functional-analysis-erdman-id-2026.08.22-ch09-source-backend.zip"
SUMS_NAME = "SHA256SUMS.txt"


def digest(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "filename": path.name,
        "bytes": len(data),
        "md5": hashlib.md5(data).hexdigest(),  # Zenodo exposes MD5 checksums.
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def token_candidates(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8-sig")
    candidates: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip().strip("`\"'")
        if ":" in stripped or "=" in stripped:
            value = re.split(r"[:=]", stripped, maxsplit=1)[1].strip().strip("`\"'")
            if re.fullmatch(r"[A-Za-z0-9._~-]{32,}", value):
                candidates.append(value)
    candidates.extend(re.findall(r"(?<![A-Za-z0-9._~-])([A-Za-z0-9._~-]{40,})(?![A-Za-z0-9._~-])", raw))
    seen: set[str] = set()
    return [x for x in candidates if not (x in seen or seen.add(x))]


def authenticated_session(token_file: Path) -> requests.Session:
    candidates = token_candidates(token_file)
    if not candidates:
        raise RuntimeError("no plausible Zenodo token found")
    for candidate in candidates:
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {candidate}"})
        response = session.get(
            f"{BASE}/api/deposit/depositions/{LATEST_DEPOSITION_ID}", timeout=30
        )
        if response.status_code == 200:
            return session
        session.close()
    raise RuntimeError("Zenodo credentials did not authorize the existing deposition")


def checked(response: requests.Response, expected: set[int]) -> requests.Response:
    if response.status_code not in expected:
        text = response.text[:800].replace("\n", " ")
        raise RuntimeError(
            f"Zenodo {response.request.method} {response.url} returned "
            f"{response.status_code}: {text}"
        )
    return response


def description() -> str:
    return (
        "<p><strong>Status: edisi dalam pengerjaan, Bab 1–9 dari 17 bab.</strong> "
        "Versi ini menambahkan Bab 9, <em>Ruang Vektor Topologis</em>, kepada "
        "reader Bahasa Indonesia yang telah diverifikasi. Bab 10–17, reader HTML "
        "semantik/aksesibel, lapisan solusi O001, dan jembatan spektral-kompak/SVD "
        "masih dalam pengerjaan.</p>"
        "<p>Adaptasi dari John M. Erdman, <em>Functional Analysis and Operator "
        "Algebras: An Introduction</em>, versi 4 Oktober 2015. Karya sumber dan "
        "adaptasi ini berlisensi CC BY-SA 4.0. Perubahan mencakup terjemahan "
        "Bahasa Indonesia, build modern, navigasi, indeks, backend modular, dan "
        "koreksi sumber yang dicatat secara transparan. Tidak ada dukungan atau "
        "persetujuan tersirat dari John M. Erdman maupun Portland State "
        "University.</p>"
        "<p>PDF 140 halaman bersifat searchable dan navigable, dengan seluruh "
        "halaman diperiksa secara visual dan semua font tertanam dengan pemetaan "
        "Unicode. PDF belum bertag; klaim aksesibilitas semantik tidak dibuat. "
        "Arsip sumber/backend mengikat commit publik GitHub "
        "<code>e3980f552a3e23c631223b3fd1802729568e101c</code> dan menyertakan "
        "manifest serta rekaman QA yang diperlukan untuk melanjutkan edisi.</p>"
        "<p>Mirror GitHub: "
        "<a href=\"https://github.com/KokunoYumeto/functional-analysis-erdman-id\">"
        "functional-analysis-erdman-id</a>.</p>"
    )


def writable_metadata(existing: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "access_right",
        "communities",
        "contributors",
        "creators",
        "description",
        "embargo_date",
        "grants",
        "imprint_isbn",
        "imprint_place",
        "imprint_publisher",
        "imprint_title",
        "keywords",
        "language",
        "license",
        "notes",
        "publication_date",
        "publication_type",
        "related_identifiers",
        "subjects",
        "title",
        "upload_type",
        "version",
    }
    metadata = {key: value for key, value in existing.items() if key in allowed}
    metadata.update(
        {
            "title": TITLE,
            "description": description(),
            "publication_date": "2026-08-22",
            "version": VERSION,
            "language": "ind",
            "access_right": "open",
            "license": "cc-by-sa-4.0",
            "upload_type": "publication",
            "publication_type": "book",
        }
    )
    related = [
        {
            "identifier": "https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_pdf.pdf",
            "relation": "isDerivedFrom",
            "resource_type": "publication-book",
        },
        {
            "identifier": "https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_web.zip",
            "relation": "isDerivedFrom",
            "resource_type": "software",
        },
        {
            "identifier": "https://github.com/KokunoYumeto/functional-analysis-erdman-id",
            "relation": "isSupplementedBy",
            "resource_type": "software",
        },
    ]
    metadata["related_identifiers"] = related
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--zip", dest="zip_path", type=Path, required=True)
    parser.add_argument("--sums", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = [args.pdf.resolve(), args.zip_path.resolve(), args.sums.resolve()]
    expected_names = [PDF_NAME, ZIP_NAME, SUMS_NAME]
    if [path.name for path in files] != expected_names or not all(path.is_file() for path in files):
        raise SystemExit("release payload filenames or paths are incorrect")
    file_receipts = [digest(path) for path in files]

    session = authenticated_session(args.token_file.resolve())
    original = checked(
        session.get(f"{BASE}/api/deposit/depositions/{LATEST_DEPOSITION_ID}", timeout=30),
        {200},
    ).json()
    if args.dry_run:
        print(
            json.dumps(
                {
                    "result": "authorized_probe_pass",
                    "deposition_id": original["id"],
                    "state": original["state"],
                    "submitted": original["submitted"],
                    "metadata_keys": sorted(original["metadata"]),
                    "has_newversion_link": "newversion" in original["links"],
                    "has_latest_draft_link": "latest_draft" in original["links"],
                    "payload": file_receipts,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    if original["state"] != "done" or not original["submitted"]:
        raise RuntimeError("latest published deposition is not in the expected done state")
    response = checked(
        session.post(original["links"]["newversion"], timeout=60), {201, 202}
    )
    newversion_response = response.json()
    draft_url = newversion_response["links"]["latest_draft"]
    draft = checked(session.get(draft_url, timeout=30), {200}).json()

    for inherited in list(draft.get("files", [])):
        checked(session.delete(inherited["links"]["self"], timeout=60), {204})

    bucket = draft["links"]["bucket"].rstrip("/")
    for path in files:
        with path.open("rb") as stream:
            checked(
                session.put(
                    f"{bucket}/{path.name}",
                    data=stream,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=300,
                ),
                {200, 201},
            )

    metadata = writable_metadata(draft["metadata"])
    draft = checked(
        session.put(draft_url, json={"metadata": metadata}, timeout=60), {200}
    ).json()
    published = checked(session.post(draft["links"]["publish"], timeout=120), {202}).json()

    result = {
        "result": "published",
        "record_id": str(published["record_id"]),
        "deposition_id": str(published["id"]),
        "conceptrecid": str(published["conceptrecid"]),
        "doi": published["doi"],
        "record_url": published["links"]["record_html"],
        "state": published["state"],
        "submitted": published["submitted"],
        "version": published["metadata"]["version"],
        "files": file_receipts,
        "credential_material_recorded": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
