#!/usr/bin/env python3
"""Validate and manifest the deterministic admitted Chapter 1--3 backend."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MANIFEST = BACKEND / "BACKEND_MANIFEST.csv"
GENERATED = [
    "units.jsonl",
    "artifacts.jsonl",
    "qa_events.jsonl",
    "corrections.jsonl",
    "terminology.jsonl",
    "semantic_units.jsonl",
    "segments.jsonl",
    "relations.jsonl",
    "formula_map.jsonl",
    "exercise_support.jsonl",
    "index_terms.csv",
]
CH01_PREFIX_LOCKS = {
    "units.jsonl": (957, "d58c211c782422004d0d144b779a75dce09a964052026d2525352169456440d4"),
    "artifacts.jsonl": (1394, "804a07178df0b03611f29c9aad15464e4123d30ea5f761367132dd39bfe50e3d"),
    "qa_events.jsonl": (2533, "c4bfa226d77ec9b7df67629c610e036dc03ba64f10a1dd048743ac18bebec4a2"),
    "corrections.jsonl": (6074, "a3663f1999eee34e4e0535f46cc4a5c33a78e46885ed99900bb587327fbe7b05"),
    "terminology.jsonl": (6030, "be3b6689fbc7bd5c1453bc71755257041df34d3c83c9af7bfe6386177fbeb39d"),
    "semantic_units.jsonl": (102130, "a8847fbac37ccbb008643df8dab994c56b2ccf007f165d9160e1d6242a056608"),
    "segments.jsonl": (116663, "4d04b9459f546ed18a865c544c3c39c1b6f6f4628ae66c157e3f869bc6d73f7a"),
    "relations.jsonl": (120798, "0fac179bf89231cafb7f3120335b9f972febf1346c67b8d7035c55e1f99488dd"),
    "formula_map.jsonl": (487668, "7337ec874b039527e44ea476cc57a453b04015343f193685ea75418d46dcf381"),
    "exercise_support.jsonl": (3062, "185420e94dbf748f3617a462b8f03936e7cf33a66b9f47b65dcf2c9a242bf4af"),
    "index_terms.csv": (47079, "e5d733d2d61493f392cc384e7d67219eb21ccb08d50e06a434654b0d1c10545b"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    data = path.read_bytes()
    text = data.decode("utf-8")
    if data and not data.endswith(b"\n"):
        raise ValueError(f"{path.name} lacks final LF")
    records: list[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise ValueError(f"{path.name}:{number} is an empty record")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number} is not an object")
        if value.get("schema") != "interlanguage-modular-math":
            raise ValueError(f"{path.name}:{number} has wrong schema")
        if value.get("schema_version") != "0.1.0":
            raise ValueError(f"{path.name}:{number} has wrong schema version")
        round_trip = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        if round_trip != line:
            raise ValueError(f"{path.name}:{number} failed exact JSON round trip")
        records.append(value)
    if json.loads(json.dumps(records, ensure_ascii=False)) != records:
        raise ValueError(f"{path.name} failed semantic JSON round trip")
    return records


def load_csv_exact(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_bytes().decode("utf-8")
    if text and not text.endswith("\n"):
        raise ValueError(f"{path.name} lacks final LF")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise ValueError(f"{path.name} lacks a header")
    rows = list(reader)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    if buffer.getvalue() != text:
        raise ValueError(f"{path.name} failed exact CSV round trip")
    return reader.fieldnames, rows


def backend_files() -> list[Path]:
    return sorted(
        [
            path
            for path in BACKEND.iterdir()
            if path.is_file() and path.name != MANIFEST.name and not path.name.endswith(".pyc")
        ],
        key=lambda path: path.name.casefold(),
    )


def hashes(paths: list[Path]) -> dict[str, str]:
    return {path.name: sha(path) for path in paths}


def render_manifest(paths: list[Path]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["relative_path", "bytes", "sha256"])
    for path in paths:
        writer.writerow([path.name, path.stat().st_size, sha(path)])
    return buffer.getvalue()


def verify_ch01_prefixes() -> None:
    for name, (size, expected_sha) in CH01_PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size:
            raise ValueError(f"{name} is shorter than its Chapter 1 prefix")
        if sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1 byte prefix changed")


def register_id(ids: dict[str, str], record_id: str, location: str) -> None:
    if not record_id:
        raise ValueError(f"record in {location} lacks a stable ID")
    if record_id in ids:
        raise ValueError(f"duplicate ID {record_id} in {ids[record_id]} and {location}")
    ids[record_id] = location


def main() -> None:
    if sha(BACKEND / "generate_ch01_backend.py") != (
        "dab8c5be6f44041606efaf7dd138a66f0344a491af5eac92415d96de32553275"
    ):
        raise ValueError("locked Chapter 1 generator changed")
    schema = json.loads((BACKEND / "schema.json").read_text(encoding="utf-8"))
    expected_sets = schema["record_sets"]
    missing = [
        name for name in expected_sets if not (BACKEND / name).is_file() and name != MANIFEST.name
    ]
    if missing:
        raise ValueError(f"missing record sets: {missing}")

    verify_ch01_prefixes()
    generated_paths = [BACKEND / name for name in GENERATED]
    before = hashes(generated_paths)
    run_one = subprocess.run(
        [sys.executable, str(BACKEND / "generate_backend.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    after_one = hashes(generated_paths)
    verify_ch01_prefixes()
    run_two = subprocess.run(
        [sys.executable, str(BACKEND / "generate_backend.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    after_two = hashes(generated_paths)
    verify_ch01_prefixes()
    if before != after_one:
        raise ValueError("canonical generator differs from checked-in backend outputs")
    if after_one != after_two or run_one.stdout != run_two.stdout:
        raise ValueError("canonical generator failed deterministic two-run validation")

    jsonl_paths = sorted(BACKEND.glob("*.jsonl"), key=lambda path: path.name.casefold())
    records_by_file = {path.name: load_jsonl(path) for path in jsonl_paths}
    all_records = [record for records in records_by_file.values() for record in records]
    index_fieldnames, term_rows = load_csv_exact(BACKEND / "index_terms.csv")
    expected_index_fields = [
        "id",
        "parent_segment_id",
        "source_order",
        "source_line",
        "source_index_tex",
        "target_line",
        "target_index_tex",
        "source_sha256",
        "target_sha256",
        "locale",
    ]
    if index_fieldnames != expected_index_fields:
        raise ValueError("index_terms.csv header changed")

    ids: dict[str, str] = {}
    for path_name, records in records_by_file.items():
        for number, record in enumerate(records, 1):
            record_id = record.get("id")
            if not isinstance(record_id, str):
                raise ValueError(f"record in {path_name}:{number} lacks a string ID")
            register_id(ids, record_id, f"{path_name}:{number}")
    for number, row in enumerate(term_rows, 2):
        register_id(ids, row["id"], f"index_terms.csv:{number}")

    rights_ids = {record["id"] for record in records_by_file["rights.jsonl"]}
    for record in all_records:
        rights_id = record.get("rights_id")
        if rights_id and rights_id not in rights_ids:
            raise ValueError(f"unresolved rights ID {rights_id} on {record['id']}")

    external_prefixes = (
        "COURSE-O007",
        "ERDMAN-FAOA-2015-LABEL-",
        "ERDMAN-FAOA-BIB-",
    )
    relation_records = records_by_file["relations.jsonl"] + records_by_file[
        "concept_relations.jsonl"
    ]
    for relation in relation_records:
        for field in ("from_id", "to_id"):
            endpoint = relation[field]
            if endpoint not in ids and not endpoint.startswith(external_prefixes):
                raise ValueError(f"unresolved relation endpoint {endpoint} on {relation['id']}")
    for number, row in enumerate(term_rows, 2):
        if row["parent_segment_id"] not in ids:
            raise ValueError(f"unresolved parent segment in index_terms.csv:{number}")

    units = records_by_file["units.jsonl"]
    chapter_units = [record for record in units if record["record_type"] == "unit"]
    if len(chapter_units) != 17 or [record["order"] for record in chapter_units] != list(
        range(1, 18)
    ):
        raise ValueError("17-chapter order invariant failed")
    chapter_one = chapter_units[0]
    if chapter_one["translation_state"] != "admitted":
        raise ValueError("Chapter 1 is not admitted")
    if chapter_one["source_sha256"] != (
        "a15cabf306adf5457cedce046f98b9474c72b38ab50197b0dc4288e942772096"
    ):
        raise ValueError("Chapter 1 authority mismatch")
    if chapter_one["target_sha256"] != (
        "4ab3098cab358f425190bfe6defa20d3ec7b2a81653e0e61bbfa67e497e2654d"
    ):
        raise ValueError("Chapter 1 target mismatch")
    chapter_two = chapter_units[1]
    chapter_two_expected = {
        "source_bytes": 27446,
        "source_lines": 574,
        "source_sha256": "6f5115e4058902e99ab7157ad59ea95f0e0013e2f4272c05ff421933f7255775",
        "target_bytes": 29254,
        "target_lines": 570,
        "target_sha256": "39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd",
        "course_role": "D20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 6,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch02.tex",
        "build_master_bytes": 9437,
        "build_master_sha256": "1ca424e166df692e8bf69421a0a1720d5dfb2540c52053bb036be99ecdde9ecd",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-2.pdf",
        "artifact_bytes": 795305,
        "artifact_pages": 32,
        "artifact_sha256": "7a04eb72ef5445ee06e429e7552b8e14a02a993c916b4632cdb9219a928a3bdb",
        "qa_receipt_id": "QA-CH02-ADMISSION-20260821",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_two_expected.items():
        if chapter_two.get(field) != expected:
            raise ValueError(f"Chapter 2 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "categories.tex"
    target_path = ROOT / "source" / "id-ID" / "categories-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        27446,
        574,
        "6f5115e4058902e99ab7157ad59ea95f0e0013e2f4272c05ff421933f7255775",
    ):
        raise ValueError("Chapter 2 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        29254,
        570,
        "39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd",
    ):
        raise ValueError("Chapter 2 target authority file mismatch")

    chapter_three = chapter_units[2]
    chapter_three_expected = {
        "source_bytes": 87537,
        "source_lines": 1920,
        "source_sha256": "01548b8e80e14f6eb66703579ed7020e68cc65bd8d30538c13a3533a5ba777e7",
        "target_bytes": 94040,
        "target_lines": 1913,
        "target_sha256": "c44f20890d5fb6b7445f0b2eeca8f477cc970d147d5c54aa4bc5df709f6b1f9d",
        "course_role": "D20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 25,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch03.tex",
        "build_master_bytes": 9311,
        "build_master_sha256": "f36da75492209ba8f4df1d8982bc5a7eae79d75a5dfeb87267715c998aeed8c7",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-3.pdf",
        "artifact_bytes": 1076473,
        "artifact_pages": 57,
        "artifact_sha256": "7a921e1f9678b0a698de237a0a0e5629f24f5b6f0798d2638d9c0a70a499b4f5",
        "qa_receipt_id": "QA-CH03-ADMISSION-20260821",
        "receipt_document_state": "present",
        "receipt_sha256": "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_three_expected.items():
        if chapter_three.get(field) != expected:
            raise ValueError(f"Chapter 3 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "normlinspaces.tex"
    target_path = ROOT / "source" / "id-ID" / "normlinspaces-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        87537,
        1920,
        "01548b8e80e14f6eb66703579ed7020e68cc65bd8d30538c13a3533a5ba777e7",
    ):
        raise ValueError("Chapter 3 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        94040,
        1913,
        "c44f20890d5fb6b7445f0b2eeca8f477cc970d147d5c54aa4bc5df709f6b1f9d",
    ):
        raise ValueError("Chapter 3 target authority file mismatch")

    expected_counts = {
        "units.jsonl": 18,
        "semantic_units.jsonl": 345,
        "segments.jsonl": 423,
        "relations.jsonl": 1294,
        "formula_map.jsonl": 2738,
        "exercise_support.jsonl": 13,
        "artifacts.jsonl": 19,
        "qa_events.jsonl": 20,
        "corrections.jsonl": 46,
        "terminology.jsonl": 56,
    }
    for name, count in expected_counts.items():
        if len(records_by_file[name]) != count:
            raise ValueError(f"{name} expected {count}, got {len(records_by_file[name])}")
    if len(term_rows) != 668:
        raise ValueError(f"index_terms.csv expected 668 rows, got {len(term_rows)}")

    chapter_two_counts = {
        "semantic_units.jsonl": 34,
        "segments.jsonl": 41,
        "relations.jsonl": 121,
        "formula_map.jsonl": 397,
        "exercise_support.jsonl": 0,
    }
    for name, count in chapter_two_counts.items():
        actual = sum(record["id"].startswith("FAOA-2015-CH02-") for record in records_by_file[name])
        if actual != count:
            raise ValueError(f"{name} Chapter 2 expected {count}, got {actual}")
    chapter_two_terms = [row for row in term_rows if row["id"].startswith("FAOA-2015-CH02-")]
    if len(chapter_two_terms) != 137:
        raise ValueError("Chapter 2 index-term projection invariant failed")

    chapter_two_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH02-")
    ]
    chapter_two_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH02-")
    ]
    if any(
        record.get("translation_state") != "admitted" or record.get("qa_state") != "passed"
        for record in chapter_two_semantic + chapter_two_segments
    ):
        raise ValueError("Chapter 2 semantic/segment admission state is not reconciled")

    chapter_three_counts = {
        "semantic_units.jsonl": 184,
        "segments.jsonl": 228,
        "relations.jsonl": 703,
        "formula_map.jsonl": 1410,
        "exercise_support.jsonl": 7,
    }
    for name, count in chapter_three_counts.items():
        actual = sum(record["id"].startswith("FAOA-2015-CH03-") for record in records_by_file[name])
        if actual != count:
            raise ValueError(f"{name} Chapter 3 expected {count}, got {actual}")
    chapter_three_terms = [row for row in term_rows if row["id"].startswith("FAOA-2015-CH03-")]
    if len(chapter_three_terms) != 344:
        raise ValueError("Chapter 3 index-term projection invariant failed")
    chapter_three_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH03-")
    ]
    chapter_three_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH03-")
    ]
    if any(
        record.get("translation_state") != "admitted" or record.get("qa_state") != "passed"
        for record in chapter_three_semantic + chapter_three_segments
    ):
        raise ValueError("Chapter 3 semantic/segment admission state is not reconciled")

    formula_records = records_by_file["formula_map.jsonl"]
    source_formula_count = sum(len(record["source_formula_ids"]) for record in formula_records)
    target_formula_count = sum(len(record["target_formula_ids"]) for record in formula_records)
    exact_alignment_kinds = {
        "preserved_exact_after_whitespace_normalization",
        "preserved_exact_after_text_aware_whitespace_normalization",
    }
    exact_formula_count = sum(record["alignment"] in exact_alignment_kinds for record in formula_records)
    if (source_formula_count, target_formula_count, exact_formula_count) != (2742, 2743, 2695):
        raise ValueError("combined formula-map coverage invariant failed")
    chapter_two_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH02-")
    ]
    chapter_two_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_two_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_two_formula),
        sum(
            record["alignment"] == "preserved_exact_after_whitespace_normalization"
            for record in chapter_two_formula
        ),
    )
    if chapter_two_formula_counts != (396, 397, 395):
        raise ValueError("Chapter 2 formula-map coverage invariant failed")
    chapter_two_deviations = [
        record for record in chapter_two_formula if record.get("sequence_opcode")
    ]
    if [record["sequence_opcode"] for record in chapter_two_deviations] != ["replace", "insert"]:
        raise ValueError("Chapter 2 formula deviations differ from replace+insert")
    if chapter_two_deviations[0]["id"] != "FAOA-2015-CH02-MATHMAP-0181":
        raise ValueError("Chapter 2 formula replacement stable ID changed")
    if chapter_two_deviations[1]["id"] != "FAOA-2015-CH02-MATHMAP-0386":
        raise ValueError("Chapter 2 formula insertion stable ID changed")

    chapter_three_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH03-")
    ]
    chapter_three_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_three_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_three_formula),
        sum(
            record["alignment"] == "preserved_exact_after_text_aware_whitespace_normalization"
            for record in chapter_three_formula
        ),
    )
    if chapter_three_formula_counts != (1414, 1414, 1394):
        raise ValueError("Chapter 3 formula-map coverage invariant failed")
    chapter_three_deviations = [
        record for record in chapter_three_formula if record.get("sequence_opcode")
    ]
    if len(chapter_three_deviations) != 16 or any(
        record["sequence_opcode"] != "replace" for record in chapter_three_deviations
    ):
        raise ValueError("Chapter 3 reviewed formula-deviation inventory changed")

    chapter_two_xrefs = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH02-REL-XREF-")
    ]
    if [(record["source_local_id"], record["resolution"]) for record in chapter_two_xrefs] != [
        ("C069414", "pending_later_source_unit"),
        ("C015127", "local"),
    ]:
        raise ValueError("Chapter 2 xref resolution invariant failed")
    if chapter_two_xrefs[0]["to_id"] != "ERDMAN-FAOA-2015-LABEL-C069414":
        raise ValueError("Chapter 2 future xref endpoint changed")
    if chapter_two_xrefs[1]["to_id"] not in ids:
        raise ValueError("Chapter 2 local xref endpoint is unresolved")

    chapter_three_xrefs = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH03-REL-XREF-")
    ]
    resolution_counts = {
        resolution: sum(record["resolution"] == resolution for record in chapter_three_xrefs)
        for resolution in ("local", "admitted_prior_unit", "pending_later_source_unit")
    }
    if len(chapter_three_xrefs) != 47 or resolution_counts != {
        "local": 39,
        "admitted_prior_unit": 7,
        "pending_later_source_unit": 1,
    }:
        raise ValueError("Chapter 3 reference-resolution inventory changed")
    future_xrefs = [
        record for record in chapter_three_xrefs if record["resolution"] == "pending_later_source_unit"
    ]
    if (
        future_xrefs[0].get("source_local_id") != "exam_ran_nonclosed"
        or future_xrefs[0].get("to_id") != "ERDMAN-FAOA-2015-LABEL-exam_ran_nonclosed"
    ):
        raise ValueError("Chapter 3 future reference endpoint changed")
    if any(
        record["to_id"] not in ids
        for record in chapter_three_xrefs
        if record["resolution"] != "pending_later_source_unit"
    ):
        raise ValueError("Chapter 3 admitted reference endpoint is unresolved")
    chapter_three_eqrefs = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH03-REL-EQREF-")
    ]
    if len(chapter_three_eqrefs) != 1 or chapter_three_eqrefs[0].get("source_local_id") != "eq_HBTI":
        raise ValueError("Chapter 3 equation-reference invariant failed")

    artifact_records = records_by_file["artifacts.jsonl"]
    chapter_two_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH02"
    ]
    expected_chapter_two_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH02-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH02-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH02-PDF",
        "ARTIFACT-FAOA-ID-CH02-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH02-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH02-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH02-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_two_artifacts] != expected_chapter_two_artifact_ids:
        raise ValueError("Chapter 2 admitted artifact inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH02-ADMISSION-20260821"
        for record in chapter_two_artifacts
    ):
        raise ValueError("Chapter 2 artifacts are not bound to the admission receipt")
    chapter_three_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH03"
    ]
    expected_chapter_three_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH03-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH03-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH03-PDF",
        "ARTIFACT-FAOA-ID-CH03-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH03-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH03-MATH-EXTRACTOR",
        "ARTIFACT-FAOA-ID-CH03-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH03-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH03-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_three_artifacts] != expected_chapter_three_artifact_ids:
        raise ValueError("Chapter 3 admitted artifact inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH03-ADMISSION-20260821"
        for record in chapter_three_artifacts
    ):
        raise ValueError("Chapter 3 artifacts are not bound to the admission receipt")
    for artifact in artifact_records:
        path = ROOT / artifact["path"]
        if not path.is_file():
            raise ValueError(f"missing artifact {artifact['path']}")
        if artifact.get("artifact_kind") == "source_corrections_ledger":
            data = path.read_bytes()
            historical_size = artifact["bytes"]
            if len(data) < historical_size or sha_bytes(data[:historical_size]) != artifact["sha256"]:
                raise ValueError(f"append-only artifact prefix mismatch {artifact['id']}")
            continue
        if path.stat().st_size != artifact["bytes"] or sha(path) != artifact["sha256"]:
            raise ValueError(f"artifact mismatch {artifact['id']}")

    chapter_two_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH02"
    ]
    expected_chapter_two_qa_ids = [
        "QA-CH02-STRUCTURAL-20260821",
        "QA-CH02-MATH-20260821",
        "QA-CH02-LANGUAGE-20260821",
        "QA-CH02-BUILD-20260821",
        "QA-CH02-VISUAL-20260821",
        "QA-CH02-RIGHTS-20260821",
        "QA-CH02-ADMISSION-20260821",
    ]
    expected_chapter_two_qa_types = [
        "unit_structural",
        "unit_mathematical",
        "unit_language",
        "cumulative_build",
        "cumulative_visual",
        "unit_rights_privacy",
        "unit_admission",
    ]
    if [record["id"] for record in chapter_two_qa] != expected_chapter_two_qa_ids:
        raise ValueError("Chapter 2 typed QA event inventory changed")
    if [record["qa_type"] for record in chapter_two_qa] != expected_chapter_two_qa_types:
        raise ValueError("Chapter 2 typed QA event kinds changed")
    if any(
        record.get("result") != "pass"
        or record.get("witness") != "provenance/CH02_BUILD_AND_QA_RECEIPT.md"
        or record.get("witness_sha256")
        != "4acd8a6e7942a8f57ad8442e9fca2fb68d041904962e18ed588704bc2098175f"
        for record in chapter_two_qa
    ):
        raise ValueError("Chapter 2 QA events are not bound to the exact passed receipt")
    admission = chapter_two_qa[-1]
    if (
        admission.get("decision") != "admitted"
        or admission.get("all_required_gates") != "pass"
        or admission.get("typed_qa_event_ids") != expected_chapter_two_qa_ids[:-1]
        or admission.get("receipt_sha256")
        != "4acd8a6e7942a8f57ad8442e9fca2fb68d041904962e18ed588704bc2098175f"
    ):
        raise ValueError("Chapter 2 admission event is incomplete")

    chapter_three_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH03"
    ]
    expected_chapter_three_qa_ids = [
        "QA-CH03-STRUCTURAL-20260821",
        "QA-CH03-MATH-20260821",
        "QA-CH03-LANGUAGE-20260821",
        "QA-CH03-BUILD-20260821",
        "QA-CH03-VISUAL-20260821",
        "QA-CH03-RIGHTS-20260821",
        "QA-CH03-ADMISSION-20260821",
    ]
    expected_chapter_three_qa_types = [
        "unit_structural",
        "unit_mathematical",
        "unit_language",
        "cumulative_build",
        "cumulative_visual",
        "unit_rights_privacy",
        "unit_admission",
    ]
    if [record["id"] for record in chapter_three_qa] != expected_chapter_three_qa_ids:
        raise ValueError("Chapter 3 typed QA event inventory changed")
    if [record["qa_type"] for record in chapter_three_qa] != expected_chapter_three_qa_types:
        raise ValueError("Chapter 3 typed QA event kinds changed")
    if any(
        record.get("result") != "pass"
        or record.get("qa_receipt_id") != "QA-CH03-ADMISSION-20260821"
        or record.get("receipt_path") != "provenance/CH03_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a"
        for record in chapter_three_qa
    ):
        raise ValueError("Chapter 3 QA events are not bound to the exact passed receipt")
    structural_event = chapter_three_qa[0]
    if (
        structural_event.get("references") != 48
        or structural_event.get("ordinary_target_references") != 46
        or structural_event.get("future_target_references") != 1
        or structural_event.get("equation_references") != 1
    ):
        raise ValueError("Chapter 3 reference-surface metadata is inconsistent")
    math_event = chapter_three_qa[1]
    if (
        math_event.get("source_math_surfaces") != 1414
        or math_event.get("target_math_surfaces") != 1414
        or math_event.get("exact_normalized_alignments") != 1394
        or math_event.get("reviewed_deviation_opcodes") != 16
        or math_event.get("extractor") != "backend/ch03_math.py"
        or math_event.get("extractor_sha256")
        != "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3"
    ):
        raise ValueError("Chapter 3 text-aware math evidence is inconsistent")
    admission = chapter_three_qa[-1]
    if (
        admission.get("decision") != "admitted"
        or admission.get("all_required_gates") != "pass"
        or admission.get("typed_qa_event_ids") != expected_chapter_three_qa_ids[:-1]
        or admission.get("receipt_document_state") != "present"
        or admission.get("witness") != "provenance/CH03_BUILD_AND_QA_RECEIPT.md"
        or admission.get("witness_sha256")
        != "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a"
    ):
        raise ValueError("Chapter 3 admission event is incomplete")

    chapter_two_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH02"
    ]
    if [record["id"] for record in chapter_two_corrections] != [
        f"FAOA-2015-CH02-CORR-{number:03d}" for number in range(1, 7)
    ]:
        raise ValueError("Chapter 2 correction inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH02-ADMISSION-20260821"
        or record.get("ledger_sha256")
        != "26708cf62c00202ad224a5d5413069e7bd376497a96e3c7c30487b66214d5c16"
        or record.get("upstream_report")
        != "deferred_until_complete_and_separately_authorized"
        for record in chapter_two_corrections
    ):
        raise ValueError("Chapter 2 corrections are not bound to the admitted evidence")

    chapter_three_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH03"
    ]
    if [record["id"] for record in chapter_three_corrections] != [
        f"FAOA-2015-CH03-CORR-{number:03d}" for number in range(1, 26)
    ]:
        raise ValueError("Chapter 3 correction inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH03-ADMISSION-20260821"
        or record.get("ledger_sha256")
        != "bb1ef771876b2c1ef0063c3fd9e28c27f20db4049f434d27f8b333fd5f3477c2"
        or record.get("upstream_report")
        != "deferred_until_complete_and_separately_authorized"
        for record in chapter_three_corrections
    ):
        raise ValueError("Chapter 3 corrections are not bound to the admitted evidence")

    expected_chapter_two_term_ids = [
        "TERM-CATEGORY",
        "TERM-OBJECT",
        "TERM-MORPHISM",
        "TERM-COMPOSITION",
        "TERM-LOCALLY-SMALL-CATEGORY",
        "TERM-SMALL-CATEGORY",
        "TERM-CONCRETE-CATEGORY",
        "TERM-ISOMORPHISM",
        "TERM-MONOMORPHISM",
        "TERM-EPIMORPHISM",
        "TERM-FUNCTOR",
        "TERM-COVARIANT-FUNCTOR",
        "TERM-CONTRAVARIANT-FUNCTOR",
        "TERM-OBJECT-MAP",
        "TERM-MORPHISM-MAP",
        "TERM-FORGETFUL-FUNCTOR",
        "TERM-POWER-SET",
        "TERM-DIAGONAL-FUNCTOR",
    ]
    chapter_two_terminology = [
        record
        for record in records_by_file["terminology.jsonl"]
        if record["id"] in expected_chapter_two_term_ids
    ]
    if [record["id"] for record in chapter_two_terminology] != expected_chapter_two_term_ids:
        raise ValueError("Chapter 2 bounded terminology inventory changed")
    if any(
        record.get("locale") != "id-ID"
        or record.get("evidence") != "FAOA-2015-CH02 and backend/index_terms.csv"
        for record in chapter_two_terminology
    ):
        raise ValueError("Chapter 2 terminology provenance changed")

    expected_chapter_three_term_ids = [
        "TERM-NORMED-LINEAR-SPACE",
        "TERM-BOUNDED-LINEAR-MAP",
        "TERM-OPERATOR-NORM",
        "TERM-NORM-PRESERVING",
        "TERM-QUOTIENT-SPACE",
        "TERM-PRODUCT-SPACE",
        "TERM-COPRODUCT",
        "TERM-NET",
        "TERM-DIRECTED-SET",
        "TERM-SUBNET",
        "TERM-CLOSURE",
        "TERM-INTERIOR",
        "TERM-CONTINUITY",
        "TERM-FUNCTIONAL-EXTENSION",
        "TERM-HAUSDORFF",
        "TERM-COMPACT",
        "TERM-HAHN-BANACH-THEOREM",
        "TERM-SCALAR-VALUED",
    ]
    chapter_three_terminology = [
        record
        for record in records_by_file["terminology.jsonl"]
        if record["id"] in expected_chapter_three_term_ids
    ]
    if [record["id"] for record in chapter_three_terminology] != expected_chapter_three_term_ids:
        raise ValueError("Chapter 3 bounded terminology inventory changed")
    if any(
        record.get("locale") != "id-ID"
        or record.get("evidence") != "FAOA-2015-CH03 and backend/index_terms.csv"
        for record in chapter_three_terminology
    ):
        raise ValueError("Chapter 3 terminology provenance changed")

    for path in backend_files():
        data = path.read_bytes()
        data.decode("utf-8")
        if b"\r\n" in data:
            raise ValueError(f"CRLF found in deterministic backend file {path.name}")

    paths = backend_files()
    expected_manifest = render_manifest(paths)
    if MANIFEST.read_bytes().decode("utf-8") != expected_manifest:
        raise ValueError("checked-in backend manifest is stale or incorrect")
    manifest_fields, manifest_rows = load_csv_exact(MANIFEST)
    if manifest_fields != ["relative_path", "bytes", "sha256"]:
        raise ValueError("backend manifest header mismatch")
    if len(manifest_rows) != len(paths):
        raise ValueError("backend manifest row count mismatch")
    for row, path in zip(manifest_rows, paths):
        if (
            row["relative_path"] != path.name
            or int(row["bytes"]) != path.stat().st_size
            or row["sha256"] != sha(path)
        ):
            raise ValueError(f"backend manifest mismatch for {path.name}")

    print(run_one.stdout.strip())
    print(
        json.dumps(
            {
                "jsonl_files": len(jsonl_paths),
                "jsonl_records": len(all_records),
                "index_term_records": len(term_rows),
                "records_with_globally_unique_ids": len(ids),
                "relation_endpoints_checked": 2 * len(relation_records),
                "json_roundtrip_files": len(jsonl_paths),
                "csv_roundtrip_files": 2,
                "deterministic_generator_runs": 2,
                "backend_manifest_rows": len(manifest_rows),
                "backend_manifest_sha256": sha(MANIFEST),
                "result": "pass",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
