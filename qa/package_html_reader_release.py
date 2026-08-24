#!/usr/bin/env python3
"""Build the deterministic O008 source-text plus semantic-HTML release bundle."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
RELEASE = "2026.08.24-html-reader"
PREFIX = f"functional-analysis-erdman-id-{RELEASE}"
PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf"
ZIP_NAME = f"{PREFIX}-source-backend.zip"
SUMS_NAME = "SHA256SUMS.txt"
OUTPUT_DIR = ROOT / "qa" / "release-html-reader"
MAX_RELEASE_BYTES = 500_000_000
SCOPE = (
    "in progress overall; complete Indonesian source-text translation and "
    "complete admitted semantic HTML reader; O001 mastery/solutions and the "
    "separately provenanced compact-spectral/SVD bridge remain"
)

EXPECTED_PDF_SHA256 = (
    "efa2358b3c3e6e8c47e0caee9a02f6afe78d15bea1b0f1822ea8449d801b2b10"
)
EXPECTED_SITE_FILE_COUNT = 105
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

TOP_LEVEL = {
    ".gitattributes",
    ".gitignore",
    "README.md",
    "BUILD.md",
    "LICENSE.md",
}
SOURCE_FILES = {
    "source/id-ID/functional-analysis-id-complete-source.tex",
    "source/id-ID/preface-id.tex",
    "source/id-ID/linalg-id.tex",
    "source/id-ID/categories-id.tex",
    "source/id-ID/normlinspaces-id.tex",
    "source/id-ID/Hilbert_spaces-id.tex",
    "source/id-ID/Hilbert_space_operators-id.tex",
    "source/id-ID/Banach_spaces-id.tex",
    "source/id-ID/compact_operators-id.tex",
    "source/id-ID/spectrum-id.tex",
    "source/id-ID/topvecspaces-id.tex",
    "source/id-ID/distributions-id.tex",
    "source/id-ID/Gelfand_Naimark-id.tex",
    "source/id-ID/no_identity-id.tex",
    "source/id-ID/GNS_construction-id.tex",
    "source/id-ID/multiplier_algebras-id.tex",
    "source/id-ID/fredholm_theory-id.tex",
    "source/id-ID/extensions-id.tex",
    "source/id-ID/K0_functor-id.tex",
    "source/id-ID/functional_analysis_op_algs_bib.bib",
    # Byte-identical Michael Barr component required by the translated master.
    "source/id-ID/DIAGXY.TEX",
}
QA_FILES = {
    "qa/HTML_BUILD_RESULT.json",
    "qa/HTML_READER_QA.json",
    "qa/HTML_VISUAL_QA.json",
    "qa/HTML_BACKEND_VALIDATION.json",
    "qa/HTML_BACKEND_RECONCILIATION.md",
}
PROVENANCE_FILES = {
    "provenance/SOURCE_AUTHORITY.md",
    "provenance/SOURCE_MANIFEST.csv",
    "provenance/PREFACE_BUILD_AND_QA_RECEIPT.md",
    "provenance/HTML_READER_BUILD_AND_QA_RECEIPT.md",
    "provenance/TRANSLATION_MODEL_PROVENANCE.md",
    "provenance/SOURCE_CORRECTIONS.md",
}
HTML_SOURCE_FILES = {
    "html/build_reader.py",
    "html/qa_reader.py",
    "html/static/reader.css",
    "html/accessibility/diagram_text.jsonl",
}
BACKEND_MANIFEST_PATH = "backend/BACKEND_MANIFEST.csv"
REQUIRED_EXACT = (
    TOP_LEVEL
    | SOURCE_FILES
    | HTML_SOURCE_FILES
    | QA_FILES
    | PROVENANCE_FILES
    | {BACKEND_MANIFEST_PATH}
)
INCLUDED_PREFIXES = ("output/html/",)
FORBIDDEN_COMPONENTS = {
    "TABLE.TEX",
    "by-sa.eps",
    "by-sa.pdf",
    "Wiener_quote.tex",
}
FORBIDDEN_COMPONENTS_LOWER = {name.lower() for name in FORBIDDEN_COMPONENTS}
FORBIDDEN_PREFIXES = (
    ".git/",
    "00_control/",
    "authority/",
    "qa/build-",
    "qa/html-final-build/",
    "qa/html-replay-",
    "qa/release-",
    "output/pdf/",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(git: str, commit: str, path: str) -> bytes:
    return subprocess.check_output(
        [git, "-C", str(ROOT), "show", f"{commit}:{path}"]
    )


def include(path: str) -> bool:
    if unsafe(path):
        return False
    if path in REQUIRED_EXACT:
        return True
    return path.startswith(INCLUDED_PREFIXES)


def unsafe(path: str) -> bool:
    lowered = path.lower()
    parts = tuple(part.lower() for part in PurePosixPath(path).parts)
    name = PurePosixPath(lowered).name
    secret_parts = {
        "token",
        "tokens",
        "credential",
        "credentials",
        "secret",
        "secrets",
        "private_key",
    }
    disposable_parts = {
        "__pycache__",
        "cache",
        "caches",
        "tmp",
        "temp",
        "scratch",
        "dump",
        "dumps",
    }
    secret_pattern = re.compile(
        r"(?:^|[^a-z0-9])(?:token|tokens|credential|credentials|secret|secrets|"
        r"private[._ -]?key)(?:$|[^a-z0-9])"
    )
    return (
        lowered.startswith(tuple(prefix.lower() for prefix in FORBIDDEN_PREFIXES))
        or name in FORBIDDEN_COMPONENTS_LOWER
        or name in {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
        or ".git" in parts
        or any(part in secret_parts or part in disposable_parts for part in parts)
        or any(secret_pattern.search(part) for part in parts)
        or lowered.endswith(
            (".pyc", ".pyo", ".tmp", ".bak", ".pem", ".key", ".p12", ".pfx")
        )
    )


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 8, 24, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    return info


def verify_site_manifest(payload_by_path: dict[str, bytes]) -> tuple[int, int, str]:
    manifest_path = "output/html/MANIFEST.csv"
    manifest = payload_by_path[manifest_path]
    if sha256(manifest) != EXPECTED_SITE_MANIFEST_SHA256:
        raise SystemExit("semantic HTML manifest is not the admitted manifest")
    rows = list(csv.DictReader(io.StringIO(manifest.decode("utf-8-sig"))))
    expected_paths = {
        path.removeprefix("output/html/")
        for path in payload_by_path
        if path.startswith("output/html/") and path != manifest_path
    }
    if {row.get("path", "") for row in rows} != expected_paths:
        raise SystemExit("semantic HTML manifest path inventory differs")
    for row in rows:
        relative = row["path"]
        data = payload_by_path[f"output/html/{relative}"]
        if int(row["bytes"]) != len(data) or row["sha256"] != sha256(data):
            raise SystemExit(f"semantic HTML manifest identity differs: {relative}")
    tree_material = "".join(
        f"{row['path']}\0{row['bytes']}\0{row['sha256']}\n" for row in rows
    ).encode("utf-8")
    tree_hash = sha256(tree_material)
    file_count = len(rows) + 1
    if file_count != EXPECTED_SITE_FILE_COUNT or tree_hash != EXPECTED_SITE_TREE_SHA256:
        raise SystemExit("semantic HTML tree is not the admitted 105-file tree")
    site_bytes = sum(
        len(data)
        for path, data in payload_by_path.items()
        if path.startswith("output/html/")
    )
    return file_count, site_bytes, tree_hash


def backend_inventory(manifest: bytes) -> tuple[set[str], list[dict[str, str]]]:
    if sha256(manifest) != EXPECTED_BACKEND_MANIFEST_SHA256:
        raise SystemExit("backend manifest is not the admitted HTML-reconciled manifest")
    rows = list(csv.DictReader(io.StringIO(manifest.decode("utf-8-sig"))))
    if not rows or set(rows[0]) != {"relative_path", "bytes", "sha256"}:
        raise SystemExit("backend manifest schema differs")
    paths: set[str] = set()
    for row in rows:
        relative = row["relative_path"]
        pure = PurePosixPath(relative)
        if (
            relative.startswith("/")
            or ".." in pure.parts
            or len(pure.parts) != 1
            or relative in paths
        ):
            raise SystemExit("backend manifest has a duplicate or unsafe path")
        paths.add(relative)
    return {f"backend/{path}" for path in paths} | {BACKEND_MANIFEST_PATH}, rows


def verify_backend_manifest(
    payload_by_path: dict[str, bytes], rows: list[dict[str, str]]
) -> None:
    expected_paths = {f"backend/{row['relative_path']}" for row in rows} | {
        BACKEND_MANIFEST_PATH
    }
    actual_paths = {path for path in payload_by_path if path.startswith("backend/")}
    if actual_paths != expected_paths:
        raise SystemExit("packaged backend inventory differs from BACKEND_MANIFEST.csv")
    for row in rows:
        path = f"backend/{row['relative_path']}"
        data = payload_by_path[path]
        if int(row["bytes"]) != len(data) or row["sha256"] != sha256(data):
            raise SystemExit(f"backend manifest identity differs: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--git", default="git")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        raise SystemExit("--commit must be an exact lowercase 40-character ID")
    if not re.fullmatch(r"[0-9a-f]{40}", args.tree):
        raise SystemExit("--tree must be an exact lowercase 40-character ID")
    output_dir = args.output_dir.resolve()
    if output_dir != OUTPUT_DIR.resolve():
        raise SystemExit(f"--output-dir must be the canonical release path: {OUTPUT_DIR}")

    resolved_commit = subprocess.check_output(
        [
            args.git,
            "-C",
            str(ROOT),
            "rev-parse",
            "--verify",
            f"{args.commit}^{{commit}}",
        ],
        text=True,
    ).strip()
    resolved_tree = subprocess.check_output(
        [
            args.git,
            "-C",
            str(ROOT),
            "rev-parse",
            "--verify",
            f"{args.commit}^{{tree}}",
        ],
        text=True,
    ).strip()
    if resolved_commit != args.commit or resolved_tree != args.tree:
        raise SystemExit("supplied commit/tree identity does not resolve exactly")

    listed = subprocess.check_output(
        [
            args.git,
            "-C",
            str(ROOT),
            "ls-tree",
            "-r",
            "--name-only",
            args.commit,
        ],
        text=True,
    ).splitlines()
    if BACKEND_MANIFEST_PATH not in listed:
        raise SystemExit("supplied commit lacks BACKEND_MANIFEST.csv")
    backend_paths, backend_rows = backend_inventory(
        git_bytes(args.git, args.commit, BACKEND_MANIFEST_PATH)
    )
    if not backend_paths <= set(listed):
        raise SystemExit("supplied commit lacks a backend-manifest member")
    selected = sorted(
        {path for path in listed if include(path)} | backend_paths
    )
    missing = REQUIRED_EXACT - set(selected)
    rejected = [path for path in selected if unsafe(path)]
    if missing:
        raise SystemExit(f"required release files are missing: {sorted(missing)}")
    if rejected:
        raise SystemExit(f"unsafe or forbidden release paths selected: {rejected}")

    payloads = [(path, git_bytes(args.git, args.commit, path)) for path in selected]
    payload_by_path = dict(payloads)
    verify_backend_manifest(payload_by_path, backend_rows)
    if sha256(payload_by_path["backend/html_routes.jsonl"]) != EXPECTED_ROUTE_MAP_SHA256:
        raise SystemExit("HTML route map is not the admitted exact-case route map")
    site_file_count, site_bytes, site_tree_hash = verify_site_manifest(payload_by_path)

    # The release is commit-derived, but the local admitted HTML tree must also be
    # exactly the same tree; this catches untracked additions and post-commit edits.
    disk_html_paths = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "output" / "html").rglob("*")
        if path.is_file()
    }
    committed_html_paths = {
        path for path in selected if path.startswith("output/html/")
    }
    if disk_html_paths != committed_html_paths:
        raise SystemExit("worktree output/html inventory differs from the supplied commit")
    for path in sorted(committed_html_paths):
        if (ROOT / path).read_bytes() != payload_by_path[path]:
            raise SystemExit(f"worktree output/html byte mismatch: {path}")

    pdf_path = ROOT / "output" / "pdf" / PDF_NAME
    if not pdf_path.is_file():
        raise SystemExit(f"missing canonical PDF reader: {pdf_path}")
    pdf_data = pdf_path.read_bytes()
    if sha256(pdf_data) != EXPECTED_PDF_SHA256:
        raise SystemExit("canonical PDF is not the admitted unchanged complete-source PDF")
    if pdf_data != git_bytes(args.git, args.commit, f"output/pdf/{PDF_NAME}"):
        raise SystemExit("worktree PDF differs from the supplied commit blob")

    private_path_markers = (
        bytes((67, 58, 47, 85, 115, 101, 114, 115, 47)),
        bytes((67, 58, 92, 85, 115, 101, 114, 115, 92)),
    )
    private_paths = [
        path
        for path, data in payloads
        if any(marker in data for marker in private_path_markers)
    ]
    if private_paths:
        raise SystemExit(f"private absolute path found in release payload: {private_paths}")

    release_manifest_stream = io.StringIO(newline="")
    writer = csv.writer(release_manifest_stream, lineterminator="\n")
    writer.writerow(["path", "bytes", "sha256"])
    for path, data in payloads:
        writer.writerow([path, len(data), sha256(data)])
    release_manifest = release_manifest_stream.getvalue().encode("utf-8")
    metadata = json.dumps(
        {
            "schema_version": "o008.release-html-reader.v1",
            "release": RELEASE,
            "overall_status": "in_progress",
            "source_text_status": "complete",
            "semantic_html_status": "complete",
            "remaining_components": [
                "O001 mastery/solutions layer",
                "separately provenanced compact-spectral/SVD bridge",
            ],
            "scope": SCOPE,
            "git_commit": args.commit,
            "git_tree": args.tree,
            "license": "CC BY-SA 4.0",
            "primary_reader_uploaded_separately": PDF_NAME,
            "semantic_html_root": "output/html/",
            "semantic_html_file_count": site_file_count,
            "semantic_html_expanded_bytes": site_bytes,
            "semantic_html_tree_sha256": site_tree_hash,
            "semantic_html_manifest_sha256": EXPECTED_SITE_MANIFEST_SHA256,
            "backend_manifest_sha256": EXPECTED_BACKEND_MANIFEST_SHA256,
            "html_route_map_sha256": EXPECTED_ROUTE_MAP_SHA256,
            "required_upstream_build_component": "source/id-ID/DIAGXY.TEX",
            "excluded_components": sorted(FORBIDDEN_COMPONENTS),
            "file_count_excluding_generated_inventory": len(payloads),
            "expanded_file_bytes_excluding_generated_inventory": sum(
                len(data) for _, data in payloads
            ),
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8") + b"\n"

    expanded_release_bytes = sum(len(data) for _, data in payloads) + len(
        release_manifest
    ) + len(metadata)
    if expanded_release_bytes + len(pdf_data) > MAX_RELEASE_BYTES:
        raise SystemExit("expanded release payload exceeds the 500,000,000-byte cap")

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / ZIP_NAME
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path, data in payloads:
            archive.writestr(zip_info(f"{PREFIX}/{path}"), data)
        archive.writestr(
            zip_info(f"{PREFIX}/RELEASE_MANIFEST.csv"), release_manifest
        )
        archive.writestr(zip_info(f"{PREFIX}/RELEASE_METADATA.json"), metadata)

    with zipfile.ZipFile(zip_path, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise SystemExit(f"corrupt ZIP entry: {bad}")
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise SystemExit("duplicate ZIP entry")
        expected_names = {
            f"{PREFIX}/{path}" for path, _ in payloads
        } | {
            f"{PREFIX}/RELEASE_MANIFEST.csv",
            f"{PREFIX}/RELEASE_METADATA.json",
        }
        if set(names) != expected_names:
            raise SystemExit("ZIP entry inventory differs from the canonical payload")
        for info in infos:
            with archive.open(info) as stream:
                while stream.read(1024 * 1024):
                    pass
        if any(
            PurePosixPath(name.lower()).name in FORBIDDEN_COMPONENTS_LOWER
            for name in names
        ):
            raise SystemExit("forbidden component entered the ZIP")

    zip_data = zip_path.read_bytes()
    if len(pdf_data) + len(zip_data) > MAX_RELEASE_BYTES:
        raise SystemExit("compressed release payload exceeds the 500,000,000-byte cap")
    sums = (
        f"{sha256(pdf_data)}  {PDF_NAME}\n"
        f"{sha256(zip_data)}  {ZIP_NAME}\n"
    ).encode("ascii")
    sums_path = output_dir / SUMS_NAME
    sums_path.write_bytes(sums)

    result = {
        "result": "pass",
        "release": RELEASE,
        "scope": SCOPE,
        "overall_status": "in_progress",
        "source_text_status": "complete",
        "semantic_html_status": "complete",
        "commit": args.commit,
        "tree": args.tree,
        "archive_entries": len(infos),
        "tracked_payload_files": len(payloads),
        "expanded_tracked_bytes": sum(len(data) for _, data in payloads),
        "semantic_html": {
            "files": site_file_count,
            "bytes": site_bytes,
            "tree_sha256": site_tree_hash,
        },
        "zip": {
            "filename": zip_path.name,
            "bytes": len(zip_data),
            "sha256": sha256(zip_data),
        },
        "pdf": {
            "filename": pdf_path.name,
            "bytes": len(pdf_data),
            "sha256": sha256(pdf_data),
        },
        "sums": {
            "filename": sums_path.name,
            "bytes": len(sums),
            "sha256": sha256(sums),
        },
        "forbidden_entries": 0,
        "commit_tree_verified": True,
        "reader_matches_commit_blob": True,
        "html_worktree_matches_commit": True,
        "private_absolute_paths": 0,
        "all_entry_streams_read": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
