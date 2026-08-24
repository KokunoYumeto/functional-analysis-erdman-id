#!/usr/bin/env python3
"""Validate the admitted Chapter 13 backend append and Chapter 1--12 lock."""

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
import ch03_math  # noqa: E402
import check_ch05_translation as common  # noqa: E402
import generate_ch13_backend as generator  # noqa: E402


CHAPTER_ID = generator.CHAPTER_ID


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(name: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (BACKEND / name).read_text(encoding="utf-8").splitlines()]


def file_identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "logical_records": len(data.splitlines()),
        "sha256": sha(data),
    }


def validate_manifest() -> str:
    with (BACKEND / "BACKEND_MANIFEST.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    expected_names = sorted(
        path.name
        for path in BACKEND.iterdir()
        if path.is_file() and path.name != "BACKEND_MANIFEST.csv" and path.suffix != ".pyc"
    )
    if [row["relative_path"] for row in rows] != sorted(expected_names, key=str.casefold):
        raise ValueError("backend manifest inventory differs")
    for row in rows:
        data = (BACKEND / row["relative_path"]).read_bytes()
        if row["bytes"] != str(len(data)) or row["sha256"] != sha(data):
            raise ValueError(f"backend manifest identity differs: {row['relative_path']}")
    return sha((BACKEND / "BACKEND_MANIFEST.csv").read_bytes())


def validate_formula_maps(records: list[dict[str, Any]]) -> dict[str, int]:
    chapter = [record for record in records if record["id"].startswith(CHAPTER_ID + "-")]
    source = generator.SOURCE_PATH.read_text(encoding="ascii")
    target = generator.TARGET_PATH.read_text(encoding="utf-8")
    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if len(chapter) != 239:
        raise ValueError(f"Chapter 13 formula map count differs: {len(chapter)}")
    expected_ids = [f"{CHAPTER_ID}-MATHMAP-{number:04d}" for number in range(1, 240)]
    if [record["id"] for record in chapter] != expected_ids:
        raise ValueError("Chapter 13 formula-map ID/order differs")
    source_coverage: set[int] = set()
    insertion_count = classified_count = 0
    valid_corrections = {f"{CHAPTER_ID}-CORR-{number:03d}" for number in range(1, 7)}
    for target_index, record in enumerate(chapter):
        target_item = target_math[target_index]
        expected_target_id = f"{CHAPTER_ID}-ID-MATH-{target_index + 1:04d}"
        if record.get("target_formula_ids") != [expected_target_id]:
            raise ValueError(f"target formula ID differs: {record['id']}")
        if record.get("target_sha256") != [target_item["sha256"]]:
            raise ValueError(f"target formula hash differs: {record['id']}")
        if record.get("target_lines") != [[target_item["line_start"], target_item["line_end"]]]:
            raise ValueError(f"target formula lines differ: {record['id']}")
        source_indexes = []
        for stable_id in record.get("source_formula_ids", []):
            ordinal = int(stable_id.rsplit("-", 1)[1])
            if stable_id != f"{CHAPTER_ID}-SRC-MATH-{ordinal:04d}" or not 1 <= ordinal <= len(source_math):
                raise ValueError(f"source formula ID out of range: {stable_id}")
            source_indexes.append(ordinal - 1)
            source_coverage.add(ordinal - 1)
        if record.get("source_sha256") != [source_math[index]["sha256"] for index in source_indexes]:
            raise ValueError(f"source formula hashes differ: {record['id']}")
        if record.get("source_lines") != [
            [source_math[index]["line_start"], source_math[index]["line_end"]]
            for index in source_indexes
        ]:
            raise ValueError(f"source formula lines differ: {record['id']}")
        if not source_indexes:
            insertion_count += 1
        if record.get("correction_id"):
            classified_count += 1
            if record["correction_id"] not in valid_corrections:
                raise ValueError(f"unknown formula correction ID: {record['id']}")
    if source_coverage != set(range(237)):
        raise ValueError("formula maps do not cover all 237 source surfaces")
    if (insertion_count, classified_count) != (2, 5):
        raise ValueError(f"formula delta closure differs: {insertion_count}/{classified_count}")
    return {
        "records": len(chapter),
        "source_surfaces_covered": len(source_coverage),
        "target_insertions": insertion_count,
        "classified_delta_maps": classified_count,
    }


