#!/usr/bin/env python3
"""Build the deterministic, complete O008 integrated release bundle.

The human-facing 298-page PDF is uploaded separately.  This packager creates
one compact, resumable archive containing the translated source, both semantic
HTML readers, the base and companion backends, licenses, and bounded QA and
provenance evidence.  Every packaged byte is read from one exact Git commit;
the command never performs a repository-wide status or diff scan.
"""

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
from typing import Any

import package_html_reader_release as BASE_PACKAGE


ROOT = Path(__file__).resolve().parents[1]
RELEASE = "2026.08.25-final-integrated"
PREFIX = f"functional-analysis-erdman-id-{RELEASE}"
PDF_NAME = (
    "analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-"
    "dengan-pendamping.pdf"
)
ZIP_NAME = f"{PREFIX}-source-backend-html.zip"
SUMS_NAME = "SHA256SUMS.txt"
OUTPUT_DIR = ROOT / "qa" / "release-final-integrated"
MAX_RELEASE_BYTES = 500_000_000
ZIP_TIMESTAMP = (2026, 8, 25, 0, 0, 0)

INPUT_SNAPSHOT = "qa/FINAL_COMPANION_INPUT_SNAPSHOT.csv"
BASE_BACKEND_MANIFEST = "backend/BACKEND_MANIFEST.csv"
COMPANION_BACKEND_MANIFEST = "backend/COMPANION_BACKEND_MANIFEST.csv"
BASE_HTML_MANIFEST = "output/html/MANIFEST.csv"
COMPANION_HTML_MANIFEST = "output/html-companion/MANIFEST.csv"

FINAL_QA_FILES = {
    INPUT_SNAPSHOT,
    "qa/FINAL_COMPANION_MASTER_RESULT.json",
    "qa/FINAL_COMPANION_BUILD_RESULT.json",
    "qa/FINAL_COMPANION_COMPONENT_VALIDATION_CONSOLE.txt",
    "qa/FINAL_COMPANION_PDF_SECURITY_NAVIGATION_AUDIT.json",
    "qa/FINAL_COMPANION_RENDER_AUDIT.json",
    "qa/FINAL_COMPANION_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
    "qa/O001_SOLUTION_VALIDATION.json",
    "qa/O001_READER_WORK_VALIDATION.json",
    "qa/COMPACT_SPECTRAL_BRIDGE_VALIDATION.json",
    "qa/COMPANION_BACKEND_VALIDATION.json",
    "qa/HTML_COMPANION_BUILD_RESULT.json",
    "qa/HTML_COMPANION_QA.json",
    "qa/HTML_COMPANION_REPRODUCIBILITY.json",
    "qa/HTML_COMPANION_VISUAL_QA.json",
}
RESUMABLE_FILES = {
    "mastery/README.md",
    "mastery/O001_EXERCISE_INVENTORY.jsonl",
    "mastery/O001_READER_WORK_INVENTORY.jsonl",
    "mastery/O001_SOLUTION_FILE_CONTRACT.md",
    "mastery/O001_READER_WORK_CONTRACT.md",
    "bridge/README.md",
    "html/build_reader.py",
    "html/qa_reader.py",
    "html/build_companion_reader.py",
    "html/qa_companion_reader.py",
    "html/verify_companion_replays.py",
    "qa/build_final_companion_master.py",
    "qa/run_final_companion_build.ps1",
    "qa/audit_final_companion_pdf.py",
    "qa/make_final_companion_render_evidence.py",
    "qa/validate_o001_solutions.py",
    "qa/validate_o001_reader_work.py",
    "qa/validate_compact_spectral_bridge.py",
    "qa/validate_companion_backend.py",
    "qa/package_final_integrated_release.py",
    "qa/publish_final_integrated_zenodo.py",
    "qa/verify_final_integrated_github_public.py",
    "qa/verify_final_integrated_zenodo_public.py",
}
PROVENANCE_FILES = {
    "provenance/SOURCE_AUTHORITY.md",
    "provenance/SOURCE_MANIFEST.csv",
    "provenance/SOURCE_CORRECTIONS.md",
    "provenance/TRANSLATION_MODEL_PROVENANCE.md",
    "provenance/HTML_READER_BUILD_AND_QA_RECEIPT.md",
    "provenance/INDONESIAN_TERMINOLOGY_QA_RECEIPT_20260822.md",
    "provenance/SELF_ADJOINT_TERMINOLOGY_ADJUDICATION.md",
    "provenance/O001_SOURCE_ADJUDICATIONS.json",
    "provenance/FINAL_COMPANION_RENDER_MANIFEST.csv",
    "provenance/FINAL_EDITION_BUILD_AND_QA_RECEIPT.md",
}
STATIC_REQUIRED = (
    set(BASE_PACKAGE.REQUIRED_EXACT)
    | FINAL_QA_FILES
    | RESUMABLE_FILES
    | PROVENANCE_FILES
    | {BASE_HTML_MANIFEST, COMPANION_BACKEND_MANIFEST, COMPANION_HTML_MANIFEST}
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(git: str, commit: str, path: str) -> bytes:
    return subprocess.check_output([git, "-C", str(ROOT), "show", f"{commit}:{path}"])


def unsafe(path: str) -> bool:
    return BASE_PACKAGE.unsafe(path)


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    return info


def csv_rows(data: bytes, required: set[str], label: str) -> list[dict[str, str]]:
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    if not rows or set(rows[0]) != required:
        raise RuntimeError(f"{label} schema differs")
    return rows


def safe_relative(path: str, *, single_component: bool = False) -> None:
    pure = PurePosixPath(path)
    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or ".." in pure.parts
        or (single_component and len(pure.parts) != 1)
    ):
        raise RuntimeError(f"unsafe relative path: {path!r}")


