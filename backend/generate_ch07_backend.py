#!/usr/bin/env python3
"""Append deterministic Chapter 7 backend records after locked Chapters 1--6.

Chapter 7 has a frozen complete translation, append-only source-correction
ledger, passed reader evidence, and an exact admission receipt.  This generator
records the admitted locale-neutral source/target topology while preserving the
honest edition-level accessibility and publication limitations.
"""

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
import check_ch06_translation as ch06check  # noqa: E402


common = ch06check.common
SOURCE_PATH = ROOT / "source" / "upstream" / "compact_operators.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "compact_operators-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH07"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
ADMISSION_QA_ID = "QA-CH07-ADMISSION-20260822"

SOURCE_SIZE = 21_755
SOURCE_LINES = 517
SOURCE_SHA = "a1f55b061f526f3e536e5a812f073781777b6f990b662f4a1dba07475152d663"
TARGET_SIZE = 22_735
TARGET_LINES = 517
TARGET_SHA = "8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a"

MASTER_PATH = "source/id-ID/functional-analysis-id-through-ch07.tex"
MASTER_SIZE = 9_691
MASTER_LINES = 333
MASTER_SHA = "c639253fab59df7b51002058b414d8d64c92d77f12e95e88068decafd0d138b9"
FINAL_PDF_PATH = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-7.pdf"
PDF_SIZE = 1_530_677
PDF_PAGES = 121
PDF_SHA = "a7ddaef324bd356d258cb47195f524e027ba54a696cb8d38a8358bb8d0a2d7ff"
CHECKER_PATH = "qa/check_ch07_translation.py"
CHECKER_SIZE = 21_468
CHECKER_LINES = 535
CHECKER_SHA = "392d2842c99fd1a54faaf671b2256ef41a896335edd2c2fe5d973f13d63e1363"
RENDER_MANIFEST_PATH = "provenance/CH07_RENDER_MANIFEST.csv"
RENDER_MANIFEST_SIZE = 23_608
RENDER_MANIFEST_ROWS = 121
RENDER_MANIFEST_SHA = "b2fa453d7b96b51826aadddf2e8151144d6deae1d093dfa34841ab589ef464ed"
CONTACT_SHEET_PATH = "provenance/CH07_CONTACT_SHEET.png"
CONTACT_SHEET_SIZE = 3_549_427
CONTACT_SHEET_SHA = "b52f348c29cdaa1cebd87c280ac0c01fad919e72a8f595ba2c48cb78ac283564"
AUDIT_PATH = "qa/CH07_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
AUDIT_SIZE = 6_182
AUDIT_LINES = 110
AUDIT_SHA = "c71c7b9bce1133d7c10bab8cf2e3bb4c310a8ceb701672ced87bbd6a412012f5"
RECEIPT_PATH = "provenance/CH07_BUILD_AND_QA_RECEIPT.md"
RECEIPT_SIZE = 9_855
RECEIPT_LINES = 181
RECEIPT_SHA = "8c9e7afa90c27a748de6b2f44c1725ed467ba7f8e4f3960a0009459a25b0b525"

LEDGER_PATH = "provenance/SOURCE_CORRECTIONS.md"
LEDGER_SIZE = 23_661
LEDGER_SHA = "285f20b012926002bb9085dab91b06cee3e0808bf7881b598a276c643ad8eea7"
LEDGER_PRIOR_SIZE = 20_716
LEDGER_PRIOR_SHA = "7de8a5892b865af84c9f5d1d4c37ec6b3112b3e099685dae243108006dc94b01"
LEDGER_SECTION_SIZE = 2_945
LEDGER_SECTION_SHA = "9f262ed1003bf8824a0485c68caf117170458fb27651491a86d7b911797a4c6d"

PUBLIC_EVIDENCE_LOCKS = {
    "source/id-ID/compact_operators-id.tex": (TARGET_SIZE, TARGET_SHA),
    MASTER_PATH: (MASTER_SIZE, MASTER_SHA),
    FINAL_PDF_PATH: (PDF_SIZE, PDF_SHA),
    CHECKER_PATH: (CHECKER_SIZE, CHECKER_SHA),
    RENDER_MANIFEST_PATH: (RENDER_MANIFEST_SIZE, RENDER_MANIFEST_SHA),
    CONTACT_SHEET_PATH: (CONTACT_SHEET_SIZE, CONTACT_SHEET_SHA),
    AUDIT_PATH: (AUDIT_SIZE, AUDIT_SHA),
    RECEIPT_PATH: (RECEIPT_SIZE, RECEIPT_SHA),
}

