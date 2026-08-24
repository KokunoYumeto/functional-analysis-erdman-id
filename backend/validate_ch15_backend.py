#!/usr/bin/env python3
"""Validate the Chapter 15 backend append and exact Chapter 1--14 prefix."""

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
import generate_ch15_backend as generator  # noqa: E402


CHAPTER_ID = generator.CHAPTER_ID
EXPECTED_MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"


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


def formula_ordinals(stable_ids: list[str], infix: str, maximum: int) -> list[int]:
    ordinals: list[int] = []
    for stable_id in stable_ids:
        prefix = f"{CHAPTER_ID}-{infix}-"
        if not stable_id.startswith(prefix):
            raise ValueError(f"formula stable ID has the wrong namespace: {stable_id}")
        ordinal = int(stable_id.removeprefix(prefix))
        if stable_id != f"{prefix}{ordinal:04d}" or not 1 <= ordinal <= maximum:
            raise ValueError(f"formula stable ID is out of range: {stable_id}")
        ordinals.append(ordinal)
    return ordinals


def validate_formula_maps(
    records: list[dict[str, Any]], ledger: dict[str, Any]
) -> dict[str, int]:
    chapter = [record for record in records if record["id"].startswith(CHAPTER_ID + "-")]
    source_math = ch03_math.extract_math(generator.SOURCE_PATH.read_text(encoding="ascii"), "ascii")
    target_math = ch03_math.extract_math(generator.TARGET_PATH.read_text(encoding="utf-8"), "utf-8")
    if len(source_math) != 203 or len(target_math) != 204 or len(chapter) != 205:
        raise ValueError(
            "Chapter 15 formula closure differs: "
            f"{len(source_math)}/{len(target_math)}/{len(chapter)}"
        )
    expected_ids = [f"{CHAPTER_ID}-MATHMAP-{number:04d}" for number in range(1, 205)]
    expected_ids.append(f"{CHAPTER_ID}-MATHMAP-SOURCE-DELETION-0001")
    if [record["id"] for record in chapter] != expected_ids:
        raise ValueError("Chapter 15 formula-map ID/order differs")

    valid_corrections = {
        record["id"] for record in generator.ledger_records(ledger)
        if record.get("affects_math") is True
    }
    if len(valid_corrections) != 5:
        raise ValueError("Chapter 15 formula-affecting correction closure differs")

    source_coverage: list[int] = []
    target_coverage: list[int] = []
    insertion_count = deletion_count = replacement_count = 0
    localized_count = exact_count = 0
    mapped_corrections: set[str] = set()
    insertion_ordinals: set[int] = set()
    replacement_ordinals: set[int] = set()
    localized_ordinals: set[int] = set()
    deletion_ordinals: set[int] = set()
    for record in chapter:
        source_ordinals = formula_ordinals(record.get("source_formula_ids", []), "SRC-MATH", 203)
        target_ordinals = formula_ordinals(record.get("target_formula_ids", []), "ID-MATH", 204)
        if len(source_ordinals) > 1 or len(target_ordinals) > 1:
            raise ValueError(f"Chapter 15 formula map is not atomic: {record['id']}")
        if not source_ordinals and not target_ordinals:
            raise ValueError(f"Chapter 15 formula map has neither endpoint: {record['id']}")

        source_indexes = [ordinal - 1 for ordinal in source_ordinals]
        target_indexes = [ordinal - 1 for ordinal in target_ordinals]
        source_coverage.extend(source_ordinals)
        target_coverage.extend(target_ordinals)
        if record.get("source_sha256") != [source_math[index]["sha256"] for index in source_indexes]:
            raise ValueError(f"source formula hash differs: {record['id']}")
        if record.get("source_lines") != [
            [source_math[index]["line_start"], source_math[index]["line_end"]]
            for index in source_indexes
        ]:
            raise ValueError(f"source formula lines differ: {record['id']}")
        if record.get("target_sha256") != [target_math[index]["sha256"] for index in target_indexes]:
            raise ValueError(f"target formula hash differs: {record['id']}")
        if record.get("target_lines") != [
            [target_math[index]["line_start"], target_math[index]["line_end"]]
            for index in target_indexes
        ]:
            raise ValueError(f"target formula lines differ: {record['id']}")

        correction_id = record.get("correction_id")
        if correction_id:
            mapped_corrections.add(correction_id)
            if correction_id not in valid_corrections:
                raise ValueError(f"unknown formula correction: {record['id']}")
        if not source_ordinals:
            insertion_count += 1
            insertion_ordinals.update(target_ordinals)
            if not correction_id or record.get("delta_class") != "classified_source_correction":
                raise ValueError(f"unclassified Chapter 15 target insertion: {record['id']}")
        elif not target_ordinals:
            deletion_count += 1
            deletion_ordinals.update(source_ordinals)
            if not correction_id or record.get("delta_class") != "classified_source_correction":
                raise ValueError(f"unclassified Chapter 15 source deletion: {record['id']}")
        elif record.get("alignment") == "reviewed_source_correction_replacement":
            replacement_count += 1
            replacement_ordinals.update(target_ordinals)
            if not correction_id or record.get("delta_class") != "classified_source_correction":
                raise ValueError(f"unclassified Chapter 15 correction replacement: {record['id']}")
        elif record.get("delta_class") == "localized_prose_translation":
            localized_count += 1
            localized_ordinals.update(target_ordinals)
            if correction_id:
                raise ValueError(f"localized Chapter 15 formula incorrectly cites correction: {record['id']}")
        elif record.get("alignment") == "preserved_exact_after_text_aware_whitespace_normalization":
            exact_count += 1
            if correction_id:
                raise ValueError(f"exact Chapter 15 formula incorrectly cites correction: {record['id']}")
        else:
            raise ValueError(f"unclassified Chapter 15 formula map: {record['id']}")

    if sorted(source_coverage) != list(range(1, 204)) or len(source_coverage) != len(set(source_coverage)):
        raise ValueError("Chapter 15 formula maps do not cover each source surface once in order")
    if target_coverage != list(range(1, 205)):
        raise ValueError("Chapter 15 formula maps do not cover each target surface once in order")
    expected = (
        insertion_count == 2 and deletion_count == 1 and replacement_count == 2
        and localized_count == 7 and exact_count == 193
        and mapped_corrections == valid_corrections
        and insertion_ordinals == {1, 52}
        and replacement_ordinals == {19, 35}
        and localized_ordinals == {4, 9, 14, 16, 21, 26, 31}
        and deletion_ordinals == {44}
    )
    if not expected:
        raise ValueError(
            "Chapter 15 formula delta closure differs: "
            f"{insertion_count}/{deletion_count}/{replacement_count}/{localized_count}/"
            f"{exact_count}/{sorted(mapped_corrections)}/"
            f"{sorted(insertion_ordinals)}/{sorted(replacement_ordinals)}/"
            f"{sorted(localized_ordinals)}/{sorted(deletion_ordinals)}"
        )
    return {
        "records": 205, "source_surfaces_covered": 203,
        "target_surfaces_covered": 204, "target_insertions": 2,
        "source_only_deletions": 1, "classified_source_correction_replacements": 2,
        "localized_prose_translation_maps": 7, "exact_maps": 193,
    }


