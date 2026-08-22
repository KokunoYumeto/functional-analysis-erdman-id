#!/usr/bin/env python3
"""Append receipt-bound deterministic Chapter 8 records after Chapters 1--7."""

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
SOURCE_PATH = ROOT / "source" / "upstream" / "spectrum.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "spectrum-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH08"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
ADMISSION_QA_ID = "QA-CH08-ADMISSION-20260822"
RECEIPT_PATH = "provenance/CH08_BUILD_AND_QA_RECEIPT.md"
RECEIPT_SIZE = 9_732
RECEIPT_LINES = 174
RECEIPT_SHA = "fe74240d2ab6bb50fdc9ae3fb019c5dc77cee20250cfb5c46cd9a773b52cac83"

SOURCE_SIZE = 25_716
SOURCE_LINES = 611
SOURCE_SHA = "ae68cf224c6218ecd501cc983428cf924a3c361c6324a6b40793b1e9ba44b4dd"
TARGET_SIZE = 26_947
TARGET_LINES = 603
TARGET_SHA = "1120da36ebd0793690ecb47b33b921c81376d1bf7d2f03d9821b79356dfd03bc"

MASTER_PATH = "source/id-ID/functional-analysis-id-through-ch08.tex"
MASTER_SIZE = 9_714
MASTER_LINES = 334
MASTER_SHA = "d0b4130b9fa6f85baef22f316ea914d5519bf30d6e82d8e6d824f2cf211c1998"
FINAL_PDF_PATH = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-8.pdf"
PDF_SIZE = 1_593_249
PDF_PAGES = 129
PDF_SHA = "fb6488691e2127bc0b8e3f94f38033eb3bdbe0c61efedc66c07de8f3b3444fbd"

CHECKER_PATH = "qa/check_ch08_translation.py"
CHECKER_SIZE = 41_639
CHECKER_LINES = 1_078
CHECKER_SHA = "2720ec3cbe46060d65079a496e5fc550744c25863c11bdb1b5bb84047b14d54f"
DELTA_REPORT_PATH = "qa/CH08_CLASSIFIED_DELTA_INVENTORY.md"
DELTA_REPORT_SIZE = 10_143
DELTA_REPORT_LINES = 158
DELTA_REPORT_SHA = "efb89e83e3bc66861f941175e9abdc40d02e93c7b1d1e0fbe6e9afcadd1c0a4f"
REVIEW_PATH = "qa/CH08_INDEPENDENT_BILINGUAL_REVIEW.md"
REVIEW_SIZE = 5_504
REVIEW_LINES = 110
REVIEW_SHA = "74647e7a65f10026601cb6b54c97badf6528809620d4d2ef93e9b690d96c078f"
AUDIT_PATH = "qa/CH08_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
AUDIT_SIZE = 6_668
AUDIT_LINES = 121
AUDIT_SHA = "4ee0a948e108e905594c0bcc1858f050a001db1c60136a7e2c8135d64cf9520b"
RENDER_MANIFEST_PATH = "provenance/CH08_RENDER_MANIFEST.csv"
RENDER_MANIFEST_SIZE = 25_114
RENDER_MANIFEST_ROWS = 129
RENDER_MANIFEST_SHA = "796f36332ef748a4b1a7d8f01b7d75c7ec9da5236640f059d31df14fa3ec3e71"
CONTACT_SHEET_PATH = "provenance/CH08_CONTACT_SHEET.png"
CONTACT_SHEET_SIZE = 3_781_079
CONTACT_SHEET_SHA = "5d53f2c381f8108dd3a947e2ad85c744c21f2070c6397611b525af978690b6cf"

LEDGER_PATH = "provenance/SOURCE_CORRECTIONS.md"
LEDGER_SIZE = 25_794
LEDGER_SHA = "93836f6e440e81cb606a55a25c837318b620348379f4690923ab700bb6b3d23b"
LEDGER_PRIOR_SIZE = 23_661
LEDGER_PRIOR_SHA = "285f20b012926002bb9085dab91b06cee3e0808bf7881b598a276c643ad8eea7"
LEDGER_SECTION_SIZE = 2_133
LEDGER_SECTION_SHA = "8b83e5625e13d22c9edb3396230515d038d8fc3bd513b4a7866602bbf25e07da"
LEDGER_BLOCK_SHA = "bb76200eee25a2a5e8305f7e62570ae4eab4a50c3785a11c78cdc4a4007c409c"

