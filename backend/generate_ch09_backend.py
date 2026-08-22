#!/usr/bin/env python3
"""Append receipt-bound deterministic Chapter 9 records after Chapters 1--8."""

from __future__ import annotations

import collections
import csv
import hashlib
import io
import json
import os
import re
import subprocess
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
import check_ch09_translation as checker  # noqa: E402


common = checker.common
SOURCE_PATH = ROOT / "source" / "upstream" / "topvecspaces.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "topvecspaces-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH09"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
ADMISSION_QA_ID = "QA-CH09-ADMISSION-20260822"

SOURCE_SIZE = 35_022
SOURCE_LINES = 806
SOURCE_SHA = "62bc645c9d0972856913098d90d4baec7a8b0f470d4d380a880416f64cd5bce4"
TARGET_SIZE = 37_705
TARGET_LINES = 804
TARGET_SHA = "791868776a07f4c854f1c13d295da23a2559b88dcac48523fb0390e1e5330ee1"

MASTER_PATH = "source/id-ID/functional-analysis-id-through-ch09.tex"
MASTER_SIZE = 9_780
MASTER_LINES = 335
MASTER_SHA = "acba53fd01601ecd49516c01fb00e38af7bfcafbbbff0358a87dea864c591e3f"
FINAL_PDF_PATH = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf"
PDF_SIZE = 1_686_477
PDF_PAGES = 140
PDF_SHA = "99215ff5987f720600152da902cec8f521329692931a0dbf89e82ef2d4ff6076"

CHECKER_PATH = "qa/check_ch09_translation.py"
CHECKER_SIZE = 35_327
CHECKER_LINES = 820
CHECKER_SHA = "de952960ea7e48d4085162a9f6f5239a29daf810cc22bf933df4031d13618425"
REPORT_PATH = "qa/ch09-translation-report.json"
REPORT_SIZE = 7_931
REPORT_LINES = 347
REPORT_SHA = "0865aa5e64ea9ed5893925c3cf0986e1fc38c5f8d1b2f529ded71e06af5efd40"
CORRECTION_LEDGER_PATH = "provenance/SOURCE_CORRECTIONS_CH09.json"
CORRECTION_LEDGER_SIZE = 14_917
CORRECTION_LEDGER_LINES = 278
CORRECTION_LEDGER_SHA = "861b96347a0ab045861042c782209d284f2811f0eaa21c85200745d11de882e9"
PROSE_LEDGER_PATH = "provenance/SOURCE_CORRECTIONS.md"
PROSE_LEDGER_SIZE = 29_933
PROSE_LEDGER_LINES = 517
PROSE_LEDGER_SHA = "8854271d5a35eaddc3fc1141f7a2fc1e100796652a30fb52b257fb5b34c9d514"
RENDER_MANIFEST_PATH = "provenance/CH09_RENDER_MANIFEST.csv"
RENDER_MANIFEST_SIZE = 27_298
RENDER_MANIFEST_ROWS = 140
RENDER_MANIFEST_SHA = "add426dfd81f96fb8adc838d8173436d64ea3b2a165cdc1ff4a732c2a0f6fb2d"
CONTACT_SHEET_PATH = "provenance/CH09_CONTACT_SHEET.png"
CONTACT_SHEET_SIZE = 4_114_399
CONTACT_SHEET_SHA = "09b3bc4d70cc83d99cd376245c578e4c72fff6995e3392810e2d55e0302986dd"

AUDIT_PATH = "qa/CH09_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
AUDIT_SIZE = 6_825
AUDIT_LINES = 124
AUDIT_SHA = "d5b3adc00a6aafd7da5ce1b76dc8e2d25fe877f1e46824596a947cd20e2f8287"
# Filled from the final root-owned Chapter 9 admission receipt before generation.
RECEIPT_PATH = "provenance/CH09_BUILD_AND_QA_RECEIPT.md"
RECEIPT_SIZE = 9_128
RECEIPT_LINES = 166
RECEIPT_SHA = "08a103ce79f1f9406ddb877c01e8f921cde0f323fd6d1e731650eedbf1bd8794"

