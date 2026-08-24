#!/usr/bin/env python3
"""Validate the additive semantic-HTML backend and frozen source-text prefix."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import generate_html_backend as generator


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SURFACE_ID = generator.SURFACE_ID


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError(f"{path.name} lacks final LF")
    records: list[dict[str, Any]] = []
    for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        if not line:
            raise ValueError(f"{path.name}:{number} is empty")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number} is not an object")
        if value.get("schema") != generator.SCHEMA or value.get("schema_version") != generator.SCHEMA_VERSION:
            raise ValueError(f"{path.name}:{number} schema differs")
        records.append(value)
    return records


def validate() -> dict[str, Any]:
    outputs_one, summary_one = generator.build_records()
    outputs_two, summary_two = generator.build_records()
    if outputs_one != outputs_two or summary_one != summary_two:
        raise ValueError("semantic-HTML backend generation is not deterministic")
    mismatches = [
        name for name, data in outputs_one.items()
        if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != data
    ]
    if mismatches:
        raise ValueError("checked-in semantic-HTML backend differs: " + ", ".join(mismatches))

    schema = json.loads((BACKEND / "schema.json").read_text(encoding="utf-8"))
    required_sets = set(schema["record_sets"])
    if not {"html_surfaces.jsonl", "html_assets.jsonl"}.issubset(required_sets):
        raise ValueError("schema omits semantic-HTML record sets")
    if schema.get("auxiliary_sets") != ["html_routes.jsonl"]:
        raise ValueError("schema HTML auxiliary route-map declaration differs")

    entity_paths = sorted(
        (path for path in BACKEND.glob("*.jsonl") if path.name != "html_routes.jsonl"),
        key=lambda path: path.name.casefold(),
    )
    records_by_file = {path.name: load_jsonl(path) for path in entity_paths}
    all_records = [record for records in records_by_file.values() for record in records]

    with (BACKEND / "index_terms.csv").open(encoding="utf-8", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    ids: list[str] = [record["id"] for record in all_records if record.get("id")]
    ids.extend(row["id"] for row in index_rows if row.get("id"))
    duplicates = [stable_id for stable_id, count in collections.Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"global entity IDs are not unique: {duplicates[:5]}")
    id_set = set(ids)

    external_prefixes = ("ERDMAN-FAOA-BIB-", "ERDMAN-FAOA-2015-LABEL-", "COURSE-O007")
    unresolved: list[tuple[str, str, str]] = []
    for relation in records_by_file["relations.jsonl"] + records_by_file["concept_relations.jsonl"]:
        for key in ("from_id", "to_id"):
            endpoint = relation.get(key)
            if endpoint and endpoint not in id_set and not any(str(endpoint).startswith(prefix) for prefix in external_prefixes):
                unresolved.append((relation["id"], key, str(endpoint)))
    if unresolved:
        raise ValueError(f"relation endpoints unresolved: {unresolved[:5]}")

    rights_ids = {record["id"] for record in records_by_file["rights.jsonl"]}
    for record in all_records:
        rights_id = record.get("rights_id")
        if rights_id and rights_id not in rights_ids:
            raise ValueError(f"unresolved rights ID {rights_id} on {record['id']}")
        component_rights = record.get("rendering_component_rights_id")
        if component_rights and component_rights not in rights_ids:
            raise ValueError(f"unresolved component rights ID {component_rights} on {record['id']}")

    surfaces = records_by_file["html_surfaces.jsonl"]
    assets = records_by_file["html_assets.jsonl"]
    if len(surfaces) != 1 or surfaces[0].get("id") != SURFACE_ID:
        raise ValueError("semantic-HTML surface cardinality differs")
    surface = surfaces[0]
    if (
        surface.get("admission_state") != "admitted"
        or surface.get("whole_edition_state") != "in_progress"
        or surface.get("html_semantic_accessibility_state") != "passed"
        or surface.get("pdf_accessibility_state") != "untagged_remediation_required"
        or surface.get("site_inventory_sha256") != "f04bb3f5ee883c794474b191faf0e724987ebc01c4711bac8f6dc5421e543f32"
    ):
        raise ValueError("semantic-HTML surface state differs")
    if len(assets) != 80 or len({record["id"] for record in assets}) != 80:
        raise ValueError("semantic-HTML asset closure differs")
    for asset in assets:
        path = ROOT / asset["path"]
        data = path.read_bytes()
        if (
            len(data) != asset["bytes"]
            or sha(data) != asset["sha256"]
            or asset.get("surface_id") != SURFACE_ID
            or asset.get("admission_state") != "admitted"
            or asset.get("description_creator") != generator.MODEL_ID
        ):
            raise ValueError(f"semantic-HTML asset binding differs: {asset['id']}")

    html_artifacts = [
        record for record in records_by_file["artifacts.jsonl"]
        if record.get("surface_id") == SURFACE_ID
    ]
    html_qa = [
        record for record in records_by_file["qa_events.jsonl"]
        if record.get("surface_id") == SURFACE_ID
    ]
    html_relations = [
        record for record in records_by_file["relations.jsonl"]
        if record.get("id", "").startswith("REL-FAOA-ID-HTML-")
    ]
    if len(html_artifacts) != 10 or len(html_qa) != 5 or len(html_relations) != 97:
        raise ValueError("semantic-HTML artifact/QA/relation closure differs")
    for artifact in html_artifacts:
        data = (ROOT / artifact["path"]).read_bytes()
        if (
            len(data) != artifact["bytes"]
            or sha(data) != artifact["sha256"]
            or artifact.get("binding_state") != "bound"
            or artifact.get("admission_state") != "admitted"
        ):
            raise ValueError(f"semantic-HTML artifact binding differs: {artifact['id']}")
    if any(
        event.get("result") != "pass"
        or event.get("admission_state") != "admitted"
        or event.get("model_id") != generator.MODEL_ID
        for event in html_qa
    ):
        raise ValueError("semantic-HTML QA/model state differs")

    route_records = generator.read_jsonl(BACKEND / "html_routes.jsonl")
    route_ids = [record["id"] for record in route_records]
    if len(route_records) != 4_838 or len(set(route_ids)) != 4_838:
        raise ValueError("case-sensitive route-map ID closure differs")
    if {value for value in route_ids if value.casefold() == "exam_dual_c0"} != {"exam_dual_C0", "exam_dual_c0"}:
        raise ValueError("inherited case-sensitive C0/c0 routes differ")

    manifest = (BACKEND / "BACKEND_MANIFEST.csv").read_bytes()
    if manifest != outputs_one["BACKEND_MANIFEST.csv"]:
        raise ValueError("backend manifest differs from deterministic inventory")
    prefix_lock_identity = sha((BACKEND / "HTML_PREFIX_LOCKS.json").read_bytes())
    receipt_identity = sha((ROOT / "provenance/HTML_READER_BUILD_AND_QA_RECEIPT.md").read_bytes())
    return {
        "schema_version": "o008.html-backend-validation.v1",
        "status": "pass",
        "surface_id": SURFACE_ID,
        "source_text_prefix_state": "byte_identical",
        "source_text_manifest_sha256": summary_one["source_text_manifest_sha256"],
        "html_surface_records": len(surfaces),
        "html_asset_records": len(assets),
        "html_artifact_records": len(html_artifacts),
        "html_qa_records": len(html_qa),
        "html_relation_records": len(html_relations),
        "route_records": len(route_records),
        "route_ids": "case_sensitive_unique",
        "global_entity_ids": "unique",
        "relation_endpoints": "resolved",
        "deterministic_generator_replays": 2,
        "site_inventory_sha256": surface["site_inventory_sha256"],
        "backend_manifest_sha256": sha(manifest),
        "html_prefix_locks_sha256": prefix_lock_identity,
        "html_admission_receipt_sha256": receipt_identity,
        "whole_edition_state": "in_progress",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate()
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.write_text(rendered, encoding="utf-8", newline="")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
