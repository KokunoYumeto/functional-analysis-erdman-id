#!/usr/bin/env python3
"""Deterministically append the FAOA-2015-CH15 backend slice."""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path[:0] = [str(BACKEND), str(ROOT / "qa")]
import generate_ch14_backend as prior  # noqa: E402


ch03_math = prior.ch03_math
common = prior.common
base = prior.base
sha = prior.sha
jsonl_bytes = prior.jsonl_bytes
csv_bytes = prior.csv_bytes
page_count = prior.page_count

SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH15"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_REL = "source/upstream/fredholm_theory.tex"
TARGET_REL = "source/id-ID/fredholm_theory-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-through-ch15.tex"
INVENTORY_REL = "qa/CH15_SOURCE_INVENTORY.md"
PRE_REVIEW_REL = "qa/CH15_PRETRANSLATION_MATH_REVIEW.md"
REPORT_REL = "qa/ch15-translation-report.json"
BILINGUAL_REVIEW_REL = "qa/CH15_BILINGUAL_MATH_REVIEW.md"
LEDGER_REL = "provenance/SOURCE_CORRECTIONS_CH15.json"
TERM_PLAN_REL = "provenance/CH15_TERMINOLOGY_PLAN.md"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-15.pdf"
RECEIPT_REL = "provenance/CH15_BUILD_AND_QA_RECEIPT.md"
RENDER_MANIFEST_REL = "provenance/CH15_RENDER_MANIFEST.csv"
RENDER_AUDIT_REL = "qa/CH15_RENDER_AUDIT.json"
ACCESSIBILITY_AUDIT_REL = "qa/CH15_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
BUILD_RESULT_REL = "qa/CH15_FINAL_BUILD_RESULT.json"
PREFIX_LOCK_REL = "backend/CH15_PREFIX_LOCKS.json"

SOURCE_PATH = ROOT / SOURCE_REL
TARGET_PATH = ROOT / TARGET_REL

# (bytes, logical records or None, SHA-256)
EXPECTED_SOURCE = (16_977, 444, "0ef2e5be3c716a099e8609a84528d77ad6387ec531c52f9890d4e34175c57d91")
EXPECTED_TARGET = (17_672, 444, "174b1ad2557f7dfa10e8171bd7482d907f858389b509f4d55de9cc785e2b43ba")
EXPECTED_MASTER = (10_541, 344, "f2df36c70dcca86f44687efe450ea46a5611be2d1170a9ded16dbfbfcdb73a33")
EXPECTED_INVENTORY = (5_246, 123, "b27bb18855c4ca1fd819163fe68c5e452b51ce898aac7e4bdb54ff03eb989b57")
EXPECTED_PRE_REVIEW = (8_269, 156, "8f539538de2b74a37bfc347facd1a2b81e3fa4130afbba40c617842c40401c25")
EXPECTED_REPORT = (5_942, 158, "ae12ef71a0c4fa09895ac3bbb547da1b89e994f5b23a3551fddf324379f2d84d")
EXPECTED_BILINGUAL = (6_538, 121, "ae0d17272540c21ef730150199ccf66b8a98fa0897e923c3d433f0dc55a556ae")
EXPECTED_LEDGER = (21_257, 297, "c33a8ab24250c376e63ce6fd45aeb42cdd4590a169f9a00efab705fac087e887")
EXPECTED_TERM_PLAN = (4_598, 87, "e790b352a689ce0169a133a7fce469eda1391bd61ba811b4abbb6b50ac25ed5c")
EXPECTED_PDF = (2_156_827, None, "5b8d5d5f44671f4695dea7f470d6ea7bb63fd2a0ff459aa8e8fb1a0c0faac7c7")
EXPECTED_BUILD_RESULT = (1_148, 36, "545cc604baf5cb720d7205eac83865a16af5629edc0b392e7dc79fba6e1a6ffe")
EXPECTED_RENDER_MANIFEST = (22_901, 201, "1b4aae6c68668641aa4f86eb6aba87720017df9676773b532dbcf7da06265567")
EXPECTED_RENDER_AUDIT = (4_313, 194, "294705139b6c1a8dd46cbb725579b0114633a0ed58740d0b41d2214414717048")
EXPECTED_ACCESSIBILITY = (3_648, 72, "90fcfd11e32a8406a6d5cb5d3cd4c6fcc71fe7a6afae159fe94985e0921bc3c9")
EXPECTED_RECEIPT = (8_080, 157, "7aa1f8c383e4366df8e30042a2212c7ba2e319d5d22aa42edf525cbd0a370f0e")
EXPECTED_AGGREGATE_CORRECTIONS = (43_492, 788, "85fe4b1afc625359ab6e43dad3b76b2ae8989c23e831627a8ec8a0ff655f9add")

JSONL_FILES = base.JSONL_FILES
INITIAL_LOCKS = {
    "units.jsonl": (21_506, "2cd200387e657d1791e11f7682507297d436d67d79fa175f4b132d4d5f6ef47a"),
    "semantic_units.jsonl": (1_276_531, "ed5a50b0a923122ac0a7a64034d9b3466e5f9500504e53a62b15104e8d5bbe43"),
    "segments.jsonl": (1_427_948, "67654fa2c4ea845e48271c66f88072370ba4b234284fa571a52fe8cc71c2aea7"),
    "relations.jsonl": (1_816_174, "839b09edd3fd134820b8d8e71b2cbae9437b879991a79b1700d9edf6b6e8e55d"),
    "formula_map.jsonl": (6_099_685, "2afdc784b94534b416c8bd575b08ec5a773a5f0331bde704f4e3a90820f50dd1"),
    "exercise_support.jsonl": (27_135, "da1bd2f951ec0982cefce076ea5bd64a69c14613102ce1d7e17ed056a1763ffc"),
    "index_terms.csv": (460_561, "3f14a26f348e4e055a74d9949bb2c6ad3f0dc479df295633944f50c888eaafb2"),
    "artifacts.jsonl": (79_682, "d657bd0854348490c42a2a934a3612a6195de584139d695ace1c449d24763b47"),
    "qa_events.jsonl": (100_546, "b673dff5b3332da0872a065fbf840ebd71869d42e446be4c8f44a249ec856bff"),
    "corrections.jsonl": (204_188, "03e12ecc5d0bc191bffb504f05968ffc0e1f1dfba21511e4d708ede93d778e85"),
    "terminology.jsonl": (151_500, "5af6a5cd4bbd89ad3827010f9b938036329da65d18dbb573f0ec10e0a1bcfce2"),
}