def identity_rows(
    data: bytes, *, path_field: str, label: str, single_component: bool = False
) -> list[dict[str, str]]:
    rows = csv_rows(data, {path_field, "bytes", "sha256"}, label)
    seen: set[str] = set()
    for row in rows:
        path = row[path_field]
        safe_relative(path, single_component=single_component)
        if path in seen or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
            raise RuntimeError(f"{label} contains a duplicate or invalid identity")
        try:
            size = int(row["bytes"])
        except ValueError as exc:
            raise RuntimeError(f"{label} contains a non-integer byte count") from exc
        if size < 0:
            raise RuntimeError(f"{label} contains a negative byte count")
        seen.add(path)
    return rows


def snapshot_paths(snapshot: bytes) -> tuple[set[str], list[dict[str, str]]]:
    rows = identity_rows(snapshot, path_field="relative_path", label="input snapshot")
    return {row["relative_path"] for row in rows}, rows


def backend_paths(
    manifest: bytes, manifest_path: str
) -> tuple[set[str], list[dict[str, str]]]:
    rows = identity_rows(
        manifest,
        path_field="relative_path",
        label=manifest_path,
        single_component=True,
    )
    paths = {f"backend/{row['relative_path']}" for row in rows}
    return paths | {manifest_path}, rows


def html_paths(
    manifest: bytes, root: str
) -> tuple[set[str], list[dict[str, str]]]:
    rows = identity_rows(manifest, path_field="path", label=f"{root}/MANIFEST.csv")
    paths = {f"{root}/{row['path']}" for row in rows}
    return paths | {f"{root}/MANIFEST.csv"}, rows


def verify_identity_rows(
    payload: dict[str, bytes],
    rows: list[dict[str, str]],
    *,
    path_field: str,
    prefix: str = "",
) -> None:
    for row in rows:
        path = f"{prefix}{row[path_field]}"
        try:
            data = payload[path]
        except KeyError as exc:
            raise RuntimeError(f"manifested payload is missing: {path}") from exc
        if int(row["bytes"]) != len(data) or row["sha256"] != sha256(data):
            raise RuntimeError(f"manifest identity differs: {path}")


