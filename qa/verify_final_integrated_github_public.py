#!/usr/bin/env python3
"""Anonymously verify the final integrated O008 GitHub commit byte-for-byte."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPOSITORY = "functional-analysis-erdman-id"
BRANCH = "main"
RECEIPT = ROOT / "provenance" / "GITHUB_PUBLICATION_RECEIPT_FINAL.json"
REQUIRED = {
    "README.md",
    "BUILD.md",
    "source/id-ID/functional-analysis-id-complete-with-companions.tex",
    "output/pdf/analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf",
    "output/html-companion/index.html",
    "output/html-companion/MANIFEST.csv",
    "mastery/O001_EXERCISE_INVENTORY.jsonl",
    "mastery/O001_READER_WORK_INVENTORY.jsonl",
    "bridge/id-ID/compact-spectral-svd.tex",
    "backend/COMPANION_BACKEND_MANIFEST.csv",
    "qa/FINAL_COMPANION_BUILD_RESULT.json",
    "qa/COMPANION_BACKEND_VALIDATION.json",
    "provenance/FINAL_EDITION_BUILD_AND_QA_RECEIPT.md",
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


def forbidden(path: str) -> bool:
    lowered = path.lower()
    parts = set(PurePosixPath(lowered).parts)
    return (
        lowered.startswith(("00_control/", "authority/", "tmp/", "qa/build-", "qa/replay-", "qa/release-"))
        or "__pycache__" in parts
        or any(part in {"token", "tokens", "credential", "credentials", "secret", "secrets"} for part in parts)
        or bool(re.search(r"(?:^|[^a-z0-9])(?:token|credential|secret)(?:$|[^a-z0-9])", lowered))
        or lowered.endswith((".pyc", ".pyo", ".tmp", ".bak", ".pem", ".key", ".p12", ".pfx"))
    )


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
    if git_text("rev-parse", "HEAD") != commit or git_text("rev-parse", "HEAD^{tree}") != tree:
        raise SystemExit("local HEAD/tree differs from supplied identity")
    if git_text("rev-parse", f"{base}^{{commit}}") != base:
        raise SystemExit("base commit does not resolve exactly")
    paths = git_text("diff", "--name-only", f"{base}..{commit}", "--").splitlines()
    if not paths or len(paths) != len(set(paths)):
        raise SystemExit("final changed-path inventory is empty or duplicated")
    if not REQUIRED <= set(paths):
        raise SystemExit(f"required final paths are absent: {sorted(REQUIRED - set(paths))}")
    rejected = [path for path in paths if forbidden(path)]
    if rejected:
        raise SystemExit(f"private or transient paths entered the final commit: {rejected}")

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
        raise RuntimeError("public ref or tree differs from the local final commit")

    total_bytes = 0
    readback: list[dict[str, object]] = []
    for path in paths:
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
        "receipt_id": "FAOA-2015-ID-FINAL-GITHUB-PUBLICATION",
        "verified_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
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
        "private_or_transient_paths_published": False,
        "credential_material_recorded": False,
        "result": "pass",
    }
    RECEIPT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
