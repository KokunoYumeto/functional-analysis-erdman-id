#!/usr/bin/env python3
"""Append deterministic Chapter 4 backend records after locked Chapters 1--3.

The existing Chapter 1--3 projections are immutable byte prefixes.  Chapter 4
is bound to its final admission receipt.  ``INTERLANGUAGE_BACKEND_DIR`` permits
complete replay against an isolated backend copy.
"""

from __future__ import annotations

import collections
import csv
import hashlib
import io
import json
import os
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
import check_ch04_translation as ch04check  # noqa: E402


SOURCE_PATH = ROOT / "source" / "upstream" / "Hilbert_spaces.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "Hilbert_spaces-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH04"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
TRANSLATION_STATE = "admitted"
QA_STATE = "passed"
ADMISSION_QA_ID = "QA-CH04-ADMISSION-20260822"

SOURCE_SIZE = 60217
SOURCE_LINES = 1340
SOURCE_SHA = "80fd8fd190beefde7787139be67ce29b9d9cce2d68ff66489aa1e4a93b54c740"
TARGET_SIZE = 62947
TARGET_LINES = 1351
TARGET_SHA = "b8e728e1f26a66ec2a420373e6104e3db4e5c954d7001acda1c13eb348322215"

# Exact canonical Chapter 1--3 backend.  Each Chapter 4 projection retains
# these bytes literally and appends only Chapter 4 records.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (284077, "afbee367d616e9ded8214dc73dc40af637cae4dea5cbfc524ecfa81e0210af2c"),
    "segments.jsonl": (329416, "a7222c6c67414a38b8ec9e54e44691ef711a5241da24e6dcadd2cc483d002ec1"),
    "relations.jsonl": (334502, "42e609d4654388332e602311888f56f2ea34d522ad61c5a3897747584ddb483b"),
    "formula_map.jsonl": (1448197, "d0980a63abefd5d7aea44b7de2b2c8314d86f802b69542591ea0746f76a21056"),
    "exercise_support.jsonl": (6604, "93e1a83c175a49ec3cc8b3a75666834fa6345e894fef608084e35692ac969e1b"),
    "index_terms.csv": (169542, "6bfc36e916e0484e6d9a731093a560a8c636e9852e04adf02dd42c047610809b"),
    "artifacts.jsonl": (8552, "d6f33162c32fb83a58783f22c15eaec11bc8c637ef76872ed98a077c199697c8"),
    "qa_events.jsonl": (13612, "c463c33701b504183a3125dcbf683eeb26296c76397215d80a55f7a8cc989579"),
    "corrections.jsonl": (24536, "d65bb38f7bb7a49a5fb1f509c6d581602adf73ba11b6848126675c045d865e43"),
    "terminology.jsonl": (16842, "fa80016533c85a8576911e0340b41826103cb4cf8e88c4637e1d8d9c898d5354"),
}
UNIT_PREFIX_LOCK = (3425, "6a6c0cbecf334c8d7e2ff12da80a9fe527300ffeb611873cc1af6bd72752934c")

