#!/usr/bin/env python3
"""Append receipt-bound deterministic Chapter 10 records after Chapters 1--9."""

from __future__ import annotations

import collections
import csv
import hashlib
import io
import json
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BACKEND = Path(os.environ.get("INTERLANGUAGE_BACKEND_DIR", ROOT / "backend")).resolve()
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "qa"))
import generate_ch01_backend as ch01  # noqa: E402
import ch03_math  # noqa: E402
import check_ch10_translation as checker  # noqa: E402


common = checker.common
SOURCE_PATH = ROOT / "source" / "upstream" / "distributions.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "distributions-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH10"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
ADMISSION_QA_ID = "QA-CH10-ADMISSION-20260822"

SOURCE_SIZE = 42_703
SOURCE_LINES = 894
SOURCE_SHA = "31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8"
TARGET_SIZE = 42_627
TARGET_LINES = 876
TARGET_SHA = "6456f9def822da572e117f3ec368931f0bfb441840aa0785be1df6080bbb6840"

MASTER_PATH = "source/id-ID/functional-analysis-id-through-ch10.tex"
MASTER_SIZE = 9_866
MASTER_LINES = 336
MASTER_SHA = "5de05f7a154bea99d11924fc21dbbf7495c8642d5a3c58e48e0fdd053dd400b4"
FINAL_PDF_PATH = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf"
PDF_SIZE = 1_796_056
PDF_PAGES = 153
PDF_SHA = "1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc"

CHECKER_PATH = "qa/check_ch10_translation.py"
CHECKER_SIZE = 16_387
CHECKER_LINES = 319
CHECKER_SHA = "fa247c00608997da81d65bdcadc0bfa916060a0bb8858c24e5f0a54ac5aa75db"
REPORT_PATH = "qa/ch10-translation-report.json"
REPORT_SIZE = 1_089
REPORT_LINES = 38
REPORT_SHA = "8b472e7b803cfb566e08c4ff3f1e464f7564520faf2f9115f3b57e7042c1218d"
CORRECTION_LEDGER_PATH = "provenance/SOURCE_CORRECTIONS_CH10.json"
CORRECTION_LEDGER_SIZE = 11_858
CORRECTION_LEDGER_LINES = 301
CORRECTION_LEDGER_SHA = "c5010ce91ae98d3c9b3637fe6a553f4df7d1ba524faa75b1f4fb42b0b036c948"
PROSE_LEDGER_PATH = "provenance/SOURCE_CORRECTIONS.md"
PROSE_LEDGER_SIZE = 32_495
PROSE_LEDGER_LINES = 573
PROSE_LEDGER_SHA = "8bd1be45b70a5e2395e67c20f192f89fc658f3d158d8ff7bb9b1e9cef77b947b"
RENDER_MANIFEST_PATH = "provenance/CH10_RENDER_MANIFEST.csv"
RENDER_MANIFEST_SIZE = 29_798
RENDER_MANIFEST_ROWS = 153
RENDER_MANIFEST_SHA = "b1dd863b6b2441e0a49bf9fe3248b759c9889f0a74654fbe060d868f60cfb7ca"
CONTACT_SHEET_PATH = "provenance/CH10_CONTACT_SHEET.png"
CONTACT_SHEET_SIZE = 4_463_573
CONTACT_SHEET_SHA = "e5b14686ad4ce088d02ba819e3df14621936dd888b429b92a9506e53ce9d34f6"
AUDIT_PATH = "qa/CH10_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
AUDIT_SIZE = 7_203
AUDIT_LINES = 129
AUDIT_SHA = "5d5ff18e230a8fc1d2aace1b801b53487ebb409c5bdb3bc6e600056b73a75bea"
TERM_DECISION_PATH = "provenance/CH10_TERMINOLOGY_DECISIONS.md"
TERM_DECISION_SIZE = 1_756
TERM_DECISION_LINES = 36
TERM_DECISION_SHA = "03005aa60200768a05c700e7d9d8cfa969034204e37ecffbd8b67126c5c66329"
TERM_WITNESS_PATH = "qa/terminology_evidence/itb-distribusi-tempered-2018-bab2.pdf"
TERM_WITNESS_SIZE = 283_518
TERM_WITNESS_SHA = "830a241c8ace73290a4c613cc6478bb17698d835b781b1fec332fa09838ddf02"

RECEIPT_PATH = "provenance/CH10_BUILD_AND_QA_RECEIPT.md"
RECEIPT_SIZE = 10_338
RECEIPT_LINES = 188
RECEIPT_SHA = "2a4d7a6379b1cc4f634fd45d75413133670c134d9b3ba55c363ff273645b9c1f"

# Exact canonical Chapter 1--9 byte prefixes. Chapter 10 may only append.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (887_156, "69cb894f6bb796ab1195ec8a7f13614c8f80e37df1b33662baf6582ad997815f"),
    "segments.jsonl": (998_274, "b81f691f34a99d02652395a753a751e8794921d2bc779dee63f239717b5f83e8"),
    "relations.jsonl": (1_231_458, "6ade8249fca5a8d89e22f17bfbb427314a83997a0d5511bbf8c7900ef36c7d4b"),
    "formula_map.jsonl": (4_119_919, "1c7c702cde9cbd02d4246a35117e8129530559818ddcf5915933f8d287f14952"),
    "exercise_support.jsonl": (19_302, "396af34f24d13d81c98b698838d7ffc92ce403e822534df682b24bac05b76814"),
    "index_terms.csv": (364_586, "8b6be5ff9f2c48868feef6328e615efc0fd5b10d1b7e5645a23f281d4d7bed90"),
    "artifacts.jsonl": (46_109, "941a6e92c90182c33da4a0eaa2cc9d2a87046bdda1f3a054a83b9b770a45b56d"),
    "qa_events.jsonl": (64_088, "d6c6f48a9078dd2bed9e7417111bbe2c4308942c1cdd8e2e15c0640b379caed4"),
    "corrections.jsonl": (126_130, "319a20d4d18a632b71a93aed15b6e6f533b23fa622a73bb26cce6aff35ff7b91"),
    "terminology.jsonl": (98_578, "98d69653ba962b1f88f84e9de28e13b9fa1c8f3fcbfbdc319e89b182f68a2144"),
}
UNIT_PREFIX_LOCK = (12_022, "297418f7329522e269bb7c66997665167e1ce8034a60dd2b06b34ddfceff0e4f")
UNIT_SUFFIX_LOCK = (3_731, "cfdb40e6debfad35ab5a0adaf8c7f0e6c2a6518ce1d7d3193e90e8b7f09cf6bc")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def admission_fields() -> dict[str, object]:
    return {
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_path": RECEIPT_PATH,
        "receipt_sha256": RECEIPT_SHA,
        "admission_state": "admitted",
    }


