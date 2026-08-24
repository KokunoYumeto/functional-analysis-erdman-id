#!/usr/bin/env python3
"""Anonymously verify the complete-source GitHub commit and all changed bytes."""

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
RECEIPT = ROOT / "provenance" / "GITHUB_PUBLICATION_RECEIPT_COMPLETE_SOURCE.json"
REPRESENTATIVE = {
    "README.md",
    "source/id-ID/preface-id.tex",
    "source/id-ID/functional-analysis-id-complete-source.tex",
    "output/pdf/analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf",
    "provenance/PREFACE_BUILD_AND_QA_RECEIPT.md",
    "backend/BACKEND_MANIFEST.csv",
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
    url = f"https://raw.githubusercontent.com/{OWNER}/{REPOSITORY}/{commit}/{quote(path, safe='/')}"
    for attempt in range(3):
        response = session.get(url, timeout=60)
        if response.status_code == 200:
            return response.content
        if attempt < 2:
            time.sleep(2)
    raise RuntimeError(f"anonymous raw read failed for {path}: HTTP {response.status_code}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    args = parser.parse_args()
    commit, tree = args.commit.lower(), args.tree.lower()
    if git_text("rev-parse", "HEAD") != commit or git_text("rev-parse", "HEAD^{tree}") != tree:
        raise SystemExit("local HEAD/tree differs from supplied commit/tree")
    paths = git_text(
        "diff-tree", "--no-commit-id", "--name-only", "-r", f"{commit}^", commit
    ).splitlines()
    if not paths or len(paths) != len(set(paths)) or not REPRESENTATIVE <= set(paths):
        raise SystemExit(f"changed-path inventory is incomplete: {len(paths)}")

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
        local, public = git_bytes(commit, path), raw_bytes(session, commit, path)
        if local != public:
            raise RuntimeError(f"public byte readback mismatch: {path}")
        total_bytes += len(public)
        if path in REPRESENTATIVE:
            representative.append(
                {"path": path, "bytes": len(public), "sha256": sha256(public), "match": True}
            )

    result = {
        "schema_version": "1.0.0",
        "receipt_id": "FAOA-2015-COMPLETE-SOURCE-GITHUB-PUBLICATION",
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