EVIDENCE_LOCKS = {
    "source/id-ID/functional-analysis-id-through-ch04.tex": (
        9348,
        "598bd1f91096a2e0e19314995f44f79f246ca06cad6328ce9e996af074ceff6c",
    ),
    "source/id-ID/Hilbert_spaces-id.tex": (TARGET_SIZE, TARGET_SHA),
    "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf": (
        1249703,
        "716e3524060f64e4728b4d3d8c1a2b906f377ec4e3b3a3cd1ef3e61759a3dd94",
    ),
    "qa/check_ch04_translation.py": (
        33292,
        "bcf98112417cf1a0405207d79a4f877f53fd25514ea72dfb985a347843118954",
    ),
    "provenance/CH04_RENDER_MANIFEST.csv": (
        7134,
        "9f8b88e46823e91920d27ade8f32af30ce347dccd0ab5d759afb2b07f0f64390",
    ),
    "provenance/CH04_CONTACT_SHEET.png": (
        2535154,
        "4712840f42f3fc988e90eeb80cdc5725ecc7db16383a339f5b98144008ecdc4d",
    ),
    "qa/CH04_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md": (
        5549,
        "699009af48643839f1b2ab216d90c4e6f07cf4c3f92d60461d2ccfdae219a8a0",
    ),
    "provenance/CH04_BUILD_AND_QA_RECEIPT.md": (
        8504,
        "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07",
    ),
    "provenance/SOURCE_CORRECTIONS.md": (
        11058,
        "8909a33f5ed5dd37065fb4c3afb08e4e0659d17ef1d1a2b8f1d7f307ed1eef2d",
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def locked_prefix(name: str) -> bytes:
    size, expected_sha = PREFIX_LOCKS[name]
    data = (BACKEND / name).read_bytes()
    if len(data) < size:
        raise ValueError(f"{name} is shorter than its locked Chapter 1--3 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha or not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1--3 prefix changed")
    return prefix


def append_jsonl(name: str, records: list[dict]) -> None:
    suffix = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")
    (BACKEND / name).write_bytes(locked_prefix(name) + suffix)


def verify_evidence() -> None:
    for relative_path, (size, expected_sha) in EVIDENCE_LOCKS.items():
        data = (ROOT / relative_path).read_bytes()
        if relative_path == "provenance/SOURCE_CORRECTIONS.md":
            if len(data) < size or sha(data[:size]) != expected_sha:
                raise ValueError(f"Chapter 4 evidence prefix changed: {relative_path}")
            continue
        if (len(data), sha(data)) != (size, expected_sha):
            raise ValueError(f"Chapter 4 evidence changed: {relative_path}")


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
    prefix = b"".join(lines[:3])
    middle = lines[3]
    suffix = b"".join(lines[4:])
    if (len(prefix), sha(prefix)) != UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--3 prefix changed")
    if json.loads(middle).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 4 replacement boundary changed")
    return prefix, suffix


def chapter_four_unit() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 4,
        "source_path": "Hilbert_spaces.tex",
        "source_bytes": SOURCE_SIZE,
        "source_lines": SOURCE_LINES,
        "source_sha256": SOURCE_SHA,
        "source_title": "HILBERT SPACES",
        "target_path": "source/id-ID/Hilbert_spaces-id.tex",
        "target_bytes": TARGET_SIZE,
        "target_lines": TARGET_LINES,
        "target_sha256": TARGET_SHA,
        "target_title": "Ruang Hilbert",
        "course_role": "D20_core",
        "translation_state": TRANSLATION_STATE,
        "qa_state": QA_STATE,
        "source_corrections": 22,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch04.tex",
        "build_master_bytes": 9348,
        "build_master_sha256": "598bd1f91096a2e0e19314995f44f79f246ca06cad6328ce9e996af074ceff6c",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf",
        "artifact_bytes": 1249703,
        "artifact_pages": 75,
        "artifact_sha256": "716e3524060f64e4728b4d3d8c1a2b906f377ec4e3b3a3cd1ef3e61759a3dd94",
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH04_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07",
        "publication_state": "pending",
        "rights_id": RIGHTS,
    }


def rewrite_units() -> None:
    prefix, suffix = unit_boundaries()
    encoded = (
        json.dumps(chapter_four_unit(), ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    (BACKEND / "units.jsonl").write_bytes(prefix + encoded + suffix)


def artifact_records() -> list[dict]:
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "artifact",
        "unit_id": CHAPTER_ID,
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
    }
    return [
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH04-TARGET-TEX",
            "artifact_kind": "admitted_translation_source",
            "path": "source/id-ID/Hilbert_spaces-id.tex",
            "bytes": TARGET_SIZE,
            "lines": TARGET_LINES,
            "sha256": TARGET_SHA,
            "locale": "id-ID",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH04-MASTER",
            "artifact_kind": "cumulative_TeX_master",
            "path": "source/id-ID/functional-analysis-id-through-ch04.tex",
            "bytes": 9348,
            "sha256": "598bd1f91096a2e0e19314995f44f79f246ca06cad6328ce9e996af074ceff6c",
            "cumulative_through_unit_id": CHAPTER_ID,
            "locale": "id-ID",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH04-PDF",
            "artifact_kind": "canonical_cumulative_reader_pdf",
            "path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf",
            "bytes": 1249703,
            "sha256": "716e3524060f64e4728b4d3d8c1a2b906f377ec4e3b3a3cd1ef3e61759a3dd94",
            "pages": 75,
            "page_size": "US Letter",
            "locale": "id-ID",
            "pdf_lang": "id-ID",
            "tagged_pdf": False,
            "bookmarks": True,
            "publication_state": "pending",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH04-STRUCTURAL-CHECKER",
            "artifact_kind": "structural_math_language_checker",
            "path": "qa/check_ch04_translation.py",
            "bytes": 33292,
            "sha256": "bcf98112417cf1a0405207d79a4f877f53fd25514ea72dfb985a347843118954",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH04-RENDER-MANIFEST",
            "artifact_kind": "visual_QA_render_manifest",
            "path": "provenance/CH04_RENDER_MANIFEST.csv",
            "bytes": 7134,
            "sha256": "9f8b88e46823e91920d27ade8f32af30ce347dccd0ab5d759afb2b07f0f64390",
            "rows": 75,
            "coverage": "75 page PNGs",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH04-CONTACT-SHEET",
            "artifact_kind": "visual_QA_contact_sheet",
            "path": "provenance/CH04_CONTACT_SHEET.png",
            "bytes": 2535154,
            "sha256": "4712840f42f3fc988e90eeb80cdc5725ecc7db16383a339f5b98144008ecdc4d",
            "visual_pages": 75,
            "all_pages_inspected": True,
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH04-VISUAL-ACCESSIBILITY-AUDIT",
            "artifact_kind": "visual_accessibility_audit",
            "path": "qa/CH04_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
            "bytes": 5549,
            "sha256": "699009af48643839f1b2ab216d90c4e6f07cf4c3f92d60461d2ccfdae219a8a0",
            "visual_result": "pass",
            "fully_accessible_pdf_claim": "fail",
            "accessible_html_or_tagged_pdf_state": "pending",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH04-QA-RECEIPT",
            "artifact_kind": "admission_receipt",
            "path": "provenance/CH04_BUILD_AND_QA_RECEIPT.md",
            "bytes": 8504,
            "sha256": "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07",
            "decision": "admitted",
        },
        common
        | {
            "id": "ARTIFACT-FAOA-ID-CH04-CORRECTIONS-LEDGER",
            "artifact_kind": "source_corrections_ledger",
            "path": "provenance/SOURCE_CORRECTIONS.md",
            "bytes": 11058,
            "sha256": "8909a33f5ed5dd37065fb4c3afb08e4e0659d17ef1d1a2b8f1d7f307ed1eef2d",
            "chapter_section_sha256": "961806d5d229310c8063dc8941c8d4fd1caeabafe65bb9fa7df9045c17f53fe3",
            "chapter_correction_count": 22,
        },
    ]


def correction_records() -> list[dict]:
    specifications: list[tuple[object, str, str]] = [
        ("Hilbert_spaces.tex:49", "uniform_norm_domain", "Take the supremum over X, not the unrelated interval [0,1]."),
        ("Hilbert_spaces.tex:220", "unbound_subsequence_index", "Use n_{j-1}, not the expression containing unbound i."),
        ("Hilbert_spaces.tex:282", "source_language", "Repair the English article naturally in Indonesian."),
        ("Hilbert_spaces.tex:286", "index_spelling", "Correct the orthogonal index-key spelling and localize display text."),
        ("Hilbert_spaces.tex:380--381", "plural_agreement", "Express the two claims with correct plural agreement."),
        ("Hilbert_spaces.tex:403", "missing_token_boundary", "Restore whitespace after the example environment opening."),
        ("Hilbert_spaces.tex:432--436", "missing_closure", "Close M-perp plus N-perp in the orthogonal-complement identity."),
        ("Hilbert_spaces.tex:443--444", "unmatched_parenthesis", "Remove the unmatched closing parenthesis."),
        ("Hilbert_spaces.tex:560--563", "coefficient_range", "Quantify c_{-n},...,c_n for the trigonometric polynomial."),
        ("Hilbert_spaces.tex:728--729", "missing_period", "Supply the sentence-ending period before the next construction."),
        ("Hilbert_spaces.tex:747--748", "missing_relation", "Restore 'wrong with his invocation' naturally in Indonesian."),
        ("Hilbert_spaces.tex:847", "evaluation_codomain", "Type the real-valued evaluation functional into R."),
        ("Hilbert_spaces.tex:849", "interval_typo", "Correct [0.1] to [0,1]."),
        ("Hilbert_spaces.tex:852", "source_language", "Supply the missing article naturally in Indonesian."),
        ("Hilbert_spaces.tex:959", "citation_quality_warning", "Retain resolving key wiki:xxx while recording its mutable target."),
        ("Hilbert_spaces.tex:1002", "environment_kind", "Call ump001z the following example, not an exercise."),
        ("Hilbert_spaces.tex:1049--1051", "misplaced_index_hooks", "Move all three l_2 index hooks to the Chapter 4 l_2 discussion."),
        ("Hilbert_spaces.tex:1074--1076", "operand_consistency", "Define concatenation with the introduced words s and t."),
        ("Hilbert_spaces.tex:1118--1119", "universal_pair_object", "Identify (Q,iota) as the universal pair."),
        ("Hilbert_spaces.tex:1169", "defined_term_boundary", "Include F within the co-universal-morphism definition boundary."),
        ("Hilbert_spaces.tex:1188--1200", "product_object_maps", "Use the declared product P and projections pi_k."),
        ("Hilbert_spaces.tex:1275", "source_language", "Supply the missing article in 'a subspace' naturally in Indonesian."),
    ]
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "correction",
        "unit_id": CHAPTER_ID,
        "target_disposition": "corrected",
        "ledger_path": "provenance/SOURCE_CORRECTIONS.md",
        "ledger_sha256": "8909a33f5ed5dd37065fb4c3afb08e4e0659d17ef1d1a2b8f1d7f307ed1eef2d",
        "ledger_section_sha256": "961806d5d229310c8063dc8941c8d4fd1caeabafe65bb9fa7df9045c17f53fe3",
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH04_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07",
        "upstream_report": "deferred_until_complete_and_separately_authorized",
    }
    if len(specifications) != 22:
        raise ValueError("Chapter 4 correction specification count changed")
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


