#!/usr/bin/env python3
"""Validate the Chapter 16 append and exact Chapter 1--15 backend prefix."""

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
import generate_ch16_backend as generator  # noqa: E402


CHAPTER_ID = generator.CHAPTER_ID
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"


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
        (path.name for path in BACKEND.iterdir() if path.is_file() and path.name != "BACKEND_MANIFEST.csv" and path.suffix != ".pyc"),
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
    prefix = f"{CHAPTER_ID}-{infix}-"
    if not stable_id.startswith(prefix):
        raise ValueError(f"wrong formula namespace: {stable_id}")
    value = int(stable_id.removeprefix(prefix))
    if stable_id != f"{prefix}{value:04d}" or not 1 <= value <= maximum:
        raise ValueError(f"formula ordinal out of range: {stable_id}")
    return value


def validate_formula_maps(records: list[dict[str, Any]], ledger_ids: set[str]) -> dict[str, int]:
    chapter = [item for item in records if item["id"].startswith(CHAPTER_ID + "-")]
    source_math = generator.ch03_math.extract_math(generator.SOURCE_PATH.read_text(encoding="ascii"), "ascii")
    target_math = generator.ch03_math.extract_math(generator.TARGET_PATH.read_text(encoding="utf-8"), "utf-8")
    expected_ids = [f"{CHAPTER_ID}-MATHMAP-{number:04d}" for number in range(1, 701)] + [
        f"{CHAPTER_ID}-MATHMAP-SOURCE-DELETION-0001"
    ]
    if len(source_math) != 702 or len(target_math) != 700 or [x["id"] for x in chapter] != expected_ids:
        raise ValueError("Chapter 16 formula ID/count closure differs")

    source_coverage: list[int] = []
    target_coverage: list[int] = []
    counters: collections.Counter[str] = collections.Counter()
    correction_ids: set[str] = set()
    correction_target_ordinals: dict[str, list[int]] = collections.defaultdict(list)
    deletion_ordinals: list[int] = []
    for record in chapter:
        source_ordinals = [ordinal(x, "SRC-MATH", 702) for x in record.get("source_formula_ids", [])]
        target_ordinals = [ordinal(x, "ID-MATH", 700) for x in record.get("target_formula_ids", [])]
        if not source_ordinals and not target_ordinals:
            raise ValueError(f"formula map without endpoints: {record['id']}")
        source_coverage.extend(source_ordinals)
        target_coverage.extend(target_ordinals)
        source_indexes = [value - 1 for value in source_ordinals]
        target_indexes = [value - 1 for value in target_ordinals]
        if record.get("source_sha256") != [source_math[i]["sha256"] for i in source_indexes]:
            raise ValueError(f"source formula hash differs: {record['id']}")
        if record.get("target_sha256") != [target_math[i]["sha256"] for i in target_indexes]:
            raise ValueError(f"target formula hash differs: {record['id']}")
        if record.get("source_lines") != [[source_math[i]["line_start"], source_math[i]["line_end"]] for i in source_indexes]:
            raise ValueError(f"source formula locator differs: {record['id']}")
        if record.get("target_lines") != [[target_math[i]["line_start"], target_math[i]["line_end"]] for i in target_indexes]:
            raise ValueError(f"target formula locator differs: {record['id']}")

        delta = record.get("delta_class")
        correction_id = record.get("correction_id")
        if delta == "classified_source_correction":
            counters["correction"] += 1
            if correction_id not in ledger_ids:
                raise ValueError(f"formula cites unknown correction: {record['id']}")
            correction_ids.add(correction_id)
            correction_target_ordinals[correction_id].extend(target_ordinals)
            if not source_ordinals:
                counters["insertion"] += 1
            if not target_ordinals:
                counters["deletion"] += 1
                deletion_ordinals.extend(source_ordinals)
        elif delta == "localized_prose_translation":
            counters["localized"] += 1
            if correction_id:
                raise ValueError(f"localized map cites correction: {record['id']}")
        elif delta == "typographic_semantic_normalization":
            counters["semantic_normalization"] += 1
            if correction_id:
                raise ValueError(f"typographic map cites correction: {record['id']}")
        elif record.get("alignment") == "preserved_exact_after_text_aware_whitespace_normalization":
            counters["exact"] += 1
            if correction_id:
                raise ValueError(f"exact map cites correction: {record['id']}")
        else:
            raise ValueError(f"unclassified formula map: {record['id']}")

    if sorted(source_coverage) != list(range(1, 703)) or len(source_coverage) != len(set(source_coverage)):
        raise ValueError("Chapter 16 source formula coverage is not exact-once")
    if target_coverage != list(range(1, 701)):
        raise ValueError("Chapter 16 target formula coverage is not exact-once/in-order")
    expected_counters = collections.Counter({
        "exact": 684, "localized": 3, "semantic_normalization": 1,
        "correction": 13, "insertion": 1, "deletion": 1,
    })
    expected_correction_ids = {
        f"{CHAPTER_ID}-CORR-{number:03d}" for number in (2, 4, 6, 8, 10, 11, 12, 15)
    }
    expected_targets = {
        f"{CHAPTER_ID}-CORR-002": [30, 38], f"{CHAPTER_ID}-CORR-004": [150],
        f"{CHAPTER_ID}-CORR-006": [180], f"{CHAPTER_ID}-CORR-008": [199, 201],
        f"{CHAPTER_ID}-CORR-010": [245], f"{CHAPTER_ID}-CORR-011": [354],
        f"{CHAPTER_ID}-CORR-012": [366, 367, 368, 371], f"{CHAPTER_ID}-CORR-015": [],
    }
    if counters != expected_counters or correction_ids != expected_correction_ids:
        raise ValueError(f"Chapter 16 formula classification differs: {counters}/{sorted(correction_ids)}")
    if dict(correction_target_ordinals) != expected_targets or deletion_ordinals != [660]:
        raise ValueError(f"Chapter 16 correction formula ordinals differ: {dict(correction_target_ordinals)}/{deletion_ordinals}")
    return {
        "records": 701, "source_surfaces_covered": 702, "target_surfaces_covered": 700,
        "exact_maps": 684, "localized_maps": 3, "semantic_normalizations": 1,
        "classified_correction_maps": 13, "target_insertions": 1, "source_only_deletions": 1,
    }