QUEUED_CH15 = {
    "schema": SCHEMA, "schema_version": VERSION, "record_type": "unit",
    "id": CHAPTER_ID, "edition_id": EDITION, "order": 15,
    "source_path": "fredholm_theory.tex", "source_bytes": EXPECTED_SOURCE[0],
    "source_lines": EXPECTED_SOURCE[1], "source_sha256": EXPECTED_SOURCE[2],
    "source_title": "FREDHOLM THEORY", "course_role": "advanced_continuation",
    "translation_state": "queued", "rights_id": RIGHTS,
}

EXPECTED_SOURCE_TERMS = [
    "Riesz-Schauder", "cokernel", "codimension", "Calkin algebra",
    "Fredholm operator", "Fredholm index", "index", "path",
    "connected by a path", "homotopic in~$X$", "path components",
]
EXPECTED_TARGET_TERMS = [
    "operator Riesz--Schauder", "kokernel", "kodimensi", "aljabar Calkin",
    "operator Fredholm", "indeks Fredholm", "indeks", "lintasan",
    "terhubung oleh lintasan", "homotop dalam~$X$", "komponen lintasan",
]
TERM_OCCURRENCE_IDS = [
    "TERM-RIESZ-SCHAUDER-OPERATOR", "TERM-COKERNEL", "TERM-CODIMENSION",
    "TERM-CALKIN-ALGEBRA", "TERM-FREDHOLM-OPERATOR", "TERM-FREDHOLM-INDEX",
    "TERM-INDEX", "TERM-PATH", "TERM-PATH-CONNECTED", "TERM-HOMOTOPIC",
    "TERM-PATH-COMPONENT",
]
NEW_TERM_SPECS = {
    "TERM-RIESZ-SCHAUDER-OPERATOR": ("Riesz-Schauder", "operator Riesz--Schauder", ["operator Riesz-Schauder"], []),
    "TERM-CALKIN-ALGEBRA": ("Calkin algebra", "aljabar Calkin", [], []),
    "TERM-FREDHOLM-OPERATOR": ("Fredholm operator", "operator Fredholm", [], []),
    "TERM-FREDHOLM-INDEX": ("Fredholm index", "indeks Fredholm", [], []),
    "TERM-INDEX": ("index", "indeks", [], []),
    "TERM-PATH": ("path", "lintasan", [], []),
    "TERM-PATH-CONNECTED": ("connected by a path", "terhubung oleh lintasan", ["terhubung lintasan"], []),
    "TERM-HOMOTOPIC": ("homotopic in~$X$", "homotop dalam~$X$", [], []),
    "TERM-PATH-COMPONENT": ("path components", "komponen lintasan", [], []),
}
EXTERNAL_PRIOR_LABELS = {"sec_onbases", "001902", "cor2_Neumann_series"}