PUBLIC_EVIDENCE_LOCKS = {
    "source/id-ID/spectrum-id.tex": (TARGET_SIZE, TARGET_SHA),
    MASTER_PATH: (MASTER_SIZE, MASTER_SHA),
    FINAL_PDF_PATH: (PDF_SIZE, PDF_SHA),
    CHECKER_PATH: (CHECKER_SIZE, CHECKER_SHA),
    DELTA_REPORT_PATH: (DELTA_REPORT_SIZE, DELTA_REPORT_SHA),
    REVIEW_PATH: (REVIEW_SIZE, REVIEW_SHA),
    AUDIT_PATH: (AUDIT_SIZE, AUDIT_SHA),
    RENDER_MANIFEST_PATH: (RENDER_MANIFEST_SIZE, RENDER_MANIFEST_SHA),
    CONTACT_SHEET_PATH: (CONTACT_SHEET_SIZE, CONTACT_SHEET_SHA),
    RECEIPT_PATH: (RECEIPT_SIZE, RECEIPT_SHA),
}

# Exact canonical Chapter 1--7 byte prefixes.  Chapter 8 may only append.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (712_537, "f21e580723ab03a093a0587212cdf385eaa61e5caabc27b369e584c8afc6dc0c"),
    "segments.jsonl": (815_244, "343b268786efaa066b89ac87ebf1c2de332faf9068d9fe5bd84b6a45b4b63fd0"),
    "relations.jsonl": (996_724, "fbd92656c8be43ccb5988e1940f73096c1eee8333bce178f9a8aaadd07e3934a"),
    "formula_map.jsonl": (3_447_333, "e9791f05b585f20852dff9fce229524b490578f1f673e03bad5dd96f51fc196a"),
    "exercise_support.jsonl": (17_627, "d4c47b75c65f60234d8eea0cca7cde7d958418877a4d55fb7b260e6e18ffed0d"),
    "index_terms.csv": (321_487, "eda03880449d80ca81878962619ff95e52c9bd5ca9bce9673775e3c10dc6d4e8"),
    "artifacts.jsonl": (31_117, "1a82e4e965370c86803820b7bda089f30fe7e7e40743b5c96aa976542066f132"),
    "qa_events.jsonl": (47_290, "503fa717ec78ab6692271a712901375ecf7c5ab2f46b4483d7c1221998ac6895"),
    "corrections.jsonl": (90_287, "1e30f208d8ad6f64f1871c90c54d2626115a0c3cbbb610062d76708303c654a9"),
    "terminology.jsonl": (77_363, "40a9c5dd0e85b2c972ef6491a51ab5b9387c1ba3ffd019874f9240da4fbb2245"),
}
UNIT_PREFIX_LOCK = (
    9_076,
    "491daaa1f4b594fd17afd79a57beb1eed32175e1c7f74b6f9476c6c088770851",
)
UNIT_SUFFIX_LOCK = (
    4_635,
    "be0a27dba0b8a51db9f8bcc8ea8465fe05ac00144ec491f7c6088943869b61c2",
)


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
        raise ValueError(f"{name} is shorter than its locked Chapter 1--7 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha or not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1--7 prefix changed")
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
    if (len(source), len(source.splitlines()), sha(source)) != (
        SOURCE_SIZE,
        SOURCE_LINES,
        SOURCE_SHA,
    ):
        raise ValueError("Chapter 8 source authority changed")
    for relative_path, (size, expected_sha) in PUBLIC_EVIDENCE_LOCKS.items():
        data = (ROOT / relative_path).read_bytes()
        if (len(data), sha(data)) != (size, expected_sha):
            raise ValueError(f"Chapter 8 evidence changed: {relative_path}")
    line_locks = {
        "source/id-ID/spectrum-id.tex": TARGET_LINES,
        MASTER_PATH: MASTER_LINES,
        CHECKER_PATH: CHECKER_LINES,
        DELTA_REPORT_PATH: DELTA_REPORT_LINES,
        REVIEW_PATH: REVIEW_LINES,
        AUDIT_PATH: AUDIT_LINES,
        RECEIPT_PATH: RECEIPT_LINES,
    }
    for relative_path, expected_lines in line_locks.items():
        if len((ROOT / relative_path).read_bytes().splitlines()) != expected_lines:
            raise ValueError(f"Chapter 8 line count changed: {relative_path}")
    if len((ROOT / RENDER_MANIFEST_PATH).read_bytes().splitlines()) != RENDER_MANIFEST_ROWS + 1:
        raise ValueError("Chapter 8 render-manifest row count changed")
    ledger = (ROOT / LEDGER_PATH).read_bytes()
    if (len(ledger), sha(ledger)) != (LEDGER_SIZE, LEDGER_SHA):
        raise ValueError("Chapter 8 correction ledger changed")
    if sha(ledger[:LEDGER_PRIOR_SIZE]) != LEDGER_PRIOR_SHA:
        raise ValueError("Chapter 1--7 correction-ledger prefix changed")
    section = ledger[LEDGER_PRIOR_SIZE:]
    if (
        len(section) != LEDGER_SECTION_SIZE
        or not section.startswith(b"\n## Chapter 8\n")
        or sha(section) != LEDGER_SECTION_SHA
    ):
        raise ValueError("Chapter 8 correction-ledger append changed")


