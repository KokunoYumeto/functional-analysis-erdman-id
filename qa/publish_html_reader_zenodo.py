#!/usr/bin/env python3
"""Publish the admitted O008 semantic-HTML checkpoint in its Zenodo concept."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import requests


def load_package_contract() -> Any:
    path = Path(__file__).with_name("package_html_reader_release.py")
    spec = importlib.util.spec_from_file_location("o008_html_package_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the HTML package contract")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKAGE = load_package_contract()


BASE = "https://zenodo.org"
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONCEPTRECID = "22059739"
EXPECTED_PREVIOUS_RECORD_ID = "22082688"
EXPECTED_PREVIOUS_VERSION = "2026.08.24-source-text"
VERSION = "2026.08.24-html-reader"
TITLE = "Analisis Fungsional dan Aljabar Operator: Suatu Pengantar — Edisi Bahasa Indonesia"
PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf"
ZIP_NAME = "functional-analysis-erdman-id-2026.08.24-html-reader-source-backend.zip"
SUMS_NAME = "SHA256SUMS.txt"
PREFIX = "functional-analysis-erdman-id-2026.08.24-html-reader"
EXPECTED_PDF_SHA256 = (
    "efa2358b3c3e6e8c47e0caee9a02f6afe78d15bea1b0f1822ea8449d801b2b10"
)
EXPECTED_SITE_TREE_SHA256 = (
    "f04bb3f5ee883c794474b191faf0e724987ebc01c4711bac8f6dc5421e543f32"
)
EXPECTED_SITE_MANIFEST_SHA256 = (
    "3a3a4a4cdd03d1cae2c49c316fc1f94fe36dad6aa9da79f3764930f011045576"
)
EXPECTED_BACKEND_MANIFEST_SHA256 = (
    "06ad5f9c6931ef1838a8307c60b8b3b94a4c89a25d6ddc12dbfb2a3ddc591cfc"
)
EXPECTED_ROUTE_MAP_SHA256 = (
    "36fb1838ae99ad850c8f4832c318d64d87f5aee1eb22415583f4ec8178a7c0f5"
)
FORBIDDEN_COMPONENTS = {"TABLE.TEX", "by-sa.eps", "by-sa.pdf", "Wiener_quote.tex"}
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "filename": path.name,
        "bytes": len(data),
        "md5": hashlib.md5(data).hexdigest(),  # Zenodo exposes MD5 checksums.
        "sha256": sha256(data),
    }


def validate_release_manifest(
    archive: zipfile.ZipFile, manifest_name: str
) -> dict[str, bytes]:
    names = [info.filename for info in archive.infolist()]
    if len(names) != len(set(names)):
        raise RuntimeError("ZIP contains duplicate entry names")
    rows = list(
        csv.DictReader(io.StringIO(archive.read(manifest_name).decode("utf-8-sig")))
    )
    if not rows or set(rows[0]) != {"path", "bytes", "sha256"}:
        raise RuntimeError("release manifest schema differs")
    payload: dict[str, bytes] = {}
    for row in rows:
        path = row["path"]
        if path in payload or path.startswith("/") or ".." in PurePosixPath(path).parts:
            raise RuntimeError("release manifest has a duplicate or unsafe path")
        data = archive.read(f"{PREFIX}/{path}")
        if int(row["bytes"]) != len(data) or row["sha256"] != sha256(data):
            raise RuntimeError(f"release manifest identity differs: {path}")
        payload[path] = data
    expected_names = {
        f"{PREFIX}/{path}" for path in payload
    } | {
        f"{PREFIX}/RELEASE_MANIFEST.csv",
        f"{PREFIX}/RELEASE_METADATA.json",
    }
    if set(names) != expected_names:
        raise RuntimeError("ZIP entry inventory differs from its release manifest")
    return payload


def validate_payload(
    pdf_path: Path, zip_path: Path, sums_path: Path, github_commit: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    receipts = [digest(path) for path in (pdf_path, zip_path, sums_path)]
    if receipts[0]["sha256"] != EXPECTED_PDF_SHA256:
        raise RuntimeError("PDF is not the admitted unchanged complete-source reader")
    expected_sums = {item["filename"]: item["sha256"] for item in receipts[:2]}
    parsed: dict[str, str] = {}
    for line in sums_path.read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match or match.group(2) in parsed:
            raise RuntimeError("SHA256SUMS.txt is malformed or duplicated")
        parsed[match.group(2)] = match.group(1)
    if parsed != expected_sums:
        raise RuntimeError("SHA256SUMS.txt does not bind exactly the PDF and ZIP")

    with zipfile.ZipFile(zip_path, "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError("source/backend ZIP failed integrity replay")
        metadata_name = f"{PREFIX}/RELEASE_METADATA.json"
        manifest_name = f"{PREFIX}/RELEASE_MANIFEST.csv"
        if metadata_name not in archive.namelist() or manifest_name not in archive.namelist():
            raise RuntimeError("source/backend ZIP lacks its exact metadata/manifest pair")
        release_metadata = json.loads(archive.read(metadata_name))
        payload = validate_release_manifest(archive, manifest_name)

    required_metadata = {
        "schema_version": "o008.release-html-reader.v1",
        "release": VERSION,
        "overall_status": "in_progress",
        "source_text_status": "complete",
        "semantic_html_status": "complete",
        "git_commit": github_commit,
        "license": "CC BY-SA 4.0",
        "primary_reader_uploaded_separately": PDF_NAME,
        "semantic_html_file_count": 105,
        "semantic_html_tree_sha256": EXPECTED_SITE_TREE_SHA256,
        "semantic_html_manifest_sha256": EXPECTED_SITE_MANIFEST_SHA256,
        "backend_manifest_sha256": EXPECTED_BACKEND_MANIFEST_SHA256,
        "html_route_map_sha256": EXPECTED_ROUTE_MAP_SHA256,
    }
    if any(release_metadata.get(key) != value for key, value in required_metadata.items()):
        raise RuntimeError("source/backend ZIP metadata differs from this release")
    if not re.fullmatch(r"[0-9a-f]{40}", str(release_metadata.get("git_tree", ""))):
        raise RuntimeError("source/backend ZIP has no exact Git tree identity")
    try:
        backend_paths, backend_rows = PACKAGE.backend_inventory(
            payload[PACKAGE.BACKEND_MANIFEST_PATH]
        )
        PACKAGE.verify_backend_manifest(payload, backend_rows)
        PACKAGE.verify_site_manifest(payload)
    except (KeyError, SystemExit) as exc:
        raise RuntimeError(f"packaged manifest replay failed: {exc}") from exc
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
        raise RuntimeError("ZIP payload differs from the canonical package inventory")
    if any(PACKAGE.unsafe(path) for path in payload):
        raise RuntimeError("ZIP contains a forbidden, secret-bearing, or transient path")
    if len(pdf_path.read_bytes()) + len(zip_path.read_bytes()) > PACKAGE.MAX_RELEASE_BYTES:
        raise RuntimeError("release payload exceeds the 500,000,000-byte cap")
    return receipts, release_metadata


def token_candidates(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8-sig")
    candidates: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip().strip(chr(96) + "\"'")
        if ":" in stripped or "=" in stripped:
            value = re.split(r"[:=]", stripped, maxsplit=1)[1].strip().strip(
                chr(96) + "\"'"
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
    return [value for value in candidates if not (value in seen or seen.add(value))]


def deposition_search(session: requests.Session) -> list[dict[str, Any]]:
    response = session.get(
        f"{BASE}/api/deposit/depositions",
        params={"q": f"conceptrecid:{EXPECTED_CONCEPTRECID}", "size": 100},
        timeout=30,
    )
    if response.status_code != 200:
        return []
    payload = response.json()
    return payload if isinstance(payload, list) else payload.get("hits", {}).get("hits", [])


def public_latest_preflight() -> dict[str, Any]:
    session = requests.Session()
    session.trust_env = False
    response = session.get(
        f"{BASE}/api/records/{EXPECTED_PREVIOUS_RECORD_ID}/versions/latest",
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"anonymous Zenodo latest-version preflight returned {response.status_code}"
        )
    latest = response.json()
    if (
        str(latest.get("id")) != EXPECTED_PREVIOUS_RECORD_ID
        or str(latest.get("conceptrecid")) != EXPECTED_CONCEPTRECID
        or latest.get("metadata", {}).get("version") != EXPECTED_PREVIOUS_VERSION
    ):
        raise RuntimeError("public O008 latest version changed; refusing a stale new-version fork")
    return latest


def authenticated_session(token_file: Path) -> requests.Session:
    candidates = token_candidates(token_file)
    if not candidates:
        raise RuntimeError("no plausible Zenodo token found")
    for candidate in candidates:
        session = requests.Session()
        session.trust_env = False
        session.headers.update({"Authorization": f"Bearer {candidate}"})
        if deposition_search(session):
            return session
        session.close()
    raise RuntimeError("Zenodo credentials did not authorize the existing deposition")


def checked(response: requests.Response, expected: set[int]) -> requests.Response:
    if response.status_code not in expected:
        detail = response.text[:800].replace("\n", " ")
        raise RuntimeError(
            f"Zenodo {response.request.method} {response.url} returned "
            f"{response.status_code}: {detail}"
        )
    return response


def description(github_commit: str) -> str:
    return (
        "<p><strong>Status keseluruhan: edisi masih dalam pengerjaan; "
        "terjemahan teks sumber dan reader HTML semantik telah lengkap.</strong> "
        "Checkpoint ini memuat prakata, seluruh 17 bab, bibliografi, indeks, "
        "serta reader HTML offline yang telah diterima. Lapisan penguasaan dan "
        "solusi O001 serta jembatan spektral-kompak/SVD berprovenans terpisah "
        "masih dalam pengerjaan.</p>"
        "<p>Adaptasi dari John M. Erdman, <em>Functional Analysis and Operator "
        "Algebras: An Introduction</em>, versi 4 Oktober 2015. Karya sumber dan "
        "adaptasi ini berlisensi CC BY-SA 4.0. Perubahan mencakup terjemahan "
        "Bahasa Indonesia, build modern, reader semantik, navigasi, indeks, "
        "backend modular, deskripsi aksesibel, penggantian sah atas dua tabel "
        "warisan, dan koreksi sumber yang dicatat transparan. Tidak ada dukungan "
        "atau persetujuan tersirat dari John M. Erdman maupun Portland State "
        "University.</p>"
        "<p>Terjemahan dan penyuntingan teknis dibantu oleh <strong>OpenAI Codex "
        "gpt-5.6-sol, Ultra</strong>, atas arahan pengguna manusia. Kredit penulis "
        "sumber dan kontributor komponen tetap dipertahankan.</p>"
        "<p>PDF 238 halaman dipertahankan byte-identik dari checkpoint teks "
        "sumber lengkap dan tetap belum bertag. Permukaan aksesibilitas tambahan "
        "adalah reader HTML statis/offline dengan 22 rute, MathML semantik, 80 "
        "diagram SVG berteks alternatif dan bertranskrip, serta reflow desktop "
        "dan seluler yang telah diperiksa. Arsip ringkas menyertakan reader HTML, "
        "sumber build, backend, lisensi, manifest, checksum, dan bukti QA; arsip "
        "itu mengikat commit publik GitHub "
        f"<code>{github_commit}</code>.</p>"
        "<p>Mirror GitHub dan unduhan reader HTML offline: "
        "<a href=\"https://github.com/KokunoYumeto/functional-analysis-erdman-id\">"
        "functional-analysis-erdman-id</a>.</p>"
    )


def writable_metadata(existing: dict[str, Any], github_commit: str) -> dict[str, Any]:
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
            "description": description(github_commit),
            "publication_date": "2026-08-24",
            "version": VERSION,
            "language": "ind",
            "access_right": "open",
            "license": "cc-by-sa-4.0",
            "upload_type": "publication",
            "publication_type": "book",
            "creators": [{"name": "Erdman, John M."}],
            "contributors": [{"name": "Codex", "type": "Other"}],
            "keywords": [
                "functional analysis",
                "operator algebras",
                "Bahasa Indonesia",
                "open textbook",
                "CC BY-SA 4.0",
                "Banach space",
                "Hilbert space",
                "spectral theory",
                "machine-readable curriculum",
            ],
        }
    )
    metadata["related_identifiers"] = [
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
    return metadata


def metadata_license_id(metadata: dict[str, Any]) -> str:
    value = metadata.get("license", "")
    if isinstance(value, dict):
        return str(value.get("id", ""))
    return str(value)


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
    description_text = str(metadata.get("description", ""))
    exact = {
        "title": TITLE,
        "publication_date": "2026-08-24",
        "version": VERSION,
        "language": "ind",
        "access_right": "open",
        "upload_type": "publication",
        "publication_type": "book",
    }
    if any(metadata.get(key) != value for key, value in exact.items()):
        raise RuntimeError("Zenodo draft metadata has an incorrect core field")
    if metadata_license_id(metadata) != "cc-by-sa-4.0":
        raise RuntimeError("Zenodo draft license is not CC BY-SA 4.0")
    if creators != EXPECTED_CREATORS or contributors != EXPECTED_CONTRIBUTORS:
        raise RuntimeError("Zenodo draft creator/contributor credit differs")
    if set(metadata.get("keywords", [])) != EXPECTED_KEYWORDS:
        raise RuntimeError("Zenodo draft keyword set differs")
    if related != EXPECTED_RELATED:
        raise RuntimeError("Zenodo draft related-identifier relations differ")
    if github_commit not in description_text or not all(
        marker in description_text for marker in DESCRIPTION_MARKERS
    ):
        raise RuntimeError("Zenodo draft description lacks a required status marker")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--zip", dest="zip_path", type=Path, required=True)
    parser.add_argument("--sums", type=Path, required=True)
    parser.add_argument("--github-commit", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    github_commit = args.github_commit.lower()
    if not re.fullmatch(r"[0-9a-f]{40}", github_commit):
        raise SystemExit("--github-commit must be an exact 40-character commit ID")
    files = [args.pdf.resolve(), args.zip_path.resolve(), args.sums.resolve()]
    expected_names = [PDF_NAME, ZIP_NAME, SUMS_NAME]
    if [path.name for path in files] != expected_names or not all(path.is_file() for path in files):
        raise SystemExit("release payload filenames or paths are incorrect")
    receipts, release_metadata = validate_payload(*files, github_commit)

    public_latest = public_latest_preflight()
    session = authenticated_session(args.token_file.resolve())
    depositions = [
        item
        for item in deposition_search(session)
        if str(item.get("conceptrecid")) == EXPECTED_CONCEPTRECID
    ]
    current = [
        item
        for item in depositions
        if item.get("state") == "done"
        and item.get("submitted") is True
        and item.get("metadata", {}).get("version") == VERSION
    ]
    if current:
        if len(current) != 1:
            raise RuntimeError("multiple published copies of the target version exist")
        published = current[0]
        print(
            json.dumps(
                {
                    "result": "already_published",
                    "record_id": str(published.get("record_id", "")),
                    "deposition_id": str(published.get("id", "")),
                    "conceptrecid": str(published.get("conceptrecid", "")),
                    "doi": str(published.get("doi", "")),
                    "version": VERSION,
                    "github_commit": github_commit,
                    "github_tree": release_metadata["git_tree"],
                    "credential_material_recorded": False,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return
    active = [
        item
        for item in depositions
        if item.get("state") != "done" or item.get("submitted") is not True
    ]
    if len(active) > 1:
        raise RuntimeError("multiple active O008 drafts exist; refusing an ambiguous mutation")
    previous = [
        item
        for item in depositions
        if item.get("state") == "done"
        and item.get("submitted") is True
        and item.get("metadata", {}).get("version") == EXPECTED_PREVIOUS_VERSION
    ]
    if len(previous) != 1:
        raise RuntimeError("could not identify the exact previous O008 version")
    original = previous[0]
    if str(original.get("record_id")) != EXPECTED_PREVIOUS_RECORD_ID:
        raise RuntimeError("authenticated previous deposition differs from public latest")

    resumable_draft: dict[str, Any] | None = None
    if active:
        candidate = active[0]
        self_url = str(candidate.get("links", {}).get("self", ""))
        if not self_url.startswith(f"{BASE}/api/deposit/depositions/"):
            raise RuntimeError("active O008 draft lacks a canonical deposition URL")
        resumable_draft = checked(session.get(self_url, timeout=30), {200}).json()
        if (
            str(resumable_draft.get("conceptrecid")) != EXPECTED_CONCEPTRECID
            or str(resumable_draft.get("id")) == str(original.get("id"))
            or str(resumable_draft.get("record_id")) == EXPECTED_PREVIOUS_RECORD_ID
            or resumable_draft.get("submitted") is True
            or resumable_draft.get("metadata", {}).get("version")
            not in {EXPECTED_PREVIOUS_VERSION, VERSION}
            or resumable_draft.get("metadata", {}).get("title") != TITLE
        ):
            raise RuntimeError("active draft is not the exact resumable O008 new version")

    if args.dry_run:
        print(
            json.dumps(
                {
                    "result": "authorized_probe_pass",
                    "conceptrecid": EXPECTED_CONCEPTRECID,
                    "previous_deposition_id": str(original["id"]),
                    "previous_version": EXPECTED_PREVIOUS_VERSION,
                    "target_version": VERSION,
                    "public_latest_record_id": str(public_latest["id"]),
                    "has_newversion_link": "newversion" in original["links"],
                    "resumable_draft_id": (
                        str(resumable_draft.get("id")) if resumable_draft else None
                    ),
                    "github_commit": github_commit,
                    "github_tree": release_metadata["git_tree"],
                    "payload_upload_order": [item["filename"] for item in receipts],
                    "payload": receipts,
                    "credential_material_recorded": False,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return

    if resumable_draft is None:
        response = checked(
            session.post(original["links"]["newversion"], timeout=60), {201, 202}
        )
        draft_url = response.json()["links"]["latest_draft"]
        draft = checked(session.get(draft_url, timeout=30), {200}).json()
    else:
        draft = resumable_draft
        draft_url = str(draft["links"]["self"])
    if str(draft.get("conceptrecid")) != EXPECTED_CONCEPTRECID:
        raise RuntimeError("new draft left the existing O008 concept")
    if str(draft.get("record_id")) == EXPECTED_PREVIOUS_RECORD_ID:
        raise RuntimeError("draft is an edit of the predecessor, not a new version")
    for inherited in list(draft.get("files", [])):
        checked(session.delete(inherited["links"]["self"], timeout=60), {204})

    bucket = draft["links"]["bucket"].rstrip("/")
    # Upload the human-readable PDF first; public APIs do not guarantee display order.
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

    uploaded = checked(session.get(draft_url, timeout=30), {200}).json()
    uploaded_by_name = {item["filename"]: item for item in uploaded.get("files", [])}
    if set(uploaded_by_name) != set(expected_names):
        raise RuntimeError("Zenodo draft file inventory differs after upload")
    for receipt in receipts:
        item = uploaded_by_name[receipt["filename"]]
        checksum = str(item.get("checksum", "")).removeprefix("md5:")
        if int(item.get("filesize", -1)) != receipt["bytes"] or checksum != receipt["md5"]:
            raise RuntimeError(f"Zenodo draft file identity differs: {receipt['filename']}")

    metadata = writable_metadata(draft["metadata"], github_commit)
    assert_release_metadata(metadata, github_commit)
    draft = checked(session.put(draft_url, json={"metadata": metadata}, timeout=60), {200}).json()
    assert_release_metadata(draft.get("metadata", {}), github_commit)
    final_files = {item.get("filename"): item for item in draft.get("files", [])}
    if set(final_files) != set(expected_names):
        raise RuntimeError("Zenodo pre-publish file inventory changed")
    for receipt in receipts:
        item = final_files[receipt["filename"]]
        checksum = str(item.get("checksum", "")).removeprefix("md5:")
        if int(item.get("filesize", -1)) != receipt["bytes"] or checksum != receipt["md5"]:
            raise RuntimeError(f"Zenodo pre-publish bytes differ: {receipt['filename']}")
    published = checked(session.post(draft["links"]["publish"], timeout=120), {202}).json()
    if (
        str(published.get("conceptrecid")) != EXPECTED_CONCEPTRECID
        or published.get("metadata", {}).get("version") != VERSION
        or published.get("state") != "done"
        or published.get("submitted") is not True
    ):
        raise RuntimeError("published Zenodo response is not the exact final O008 version")
    assert_release_metadata(published.get("metadata", {}), github_commit)

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
        "github_commit": github_commit,
        "github_tree": release_metadata["git_tree"],
        "files": receipts,
        "credential_material_recorded": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
