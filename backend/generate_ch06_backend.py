#!/usr/bin/env python3
"""Append deterministic Chapter 6 backend records after locked Chapters 1--5.

Chapter 1--5 projections are immutable byte prefixes. Chapter 6 is admitted:
its source/target checker, deterministic build, public reader/render evidence,
formal visual/accessibility audit, rights/privacy closure, and admission
receipt are all hash-bound while semantic accessibility remediation remains a
nonblocking edition-level deliverable.
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
SOURCE_PATH = ROOT / "source" / "upstream" / "Banach_spaces.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "Banach_spaces-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH06"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
ADMISSION_QA_ID = "QA-CH06-ADMISSION-20260822"

# Frozen source/target and currently available cumulative evidence.
SOURCE_SIZE = 79_549
SOURCE_LINES = 1_605
SOURCE_SHA = "0f401d088ec3e2d3f2ca4dafa2595a7f0049193a097b6b27af7b247fd433df51"
TARGET_SIZE = 82_940
TARGET_LINES = 1_569
TARGET_SHA = "ca32547e4b47af3444d454476beac71ad8870e88b436dc008e1cb5dbb6755e9c"
MASTER_SIZE = 9_660
MASTER_LINES = 333
MASTER_SHA = "92ab981f81488472f2c45271727b6652bfa62227533107725bff08f4416e738a"
PDF_SIZE = 1_468_946
PDF_PAGES = 114
PDF_SHA = "93cfdf76515205ca259c91537a58cfa2b0ae7cab67e4b1b818ac9f5784aaa55c"
CHECKER_SIZE = 15_728
CHECKER_SHA = "88412b9799d25e3342894dfb2ecba7e3a90d59232c837ef6d0913689c6778391"
BUILD_LOG_SIZE = 46_285
BUILD_LOG_SHA = "d3f234b73aa71121a463b752dd68fa558309ad2056df31d956c2e060814bfeef"
LEDGER_SIZE = 20_716
LEDGER_SHA = "7de8a5892b865af84c9f5d1d4c37ec6b3112b3e099685dae243108006dc94b01"
LEDGER_PRIOR_SIZE = 16_450
LEDGER_PRIOR_SHA = "2408e045efb307602fbe8540efcb6307944d01d7ace610d78e4341856a0e35b7"
LEDGER_SECTION_SIZE = 4_266
LEDGER_SECTION_SHA = "51c26be9d5346ced5707d0ce91e2ed27f313c60666aab81155dafd572cde2118"
BUILD_PDF_PATH = "qa/build-through-ch06-a/functional-analysis-id-through-ch06.pdf"
BUILD_LOG_PATH = "qa/build-through-ch06-a/functional-analysis-id-through-ch06.log"
FINAL_PDF_PATH = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-6.pdf"
RENDER_MANIFEST_PATH = "provenance/CH06_RENDER_MANIFEST.csv"
RENDER_MANIFEST_SIZE = 22_218
RENDER_MANIFEST_SHA = "ba63bc106be574414792ac6bc37b76483a01491822fca4745962e8ff9e407db8"
CONTACT_SHEET_PATH = "provenance/CH06_CONTACT_SHEET.png"
CONTACT_SHEET_SIZE = 3_339_772
CONTACT_SHEET_SHA = "1b5aaad85c2c13651c51d92d6452eb21fca892b641abe87c3991e95bc4f1bedf"
AUDIT_PATH = "qa/CH06_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
AUDIT_SIZE = 5_197
AUDIT_SHA = "3da448996dba97de722ccc48eaa7590a5a9d2f462dcaa4766aecd153139d528b"
RECEIPT_PATH: str | None = "provenance/CH06_BUILD_AND_QA_RECEIPT.md"
RECEIPT_SIZE: int | None = 9_867
RECEIPT_LINES = 178
RECEIPT_SHA: str | None = "acc110923270c2918ca7aa1a6a2c839ae4c99504133e60c20d44a906b5830293"

PREFIX_LOCKS = {
    "semantic_units.jsonl": (510448, "566655e3f1a662b94156a4316d2915f9d332948e60ab7f6ee337ebdc1d1287ce"),
    "segments.jsonl": (584376, "8e474b281db34de922c5fddb017ab6229bba5f6538acf1170c63ef382e854ade"),
    "relations.jsonl": (679917, "d0bc5aecb93cdef3b0c8b8727f2b4414187119d45b6cee7fbe1c4cce8168c0ef"),
    "formula_map.jsonl": (2482098, "4864f830135cb60bd00144eae55e5d93f093cd3c6c01ad2474d092faa77ed22e"),
    "exercise_support.jsonl": (13689, "5f77abb0d5b396a3e747d5906a750acac1b0c200c3858aeebc93581f487a704b"),
    "index_terms.csv": (257545, "99e0e2354f6866448f1b9e0c1bc5ea8357bfa130e8fad72efb7a2dddf30ad1c6"),
    "artifacts.jsonl": (18795, "cdb9459ce39642e8a9199c7a16e2e8bcb9e368722e187e01c13103cb5302f7fa"),
    "qa_events.jsonl": (28862, "fc69b8098bd3acd909e665a17ec40b7a20208fe14d74e8ac7b84dba0845033c8"),
    "corrections.jsonl": (63360, "770b70c91d7dd85801059e4add075961270689f94a63fa96b1c2ae753461f275"),
    "terminology.jsonl": (57228, "255890655e18f76ca4df8d3a9e02180b8fa99aa51129b3c9e73290b75f8f3a21"),
}
UNIT_PREFIX_LOCK = (
    6_179,
    "06bd36d86a525d3e0669081e2a3b9a41e6ea826ac21317778028eab55f5402d7",
)
UNIT_SUFFIX_LOCK = (
    5_511,
    "2bd13cb93dffbaa5903d15779ec5191ad22b1c9a7b6dd52235edd50f8f5613b1",
)

PUBLIC_EVIDENCE_LOCKS = {
    "source/id-ID/Banach_spaces-id.tex": (TARGET_SIZE, TARGET_SHA),
    "source/id-ID/functional-analysis-id-through-ch06.tex": (MASTER_SIZE, MASTER_SHA),
    "qa/check_ch06_translation.py": (CHECKER_SIZE, CHECKER_SHA),
    FINAL_PDF_PATH: (PDF_SIZE, PDF_SHA),
    RENDER_MANIFEST_PATH: (RENDER_MANIFEST_SIZE, RENDER_MANIFEST_SHA),
    CONTACT_SHEET_PATH: (CONTACT_SHEET_SIZE, CONTACT_SHEET_SHA),
    AUDIT_PATH: (AUDIT_SIZE, AUDIT_SHA),
    "provenance/SOURCE_CORRECTIONS.md": (LEDGER_SIZE, LEDGER_SHA),
}
LOCAL_EVIDENCE_LOCKS = {
    BUILD_PDF_PATH: (PDF_SIZE, PDF_SHA),
    BUILD_LOG_PATH: (BUILD_LOG_SIZE, BUILD_LOG_SHA),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def receipt_bound() -> bool:
    values = (RECEIPT_PATH, RECEIPT_SIZE, RECEIPT_SHA)
    return all(value is not None for value in values)


def admission_fields() -> dict[str, object]:
    fields: dict[str, object] = {
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present" if receipt_bound() else "pending",
    }
    if receipt_bound():
        fields |= {
            "receipt_path": RECEIPT_PATH,
            "receipt_sha256": RECEIPT_SHA,
        }
    return fields


def locked_prefix(name: str) -> bytes:
    size, expected_sha = PREFIX_LOCKS[name]
    data = (BACKEND / name).read_bytes()
    if len(data) < size:
        raise ValueError(f"{name} is shorter than its locked Chapter 1--5 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha or not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1--5 prefix changed")
    return prefix


def append_jsonl(name: str, records: list[dict]) -> None:
    suffix = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")
    (BACKEND / name).write_bytes(locked_prefix(name) + suffix)


def verify_evidence() -> None:
    for relative_path, (size, expected_sha) in PUBLIC_EVIDENCE_LOCKS.items():
        data = (ROOT / relative_path).read_bytes()
        if relative_path == "provenance/SOURCE_CORRECTIONS.md":
            if len(data) < size or sha(data[:size]) != expected_sha:
                raise ValueError("Chapter 6 correction-ledger prefix changed")
            if sha(data[:LEDGER_PRIOR_SIZE]) != LEDGER_PRIOR_SHA:
                raise ValueError("Chapter 1--5 correction-ledger prefix changed")
            section = data[LEDGER_PRIOR_SIZE:LEDGER_SIZE]
            if (
                len(section) != LEDGER_SECTION_SIZE
                or not section.startswith(b"## Chapter 6\n")
                or sha(section) != LEDGER_SECTION_SHA
            ):
                raise ValueError("Chapter 6 correction-ledger section changed")
            continue
        if (len(data), sha(data)) != (size, expected_sha):
            raise ValueError(f"Chapter 6 evidence changed: {relative_path}")
    for relative_path, (size, expected_sha) in LOCAL_EVIDENCE_LOCKS.items():
        data = (ROOT / relative_path).read_bytes()
        if (len(data), sha(data)) != (size, expected_sha):
            raise ValueError(f"Chapter 6 fixed-path build evidence changed: {relative_path}")
    if receipt_bound():
        data = (ROOT / str(RECEIPT_PATH)).read_bytes()
        if (len(data), sha(data)) != (RECEIPT_SIZE, RECEIPT_SHA):
            raise ValueError("Chapter 6 admission receipt changed")
        if data.count(b"\n") != RECEIPT_LINES or b"\r" in data:
            raise ValueError("Chapter 6 admission receipt line-ending closure changed")


def unit_boundaries() -> tuple[bytes, bytes]:
    lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    expected_ids = [f"FAOA-2015-CH{number:02d}" for number in range(1, 18)] + [
        "FAOA-ID-BRIDGE-CS"
    ]
    if len(lines) != len(expected_ids) or any(not line.endswith(b"\n") for line in lines):
        raise ValueError("units.jsonl ordered unit closure changed")
    if [json.loads(line)["id"] for line in lines] != expected_ids:
        raise ValueError("units.jsonl ordered unit IDs changed")
    prefix = b"".join(lines[:5])
    middle = lines[5]
    suffix = b"".join(lines[6:])
    if (len(prefix), sha(prefix)) != UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--5 prefix changed")
    if (len(suffix), sha(suffix)) != UNIT_SUFFIX_LOCK:
        raise ValueError("units.jsonl Chapter 7--bridge suffix changed")
    if json.loads(middle).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 6 replacement boundary changed")
    return prefix, suffix


def chapter_six_unit() -> dict:
    state = "admitted" if receipt_bound() else "complete_pending_admission"
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 6,
        "source_path": "Banach_spaces.tex",
        "source_bytes": SOURCE_SIZE,
        "source_lines": SOURCE_LINES,
        "source_sha256": SOURCE_SHA,
        "source_title": "BANACH SPACES",
        "target_path": "source/id-ID/Banach_spaces-id.tex",
        "target_bytes": TARGET_SIZE,
        "target_lines": TARGET_LINES,
        "target_sha256": TARGET_SHA,
        "target_title": "Ruang Banach",
        "course_role": "d20_core",
        "translation_state": state,
        "qa_state": (
            "passed" if receipt_bound()
            else "structural_math_language_build_passed_visual_rights_admission_pending"
        ),
        "source_corrections": 20,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch06.tex",
        "build_master_bytes": MASTER_SIZE,
        "build_master_lines": MASTER_LINES,
        "build_master_sha256": MASTER_SHA,
        "artifact_path": FINAL_PDF_PATH,
        "artifact_bytes": PDF_SIZE,
        "artifact_pages": PDF_PAGES,
        "artifact_sha256": PDF_SHA,
        "artifact_state": "canonical_output_copy_present_and_fixed_path_gate_passed",
        **admission_fields(),
        "publication_state": "pending",
        "rights_id": RIGHTS,
    }


def rewrite_units() -> None:
    prefix, suffix = unit_boundaries()
    encoded = (
        json.dumps(chapter_six_unit(), ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    (BACKEND / "units.jsonl").write_bytes(prefix + encoded + suffix)


def artifact_records() -> list[dict]:
    common_fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "artifact",
        "unit_id": CHAPTER_ID,
        **admission_fields(),
    }
    return [
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH06-TARGET-TEX",
            "artifact_kind": "admitted_translation_source",
            "path": "source/id-ID/Banach_spaces-id.tex",
            "bytes": TARGET_SIZE,
            "lines": TARGET_LINES,
            "sha256": TARGET_SHA,
            "locale": "id-ID",
        },
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH06-MASTER",
            "artifact_kind": "cumulative_TeX_master",
            "path": "source/id-ID/functional-analysis-id-through-ch06.tex",
            "bytes": MASTER_SIZE,
            "lines": MASTER_LINES,
            "sha256": MASTER_SHA,
            "cumulative_through_unit_id": CHAPTER_ID,
            "locale": "id-ID",
        },
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH06-PDF",
            "artifact_kind": "canonical_cumulative_reader_pdf",
            "path": FINAL_PDF_PATH,
            "bytes": PDF_SIZE,
            "sha256": PDF_SHA,
            "pages": PDF_PAGES,
            "page_size": "US Letter",
            "locale": "id-ID",
            "pdf_lang": "id-ID",
            "fixed_path_replays_byte_identical": True,
            "fixed_path_build_path": BUILD_PDF_PATH,
            "final_output_copy_state": "present_byte_identical",
            "publication_state": "pending",
        },
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH06-STRUCTURAL-CHECKER",
            "artifact_kind": "structural_math_language_checker",
            "path": "qa/check_ch06_translation.py",
            "bytes": CHECKER_SIZE,
            "sha256": CHECKER_SHA,
        },
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH06-RENDER-MANIFEST",
            "artifact_kind": "visual_QA_render_manifest",
            "path": RENDER_MANIFEST_PATH,
            "bytes": RENDER_MANIFEST_SIZE,
            "sha256": RENDER_MANIFEST_SHA,
            "rows": PDF_PAGES,
            "render_pages": PDF_PAGES,
            "uniform_pixel_dimensions": "1275x1650",
        },
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH06-CONTACT-SHEET",
            "artifact_kind": "visual_QA_contact_sheet",
            "path": CONTACT_SHEET_PATH,
            "bytes": CONTACT_SHEET_SIZE,
            "sha256": CONTACT_SHEET_SHA,
            "visual_pages": PDF_PAGES,
            "all_pages_inspected": True,
        },
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH06-VISUAL-ACCESSIBILITY-AUDIT",
            "artifact_kind": "visual_accessibility_audit",
            "path": AUDIT_PATH,
            "bytes": AUDIT_SIZE,
            "sha256": AUDIT_SHA,
            "visual_result": "pass",
            "accessibility_gate_result": "pass",
            "fully_accessible_pdf_claim": "fail",
            "tagged_pdf": False,
            "accessibility_remediation_state": "pending_nonblocking",
            "accessible_html_or_tagged_pdf_state": "pending",
        },
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH06-QA-RECEIPT",
            "artifact_kind": "admission_receipt",
            "path": RECEIPT_PATH,
            "bytes": RECEIPT_SIZE,
            "lines": RECEIPT_LINES,
            "sha256": RECEIPT_SHA,
            "decision": "admitted",
        },
        common_fields
        | {
            "id": "ARTIFACT-FAOA-ID-CH06-CORRECTIONS-LEDGER",
            "artifact_kind": "source_corrections_ledger",
            "path": "provenance/SOURCE_CORRECTIONS.md",
            "bytes": LEDGER_SIZE,
            "sha256": LEDGER_SHA,
            "prior_prefix_bytes": LEDGER_PRIOR_SIZE,
            "prior_prefix_sha256": LEDGER_PRIOR_SHA,
            "chapter_section_bytes": LEDGER_SECTION_SIZE,
            "chapter_section_sha256": LEDGER_SECTION_SHA,
            "chapter_correction_count": 20,
        },
    ]


def correction_records() -> list[dict]:
    specifications: list[tuple[str, str, str]] = [
        (
            "Banach_spaces.tex:16,60--62,330,403,423,496,502,684,797,909,912,932,1055,1171",
            "source_language_and_punctuation",
            "Repair comma and parenthesis defects, typos, token boundaries, articles, conjunctions, and punctuation naturally in Indonesian.",
        ),
        (
            "Banach_spaces.tex:128",
            "future_reference_resolution",
            r"Render the Chapter 11 endpoint as \futurexref{11.2.20}{000731}.",
        ),
        (
            "Banach_spaces.tex:213--214",
            "annihilator_empty_subset",
            "Use a subset-of-zero right-hand side in both annihilator biconditionals.",
        ),
        (
            "Banach_spaces.tex:275",
            "weak_star_convergence_wording",
            "State weak-star convergence with the intended pointwise-evaluation wording.",
        ),
        (
            "Banach_spaces.tex:303--305",
            "alaoglu_dual_ball",
            "State Alaoglu's theorem for the closed unit ball of the dual space V*.",
        ),
        (
            "Banach_spaces.tex:396",
            "unbound_sequence_term",
            "Replace the unbound w_o token by w_0.",
        ),
        (
            "Banach_spaces.tex:407--410",
            "category_index",
            "Replace BAN_1 by BAN_infty in the category notation and index entry.",
        ),
        (
            "Banach_spaces.tex:476",
            "environment_kind",
            "Refer to the labelled source environment as an example, not an exercise.",
        ),
        (
            "Banach_spaces.tex:546--549",
            "proof_hint_markup",
            "Normalize the emphasized proof-hint heading markup.",
        ),
        (
            "Banach_spaces.tex:661--665",
            "undefined_ambient_algebra",
            "Bind the ambient Banach algebra A before using it.",
        ),
        (
            "Banach_spaces.tex:924--925",
            "sequence_space_and_norm_limit",
            "Retain c and l_infty as the intended sequence spaces and retain limit 1.",
        ),
        (
            "Banach_spaces.tex:955",
            "undefined_ambient_banach_space",
            "Bind the ambient Banach space B.",
        ),
        (
            "Banach_spaces.tex:1205",
            "subspace_order_symbol",
            "Replace preceq by preccurlyeq for the subspace order.",
        ),
        (
            "Banach_spaces.tex:1253",
            "functor_morphism_linearity",
            "Specify continuous linear maps as the functor morphisms.",
        ),
        (
            "Banach_spaces.tex:1254",
            "dual_superscript",
            "Restore the superscript in B^*.",
        ),
        (
            "Banach_spaces.tex:1327",
            "ambient_space_name",
            "Use the bound ambient space name B rather than M.",
        ),
        (
            "Banach_spaces.tex:1384",
            "nonempty_baire_hypothesis",
            "Require a nonempty complete metric space in the Baire-category hypothesis.",
        ),
        (
            "Banach_spaces.tex:1447",
            "missing_modulus",
            "Restore the modulus around a**(f).",
        ),
        (
            "Banach_spaces.tex:1490--1495",
            "piecewise_right_delimiter",
            "Use a right-dot delimiter rather than an unmatched right brace.",
        ),
        (
            "Banach_spaces.tex:1566,1574",
            "operator_topology_index_sort_keys",
            "Give the strong and uniform operator-topology entries distinct sort keys.",
        ),
    ]
    if len(specifications) != 20:
        raise ValueError("Chapter 6 correction specification count changed")
    fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "correction",
        "unit_id": CHAPTER_ID,
        "target_disposition": "corrected",
        "ledger_path": "provenance/SOURCE_CORRECTIONS.md",
        "ledger_sha256": LEDGER_SHA,
        "ledger_section_sha256": LEDGER_SECTION_SHA,
        **admission_fields(),
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


# One row per distinct raw source \df hook, in first-occurrence order.
TERM_SPECS: list[tuple[str, str, str]] = [
    ("TERM-ADJOINT", "adjoint", "adjoin"),
    ("TERM-SECOND-DUAL", "second dual", "dual kedua"),
    ("TERM-SECOND-DUAL-FUNCTOR", "second dual functor", "funktor dual kedua"),
    ("TERM-NATURAL-TRANSFORMATION", "natural transformation", "transformasi alami"),
    ("TERM-NATURAL-EQUIVALENCE", "natural equivalence", "ekuivalensi alami"),
    ("TERM-NATURAL-EMBEDDING", "natural embedding", "pembenaman alami"),
    ("TERM-REFLEXIVE", "reflexive", "refleksif"),
    ("TERM-ANNIHILATOR", "annihilator", "anihilator"),
    ("TERM-PRE-ANNIHILATOR", "pre-annihilator", "praanihilator"),
    ("TERM-WEAK-TOPOLOGY", "weak topology", "topologi lemah"),
    ("TERM-WEAK-STAR-TOPOLOGY", r"$w^*$-topology", r"topologi-$w^*$"),
    ("TERM-UNIVERSAL", "universal", "universal"),
    ("TERM-OPEN", "open", "terbuka"),
    ("TERM-BOUNDED-AWAY-FROM-ZERO", "bounded away from zero", "terbatas jauh dari nol"),
    ("TERM-BOUNDED-BELOW", "bounded below", "terbatas dari bawah"),
    ("TERM-IDEMPOTENT", "idempotent", "idempoten"),
    ("TERM-EXACT-AT", "exact at", "eksak di"),
    ("TERM-EXACT", "exact", "eksak"),
    ("TERM-SHORT-EXACT-SEQUENCE", "short exact sequence", "barisan eksak pendek"),
    ("TERM-COKERNEL", "cokernel", "kokernel"),
    ("TERM-SCHAUDER-BASIS", "Schauder basis", "basis Schauder"),
    ("TERM-STANDARD", "standard", "standar"),
    ("TERM-USUAL", "usual", "biasa"),
    ("TERM-BASIS-VECTORS", "basis vectors", "vektor-vektor basis"),
    ("TERM-LOCALLY-COMPACT", "locally compact", "kompak lokal"),
    ("TERM-PROJECTION", "projection", "proyeksi"),
    (
        "TERM-PROJECTION-ALONG-KERNEL-ONTO-RANGE",
        r"along $\ker E$ onto $\ran E$",
        r"pada $\ran E$ sepanjang $\ker E$",
    ),
    ("TERM-COMPLEMENTED", "complemented", "terkomplemen"),
    (
        "TERM-BANACH-SPACE-COMPLEMENT",
        "(Banach space) complement",
        "komplemen (ruang Banach)",
    ),
    ("TERM-COMPLEMENTARY", "complementary", "komplementer"),
    ("TERM-CODIMENSION", "codimension", "kodimensi"),
    ("TERM-POINTWISE-BOUNDED", "pointwise bounded", "terbatas titik demi titik"),
    ("TERM-UNIFORMLY-BOUNDED", "uniformly bounded", "terbatas seragam"),
    ("TERM-WEAKLY-BOUNDED", "weakly bounded", "terbatas secara lemah"),
    ("TERM-WEAKLY-CAUCHY", "weakly Cauchy", "Cauchy secara lemah"),
    ("TERM-CONVERGE-WEAKLY", "converges weakly", "konvergen secara lemah"),
    (
        "TERM-WEAKLY-SEQUENTIALLY-COMPLETE",
        "weakly sequentially complete",
        "lengkap sekuensial secara lemah",
    ),
    (
        "TERM-CONVERGES-IN-WEAK-OPERATOR-TOPOLOGY",
        "converges in the weak operator topology",
        "konvergen dalam topologi operator lemah",
    ),
    (
        "TERM-BOUNDED-IN-WEAK-OPERATOR-TOPOLOGY",
        "bounded in the weak operator topology",
        "terbatas dalam topologi operator lemah",
    ),
    ("TERM-CONVERGE-STRONGLY", "converges strongly", "konvergen secara kuat"),
    (
        "TERM-CONVERGES-IN-STRONG-OPERATOR-TOPOLOGY",
        "converges in the strong operator topology",
        "konvergen dalam topologi operator kuat",
    ),
    ("TERM-UNIFORM-CONVERGENCE", "uniform convergence", "konvergensi seragam"),
    (
        "TERM-CONVERGENCE-IN-UNIFORM-OPERATOR-TOPOLOGY",
        "convergence in the uniform operator topology",
        "konvergensi dalam topologi operator seragam",
    ),
]
EXISTING_TERM_IDS = {
    "adjoint": "TERM-ADJOINT",
    "weak topology": "TERM-WEAK-TOPOLOGY",
    "bounded away from zero": "TERM-BOUNDED-AWAY-FROM-ZERO",
    "bounded below": "TERM-BOUNDED-BELOW",
    "standard": "TERM-STANDARD",
    "usual": "TERM-USUAL",
    "projection": "TERM-PROJECTION",
    "codimension": "TERM-CODIMENSION",
    "converges weakly": "TERM-CONVERGE-WEAKLY",
    "converges strongly": "TERM-CONVERGE-STRONGLY",
}


def term_id_map() -> dict[str, str]:
    mapping = {source: stable_id for stable_id, source, _ in TERM_SPECS}
    if len(mapping) != 43:
        raise ValueError("Chapter 6 distinct defined-term inventory changed")
    return mapping


def terminology_records() -> list[dict]:
    records: list[dict] = []
    emitted: set[str] = set()
    for stable_id, source_term, preferred in TERM_SPECS:
        if source_term in EXISTING_TERM_IDS or stable_id in emitted:
            continue
        emitted.add(stable_id)
        records.append(
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
                "scope": "Banach spaces, duality, and operator topologies",
                "evidence": "FAOA-2015-CH06 final target source/id-ID/Banach_spaces-id.tex; backend/index_terms.csv; qa/check_ch06_translation.py",
            }
        )
    if len(records) != 33:
        raise ValueError(f"Chapter 6 new terminology record count changed: {len(records)}")
    return records


def qa_records(formula_summary: dict[str, object]) -> list[dict]:
    typed_ids = [
        "QA-CH06-STRUCTURAL-20260822",
        "QA-CH06-MATH-20260822",
        "QA-CH06-LANGUAGE-20260822",
        "QA-CH06-BUILD-20260822",
        "QA-CH06-VISUAL-20260822",
        "QA-CH06-ACCESSIBILITY-20260822",
        "QA-CH06-RIGHTS-20260822",
    ]
    common_fields = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "timestamp": "2026-08-22",
        "responsible_workflow": "Codex",
        **admission_fields(),
    }
    return [
        common_fields
        | {
            "id": typed_ids[0],
            "qa_type": "unit_structural",
            "result": "pass",
            "witness": "qa/check_ch06_translation.py",
            "witness_sha256": CHECKER_SHA,
            "semantic_anchors": 167,
            "semantic_units": 166,
            "segments": 206,
            "all_environment_pairs": 178,
            "semantic_environment_anchors": 159,
            "sections": 7,
            "labels": 56,
            "references": 80,
            "ordinary_target_references": 79,
            "future_target_references": 1,
            "equation_references": 2,
            "citations": 13,
            "index_terms": 155,
            "defined_terms": 47,
            "exercise_environments": 6,
            "proof_environments": 29,
            "proof_hints": 28,
            "ordinary_proofs": 1,
        },
        common_fields
        | {
            "id": typed_ids[1],
            "qa_type": "unit_mathematical",
            "result": "pass",
            "witness": "qa/check_ch06_translation.py",
            "witness_sha256": CHECKER_SHA,
            "source_math_surfaces": 1_155,
            "target_math_surfaces": 1_156,
            **formula_summary,
            "classified_math_edit_blocks": 22,
            "unexplained_deltas": 0,
            "extractor": "backend/ch03_math.py",
            "extractor_sha256": "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3",
        },
        common_fields
        | {
            "id": typed_ids[2],
            "qa_type": "unit_language",
            "result": "pass",
            "witness": "qa/check_ch06_translation.py",
            "witness_sha256": CHECKER_SHA,
            "severity_counts": {"P1": 0, "P2": 0, "P3": 0},
            "unintended_english_prose": 0,
            "placeholders": 0,
            "terminology_reconciled": True,
        },
        common_fields
        | {
            "id": typed_ids[3],
            "qa_type": "cumulative_build",
            "result": "pass",
            "witness": FINAL_PDF_PATH,
            "witness_sha256": PDF_SHA,
            "master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH06-MASTER",
            "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH06-PDF",
            "fixed_path_clean_builds_byte_identical": True,
            "fixed_path_build_pdf_path": BUILD_PDF_PATH,
            "final_output_copy_state": "present_byte_identical",
            "pages": PDF_PAGES,
            "local_build_log_path": BUILD_LOG_PATH,
            "local_build_log_bytes": BUILD_LOG_SIZE,
            "local_build_log_sha256": BUILD_LOG_SHA,
            "local_build_log_publication_state": "excluded_ignored_build_intermediate",
        },
        common_fields
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
            "rendered_png_bytes": 40_224_010,
            "word_boxes": 54_378,
            "out_of_bounds_word_boxes": 0,
            "intentional_blank_versos": [20, 48, 78, 100, 102],
            "visual_defects": 0,
            "render_manifest_state": "present",
            "render_manifest_sha256": RENDER_MANIFEST_SHA,
            "contact_sheet_state": "present",
            "contact_sheet_sha256": CONTACT_SHEET_SHA,
            "render_manifest_artifact_id": "ARTIFACT-FAOA-ID-CH06-RENDER-MANIFEST",
            "contact_sheet_artifact_id": "ARTIFACT-FAOA-ID-CH06-CONTACT-SHEET",
        },
        common_fields
        | {
            "id": typed_ids[5],
            "qa_type": "cumulative_accessibility",
            "result": "pass",
            "decision": "honest_chapter_boundary_accessibility_pass",
            "witness": AUDIT_PATH,
            "witness_sha256": AUDIT_SHA,
            "visual_accessibility_artifact_id": "ARTIFACT-FAOA-ID-CH06-VISUAL-ACCESSIBILITY-AUDIT",
            "tagged_pdf": False,
            "fully_accessible_pdf_claim": False,
            "unicode_mapped_font_resources": 43,
            "total_font_resources": 43,
            "text_extraction_bytes": 436_932,
            "text_extraction_sha256": "d9fa66b1ec42ede6ab4247f81eb70361c274922cb5d3eeaacf0616fc30235c4c",
            "replacement_characters": 0,
            "resolved_internal_links": 1_500,
            "named_destinations": 1_052,
            "outline_entries": 42,
            "semantic_accessibility_state": "remediation_required",
            "accessibility_remediation_state": "pending_nonblocking",
            "accessible_html_or_tagged_pdf_state": "pending",
            "admission_blocker_for_chapter_boundary": False,
        },
        common_fields
        | {
            "id": typed_ids[6],
            "qa_type": "unit_rights_privacy",
            "result": "pass",
            "decision": "rights_component_privacy_closure_pass",
            "witness": RECEIPT_PATH,
            "witness_sha256": RECEIPT_SHA,
            "rights_id": RIGHTS,
            "attribution_change_notice_sharealike_nonendorsement": "present",
            "excluded_components_absent": True,
            "private_control_paths_absent_from_public_artifacts": True,
            "credential_or_token_residue": 0,
        },
        common_fields
        | {
            "id": ADMISSION_QA_ID,
            "qa_type": "unit_admission",
            "result": "pass" if receipt_bound() else "pending",
            "decision": "admitted" if receipt_bound() else "pending_receipt_and_open_gates",
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
            },
            "all_required_admission_gates": "pass" if receipt_bound() else "pending",
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
    165: f"{CHAPTER_ID}-CORR-003",
    167: f"{CHAPTER_ID}-CORR-003",
    316: f"{CHAPTER_ID}-CORR-006",
    330: f"{CHAPTER_ID}-CORR-007",
    531: f"{CHAPTER_ID}-CORR-010",
    686: f"{CHAPTER_ID}-CORR-011",
    710: f"{CHAPTER_ID}-CORR-012",
    894: f"{CHAPTER_ID}-CORR-013",
    927: f"{CHAPTER_ID}-CORR-015",
    965: f"{CHAPTER_ID}-CORR-016",
    1065: f"{CHAPTER_ID}-CORR-018",
    1093: f"{CHAPTER_ID}-CORR-019",
}
LOCALIZED_KEY_DIFFERENCES = {133, 134, 670, 722, 1091, 1092}
REORDERED_FORMULAS = {834, 857, 906}
TARGET_ONLY_FORMULAS = {531, 710}
CONSOLIDATED_FORMULAS = {686}


def build_math_pairs(source: str, target: str) -> tuple[list[dict], dict[str, object]]:
    source_math = ch03_math.extract_math(source, SOURCE_ENCODING)
    target_math = ch03_math.extract_math(target, TARGET_ENCODING)
    if (len(source_math), len(target_math)) != (1_155, 1_156):
        raise ValueError("Chapter 6 math-surface count changed")
    if ch06check.math_edit_signature(source_math, target_math) != ch06check.EXPECTED_MATH_EDITS:
        raise ValueError("Chapter 6 mathematical edit-block lock changed")
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
    mapping[530] = []
    mapping[685] = [685, 686]
    mapping[709] = []
    mapping[833] = [833]
    mapping[856] = [856]
    mapping[905] = [905]
    if any(value is None for value in mapping):
        raise ValueError("Chapter 6 target formula coverage is incomplete")
    complete_mapping = [value for value in mapping if value is not None]
    used_sources = [index for group in complete_mapping for index in group]
    if sorted(used_sources) != list(range(len(source_math))):
        raise ValueError("Chapter 6 source formula coverage is not one-to-one")

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
        elif key_equal:
            alignment = "localized_math_text_preserved_math_key"
        elif number in LOCALIZED_KEY_DIFFERENCES:
            alignment = "localized_math_key_reviewed"
        elif number in TARGET_ONLY_FORMULAS:
            alignment = "reviewed_target_only_source_correction"
        elif number in CONSOLIDATED_FORMULAS:
            alignment = "reviewed_consolidated_source_correction"
        elif number in CORRECTION_FORMULAS:
            alignment = "reviewed_source_correction"
        else:
            raise ValueError(f"unexpected Chapter 6 formula delta at target {number}")
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
                else "localized_difference"
                if number in LOCALIZED_KEY_DIFFERENCES
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
        elif number in LOCALIZED_KEY_DIFFERENCES:
            record |= {
                "sequence_opcode": "replace",
                "delta_class": "localized_math_text",
                "correction_disposition": "not_a_source_correction",
                "qa_state": "passed",
            }
        elif number in CORRECTION_FORMULAS:
            record |= {
                "sequence_opcode": (
                    "insert"
                    if number in TARGET_ONLY_FORMULAS
                    else "merge"
                    if number in CONSOLIDATED_FORMULAS
                    else "replace"
                ),
                "delta_class": "source_correction",
                "correction_id": CORRECTION_FORMULAS[number],
                "correction_disposition": "corrected",
                "review_witness": "provenance/SOURCE_CORRECTIONS.md and qa/check_ch06_translation.py",
                "qa_state": "passed",
            }
        records.append(record)
    expected_counts = {
        "preserved_exact_after_text_aware_whitespace_normalization": 1_128,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 3,
        "localized_math_text_preserved_math_key": 7,
        "localized_math_key_reviewed": 6,
        "reviewed_source_correction": 9,
        "reviewed_target_only_source_correction": 2,
        "reviewed_consolidated_source_correction": 1,
    }
    if dict(counts) != expected_counts:
        raise ValueError(f"Chapter 6 formula alignment counts changed: {dict(counts)}")
    return records, {
        "exact_normalized_alignments": 1_131,
        "math_key_equal_alignments": 1_138,
        "localized_math_text_alignments": 7,
        "localized_math_key_differences": 6,
        "reviewed_source_correction_maps": 12,
        "target_only_source_corrections": 2,
        "consolidated_source_corrections": 1,
        "localization_phrase_reorderings": 3,
        "formula_map_records": 1_156,
    }


def main() -> None:
    source_bytes = SOURCE_PATH.read_bytes()
    target_bytes = TARGET_PATH.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha(source_bytes)) != (
        SOURCE_SIZE,
        SOURCE_LINES,
        SOURCE_SHA,
    ):
        raise ValueError("Chapter 6 source authority changed")
    if (len(target_bytes), len(target_bytes.splitlines()), sha(target_bytes)) != (
        TARGET_SIZE,
        TARGET_LINES,
        TARGET_SHA,
    ):
        raise ValueError("final Chapter 6 target lock changed")
    source = source_bytes.decode(SOURCE_ENCODING)
    target = target_bytes.decode(TARGET_ENCODING)
    verify_evidence()
    for name in PREFIX_LOCKS:
        locked_prefix(name)
    unit_boundaries()
    checker_run = subprocess.run(
        [sys.executable, str(ROOT / "qa" / "check_ch06_translation.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    checker_result = json.loads(checker_run.stdout)
    if checker_result.get("result") != "pass":
        raise ValueError("Chapter 6 checker did not return its locked pass result")

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if len(source_anchors) != 167 or [
        ch01.anchor_signature(anchor) for anchor in source_anchors
    ] != [ch01.anchor_signature(anchor) for anchor in target_anchors]:
        raise ValueError("Chapter 6 semantic anchor topology differs")
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 56 or [item["argument"] for item in source_labels] != [
        item["argument"] for item in target_labels
    ]:
        raise ValueError("Chapter 6 label sequence differs")

    semantic_units: list[dict] = []
    segment_records: list[dict] = []
    relations: list[dict] = []
    anchor_ids: list[str] = []
    anchor_bounds: dict[str, tuple[int, int]] = {}
    current_section = CHAPTER_ID
    current_section_by_anchor: list[str] = []
    section_number = 0
    node_number = 0
    state = "admitted" if receipt_bound() else "complete_pending_admission"
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
                "source_path": "source/upstream/Banach_spaces.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_fragment_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/Banach_spaces-id.tex",
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
    if (len(semantic_units), section_number, node_number) != (166, 7, 159):
        raise ValueError("Chapter 6 semantic-unit topology invariant failed")

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
    if len(source_parts) != 206 or len(target_parts) != 206:
        raise ValueError("Chapter 6 source/target segment count differs from 206")

    for number, (source_part, target_part) in enumerate(
        zip(source_parts, target_parts, strict=True), 1
    ):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if role != target_role or parent_id != target_parent:
            raise ValueError("Chapter 6 source/target segment role differs")
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
                "source_path": "source/upstream/Banach_spaces.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_bytes": source_fragment["bytes"],
                "source_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/Banach_spaces-id.tex",
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
    if len(local_label_map) != 56:
        raise ValueError("Chapter 6 local label map changed")

    source_refs = common.macro(source, "ref")
    target_refs = common.macro(target, "ref")
    if len(source_refs) != 80 or len(target_refs) != 79:
        raise ValueError("Chapter 6 ordinary reference count changed")
    if [item["argument"] for item in target_refs] != [
        item["argument"] for item in source_refs if item["argument"] != "000731"
    ]:
        raise ValueError("Chapter 6 target ordinary reference sequence changed")
    future_matches = list(
        re.finditer(r"\\futurexref\{([^{}]*)\}\{([^{}]+)\}", ch01.active_same_length(target))
    )
    if [(match.group(1), match.group(2)) for match in future_matches] != [
        ("11.2.20", "000731")
    ]:
        raise ValueError("Chapter 6 futurexref endpoint changed")
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
        elif label == "000731":
            to_id = "ERDMAN-FAOA-2015-LABEL-000731"
            resolution = "pending_later_source_unit"
            target_surface = "futurexref"
        else:
            raise ValueError(f"unexpected unresolved Chapter 6 reference: {label}")
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
        "admitted_prior_unit": 32,
        "local": 47,
        "pending_later_source_unit": 1,
    }:
        raise ValueError(f"Chapter 6 reference-resolution counts changed: {dict(reference_counts)}")

    source_eqrefs = common.macro(source, "eqref")
    target_eqrefs = common.macro(target, "eqref")
    if [item["argument"] for item in source_eqrefs] != [
        "eqn_exactCD_Bbar",
        "eqn_exactCD_Bbar",
    ] or [item["argument"] for item in target_eqrefs] != [
        "eqn_exactCD_Bbar",
        "eqn_exactCD_Bbar",
    ]:
        raise ValueError("Chapter 6 eqref sequence differs")
    for number, occurrence in enumerate(source_eqrefs, 1):
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-EQREF-{number:04d}",
                "relation_type": "xref",
                "from_id": ch01.containing_segment(
                    segment_records, occurrence["start"], "source"
                ),
                "to_id": local_label_map[occurrence["argument"]],
                "source_local_id": occurrence["argument"],
                "resolution": "local",
                "target_surface": "eqref",
            }
        )

    source_cites = common.macro(source, "cite")
    target_cites = common.macro(target, "cite")
    if len(source_cites) != 13 or [item["argument"] for item in source_cites] != [
        item["argument"] for item in target_cites
    ]:
        raise ValueError("Chapter 6 citation sequence differs")
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
    if cite_key_count != 13:
        raise ValueError("Chapter 6 citation-key count changed")

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
            raise ValueError("Chapter 6 proof hint lacks a preceding statement")
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
    if (proof_count, hint_relations) != (29, 28):
        raise ValueError("Chapter 6 proof/proof-hint topology changed")

    source_df = common.macro(source, "df")
    target_df = common.macro(target, "df")
    term_ids = term_id_map()
    if (
        len(source_df) != 47
        or len(target_df) != 47
        or set(term_ids) != {record["argument"] for record in source_df}
    ):
        raise ValueError("Chapter 6 defined-term inventory changed")
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
        len(source_terms) != 155
        or len(target_terms) != 155
        or [common.index_signature(item["argument"]) for item in source_terms]
        != [common.index_signature(item["argument"]) for item in target_terms]
    ):
        raise ValueError("Chapter 6 index-term alignment changed")
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
    expected_inline_hint_lines = {2: 464, 3: 489, 6: 1461}
    for record in semantic_units:
        if record["unit_kind"] != "exer":
            continue
        number = len(exercises) + 1
        start, end = anchor_bounds[record["id"]]
        fragment = source[start:end]
        hint_match = re.search(r"\\emph\{Hint(?:[.:])?\}", fragment)
        hint_line = source.count("\n", 0, start + hint_match.start()) + 1 if hint_match else None
        if hint_line != expected_inline_hint_lines.get(number):
            raise ValueError(f"Chapter 6 exercise {number} inline-hint state changed")
        exercise_record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "exercise_support",
            "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-{number:03d}",
            "exercise_unit_id": record["id"],
            "source_exercise_order": number,
            "upstream_hint_ids": hint_ids_by_statement.get(record["id"], []),
            "upstream_inline_hint_state": "present" if hint_line else "absent",
            "upstream_answer_state": "absent",
            "upstream_solution_state": "absent",
            "original_solution_id": f"O001-{CHAPTER_ID}-EX-{number:03d}-SOLUTION",
            "original_solution_state": "queued_in_O001",
            "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0",
            "provenance": "separately_authored_not_Erdman",
        }
        if hint_line:
            exercise_record["upstream_inline_hint_source_lines"] = [hint_line]
        exercises.append(exercise_record)
    if len(exercises) != 6 or any(record["upstream_hint_ids"] for record in exercises):
        raise ValueError("Chapter 6 exercise-support topology changed")
    if any(
        kind == "begin" and environment in {"answer", "solution"}
        for kind, environment in common.env_sequence(source)
    ):
        raise ValueError("Chapter 6 unexpectedly contains a source answer or solution")

    # Close two append-only pending xrefs from already-admitted chapters.
    for number, (label, pending_relation_id) in enumerate(
        (
            ("C069414", "FAOA-2015-CH02-REL-XREF-0001"),
            ("C067441", "FAOA-2015-CH04-REL-XREF-0034"),
        ),
        1,
    ):
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-RESOLVES-{number:04d}",
                "relation_type": "resolves_pending_reference",
                "from_id": local_label_map[label],
                "to_id": pending_relation_id,
                "source_local_id": label,
                "stable_label_id": f"ERDMAN-FAOA-2015-LABEL-{label}",
                "resolution": "declared_in_current_unit",
            }
        )

    artifacts = artifact_records()
    corrections = correction_records()
    terms = terminology_records()
    qa = qa_records(formula_summary)
    if (len(artifacts), len(corrections), len(terms), len(qa)) != (9, 20, 33, 8):
        raise ValueError("Chapter 6 evidence record counts changed")
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
            "ARTIFACT-FAOA-ID-CH06-TARGET-TEX",
            "ARTIFACT-FAOA-ID-CH06-STRUCTURAL-CHECKER",
        ),
        1,
    ):
        relations.append(
            relation_common
            | {
                "id": f"{CHAPTER_ID}-REL-TERM-EVIDENCE-{number:04d}",
                "relation_type": "terminology_evidence",
                "to_id": artifact_id,
                "evidence_scope": "all Chapter 6 terminology records and occurrences",
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
    if len(relations) != 845:
        raise ValueError(f"Chapter 6 relation invariant failed: {len(relations)}")

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
                "closed_prior_pending_references": 2,
                "eqrefs": len(source_eqrefs),
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
                "receipt_document_state": "present" if receipt_bound() else "pending",
                "translation_state": state,
                "qa_state": chapter_six_unit()["qa_state"],
                **formula_summary,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
