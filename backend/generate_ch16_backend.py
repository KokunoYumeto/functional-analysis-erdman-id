#!/usr/bin/env python3
"""Deterministically append the FAOA-2015-CH16 locale-neutral backend slice."""

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
import generate_ch15_backend as prior  # noqa: E402


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
CHAPTER_ID = "FAOA-2015-CH16"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_REL = "source/upstream/extensions.tex"
TARGET_REL = "source/id-ID/extensions-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-through-ch16.tex"
INVENTORY_REL = "qa/CH16_SOURCE_INVENTORY.md"
PRE_REVIEW_REL = "qa/CH16_PRETRANSLATION_MATH_REVIEW.md"
REPORT_REL = "qa/ch16-translation-report.json"
BILINGUAL_REVIEW_REL = "qa/CH16_BILINGUAL_MATH_REVIEW.md"
LEDGER_REL = "provenance/SOURCE_CORRECTIONS_CH16.json"
TERM_PLAN_REL = "provenance/CH16_TERMINOLOGY_PLAN.md"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-16.pdf"
RECEIPT_REL = "provenance/CH16_BUILD_AND_QA_RECEIPT.md"
BUILD_RESULT_REL = "qa/CH16_FINAL_BUILD_RESULT.json"
RENDER_MANIFEST_REL = "provenance/CH16_RENDER_MANIFEST.csv"
RENDER_AUDIT_REL = "qa/CH16_RENDER_AUDIT.json"
ACCESSIBILITY_AUDIT_REL = "qa/CH16_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
PREFIX_LOCK_REL = "backend/CH16_PREFIX_LOCKS.json"

SOURCE_PATH = ROOT / SOURCE_REL
TARGET_PATH = ROOT / TARGET_REL

# (bytes, logical records, SHA-256)
EXPECTED_SOURCE = (42_614, 1_000, "e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318")
EXPECTED_TARGET = (43_804, 1_000, "59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3")
EXPECTED_MASTER = (10_679, 345, "6e528b0193d3179b58e44169430d043fa5399f7c860f09d832eb3ccd954a5388")
EXPECTED_INVENTORY = (9_031, 186, "899c11dce4eacaf5639512bbb02e649c2fa8ebab336a3d8d34bc4d058e9d9298")
EXPECTED_PRE_REVIEW = (12_712, 222, "baeb6f5e68454df1f7b8a9511b608ed3469c2c358fea8f366f2eb267132d9d12")
EXPECTED_TERM_PLAN = (12_546, 215, "b1dcdefa587d9c9e9aeafc3d680d2facbb89dea43939f517a11c99e191bf879c")

JSONL_FILES = prior.JSONL_FILES
INITIAL_LOCKS = {
    "units.jsonl": (22_549, "b7f984ad75e28b3d4c563b5929d803b0b3952658e42b561b0a615e4a284840c5"),
    "semantic_units.jsonl": (1_323_512, "1044b2d70b41aae1290fd064b600e049a998033a86de9858faaae1aac0423782"),
    "segments.jsonl": (1_483_800, "53451742eb0ae64749b86a7b5f529803770408896e6594c8390fb02222973924"),
    "relations.jsonl": (1_900_009, "04402b64cae7fb1b26980f1f624ac95a5e331912515bede002b7f39cbab803f2"),
    "formula_map.jsonl": (6_229_001, "04b153c5fc15cc2236fab9a7e08fb63d88bf6317b42bbc008e3dc7473b0d2bfd"),
    "exercise_support.jsonl": (27_135, "da1bd2f951ec0982cefce076ea5bd64a69c14613102ce1d7e17ed056a1763ffc"),
    "index_terms.csv": (472_386, "fde06aab509094efd2f56f689f05e197b85f4006d9abed238d2f53bea595f327"),
    "artifacts.jsonl": (85_990, "f1b3f149ac57e017055524363e69503ce5382ec1b8984ded7d2145a086c3dbfa"),
    "qa_events.jsonl": (107_228, "2c3cf1a3f97467a9e7f02bd9dc2499ae03b07010f2f4fc2c2d67236f1ad3e900"),
    "corrections.jsonl": (216_589, "367cf49965493e78cf39a781d7234002d731ef64ec3a6cafa8ef4b2901e2285c"),
    "terminology.jsonl": (155_122, "377cf36d4f8b11b7a81682e8881ed658ced82bb99ff11dfbc0d1b78d48ebcb35"),
}

QUEUED_CH16 = {
    "schema": SCHEMA, "schema_version": VERSION, "record_type": "unit",
    "id": CHAPTER_ID, "edition_id": EDITION, "order": 16,
    "source_path": "extensions.tex", "source_bytes": EXPECTED_SOURCE[0],
    "source_lines": EXPECTED_SOURCE[1], "source_sha256": EXPECTED_SOURCE[2],
    "source_title": "EXTENSIONS", "course_role": "advanced_continuation",
    "translation_state": "queued", "rights_id": RIGHTS,
}

