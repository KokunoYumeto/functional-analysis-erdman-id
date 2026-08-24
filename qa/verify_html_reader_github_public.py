#!/usr/bin/env python3
"""Anonymously verify the semantic-HTML GitHub commit and every changed byte."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPOSITORY = "functional-analysis-erdman-id"
BRANCH = "main"
EXPECTED_PATH_COUNT = 131
RECEIPT = ROOT / "provenance" / "GITHUB_PUBLICATION_RECEIPT_HTML_READER.json"
REPRESENTATIVE = {
    "README.md",
    "BUILD.md",
    "html/build_reader.py",
    "html/qa_reader.py",
    "output/html/index.html",
    "output/html/MANIFEST.csv",
    "backend/html_routes.jsonl",
    "backend/BACKEND_MANIFEST.csv",
    "qa/HTML_VISUAL_QA.json",
    "provenance/HTML_READER_BUILD_AND_QA_RECEIPT.md",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def checked_json(session: requests.Session, url: str) -> dict[str, object]:
    response = session.get(url, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"anonymous GitHub API read returned {response.status_code}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("anonymous GitHub API response is not an object")
    return payload


def raw_bytes(session: requests.Session, commit: str, path: str) -> bytes:
    url = (
        f"https://raw.githubusercontent.com/{OWNER}/{REPOSITORY}/"
        f"{commit}/{quote(path, safe='/')}"
    )
    for attempt in range(4):
        response = session.get(url, timeout=60)
        if response.status_code == 200:
            return response.content
        if attempt < 3:
            time.sleep(2)
    raise RuntimeError(f"anonymous raw read failed for {path}: HTTP {response.status_code}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    args = parser.parse_args()
    commit, tree = args.commit.lower(), args.tree.lower()
    if git_text("rev-parse", "HEAD") != commit:
        raise SystemExit("local HEAD differs from supplied commit")
    if git_text("rev-parse", "HEAD^{tree}") != tree:
        raise SystemExit("local tree differs from supplied tree")

    paths = git_text(
        "diff-tree", "--no-commit-id", "--name-only", "-r", f"{commit}^", commit
    ).splitlines()
    if len(paths) != EXPECTED_PATH_COUNT or len(paths) != len(set(paths)):
        raise SystemExit(f"changed-path inventory mismatch: {len(paths)}")
    if not REPRESENTATIVE <= set(paths):
        raise SystemExit("representative HTML paths are missing from the commit")
    if any(path.startswith(("00_control/", "authority/", "tmp/")) for path in paths):
        raise SystemExit("private or transient path entered the public commit")
    if any("html-replay-" in path or "CLEANUP_RECEIPT" in path for path in paths):
        raise SystemExit("replay or cleanup-only evidence entered the public commit")

    session = requests.Session()
    session.headers.update({"Accept": "application/vnd.github+json"})
    ref = checked_json(
        session,
        f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/git/ref/heads/{BRANCH}",
    )
    remote_head = str(dict(ref.get("object", {})).get("sha", ""))
    commit_payload = checked_json(
        session, f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/git/commits/{commit}"
    )
    remote_tree = str(dict(commit_payload.get("tree", {})).get("sha", ""))
    if remote_head != commit or remote_tree != tree:
        raise RuntimeError("public ref or tree differs from the local commit")

    total_bytes = 0
    representative: list[dict[str, object]] = []
    for path in paths:
        local = git_bytes(commit, path)
        public = raw_bytes(session, commit, path)
        if local != public:
            raise RuntimeError(f"public byte readback mismatch: {path}")
        total_bytes += len(public)
        if path in REPRESENTATIVE:
            representative.append(
                {"path": path, "bytes": len(public), "sha256": sha256(public), "match": True}
            )

    result = {
        "schema_version": "1.0.0",
        "receipt_id": "FAOA-2015-ID-HTML-GITHUB-PUBLICATION",
        "verified_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "repository": f"https://github.com/{OWNER}/{REPOSITORY}",
        "branch": BRANCH,
        "commit": commit,
        "tree": tree,
        "remote_head": remote_head,
        "remote_tree": remote_tree,
        "remote_head_matches": True,
        "remote_tree_matches": True,
        "anonymous_changed_path_readback": {
            "path_count": len(paths),
            "total_bytes": total_bytes,
            "all_paths_match_local_bytes": True,
            "mismatch_count": 0,
        },
        "representative_raw_readback": sorted(
            representative, key=lambda item: str(item["path"])
        ),
        "private_or_transient_paths_published": False,
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
