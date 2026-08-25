#!/usr/bin/env python3
"""Anonymously verify the terminal O008 backend-reconciliation closeout."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import sys

import verify_authority_hash_correction_github_public as _base


RECEIPT = (
    _base.ROOT
    / "provenance"
    / "GITHUB_PUBLICATION_RECEIPT_BACKEND_ARTIFACT_RECONCILIATION_FINAL_CLOSEOUT.json"
)
RELEASE_COMMIT = "059bda086dfd6e6aa80f2077b2338c5d15039057"
RELEASE_TREE = "77822a94a46d6422d9ed9c6b48e345229a4e7c05"
VERSION_DOI = "10.5281/zenodo.22088947"
EXPECTED_PATHS = {
    "README.md",
    "provenance/BACKEND_ARTIFACT_RECONCILIATION_RELEASE_PACKAGE_RECEIPT.json",
    "provenance/FINAL_EDITION_BUILD_AND_QA_RECEIPT.md",
    "provenance/GITHUB_PUBLICATION_RECEIPT_BACKEND_ARTIFACT_RECONCILIATION.json",
    "provenance/GITHUB_REPOSITORY_METADATA_BACKEND_ARTIFACT_RECONCILIATION.json",
    "provenance/O008_COORDINATOR_HANDOFF_FINAL.json",
    "provenance/ZENODO_PUBLICATION_RECEIPT_BACKEND_ARTIFACT_RECONCILIATION.json",
    "qa/verify_backend_artifact_reconciliation_final_closeout_github_public.py",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(commit: str, path: str) -> tuple[bytes, dict[str, object]]:
    data = _base.git_bytes(commit, path)
    value = json.loads(data)
    if not isinstance(value, dict):
        raise SystemExit(f"closeout JSON is not an object: {path}")
    return data, value


def assert_pointer(commit: str, pointer: dict[str, object]) -> dict[str, object]:
    path = str(pointer.get("path", ""))
    if not re.fullmatch(r"provenance/[A-Za-z0-9_.-]+", path):
        raise SystemExit(f"unsafe or missing handoff receipt path: {path!r}")
    data, value = json_bytes(commit, path)
    if int(pointer.get("bytes", -1)) != len(data) or pointer.get("sha256") != sha256(data):
        raise SystemExit(f"handoff receipt identity differs: {path}")
    if value.get("result") != "pass":
        raise SystemExit(f"handoff receipt did not pass: {path}")
    return value


def main() -> None:
    _base.EXPECTED_PATHS = EXPECTED_PATHS
    _base.RECEIPT = RECEIPT
    if any(argument in {"-h", "--help"} for argument in sys.argv[1:]):
        _base.main()
        return
    with contextlib.redirect_stdout(io.StringIO()):
        _base.main()
    result = json.loads(RECEIPT.read_text(encoding="utf-8"))
    commit = str(result["commit"])
    if result.get("base_commit") != RELEASE_COMMIT:
        raise SystemExit("closeout commit is not the direct child of the release commit")

    readme = _base.git_bytes(commit, "README.md")
    build = _base.git_bytes(commit, "provenance/FINAL_EDITION_BUILD_AND_QA_RECEIPT.md")
    handoff_data, handoff = json_bytes(
        commit, "provenance/O008_COORDINATOR_HANDOFF_FINAL.json"
    )
    publication = dict(handoff.get("publication", {}))
    github = dict(publication.get("github", {}))
    zenodo = dict(publication.get("zenodo", {}))
    reconciliation = dict(publication.get("backend_artifact_reconciliation", {}))
    quality = dict(handoff.get("quality_gates", {}))

    build_pointer = dict(quality.get("build_receipt", {}))
    if (
        build_pointer.get("path") != "provenance/FINAL_EDITION_BUILD_AND_QA_RECEIPT.md"
        or int(build_pointer.get("bytes", -1)) != len(build)
        or build_pointer.get("sha256") != sha256(build)
    ):
        raise SystemExit("handoff build-receipt identity differs")

    github_receipt = assert_pointer(
        commit, dict(github.get("backend_artifact_reconciliation_receipt", {}))
    )
    zenodo_receipt = assert_pointer(commit, dict(zenodo.get("receipt", {})))
    metadata_receipt = assert_pointer(commit, {
        "path": dict(github.get("discoverability", {})).get("receipt_path"),
        "bytes": dict(github.get("discoverability", {})).get("receipt_bytes"),
        "sha256": dict(github.get("discoverability", {})).get("receipt_sha256"),
    })
    package_receipt = assert_pointer(
        commit, dict(publication.get("release_package_receipt", {}))
    )

    if (
        handoff.get("status") != "complete"
        or reconciliation.get("status") != "complete"
        or reconciliation.get("exact_byte_binding_commit") != RELEASE_COMMIT
        or reconciliation.get("exact_byte_binding_tree") != RELEASE_TREE
        or github.get("backend_artifact_reconciliation_commit") != RELEASE_COMMIT
        or github.get("backend_artifact_reconciliation_tree") != RELEASE_TREE
        or zenodo.get("record_id") != "22088947"
        or zenodo.get("version_doi") != VERSION_DOI
        or not zenodo.get("latest_in_concept")
        or github_receipt.get("commit") != RELEASE_COMMIT
        or not github_receipt.get("anonymous_changed_path_readback", {}).get(
            "all_paths_match_local_bytes"
        )
        or zenodo_receipt.get("record_id") != "22088947"
        or not zenodo_receipt.get("anonymous_file_byte_readback")
        or package_receipt.get("git_commit") != RELEASE_COMMIT
        or package_receipt.get("git_tree") != RELEASE_TREE
        or metadata_receipt.get("homepage") != f"https://doi.org/{VERSION_DOI}"
        or VERSION_DOI.encode("ascii") not in readme
        or VERSION_DOI.encode("ascii") not in build
    ):
        raise SystemExit("terminal closeout relationship differs")

    public_material = b"\n".join(
        _base.git_bytes(commit, path) for path in sorted(EXPECTED_PATHS)
    )
    if re.search(rb"[A-Za-z]:[\\/]Users[\\/]", public_material, re.IGNORECASE):
        raise SystemExit("private profile path appears in terminal closeout")
    if re.search(
        rb"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})",
        public_material,
        re.IGNORECASE,
    ):
        raise SystemExit("credential-shaped literal appears in terminal closeout")

    result["receipt_id"] = "FAOA-2015-ID-GITHUB-BACKEND-RECONCILIATION-FINAL-CLOSEOUT"
    result["terminal_closeout"] = {
        "release_commit": RELEASE_COMMIT,
        "release_tree": RELEASE_TREE,
        "zenodo_record_id": "22088947",
        "zenodo_version_doi": VERSION_DOI,
        "handoff_bytes": len(handoff_data),
        "handoff_sha256": sha256(handoff_data),
        "build_receipt_bytes": len(build),
        "build_receipt_sha256": sha256(build),
        "github_publication_receipt_sha256": sha256(
            _base.git_bytes(
                commit,
                "provenance/GITHUB_PUBLICATION_RECEIPT_BACKEND_ARTIFACT_RECONCILIATION.json",
            )
        ),
        "zenodo_publication_receipt_sha256": sha256(
            _base.git_bytes(
                commit,
                "provenance/ZENODO_PUBLICATION_RECEIPT_BACKEND_ARTIFACT_RECONCILIATION.json",
            )
        ),
        "repository_metadata_receipt_sha256": sha256(
            _base.git_bytes(
                commit,
                "provenance/GITHUB_REPOSITORY_METADATA_BACKEND_ARTIFACT_RECONCILIATION.json",
            )
        ),
        "release_package_receipt_sha256": sha256(
            _base.git_bytes(
                commit,
                "provenance/BACKEND_ARTIFACT_RECONCILIATION_RELEASE_PACKAGE_RECEIPT.json",
            )
        ),
        "public_receipt_relationships_pass": True,
        "private_absolute_paths": 0,
        "credential_material_recorded": False,
    }
    RECEIPT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