# Exact canonical Chapter 1--6 byte prefixes.  Chapter 7 may only append.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (650_244, "2fa15e508b1aa18e707484b7c5109b643900dcc8f59f4dae1e8543b0159c4ed2"),
    "segments.jsonl": (747_490, "7f65fe4d47ffdbb902235ad1fbb8c574c51b8f2154ab8e02564cf1a00aba39d3"),
    "relations.jsonl": (905_248, "6716f53995ec4da47e68bef0dde091820f9968e7a486bdda15a924fe91870e7e"),
    "formula_map.jsonl": (3_243_961, "82e264d01ce8174973eb19b2079ac69ed613af36984ed967beb0ab5ca2f9b0fe"),
    "exercise_support.jsonl": (17_083, "f13f4e3f23495100508057b19e4e49fc6674f3a7126a13e50d804165d3a284f1"),
    "index_terms.csv": (298_201, "5a3630fc62e82ef04ca2c6ae58b500b1881b0b607c5c5540ca30ccda1e3080fe"),
    "artifacts.jsonl": (24_928, "a09bfa4b671574a140652d5ae5a7a67d9b63a50622a71bc72347c00e4412e199"),
    "qa_events.jsonl": (38_259, "9e65e57fdbcc2b566c63bfc8c2683d3b08418c9c36512d1ccf0f887c4daf50d6"),
    "corrections.jsonl": (80_587, "ad8e7a2d8837f09182ccedc5a875bef0b7285b5fa3e6ddab64c8252b6cbe37b4"),
    "terminology.jsonl": (71_021, "e82539683deb4d4ab46c5f0e1f3613ede9ba9cc7fb4b0700f08673108b2f653a"),
}
UNIT_PREFIX_LOCK = (
    7_621,
    "30d340d0d1070d18d8999ab929c36234b89ef7b762e04b185631e4ad3d0f6d0f",
)
UNIT_SUFFIX_LOCK = (
    6_095,
    "1de61dcc0f8e2de97feda39ddf8d56dd4f3b9460dfc01150735b4ac61bcc36a2",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def locked_prefix(name: str) -> bytes:
    size, expected_sha = PREFIX_LOCKS[name]
    data = (BACKEND / name).read_bytes()
    if len(data) < size:
        raise ValueError(f"{name} is shorter than its locked Chapter 1--6 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha or not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1--6 prefix changed")
    return prefix


def append_jsonl(name: str, records: list[dict]) -> None:
    suffix = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")
    (BACKEND / name).write_bytes(locked_prefix(name) + suffix)


def verify_evidence() -> None:
    source = SOURCE_PATH.read_bytes()
    target = TARGET_PATH.read_bytes()
    if (len(source), len(source.splitlines()), sha(source)) != (
        SOURCE_SIZE,
        SOURCE_LINES,
        SOURCE_SHA,
    ):
        raise ValueError("Chapter 7 source authority changed")
    if (len(target), len(target.splitlines()), sha(target)) != (
        TARGET_SIZE,
        TARGET_LINES,
        TARGET_SHA,
    ):
        raise ValueError("Chapter 7 target candidate changed")
    for relative_path, (size, expected_sha) in PUBLIC_EVIDENCE_LOCKS.items():
        data = (ROOT / relative_path).read_bytes()
        if (len(data), sha(data)) != (size, expected_sha):
            raise ValueError(f"Chapter 7 evidence changed: {relative_path}")
    if len((ROOT / MASTER_PATH).read_bytes().splitlines()) != MASTER_LINES:
        raise ValueError("Chapter 7 cumulative master line count changed")
    if len((ROOT / CHECKER_PATH).read_bytes().splitlines()) != CHECKER_LINES:
        raise ValueError("Chapter 7 checker line count changed")
    if len((ROOT / AUDIT_PATH).read_bytes().splitlines()) != AUDIT_LINES:
        raise ValueError("Chapter 7 audit line count changed")
    receipt = (ROOT / RECEIPT_PATH).read_bytes()
    if len(receipt.splitlines()) != RECEIPT_LINES or receipt.count(b"\n") != RECEIPT_LINES:
        raise ValueError("Chapter 7 admission receipt line count changed")
    if len((ROOT / RENDER_MANIFEST_PATH).read_bytes().splitlines()) != RENDER_MANIFEST_ROWS + 1:
        raise ValueError("Chapter 7 render-manifest row count changed")
    ledger = (ROOT / LEDGER_PATH).read_bytes()
    if len(ledger) < LEDGER_SIZE or sha(ledger[:LEDGER_SIZE]) != LEDGER_SHA:
        raise ValueError("Chapter 7 correction-ledger prefix changed")
    if sha(ledger[:LEDGER_PRIOR_SIZE]) != LEDGER_PRIOR_SHA:
        raise ValueError("Chapter 1--6 correction-ledger prefix changed")
    section = ledger[LEDGER_PRIOR_SIZE:LEDGER_SIZE]
    if (
        len(section) != LEDGER_SECTION_SIZE
        or not section.startswith(b"\n## Chapter 7\n")
        or sha(section) != LEDGER_SECTION_SHA
    ):
        raise ValueError("Chapter 7 correction-ledger section changed")


def unit_boundaries() -> tuple[bytes, bytes]:
    lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    expected_ids = [f"FAOA-2015-CH{number:02d}" for number in range(1, 18)] + [
        "FAOA-ID-BRIDGE-CS"
    ]
    if len(lines) != len(expected_ids) or any(not line.endswith(b"\n") for line in lines):
        raise ValueError("units.jsonl ordered unit closure changed")
    if [json.loads(line)["id"] for line in lines] != expected_ids:
        raise ValueError("units.jsonl ordered unit IDs changed")
    prefix = b"".join(lines[:6])
    middle = lines[6]
    suffix = b"".join(lines[7:])
    if (len(prefix), sha(prefix)) != UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--6 prefix changed")
    if (len(suffix), sha(suffix)) != UNIT_SUFFIX_LOCK:
        raise ValueError("units.jsonl Chapter 8--bridge suffix changed")
    if json.loads(middle).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 7 replacement boundary changed")
    return prefix, suffix


def chapter_seven_unit() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 7,
        "source_path": "compact_operators.tex",
        "source_bytes": SOURCE_SIZE,
        "source_lines": SOURCE_LINES,
        "source_sha256": SOURCE_SHA,
        "source_title": "COMPACT OPERATORS",
        "target_path": "source/id-ID/compact_operators-id.tex",
        "target_bytes": TARGET_SIZE,
        "target_lines": TARGET_LINES,
        "target_sha256": TARGET_SHA,
        "target_title": "Operator Kompak",
        "course_role": "d20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 11,
        "build_master_path": MASTER_PATH,
        "build_master_bytes": MASTER_SIZE,
        "build_master_lines": MASTER_LINES,
        "build_master_sha256": MASTER_SHA,
        "artifact_path": FINAL_PDF_PATH,
        "artifact_bytes": PDF_SIZE,
        "artifact_pages": PDF_PAGES,
        "artifact_sha256": PDF_SHA,
        "artifact_state": "canonical_output_copy_present_and_fixed_path_gate_passed",
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_path": RECEIPT_PATH,
        "receipt_sha256": RECEIPT_SHA,
        "publication_state": "pending",
        "rights_id": RIGHTS,
    }


def rewrite_units() -> None:
    prefix, suffix = unit_boundaries()
    encoded = (
        json.dumps(chapter_seven_unit(), ensure_ascii=False, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    (BACKEND / "units.jsonl").write_bytes(prefix + encoded + suffix)


def artifact_records() -> list[dict]:
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "artifact",
        "unit_id": CHAPTER_ID,
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_path": RECEIPT_PATH,
        "receipt_sha256": RECEIPT_SHA,
    }
    return [
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH07-TARGET-TEX",
            "artifact_kind": "admitted_translation_source",
            "path": "source/id-ID/compact_operators-id.tex",
            "bytes": TARGET_SIZE,
            "lines": TARGET_LINES,
            "sha256": TARGET_SHA,
            "locale": "id-ID",
            "admission_state": "admitted",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH07-MASTER",
            "artifact_kind": "cumulative_TeX_master",
            "path": MASTER_PATH,
            "bytes": MASTER_SIZE,
            "lines": MASTER_LINES,
            "sha256": MASTER_SHA,
            "cumulative_through_unit_id": CHAPTER_ID,
            "locale": "id-ID",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH07-PDF",
            "artifact_kind": "canonical_cumulative_reader_pdf",
            "path": FINAL_PDF_PATH,
            "bytes": PDF_SIZE,
            "sha256": PDF_SHA,
            "pages": PDF_PAGES,
            "page_size": "US Letter",
            "locale": "id-ID",
            "pdf_lang": "id-ID",
            "fixed_path_replays_byte_identical": True,
            "fixed_path_build_path": "qa/build-through-ch07-a/functional-analysis-id-through-ch07.pdf",
            "final_output_copy_state": "present_byte_identical",
            "publication_state": "pending",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH07-STRUCTURAL-CHECKER",
            "artifact_kind": "structural_math_language_checker",
            "path": CHECKER_PATH,
            "bytes": CHECKER_SIZE,
            "lines": CHECKER_LINES,
            "sha256": CHECKER_SHA,
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH07-RENDER-MANIFEST",
            "artifact_kind": "visual_QA_render_manifest",
            "path": RENDER_MANIFEST_PATH,
            "bytes": RENDER_MANIFEST_SIZE,
            "sha256": RENDER_MANIFEST_SHA,
            "rows": RENDER_MANIFEST_ROWS,
            "render_pages": PDF_PAGES,
            "uniform_pixel_dimensions": "1275x1650",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH07-CONTACT-SHEET",
            "artifact_kind": "visual_QA_contact_sheet",
            "path": CONTACT_SHEET_PATH,
            "bytes": CONTACT_SHEET_SIZE,
            "sha256": CONTACT_SHEET_SHA,
            "visual_pages": PDF_PAGES,
            "all_pages_inspected": True,
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH07-VISUAL-ACCESSIBILITY-AUDIT",
            "artifact_kind": "visual_accessibility_audit",
            "path": AUDIT_PATH,
            "bytes": AUDIT_SIZE,
            "lines": AUDIT_LINES,
            "sha256": AUDIT_SHA,
            "visual_result": "pass",
            "accessibility_gate_result": "pass",
            "fully_accessible_pdf_claim": "fail",
            "tagged_pdf": False,
            "accessibility_remediation_state": "pending_nonblocking",
            "accessible_html_or_tagged_pdf_state": "pending",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH07-QA-RECEIPT",
            "artifact_kind": "admission_receipt",
            "path": RECEIPT_PATH,
            "bytes": RECEIPT_SIZE,
            "lines": RECEIPT_LINES,
            "sha256": RECEIPT_SHA,
            "decision": "admitted",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH07-CORRECTIONS-LEDGER",
            "artifact_kind": "source_corrections_ledger",
            "path": LEDGER_PATH,
            "bytes": LEDGER_SIZE,
            "sha256": LEDGER_SHA,
            "prior_prefix_bytes": LEDGER_PRIOR_SIZE,
            "prior_prefix_sha256": LEDGER_PRIOR_SHA,
            "chapter_section_bytes": LEDGER_SECTION_SIZE,
            "chapter_section_sha256": LEDGER_SECTION_SHA,
            "chapter_correction_count": 11,
        },
    ]