SOURCE_TERMS = [
    "essential spectrum", "essentially unitarily equivalent", "compalent", "unitary",
    "unitarily equivalent", "essentially normal", "essentially self-adjoint",
    "Toeplitz operator", "symbol", "Toeplitz matrix", "Toeplitz algebra",
    "Toeplitz extension", "winding number", "extension of $\\ofml K = \\ofml K(H)$ by $A$",
    "equivalent", "conjugation", "extension of $\\ofml K(H)$ determined by~$T$",
    "pullback of $A_1$ and $A_2$ along $\\phi_1$ and $\\phi_2$", "unitarily equivalent",
    "abstract Toeplitz operator", "with symbol $a$ associated with",
    "abstract Toeplitz extension $\\tau_P$ associated with the pair $(\\mathbf r,P)$",
    "semisplit", "positive", "standard matrix units", "$n$-positive",
    "completely positive", "completely bounded", "nuclear",
]
TARGET_TERMS = [
    "spektrum esensial", "ekuivalen uniter secara esensial", "kompalen", "uniter",
    "ekuivalen secara uniter", "normal secara esensial", "swaadjoin secara esensial",
    "operator Toeplitz", "simbol", "matriks Toeplitz", "aljabar Toeplitz",
    "ekstensi Toeplitz", "bilangan lilit", "ekstensi $\\ofml K = \\ofml K(H)$ oleh $A$",
    "ekuivalen", "konjugasi", "ekstensi $\\ofml K(H)$ yang ditentukan oleh~$T$",
    "tarik balik $A_1$ dan $A_2$ sepanjang $\\phi_1$ dan $\\phi_2$", "ekuivalen secara uniter",
    "operator Toeplitz abstrak", "bersimbol $a$ yang dikaitkan dengan",
    "ekstensi Toeplitz abstrak $\\tau_P$ yang dikaitkan dengan pasangan $(\\mathbf r,P)$",
    "semiterbelah", "positif", "unit matriks standar", "$n$-positif",
    "positif lengkap", "terbatas lengkap", "nuklir",
]

TERM_MAPPING = [
    "TERM-ESSENTIAL-SPECTRUM", "TERM-ESSENTIAL-UNITARY-EQUIVALENCE", "TERM-COMPALENT",
    "TERM-UNITARY", "TERM-UNITARILY-EQUIVALENT", "TERM-ESSENTIALLY-NORMAL",
    "TERM-ESSENTIALLY-SELF-ADJOINT", "TERM-TOEPLITZ-OPERATOR", "TERM-TOEPLITZ-SYMBOL",
    "TERM-TOEPLITZ-MATRIX", "TERM-TOEPLITZ-ALGEBRA", "TERM-TOEPLITZ-EXTENSION",
    "TERM-WINDING-NUMBER", "TERM-ALGEBRA-EXTENSION", "TERM-EQUIVALENT-EXTENSIONS",
    "TERM-CONJUGATION", "TERM-ALGEBRA-EXTENSION", "TERM-PULLBACK",
    "TERM-UNITARILY-EQUIVALENT", "TERM-ABSTRACT-TOEPLITZ-OPERATOR", "TERM-TOEPLITZ-SYMBOL",
    "TERM-ABSTRACT-TOEPLITZ-EXTENSION", "TERM-SEMISPLIT", "TERM-POSITIVE",
    "TERM-STANDARD-MATRIX-UNITS", "TERM-N-POSITIVE", "TERM-COMPLETELY-POSITIVE",
    "TERM-COMPLETELY-BOUNDED", "TERM-NUCLEAR",
]

NEW_TERM_SPECS = {
    "TERM-ESSENTIAL-SPECTRUM": ("essential spectrum", "spektrum esensial", [], []),
    "TERM-ESSENTIAL-UNITARY-EQUIVALENCE": ("essentially unitarily equivalent", "ekuivalen uniter secara esensial", ["ekuivalensi uniter esensial"], []),
    "TERM-COMPALENT": ("compalent", "kompalen", [], []),
    "TERM-ESSENTIALLY-NORMAL": ("essentially normal", "normal secara esensial", [], []),
    "TERM-ESSENTIALLY-SELF-ADJOINT": ("essentially self-adjoint", "swaadjoin secara esensial", [], []),
    "TERM-TOEPLITZ-OPERATOR": ("Toeplitz operator", "operator Toeplitz", [], []),
    "TERM-TOEPLITZ-SYMBOL": ("symbol", "simbol", [], []),
    "TERM-TOEPLITZ-MATRIX": ("Toeplitz matrix", "matriks Toeplitz", [], []),
    "TERM-TOEPLITZ-ALGEBRA": ("Toeplitz algebra", "aljabar Toeplitz", [], []),
    "TERM-TOEPLITZ-EXTENSION": ("Toeplitz extension", "ekstensi Toeplitz", [], []),
    "TERM-WINDING-NUMBER": ("winding number", "bilangan lilit", ["bilangan belitan"], []),
    "TERM-EQUIVALENT-EXTENSIONS": ("equivalent extensions", "ekstensi yang ekuivalen", ["ekuivalensi ekstensi"], []),
    "TERM-PULLBACK": ("pullback", "tarik balik", [], []),
    "TERM-ABSTRACT-TOEPLITZ-OPERATOR": ("abstract Toeplitz operator", "operator Toeplitz abstrak", [], []),
    "TERM-ABSTRACT-TOEPLITZ-EXTENSION": ("abstract Toeplitz extension", "ekstensi Toeplitz abstrak", [], []),
    "TERM-SEMISPLIT": ("semisplit", "semiterbelah", [], []),
    "TERM-STANDARD-MATRIX-UNITS": ("standard matrix units", "unit matriks standar", [], []),
    "TERM-N-POSITIVE": ("n-positive", "n-positif", [], []),
    "TERM-COMPLETELY-POSITIVE": ("completely positive", "positif lengkap", ["pemetaan positif lengkap"], ["sepenuhnya positif"]),
    "TERM-COMPLETELY-BOUNDED": ("completely bounded", "terbatas lengkap", [], []),
    "TERM-NUCLEAR": ("nuclear", "nuklir", [], []),
}


