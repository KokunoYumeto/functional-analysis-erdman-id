#!/usr/bin/env python3
"""Validate the Chapter 14 backend append and exact Chapter 1--13 prefix."""

from __future__ import annotations

import argparse
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
import ch03_math  # noqa: E402
import check_ch05_translation as common  # noqa: E402
import generate_ch14_backend as generator  # noqa: E402


CHAPTER_ID = generator.CHAPTER_ID


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


def validate_manifest() -> str:
    with (BACKEND / "BACKEND_MANIFEST.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    expected_names = sorted(
        path.name for path in BACKEND.iterdir()
        if path.is_file() and path.name != "BACKEND_MANIFEST.csv" and path.suffix != ".pyc"
    )
    if [row["relative_path"] for row in rows] != sorted(expected_names, key=str.casefold):
        raise ValueError("backend manifest inventory differs")
    for row in rows:
        data = (BACKEND / row["relative_path"]).read_bytes()
        if row["bytes"] != str(len(data)) or row["sha256"] != sha(data):
            raise ValueError(f"backend manifest identity differs: {row['relative_path']}")
    return sha((BACKEND / "BACKEND_MANIFEST.csv").read_bytes())


def validate_formula_maps(
    records: list[dict[str, Any]], ledger: dict[str, Any]
) -> dict[str, int]:
    chapter = [record for record in records if record["id"].startswith(CHAPTER_ID + "-")]
    source_math = ch03_math.extract_math(generator.SOURCE_PATH.read_text(encoding="ascii"), "ascii")
    target_math = ch03_math.extract_math(generator.TARGET_PATH.read_text(encoding="utf-8"), "utf-8")
    if len(source_math) != 642 or len(target_math) != 642 or len(chapter) != 642:
        raise ValueError(f"Chapter 14 formula closure differs: {len(source_math)}/{len(target_math)}/{len(chapter)}")
    expected_ids = [f"{CHAPTER_ID}-MATHMAP-{number:04d}" for number in range(1, 643)]
    if [record["id"] for record in chapter] != expected_ids:
        raise ValueError("Chapter 14 formula-map ID/order differs")
    valid_corrections = {
        record["id"] for record in generator.ledger_records(ledger)
        if record.get("affects_math") is True
    }
    if len(valid_corrections) != 2:
        raise ValueError("Chapter 14 mathematical correction closure differs")
    source_coverage: set[int] = set()
    insertion_count = correction_count = reordered_count = localized_count = 0
    correction_ordinals = set()
    reordered_ordinals = set()
    localized_ordinals = set()
    for target_index, record in enumerate(chapter):
        target_item = target_math[target_index]
        if record.get("target_formula_ids") != [f"{CHAPTER_ID}-ID-MATH-{target_index + 1:04d}"]:
            raise ValueError(f"target formula ID differs: {record['id']}")
        if record.get("target_sha256") != [target_item["sha256"]] or record.get("target_lines") != [[target_item["line_start"], target_item["line_end"]]]:
            raise ValueError(f"target formula identity differs: {record['id']}")
        source_indexes = []
        for stable_id in record.get("source_formula_ids", []):
            ordinal = int(stable_id.rsplit("-", 1)[1])
            if stable_id != f"{CHAPTER_ID}-SRC-MATH-{ordinal:04d}" or not 1 <= ordinal <= 642:
                raise ValueError(f"source formula ID out of range: {stable_id}")
            source_indexes.append(ordinal - 1)
            source_coverage.add(ordinal - 1)
        if record.get("source_sha256") != [source_math[index]["sha256"] for index in source_indexes]:
            raise ValueError(f"source formula hash differs: {record['id']}")
        if record.get("source_lines") != [[source_math[index]["line_start"], source_math[index]["line_end"]] for index in source_indexes]:
            raise ValueError(f"source formula lines differ: {record['id']}")
        if not source_indexes:
            insertion_count += 1
        if record.get("correction_id"):
            correction_count += 1
            correction_ordinals.add(target_index + 1)
            if record["correction_id"] not in valid_corrections:
                raise ValueError(f"unknown formula correction: {record['id']}")
        if record.get("alignment", "").endswith("_reordered"):
            reordered_count += 1
            reordered_ordinals.add(target_index + 1)
        if record.get("delta_class") == "localized_prose_translation":
            localized_count += 1
            localized_ordinals.add(target_index + 1)
    if source_coverage != set(range(642)):
        raise ValueError("Chapter 14 formula maps do not cover all source surfaces")
    expected = (
        insertion_count == 0 and correction_count == 2 and reordered_count == 5
        and localized_count == 4 and correction_ordinals == {55, 233}
        and reordered_ordinals == {59, 60, 61, 606, 607}
        and localized_ordinals == {278, 301, 388, 466}
    )
    if not expected:
        raise ValueError(
            "Chapter 14 formula delta closure differs: "
            f"{insertion_count}/{correction_count}/{reordered_count}/{localized_count}/"
            f"{sorted(correction_ordinals)}/{sorted(reordered_ordinals)}/{sorted(localized_ordinals)}"
        )
    return {
        "records": 642, "source_surfaces_covered": 642, "target_insertions": 0,
        "classified_source_correction_maps": 2, "exact_reordered_maps": 5,
        "localized_prose_translation_maps": 4,
    }


