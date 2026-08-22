#!/usr/bin/env python3
"""Append deterministic Chapter 5 backend records after locked Chapters 1--4.

The existing Chapter 1--4 projections are immutable byte prefixes. Chapter 5
is final-shaped while its admission receipt is pending: binding the eventual
receipt changes evidence fields and admission states, never record IDs/counts.
INTERLANGUAGE_BACKEND_DIR permits replay against an isolated backend copy.
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
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BACKEND = Path(os.environ.get("INTERLANGUAGE_BACKEND_DIR", ROOT / "backend")).resolve()
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "qa"))
import generate_ch01_backend as ch01  # noqa: E402
import ch03_math  # noqa: E402
import check_ch05_translation as ch05check  # noqa: E402


SOURCE_PATH = ROOT / "source" / "upstream" / "Hilbert_space_operators.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "Hilbert_space_operators-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH05"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
ADMISSION_QA_ID = "QA-CH05-ADMISSION-20260822"

SOURCE_SIZE = 48838
SOURCE_LINES = 1147
SOURCE_SHA = "93293a89c9a9f34315a43d6f114084490ceb370119fb09aeaccabe634efb96b1"
TARGET_SIZE = 51529
TARGET_LINES = 1147
TARGET_SHA = "323f0b156eb6e945e3b6ed273da298af4e0e2b2d9abb73514a9018cbe0d0b29f"
MASTER_SIZE = 9630
MASTER_LINES = 330
MASTER_SHA = "2b8987e70b08b7b7045b50569667e0ab06634767645401a8c1d95712c48d80e2"
PDF_SIZE = 1271325
PDF_PAGES = 90
PDF_SHA = "850310f11cb7ab8c83cb52347aad43bc311cc1d2a811bef476038c61c8698af0"
CHECKER_SIZE = 15162
CHECKER_SHA = "c04266c3924d7336cec886b687da99db25c4403b8f030ee8fd47e47f2b838e2b"
BUILD_LOG_SIZE = 41858
BUILD_LOG_SHA = "e026c44275a136495843ee3fa04b6e2ce4d12b75bd07612b3fad5b68a8c8d0ed"
RENDER_MANIFEST_SIZE = 8656
RENDER_MANIFEST_SHA = "061bd3b31fcf2518d48fbd797fd85f19a0932fb8ae4f3b252099c7d54f9c2be2"
CONTACT_SIZE = 13365085
CONTACT_SHA = "5a65ee523e93e0c8bc3f34e8891ffc5a1b48547b715d94af38ad512788cf9e71"
AUDIT_SIZE = 5693
AUDIT_SHA = "9b0f638cd7541952bdc3e16e8c9a1ad14db9904e0fc0c5ca46565a99dfc99a03"
PDF_AUDITOR_SIZE = 4765
PDF_AUDITOR_SHA = "7577942fded7863dd0be76b6642ea7236085c338a025dbb6be499e4a9fb01cb3"
LEDGER_SIZE = 16450
LEDGER_SHA = "2408e045efb307602fbe8540efcb6307944d01d7ace610d78e4341856a0e35b7"
LEDGER_SECTION_SHA = "95f76df166278c995fe031f65f1b4dc4a6740b5776f579bd8970faee9b526f79"

# Final admission receipt lock.
RECEIPT_PATH = "provenance/CH05_BUILD_AND_QA_RECEIPT.md"
RECEIPT_SIZE: int | None = 9383
RECEIPT_SHA: str | None = "11ea57ad7a5f73f806846d7303246e7391b7c2aca37ce5a7fc2d53d7013b7ca5"

PREFIX_LOCKS = {
    "semantic_units.jsonl": (393119, "54cca57d75ee8cb8b46ea6ea46876c14207acf2e99a1eee04bd310223320b7d5"),
    "segments.jsonl": (456214, "82f44070f44944e8dd2496e87fe5dfdffbf4cd0d2b5bd71d23447e9e41d09a61"),
    "relations.jsonl": (513115, "ef9b559648ea060c691a242a0ef492437efa5cd087bf57ca659a1be418e67b07"),
    "formula_map.jsonl": (1972193, "7ec7935fc97003a5977b480e4965dea805305a126e9cbf9cf1123bf714f88805"),
    "exercise_support.jsonl": (11665, "3411cc479cfe6ba27396e9e7e05a84f2b95f72e98195bfe3601f4517c11a6b4f"),
    "index_terms.csv": (214509, "74755e7af6c4f1e06200580eb324c56461098d791def101a0a707b767cfb15bb"),
    "artifacts.jsonl": (12956, "90d6b44eb75134ce828a7c5a25657d435dd2a59f941f091485139cabf613d9e2"),
    "qa_events.jsonl": (20773, "36c816002e3a205b70bfdb5845503f598f81021a91b87eaf86bbf461007794fc"),
    "corrections.jsonl": (43201, "7d02b1e02e929cebfbb2c6a3398f74a77c801cd58ed3e8545f9dd9801a995bb2"),
    "terminology.jsonl": (39107, "09bcc4d8bc83505e22c1c13cf33a3fa39ae3384a091224d0e323eac1dd9ed630"),
}
UNIT_PREFIX_LOCK = (
    4769,
    "bf26c0f69bf69b1ef63e785de2c2649424d3aa9f50faebb8043b3b0df51c33c4",
)

PUBLIC_EVIDENCE_LOCKS = {
    "source/id-ID/Hilbert_space_operators-id.tex": (TARGET_SIZE, TARGET_SHA),
    "source/id-ID/functional-analysis-id-through-ch05.tex": (MASTER_SIZE, MASTER_SHA),
    "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf": (
        PDF_SIZE,
        PDF_SHA,
    ),
    "qa/check_ch05_translation.py": (CHECKER_SIZE, CHECKER_SHA),
    "qa/audit_ch05_pdf.py": (PDF_AUDITOR_SIZE, PDF_AUDITOR_SHA),
    "provenance/CH05_RENDER_MANIFEST.csv": (
        RENDER_MANIFEST_SIZE,
        RENDER_MANIFEST_SHA,
    ),
    "provenance/CH05_CONTACT_SHEET.png": (CONTACT_SIZE, CONTACT_SHA),
    "qa/CH05_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md": (AUDIT_SIZE, AUDIT_SHA),
    "provenance/SOURCE_CORRECTIONS.md": (LEDGER_SIZE, LEDGER_SHA),
}
LOCAL_EVIDENCE_LOCKS = {
    "qa/build-through-ch05/functional-analysis-id-through-ch05.log": (
        BUILD_LOG_SIZE,
        BUILD_LOG_SHA,
    )
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def receipt_bound() -> bool:
    return RECEIPT_SIZE is not None and RECEIPT_SHA is not None


def admission_fields() -> dict[str, object]:
    fields: dict[str, object] = {
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present" if receipt_bound() else "pending",
    }
    if receipt_bound():
        fields |= {"receipt_path": RECEIPT_PATH, "receipt_sha256": RECEIPT_SHA}
    return fields


def locked_prefix(name: str) -> bytes:
    size, expected_sha = PREFIX_LOCKS[name]
    data = (BACKEND / name).read_bytes()
    if len(data) < size:
        raise ValueError(f"{name} is shorter than its locked Chapter 1--4 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha or not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1--4 prefix changed")
    return prefix


def append_jsonl(name: str, records: list[dict]) -> None:
    suffix = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")
    (BACKEND / name).write_bytes(locked_prefix(name) + suffix)


def verify_evidence() -> None:
    for relative_path, (size, expected_sha) in (
        PUBLIC_EVIDENCE_LOCKS | LOCAL_EVIDENCE_LOCKS
    ).items():
        data = (ROOT / relative_path).read_bytes()
        if (len(data), sha(data)) != (size, expected_sha):
            raise ValueError(f"Chapter 5 evidence changed: {relative_path}")
    ledger = (ROOT / "provenance" / "SOURCE_CORRECTIONS.md").read_text(
        encoding="utf-8"
    )
    start = ledger.find("## Chapter 5")
    if start < 0 or sha(ledger[start:].encode("utf-8")) != LEDGER_SECTION_SHA:
        raise ValueError("Chapter 5 correction-ledger section changed")
    if receipt_bound():
        data = (ROOT / RECEIPT_PATH).read_bytes()
        if (len(data), sha(data)) != (RECEIPT_SIZE, RECEIPT_SHA):
            raise ValueError("Chapter 5 admission receipt changed")
    elif (ROOT / RECEIPT_PATH).exists():
        raise ValueError("Chapter 5 receipt exists but generator placeholders are unbound")


def unit_boundaries() -> tuple[bytes, bytes]:
    data = (BACKEND / "units.jsonl").read_bytes()
    lines = data.splitlines(keepends=True)
    expected_ids = [f"FAOA-2015-CH{number:02d}" for number in range(1, 18)] + [
        "FAOA-ID-BRIDGE-CS"
    ]
    if len(lines) != len(expected_ids) or any(not line.endswith(b"\n") for line in lines):
        raise ValueError("units.jsonl ordered unit closure changed")
    if [json.loads(line)["id"] for line in lines] != expected_ids:
        raise ValueError("units.jsonl ordered unit IDs changed")
    prefix = b"".join(lines[:4])
    middle = lines[4]
    suffix = b"".join(lines[5:])
    if (len(prefix), sha(prefix)) != UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--4 prefix changed")
    if json.loads(middle).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 5 replacement boundary changed")
    return prefix, suffix


def chapter_five_unit() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 5,
        "source_path": "Hilbert_space_operators.tex",
        "source_bytes": SOURCE_SIZE,
        "source_lines": SOURCE_LINES,
        "source_sha256": SOURCE_SHA,
        "source_title": "HILBERT SPACE OPERATORS",
        "target_path": "source/id-ID/Hilbert_space_operators-id.tex",
        "target_bytes": TARGET_SIZE,
        "target_lines": TARGET_LINES,
        "target_sha256": TARGET_SHA,
        "target_title": "Operator pada Ruang Hilbert",
        "course_role": "D20_core",
        "translation_state": "admitted" if receipt_bound() else "ready_for_admission",
        "qa_state": "passed",
        "source_corrections": 23,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch05.tex",
        "build_master_bytes": MASTER_SIZE,
        "build_master_lines": MASTER_LINES,
        "build_master_sha256": MASTER_SHA,
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf",
        "artifact_bytes": PDF_SIZE,
        "artifact_pages": PDF_PAGES,
        "artifact_sha256": PDF_SHA,
        **admission_fields(),
        "publication_state": "pending",
        "rights_id": RIGHTS,
    }


def rewrite_units() -> None:
    prefix, suffix = unit_boundaries()
    encoded = (
        json.dumps(chapter_five_unit(), ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    (BACKEND / "units.jsonl").write_bytes(prefix + encoded + suffix)


def artifact_records() -> list[dict]:
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "artifact",
        "unit_id": CHAPTER_ID,
        **admission_fields(),
    }
    receipt_artifact: dict[str, object] = common | {
        "id": "ARTIFACT-FAOA-ID-CH05-QA-RECEIPT",
        "artifact_kind": "admission_receipt",
        "intended_path": RECEIPT_PATH,
        "decision": "admitted" if receipt_bound() else "pending_receipt",
    }
    if receipt_bound():
        receipt_artifact |= {
            "path": RECEIPT_PATH,
            "bytes": RECEIPT_SIZE,
            "sha256": RECEIPT_SHA,
        }
    return [
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH05-TARGET-TEX",
            "artifact_kind": "admitted_translation_source"
            if receipt_bound()
            else "final_translation_source_pending_admission_receipt",
            "path": "source/id-ID/Hilbert_space_operators-id.tex",
            "bytes": TARGET_SIZE,
            "lines": TARGET_LINES,
            "sha256": TARGET_SHA,
            "locale": "id-ID",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH05-MASTER",
            "artifact_kind": "cumulative_TeX_master",
            "path": "source/id-ID/functional-analysis-id-through-ch05.tex",
            "bytes": MASTER_SIZE,
            "lines": MASTER_LINES,
            "sha256": MASTER_SHA,
            "cumulative_through_unit_id": CHAPTER_ID,
            "locale": "id-ID",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH05-PDF",
            "artifact_kind": "canonical_cumulative_reader_pdf",
            "path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf",
            "bytes": PDF_SIZE,
            "sha256": PDF_SHA,
            "pages": PDF_PAGES,
            "page_size": "US Letter",
            "locale": "id-ID",
            "pdf_lang": "id-ID",
            "tagged_pdf": False,
            "bookmarks": True,
            "publication_state": "pending",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH05-STRUCTURAL-CHECKER",
            "artifact_kind": "structural_math_language_checker",
            "path": "qa/check_ch05_translation.py",
            "bytes": CHECKER_SIZE,
            "sha256": CHECKER_SHA,
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH05-RENDER-MANIFEST",
            "artifact_kind": "visual_QA_render_manifest",
            "path": "provenance/CH05_RENDER_MANIFEST.csv",
            "bytes": RENDER_MANIFEST_SIZE,
            "sha256": RENDER_MANIFEST_SHA,
            "rows": PDF_PAGES,
            "coverage": "90 page PNGs",
            "rendered_png_bytes": 30284058,
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH05-CONTACT-SHEET",
            "artifact_kind": "visual_QA_contact_sheet",
            "path": "provenance/CH05_CONTACT_SHEET.png",
            "bytes": CONTACT_SIZE,
            "sha256": CONTACT_SHA,
            "visual_pages": PDF_PAGES,
            "all_pages_inspected": True,
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH05-VISUAL-ACCESSIBILITY-AUDIT",
            "artifact_kind": "visual_accessibility_audit",
            "path": "qa/CH05_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
            "bytes": AUDIT_SIZE,
            "sha256": AUDIT_SHA,
            "visual_result": "pass",
            "fully_accessible_pdf_claim": "fail",
            "accessibility_remediation_state": "partial_nonblocking",
            "accessible_html_or_tagged_pdf_state": "pending",
        },
        receipt_artifact,
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH05-CORRECTIONS-LEDGER",
            "artifact_kind": "source_corrections_ledger",
            "path": "provenance/SOURCE_CORRECTIONS.md",
            "bytes": LEDGER_SIZE,
            "sha256": LEDGER_SHA,
            "chapter_section_sha256": LEDGER_SECTION_SHA,
            "chapter_correction_count": 23,
        },
    ]


def correction_records() -> list[dict]:
    specifications: list[tuple[str, str, str]] = [
        ("Hilbert_space_operators.tex:42,44", "index_spelling", "Correct the misspelled reader-facing index display word."),
        ("Hilbert_space_operators.tex:143", "omitted_predicate", "Restore the zero-function predicate for the associated quadratic form."),
        ("Hilbert_space_operators.tex:188--189", "sesquilinear_domain", "Quantify x in H and y in K in the sesquilinear bound."),
        ("Hilbert_space_operators.tex:481", "scalar_conjugation_macro", "Use the semantic scalar-conjugation macro rather than the closure macro."),
        ("Hilbert_space_operators.tex:490", "defined_term_boundary", "Remove the trailing space from the translated raw star-algebra term."),
        ("Hilbert_space_operators.tex:536", "unclosed_parenthesis", "Close the pronunciation parenthesis in the star-homomorphism definition."),
        ("Hilbert_space_operators.tex:576", "unital_scope", "Scope unitary elements and their notation to unital star algebras."),
        ("Hilbert_space_operators.tex:602", "unclosed_index_parenthesis", "Close the reader-facing star-subalgebra index parenthesis."),
        ("Hilbert_space_operators.tex:790--792", "real_field_macro", "Use the established real-field macro in both occurrences."),
        ("Hilbert_space_operators.tex:838--840", "unital_scope", "Require a unital star algebra before using its multiplicative identity."),
        ("Hilbert_space_operators.tex:864--866", "premature_notation", "State directly that a in A is positive instead of using undefined A-plus notation."),
        ("Hilbert_space_operators.tex:1076", "missing_token_boundary", "Restore the missing space after the comma."),
        ("Hilbert_space_operators.tex:1106--1107", "nonzero_scope", "Exclude the zero Hilbert space from the minimal-ideal claim."),
        ("Hilbert_space_operators.tex:221,234,249,300,536,843,1076; line 834", "source_language_and_punctuation", "Repair ordinary source-language defects and the stray comma naturally in Indonesian."),
        ("Hilbert_space_operators.tex:77--81", "nonzero_unit_sphere_scope", "Require nonzero Hilbert spaces for the unit-sphere suprema."),
        ("Hilbert_space_operators.tex:179--212", "nonzero_norm_scope", "Require nonzero Hilbert spaces where the norm uses unit and nonzero vectors."),
        ("Hilbert_space_operators.tex:307--310", "complex_scalar_scope", "State the finite-dimensional spectral theorem over a complex inner-product space."),
        ("Hilbert_space_operators.tex:370--375", "complex_scalar_scope", "Require a complex Hilbert space before scalar multiplication by complex alpha."),
        ("Hilbert_space_operators.tex:620--635", "nonzero_numerical_range_scope", "Require a nonzero Hilbert space for numerical range and numerical radius."),
        ("Hilbert_space_operators.tex:962--968", "unbound_space_and_vectors", "Bind u and v to the same Hilbert space on which T acts."),
        ("Hilbert_space_operators.tex:970--971", "nonzero_minimal_ideal_scope", "Require a nonzero Hilbert space in the minimal finite-rank ideal preview."),
        ("Hilbert_space_operators.tex:1116--1118", "infinite_dimension_scope", "Restrict nonclosedness of finite-rank operators to infinite-dimensional Hilbert spaces."),
        ("functional_analysis_op_algs_bib.bib:Erdman:2010", "dead_authority_url", "Replace the dead ELMA URL with the durable DOI while retaining the source citation year."),
    ]
    if len(specifications) != 23:
        raise ValueError("Chapter 5 correction specification count changed")
    common = {
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
        common
        | {
            "id": f"{CHAPTER_ID}-CORR-{number:03d}",
            "source_locator": locator,
            "correction_type": correction_type,
            "summary": summary,
        }
        for number, (locator, correction_type, summary) in enumerate(specifications, 1)
    ]


# One row for each distinct raw source defined-term hook, in first-occurrence
# order. Existing global concepts retain their already-admitted stable IDs.
TERM_SPECS: list[tuple[str, str, str]] = [
    ("TERM-INNER-PRODUCT-PRESERVING", "inner product preserving", "mempertahankan hasil kali dalam"),
    ("TERM-CURVE", "curve", "kurva"),
    ("TERM-SIMPLE", "simple", "sederhana"),
    ("TERM-CHORD", "chord", "tali busur"),
    ("TERM-NON-OVERLAPPING", "non-overlapping", "tak bertumpang tindih"),
    ("TERM-ASSOCIATED-QUADRATIC-FORM", r"quadratic form associated with~$T$", r"bentuk kuadratik yang terkait dengan~$T$"),
    ("TERM-CONJUGATE-LINEAR", "conjugate linear", "linear konjugat"),
    ("TERM-SESQUILINEAR-FUNCTIONAL", "sesquilinear functional", "fungsional seskuilinear"),
    ("TERM-BOUNDED", "bounded", "terbatas"),
    ("TERM-ADJOINT", "adjoint", "adjoin"),
    ("TERM-UNILATERAL-SHIFT-OPERATOR", "unilateral shift operator", "operator geser unilateral"),
    ("TERM-DIAGONAL-OPERATOR", "diagonal operator", "operator diagonal"),
    ("TERM-MULTIPLICATION-OPERATOR", "multiplication operator", "operator perkalian"),
    ("TERM-UNITARILY-EQUIVALENT", "unitarily equivalent", "ekuivalen secara uniter"),
    ("TERM-SPECTRAL-THEOREM", "spectral theorem", "teorema spektral"),
    ("TERM-INTEGRAL-OPERATOR", "integral operator", "operator integral"),
    ("TERM-KERNEL", "kernel", "kernel"),
    ("TERM-VOLTERRA-OPERATOR", "Volterra operator", "operator Volterra"),
    ("TERM-BOUNDED-AWAY-FROM-ZERO", "bounded away from zero", "terbatas jauh dari nol"),
    ("TERM-BOUNDED-BELOW", "bounded below", "terbatas dari bawah"),
    ("TERM-INVOLUTION", "involution", "involusi"),
    ("TERM-STAR-ALGEBRA", "$*\\,$-algebra ", "aljabar-$*\\,$"),
    ("TERM-STAR-HOMOMORPHISM", "$*\\,$-homomorphism", "homomorfisme-$*\\,$"),
    ("TERM-UNITAL", "unital", "beridentitas"),
    ("TERM-STAR-ISOMORPHISM", "$*\\,$-isomorphisms", "isomorfisme-$*\\,$"),
    ("TERM-SELF-ADJOINT", "self-adjoint", "swaadjoin"),
    ("TERM-HERMITIAN", "Hermitian", "Hermitian"),
    ("TERM-NORMAL", "normal", "normal"),
    ("TERM-UNITARY", "unitary", "uniter"),
    ("TERM-STAR-SUBALGEBRA", "$*\\,$-subalgebra", "subaljabar-$*\\,$"),
    ("TERM-STAR-SUBALGEBRA", "sub-$*\\,$-algebra", "subaljabar-$*\\,$"),
    ("TERM-NUMERICAL-RANGE", "numerical range", "jangkauan numerik"),
    ("TERM-NUMERICAL-RADIUS", "numerical radius", "radius numerik"),
    ("TERM-POSITIVE", "positive", "positif"),
    ("TERM-PROJECTION", "projection", "proyeksi"),
    ("TERM-ABSTRACT", "abstract", "abstrak"),
    ("TERM-SPATIAL", "spatial", "spasial"),
    ("TERM-CONCRETE", "concrete", "konkret"),
    ("TERM-ORTHOGONAL", "orthogonal", "ortogonal"),
    ("TERM-RANK", "rank", "peringkat"),
    ("TERM-FINITE-RANK", "finite rank", "berperingkat hingga"),
    ("TERM-LEFT-IDEAL", "left ideal", "ideal kiri"),
    ("TERM-RIGHT-IDEAL", "right ideals", "ideal kanan"),
    ("TERM-IDEAL", "ideal", "ideal"),
    ("TERM-PROPER", "proper", "sejati"),
    ("TERM-TRIVIAL-IDEAL", "trivial ideals", "ideal trivial"),
    ("TERM-MAXIMAL", "maximal", "maksimal"),
    ("TERM-MINIMAL", "minimal", "minimal"),
    ("TERM-PRINCIPAL-IDEAL", "principal ideal", "ideal utama"),
    ("TERM-QUOTIENT-ALGEBRA", "quotient algebra", "aljabar hasil bagi"),
    ("TERM-QUOTIENT-MAP", "quotient map", "pemetaan hasil bagi"),
    ("TERM-STAR-IDEAL", "$*\\,$-ideal", "ideal-$*\\,$"),
    ("TERM-QUOTIENT", "quotient", "hasil bagi"),
]
EXISTING_TERM_IDS = {
    "conjugate linear": "TERM-CONJUGATE-LINEAR",
    "adjoint": "TERM-ADJOINT",
    "spectral theorem": "TERM-SPECTRAL-THEOREM",
    "self-adjoint": "TERM-SELF-ADJOINT",
    "unitary": "TERM-UNITARY",
    "projection": "TERM-PROJECTION",
    "orthogonal": "TERM-ORTHOGONAL",
    "rank": "TERM-RANK",
}


def term_id_map() -> dict[str, str]:
    mapping = {source: stable_id for stable_id, source, _ in TERM_SPECS}
    if len(mapping) != 53:
        raise ValueError("Chapter 5 distinct defined-term inventory changed")
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
                "scope": "Hilbert-space operators and operator algebras",
                "evidence": "FAOA-2015-CH05 final target source/id-ID/Hilbert_space_operators-id.tex; backend/index_terms.csv; qa/check_ch05_translation.py",
            }
        )
    if len(records) != 44:
        raise ValueError(f"Chapter 5 new terminology record count changed: {len(records)}")
    return records


def qa_records(formula_summary: dict[str, object]) -> list[dict]:
    typed_ids = [
        "QA-CH05-STRUCTURAL-20260822",
        "QA-CH05-MATH-20260822",
        "QA-CH05-LANGUAGE-20260822",
        "QA-CH05-BUILD-20260822",
        "QA-CH05-VISUAL-20260822",
        "QA-CH05-ACCESSIBILITY-20260822",
        "QA-CH05-RIGHTS-20260822",
    ]
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "result": "pass",
        "timestamp": "2026-08-22",
        "responsible_workflow": "Codex",
        **admission_fields(),
    }
    return [
        common
        | {
            "id": typed_ids[0],
            "qa_type": "unit_structural",
            "witness": "qa/check_ch05_translation.py",
            "witness_sha256": CHECKER_SHA,
            "semantic_anchors": 138,
            "semantic_units": 137,
            "segments": 158,
            "all_environment_pairs": 152,
            "semantic_environment_anchors": 130,
            "sections": 7,
            "labels": 39,
            "references": 25,
            "ordinary_target_references": 23,
            "future_target_references": 1,
            "equation_references": 1,
            "citations": 1,
            "index_terms": 168,
            "defined_terms": 56,
            "exercise_environments": 4,
            "proof_hints": 17,
        },
        common
        | {
            "id": typed_ids[1],
            "qa_type": "unit_mathematical",
            "witness": "qa/check_ch05_translation.py",
            "witness_sha256": CHECKER_SHA,
            "source_math_surfaces": 827,
            "target_math_surfaces": 827,
            **formula_summary,
            "locked_source_correction_surfaces": 6,
            "unexplained_deltas": 0,
            "extractor": "backend/ch03_math.py",
            "extractor_sha256": "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3",
        },
        common
        | {
            "id": typed_ids[2],
            "qa_type": "unit_language",
            "witness": "qa/check_ch05_translation.py",
            "witness_sha256": CHECKER_SHA,
            "severity_counts": {"P1": 0, "P2": 0, "P3": 0},
            "unintended_english_prose": 0,
            "placeholders": 0,
            "terminology_reconciled": True,
        },
        common
        | {
            "id": typed_ids[3],
            "qa_type": "cumulative_build",
            "witness": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf",
            "witness_sha256": PDF_SHA,
            "master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH05-MASTER",
            "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH05-PDF",
            "final_pdf_locked": True,
            "fixed_path_clean_builds_byte_identical": True,
            "pages": PDF_PAGES,
            "local_build_log_bytes": BUILD_LOG_SIZE,
            "local_build_log_sha256": BUILD_LOG_SHA,
            "local_build_log_publication_state": "excluded_ignored_build_intermediate",
        },
        common
        | {
            "id": typed_ids[4],
            "qa_type": "cumulative_visual",
            "witness": "qa/CH05_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
            "witness_sha256": AUDIT_SHA,
            "render_manifest_artifact_id": "ARTIFACT-FAOA-ID-CH05-RENDER-MANIFEST",
            "contact_sheet_artifact_id": "ARTIFACT-FAOA-ID-CH05-CONTACT-SHEET",
            "pages_rendered": PDF_PAGES,
            "pages_inspected": PDF_PAGES,
            "visual_defects": 0,
        },
        common
        | {
            "id": typed_ids[5],
            "qa_type": "cumulative_accessibility",
            "result": "fail",
            "failure_scope": "claim_of_fully_accessible_pdf",
            "witness": "qa/CH05_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
            "witness_sha256": AUDIT_SHA,
            "tagged_pdf": False,
            "unicode_mapped_font_resources": 38,
            "total_font_resources": 40,
            "remaining_c0_controls": 24,
            "affected_xy_diagram_pages": 6,
            "resolved_internal_links": 1228,
            "named_destinations": 861,
            "outline_entries": 34,
            "ordinary_prose_extraction": "materially_improved",
            "admission_blocker_for_visual_pdf_boundary": False,
            "accessibility_remediation_state": "partial_nonblocking",
            "accessible_html_or_tagged_pdf_state": "pending",
        },
        common
        | {
            "id": typed_ids[6],
            "qa_type": "unit_rights_privacy",
            "witness": "source/id-ID/functional-analysis-id-through-ch05.tex",
            "witness_sha256": MASTER_SHA,
            "rights_id": RIGHTS,
            "attribution_change_notice_sharealike_nonendorsement": "present",
            "excluded_components_absent": True,
            "private_control_paths_absent_from_public_artifacts": True,
        },
        common
        | {
            "id": ADMISSION_QA_ID,
            "qa_type": "unit_admission",
            "result": "pass" if receipt_bound() else "pending",
            "decision": "admitted" if receipt_bound() else "pending_receipt",
            "source_sha256": SOURCE_SHA,
            "target_sha256": TARGET_SHA,
            "build_master_sha256": MASTER_SHA,
            "artifact_sha256": PDF_SHA,
            "render_manifest_sha256": RENDER_MANIFEST_SHA,
            "visual_accessibility_audit_sha256": AUDIT_SHA,
            "corrections_ledger_sha256": LEDGER_SHA,
            "typed_qa_event_ids": typed_ids,
            "required_admission_gate_results": {
                "unit_structural": "pass",
                "unit_mathematical": "pass",
                "unit_language": "pass",
                "cumulative_build": "pass",
                "cumulative_visual": "pass",
                "cumulative_accessibility": "fail_nonblocking",
                "unit_rights_privacy": "pass",
            },
            "all_required_admission_gates": "pass",
            "accessibility_remediation_state": "partial_nonblocking",
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


def build_math_pairs(source: str, target: str) -> tuple[list[dict], dict[str, object]]:
    source_math = ch03_math.extract_math(source, SOURCE_ENCODING)
    target_math = ch03_math.extract_math(target, TARGET_ENCODING)
    if len(source_math) != 827 or len(target_math) != 827:
        raise ValueError("Chapter 5 math-surface count changed")
    expected_differences = {
        tuple(item[:7]): item[7] for item in ch05check.EXPECTED_MATH_MISMATCHES
    }
    seen_differences: dict[tuple, str] = {}
    alignment_counts: collections.Counter[str] = collections.Counter()
    records: list[dict] = []
    for number, (source_record, target_record) in enumerate(
        zip(source_math, target_math, strict=True), 1
    ):
        source_key = ch03_math.math_key(source_record["normalized"])
        target_key = ch03_math.math_key(target_record["normalized"])
        key_equal = source_key == target_key
        signature = (
            number,
            number,
            source_record["line_start"],
            target_record["line_start"],
            source_record["delimiter"],
            sha(source_key.encode("utf-8")),
            sha(target_key.encode("utf-8")),
        )
        if source_record["normalized"] == target_record["normalized"]:
            alignment = "preserved_exact_after_text_aware_whitespace_normalization"
        elif key_equal:
            alignment = "localized_math_text_preserved_math_key"
        elif signature in expected_differences:
            alignment = "reviewed_source_correction"
            seen_differences[signature] = expected_differences[signature]
        else:
            raise ValueError(f"unexpected Chapter 5 mathematical delta: {signature}")
        alignment_counts[alignment] += 1
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{number:04d}",
            "alignment": alignment,
            "math_key_alignment": "equal" if key_equal else "reviewed_difference",
            "ordinal_alignment": "same",
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{number:04d}"],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{number:04d}"],
            "source_lines": [[source_record["line_start"], source_record["line_end"]]],
            "target_lines": [[target_record["line_start"], target_record["line_end"]]],
            "source_sha256": [source_record["sha256"]],
            "target_sha256": [target_record["sha256"]],
            "delimiter": source_record["delimiter"],
        }
        if not key_equal:
            record |= {
                "sequence_opcode": "replace",
                "qa_state": "passed",
                "correction_disposition": expected_differences[signature],
                "review_witness": "provenance/SOURCE_CORRECTIONS.md and qa/check_ch05_translation.py",
            }
        records.append(record)
    expected_counts = {
        "preserved_exact_after_text_aware_whitespace_normalization": 816,
        "localized_math_text_preserved_math_key": 5,
        "reviewed_source_correction": 6,
    }
    if dict(alignment_counts) != expected_counts:
        raise ValueError(f"Chapter 5 formula alignments changed: {dict(alignment_counts)}")
    if seen_differences != expected_differences:
        raise ValueError("Chapter 5 reviewed mathematical differences changed")
    return records, {
        "exact_normalized_alignments": 816,
        "math_key_equal_alignments": 821,
        "localized_math_text_alignments": 5,
        "reviewed_source_corrections": 6,
        "formula_map_records": 827,
    }


def main() -> None:
    source_bytes = SOURCE_PATH.read_bytes()
    target_bytes = TARGET_PATH.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha(source_bytes)) != (
        SOURCE_SIZE,
        SOURCE_LINES,
        SOURCE_SHA,
    ):
        raise ValueError("Chapter 5 source authority changed")
    if (len(target_bytes), len(target_bytes.splitlines()), sha(target_bytes)) != (
        TARGET_SIZE,
        TARGET_LINES,
        TARGET_SHA,
    ):
        raise ValueError("final Chapter 5 target lock changed")
    source = source_bytes.decode(SOURCE_ENCODING)
    target = target_bytes.decode(TARGET_ENCODING)

    verify_evidence()
    for name in PREFIX_LOCKS:
        locked_prefix(name)
    unit_boundaries()
    checker_run = subprocess.run(
        [sys.executable, str(ROOT / "qa" / "check_ch05_translation.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    checker_result = json.loads(checker_run.stdout)
    if checker_result.get("result") != "pass":
        raise ValueError("Chapter 5 checker did not return its locked pass result")

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if len(source_anchors) != 138 or [ch01.anchor_signature(a) for a in source_anchors] != [
        ch01.anchor_signature(a) for a in target_anchors
    ]:
        raise ValueError("Chapter 5 semantic anchor topology differs")
    source_labels = ch05check.macro(source, "label")
    target_labels = ch05check.macro(target, "label")
    if len(source_labels) != 39 or [x["argument"] for x in source_labels] != [
        x["argument"] for x in target_labels
    ]:
        raise ValueError("Chapter 5 label sequence differs")

    semantic_units: list[dict] = []
    segment_records: list[dict] = []
    relations: list[dict] = []
    anchor_ids: list[str] = []
    current_section = CHAPTER_ID
    current_section_by_anchor: list[str] = []
    section_number = 0
    node_number = 0
    state = "admitted" if receipt_bound() else "ready_for_admission"
    for source_anchor, target_anchor in zip(source_anchors, target_anchors, strict=True):
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
                "source_path": "source/upstream/Hilbert_space_operators.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_fragment_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/Hilbert_space_operators-id.tex",
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
    if (len(semantic_units), section_number, node_number) != (137, 7, 130):
        raise ValueError("Chapter 5 semantic-unit topology invariant failed")

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
    if len(source_parts) != 158 or len(target_parts) != 158:
        raise ValueError("Chapter 5 source/target segment count differs from 158")

    for number, (source_part, target_part) in enumerate(
        zip(source_parts, target_parts, strict=True), 1
    ):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if role != target_role or parent_id != target_parent:
            raise ValueError("Chapter 5 source/target segment role differs")
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
                "source_path": "source/upstream/Hilbert_space_operators.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_bytes": source_fragment["bytes"],
                "source_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/Hilbert_space_operators-id.tex",
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
    if len(local_label_map) != 39:
        raise ValueError("Chapter 5 local label map changed")

    source_refs = ch05check.macro(source, "ref")
    target_refs = ch05check.macro(target, "ref")
    expected_target_refs = [
        item["argument"] for item in source_refs if item["argument"] != "chap_cpt_ops"
    ]
    if len(source_refs) != 24 or len(target_refs) != 23 or [
        item["argument"] for item in target_refs
    ] != expected_target_refs:
        raise ValueError("Chapter 5 ref sequence differs")
    future_matches = list(
        re.finditer(
            r"\\futurexref\{([^{}]*)\}\{([^{}]+)\}",
            ch01.active_same_length(target),
        )
    )
    if [(match.group(1), match.group(2)) for match in future_matches] != [
        ("7", "chap_cpt_ops")
    ]:
        raise ValueError("Chapter 5 futurexref endpoint differs")
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
        elif label == "sec_bdd_lin_maps":
            to_id = "ERDMAN-FAOA-2015-LABEL-sec_bdd_lin_maps"
            resolution = "admitted_prior_unit"
            target_surface = "ref"
        elif label == "chap_cpt_ops":
            to_id = "ERDMAN-FAOA-2015-LABEL-chap_cpt_ops"
            resolution = "pending_later_source_unit"
            target_surface = "futurexref"
        else:
            raise ValueError(f"unexpected unresolved Chapter 5 reference: {label}")
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
        "admitted_prior_unit": 10,
        "local": 13,
        "pending_later_source_unit": 1,
    }:
        raise ValueError(
            f"Chapter 5 reference-resolution counts changed: {dict(reference_counts)}"
        )

    source_eqrefs = ch05check.macro(source, "eqref")
    target_eqrefs = ch05check.macro(target, "eqref")
    if [item["argument"] for item in source_eqrefs] != ["num_ran_saop_eqn2"] or [
        item["argument"] for item in target_eqrefs
    ] != ["num_ran_saop_eqn2"]:
        raise ValueError("Chapter 5 eqref sequence differs")
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

    source_cites = ch05check.macro(source, "cite")
    target_cites = ch05check.macro(target, "cite")
    if [item["argument"] for item in source_cites] != ["Halmos:1982"] or [
        item["argument"] for item in target_cites
    ] != ["Halmos:1982"]:
        raise ValueError("Chapter 5 citation sequence differs")
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
                    "from_id": ch01.containing_segment(
                        segment_records, occurrence["start"], "source"
                    ),
                    "to_id": f"ERDMAN-FAOA-BIB-{key}",
                    "source_local_id": key,
                }
            )
    if cite_key_count != 1:
        raise ValueError("Chapter 5 citation-key count changed")

    previous_statement: str | None = None
    hint_ids_by_statement: dict[str, list[str]] = collections.defaultdict(list)
    hint_relations = 0
    for record in semantic_units:
        if record["unit_kind"] != "proof":
            previous_statement = record["id"]
            continue
        title = record.get("source_title_tex") or ""
        if "Hint for proof" not in title:
            continue
        if previous_statement is None:
            raise ValueError("Chapter 5 proof hint lacks a preceding statement")
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
    if hint_relations != 17:
        raise ValueError("Chapter 5 proof-hint topology changed")

    source_df = ch05check.macro(source, "df")
    target_df = ch05check.macro(target, "df")
    term_ids = term_id_map()
    if (
        len(source_df) != 56
        or len(target_df) != 56
        or set(term_ids) != {record["argument"] for record in source_df}
    ):
        raise ValueError("Chapter 5 defined-term inventory changed")
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

    source_terms = ch05check.macro(source, "index")
    target_terms = ch05check.macro(target, "index")
    if (
        len(source_terms) != 168
        or len(target_terms) != 168
        or [
            ch05check.index_signature(item["argument"]) for item in source_terms
        ]
        != [ch05check.index_signature(item["argument"]) for item in target_terms]
    ):
        raise ValueError("Chapter 5 index-term alignment changed")
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
    if len(exercises) != 4 or any(record["upstream_hint_ids"] for record in exercises):
        raise ValueError("Chapter 5 exercise-support topology changed")

    artifacts = artifact_records()
    corrections = correction_records()
    terms = terminology_records()
    qa = qa_records(formula_summary)
    if (len(artifacts), len(corrections), len(terms), len(qa)) != (9, 23, 44, 8):
        raise ValueError("Chapter 5 evidence record counts changed")
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
            "ARTIFACT-FAOA-ID-CH05-TARGET-TEX",
            "ARTIFACT-FAOA-ID-CH05-STRUCTURAL-CHECKER",
        ),
        1,
    ):
        relations.append(
            relation_common
            | {
                "id": f"{CHAPTER_ID}-REL-TERM-EVIDENCE-{number:04d}",
                "relation_type": "terminology_evidence",
                "to_id": artifact_id,
                "evidence_scope": "all Chapter 5 terminology records and occurrences",
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
    if len(relations) != 633:
        raise ValueError(f"Chapter 5 relation invariant failed: {len(relations)}")

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
                "admitted_prior_references": reference_counts[
                    "admitted_prior_unit"
                ],
                "future_references": reference_counts["pending_later_source_unit"],
                "eqrefs": len(source_eqrefs),
                "cites": cite_key_count,
                "index_terms": len(source_terms),
                "defined_terms": len(source_df),
                "formula_map_records": len(formula_records),
                "exercises": len(exercises),
                "proof_hints": hint_relations,
                "corrections": len(corrections),
                "terminology_records": len(terms),
                "artifacts": len(artifacts),
                "qa_events": len(qa),
                "receipt_document_state": "present" if receipt_bound() else "pending",
                "translation_state": state,
                "qa_state": "passed",
                **formula_summary,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