def inventory_digest(rows: dict[str, tuple[int, str]]) -> str:
    material = "".join(
        f"{path}\0{size}\0{digest}\n"
        for path, (size, digest) in sorted(rows.items())
    ).encode("utf-8")
    return sha256(material)


def verify_companion_html(
    payload: dict[str, bytes], rows: list[dict[str, str]]
) -> dict[str, Any]:
    verify_identity_rows(payload, rows, path_field="path", prefix="output/html-companion/")
    manifest = payload[COMPANION_HTML_MANIFEST]
    inventory_without_manifest = {
        row["path"]: (int(row["bytes"]), row["sha256"]) for row in rows
    }
    inventory_with_manifest = dict(inventory_without_manifest)
    inventory_with_manifest["MANIFEST.csv"] = (len(manifest), sha256(manifest))
    site_hash = inventory_digest(inventory_without_manifest)
    full_hash = inventory_digest(inventory_with_manifest)

    build = json.loads(payload["qa/HTML_COMPANION_BUILD_RESULT.json"])
    qa = json.loads(payload["qa/HTML_COMPANION_QA.json"])
    reproducibility = json.loads(payload["qa/HTML_COMPANION_REPRODUCIBILITY.json"])
    visual = json.loads(payload["qa/HTML_COMPANION_VISUAL_QA.json"])
    if build.get("result") != "pass" or not qa.get("passed"):
        raise RuntimeError("companion HTML build or structural QA did not pass")
    if not reproducibility.get("passed") or not visual.get("passed"):
        raise RuntimeError("companion HTML reproducibility or visual QA did not pass")
    artifacts = build.get("artifacts", {})
    if (
        artifacts.get("manifest_sha256") != sha256(manifest)
        or artifacts.get("site_inventory_sha256") != site_hash
        or artifacts.get("route_map_sha256")
        != sha256(payload["output/html-companion/COMPANION_ROUTES.jsonl"])
        or int(build.get("counts", {}).get("manifested_files", -1)) != len(rows)
        or int(build.get("counts", {}).get("routes", -1)) != 14
        or int(build.get("counts", {}).get("solutions", -1)) != 52
        or int(build.get("counts", {}).get("reader_work", -1)) != 10
        or int(build.get("counts", {}).get("bridge_units", -1)) != 13
    ):
        raise RuntimeError("companion HTML build receipt differs from its exact tree")
    canonical = next(
        (item for item in reproducibility.get("builds", []) if item.get("role") == "canonical"),
        None,
    )
    if (
        not isinstance(canonical, dict)
        or int(canonical.get("files", -1)) != len(rows) + 1
        or int(canonical.get("bytes", -1))
        != sum(size for size, _ in inventory_with_manifest.values())
        or canonical.get("inventory_sha256_including_manifest") != full_hash
    ):
        raise RuntimeError("companion HTML reproducibility identity differs")
    return {
        "files": len(rows) + 1,
        "bytes": sum(size for size, _ in inventory_with_manifest.values()),
        "tree_sha256_excluding_manifest": site_hash,
        "tree_sha256_including_manifest": full_hash,
        "manifest_sha256": sha256(manifest),
        "routes": 14,
    }