def validate_index(rows: list[dict[str, str]]) -> None:
    chapter = [row for row in rows if row["id"].startswith(CHAPTER_ID + "-")]
    source_indexes = common.macro(generator.SOURCE_PATH.read_text(encoding="ascii"), "index")
    target_indexes = common.macro(generator.TARGET_PATH.read_text(encoding="utf-8"), "index")
    if len(chapter) != 46 or len(source_indexes) != 46 or len(target_indexes) != 46:
        raise ValueError("Chapter 15 index closure differs")
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
            raise ValueError(f"Chapter 15 index occurrence differs: {number}")


def validate_artifacts(artifacts: list[dict[str, Any]], bound: bool) -> None:
    if len(artifacts) != 15:
        raise ValueError(f"Chapter 15 artifact closure differs: {len(artifacts)}")
    for record in artifacts:
        if record.get("binding_state") == "bound":
            path = ROOT / record["path"]
            info = file_identity(path)
            if record.get("bytes") != info["bytes"] or record.get("sha256") != info["sha256"]:
                raise ValueError(f"bound artifact identity differs: {record['id']}")
            if not record["path"].endswith(".pdf") and record.get("lines") != info["logical_records"]:
                raise ValueError(f"bound artifact record count differs: {record['id']}")
        elif bound:
            raise ValueError(f"admitted Chapter 15 artifact is unbound: {record['id']}")
        elif any(key in record for key in ("bytes", "sha256", "pages")):
            raise ValueError(f"pending Chapter 15 artifact leaks an unfrozen identity: {record['id']}")
    pdf = next(record for record in artifacts if record["id"] == "ARTIFACT-FAOA-ID-THROUGH-CH15-PDF")
    if bound:
        if pdf.get("pages") != generator.page_count(ROOT / generator.PDF_REL):
            raise ValueError("bound Chapter 15 PDF page count differs")
    elif pdf.get("binding_state") != "pending_final_artifact_binding":
        raise ValueError("pending Chapter 15 PDF state differs")