def validate_index(rows: list[dict[str, str]]) -> None:
    chapter = [row for row in rows if row["id"].startswith(CHAPTER_ID + "-")]
    source_indexes = common.macro(generator.SOURCE_PATH.read_text(encoding="ascii"), "index")
    target_indexes = common.macro(generator.TARGET_PATH.read_text(encoding="utf-8"), "index")
    if len(chapter) != 79 or len(source_indexes) != 79 or len(target_indexes) != 79:
        raise ValueError("Chapter 14 index closure differs")
    for number, (row, source_item, target_item) in enumerate(
        zip(chapter, source_indexes, target_indexes, strict=True), 1
    ):
        expected = {
            "id": f"{CHAPTER_ID}-TERM-OCC-{number:04d}", "source_order": str(number),
            "source_line": str(source_item["line"]), "source_index_tex": source_item["argument"],
            "target_line": str(target_item["line"]), "target_index_tex": target_item["argument"],
            "source_sha256": sha(source_item["argument"].encode("ascii")),
            "target_sha256": sha(target_item["argument"].encode("utf-8")), "locale": "id-ID",
        }
        if any(row.get(key) != value for key, value in expected.items()):
            raise ValueError(f"Chapter 14 index occurrence differs: {number}")


def validate_artifacts(artifacts: list[dict[str, Any]], bound: bool) -> None:
    if len(artifacts) != 15:
        raise ValueError(f"Chapter 14 artifact closure differs: {len(artifacts)}")
    for record in artifacts:
        if record.get("binding_state") == "bound":
            path = ROOT / record["path"]
            info = file_identity(path)
            if record.get("bytes") != info["bytes"] or record.get("sha256") != info["sha256"]:
                raise ValueError(f"bound artifact identity differs: {record['id']}")
            if not record["path"].endswith(".pdf") and record.get("lines") != info["logical_records"]:
                raise ValueError(f"bound artifact record count differs: {record['id']}")
        elif bound:
            raise ValueError(f"admitted Chapter 14 artifact is unbound: {record['id']}")
        elif any(key in record for key in ("bytes", "sha256", "pages")):
            raise ValueError(f"pending Chapter 14 artifact leaks an unfrozen identity: {record['id']}")
    pdf = next(record for record in artifacts if record["id"] == "ARTIFACT-FAOA-ID-THROUGH-CH14-PDF")
    if bound:
        if pdf.get("pages") != generator.page_count(ROOT / generator.PDF_REL):
            raise ValueError("bound Chapter 14 PDF page count differs")
    elif pdf.get("binding_state") != "pending_final_artifact_binding":
        raise ValueError("pending Chapter 14 PDF state differs")