def identity(path: Path, expected: tuple[int, int | None, str] | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    value = {
        "path": path.relative_to(ROOT).as_posix(), "bytes": len(data),
        "lines": len(data.splitlines()), "sha256": sha(data),
    }
    if expected:
        actual = (value["bytes"], value["sha256"])
        wanted = (expected[0], expected[2])
        if actual != wanted or (expected[1] is not None and value["lines"] != expected[1]):
            raise RuntimeError(f"identity mismatch: {value}")
    return value


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


def strip_ch15(records: dict[str, list[dict[str, Any]]], index_rows: list[dict[str, str]]) -> None:
    for name, values in records.items():
        if name == "units.jsonl":
            values[:] = [QUEUED_CH15.copy() if item.get("id") == CHAPTER_ID else item for item in values]
            continue
        values[:] = [
            item for item in values
            if not (
                str(item.get("id", "")).startswith(CHAPTER_ID + "-")
                or item.get("unit_id") == CHAPTER_ID
                or item.get("introduced_in_unit") == CHAPTER_ID
                or str(item.get("exercise_unit_id", "")).startswith(CHAPTER_ID + "-")
            )
        ]
    index_rows[:] = [row for row in index_rows if not row.get("id", "").startswith(CHAPTER_ID + "-")]


def prefix_payload(
    records: dict[str, list[dict[str, Any]]], fields: list[str], index_rows: list[dict[str, str]]
) -> tuple[dict[str, bytes], dict[str, Any]]:
    payload = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    payload["index_terms.csv"] = csv_bytes(fields, index_rows)
    locks = {
        "schema_version": "o008.ch15-prefix-locks.v1", "unit_id": CHAPTER_ID,
        "scope": "complete admitted Chapters 1--14 backend; excludes every Chapter 15-derived record",
        "files": {
            name: {
                "bytes": len(data), "sha256": sha(data),
                "records": len(records[name]) if name in records else len(index_rows),
            }
            for name, data in payload.items()
        },
    }
    return payload, locks


def stripped_prefix() -> tuple[
    dict[str, list[dict[str, Any]]], list[str], list[dict[str, str]], bytes, bool
]:
    configure_base()
    was_initial = initial_state()
    records, fields, index_rows = load_data()
    strip_ch15(records, index_rows)
    base.assert_unit_order(records["units.jsonl"])
    _, locks = prefix_payload(records, fields, index_rows)
    lock_bytes = (json.dumps(locks, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    lock_path = ROOT / PREFIX_LOCK_REL
    if not was_initial:
        if not lock_path.is_file() or lock_path.read_bytes() != lock_bytes:
            raise RuntimeError("backend is neither the exact Chapter 14 state nor a locked Chapter 15 state")
    return records, fields, index_rows, lock_bytes, was_initial


def target_sha(document: dict[str, Any]) -> str | None:
    values = [
        document.get("target_sha256"), document.get("identities", {}).get("target_sha256"),
        document.get("target", {}).get("sha256"),
        document.get("identities", {}).get("target", {}).get("sha256"),
    ]
    return next((value for value in values if isinstance(value, str)), None)


def ledger_records(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    records = ledger.get("records")
    if not isinstance(records, list) or len(records) != 9 or ledger.get("record_count") != 9:
        raise RuntimeError("Chapter 15 correction ledger closure differs")
    expected = [f"{CHAPTER_ID}-CORR-{number:03d}" for number in range(1, 10)]
    if [item.get("id") for item in records] != expected:
        raise RuntimeError("Chapter 15 correction IDs/order differ")
    return records


def evidence(bind_final: bool) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    ids = {
        "source": identity(SOURCE_PATH, EXPECTED_SOURCE),
        "target": identity(TARGET_PATH, EXPECTED_TARGET),
        "master": identity(ROOT / MASTER_REL, EXPECTED_MASTER),
        "inventory": identity(ROOT / INVENTORY_REL, EXPECTED_INVENTORY),
        "pre_review": identity(ROOT / PRE_REVIEW_REL, EXPECTED_PRE_REVIEW),
        "report": identity(ROOT / REPORT_REL, EXPECTED_REPORT),
        "bilingual_review": identity(ROOT / BILINGUAL_REVIEW_REL, EXPECTED_BILINGUAL),
        "ledger": identity(ROOT / LEDGER_REL, EXPECTED_LEDGER),
        "term_plan": identity(ROOT / TERM_PLAN_REL, EXPECTED_TERM_PLAN),
        "pdf": identity(ROOT / PDF_REL, EXPECTED_PDF),
        "build_result": identity(ROOT / BUILD_RESULT_REL, EXPECTED_BUILD_RESULT),
        "render_manifest": identity(ROOT / RENDER_MANIFEST_REL, EXPECTED_RENDER_MANIFEST),
        "render_audit": identity(ROOT / RENDER_AUDIT_REL, EXPECTED_RENDER_AUDIT),
        "accessibility": identity(ROOT / ACCESSIBILITY_AUDIT_REL, EXPECTED_ACCESSIBILITY),
        "aggregate_corrections": identity(ROOT / "provenance/SOURCE_CORRECTIONS.md", EXPECTED_AGGREGATE_CORRECTIONS),
    }
    ids["pdf"]["pages"] = page_count(ROOT / PDF_REL)
    if ids["pdf"]["pages"] != 200:
        raise RuntimeError("Chapter 15 PDF page closure differs")
    report = json.loads((ROOT / REPORT_REL).read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / LEDGER_REL).read_text(encoding="utf-8"))
    build = json.loads((ROOT / BUILD_RESULT_REL).read_text(encoding="utf-8"))
    render = json.loads((ROOT / RENDER_AUDIT_REL).read_text(encoding="utf-8"))
    if report.get("status") != "pass" or report.get("unit_id") != CHAPTER_ID or target_sha(report) != EXPECTED_TARGET[2]:
        raise RuntimeError("Chapter 15 translation report is stale or not passing")
    if ledger.get("unit_id") != CHAPTER_ID or target_sha(ledger) != EXPECTED_TARGET[2]:
        raise RuntimeError("Chapter 15 correction ledger is stale")
    ledger_records(ledger)
    if not build.get("byte_identical") or build.get("pages") != 200 or build.get("reader", {}).get("sha256") != EXPECTED_PDF[2]:
        raise RuntimeError("Chapter 15 deterministic-build evidence differs")
    if render.get("page_count") != 200 or render.get("pdf", {}).get("sha256") != EXPECTED_PDF[2]:
        raise RuntimeError("Chapter 15 render evidence differs")
    if bind_final:
        receipt = ROOT / RECEIPT_REL
        if not receipt.is_file():
            raise RuntimeError("final artifact binding input missing: " + RECEIPT_REL)
        receipt_text = receipt.read_text(encoding="utf-8")
        if CHAPTER_ID not in receipt_text or not re.search(r"\badmitted\b", receipt_text, re.I):
            raise RuntimeError("Chapter 15 receipt does not assert this unit admitted")
        ids["receipt"] = identity(receipt, EXPECTED_RECEIPT)
    return ids, ledger


def preflight() -> dict[str, Any]:
    _, _, _, lock_bytes, was_initial = stripped_prefix()
    ids, ledger = evidence(False)
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    checks = {
        "source_records": len(source.splitlines()), "target_records": len(target.splitlines()),
        "sections": len(common.macro(source, "section")), "labels": len(common.macro(source, "label")),
        "references": len(common.reference_sequence(source)), "citations": len(common.macro(source, "cite")),
        "index_terms": len(common.macro(source, "index")), "defined_terms": len(common.macro(source, "df")),
        "source_math_surfaces": len(ch03_math.extract_math(source, "ascii")),
        "target_math_surfaces": len(ch03_math.extract_math(target, "utf-8")),
        "corrections": len(ledger_records(ledger)), "pdf_pages": ids["pdf"]["pages"],
    }
    expected = {
        "source_records": 444, "target_records": 444, "sections": 4, "labels": 33,
        "references": 27, "citations": 17, "index_terms": 46, "defined_terms": 11,
        "source_math_surfaces": 203, "target_math_surfaces": 204,
        "corrections": 9, "pdf_pages": 200,
    }
    if checks != expected:
        raise RuntimeError(f"Chapter 15 preflight closure differs: {checks}")
    return {
        "status": "pass", "unit_id": CHAPTER_ID,
        "backend_prefix_state": "exact_chapter14" if was_initial else "stripped_locked_chapter15",
        "prefix_lock_sha256": sha(lock_bytes), "identities": ids,
        "structural_closure": checks,
        "receipt_state": "present" if (ROOT / RECEIPT_REL).is_file() else "pending",
        "writes_performed": False,
    }


def chapter_unit(
    ids: dict[str, dict[str, Any]], corrections: list[dict[str, Any]], bind_final: bool
) -> dict[str, Any]:
    record = QUEUED_CH15 | {
        "target_path": TARGET_REL, "target_bytes": ids["target"]["bytes"],
        "target_lines": ids["target"]["lines"], "target_sha256": ids["target"]["sha256"],
        "target_title": common.macro(TARGET_PATH.read_text(encoding="utf-8"), "chapter")[0]["argument"],
        "translation_state": "admitted" if bind_final else "qa_passed_pending_artifact_binding",
        "qa_state": "passed", "source_corrections": len(corrections),
        "build_master_path": MASTER_REL, "build_master_bytes": ids["master"]["bytes"],
        "build_master_lines": ids["master"]["lines"], "build_master_sha256": ids["master"]["sha256"],
        "artifact_path": PDF_REL,
        "artifact_state": "canonical_output_copy_present_and_frozen" if bind_final else "pending_final_artifact_binding",
        "publication_state": "pending", "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        "receipt_path": RECEIPT_REL, "model_provenance": MODEL_ID,
    }
    if bind_final:
        record.update(
            artifact_bytes=ids["pdf"]["bytes"], artifact_pages=ids["pdf"]["pages"],
            artifact_sha256=ids["pdf"]["sha256"], qa_receipt_id="QA-CH15-ADMISSION-20260824",
            receipt_sha256=ids["receipt"]["sha256"],
        )
    return record


def correction_records(
    ledger: dict[str, Any], ledger_sha: str, bind_final: bool, receipt_sha: str | None
) -> list[dict[str, Any]]:
    output = []
    for item in ledger_records(ledger):
        source_lines, target_lines = item["source_lines"], item["target_lines"]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "correction",
            "id": item["id"], "unit_id": CHAPTER_ID,
            "source_locator": f"fredholm_theory.tex:{source_lines['start']}--{source_lines['end']}",
            "target_locator": f"fredholm_theory-id.tex:{target_lines['start']}--{target_lines['end']}",
            "correction_type": str(item.get("classification", "mechanical")).lower(),
            "decision": item.get("decision", ""),
            "source_normalized_snippet_sha256": item.get("source_normalized_snippet_sha256"),
            "target_normalized_snippet_sha256": item.get("target_normalized_snippet_sha256"),
            "required_target_anchors": item.get("required_target_anchors", []),
            "forbidden_target_anchors": item.get("forbidden_target_anchors", []),
            "affects_math": item.get("affects_math", False), "target_disposition": "corrected",
            "ledger_path": LEDGER_REL, "ledger_sha256": ledger_sha, "qa_state": "passed",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
            "upstream_report": "deferred_until_complete_and_separately_authorized",
            "receipt_document_state": "present" if bind_final else "pending", "receipt_path": RECEIPT_REL,
        }
        if bind_final:
            record.update(qa_receipt_id="QA-CH15-ADMISSION-20260824", receipt_sha256=receipt_sha)
        output.append(record)
    return output


def terminology_records(
    source: str, target: str, prior_records: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    source_terms = [item["argument"] for item in common.macro(source, "df")]
    target_terms = [item["argument"] for item in common.macro(target, "df")]
    if source_terms != EXPECTED_SOURCE_TERMS or target_terms != EXPECTED_TARGET_TERMS:
        raise RuntimeError("Chapter 15 defined-term sequence differs")
    prior_by_id = {item["id"]: item for item in prior_records}
    inherited = set(TERM_OCCURRENCE_IDS) - set(NEW_TERM_SPECS)
    expected_inherited = {"TERM-COKERNEL", "TERM-CODIMENSION"}
    if inherited != expected_inherited:
        raise RuntimeError("Chapter 15 inherited-term plan differs")
    for stable_id in inherited:
        if stable_id not in prior_by_id:
            raise RuntimeError(f"inherited term missing: {stable_id}")
    output = []
    for stable_id, (source_term, preferred, variants, rejected) in NEW_TERM_SPECS.items():
        if stable_id in prior_by_id:
            raise RuntimeError(f"new Chapter 15 stable ID collides with admitted prefix: {stable_id}")
        output.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "term", "id": stable_id,
            "source_term": source_term, "locale": "id-ID", "preferred": preferred,
            "variants": variants, "rejected": rejected,
            "scope": "Fredholm theory, Calkin algebra, index, paths, and homotopy",
            "evidence": f"{CHAPTER_ID} target; {TERM_PLAN_REL}", "introduced_in_unit": CHAPTER_ID,
        })
    if len(output) != 9:
        raise RuntimeError("Chapter 15 new-term closure differs")
    return output, TERM_OCCURRENCE_IDS.copy()


def formula_records(
    source: str, target: str, ledger: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (203, 204):
        raise RuntimeError("Chapter 15 math closure changed")
    ledger_ids = {item["id"] for item in ledger_records(ledger)}
    correction_by_target = {
        0: f"{CHAPTER_ID}-CORR-001", 18: f"{CHAPTER_ID}-CORR-002",
        34: f"{CHAPTER_ID}-CORR-003", 51: f"{CHAPTER_ID}-CORR-005",
    }
    if not set(correction_by_target.values()).issubset(ledger_ids) or f"{CHAPTER_ID}-CORR-004" not in ledger_ids:
        raise RuntimeError("Chapter 15 formula correction IDs differ")
    localized = {3, 8, 13, 15, 20, 25, 30}
    target_to_source: list[list[int]] = []
    for target_index in range(204):
        if target_index in {0, 51}:
            target_to_source.append([])
        elif target_index <= 43:
            target_to_source.append([target_index - 1])
        elif target_index <= 50:
            target_to_source.append([target_index])
        else:
            target_to_source.append([target_index - 1])
    coverage = {index for group in target_to_source for index in group}
    if coverage != set(range(203)) - {43}:
        raise RuntimeError("Chapter 15 target-oriented formula coverage differs")
    records = []
    exact = localized_count = correction_count = insertion_count = 0
    for target_index, source_group in enumerate(target_to_source):
        target_item = target_math[target_index]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{target_index + 1:04d}",
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{index + 1:04d}" for index in source_group],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{target_index + 1:04d}"],
            "source_lines": [[source_math[index]["line_start"], source_math[index]["line_end"]] for index in source_group],
            "target_lines": [[target_item["line_start"], target_item["line_end"]]],
            "source_sha256": [source_math[index]["sha256"] for index in source_group],
            "target_sha256": [target_item["sha256"]],
            "source_delimiters": [source_math[index]["delimiter"] for index in source_group],
            "delimiter": target_item["delimiter"], "ordinal_alignment": "mapped" if source_group else "target_insertion",
        }
        if not source_group:
            record.update(
                alignment="reviewed_source_correction_insertion", sequence_opcode="insert",
                delta_class="classified_source_correction", correction_id=correction_by_target[target_index],
                correction_disposition="corrected", qa_state="passed",
            )
            insertion_count += 1
            correction_count += 1
        else:
            source_index = source_group[0]
            if target_index in correction_by_target:
                record.update(
                    alignment="reviewed_source_correction_replacement", sequence_opcode="replace",
                    delta_class="classified_source_correction", correction_id=correction_by_target[target_index],
                    correction_disposition="corrected", qa_state="passed",
                )
                correction_count += 1
            elif target_index in localized:
                record.update(
                    alignment="translated_internal_prose_preserving_formula_structure",
                    sequence_opcode="replace", delta_class="localized_prose_translation", qa_state="passed",
                )
                localized_count += 1
            elif source_math[source_index]["normalized"] == target_item["normalized"]:
                record["alignment"] = "preserved_exact_after_text_aware_whitespace_normalization"
                exact += 1
            else:
                raise RuntimeError(f"unclassified Chapter 15 formula delta: target {target_index + 1}")
        records.append(record)
    deleted = source_math[43]
    records.append({
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map",
        "id": f"{CHAPTER_ID}-MATHMAP-SOURCE-DELETION-0001",
        "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-0044"], "target_formula_ids": [],
        "source_lines": [[deleted["line_start"], deleted["line_end"]]], "target_lines": [],
        "source_sha256": [deleted["sha256"]], "target_sha256": [],
        "source_delimiters": [deleted["delimiter"]], "delimiter": None,
        "ordinal_alignment": "source_deletion", "alignment": "reviewed_source_correction_deletion",
        "sequence_opcode": "delete", "delta_class": "classified_source_correction",
        "correction_id": f"{CHAPTER_ID}-CORR-004", "correction_disposition": "corrected",
        "qa_state": "passed",
    })
    correction_count += 1
    if (len(records), exact, localized_count, correction_count, insertion_count) != (205, 193, 7, 5, 2):
        raise RuntimeError("Chapter 15 formula classification closure differs")
    return records, {
        "source_math_surfaces": 203, "target_math_surfaces": 204,
        "formula_map_records": 205, "preserved_exact_maps": 193,
        "localized_prose_translation_maps": 7, "classified_source_correction_maps": 5,
        "target_insertions": 2, "source_deletions": 1,
    }