def locked_prefix(name: str) -> bytes:
    size, expected_sha = PREFIX_LOCKS[name]
    data = (BACKEND / name).read_bytes()
    if len(data) < size:
        raise ValueError(f"{name} is shorter than its locked Chapter 1--9 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha or not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1--9 prefix changed")
    return prefix


def append_jsonl(name: str, records: list[dict]) -> None:
    suffix = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")
    (BACKEND / name).write_bytes(locked_prefix(name) + suffix)


def verify_evidence() -> None:
    if not RECEIPT_SIZE or not RECEIPT_LINES or not RECEIPT_SHA:
        raise ValueError("Chapter 10 admission receipt identity has not been frozen")
    locks = {
        "source/upstream/distributions.tex": (SOURCE_SIZE, SOURCE_LINES, SOURCE_SHA),
        "source/id-ID/distributions-id.tex": (TARGET_SIZE, TARGET_LINES, TARGET_SHA),
        MASTER_PATH: (MASTER_SIZE, MASTER_LINES, MASTER_SHA),
        CHECKER_PATH: (CHECKER_SIZE, CHECKER_LINES, CHECKER_SHA),
        REPORT_PATH: (REPORT_SIZE, REPORT_LINES, REPORT_SHA),
        CORRECTION_LEDGER_PATH: (CORRECTION_LEDGER_SIZE, CORRECTION_LEDGER_LINES, CORRECTION_LEDGER_SHA),
        PROSE_LEDGER_PATH: (PROSE_LEDGER_SIZE, PROSE_LEDGER_LINES, PROSE_LEDGER_SHA),
        RENDER_MANIFEST_PATH: (RENDER_MANIFEST_SIZE, RENDER_MANIFEST_ROWS + 1, RENDER_MANIFEST_SHA),
        AUDIT_PATH: (AUDIT_SIZE, AUDIT_LINES, AUDIT_SHA),
        TERM_DECISION_PATH: (TERM_DECISION_SIZE, TERM_DECISION_LINES, TERM_DECISION_SHA),
        RECEIPT_PATH: (RECEIPT_SIZE, RECEIPT_LINES, RECEIPT_SHA),
    }
    for relative_path, (size, lines, expected_sha) in locks.items():
        path = ROOT / relative_path
        data = path.read_bytes()
        if (len(data), len(data.splitlines()), sha(data)) != (size, lines, expected_sha):
            raise ValueError(f"Chapter 10 evidence changed: {relative_path}")
    for relative_path, size, expected_sha in (
        (FINAL_PDF_PATH, PDF_SIZE, PDF_SHA),
        (CONTACT_SHEET_PATH, CONTACT_SHEET_SIZE, CONTACT_SHEET_SHA),
        (TERM_WITNESS_PATH, TERM_WITNESS_SIZE, TERM_WITNESS_SHA),
    ):
        data = (ROOT / relative_path).read_bytes()
        if (len(data), sha(data)) != (size, expected_sha):
            raise ValueError(f"Chapter 10 binary evidence changed: {relative_path}")
    report = json.loads((ROOT / REPORT_PATH).read_text(encoding="utf-8"))
    if report.get("status") != "pass" or report.get("unit_id") != CHAPTER_ID:
        raise ValueError("Chapter 10 checker report is not a frozen pass")


def unit_boundaries() -> tuple[bytes, bytes]:
    lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    expected_ids = [f"FAOA-2015-CH{number:02d}" for number in range(1, 18)] + ["FAOA-ID-BRIDGE-CS"]
    if len(lines) != len(expected_ids) or [json.loads(line)["id"] for line in lines] != expected_ids:
        raise ValueError("units.jsonl ordered unit closure changed")
    prefix = b"".join(lines[:9])
    middle = lines[9]
    suffix = b"".join(lines[10:])
    if (len(prefix), sha(prefix)) != UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--9 prefix changed")
    if (len(suffix), sha(suffix)) != UNIT_SUFFIX_LOCK:
        raise ValueError("units.jsonl Chapter 11--bridge suffix changed")
    if json.loads(middle).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 10 replacement boundary changed")
    return prefix, suffix


def chapter_ten_unit() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 10,
        "source_path": "distributions.tex",
        "source_bytes": SOURCE_SIZE,
        "source_lines": SOURCE_LINES,
        "source_sha256": SOURCE_SHA,
        "source_title": "DISTRIBUTIONS",
        "target_path": "source/id-ID/distributions-id.tex",
        "target_bytes": TARGET_SIZE,
        "target_lines": TARGET_LINES,
        "target_sha256": TARGET_SHA,
        "target_title": "Distribusi",
        "course_role": "advanced_continuation",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 16,
        "build_master_path": MASTER_PATH,
        "build_master_bytes": MASTER_SIZE,
        "build_master_lines": MASTER_LINES,
        "build_master_sha256": MASTER_SHA,
        "artifact_path": FINAL_PDF_PATH,
        "artifact_bytes": PDF_SIZE,
        "artifact_pages": PDF_PAGES,
        "artifact_sha256": PDF_SHA,
        "artifact_state": "canonical_output_copy_present_and_frozen",
        **admission_fields(),
        "publication_state": "pending",
        "rights_id": RIGHTS,
    }