# Exact canonical Chapter 1--8 byte prefixes. Chapter 9 may only append.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (783_607, "9b559d11a0477e91484d453ec89ced8cd8feb2735d861670d6e7730de45ebc37"),
    "segments.jsonl": (890_177, "6c81fb6f6c5a71916b1ae8e9f1a3d654d7addbfff500910a935d23ae55f5ab25"),
    "relations.jsonl": (1_098_306, "443cd0a583907111371da68eac8c96115cca0cd4393cef0552a02353d3b9acf0"),
    "formula_map.jsonl": (3_720_317, "1c34c2302d282a0304ce6d5ed27838da5d344e85c6c9950eedd296b88de49457"),
    "exercise_support.jsonl": (18_758, "266724595e7418b01bdd981c40d23fa31ea985ac5c4d7c2adfd2919c426b78ce"),
    "index_terms.csv": (340_701, "a4e899a0108c7afd309eb10d7b26818add37c477c291db36f2a1409c31b1b75c"),
    "artifacts.jsonl": (38_750, "8cd2aed17bd05eb01acefdf8fd077bed0b84e3024f3507c8cd5861ed93c9c9d7"),
    "qa_events.jsonl": (56_661, "b50ec3b0b53f8b31c8fd65eea61192a5b1b22b4967cb5c35a4271d8379a3db7e"),
    "corrections.jsonl": (98_338, "513452e092ccc2719599c570e77b06cd32779baed7237f4a660f2313f1a1c270"),
    "terminology.jsonl": (84_238, "429b39ae517ca81be3c37d1323046e0fa6246f00bcc85b1e76e5e47f4df7a932"),
}
UNIT_PREFIX_LOCK = (10_536, "864e0e6a2973092b2b4533465e297203e1013e9e5d74009423da6b3c0fe4503f")
UNIT_SUFFIX_LOCK = (4_178, "1812c471ebe0120e85ce9b533bc7adc537778c216d6549fe852ec8d1056a967c")


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
        raise ValueError(f"{name} is shorter than its locked Chapter 1--8 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha or not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1--8 prefix changed")
    return prefix


def append_jsonl(name: str, records: list[dict]) -> None:
    suffix = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")
    (BACKEND / name).write_bytes(locked_prefix(name) + suffix)


def verify_evidence() -> None:
    locks = {
        "source/upstream/topvecspaces.tex": (SOURCE_SIZE, SOURCE_LINES, SOURCE_SHA),
        "source/id-ID/topvecspaces-id.tex": (TARGET_SIZE, TARGET_LINES, TARGET_SHA),
        MASTER_PATH: (MASTER_SIZE, MASTER_LINES, MASTER_SHA),
        CHECKER_PATH: (CHECKER_SIZE, CHECKER_LINES, CHECKER_SHA),
        REPORT_PATH: (REPORT_SIZE, REPORT_LINES, REPORT_SHA),
        CORRECTION_LEDGER_PATH: (
            CORRECTION_LEDGER_SIZE,
            CORRECTION_LEDGER_LINES,
            CORRECTION_LEDGER_SHA,
        ),
        PROSE_LEDGER_PATH: (PROSE_LEDGER_SIZE, PROSE_LEDGER_LINES, PROSE_LEDGER_SHA),
        RENDER_MANIFEST_PATH: (RENDER_MANIFEST_SIZE, RENDER_MANIFEST_ROWS + 1, RENDER_MANIFEST_SHA),
        AUDIT_PATH: (AUDIT_SIZE, AUDIT_LINES, AUDIT_SHA),
        RECEIPT_PATH: (RECEIPT_SIZE, RECEIPT_LINES, RECEIPT_SHA),
    }
    for relative_path, (size, lines, expected_sha) in locks.items():
        path = ROOT / relative_path
        if not path.is_file() or not size or not expected_sha:
            raise ValueError(f"Chapter 9 evidence boundary is not frozen: {relative_path}")
        data = path.read_bytes()
        if (len(data), len(data.splitlines()), sha(data)) != (size, lines, expected_sha):
            raise ValueError(f"Chapter 9 evidence changed: {relative_path}")
    for relative_path, size, expected_sha in (
        (FINAL_PDF_PATH, PDF_SIZE, PDF_SHA),
        (CONTACT_SHEET_PATH, CONTACT_SHEET_SIZE, CONTACT_SHEET_SHA),
    ):
        data = (ROOT / relative_path).read_bytes()
        if (len(data), sha(data)) != (size, expected_sha):
            raise ValueError(f"Chapter 9 binary evidence changed: {relative_path}")


def unit_boundaries() -> tuple[bytes, bytes]:
    lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    expected_ids = [f"FAOA-2015-CH{number:02d}" for number in range(1, 18)] + [
        "FAOA-ID-BRIDGE-CS"
    ]
    if len(lines) != len(expected_ids) or [json.loads(line)["id"] for line in lines] != expected_ids:
        raise ValueError("units.jsonl ordered unit closure changed")
    prefix = b"".join(lines[:8])
    middle = lines[8]
    suffix = b"".join(lines[9:])
    if (len(prefix), sha(prefix)) != UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--8 prefix changed")
    if (len(suffix), sha(suffix)) != UNIT_SUFFIX_LOCK:
        raise ValueError("units.jsonl Chapter 10--bridge suffix changed")
    if json.loads(middle).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 9 replacement boundary changed")
    return prefix, suffix