def artifact_records(ids: dict[str, dict[str, Any]], bind_final: bool) -> list[dict[str, Any]]:
    present_specs = [
        ("ARTIFACT-FAOA-ID-CH15-TARGET-TEX", "translation_source", TARGET_REL, "id-ID"),
        ("ARTIFACT-FAOA-ID-THROUGH-CH15-MASTER", "cumulative_TeX_master", MASTER_REL, "id-ID"),
        ("ARTIFACT-FAOA-ID-CH15-SOURCE-INVENTORY", "source_inventory", INVENTORY_REL, None),
        ("ARTIFACT-FAOA-ID-CH15-PRETRANSLATION-REVIEW", "pretranslation_mathematical_review", PRE_REVIEW_REL, None),
        ("ARTIFACT-FAOA-ID-CH15-BILINGUAL-REVIEW", "bilingual_mathematical_review", BILINGUAL_REVIEW_REL, None),
        ("ARTIFACT-FAOA-ID-CH15-TRANSLATION-REPORT", "translation_QA_report", REPORT_REL, None),
        ("ARTIFACT-FAOA-ID-CH15-TERM-PLAN", "terminology_plan", TERM_PLAN_REL, None),
        ("ARTIFACT-FAOA-ID-CH15-CORRECTIONS-LEDGER", "chapter_source_corrections_ledger", LEDGER_REL, None),
        ("ARTIFACT-FAOA-ID-SOURCE-CORRECTIONS-AGGREGATE-CH15", "aggregate_source_corrections_log", "provenance/SOURCE_CORRECTIONS.md", None),
    ]
    final_specs = [
        ("ARTIFACT-FAOA-ID-THROUGH-CH15-PDF", "canonical_cumulative_reader_pdf", PDF_REL),
        ("ARTIFACT-FAOA-ID-CH15-FINAL-BUILD-RESULT", "deterministic_build_result", BUILD_RESULT_REL),
        ("ARTIFACT-FAOA-ID-CH15-RENDER-MANIFEST", "visual_QA_render_manifest", RENDER_MANIFEST_REL),
        ("ARTIFACT-FAOA-ID-CH15-RENDER-AUDIT", "visual_QA_audit", RENDER_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH15-ACCESSIBILITY-AUDIT", "visual_accessibility_audit", ACCESSIBILITY_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH15-QA-RECEIPT", "admission_receipt", RECEIPT_REL),
    ]
    output = []
    for stable_id, kind, relative_path, locale in present_specs:
        info = identity(
            ROOT / relative_path,
            EXPECTED_AGGREGATE_CORRECTIONS if relative_path == "provenance/SOURCE_CORRECTIONS.md" else None,
        )
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "artifact",
            "id": stable_id, "unit_id": CHAPTER_ID, "artifact_kind": kind,
            "path": relative_path, "bytes": info["bytes"], "lines": info["lines"],
            "sha256": info["sha256"], "binding_state": "bound",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if locale:
            record["locale"] = locale
        if kind == "cumulative_TeX_master":
            record["cumulative_through_unit_id"] = CHAPTER_ID
        output.append(record)
    for stable_id, kind, relative_path in final_specs:
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "artifact",
            "id": stable_id, "unit_id": CHAPTER_ID, "artifact_kind": kind, "path": relative_path,
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
                    pages=ids["pdf"]["pages"], page_size="US Letter", pdf_lang="id-ID",
                    publication_state="pending",
                )
            elif kind == "visual_QA_render_manifest":
                record["render_pages"] = ids["pdf"]["pages"]
            elif kind == "admission_receipt":
                record["decision"] = "admitted"
        output.append(record)
    if len(output) != 15:
        raise RuntimeError("Chapter 15 artifact closure differs")
    return output