def correction_records() -> list[dict]:
    specifications: list[tuple[str, str, str]] = [
        (
            "compact_operators.tex:22--26",
            "duplicate_environment_source_language",
            "Preserve both published proposition environments while repairing the first copy's malformed wording naturally in Indonesian.",
        ),
        (
            "compact_operators.tex:117",
            "missing_article",
            "Supply the missing article before the square-integrable-function phrase naturally in Indonesian.",
        ),
        (
            "compact_operators.tex:127--129",
            "unclosed_parenthesis",
            "Close the parenthetical reference to the earlier example.",
        ),
        (
            "compact_operators.tex:137",
            "undefined_compact_operator_space",
            r"Use \ofml K(B), matching the Banach space introduced by the example, rather than undefined \ofml K(H).",
        ),
        (
            "compact_operators.tex:162--165",
            "duplicated_conjunction",
            "Remove the duplicated 'that' construction naturally in Indonesian.",
        ),
        (
            "compact_operators.tex:299",
            "stray_parenthesis",
            "Remove the stray closing parenthesis following the definition of the final space.",
        ),
        (
            "compact_operators.tex:397--400",
            "positive_scalar_domain",
            r"Require \alpha\ge 0 because the trace is defined here only for positive operators.",
        ),
        (
            "compact_operators.tex:422",
            "wrong_operator_symbol",
            r"Use e^k=Uf^k, matching the unique unitary U introduced by the sentence.",
        ),
        (
            "compact_operators.tex:425--430",
            "defining_condition_conjunction",
            "Replace both instances of 'is' by 'if' in the cone and proper-cone conditions.",
        ),
        (
            "compact_operators.tex:436--437",
            "unbound_hilbert_space",
            r"Bind the separable Hilbert space as H before forming \ofml B(H).",
        ),
        (
            "compact_operators.tex:497",
            "missing_sequence_comma",
            r"Insert the missing comma in \{e_1, \dots, e_n\}.",
        ),
    ]
    if len(specifications) != 11:
        raise ValueError("Chapter 7 correction specification count changed")
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "correction",
        "unit_id": CHAPTER_ID,
        "target_disposition": "corrected",
        "ledger_path": LEDGER_PATH,
        "ledger_sha256": LEDGER_SHA,
        "ledger_section_sha256": LEDGER_SECTION_SHA,
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_path": RECEIPT_PATH,
        "receipt_sha256": RECEIPT_SHA,
        "upstream_report": "deferred_until_complete_and_separately_authorized",
    }
    return [
        fields
        | {
            "id": f"{CHAPTER_ID}-CORR-{number:03d}",
            "source_locator": locator,
            "correction_type": correction_type,
            "summary": summary,
        }
        for number, (locator, correction_type, summary) in enumerate(specifications, 1)
    ]


# One record per new distinct source term.  Established IDs are reused below.
TERM_SPECS: list[tuple[str, str, str]] = [
    ("TERM-TOTALLY-BOUNDED", "totally bounded", "terbatas total"),
    ("TERM-RELATIVELY-COMPACT", "relatively compact", "kompak relatif"),
    ("TERM-CSTAR-ALGEBRA", r"$C^\ast$-algebra", r"aljabar-$C^\ast$"),
    ("TERM-CSTAR-NORM", "$C^*$-norm", "norma-$C^*$"),
    ("TERM-CSTAR-SUBALGEBRA", "$C^*$-subalgebra", "subaljabar-$C^*$"),
    ("TERM-PARTIAL-ISOMETRY", "partial isometry", "isometri parsial"),
    ("TERM-INITIAL", "initial", "awal"),
    ("TERM-SUPPORT", "support", "tumpuan"),
    ("TERM-FINAL", "final", "akhir"),
    ("TERM-SPACE", "space", "ruang"),
    ("TERM-FINAL-SPACE", "final space", "ruang akhir"),
    ("TERM-TRACE", "trace", "jejak"),
    ("TERM-SIMILAR", "similar", "serupa"),
    ("TERM-CONE", "cone", "kerucut"),
    ("TERM-PROPER-CONE", "proper", "proper"),
    ("TERM-TRACE-CLASS", "trace class", "kelas jejak"),
    ("TERM-HILBERT-SCHMIDT", "Hilbert-Schmidt", "Hilbert--Schmidt"),
]
EXISTING_TERM_IDS = {
    "weakly continuous": "TERM-WEAKLY-CONTINUOUS",
    "compact": "TERM-COMPACT",
    "projection": "TERM-PROJECTION",
    "range": "TERM-RANGE",
}


def term_id_map() -> dict[str, str]:
    mapping = EXISTING_TERM_IDS | {
        source: stable_id for stable_id, source, _preferred in TERM_SPECS
    }
    if len(mapping) != 21:
        raise ValueError("Chapter 7 distinct defined-term inventory changed")
    return mapping


