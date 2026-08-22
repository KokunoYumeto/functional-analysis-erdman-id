#!/usr/bin/env python3
"""Update the existing O008 Figshare metadata/link item for Chapter 10."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import requests


BASE = "https://api.figshare.com/v2"
ARTICLE_ID = 33314709
EXPECTED_CURRENT_VERSION = 3
EXPECTED_NEW_VERSION = 4
PROJECT_ID = 280296
COLLECTION_ID = 8668413
PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf"
ZIP_NAME = "functional-analysis-erdman-id-2026.08.22-ch10-source-backend.zip"
SUMS_NAME = "SHA256SUMS.txt"


def digest(path: Path, expected_name: str) -> dict[str, Any]:
    resolved = path.resolve()
    if resolved.name != expected_name or not resolved.is_file():
        raise SystemExit(f"missing or incorrectly named release file: {expected_name}")
    data = resolved.read_bytes()
    return {
        "filename": resolved.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def token_candidates(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8-sig")
    candidates: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip().strip(chr(96) + "\"'")
        if ":" in stripped or "=" in stripped:
            value = (
                re.split(r"[:=]", stripped, maxsplit=1)[1]
                .strip()
                .strip(chr(96) + "\"'")
            )
            if re.fullmatch(r"[A-Za-z0-9._~-]{32,}", value):
                candidates.append(value)
    candidates.extend(
        re.findall(
            r"(?<![A-Za-z0-9._~-])([A-Za-z0-9._~-]{40,})(?![A-Za-z0-9._~-])",
            raw,
        )
    )
    seen: set[str] = set()
    return [x for x in candidates if not (x in seen or seen.add(x))]


def authenticated_session(token_file: Path) -> requests.Session:
    candidates = token_candidates(token_file)
    if not candidates:
        raise RuntimeError("no plausible Figshare token found")
    for candidate in candidates:
        for scheme in ("token", "Bearer"):
            session = requests.Session()
            session.headers.update({"Authorization": f"{scheme} {candidate}"})
            response = session.get(f"{BASE}/account/articles/{ARTICLE_ID}", timeout=30)
            if response.status_code == 200:
                return session
            session.close()
    raise RuntimeError("Figshare credentials did not authorize the existing article")


def checked(response: requests.Response, expected: set[int]) -> requests.Response:
    if response.status_code not in expected:
        text = response.text[:800].replace("\n", " ")
        raise RuntimeError(
            f"Figshare {response.request.method} {response.url} returned "
            f"{response.status_code}: {text}"
        )
    return response


def description(
    zenodo_doi: str,
    pdf_url: str,
    zip_url: str,
    sums_url: str,
    files: dict[str, dict[str, Any]],
) -> str:
    pdf = files[PDF_NAME]
    archive = files[ZIP_NAME]
    sums = files[SUMS_NAME]
    return (
        "<p><strong>Status: edisi dalam pengerjaan, Bab 1–10 dari 17 bab.</strong> "
        "Checkpoint ini menambahkan Bab 10, <em>Distribusi</em>. Bab 11–17, "
        "HTML semantik/aksesibel, lapisan solusi O001, dan jembatan "
        "spektral-kompak/SVD masih dalam pengerjaan.</p>"
        "<p><strong>Batas lisensi:</strong> CC0 pada Figshare berlaku hanya untuk "
        "metadata dan penunjuk tautan ini. PDF, sumber, backend, dan seluruh "
        "berkas substantif di Zenodo tetap berlisensi "
        "<a href=\"https://creativecommons.org/licenses/by-sa/4.0/\">CC BY-SA "
        "4.0</a>; tidak ada berkas substantif yang diunggah ulang ke Figshare "
        "dengan lisensi pengganti.</p>"
        "<p>Sumber: John M. Erdman, <em>Functional Analysis and Operator "
        "Algebras: An Introduction</em>, versi 4 Oktober 2015. Perubahan mencakup "
        "terjemahan Bahasa Indonesia, build modern, navigasi, indeks, backend "
        "modular, dan koreksi sumber yang dicatat. Tidak ada dukungan atau "
        "persetujuan tersirat dari Erdman maupun Portland State University.</p>"
        "<p>Terjemahan dan penyuntingan teknis dibantu oleh "
        "<strong>OpenAI Codex gpt-5.6-sol, Ultra</strong>, atas arahan pengguna "
        "manusia. Kredit penulis sumber dan kontributor komponen tetap "
        "dipertahankan.</p>"
        f"<p><strong>Reader utama:</strong> <a href=\"{pdf_url}\">{PDF_NAME}</a> "
        f"({pdf['bytes']:,} byte; SHA-256 "
        f"<code>{pdf['sha256']}</code>). PDF 153 halaman ini searchable dan "
        "navigable, seluruh halamannya telah diperiksa secara visual, tetapi "
        "PDF belum bertag.</p>"
        f"<p><strong>Sumber/backend:</strong> <a href=\"{zip_url}\">{ZIP_NAME}</a> "
        f"({archive['bytes']:,} byte; SHA-256 "
        f"<code>{archive['sha256']}</code>). "
        f"<a href=\"{sums_url}\">{SUMS_NAME}</a> "
        f"({sums['bytes']:,} byte; SHA-256 "
        f"<code>{sums['sha256']}</code>).</p>"
        f"<p>Zenodo: <a href=\"https://doi.org/{zenodo_doi}\">{zenodo_doi}</a>. "
        "GitHub: "
        "<a href=\"https://github.com/KokunoYumeto/functional-analysis-erdman-id\">"
        "functional-analysis-erdman-id</a>.</p>"
    )


def article_ids(items: list[dict[str, Any]]) -> set[int]:
    return {int(item["id"]) for item in items}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--zenodo-record-id", required=True)
    parser.add_argument("--zenodo-doi", required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--zip", dest="zip_path", type=Path, required=True)
    parser.add_argument("--sums", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    zenodo_record_id = args.zenodo_record_id.strip()
    if not re.fullmatch(r"[0-9]+", zenodo_record_id):
        raise SystemExit("--zenodo-record-id must contain digits only")
    zenodo_doi = args.zenodo_doi.strip().removeprefix("https://doi.org/")
    if zenodo_doi != f"10.5281/zenodo.{zenodo_record_id}":
        raise SystemExit("--zenodo-doi does not match --zenodo-record-id")

    release_files = {
        item["filename"]: item
        for item in (
            digest(args.pdf, PDF_NAME),
            digest(args.zip_path, ZIP_NAME),
            digest(args.sums, SUMS_NAME),
        )
    }
    referenced_payload_bytes = sum(item["bytes"] for item in release_files.values())
    if referenced_payload_bytes > 500_000_000:
        raise RuntimeError("referenced task payload exceeds the 500,000,000-byte cap")

    record_url = f"https://zenodo.org/records/{zenodo_record_id}"
    pdf_url = f"{record_url}/files/{PDF_NAME}"
    zip_url = f"{record_url}/files/{ZIP_NAME}"
    sums_url = f"{record_url}/files/{SUMS_NAME}"

    session = authenticated_session(args.token_file.resolve())
    article_url = f"{BASE}/account/articles/{ARTICLE_ID}"
    article = checked(session.get(article_url, timeout=30), {200}).json()
    files = checked(session.get(f"{article_url}/files", timeout=30), {200}).json()
    collection_url = f"{BASE}/account/collections/{COLLECTION_ID}"
    private_collection_items = checked(
        session.get(
            f"{collection_url}/articles", params={"page_size": 1000}, timeout=30
        ),
        {200},
    ).json()
    public_collection_items = checked(
        session.get(
            f"{BASE}/collections/{COLLECTION_ID}/articles",
            params={"page_size": 1000},
            timeout=30,
        ),
        {200},
    ).json()
    project_items = checked(
        session.get(
            f"{BASE}/account/projects/{PROJECT_ID}/articles",
            params={"page_size": 1000},
            timeout=30,
        ),
        {200},
    ).json()

    if args.dry_run:
        print(
            json.dumps(
                {
                    "result": "authorized_probe_pass",
                    "article": {
                        "id": article["id"],
                        "title": article["title"],
                        "version": article.get("version"),
                        "status": article.get("status"),
                        "license": article.get("license"),
                        "files": [
                            {
                                "id": item["id"],
                                "name": item["name"],
                                "is_link_only": item.get("is_link_only"),
                                "download_url": item.get("download_url"),
                            }
                            for item in files
                        ],
                    },
                    "zenodo_record_id": zenodo_record_id,
                    "zenodo_doi": zenodo_doi,
                    "release_files": release_files,
                    "referenced_payload_bytes": referenced_payload_bytes,
                    "collection_private_count": len(private_collection_items),
                    "collection_private_contains_article": ARTICLE_ID
                    in article_ids(private_collection_items),
                    "collection_public_count": len(public_collection_items),
                    "collection_public_contains_article": ARTICLE_ID
                    in article_ids(public_collection_items),
                    "project_article_count": len(project_items),
                    "project_contains_article": ARTICLE_ID in article_ids(project_items),
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return

    if article.get("version") != EXPECTED_CURRENT_VERSION:
        raise RuntimeError(
            f"unexpected current Figshare version: {article.get('version')}"
        )
    if ARTICLE_ID not in article_ids(project_items):
        raise RuntimeError("existing O008 article is no longer in the required project")
    if article.get("license", {}).get("value") != 2:
        raise RuntimeError("existing Figshare item is not using CC0 for metadata/pointers")

    payload = {
        "title": (
            "Analisis Fungsional dan Aljabar Operator: Suatu Pengantar — "
            "Edisi Bahasa Indonesia (Bab 1–10 dari 17)"
        ),
        "description": description(
            zenodo_doi, pdf_url, zip_url, sums_url, release_files
        ),
        "keywords": [
            "Bahasa Indonesia",
            "functional analysis",
            "operator algebras",
            "topological vector spaces",
            "distributions",
            "open textbook",
            "CC BY-SA 4.0",
            "partial edition",
            "O008",
            "D20",
            "reader",
        ],
        "references": [
            f"https://doi.org/{zenodo_doi}",
            record_url,
            "https://web.pdx.edu/~erdman/",
            f"https://zenodo.org/api/records/{zenodo_record_id}/files/{PDF_NAME}/content",
            f"https://zenodo.org/api/records/{zenodo_record_id}/files/{ZIP_NAME}/content",
            f"https://zenodo.org/api/records/{zenodo_record_id}/files/{SUMS_NAME}/content",
            "https://github.com/KokunoYumeto/functional-analysis-erdman-id",
        ],
        "license": 2,
    }
    checked(session.put(article_url, json=payload, timeout=60), {205})

    for item in files:
        checked(session.delete(f"{article_url}/files/{item['id']}", timeout=60), {204})
    linked = checked(
        session.post(f"{article_url}/files", json={"link": pdf_url}, timeout=60),
        {201},
    )
    linked_location = linked.headers.get("Location")
    if not linked_location:
        raise RuntimeError("Figshare did not return the linked-file location")
    linked_file = checked(session.get(linked_location, timeout=30), {200}).json()
    if not linked_file.get("is_link_only") or linked_file.get("download_url") != pdf_url:
        raise RuntimeError("Figshare linked-file readback mismatch before publish")

    checked(session.post(f"{article_url}/publish", timeout=120), {201})
    public_article = checked(
        session.get(f"{BASE}/articles/{ARTICLE_ID}", timeout=30), {200}
    ).json()
    if public_article.get("version") != EXPECTED_NEW_VERSION:
        raise RuntimeError(
            f"unexpected public article version: {public_article.get('version')}"
        )

    private_ids = article_ids(private_collection_items)
    if ARTICLE_ID not in private_ids:
        checked(
            session.post(
                f"{collection_url}/articles",
                json={"articles": [ARTICLE_ID]},
                timeout=60,
            ),
            {201},
        )
    checked(session.post(f"{collection_url}/publish", timeout=120), {201})
    collection = checked(
        session.get(f"{BASE}/collections/{COLLECTION_ID}", timeout=30), {200}
    ).json()
    public_after = checked(
        session.get(
            f"{BASE}/collections/{COLLECTION_ID}/articles",
            params={"page_size": 1000},
            timeout=30,
        ),
        {200},
    ).json()
    public_before_ids = article_ids(public_collection_items)
    public_after_ids = article_ids(public_after)
    if not public_before_ids.issubset(public_after_ids) or ARTICLE_ID not in public_after_ids:
        raise RuntimeError("collection update was not additive")

    result = {
        "result": "published",
        "article": {
            "id": ARTICLE_ID,
            "version": public_article["version"],
            "doi": public_article["doi"],
            "url": public_article["url_private_api"].replace(
                "api.figshare.com/v2/account/articles",
                "figshare.com/articles/online_resource",
            )
            if public_article.get("url_private_api")
            else f"https://figshare.com/articles/online_resource/{ARTICLE_ID}",
            "file_id": linked_file["id"],
            "file_name": linked_file["name"],
            "file_url": linked_file["download_url"],
            "license_value": public_article["license"]["value"],
            "license_name": public_article["license"]["name"],
        },
        "zenodo": {
            "record_id": zenodo_record_id,
            "doi": zenodo_doi,
            "release_files": release_files,
            "referenced_payload_bytes": referenced_payload_bytes,
        },
        "project": {
            "id": PROJECT_ID,
            "contains_article": True,
            "article_count": len(project_items),
        },
        "collection": {
            "id": COLLECTION_ID,
            "version": collection.get("version"),
            "doi": collection.get("doi"),
            "before_public_count": len(public_collection_items),
            "after_public_count": len(public_after),
            "old_members_preserved": True,
            "contains_article": True,
        },
        "substantive_bytes_uploaded_to_figshare": False,
        "credential_material_recorded": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