def qa_records(
    ids: dict[str, dict[str, Any]], formula_summary: dict[str, int], bind_final: bool,
    prefix_lock_sha256: str,
) -> list[dict[str, Any]]:
    base_record = {
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "qa_event",
        "unit_id": CHAPTER_ID, "timestamp": "2026-08-24",
        "responsible_workflow": "Codex", "model_id": MODEL_ID,
    }
    specs = [
        ("QA-CH15-STRUCTURAL-20260824", "unit_structural", REPORT_REL, "pass"),
        ("QA-CH15-MATH-20260824", "unit_mathematical", BILINGUAL_REVIEW_REL, "pass"),
        ("QA-CH15-LANGUAGE-20260824", "unit_language_terminology", TERM_PLAN_REL, "pass"),
        ("QA-CH15-EXERCISE-SUPPORT-20260824", "exercise_support_provenance", INVENTORY_REL, "pass"),
        ("QA-CH15-RIGHTS-20260824", "unit_rights_privacy", RECEIPT_REL, "pass" if bind_final else "pending"),
        ("QA-CH15-BUILD-20260824", "cumulative_build", BUILD_RESULT_REL, "pass" if bind_final else "pending"),
        ("QA-CH15-VISUAL-20260824", "cumulative_visual", RENDER_AUDIT_REL, "pass" if bind_final else "pending"),
        ("QA-CH15-ACCESSIBILITY-20260824", "cumulative_accessibility", ACCESSIBILITY_AUDIT_REL, "pass" if bind_final else "pending"),
        ("QA-CH15-BACKEND-20260824", "backend_reconciliation", PREFIX_LOCK_REL, "pass"),
        ("QA-CH15-ADMISSION-20260824", "unit_admission", RECEIPT_REL, "pass" if bind_final else "pending"),
    ]
    output = []
    for stable_id, kind, witness, result in specs:
        record = base_record | {
            "id": stable_id, "qa_type": kind, "result": result, "witness": witness,
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if stable_id == "QA-CH15-BACKEND-20260824":
            record["witness_sha256"] = prefix_lock_sha256
        elif result == "pass" and (ROOT / witness).is_file():
            record["witness_sha256"] = sha((ROOT / witness).read_bytes())
        else:
            record["witness_state"] = "pending_final_artifact_binding"
        output.append(record)
    output[0].update(
        sections=4, environment_begins=60, semantic_environment_begins=50,
        labels=33, references=27, citations=17, index_terms=46, defined_terms=11,
        manual_equation_tags=12, examples=8, exercise_environments=0,
        proof_environments=13, proof_hints=2, citation_only_proofs=8,
    )
    output[1].update(formula_summary | {"unexplained_deltas": 0, "extractor": "backend/ch03_math.py"})
    output[2].update(
        severity_counts={"P1": 0, "P2": 0, "P3": 0}, unintended_english_prose=0,
        placeholders=0, defined_term_occurrences=11, new_controlled_terms=9,
    )
    output[3].update(
        source_exercises=0, upstream_exercise_hints=0, upstream_proof_hints=2,
        upstream_answers=0, upstream_solutions=0, exercise_support_records=0,
        provenance="no_formal_exercise_surface_upstream",
    )
    output[4].update(
        rights_id=RIGHTS,
        attribution_change_notice_sharealike_nonendorsement="present",
        credential_or_token_residue=0,
    )
    if bind_final:
        output[5].update(
            master_artifact_id="ARTIFACT-FAOA-ID-THROUGH-CH15-MASTER",
            pdf_artifact_id="ARTIFACT-FAOA-ID-THROUGH-CH15-PDF", pages=ids["pdf"]["pages"],
            deterministic_replays=2, byte_identical=True,
        )
        output[6].update(
            pages_rendered=ids["pdf"]["pages"], pages_inspected=ids["pdf"]["pages"],
            visual_defects=0,
        )
        output[7].update(
            tagged_pdf=False, fully_accessible_pdf_claim=False,
            semantic_accessibility_state="remediation_required",
            accessible_html_or_tagged_pdf_state="pending",
            admission_blocker_for_chapter_boundary=False,
        )
        output[9].update(
            decision="admitted", source_sha256=ids["source"]["sha256"],
            target_sha256=ids["target"]["sha256"], build_master_sha256=ids["master"]["sha256"],
            artifact_sha256=ids["pdf"]["sha256"], correction_ledger_sha256=ids["ledger"]["sha256"],
            receipt_sha256=ids["receipt"]["sha256"], all_required_admission_gates="pass",
            publication_state="pending",
        )
    return output


def build_outputs(bind_final: bool) -> tuple[dict[str, bytes], dict[str, Any]]:
    records, index_fields, index_rows, lock_bytes, _ = stripped_prefix()
    ids, ledger = evidence(bind_final)
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    semantic, segments, relations, source_anchors, _ = base.build_units_and_segments(source, target)
    kinds = collections.Counter(record["unit_kind"] for record in semantic)
    expected_kinds = collections.Counter({
        "section": 4, "prop": 16, "proof": 13, "exam": 8, "defn": 6,
        "lem": 3, "cor": 2, "thm": 1, "notn": 1,
    })
    if len(semantic) != 54 or kinds != expected_kinds or len(segments) != 68 or len(relations) != 189:
        raise RuntimeError(f"Chapter 15 semantic closure differs: {len(semantic)}/{kinds}/{len(segments)}/{len(relations)}")
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
    if len(source_anchors) != 55 or (section_number, node_number) != (4, 50):
        raise RuntimeError("Chapter 15 anchor closure differs")
    for anchor, stable_id in zip(source_anchors, anchor_ids, strict=True):
        if anchor["anchor_type"] != "chapter":
            semantic_offsets.append((anchor["start"], anchor["end"], stable_id))

    prior_labels = {
        item.get("source_local_id"): item["id"]
        for item in records["semantic_units.jsonl"] if item.get("source_local_id")
    }
    local_labels: dict[str, str] = {}
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 33 or [item["argument"] for item in source_labels] != [item["argument"] for item in target_labels]:
        raise RuntimeError("Chapter 15 label sequence differs")
    for number, occurrence in enumerate(source_labels, 1):
        candidates = [
            (end - start, stable_id)
            for start, end, stable_id in semantic_offsets if start <= occurrence["start"] < end
        ]
        owner = min(candidates)[1] if candidates else CHAPTER_ID
        local_labels[occurrence["argument"]] = owner
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-LABEL-{number:04d}", "relation_type": "declares_label",
            "from_id": base.ch01.containing_segment(segments, occurrence["start"], "source"),
            "to_id": owner, "source_local_id": occurrence["argument"],
            "label_id": f"ERDMAN-FAOA-2015-LABEL-{occurrence['argument']}",
        })

    source_refs = common.reference_sequence(source)
    target_refs = common.reference_sequence(target)
    if len(source_refs) != 27 or len(target_refs) != 27:
        raise RuntimeError("Chapter 15 reference count differs")
    if [(kind, label) for _, kind, label in source_refs] != [(kind, label) for _, kind, label in target_refs]:
        raise RuntimeError("Chapter 15 reference sequence differs")
    resolution_counts: collections.Counter[str] = collections.Counter()
    for number, (source_ref, target_ref) in enumerate(zip(source_refs, target_refs, strict=True), 1):
        source_position, source_kind, source_label = source_ref
        _, target_kind, target_label = target_ref
        if target_label in local_labels:
            endpoint, resolution = local_labels[target_label], "local"
        elif target_label in prior_labels:
            endpoint, resolution = prior_labels[target_label], "admitted_prior_unit"
        elif target_label in EXTERNAL_PRIOR_LABELS:
            endpoint = f"ERDMAN-FAOA-2015-LABEL-{target_label}"
            resolution = "admitted_prior_unit"
        else:
            raise RuntimeError(f"unresolved Chapter 15 reference: {source_label!r} -> {target_label!r}")
        resolution_counts[resolution] += 1
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}", "relation_type": "xref",
            "from_id": base.ch01.containing_segment(segments, source_position, "source"),
            "to_id": endpoint, "source_local_id": source_label, "target_local_id": target_label,
            "resolution": resolution, "source_surface": source_kind, "target_surface": target_kind,
        })
    if resolution_counts != collections.Counter({"local": 24, "admitted_prior_unit": 3}):
        raise RuntimeError(f"Chapter 15 reference-resolution closure differs: {resolution_counts}")

    source_citations = common.macro(source, "cite")
    target_citations = common.macro(target, "cite")
    if len(source_citations) != 17 or [item["argument"] for item in source_citations] != [item["argument"] for item in target_citations]:
        raise RuntimeError("Chapter 15 citation sequence differs")
    for number, occurrence in enumerate(source_citations, 1):
        key = occurrence["argument"]
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-CITE-{number:04d}", "relation_type": "cites",
            "from_id": base.ch01.containing_segment(segments, occurrence["start"], "source"),
            "to_id": f"ERDMAN-FAOA-BIB-{key}", "source_local_id": key,
        })

    terms, term_mapping = terminology_records(source, target, records["terminology.jsonl"])
    source_terms = common.macro(source, "df")
    target_terms = common.macro(target, "df")
    for number, (source_term, target_term, term_id) in enumerate(
        zip(source_terms, target_terms, term_mapping, strict=True), 1
    ):
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}", "relation_type": "uses_term",
            "from_id": base.ch01.containing_segment(segments, source_term["start"], "source"),
            "to_id": term_id, "source_term_tex": source_term["argument"],
            "target_term_tex": target_term["argument"], "locale": "id-ID",
        })

    source_indexes = common.macro(source, "index")
    target_indexes = common.macro(target, "index")
    if len(source_indexes) != 46 or len(target_indexes) != 46:
        raise RuntimeError("Chapter 15 index count differs")
    new_index_rows = []
    for number, (source_index, target_index) in enumerate(zip(source_indexes, target_indexes, strict=True), 1):
        new_index_rows.append({
            "id": f"{CHAPTER_ID}-TERM-OCC-{number:04d}",
            "parent_segment_id": base.ch01.containing_segment(segments, source_index["start"], "source"),
            "source_order": str(number), "source_line": str(source_index["line"]),
            "source_index_tex": source_index["argument"], "target_line": str(target_index["line"]),
            "target_index_tex": target_index["argument"],
            "source_sha256": sha(source_index["argument"].encode("ascii")),
            "target_sha256": sha(target_index["argument"].encode("utf-8")), "locale": "id-ID",
        })

    receipt_sha = ids.get("receipt", {}).get("sha256")
    corrections = correction_records(ledger, ids["ledger"]["sha256"], bind_final, receipt_sha)
    formulas, formula_summary = formula_records(source, target, ledger)
    artifacts = artifact_records(ids, bind_final)
    qa = qa_records(ids, formula_summary, bind_final, sha(lock_bytes))

    common_relation = {
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "from_id": CHAPTER_ID,
    }
    relations.append(common_relation | {
        "id": f"{CHAPTER_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS,
    })
    for number, artifact in enumerate(artifacts, 1):
        relations.append(common_relation | {
            "id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}", "relation_type": "has_artifact",
            "to_id": artifact["id"],
        })
    for number, event in enumerate(qa, 1):
        relations.append(common_relation | {
            "id": f"{CHAPTER_ID}-REL-QA-{number:04d}", "relation_type": "has_qa_event",
            "to_id": event["id"],
        })
    for number, correction in enumerate(corrections, 1):
        relations.append(common_relation | {
            "id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}",
            "relation_type": "documents_correction", "to_id": correction["id"],
        })
    if len(relations) != 312:
        raise RuntimeError(f"Chapter 15 relation closure differs: {len(relations)}")

    for segment in segments:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            segment.pop(key, None)
    records["semantic_units.jsonl"].extend(semantic)
    records["segments.jsonl"].extend(segments)
    records["relations.jsonl"].extend(relations)
    records["formula_map.jsonl"].extend(formulas)
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
    outputs["CH15_PREFIX_LOCKS.json"] = lock_bytes
    outputs["BACKEND_MANIFEST.csv"] = base.manifest_bytes(outputs)
    summary = {
        "unit": CHAPTER_ID, "binding_state": "bound" if bind_final else "pending_final_artifact_binding",
        "semantic_units": len(semantic), "segments": len(segments), "relations": len(relations),
        "formula_maps": len(formulas), "index_rows": len(new_index_rows), "new_terms": len(terms),
        "corrections": len(corrections), "exercise_support": 0,
        "qa_events": len(qa), "artifacts": len(artifacts),
        "reference_resolution": dict(resolution_counts), "target_sha256": ids["target"]["sha256"],
        "model_id": MODEL_ID,
    }
    return outputs, summary


