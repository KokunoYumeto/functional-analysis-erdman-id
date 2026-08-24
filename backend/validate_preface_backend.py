#!/usr/bin/env python3
"""Validate the append-only FAOA-2015-PREFACE backend extension."""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path[:0] = [str(BACKEND), str(ROOT / "qa")]
import generate_preface_backend as generator  # noqa: E402


UNIT_ID = generator.UNIT_ID
MODEL_ID = generator.MODEL_ID


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(name: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (BACKEND / name).read_text(encoding="utf-8").splitlines()]


def file_identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(), "bytes": len(data),
        "logical_records": len(data.splitlines()), "sha256": sha(data),
    }


def validate_prefix() -> dict[str, Any]:
    lock_path = ROOT / generator.PREFIX_LOCK_REL
    expected_lock = generator.prefix_lock_bytes()
    if not lock_path.is_file() or lock_path.read_bytes() != expected_lock:
        raise ValueError("preface prefix-lock document differs")
    for name, (expected_bytes, expected_records, expected_sha) in generator.PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        prefix = data[:expected_bytes]
        if len(prefix) != expected_bytes or sha(prefix) != expected_sha:
            raise ValueError(f"Chapter 1--17 prefix differs: {name}")
        actual_records = len(prefix.splitlines()) - (1 if name == "index_terms.csv" else 0)
        if actual_records != expected_records:
            raise ValueError(f"Chapter 1--17 prefix record count differs: {name}")
    return {
        "status": "pass", "files": len(generator.PREFIX_LOCKS),
        "lock_sha256": sha(expected_lock), "prefix_records": 27_633,
    }


def validate_manifest() -> str:
    with (BACKEND / "BACKEND_MANIFEST.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    expected_names = sorted(
        (
            path.name for path in BACKEND.iterdir()
            if path.is_file() and path.name != "BACKEND_MANIFEST.csv" and path.suffix != ".pyc"
        ),
        key=str.casefold,
    )
    if [row["relative_path"] for row in rows] != expected_names:
        raise ValueError("backend manifest inventory differs")
    for row in rows:
        data = (BACKEND / row["relative_path"]).read_bytes()
        if row["bytes"] != str(len(data)) or row["sha256"] != sha(data):
            raise ValueError(f"backend manifest identity differs: {row['relative_path']}")
    return sha((BACKEND / "BACKEND_MANIFEST.csv").read_bytes())


def ordinal(stable_id: str, infix: str, maximum: int) -> int:
    prefix = f"{UNIT_ID}-{infix}-"
    if not stable_id.startswith(prefix):
        raise ValueError(f"wrong preface formula namespace: {stable_id}")
    value = int(stable_id.removeprefix(prefix))
    if stable_id != f"{prefix}{value:04d}" or not 1 <= value <= maximum:
        raise ValueError(f"preface formula ordinal out of range: {stable_id}")
    return value