def identity(path: Path, expected: tuple[int, int | None, str] | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    result = {
        "path": path.relative_to(ROOT).as_posix(), "bytes": len(data),
        "lines": len(data.splitlines()), "sha256": sha(data),
    }
    if expected and (
        result["bytes"] != expected[0] or result["sha256"] != expected[2]
        or (expected[1] is not None and result["lines"] != expected[1])
    ):
        raise RuntimeError(f"identity mismatch: {result}")
    return result


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


def strip_ch16(records: dict[str, list[dict[str, Any]]], index_rows: list[dict[str, str]]) -> None:
    for name, values in records.items():
        if name == "units.jsonl":
            values[:] = [QUEUED_CH16.copy() if item.get("id") == CHAPTER_ID else item for item in values]
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
    records: dict[str, list[dict[str, Any]]], fields: list[str], index_rows: list[dict[str, str]],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    payload = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    payload["index_terms.csv"] = csv_bytes(fields, index_rows)
    locks = {
        "schema_version": "o008.ch16-prefix-locks.v1", "unit_id": CHAPTER_ID,
        "scope": "complete admitted Chapters 1--15 backend; excludes every Chapter 16-derived record",
        "files": {
            name: {
                "bytes": len(data), "sha256": sha(data),
                "records": len(records[name]) if name in records else len(index_rows),
            }
            for name, data in payload.items()
        },
    }
    return payload, locks


def stripped_prefix() -> tuple[dict[str, list[dict[str, Any]]], list[str], list[dict[str, str]], bytes, bool]:
    configure_base()
    was_initial = initial_state()
    records, fields, index_rows = load_data()
    strip_ch16(records, index_rows)
    base.assert_unit_order(records["units.jsonl"])
    _, locks = prefix_payload(records, fields, index_rows)
    lock_bytes = (json.dumps(locks, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    lock_path = ROOT / PREFIX_LOCK_REL
    if not was_initial and (not lock_path.is_file() or lock_path.read_bytes() != lock_bytes):
        raise RuntimeError("backend is neither exact Chapter 15 state nor locked Chapter 16 state")
    return records, fields, index_rows, lock_bytes, was_initial


def ledger_records() -> tuple[list[dict[str, Any]], str]:
    path = ROOT / LEDGER_REL
    if not path.is_file():
        raise RuntimeError("Chapter 16 correction ledger is not yet present")
    document = json.loads(path.read_text(encoding="utf-8"))
    values = document.get("records")
    if not isinstance(values, list):
        values = document.get("corrections")
    expected = [f"{CHAPTER_ID}-CORR-{number:03d}" for number in range(1, 16)]
    if not isinstance(values, list) or len(values) != 15 or [item.get("id") for item in values] != expected:
        raise RuntimeError("Chapter 16 correction IDs/order differ")
    target_hashes = {
        document.get("target_sha256"), document.get("identities", {}).get("target_sha256"),
        document.get("target", {}).get("sha256"),
        document.get("identities", {}).get("target", {}).get("sha256"),
    }
    if EXPECTED_TARGET[2] not in target_hashes:
        raise RuntimeError("Chapter 16 correction ledger is not bound to the final target")
    return values, sha(path.read_bytes())


def core_evidence() -> dict[str, dict[str, Any]]:
    return {
        "source": identity(SOURCE_PATH, EXPECTED_SOURCE),
        "target": identity(TARGET_PATH, EXPECTED_TARGET),
        "master": identity(ROOT / MASTER_REL, EXPECTED_MASTER),
        "inventory": identity(ROOT / INVENTORY_REL, EXPECTED_INVENTORY),
        "pre_review": identity(ROOT / PRE_REVIEW_REL, EXPECTED_PRE_REVIEW),
        "term_plan": identity(ROOT / TERM_PLAN_REL, EXPECTED_TERM_PLAN),
        "ledger": identity(ROOT / LEDGER_REL),
    }


def final_available() -> bool:
    return all((ROOT / path).is_file() for path in (
        REPORT_REL, BILINGUAL_REVIEW_REL, PDF_REL, RECEIPT_REL, BUILD_RESULT_REL,
        RENDER_MANIFEST_REL, RENDER_AUDIT_REL, ACCESSIBILITY_AUDIT_REL,
    ))


def final_evidence(ids: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    for key, path in (
        ("report", REPORT_REL), ("bilingual_review", BILINGUAL_REVIEW_REL), ("pdf", PDF_REL),
        ("receipt", RECEIPT_REL), ("build_result", BUILD_RESULT_REL),
        ("render_manifest", RENDER_MANIFEST_REL), ("render_audit", RENDER_AUDIT_REL),
        ("accessibility", ACCESSIBILITY_AUDIT_REL),
    ):
        ids[key] = identity(ROOT / path)
    ids["pdf"]["pages"] = page_count(ROOT / PDF_REL)
    receipt = (ROOT / RECEIPT_REL).read_text(encoding="utf-8")
    if CHAPTER_ID not in receipt or not re.search(r"\badmitted\b", receipt, re.I):
        raise RuntimeError("Chapter 16 receipt does not assert admission")
    return ids


def preflight() -> dict[str, Any]:
    _, _, _, lock_bytes, was_initial = stripped_prefix()
    ids = core_evidence()
    ledger, _ = ledger_records()
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    checks = {
        "source_records": len(source.splitlines()), "target_records": len(target.splitlines()),
        "sections": len(common.macro(source, "section")), "labels": len(common.macro(source, "label")),
        "references": len(common.reference_sequence(source)), "citations": len(common.macro(source, "cite")),
        "index_terms": len(common.macro(source, "index")), "defined_terms": len(common.macro(source, "df")),
        "source_math_surfaces": len(ch03_math.extract_math(source, "ascii")),
        "target_math_surfaces": len(ch03_math.extract_math(target, "utf-8")),
        "corrections": len(ledger),
    }
    expected = {
        "source_records": 1000, "target_records": 1000, "sections": 4, "labels": 36,
        "references": 28, "citations": 59, "index_terms": 107, "defined_terms": 29,
        "source_math_surfaces": 702, "target_math_surfaces": 700, "corrections": 15,
    }
    if checks != expected:
        raise RuntimeError(f"Chapter 16 preflight closure differs: {checks}")
    return {
        "status": "pass", "unit_id": CHAPTER_ID,
        "backend_prefix_state": "exact_chapter15" if was_initial else "stripped_locked_chapter16",
        "prefix_lock_sha256": sha(lock_bytes), "identities": ids,
        "structural_closure": checks, "final_artifacts_available": final_available(),
        "writes_performed": False,
    }


def terminology_records(source: str, target: str, prior_terms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if [x["argument"] for x in common.macro(source, "df")] != SOURCE_TERMS:
        raise RuntimeError("Chapter 16 source defined-term sequence differs")
    if [x["argument"] for x in common.macro(target, "df")] != TARGET_TERMS:
        raise RuntimeError("Chapter 16 target defined-term sequence differs")
    prior_ids = {item["id"] for item in prior_terms}
    inherited = set(TERM_MAPPING) - set(NEW_TERM_SPECS)
    if not inherited.issubset(prior_ids) or set(NEW_TERM_SPECS) & prior_ids:
        raise RuntimeError("Chapter 16 inherited/new terminology boundary differs")
    output = []
    for stable_id, (source_term, preferred, variants, rejected) in NEW_TERM_SPECS.items():
        output.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "term", "id": stable_id,
            "source_term": source_term, "locale": "id-ID", "preferred": preferred,
            "variants": variants, "rejected": rejected,
            "scope": "extensions, Toeplitz operators, and completely positive maps",
            "evidence": f"{CHAPTER_ID} target; {TERM_PLAN_REL}", "introduced_in_unit": CHAPTER_ID,
        })
    return output


def correction_records(items: list[dict[str, Any]], ledger_sha: str, bound: bool) -> list[dict[str, Any]]:
    output = []
    for item in items:
        source_lines = item.get("source_lines", {})
        target_lines = item.get("target_lines", {})
        def locator(value: Any, path: str) -> str:
            if isinstance(value, dict):
                start, end = value.get("start"), value.get("end")
            elif isinstance(value, list) and value:
                start, end = value[0], value[-1]
            else:
                start = end = value
            return f"{path}:{start}--{end}"
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "correction",
            "id": item["id"], "unit_id": CHAPTER_ID,
            "source_locator": locator(source_lines, "extensions.tex"),
            "target_locator": locator(target_lines, "extensions-id.tex"),
            "correction_type": str(item.get("classification", item.get("type", "source_correction"))).lower(),
            "decision": item.get("decision", item.get("rationale", "")),
            "affects_math": bool(item.get("affects_math", False)), "target_disposition": "corrected",
            "ledger_path": LEDGER_REL, "ledger_sha256": ledger_sha, "qa_state": "passed",
            "admission_state": "admitted" if bound else "pending_final_artifact_binding",
            "upstream_report": "deferred_until_complete_and_separately_authorized",
            "receipt_document_state": "present" if bound else "pending", "receipt_path": RECEIPT_REL,
        }
        for key in (
            "source_normalized_snippet_sha256", "target_normalized_snippet_sha256",
            "required_target_anchors", "forbidden_target_anchors",
        ):
            if key in item:
                record[key] = item[key]
        output.append(record)
    return output


def formula_records(source: str, target: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (702, 700):
        raise RuntimeError("Chapter 16 math closure changed")

    # Default ordinal alignment is one-to-one up to the two count-changing regions.
    target_to_source: list[list[int]] = []
    for target_index in range(700):
        ordinal = target_index + 1
        if ordinal <= 365:
            source_group = [target_index]
        elif ordinal == 366:
            source_group = [366, 367]  # tau_1,tau_2 -> j=1,2
        elif ordinal == 367:
            source_group = [368, 369]  # A,Q(H) -> one map surface
        elif ordinal == 368:
            source_group = [365]       # relocated *\, marker for the rewritten declaration
        elif ordinal in (369, 370):
            source_group = [target_index + 2]
        elif ordinal == 371:
            source_group = []          # restored missing operator name U
        elif ordinal <= 658:
            source_group = [target_index + 1]
        else:
            source_group = [target_index + 2]  # source ordinal 660 is deleted
        target_to_source.append(source_group)
    coverage = [index for group in target_to_source for index in group]
    if len(coverage) != 701 or len(set(coverage)) != 701 or set(coverage) != set(range(702)) - {659}:
        raise RuntimeError("Chapter 16 formula source coverage differs")

    correction_by_target = {
        30: f"{CHAPTER_ID}-CORR-002", 38: f"{CHAPTER_ID}-CORR-002",
        150: f"{CHAPTER_ID}-CORR-004", 180: f"{CHAPTER_ID}-CORR-006",
        199: f"{CHAPTER_ID}-CORR-008", 201: f"{CHAPTER_ID}-CORR-008",
        245: f"{CHAPTER_ID}-CORR-010", 354: f"{CHAPTER_ID}-CORR-011",
        366: f"{CHAPTER_ID}-CORR-012", 367: f"{CHAPTER_ID}-CORR-012",
        368: f"{CHAPTER_ID}-CORR-012",
        371: f"{CHAPTER_ID}-CORR-012",
    }
    localized = {142, 542, 543}
    semantic_normalization = {75}
    records = []
    counters = collections.Counter()
    for target_index, source_group in enumerate(target_to_source):
        ordinal = target_index + 1
        target_item = target_math[target_index]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{ordinal:04d}",
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{i + 1:04d}" for i in source_group],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{ordinal:04d}"],
            "source_lines": [[source_math[i]["line_start"], source_math[i]["line_end"]] for i in source_group],
            "target_lines": [[target_item["line_start"], target_item["line_end"]]],
            "source_sha256": [source_math[i]["sha256"] for i in source_group],
            "target_sha256": [target_item["sha256"]],
            "source_delimiters": [source_math[i]["delimiter"] for i in source_group],
            "delimiter": target_item["delimiter"],
            "ordinal_alignment": "mapped" if source_group else "target_insertion",
        }
        correction_id = correction_by_target.get(ordinal)
        if correction_id:
            record.update(
                alignment="reviewed_source_correction_insertion" if not source_group else "reviewed_source_correction_replacement",
                sequence_opcode="insert" if not source_group else "replace",
                delta_class="classified_source_correction", correction_id=correction_id,
                correction_disposition="corrected", qa_state="passed",
            )
            counters["correction"] += 1
            if not source_group:
                counters["insertion"] += 1
        elif ordinal in localized:
            record.update(
                alignment="translated_or_consolidated_internal_prose_preserving_formula_meaning",
                sequence_opcode="replace", delta_class="localized_prose_translation", qa_state="passed",
            )
            counters["localized"] += 1
        elif ordinal in semantic_normalization:
            record.update(
                alignment="preserved_semantics_after_brace_normalization",
                sequence_opcode="replace", delta_class="typographic_semantic_normalization", qa_state="passed",
            )
            counters["semantic_normalization"] += 1
        elif len(source_group) == 1 and source_math[source_group[0]]["normalized"] == target_item["normalized"]:
            record["alignment"] = "preserved_exact_after_text_aware_whitespace_normalization"
            counters["exact"] += 1
        else:
            raise RuntimeError(f"unclassified Chapter 16 formula delta: target {ordinal}")
        records.append(record)

    deleted = source_math[659]
    records.append({
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map",
        "id": f"{CHAPTER_ID}-MATHMAP-SOURCE-DELETION-0001",
        "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-0660"], "target_formula_ids": [],
        "source_lines": [[deleted["line_start"], deleted["line_end"]]], "target_lines": [],
        "source_sha256": [deleted["sha256"]], "target_sha256": [],
        "source_delimiters": [deleted["delimiter"]], "delimiter": None,
        "ordinal_alignment": "source_deletion", "alignment": "reviewed_source_correction_deletion",
        "sequence_opcode": "delete", "delta_class": "classified_source_correction",
        "correction_id": f"{CHAPTER_ID}-CORR-015", "correction_disposition": "corrected",
        "qa_state": "passed",
    })
    counters["correction"] += 1
    counters["deletion"] += 1
    expected = collections.Counter({
        "exact": 684, "localized": 3, "semantic_normalization": 1,
        "correction": 13, "insertion": 1, "deletion": 1,
    })
    if counters != expected or len(records) != 701:
        raise RuntimeError(f"Chapter 16 formula classification differs: {counters}")
    return records, {
        "source_math_surfaces": 702, "target_math_surfaces": 700, "formula_map_records": 701,
        "preserved_exact_maps": 684, "localized_prose_translation_maps": 3,
        "typographic_semantic_normalization_maps": 1, "classified_source_correction_maps": 13,
        "target_insertions": 1, "source_deletions": 1,
    }


