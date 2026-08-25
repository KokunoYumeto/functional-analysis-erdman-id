#!/usr/bin/env python3
"""Validate the additive O001/O008 companion backend and replay it exactly."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
REPORT = ROOT / "qa" / "COMPANION_BACKEND_VALIDATION.json"
GENERATOR = BACKEND / "generate_companion_backend.py"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
BASE_MANIFEST_SHA256 = "06ad5f9c6931ef1838a8307c60b8b3b94a4c89a25d6ddc12dbfb2a3ddc591cfc"
ORIGINAL_RIGHTS_ID = "RIGHTS-ORIGINAL-CC-BY-SA-4.0"

ROOT_COMPONENT = "O008-FAOA-2015-COMPANION"
EXERCISE_COMPONENT = "O001-FAOA-2015-EXERCISE-SOLUTIONS"
READER_WORK_COMPONENT = "O001-FAOA-2015-READER-WORK-SOLUTIONS"
BRIDGE_COMPONENT = "O008-FAOA-2015-COMPACT-SPECTRAL-SVD-BRIDGE"

EXERCISE_PROVENANCE = "PROV-O001-FAOA-2015-EXERCISE-SOLUTIONS"
READER_WORK_PROVENANCE = "PROV-O001-FAOA-2015-READER-WORK-SOLUTIONS"
BRIDGE_PROVENANCE = "PROV-O008-FAOA-2015-COMPACT-SPECTRAL-SVD-BRIDGE"
EDITION_PROVENANCE = "PROV-O008-FAOA-2015-COMPANION-EDITION"

PDF_SURFACE = "O008-FAOA-2015-COMPANION-PDF"
HTML_SURFACE = "O008-FAOA-2015-COMPANION-HTML"

GENERATED_NAMES = (
    "companion_schema.json",
    "companion_components.jsonl",
    "companion_provenance.jsonl",
    "o001_mastery.jsonl",
    "o001_status.jsonl",
    "bridge_units.jsonl",
    "companion_surfaces.jsonl",
    "companion_html_routes.jsonl",
    "companion_relations.jsonl",
    "companion_artifacts.jsonl",
    "COMPANION_BACKEND_MANIFEST.csv",
)

EXPECTED_BRIDGE_IDS = [
    "O008-BRIDGE-CS-DEF-001",
    "O008-BRIDGE-CS-THM-001",
    "O008-BRIDGE-CS-REM-001",
    "O008-BRIDGE-CS-EXAM-001",
    "O008-BRIDGE-CS-LEM-001",
    "O008-BRIDGE-CS-LEM-002",
    "O008-BRIDGE-CS-THM-002",
    "O008-BRIDGE-CS-COR-001",
    "O008-BRIDGE-CS-DEF-002",
    "O008-BRIDGE-CS-THM-003",
    "O008-BRIDGE-CS-COR-002",
    "O008-BRIDGE-CS-PROP-001",
    "O008-BRIDGE-CS-EXAM-002",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            raise RuntimeError(f"blank JSONL row in {rel(path)}:{number}")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"non-object JSONL row in {rel(path)}:{number}")
        rows.append(value)
    return rows


def finding(findings: list[dict[str, Any]], code: str, **evidence: Any) -> None:
    findings.append({"code": code, **evidence})


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def inventory_digest(rows: list[tuple[str, int, str]]) -> str:
    material = "".join(
        f"{path}\0{size}\0{digest}\n" for path, size, digest in sorted(rows)
    ).encode("utf-8")
    return sha256(material)


def check_base_lock(findings: list[dict[str, Any]]) -> tuple[int, int]:
    manifest_path = BACKEND / "BACKEND_MANIFEST.csv"
    manifest_raw = manifest_path.read_bytes()
    actual_manifest_hash = sha256(manifest_raw)
    if actual_manifest_hash != BASE_MANIFEST_SHA256:
        finding(
            findings,
            "BASE_MANIFEST_CHANGED",
            expected=BASE_MANIFEST_SHA256,
            actual=actual_manifest_hash,
        )
        return 0, 0
    rows = read_manifest(manifest_path)
    locked = 0
    locked_bytes = 0
    for row in rows:
        path_string = row["relative_path"]
        if not path_string.endswith(".jsonl"):
            continue
        path = BACKEND / path_string
        raw = path.read_bytes()
        locked += 1
        locked_bytes += len(raw)
        if len(raw) != int(row["bytes"]) or sha256(raw) != row["sha256"]:
            finding(
                findings,
                "ADMITTED_BASE_JSONL_CHANGED",
                path=f"backend/{path_string}",
                expected_bytes=int(row["bytes"]),
                actual_bytes=len(raw),
                expected_sha256=row["sha256"],
                actual_sha256=sha256(raw),
            )
    return locked, locked_bytes


def check_companion_manifest(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    path = BACKEND / "COMPANION_BACKEND_MANIFEST.csv"
    rows = read_manifest(path)
    expected_paths = {
        "bridge_units.jsonl",
        "companion_artifacts.jsonl",
        "companion_components.jsonl",
        "companion_provenance.jsonl",
        "companion_relations.jsonl",
        "companion_schema.json",
        "companion_surfaces.jsonl",
        "companion_html_routes.jsonl",
        "generate_companion_backend.py",
        "o001_mastery.jsonl",
        "o001_status.jsonl",
    }
    actual_paths = {row["relative_path"] for row in rows}
    if actual_paths != expected_paths:
        finding(
            findings,
            "COMPANION_MANIFEST_CLOSURE",
            missing=sorted(expected_paths - actual_paths),
            extra=sorted(actual_paths - expected_paths),
        )
    inventory: list[dict[str, Any]] = []
    for row in rows:
        name = row["relative_path"]
        current = BACKEND / name
        raw = current.read_bytes()
        actual = {"path": f"backend/{name}", "bytes": len(raw), "sha256": sha256(raw)}
        inventory.append(actual)
        if len(raw) != int(row["bytes"]) or sha256(raw) != row["sha256"]:
            finding(
                findings,
                "COMPANION_MANIFEST_MISMATCH",
                **actual,
                expected_bytes=int(row["bytes"]),
                expected_sha256=row["sha256"],
            )
    return inventory


def replay_generator(findings: list[dict[str, Any]]) -> None:
    with tempfile.TemporaryDirectory(prefix="o008-companion-backend-replay-") as temp:
        scratch = Path(temp)
        process = subprocess.run(
            [sys.executable, str(GENERATOR), "--output-dir", str(scratch)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            finding(
                findings,
                "GENERATOR_REPLAY_FAILED",
                exit_code=process.returncode,
                stderr=process.stderr[-2000:],
            )
            return
        for name in GENERATED_NAMES:
            expected = (BACKEND / name).read_bytes()
            replayed = (scratch / name).read_bytes()
            if replayed != expected:
                finding(
                    findings,
                    "GENERATOR_REPLAY_BYTE_MISMATCH",
                    path=f"backend/{name}",
                    expected_sha256=sha256(expected),
                    replay_sha256=sha256(replayed),
                )


def main() -> None:
    findings: list[dict[str, Any]] = []
    base_jsonl_files_locked, base_jsonl_bytes_locked = check_base_lock(findings)
    generated_inventory = check_companion_manifest(findings)

    schema = json.loads((BACKEND / "companion_schema.json").read_text(encoding="utf-8"))
    if schema.get("base_backend_manifest_sha256") != BASE_MANIFEST_SHA256:
        finding(findings, "SCHEMA_BASE_LOCK_MISMATCH")
    if schema.get("write_policy") != "additive overlay; admitted base backend files are read-only":
        finding(findings, "SCHEMA_WRITE_POLICY_MISMATCH")
    if schema.get("state_policy", {}).get("admission_state") != "admitted":
        finding(findings, "SCHEMA_ADMISSION_STATE")

    components = load_jsonl(BACKEND / "companion_components.jsonl")
    provenance = load_jsonl(BACKEND / "companion_provenance.jsonl")
    mastery = load_jsonl(BACKEND / "o001_mastery.jsonl")
    statuses = load_jsonl(BACKEND / "o001_status.jsonl")
    bridge = load_jsonl(BACKEND / "bridge_units.jsonl")
    surfaces = load_jsonl(BACKEND / "companion_surfaces.jsonl")
    html_routes = load_jsonl(BACKEND / "companion_html_routes.jsonl")
    relations = load_jsonl(BACKEND / "companion_relations.jsonl")
    artifacts = load_jsonl(BACKEND / "companion_artifacts.jsonl")

    expected_counts = {
        "components": 4,
        "provenance": 4,
        "exercise_solutions": 52,
        "reader_work_solutions": 10,
        "exercise_status_overlays": 52,
        "bridge_units": 13,
        "surfaces": 2,
        "html_routes": 294,
        "relations": 826,
        "artifacts": 70,
    }
    mastery_types = Counter(str(row["record_type"]) for row in mastery)
    actual_counts = {
        "components": len(components),
        "provenance": len(provenance),
        "exercise_solutions": mastery_types["o001_exercise_solution"],
        "reader_work_solutions": mastery_types["o001_reader_work_solution"],
        "exercise_status_overlays": len(statuses),
        "bridge_units": len(bridge),
        "surfaces": len(surfaces),
        "html_routes": len(html_routes),
        "relations": len(relations),
        "artifacts": len(artifacts),
    }
    for key, expected in expected_counts.items():
        if expected >= 0 and actual_counts[key] != expected:
            finding(
                findings,
                "RECORD_COUNT",
                record_set=key,
                expected=expected,
                actual=actual_counts[key],
            )

    component_ids = [str(row["id"]) for row in components]
    expected_component_ids = [
        ROOT_COMPONENT,
        EXERCISE_COMPONENT,
        READER_WORK_COMPONENT,
        BRIDGE_COMPONENT,
    ]
    if component_ids != expected_component_ids:
        finding(
            findings,
            "COMPONENT_ID_ORDER",
            expected=expected_component_ids,
            actual=component_ids,
        )
    provenance_ids = [str(row["id"]) for row in provenance]
    expected_provenance_ids = [
        EDITION_PROVENANCE,
        EXERCISE_PROVENANCE,
        READER_WORK_PROVENANCE,
        BRIDGE_PROVENANCE,
    ]
    if provenance_ids != expected_provenance_ids:
        finding(
            findings,
            "PROVENANCE_ID_ORDER",
            expected=expected_provenance_ids,
            actual=provenance_ids,
        )
    for row in provenance:
        for field, expected in (
            ("creation_agent", MODEL),
            ("creation_direction", "at_user_direction"),
            ("source_author_credit_preserved", "John M. Erdman"),
        ):
            if row.get(field) != expected:
                finding(
                    findings,
                    "PROVENANCE_FIELD",
                    id=row.get("id"),
                    field=field,
                    expected=expected,
                    actual=row.get(field),
                )
        if "not authored or endorsed" not in str(row.get("nonendorsement", "")).lower():
            finding(findings, "PROVENANCE_NONENDORSEMENT", id=row.get("id"))
        if row["id"] == EDITION_PROVENANCE:
            if row.get("rights_ids") != ["RIGHTS-ERDMAN-CC-BY-SA-4.0", ORIGINAL_RIGHTS_ID]:
                finding(findings, "EDITION_PROVENANCE_RIGHTS")
        elif row.get("rights_id") != ORIGINAL_RIGHTS_ID:
            finding(findings, "PROVENANCE_RIGHTS", id=row.get("id"))

    for record_set in (
        components,
        provenance,
        mastery,
        statuses,
        bridge,
        surfaces,
        html_routes,
        artifacts,
    ):
        for row in record_set:
            if row.get("admission_state") != "admitted":
                finding(
                    findings,
                    "NONADMITTED_OVERLAY_RECORD",
                    id=row.get("id"),
                    state=row.get("admission_state"),
                )

    base_manifest_rows = read_manifest(BACKEND / "BACKEND_MANIFEST.csv")
    base_endpoints: set[str] = set()
    for manifest_row in base_manifest_rows:
        name = manifest_row["relative_path"]
        if not name.endswith(".jsonl"):
            continue
        for row in load_jsonl(BACKEND / name):
            if "id" in row:
                base_endpoints.add(str(row["id"]))

    overlay_record_sets = (
        components,
        provenance,
        mastery,
        statuses,
        bridge,
        surfaces,
        html_routes,
        relations,
        artifacts,
    )
    overlay_ids = [str(row["id"]) for rows in overlay_record_sets for row in rows]
    if len(overlay_ids) != len(set(overlay_ids)):
        duplicates = sorted(key for key, count in Counter(overlay_ids).items() if count > 1)
        finding(findings, "DUPLICATE_OVERLAY_ID", ids=duplicates)
    collisions = sorted(set(overlay_ids) & base_endpoints)
    if collisions:
        finding(findings, "OVERLAY_ID_COLLIDES_WITH_BASE", ids=collisions)
    all_endpoints = base_endpoints | set(overlay_ids)
    relation_ids = [str(row["id"]) for row in relations]
    expected_relation_ids = [
        f"O008-COMPANION-REL-{number:04d}" for number in range(1, len(relations) + 1)
    ]
    if relation_ids != expected_relation_ids:
        finding(findings, "RELATION_ID_SEQUENCE")
    for row in relations:
        for endpoint_field in ("from_id", "to_id"):
            endpoint = str(row[endpoint_field])
            if endpoint not in all_endpoints:
                finding(
                    findings,
                    "UNRESOLVED_RELATION_ENDPOINT",
                    relation_id=row["id"],
                    field=endpoint_field,
                    endpoint=endpoint,
                )
    edges = {
        (str(row["from_id"]), str(row["relation_type"]), str(row["to_id"]))
        for row in relations
    }

    exercise_inventory = load_jsonl(ROOT / "mastery" / "O001_EXERCISE_INVENTORY.jsonl")
    exercise_by_solution = {
        str(row["id"]): row
        for row in mastery
        if row["record_type"] == "o001_exercise_solution"
    }
    status_by_solution = {str(row["solution_id"]): row for row in statuses}
    base_support_rows = load_jsonl(BACKEND / "exercise_support.jsonl")
    base_support_by_id = {str(row["id"]): row for row in base_support_rows}
    for inventory_row in exercise_inventory:
        solution_id = str(inventory_row["solution_id"])
        solution = exercise_by_solution.get(solution_id)
        status = status_by_solution.get(solution_id)
        if solution is None or status is None:
            finding(findings, "EXERCISE_OVERLAY_MISSING", solution_id=solution_id)
            continue
        expected_fields = {
            "exercise_unit_id": inventory_row["exercise_unit_id"],
            "support_id": inventory_row["support_id"],
            "statement_target_fragment_sha256": inventory_row[
                "statement_target_fragment_sha256"
            ],
            "statement_source_fragment_sha256": inventory_row[
                "statement_source_fragment_sha256"
            ],
            "source_exercise_order": inventory_row["source_exercise_order"],
            "rights_id": ORIGINAL_RIGHTS_ID,
            "model_provenance": MODEL,
        }
        for field, expected in expected_fields.items():
            if solution.get(field) != expected:
                finding(
                    findings,
                    "EXERCISE_BINDING_FIELD",
                    solution_id=solution_id,
                    field=field,
                    expected=expected,
                    actual=solution.get(field),
                )
        support_id = str(inventory_row["support_id"])
        if support_id not in base_support_by_id:
            finding(findings, "BASE_SUPPORT_MISSING", support_id=support_id)
        if status.get("base_support_id") != support_id:
            finding(findings, "STATUS_SUPPORT_BINDING", solution_id=solution_id)
        if status.get("effective_original_solution_state") != "admitted_in_companion_readers":
            finding(findings, "STATUS_EFFECTIVE_STATE", solution_id=solution_id)
        if solution.get("validation_state") != "integrated_pdf_html_passed":
            finding(findings, "EXERCISE_INTEGRATED_STATE", solution_id=solution_id)
        if status.get("validation_state") != "integrated_pdf_html_passed":
            finding(findings, "STATUS_INTEGRATED_STATE", solution_id=solution_id)
        required_edges = {
            (EXERCISE_COMPONENT, "contains_solution", solution_id),
            (solution_id, "solves", str(inventory_row["exercise_unit_id"])),
            (str(status["id"]), "overlays_support", support_id),
            (str(status["id"]), "reports_solution", solution_id),
        }
        for edge in sorted(required_edges):
            if edge not in edges:
                finding(findings, "MISSING_EXERCISE_RELATION", edge=list(edge))
        for hint in inventory_row["upstream_hint_records"]:
            edge = (solution_id, "uses_source_hint", str(hint["hint_unit_id"]))
            if edge not in edges:
                finding(findings, "MISSING_EXERCISE_HINT_RELATION", edge=list(edge))

    reader_inventory = load_jsonl(ROOT / "mastery" / "O001_READER_WORK_INVENTORY.jsonl")
    reader_by_solution = {
        str(row["id"]): row
        for row in mastery
        if row["record_type"] == "o001_reader_work_solution"
    }
    for inventory_row in reader_inventory:
        solution_id = str(inventory_row["solution_id"])
        solution = reader_by_solution.get(solution_id)
        if solution is None:
            finding(findings, "READER_WORK_OVERLAY_MISSING", solution_id=solution_id)
            continue
        expected_fields = {
            "result_unit_id": inventory_row["result_unit_id"],
            "upstream_hint_unit_id": inventory_row["upstream_hint_unit_id"],
            "result_target_fragment_sha256": inventory_row[
                "result_target_fragment_sha256"
            ],
            "upstream_hint_target_fragment_sha256": inventory_row[
                "upstream_hint_target_fragment_sha256"
            ],
            "rights_id": ORIGINAL_RIGHTS_ID,
            "model_provenance": MODEL,
        }
        for field, expected in expected_fields.items():
            if solution.get(field) != expected:
                finding(
                    findings,
                    "READER_WORK_BINDING_FIELD",
                    solution_id=solution_id,
                    field=field,
                    expected=expected,
                    actual=solution.get(field),
                )
        required_edges = {
            (READER_WORK_COMPONENT, "contains_solution", solution_id),
            (solution_id, "completes_source_proof", str(inventory_row["result_unit_id"])),
            (solution_id, "uses_source_hint", str(inventory_row["upstream_hint_unit_id"])),
        }
        for edge in sorted(required_edges):
            if edge not in edges:
                finding(findings, "MISSING_READER_WORK_RELATION", edge=list(edge))
        if solution.get("validation_state") != "integrated_pdf_html_passed":
            finding(findings, "READER_WORK_INTEGRATED_STATE", solution_id=solution_id)

    bridge_ids = [str(row["id"]) for row in bridge]
    if bridge_ids != EXPECTED_BRIDGE_IDS:
        finding(
            findings,
            "BRIDGE_ID_ORDER",
            expected=EXPECTED_BRIDGE_IDS,
            actual=bridge_ids,
        )
    bridge_labels = [row["label"] for row in bridge if row.get("label")]
    if len(bridge_labels) != len(set(bridge_labels)):
        finding(findings, "DUPLICATE_BRIDGE_LABEL")
    for order, row in enumerate(bridge, 1):
        if row.get("order_in_component") != order:
            finding(findings, "BRIDGE_ORDER", id=row.get("id"), expected=order)
        for field, expected in (
            ("component_id", BRIDGE_COMPONENT),
            ("rights_id", ORIGINAL_RIGHTS_ID),
            ("provenance_id", BRIDGE_PROVENANCE),
            ("model_provenance", MODEL),
        ):
            if row.get(field) != expected:
                finding(findings, "BRIDGE_FIELD", id=row.get("id"), field=field)
        if row.get("validation_state") != "integrated_pdf_html_passed":
            finding(findings, "BRIDGE_INTEGRATED_STATE", id=row.get("id"))
        edge = (BRIDGE_COMPONENT, "contains_bridge_unit", str(row["id"]))
        if edge not in edges:
            finding(findings, "MISSING_BRIDGE_CONTAINS_RELATION", edge=list(edge))
    for chapter_id in (
        "FAOA-2015-CH04",
        "FAOA-2015-CH07",
        "FAOA-2015-CH08",
        "FAOA-2015-CH11",
        "FAOA-2015-CH15",
    ):
        edge = (BRIDGE_COMPONENT, "requires_chapter", chapter_id)
        if edge not in edges:
            finding(findings, "MISSING_BRIDGE_PREREQUISITE", edge=list(edge))

    surface_by_id = {str(row["id"]): row for row in surfaces}
    if [str(row["id"]) for row in surfaces] != [PDF_SURFACE, HTML_SURFACE]:
        finding(findings, "SURFACE_ID_ORDER")
    for surface_id in (PDF_SURFACE, HTML_SURFACE):
        surface = surface_by_id.get(surface_id)
        if surface is None:
            continue
        if surface.get("provenance_id") != EDITION_PROVENANCE:
            finding(findings, "SURFACE_PROVENANCE", surface_id=surface_id)
        if surface.get("rights_ids") != [
            "RIGHTS-ERDMAN-CC-BY-SA-4.0",
            ORIGINAL_RIGHTS_ID,
        ]:
            finding(findings, "SURFACE_RIGHTS", surface_id=surface_id)
        required_edges = {
            (ROOT_COMPONENT, "rendered_as", surface_id),
            (surface_id, "governed_by_provenance", EDITION_PROVENANCE),
            (surface_id, "licensed_under", "RIGHTS-ERDMAN-CC-BY-SA-4.0"),
            (surface_id, "licensed_under", ORIGINAL_RIGHTS_ID),
        }
        for edge in required_edges:
            if edge not in edges:
                finding(findings, "MISSING_SURFACE_RELATION", edge=list(edge))
        for component_id in (EXERCISE_COMPONENT, READER_WORK_COMPONENT, BRIDGE_COMPONENT):
            edge = (component_id, "available_on_surface", surface_id)
            if edge not in edges:
                finding(findings, "MISSING_COMPONENT_SURFACE_RELATION", edge=list(edge))

    pdf_path = (
        ROOT
        / "output"
        / "pdf"
        / "analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf"
    )
    pdf_raw = pdf_path.read_bytes()
    pdf_surface = surface_by_id.get(PDF_SURFACE, {})
    expected_pdf_fields = {
        "path": rel(pdf_path),
        "bytes": len(pdf_raw),
        "sha256": sha256(pdf_raw),
        "pages": 298,
        "surface_kind": "pdf_reader",
        "deterministic_replay": True,
        "pdf_tagging_state": "untagged",
        "accessible_alternative_surface_id": HTML_SURFACE,
    }
    for field, expected in expected_pdf_fields.items():
        if pdf_surface.get(field) != expected:
            finding(
                findings,
                "PDF_SURFACE_FIELD",
                field=field,
                expected=expected,
                actual=pdf_surface.get(field),
            )
    final_build = json.loads(
        (ROOT / "qa" / "FINAL_COMPANION_BUILD_RESULT.json").read_text(encoding="utf-8")
    )
    security = json.loads(
        (ROOT / "qa" / "FINAL_COMPANION_PDF_SECURITY_NAVIGATION_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    render = json.loads(
        (ROOT / "qa" / "FINAL_COMPANION_RENDER_AUDIT.json").read_text(encoding="utf-8")
    )
    if (
        final_build.get("result") != "pass"
        or not final_build.get("byte_identical")
        or final_build.get("companion_overfull_box_count") != 0
        or any(final_build.get("final_log_forbidden_counts", {}).values())
    ):
        finding(findings, "PDF_BUILD_GATE")
    snapshot_path = ROOT / "qa" / "FINAL_COMPANION_INPUT_SNAPSHOT.csv"
    snapshot_rows = read_manifest(snapshot_path)
    snapshot_raw = snapshot_path.read_bytes()
    if (
        len(snapshot_rows) != final_build.get("input_snapshot", {}).get("rows")
        or sha256(snapshot_raw) != final_build.get("input_snapshot", {}).get("sha256")
    ):
        finding(findings, "PDF_INPUT_SNAPSHOT_RECEIPT")
    for snapshot_row in snapshot_rows:
        input_path = ROOT / snapshot_row["relative_path"]
        input_raw = input_path.read_bytes()
        if (
            len(input_raw) != int(snapshot_row["bytes"])
            or sha256(input_raw) != snapshot_row["sha256"]
        ):
            finding(
                findings,
                "PDF_INPUT_SNAPSHOT_STALE",
                path=snapshot_row["relative_path"],
            )
    for receipt_name, receipt_pdf in (
        ("build", final_build.get("pdf", {})),
        ("security", security.get("pdf", {})),
        ("render", render.get("pdf", {})),
    ):
        if receipt_pdf.get("bytes") != len(pdf_raw) or receipt_pdf.get("sha256") != sha256(pdf_raw):
            finding(findings, "PDF_RECEIPT_IDENTITY", receipt=receipt_name)
    if security.get("status") != "pass" or security.get("failures") != []:
        finding(findings, "PDF_SECURITY_GATE")
    if render.get("outer_5px_ink_pages") != [] or render.get("page_count") != 298:
        finding(findings, "PDF_RENDER_GATE")

    html_root = ROOT / "output" / "html-companion"
    html_manifest_path = html_root / "MANIFEST.csv"
    html_manifest_rows = read_manifest(html_manifest_path)
    site_rows: list[tuple[str, int, str]] = []
    expected_site_paths = {"MANIFEST.csv"}
    for row in html_manifest_rows:
        path = html_root / row["path"]
        raw = path.read_bytes()
        expected_site_paths.add(row["path"])
        site_rows.append((row["path"], len(raw), sha256(raw)))
        if len(raw) != int(row["bytes"]) or sha256(raw) != row["sha256"]:
            finding(findings, "HTML_MANIFEST_FILE_IDENTITY", path=row["path"])
    actual_site_paths = {
        path.relative_to(html_root).as_posix()
        for path in html_root.rglob("*")
        if path.is_file()
    }
    if actual_site_paths != expected_site_paths:
        finding(
            findings,
            "HTML_SITE_CLOSURE",
            missing=sorted(expected_site_paths - actual_site_paths),
            extra=sorted(actual_site_paths - expected_site_paths),
        )
    html_manifest_raw = html_manifest_path.read_bytes()
    all_site_rows = site_rows + [
        ("MANIFEST.csv", len(html_manifest_raw), sha256(html_manifest_raw))
    ]
    html_surface = surface_by_id.get(HTML_SURFACE, {})
    expected_html_fields = {
        "directory_path": "output/html-companion",
        "files": 19,
        "bytes": sum(size for _, size, _ in all_site_rows),
        "manifest_sha256": sha256(html_manifest_raw),
        "inventory_sha256_excluding_manifest": inventory_digest(site_rows),
        "inventory_sha256_including_manifest": inventory_digest(all_site_rows),
        "html_documents": 15,
        "routes": 14,
        "route_records": 294,
        "mathml_elements": 2288,
        "exercise_solutions": 52,
        "reader_work_solutions": 10,
        "bridge_units": 13,
        "surface_kind": "semantic_html_reader",
        "math_surface": "native_MathML",
        "deterministic_replay": True,
    }
    for field, expected in expected_html_fields.items():
        if html_surface.get(field) != expected:
            finding(
                findings,
                "HTML_SURFACE_FIELD",
                field=field,
                expected=expected,
                actual=html_surface.get(field),
            )
    html_reports = {
        "build": json.loads(
            (ROOT / "qa" / "HTML_COMPANION_BUILD_RESULT.json").read_text(encoding="utf-8")
        ),
        "machine": json.loads(
            (ROOT / "qa" / "HTML_COMPANION_QA.json").read_text(encoding="utf-8")
        ),
        "repro": json.loads(
            (ROOT / "qa" / "HTML_COMPANION_REPRODUCIBILITY.json").read_text(
                encoding="utf-8"
            )
        ),
        "visual": json.loads(
            (ROOT / "qa" / "HTML_COMPANION_VISUAL_QA.json").read_text(encoding="utf-8")
        ),
    }
    if html_reports["build"].get("result") != "pass":
        finding(findings, "HTML_BUILD_GATE")
    for item in html_reports["build"].get("inputs", []):
        input_path = ROOT / str(item["path"])
        input_raw = input_path.read_bytes()
        if len(input_raw) != int(item["bytes"]) or sha256(input_raw) != item["sha256"]:
            finding(findings, "HTML_BUILD_INPUT_STALE", path=item["path"])
    for name in ("machine", "repro", "visual"):
        if not html_reports[name].get("passed"):
            finding(findings, "HTML_QA_GATE", receipt=name)
    expected_html_artifacts = {
        "manifest_sha256": sha256(html_manifest_raw),
        "route_map_sha256": sha256(
            (html_root / "COMPANION_ROUTES.jsonl").read_bytes()
        ),
        "site_inventory_sha256": inventory_digest(site_rows),
        "site_inventory_sha256_excluding_manifest": inventory_digest(site_rows),
        "inventory_sha256_including_manifest": inventory_digest(all_site_rows),
    }
    for report_name in ("machine", "visual"):
        report_artifacts = html_reports[report_name].get("artifacts", {})
        for key, expected in expected_html_artifacts.items():
            if key in report_artifacts and report_artifacts[key] != expected:
                finding(
                    findings,
                    "HTML_QA_ARTIFACT_IDENTITY",
                    receipt=report_name,
                    field=key,
                    expected=expected,
                    actual=report_artifacts[key],
                )

    source_route_path = html_root / "COMPANION_ROUTES.jsonl"
    source_route_lines = source_route_path.read_text(encoding="utf-8").splitlines()
    if len(source_route_lines) != len(html_routes):
        finding(
            findings,
            "HTML_ROUTE_COUNT",
            source=len(source_route_lines),
            overlay=len(html_routes),
        )
    artifact_by_path = {str(row["path"]): str(row["id"]) for row in artifacts}
    primary_ids = set(exercise_by_solution) | set(reader_by_solution) | set(bridge_ids)
    html_text_cache: dict[str, str] = {}
    for order, (source_line, route) in enumerate(
        zip(source_route_lines, html_routes, strict=False), 1
    ):
        source = json.loads(source_line)
        expected_route_id = f"O008-COMPANION-HTML-ROUTE-{order:04d}"
        expected_output_artifact = artifact_by_path.get(
            f"output/html-companion/{source['output_path']}"
        )
        expected_route_fields = {
            "id": expected_route_id,
            "admission_state": "admitted",
            "surface_id": HTML_SURFACE,
            "route_order": order,
            "target_stable_id": source["id"],
            "href": source["href"],
            "output_path": source["output_path"],
            "route": source["route"],
            "locale": source["locale"],
            "route_map_line_sha256": sha256(source_line.encode("utf-8")),
            "output_artifact_id": expected_output_artifact,
        }
        for field, expected in expected_route_fields.items():
            if route.get(field) != expected:
                finding(
                    findings,
                    "HTML_ROUTE_FIELD",
                    route_id=expected_route_id,
                    field=field,
                    expected=expected,
                    actual=route.get(field),
                )
        output_path = str(source["output_path"])
        if output_path not in html_text_cache:
            html_text_cache[output_path] = (html_root / output_path).read_text(encoding="utf-8")
        if f'id="{source["id"]}"' not in html_text_cache[output_path]:
            finding(
                findings,
                "HTML_ROUTE_ANCHOR_MISSING",
                route_id=expected_route_id,
                target=source["id"],
                output_path=output_path,
            )
        expose_edge = (HTML_SURFACE, "exposes_route", expected_route_id)
        if expose_edge not in edges:
            finding(findings, "MISSING_ROUTE_EXPOSURE", edge=list(expose_edge))
        if source["id"] in primary_ids:
            content_edge = (source["id"], "available_at_route", expected_route_id)
            if content_edge not in edges:
                finding(findings, "MISSING_CONTENT_ROUTE", edge=list(content_edge))

    for artifact in artifacts:
        path = ROOT / str(artifact["path"])
        raw = path.read_bytes()
        if len(raw) != artifact.get("bytes") or sha256(raw) != artifact.get("sha256"):
            finding(
                findings,
                "ARTIFACT_HASH_MISMATCH",
                artifact_id=artifact["id"],
                path=artifact["path"],
            )
        edge = (
            str(artifact["component_id"]),
            "represented_by_artifact",
            str(artifact["id"]),
        )
        if edge not in edges:
            finding(findings, "MISSING_ARTIFACT_RELATION", edge=list(edge))
        if artifact.get("surface_id"):
            surface_edge = (
                str(artifact["surface_id"]),
                "represented_by_artifact",
                str(artifact["id"]),
            )
            if surface_edge not in edges:
                finding(findings, "MISSING_SURFACE_ARTIFACT_RELATION", edge=list(surface_edge))

    replay_generator(findings)

    file_inventory = []
    for name in GENERATED_NAMES:
        path = BACKEND / name
        raw = path.read_bytes()
        file_inventory.append(
            {"path": f"backend/{name}", "bytes": len(raw), "sha256": sha256(raw)}
        )
    generator_raw = GENERATOR.read_bytes()
    report = {
        "actual_counts": actual_counts,
        "base_backend_manifest_bytes": (BACKEND / "BACKEND_MANIFEST.csv").stat().st_size,
        "base_backend_manifest_sha256": sha256((BACKEND / "BACKEND_MANIFEST.csv").read_bytes()),
        "base_jsonl_bytes_locked": base_jsonl_bytes_locked,
        "base_jsonl_files_locked": base_jsonl_files_locked,
        "endpoint_count": len(all_endpoints),
        "findings": findings,
        "generated_files": file_inventory,
        "generator": {
            "path": rel(GENERATOR),
            "bytes": len(generator_raw),
            "sha256": sha256(generator_raw),
        },
        "manifest_entries": generated_inventory,
        "result": "pass" if not findings else "fail",
        "schema_version": "o008.companion-backend-validation.v1",
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(rendered, encoding="utf-8", newline="\n")
    if REPORT.read_text(encoding="utf-8") != rendered:
        raise RuntimeError("validation report deterministic serialization mismatch")
    print(rendered, end="")
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