def chapter_nine_unit() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 9,
        "source_path": "topvecspaces.tex",
        "source_bytes": SOURCE_SIZE,
        "source_lines": SOURCE_LINES,
        "source_sha256": SOURCE_SHA,
        "source_title": "TOPOLOGICAL VECTOR SPACES",
        "target_path": "source/id-ID/topvecspaces-id.tex",
        "target_bytes": TARGET_SIZE,
        "target_lines": TARGET_LINES,
        "target_sha256": TARGET_SHA,
        "target_title": "Ruang Vektor Topologis",
        "course_role": "advanced_continuation",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 26,
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
    encoded = (json.dumps(chapter_nine_unit(), ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
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
        ("ARTIFACT-FAOA-ID-CH09-TARGET-TEX", "admitted_translation_source", "source/id-ID/topvecspaces-id.tex", TARGET_SIZE, TARGET_SHA),
        ("ARTIFACT-FAOA-ID-THROUGH-CH09-MASTER", "cumulative_TeX_master", MASTER_PATH, MASTER_SIZE, MASTER_SHA),
        ("ARTIFACT-FAOA-ID-THROUGH-CH09-PDF", "canonical_cumulative_reader_pdf", FINAL_PDF_PATH, PDF_SIZE, PDF_SHA),
        ("ARTIFACT-FAOA-ID-CH09-STRUCTURAL-CHECKER", "structural_math_language_checker", CHECKER_PATH, CHECKER_SIZE, CHECKER_SHA),
        ("ARTIFACT-FAOA-ID-CH09-TRANSLATION-REPORT", "classified_translation_report", REPORT_PATH, REPORT_SIZE, REPORT_SHA),
        ("ARTIFACT-FAOA-ID-CH09-CORRECTIONS-LEDGER", "chapter_source_corrections_ledger", CORRECTION_LEDGER_PATH, CORRECTION_LEDGER_SIZE, CORRECTION_LEDGER_SHA),
        ("ARTIFACT-FAOA-ID-CH09-PROSE-CORRECTIONS-LEDGER", "source_corrections_ledger", PROSE_LEDGER_PATH, PROSE_LEDGER_SIZE, PROSE_LEDGER_SHA),
        ("ARTIFACT-FAOA-ID-CH09-RENDER-MANIFEST", "visual_QA_render_manifest", RENDER_MANIFEST_PATH, RENDER_MANIFEST_SIZE, RENDER_MANIFEST_SHA),
        ("ARTIFACT-FAOA-ID-CH09-CONTACT-SHEET", "visual_QA_contact_sheet", CONTACT_SHEET_PATH, CONTACT_SHEET_SIZE, CONTACT_SHEET_SHA),
        ("ARTIFACT-FAOA-ID-CH09-VISUAL-ACCESSIBILITY-AUDIT", "visual_accessibility_audit", AUDIT_PATH, AUDIT_SIZE, AUDIT_SHA),
        ("ARTIFACT-FAOA-ID-CH09-QA-RECEIPT", "admission_receipt", RECEIPT_PATH, RECEIPT_SIZE, RECEIPT_SHA),
    ]
    records = [fields | {"id": record_id, "artifact_kind": kind, "path": path, "bytes": size, "sha256": digest} for record_id, kind, path, size, digest in specs]
    records[0] |= {"lines": TARGET_LINES, "locale": "id-ID"}
    records[1] |= {"lines": MASTER_LINES, "locale": "id-ID", "cumulative_through_unit_id": CHAPTER_ID}
    records[2] |= {"pages": PDF_PAGES, "page_size": "US Letter", "locale": "id-ID", "pdf_lang": "id-ID", "publication_state": "pending"}
    records[3] |= {"lines": CHECKER_LINES}
    records[4] |= {"lines": REPORT_LINES, "decision": "pass", "classified_math_edit_blocks": 13}
    records[5] |= {"lines": CORRECTION_LEDGER_LINES, "chapter_correction_count": 26, "mechanical_repairs": 17, "mathematical_repairs": 9}
    records[6] |= {"lines": PROSE_LEDGER_LINES, "chapter_correction_count": 26, "append_only_through_unit_id": CHAPTER_ID}
    records[7] |= {"rows": RENDER_MANIFEST_ROWS, "render_pages": PDF_PAGES, "uniform_pixel_dimensions": "1275x1650"}
    records[8] |= {"visual_pages": PDF_PAGES, "all_pages_inspected": True}
    records[9] |= {"lines": AUDIT_LINES, "visual_result": "pass", "accessibility_gate_result": "pass", "fully_accessible_pdf_claim": "fail", "tagged_pdf": False, "accessible_html_or_tagged_pdf_state": "pending"}
    records[10] |= {"lines": RECEIPT_LINES, "decision": "admitted"}
    return records


def correction_records() -> list[dict]:
    ledger = json.loads((ROOT / CORRECTION_LEDGER_PATH).read_text(encoding="utf-8"))
    if ledger.get("record_count") != 26 or len(ledger.get("records", [])) != 26:
        raise ValueError("Chapter 9 correction-ledger count changed")
    records = []
    for item in ledger["records"]:
        records.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "correction",
                "id": item["id"],
                "unit_id": CHAPTER_ID,
                "source_locator": f"topvecspaces.tex:{item['source_lines']['start']}--{item['source_lines']['end']}",
                "correction_type": item["classification"].lower(),
                "source_normalized_snippet_sha256": item["source_normalized_snippet_sha256"],
                "target_normalized_snippet_sha256": item["target_normalized_snippet_sha256"],
                "required_target_anchor": item["required_target_anchor"],
                "forbidden_source_anchor": item["forbidden_source_anchor"],
                "target_disposition": "corrected",
                "ledger_path": CORRECTION_LEDGER_PATH,
                "ledger_sha256": CORRECTION_LEDGER_SHA,
                **admission_fields(),
                "qa_state": "passed",
                "upstream_report": "deferred_until_complete_and_separately_authorized",
            }
        )
    return records


