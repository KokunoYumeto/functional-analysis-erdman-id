#!/usr/bin/env python3
"""Deterministically append the admitted FAOA-2015-CH13 backend slice."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path[:0] = [str(BACKEND), str(ROOT / "qa")]
import ch03_math  # noqa: E402
import check_ch05_translation as common  # noqa: E402
import generate_ch12_backend as base  # noqa: E402


SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH13"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_REL = "source/upstream/GNS_construction.tex"
TARGET_REL = "source/id-ID/GNS_construction-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-through-ch13.tex"
REPORT_REL = "qa/ch13-translation-report.json"
LEDGER_REL = "provenance/SOURCE_CORRECTIONS_CH13.json"
TERM_PLAN_REL = "provenance/CH13_TERMINOLOGY_PLAN.md"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-13.pdf"
RECEIPT_REL = "provenance/CH13_BUILD_AND_QA_RECEIPT.md"
RENDER_MANIFEST_REL = "provenance/CH13_RENDER_MANIFEST.csv"
RENDER_AUDIT_REL = "qa/CH13_RENDER_AUDIT.json"
ACCESSIBILITY_AUDIT_REL = "qa/CH13_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
BUILD_RESULT_REL = "qa/CH13_FINAL_BUILD_RESULT.json"
PREFIX_LOCK_REL = "backend/CH13_PREFIX_LOCKS.json"

SOURCE_PATH = ROOT / SOURCE_REL
TARGET_PATH = ROOT / TARGET_REL

EXPECTED_SOURCE = (11_965, 289, "fcc774cecc607d9860540da7b757ae04a3c43afe9d9a17e8c881e077f02682c1")
EXPECTED_TARGET = (12_601, 289, "4c95b339702180ef8f2ea42cfba9e19a60a1740ca7d25a0568a6290f0170371f")
EXPECTED_MASTER = (10_345, 342, "d1734ea09a576c9e5c8f38bb9430a132e8cd38551c9b0c6cbd9bf65b4923c87e")

JSONL_FILES = base.JSONL_FILES
INITIAL_LOCKS = {
    "units.jsonl": (19_502, "a02b16b597dd2bbf5e0b8f7ed98b2888100ff6e4203d91945096968c72366582"),
    "semantic_units.jsonl": (1_185_973, "b5293b739cf569f6d915b2d3fd864685b78678b7b0d814e039807072f04d914d"),
    "segments.jsonl": (1_321_245, "9e7880d691fa537f2bdcdc4922a96104bcab4f09b9f4cccf477263f8e3cebe95"),
    "relations.jsonl": (1_669_547, "b753a0618a2f529fa1291c4680b7741508d44e1c5f565b01409bd6791b66324f"),
    "formula_map.jsonl": (5_547_300, "23f92a3918a0ed37f54b594de8fb17a2e4b0e5b89c6503f2ad03110e929b396c"),
    "exercise_support.jsonl": (25_503, "45b128f45d61057837c2eddcf1e45024e62b231e7d4b46e2b2dfb7c849a44925"),
    "index_terms.csv": (433_754, "28e30b1f0e88f1e8eb38a97385754da1122f6eccebc34137bf9b79b316896c81"),
    "artifacts.jsonl": (67_064, "0805434888baa98a7f896ad84d88d3bc3889235df752e205f3f4d1e6c24f4694"),
    "qa_events.jsonl": (87_529, "0da368a877ee6928fa3a9f38a579238cfb8bcda73852af9e71e9188ed5404d55"),
    "corrections.jsonl": (185_233, "5b5e362a8d061b15225ad87b05d4b2c13aa0b00b956e3e2af1918d26d60163a9"),
    "terminology.jsonl": (138_915, "f6140d3c78be026175d6609524d5756c580c5127a08787f24216832b487ad667"),
}

QUEUED_CH13 = {
    "schema": SCHEMA,
    "schema_version": VERSION,
    "record_type": "unit",
    "id": CHAPTER_ID,
    "edition_id": EDITION,
    "order": 13,
    "source_path": "GNS_construction.tex",
    "source_bytes": EXPECTED_SOURCE[0],
    "source_lines": EXPECTED_SOURCE[1],
    "source_sha256": EXPECTED_SOURCE[2],
    "source_title": "THE GELFAND-NAIMARK-SEGAL CONSTRUCTION",
    "course_role": "advanced_continuation",
    "translation_state": "queued",
    "rights_id": RIGHTS,
}

TERM_IDS = {
    "Hermitian": "TERM-HERMITIAN",
    "positive": "TERM-POSITIVE",
    "state": "TERM-STATE",
    "vector state": "TERM-VECTOR-STATE",
    "representation": "TERM-CSTAR-REPRESENTATION",
    "nondegenerate": "TERM-NONDEGENERATE-REPRESENTATION",
    "faithful": "TERM-FAITHFUL-REPRESENTATION",
    "cyclic": "TERM-CYCLIC-REPRESENTATION",
    "cyclic vector": "TERM-CYCLIC-VECTOR",
    "left kernel": "TERM-LEFT-KERNEL",
    "direct sum": "TERM-DIRECT-SUM",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")


def identity(path: Path, expected: tuple[int, int, str] | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    value = {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "lines": len(data.splitlines()),
        "sha256": sha(data),
    }
    if expected and (value["bytes"], value["lines"], value["sha256"]) != expected:
        raise RuntimeError(f"identity mismatch: {value}")
    return value


def csv_bytes(fieldnames: list[str], rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def configure_base() -> None:
    base.CHAPTER_ID = CHAPTER_ID
    base.SOURCE_REL = SOURCE_REL
    base.TARGET_REL = TARGET_REL
    base.MASTER_REL = MASTER_REL
    base.SOURCE_PATH = SOURCE_PATH
    base.TARGET_PATH = TARGET_PATH
    base.RIGHTS = RIGHTS
    base.EDITION = EDITION
    base.TARGET_EDITION = TARGET_EDITION


def load_data() -> tuple[dict[str, list[dict[str, Any]]], list[str], list[dict[str, str]]]:
    records = {
        name: [json.loads(line) for line in (BACKEND / name).read_text(encoding="utf-8").splitlines()]
        for name in JSONL_FILES
    }
    with (BACKEND / "index_terms.csv").open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    return records, fields, rows


def initial_state() -> bool:
    return all(
        (len((BACKEND / name).read_bytes()), sha((BACKEND / name).read_bytes())) == expected
        for name, expected in INITIAL_LOCKS.items()
    )


def strip_ch13(records: dict[str, list[dict[str, Any]]], index_rows: list[dict[str, str]]) -> None:
    for name, values in records.items():
        if name == "units.jsonl":
            values[:] = [QUEUED_CH13.copy() if item.get("id") == CHAPTER_ID else item for item in values]
            continue
        values[:] = [
            item
            for item in values
            if not (
                str(item.get("id", "")).startswith(CHAPTER_ID + "-")
                or item.get("unit_id") == CHAPTER_ID
                or item.get("introduced_in_unit") == CHAPTER_ID
                or item.get("exercise_unit_id", "").startswith(CHAPTER_ID + "-")
            )
        ]
    index_rows[:] = [row for row in index_rows if not row.get("id", "").startswith(CHAPTER_ID + "-")]


def prefix_payload(
    records: dict[str, list[dict[str, Any]]], fields: list[str], index_rows: list[dict[str, str]]
) -> tuple[dict[str, bytes], dict[str, Any]]:
    payload = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    payload["index_terms.csv"] = csv_bytes(fields, index_rows)
    locks = {
        "schema_version": "o008.ch13-prefix-locks.v1",
        "unit_id": CHAPTER_ID,
        "scope": "complete admitted Chapters 1--12 backend; excludes every Chapter 13-derived record",
        "files": {
            name: {
                "bytes": len(data),
                "sha256": sha(data),
                "records": len(records[name]) if name in records else len(index_rows),
            }
            for name, data in payload.items()
        },
    }
    return payload, locks


def page_count(pdf: Path) -> int:
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(pdf)).pages)
    except Exception:
        return len(re.findall(rb"/Type\s*/Page(?:\s|/|>)", pdf.read_bytes()))


def evidence(bind_final: bool) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    ids = {
        "source": identity(SOURCE_PATH, EXPECTED_SOURCE),
        "target": identity(TARGET_PATH, EXPECTED_TARGET),
        "master": identity(ROOT / MASTER_REL, EXPECTED_MASTER),
        "report": identity(ROOT / REPORT_REL),
        "ledger": identity(ROOT / LEDGER_REL),
        "term_plan": identity(ROOT / TERM_PLAN_REL),
    }
    report = json.loads((ROOT / REPORT_REL).read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / LEDGER_REL).read_text(encoding="utf-8"))
    if report.get("status") != "pass" or report.get("unit_id") != CHAPTER_ID:
        raise RuntimeError("Chapter 13 translation report is not passing")
    if report.get("identities", {}).get("target_sha256") != EXPECTED_TARGET[2]:
        raise RuntimeError("Chapter 13 translation report target identity is stale")
    if ledger.get("unit_id") != CHAPTER_ID or ledger.get("record_count") != 6 or len(ledger.get("records", [])) != 6:
        raise RuntimeError("Chapter 13 correction ledger closure changed")
    if ledger.get("target", {}).get("sha256") != EXPECTED_TARGET[2]:
        raise RuntimeError("Chapter 13 correction ledger target identity is stale")
    if bind_final:
        required = [
            PDF_REL,
            RECEIPT_REL,
            RENDER_MANIFEST_REL,
            RENDER_AUDIT_REL,
            ACCESSIBILITY_AUDIT_REL,
            BUILD_RESULT_REL,
        ]
        missing = [relative for relative in required if not (ROOT / relative).is_file()]
        if missing:
            raise RuntimeError("final artifact binding inputs missing: " + ", ".join(missing))
        receipt_text = (ROOT / RECEIPT_REL).read_text(encoding="utf-8")
        if not re.search(r"Decision:\s*\*\*admitted\*\*", receipt_text, re.I):
            raise RuntimeError("Chapter 13 receipt does not assert admitted")
        ids["pdf"] = identity(ROOT / PDF_REL)
        ids["pdf"]["pages"] = page_count(ROOT / PDF_REL)
        ids["receipt"] = identity(ROOT / RECEIPT_REL)
    return ids, ledger


def chapter_unit(ids: dict[str, dict[str, Any]], corrections: list[dict[str, Any]], bind_final: bool) -> dict[str, Any]:
    record = QUEUED_CH13 | {
        "target_path": TARGET_REL,
        "target_bytes": ids["target"]["bytes"],
        "target_lines": ids["target"]["lines"],
        "target_sha256": ids["target"]["sha256"],
        "target_title": common.macro(TARGET_PATH.read_text(encoding="utf-8"), "chapter")[0]["argument"],
        "translation_state": "admitted" if bind_final else "qa_passed_pending_artifact_binding",
        "qa_state": "passed",
        "source_corrections": len(corrections),
        "build_master_path": MASTER_REL,
        "build_master_bytes": ids["master"]["bytes"],
        "build_master_lines": ids["master"]["lines"],
        "build_master_sha256": ids["master"]["sha256"],
        "artifact_path": PDF_REL,
        "artifact_state": "canonical_output_copy_present_and_frozen" if bind_final else "pending_final_artifact_binding",
        "publication_state": "pending",
        "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        "receipt_path": RECEIPT_REL,
    }
    if bind_final:
        record.update(
            artifact_bytes=ids["pdf"]["bytes"],
            artifact_pages=ids["pdf"]["pages"],
            artifact_sha256=ids["pdf"]["sha256"],
            qa_receipt_id="QA-CH13-ADMISSION-20260824",
            receipt_sha256=ids["receipt"]["sha256"],
        )
    return record


def correction_records(
    ledger: dict[str, Any], ledger_sha: str, bind_final: bool, receipt_sha: str | None
) -> list[dict[str, Any]]:
    output = []
    for item in ledger["records"]:
        source_lines, target_lines = item["source_lines"], item["target_lines"]
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "correction",
            "id": item["id"],
            "unit_id": CHAPTER_ID,
            "source_locator": f"GNS_construction.tex:{source_lines['start']}--{source_lines['end']}",
            "target_locator": f"GNS_construction-id.tex:{target_lines['start']}--{target_lines['end']}",
            "correction_type": str(item.get("classification", "mechanical")).lower(),
            "decision": item.get("decision", ""),
            "source_normalized_snippet_sha256": item.get("source_normalized_snippet_sha256"),
            "target_normalized_snippet_sha256": item.get("target_normalized_snippet_sha256"),
            "required_target_anchors": item.get("required_target_anchors", []),
            "forbidden_target_anchors": item.get("forbidden_target_anchors", []),
            "target_disposition": "corrected",
            "ledger_path": LEDGER_REL,
            "ledger_sha256": ledger_sha,
            "qa_state": "passed",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
            "upstream_report": "deferred_until_complete_and_separately_authorized",
            "receipt_document_state": "present" if bind_final else "pending",
            "receipt_path": RECEIPT_REL,
        }
        if bind_final:
            record.update(
                qa_receipt_id="QA-CH13-ADMISSION-20260824",
                receipt_sha256=receipt_sha,
            )
        output.append(record)
    return output


def terminology_records(
    source: str, target: str, prior_records: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    source_terms = common.macro(source, "df")
    target_terms = common.macro(target, "df")
    if len(source_terms) != 13 or len(target_terms) != 13:
        raise RuntimeError("Chapter 13 defined-term count changed")
    expected_source = [
        "Hermitian",
        "positive",
        "state",
        "vector state",
        "representation",
        "nondegenerate",
        "faithful",
        "cyclic",
        "cyclic vector",
        "left kernel",
        "direct sum",
        "direct sum",
        "direct sum",
    ]
    expected_target = [
        "Hermitian",
        "positif",
        "keadaan",
        "keadaan vektor",
        "representasi",
        "tak terdegenerasi",
        "setia",
        "siklik",
        "vektor siklik",
        "kernel kiri",
        "jumlah langsung",
        "jumlah langsung",
        "jumlah langsung",
    ]
    actual_source = [item["argument"] for item in source_terms]
    actual_target = [item["argument"] for item in target_terms]
    if actual_source != expected_source or actual_target != expected_target:
        raise RuntimeError("Chapter 13 defined-term sequence differs")
    prior_by_id = {item["id"]: item for item in prior_records}
    mapping: dict[str, str] = {}
    preferred: dict[str, str] = {}
    for source_term, target_term in zip(actual_source, actual_target, strict=True):
        stable_id = TERM_IDS[source_term]
        if source_term in mapping and mapping[source_term] != stable_id:
            raise RuntimeError("unstable repeated Chapter 13 term")
        if source_term in preferred and preferred[source_term] != target_term:
            raise RuntimeError("inconsistent repeated Chapter 13 target term")
        mapping[source_term] = stable_id
        preferred[source_term] = target_term
    for inherited in ("TERM-HERMITIAN", "TERM-POSITIVE", "TERM-DIRECT-SUM"):
        if inherited not in prior_by_id:
            raise RuntimeError(f"inherited term missing: {inherited}")
    output = []
    for source_term, stable_id in mapping.items():
        if stable_id in prior_by_id:
            continue
        output.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "term",
                "id": stable_id,
                "source_term": source_term,
                "locale": "id-ID",
                "preferred": preferred[source_term],
                "variants": ["state"] if source_term == "state" else [],
                "rejected": ["andal"] if source_term == "faithful" else [],
                "scope": "states, representations, GNS construction, and direct sums in C-star algebras",
                "evidence": f"{CHAPTER_ID} target; {TERM_PLAN_REL}",
                "introduced_in_unit": CHAPTER_ID,
            }
        )
    return output, mapping


def formula_records(
    source: str, target: str, ledger: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (237, 239):
        raise RuntimeError("Chapter 13 math closure changed")
    source_keys = [ch03_math.math_key(item["normalized"]) for item in source_math]
    target_keys = [ch03_math.math_key(item["normalized"]) for item in target_math]
    opcodes = SequenceMatcher(None, source_keys, target_keys, autojunk=False).get_opcodes()
    expected_shapes = [
        ("equal", 0, 24, 0, 24),
        ("insert", 24, 24, 24, 25),
        ("equal", 24, 25, 25, 26),
        ("delete", 25, 27, 26, 26),
        ("equal", 27, 35, 26, 34),
        ("replace", 35, 36, 34, 37),
        ("equal", 36, 174, 37, 175),
        ("insert", 174, 174, 175, 176),
        ("equal", 174, 237, 176, 239),
    ]
    if opcodes != expected_shapes:
        raise RuntimeError(f"Chapter 13 math opcode closure changed: {opcodes}")
    mapping: list[list[int] | None] = [None] * len(target_math)
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            for source_index, target_index in zip(range(i1, i2), range(j1, j2), strict=True):
                mapping[target_index] = [source_index]
    mapping[24] = [25, 26]
    mapping[34] = [35]
    mapping[35] = []
    mapping[36] = [35]
    mapping[175] = []
    if any(value is None for value in mapping):
        raise RuntimeError("Chapter 13 formula mapping incomplete")
    if {index for group in mapping for index in (group or [])} != set(range(len(source_math))):
        raise RuntimeError("Chapter 13 source formula coverage incomplete")

    correction_by_target_line = {
        30: "FAOA-2015-CH13-CORR-001",
        45: "FAOA-2015-CH13-CORR-002",
        46: "FAOA-2015-CH13-CORR-002",
        218: "FAOA-2015-CH13-CORR-005",
    }
    valid_corrections = {item["id"] for item in ledger["records"]}
    records = []
    exact = 0
    classified = 0
    insertions = 0
    for target_index, source_group_value in enumerate(mapping):
        source_group = source_group_value or []
        target_item = target_math[target_index]
        is_exact = (
            len(source_group) == 1
            and source_math[source_group[0]]["normalized"] == target_item["normalized"]
        )
        if is_exact:
            state = "preserved_exact_after_text_aware_whitespace_normalization"
            exact += 1
        elif not source_group:
            state = "reviewed_target_insertion_from_source_correction"
            insertions += 1
            classified += 1
        elif len(source_group) > 1:
            state = "reviewed_source_correction_consolidation"
            classified += 1
        else:
            state = "reviewed_source_correction_split_or_replacement"
            classified += 1
        source_items = [source_math[index] for index in source_group]
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{target_index + 1:04d}",
            "alignment": state,
            "ordinal_alignment": "target_insertion" if not source_group else "mapped",
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{index + 1:04d}" for index in source_group],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{target_index + 1:04d}"],
            "source_lines": [[item["line_start"], item["line_end"]] for item in source_items],
            "target_lines": [[target_item["line_start"], target_item["line_end"]]],
            "source_sha256": [item["sha256"] for item in source_items],
            "target_sha256": [target_item["sha256"]],
            "source_delimiters": [item["delimiter"] for item in source_items],
            "delimiter": target_item["delimiter"],
        }
        if not is_exact:
            correction_id = correction_by_target_line.get(target_item["line_start"])
            if correction_id not in valid_corrections:
                raise RuntimeError(f"formula delta lacks correction record: {target_index + 1}")
            record.update(
                sequence_opcode="insert" if not source_group else "replace",
                delta_class="classified_source_correction",
                correction_id=correction_id,
                correction_disposition="corrected",
                qa_state="passed",
            )
        records.append(record)
    return records, {
        "source_math_surfaces": len(source_math),
        "target_math_surfaces": len(target_math),
        "formula_map_records": len(records),
        "exact_or_reordered": exact,
        "classified_delta_maps": classified,
        "target_insertions": insertions,
    }


def artifact_records(ids: dict[str, dict[str, Any]], bind_final: bool) -> list[dict[str, Any]]:
    present_specs = [
        ("ARTIFACT-FAOA-ID-CH13-TARGET-TEX", "translation_source", TARGET_REL, "id-ID"),
        ("ARTIFACT-FAOA-ID-THROUGH-CH13-MASTER", "cumulative_TeX_master", MASTER_REL, "id-ID"),
        ("ARTIFACT-FAOA-ID-CH13-SOURCE-INVENTORY", "source_inventory", "qa/CH13_SOURCE_INVENTORY.md", None),
        ("ARTIFACT-FAOA-ID-CH13-PRETRANSLATION-REVIEW", "pretranslation_mathematical_review", "qa/CH13_PRETRANSLATION_MATH_REVIEW.md", None),
        ("ARTIFACT-FAOA-ID-CH13-BILINGUAL-REVIEW", "bilingual_mathematical_review", "qa/CH13_BILINGUAL_MATH_REVIEW.md", None),
        ("ARTIFACT-FAOA-ID-CH13-TRANSLATION-REPORT", "translation_QA_report", REPORT_REL, None),
        ("ARTIFACT-FAOA-ID-CH13-TERM-PLAN", "terminology_plan", TERM_PLAN_REL, None),
        ("ARTIFACT-FAOA-ID-CH13-CORRECTIONS-LEDGER", "chapter_source_corrections_ledger", LEDGER_REL, None),
        ("ARTIFACT-FAOA-ID-SOURCE-CORRECTIONS-AGGREGATE-CH13", "aggregate_source_corrections_log", "provenance/SOURCE_CORRECTIONS.md", None),
    ]
    final_specs = [
        ("ARTIFACT-FAOA-ID-THROUGH-CH13-PDF", "canonical_cumulative_reader_pdf", PDF_REL),
        ("ARTIFACT-FAOA-ID-CH13-FINAL-BUILD-RESULT", "deterministic_build_result", BUILD_RESULT_REL),
        ("ARTIFACT-FAOA-ID-CH13-RENDER-MANIFEST", "visual_QA_render_manifest", RENDER_MANIFEST_REL),
        ("ARTIFACT-FAOA-ID-CH13-RENDER-AUDIT", "visual_QA_audit", RENDER_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH13-ACCESSIBILITY-AUDIT", "visual_accessibility_audit", ACCESSIBILITY_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH13-QA-RECEIPT", "admission_receipt", RECEIPT_REL),
    ]
    output = []
    for stable_id, kind, relative_path, locale in present_specs:
        info = identity(ROOT / relative_path)
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": stable_id,
            "unit_id": CHAPTER_ID,
            "artifact_kind": kind,
            "path": relative_path,
            "bytes": info["bytes"],
            "lines": info["lines"],
            "sha256": info["sha256"],
            "binding_state": "bound",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if locale:
            record["locale"] = locale
        if kind == "cumulative_TeX_master":
            record["cumulative_through_unit_id"] = CHAPTER_ID
        output.append(record)
    for stable_id, kind, relative_path in final_specs:
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": stable_id,
            "unit_id": CHAPTER_ID,
            "artifact_kind": kind,
            "path": relative_path,
            "binding_state": "bound" if bind_final else "pending_final_artifact_binding",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if bind_final:
            info = identity(ROOT / relative_path)
            record.update(bytes=info["bytes"], sha256=info["sha256"])
            if not relative_path.endswith(".pdf"):
                record["lines"] = info["lines"]
            if kind == "canonical_cumulative_reader_pdf":
                record.update(
                    pages=ids["pdf"]["pages"],
                    page_size="US Letter",
                    pdf_lang="id-ID",
                    publication_state="pending",
                )
            if kind == "visual_QA_render_manifest":
                record["render_pages"] = ids["pdf"]["pages"]
            if kind == "admission_receipt":
                record["decision"] = "admitted"
        output.append(record)
    return output


def qa_records(
    ids: dict[str, dict[str, Any]],
    formula_summary: dict[str, int],
    bind_final: bool,
    prefix_lock_sha256: str,
) -> list[dict[str, Any]]:
    base_record = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "timestamp": "2026-08-24",
        "responsible_workflow": "Codex",
        "model_id": MODEL_ID,
    }
    specs = [
        ("QA-CH13-STRUCTURAL-20260824", "unit_structural", REPORT_REL, "pass"),
        ("QA-CH13-MATH-20260824", "unit_mathematical", "qa/CH13_BILINGUAL_MATH_REVIEW.md", "pass"),
        ("QA-CH13-LANGUAGE-20260824", "unit_language_terminology", TERM_PLAN_REL, "pass"),
        ("QA-CH13-EXERCISE-SUPPORT-20260824", "exercise_support_provenance", "qa/CH13_SOURCE_INVENTORY.md", "pass"),
        ("QA-CH13-RIGHTS-20260824", "unit_rights_privacy", RECEIPT_REL, "pass" if bind_final else "pending"),
        ("QA-CH13-BUILD-20260824", "cumulative_build", BUILD_RESULT_REL, "pass" if bind_final else "pending"),
        ("QA-CH13-VISUAL-20260824", "cumulative_visual", RENDER_AUDIT_REL, "pass" if bind_final else "pending"),
        ("QA-CH13-ACCESSIBILITY-20260824", "cumulative_accessibility", ACCESSIBILITY_AUDIT_REL, "pass" if bind_final else "pending"),
        ("QA-CH13-BACKEND-20260824", "backend_reconciliation", PREFIX_LOCK_REL, "pass"),
        ("QA-CH13-ADMISSION-20260824", "unit_admission", RECEIPT_REL, "pass" if bind_final else "pending"),
    ]
    output = []
    for stable_id, kind, witness, result in specs:
        record = base_record | {
            "id": stable_id,
            "qa_type": kind,
            "result": result,
            "witness": witness,
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if stable_id == "QA-CH13-BACKEND-20260824":
            record["witness_sha256"] = prefix_lock_sha256
        elif result == "pass" and (ROOT / witness).is_file():
            record["witness_sha256"] = sha((ROOT / witness).read_bytes())
        else:
            record["witness_state"] = "pending_final_artifact_binding"
        output.append(record)
    output[0].update(
        sections=3,
        environment_begins=32,
        labels=7,
        references=2,
        citations=7,
        index_terms=28,
        defined_terms=13,
        exercise_environments=1,
        proof_environments=2,
        proof_hints=0,
        citation_only_proofs=2,
    )
    output[1].update(formula_summary | {"unexplained_deltas": 0, "extractor": "backend/ch03_math.py"})
    output[2].update(
        severity_counts={"P1": 0, "P2": 0, "P3": 0},
        unintended_english_prose=0,
        placeholders=0,
        preferred_dense_term="padat",
    )
    output[3].update(
        source_exercises=1,
        upstream_hints=0,
        upstream_answers=0,
        upstream_solutions=0,
        original_solution_state="queued_in_O001",
        provenance="separately_authored_not_Erdman",
    )
    output[4].update(
        rights_id=RIGHTS,
        attribution_change_notice_sharealike_nonendorsement="present",
        credential_or_token_residue=0,
    )
    if bind_final:
        output[5].update(
            master_artifact_id="ARTIFACT-FAOA-ID-THROUGH-CH13-MASTER",
            pdf_artifact_id="ARTIFACT-FAOA-ID-THROUGH-CH13-PDF",
            pages=ids["pdf"]["pages"],
        )
        output[6].update(pages_rendered=ids["pdf"]["pages"], pages_inspected=ids["pdf"]["pages"], visual_defects=0)
        output[7].update(
            tagged_pdf=False,
            fully_accessible_pdf_claim=False,
            semantic_accessibility_state="remediation_required",
            accessible_html_or_tagged_pdf_state="pending",
            admission_blocker_for_chapter_boundary=False,
        )
        output[9].update(
            decision="admitted",
            source_sha256=ids["source"]["sha256"],
            target_sha256=ids["target"]["sha256"],
            build_master_sha256=ids["master"]["sha256"],
            artifact_sha256=ids["pdf"]["sha256"],
            correction_ledger_sha256=ids["ledger"]["sha256"],
            receipt_sha256=ids["receipt"]["sha256"],
            all_required_admission_gates="pass",
            publication_state="pending",
        )
    return output


def exercise_support_record(exercise_unit_id: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "exercise_support",
        "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-001",
        "exercise_unit_id": exercise_unit_id,
        "source_exercise_order": 1,
        "upstream_hint_ids": [],
        "upstream_inline_hint_state": "absent",
        "upstream_answer_state": "absent",
        "upstream_solution_state": "absent",
        "original_solution_id": f"O001-{CHAPTER_ID}-EX-001-SOLUTION",
        "original_solution_state": "queued_in_O001",
        "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0",
        "provenance": "separately_authored_not_Erdman",
    }


def build_outputs(bind_final: bool) -> tuple[dict[str, bytes], dict[str, Any]]:
    configure_base()
    was_initial = initial_state()
    records, index_fields, index_rows = load_data()
    strip_ch13(records, index_rows)
    base.assert_unit_order(records["units.jsonl"])
    _, locks = prefix_payload(records, index_fields, index_rows)
    lock_bytes = (json.dumps(locks, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    lock_path = ROOT / PREFIX_LOCK_REL
    if lock_path.is_file() and not was_initial:
        if lock_path.read_bytes() != lock_bytes:
            raise RuntimeError("Chapter 1--12 prefix lock differs after stripping Chapter 13")
    elif not was_initial:
        raise RuntimeError("backend is neither exact Chapter 12 state nor locked Chapter 13 state")

    ids, ledger = evidence(bind_final)
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    semantic, segments, relations, source_anchors, _ = base.build_units_and_segments(source, target)
    if bind_final:
        for record in semantic + segments:
            record["translation_state"] = "admitted"
            record["admission_state"] = "admitted"

    semantic_offsets = []
    anchor_ids = []
    section_number = node_number = 0
    for anchor in source_anchors:
        if anchor["anchor_type"] == "chapter":
            anchor_ids.append(CHAPTER_ID)
        elif anchor["anchor_type"] == "section":
            section_number += 1
            anchor_ids.append(f"{CHAPTER_ID}-SEC-{section_number:03d}")
        else:
            node_number += 1
            anchor_ids.append(f"{CHAPTER_ID}-NODE-{node_number:04d}")
    for anchor, stable_id in zip(source_anchors, anchor_ids, strict=True):
        if anchor["anchor_type"] != "chapter":
            semantic_offsets.append((anchor["start"], anchor["end"], stable_id))

    prior_labels = {
        item.get("source_local_id"): item["id"]
        for item in records["semantic_units.jsonl"]
        if item.get("source_local_id")
    }
    local_labels: dict[str, str] = {}
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 7 or [item["argument"] for item in source_labels] != [item["argument"] for item in target_labels]:
        raise RuntimeError("Chapter 13 label sequence differs")
    for number, occurrence in enumerate(source_labels, 1):
        candidates = [
            (end - start, stable_id)
            for start, end, stable_id in semantic_offsets
            if start <= occurrence["start"] < end
        ]
        owner = min(candidates)[1] if candidates else CHAPTER_ID
        segment_id = base.ch01.containing_segment(segments, occurrence["start"], "source")
        local_labels[occurrence["argument"]] = owner
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-LABEL-{number:04d}",
                "relation_type": "declares_label",
                "from_id": segment_id,
                "to_id": owner,
                "source_local_id": occurrence["argument"],
                "label_id": f"ERDMAN-FAOA-2015-LABEL-{occurrence['argument']}",
            }
        )

    source_refs = common.reference_sequence(source)
    target_refs = common.reference_sequence(target)
    if len(source_refs) != 2 or len(target_refs) != 2:
        raise RuntimeError("Chapter 13 reference count changed")
    resolution_counts: collections.Counter[str] = collections.Counter()
    for number, (source_ref, target_ref) in enumerate(zip(source_refs, target_refs, strict=True), 1):
        source_position, source_kind, source_label = source_ref
        _, target_kind, target_label = target_ref
        if target_label in local_labels:
            endpoint, resolution = local_labels[target_label], "local"
        elif target_label in prior_labels:
            endpoint, resolution = prior_labels[target_label], "admitted_prior_unit"
        else:
            raise RuntimeError(f"unresolved Chapter 13 reference: {source_label!r} -> {target_label!r}")
        resolution_counts[resolution] += 1
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}",
                "relation_type": "xref",
                "from_id": base.ch01.containing_segment(segments, source_position, "source"),
                "to_id": endpoint,
                "source_local_id": source_label,
                "target_local_id": target_label,
                "resolution": resolution,
                "source_surface": source_kind,
                "target_surface": target_kind,
            }
        )

    source_citations = common.macro(source, "cite")
    target_citations = common.macro(target, "cite")
    if len(source_citations) != 7 or [item["argument"] for item in source_citations] != [item["argument"] for item in target_citations]:
        raise RuntimeError("Chapter 13 citation sequence differs")
    for number, occurrence in enumerate(source_citations, 1):
        key = occurrence["argument"]
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-CITE-{number:04d}",
                "relation_type": "cites",
                "from_id": base.ch01.containing_segment(segments, occurrence["start"], "source"),
                "to_id": f"ERDMAN-FAOA-BIB-{key}",
                "source_local_id": key,
            }
        )

    terms, term_mapping = terminology_records(source, target, records["terminology.jsonl"])
    source_terms = common.macro(source, "df")
    target_terms = common.macro(target, "df")
    for number, (source_term, target_term) in enumerate(zip(source_terms, target_terms, strict=True), 1):
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}",
                "relation_type": "uses_term",
                "from_id": base.ch01.containing_segment(segments, source_term["start"], "source"),
                "to_id": term_mapping[source_term["argument"]],
                "source_term_tex": source_term["argument"],
                "target_term_tex": target_term["argument"],
                "locale": "id-ID",
            }
        )

    source_indexes = common.macro(source, "index")
    target_indexes = common.macro(target, "index")
    if len(source_indexes) != 28 or len(target_indexes) != 28:
        raise RuntimeError("Chapter 13 index count changed")
    new_index_rows = []
    for number, (source_index, target_index) in enumerate(zip(source_indexes, target_indexes, strict=True), 1):
        new_index_rows.append(
            {
                "id": f"{CHAPTER_ID}-TERM-OCC-{number:04d}",
                "parent_segment_id": base.ch01.containing_segment(segments, source_index["start"], "source"),
                "source_order": str(number),
                "source_line": str(source_index["line"]),
                "source_index_tex": source_index["argument"],
                "target_line": str(target_index["line"]),
                "target_index_tex": target_index["argument"],
                "source_sha256": sha(source_index["argument"].encode("ascii")),
                "target_sha256": sha(target_index["argument"].encode("utf-8")),
                "locale": "id-ID",
            }
        )

    receipt_sha = ids.get("receipt", {}).get("sha256")
    corrections = correction_records(ledger, ids["ledger"]["sha256"], bind_final, receipt_sha)
    formulas, formula_summary = formula_records(source, target, ledger)
    artifacts = artifact_records(ids, bind_final)
    qa = qa_records(ids, formula_summary, bind_final, sha(lock_bytes))
    exercises = [record for record in semantic if record["unit_kind"] == "exer"]
    if len(exercises) != 1:
        raise RuntimeError("Chapter 13 exercise semantic closure differs")
    support = exercise_support_record(exercises[0]["id"])

    common_relation = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "relation",
        "from_id": CHAPTER_ID,
    }
    relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS})
    for number, artifact in enumerate(artifacts, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}", "relation_type": "has_artifact", "to_id": artifact["id"]})
    for number, event in enumerate(qa, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-QA-{number:04d}", "relation_type": "has_qa_event", "to_id": event["id"]})
    for number, correction in enumerate(corrections, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}", "relation_type": "documents_correction", "to_id": correction["id"]})
    relations.append(
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-EXERCISE-SUPPORT-0001",
            "relation_type": "has_exercise_support",
            "from_id": exercises[0]["id"],
            "to_id": support["id"],
        }
    )

    for segment in segments:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            segment.pop(key, None)
    records["semantic_units.jsonl"].extend(semantic)
    records["segments.jsonl"].extend(segments)
    records["relations.jsonl"].extend(relations)
    records["formula_map.jsonl"].extend(formulas)
    records["exercise_support.jsonl"].append(support)
    records["artifacts.jsonl"].extend(artifacts)
    records["qa_events.jsonl"].extend(qa)
    records["corrections.jsonl"].extend(corrections)
    records["terminology.jsonl"].extend(terms)
    index_rows.extend(new_index_rows)
    records["units.jsonl"] = [
        chapter_unit(ids, corrections, bind_final) if item.get("id") == CHAPTER_ID else item
        for item in records["units.jsonl"]
    ]

    outputs = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    outputs["index_terms.csv"] = csv_bytes(index_fields, index_rows)
    outputs["CH13_PREFIX_LOCKS.json"] = lock_bytes
    outputs["BACKEND_MANIFEST.csv"] = base.manifest_bytes(outputs)
    summary = {
        "unit": CHAPTER_ID,
        "binding_state": "bound" if bind_final else "pending_final_artifact_binding",
        "semantic_units": len(semantic),
        "segments": len(segments),
        "relations": len(relations),
        "formula_maps": len(formulas),
        "index_rows": len(new_index_rows),
        "new_terms": len(terms),
        "corrections": len(corrections),
        "exercise_support": 1,
        "qa_events": len(qa),
        "artifacts": len(artifacts),
        "reference_resolution": dict(resolution_counts),
        "target_sha256": ids["target"]["sha256"],
    }
    return outputs, summary


def reconciliation_report(summary: dict[str, Any], outputs: dict[str, bytes]) -> bytes:
    names = [
        "units.jsonl",
        "semantic_units.jsonl",
        "segments.jsonl",
        "relations.jsonl",
        "formula_map.jsonl",
        "exercise_support.jsonl",
        "index_terms.csv",
        "artifacts.jsonl",
        "qa_events.jsonl",
        "corrections.jsonl",
        "terminology.jsonl",
        "CH13_PREFIX_LOCKS.json",
        "BACKEND_MANIFEST.csv",
    ]
    if summary["binding_state"] == "bound":
        boundary_line = (
            "Generated from the passing Chapter 13 translation report, correction ledger, frozen PDF, "
            "render evidence, deterministic-build result, and admission receipt."
        )
        artifact_line = (
            "- The Chapter 13 PDF byte count, page count, SHA-256 identity, and admission-receipt "
            "identity are bound in the admitted slice."
        )
    else:
        boundary_line = (
            "Generated from the passing Chapter 13 translation report and correction ledger. The final "
            "PDF and admission receipt are deliberately unbound; run `python "
            "backend/generate_ch13_backend.py --bind-final-artifacts` only after both are frozen."
        )
        artifact_line = (
            "- No final PDF byte count, page count, or cryptographic hash is present in the pending "
            "Chapter 13 slice."
        )
    lines = [
        "# FAOA-2015-CH13 backend reconciliation",
        "",
        boundary_line,
        "",
        f"- Target: `{TARGET_REL}` — {EXPECTED_TARGET[0]} bytes, SHA-256 `{EXPECTED_TARGET[2]}`.",
        f"- Semantic units: {summary['semantic_units']}; segments: {summary['segments']}; relations: {summary['relations']}; formula maps: {summary['formula_maps']}; index rows: {summary['index_rows']}.",
        f"- New terminology records: {summary['new_terms']}; correction records: {summary['corrections']}; exercise-support records: {summary['exercise_support']}; QA events: {summary['qa_events']}; artifacts: {summary['artifacts']}.",
        "- The complete admitted Chapter 1--12 prefix is locked in `backend/CH13_PREFIX_LOCKS.json`.",
        "- Relation endpoint, stable-ID, formula, index, exercise-support, manifest, and deterministic round-trip validation is performed by `backend/validate_ch13_backend.py`.",
        artifact_line,
        "",
        "Generated backend file identities:",
        "",
    ]
    lines.extend(f"- `{name}` — {len(outputs[name])} bytes, SHA-256 `{sha(outputs[name])}`" for name in names)
    return ("\n".join(lines) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind-final-artifacts", action="store_true")
    parser.add_argument("--check", action="store_true", help="compare generated bytes without writing")
    args = parser.parse_args()
    outputs, summary = build_outputs(args.bind_final_artifacts)
    if args.check:
        mismatches = [
            name
            for name, expected in outputs.items()
            if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != expected
        ]
        if mismatches:
            raise RuntimeError("deterministic backend replay differs: " + ", ".join(mismatches))
        print(json.dumps(summary | {"deterministic_replay": "pass"}, sort_keys=True))
        return
    for name, data in outputs.items():
        (BACKEND / name).write_bytes(data)
    report = reconciliation_report(summary, outputs)
    (ROOT / "qa/CH13_BACKEND_RECONCILIATION.md").write_bytes(report)
    print(json.dumps(summary | {"backend_report": "qa/CH13_BACKEND_RECONCILIATION.md"}, sort_keys=True))


if __name__ == "__main__":
    main()
