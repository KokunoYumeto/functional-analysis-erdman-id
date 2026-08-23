#!/usr/bin/env python3
"""Validate the Chapter 12 modular-backend append and its locked prefix."""

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
import generate_ch12_backend as generator  # noqa: E402
import check_ch05_translation as common  # noqa: E402


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
    if len(chapter) != 931:
        raise ValueError(f"Chapter 12 formula map count differs: {len(chapter)}")
    expected_ids = [f"{CHAPTER_ID}-MATHMAP-{number:04d}" for number in range(1, 932)]
    if [record["id"] for record in chapter] != expected_ids:
        raise ValueError("Chapter 12 formula-map ID/order differs")
    source_coverage: set[int] = set()
    insertion_count = 0
    classified_count = 0
    for target_index, record in enumerate(chapter):
        target_item = target_math[target_index]
        expected_target_id = f"{CHAPTER_ID}-ID-MATH-{target_index + 1:04d}"
        if record.get("target_formula_ids") != [expected_target_id]:
            raise ValueError(f"target formula ID differs: {record['id']}")
        if record.get("target_sha256") != [target_item["sha256"]] or record.get("target_lines") != [[target_item["line_start"], target_item["line_end"]]]:
            raise ValueError(f"target formula binding differs: {record['id']}")
        source_ids = record.get("source_formula_ids", [])
        source_indexes = []
        for stable_id in source_ids:
            try:
                ordinal = int(stable_id.rsplit("-", 1)[1])
            except Exception as exc:
                raise ValueError(f"malformed source formula ID: {stable_id}") from exc
            if stable_id != f"{CHAPTER_ID}-SRC-MATH-{ordinal:04d}" or not 1 <= ordinal <= len(source_math):
                raise ValueError(f"source formula ID out of range: {stable_id}")
            source_indexes.append(ordinal - 1)
            source_coverage.add(ordinal - 1)
        expected_source_hashes = [source_math[index]["sha256"] for index in source_indexes]
        expected_source_lines = [[source_math[index]["line_start"], source_math[index]["line_end"]] for index in source_indexes]
        if record.get("source_sha256") != expected_source_hashes or record.get("source_lines") != expected_source_lines:
            raise ValueError(f"source formula binding differs: {record['id']}")
        if not source_ids:
            insertion_count += 1
        if record.get("correction_id"):
            classified_count += 1
    if source_coverage != set(range(927)):
        raise ValueError("formula maps do not cover all 927 source surfaces")
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
    if len(chapter) != 102:
        raise ValueError(f"Chapter 12 index row count differs: {len(chapter)}")
    for number, (row, source_item, target_item) in enumerate(zip(chapter, source_indexes, target_indexes, strict=True), 1):
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
            raise ValueError(f"Chapter 12 index occurrence differs: {number}")