def rewrite_units() -> None:
    prefix, suffix = unit_boundaries()
    encoded = (json.dumps(chapter_ten_unit(), ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    (BACKEND / "units.jsonl").write_bytes(prefix + encoded + suffix)


def artifact_records() -> list[dict]:
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "artifact",
        "unit_id": CHAPTER_ID,
        **admission_fields(),
    }
    specs = [
        ("ARTIFACT-FAOA-ID-CH10-TARGET-TEX", "admitted_translation_source", "source/id-ID/distributions-id.tex", TARGET_SIZE, TARGET_SHA),
        ("ARTIFACT-FAOA-ID-THROUGH-CH10-MASTER", "cumulative_TeX_master", MASTER_PATH, MASTER_SIZE, MASTER_SHA),
        ("ARTIFACT-FAOA-ID-THROUGH-CH10-PDF", "canonical_cumulative_reader_pdf", FINAL_PDF_PATH, PDF_SIZE, PDF_SHA),
        ("ARTIFACT-FAOA-ID-CH10-STRUCTURAL-CHECKER", "structural_math_language_checker", CHECKER_PATH, CHECKER_SIZE, CHECKER_SHA),
        ("ARTIFACT-FAOA-ID-CH10-TRANSLATION-REPORT", "classified_translation_report", REPORT_PATH, REPORT_SIZE, REPORT_SHA),
        ("ARTIFACT-FAOA-ID-CH10-CORRECTIONS-LEDGER", "chapter_source_corrections_ledger", CORRECTION_LEDGER_PATH, CORRECTION_LEDGER_SIZE, CORRECTION_LEDGER_SHA),
        ("ARTIFACT-FAOA-ID-CH10-PROSE-CORRECTIONS-LEDGER", "source_corrections_ledger", PROSE_LEDGER_PATH, PROSE_LEDGER_SIZE, PROSE_LEDGER_SHA),
        ("ARTIFACT-FAOA-ID-CH10-RENDER-MANIFEST", "visual_QA_render_manifest", RENDER_MANIFEST_PATH, RENDER_MANIFEST_SIZE, RENDER_MANIFEST_SHA),
        ("ARTIFACT-FAOA-ID-CH10-CONTACT-SHEET", "visual_QA_contact_sheet", CONTACT_SHEET_PATH, CONTACT_SHEET_SIZE, CONTACT_SHEET_SHA),
        ("ARTIFACT-FAOA-ID-CH10-VISUAL-ACCESSIBILITY-AUDIT", "visual_accessibility_audit", AUDIT_PATH, AUDIT_SIZE, AUDIT_SHA),
        ("ARTIFACT-FAOA-ID-CH10-QA-RECEIPT", "admission_receipt", RECEIPT_PATH, RECEIPT_SIZE, RECEIPT_SHA),
    ]
    records = [
        fields | {"id": record_id, "artifact_kind": kind, "path": path, "bytes": size, "sha256": digest}
        for record_id, kind, path, size, digest in specs
    ]
    records[0] |= {"lines": TARGET_LINES, "locale": "id-ID"}
    records[1] |= {"lines": MASTER_LINES, "locale": "id-ID", "cumulative_through_unit_id": CHAPTER_ID}
    records[2] |= {"pages": PDF_PAGES, "page_size": "US Letter", "locale": "id-ID", "pdf_lang": "id-ID", "publication_state": "pending"}
    records[3] |= {"lines": CHECKER_LINES}
    records[4] |= {"lines": REPORT_LINES, "decision": "pass", "classified_math_edit_blocks": 13, "model_id": "OpenAI Codex gpt-5.6-sol, Ultra"}
    records[5] |= {"lines": CORRECTION_LEDGER_LINES, "chapter_correction_count": 16, "mechanical_repairs": 5, "mathematical_repairs": 9, "semantic_repairs": 2}
    records[6] |= {"lines": PROSE_LEDGER_LINES, "chapter_correction_count": 16, "append_only_through_unit_id": CHAPTER_ID}
    records[7] |= {"rows": RENDER_MANIFEST_ROWS, "render_pages": PDF_PAGES, "uniform_pixel_dimensions": "1275x1650"}
    records[8] |= {"visual_pages": PDF_PAGES, "all_pages_inspected": True}
    records[9] |= {"lines": AUDIT_LINES, "visual_result": "pass", "accessibility_gate_result": "pass", "fully_accessible_pdf_claim": "fail", "tagged_pdf": False, "accessible_html_or_tagged_pdf_state": "pending"}
    records[10] |= {"lines": RECEIPT_LINES, "decision": "admitted"}
    return records


def correction_records() -> list[dict]:
    ledger = json.loads((ROOT / CORRECTION_LEDGER_PATH).read_text(encoding="utf-8"))
    if ledger.get("record_count") != 16 or len(ledger.get("records", [])) != 16:
        raise ValueError("Chapter 10 correction-ledger count changed")
    records = []
    for item in ledger["records"]:
        records.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "correction",
            "id": item["id"],
            "unit_id": CHAPTER_ID,
            "source_locator": f"distributions.tex:{item['source_lines']['start']}--{item['source_lines']['end']}",
            "target_locator": f"source/id-ID/distributions-id.tex:{item['target_lines']['start']}--{item['target_lines']['end']}",
            "correction_type": item["classification"].lower(),
            "decision": item["decision"],
            "source_normalized_snippet_sha256": item["source_normalized_snippet_sha256"],
            "target_normalized_snippet_sha256": item["target_normalized_snippet_sha256"],
            "required_target_anchor": item["required_target_anchor"],
            "target_disposition": "corrected",
            "ledger_path": CORRECTION_LEDGER_PATH,
            "ledger_sha256": CORRECTION_LEDGER_SHA,
            **admission_fields(),
            "qa_state": "passed",
            "upstream_report": "deferred_until_complete_and_separately_authorized",
        })
    return records