def verify_final_qa(
    payload: dict[str, bytes], snapshot_rows_data: list[dict[str, str]]
) -> dict[str, Any]:
    verify_identity_rows(payload, snapshot_rows_data, path_field="relative_path")
    build = json.loads(payload["qa/FINAL_COMPANION_BUILD_RESULT.json"])
    master = json.loads(payload["qa/FINAL_COMPANION_MASTER_RESULT.json"])
    security = json.loads(
        payload["qa/FINAL_COMPANION_PDF_SECURITY_NAVIGATION_AUDIT.json"]
    )
    render = json.loads(payload["qa/FINAL_COMPANION_RENDER_AUDIT.json"])
    solution = json.loads(payload["qa/O001_SOLUTION_VALIDATION.json"])
    reader_work = json.loads(payload["qa/O001_READER_WORK_VALIDATION.json"])
    bridge = json.loads(payload["qa/COMPACT_SPECTRAL_BRIDGE_VALIDATION.json"])
    companion_backend = json.loads(payload["qa/COMPANION_BACKEND_VALIDATION.json"])
    visual_text = payload["qa/FINAL_COMPANION_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"].decode(
        "utf-8-sig"
    )
    pdf = build.get("pdf", {})
    final_master_path = "source/id-ID/functional-analysis-id-complete-with-companions.tex"
    if (
        build.get("schema_version") != "o008.final-companion-build.v1"
        or build.get("result") != "pass"
        or build.get("byte_identical") is not True
        or build.get("inputs_unchanged") is not True
        or int(build.get("input_count", -1)) != len(snapshot_rows_data)
        or int(build.get("pages", -1)) != 298
        or pdf.get("path") != f"output/pdf/{PDF_NAME}"
        or not re.fullmatch(r"[0-9a-f]{64}", str(pdf.get("sha256", "")))
        or int(build.get("component_counts", {}).get("source_exercise_solutions", -1)) != 52
        or int(build.get("component_counts", {}).get("selected_reader_work_solutions", -1)) != 10
        or int(build.get("component_counts", {}).get("bridge_units", -1)) != 13
        or int(build.get("component_counts", {}).get("solution_files", -1)) != 12
        or int(build.get("companion_overfull_box_count", -1)) != 0
    ):
        raise RuntimeError("final integrated PDF build receipt is not an exact pass")
    master_data = payload[final_master_path]
    if (
        master.get("result") != "pass"
        or master.get("output_path") != final_master_path
        or int(master.get("output_bytes", -1)) != len(master_data)
        or master.get("output_sha256") != sha256(master_data)
        or int(master.get("explicit_exercise_solution_count", -1)) != 52
        or int(master.get("selected_reader_work_count", -1)) != 10
        or int(master.get("solution_component_count", -1)) != 12
    ):
        raise RuntimeError("final integrated TeX master receipt differs")
    if (
        security.get("status") != "pass"
        or security.get("failures") != []
        or int(security.get("pages", -1)) != 298
        or security.get("pdf", {}).get("sha256") != pdf.get("sha256")
        or render.get("schema_version") != "o008.final-companion-render-audit.v1"
        or int(render.get("page_count", -1)) != 298
        or render.get("pdf", {}).get("sha256") != pdf.get("sha256")
        or "Status: **pass**" not in visual_text
        or "Physical pages: 298" not in visual_text
        or str(pdf.get("sha256")) not in visual_text
    ):
        raise RuntimeError("final PDF security, render, or visual evidence differs")
    checks = (
        (solution, "result", "pass", "O001 solution validation"),
        (reader_work, "result", "pass", "reader-work validation"),
        (bridge, "result", "pass", "compact-spectral bridge validation"),
        (companion_backend, "result", "pass", "companion backend validation"),
    )
    for report, key, expected, label in checks:
        if report.get(key) != expected or report.get("findings") not in (None, []):
            raise RuntimeError(f"{label} did not pass cleanly")
    if (
        int(solution.get("parsed_solutions", -1)) != 52
        or int(reader_work.get("parsed_records", -1)) != 10
        or int(bridge.get("stable_id_count", -1)) != 13
    ):
        raise RuntimeError("final companion component census differs")
    return {
        "pages": 298,
        "pdf_bytes": int(pdf["bytes"]),
        "pdf_sha256": str(pdf["sha256"]),
        "input_files": len(snapshot_rows_data),
        "exercise_solutions": 52,
        "selected_reader_work": 10,
        "bridge_units": 13,
    }


def private_path_markers() -> tuple[bytes, ...]:
    # Construct these markers numerically so this source can safely scan itself.
    return (
        bytes((67, 58, 47, 85, 115, 101, 114, 115, 47)),
        bytes((99, 58, 47, 117, 115, 101, 114, 115, 47)),
        bytes((67, 58, 92, 85, 115, 101, 114, 115, 92)),
        bytes((99, 58, 92, 117, 115, 101, 114, 115, 92)),
        bytes((102, 105, 108, 101, 58, 47, 47, 47, 67, 58, 47, 85, 115, 101, 114, 115, 47)),
        bytes((47, 104, 111, 109, 101, 47)),
    )


