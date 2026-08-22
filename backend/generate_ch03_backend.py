#!/usr/bin/env python3
"""Append deterministic Chapter 3 backend records after locked Chapters 1--2.

The existing Chapter 1--2 backend is an immutable byte prefix.  The optional
``INTERLANGUAGE_BACKEND_DIR`` environment variable permits a complete replay
against a scratch copy without mutating the canonical backend.
"""

from __future__ import annotations

import csv
import difflib
import hashlib
import io
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
import generate_ch01_backend as ch01
import ch03_math


ROOT = Path(__file__).resolve().parents[1]
BACKEND = Path(os.environ.get("INTERLANGUAGE_BACKEND_DIR", ROOT / "backend")).resolve()
SOURCE_PATH = ROOT / "source" / "upstream" / "normlinspaces.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "normlinspaces-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH03"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
TRANSLATION_STATE = "admitted"
QA_STATE = "passed"
ADMISSION_QA_ID = "QA-CH03-ADMISSION-20260821"

SOURCE_SIZE = 87537
SOURCE_LINES = 1920
SOURCE_SHA = "01548b8e80e14f6eb66703579ed7020e68cc65bd8d30538c13a3533a5ba777e7"
TARGET_SIZE = 94040
TARGET_LINES = 1913
TARGET_SHA = "c44f20890d5fb6b7445f0b2eeca8f477cc970d147d5c54aa4bc5df709f6b1f9d"

# Exact canonical Chapter 1--2 backend.  Every generated Chapter 3 projection
# retains these bytes literally and appends only Chapter 3 records.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (130118, "33cfd2695c25382481a73e475f554b1de74a053e5e280f5a09bd65aace035065"),
    "segments.jsonl": (148764, "a29b3500ea61ac2158635def07ce9b9cae7da1cb7d058a0a74a59ad8dc89355f"),
    "relations.jsonl": (152072, "59a639312c362dda0f6b7a7968668b9ce1ea7e01558d2f6f73273c33ac52c200"),
    "formula_map.jsonl": (694060, "c923f95258e7237ed1e554c4677624fd489209c6807c9f5abbe1afbdca18e027"),
    "exercise_support.jsonl": (3062, "185420e94dbf748f3617a462b8f03936e7cf33a66b9f47b65dcf2c9a242bf4af"),
    "index_terms.csv": (80770, "f0c7dc67e655c6e0ba24aaf1d5fc154b7f378d7e561ee78548b64d1a5b1dd799"),
    "artifacts.jsonl": (4604, "2d7f7fe711a1ea1f6b0083c2422953dbfc0be440e813f16feec6d3a6f71c15dc"),
    "qa_events.jsonl": (7118, "5161bce67b85db0d24da3255852a44a9aca0fe4d0e43a6cafe060043ea0a9df5"),
    "corrections.jsonl": (9793, "36a72e5ec53d2804d2129a2d8215ac9119e5aef570f0836cd69fe0c4e4db9b7b"),
    "terminology.jsonl": (11420, "3cbb3d2077e7e0f56bdf92b0bd77afff7ae420e9acb1acb48b0b1ab84e336461"),
}

UNIT_PREFIX_LOCK = (2156, "71f2f9fece48c4e4d8499ba19bdf169344a4519dc35b849a2874d71f212abfde")

# Lock every final witness, including the admission receipt created after the
# isolated pre-admission replay.
EVIDENCE_LOCKS = {
    "source/id-ID/functional-analysis-id-through-ch03.tex": (
        9311,
        "f36da75492209ba8f4df1d8982bc5a7eae79d75a5dfeb87267715c998aeed8c7",
    ),
    "source/id-ID/normlinspaces-id.tex": (TARGET_SIZE, TARGET_SHA),
    "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-3.pdf": (
        1076473,
        "7a921e1f9678b0a698de237a0a0e5629f24f5b6f0798d2638d9c0a70a499b4f5",
    ),
    "qa/check_ch03_translation.py": (
        7420,
        "9fed1e9c4d6111db8c10e19f05589b070e3508b2290c1a897a73a7eb04364386",
    ),
    "backend/ch03_math.py": (
        6352,
        "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3",
    ),
    "provenance/CH03_RENDER_MANIFEST.csv": (
        5211,
        "162328427d9912347eeadb39c1c78f8cbad62f599904cc929e075ac109e96b73",
    ),
    "provenance/CH03_CONTACT_SHEET.png": (
        1267020,
        "bf4872e145c57768cc369cb748ef7d4cbc61a424414ee158a0a18572a381a284",
    ),
    "provenance/SOURCE_CORRECTIONS.md": (
        7325,
        "bb1ef771876b2c1ef0063c3fd9e28c27f20db4049f434d27f8b333fd5f3477c2",
    ),
    "provenance/CH03_BUILD_AND_QA_RECEIPT.md": (
        6871,
        "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a",
    ),
}