EXISTING_TERM_IDS = {
    "regular": "TERM-REGULAR",
    "weak topology": "TERM-WEAK-TOPOLOGY",
    "$w^*$-topology": "TERM-WEAK-STAR-TOPOLOGY",
    "support": "TERM-SUPPORT",
}
NEW_TERM_SPECS: list[tuple[str, str, str]] = [
    ("TERM-DIRECTED-SYSTEM", "directed system", "sistem terarah"),
    ("TERM-INDUCTIVE-LIMIT", "inductive limit", "limit induktif"),
    ("TERM-DIRECT-LIMIT", "direct limit", "limit langsung"),
    ("TERM-STRONG-TOPOLOGY", "strong topology", "topologi kuat"),
    ("TERM-STRICT-INDUCTIVE-SEQUENCE", "strict inductive sequence", "barisan induktif ketat"),
    ("TERM-STRICT-INDUCTIVE-LIMIT", "strict inductive limit", "limit induktif ketat"),
    ("TERM-INDUCTIVE-LIMIT-TOPOLOGY", "inductive limit topology", "topologi limit induktif"),
    ("TERM-LF-SPACE", "$LF$-space", "ruang-$LF$"),
    ("TERM-LOCALLY-INTEGRABLE", "locally integrable", "terintegralkan secara lokal"),
    ("TERM-DISTRIBUTION", "distribution", "distribusi"),
    ("TERM-SINGULAR", "singular", "singular"),
    ("TERM-DIRAC-MEASURE", "Dirac measure", "ukuran Dirac"),
    ("TERM-DIRAC-DELTA-DISTRIBUTION-AT-A", "Dirac delta distribution at $a$", "distribusi delta Dirac di $a$"),
    ("TERM-HEAVISIDE-FUNCTION", "Heaviside function", "fungsi Heaviside"),
    ("TERM-HEAVISIDE-DISTRIBUTION", "Heaviside distribution", "distribusi Heaviside"),
    ("TERM-DERIVATIVE", "derivative", "turunan"),
    ("TERM-DIFFERENTIAL-OPERATOR", "differential operator", "operator diferensial"),
    ("TERM-DIPOLE", "dipole", "dipol"),
    ("TERM-NORMALIZED-LEBESGUE-MEASURE", "normalized Lebesgue measure", "ukuran Lebesgue ternormalisasi"),
    ("TERM-CONVOLUTION", "convolution", "konvolusi"),
    ("TERM-FOURIER-TRANSFORM", "Fourier transform", "transformasi Fourier"),
    ("TERM-FORMAL-ADJOINT", "formal adjoint", "adjoin formal"),
    ("TERM-CLASSICAL", "classical", "klasik"),
    ("TERM-WEAK", "weak", "lemah"),
    ("TERM-DISTRIBUTIONAL", "distributional", "distribusional"),
    ("TERM-GENERALIZED", "generalized", "diperumum"),
    ("TERM-TEMPERED-DISTRIBUTIONS", "tempered distributions", "distribusi tempered"),
    ("TERM-TEMPERATE-DISTRIBUTIONS", "temperate distributions", "distribusi temperate"),
]


def term_id_map() -> dict[str, str]:
    mapping = EXISTING_TERM_IDS | {source: stable_id for stable_id, source, _ in NEW_TERM_SPECS}
    if len(mapping) != 32:
        raise ValueError("Chapter 10 distinct defined-term inventory changed")
    return mapping


def terminology_records() -> list[dict]:
    records = []
    for stable_id, source, preferred in NEW_TERM_SPECS:
        evidence = f"{CHAPTER_ID} target; {CHECKER_PATH}; {REPORT_PATH}"
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "term",
            "id": stable_id,
            "source_term": source,
            "locale": "id-ID",
            "preferred": preferred,
            "variants": [],
            "rejected": [],
            "scope": "inductive limits, distributions, convolution, ODEs, and Fourier analysis",
            "evidence": evidence,
        }
        if stable_id == "TERM-TEMPERED-DISTRIBUTIONS":
            record |= {
                "variants": ["distribusi temperate"],
                "terminology_decision_path": TERM_DECISION_PATH,
                "terminology_decision_sha256": TERM_DECISION_SHA,
                "field_usage_witness_sha256": TERM_WITNESS_SHA,
            }
        elif stable_id == "TERM-TEMPERATE-DISTRIBUTIONS":
            record |= {
                "canonical_term_id": "TERM-TEMPERED-DISTRIBUTIONS",
                "recognition_form": True,
                "terminology_decision_path": TERM_DECISION_PATH,
                "terminology_decision_sha256": TERM_DECISION_SHA,
            }
        records.append(record)
    return records


FORMULA_CORRECTIONS = {
    42: f"{CHAPTER_ID}-CORR-001",
    **{number: f"{CHAPTER_ID}-CORR-003" for number in range(63, 69)},
    86: f"{CHAPTER_ID}-CORR-005",
    88: f"{CHAPTER_ID}-CORR-006",
    330: f"{CHAPTER_ID}-CORR-010",
    404: f"{CHAPTER_ID}-CORR-012",
    438: f"{CHAPTER_ID}-CORR-013",
    443: f"{CHAPTER_ID}-CORR-014",
    592: f"{CHAPTER_ID}-CORR-015",
    602: f"{CHAPTER_ID}-CORR-016",
    603: f"{CHAPTER_ID}-CORR-016",
}
DIRECT_LIMIT_TARGETS = set(range(63, 69))
LOCALIZED_HBOX_TARGETS = {251, 252, 259, 260, 261, 265, 266, 267}
MATH_KEY_LOCALIZED_TARGETS = {186}


