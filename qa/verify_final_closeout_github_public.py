#!/usr/bin/env python3
"""Anonymously verify the O008 publication-closeout commit byte-for-byte."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
RECEIPT = ROOT / "provenance" / "GITHUB_PUBLICATION_RECEIPT_FINAL_CLOSEOUT.json"
EXPECTED_PATHS = {
    "README.md",
    "provenance/FINAL_RELEASE_PACKAGE_RECEIPT.json",
    "provenance/GITHUB_PUBLICATION_RECEIPT_FINAL.json",
    "provenance/GITHUB_REPOSITORY_METADATA_FINAL.json",
    "provenance/O008_COORDINATOR_HANDOFF_FINAL.json",
    "provenance/ZENODO_PUBLICATION_RECEIPT_FINAL_INTEGRATED.json",
    "qa/verify_final_closeout_github_public.py",
}


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_json(session: requests.Session, url: str) -> dict[str, object]:
    response = session.get(url, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"anonymous GitHub API read returned {response.status_code}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("anonymous GitHub response is not an object")
    return payload


def raw_bytes(session: requests.Session, commit: str, path: str) -> bytes:
    url = (
        f"https://raw.githubusercontent.com/{OWNER}/{REPOSITORY}/"
        f"{commit}/{quote(path, safe='/')}"
    )
    for attempt in range(5):
        response = session.get(url, timeout=90)
        if response.status_code == 200:
            return response.content
        if attempt < 4:
            time.sleep(2)
    raise RuntimeError(f"anonymous raw read failed for {path}: HTTP {response.status_code}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    args = parser.parse_args()
    base, commit, tree = args.base.lower(), args.commit.lower(), args.tree.lower()
    for label, value in (("base", base), ("commit", commit), ("tree", tree)):
        if not re.fullmatch(r"[0-9a-f]{40}", value):
            raise SystemExit(f"--{label} must be an exact lowercase object ID")

    if git_text("rev-parse", "HEAD") != commit:
        raise SystemExit("local HEAD differs from supplied commit")
    if git_text("rev-parse", "HEAD^{tree}") != tree:
        raise SystemExit("local tree differs from supplied tree")
    if git_text("rev-parse", "HEAD^") != base:
        raise SystemExit("closeout commit is not the direct child of --base")
    paths = set(git_text("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines())
    if paths != EXPECTED_PATHS:
        raise SystemExit(
            "closeout path inventory differs: "
            f"missing={sorted(EXPECTED_PATHS - paths)} extra={sorted(paths - EXPECTED_PATHS)}"
        )

    session = requests.Session()
    session.trust_env = False
    session.headers.update({"Accept": "application/vnd.github+json"})
    ref = checked_json(
        session,
        f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/git/ref/heads/{BRANCH}",
    )
    remote_head = str(dict(ref.get("object", {})).get("sha", ""))
    commit_payload = checked_json(
        session,
        f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/git/commits/{commit}",
    )
    remote_tree = str(dict(commit_payload.get("tree", {})).get("sha", ""))
    if remote_head != commit or remote_tree != tree:
        raise RuntimeError("public ref or tree differs from the local closeout commit")

    total_bytes = 0
    readback: list[dict[str, object]] = []
    for path in sorted(paths):
        local = git_bytes(commit, path)
        public = raw_bytes(session, commit, path)
        if local != public:
            raise RuntimeError(f"public byte readback mismatch: {path}")
        total_bytes += len(public)
        readback.append(
            {"path": path, "bytes": len(public), "sha256": sha256(public), "match": True}
        )

    result = {
        "schema_version": "1.0.0",
        "receipt_id": "FAOA-2015-ID-FINAL-GITHUB-PUBLICATION-CLOSEOUT",
        "verified_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "repository": f"https://github.com/{OWNER}/{REPOSITORY}",
        "branch": BRANCH,
        "base_commit": base,
        "commit": commit,
        "tree": tree,
        "remote_head": remote_head,
        "remote_tree": remote_tree,
        "anonymous_changed_path_readback": {
            "path_count": len(paths),
            "total_bytes": total_bytes,
            "all_paths_match_local_bytes": True,
            "paths": readback,
        },
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