def validate_index(rows: list[dict[str, str]]) -> None:
    chapter = [row for row in rows if row["id"].startswith(CHAPTER_ID + "-")]
    source_indexes = generator.common.macro(generator.SOURCE_PATH.read_text(encoding="ascii"), "index")
    target_indexes = generator.common.macro(generator.TARGET_PATH.read_text(encoding="utf-8"), "index")
    if len(chapter) != 107 or len(source_indexes) != 107 or len(target_indexes) != 107:
        raise ValueError("Chapter 16 index closure differs")
    for number, (row, source_item, target_item) in enumerate(zip(chapter, source_indexes, target_indexes, strict=True), 1):
        expected = {
            "id": f"{CHAPTER_ID}-TERM-OCC-{number:04d}", "source_order": str(number),
            "source_line": str(source_item["line"]), "source_index_tex": source_item["argument"],
            "target_line": str(target_item["line"]), "target_index_tex": target_item["argument"],
            "source_sha256": sha(source_item["argument"].encode("ascii")),
            "target_sha256": sha(target_item["argument"].encode("utf-8")), "locale": "id-ID",
        }
        if any(row.get(key) != value for key, value in expected.items()):
            raise ValueError(f"Chapter 16 index occurrence differs: {number}")


def validate() -> dict[str, Any]:
    if generator.MODEL_ID != MODEL_ID:
        raise ValueError("model identity differs")
    records = {name: load_jsonl(name) for name in generator.JSONL_FILES}
    unit = next(item for item in records["units.jsonl"] if item.get("id") == CHAPTER_ID)
    bound = unit.get("admission_state") == "admitted"
    outputs, summary = generator.build_outputs(bound)
    mismatches = [name for name, data in outputs.items() if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != data]
    if mismatches:
        raise ValueError("deterministic round-trip differs: " + ", ".join(mismatches))

    with (BACKEND / "index_terms.csv").open(encoding="utf-8", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
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
        raise ValueError(f"global stable IDs are not unique: {duplicates[:5]}")
    id_set = set(ids)

    unresolved = []
    external_prefixes = ("ERDMAN-FAOA-BIB-", "ERDMAN-FAOA-2015-LABEL-", "COURSE-O007")
    for relation in records["relations.jsonl"]:
        for key in ("from_id", "to_id"):
            endpoint = relation.get(key)
            if endpoint and endpoint not in id_set and not any(str(endpoint).startswith(prefix) for prefix in external_prefixes):
                unresolved.append((relation["id"], key, endpoint))
    if unresolved:
        raise ValueError(f"relation endpoints unresolved: {unresolved[:5]}")

    semantic = [item for item in records["semantic_units.jsonl"] if item["id"].startswith(CHAPTER_ID + "-")]
    segments = [item for item in records["segments.jsonl"] if item["id"].startswith(CHAPTER_ID + "-")]
    kinds = collections.Counter(item["unit_kind"] for item in semantic)
    expected_kinds = collections.Counter({
        "section": 4, "prop": 38, "proof": 31, "defn": 21, "exam": 15,
        "thm": 8, "cor": 6, "notn": 3, "conv": 1,
    })
    if len(semantic) != 127 or len(segments) != 141 or kinds != expected_kinds:
        raise ValueError(f"Chapter 16 semantic closure differs: {len(semantic)}/{len(segments)}/{kinds}")
    state = "admitted" if bound else "qa_passed_pending_artifact_binding"
    if any(item.get("qa_state") != "passed" or item.get("translation_state") != state for item in semantic + segments):
        raise ValueError("Chapter 16 semantic/segment state differs")

    ledger_items, ledger_sha = generator.ledger_records()
    ledger_ids = {item["id"] for item in ledger_items}
    formula_summary = validate_formula_maps(records["formula_map.jsonl"], ledger_ids)
    validate_index(index_rows)
    corrections = [item for item in records["corrections.jsonl"] if item.get("unit_id") == CHAPTER_ID]
    if [item["id"] for item in corrections] != [item["id"] for item in ledger_items]:
        raise ValueError("Chapter 16 correction closure differs")
    if any(item.get("ledger_sha256") != ledger_sha or item.get("qa_state") != "passed" for item in corrections):
        raise ValueError("Chapter 16 correction binding differs")

    chapter_relations = [item for item in records["relations.jsonl"] if item["id"].startswith(CHAPTER_ID + "-")]
    if len(chapter_relations) != 601:
        raise ValueError(f"Chapter 16 relation closure differs: {len(chapter_relations)}")
    rights = [item for item in chapter_relations if item.get("relation_type") == "licensed_under"]
    if len(rights) != 1 or rights[0].get("to_id") != generator.RIGHTS:
        raise ValueError("Chapter 16 rights relation differs")
    term_relations = [item for item in chapter_relations if item.get("relation_type") == "uses_term"]
    chapter_terms = [item for item in records["terminology.jsonl"] if item.get("introduced_in_unit") == CHAPTER_ID]
    if len(term_relations) != 29 or len(chapter_terms) != 21 or {item["id"] for item in chapter_terms} != set(generator.NEW_TERM_SPECS):
        raise ValueError("Chapter 16 terminology closure differs")
    if any(item.get("to_id") not in id_set for item in term_relations):
        raise ValueError("Chapter 16 term relation endpoint differs")
    for item in chapter_terms:
        for field in ("source_term", "preferred"):
            if "\\index{" in item.get(field, "") or "\n" in item.get(field, "") or "\r" in item.get(field, ""):
                raise ValueError(f"terminology field contaminated: {item['id']}")

    support = [item for item in records["exercise_support.jsonl"] if item.get("id", "").startswith(CHAPTER_ID + "-")]
    if support or any(item.get("relation_type") == "has_exercise_support" for item in chapter_relations):
        raise ValueError("Chapter 16 must not invent exercise support")
    artifacts = [item for item in records["artifacts.jsonl"] if item.get("unit_id") == CHAPTER_ID]
    qa_events = [item for item in records["qa_events.jsonl"] if item.get("unit_id") == CHAPTER_ID]
    if len(artifacts) != 15 or len(qa_events) != 10 or any(item.get("model_id") != MODEL_ID for item in qa_events):
        raise ValueError("Chapter 16 artifact/QA/model closure differs")
    for artifact in artifacts:
        if artifact.get("binding_state") == "bound":
            info = file_identity(ROOT / artifact["path"])
            if artifact.get("bytes") != info["bytes"] or artifact.get("sha256") != info["sha256"]:
                raise ValueError(f"bound artifact identity differs: {artifact['id']}")
        elif bound:
            raise ValueError(f"admitted Chapter 16 artifact remains pending: {artifact['id']}")

    manifest_sha = validate_manifest()
    aggregate_records = sum(len(records[name]) for name in generator.JSONL_FILES) + len(index_rows)
    return {
        "status": "pass", "unit_id": CHAPTER_ID,
        "binding_state": "bound" if bound else "pending_final_artifact_binding",
        "source_sha256": generator.EXPECTED_SOURCE[2], "target_sha256": generator.EXPECTED_TARGET[2],
        "master_sha256": generator.EXPECTED_MASTER[2], "model_id": MODEL_ID,
        "chapter16": {
            "semantic_units": len(semantic), "segments": len(segments), "relations": len(chapter_relations),
            "formula_map": formula_summary, "index_terms": 107, "new_terms": len(chapter_terms),
            "term_uses": len(term_relations), "corrections": len(corrections), "exercise_support": 0,
            "qa_events": len(qa_events), "artifacts": len(artifacts),
        },
        "aggregate_records": aggregate_records, "global_stable_ids": "unique",
        "relation_endpoints": "resolved", "deterministic_round_trip": "pass",
        "chapter1_ch15_prefix_lock": "pass", "reference_resolution": summary["reference_resolution"],
        "backend_manifest_sha256": manifest_sha,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(generator.preflight(), ensure_ascii=False, sort_keys=True))
        return
    result = validate()
    payload = {
        "schema_version": "o008.backend-validation.v1", "timestamp": "2026-08-24",
        **result, "validator": file_identity(Path(__file__)),
    }
    output = ROOT / "qa/CH16_BACKEND_VALIDATION.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