def validate_formula_maps(
    records: list[dict[str, Any]], segment_ids: set[str], correction_ids: set[str],
) -> dict[str, int]:
    formulas = [item for item in records if item.get("id", "").startswith(UNIT_ID + "-MATHMAP-")]
    if [item["id"] for item in formulas] != [f"{UNIT_ID}-MATHMAP-{number:04d}" for number in range(1, 225)]:
        raise ValueError("preface formula-map ID/count closure differs")
    source = generator.read_text(generator.SOURCE_PATH, "ascii")
    target = generator.read_text(generator.TARGET_PATH, "utf-8")
    source_surfaces = sorted(
        generator.active_dollar_surfaces(source, "ascii")
        + generator.align_row_surfaces(source, "ascii")
        + generator.diagram_surfaces(source, "ascii"),
        key=lambda item: item["start"],
    )
    target_surfaces = sorted(
        generator.active_dollar_surfaces(target, "utf-8")
        + generator.align_row_surfaces(target, "utf-8")
        + generator.diagram_surfaces(target, "utf-8"),
        key=lambda item: item["start"],
    )
    if (len(source_surfaces), len(target_surfaces)) != (223, 224):
        raise ValueError("preface source/target math census differs")
    source_coverage: list[int] = []
    target_coverage: list[int] = []
    counters: collections.Counter[str] = collections.Counter()
    correction_bindings: dict[str, list[int]] = collections.defaultdict(list)
    for record in formulas:
        source_ordinals = [ordinal(value, "SRC-MATH", 223) for value in record.get("source_formula_ids", [])]
        target_ordinals = [ordinal(value, "ID-MATH", 224) for value in record.get("target_formula_ids", [])]
        source_coverage.extend(source_ordinals)
        target_coverage.extend(target_ordinals)
        if record.get("source_sha256") != [source_surfaces[value - 1]["sha256"] for value in source_ordinals]:
            raise ValueError(f"preface source formula hash differs: {record['id']}")
        if record.get("target_sha256") != [target_surfaces[value - 1]["sha256"] for value in target_ordinals]:
            raise ValueError(f"preface target formula hash differs: {record['id']}")
        if record.get("source_lines") != [
            [source_surfaces[value - 1]["line_start"], source_surfaces[value - 1]["line_end"]]
            for value in source_ordinals
        ]:
            raise ValueError(f"preface source formula locator differs: {record['id']}")
        if record.get("target_lines") != [
            [target_surfaces[value - 1]["line_start"], target_surfaces[value - 1]["line_end"]]
            for value in target_ordinals
        ]:
            raise ValueError(f"preface target formula locator differs: {record['id']}")
        if record.get("parent_segment_id") not in segment_ids:
            raise ValueError(f"preface formula parent segment unresolved: {record['id']}")
        delta = record.get("delta_class")
        counters[delta] += 1
        correction_id = record.get("correction_id")
        if correction_id:
            if correction_id not in correction_ids or delta != "classified_source_correction":
                raise ValueError(f"preface formula correction binding differs: {record['id']}")
            correction_bindings[correction_id].extend(target_ordinals)
    if source_coverage != list(range(1, 224)) or target_coverage != list(range(1, 225)):
        raise ValueError("preface formula coverage is not exact-once and in order")
    expected_correction_ids = {
        f"{UNIT_ID}-CORR-008", f"{UNIT_ID}-CORR-009", f"{UNIT_ID}-CORR-010",
        f"{UNIT_ID}-CORR-011", f"{UNIT_ID}-CORR-014",
    }
    if set(correction_bindings) != expected_correction_ids:
        raise ValueError(f"preface formula correction set differs: {dict(correction_bindings)}")
    expected = collections.Counter({
        "none": 211, "localized_prose_translation": 8,
        "classified_source_correction": 5,
    })
    if counters != expected:
        raise ValueError(f"preface formula classification differs: {counters}")
    return {
        "records": 224, "source_surfaces_covered": 223, "target_surfaces_covered": 224,
        "exact": expected["none"], "localized_prose_translation": expected["localized_prose_translation"],
        "classified_source_correction": expected["classified_source_correction"],
    }


