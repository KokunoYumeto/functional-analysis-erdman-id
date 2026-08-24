#!/usr/bin/env python3
"""Generate the additive semantic-HTML backend over the frozen source-text prefix."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
PREFIX_LOCK_PATH = BACKEND / "HTML_PREFIX_LOCKS.json"
SURFACE_ID = "FAOA-2015-ID-HTML-SOURCE-TEXT"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"
SCHEMA = "interlanguage-modular-math"
SCHEMA_VERSION = "0.1.0"

BUILD_RESULT_PATH = ROOT / "qa/HTML_BUILD_RESULT.json"
MACHINE_QA_PATH = ROOT / "qa/HTML_READER_QA.json"
VISUAL_QA_PATH = ROOT / "qa/HTML_VISUAL_QA.json"
DIAGRAM_TEXT_PATH = ROOT / "html/accessibility/diagram_text.jsonl"
SITE_ROOT = ROOT / "output/html"
SITE_MANIFEST_PATH = SITE_ROOT / "MANIFEST.csv"
ROUTE_MAP_PATH = BACKEND / "html_routes.jsonl"

ARTIFACT_SPECS = [
    ("SITE-MANIFEST", "html_site_manifest", "output/html/MANIFEST.csv"),
    ("ROUTE-MAP", "html_route_map", "backend/html_routes.jsonl"),
    ("BUILD-RESULT", "html_build_result", "qa/HTML_BUILD_RESULT.json"),
    ("MACHINE-QA", "html_machine_qa", "qa/HTML_READER_QA.json"),
    ("VISUAL-QA", "html_responsive_visual_qa", "qa/HTML_VISUAL_QA.json"),
    ("BUILDER", "html_builder", "html/build_reader.py"),
    ("QA-SCRIPT", "html_qa_checker", "html/qa_reader.py"),
    ("CSS", "html_reader_stylesheet", "html/static/reader.css"),
    ("DIAGRAM-TRANSCRIPTS", "diagram_accessibility_transcripts", "html/accessibility/diagram_text.jsonl"),
    ("ADMISSION-RECEIPT", "html_admission_receipt", "provenance/HTML_READER_BUILD_AND_QA_RECEIPT.md"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} is not a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise RuntimeError(f"{path} lacks final LF")
    records: list[dict[str, Any]] = []
    for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        if not line:
            raise RuntimeError(f"{path}:{number} is empty")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"{path}:{number} is not an object")
        records.append(value)
    return records


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return (
        "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            for record in records
        )
    ).encode("utf-8")


def file_identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "bytes": len(data),
        "sha256": sha(data),
        "lines": len(data.splitlines()),
    }


def locked_prefixes() -> tuple[dict[str, Any], dict[str, bytes]]:
    lock = read_json(PREFIX_LOCK_PATH)
    if lock.get("schema_version") != "o008.html-prefix-locks.v1":
        raise RuntimeError("HTML prefix-lock schema differs")
    prefixes: dict[str, bytes] = {}
    for name, expected in lock["prefixes"].items():
        data = (BACKEND / name).read_bytes()
        size = int(expected["bytes"])
        prefix = data[:size]
        if (
            len(prefix) != size
            or sha(prefix) != expected["sha256"]
            or len(prefix.splitlines()) != int(expected["records"])
        ):
            raise RuntimeError(f"frozen source-text backend prefix differs: {name}")
        prefixes[name] = prefix
    return lock, prefixes


def route_for(diagram_id: str) -> str:
    if diagram_id.startswith("FAOA-2015-DIAGRAM-PREFACE-"):
        return "prakata"
    marker = "FAOA-2015-DIAGRAM-CH"
    if diagram_id.startswith(marker):
        chapter = int(diagram_id[len(marker) : len(marker) + 2])
        return f"bab-{chapter:02d}"
    raise RuntimeError(f"cannot derive route for {diagram_id}")


def validate_site_manifest() -> tuple[list[dict[str, str]], int]:
    with SITE_MANIFEST_PATH.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["path", "bytes", "sha256"]:
            raise RuntimeError("HTML site manifest header differs")
        rows = list(reader)
    total = 0
    for row in rows:
        path = SITE_ROOT / row["path"]
        identity = file_identity(path)
        if identity["bytes"] != int(row["bytes"]) or identity["sha256"] != row["sha256"]:
            raise RuntimeError(f"HTML site manifest mismatch: {row['path']}")
        total += identity["bytes"]
    return rows, total


def validate_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    build = read_json(BUILD_RESULT_PATH)
    machine = read_json(MACHINE_QA_PATH)
    visual = read_json(VISUAL_QA_PATH)
    diagrams = read_jsonl(DIAGRAM_TEXT_PATH)
    svg_results = {item["id"]: item for item in build["svg_results"]}
    routes = read_jsonl(ROUTE_MAP_PATH)

    if build.get("status") != "passed" or any(build.get("failures", {}).values()):
        raise RuntimeError("HTML build report is not a clean pass")
    if machine.get("passed") is not True or machine.get("counts", {}).get("findings") != 0:
        raise RuntimeError("HTML machine QA is not a zero-finding pass")
    if visual.get("status") != "passed":
        raise RuntimeError("HTML visual QA is not a pass")
    if len(diagrams) != 80 or len(svg_results) != 80 or {d["diagram_id"] for d in diagrams} != set(svg_results):
        raise RuntimeError("diagram transcript/SVG closure differs")
    if len(routes) != 4_838 or len({item["id"] for item in routes}) != 4_838:
        raise RuntimeError("case-sensitive HTML route-map closure differs")
    if {item["id"] for item in routes if item["id"].casefold() == "exam_dual_c0"} != {"exam_dual_C0", "exam_dual_c0"}:
        raise RuntimeError("case-sensitive inherited C0/c0 anchors differ")

    site_rows, site_payload_bytes = validate_site_manifest()
    if (
        len(site_rows) != 104
        or build.get("site_file_count_excluding_manifest") != 104
        or build.get("site_tree_sha256") != "f04bb3f5ee883c794474b191faf0e724987ebc01c4711bac8f6dc5421e543f32"
        or machine.get("artifacts", {}).get("inventory_sha256") != build["site_tree_sha256"]
        or machine.get("artifacts", {}).get("route_map_sha256") != build["route_map_sha256"]
        or file_identity(SITE_MANIFEST_PATH)["sha256"] != build["manifest_sha256"]
    ):
        raise RuntimeError("HTML site identity closure differs")
    site_total_bytes = site_payload_bytes + SITE_MANIFEST_PATH.stat().st_size
    if site_total_bytes != visual.get("artifact", {}).get("bytes"):
        raise RuntimeError("HTML site byte total differs")
    return build, machine, visual, diagrams, svg_results, routes


def build_records() -> tuple[dict[str, bytes], dict[str, Any]]:
    lock, prefixes = locked_prefixes()
    build, machine, visual, diagrams, svg_results, routes = validate_inputs()

    surface = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "record_type": "html_surface",
        "id": SURFACE_ID,
        "edition_id": "ERDMAN-FAOA-2015-ID",
        "source_edition_id": "ERDMAN-FAOA-2015",
        "locale": "id-ID",
        "surface_kind": "offline_semantic_html_reader",
        "scope": "preface_all_17_chapters_bibliography_index_and_edition_information",
        "admission_state": "admitted",
        "publication_state": "pending",
        "whole_edition_state": "in_progress",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
        "model_provenance": MODEL_ID,
        "site_path": "output/html",
        "site_files": machine["counts"]["files"],
        "site_bytes": visual["artifact"]["bytes"],
        "site_inventory_sha256": build["site_tree_sha256"],
        "site_manifest_sha256": build["manifest_sha256"],
        "route_map_path": "backend/html_routes.jsonl",
        "route_records": build["route_map_count"],
        "route_map_sha256": build["route_map_sha256"],
        "route_count": build["route_count"],
        "semantic_unit_count": build["semantic_unit_count"],
        "segment_anchor_count": build["segment_count"],
        "mathml_count": machine["counts"]["mathml_elements"],
        "diagram_count": build["diagram_count"],
        "index_occurrence_count": build["index_occurrence_count"],
        "citation_count": build["reference_totals"]["citations_rewritten"],
        "cross_reference_count": build["reference_totals"]["references_rewritten"],
        "html_semantic_accessibility_state": "passed",
        "pdf_accessibility_state": "untagged_remediation_required",
        "pdf_companion_sha256": "efa2358b3c3e6e8c47e0caee9a02f6afe78d15bea1b0f1822ea8449d801b2b10",
        "pending_components": ["O001_mastery_and_solutions", "compact_spectral_and_SVD_bridge"],
    }

    descriptions = {item["diagram_id"]: item for item in diagrams}
    html_assets: list[dict[str, Any]] = []
    for diagram_id in sorted(svg_results):
        description = descriptions[diagram_id]
        result = svg_results[diagram_id]
        rel_path = f"output/html/assets/diagrams/{diagram_id}.svg"
        identity = file_identity(ROOT / rel_path)
        if identity["bytes"] != result["bytes"] or identity["sha256"] != result["sha256"]:
            raise RuntimeError(f"final SVG identity differs: {diagram_id}")
        html_assets.append({
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "html_asset",
            "id": diagram_id,
            "surface_id": SURFACE_ID,
            "asset_kind": "accessible_svg_diagram",
            "route": route_for(diagram_id),
            "fragment_id": diagram_id,
            "path": rel_path,
            "bytes": identity["bytes"],
            "sha256": identity["sha256"],
            "source_file": description["source_file"],
            "source_line": description["source_line"],
            "source_end_line": description["source_end_line"],
            "source_anchor": description["source_anchor"],
            "source_form": description["source_form"],
            "description_id": description["description_id"],
            "description_sha256": sha(description["description_id"].encode("utf-8")),
            "source_creator": "John M. Erdman",
            "description_creator": MODEL_ID,
            "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
            "rendering_component_rights_id": "RIGHTS-DIAGXY-BARR",
            "nonendorsement": True,
            "admission_state": "admitted",
        })

    artifacts: list[dict[str, Any]] = []
    for suffix, kind, rel_path in ARTIFACT_SPECS:
        identity = file_identity(ROOT / rel_path)
        artifacts.append({
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "artifact",
            "id": f"ARTIFACT-FAOA-ID-HTML-{suffix}",
            "surface_id": SURFACE_ID,
            "artifact_kind": kind,
            "path": rel_path,
            "bytes": identity["bytes"],
            "lines": identity["lines"],
            "sha256": identity["sha256"],
            "binding_state": "bound",
            "admission_state": "admitted",
        })

    replay_identity = file_identity(ROOT / "qa/html-replay-c-build/result.json")
    if replay_identity != file_identity(ROOT / "qa/html-replay-d-build/result.json"):
        raise RuntimeError("corrected HTML replay reports differ")
    qa_events = [
        {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "qa_event",
            "id": "QA-FAOA-ID-HTML-BUILD-20260824",
            "surface_id": SURFACE_ID,
            "qa_type": "semantic_html_build",
            "result": "pass",
            "timestamp": "2026-08-24",
            "model_id": MODEL_ID,
            "routes": 22,
            "mathml_nodes": 11_193,
            "svg_diagrams": 80,
            "failures": 0,
            "witness": "qa/HTML_BUILD_RESULT.json",
            "witness_sha256": file_identity(BUILD_RESULT_PATH)["sha256"],
            "admission_state": "admitted",
        },
        {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "qa_event",
            "id": "QA-FAOA-ID-HTML-REPLAY-20260824",
            "surface_id": SURFACE_ID,
            "qa_type": "deterministic_html_replay",
            "result": "pass",
            "timestamp": "2026-08-24",
            "model_id": MODEL_ID,
            "replay_count": 2,
            "public_file_differences": 0,
            "site_inventory_sha256": build["site_tree_sha256"],
            "witness": "qa/html-replay-c-build/result.json",
            "witness_sha256": replay_identity["sha256"],
            "second_witness": "qa/html-replay-d-build/result.json",
            "second_witness_sha256": replay_identity["sha256"],
            "admission_state": "admitted",
        },
        {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "qa_event",
            "id": "QA-FAOA-ID-HTML-MACHINE-20260824",
            "surface_id": SURFACE_ID,
            "qa_type": "html_structure_math_accessibility_security",
            "result": "pass",
            "timestamp": "2026-08-24",
            "model_id": MODEL_ID,
            "findings": 0,
            "witness": "qa/HTML_READER_QA.json",
            "witness_sha256": file_identity(MACHINE_QA_PATH)["sha256"],
            "admission_state": "admitted",
        },
        {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "qa_event",
            "id": "QA-FAOA-ID-HTML-VISUAL-20260824",
            "surface_id": SURFACE_ID,
            "qa_type": "responsive_visual",
            "result": "pass",
            "timestamp": "2026-08-24",
            "model_id": MODEL_ID,
            "desktop_routes": 22,
            "mobile_routes": 22,
            "svg_images_loaded_mobile": 80,
            "horizontal_overflow_failures": 0,
            "witness": "qa/HTML_VISUAL_QA.json",
            "witness_sha256": file_identity(VISUAL_QA_PATH)["sha256"],
            "admission_state": "admitted",
        },
        {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "qa_event",
            "id": "QA-FAOA-ID-HTML-ADMISSION-20260824",
            "surface_id": SURFACE_ID,
            "qa_type": "html_surface_admission",
            "result": "pass",
            "decision": "admitted",
            "timestamp": "2026-08-24",
            "model_id": MODEL_ID,
            "whole_edition_state": "in_progress",
            "site_inventory_sha256": build["site_tree_sha256"],
            "witness": "provenance/HTML_READER_BUILD_AND_QA_RECEIPT.md",
            "witness_sha256": file_identity(ROOT / "provenance/HTML_READER_BUILD_AND_QA_RECEIPT.md")["sha256"],
            "admission_state": "admitted",
        },
    ]

    relations: list[dict[str, Any]] = [
        {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "relation",
            "id": "REL-FAOA-ID-HTML-EDITION-SURFACE",
            "relation_type": "has_html_surface",
            "from_id": "ERDMAN-FAOA-2015-ID",
            "to_id": SURFACE_ID,
        },
        {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "relation",
            "id": "REL-FAOA-ID-HTML-LICENSE",
            "relation_type": "licensed_under",
            "from_id": SURFACE_ID,
            "to_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
        },
    ]
    for number, artifact in enumerate(artifacts, 1):
        relations.append({
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "relation",
            "id": f"REL-FAOA-ID-HTML-ARTIFACT-{number:03d}",
            "relation_type": "documented_by",
            "from_id": SURFACE_ID,
            "to_id": artifact["id"],
        })
    for number, event in enumerate(qa_events, 1):
        relations.append({
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "relation",
            "id": f"REL-FAOA-ID-HTML-QA-{number:03d}",
            "relation_type": "validated_by",
            "from_id": SURFACE_ID,
            "to_id": event["id"],
        })
    for number, asset in enumerate(html_assets, 1):
        relations.append({
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "record_type": "relation",
            "id": f"REL-FAOA-ID-HTML-ASSET-{number:03d}",
            "relation_type": "renders_asset",
            "from_id": SURFACE_ID,
            "to_id": asset["id"],
        })

    outputs: dict[str, bytes] = {
        "html_surfaces.jsonl": jsonl_bytes([surface]),
        "html_assets.jsonl": jsonl_bytes(html_assets),
        "artifacts.jsonl": prefixes["artifacts.jsonl"] + jsonl_bytes(artifacts),
        "qa_events.jsonl": prefixes["qa_events.jsonl"] + jsonl_bytes(qa_events),
        "relations.jsonl": prefixes["relations.jsonl"] + jsonl_bytes(relations),
    }

    names = {
        path.name
        for path in BACKEND.iterdir()
        if path.is_file() and path.name != "BACKEND_MANIFEST.csv" and path.suffix != ".pyc"
    } | set(outputs)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["relative_path", "bytes", "sha256"])
    for name in sorted(names, key=str.casefold):
        data = outputs[name] if name in outputs else (BACKEND / name).read_bytes()
        writer.writerow([name, len(data), sha(data)])
    outputs["BACKEND_MANIFEST.csv"] = buffer.getvalue().encode("utf-8")

    summary = {
        "status": "pass",
        "surface_id": SURFACE_ID,
        "source_text_manifest_sha256": lock["source_text_backend_manifest_sha256"],
        "site_inventory_sha256": build["site_tree_sha256"],
        "route_records": len(routes),
        "html_assets": len(html_assets),
        "artifacts_appended": len(artifacts),
        "qa_events_appended": len(qa_events),
        "relations_appended": len(relations),
        "backend_manifest_sha256": sha(outputs["BACKEND_MANIFEST.csv"]),
    }
    return outputs, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Verify deterministic bytes without writing")
    args = parser.parse_args()
    outputs, summary = build_records()
    mismatches = [
        name for name, data in outputs.items()
        if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != data
    ]
    if args.check:
        if mismatches:
            raise RuntimeError("checked-in HTML backend differs: " + ", ".join(mismatches))
    else:
        for name, data in outputs.items():
            (BACKEND / name).write_bytes(data)
    summary["writes_performed"] = not args.check
    summary["mismatches_before_write"] = mismatches
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