TERM_SPECS = [
    ("HILBERT-SPACE", "Hilbert space", "ruang Hilbert"),
    ("BANACH-SPACE", "Banach space", "ruang Banach"),
    ("BANACH-ALGEBRA", "Banach algebra", "aljabar Banach"),
    ("UNIFORM-NORM", "uniform norm", "norma seragam"),
    ("MEASURABLE", "measurable", "terukur"),
    ("SQUARE-INTEGRABLE", "square integrable", "terintegralkan kuadrat"),
    ("INTEGRABLE", "integrable", "terintegralkan"),
    ("ABSOLUTELY-CONTINUOUS", "absolutely continuous", "kontinu mutlak"),
    ("SUMMABLE", "summable", "dapat dijumlahkan"),
    ("SUM", "sum", "jumlah"),
    ("ABSOLUTELY-SUMMABLE", "absolutely summable", "dapat dijumlahkan secara mutlak"),
    ("CONVERGES", "converges", "konvergen"),
    ("EXISTS", "exists", "ada"),
    ("ABSOLUTELY-CONVERGENT", "absolutely convergent", "konvergen mutlak"),
    ("CONVERGENT-SERIES", "convergent series", "deret konvergen"),
    ("EXTERNAL-ORTHOGONAL-DIRECT-SUM", "(external orthogonal) direct sum", "jumlah langsung ortogonal (eksternal)"),
    ("CLOSED-LINEAR-SPAN", "closed linear span", "rentang linear tertutup"),
    ("ORTHONORMAL", "orthonormal", "ortonormal"),
    ("ORTHONORMAL-BASIS", "orthonormal basis", "basis ortonormal"),
    ("COMPLETE-ORTHONORMAL-SET", "complete orthonormal set", "himpunan ortonormal lengkap"),
    ("HILBERT-SPACE-BASIS", "Hilbert space basis", "basis ruang Hilbert"),
    ("USUAL", "usual", "biasa"),
    ("STANDARD", "standard", "standar"),
    ("TRIGONOMETRIC-POLYNOMIAL", "trigonometric polynomial", "polinom trigonometri"),
    ("DIMENSION", "dimension", "dimensi"),
    ("CODIMENSION", "codimension", "kodimensi"),
    ("CONJUGATE-LINEAR", "conjugate linear", "linear konjugat"),
    ("ANTI-ISOMORPHISM", "anti-isomorphism", "antiisomorfisme"),
    ("CONJUGATION", "conjugation", "konjugasi"),
    ("WEAK-TOPOLOGY", "weak topology", "topologi lemah"),
    ("PRODUCT-TOPOLOGY", "product topology", "topologi hasil kali"),
    ("CONVERGE-WEAKLY", "converge weakly", "konvergen secara lemah"),
    ("CONVERGE-STRONGLY", "converge strongly", "konvergen secara kuat"),
    ("CONVERGE-IN-NORM", "converge in norm", "konvergen dalam norma"),
    ("WEAKLY-CLOSED", "weakly closed", "tertutup secara lemah"),
    ("WEAKLY-COMPACT", "weakly compact", "kompak secara lemah"),
    ("WEAKLY-CONTINUOUS", "weakly continuous", "kontinu secara lemah"),
    ("UNIVERSAL-MAPPING-DIAGRAM", "universal mapping diagram", "diagram pemetaan universal"),
    ("UNIVERSAL-PROPERTY", "universal property", "sifat universal"),
    ("UNIVERSAL-MORPHISM", "universal morphism", "morfisme universal"),
    ("UNIVERSAL-OBJECT", "universal object", "objek universal"),
    ("FREE-ON", "free on", "bebas pada"),
    ("FREE-OBJECT-GENERATED-BY", "free object generated by", "objek bebas yang dibangkitkan oleh"),
    ("FREE-VECTOR-SPACES", "free vector spaces", "ruang vektor bebas"),
    ("CHARACTERISTIC-FUNCTION", "characteristic function", "fungsi karakteristik"),
    ("WORD", "word", "kata"),
    ("EMPTY-WORD", "empty word", "kata kosong"),
    ("CONCATENATION", "concatenation", "konkatenasi"),
    ("FREE-MONOID", "free monoid", "monoid bebas"),
    ("FREE-SEMIGROUP", "free semigroup", "semigrup bebas"),
    ("COPRODUCT", "coproduct", "koproduk"),
    ("DIRECT-SUM", "direct sum", "jumlah langsung"),
    ("CO-UNIVERSAL-MORPHISM", "co-universal morphism for $B$ (with respect to", r"morfisme kouniversal untuk $B$ (terhadap~$\ftr F$)"),
    ("CATEGORICAL-PRODUCT", "product", "hasil kali"),
    ("COMPLETION", "completion", "pelengkapan"),
]
EXISTING_TERM_IDS = {"coproduct": "TERM-COPRODUCT", "direct sum": "TERM-DIRECT-SUM"}