def terminology_records() -> list[dict]:
    records = []
    for stable_id, source_term, preferred in TERM_SPECS:
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "term",
            "id": stable_id,
            "source_term": source_term,
            "locale": "id-ID",
            "preferred": preferred,
            "variants": [],
            "rejected": [],
            "scope": "compact operators, partial isometries, and trace ideals",
            "evidence": "FAOA-2015-CH07 target source/id-ID/compact_operators-id.tex and backend/index_terms.csv",
        }
        if stable_id == "TERM-PROPER-CONE":
            record["scope"] = "proper cones in ordered vector spaces"
            record["rejected"] = ["wajar"]
        records.append(record)
    if len(records) != 17:
        raise ValueError("Chapter 7 new terminology record count changed")
    return records


def qa_records(formula_summary: dict[str, object]) -> list[dict]:
    common_fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "timestamp": "2026-08-22",
        "responsible_workflow": "Codex",
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_path": RECEIPT_PATH,
        "receipt_sha256": RECEIPT_SHA,
    }
    return [
        common_fields
        | {
            "id": "QA-CH07-STRUCTURAL-20260822",
            "qa_type": "unit_structural",
            "result": "pass",
            "witness": CHECKER_PATH,
            "witness_sha256": CHECKER_SHA,
            "semantic_anchors": 75,
            "semantic_units": 74,
            "segments": 85,
            "all_environment_pairs": 72,
            "semantic_environment_anchors": 70,
            "sections": 4,
            "labels": 20,
            "references": 13,
            "ordinary_target_references": 10,
            "future_target_references": 3,
            "equation_references": 0,
            "citations": 8,
            "index_terms": 91,
            "defined_terms": 26,
            "exercise_environments": 1,
            "proof_environments": 9,
            "proof_hints": 7,
            "ordinary_proofs": 2,
        },
        common_fields
        | {
            "id": "QA-CH07-MATH-20260822",
            "qa_type": "unit_mathematical",
            "result": "pass",
            "witness": CHECKER_PATH,
            "witness_sha256": CHECKER_SHA,
            **formula_summary,
            "classified_math_edit_blocks": 8,
            "unexplained_deltas": 0,
            "extractor": "backend/ch03_math.py",
            "extractor_sha256": "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3",
        },
        common_fields
        | {
            "id": "QA-CH07-LANGUAGE-20260822",
            "qa_type": "unit_language",
            "result": "pass",
            "witness": CHECKER_PATH,
            "witness_sha256": CHECKER_SHA,
            "severity_counts": {"P1": 0, "P2": 0, "P3": 0},
            "unintended_english_prose": 0,
            "placeholders": 0,
            "terminology_reconciled": True,
        },
        common_fields
        | {
            "id": "QA-CH07-BUILD-20260822",
            "qa_type": "cumulative_build",
            "result": "pass",
            "witness": FINAL_PDF_PATH,
            "witness_sha256": PDF_SHA,
            "master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH07-MASTER",
            "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH07-PDF",
            "pages": PDF_PAGES,
            "canonical_output_copy_state": "present_byte_identical",
            "fixed_path_clean_builds_byte_identical": True,
            "fixed_path_build_pdf_path": "qa/build-through-ch07-a/functional-analysis-id-through-ch07.pdf",
            "local_build_log_path": "qa/build-through-ch07-a/functional-analysis-id-through-ch07.log",
            "local_build_log_bytes": 47_575,
            "local_build_log_sha256": "35cf19763a0e6b8336ad962f49940791d17dad89d4b55451e10dd65e8f923af5",
            "local_build_log_publication_state": "excluded_ignored_build_intermediate",
            "admission_receipt_state": "present",
        },
        common_fields
        | {
            "id": "QA-CH07-VISUAL-20260822",
            "qa_type": "cumulative_visual",
            "result": "pass",
            "decision": "visual_render_navigation_pass",
            "witness": AUDIT_PATH,
            "witness_sha256": AUDIT_SHA,
            "pages_rendered": PDF_PAGES,
            "pages_inspected": PDF_PAGES,
            "uniform_pixel_dimensions": "1275x1650",
            "outer_5px_edge_ink_pages": 0,
            "rendered_png_bytes": 42_779_126,
            "word_boxes": 57_431,
            "out_of_bounds_word_boxes": 0,
            "intentional_blank_versos": [20, 48, 78, 100, 108],
            "visual_defects": 0,
            "render_manifest_sha256": RENDER_MANIFEST_SHA,
            "contact_sheet_sha256": CONTACT_SHEET_SHA,
        },
        common_fields
        | {
            "id": "QA-CH07-ACCESSIBILITY-20260822",
            "qa_type": "cumulative_accessibility",
            "result": "pass",
            "decision": "honest_chapter_boundary_accessibility_pass",
            "witness": AUDIT_PATH,
            "witness_sha256": AUDIT_SHA,
            "tagged_pdf": False,
            "fully_accessible_pdf_claim": False,
            "unicode_mapped_font_resources": 43,
            "total_font_resources": 43,
            "text_extraction_bytes": 463_585,
            "text_extraction_sha256": "aad0d057d0a8bd51bc9e39ea90da922b635c590b0c3746d8c82b7181fda6d6c1",
            "replacement_characters": 0,
            "resolved_internal_links": 1_620,
            "named_destinations": 1_132,
            "outline_entries": 47,
            "semantic_accessibility_state": "remediation_required",
            "accessible_html_or_tagged_pdf_state": "pending",
            "admission_blocker_for_chapter_boundary": False,
        },
        common_fields
        | {
            "id": "QA-CH07-RIGHTS-20260822",
            "qa_type": "unit_rights_privacy",
            "result": "pass",
            "decision": "rights_wrapper_and_public_path_closure_pass",
            "witness": CHECKER_PATH,
            "witness_sha256": CHECKER_SHA,
            "supplementary_witness": AUDIT_PATH,
            "supplementary_witness_sha256": AUDIT_SHA,
            "rights_id": RIGHTS,
            "attribution_change_notice_sharealike_nonendorsement": "present",
            "private_control_paths_absent_from_public_artifacts": True,
            "credential_or_token_residue": 0,
        },
        common_fields
        | {
            "id": ADMISSION_QA_ID,
            "qa_type": "unit_admission",
            "result": "pass",
            "decision": "admitted",
            "source_sha256": SOURCE_SHA,
            "target_sha256": TARGET_SHA,
            "build_master_sha256": MASTER_SHA,
            "artifact_sha256": PDF_SHA,
            "render_manifest_sha256": RENDER_MANIFEST_SHA,
            "contact_sheet_sha256": CONTACT_SHEET_SHA,
            "visual_accessibility_audit_sha256": AUDIT_SHA,
            "corrections_ledger_sha256": LEDGER_SHA,
            "receipt_path": RECEIPT_PATH,
            "receipt_sha256": RECEIPT_SHA,
            "typed_qa_event_ids": [
                "QA-CH07-STRUCTURAL-20260822",
                "QA-CH07-MATH-20260822",
                "QA-CH07-LANGUAGE-20260822",
                "QA-CH07-BUILD-20260822",
                "QA-CH07-VISUAL-20260822",
                "QA-CH07-ACCESSIBILITY-20260822",
                "QA-CH07-RIGHTS-20260822",
            ],
            "required_admission_gate_results": {
                "unit_structural": "pass",
                "unit_mathematical": "pass",
                "unit_language": "pass",
                "cumulative_build": "pass",
                "cumulative_visual": "pass",
                "cumulative_accessibility": "pass",
                "unit_rights_privacy": "pass",
                "admission_receipt": "pass",
            },
            "all_required_admission_gates": "pass",
            "publication_state": "pending",
        },
    ]