EXISTING_TERM_IDS = {"converges": "TERM-CONVERGES", "bounded": "TERM-BOUNDED"}
NEW_TERM_SPECS: list[tuple[str, str, str]] = [
    ("TERM-BALANCED", "balanced", "seimbang"),
    ("TERM-CIRCLED", "circled", "melingkar"),
    ("TERM-BALANCED-HULL", "balanced hull", "selubung seimbang"),
    ("TERM-ABSORBS", "absorbs", "menyerap"),
    ("TERM-ABSORBING", "absorbing", "menyerap"),
    ("TERM-RADIAL", "radial", "radial"),
    ("TERM-FILTER", "filter", "filter"),
    ("TERM-NEIGHBORHOOD-FILTER", "neighborhood filter", "filter lingkungan"),
    ("TERM-FILTERBASE", "filterbase", "basis filter"),
    ("TERM-FILTERBASE-FOR", "filterbase for", "basis filter bagi"),
    ("TERM-FILTER-GENERATED-BY", "filter generated by", "dibangkitkan oleh"),
    ("TERM-GENERATED-BY", "generated by", "dibangkitkan oleh"),
    ("TERM-BASED-ON", "based on", "didasarkan pada"),
    ("TERM-COMPATIBLE", "compatible", "kompatibel"),
    ("TERM-TOPOLOGICAL-VECTOR-SPACE", "topological vector space", "ruang vektor topologis"),
    ("TERM-TRANSLATION", "translation", "translasi"),
    ("TERM-LOCAL-BASE", "local base", "basis lokal"),
    ("TERM-UNIFORM-CONVERGENCE-ON-COMPACT-SETS-TOPOLOGY", "topology of uniform convergence on compact sets", "topologi konvergensi seragam pada himpunan-himpunan kompak"),
    ("TERM-REGULAR", "regular", "regular"),
    ("TERM-CAUCHY-FILTER", "Cauchy filter", "filter Cauchy"),
    ("TERM-COMPLETE", "complete", "lengkap"),
    ("TERM-QUOTIENT-TOPOLOGY", "quotient topology", "topologi hasil bagi"),
    ("TERM-LOCALLY-CONVEX", "locally convex", "konveks lokal"),
    ("TERM-LOCALLY-CONVEX-SPACE", "locally convex space", "ruang konveks lokal"),
    ("TERM-OPEN-SEMIBALL", "open semiball", "semibola terbuka"),
    ("TERM-CLOSED-SEMIBALL", "closed semiball", "semibola tertutup"),
    ("TERM-MINKOWSKI-FUNCTIONAL", "Minkowski functional", "fungsional Minkowski"),
    ("TERM-SEPARATING", "separating", "pemisah"),
    ("TERM-METRIZABLE", "metrizable", "dapat dimetrikkan"),
    ("TERM-TRANSLATION-INVARIANT", "translation invariant", "invarian terhadap translasi"),
    ("TERM-FRECHET-SPACE", "Fr\\'echet space", "ruang Fr\\'echet"),
    ("TERM-SMOOTH", "smooth", "mulus"),
    ("TERM-TEST-FUNCTIONS", "test functions", "fungsi uji"),
    ("TERM-MULTI-INDEX", "multi-index", "multi-indeks"),
    ("TERM-ORDER", "order", "orde"),
    ("TERM-SCHWARTZ-SPACE", "Schwartz space", "ruang Schwartz"),
]


def term_id_map() -> dict[str, str]:
    mapping = EXISTING_TERM_IDS | {source: stable_id for stable_id, source, _ in NEW_TERM_SPECS}
    if len(mapping) != 38:
        raise ValueError("Chapter 9 distinct defined-term inventory changed")
    return mapping