def term_id_map() -> dict[str, str]:
    return {
        source_term: EXISTING_TERM_IDS.get(source_term, f"TERM-{stable_id}")
        for stable_id, source_term, _ in TERM_SPECS
    }


def terminology_records() -> list[dict]:
    return [
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "term",
            "id": f"TERM-{stable_id}",
            "source_term": source_term,
            "locale": "id-ID",
            "preferred": preferred,
            "variants": [],
            "rejected": [],
            "scope": "Hilbert spaces and universal constructions",
            "evidence": "FAOA-2015-CH04 admitted target source/id-ID/Hilbert_spaces-id.tex; backend/index_terms.csv; provenance/CH04_BUILD_AND_QA_RECEIPT.md",
        }
        for stable_id, source_term, preferred in TERM_SPECS
        if source_term not in EXISTING_TERM_IDS
    ]


def qa_records(formula_summary: dict[str, object]) -> list[dict]:
    checker = "qa/check_ch04_translation.py"
    checker_sha = "bcf98112417cf1a0405207d79a4f877f53fd25514ea72dfb985a347843118954"
    typed_ids = [
        "QA-CH04-STRUCTURAL-20260822",
        "QA-CH04-MATH-20260822",
        "QA-CH04-LANGUAGE-20260822",
        "QA-CH04-BUILD-20260822",
        "QA-CH04-VISUAL-20260822",
        "QA-CH04-ACCESSIBILITY-20260822",
        "QA-CH04-RIGHTS-20260822",
    ]
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "result": "pass",
        "timestamp": "2026-08-22",
        "responsible_workflow": "Codex",
        "qa_receipt_id": ADMISSION_QA_ID,
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH04_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07",
    }
    return [
        common
        | {
            "id": typed_ids[0],
            "qa_type": "unit_structural",
            "witness": checker,
            "witness_sha256": checker_sha,
            "semantic_anchors": 131,
            "semantic_units": 130,
            "segments": 160,
            "labels": 44,
            "references": 53,
            "ordinary_target_references": 50,
            "future_target_references": 1,
            "equation_references": 2,
            "citations": 12,
            "index_terms": 177,
            "defined_terms": 59,
            "exercise_environments": 10,
            "proof_hints": 11,
            "diagram_blocks": 11,
        },
        common
        | {
            "id": typed_ids[1],
            "qa_type": "unit_mathematical",
            "witness": checker,
            "witness_sha256": checker_sha,
            "source_math_surfaces": 817,
            "target_math_surfaces": 817,
            **formula_summary,
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
            "placeholders": 0,
            "terminology_reconciled": True,
        },
        common
        | {
            "id": typed_ids[3],
            "qa_type": "cumulative_build",
            "witness": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf",
            "witness_sha256": "716e3524060f64e4728b4d3d8c1a2b906f377ec4e3b3a3cd1ef3e61759a3dd94",
            "master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH04-MASTER",
            "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH04-PDF",
            "final_pdf_locked": True,
            "pages": 75,
        },
        common
        | {
            "id": typed_ids[4],
            "qa_type": "cumulative_visual",
            "witness": "qa/CH04_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
            "witness_sha256": "699009af48643839f1b2ab216d90c4e6f07cf4c3f92d60461d2ccfdae219a8a0",
            "render_manifest_artifact_id": "ARTIFACT-FAOA-ID-CH04-RENDER-MANIFEST",
            "contact_sheet_artifact_id": "ARTIFACT-FAOA-ID-CH04-CONTACT-SHEET",
            "pages_rendered": 75,
            "pages_inspected": 75,
            "visual_defects": 0,
        },
        common
        | {
            "id": typed_ids[5],
            "qa_type": "cumulative_accessibility",
            "result": "fail",
            "failure_scope": "claim_of_fully_accessible_pdf",
            "witness": "qa/CH04_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
            "witness_sha256": "699009af48643839f1b2ab216d90c4e6f07cf4c3f92d60461d2ccfdae219a8a0",
            "tagged_pdf": False,
            "math_diagram_unicode_maps_complete": False,
            "ordinary_prose_extraction": "intact",
            "admission_blocker_for_visual_pdf_boundary": False,
            "accessible_html_or_tagged_pdf_state": "pending",
        },
        common
        | {
            "id": typed_ids[6],
            "qa_type": "unit_rights_privacy",
            "witness": "source/id-ID/functional-analysis-id-through-ch04.tex",
            "witness_sha256": "598bd1f91096a2e0e19314995f44f79f246ca06cad6328ce9e996af074ceff6c",
            "rights_id": RIGHTS,
            "attribution_change_notice_sharealike_nonendorsement": "present",
            "excluded_components_absent": True,
        },
        common
        | {
            "id": ADMISSION_QA_ID,
            "qa_type": "unit_admission",
            "result": "pass",
            "decision": "admitted",
            "source_sha256": SOURCE_SHA,
            "target_sha256": TARGET_SHA,
            "build_master_sha256": "598bd1f91096a2e0e19314995f44f79f246ca06cad6328ce9e996af074ceff6c",
            "artifact_sha256": "716e3524060f64e4728b4d3d8c1a2b906f377ec4e3b3a3cd1ef3e61759a3dd94",
            "render_manifest_sha256": "9f8b88e46823e91920d27ade8f32af30ce347dccd0ab5d759afb2b07f0f64390",
            "corrections_ledger_sha256": "8909a33f5ed5dd37065fb4c3afb08e4e0659d17ef1d1a2b8f1d7f307ed1eef2d",
            "receipt_document_state": "present",
            "receipt_sha256": "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07",
            "typed_qa_event_ids": typed_ids,
            "all_required_admission_gates": "pass",
            "accessibility_remediation_state": "pending_nonblocking",
            "publication_state": "pending",
        },
    ]