def prior_label_map() -> dict[str, str]:
    records = [
        json.loads(line) for line in locked_prefix("semantic_units.jsonl").splitlines()
    ]
    return {
        record["source_local_id"]: record["id"]
        for record in records
        if record.get("source_local_id")
    }


CORRECTION_FORMULAS = {
    69: f"{CHAPTER_ID}-CORR-004",
    249: f"{CHAPTER_ID}-CORR-007",
    263: f"{CHAPTER_ID}-CORR-008",
    267: f"{CHAPTER_ID}-CORR-009",
    275: f"{CHAPTER_ID}-CORR-010",
    309: f"{CHAPTER_ID}-CORR-011",
}
REORDERED_FORMULAS = {91, 92, 93}
CONSOLIDATED_SOURCE_CORRECTION_FORMULAS = {267}
TARGET_ONLY_FORMULAS = {275}


def build_math_pairs(source: str, target: str) -> tuple[list[dict], dict[str, object]]:
    source_math = ch03_math.extract_math(source, SOURCE_ENCODING)
    target_math = ch03_math.extract_math(target, TARGET_ENCODING)
    if (len(source_math), len(target_math)) != (309, 309):
        raise ValueError("Chapter 7 math-surface count changed")
    source_keys = [ch03_math.math_key(record["normalized"]) for record in source_math]
    target_keys = [ch03_math.math_key(record["normalized"]) for record in target_math]
    mapping: list[list[int] | None] = [None] * len(target_math)
    for tag, i1, i2, j1, j2 in SequenceMatcher(
        None, source_keys, target_keys, autojunk=False
    ).get_opcodes():
        if tag in {"equal", "replace"} and i2 - i1 == j2 - j1:
            for source_index, target_index in zip(
                range(i1, i2), range(j1, j2), strict=True
            ):
                mapping[target_index] = [source_index]
    # Natural Indonesian order moves CSA after its noun phrase.
    mapping[92] = [90]
    # One target V carries the two source occurrences in the repaired cone definition.
    mapping[266] = [266, 267]
    # Binding H is an explicit target-only source correction.
    mapping[274] = []
    if any(value is None for value in mapping):
        raise ValueError("Chapter 7 target formula coverage is incomplete")
    complete_mapping = [value for value in mapping if value is not None]
    used_sources = [index for group in complete_mapping for index in group]
    if sorted(used_sources) != list(range(len(source_math))):
        raise ValueError("Chapter 7 source formula coverage is incomplete")

    counts: collections.Counter[str] = collections.Counter()
    records: list[dict] = []
    for number, (source_indexes, target_record) in enumerate(
        zip(complete_mapping, target_math, strict=True), 1
    ):
        source_records = [source_math[index] for index in source_indexes]
        key_equal = (
            len(source_records) == 1
            and source_keys[source_indexes[0]] == target_keys[number - 1]
        )
        normalized_equal = (
            len(source_records) == 1
            and source_records[0]["normalized"] == target_record["normalized"]
        )
        if normalized_equal:
            alignment = (
                "preserved_exact_after_text_aware_whitespace_normalization_reordered"
                if number in REORDERED_FORMULAS
                else "preserved_exact_after_text_aware_whitespace_normalization"
            )
        elif number in TARGET_ONLY_FORMULAS:
            alignment = "reviewed_target_only_source_correction"
        elif number in CONSOLIDATED_SOURCE_CORRECTION_FORMULAS:
            alignment = "reviewed_consolidated_source_correction"
        elif number in CORRECTION_FORMULAS:
            alignment = "reviewed_source_correction"
        else:
            raise ValueError(f"unexpected Chapter 7 formula delta at target {number}")
        counts[alignment] += 1
        if not source_indexes:
            ordinal_alignment = "source_absent"
        elif len(source_indexes) > 1:
            ordinal_alignment = "consolidated"
        elif number in REORDERED_FORMULAS:
            ordinal_alignment = "reordered"
        elif source_indexes[0] + 1 == number:
            ordinal_alignment = "same"
        else:
            ordinal_alignment = "shifted"
        record: dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{number:04d}",
            "alignment": alignment,
            "math_key_alignment": (
                "equal"
                if key_equal
                else "target_only"
                if not source_indexes
                else "reviewed_difference"
            ),
            "ordinal_alignment": ordinal_alignment,
            "source_formula_ids": [
                f"{CHAPTER_ID}-SRC-MATH-{index + 1:04d}" for index in source_indexes
            ],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{number:04d}"],
            "source_lines": [
                [item["line_start"], item["line_end"]] for item in source_records
            ],
            "target_lines": [[target_record["line_start"], target_record["line_end"]]],
            "source_sha256": [item["sha256"] for item in source_records],
            "target_sha256": [target_record["sha256"]],
            "source_delimiters": [item["delimiter"] for item in source_records],
            "delimiter": target_record["delimiter"],
        }
        if number in REORDERED_FORMULAS:
            record |= {
                "sequence_opcode": "reorder",
                "delta_class": "localization_phrase_reordering",
                "correction_disposition": "not_a_source_correction",
                "qa_state": "passed",
            }
        elif number in CONSOLIDATED_SOURCE_CORRECTION_FORMULAS:
            record |= {
                "sequence_opcode": "merge",
                "delta_class": "source_correction",
                "correction_id": CORRECTION_FORMULAS[number],
                "correction_disposition": "corrected",
                "review_witness": LEDGER_PATH,
                "qa_state": "passed",
            }
        elif number in CORRECTION_FORMULAS:
            record |= {
                "sequence_opcode": "insert" if number in TARGET_ONLY_FORMULAS else "replace",
                "delta_class": "source_correction",
                "correction_id": CORRECTION_FORMULAS[number],
                "correction_disposition": "corrected",
                "review_witness": LEDGER_PATH,
                "qa_state": "passed",
            }
        records.append(record)
    expected_counts = {
        "preserved_exact_after_text_aware_whitespace_normalization": 300,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 3,
        "reviewed_source_correction": 4,
        "reviewed_consolidated_source_correction": 1,
        "reviewed_target_only_source_correction": 1,
    }
    if dict(counts) != expected_counts:
        raise ValueError(f"Chapter 7 formula alignment counts changed: {dict(counts)}")
    return records, {
        "source_math_surfaces": 309,
        "target_math_surfaces": 309,
        "exact_normalized_alignments": 303,
        "reviewed_source_correction_maps": 6,
        "target_only_source_corrections": 1,
        "consolidated_source_corrections": 1,
        "localization_phrase_reorderings": 3,
        "formula_map_records": 309,
    }