def unit_boundaries() -> tuple[bytes, bytes]:
    lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    expected_ids = [f"FAOA-2015-CH{number:02d}" for number in range(1, 18)] + [
        "FAOA-ID-BRIDGE-CS"
    ]
    if len(lines) != len(expected_ids) or any(not line.endswith(b"\n") for line in lines):
        raise ValueError("units.jsonl ordered unit closure changed")
    if [json.loads(line)["id"] for line in lines] != expected_ids:
        raise ValueError("units.jsonl ordered unit IDs changed")
    prefix = b"".join(lines[:7])
    middle = lines[7]
    suffix = b"".join(lines[8:])
    if (len(prefix), sha(prefix)) != UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--7 prefix changed")
    if (len(suffix), sha(suffix)) != UNIT_SUFFIX_LOCK:
        raise ValueError("units.jsonl Chapter 9--bridge suffix changed")
    if json.loads(middle).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 8 replacement boundary changed")
    return prefix, suffix


def chapter_eight_unit() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 8,
        "source_path": "spectrum.tex",
        "source_bytes": SOURCE_SIZE,
        "source_lines": SOURCE_LINES,
        "source_sha256": SOURCE_SHA,
        "source_title": "SOME SPECTRAL THEORY",
        "target_path": "source/id-ID/spectrum-id.tex",
        "target_bytes": TARGET_SIZE,
        "target_lines": TARGET_LINES,
        "target_sha256": TARGET_SHA,
        "target_title": "Beberapa Teori Spektral",
        "course_role": "d20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 8,
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
    encoded = (
        json.dumps(chapter_eight_unit(), ensure_ascii=False, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    (BACKEND / "units.jsonl").write_bytes(prefix + encoded + suffix)


def artifact_records() -> list[dict]:
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "artifact",
        "unit_id": CHAPTER_ID,
        **admission_fields(),
    }
    return [
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH08-TARGET-TEX",
            "artifact_kind": "admitted_translation_source",
            "path": "source/id-ID/spectrum-id.tex",
            "bytes": TARGET_SIZE,
            "lines": TARGET_LINES,
            "sha256": TARGET_SHA,
            "locale": "id-ID",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH08-MASTER",
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
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH08-PDF",
            "artifact_kind": "canonical_cumulative_reader_pdf",
            "path": FINAL_PDF_PATH,
            "bytes": PDF_SIZE,
            "sha256": PDF_SHA,
            "pages": PDF_PAGES,
            "page_size": "US Letter",
            "locale": "id-ID",
            "pdf_lang": "id-ID",
            "final_output_copy_state": "present_and_frozen",
            "publication_state": "pending",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH08-STRUCTURAL-CHECKER",
            "artifact_kind": "structural_math_language_checker",
            "path": CHECKER_PATH,
            "bytes": CHECKER_SIZE,
            "lines": CHECKER_LINES,
            "sha256": CHECKER_SHA,
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH08-DELTA-REPORT",
            "artifact_kind": "classified_source_target_delta_report",
            "path": DELTA_REPORT_PATH,
            "bytes": DELTA_REPORT_SIZE,
            "lines": DELTA_REPORT_LINES,
            "sha256": DELTA_REPORT_SHA,
            "unclassified_deltas": 0,
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH08-BILINGUAL-REVIEW",
            "artifact_kind": "independent_bilingual_review",
            "path": REVIEW_PATH,
            "bytes": REVIEW_SIZE,
            "lines": REVIEW_LINES,
            "sha256": REVIEW_SHA,
            "decision": "pass",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH08-RENDER-MANIFEST",
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
            "id": "ARTIFACT-FAOA-ID-CH08-CONTACT-SHEET",
            "artifact_kind": "visual_QA_contact_sheet",
            "path": CONTACT_SHEET_PATH,
            "bytes": CONTACT_SHEET_SIZE,
            "sha256": CONTACT_SHEET_SHA,
            "visual_pages": PDF_PAGES,
            "all_pages_inspected": True,
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH08-VISUAL-ACCESSIBILITY-AUDIT",
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
            "id": "ARTIFACT-FAOA-ID-CH08-QA-RECEIPT",
            "artifact_kind": "admission_receipt",
            "path": RECEIPT_PATH,
            "bytes": RECEIPT_SIZE,
            "lines": RECEIPT_LINES,
            "sha256": RECEIPT_SHA,
            "decision": "admitted",
        },
        fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH08-CORRECTIONS-LEDGER",
            "artifact_kind": "source_corrections_ledger",
            "path": LEDGER_PATH,
            "bytes": LEDGER_SIZE,
            "sha256": LEDGER_SHA,
            "prior_prefix_bytes": LEDGER_PRIOR_SIZE,
            "prior_prefix_sha256": LEDGER_PRIOR_SHA,
            "chapter_section_bytes": LEDGER_SECTION_SIZE,
            "chapter_section_sha256": LEDGER_SECTION_SHA,
            "chapter_block_sha256": LEDGER_BLOCK_SHA,
            "chapter_correction_count": 8,
        },
    ]