def build_math_pairs(source: str, target: str) -> tuple[list[dict], dict[str, object]]:
    source_math = ch03_math.extract_math(source, SOURCE_ENCODING)
    target_math = ch03_math.extract_math(target, TARGET_ENCODING)
    if (len(source_math), len(target_math)) != (651, 648):
        raise ValueError("Chapter 10 math-surface count changed")
    source_keys = [ch03_math.math_key(record["normalized"]) for record in source_math]
    target_keys = [ch03_math.math_key(record["normalized"]) for record in target_math]
    mapping: list[list[int] | None] = [None] * len(target_math)
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, source_keys, target_keys, autojunk=False).get_opcodes():
        if tag == "equal":
            for source_index, target_index in zip(range(i1, i2), range(j1, j2), strict=True):
                mapping[target_index] = [source_index]
        elif (tag, i1, i2, j1, j2) == ("replace", 62, 71, 62, 68):
            mapping[62] = list(range(62, 71))
            for target_index in range(63, 68):
                mapping[target_index] = []
        elif (tag, i1, i2, j1, j2) == ("insert", 88, 88, 85, 86):
            mapping[85] = [89]
        elif (tag, i1, i2, j1, j2) == ("replace", 89, 91, 87, 88):
            mapping[87] = [90]
        elif tag == "replace" and i2 - i1 == j2 - j1:
            for source_index, target_index in zip(range(i1, i2), range(j1, j2), strict=True):
                mapping[target_index] = [source_index]
        else:
            raise ValueError(f"unexpected Chapter 10 math opcode: {(tag, i1, i2, j1, j2)}")
    if any(value is None for value in mapping):
        raise ValueError("Chapter 10 target formula coverage is incomplete")
    complete = [value for value in mapping if value is not None]
    flattened = [index for group in complete for index in group]
    if sorted(flattened) != list(range(len(source_math))):
        raise ValueError("Chapter 10 source formula closure is not exact and one-to-one")

    records: list[dict] = []
    counts: collections.Counter[str] = collections.Counter()
    group_source_ids = [f"{CHAPTER_ID}-SRC-MATH-{number:04d}" for number in range(63, 72)]
    group_target_ids = [f"{CHAPTER_ID}-ID-MATH-{number:04d}" for number in range(63, 69)]
    for number, (source_indexes, target_record) in enumerate(zip(complete, target_math, strict=True), 1):
        source_records = [source_math[index] for index in source_indexes]
        exact = len(source_records) == 1 and source_records[0]["normalized"] == target_record["normalized"]
        key_equal = len(source_records) == 1 and source_keys[source_indexes[0]] == target_keys[number - 1]
        if number == 86:
            alignment = "preserved_exact_after_text_aware_whitespace_normalization_reordered"
        elif number in MATH_KEY_LOCALIZED_TARGETS:
            alignment = "preserved_math_key_after_localized_text_substitution"
        elif number in LOCALIZED_HBOX_TARGETS:
            alignment = "localized_math_text_reviewed"
        elif number == 63:
            alignment = "reviewed_source_correction_group_primary"
        elif number in DIRECT_LIMIT_TARGETS:
            alignment = "reviewed_target_only_source_correction_group_member"
        elif number in FORMULA_CORRECTIONS:
            alignment = "reviewed_source_correction"
        elif exact:
            alignment = "preserved_exact_after_text_aware_whitespace_normalization"
        else:
            raise ValueError(f"unexpected Chapter 10 formula delta at target {number}")
        counts[alignment] += 1
        record: dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{number:04d}",
            "alignment": alignment,
            "math_key_alignment": "equal" if key_equal else "target_only" if not source_indexes else "reviewed_difference",
            "ordinal_alignment": "source_absent" if not source_indexes else "same" if source_indexes[0] + 1 == number else "shifted",
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{index + 1:04d}" for index in source_indexes],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{number:04d}"],
            "source_lines": [[item["line_start"], item["line_end"]] for item in source_records],
            "target_lines": [[target_record["line_start"], target_record["line_end"]]],
            "source_sha256": [item["sha256"] for item in source_records],
            "target_sha256": [target_record["sha256"]],
            "source_delimiters": [item["delimiter"] for item in source_records],
            "delimiter": target_record["delimiter"],
        }
        if number in FORMULA_CORRECTIONS:
            record |= {
                "sequence_opcode": "move" if number == 86 else "replace",
                "delta_class": "source_correction",
                "correction_id": FORMULA_CORRECTIONS[number],
                "correction_disposition": "corrected",
                "review_witness": REPORT_PATH,
                "qa_state": "passed",
            }
        elif number in MATH_KEY_LOCALIZED_TARGETS or number in LOCALIZED_HBOX_TARGETS:
            record |= {
                "sequence_opcode": "localize_text",
                "delta_class": "localization_inside_math_text",
                "correction_disposition": "not_a_source_correction",
                "qa_state": "passed",
            }
        if number in DIRECT_LIMIT_TARGETS:
            record |= {
                "replacement_group_id": f"{CHAPTER_ID}-CORR-003-MATH-GROUP",
                "replacement_group_source_formula_ids": group_source_ids,
                "replacement_group_target_formula_ids": group_target_ids,
                "replacement_group_role": "primary" if number == 63 else "member",
            }
        records.append(record)

    expected = {
        "preserved_exact_after_text_aware_whitespace_normalization": 623,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 1,
        "preserved_math_key_after_localized_text_substitution": 1,
        "localized_math_text_reviewed": 8,
        "reviewed_source_correction_group_primary": 1,
        "reviewed_target_only_source_correction_group_member": 5,
        "reviewed_source_correction": 9,
    }
    if dict(counts) != expected:
        raise ValueError(f"Chapter 10 formula alignment counts changed: {dict(counts)}")
    return records, {
        "source_math_surfaces": 651,
        "target_math_surfaces": 648,
        "exact_normalized_alignments": 624,
        "math_key_preserving_alignments": 625,
        "localization_only_math_text_substitutions": 9,
        "reviewed_source_correction_maps": 16,
        "grouped_source_correction_maps": 6,
        "formula_map_records": 648,
    }


def qa_records(formula_summary: dict[str, object]) -> list[dict]:
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "timestamp": "2026-08-22",
        "responsible_workflow": "Codex",
        "model_id": "OpenAI Codex gpt-5.6-sol, Ultra",
        **admission_fields(),
    }
    specs = [
        ("QA-CH10-STRUCTURAL-20260822", "unit_structural", CHECKER_PATH, CHECKER_SHA),
        ("QA-CH10-MATH-20260822", "unit_mathematical", REPORT_PATH, REPORT_SHA),
        ("QA-CH10-LANGUAGE-20260822", "unit_language_terminology", REPORT_PATH, REPORT_SHA),
        ("QA-CH10-BUILD-20260822", "cumulative_build", FINAL_PDF_PATH, PDF_SHA),
        ("QA-CH10-VISUAL-20260822", "cumulative_visual", AUDIT_PATH, AUDIT_SHA),
        ("QA-CH10-ACCESSIBILITY-20260822", "cumulative_accessibility", AUDIT_PATH, AUDIT_SHA),
        ("QA-CH10-RIGHTS-20260822", "unit_rights_privacy", CHECKER_PATH, CHECKER_SHA),
        (ADMISSION_QA_ID, "unit_admission", RECEIPT_PATH, RECEIPT_SHA),
    ]
    records = [
        fields | {"id": record_id, "qa_type": kind, "result": "pass", "witness": witness, "witness_sha256": witness_sha}
        for record_id, kind, witness, witness_sha in specs
    ]
    records[0] |= {"semantic_anchors": 117, "semantic_units": 116, "segments": 132, "sections": 6, "environment_begins": 124, "labels": 18, "references": 20, "citations": 29, "index_terms": 101, "defined_terms": 35, "exercise_environments": 11, "proof_environments": 18, "proof_hints": 3, "citation_only_proofs": 15}
    records[1] |= formula_summary | {"classified_math_edit_blocks": 13, "unexplained_deltas": 0, "extractor": "backend/ch03_math.py", "extractor_sha256": "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3"}
    records[2] |= {"severity_counts": {"P1": 0, "P2": 0, "P3": 0}, "unintended_english_prose": 0, "placeholders": 0, "terminology_reconciled": True, "terminology_decision_path": TERM_DECISION_PATH, "terminology_decision_sha256": TERM_DECISION_SHA, "field_usage_witness_sha256": TERM_WITNESS_SHA, "field_usage_witness_publication_state": "excluded_rights_not_established"}
    records[3] |= {"master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH10-MASTER", "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH10-PDF", "pages": PDF_PAGES}
    records[4] |= {"pages_rendered": PDF_PAGES, "pages_inspected": PDF_PAGES, "render_manifest_sha256": RENDER_MANIFEST_SHA, "contact_sheet_sha256": CONTACT_SHEET_SHA, "visual_defects": 0}
    records[5] |= {"tagged_pdf": False, "fully_accessible_pdf_claim": False, "semantic_accessibility_state": "remediation_required", "accessible_html_or_tagged_pdf_state": "pending", "admission_blocker_for_chapter_boundary": False}
    records[6] |= {"rights_id": RIGHTS, "attribution_change_notice_sharealike_nonendorsement": "present", "private_control_paths_absent_from_public_artifacts": True, "credential_or_token_residue": 0, "unlicensed_terminology_witness_excluded_from_public_release": True}
    records[7] |= {"decision": "admitted", "source_sha256": SOURCE_SHA, "target_sha256": TARGET_SHA, "build_master_sha256": MASTER_SHA, "artifact_sha256": PDF_SHA, "correction_ledger_sha256": CORRECTION_LEDGER_SHA, "required_admission_gate_results": {kind: "pass" for kind in ("unit_structural", "unit_mathematical", "unit_language_terminology", "cumulative_build", "cumulative_visual", "cumulative_accessibility", "unit_rights_privacy", "admission_receipt")}, "all_required_admission_gates": "pass", "publication_state": "pending"}
    return records