EXPECTED_MATH_DEVIATIONS = [
    ("replace", 40, 41, 40, 41),
    ("replace", 58, 59, 58, 59),
    ("replace", 61, 62, 61, 62),
    ("replace", 125, 126, 125, 126),
    ("replace", 369, 370, 369, 370),
    ("replace", 583, 584, 583, 584),
    ("replace", 682, 685, 682, 685),
    ("replace", 730, 731, 730, 731),
    ("replace", 739, 741, 739, 741),
    ("replace", 837, 838, 837, 838),
    ("replace", 877, 878, 877, 878),
    ("replace", 919, 920, 919, 920),
    ("replace", 1070, 1071, 1070, 1071),
    ("replace", 1117, 1118, 1117, 1118),
    ("replace", 1300, 1302, 1300, 1302),
    ("replace", 1379, 1380, 1379, 1380),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def locked_prefix(name: str) -> bytes:
    size, expected_sha = PREFIX_LOCKS[name]
    data = (BACKEND / name).read_bytes()
    if len(data) < size:
        raise ValueError(f"{name} is shorter than its locked Chapter 1--2 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha:
        raise ValueError(f"{name} Chapter 1--2 prefix hash changed")
    if not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1--2 prefix lacks final LF")
    return prefix


def append_jsonl(name: str, records: list[dict]) -> None:
    suffix = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")
    (BACKEND / name).write_bytes(locked_prefix(name) + suffix)


def verify_evidence() -> None:
    for relative_path, identity in EVIDENCE_LOCKS.items():
        data = (ROOT / relative_path).read_bytes()
        if relative_path == "provenance/SOURCE_CORRECTIONS.md":
            historical_size, historical_sha = identity
            if len(data) < historical_size or sha(data[:historical_size]) != historical_sha:
                raise ValueError(f"Chapter 3 evidence prefix changed: {relative_path}")
            continue
        if (len(data), sha(data)) != identity:
            raise ValueError(f"Chapter 3 evidence changed: {relative_path}")


def unit_boundaries() -> tuple[bytes, bytes]:
    data = (BACKEND / "units.jsonl").read_bytes()
    prefix_size, prefix_sha = UNIT_PREFIX_LOCK
    lines = data.splitlines(keepends=True)
    expected_ids = [f"FAOA-2015-CH{number:02d}" for number in range(1, 18)] + [
        "FAOA-ID-BRIDGE-CS"
    ]
    if len(lines) != len(expected_ids) or any(not line.endswith(b"\n") for line in lines):
        raise ValueError("units.jsonl ordered unit closure changed")
    if [json.loads(line)["id"] for line in lines] != expected_ids:
        raise ValueError("units.jsonl ordered unit IDs changed")
    prefix = b"".join(lines[:2])
    middle = lines[2]
    suffix = b"".join(lines[3:])
    if len(prefix) != prefix_size or sha(prefix) != prefix_sha:
        raise ValueError("units.jsonl Chapter 1--2 prefix changed")
    if json.loads(middle).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 3 replacement boundary changed")
    return prefix, suffix


def chapter_three_unit() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 3,
        "source_path": "normlinspaces.tex",
        "source_bytes": SOURCE_SIZE,
        "source_lines": SOURCE_LINES,
        "source_sha256": SOURCE_SHA,
        "source_title": "NORMED LINEAR SPACES",
        "target_path": "source/id-ID/normlinspaces-id.tex",
        "target_bytes": TARGET_SIZE,
        "target_lines": TARGET_LINES,
        "target_sha256": TARGET_SHA,
        "target_title": "Ruang Linear Bernorma",
        "course_role": "D20_core",
        "translation_state": TRANSLATION_STATE,
        "qa_state": QA_STATE,
        "source_corrections": 25,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch03.tex",
        "build_master_bytes": 9311,
        "build_master_sha256": "f36da75492209ba8f4df1d8982bc5a7eae79d75a5dfeb87267715c998aeed8c7",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-3.pdf",
        "artifact_bytes": 1076473,
        "artifact_pages": 57,
        "artifact_sha256": "7a921e1f9678b0a698de237a0a0e5629f24f5b6f0798d2638d9c0a70a499b4f5",
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_sha256": "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a",
        "rights_id": RIGHTS,
    }


def rewrite_units() -> None:
    prefix, suffix = unit_boundaries()
    encoded = (
        json.dumps(chapter_three_unit(), ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    (BACKEND / "units.jsonl").write_bytes(prefix + encoded + suffix)


def artifact_records() -> list[dict]:
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "artifact",
        "unit_id": CHAPTER_ID,
        "qa_receipt_id": ADMISSION_QA_ID,
    }
    return [
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH03-TARGET-TEX",
            "artifact_kind": "admitted_translation_source",
            "path": "source/id-ID/normlinspaces-id.tex",
            "bytes": TARGET_SIZE,
            "lines": TARGET_LINES,
            "sha256": TARGET_SHA,
            "locale": "id-ID",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH03-MASTER",
            "artifact_kind": "cumulative_TeX_master",
            "path": "source/id-ID/functional-analysis-id-through-ch03.tex",
            "bytes": 9311,
            "sha256": "f36da75492209ba8f4df1d8982bc5a7eae79d75a5dfeb87267715c998aeed8c7",
            "cumulative_through_unit_id": CHAPTER_ID,
            "locale": "id-ID",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH03-PDF",
            "artifact_kind": "canonical_cumulative_reader_pdf",
            "path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-3.pdf",
            "bytes": 1076473,
            "sha256": "7a921e1f9678b0a698de237a0a0e5629f24f5b6f0798d2638d9c0a70a499b4f5",
            "pages": 57,
            "page_size": "US Letter",
            "locale": "id-ID",
            "pdf_lang": "id-ID",
            "tagged_pdf": False,
            "bookmarks": True,
            "toolchain": "MiKTeX 26.5; pdfTeX 1.40.29; latexmk 4.88; BibTeX; MakeIndex; Xy-pic",
            "source_date_epoch": 1444126743,
            "two_clean_builds_byte_identical": True,
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH03-QA-RECEIPT",
            "artifact_kind": "admission_receipt",
            "path": "provenance/CH03_BUILD_AND_QA_RECEIPT.md",
            "bytes": 6871,
            "sha256": "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH03-STRUCTURAL-CHECKER",
            "artifact_kind": "structural_math_language_checker",
            "path": "qa/check_ch03_translation.py",
            "bytes": 7420,
            "sha256": "9fed1e9c4d6111db8c10e19f05589b070e3508b2290c1a897a73a7eb04364386",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH03-MATH-EXTRACTOR",
            "artifact_kind": "text_aware_math_extractor",
            "path": "backend/ch03_math.py",
            "bytes": 6352,
            "sha256": "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH03-RENDER-MANIFEST",
            "artifact_kind": "visual_QA_render_manifest",
            "path": "provenance/CH03_RENDER_MANIFEST.csv",
            "bytes": 5211,
            "sha256": "162328427d9912347eeadb39c1c78f8cbad62f599904cc929e075ac109e96b73",
            "rows": 57,
            "coverage": "57 page PNGs",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH03-CONTACT-SHEET",
            "artifact_kind": "visual_QA_contact_sheet",
            "path": "provenance/CH03_CONTACT_SHEET.png",
            "bytes": 1267020,
            "sha256": "bf4872e145c57768cc369cb748ef7d4cbc61a424414ee158a0a18572a381a284",
            "visual_pages": 57,
            "all_pages_inspected": True,
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH03-CORRECTIONS-LEDGER",
            "artifact_kind": "source_corrections_ledger",
            "path": "provenance/SOURCE_CORRECTIONS.md",
            "bytes": 7325,
            "sha256": "bb1ef771876b2c1ef0063c3fd9e28c27f20db4049f434d27f8b333fd5f3477c2",
            "chapter_correction_count": 25,
        },
    ]


def qa_records(non_equal_map_ids: list[str]) -> list[dict]:
    checker = "qa/check_ch03_translation.py"
    checker_sha = "9fed1e9c4d6111db8c10e19f05589b070e3508b2290c1a897a73a7eb04364386"
    typed_ids = [
        "QA-CH03-STRUCTURAL-20260821",
        "QA-CH03-MATH-20260821",
        "QA-CH03-LANGUAGE-20260821",
        "QA-CH03-BUILD-20260821",
        "QA-CH03-VISUAL-20260821",
        "QA-CH03-RIGHTS-20260821",
    ]
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "result": "pass",
        "timestamp": "2026-08-21",
        "responsible_workflow": "Codex",
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_path": "provenance/CH03_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a",
    }
    return [
        common
        | {
            "id": typed_ids[0],
            "qa_type": "unit_structural",
            "witness": checker,
            "witness_sha256": checker_sha,
            "semantic_anchors": 185,
            "semantic_units": 184,
            "segments": 228,
            "labels": 91,
            "references": 48,
            "ordinary_target_references": 46,
            "future_target_references": 1,
            "equation_references": 1,
            "citations": 6,
            "index_terms": 344,
            "exercise_environments": 7,
        },
        common
        | {
            "id": typed_ids[1],
            "qa_type": "unit_mathematical",
            "witness": checker,
            "witness_sha256": checker_sha,
            "source_math_surfaces": 1414,
            "target_math_surfaces": 1414,
            "exact_normalized_alignments": 1394,
            "non_equal_map_ids": non_equal_map_ids,
            "reviewed_deviation_opcodes": 16,
            "unexplained_deltas": 0,
            "extractor": "backend/ch03_math.py",
            "extractor_sha256": "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3",
        },
        common
        | {
            "id": typed_ids[2],
            "qa_type": "unit_language",
            "witness": checker,
            "witness_sha256": checker_sha,
            "severity_counts": {"P1": 0, "P2": 0, "P3": 0},
            "unintended_english_prose": 0,
            "mojibake_or_replacement_characters": 0,
            "terminology_reconciled": True,
        },
        common
        | {
            "id": typed_ids[3],
            "qa_type": "cumulative_build",
            "witness": "provenance/CH03_BUILD_AND_QA_RECEIPT.md",
            "witness_sha256": "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a",
            "master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH03-MASTER",
            "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH03-PDF",
            "clean_builds": 2,
            "byte_identical": True,
            "tex_errors": 0,
            "unresolved_references_or_citations": 0,
            "overfull_boxes": 0,
        },
        common
        | {
            "id": typed_ids[4],
            "qa_type": "cumulative_visual",
            "witness": "provenance/CH03_RENDER_MANIFEST.csv",
            "witness_sha256": "162328427d9912347eeadb39c1c78f8cbad62f599904cc929e075ac109e96b73",
            "render_manifest_artifact_id": "ARTIFACT-FAOA-ID-CH03-RENDER-MANIFEST",
            "contact_sheet_artifact_id": "ARTIFACT-FAOA-ID-CH03-CONTACT-SHEET",
            "pages_rendered": 57,
            "pages_inspected": 57,
            "visual_defects": 0,
        },
        common
        | {
            "id": typed_ids[5],
            "qa_type": "unit_rights_privacy",
            "witness": "source/id-ID/functional-analysis-id-through-ch03.tex",
            "witness_sha256": "f36da75492209ba8f4df1d8982bc5a7eae79d75a5dfeb87267715c998aeed8c7",
            "rights_id": RIGHTS,
            "attribution_change_notice_sharealike_nonendorsement": "present",
            "excluded_components_absent": True,
            "privacy_scans": "pass",
        },
        common
        | {
            "id": ADMISSION_QA_ID,
            "qa_type": "unit_admission",
            "timestamp": "2026-08-22",
            "decision": "admitted",
            "witness": "provenance/CH03_BUILD_AND_QA_RECEIPT.md",
            "witness_sha256": "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a",
            "source_sha256": SOURCE_SHA,
            "target_sha256": TARGET_SHA,
            "build_master_sha256": "f36da75492209ba8f4df1d8982bc5a7eae79d75a5dfeb87267715c998aeed8c7",
            "artifact_sha256": "7a921e1f9678b0a698de237a0a0e5629f24f5b6f0798d2638d9c0a70a499b4f5",
            "render_manifest_sha256": "162328427d9912347eeadb39c1c78f8cbad62f599904cc929e075ac109e96b73",
            "corrections_ledger_sha256": "bb1ef771876b2c1ef0063c3fd9e28c27f20db4049f434d27f8b333fd5f3477c2",
            "receipt_document_state": "present",
            "typed_qa_event_ids": typed_ids,
            "all_required_gates": "pass",
        },
    ]