def verify_payload(payload: dict[str, bytes]) -> dict[str, Any]:
    snapshot_set, snapshot_rows_data = snapshot_paths(payload[INPUT_SNAPSHOT])
    base_backend_set, base_backend_rows = BASE_PACKAGE.backend_inventory(
        payload[BASE_BACKEND_MANIFEST]
    )
    companion_backend_set, companion_backend_rows = backend_paths(
        payload[COMPANION_BACKEND_MANIFEST], COMPANION_BACKEND_MANIFEST
    )
    base_html_set, _ = html_paths(payload[BASE_HTML_MANIFEST], "output/html")
    companion_html_set, companion_html_rows = html_paths(
        payload[COMPANION_HTML_MANIFEST], "output/html-companion"
    )
    expected = (
        STATIC_REQUIRED
        | snapshot_set
        | base_backend_set
        | companion_backend_set
        | base_html_set
        | companion_html_set
    )
    if set(payload) != expected:
        missing = sorted(expected - set(payload))
        extra = sorted(set(payload) - expected)
        raise RuntimeError(f"release payload inventory differs; missing={missing}, extra={extra}")
    rejected = sorted(path for path in payload if unsafe(path))
    if rejected:
        raise RuntimeError(f"unsafe or forbidden release paths selected: {rejected}")

    BASE_PACKAGE.verify_backend_manifest(
        {path: payload[path] for path in base_backend_set}, base_backend_rows
    )
    verify_identity_rows(
        payload,
        companion_backend_rows,
        path_field="relative_path",
        prefix="backend/",
    )
    base_files, base_bytes, base_tree = BASE_PACKAGE.verify_site_manifest(payload)
    companion_html = verify_companion_html(payload, companion_html_rows)
    final = verify_final_qa(payload, snapshot_rows_data)

    private_paths = [
        path
        for path, data in payload.items()
        if any(marker in data for marker in private_path_markers())
    ]
    if private_paths:
        raise RuntimeError(f"private absolute path found in release payload: {private_paths}")
    return {
        "final": final,
        "base_html": {"files": base_files, "bytes": base_bytes, "tree_sha256": base_tree},
        "companion_html": companion_html,
        "base_backend_files": len(base_backend_set),
        "companion_backend_files": len(companion_backend_set),
    }