def validate() -> dict[str, Any]:
    records = {name: load_jsonl(name) for name in generator.JSONL_FILES}
    units = {record["id"]: record for record in records["units.jsonl"]}
    unit = units[CHAPTER_ID]
    bound = unit.get("admission_state") == "admitted"
    outputs, generated_summary = generator.build_outputs(bound)
    mismatches = [
        name for name, expected in outputs.items()
        if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != expected
    ]
    if mismatches:
        raise ValueError("deterministic round-trip differs: " + ", ".join(mismatches))

    with (BACKEND / "index_terms.csv").open(encoding="utf-8", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    all_records = [record for name in generator.JSONL_FILES for record in records[name]]
    ids = [record["id"] for record in all_records if record.get("id")]
    for static_name in (
        "assets.jsonl", "rights.jsonl", "concepts.jsonl", "concept_relations.jsonl",
        "resources.jsonl", "terminology_qa.jsonl",
    ):
        ids.extend(record["id"] for record in load_jsonl(static_name) if record.get("id"))
    ids.extend(row["id"] for row in index_rows if row.get("id"))
    duplicates = [stable_id for stable_id, count in collections.Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"global stable IDs are not unique: {duplicates[:5]}")
    id_set = set(ids)

    chapter_relations = [
        record for record in records["relations.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")
    ]
    unresolved = []
    external_prefixes = ("ERDMAN-FAOA-BIB-", "ERDMAN-FAOA-2015-LABEL-", "COURSE-O007")
    for record in records["relations.jsonl"]:
        for key in ("from_id", "to_id"):
            endpoint = record.get(key)
            if endpoint and endpoint not in id_set and not any(str(endpoint).startswith(prefix) for prefix in external_prefixes):
                unresolved.append((record["id"], key, endpoint))
    if unresolved:
        raise ValueError(f"relation endpoints unresolved: {unresolved[:5]}")

    semantic = [record for record in records["semantic_units.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")]
    segments = [record for record in records["segments.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")]
    kinds = collections.Counter(record["unit_kind"] for record in semantic)
    if len(semantic) != 69 or len(segments) != 86 or kinds != collections.Counter({
        "section": 3, "conv": 2, "defn": 19, "exam": 9, "exer": 2,
        "notn": 6, "prop": 24, "proof": 3, "cor": 1,
    }):
        raise ValueError(f"Chapter 14 semantic closure differs: {len(semantic)}/{len(segments)}/{kinds}")
    expected_state = "admitted" if bound else "qa_passed_pending_artifact_binding"
    if any(record.get("qa_state") != "passed" or record.get("translation_state") != expected_state for record in semantic + segments):
        raise ValueError("Chapter 14 semantic/segment state differs")

    ledger = json.loads((ROOT / generator.LEDGER_REL).read_text(encoding="utf-8"))
    formula_summary = validate_formula_maps(records["formula_map.jsonl"], ledger)
    validate_index(index_rows)
    corrections = [record for record in records["corrections.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    ledger_items = generator.ledger_records(ledger)
    if [record["id"] for record in corrections] != [record["id"] for record in ledger_items]:
        raise ValueError("Chapter 14 correction closure differs")
    ledger_sha = sha((ROOT / generator.LEDGER_REL).read_bytes())
    if any(record.get("ledger_sha256") != ledger_sha or record.get("qa_state") != "passed" for record in corrections):
        raise ValueError("Chapter 14 correction ledger binding differs")

    artifacts = [record for record in records["artifacts.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    qa_events = [record for record in records["qa_events.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    validate_artifacts(artifacts, bound)
    if len(qa_events) != 10 or any(record.get("model_id") != generator.MODEL_ID for record in qa_events):
        raise ValueError("Chapter 14 QA/model closure differs")
    if bound:
        admission = next(record for record in qa_events if record["id"] == "QA-CH14-ADMISSION-20260824")
        if admission.get("decision") != "admitted" or admission.get("result") != "pass":
            raise ValueError("Chapter 14 admission QA state differs")

    for record in records["terminology.jsonl"]:
        for field in ("source_term", "preferred"):
            value = record.get(field, "")
            if "\\index{" in value or "\n" in value or "\r" in value:
                raise ValueError(f"terminology field is contaminated: {record.get('id')} {field}")
    chapter_terms = [record for record in records["terminology.jsonl"] if record.get("introduced_in_unit") == CHAPTER_ID]
    if len(chapter_terms) != 21 or {record["id"] for record in chapter_terms} != set(generator.NEW_TERM_SPECS):
        raise ValueError("Chapter 14 new-term closure differs")
    required_terms = {
        "TERM-A-MODULE", "TERM-HILBERT-A-MODULE", "TERM-A-VALUED-SEMI-INNER-PRODUCT",
        "TERM-ADJOINTABLE", "TERM-OPPOSITE-ALGEBRA", "TERM-ANTIHOMOMORPHISM",
        "TERM-ESSENTIAL-IDEAL", "TERM-ZERO-SET", "TERM-COMPACTIFICATION",
        "TERM-ESSENTIAL-COMPACTIFICATION", "TERM-EMBEDDING", "TERM-MULTIPLIER-ALGEBRA",
    }
    if not required_terms.issubset({record["id"] for record in chapter_terms}):
        raise ValueError("Chapter 14 required controlled terminology is incomplete")
    if any("riesz" in (record.get("source_term", "") + record.get("preferred", "")).casefold() for record in chapter_terms):
        raise ValueError("Riesz terminology was incorrectly introduced in Chapter 14")
    term_relations = [record for record in chapter_relations if record.get("relation_type") == "uses_term"]
    if len(term_relations) != 36 or any(record.get("to_id") not in id_set for record in term_relations):
        raise ValueError("Chapter 14 defined-term relation closure differs")

    support = [record for record in records["exercise_support.jsonl"] if record.get("id", "").startswith(CHAPTER_ID + "-")]
    if len(support) != 2:
        raise ValueError("Chapter 14 exercise-support closure differs")
    for number, record in enumerate(support, 1):
        if (
            record.get("id") != f"{CHAPTER_ID}-EXERCISE-SUPPORT-{number:03d}"
            or record.get("upstream_solution_state") != "absent"
            or record.get("original_solution_state") != "queued_in_O001"
            or record.get("provenance") != "separately_authored_not_Erdman"
            or record.get("exercise_unit_id") not in id_set
        ):
            raise ValueError(f"Chapter 14 exercise-support provenance differs: {number}")
    support_relations = [record for record in chapter_relations if record.get("relation_type") == "has_exercise_support"]
    if len(support_relations) != 2 or {record["to_id"] for record in support_relations} != {record["id"] for record in support}:
        raise ValueError("Chapter 14 exercise-support relations differ")
    rights_relations = [record for record in chapter_relations if record.get("relation_type") == "licensed_under"]
    if len(rights_relations) != 1 or rights_relations[0].get("to_id") != generator.RIGHTS:
        raise ValueError("Chapter 14 rights relation differs")
    if len(chapter_relations) != 368:
        raise ValueError(f"Chapter 14 relation closure differs: {len(chapter_relations)}")

    manifest_sha = validate_manifest()
    aggregate_records = sum(len(records[name]) for name in generator.JSONL_FILES) + len(index_rows)
    return {
        "status": "pass", "unit_id": CHAPTER_ID,
        "binding_state": "bound" if bound else "pending_final_artifact_binding",
        "source_sha256": generator.EXPECTED_SOURCE[2], "target_sha256": generator.EXPECTED_TARGET[2],
        "master_sha256": generator.EXPECTED_MASTER[2], "model_id": generator.MODEL_ID,
        "chapter14": {
            "semantic_units": len(semantic), "segments": len(segments),
            "relations": len(chapter_relations), "formula_map": formula_summary,
            "index_terms": 79, "new_terms": len(chapter_terms), "corrections": len(corrections),
            "exercise_support": len(support), "qa_events": len(qa_events), "artifacts": len(artifacts),
        },
        "aggregate_records": aggregate_records, "global_stable_ids": "unique",
        "relation_endpoints": "resolved", "deterministic_round_trip": "pass",
        "chapter1_ch13_prefix_lock": "pass",
        "reference_resolution": generated_summary["reference_resolution"],
        "backend_manifest_sha256": manifest_sha,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true", help="verify the exact prefix and inputs without writing")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(generator.preflight(), ensure_ascii=False, sort_keys=True))
        return
    result = validate()
    payload = {
        "schema_version": "o008.backend-validation.v1", "timestamp": "2026-08-24",
        **result, "validator": file_identity(Path(__file__)),
    }
    output = ROOT / "qa/CH14_BACKEND_VALIDATION.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
