#!/usr/bin/env python3
"""Build and verify the deterministic Chapter 11 Zenodo source/backend bundle."""

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


RELEASE = "2026.08.23-ch11"
PREFIX = f"functional-analysis-erdman-id-{RELEASE}"
PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-bab-1-11.pdf"
ZIP_NAME = f"{PREFIX}-source-backend.zip"
SCOPE = "in progress; Chapters 1--11 of 17"
FORBIDDEN = {
    "source/upstream/TABLE.TEX",
    "source/upstream/by-sa.eps",
    "source/upstream/by-sa.pdf",
    "source/upstream/Wiener_quote.tex",
}
TOP_LEVEL = {
    ".gitattributes",
    ".gitignore",
    "README.md",
    "BUILD.md",
    "LICENSE.md",
    "CITATION.cff",
}
PREFIXES = ("source/id-ID/", "source/upstream/", "backend/", "provenance/", "qa/")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(git: str, commit: str, path: str) -> bytes:
    return subprocess.check_output([git, "show", f"{commit}:{path}"])


def include(path: str) -> bool:
    if path in FORBIDDEN:
        return False
    if path in TOP_LEVEL:
        return True
    if not path.startswith(PREFIXES):
        return False
    if path.startswith("qa/build-") or path.startswith("qa/renders/"):
        return False
    if path.startswith("qa/release-"):
        return False
    if "backend-scratch" in path or "/__pycache__/" in path:
        return False
    suffix = PurePosixPath(path).suffix.lower()
    if path.startswith("provenance/") and suffix in {".png", ".pdf"}:
        return False
    if path.startswith("qa/") and suffix in {".png", ".pdf", ".html"}:
        return False
    return True


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 8, 23, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    return info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--git", default="git")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        raise SystemExit("--commit must be an exact lowercase 40-character ID")
    if not re.fullmatch(r"[0-9a-f]{40}", args.tree):
        raise SystemExit("--tree must be an exact lowercase 40-character ID")
    resolved_commit = subprocess.check_output(
        [args.git, "rev-parse", "--verify", f"{args.commit}^{{commit}}"], text=True
    ).strip()
    resolved_tree = subprocess.check_output(
        [args.git, "rev-parse", "--verify", f"{args.commit}^{{tree}}"], text=True
    ).strip()
    if resolved_commit != args.commit or resolved_tree != args.tree:
        raise SystemExit("supplied commit/tree identity does not resolve exactly")

    root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = root / "output" / "pdf" / PDF_NAME
    if not pdf_path.is_file():
        raise SystemExit(f"missing reader: {pdf_path}")
    pdf_data = pdf_path.read_bytes()
    committed_pdf = git_bytes(args.git, args.commit, f"output/pdf/{PDF_NAME}")
    if pdf_data != committed_pdf:
        raise SystemExit("worktree reader differs from the supplied commit blob")

    listed = subprocess.check_output(
        [args.git, "ls-tree", "-r", "--name-only", args.commit], text=True
    ).splitlines()
    paths = sorted(path for path in listed if include(path))
    missing_top = {"README.md", "BUILD.md", "LICENSE.md"} - set(paths)
    if missing_top:
        raise SystemExit(f"missing required tracked files: {sorted(missing_top)}")
    if FORBIDDEN & set(paths):
        raise SystemExit("forbidden component selected")

    payloads = [(path, git_bytes(args.git, args.commit, path)) for path in paths]
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
    manifest_buffer = io.StringIO(newline="")
    writer = csv.writer(manifest_buffer, lineterminator="\n")
    writer.writerow(["path", "bytes", "sha256"])
    for path, data in payloads:
        writer.writerow([path, len(data), sha256(data)])
    manifest = manifest_buffer.getvalue().encode("utf-8")
    metadata = json.dumps(
        {
            "schema_version": "o008.release-source-backend.v1",
            "release": RELEASE,
            "scope": SCOPE,
            "git_commit": args.commit,
            "git_tree": args.tree,
            "license": "CC BY-SA 4.0",
            "reader_uploaded_separately": PDF_NAME,
            "excluded_components": sorted(FORBIDDEN),
            "file_count_excluding_generated_inventory": len(payloads),
            "expanded_file_bytes_excluding_generated_inventory": sum(
                len(data) for _, data in payloads
            ),
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8") + b"\n"

    zip_path = output_dir / ZIP_NAME
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zf:
        for path, data in payloads:
            zf.writestr(zip_info(f"{PREFIX}/{path}"), data)
        zf.writestr(zip_info(f"{PREFIX}/RELEASE_MANIFEST.csv"), manifest)
        zf.writestr(zip_info(f"{PREFIX}/RELEASE_METADATA.json"), metadata)

    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            raise SystemExit(f"corrupt ZIP entry: {bad}")
        infos = zf.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise SystemExit("duplicate ZIP entry")
        for info in infos:
            with zf.open(info) as stream:
                while stream.read(1024 * 1024):
                    pass
        forbidden_names = [
            name for name in names if any(name.endswith(x) for x in FORBIDDEN)
        ]
        if forbidden_names:
            raise SystemExit(f"forbidden ZIP entries: {forbidden_names}")

    zip_data = zip_path.read_bytes()
    sums = (
        f"{sha256(pdf_data)}  {PDF_NAME}\n"
        f"{sha256(zip_data)}  {ZIP_NAME}\n"
    ).encode("ascii")
    sums_path = output_dir / "SHA256SUMS.txt"
    sums_path.write_bytes(sums)

    result = {
        "result": "pass",
        "release": RELEASE,
        "scope": SCOPE,
        "commit": args.commit,
        "tree": args.tree,
        "archive_entries": len(infos),
        "tracked_payload_files": len(payloads),
        "expanded_tracked_bytes": sum(len(data) for _, data in payloads),
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
        "private_absolute_paths": 0,
        "all_entry_streams_read": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