def correction_records() -> list[dict]:
    specifications: list[tuple[object, str, str]] = [
        ("normlinspaces.tex:52", "stray_tuple_comma", "Remove the stray comma in the sequence tuple."),
        ("normlinspaces.tex:74", "malformed_subscript", r"Repair malformed c) as c_0."),
        ("normlinspaces.tex:78--80", "scalar_field_consistency", "Use the scalar field K for bounded scalar-valued functions."),
        ("normlinspaces.tex:141", "missing_subscript", r"Repair (fn) as (f_n)."),
        ("normlinspaces.tex:388", "missing_verb", "Supply the missing verb in the sequence hypothesis."),
        ("normlinspaces.tex:482", "source_language", "Repair the source-language slip naturally in translation."),
        ("normlinspaces.tex:527", "wrong_preceding_object", "Refer to the preceding proposition, not a nonexistent exercise."),
        ("normlinspaces.tex:625", "stray_parenthesis", "Remove the stray parenthesis in the norm-preserving definition."),
        ("normlinspaces.tex:737", "future_cross_reference", "Represent exam_ran_nonclosed as typed future reference 5.2.14."),
        ("normlinspaces.tex:798", "scalar_field_consistency", "Use alpha in K for quotient scalar multiplication."),
        ("normlinspaces.tex:960--971", "product_space_notation", "Repair the product sentence and use V_1,V_2 consistently."),
        (["normlinspaces.tex:974", "normlinspaces.tex:1323"], "missing_verb", "Supply two missing verbs naturally in translation."),
        ("normlinspaces.tex:1039--1040", "undefined_product_family", "Replace A_lambda by V_lambda and use K."),
        ("normlinspaces.tex:1086", "wrong_product_norm_ordinal", "Identify the selected product norm as the second, the 1-norm."),
        ("normlinspaces.tex:1156--1216", "scalar_codomain_consistency", "Treat B(S), C(X), and C_b(X) as K-valued and type evaluation into K."),
        ("normlinspaces.tex:1260", "wrong_coproduct_domain", "Give the universal coproduct morphism domain Q, not P."),
        ("normlinspaces.tex:1299--1300", "disjoint_union_definition", "Define the indexed disjoint union by pairs (a,lambda) with a in A_lambda."),
        ("normlinspaces.tex:1607", "incomplete_bounded_net_definition", "Require a bounded range in the bounded-net definition."),
        ("normlinspaces.tex:1702", "index_spelling_and_term", "Repair the index key and use the controlled term tutupan."),
        ("normlinspaces.tex:1741--1742", "pronunciation_localization", "Replace English-only pronunciation cues with Indonesian sound examples."),
        ("normlinspaces.tex:1798--1799", "real_part_variable", "Use u, the real part of f, in the real-linearity equations."),
        ("normlinspaces.tex:1820", "theorem_kind", "Identify HBT III as a theorem, not a proposition."),
        ("normlinspaces.tex:1859--1860", "nonzero_hypothesis", "Require a nonzero vector in the norm-one-functional corollary."),
        ("normlinspaces.tex:205--215", "distinguished_zero_scope", "Condition zero-centered ball and sphere shorthand on a distinguished zero point."),
        (
            ["normlinspaces.tex:527--541", "normlinspaces.tex:594--598", "normlinspaces.tex:1220--1222"],
            "zero_domain_operator_norm",
            "Handle the zero domain in operator-norm formulas and restrict unit-norm and unital claims to nonzero spaces.",
        ),
    ]
    if len(specifications) != 25:
        raise ValueError("Chapter 3 correction specification count changed")
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "correction",
        "unit_id": CHAPTER_ID,
        "target_disposition": "corrected",
        "ledger_path": "provenance/SOURCE_CORRECTIONS.md",
        "ledger_sha256": "bb1ef771876b2c1ef0063c3fd9e28c27f20db4049f434d27f8b333fd5f3477c2",
        "qa_receipt_id": ADMISSION_QA_ID,
        "upstream_report": "deferred_until_complete_and_separately_authorized",
    }
    return [
        common
        | {
            "id": f"{CHAPTER_ID}-CORR-{number:03d}",
            "source_locator": locator,
            "correction_type": correction_type,
            "summary": summary,
        }
        for number, (locator, correction_type, summary) in enumerate(specifications, 1)
    ]