def write_manifest() -> None:
    paths = sorted(
        [
            path
            for path in BACKEND.iterdir()
            if path.is_file()
            and path.name != "BACKEND_MANIFEST.csv"
            and not path.name.endswith(".pyc")
        ],
        key=lambda path: path.name.casefold(),
    )
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["relative_path", "bytes", "sha256"])
    for path in paths:
        data = path.read_bytes()
        writer.writerow([path.name, len(data), sha(data)])
    (BACKEND / "BACKEND_MANIFEST.csv").write_text(
        buffer.getvalue(), encoding="utf-8", newline=""
    )


def main() -> None:
    verify_evidence()
    for name in PREFIX_LOCKS:
        locked_prefix(name)
    unit_boundaries()
    source = SOURCE_PATH.read_text(encoding=SOURCE_ENCODING)
    target = TARGET_PATH.read_text(encoding=TARGET_ENCODING)
    checker_run = subprocess.run(
        [sys.executable, str(ROOT / CHECKER_PATH)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    checker_result = json.loads(checker_run.stdout)
    if checker_result.get("result") != "pass":
        raise ValueError("Chapter 7 checker did not return its frozen pass result")

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if len(source_anchors) != 75 or [
        ch01.anchor_signature(anchor) for anchor in source_anchors
    ] != [ch01.anchor_signature(anchor) for anchor in target_anchors]:
        raise ValueError("Chapter 7 semantic anchor topology differs")
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 20 or [item["argument"] for item in source_labels] != [
        item["argument"] for item in target_labels
    ]:
        raise ValueError("Chapter 7 label sequence differs")

    semantic_units: list[dict] = []
    segment_records: list[dict] = []
    relations: list[dict] = []
    anchor_ids: list[str] = []
    anchor_bounds: dict[str, tuple[int, int]] = {}
    current_section = CHAPTER_ID
    current_section_by_anchor: list[str] = []
    section_number = 0
    node_number = 0
    state = "admitted"
    qa_state = "passed"
    for source_anchor, target_anchor in zip(
        source_anchors, target_anchors, strict=True
    ):
        if source_anchor["anchor_type"] == "chapter":
            unit_id = CHAPTER_ID
            parent_id = TARGET_EDITION
            kind = "chapter"
        elif source_anchor["anchor_type"] == "section":
            section_number += 1
            unit_id = f"{CHAPTER_ID}-SEC-{section_number:03d}"
            parent_id = CHAPTER_ID
            current_section = unit_id
            kind = "section"
        else:
            node_number += 1
            unit_id = f"{CHAPTER_ID}-NODE-{node_number:04d}"
            parent_id = current_section
            kind = source_anchor["environment"]
        anchor_ids.append(unit_id)
        current_section_by_anchor.append(current_section)
        anchor_bounds[unit_id] = (source_anchor["start"], source_anchor["end"])
        if source_anchor["anchor_type"] == "chapter":
            continue
        source_fragment = ch01.fragment(
            source, source_anchor["start"], source_anchor["end"], SOURCE_ENCODING
        )
        target_fragment = ch01.fragment(
            target, target_anchor["start"], target_anchor["end"], TARGET_ENCODING
        )
        semantic_units.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "unit",
                "id": unit_id,
                "unit_kind": kind,
                "parent_id": parent_id,
                "order_in_chapter": len(semantic_units) + 1,
                "edition_id": EDITION,
                "target_edition_id": TARGET_EDITION,
                "source_path": "source/upstream/compact_operators.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_fragment_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/compact_operators-id.tex",
                "target_line_start": target_fragment["line_start"],
                "target_line_end": target_fragment["line_end"],
                "target_fragment_sha256": target_fragment["sha256"],
                "source_local_id": source_anchor.get("label"),
                "source_title_tex": source_anchor.get("title"),
                "target_title_tex": target_anchor.get("title"),
                "locale": "id-ID",
                "translation_state": state,
                "qa_state": qa_state,
                "rights_id": RIGHTS,
            }
        )
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-CONTAINS-{len(semantic_units):04d}",
                "relation_type": "contains",
                "from_id": parent_id,
                "to_id": unit_id,
            }
        )
    if (len(semantic_units), section_number, node_number) != (74, 4, 70):
        raise ValueError("Chapter 7 semantic-unit topology invariant failed")

    source_parts: list[tuple[int, int, str, str]] = []
    target_parts: list[tuple[int, int, str, str]] = []
    previous_source = previous_target = 0
    previous_parent = CHAPTER_ID
    for index, (source_anchor, target_anchor, unit_id) in enumerate(
        zip(source_anchors, target_anchors, anchor_ids, strict=True)
    ):
        if source_anchor["start"] > previous_source or target_anchor["start"] > previous_target:
            source_raw = ch01.active_same_length(
                source[previous_source : source_anchor["start"]]
            ).strip()
            target_raw = ch01.active_same_length(
                target[previous_target : target_anchor["start"]]
            ).strip()
            if source_raw or target_raw:
                source_parts.append(
                    (previous_source, source_anchor["start"], "prose", previous_parent)
                )
                target_parts.append(
                    (previous_target, target_anchor["start"], "prose", previous_parent)
                )
        role = (
            "title"
            if source_anchor["anchor_type"] in {"chapter", "section"}
            else "semantic_environment"
        )
        source_parts.append((source_anchor["start"], source_anchor["end"], role, unit_id))
        target_parts.append((target_anchor["start"], target_anchor["end"], role, unit_id))
        previous_source, previous_target = source_anchor["end"], target_anchor["end"]
        previous_parent = current_section_by_anchor[index]
    if previous_source < len(source) or previous_target < len(target):
        source_raw = ch01.active_same_length(source[previous_source:]).strip()
        target_raw = ch01.active_same_length(target[previous_target:]).strip()
        if source_raw or target_raw:
            source_parts.append((previous_source, len(source), "prose", previous_parent))
            target_parts.append((previous_target, len(target), "prose", previous_parent))
    if len(source_parts) != 85 or len(target_parts) != 85:
        raise ValueError("Chapter 7 source/target segment count differs from 85")

    for number, (source_part, target_part) in enumerate(
        zip(source_parts, target_parts, strict=True), 1
    ):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if role != target_role or parent_id != target_parent:
            raise ValueError("Chapter 7 source/target segment role differs")
        source_fragment = ch01.fragment(source, source_start, source_end, SOURCE_ENCODING)
        target_fragment = ch01.fragment(target, target_start, target_end, TARGET_ENCODING)
        segment_id = f"{CHAPTER_ID}-SEG-{number:04d}"
        segment_records.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "segment",
                "id": segment_id,
                "parent_id": parent_id,
                "order": number,
                "segment_role": role,
                "source_path": "source/upstream/compact_operators.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_bytes": source_fragment["bytes"],
                "source_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/compact_operators-id.tex",
                "target_line_start": target_fragment["line_start"],
                "target_line_end": target_fragment["line_end"],
                "target_bytes": target_fragment["bytes"],
                "target_sha256": target_fragment["sha256"],
                "source_edition_id": EDITION,
                "target_edition_id": TARGET_EDITION,
                "locale": "id-ID",
                "translation_state": state,
                "qa_state": qa_state,
                "rights_id": RIGHTS,
                "_source_start": source_start,
                "_source_end": source_end,
                "_target_start": target_start,
                "_target_end": target_end,
            }
        )
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-TRANSLATES-{number:04d}",
                "relation_type": "translates",
                "from_id": segment_id,
                "to_id": segment_id,
                "source_edition_id": EDITION,
                "target_edition_id": TARGET_EDITION,
            }
        )
        if number > 1:
            relations.append(
                {
                    "schema": SCHEMA,
                    "schema_version": VERSION,
                    "record_type": "relation",
                    "id": f"{CHAPTER_ID}-REL-PRECEDES-{number - 1:04d}",
                    "relation_type": "precedes",
                    "from_id": f"{CHAPTER_ID}-SEG-{number - 1:04d}",
                    "to_id": segment_id,
                }
            )

    local_label_map: dict[str, str] = {}
    for number, occurrence in enumerate(source_labels, 1):
        segment_id = ch01.containing_segment(segment_records, occurrence["start"], "source")
        segment = next(record for record in segment_records if record["id"] == segment_id)
        local_label_map[occurrence["argument"]] = segment["parent_id"]
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-LABEL-{number:04d}",
                "relation_type": "declares_label",
                "from_id": segment_id,
                "to_id": segment["parent_id"],
                "source_local_id": occurrence["argument"],
                "label_id": f"ERDMAN-FAOA-2015-LABEL-{occurrence['argument']}",
            }
        )
    if len(local_label_map) != 20:
        raise ValueError("Chapter 7 local label map changed")

    source_refs = common.macro(source, "ref")
    target_refs = common.macro(target, "ref")
    future_labels = {"00152171", "00152181", "X_sqroot_op"}
    if len(source_refs) != 13 or len(target_refs) != 10:
        raise ValueError("Chapter 7 reference count changed")
    if [item["argument"] for item in target_refs] != [
        item["argument"] for item in source_refs if item["argument"] not in future_labels
    ]:
        raise ValueError("Chapter 7 target ordinary reference sequence changed")
    future_matches = list(
        re.finditer(r"\\futurexref\{([^{}]*)\}\{([^{}]+)\}", ch01.active_same_length(target))
    )
    if [(match.group(1), match.group(2)) for match in future_matches] != [
        ("12.3.16", "00152171"),
        ("12.3.17", "00152181"),
        ("11.5.7", "X_sqroot_op"),
    ]:
        raise ValueError("Chapter 7 futurexref endpoints changed")
    prior_labels = prior_label_map()
    reference_counts: collections.Counter[str] = collections.Counter()
    for number, occurrence in enumerate(source_refs, 1):
        label = occurrence["argument"]
        if label in local_label_map:
            to_id = local_label_map[label]
            resolution = "local"
            target_surface = "ref"
        elif label in prior_labels:
            to_id = prior_labels[label]
            resolution = "admitted_prior_unit"
            target_surface = "ref"
        elif label in future_labels:
            to_id = f"ERDMAN-FAOA-2015-LABEL-{label}"
            resolution = "pending_later_source_unit"
            target_surface = "futurexref"
        else:
            raise ValueError(f"unexpected unresolved Chapter 7 reference: {label}")
        reference_counts[resolution] += 1
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}",
                "relation_type": "xref",
                "from_id": ch01.containing_segment(
                    segment_records, occurrence["start"], "source"
                ),
                "to_id": to_id,
                "source_local_id": label,
                "resolution": resolution,
                "target_surface": target_surface,
            }
        )
    if dict(reference_counts) != {
        "admitted_prior_unit": 6,
        "local": 4,
        "pending_later_source_unit": 3,
    }:
        raise ValueError(f"Chapter 7 reference-resolution counts changed: {dict(reference_counts)}")
    if common.macro(source, "eqref") or common.macro(target, "eqref"):
        raise ValueError("Chapter 7 unexpectedly contains equation references")

    source_cites = common.macro(source, "cite")
    target_cites = common.macro(target, "cite")
    if len(source_cites) != 8 or [item["argument"] for item in source_cites] != [
        item["argument"] for item in target_cites
    ]:
        raise ValueError("Chapter 7 citation sequence differs")
    cite_key_count = 0
    for occurrence_number, occurrence in enumerate(source_cites, 1):
        for key in [item.strip() for item in occurrence["argument"].split(",")]:
            cite_key_count += 1
            relations.append(
                {
                    "schema": SCHEMA,
                    "schema_version": VERSION,
                    "record_type": "relation",
                    "id": f"{CHAPTER_ID}-REL-CITE-{occurrence_number:04d}-{key}",
                    "relation_type": "cites",
                    "from_id": ch01.containing_segment(
                        segment_records, occurrence["start"], "source"
                    ),
                    "to_id": f"ERDMAN-FAOA-BIB-{key}",
                    "source_local_id": key,
                }
            )
    if cite_key_count != 8:
        raise ValueError("Chapter 7 citation-key count changed")

    previous_statement: str | None = None
    hint_ids_by_statement: dict[str, list[str]] = collections.defaultdict(list)
    hint_relations = 0
    proof_count = 0
    for record in semantic_units:
        if record["unit_kind"] != "proof":
            previous_statement = record["id"]
            continue
        proof_count += 1
        if "Hint for proof" not in (record.get("source_title_tex") or ""):
            continue
        if previous_statement is None:
            raise ValueError("Chapter 7 proof hint lacks a preceding statement")
        hint_relations += 1
        hint_ids_by_statement[previous_statement].append(record["id"])
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-HINTS-{hint_relations:04d}",
                "relation_type": "hints",
                "from_id": record["id"],
                "to_id": previous_statement,
            }
        )
    if (proof_count, hint_relations) != (9, 7):
        raise ValueError("Chapter 7 proof/proof-hint topology changed")

    source_df = common.macro(source, "df")
    target_df = common.macro(target, "df")
    if len(source_df) != 26 or len(target_df) != 26:
        raise ValueError("Chapter 7 defined-term occurrence count changed")
    # Source and Indonesian phrases are semantically paired despite deliberate
    # local reordering around nested projection/support definitions.
    target_df_order = list(range(9)) + [10, 11, 9, 13, 14, 12, 16, 17, 15] + list(range(18, 26))
    expected_target_terms = [
        "terbatas total", "terbatas total", "kompak relatif",
        "kontinu secara lemah", "kompak", r"aljabar-$C^\ast$",
        "norma-$C^*$", "subaljabar-$C^*$", "isometri parsial",
        "awal", "tumpuan", "proyeksi", "akhir", "jangkauan", "proyeksi",
        "awal", "tumpuan", "ruang", "ruang akhir", "jejak", "serupa",
        "jejak", "kerucut", "proper", "kelas jejak", "Hilbert--Schmidt",
    ]
    paired_target_df = [target_df[index] for index in target_df_order]
    if [record["argument"] for record in paired_target_df] != expected_target_terms:
        raise ValueError("Chapter 7 semantic defined-term pairing changed")
    term_ids = term_id_map()
    if set(term_ids) != {record["argument"] for record in source_df}:
        raise ValueError("Chapter 7 distinct defined-term inventory changed")
    for number, (source_term, target_term) in enumerate(
        zip(source_df, paired_target_df, strict=True), 1
    ):
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}",
                "relation_type": "uses_term",
                "from_id": ch01.containing_segment(
                    segment_records, source_term["start"], "source"
                ),
                "to_id": term_ids[source_term["argument"]],
                "source_term_tex": source_term["argument"],
                "target_term_tex": target_term["argument"],
                "locale": "id-ID",
            }
        )

    source_terms = common.macro(source, "index")
    target_terms = common.macro(target, "index")
    if (
        len(source_terms) != 91
        or len(target_terms) != 91
        or [common.index_signature(item["argument"]) for item in source_terms]
        != [common.index_signature(item["argument"]) for item in target_terms]
    ):
        raise ValueError("Chapter 7 index-term alignment changed")
    term_buffer = io.StringIO(newline="")
    term_writer = csv.writer(term_buffer, lineterminator="\n")
    for number, (source_term, target_term) in enumerate(
        zip(source_terms, target_terms, strict=True), 1
    ):
        term_writer.writerow(
            [
                f"{CHAPTER_ID}-TERM-OCC-{number:04d}",
                ch01.containing_segment(
                    segment_records, source_term["start"], "source"
                ),
                number,
                source_term["line"],
                source_term["argument"],
                target_term["line"],
                target_term["argument"],
                sha(source_term["argument"].encode(SOURCE_ENCODING)),
                sha(target_term["argument"].encode(TARGET_ENCODING)),
                "id-ID",
            ]
        )

    formula_records, formula_summary = build_math_pairs(source, target)
    exercises: list[dict] = []
    for record in semantic_units:
        if record["unit_kind"] != "exer":
            continue
        number = len(exercises) + 1
        start, end = anchor_bounds[record["id"]]
        fragment = source[start:end]
        if re.search(r"\\emph\{Hint(?:[.:])?\}", fragment):
            raise ValueError("Chapter 7 exercise inline-hint state changed")
        exercises.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "exercise_support",
                "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-{number:03d}",
                "exercise_unit_id": record["id"],
                "source_exercise_order": number,
                "upstream_hint_ids": hint_ids_by_statement.get(record["id"], []),
                "upstream_inline_hint_state": "absent",
                "upstream_answer_state": "absent",
                "upstream_solution_state": "absent",
                "original_solution_id": f"O001-{CHAPTER_ID}-EX-{number:03d}-SOLUTION",
                "original_solution_state": "queued_in_O001",
                "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0",
                "provenance": "separately_authored_not_Erdman",
            }
        )
    if len(exercises) != 1 or exercises[0]["upstream_hint_ids"]:
        raise ValueError("Chapter 7 exercise-support topology changed")
    if any(
        kind == "begin" and environment in {"answer", "solution"}
        for kind, environment in common.env_sequence(source)
    ):
        raise ValueError("Chapter 7 unexpectedly contains a source answer or solution")

    relations.append(
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-RESOLVES-0001",
            "relation_type": "resolves_pending_reference",
            "from_id": local_label_map["chap_cpt_ops"],
            "to_id": "FAOA-2015-CH05-REL-XREF-0010",
            "source_local_id": "chap_cpt_ops",
            "stable_label_id": "ERDMAN-FAOA-2015-LABEL-chap_cpt_ops",
            "resolution": "declared_in_current_unit",
        }
    )

    artifacts = artifact_records()
    corrections = correction_records()
    terms = terminology_records()
    qa = qa_records(formula_summary)
    relation_common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "relation",
        "from_id": CHAPTER_ID,
    }
    relations.append(
        relation_common
        | {
            "id": f"{CHAPTER_ID}-REL-RIGHTS-0001",
            "relation_type": "licensed_under",
            "to_id": RIGHTS,
        }
    )
    for number, artifact in enumerate(artifacts, 1):
        relations.append(
            relation_common
            | {
                "id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}",
                "relation_type": "has_artifact",
                "to_id": artifact["id"],
            }
        )
    for number, artifact_id in enumerate(
        (
            "ARTIFACT-FAOA-ID-CH07-TARGET-TEX",
            "ARTIFACT-FAOA-ID-CH07-STRUCTURAL-CHECKER",
        ),
        1,
    ):
        relations.append(
            relation_common
            | {
                "id": f"{CHAPTER_ID}-REL-TERM-EVIDENCE-{number:04d}",
                "relation_type": "terminology_evidence",
                "to_id": artifact_id,
                "evidence_scope": "all Chapter 7 terminology records and occurrences",
            }
        )
    for number, event in enumerate(qa, 1):
        relations.append(
            relation_common
            | {
                "id": f"{CHAPTER_ID}-REL-QA-{number:04d}",
                "relation_type": "has_qa_event",
                "to_id": event["id"],
            }
        )
    for number, correction in enumerate(corrections, 1):
        relations.append(
            relation_common
            | {
                "id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}",
                "relation_type": "documents_correction",
                "to_id": correction["id"],
            }
        )
    if len(relations) != 349:
        raise ValueError(f"Chapter 7 relation invariant failed: {len(relations)}")

    for record in segment_records:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            del record[key]
    append_jsonl("semantic_units.jsonl", semantic_units)
    append_jsonl("segments.jsonl", segment_records)
    append_jsonl("relations.jsonl", relations)
    append_jsonl("formula_map.jsonl", formula_records)
    append_jsonl("exercise_support.jsonl", exercises)
    (BACKEND / "index_terms.csv").write_bytes(
        locked_prefix("index_terms.csv") + term_buffer.getvalue().encode("utf-8")
    )
    rewrite_units()
    append_jsonl("artifacts.jsonl", artifacts)
    append_jsonl("qa_events.jsonl", qa)
    append_jsonl("corrections.jsonl", corrections)
    append_jsonl("terminology.jsonl", terms)
    write_manifest()

    print(
        json.dumps(
            {
                "anchors": len(source_anchors),
                "semantic_units": len(semantic_units),
                "segments": len(segment_records),
                "relations": len(relations),
                "labels": len(source_labels),
                "source_ref_occurrences": len(source_refs),
                "target_ref_occurrences": len(target_refs),
                "local_references": reference_counts["local"],
                "admitted_prior_references": reference_counts["admitted_prior_unit"],
                "future_references": reference_counts["pending_later_source_unit"],
                "closed_prior_pending_references": 1,
                "cites": cite_key_count,
                "index_terms": len(source_terms),
                "defined_terms": len(source_df),
                "formula_map_records": len(formula_records),
                "exercises": len(exercises),
                "proofs": proof_count,
                "proof_hints": hint_relations,
                "ordinary_proofs": proof_count - hint_relations,
                "corrections": len(corrections),
                "terminology_records": len(terms),
                "artifacts": len(artifacts),
                "qa_events": len(qa),
                "receipt_document_state": "present",
                "translation_state": state,
                "qa_state": qa_state,
                **formula_summary,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