def prior_label_map() -> dict[str, str]:
    records = [json.loads(line) for line in locked_prefix("semantic_units.jsonl").splitlines()]
    return {
        record["source_local_id"]: record["id"]
        for record in records
        if record.get("source_local_id")
    }


def build_math_pairs(source: str, target: str) -> tuple[list[dict], dict[str, object]]:
    source_math = ch03_math.extract_math(ch04check.blank_index_macros(source), SOURCE_ENCODING)
    target_math = ch03_math.extract_math(ch04check.blank_index_macros(target), TARGET_ENCODING)
    if len(source_math) != 817 or len(target_math) != 817:
        raise ValueError("Chapter 4 math-surface count changed")
    source_groups = ch04check.group_math_by_region(
        source_math, ch04check.structural_boundaries(source)
    )
    target_groups = ch04check.group_math_by_region(
        target_math, ch04check.structural_boundaries(target)
    )
    pairs: list[tuple[int, int, int, bool]] = []
    for region in sorted(set(source_groups) | set(target_groups)):
        source_by_key: dict[str, list[int]] = collections.defaultdict(list)
        target_by_key: dict[str, list[int]] = collections.defaultdict(list)
        for ordinal in source_groups[region]:
            source_by_key[ch03_math.math_key(source_math[ordinal]["normalized"])].append(ordinal)
        for ordinal in target_groups[region]:
            target_by_key[ch03_math.math_key(target_math[ordinal]["normalized"])].append(ordinal)
        unmatched_source: list[int] = []
        unmatched_target: list[int] = []
        for key in sorted(set(source_by_key) | set(target_by_key)):
            source_ordinals = source_by_key[key]
            target_ordinals = target_by_key[key]
            shared = min(len(source_ordinals), len(target_ordinals))
            pairs.extend(
                (region, source_ordinal, target_ordinal, True)
                for source_ordinal, target_ordinal in zip(
                    source_ordinals[:shared], target_ordinals[:shared], strict=True
                )
            )
            unmatched_source.extend(source_ordinals[shared:])
            unmatched_target.extend(target_ordinals[shared:])
        unmatched_source.sort()
        unmatched_target.sort()
        if len(unmatched_source) != len(unmatched_target):
            raise ValueError(f"Chapter 4 region {region} has unpaired math")
        pairs.extend(
            (region, source_ordinal, target_ordinal, False)
            for source_ordinal, target_ordinal in zip(
                unmatched_source, unmatched_target, strict=True
            )
        )
    pairs.sort(key=lambda item: item[1])
    if [item[1] for item in pairs] != list(range(817)) or sorted(item[2] for item in pairs) != list(
        range(817)
    ):
        raise ValueError("Chapter 4 formula pairing is not bijective")

    formula_records: list[dict] = []
    alignment_counts: collections.Counter[str] = collections.Counter()
    key_difference_signatures: list[tuple] = []
    for region, source_ordinal, target_ordinal, key_equal in pairs:
        source_record = source_math[source_ordinal]
        target_record = target_math[target_ordinal]
        signature = (
            region,
            source_ordinal,
            target_ordinal,
            source_record["line_start"],
            target_record["line_start"],
            source_record["delimiter"],
            ch04check.normalized_sha(source_record["normalized"]),
            ch04check.normalized_sha(target_record["normalized"]),
        )
        if key_equal and source_record["normalized"] == target_record["normalized"]:
            if source_ordinal == target_ordinal:
                alignment = "preserved_exact_after_text_aware_whitespace_normalization"
            else:
                alignment = "preserved_exact_after_text_aware_whitespace_normalization_reordered"
        elif key_equal:
            alignment = "localized_math_text_preserved_math_key"
        elif signature in ch04check.EXPECTED_MATH_KEY_LOCALIZATIONS:
            alignment = "localized_math_key_reviewed"
            key_difference_signatures.append(signature)
        else:
            alignment = "reviewed_source_correction"
            key_difference_signatures.append(signature)
        alignment_counts[alignment] += 1
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{source_ordinal + 1:04d}",
            "alignment": alignment,
            "math_key_alignment": "equal" if key_equal else "reviewed_difference",
            "ordinal_alignment": "same" if source_ordinal == target_ordinal else "localized_reordering",
            "structural_region": region,
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{source_ordinal + 1:04d}"],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{target_ordinal + 1:04d}"],
            "source_lines": [[source_record["line_start"], source_record["line_end"]]],
            "target_lines": [[target_record["line_start"], target_record["line_end"]]],
            "source_sha256": [source_record["sha256"]],
            "target_sha256": [target_record["sha256"]],
            "delimiter": source_record["delimiter"],
        }
        if not key_equal:
            record |= {
                "sequence_opcode": "replace",
                "qa_state": QA_STATE,
                "review_witness": "provenance/SOURCE_CORRECTIONS.md and qa/check_ch04_translation.py",
            }
        formula_records.append(record)

    expected_counts = {
        "preserved_exact_after_text_aware_whitespace_normalization": 787,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 15,
        "localized_math_text_preserved_math_key": 5,
        "localized_math_key_reviewed": 1,
        "reviewed_source_correction": 9,
    }
    if dict(alignment_counts) != expected_counts:
        raise ValueError(f"Chapter 4 formula alignments changed: {dict(alignment_counts)}")
    expected_differences = list(ch04check.EXPECTED_MATH_CORRECTIONS) + list(
        ch04check.EXPECTED_MATH_KEY_LOCALIZATIONS
    )
    if sorted(key_difference_signatures) != sorted(expected_differences):
        raise ValueError("Chapter 4 reviewed formula differences changed")
    summary: dict[str, object] = {
        "exact_normalized_alignments": 802,
        "math_key_equal_alignments": 807,
        "localized_reorderings": 15,
        "localized_math_text_alignments": 6,
        "reviewed_source_corrections": 9,
        "formula_map_records": 817,
    }
    return formula_records, summary