def validate() -> dict[str, Any]:
    if generator.MODEL_ID != MODEL_ID:
        raise ValueError("model identity differs")
    prefix_result = validate_prefix()
    outputs, summary, _ = generator.build_outputs(True)
    mismatches = [
        name for name, data in outputs.items()
        if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != data
    ]
    if mismatches:
        raise ValueError("deterministic preface backend round trip differs: " + ", ".join(mismatches))

    records = {name: load_jsonl(name) for name in generator.JSONL_FILES}
    with (BACKEND / "index_terms.csv").open(encoding="utf-8", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    unit = next(item for item in records["units.jsonl"] if item.get("id") == UNIT_ID)
    if records["units.jsonl"][-1].get("id") != UNIT_ID or unit.get("order") != 0:
        raise ValueError("preface append order/source-order metadata differs")
    if (
        unit.get("admission_state") != "admitted"
        or unit.get("translation_state") != "admitted"
        or unit.get("qa_state") != "passed"
        or unit.get("publication_state") != "pending"
        or unit.get("artifact_sha256") != generator.EXPECTED_FINAL["pdf"][2]
        or unit.get("receipt_sha256") != generator.EXPECTED_FINAL["receipt"][2]
        or unit.get("semantic_accessibility_state") != "remediation_required"
        or unit.get("html_state") != "pending"
    ):
        raise ValueError("preface admitted unit binding differs")

    all_records = [item for name in generator.JSONL_FILES for item in records[name]]
    ids = [item["id"] for item in all_records if item.get("id")]
    for static_name in (
        "assets.jsonl", "rights.jsonl", "concepts.jsonl", "concept_relations.jsonl",
        "resources.jsonl", "terminology_qa.jsonl",
    ):
        ids.extend(item["id"] for item in load_jsonl(static_name) if item.get("id"))
    ids.extend(row["id"] for row in index_rows if row.get("id"))
    duplicates = [stable_id for stable_id, count in collections.Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"global backend stable IDs are not unique: {duplicates[:5]}")
    id_set = set(ids)

    unresolved = []
    external_prefixes = ("ERDMAN-FAOA-BIB-", "ERDMAN-FAOA-2015-LABEL-", "COURSE-O007")
    for relation in records["relations.jsonl"]:
        for key in ("from_id", "to_id"):
            endpoint = relation.get(key)
            if endpoint and endpoint not in id_set and not any(str(endpoint).startswith(prefix) for prefix in external_prefixes):
                unresolved.append((relation["id"], key, endpoint))
    if unresolved:
        raise ValueError(f"backend relation endpoints unresolved: {unresolved[:5]}")

    semantic = [item for item in records["semantic_units.jsonl"] if item.get("id", "").startswith(UNIT_ID + "-")]
    segments = [item for item in records["segments.jsonl"] if item.get("id", "").startswith(UNIT_ID + "-")]
    relations = [item for item in records["relations.jsonl"] if item.get("id", "").startswith(UNIT_ID + "-")]
    expected_kinds = collections.Counter({
        "section": 4, "alphabet_table_greek": 1, "fraktur_table": 1,
        "number_set_notation": 1, "commutative_diagram_rectangular": 1,
        "commutative_diagram_triangular": 1,
    })
    if len(semantic) != 9 or collections.Counter(item["unit_kind"] for item in semantic) != expected_kinds:
        raise ValueError("preface semantic-unit closure differs")
    if len(segments) != 5 or len(relations) != 88:
        raise ValueError("preface segment/relation closure differs")
    if any(
        item.get("admission_state") != "admitted"
        or item.get("translation_state") != "admitted"
        or item.get("qa_state") != "passed"
        for item in semantic + segments
    ):
        raise ValueError("preface semantic/segment admission state differs")
    segment_ids = {item["id"] for item in segments}

    corrections = [item for item in records["corrections.jsonl"] if item.get("unit_id") == UNIT_ID]
    ledger_document = json.loads((ROOT / generator.LEDGER_REL).read_text(encoding="utf-8"))
    ledger_ids = [item["id"] for item in ledger_document["records"]]
    if [item["id"] for item in corrections] != ledger_ids or len(corrections) != 14:
        raise ValueError("preface correction closure differs")
    ledger_sha = sha((ROOT / generator.LEDGER_REL).read_bytes())
    if any(
        item.get("ledger_sha256") != ledger_sha
        or item.get("qa_state") != "passed"
        or item.get("admission_state") != "admitted"
        or item.get("receipt_sha256") != generator.EXPECTED_FINAL["receipt"][2]
        for item in corrections
    ):
        raise ValueError("preface correction provenance differs")
    formula_summary = validate_formula_maps(records["formula_map.jsonl"], segment_ids, set(ledger_ids))

    term_relations = [item for item in relations if item.get("relation_type") == "uses_term"]
    new_terms = [item for item in records["terminology.jsonl"] if item.get("introduced_in_unit") == UNIT_ID]
    if len(term_relations) != 21 or len(new_terms) != 18 or {item["id"] for item in new_terms} != set(generator.NEW_TERM_SPECS):
        raise ValueError("preface terminology closure differs")
    if any(item.get("to_id") not in id_set for item in term_relations):
        raise ValueError("preface terminology endpoint differs")

    preface_index = [row for row in index_rows if row.get("id", "").startswith(UNIT_ID + "-")]
    source_indexes = generator.prior.common.macro(generator.read_text(generator.SOURCE_PATH, "ascii"), "index")
    target_indexes = generator.prior.common.macro(generator.read_text(generator.TARGET_PATH, "utf-8"), "index")
    if len(preface_index) != 53 or len(source_indexes) != 53 or len(target_indexes) != 53:
        raise ValueError("preface index closure differs")
    for number, (row, source_item, target_item) in enumerate(zip(preface_index, source_indexes, target_indexes, strict=True), 1):
        expected = {
            "id": f"{UNIT_ID}-TERM-OCC-{number:04d}", "source_order": str(number),
            "source_line": str(source_item["line"]), "source_index_tex": source_item["argument"],
            "target_line": str(target_item["line"]), "target_index_tex": target_item["argument"],
            "source_sha256": sha(source_item["argument"].encode("ascii")),
            "target_sha256": sha(target_item["argument"].encode("utf-8")), "locale": "id-ID",
        }
        if any(row.get(key) != value for key, value in expected.items()) or row.get("parent_segment_id") not in segment_ids:
            raise ValueError(f"preface index occurrence differs: {number}")

    citations = [item for item in relations if item.get("relation_type") == "cites"]
    labels = [item for item in relations if item.get("relation_type") == "declares_label"]
    rights = [item for item in relations if item.get("relation_type") == "licensed_under"]
    if len(citations) != 5 or len(labels) != 1 or len(rights) != 1 or rights[0].get("to_id") != generator.RIGHTS_ID:
        raise ValueError("preface citation/label/rights closure differs")

    artifacts = [item for item in records["artifacts.jsonl"] if item.get("unit_id") == UNIT_ID]
    qa_events = [item for item in records["qa_events.jsonl"] if item.get("unit_id") == UNIT_ID]
    if len(artifacts) != 18 or len(qa_events) != 10 or any(item.get("model_id") != MODEL_ID for item in qa_events):
        raise ValueError("preface artifact/QA/model closure differs")
    for artifact in artifacts:
        info = file_identity(ROOT / artifact["path"])
        if (
            artifact.get("bytes") != info["bytes"]
            or artifact.get("sha256") != info["sha256"]
            or artifact.get("binding_state") != "bound"
            or artifact.get("admission_state") != "admitted"
        ):
            raise ValueError(f"preface bound evidence identity differs: {artifact['id']}")
    admission = [item for item in qa_events if item.get("qa_type") == "unit_admission"]
    if (
        len(admission) != 1 or admission[0].get("result") != "pass"
        or admission[0].get("decision") != "admitted"
        or admission[0].get("receipt_sha256") != generator.EXPECTED_FINAL["receipt"][2]
    ):
        raise ValueError("preface admission event differs")
    if any(item.get("result") != "pass" or item.get("admission_state") != "admitted" for item in qa_events):
        raise ValueError("preface admitted QA state differs")
    accessibility = [item for item in qa_events if item.get("qa_type") == "cumulative_accessibility"]
    if (
        len(accessibility) != 1
        or accessibility[0].get("tagged_pdf") is not False
        or accessibility[0].get("semantic_accessibility_state") != "remediation_required"
        or accessibility[0].get("html_state") != "pending"
    ):
        raise ValueError("preface accessibility limitation is not preserved")

    manifest_sha = validate_manifest()
    aggregate_records = sum(len(records[name]) for name in generator.JSONL_FILES) + len(index_rows)
    if aggregate_records != 28_073:
        raise ValueError(f"aggregate backend record count differs: {aggregate_records}")
    if summary.get("aggregate_records") != aggregate_records:
        raise ValueError("generator aggregate summary differs")
    return {
        "status": "pass", "unit_id": UNIT_ID,
        "binding_state": "bound",
        "source_sha256": generator.EXPECTED_SOURCE[2],
        "target_sha256": generator.EXPECTED_TARGET[2],
        "master_sha256": generator.EXPECTED_MASTER[2], "model_id": MODEL_ID,
        "preface": {
            "semantic_units": len(semantic), "segments": len(segments), "relations": len(relations),
            "formula_map": formula_summary, "index_terms": len(preface_index),
            "new_terms": len(new_terms), "term_uses": len(term_relations),
            "citations": len(citations), "corrections": len(corrections),
            "artifacts": len(artifacts), "qa_events": len(qa_events),
        },
        "aggregate_records": aggregate_records, "global_stable_ids": "unique",
        "relation_endpoints": "resolved", "deterministic_round_trip": "pass",
        "chapter1_ch17_prefix_lock": prefix_result, "backend_manifest_sha256": manifest_sha,
        "admission_claim": "admitted_by_exact_receipt_binding",
        "receipt_sha256": generator.EXPECTED_FINAL["receipt"][2],
        "reader_sha256": generator.EXPECTED_FINAL["pdf"][2],
        "semantic_accessibility_state": "remediation_required", "html_state": "pending",
    }


def main() -> None:
    result = validate()
    payload = {
        "schema_version": "o008.backend-validation.v1", "timestamp": "2026-08-24",
        **result, "validator": file_identity(Path(__file__)),
    }
    output = ROOT / "qa/PREFACE_BACKEND_VALIDATION.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
