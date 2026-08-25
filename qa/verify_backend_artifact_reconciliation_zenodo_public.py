#!/usr/bin/env python3
"""Anonymously verify the O008 backend-artifact reconciliation on Zenodo."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys

import package_authority_hash_correction_release as package
import verify_authority_hash_correction_zenodo_public as _base


RECEIPT = (
    package.ROOT
    / "provenance"
    / "ZENODO_PUBLICATION_RECEIPT_BACKEND_ARTIFACT_RECONCILIATION.json"
)
ARTIFACTS_SHA256 = "6256503166fb89d9de4959571602abcf9599b39f5edc902ac1851ef5bf1e7b30"
MANIFEST_SHA256 = "9be0d071106f9ba38e00f50811a718c84102e4527ae507a8e51250bbd9bfb201"
VALIDATION_SHA256 = "ee7ae54a5a069e22aabd9e2c76e16a5b8571736cf93a6298babd80730735312d"
CONSOLE_SHA256 = "874ea2a4da664f01be45152bc9dbaa1e15333608d7badc82df7082226e523d29"
BOUND_ARTIFACTS = {
    "qa/FINAL_COMPANION_BUILD_RESULT.json": (
        1935,
        "5719f9a726fb5a411a7b76879058ad7e14c155717130ad5e8c4672c941c591df",
    ),
    "qa/FINAL_COMPANION_INPUT_SNAPSHOT.csv": (
        4113,
        "322799f519043092002ad61fbf3f38367cf15004f5d43304b976187c3769d869",
    ),
    "qa/FINAL_COMPANION_COMPONENT_VALIDATION_CONSOLE.txt": (4330, CONSOLE_SHA256),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    _base.RECEIPT = RECEIPT
    if any(argument in {"-h", "--help"} for argument in sys.argv[1:]):
        _base.main()
        return
    _, payload, _ = package.read_release_archive(package.OUTPUT_DIR / package.ZIP_NAME)
    artifacts = payload["backend/companion_artifacts.jsonl"]
    manifest = payload["backend/COMPANION_BACKEND_MANIFEST.csv"]
    validation_data = payload["qa/COMPANION_BACKEND_VALIDATION.json"]
    validation = json.loads(validation_data)
    records = {
        record["path"]: record
        for record in (
            json.loads(line) for line in artifacts.decode("utf-8").splitlines()
        )
    }
    bindings = []
    for path, (expected_bytes, expected_sha256) in sorted(BOUND_ARTIFACTS.items()):
        data = payload[path]
        record = records.get(path)
        if (
            len(data) != expected_bytes
            or sha256(data) != expected_sha256
            or not isinstance(record, dict)
            or int(record.get("bytes", -1)) != expected_bytes
            or record.get("sha256") != expected_sha256
        ):
            raise SystemExit(f"packaged artifact binding differs: {path}")
        bindings.append(
            {"path": path, "bytes": expected_bytes, "sha256": expected_sha256}
        )
    if (
        sha256(artifacts) != ARTIFACTS_SHA256
        or sha256(manifest) != MANIFEST_SHA256
        or sha256(validation_data) != VALIDATION_SHA256
        or validation.get("result") != "pass"
        or validation.get("findings") != []
    ):
        raise SystemExit("packaged backend reconciliation identity differs")

    with contextlib.redirect_stdout(io.StringIO()):
        _base.main()
    result = json.loads(RECEIPT.read_text(encoding="utf-8"))
    result["receipt_id"] = "FAOA-2015-ID-ZENODO-BACKEND-ARTIFACT-RECONCILIATION"
    result["backend_artifact_reconciliation"] = {
        "companion_artifacts_sha256": ARTIFACTS_SHA256,
        "companion_manifest_sha256": MANIFEST_SHA256,
        "validation_report_sha256": VALIDATION_SHA256,
        "exact_packaged_artifact_bindings": bindings,
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