def main() -> None:
    source_bytes = SOURCE_PATH.read_bytes()
    target_bytes = TARGET_PATH.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha(source_bytes)) != (
        SOURCE_SIZE,
        SOURCE_LINES,
        SOURCE_SHA,
    ):
        raise ValueError("Chapter 4 source authority changed")
    if (len(target_bytes), len(target_bytes.splitlines()), sha(target_bytes)) != (
        TARGET_SIZE,
        TARGET_LINES,
        TARGET_SHA,
    ):
        raise ValueError("final Chapter 4 target lock changed")
    source = source_bytes.decode(SOURCE_ENCODING)
    target = target_bytes.decode(TARGET_ENCODING)

    verify_evidence()
    for name in PREFIX_LOCKS:
        locked_prefix(name)
    unit_boundaries()
    checker_run = subprocess.run(
        [sys.executable, str(ROOT / "qa" / "check_ch04_translation.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    checker_result = json.loads(checker_run.stdout)
    if checker_result.get("result") != "pass_reviewed_ch04_translation_locked":
        raise ValueError("Chapter 4 checker did not return its locked pass result")

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if len(source_anchors) != 131 or [ch01.anchor_signature(a) for a in source_anchors] != [
        ch01.anchor_signature(a) for a in target_anchors
    ]:
        raise ValueError("Chapter 4 semantic anchor topology differs")
    source_labels = ch04check.exact_macro_occurrences(source, "label")
    target_labels = ch04check.exact_macro_occurrences(target, "label")
    if len(source_labels) != 44 or [x["argument"] for x in source_labels] != [
        x["argument"] for x in target_labels
    ]:
        raise ValueError("Chapter 4 label sequence differs")

    semantic_units: list[dict] = []
    segment_records: list[dict] = []
    relations: list[dict] = []
    anchor_ids: list[str] = []
    current_section = CHAPTER_ID
    current_section_by_anchor: list[str] = []
    section_number = 0
    node_number = 0
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
                "source_path": "source/upstream/Hilbert_spaces.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_fragment_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/Hilbert_spaces-id.tex",
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
                "id": f"{CHAPTER_ID}-REL-CONTAINS-{len(semantic_units):04d}",
                "relation_type": "contains",
                "from_id": parent_id,
                "to_id": unit_id,
            }
        )
    if (len(semantic_units), section_number, node_number) != (130, 8, 122):
        raise ValueError("Chapter 4 semantic-unit topology invariant failed")

    source_parts: list[tuple[int, int, str, str]] = []
    target_parts: list[tuple[int, int, str, str]] = []
    previous_source = previous_target = 0
    previous_parent = CHAPTER_ID
    for index, (source_anchor, target_anchor, unit_id) in enumerate(
        zip(source_anchors, target_anchors, anchor_ids, strict=True)
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
    if len(source_parts) != 160 or len(target_parts) != 160:
        raise ValueError("Chapter 4 source/target segment count differs from 160")

    for number, (source_part, target_part) in enumerate(
        zip(source_parts, target_parts, strict=True), 1
    ):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if role != target_role or parent_id != target_parent:
            raise ValueError("Chapter 4 source/target segment role differs")
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
                "source_path": "source/upstream/Hilbert_spaces.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_bytes": source_fragment["bytes"],
                "source_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/Hilbert_spaces-id.tex",
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
    if len(local_label_map) != 44:
        raise ValueError("Chapter 4 local label map changed")

    source_refs = ch04check.exact_macro_occurrences(source, "ref")
    target_refs = ch04check.exact_macro_occurrences(target, "ref")
    expected_target_refs = [x["argument"] for x in source_refs if x["argument"] != "C067441"]
    if len(source_refs) != 51 or len(target_refs) != 50 or [x["argument"] for x in target_refs] != expected_target_refs:
        raise ValueError("Chapter 4 ref sequence differs")
    future_refs = ch04check.futurexref_occurrences(target)
    if [(x["printed"], x["source_label"]) for x in future_refs] != [("6.2.9", "C067441")]:
        raise ValueError("Chapter 4 futurexref endpoint differs")
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
        elif label == "C067441":
            to_id = "ERDMAN-FAOA-2015-LABEL-C067441"
            resolution = "pending_later_source_unit"
            target_surface = "futurexref"
        else:
            raise ValueError(f"unexpected unresolved Chapter 4 reference: {label}")
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
    if dict(reference_counts) != {
        "admitted_prior_unit": 23,
        "local": 27,
        "pending_later_source_unit": 1,
    }:
        raise ValueError(f"Chapter 4 reference-resolution counts changed: {dict(reference_counts)}")

    source_eqrefs = ch04check.exact_macro_occurrences(source, "eqref")
    target_eqrefs = ch04check.exact_macro_occurrences(target, "eqref")
    if [x["argument"] for x in source_eqrefs] != ["00078i", "00078i"] or [
        x["argument"] for x in target_eqrefs
    ] != ["00078i", "00078i"]:
        raise ValueError("Chapter 4 eqref sequence differs")
    for number, occurrence in enumerate(source_eqrefs, 1):
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-EQREF-{number:04d}",
                "relation_type": "xref",
                "from_id": ch01.containing_segment(segment_records, occurrence["start"], "source"),
                "to_id": local_label_map[occurrence["argument"]],
                "source_local_id": occurrence["argument"],
                "resolution": "local",
                "target_surface": "eqref",
            }
        )

    source_cites = ch04check.exact_macro_occurrences(source, "cite")
    target_cites = ch04check.exact_macro_occurrences(target, "cite")
    if len(source_cites) != 12 or [x["argument"] for x in source_cites] != [
        x["argument"] for x in target_cites
    ]:
        raise ValueError("Chapter 4 citation sequence differs")
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
    if cite_key_count != 12:
        raise ValueError("Chapter 4 citation-key count changed")

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
            raise ValueError("Chapter 4 proof hint lacks a preceding statement")
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
    if hint_relations != 11:
        raise ValueError("Chapter 4 proof-hint topology changed")

    source_df = ch04check.exact_macro_occurrences(source, "df")
    target_df = ch04check.exact_macro_occurrences(target, "df")
    term_ids = term_id_map()
    if len(source_df) != 59 or len(target_df) != 59 or set(term_ids) != {
        record["argument"] for record in source_df
    }:
        raise ValueError("Chapter 4 defined-term inventory changed")
    for number, (source_term, target_term) in enumerate(zip(source_df, target_df, strict=True), 1):
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}",
                "relation_type": "uses_term",
                "from_id": ch01.containing_segment(segment_records, source_term["start"], "source"),
                "to_id": term_ids[source_term["argument"]],
                "source_term_tex": source_term["argument"],
                "target_term_tex": target_term["argument"],
                "locale": "id-ID",
            }
        )

    source_terms = ch04check.exact_macro_occurrences(source, "index")
    target_terms = ch04check.exact_macro_occurrences(target, "index")
    moved = [target_terms[position] for position in ch04check.MOVED_INDEX_TARGET_POSITIONS]
    remaining_target = [
        record
        for position, record in enumerate(target_terms)
        if position not in ch04check.MOVED_INDEX_TARGET_POSITIONS
    ]
    aligned_target: list[dict] = []
    remaining_cursor = 0
    for position in range(len(source_terms)):
        if position in ch04check.MOVED_INDEX_SOURCE_POSITIONS:
            aligned_target.append(moved[ch04check.MOVED_INDEX_SOURCE_POSITIONS.index(position)])
        else:
            aligned_target.append(remaining_target[remaining_cursor])
            remaining_cursor += 1
    if len(source_terms) != 177 or len(aligned_target) != 177:
        raise ValueError("Chapter 4 index-term alignment changed")
    term_buffer = io.StringIO(newline="")
    term_writer = csv.writer(term_buffer, lineterminator="\n")
    for number, (source_term, target_term) in enumerate(
        zip(source_terms, aligned_target, strict=True), 1
    ):
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
    if len(exercises) != 10 or any(record["upstream_hint_ids"] for record in exercises):
        raise ValueError("Chapter 4 exercise-support topology changed")

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
            "ARTIFACT-FAOA-ID-CH04-TARGET-TEX",
            "ARTIFACT-FAOA-ID-CH04-QA-RECEIPT",
        ),
        1,
    ):
        relations.append(
            relation_common
            | {
                "id": f"{CHAPTER_ID}-REL-TERM-EVIDENCE-{number:04d}",
                "relation_type": "terminology_evidence",
                "to_id": artifact_id,
                "evidence_scope": "all Chapter 4 terminology records",
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
    if len(relations) != 670:
        raise ValueError(f"Chapter 4 relation invariant failed: {len(relations)}")

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
                "receipt_document_state": "present",
                "translation_state": TRANSLATION_STATE,
                "qa_state": QA_STATE,
                **formula_summary,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