def prior_label_map() -> dict[str, str]:
    return {
        record["source_local_id"]: record["id"]
        for record in (json.loads(line) for line in locked_prefix("semantic_units.jsonl").splitlines())
        if record.get("source_local_id")
    }


def write_manifest() -> None:
    paths = sorted(
        [path for path in BACKEND.iterdir() if path.is_file() and path.name != "BACKEND_MANIFEST.csv" and not path.name.endswith(".pyc")],
        key=lambda path: path.name.casefold(),
    )
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["relative_path", "bytes", "sha256"])
    for path in paths:
        data = path.read_bytes()
        writer.writerow([path.name, len(data), sha(data)])
    (BACKEND / "BACKEND_MANIFEST.csv").write_text(buffer.getvalue(), encoding="utf-8", newline="")


def main() -> None:
    verify_evidence()
    for name in PREFIX_LOCKS:
        locked_prefix(name)
    unit_boundaries()
    source = SOURCE_PATH.read_text(encoding=SOURCE_ENCODING)
    target = TARGET_PATH.read_text(encoding=TARGET_ENCODING)

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if len(source_anchors) != 117 or [ch01.anchor_signature(anchor) for anchor in source_anchors] != [ch01.anchor_signature(anchor) for anchor in target_anchors]:
        raise ValueError("Chapter 10 semantic anchor topology differs")
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 18 or [item["argument"] for item in source_labels] != [item["argument"] for item in target_labels]:
        raise ValueError("Chapter 10 label sequence differs")

    semantic_units: list[dict] = []
    segment_records: list[dict] = []
    relations: list[dict] = []
    anchor_ids: list[str] = []
    anchor_bounds: dict[str, tuple[int, int]] = {}
    current_section = CHAPTER_ID
    current_section_by_anchor: list[str] = []
    section_number = node_number = 0
    for source_anchor, target_anchor in zip(source_anchors, target_anchors, strict=True):
        if source_anchor["anchor_type"] == "chapter":
            unit_id, parent_id, kind = CHAPTER_ID, TARGET_EDITION, "chapter"
        elif source_anchor["anchor_type"] == "section":
            section_number += 1
            unit_id, parent_id, kind = f"{CHAPTER_ID}-SEC-{section_number:03d}", CHAPTER_ID, "section"
            current_section = unit_id
        else:
            node_number += 1
            unit_id, parent_id, kind = f"{CHAPTER_ID}-NODE-{node_number:04d}", current_section, source_anchor["environment"]
        anchor_ids.append(unit_id)
        current_section_by_anchor.append(current_section)
        anchor_bounds[unit_id] = (source_anchor["start"], source_anchor["end"])
        if source_anchor["anchor_type"] == "chapter":
            continue
        source_fragment = ch01.fragment(source, source_anchor["start"], source_anchor["end"], SOURCE_ENCODING)
        target_fragment = ch01.fragment(target, target_anchor["start"], target_anchor["end"], TARGET_ENCODING)
        semantic_units.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "unit", "id": unit_id,
            "unit_kind": kind, "parent_id": parent_id, "order_in_chapter": len(semantic_units) + 1,
            "edition_id": EDITION, "target_edition_id": TARGET_EDITION,
            "source_path": "source/upstream/distributions.tex", "source_line_start": source_fragment["line_start"], "source_line_end": source_fragment["line_end"], "source_fragment_sha256": source_fragment["sha256"],
            "target_path": "source/id-ID/distributions-id.tex", "target_line_start": target_fragment["line_start"], "target_line_end": target_fragment["line_end"], "target_fragment_sha256": target_fragment["sha256"],
            "source_local_id": source_anchor.get("label"), "source_title_tex": source_anchor.get("title"), "target_title_tex": target_anchor.get("title"),
            "locale": "id-ID", "translation_state": "admitted", "qa_state": "passed", "rights_id": RIGHTS,
        })
        relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-CONTAINS-{len(semantic_units):04d}", "relation_type": "contains", "from_id": parent_id, "to_id": unit_id})
    if (len(semantic_units), section_number, node_number) != (116, 6, 110):
        raise ValueError("Chapter 10 semantic-unit topology invariant failed")

    source_parts: list[tuple[int, int, str, str]] = []
    target_parts: list[tuple[int, int, str, str]] = []
    previous_source = previous_target = 0
    previous_parent = CHAPTER_ID
    for index, (source_anchor, target_anchor, unit_id) in enumerate(zip(source_anchors, target_anchors, anchor_ids, strict=True)):
        if source_anchor["start"] > previous_source or target_anchor["start"] > previous_target:
            source_raw = ch01.active_same_length(source[previous_source:source_anchor["start"]]).strip()
            target_raw = ch01.active_same_length(target[previous_target:target_anchor["start"]]).strip()
            if source_raw or target_raw:
                source_parts.append((previous_source, source_anchor["start"], "prose", previous_parent))
                target_parts.append((previous_target, target_anchor["start"], "prose", previous_parent))
        role = "title" if source_anchor["anchor_type"] in {"chapter", "section"} else "semantic_environment"
        source_parts.append((source_anchor["start"], source_anchor["end"], role, unit_id))
        target_parts.append((target_anchor["start"], target_anchor["end"], role, unit_id))
        previous_source, previous_target = source_anchor["end"], target_anchor["end"]
        previous_parent = current_section_by_anchor[index]
    if previous_source < len(source) or previous_target < len(target):
        if ch01.active_same_length(source[previous_source:]).strip() or ch01.active_same_length(target[previous_target:]).strip():
            source_parts.append((previous_source, len(source), "prose", previous_parent))
            target_parts.append((previous_target, len(target), "prose", previous_parent))
    if len(source_parts) != 132 or len(target_parts) != 132:
        raise ValueError("Chapter 10 segment topology differs")

    for number, (source_part, target_part) in enumerate(zip(source_parts, target_parts, strict=True), 1):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if (role, parent_id) != (target_role, target_parent):
            raise ValueError("Chapter 10 source/target segment roles differ")
        source_fragment = ch01.fragment(source, source_start, source_end, SOURCE_ENCODING)
        target_fragment = ch01.fragment(target, target_start, target_end, TARGET_ENCODING)
        segment_id = f"{CHAPTER_ID}-SEG-{number:04d}"
        segment_records.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "segment", "id": segment_id, "parent_id": parent_id, "order": number, "segment_role": role,
            "source_path": "source/upstream/distributions.tex", "source_line_start": source_fragment["line_start"], "source_line_end": source_fragment["line_end"], "source_bytes": source_fragment["bytes"], "source_sha256": source_fragment["sha256"],
            "target_path": "source/id-ID/distributions-id.tex", "target_line_start": target_fragment["line_start"], "target_line_end": target_fragment["line_end"], "target_bytes": target_fragment["bytes"], "target_sha256": target_fragment["sha256"],
            "source_edition_id": EDITION, "target_edition_id": TARGET_EDITION, "locale": "id-ID", "translation_state": "admitted", "qa_state": "passed", "rights_id": RIGHTS,
            "_source_start": source_start, "_source_end": source_end, "_target_start": target_start, "_target_end": target_end,
        })
        relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-TRANSLATES-{number:04d}", "relation_type": "translates", "from_id": segment_id, "to_id": segment_id, "source_edition_id": EDITION, "target_edition_id": TARGET_EDITION})
        if number > 1:
            relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-PRECEDES-{number - 1:04d}", "relation_type": "precedes", "from_id": f"{CHAPTER_ID}-SEG-{number - 1:04d}", "to_id": segment_id})

    local_label_map: dict[str, str] = {}
    for number, occurrence in enumerate(source_labels, 1):
        segment_id = ch01.containing_segment(segment_records, occurrence["start"], "source")
        segment = next(record for record in segment_records if record["id"] == segment_id)
        local_label_map[occurrence["argument"]] = segment["parent_id"]
        relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-LABEL-{number:04d}", "relation_type": "declares_label", "from_id": segment_id, "to_id": segment["parent_id"], "source_local_id": occurrence["argument"], "label_id": f"ERDMAN-FAOA-2015-LABEL-{occurrence['argument']}"})

    source_refs = common.reference_sequence(source)
    target_refs = common.reference_sequence(target)
    if len(source_refs) != 20 or [item[1:] for item in source_refs] != [item[1:] for item in target_refs]:
        raise ValueError("Chapter 10 reference sequence differs")
    prior_labels = prior_label_map()
    reference_counts: collections.Counter[str] = collections.Counter()
    reference_kinds: collections.Counter[str] = collections.Counter()
    for number, (position, kind, label) in enumerate(source_refs, 1):
        if label in local_label_map:
            to_id, resolution = local_label_map[label], "local"
        elif label in prior_labels:
            to_id, resolution = prior_labels[label], "admitted_prior_unit"
        else:
            raise ValueError(f"unresolved Chapter 10 reference: {label}")
        reference_counts[resolution] += 1
        reference_kinds[kind] += 1
        relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}", "relation_type": "xref", "from_id": ch01.containing_segment(segment_records, position, "source"), "to_id": to_id, "source_local_id": label, "resolution": resolution, "target_surface": kind})
    if dict(reference_counts) != {"local": 15, "admitted_prior_unit": 5} or dict(reference_kinds) != {"ref": 13, "eqref": 7}:
        raise ValueError(f"Chapter 10 reference closure changed: {dict(reference_counts)}, {dict(reference_kinds)}")

    source_cites = common.macro(source, "cite")
    target_cites = common.macro(target, "cite")
    if len(source_cites) != 29 or [item["argument"] for item in source_cites] != [item["argument"] for item in target_cites]:
        raise ValueError("Chapter 10 citation sequence differs")
    cite_key_count = 0
    for occurrence_number, occurrence in enumerate(source_cites, 1):
        for key in [item.strip() for item in occurrence["argument"].split(",")]:
            cite_key_count += 1
            relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-CITE-{occurrence_number:04d}-{key}", "relation_type": "cites", "from_id": ch01.containing_segment(segment_records, occurrence["start"], "source"), "to_id": f"ERDMAN-FAOA-BIB-{key}", "source_local_id": key})
    if cite_key_count != 29:
        raise ValueError("Chapter 10 citation-key count changed")

    previous_statement: str | None = None
    hint_ids_by_statement: dict[str, list[str]] = collections.defaultdict(list)
    proof_count = hint_relations = 0
    for record in semantic_units:
        if record["unit_kind"] != "proof":
            previous_statement = record["id"]
            continue
        proof_count += 1
        if "Hint for proof" in (record.get("source_title_tex") or ""):
            if previous_statement is None:
                raise ValueError("Chapter 10 proof hint lacks preceding statement")
            hint_relations += 1
            hint_ids_by_statement[previous_statement].append(record["id"])
            relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-HINTS-{hint_relations:04d}", "relation_type": "hints", "from_id": record["id"], "to_id": previous_statement})
    proof_roles = collections.Counter(item["role"] for item in checker.ch09.proof_records(source))
    if (proof_count, hint_relations, proof_roles) != (18, 3, collections.Counter({"citation": 15, "hint": 3})):
        raise ValueError("Chapter 10 proof-role topology changed")

    source_df = common.macro(source, "df")
    target_df = common.macro(target, "df")
    if len(source_df) != 35 or len(target_df) != 35:
        raise ValueError("Chapter 10 defined-term occurrence count changed")
    term_ids = term_id_map()
    if set(term_ids) != {item["argument"] for item in source_df}:
        raise ValueError("Chapter 10 distinct defined-term closure changed")
    for number, (source_term, target_term) in enumerate(zip(source_df, target_df, strict=True), 1):
        relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}", "relation_type": "uses_term", "from_id": ch01.containing_segment(segment_records, source_term["start"], "source"), "to_id": term_ids[source_term["argument"]], "source_term_tex": source_term["argument"], "target_term_tex": target_term["argument"], "locale": "id-ID"})

    source_terms = common.macro(source, "index")
    target_terms = common.macro(target, "index")
    if len(source_terms) != 101 or len(target_terms) != 101 or [common.index_signature(item["argument"]) for item in source_terms] != [common.index_signature(item["argument"]) for item in target_terms]:
        raise ValueError("Chapter 10 index-term alignment changed")
    term_buffer = io.StringIO(newline="")
    term_writer = csv.writer(term_buffer, lineterminator="\n")
    for number, (source_term, target_term) in enumerate(zip(source_terms, target_terms, strict=True), 1):
        term_writer.writerow([f"{CHAPTER_ID}-TERM-OCC-{number:04d}", ch01.containing_segment(segment_records, source_term["start"], "source"), number, source_term["line"], source_term["argument"], target_term["line"], target_term["argument"], sha(source_term["argument"].encode(SOURCE_ENCODING)), sha(target_term["argument"].encode(TARGET_ENCODING)), "id-ID"])

    formula_records, formula_summary = build_math_pairs(source, target)
    exercises: list[dict] = []
    expected_inline_lines = [[], [], [], [], [], [383], [425], [432], [441], [670], []]
    for record in semantic_units:
        if record["unit_kind"] != "exer":
            continue
        number = len(exercises) + 1
        start, end = anchor_bounds[record["id"]]
        fragment = source[start:end]
        inline_lines = [source.count("\n", 0, start + match.start()) + 1 for match in re.finditer(r"\\emph\{Hint\.\}", fragment)]
        exercises.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "exercise_support", "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-{number:03d}", "exercise_unit_id": record["id"], "source_exercise_order": number, "upstream_hint_ids": hint_ids_by_statement.get(record["id"], []), "upstream_inline_hint_state": "present" if inline_lines else "absent", **({"upstream_inline_hint_source_lines": inline_lines} if inline_lines else {}), "upstream_answer_state": "absent", "upstream_solution_state": "absent", "original_solution_id": f"O001-{CHAPTER_ID}-EX-{number:03d}-SOLUTION", "original_solution_state": "queued_in_O001", "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0", "provenance": "separately_authored_not_Erdman"})
    if len(exercises) != 11 or [record.get("upstream_inline_hint_source_lines", []) for record in exercises] != expected_inline_lines or any(record["upstream_hint_ids"] for record in exercises):
        raise ValueError("Chapter 10 exercise-support topology changed")

    artifacts = artifact_records()
    corrections = correction_records()
    terms = terminology_records()
    qa = qa_records(formula_summary)
    relation_common = {"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "from_id": CHAPTER_ID}
    relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS})
    for number, artifact in enumerate(artifacts, 1):
        relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}", "relation_type": "has_artifact", "to_id": artifact["id"]})
    for number, artifact_id in enumerate(("ARTIFACT-FAOA-ID-CH10-TARGET-TEX", "ARTIFACT-FAOA-ID-CH10-STRUCTURAL-CHECKER", "ARTIFACT-FAOA-ID-CH10-TRANSLATION-REPORT"), 1):
        relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-TERM-EVIDENCE-{number:04d}", "relation_type": "terminology_evidence", "to_id": artifact_id, "evidence_scope": "all Chapter 10 terminology records and occurrences", "terminology_decision_sha256": TERM_DECISION_SHA})
    for number, event in enumerate(qa, 1):
        relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-QA-{number:04d}", "relation_type": "has_qa_event", "to_id": event["id"]})
    for number, correction in enumerate(corrections, 1):
        relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}", "relation_type": "documents_correction", "to_id": correction["id"]})
    if len(relations) != 523:
        raise ValueError(f"Chapter 10 relation invariant failed: {len(relations)}")

    for record in segment_records:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            del record[key]
    append_jsonl("semantic_units.jsonl", semantic_units)
    append_jsonl("segments.jsonl", segment_records)
    append_jsonl("relations.jsonl", relations)
    append_jsonl("formula_map.jsonl", formula_records)
    append_jsonl("exercise_support.jsonl", exercises)
    (BACKEND / "index_terms.csv").write_bytes(locked_prefix("index_terms.csv") + term_buffer.getvalue().encode("utf-8"))
    rewrite_units()
    append_jsonl("artifacts.jsonl", artifacts)
    append_jsonl("qa_events.jsonl", qa)
    append_jsonl("corrections.jsonl", corrections)
    append_jsonl("terminology.jsonl", terms)
    write_manifest()
    print(json.dumps({"anchors": len(source_anchors), "semantic_units": len(semantic_units), "segments": len(segment_records), "relations": len(relations), "labels": len(source_labels), "references": len(source_refs), "local_references": reference_counts["local"], "prior_references": reference_counts["admitted_prior_unit"], "cites": cite_key_count, "index_terms": len(source_terms), "defined_terms": len(source_df), "formula_map_records": len(formula_records), "exercises": len(exercises), "proofs": proof_count, "proof_hints": hint_relations, "citation_only_proofs": proof_roles["citation"], "corrections": len(corrections), "terminology_records": len(terms), "artifacts": len(artifacts), "qa_events": len(qa), "translation_state": "admitted", "qa_state": "passed", **formula_summary}, sort_keys=True))


if __name__ == "__main__":
    main()