def terminology_records() -> list[dict]:
    return [
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "term",
            "id": stable_id,
            "source_term": source,
            "locale": "id-ID",
            "preferred": preferred,
            "variants": [],
            "rejected": [],
            "scope": "topological vector spaces, local convexity, seminorms, and Frechet spaces",
            "evidence": f"{CHAPTER_ID} target; {CHECKER_PATH}; {REPORT_PATH}",
        }
        for stable_id, source, preferred in NEW_TERM_SPECS
    ]


FORMULA_CORRECTIONS = {
    139: f"{CHAPTER_ID}-CORR-003",
    **{number: f"{CHAPTER_ID}-CORR-006" for number in range(186, 190)},
    293: f"{CHAPTER_ID}-CORR-020",
    439: f"{CHAPTER_ID}-CORR-021",
    440: f"{CHAPTER_ID}-CORR-021",
    459: f"{CHAPTER_ID}-CORR-023",
    470: f"{CHAPTER_ID}-CORR-024",
    473: f"{CHAPTER_ID}-CORR-024",
    477: f"{CHAPTER_ID}-CORR-010",
    489: f"{CHAPTER_ID}-CORR-011",
    500: f"{CHAPTER_ID}-CORR-025",
    501: f"{CHAPTER_ID}-CORR-025",
    586: f"{CHAPTER_ID}-CORR-015",
    592: f"{CHAPTER_ID}-CORR-016",
    595: f"{CHAPTER_ID}-CORR-026",
}
TARGET_ONLY_FORMULAS = {440, 500, 501}


def build_math_pairs(source: str, target: str) -> tuple[list[dict], dict[str, object]]:
    source_math = ch03_math.extract_math(source, SOURCE_ENCODING)
    target_math = ch03_math.extract_math(target, TARGET_ENCODING)
    if (len(source_math), len(target_math)) != (603, 606):
        raise ValueError("Chapter 9 math-surface count changed")
    source_keys = [ch03_math.math_key(record["normalized"]) for record in source_math]
    target_keys = [ch03_math.math_key(record["normalized"]) for record in target_math]
    mapping: list[list[int] | None] = [None] * len(target_math)
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, source_keys, target_keys, autojunk=False).get_opcodes():
        if tag == "equal":
            for source_index, target_index in zip(range(i1, i2), range(j1, j2), strict=True):
                mapping[target_index] = [source_index]
        elif tag == "replace":
            paired = min(i2 - i1, j2 - j1)
            for offset in range(paired):
                mapping[j1 + offset] = [i1 + offset]
            for target_index in range(j1 + paired, j2):
                mapping[target_index] = []
        elif tag == "insert":
            for target_index in range(j1, j2):
                mapping[target_index] = []
        else:
            raise ValueError(f"unexpected Chapter 9 math opcode: {tag}")
    if any(value is None for value in mapping):
        raise ValueError("Chapter 9 target formula coverage is incomplete")
    complete = [value for value in mapping if value is not None]
    if sorted(index for group in complete for index in group) != list(range(len(source_math))):
        raise ValueError("Chapter 9 source formula coverage is incomplete")
    records: list[dict] = []
    counts: collections.Counter[str] = collections.Counter()
    for number, (source_indexes, target_record) in enumerate(zip(complete, target_math, strict=True), 1):
        source_records = [source_math[index] for index in source_indexes]
        exact = len(source_records) == 1 and source_records[0]["normalized"] == target_record["normalized"]
        key_equal = len(source_records) == 1 and source_keys[source_indexes[0]] == target_keys[number - 1]
        if exact:
            alignment = "preserved_exact_after_text_aware_whitespace_normalization"
        elif key_equal and number not in FORMULA_CORRECTIONS:
            alignment = "preserved_math_key_after_localized_text_substitution"
        elif number in TARGET_ONLY_FORMULAS:
            alignment = "reviewed_target_only_source_correction"
        elif number in FORMULA_CORRECTIONS:
            alignment = "reviewed_source_correction"
        else:
            raise ValueError(f"unexpected Chapter 9 formula delta at target {number}")
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
        if alignment == "preserved_math_key_after_localized_text_substitution":
            record |= {
                "sequence_opcode": "localize_text",
                "delta_class": "localization_inside_math_text",
                "correction_disposition": "not_a_source_correction",
                "qa_state": "passed",
            }
        elif not exact:
            record |= {
                "sequence_opcode": "insert" if not source_indexes else "replace",
                "delta_class": "source_correction",
                "correction_id": FORMULA_CORRECTIONS[number],
                "correction_disposition": "corrected",
                "review_witness": REPORT_PATH,
                "qa_state": "passed",
            }
        records.append(record)
    expected = {
        "preserved_exact_after_text_aware_whitespace_normalization": 585,
        "preserved_math_key_after_localized_text_substitution": 3,
        "reviewed_source_correction": 15,
        "reviewed_target_only_source_correction": 3,
    }
    if dict(counts) != expected:
        raise ValueError(f"Chapter 9 formula alignment counts changed: {dict(counts)}")
    return records, {
        "source_math_surfaces": 603,
        "target_math_surfaces": 606,
        "exact_normalized_alignments": 585,
        "math_key_preserving_alignments": 588,
        "localization_only_math_text_substitutions": 3,
        "reviewed_source_correction_maps": 18,
        "target_only_source_corrections": 3,
        "formula_map_records": 606,
    }