def correction_records() -> list[dict]:
    specifications: list[tuple[str, str, str]] = [
        (
            "spectrum.tex:17",
            "missing_word_boundary",
            "Restore the missing word boundary after the parenthetical phrase naturally in Indonesian.",
        ),
        (
            "spectrum.tex:178--181",
            "reciprocal_parameter_domain",
            r"Restrict the reciprocal-spectrum equivalence to nonzero complex \lambda.",
        ),
        (
            "spectrum.tex:348",
            "stray_parenthesis",
            "Remove the stray closing parenthesis after the reference to Proposition C073134.",
        ),
        (
            "spectrum.tex:372",
            "mismatched_scalable_delimiter",
            r"Replace the mismatched \bigr( opening with \bigl(.",
        ),
        (
            "spectrum.tex:396--412",
            "volterra_operator_domain",
            r"Use Example 000319 as the formula precedent and explicitly define Vf(x)=\int_0^x f(t)\,dt on C([0,1]).",
        ),
        (
            "spectrum.tex:443--450",
            "unbound_hilbert_space_and_operator",
            r"Bind the Hilbert space H and T \in \ofml B(H) before using T=S^*S.",
        ),
        (
            "spectrum.tex:509",
            "theorem_optional_title",
            "Make Teorema Pemetaan Spektral the theorem environment's optional title.",
        ),
        (
            "spectrum.tex:547",
            "invalid_union_of_scalars",
            r"Define the diagonal-entry set as A=\{a_k\colon k\in\N\}.",
        ),
    ]
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "correction",
        "unit_id": CHAPTER_ID,
        "target_disposition": "corrected",
        "ledger_path": LEDGER_PATH,
        "ledger_sha256": LEDGER_SHA,
        "ledger_section_sha256": LEDGER_SECTION_SHA,
        "ledger_block_sha256": LEDGER_BLOCK_SHA,
        **admission_fields(),
        "qa_state": "passed",
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


EXISTING_TERM_IDS = {
    "idempotent": "TERM-IDEMPOTENT",
    "direct sum": "TERM-DIRECT-SUM",
    "eigenvalues": "TERM-EIGENVALUE",
    "similar": "TERM-SIMILAR",
}
NEW_TERM_SPECS: list[tuple[str, str, str]] = [
    ("TERM-LEFT-INVERTIBLE", "left invertible", "invertibel kiri"),
    ("TERM-LEFT-INVERSE", "left inverse", "invers kiri"),
    ("TERM-RIGHT-INVERTIBLE", "right invertible", "invertibel kanan"),
    ("TERM-RIGHT-INVERSE", "right inverse", "invers kanan"),
    ("TERM-INVERTIBLE", "invertible", "invertibel"),
    ("TERM-SPECTRUM", "spectrum", "spektrum"),
    (
        "TERM-BANACH-ALGEBRA-HOMOMORPHISM",
        "(Banach algebra) homomorphism",
        "homomorfisme (aljabar Banach)",
    ),
    ("TERM-RESOLVENT-MAPPING", "resolvent mapping", "pemetaan resolven"),
    ("TERM-ANALYTIC", "analytic", "analitik"),
    ("TERM-ENTIRE", "entire", "entire"),
    ("TERM-SPECTRAL-RADIUS", "spectral radius", "radius spektral"),
    ("TERM-RESOLVENT-SET", "resolvent set", "himpunan resolven"),
    ("TERM-POINT-SPECTRUM", "point spectrum", "spektrum titik"),
    (
        "TERM-APPROXIMATE-POINT-SPECTRUM",
        "approximate point spectrum",
        "spektrum titik aproksimatif",
    ),
    ("TERM-COMPRESSION-SPECTRUM", "compression spectrum", "spektrum kompresi"),
    ("TERM-RESIDUAL-SPECTRUM", "residual spectrum", "spektrum residual"),
]