def reconciliation_report(summary: dict[str, Any], outputs: dict[str, bytes]) -> bytes:
    names = [
        "units.jsonl", "semantic_units.jsonl", "segments.jsonl", "relations.jsonl",
        "formula_map.jsonl", "exercise_support.jsonl", "index_terms.csv", "artifacts.jsonl",
        "qa_events.jsonl", "corrections.jsonl", "terminology.jsonl", "CH15_PREFIX_LOCKS.json",
        "BACKEND_MANIFEST.csv",
    ]
    lines = [
        "# FAOA-2015-CH15 backend reconciliation", "",
        "Generated from the passing Chapter 15 translation, mathematical, build, render, accessibility, and admission evidence.", "",
        f"- Target: `{TARGET_REL}` — {EXPECTED_TARGET[0]} bytes, SHA-256 `{EXPECTED_TARGET[2]}`.",
        f"- Semantic units: {summary['semantic_units']}; segments: {summary['segments']}; relations: {summary['relations']}; formula maps: {summary['formula_maps']}; index rows: {summary['index_rows']}.",
        f"- New terminology records: {summary['new_terms']}; correction records: {summary['corrections']}; exercise-support records: {summary['exercise_support']}; QA events: {summary['qa_events']}; artifacts: {summary['artifacts']}.",
        "- The complete admitted Chapter 1--14 prefix is locked in `backend/CH15_PREFIX_LOCKS.json`.",
        "- Formula closure explicitly represents two target insertions and one source-only deletion; no source formula is hidden or lost.",
        "- Relation endpoint, stable-ID, formula, index, manifest, and deterministic round-trip validation is performed by `backend/validate_ch15_backend.py`.",
        f"- Model provenance: `{MODEL_ID}`.", "", "Generated backend file identities:", "",
    ]
    lines.extend(f"- `{name}` — {len(outputs[name])} bytes, SHA-256 `{sha(outputs[name])}`" for name in names)
    return ("\n".join(lines) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true", help="verify frozen inputs and prefix without writing")
    parser.add_argument("--bind-final-artifacts", action="store_true", help="write/replay the admitted bound slice")
    parser.add_argument("--check", action="store_true", help="compare generated bytes without writing")
    args = parser.parse_args()
    if args.preflight or (not args.bind_final_artifacts and not args.check):
        if args.preflight and (args.bind_final_artifacts or args.check):
            parser.error("--preflight cannot be combined with generation modes")
        print(json.dumps(preflight(), ensure_ascii=False, sort_keys=True))
        return
    outputs, summary = build_outputs(args.bind_final_artifacts)
    if args.check:
        mismatches = [
            name for name, expected in outputs.items()
            if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != expected
        ]
        if mismatches:
            raise RuntimeError("deterministic backend replay differs: " + ", ".join(mismatches))
        print(json.dumps(summary | {"deterministic_replay": "pass"}, sort_keys=True))
        return
    if not args.bind_final_artifacts:
        parser.error("aggregate writes require --bind-final-artifacts")
    for name, data in outputs.items():
        (BACKEND / name).write_bytes(data)
    report = reconciliation_report(summary, outputs)
    (ROOT / "qa/CH15_BACKEND_RECONCILIATION.md").write_bytes(report)
    print(json.dumps(summary | {"backend_report": "qa/CH15_BACKEND_RECONCILIATION.md"}, sort_keys=True))


if __name__ == "__main__":
    main()