def terminology_records() -> list[dict]:
    specifications = [
        ("NORMED-LINEAR-SPACE", "normed linear space", "ruang linear bernorma", [], [], "normed-space theory"),
        ("BOUNDED-LINEAR-MAP", "bounded linear map", "pemetaan linear terbatas", [], [], "operator theory"),
        ("OPERATOR-NORM", "operator norm", "norma operator", [], [], "operator theory"),
        ("NORM-PRESERVING", "norm preserving", "mempertahankan norma", ["pelestari norma"], [], "maps between normed spaces"),
        ("QUOTIENT-SPACE", "quotient space", "ruang hasil bagi", [], [], "normed-space constructions"),
        ("PRODUCT-SPACE", "product space", "ruang hasil kali", [], [], "normed-space constructions"),
        ("COPRODUCT", "coproduct", "koproduk", [], [], "categorical normed-space constructions"),
        ("NET", "net", "jaring", [], [], "topology"),
        ("DIRECTED-SET", "directed set", "himpunan terarah", [], [], "nets and topology"),
        ("SUBNET", "subnet", "subjaring", [], [], "nets and topology"),
        ("CLOSURE", "closure", "tutupan", [], ["penutupan"], "topology and convexity"),
        ("INTERIOR", "interior", "interior", [], [], "topology"),
        ("CONTINUITY", "continuity", "kekontinuan", [], ["kontinuitas"], "whole edition"),
        ("FUNCTIONAL-EXTENSION", "extension", "perpanjangan", [], ["perluasan"], "extension of functionals"),
        ("HAUSDORFF", "Hausdorff", "Hausdorff", [], [], "topology"),
        ("COMPACT", "compact", "kompak", [], [], "topology"),
        ("HAHN-BANACH-THEOREM", "Hahn--Banach theorem", "teorema Hahn--Banach", [], [], "functional analysis"),
        ("SCALAR-VALUED", "scalar-valued", "bernilai skalar", [], [], "function spaces and operators"),
    ]
    return [
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "term",
            "id": f"TERM-{stable_id}",
            "source_term": source_term,
            "locale": "id-ID",
            "preferred": preferred,
            "variants": variants,
            "rejected": rejected,
            "scope": scope,
            "evidence": "FAOA-2015-CH03 and backend/index_terms.csv",
        }
        for stable_id, source_term, preferred, variants, rejected, scope in specifications
    ]


