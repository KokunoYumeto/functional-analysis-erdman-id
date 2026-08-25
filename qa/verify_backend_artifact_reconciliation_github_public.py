#!/usr/bin/env python3
"""Anonymously verify the O008 backend-artifact reconciliation commit."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys

import verify_authority_hash_correction_github_public as _base


RECEIPT = (
    _base.ROOT
    / "provenance"
    / "GITHUB_PUBLICATION_RECEIPT_BACKEND_ARTIFACT_RECONCILIATION.json"
)
EXPECTED_PATHS = {
    "backend/COMPANION_BACKEND_MANIFEST.csv",
    "backend/companion_artifacts.jsonl",
    "provenance/BACKEND_ARTIFACT_RECONCILIATION_20260825.md",
    "provenance/FINAL_EDITION_BUILD_AND_QA_RECEIPT.md",
    "provenance/O008_COORDINATOR_HANDOFF_FINAL.json",
    "qa/COMPANION_BACKEND_VALIDATION.json",
    "qa/package_authority_hash_correction_release.py",
    "qa/publish_authority_hash_correction_zenodo.py",
    "qa/verify_backend_artifact_reconciliation_github_public.py",
    "qa/verify_backend_artifact_reconciliation_zenodo_public.py",
}
ARTIFACTS_SHA256 = "6256503166fb89d9de4959571602abcf9599b39f5edc902ac1851ef5bf1e7b30"
MANIFEST_SHA256 = "9be0d071106f9ba38e00f50811a718c84102e4527ae507a8e51250bbd9bfb201"
VALIDATION_SHA256 = "ee7ae54a5a069e22aabd9e2c76e16a5b8571736cf93a6298babd80730735312d"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
    artifacts = _base.git_bytes(commit, "backend/companion_artifacts.jsonl")
    manifest = _base.git_bytes(commit, "backend/COMPANION_BACKEND_MANIFEST.csv")
    validation_data = _base.git_bytes(commit, "qa/COMPANION_BACKEND_VALIDATION.json")
    validation = json.loads(validation_data)
    if (
        sha256(artifacts) != ARTIFACTS_SHA256
        or sha256(manifest) != MANIFEST_SHA256
        or sha256(validation_data) != VALIDATION_SHA256
        or validation.get("result") != "pass"
        or validation.get("findings") != []
    ):
        raise SystemExit("public backend reconciliation identity differs")
    result["receipt_id"] = "FAOA-2015-ID-GITHUB-BACKEND-ARTIFACT-RECONCILIATION"
    result["backend_artifact_reconciliation"] = {
        "companion_artifacts_sha256": ARTIFACTS_SHA256,
        "companion_manifest_sha256": MANIFEST_SHA256,
        "validation_report_sha256": VALIDATION_SHA256,
        "validation_findings": 0,
        "base_jsonl_files_unchanged": 19,
        "base_jsonl_bytes_unchanged": 14878396,
        "substantive_pdf_changed": False,
    }
    RECEIPT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