def validate() -> dict[str, Any]:
    records = {name: load_jsonl(name) for name in generator.JSONL_FILES}
    units = {record["id"]: record for record in records["units.jsonl"]}
    unit = units[CHAPTER_ID]
    bound = unit.get("admission_state") == "admitted"
    outputs, generated_summary = generator.build_outputs(bound)
    mismatches = [name for name, expected in outputs.items() if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != expected]
    if mismatches:
        raise ValueError("deterministic round-trip differs: " + ", ".join(mismatches))

    all_records = []
    for name in generator.JSONL_FILES:
        all_records.extend(records[name])
    ids = [record.get("id") for record in all_records if record.get("id")]
    for static_name in ("assets.jsonl", "rights.jsonl", "concepts.jsonl", "concept_relations.jsonl", "resources.jsonl", "terminology_qa.jsonl"):
        ids.extend(record.get("id") for record in load_jsonl(static_name) if record.get("id"))
    duplicate_ids = [stable_id for stable_id, count in collections.Counter(ids).items() if count > 1]
    if duplicate_ids:
        raise ValueError(f"global stable IDs are not unique: {duplicate_ids[:5]}")
    id_set = set(ids)

    relations = records["relations.jsonl"]
    chapter_relations = [record for record in relations if record["id"].startswith(CHAPTER_ID + "-")]
    unresolved = []
    for record in relations:
        for key in ("from_id", "to_id"):
            endpoint = record.get(key)
            external_prefixes = ("ERDMAN-FAOA-BIB-", "ERDMAN-FAOA-2015-LABEL-", "COURSE-O007")
            if endpoint and endpoint not in id_set and not any(str(endpoint).startswith(prefix) for prefix in external_prefixes):
                unresolved.append((record["id"], key, endpoint))
    if unresolved:
        raise ValueError(f"relation endpoints unresolved: {unresolved[:5]}")

    semantic = [record for record in records["semantic_units.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")]
    segments = [record for record in records["segments.jsonl"] if record["id"].startswith(CHAPTER_ID + "-")]
    if collections.Counter(record["unit_kind"] for record in semantic)["section"] != 6:
        raise ValueError("Chapter 12 semantic section count differs")
    if any(record.get("qa_state") != "passed" for record in semantic + segments):
        raise ValueError("Chapter 12 semantic/segment QA state differs")
    expected_translation_state = "admitted" if bound else "qa_passed_pending_artifact_binding"
    if any(record.get("translation_state") != expected_translation_state for record in semantic + segments):
        raise ValueError("Chapter 12 semantic/segment translation state differs")

    formula_summary = validate_formula_maps(records["formula_map.jsonl"])
    with (BACKEND / "index_terms.csv").open(encoding="utf-8", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    validate_index(index_rows)

    ledger = json.loads((ROOT / generator.LEDGER_REL).read_text(encoding="utf-8"))
    corrections = [record for record in records["corrections.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    if len(corrections) != 29 or [record["id"] for record in corrections] != [record["id"] for record in ledger["records"]]:
        raise ValueError("Chapter 12 correction record closure differs")
    ledger_sha = sha((ROOT / generator.LEDGER_REL).read_bytes())
    if any(record.get("ledger_sha256") != ledger_sha or record.get("qa_state") != "passed" for record in corrections):
        raise ValueError("Chapter 12 correction ledger binding differs")

    artifacts = [record for record in records["artifacts.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    qa_events = [record for record in records["qa_events.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    if len(artifacts) != 14 or len(qa_events) != 10:
        raise ValueError(f"Chapter 12 artifact/QA closure differs: {len(artifacts)}/{len(qa_events)}")
    pdf_artifact = next(record for record in artifacts if record["id"] == "ARTIFACT-FAOA-ID-THROUGH-CH12-PDF")
    if not bound:
        forbidden_pdf_fields = {"bytes", "sha256", "pages"}.intersection(pdf_artifact)
        if forbidden_pdf_fields:
            raise ValueError(f"pending PDF artifact leaks final identity fields: {forbidden_pdf_fields}")
        if any(field in unit for field in ("artifact_bytes", "artifact_pages", "artifact_sha256")):
            raise ValueError("pending Chapter 12 unit contains a final PDF identity")
        final_qa_ids = {
            "QA-CH12-BUILD-20260823",
            "QA-CH12-VISUAL-20260823",
            "QA-CH12-ACCESSIBILITY-20260823",
            "QA-CH12-ADMISSION-20260823",
        }
        if any(record.get("result") != "pending" for record in qa_events if record["id"] in final_qa_ids):
            raise ValueError("a final Chapter 12 QA gate is prematurely marked pass")

    self_adjoint = [record for record in records["terminology.jsonl"] if record.get("id") == "TERM-SELF-ADJOINT"]
    if len(self_adjoint) != 1 or self_adjoint[0].get("preferred") != "swaadjoin" or self_adjoint[0].get("variants") != ["swadjoin", "adjoin-diri"]:
        raise ValueError("whole-edition self-adjoint terminology record differs")
    for record in records["terminology.jsonl"]:
        for field in ("source_term", "preferred"):
            value = record.get(field, "")
            if "\\index{" in value:
                raise ValueError(f"terminology {field} contains an index hook: {record.get('id')}")
            if "\n" in value or "\r" in value:
                raise ValueError(f"terminology {field} is multiline: {record.get('id')}")
    chapter_terms = [record for record in records["terminology.jsonl"] if record.get("introduced_in_unit") == CHAPTER_ID]
    term_relations = [record for record in chapter_relations if record.get("relation_type") == "uses_term"]
    if len(term_relations) != 42 or any(record.get("to_id") not in id_set for record in term_relations):
        raise ValueError("Chapter 12 defined-term relation closure differs")

    rights_relations = [record for record in chapter_relations if record.get("relation_type") == "licensed_under"]
    if len(rights_relations) != 1 or rights_relations[0].get("to_id") != generator.RIGHTS:
        raise ValueError("Chapter 12 rights relation differs")
    if any(record.get("unit_id") == CHAPTER_ID for record in records["exercise_support.jsonl"]):
        raise ValueError("Chapter 12 unexpectedly has exercise-support records")

    manifest_sha = validate_manifest()
    aggregate_records = sum(len(records[name]) for name in generator.JSONL_FILES) + len(index_rows)
    return {
        "status": "pass",
        "unit_id": CHAPTER_ID,
        "binding_state": "bound" if bound else "pending_final_artifact_binding",
        "source_sha256": generator.EXPECTED_SOURCE[2],
        "target_sha256": generator.EXPECTED_TARGET[2],
        "master_sha256": generator.EXPECTED_MASTER[2],
        "chapter12": {
            "semantic_units": len(semantic),
            "segments": len(segments),
            "relations": len(chapter_relations),
            "formula_map": formula_summary,
            "index_terms": 102,
            "new_terms": len(chapter_terms),
            "corrections": len(corrections),
            "qa_events": len(qa_events),
            "artifacts": len(artifacts),
        },
        "aggregate_records": aggregate_records,
        "global_stable_ids": "unique",
        "relation_endpoints": "resolved",
        "deterministic_round_trip": "pass",
        "chapter1_ch11_prefix_lock": "pass",
        "chapter11_swaadjoin_reconciliation": generated_summary["ch11_reconciliation"],
        "backend_manifest_sha256": manifest_sha,
    }


def main() -> None:
    result = validate()
    validator = file_identity(Path(__file__))
    payload = {
        "schema_version": "o008.backend-validation.v1",
        "timestamp": "2026-08-23",
        **result,
        "validator": validator,
    }
    output = ROOT / "qa/CH12_BACKEND_VALIDATION.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