def validate() -> dict[str, Any]:
    if generator.MODEL_ID != EXPECTED_MODEL_ID:
        raise ValueError(f"Chapter 15 model identity differs: {generator.MODEL_ID!r}")
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
            if endpoint and endpoint not in id_set and not any(
                str(endpoint).startswith(prefix) for prefix in external_prefixes
            ):
                unresolved.append((record["id"], key, endpoint))
    if unresolved:
        raise ValueError(f"relation endpoints unresolved: {unresolved[:5]}")

    semantic = [record for record in records["semantic_units.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")]
    segments = [record for record in records["segments.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")]
    kinds = collections.Counter(record["unit_kind"] for record in semantic)
    expected_kinds = collections.Counter({
        "section": 4, "prop": 16, "proof": 13, "exam": 8, "defn": 6,
        "lem": 3, "cor": 2, "thm": 1, "notn": 1,
    })
    if len(semantic) != 54 or len(segments) != 68 or kinds != expected_kinds:
        raise ValueError(f"Chapter 15 semantic closure differs: {len(semantic)}/{len(segments)}/{kinds}")
    expected_state = "admitted" if bound else "qa_passed_pending_artifact_binding"
    if any(
        record.get("qa_state") != "passed" or record.get("translation_state") != expected_state
        for record in semantic + segments
    ):
        raise ValueError("Chapter 15 semantic/segment state differs")

    ledger = json.loads((ROOT / generator.LEDGER_REL).read_text(encoding="utf-8"))
    formula_summary = validate_formula_maps(records["formula_map.jsonl"], ledger)
    validate_index(index_rows)
    corrections = [record for record in records["corrections.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    ledger_items = generator.ledger_records(ledger)
    if len(corrections) != 9 or [record["id"] for record in corrections] != [
        record["id"] for record in ledger_items
    ]:
        raise ValueError("Chapter 15 correction closure differs")
    ledger_sha = sha((ROOT / generator.LEDGER_REL).read_bytes())
    if any(
        record.get("ledger_sha256") != ledger_sha or record.get("qa_state") != "passed"
        for record in corrections
    ):
        raise ValueError("Chapter 15 correction ledger binding differs")

    artifacts = [record for record in records["artifacts.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    qa_events = [record for record in records["qa_events.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    validate_artifacts(artifacts, bound)
    if len(qa_events) != 10 or any(record.get("model_id") != EXPECTED_MODEL_ID for record in qa_events):
        raise ValueError("Chapter 15 QA/model closure differs")
    if bound:
        admission = next(record for record in qa_events if record["id"] == "QA-CH15-ADMISSION-20260824")
        if admission.get("decision") != "admitted" or admission.get("result") != "pass":
            raise ValueError("Chapter 15 admission QA state differs")

    for record in records["terminology.jsonl"]:
        for field in ("source_term", "preferred"):
            value = record.get(field, "")
            if "\\index{" in value or "\n" in value or "\r" in value:
                raise ValueError(f"terminology field is contaminated: {record.get('id')} {field}")
    chapter_terms = [record for record in records["terminology.jsonl"] if record.get("introduced_in_unit") == CHAPTER_ID]
    if len(chapter_terms) != 9 or {record["id"] for record in chapter_terms} != set(generator.NEW_TERM_SPECS):
        raise ValueError("Chapter 15 new-term closure differs")
    inherited_terms = {"TERM-COKERNEL", "TERM-CODIMENSION"}
    if not inherited_terms.issubset(id_set) or inherited_terms & {record["id"] for record in chapter_terms}:
        raise ValueError("Chapter 15 inherited terminology closure differs")
    term_relations = [record for record in chapter_relations if record.get("relation_type") == "uses_term"]
    if len(term_relations) != 11 or any(record.get("to_id") not in id_set for record in term_relations):
        raise ValueError("Chapter 15 defined-term relation closure differs")
    if not inherited_terms.issubset({record.get("to_id") for record in term_relations}):
        raise ValueError("Chapter 15 inherited term uses are missing")

    support = [record for record in records["exercise_support.jsonl"] if record.get("id", "").startswith(CHAPTER_ID + "-")]
    if support:
        raise ValueError(f"Chapter 15 must not invent exercise support: {len(support)}")
    support_relations = [
        record for record in chapter_relations if record.get("relation_type") == "has_exercise_support"
    ]
    if support_relations:
        raise ValueError("Chapter 15 must not invent exercise-support relations")
    rights_relations = [record for record in chapter_relations if record.get("relation_type") == "licensed_under"]
    if len(rights_relations) != 1 or rights_relations[0].get("to_id") != generator.RIGHTS:
        raise ValueError("Chapter 15 rights relation differs")
    if len(chapter_relations) != 312:
        raise ValueError(f"Chapter 15 relation closure differs: {len(chapter_relations)}")

    manifest_sha = validate_manifest()
    aggregate_records = sum(len(records[name]) for name in generator.JSONL_FILES) + len(index_rows)
    return {
        "status": "pass", "unit_id": CHAPTER_ID,
        "binding_state": "bound" if bound else "pending_final_artifact_binding",
        "source_sha256": generator.EXPECTED_SOURCE[2], "target_sha256": generator.EXPECTED_TARGET[2],
        "master_sha256": generator.EXPECTED_MASTER[2], "model_id": generator.MODEL_ID,
        "chapter15": {
            "semantic_units": len(semantic), "segments": len(segments),
            "relations": len(chapter_relations), "formula_map": formula_summary,
            "index_terms": 46, "new_terms": len(chapter_terms), "term_uses": len(term_relations),
            "corrections": len(corrections), "exercise_support": len(support),
            "qa_events": len(qa_events), "artifacts": len(artifacts),
        },
        "aggregate_records": aggregate_records, "global_stable_ids": "unique",
        "relation_endpoints": "resolved", "deterministic_round_trip": "pass",
        "chapter1_ch14_prefix_lock": "pass",
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
    output = ROOT / "qa/CH15_BACKEND_VALIDATION.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