def artifact_records(ids: dict[str, dict[str, Any]], bound: bool) -> list[dict[str, Any]]:
    specs = [
        ("ARTIFACT-FAOA-ID-CH16-TARGET-TEX", "translation_source", TARGET_REL, True),
        ("ARTIFACT-FAOA-ID-THROUGH-CH16-MASTER", "cumulative_TeX_master", MASTER_REL, True),
        ("ARTIFACT-FAOA-ID-CH16-SOURCE-INVENTORY", "source_inventory", INVENTORY_REL, True),
        ("ARTIFACT-FAOA-ID-CH16-PRETRANSLATION-REVIEW", "pretranslation_mathematical_review", PRE_REVIEW_REL, True),
        ("ARTIFACT-FAOA-ID-CH16-TERM-PLAN", "terminology_plan", TERM_PLAN_REL, True),
        ("ARTIFACT-FAOA-ID-CH16-CORRECTIONS-LEDGER", "chapter_source_corrections_ledger", LEDGER_REL, True),
        ("ARTIFACT-FAOA-ID-CH16-TRANSLATION-REPORT", "translation_QA_report", REPORT_REL, bound),
        ("ARTIFACT-FAOA-ID-CH16-BILINGUAL-REVIEW", "bilingual_mathematical_review", BILINGUAL_REVIEW_REL, bound),
        ("ARTIFACT-FAOA-ID-THROUGH-CH16-PDF", "canonical_cumulative_reader_pdf", PDF_REL, bound),
        ("ARTIFACT-FAOA-ID-CH16-FINAL-BUILD-RESULT", "deterministic_build_result", BUILD_RESULT_REL, bound),
        ("ARTIFACT-FAOA-ID-CH16-RENDER-MANIFEST", "visual_QA_render_manifest", RENDER_MANIFEST_REL, bound),
        ("ARTIFACT-FAOA-ID-CH16-RENDER-AUDIT", "visual_QA_audit", RENDER_AUDIT_REL, bound),
        ("ARTIFACT-FAOA-ID-CH16-ACCESSIBILITY-AUDIT", "visual_accessibility_audit", ACCESSIBILITY_AUDIT_REL, bound),
        ("ARTIFACT-FAOA-ID-CH16-QA-RECEIPT", "admission_receipt", RECEIPT_REL, bound),
        ("ARTIFACT-FAOA-ID-SOURCE-CORRECTIONS-AGGREGATE-CH16", "aggregate_source_corrections_log", "provenance/SOURCE_CORRECTIONS.md", True),
    ]
    output = []
    for stable_id, kind, path, present in specs:
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "artifact",
            "id": stable_id, "unit_id": CHAPTER_ID, "artifact_kind": kind, "path": path,
            "binding_state": "bound" if present else "pending_final_artifact_binding",
            "admission_state": "admitted" if bound else "pending_final_artifact_binding",
        }
        if present:
            info = identity(ROOT / path)
            record.update(bytes=info["bytes"], sha256=info["sha256"])
            if not path.endswith(".pdf"):
                record["lines"] = info["lines"]
            if kind == "canonical_cumulative_reader_pdf":
                record.update(pages=ids["pdf"]["pages"], page_size="US Letter", pdf_lang="id-ID")
        output.append(record)
    return output