def term_id_map() -> dict[str, str]:
    mapping = EXISTING_TERM_IDS | {
        source: stable_id for stable_id, source, _preferred in NEW_TERM_SPECS
    }
    mapping["right\ninverse"] = mapping.pop("right inverse")
    if len(mapping) != 20:
        raise ValueError("Chapter 8 distinct defined-term inventory changed")
    return mapping


def terminology_records() -> list[dict]:
    records = [
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "term",
            "id": stable_id,
            "source_term": source_term,
            "locale": "id-ID",
            "preferred": preferred,
            "variants": [],
            "rejected": [],
            "scope": "spectral theory for Banach algebras and Hilbert-space operators",
            "evidence": (
                "FAOA-2015-CH08 target source/id-ID/spectrum-id.tex; "
                "qa/check_ch08_translation.py; qa/CH08_INDEPENDENT_BILINGUAL_REVIEW.md"
            ),
        }
        for stable_id, source_term, preferred in NEW_TERM_SPECS
    ]
    return records


def qa_records(formula_summary: dict[str, object]) -> list[dict]:
    typed_ids = [
        "QA-CH08-STRUCTURAL-20260822",
        "QA-CH08-MATH-20260822",
        "QA-CH08-LANGUAGE-20260822",
        "QA-CH08-BUILD-20260822",
        "QA-CH08-VISUAL-20260822",
        "QA-CH08-ACCESSIBILITY-20260822",
        "QA-CH08-RIGHTS-20260822",
    ]
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "timestamp": "2026-08-22",
        "responsible_workflow": "Codex",
        **admission_fields(),
    }
    return [
        fields
        | {
            "id": typed_ids[0],
            "qa_type": "unit_structural",
            "result": "pass",
            "witness": CHECKER_PATH,
            "witness_sha256": CHECKER_SHA,
            "semantic_anchors": 87,
            "semantic_units": 86,
            "segments": 96,
            "all_environment_pairs": 96,
            "semantic_environment_anchors": 84,
            "sections": 2,
            "labels": 28,
            "references": 16,
            "ordinary_target_references": 16,
            "future_target_references": 0,
            "equation_references": 0,
            "citations": 3,
            "index_terms": 73,
            "defined_terms": 20,
            "exercise_environments": 2,
            "proof_environments": 14,
            "proof_hints": 12,
            "proof_comments": 1,
            "plain_proofs": 1,
        },
        fields
        | {
            "id": typed_ids[1],
            "qa_type": "unit_mathematical",
            "result": "pass",
            "witness": CHECKER_PATH,
            "witness_sha256": CHECKER_SHA,
            "supplementary_witness": DELTA_REPORT_PATH,
            "supplementary_witness_sha256": DELTA_REPORT_SHA,
            **formula_summary,
            "classified_math_edit_blocks": 6,
            "classified_control_edit_blocks": 1,
            "unexplained_deltas": 0,
            "extractor": "backend/ch03_math.py",
            "extractor_sha256": "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3",
        },
        fields
        | {
            "id": typed_ids[2],
            "qa_type": "unit_language",
            "result": "pass",
            "witness": REVIEW_PATH,
            "witness_sha256": REVIEW_SHA,
            "supplementary_witness": CHECKER_PATH,
            "supplementary_witness_sha256": CHECKER_SHA,
            "severity_counts": {"P1": 0, "P2": 0, "P3": 0},
            "unintended_english_prose": 0,
            "placeholders": 0,
            "terminology_reconciled": True,
        },
        fields
        | {
            "id": typed_ids[3],
            "qa_type": "cumulative_build",
            "result": "pass",
            "witness": FINAL_PDF_PATH,
            "witness_sha256": PDF_SHA,
            "master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH08-MASTER",
            "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH08-PDF",
            "pages": PDF_PAGES,
            "canonical_output_copy_state": "present_and_frozen",
            "admission_receipt_state": "present",
        },
        fields
        | {
            "id": typed_ids[4],
            "qa_type": "cumulative_visual",
            "result": "pass",
            "decision": "visual_render_navigation_pass",
            "witness": AUDIT_PATH,
            "witness_sha256": AUDIT_SHA,
            "pages_rendered": PDF_PAGES,
            "pages_inspected": PDF_PAGES,
            "uniform_pixel_dimensions": "1275x1650",
            "outer_5px_edge_ink_pages": 0,
            "rendered_png_bytes": 45_549_537,
            "word_boxes": 61_064,
            "out_of_bounds_word_boxes": 0,
            "intentional_blank_versos": [20, 48, 78, 100, 114, 116],
            "visual_defects": 0,
            "render_manifest_sha256": RENDER_MANIFEST_SHA,
            "contact_sheet_sha256": CONTACT_SHEET_SHA,
        },
        fields
        | {
            "id": typed_ids[5],
            "qa_type": "cumulative_accessibility",
            "result": "pass",
            "decision": "honest_chapter_boundary_accessibility_pass",
            "witness": AUDIT_PATH,
            "witness_sha256": AUDIT_SHA,
            "tagged_pdf": False,
            "fully_accessible_pdf_claim": False,
            "unicode_mapped_font_resources": 43,
            "total_font_resources": 43,
            "text_extraction_bytes": 491_578,
            "text_extraction_sha256": "ee477d952cb150428f39dba08acdff3ce43820f63dd462fcf5d8eb3136c7817e",
            "replacement_characters": 0,
            "resolved_internal_links": 1_718,
            "named_destinations": 1_241,
            "outline_entries": 50,
            "semantic_accessibility_state": "remediation_required",
            "accessibility_remediation_state": "pending_nonblocking",
            "accessible_html_or_tagged_pdf_state": "pending",
            "admission_blocker_for_chapter_boundary": False,
        },
        fields
        | {
            "id": typed_ids[6],
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
        fields
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
            "typed_qa_event_ids": typed_ids,
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
            "all_nonreceipt_gates": "pass",
            "all_required_admission_gates": "pass",
            "accessibility_remediation_state": "pending_nonblocking",
            "accessible_html_or_tagged_pdf_state": "pending",
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
    263: f"{CHAPTER_ID}-CORR-004",
    280: f"{CHAPTER_ID}-CORR-005",
    303: f"{CHAPTER_ID}-CORR-006",
    304: f"{CHAPTER_ID}-CORR-006",
    391: f"{CHAPTER_ID}-CORR-008",
}
REORDERED_FORMULAS = {64, 65}
TARGET_ONLY_FORMULAS = {280, 303}


def build_math_pairs(source: str, target: str) -> tuple[list[dict], dict[str, object]]:
    source_math = ch03_math.extract_math(source, SOURCE_ENCODING)
    target_math = ch03_math.extract_math(target, TARGET_ENCODING)
    if (len(source_math), len(target_math)) != (414, 416):
        raise ValueError("Chapter 8 math-surface count changed")
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
    # Indonesian word order moves the identical A surface one position earlier.
    mapping[63] = [64]
    # Corrections 5 and 6 add the Volterra definition and bind H explicitly.
    mapping[279] = []
    mapping[302] = []
    mapping[303] = [301]
    if any(value is None for value in mapping):
        missing = [number + 1 for number, value in enumerate(mapping) if value is None]
        raise ValueError(f"Chapter 8 target formula coverage is incomplete: {missing}")
    complete_mapping = [value for value in mapping if value is not None]
    used_sources = [index for group in complete_mapping for index in group]
    if sorted(used_sources) != list(range(len(source_math))):
        raise ValueError("Chapter 8 source formula coverage is incomplete")

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
        elif number in CORRECTION_FORMULAS:
            alignment = "reviewed_source_correction"
        else:
            raise ValueError(f"unexpected Chapter 8 formula delta at target {number}")
        counts[alignment] += 1
        if not source_indexes:
            ordinal_alignment = "source_absent"
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
        elif number in CORRECTION_FORMULAS:
            record |= {
                "sequence_opcode": "insert" if number in TARGET_ONLY_FORMULAS else "replace",
                "delta_class": "source_correction",
                "correction_id": CORRECTION_FORMULAS[number],
                "correction_disposition": "corrected",
                "review_witness": DELTA_REPORT_PATH,
                "qa_state": "passed",
            }
        records.append(record)
    expected_counts = {
        "preserved_exact_after_text_aware_whitespace_normalization": 409,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 2,
        "reviewed_source_correction": 3,
        "reviewed_target_only_source_correction": 2,
    }
    if dict(counts) != expected_counts:
        raise ValueError(f"Chapter 8 formula alignment counts changed: {dict(counts)}")
    return records, {
        "source_math_surfaces": 414,
        "target_math_surfaces": 416,
        "exact_normalized_alignments": 411,
        "reviewed_source_correction_maps": 5,
        "target_only_source_corrections": 2,
        "localization_phrase_reorderings": 2,
        "formula_map_records": 416,
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
        raise ValueError("Chapter 8 checker did not return its frozen pass result")

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if len(source_anchors) != 87 or [
        ch01.anchor_signature(anchor) for anchor in source_anchors
    ] != [ch01.anchor_signature(anchor) for anchor in target_anchors]:
        raise ValueError("Chapter 8 semantic anchor topology differs")
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 28 or [item["argument"] for item in source_labels] != [
        item["argument"] for item in target_labels
    ]:
        raise ValueError("Chapter 8 label sequence differs")

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
                "source_path": "source/upstream/spectrum.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_fragment_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/spectrum-id.tex",
                "target_line_start": target_fragment["line_start"],
                "target_line_end": target_fragment["line_end"],
                "target_fragment_sha256": target_fragment["sha256"],
                "source_local_id": source_anchor.get("label"),
                "source_title_tex": source_anchor.get("title"),
                "target_title_tex": target_anchor.get("title"),
                "locale": "id-ID",
                "translation_state": state,
                "qa_state": "passed",
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
    if (len(semantic_units), section_number, node_number) != (86, 2, 84):
        raise ValueError("Chapter 8 semantic-unit topology invariant failed")

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
    if len(source_parts) != 96 or len(target_parts) != 96:
        raise ValueError("Chapter 8 source/target segment count differs from 96")

    for number, (source_part, target_part) in enumerate(
        zip(source_parts, target_parts, strict=True), 1
    ):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if role != target_role or parent_id != target_parent:
            raise ValueError("Chapter 8 source/target segment role differs")
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
                "source_path": "source/upstream/spectrum.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_bytes": source_fragment["bytes"],
                "source_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/spectrum-id.tex",
                "target_line_start": target_fragment["line_start"],
                "target_line_end": target_fragment["line_end"],
                "target_bytes": target_fragment["bytes"],
                "target_sha256": target_fragment["sha256"],
                "source_edition_id": EDITION,
                "target_edition_id": TARGET_EDITION,
                "locale": "id-ID",
                "translation_state": state,
                "qa_state": "passed",
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

    source_refs = common.macro(source, "ref")
    target_refs = common.macro(target, "ref")
    if len(source_refs) != 16 or [item["argument"] for item in source_refs] != [
        item["argument"] for item in target_refs
    ]:
        raise ValueError("Chapter 8 reference sequence changed")
    if re.search(r"\\futurexref\{", ch01.active_same_length(target)):
        raise ValueError("Chapter 8 unexpectedly has a future reference")
    prior_labels = prior_label_map()
    reference_counts: collections.Counter[str] = collections.Counter()
    for number, occurrence in enumerate(source_refs, 1):
        label = occurrence["argument"]
        if label in local_label_map:
            to_id = local_label_map[label]
            resolution = "local"
        elif label in prior_labels:
            to_id = prior_labels[label]
            resolution = "admitted_prior_unit"
        else:
            raise ValueError(f"unexpected unresolved Chapter 8 reference: {label}")
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
                "target_surface": "ref",
            }
        )
    if dict(reference_counts) != {"local": 9, "admitted_prior_unit": 7}:
        raise ValueError(f"Chapter 8 reference-resolution counts changed: {dict(reference_counts)}")
    if common.macro(source, "eqref") or common.macro(target, "eqref"):
        raise ValueError("Chapter 8 unexpectedly contains equation references")

    source_cites = common.macro(source, "cite")
    target_cites = common.macro(target, "cite")
    if len(source_cites) != 3 or [item["argument"] for item in source_cites] != [
        item["argument"] for item in target_cites
    ]:
        raise ValueError("Chapter 8 citation sequence differs")
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
    if cite_key_count != 3:
        raise ValueError("Chapter 8 citation-key count changed")

    previous_statement: str | None = None
    hint_ids_by_statement: dict[str, list[str]] = collections.defaultdict(list)
    hint_relations = 0
    comment_relations = 0
    proof_count = 0
    for record in semantic_units:
        if record["unit_kind"] != "proof":
            previous_statement = record["id"]
            continue
        proof_count += 1
        title = record.get("source_title_tex") or ""
        if "Hint for proof" in title:
            if previous_statement is None:
                raise ValueError("Chapter 8 proof hint lacks a preceding statement")
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
        elif "Comment on proof" in title:
            if previous_statement is None:
                raise ValueError("Chapter 8 proof comment lacks a preceding statement")
            comment_relations += 1
            relations.append(
                {
                    "schema": SCHEMA,
                    "schema_version": VERSION,
                    "record_type": "relation",
                    "id": f"{CHAPTER_ID}-REL-COMMENTS-{comment_relations:04d}",
                    "relation_type": "comments_on",
                    "from_id": record["id"],
                    "to_id": previous_statement,
                }
            )
    if (proof_count, hint_relations, comment_relations) != (14, 12, 1):
        raise ValueError("Chapter 8 proof-role topology changed")

    source_df = common.macro(source, "df")
    target_df = common.macro(target, "df")
    expected_target_terms = [
        "invertibel kiri",
        "invers kiri",
        "invertibel kanan",
        "invers\nkanan",
        "invertibel",
        "spektrum",
        "idempoten",
        "homomorfisme (aljabar Banach)",
        "jumlah langsung",
        "Pemetaan resolven",
        "analitik",
        "entire",
        "radius spektral",
        "himpunan resolven",
        "spektrum titik",
        "nilai eigen",
        "spektrum titik aproksimatif",
        "spektrum kompresi",
        "spektrum residual",
        "serupa",
    ]
    if len(source_df) != 20 or [record["argument"] for record in target_df] != expected_target_terms:
        raise ValueError("Chapter 8 semantic defined-term pairing changed")
    term_ids = term_id_map()
    if set(term_ids) != {record["argument"] for record in source_df}:
        raise ValueError("Chapter 8 distinct defined-term inventory changed")
    for number, (source_term, target_term) in enumerate(
        zip(source_df, target_df, strict=True), 1
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
        len(source_terms) != 73
        or len(target_terms) != 73
        or [common.index_signature(item["argument"]) for item in source_terms]
        != [common.index_signature(item["argument"]) for item in target_terms]
    ):
        raise ValueError("Chapter 8 index-term alignment changed")
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
        inline_matches = list(re.finditer(r"\\emph\{Hint\.\}", fragment))
        inline_lines = [
            source.count("\n", 0, start + match.start()) + 1 for match in inline_matches
        ]
        exercises.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "exercise_support",
                "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-{number:03d}",
                "exercise_unit_id": record["id"],
                "source_exercise_order": number,
                "upstream_hint_ids": hint_ids_by_statement.get(record["id"], []),
                "upstream_inline_hint_state": "present" if inline_lines else "absent",
                **(
                    {"upstream_inline_hint_source_lines": inline_lines}
                    if inline_lines
                    else {}
                ),
                "upstream_answer_state": "absent",
                "upstream_solution_state": "absent",
                "original_solution_id": f"O001-{CHAPTER_ID}-EX-{number:03d}-SOLUTION",
                "original_solution_state": "queued_in_O001",
                "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0",
                "provenance": "separately_authored_not_Erdman",
            }
        )
    if len(exercises) != 2 or [
        record.get("upstream_inline_hint_source_lines") for record in exercises
    ] != [None, [401]]:
        raise ValueError("Chapter 8 exercise-support topology changed")
    if any(
        kind == "begin" and environment in {"answer", "solution"}
        for kind, environment in common.env_sequence(source)
    ):
        raise ValueError("Chapter 8 unexpectedly contains a source answer or solution")

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
            "ARTIFACT-FAOA-ID-CH08-TARGET-TEX",
            "ARTIFACT-FAOA-ID-CH08-STRUCTURAL-CHECKER",
            "ARTIFACT-FAOA-ID-CH08-BILINGUAL-REVIEW",
        ),
        1,
    ):
        relations.append(
            relation_common
            | {
                "id": f"{CHAPTER_ID}-REL-TERM-EVIDENCE-{number:04d}",
                "relation_type": "terminology_evidence",
                "to_id": artifact_id,
                "evidence_scope": "all Chapter 8 terminology records and occurrences",
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
    if len(relations) != 388:
        raise ValueError(f"Chapter 8 relation invariant failed: {len(relations)}")

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
                "future_references": 0,
                "closed_prior_pending_references": 0,
                "cites": cite_key_count,
                "index_terms": len(source_terms),
                "defined_terms": len(source_df),
                "formula_map_records": len(formula_records),
                "exercises": len(exercises),
                "proofs": proof_count,
                "proof_hints": hint_relations,
                "proof_comments": comment_relations,
                "ordinary_proofs": proof_count - hint_relations - comment_relations,
                "corrections": len(corrections),
                "terminology_records": len(terms),
                "artifacts": len(artifacts),
                "qa_events": len(qa),
                "receipt_document_state": "present",
                "translation_state": state,
                "qa_state": chapter_eight_unit()["qa_state"],
                **formula_summary,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