def read_release_archive(
    zip_path: Path,
) -> tuple[dict[str, Any], dict[str, bytes], list[zipfile.ZipInfo]]:
    with zipfile.ZipFile(zip_path, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt ZIP entry: {bad}")
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise RuntimeError("duplicate ZIP entry")
        metadata_name = f"{PREFIX}/RELEASE_METADATA.json"
        manifest_name = f"{PREFIX}/RELEASE_MANIFEST.csv"
        if metadata_name not in names or manifest_name not in names:
            raise RuntimeError("release ZIP lacks its metadata/manifest pair")
        metadata = json.loads(archive.read(metadata_name))
        rows = identity_rows(
            archive.read(manifest_name), path_field="path", label="release manifest"
        )
        payload: dict[str, bytes] = {}
        for row in rows:
            path = row["path"]
            data = archive.read(f"{PREFIX}/{path}")
            if int(row["bytes"]) != len(data) or row["sha256"] != sha256(data):
                raise RuntimeError(f"release manifest identity differs: {path}")
            payload[path] = data
        expected_names = {
            f"{PREFIX}/{path}" for path in payload
        } | {metadata_name, manifest_name}
        if set(names) != expected_names:
            raise RuntimeError("ZIP entry inventory differs from the release manifest")
    verify_payload(payload)
    return metadata, payload, infos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--git", default="git")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        raise SystemExit("--commit must be an exact lowercase 40-character ID")
    if not re.fullmatch(r"[0-9a-f]{40}", args.tree):
        raise SystemExit("--tree must be an exact lowercase 40-character ID")
    if args.output_dir.resolve() != OUTPUT_DIR.resolve():
        raise SystemExit(f"--output-dir must be the canonical release path: {OUTPUT_DIR}")

    resolved_commit = subprocess.check_output(
        [args.git, "-C", str(ROOT), "rev-parse", "--verify", f"{args.commit}^{{commit}}"],
        text=True,
    ).strip()
    resolved_tree = subprocess.check_output(
        [args.git, "-C", str(ROOT), "rev-parse", "--verify", f"{args.commit}^{{tree}}"],
        text=True,
    ).strip()
    if resolved_commit != args.commit or resolved_tree != args.tree:
        raise SystemExit("supplied commit/tree identity does not resolve exactly")

    # Discover only paths named by exact, commit-resident manifests.
    seeds = {path: git_bytes(args.git, args.commit, path) for path in STATIC_REQUIRED}
    snapshot_set, _ = snapshot_paths(seeds[INPUT_SNAPSHOT])
    base_backend_set, _ = BASE_PACKAGE.backend_inventory(seeds[BASE_BACKEND_MANIFEST])
    companion_backend_set, _ = backend_paths(
        seeds[COMPANION_BACKEND_MANIFEST], COMPANION_BACKEND_MANIFEST
    )
    base_html_set, _ = html_paths(seeds[BASE_HTML_MANIFEST], "output/html")
    companion_html_set, _ = html_paths(
        seeds[COMPANION_HTML_MANIFEST], "output/html-companion"
    )
    selected = sorted(
        STATIC_REQUIRED
        | snapshot_set
        | base_backend_set
        | companion_backend_set
        | base_html_set
        | companion_html_set
    )
    payload = {
        path: seeds[path] if path in seeds else git_bytes(args.git, args.commit, path)
        for path in selected
    }
    contract = verify_payload(payload)

    # Bind the live final reader to both the commit and the admitted build receipt.
    pdf_path = ROOT / "output" / "pdf" / PDF_NAME
    if not pdf_path.is_file():
        raise SystemExit(f"missing final PDF reader: {pdf_path}")
    pdf_data = pdf_path.read_bytes()
    final = contract["final"]
    if (
        len(pdf_data) != final["pdf_bytes"]
        or sha256(pdf_data) != final["pdf_sha256"]
        or pdf_data != git_bytes(args.git, args.commit, f"output/pdf/{PDF_NAME}")
    ):
        raise SystemExit("final PDF differs from its build receipt or supplied commit")
    for row in snapshot_paths(payload[INPUT_SNAPSHOT])[1]:
        path = row["relative_path"]
        disk = ROOT / path
        if not disk.is_file() or disk.read_bytes() != payload[path]:
            raise SystemExit(f"worktree final input differs from supplied commit: {path}")

    for root_name in ("output/html", "output/html-companion"):
        expected = {path for path in payload if path.startswith(f"{root_name}/")}
        disk_paths = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / root_name).rglob("*")
            if path.is_file()
        }
        if disk_paths != expected:
            raise SystemExit(f"worktree {root_name} inventory differs from supplied commit")
        for path in expected:
            if (ROOT / path).read_bytes() != payload[path]:
                raise SystemExit(f"worktree HTML byte mismatch: {path}")

    manifest_stream = io.StringIO(newline="")
    writer = csv.writer(manifest_stream, lineterminator="\n")
    writer.writerow(["path", "bytes", "sha256"])
    for path in selected:
        data = payload[path]
        writer.writerow([path, len(data), sha256(data)])
    release_manifest = manifest_stream.getvalue().encode("utf-8")
    metadata = json.dumps(
        {
            "schema_version": "o008.release-final-integrated.v1",
            "release": RELEASE,
            "overall_status": "complete",
            "source_text_status": "complete",
            "semantic_html_status": "complete",
            "mastery_solution_status": "complete",
            "selected_reader_work_status": "complete",
            "compact_spectral_svd_bridge_status": "complete",
            "companion_html_status": "complete",
            "remaining_components": [],
            "scope": (
                "complete Indonesian edition: full 17-chapter source text, bibliography, "
                "translated index, all 52 source-exercise solutions, 10 selected reader-work "
                "solutions, 13-unit compact-spectral/SVD bridge, and both semantic HTML readers"
            ),
            "git_commit": args.commit,
            "git_tree": args.tree,
            "license": "CC BY-SA 4.0",
            "primary_reader_uploaded_separately": PDF_NAME,
            "primary_reader_pages": 298,
            "primary_reader_bytes": len(pdf_data),
            "primary_reader_sha256": sha256(pdf_data),
            "source_exercise_solutions": 52,
            "selected_reader_work_solutions": 10,
            "compact_spectral_svd_bridge_units": 13,
            "source_html": contract["base_html"],
            "companion_html": contract["companion_html"],
            "base_backend_manifest_sha256": sha256(payload[BASE_BACKEND_MANIFEST]),
            "companion_backend_manifest_sha256": sha256(
                payload[COMPANION_BACKEND_MANIFEST]
            ),
            "required_upstream_build_component": "source/id-ID/DIAGXY.TEX",
            "excluded_components": sorted(BASE_PACKAGE.FORBIDDEN_COMPONENTS),
            "component_rights_note": (
                "Erdman adaptation is CC BY-SA 4.0; separately authored O001 mastery, "
                "bridge, backend, and accessibility components retain explicit compatible "
                "provenance; no endorsement is implied"
            ),
            "file_count_excluding_generated_inventory": len(payload),
            "expanded_file_bytes_excluding_generated_inventory": sum(
                len(data) for data in payload.values()
            ),
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8") + b"\n"
    expanded = sum(len(data) for data in payload.values()) + len(release_manifest) + len(metadata)
    if expanded + len(pdf_data) > MAX_RELEASE_BYTES:
        raise SystemExit("expanded release payload exceeds the 500,000,000-byte cap")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OUTPUT_DIR / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in selected:
            archive.writestr(zip_info(f"{PREFIX}/{path}"), payload[path])
        archive.writestr(zip_info(f"{PREFIX}/RELEASE_MANIFEST.csv"), release_manifest)
        archive.writestr(zip_info(f"{PREFIX}/RELEASE_METADATA.json"), metadata)

    archived_metadata, _, infos = read_release_archive(zip_path)
    if archived_metadata != json.loads(metadata):
        raise SystemExit("ZIP metadata readback differs")
    zip_data = zip_path.read_bytes()
    if len(pdf_data) + len(zip_data) > MAX_RELEASE_BYTES:
        raise SystemExit("compressed release payload exceeds the 500,000,000-byte cap")
    sums = (
        f"{sha256(pdf_data)}  {PDF_NAME}\n"
        f"{sha256(zip_data)}  {ZIP_NAME}\n"
    ).encode("ascii")
    sums_path = OUTPUT_DIR / SUMS_NAME
    sums_path.write_bytes(sums)

    result = {
        "result": "pass",
        "release": RELEASE,
        "overall_status": "complete",
        "commit": args.commit,
        "tree": args.tree,
        "archive_entries": len(infos),
        "tracked_payload_files": len(payload),
        "expanded_tracked_bytes": sum(len(data) for data in payload.values()),
        "final_pdf": {
            "filename": PDF_NAME,
            "pages": 298,
            "bytes": len(pdf_data),
            "sha256": sha256(pdf_data),
        },
        "archive": {
            "filename": ZIP_NAME,
            "bytes": len(zip_data),
            "sha256": sha256(zip_data),
        },
        "checksums": {
            "filename": SUMS_NAME,
            "bytes": len(sums),
            "sha256": sha256(sums),
        },
        "source_html": contract["base_html"],
        "companion_html": contract["companion_html"],
        "commit_tree_verified": True,
        "reader_matches_commit_and_build_receipt": True,
        "html_worktrees_match_commit": True,
        "private_absolute_paths": 0,
        "forbidden_entries": 0,
        "all_entry_streams_read": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