def qa_records(ids: dict[str, dict[str, Any]], formula_summary: dict[str, int], bound: bool, lock_sha: str) -> list[dict[str, Any]]:
    specs = [
        ("STRUCTURAL", "unit_structural", REPORT_REL, "pass"),
        ("MATH", "unit_mathematical", BILINGUAL_REVIEW_REL, "pass"),
        ("LANGUAGE", "unit_language_terminology", TERM_PLAN_REL, "pass"),
        ("EXERCISE-SUPPORT", "exercise_support_provenance", INVENTORY_REL, "pass"),
        ("RIGHTS", "unit_rights_privacy", RECEIPT_REL, "pass" if bound else "pending"),
        ("BUILD", "cumulative_build", BUILD_RESULT_REL, "pass" if bound else "pending"),
        ("VISUAL", "cumulative_visual", RENDER_AUDIT_REL, "pass" if bound else "pending"),
        ("ACCESSIBILITY", "cumulative_accessibility", ACCESSIBILITY_AUDIT_REL, "pass" if bound else "pending"),
        ("BACKEND", "backend_reconciliation", PREFIX_LOCK_REL, "pass"),
        ("ADMISSION", "unit_admission", RECEIPT_REL, "pass" if bound else "pending"),
    ]
    output = []
    for label, kind, witness, result in specs:
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "qa_event",
            "id": f"QA-CH16-{label}-20260824", "unit_id": CHAPTER_ID,
            "timestamp": "2026-08-24", "responsible_workflow": "Codex", "model_id": MODEL_ID,
            "qa_type": kind, "result": result, "witness": witness,
            "admission_state": "admitted" if bound else "pending_final_artifact_binding",
        }
        if label == "BACKEND":
            record["witness_sha256"] = lock_sha
        elif (ROOT / witness).is_file() and (result == "pass" or bound):
            record["witness_sha256"] = sha((ROOT / witness).read_bytes())
        else:
            record["witness_state"] = "pending_final_artifact_binding"
        output.append(record)
    output[0].update(
        sections=4, environment_begins=142, semantic_environment_begins=124,
        labels=36, references=28, citations=59, index_terms=107, defined_terms=29,
        manual_equation_tags=1, examples=15, exercise_environments=0, proof_environments=31,
    )
    output[1].update(formula_summary | {"unexplained_deltas": 0, "extractor": "backend/ch03_math.py"})
    output[2].update(defined_term_occurrences=29, new_controlled_terms=len(NEW_TERM_SPECS))
    output[3].update(
        source_exercises=0, upstream_exercise_hints=0, upstream_answers=0, upstream_solutions=0,
        exercise_support_records=0, provenance="no_formal_exercise_surface_upstream",
    )
    output[4].update(
        rights_id=RIGHTS, attribution_change_notice_sharealike_nonendorsement="present",
        credential_or_token_residue=0,
    )
    if bound:
        output[5].update(pages=ids["pdf"]["pages"], deterministic_replays=2, byte_identical=True)
        output[6].update(pages_rendered=ids["pdf"]["pages"], pages_inspected=ids["pdf"]["pages"], visual_defects=0)
        output[7].update(tagged_pdf=False, fully_accessible_pdf_claim=False, semantic_accessibility_state="remediation_required")
        output[9].update(
            decision="admitted", source_sha256=EXPECTED_SOURCE[2], target_sha256=EXPECTED_TARGET[2],
            build_master_sha256=EXPECTED_MASTER[2], artifact_sha256=ids["pdf"]["sha256"],
            correction_ledger_sha256=ids["ledger"]["sha256"], receipt_sha256=ids["receipt"]["sha256"],
            all_required_admission_gates="pass", publication_state="pending",
        )
    return output