def prior_label_map() -> dict[str, str]:
    records = [json.loads(line) for line in locked_prefix("semantic_units.jsonl").splitlines()]
    return {
        record["source_local_id"]: record["id"]
        for record in records
        if record.get("source_local_id")
    }


def main() -> None:
    source_bytes = SOURCE_PATH.read_bytes()
    target_bytes = TARGET_PATH.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha(source_bytes)) != (
        SOURCE_SIZE,
        SOURCE_LINES,
        SOURCE_SHA,
    ):
        raise ValueError("Chapter 3 source authority changed")
    if (len(target_bytes), len(target_bytes.splitlines()), sha(target_bytes)) != (
        TARGET_SIZE,
        TARGET_LINES,
        TARGET_SHA,
    ):
        raise ValueError("finalized Chapter 3 target changed")
    source = source_bytes.decode(SOURCE_ENCODING)
    target = target_bytes.decode(TARGET_ENCODING)

    # Fail before the first write if any source, evidence, prefix, or unit
    # replacement boundary differs from the finalized state.
    verify_evidence()
    for name in PREFIX_LOCKS:
        locked_prefix(name)
    unit_boundaries()

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if len(source_anchors) != 185 or [ch01.anchor_signature(a) for a in source_anchors] != [
        ch01.anchor_signature(a) for a in target_anchors
    ]:
        raise ValueError("Chapter 3 semantic anchor topology differs")

    source_labels = ch01.macro_occurrences(source, "label")
    target_labels = ch01.macro_occurrences(target, "label")
    if len(source_labels) != 91 or [x["argument"] for x in source_labels] != [
        x["argument"] for x in target_labels
    ]:
        raise ValueError("Chapter 3 label sequence differs")

    semantic_units: list[dict] = []
    segment_records: list[dict] = []
    relations: list[dict] = []
    anchor_ids: list[str] = []
    label_to_id: dict[str, str] = {}
    current_section = CHAPTER_ID
    current_section_by_anchor: list[str] = []
    section_number = 0
    node_number = 0

    for source_anchor, target_anchor in zip(source_anchors, target_anchors):
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
        if source_anchor.get("label"):
            label_to_id[source_anchor["label"]] = unit_id
        if source_anchor["anchor_type"] == "chapter":
            continue
        source_fragment = ch01.fragment(source, source_anchor["start"], source_anchor["end"], SOURCE_ENCODING)
        target_fragment = ch01.fragment(target, target_anchor["start"], target_anchor["end"], TARGET_ENCODING)
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
                "source_path": "source/upstream/normlinspaces.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_fragment_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/normlinspaces-id.tex",
                "target_line_start": target_fragment["line_start"],
                "target_line_end": target_fragment["line_end"],
                "target_fragment_sha256": target_fragment["sha256"],
                "source_local_id": source_anchor.get("label"),
                "source_title_tex": source_anchor.get("title"),
                "target_title_tex": target_anchor.get("title"),
                "locale": "id-ID",
                "translation_state": TRANSLATION_STATE,
                "qa_state": QA_STATE,
                "rights_id": RIGHTS,
            }
        )
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-CONTAINS-{len(relations)+1:04d}",
                "relation_type": "contains",
                "from_id": parent_id,
                "to_id": unit_id,
            }
        )
    if (len(semantic_units), section_number, node_number) != (184, 8, 176):
        raise ValueError("Chapter 3 semantic-unit topology invariant failed")

    source_parts: list[tuple[int, int, str, str]] = []
    target_parts: list[tuple[int, int, str, str]] = []
    previous_source = previous_target = 0
    previous_parent = CHAPTER_ID
    for index, (source_anchor, target_anchor, unit_id) in enumerate(
        zip(source_anchors, target_anchors, anchor_ids)
    ):
        if source_anchor["start"] > previous_source or target_anchor["start"] > previous_target:
            source_raw = ch01.active_same_length(source[previous_source : source_anchor["start"]]).strip()
            target_raw = ch01.active_same_length(target[previous_target : target_anchor["start"]]).strip()
            if source_raw or target_raw:
                source_parts.append((previous_source, source_anchor["start"], "prose", previous_parent))
                target_parts.append((previous_target, target_anchor["start"], "prose", previous_parent))
        role = "title" if source_anchor["anchor_type"] in {"chapter", "section"} else "semantic_environment"
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
    if len(source_parts) != 228 or len(target_parts) != 228:
        raise ValueError("Chapter 3 source/target segment count differs from 228")

    for number, (source_part, target_part) in enumerate(zip(source_parts, target_parts), 1):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if role != target_role or parent_id != target_parent:
            raise ValueError("Chapter 3 source/target segment role differs")
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
                "source_path": "source/upstream/normlinspaces.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_bytes": source_fragment["bytes"],
                "source_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/normlinspaces-id.tex",
                "target_line_start": target_fragment["line_start"],
                "target_line_end": target_fragment["line_end"],
                "target_bytes": target_fragment["bytes"],
                "target_sha256": target_fragment["sha256"],
                "source_edition_id": EDITION,
                "target_edition_id": TARGET_EDITION,
                "locale": "id-ID",
                "translation_state": TRANSLATION_STATE,
                "qa_state": QA_STATE,
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
                    "id": f"{CHAPTER_ID}-REL-PRECEDES-{number-1:04d}",
                    "relation_type": "precedes",
                    "from_id": f"{CHAPTER_ID}-SEG-{number-1:04d}",
                    "to_id": segment_id,
                }
            )

    source_refs = ch01.macro_occurrences(source, "ref")
    target_refs = ch01.macro_occurrences(target, "ref")
    expected_target_refs = [x["argument"] for x in source_refs if x["argument"] != "exam_ran_nonclosed"]
    if len(source_refs) != 47 or len(target_refs) != 46 or [x["argument"] for x in target_refs] != expected_target_refs:
        raise ValueError("Chapter 3 ref sequence differs")
    future_refs = re.findall(r"\\futurexref\{([^{}]+)\}\{([^{}]+)\}", ch01.active_same_length(target))
    if future_refs != [("5.2.14", "exam_ran_nonclosed")]:
        raise ValueError("Chapter 3 futurexref endpoint differs")

    prior_labels = prior_label_map()
    reference_counts = defaultdict(int)
    for number, occurrence in enumerate(source_refs, 1):
        label = occurrence["argument"]
        if label in label_to_id:
            to_id = label_to_id[label]
            resolution = "local"
            target_surface = "ref"
        elif label in prior_labels:
            to_id = prior_labels[label]
            resolution = "admitted_prior_unit"
            target_surface = "ref"
        elif label == "exam_ran_nonclosed":
            to_id = f"ERDMAN-FAOA-2015-LABEL-{label}"
            resolution = "pending_later_source_unit"
            target_surface = "futurexref"
        else:
            raise ValueError(f"unexpected unresolved Chapter 3 reference: {label}")
        reference_counts[resolution] += 1
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}",
                "relation_type": "xref",
                "from_id": ch01.containing_segment(segment_records, occurrence["start"], "source"),
                "to_id": to_id,
                "source_local_id": label,
                "resolution": resolution,
                "target_surface": target_surface,
            }
        )
    if dict(reference_counts) != {"local": 39, "admitted_prior_unit": 7, "pending_later_source_unit": 1}:
        raise ValueError(f"Chapter 3 reference-resolution counts changed: {dict(reference_counts)}")

    source_eqrefs = ch01.macro_occurrences(source, "eqref")
    target_eqrefs = ch01.macro_occurrences(target, "eqref")
    if [x["argument"] for x in source_eqrefs] != ["eq_HBTI"] or [x["argument"] for x in target_eqrefs] != ["eq_HBTI"]:
        raise ValueError("Chapter 3 eqref sequence differs")
    eqref = source_eqrefs[0]
    relations.append(
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-EQREF-0001",
            "relation_type": "xref",
            "from_id": ch01.containing_segment(segment_records, eqref["start"], "source"),
            "to_id": label_to_id["eq_HBTI"],
            "source_local_id": "eq_HBTI",
            "resolution": "local",
            "target_surface": "eqref",
        }
    )

    source_cites = ch01.macro_occurrences(source, "cite")
    target_cites = ch01.macro_occurrences(target, "cite")
    if len(source_cites) != 6 or [x["argument"] for x in source_cites] != [x["argument"] for x in target_cites]:
        raise ValueError("Chapter 3 citation sequence differs")
    cite_key_count = 0
    for number, occurrence in enumerate(source_cites, 1):
        for key in [item.strip() for item in occurrence["argument"].split(",")]:
            cite_key_count += 1
            relations.append(
                {
                    "schema": SCHEMA,
                    "schema_version": VERSION,
                    "record_type": "relation",
                    "id": f"{CHAPTER_ID}-REL-CITE-{number:04d}-{key}",
                    "relation_type": "cites",
                    "from_id": ch01.containing_segment(segment_records, occurrence["start"], "source"),
                    "to_id": f"ERDMAN-FAOA-BIB-{key}",
                    "source_local_id": key,
                }
            )
    if cite_key_count != 6:
        raise ValueError("Chapter 3 citation-key count changed")

    previous_statement: str | None = None
    hint_ids_by_statement: dict[str, list[str]] = defaultdict(list)
    proof_relations = 0
    for record in semantic_units:
        if record["unit_kind"] != "proof":
            previous_statement = record["id"]
            continue
        if previous_statement is None or "Hint for proof" not in (record.get("source_title_tex") or ""):
            raise ValueError("Chapter 3 proof-hint topology changed")
        proof_relations += 1
        hint_ids_by_statement[previous_statement].append(record["id"])
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-HINTS-{proof_relations:04d}",
                "relation_type": "hints",
                "from_id": record["id"],
                "to_id": previous_statement,
            }
        )
    if proof_relations != 10 or len(relations) != 703:
        raise ValueError(f"Chapter 3 relation invariant failed: {len(relations)}")

    source_terms = ch01.macro_occurrences(source, "index")
    target_terms = ch01.macro_occurrences(target, "index")
    operator_shape = lambda value: (value.count("@"), value.count("!"), value.count("|"))
    if len(source_terms) != 344 or len(target_terms) != 344 or [
        operator_shape(x["argument"]) for x in source_terms
    ] != [operator_shape(x["argument"]) for x in target_terms]:
        raise ValueError("Chapter 3 MakeIndex topology differs")
    term_buffer = io.StringIO(newline="")
    term_writer = csv.writer(term_buffer, lineterminator="\n")
    for number, (source_term, target_term) in enumerate(zip(source_terms, target_terms), 1):
        term_writer.writerow(
            [
                f"{CHAPTER_ID}-TERM-OCC-{number:04d}",
                ch01.containing_segment(segment_records, source_term["start"], "source"),
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

    source_math = ch03_math.extract_math(source, SOURCE_ENCODING)
    target_math = ch03_math.extract_math(target, TARGET_ENCODING)
    if (len(source_math), len(target_math)) != (1414, 1414):
        raise ValueError("Chapter 3 math-surface count changed")
    if [x["delimiter"] for x in source_math] != [x["delimiter"] for x in target_math]:
        raise ValueError("Chapter 3 math delimiter topology changed")
    matcher = difflib.SequenceMatcher(
        a=[ch03_math.math_key(x["normalized"]) for x in source_math],
        b=[ch03_math.math_key(x["normalized"]) for x in target_math],
        autojunk=False,
    )
    deviations = [opcode for opcode in matcher.get_opcodes() if opcode[0] != "equal"]
    if deviations != EXPECTED_MATH_DEVIATIONS:
        raise ValueError(f"unexpected Chapter 3 math deviations: {deviations}")

    formula_records: list[dict] = []
    exact_formula_count = 0
    non_equal_map_ids: list[str] = []
    for tag, source_start, source_end, target_start, target_end in matcher.get_opcodes():
        if tag == "equal":
            for source_index, target_index in zip(range(source_start, source_end), range(target_start, target_end)):
                map_id = f"{CHAPTER_ID}-MATHMAP-{len(formula_records)+1:04d}"
                exact_formula_count += 1
                formula_records.append(
                    {
                        "schema": SCHEMA,
                        "schema_version": VERSION,
                        "record_type": "formula_map",
                        "id": map_id,
                        "alignment": "preserved_exact_after_text_aware_whitespace_normalization",
                        "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{source_index+1:04d}"],
                        "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{target_index+1:04d}"],
                        "source_lines": [[source_math[source_index]["line_start"], source_math[source_index]["line_end"]]],
                        "target_lines": [[target_math[target_index]["line_start"], target_math[target_index]["line_end"]]],
                        "source_sha256": [source_math[source_index]["sha256"]],
                        "target_sha256": [target_math[target_index]["sha256"]],
                    }
                )
        else:
            map_id = f"{CHAPTER_ID}-MATHMAP-{len(formula_records)+1:04d}"
            non_equal_map_ids.append(map_id)
            formula_records.append(
                {
                    "schema": SCHEMA,
                    "schema_version": VERSION,
                    "record_type": "formula_map",
                    "id": map_id,
                    "alignment": "reviewed_source_correction_or_localized_math_text",
                    "sequence_opcode": tag,
                    "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{i+1:04d}" for i in range(source_start, source_end)],
                    "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{i+1:04d}" for i in range(target_start, target_end)],
                    "source_lines": [[source_math[i]["line_start"], source_math[i]["line_end"]] for i in range(source_start, source_end)],
                    "target_lines": [[target_math[i]["line_start"], target_math[i]["line_end"]] for i in range(target_start, target_end)],
                    "source_sha256": [source_math[i]["sha256"] for i in range(source_start, source_end)],
                    "target_sha256": [target_math[i]["sha256"] for i in range(target_start, target_end)],
                    "qa_state": QA_STATE,
                    "review_witness": "provenance/SOURCE_CORRECTIONS.md and qa/check_ch03_translation.py",
                }
            )
    if (exact_formula_count, len(non_equal_map_ids), len(formula_records)) != (1394, 16, 1410):
        raise ValueError("Chapter 3 formula-map alignment invariant failed")

    exercises: list[dict] = []
    for record in semantic_units:
        if record["unit_kind"] != "exer":
            continue
        number = len(exercises) + 1
        exercises.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "exercise_support",
                "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-{number:03d}",
                "exercise_unit_id": record["id"],
                "source_exercise_order": number,
                "upstream_hint_ids": hint_ids_by_statement.get(record["id"], []),
                "upstream_answer_state": "absent",
                "upstream_solution_state": "absent",
                "original_solution_id": f"O001-{CHAPTER_ID}-EX-{number:03d}-SOLUTION",
                "original_solution_state": "queued_in_O001",
                "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0",
                "provenance": "separately_authored_not_Erdman",
            }
        )
    if len(exercises) != 7 or any(x["upstream_hint_ids"] for x in exercises):
        raise ValueError("Chapter 3 exercise-support topology changed")

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
    append_jsonl("artifacts.jsonl", artifact_records())
    append_jsonl("qa_events.jsonl", qa_records(non_equal_map_ids))
    append_jsonl("corrections.jsonl", correction_records())
    append_jsonl("terminology.jsonl", terminology_records())

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
                "eqrefs": len(source_eqrefs),
                "cites": cite_key_count,
                "index_terms": len(source_terms),
                "source_math": len(source_math),
                "target_math": len(target_math),
                "exact_math": exact_formula_count,
                "formula_map_records": len(formula_records),
                "exercises": len(exercises),
                "corrections": len(correction_records()),
                "terminology_records": len(terminology_records()),
                "artifacts": len(artifact_records()),
                "qa_events": len(qa_records(non_equal_map_ids)),
                "receipt_document_state": "present",
                "translation_state": TRANSLATION_STATE,
                "qa_state": QA_STATE,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