def validate_index(rows: list[dict[str, str]]) -> None:
    chapter = [row for row in rows if row["id"].startswith(CHAPTER_ID + "-")]
    source_indexes = common.macro(generator.SOURCE_PATH.read_text(encoding="ascii"), "index")
    target_indexes = common.macro(generator.TARGET_PATH.read_text(encoding="utf-8"), "index")
    if len(chapter) != 28:
        raise ValueError(f"Chapter 13 index row count differs: {len(chapter)}")
    for number, (row, source_item, target_item) in enumerate(
        zip(chapter, source_indexes, target_indexes, strict=True), 1
    ):
        expected = {
            "id": f"{CHAPTER_ID}-TERM-OCC-{number:04d}",
            "source_order": str(number),
            "source_line": str(source_item["line"]),
            "source_index_tex": source_item["argument"],
            "target_line": str(target_item["line"]),
            "target_index_tex": target_item["argument"],
            "source_sha256": sha(source_item["argument"].encode("ascii")),
            "target_sha256": sha(target_item["argument"].encode("utf-8")),
            "locale": "id-ID",
        }
        if any(row.get(key) != value for key, value in expected.items()):
            raise ValueError(f"Chapter 13 index occurrence differs: {number}")


def validate() -> dict[str, Any]:
    records = {name: load_jsonl(name) for name in generator.JSONL_FILES}
    units = {record["id"]: record for record in records["units.jsonl"]}
    unit = units[CHAPTER_ID]
    bound = unit.get("admission_state") == "admitted"
    outputs, generated_summary = generator.build_outputs(bound)
    mismatches = [
        name
        for name, expected in outputs.items()
        if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != expected
    ]
    if mismatches:
        raise ValueError("deterministic round-trip differs: " + ", ".join(mismatches))

    with (BACKEND / "index_terms.csv").open(encoding="utf-8", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    all_records = []
    for name in generator.JSONL_FILES:
        all_records.extend(records[name])
    ids = [record.get("id") for record in all_records if record.get("id")]
    for static_name in (
        "assets.jsonl",
        "rights.jsonl",
        "concepts.jsonl",
        "concept_relations.jsonl",
        "resources.jsonl",
        "terminology_qa.jsonl",
    ):
        ids.extend(record.get("id") for record in load_jsonl(static_name) if record.get("id"))
    ids.extend(row.get("id") for row in index_rows if row.get("id"))
    duplicates = [stable_id for stable_id, count in collections.Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"global stable IDs are not unique: {duplicates[:5]}")
    id_set = set(ids)

    relations = records["relations.jsonl"]
    chapter_relations = [record for record in relations if record["id"].startswith(CHAPTER_ID + "-")]
    unresolved = []
    for record in relations:
        for key in ("from_id", "to_id"):
            endpoint = record.get(key)
            external_prefixes = ("ERDMAN-FAOA-BIB-", "ERDMAN-FAOA-2015-LABEL-", "COURSE-O007")
            if endpoint and endpoint not in id_set and not any(
                str(endpoint).startswith(prefix) for prefix in external_prefixes
            ):
                unresolved.append((record["id"], key, endpoint))
    if unresolved:
        raise ValueError(f"relation endpoints unresolved: {unresolved[:5]}")

    semantic = [record for record in records["semantic_units.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")]
    segments = [record for record in records["segments.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")]
    kinds = collections.Counter(record["unit_kind"] for record in semantic)
    if len(semantic) != 35 or kinds["section"] != 3 or kinds["exer"] != 1 or kinds["proof"] != 2:
        raise ValueError(f"Chapter 13 semantic closure differs: {len(semantic)}/{kinds}")
    if any(record.get("qa_state") != "passed" for record in semantic + segments):
        raise ValueError("Chapter 13 semantic/segment QA state differs")
    expected_translation_state = "admitted" if bound else "qa_passed_pending_artifact_binding"
    if any(record.get("translation_state") != expected_translation_state for record in semantic + segments):
        raise ValueError("Chapter 13 semantic/segment translation state differs")

    formula_summary = validate_formula_maps(records["formula_map.jsonl"])
    validate_index(index_rows)

    ledger = json.loads((ROOT / generator.LEDGER_REL).read_text(encoding="utf-8"))
    corrections = [record for record in records["corrections.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    if len(corrections) != 6 or [record["id"] for record in corrections] != [
        record["id"] for record in ledger["records"]
    ]:
        raise ValueError("Chapter 13 correction closure differs")
    ledger_sha = sha((ROOT / generator.LEDGER_REL).read_bytes())
    if any(record.get("ledger_sha256") != ledger_sha or record.get("qa_state") != "passed" for record in corrections):
        raise ValueError("Chapter 13 correction ledger binding differs")

    artifacts = [record for record in records["artifacts.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    qa_events = [record for record in records["qa_events.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    if len(artifacts) != 15 or len(qa_events) != 10:
        raise ValueError(f"Chapter 13 artifact/QA closure differs: {len(artifacts)}/{len(qa_events)}")
    if bound:
        pdf_artifact = next(
            record for record in artifacts if record["id"] == "ARTIFACT-FAOA-ID-THROUGH-CH13-PDF"
        )
        if (
            pdf_artifact.get("bytes") != 2_031_973
            or pdf_artifact.get("pages") != 183
            or pdf_artifact.get("sha256") != "b7810718cb9a633c694aed126fc5c10786864650b076c2ad5bb7329191db3b65"
        ):
            raise ValueError("bound Chapter 13 PDF artifact differs")
        admission = next(record for record in qa_events if record["id"] == "QA-CH13-ADMISSION-20260824")
        if admission.get("decision") != "admitted" or admission.get("result") != "pass":
            raise ValueError("Chapter 13 admission QA event differs")

    for record in records["terminology.jsonl"]:
        for field in ("source_term", "preferred"):
            value = record.get(field, "")
            if "\\index{" in value or "\n" in value or "\r" in value:
                raise ValueError(f"terminology field is contaminated: {record.get('id')} {field}")
    chapter_terms = [record for record in records["terminology.jsonl"] if record.get("introduced_in_unit") == CHAPTER_ID]
    if len(chapter_terms) != 8:
        raise ValueError(f"Chapter 13 new-term count differs: {len(chapter_terms)}")
    state = next(record for record in chapter_terms if record["id"] == "TERM-STATE")
    if state.get("preferred") != "keadaan" or state.get("variants") != ["state"]:
        raise ValueError("state terminology record differs")
    term_relations = [record for record in chapter_relations if record.get("relation_type") == "uses_term"]
    if len(term_relations) != 13 or any(record.get("to_id") not in id_set for record in term_relations):
        raise ValueError("Chapter 13 defined-term relation closure differs")

    support = [
        record
        for record in records["exercise_support.jsonl"]
        if record.get("id") == f"{CHAPTER_ID}-EXERCISE-SUPPORT-001"
    ]
    if len(support) != 1:
        raise ValueError("Chapter 13 exercise-support record missing")
    support_record = support[0]
    if (
        support_record.get("upstream_solution_state") != "absent"
        or support_record.get("original_solution_state") != "queued_in_O001"
        or support_record.get("provenance") != "separately_authored_not_Erdman"
        or support_record.get("exercise_unit_id") not in id_set
    ):
        raise ValueError("Chapter 13 exercise-support provenance differs")
    support_relations = [
        record for record in chapter_relations if record.get("relation_type") == "has_exercise_support"
    ]
    if len(support_relations) != 1 or support_relations[0].get("to_id") != support_record["id"]:
        raise ValueError("Chapter 13 exercise-support relation differs")

    rights_relations = [record for record in chapter_relations if record.get("relation_type") == "licensed_under"]
    if len(rights_relations) != 1 or rights_relations[0].get("to_id") != generator.RIGHTS:
        raise ValueError("Chapter 13 rights relation differs")

    manifest_sha = validate_manifest()
    aggregate_records = sum(len(records[name]) for name in generator.JSONL_FILES) + len(index_rows)
    return {
        "status": "pass",
        "unit_id": CHAPTER_ID,
        "binding_state": "bound" if bound else "pending_final_artifact_binding",
        "source_sha256": generator.EXPECTED_SOURCE[2],
        "target_sha256": generator.EXPECTED_TARGET[2],
        "master_sha256": generator.EXPECTED_MASTER[2],
        "chapter13": {
            "semantic_units": len(semantic),
            "segments": len(segments),
            "relations": len(chapter_relations),
            "formula_map": formula_summary,
            "index_terms": 28,
            "new_terms": len(chapter_terms),
            "corrections": len(corrections),
            "exercise_support": 1,
            "qa_events": len(qa_events),
            "artifacts": len(artifacts),
        },
        "aggregate_records": aggregate_records,
        "global_stable_ids": "unique",
        "relation_endpoints": "resolved",
        "deterministic_round_trip": "pass",
        "chapter1_ch12_prefix_lock": "pass",
        "reference_resolution": generated_summary["reference_resolution"],
        "backend_manifest_sha256": manifest_sha,
    }


def main() -> None:
    result = validate()
    payload = {
        "schema_version": "o008.backend-validation.v1",
        "timestamp": "2026-08-24",
        **result,
        "validator": file_identity(Path(__file__)),
    }
    output = ROOT / "qa/CH13_BACKEND_VALIDATION.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