def chapter_unit(ids: dict[str, dict[str, Any]], bound: bool) -> dict[str, Any]:
    record = QUEUED_CH16 | {
        "target_path": TARGET_REL, "target_bytes": EXPECTED_TARGET[0], "target_lines": EXPECTED_TARGET[1],
        "target_sha256": EXPECTED_TARGET[2], "target_title": "EKSTENSI",
        "translation_state": "admitted" if bound else "qa_passed_pending_artifact_binding",
        "qa_state": "passed", "source_corrections": 15,
        "build_master_path": MASTER_REL, "build_master_bytes": EXPECTED_MASTER[0],
        "build_master_lines": EXPECTED_MASTER[1], "build_master_sha256": EXPECTED_MASTER[2],
        "artifact_path": PDF_REL, "artifact_state": "canonical_output_copy_present_and_frozen" if bound else "pending_final_artifact_binding",
        "publication_state": "pending", "admission_state": "admitted" if bound else "pending_final_artifact_binding",
        "receipt_path": RECEIPT_REL, "model_provenance": MODEL_ID,
    }
    if bound:
        record.update(
            artifact_bytes=ids["pdf"]["bytes"], artifact_pages=ids["pdf"]["pages"],
            artifact_sha256=ids["pdf"]["sha256"], qa_receipt_id="QA-CH16-ADMISSION-20260824",
            receipt_sha256=ids["receipt"]["sha256"],
        )
    return record