def qa_records(formula_summary: dict[str, object]) -> list[dict]:
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "timestamp": "2026-08-22",
        "responsible_workflow": "Codex",
        **admission_fields(),
    }
    specs = [
        ("QA-CH09-STRUCTURAL-20260822", "unit_structural", CHECKER_PATH, CHECKER_SHA),
        ("QA-CH09-MATH-20260822", "unit_mathematical", REPORT_PATH, REPORT_SHA),
        ("QA-CH09-LANGUAGE-20260822", "unit_language", REPORT_PATH, REPORT_SHA),
        ("QA-CH09-BUILD-20260822", "cumulative_build", FINAL_PDF_PATH, PDF_SHA),
        ("QA-CH09-VISUAL-20260822", "cumulative_visual", AUDIT_PATH, AUDIT_SHA),
        ("QA-CH09-ACCESSIBILITY-20260822", "cumulative_accessibility", AUDIT_PATH, AUDIT_SHA),
        ("QA-CH09-RIGHTS-20260822", "unit_rights_privacy", CHECKER_PATH, CHECKER_SHA),
        (ADMISSION_QA_ID, "unit_admission", RECEIPT_PATH, RECEIPT_SHA),
    ]
    records = [fields | {"id": record_id, "qa_type": kind, "result": "pass", "witness": witness, "witness_sha256": witness_sha} for record_id, kind, witness, witness_sha in specs]
    records[0] |= {"semantic_anchors": 126, "semantic_units": 125, "segments": 137, "sections": 6, "labels": 9, "references": 7, "citations": 5, "index_terms": 91, "defined_terms": 40, "exercise_environments": 1, "proof_environments": 9, "proof_hints": 5}
    records[1] |= formula_summary | {"classified_math_edit_blocks": 13, "unexplained_deltas": 0, "extractor": "backend/ch03_math.py", "extractor_sha256": "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3"}
    records[2] |= {"severity_counts": {"P1": 0, "P2": 0, "P3": 0}, "unintended_english_prose": 0, "placeholders": 0, "terminology_reconciled": True}
    records[3] |= {"master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH09-MASTER", "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH09-PDF", "pages": PDF_PAGES}
    records[4] |= {"pages_rendered": PDF_PAGES, "pages_inspected": PDF_PAGES, "render_manifest_sha256": RENDER_MANIFEST_SHA, "contact_sheet_sha256": CONTACT_SHEET_SHA, "visual_defects": 0}
    records[5] |= {"tagged_pdf": False, "fully_accessible_pdf_claim": False, "semantic_accessibility_state": "remediation_required", "accessible_html_or_tagged_pdf_state": "pending", "admission_blocker_for_chapter_boundary": False}
    records[6] |= {"rights_id": RIGHTS, "attribution_change_notice_sharealike_nonendorsement": "present", "private_control_paths_absent_from_public_artifacts": True, "credential_or_token_residue": 0}
    records[7] |= {"decision": "admitted", "source_sha256": SOURCE_SHA, "target_sha256": TARGET_SHA, "build_master_sha256": MASTER_SHA, "artifact_sha256": PDF_SHA, "correction_ledger_sha256": CORRECTION_LEDGER_SHA, "required_admission_gate_results": {kind: "pass" for kind in ("unit_structural", "unit_mathematical", "unit_language", "cumulative_build", "cumulative_visual", "cumulative_accessibility", "unit_rights_privacy", "admission_receipt")}, "all_required_admission_gates": "pass", "publication_state": "pending"}
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
    checker_run = subprocess.run([sys.executable, str(ROOT / CHECKER_PATH)], cwd=ROOT, check=True, capture_output=True, text=True)
    checker_result = json.loads(checker_run.stdout)
    if checker_result.get("result") != "pass":
        raise ValueError("Chapter 9 checker did not return its frozen pass result")

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if len(source_anchors) != 126 or [ch01.anchor_signature(anchor) for anchor in source_anchors] != [ch01.anchor_signature(anchor) for anchor in target_anchors]:
        raise ValueError("Chapter 9 semantic anchor topology differs")
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 9 or [item["argument"] for item in source_labels] != [item["argument"] for item in target_labels]:
        raise ValueError("Chapter 9 label sequence differs")

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
            "source_path": "source/upstream/topvecspaces.tex", "source_line_start": source_fragment["line_start"], "source_line_end": source_fragment["line_end"], "source_fragment_sha256": source_fragment["sha256"],
            "target_path": "source/id-ID/topvecspaces-id.tex", "target_line_start": target_fragment["line_start"], "target_line_end": target_fragment["line_end"], "target_fragment_sha256": target_fragment["sha256"],
            "source_local_id": source_anchor.get("label"), "source_title_tex": source_anchor.get("title"), "target_title_tex": target_anchor.get("title"),
            "locale": "id-ID", "translation_state": "admitted", "qa_state": "passed", "rights_id": RIGHTS,
        })
        relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-CONTAINS-{len(semantic_units):04d}", "relation_type": "contains", "from_id": parent_id, "to_id": unit_id})
    if (len(semantic_units), section_number, node_number) != (125, 6, 119):
        raise ValueError("Chapter 9 semantic-unit topology invariant failed")

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
    if len(source_parts) != 137 or len(target_parts) != 137:
        raise ValueError("Chapter 9 segment topology differs")

    for number, (source_part, target_part) in enumerate(zip(source_parts, target_parts, strict=True), 1):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if (role, parent_id) != (target_role, target_parent):
            raise ValueError("Chapter 9 source/target segment roles differ")
        source_fragment = ch01.fragment(source, source_start, source_end, SOURCE_ENCODING)
        target_fragment = ch01.fragment(target, target_start, target_end, TARGET_ENCODING)
        segment_id = f"{CHAPTER_ID}-SEG-{number:04d}"
        segment_records.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "segment", "id": segment_id, "parent_id": parent_id, "order": number, "segment_role": role,
            "source_path": "source/upstream/topvecspaces.tex", "source_line_start": source_fragment["line_start"], "source_line_end": source_fragment["line_end"], "source_bytes": source_fragment["bytes"], "source_sha256": source_fragment["sha256"],
            "target_path": "source/id-ID/topvecspaces-id.tex", "target_line_start": target_fragment["line_start"], "target_line_end": target_fragment["line_end"], "target_bytes": target_fragment["bytes"], "target_sha256": target_fragment["sha256"],
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

    source_refs = common.macro(source, "ref")
    target_refs = common.macro(target, "ref")
    if len(source_refs) != 7 or [item["argument"] for item in source_refs] != [item["argument"] for item in target_refs]:
        raise ValueError("Chapter 9 reference sequence differs")
    prior_labels = prior_label_map()
    reference_counts: collections.Counter[str] = collections.Counter()
    for number, occurrence in enumerate(source_refs, 1):
        label = occurrence["argument"]
        if label in local_label_map:
            to_id, resolution = local_label_map[label], "local"
        elif label in prior_labels:
            to_id, resolution = prior_labels[label], "admitted_prior_unit"
        else:
            raise ValueError(f"unresolved Chapter 9 reference: {label}")
        reference_counts[resolution] += 1
        relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}", "relation_type": "xref", "from_id": ch01.containing_segment(segment_records, occurrence["start"], "source"), "to_id": to_id, "source_local_id": label, "resolution": resolution, "target_surface": "ref"})
    if dict(reference_counts) != {"local": 7}:
        raise ValueError(f"Chapter 9 reference closure changed: {dict(reference_counts)}")
    if common.macro(source, "eqref") or common.macro(target, "eqref") or re.search(r"\\futurexref\{", ch01.active_same_length(target)):
        raise ValueError("Chapter 9 unexpectedly contains eqref or futurexref")

    source_cites = common.macro(source, "cite")
    target_cites = common.macro(target, "cite")
    if len(source_cites) != 5 or [item["argument"] for item in source_cites] != [item["argument"] for item in target_cites]:
        raise ValueError("Chapter 9 citation sequence differs")
    cite_key_count = 0
    for occurrence_number, occurrence in enumerate(source_cites, 1):
        for key in [item.strip() for item in occurrence["argument"].split(",")]:
            cite_key_count += 1
            relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-CITE-{occurrence_number:04d}-{key}", "relation_type": "cites", "from_id": ch01.containing_segment(segment_records, occurrence["start"], "source"), "to_id": f"ERDMAN-FAOA-BIB-{key}", "source_local_id": key})

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
                raise ValueError("Chapter 9 proof hint lacks preceding statement")
            hint_relations += 1
            hint_ids_by_statement[previous_statement].append(record["id"])
            relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-HINTS-{hint_relations:04d}", "relation_type": "hints", "from_id": record["id"], "to_id": previous_statement})
    if (proof_count, hint_relations) != (9, 5):
        raise ValueError("Chapter 9 proof-role topology changed")

    source_df = common.macro(source, "df")
    target_df = common.macro(target, "df")
    if len(source_df) != 40 or tuple(item["argument"] for item in target_df) != checker.EXPECTED_TARGET_DEFINED_TERMS:
        raise ValueError("Chapter 9 defined-term pairing changed")
    term_ids = term_id_map()
    if set(term_ids) != {item["argument"] for item in source_df}:
        raise ValueError("Chapter 9 distinct defined-term closure changed")
    for number, (source_term, target_term) in enumerate(zip(source_df, target_df, strict=True), 1):
        relations.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}", "relation_type": "uses_term", "from_id": ch01.containing_segment(segment_records, source_term["start"], "source"), "to_id": term_ids[source_term["argument"]], "source_term_tex": source_term["argument"], "target_term_tex": target_term["argument"], "locale": "id-ID"})

    source_terms = common.macro(source, "index")
    target_terms = common.macro(target, "index")
    if len(source_terms) != 91 or len(target_terms) != 91 or [common.index_signature(item["argument"]) for item in source_terms] != [common.index_signature(item["argument"]) for item in target_terms]:
        raise ValueError("Chapter 9 index-term alignment changed")
    term_buffer = io.StringIO(newline="")
    term_writer = csv.writer(term_buffer, lineterminator="\n")
    for number, (source_term, target_term) in enumerate(zip(source_terms, target_terms, strict=True), 1):
        term_writer.writerow([f"{CHAPTER_ID}-TERM-OCC-{number:04d}", ch01.containing_segment(segment_records, source_term["start"], "source"), number, source_term["line"], source_term["argument"], target_term["line"], target_term["argument"], sha(source_term["argument"].encode(SOURCE_ENCODING)), sha(target_term["argument"].encode(TARGET_ENCODING)), "id-ID"])

    formula_records, formula_summary = build_math_pairs(source, target)
    exercises: list[dict] = []
    for record in semantic_units:
        if record["unit_kind"] != "exer":
            continue
        number = len(exercises) + 1
        start, end = anchor_bounds[record["id"]]
        fragment = source[start:end]
        inline_lines = [source.count("\n", 0, start + match.start()) + 1 for match in re.finditer(r"\\emph\{Hint\.\}", fragment)]
        exercises.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "exercise_support", "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-{number:03d}", "exercise_unit_id": record["id"], "source_exercise_order": number, "upstream_hint_ids": hint_ids_by_statement.get(record["id"], []), "upstream_inline_hint_state": "present" if inline_lines else "absent", **({"upstream_inline_hint_source_lines": inline_lines} if inline_lines else {}), "upstream_answer_state": "absent", "upstream_solution_state": "absent", "original_solution_id": f"O001-{CHAPTER_ID}-EX-{number:03d}-SOLUTION", "original_solution_state": "queued_in_O001", "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0", "provenance": "separately_authored_not_Erdman"})
    if len(exercises) != 1 or exercises[0]["upstream_inline_hint_state"] != "absent" or exercises[0]["upstream_hint_ids"]:
        raise ValueError("Chapter 9 exercise-support topology changed")

    artifacts = artifact_records()
    corrections = correction_records()
    terms = terminology_records()
    qa = qa_records(formula_summary)
    relation_common = {"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "from_id": CHAPTER_ID}
    relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS})
    for number, artifact in enumerate(artifacts, 1):
        relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}", "relation_type": "has_artifact", "to_id": artifact["id"]})
    for number, artifact_id in enumerate(("ARTIFACT-FAOA-ID-CH09-TARGET-TEX", "ARTIFACT-FAOA-ID-CH09-STRUCTURAL-CHECKER", "ARTIFACT-FAOA-ID-CH09-TRANSLATION-REPORT"), 1):
        relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-TERM-EVIDENCE-{number:04d}", "relation_type": "terminology_evidence", "to_id": artifact_id, "evidence_scope": "all Chapter 9 terminology records and occurrences"})
    for number, event in enumerate(qa, 1):
        relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-QA-{number:04d}", "relation_type": "has_qa_event", "to_id": event["id"]})
    for number, correction in enumerate(corrections, 1):
        relations.append(relation_common | {"id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}", "relation_type": "documents_correction", "to_id": correction["id"]})
    if len(relations) != 513:
        raise ValueError(f"Chapter 9 relation invariant failed: {len(relations)}")

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
    print(json.dumps({"anchors": len(source_anchors), "semantic_units": len(semantic_units), "segments": len(segment_records), "relations": len(relations), "labels": len(source_labels), "references": len(source_refs), "local_references": reference_counts["local"], "cites": cite_key_count, "index_terms": len(source_terms), "defined_terms": len(source_df), "formula_map_records": len(formula_records), "exercises": len(exercises), "proofs": proof_count, "proof_hints": hint_relations, "corrections": len(corrections), "terminology_records": len(terms), "artifacts": len(artifacts), "qa_events": len(qa), "translation_state": "admitted", "qa_state": "passed", **formula_summary}, sort_keys=True))


if __name__ == "__main__":
    main()