def build_outputs(bind_final: bool) -> tuple[dict[str, bytes], dict[str, Any]]:
    records, index_fields, index_rows, lock_bytes, _ = stripped_prefix()
    ids = core_evidence()
    ledger, ledger_sha = ledger_records()
    if bind_final:
        if not final_available():
            raise RuntimeError("final Chapter 16 artifact set is incomplete")
        ids = final_evidence(ids)
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    semantic, segments, relations, source_anchors, _ = base.build_units_and_segments(source, target)
    kinds = collections.Counter(item["unit_kind"] for item in semantic)
    expected_kinds = collections.Counter({
        "section": 4, "prop": 38, "proof": 31, "defn": 21, "exam": 15,
        "thm": 8, "cor": 6, "notn": 3, "conv": 1,
    })
    if len(semantic) != 127 or kinds != expected_kinds or len(segments) != 141 or len(relations) != 408:
        raise RuntimeError(f"Chapter 16 semantic closure differs: {len(semantic)}/{kinds}/{len(segments)}/{len(relations)}")
    if bind_final:
        for item in semantic + segments:
            item["translation_state"] = "admitted"
            item["admission_state"] = "admitted"

    offsets: list[tuple[int, int, str]] = []
    anchor_ids = []
    section_number = node_number = 0
    for anchor in source_anchors:
        if anchor["anchor_type"] == "chapter":
            stable_id = CHAPTER_ID
        elif anchor["anchor_type"] == "section":
            section_number += 1
            stable_id = f"{CHAPTER_ID}-SEC-{section_number:03d}"
        else:
            node_number += 1
            stable_id = f"{CHAPTER_ID}-NODE-{node_number:04d}"
        anchor_ids.append(stable_id)
        if anchor["anchor_type"] != "chapter":
            offsets.append((anchor["start"], anchor["end"], stable_id))
    if len(source_anchors) != 128 or (section_number, node_number) != (4, 123):
        raise RuntimeError("Chapter 16 anchor closure differs")

    prior_labels = {
        item.get("source_local_id"): item["id"]
        for item in records["semantic_units.jsonl"] if item.get("source_local_id")
    }
    local_labels: dict[str, str] = {}
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if [x["argument"] for x in source_labels] != [x["argument"] for x in target_labels] or len(source_labels) != 36:
        raise RuntimeError("Chapter 16 label sequence differs")
    for number, occurrence in enumerate(source_labels, 1):
        candidates = [(end - start, stable_id) for start, end, stable_id in offsets if start <= occurrence["start"] < end]
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
    if [(kind, label) for _, kind, label in source_refs] != [(kind, label) for _, kind, label in target_refs] or len(source_refs) != 28:
        raise RuntimeError("Chapter 16 reference sequence differs")
    resolution_counts: collections.Counter[str] = collections.Counter()
    for number, (source_ref, target_ref) in enumerate(zip(source_refs, target_refs, strict=True), 1):
        source_position, source_kind, source_label = source_ref
        _, target_kind, target_label = target_ref
        if target_label in local_labels:
            endpoint, resolution = local_labels[target_label], "local"
        elif target_label in prior_labels:
            endpoint, resolution = prior_labels[target_label], "admitted_prior_unit"
        else:
            raise RuntimeError(f"unresolved Chapter 16 reference: {target_label}")
        resolution_counts[resolution] += 1
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}", "relation_type": "xref",
            "from_id": base.ch01.containing_segment(segments, source_position, "source"), "to_id": endpoint,
            "source_local_id": source_label, "target_local_id": target_label, "resolution": resolution,
            "source_surface": source_kind, "target_surface": target_kind,
        })
    if resolution_counts != collections.Counter({"local": 16, "admitted_prior_unit": 12}):
        raise RuntimeError(f"Chapter 16 reference-resolution closure differs: {resolution_counts}")

    source_cites = common.macro(source, "cite")
    target_cites = common.macro(target, "cite")
    if [x["argument"] for x in source_cites] != [x["argument"] for x in target_cites] or len(source_cites) != 59:
        raise RuntimeError("Chapter 16 citation sequence differs")
    for number, occurrence in enumerate(source_cites, 1):
        key = occurrence["argument"]
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-CITE-{number:04d}", "relation_type": "cites",
            "from_id": base.ch01.containing_segment(segments, occurrence["start"], "source"),
            "to_id": f"ERDMAN-FAOA-BIB-{key}", "source_local_id": key,
        })

    new_terms = terminology_records(source, target, records["terminology.jsonl"])
    source_defs = common.macro(source, "df")
    target_defs = common.macro(target, "df")
    for number, (sdef, tdef, term_id) in enumerate(zip(source_defs, target_defs, TERM_MAPPING, strict=True), 1):
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}", "relation_type": "uses_term",
            "from_id": base.ch01.containing_segment(segments, sdef["start"], "source"), "to_id": term_id,
            "source_term_tex": sdef["argument"], "target_term_tex": tdef["argument"], "locale": "id-ID",
        })

    source_indexes = common.macro(source, "index")
    target_indexes = common.macro(target, "index")
    if len(source_indexes) != 107 or len(target_indexes) != 107:
        raise RuntimeError("Chapter 16 index count differs")
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

    corrections = correction_records(ledger, ledger_sha, bind_final)
    formulas, formula_summary = formula_records(source, target)
    artifacts = artifact_records(ids, bind_final)
    qa = qa_records(ids, formula_summary, bind_final, sha(lock_bytes))
    common_relation = {"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "from_id": CHAPTER_ID}
    relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS})
    for number, artifact in enumerate(artifacts, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}", "relation_type": "has_artifact", "to_id": artifact["id"]})
    for number, event in enumerate(qa, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-QA-{number:04d}", "relation_type": "has_qa_event", "to_id": event["id"]})
    for number, correction in enumerate(corrections, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}", "relation_type": "documents_correction", "to_id": correction["id"]})
    if len(relations) != 601:
        raise RuntimeError(f"Chapter 16 relation closure differs: {len(relations)}")

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
    records["terminology.jsonl"].extend(new_terms)
    index_rows.extend(new_index_rows)
    records["units.jsonl"] = [chapter_unit(ids, bind_final) if x.get("id") == CHAPTER_ID else x for x in records["units.jsonl"]]

    outputs = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    outputs["index_terms.csv"] = csv_bytes(index_fields, index_rows)
    outputs["CH16_PREFIX_LOCKS.json"] = lock_bytes
    outputs["BACKEND_MANIFEST.csv"] = base.manifest_bytes(outputs)
    summary = {
        "unit": CHAPTER_ID, "binding_state": "bound" if bind_final else "pending_final_artifact_binding",
        "semantic_units": len(semantic), "segments": len(segments), "relations": len(relations),
        "formula_maps": len(formulas), "index_rows": len(new_index_rows), "new_terms": len(new_terms),
        "term_uses": len(TERM_MAPPING), "corrections": len(corrections), "exercise_support": 0,
        "qa_events": len(qa), "artifacts": len(artifacts),
        "reference_resolution": dict(resolution_counts), "target_sha256": EXPECTED_TARGET[2],
        "model_id": MODEL_ID,
    }
    return outputs, summary


def reconciliation_report(summary: dict[str, Any], outputs: dict[str, bytes]) -> bytes:
    lines = [
        "# FAOA-2015-CH16 backend reconciliation", "",
        "The Chapter 16 append preserves the exact admitted Chapter 1--15 byte prefix and binds the complete Extensions source/target topology.", "",
        f"- Target: `{TARGET_REL}` — {EXPECTED_TARGET[0]} bytes, SHA-256 `{EXPECTED_TARGET[2]}`.",
        f"- Semantic units: {summary['semantic_units']}; segments: {summary['segments']}; relations: {summary['relations']}.",
        f"- Formula maps: {summary['formula_maps']} covering 702 source and 700 target surfaces exactly once; index rows: {summary['index_rows']}.",
        f"- New terms: {summary['new_terms']}; term uses: {summary['term_uses']}; corrections: {summary['corrections']}; exercise-support records: 0.",
        "- `backend/CH16_PREFIX_LOCKS.json` locks the complete Chapter 1--15 prefix byte-for-byte.",
        "- `backend/validate_ch16_backend.py` checks stable-ID uniqueness, relation endpoints, formula/index closure, manifest identity, and deterministic replay.",
        f"- Model provenance: `{MODEL_ID}`.", "", "Generated identities:", "",
    ]
    for name in sorted(outputs, key=str.casefold):
        lines.append(f"- `{name}` — {len(outputs[name])} bytes, SHA-256 `{sha(outputs[name])}`")
    return ("\n".join(lines) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--bind-final-artifacts", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.preflight or (not args.bind_final_artifacts and not args.check):
        print(json.dumps(preflight(), ensure_ascii=False, sort_keys=True))
        return
    current_unit = next(json.loads(line) for line in (BACKEND / "units.jsonl").read_text(encoding="utf-8").splitlines() if json.loads(line).get("id") == CHAPTER_ID)
    bound = args.bind_final_artifacts or current_unit.get("admission_state") == "admitted"
    outputs, summary = build_outputs(bound)
    if args.check:
        mismatches = [name for name, data in outputs.items() if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != data]
        if mismatches:
            raise RuntimeError("deterministic backend replay differs: " + ", ".join(mismatches))
        print(json.dumps(summary | {"deterministic_replay": "pass"}, sort_keys=True))
        return
    for name, data in outputs.items():
        (BACKEND / name).write_bytes(data)
    report = reconciliation_report(summary, outputs)
    (ROOT / "qa/CH16_BACKEND_RECONCILIATION.md").write_bytes(report)
    print(json.dumps(summary | {"backend_report": "qa/CH16_BACKEND_RECONCILIATION.md"}, sort_keys=True))


if __name__ == "__main__":
    main()
