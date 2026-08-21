#!/usr/bin/env python3
"""Append deterministic, admitted Chapter 2 backend records.

Chapter 1 is a locked admitted prefix.  This generator validates that prefix,
discards any prior Chapter 2 suffix, and appends a fresh evidence-backed
Chapter 2 projection.  Run ``generate_backend.py`` to rebuild both chapters.
"""

from __future__ import annotations

import csv
import difflib
import hashlib
import io
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import generate_ch01_backend as ch01


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SOURCE_PATH = ROOT / "source" / "upstream" / "categories.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "categories-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH02"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
TRANSLATION_STATE = "admitted"
QA_STATE = "passed"
ADMISSION_QA_ID = "QA-CH02-ADMISSION-20260821"

# Exact Chapter 1 generator outputs.  Every generated Chapter 2 file must
# retain the corresponding bytes as a literal prefix.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (102130, "a8847fbac37ccbb008643df8dab994c56b2ccf007f165d9160e1d6242a056608"),
    "segments.jsonl": (116663, "4d04b9459f546ed18a865c544c3c39c1b6f6f4628ae66c157e3f869bc6d73f7a"),
    "relations.jsonl": (120798, "0fac179bf89231cafb7f3120335b9f972febf1346c67b8d7035c55e1f99488dd"),
    "formula_map.jsonl": (487668, "7337ec874b039527e44ea476cc57a453b04015343f193685ea75418d46dcf381"),
    "exercise_support.jsonl": (3062, "185420e94dbf748f3617a462b8f03936e7cf33a66b9f47b65dcf2c9a242bf4af"),
    "index_terms.csv": (47079, "e5d733d2d61493f392cc384e7d67219eb21ccb08d50e06a434654b0d1c10545b"),
    "artifacts.jsonl": (1394, "804a07178df0b03611f29c9aad15464e4123d30ea5f761367132dd39bfe50e3d"),
    "qa_events.jsonl": (2533, "c4bfa226d77ec9b7df67629c610e036dc03ba64f10a1dd048743ac18bebec4a2"),
    "corrections.jsonl": (6074, "a3663f1999eee34e4e0535f46cc4a5c33a78e46885ed99900bb587327fbe7b05"),
    "terminology.jsonl": (6030, "be3b6689fbc7bd5c1453bc71755257041df34d3c83c9af7bfe6386177fbeb39d"),
}
UNIT_PREFIX_LOCK = (957, "d58c211c782422004d0d144b779a75dce09a964052026d2525352169456440d4")
UNIT_SUFFIX_LOCK = (7276, "d2050b93c9955e79d42a2f38af5cf21be253d1f6ba85779db2e3afe2de790aef")
EVIDENCE_LOCKS = {
    "source/id-ID/functional-analysis-id-through-ch02.tex": (
        9437,
        "1ca424e166df692e8bf69421a0a1720d5dfb2540c52053bb036be99ecdde9ecd",
    ),
    "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-2.pdf": (
        795305,
        "7a04eb72ef5445ee06e429e7552b8e14a02a993c916b4632cdb9219a928a3bdb",
    ),
    "provenance/CH02_BUILD_AND_QA_RECEIPT.md": (
        6715,
        "4acd8a6e7942a8f57ad8442e9fca2fb68d041904962e18ed588704bc2098175f",
    ),
    "provenance/CH02_RENDER_MANIFEST.csv": (
        2938,
        "ac7f79b32125a554322faa242c656704f5643e78598c5973c68072ec28d8d670",
    ),
    "provenance/CH02_CONTACT_SHEET.png": (
        4172883,
        "fa396362069095471d1c6cfe23327d4e6362efe6a325684dc4236dc5dc91fc53",
    ),
    "provenance/SOURCE_CORRECTIONS.md": (
        3408,
        "26708cf62c00202ad224a5d5413069e7bd376497a96e3c7c30487b66214d5c16",
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def locked_prefix(name: str) -> bytes:
    size, expected_sha = PREFIX_LOCKS[name]
    data = (BACKEND / name).read_bytes()
    if len(data) < size:
        raise ValueError(f"{name} is shorter than its locked Chapter 1 prefix")
    prefix = data[:size]
    if sha(prefix) != expected_sha:
        raise ValueError(f"{name} Chapter 1 prefix hash changed")
    if not prefix.endswith(b"\n"):
        raise ValueError(f"{name} Chapter 1 prefix lacks final LF")
    return prefix


def append_jsonl(name: str, records: list[dict]) -> None:
    suffix = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")
    (BACKEND / name).write_bytes(locked_prefix(name) + suffix)


def chapter_two_unit() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 2,
        "source_path": "categories.tex",
        "source_bytes": 27446,
        "source_lines": 574,
        "source_sha256": "6f5115e4058902e99ab7157ad59ea95f0e0013e2f4272c05ff421933f7255775",
        "source_title": "A VERY BRIEF DIGRESSION ON THE LANGUAGE OF CATEGORIES",
        "target_path": "source/id-ID/categories-id.tex",
        "target_bytes": 29254,
        "target_lines": 570,
        "target_sha256": "39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd",
        "target_title": "Selingan Sangat Singkat tentang Bahasa Kategori",
        "course_role": "D20_core",
        "translation_state": TRANSLATION_STATE,
        "qa_state": QA_STATE,
        "source_corrections": 6,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch02.tex",
        "build_master_bytes": 9437,
        "build_master_sha256": "1ca424e166df692e8bf69421a0a1720d5dfb2540c52053bb036be99ecdde9ecd",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-2.pdf",
        "artifact_bytes": 795305,
        "artifact_pages": 32,
        "artifact_sha256": "7a04eb72ef5445ee06e429e7552b8e14a02a993c916b4632cdb9219a928a3bdb",
        "qa_receipt_id": ADMISSION_QA_ID,
        "rights_id": RIGHTS,
    }


def unit_boundaries() -> tuple[bytes, bytes]:
    path = BACKEND / "units.jsonl"
    data = path.read_bytes()
    prefix_size, prefix_sha = UNIT_PREFIX_LOCK
    suffix_size, suffix_sha = UNIT_SUFFIX_LOCK
    if len(data) <= prefix_size + suffix_size:
        raise ValueError("units.jsonl lacks a replaceable Chapter 2 record")
    prefix = data[:prefix_size]
    suffix = data[-suffix_size:]
    if sha(prefix) != prefix_sha or sha(suffix) != suffix_sha:
        raise ValueError("units.jsonl non-Chapter-2 byte lock changed")
    middle = data[prefix_size:-suffix_size]
    middle_lines = middle.splitlines()
    if len(middle_lines) != 1 or json.loads(middle_lines[0]).get("id") != CHAPTER_ID:
        raise ValueError("units.jsonl Chapter 2 replacement boundary changed")
    return prefix, suffix


def rewrite_units() -> None:
    path = BACKEND / "units.jsonl"
    prefix, suffix = unit_boundaries()
    encoded = (
        json.dumps(chapter_two_unit(), ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    path.write_bytes(prefix + encoded + suffix)


def verify_evidence() -> None:
    for relative_path, (expected_bytes, expected_sha) in EVIDENCE_LOCKS.items():
        data = (ROOT / relative_path).read_bytes()
        if (len(data), sha(data)) != (expected_bytes, expected_sha):
            raise ValueError(f"admission evidence changed: {relative_path}")


def artifact_records() -> list[dict]:
    return [
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": "ARTIFACT-FAOA-ID-CH02-TARGET-TEX",
            "unit_id": CHAPTER_ID,
            "artifact_kind": "admitted_translation_source",
            "path": "source/id-ID/categories-id.tex",
            "bytes": 29254,
            "lines": 570,
            "sha256": "39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd",
            "locale": "id-ID",
            "qa_receipt_id": ADMISSION_QA_ID,
        },
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH02-MASTER",
            "unit_id": CHAPTER_ID,
            "artifact_kind": "cumulative_TeX_master",
            "path": "source/id-ID/functional-analysis-id-through-ch02.tex",
            "bytes": 9437,
            "sha256": "1ca424e166df692e8bf69421a0a1720d5dfb2540c52053bb036be99ecdde9ecd",
            "cumulative_through_unit_id": CHAPTER_ID,
            "locale": "id-ID",
            "qa_receipt_id": ADMISSION_QA_ID,
        },
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": "ARTIFACT-FAOA-ID-THROUGH-CH02-PDF",
            "unit_id": CHAPTER_ID,
            "artifact_kind": "canonical_cumulative_reader_pdf",
            "path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-2.pdf",
            "bytes": 795305,
            "sha256": "7a04eb72ef5445ee06e429e7552b8e14a02a993c916b4632cdb9219a928a3bdb",
            "pages": 32,
            "page_size": "US Letter",
            "locale": "id-ID",
            "pdf_lang": "id-ID",
            "tagged_pdf": False,
            "bookmarks": True,
            "toolchain": "MiKTeX 26.5; pdfTeX 1.40.29; latexmk 4.88; BibTeX; MakeIndex; Xy-pic",
            "source_date_epoch": 1444126743,
            "two_clean_builds_byte_identical": True,
            "qa_receipt_id": ADMISSION_QA_ID,
        },
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": "ARTIFACT-FAOA-ID-CH02-QA-RECEIPT",
            "unit_id": CHAPTER_ID,
            "artifact_kind": "build_and_QA_receipt",
            "path": "provenance/CH02_BUILD_AND_QA_RECEIPT.md",
            "bytes": 6715,
            "sha256": "4acd8a6e7942a8f57ad8442e9fca2fb68d041904962e18ed588704bc2098175f",
            "decision": "admitted",
            "qa_receipt_id": ADMISSION_QA_ID,
        },
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": "ARTIFACT-FAOA-ID-CH02-RENDER-MANIFEST",
            "unit_id": CHAPTER_ID,
            "artifact_kind": "visual_QA_render_manifest",
            "path": "provenance/CH02_RENDER_MANIFEST.csv",
            "bytes": 2938,
            "sha256": "ac7f79b32125a554322faa242c656704f5643e78598c5973c68072ec28d8d670",
            "rows": 32,
            "coverage": "32 page PNGs",
            "qa_receipt_id": ADMISSION_QA_ID,
        },
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": "ARTIFACT-FAOA-ID-CH02-CONTACT-SHEET",
            "unit_id": CHAPTER_ID,
            "artifact_kind": "visual_QA_contact_sheet",
            "path": "provenance/CH02_CONTACT_SHEET.png",
            "bytes": 4172883,
            "sha256": "fa396362069095471d1c6cfe23327d4e6362efe6a325684dc4236dc5dc91fc53",
            "visual_pages": 32,
            "all_pages_inspected": True,
            "qa_receipt_id": ADMISSION_QA_ID,
        },
        {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": "ARTIFACT-FAOA-ID-CH02-CORRECTIONS-LEDGER",
            "unit_id": CHAPTER_ID,
            "artifact_kind": "source_corrections_ledger",
            "path": "provenance/SOURCE_CORRECTIONS.md",
            "bytes": 3408,
            "sha256": "26708cf62c00202ad224a5d5413069e7bd376497a96e3c7c30487b66214d5c16",
            "chapter_correction_count": 6,
            "qa_receipt_id": ADMISSION_QA_ID,
        },
    ]


def qa_records() -> list[dict]:
    receipt = "provenance/CH02_BUILD_AND_QA_RECEIPT.md"
    common = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "result": "pass",
        "witness": receipt,
        "witness_sha256": "4acd8a6e7942a8f57ad8442e9fca2fb68d041904962e18ed588704bc2098175f",
        "timestamp": "2026-08-21",
        "responsible_workflow": "Codex",
    }
    typed_ids = [
        "QA-CH02-STRUCTURAL-20260821",
        "QA-CH02-MATH-20260821",
        "QA-CH02-LANGUAGE-20260821",
        "QA-CH02-BUILD-20260821",
        "QA-CH02-VISUAL-20260821",
        "QA-CH02-RIGHTS-20260821",
    ]
    return [
        common
        | {
            "id": typed_ids[0],
            "qa_type": "unit_structural",
            "semantic_anchors": 35,
            "semantic_units": 34,
            "segments": 41,
            "labels": 12,
            "citations": 4,
            "index_terms": 137,
            "exercise_environments": 0,
        },
        common
        | {
            "id": typed_ids[1],
            "qa_type": "unit_mathematical",
            "source_math_surfaces": 396,
            "target_math_surfaces": 397,
            "exact_normalized_alignments": 395,
            "non_equal_map_ids": [
                "FAOA-2015-CH02-MATHMAP-0181",
                "FAOA-2015-CH02-MATHMAP-0386",
            ],
            "unexplained_deltas": 0,
        },
        common
        | {
            "id": typed_ids[2],
            "qa_type": "unit_language",
            "severity_counts": {"P1": 0, "P2": 0, "P3": 0},
            "unintended_english_prose": 0,
            "mojibake_or_replacement_characters": 0,
            "terminology_reconciled": True,
        },
        common
        | {
            "id": typed_ids[3],
            "qa_type": "cumulative_build",
            "master_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH02-MASTER",
            "pdf_artifact_id": "ARTIFACT-FAOA-ID-THROUGH-CH02-PDF",
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
            "render_manifest_artifact_id": "ARTIFACT-FAOA-ID-CH02-RENDER-MANIFEST",
            "contact_sheet_artifact_id": "ARTIFACT-FAOA-ID-CH02-CONTACT-SHEET",
            "pages_rendered": 32,
            "pages_inspected": 32,
            "visual_defects": 0,
        },
        common
        | {
            "id": typed_ids[5],
            "qa_type": "unit_rights_privacy",
            "rights_id": RIGHTS,
            "attribution_change_notice_sharealike_nonendorsement": "present",
            "excluded_components_absent": True,
            "privacy_scans": "pass",
        },
        common
        | {
            "id": ADMISSION_QA_ID,
            "qa_type": "unit_admission",
            "decision": "admitted",
            "source_sha256": "6f5115e4058902e99ab7157ad59ea95f0e0013e2f4272c05ff421933f7255775",
            "target_sha256": "39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd",
            "build_master_sha256": "1ca424e166df692e8bf69421a0a1720d5dfb2540c52053bb036be99ecdde9ecd",
            "artifact_sha256": "7a04eb72ef5445ee06e429e7552b8e14a02a993c916b4632cdb9219a928a3bdb",
            "render_manifest_sha256": "ac7f79b32125a554322faa242c656704f5643e78598c5973c68072ec28d8d670",
            "corrections_ledger_sha256": "26708cf62c00202ad224a5d5413069e7bd376497a96e3c7c30487b66214d5c16",
            "receipt_sha256": "4acd8a6e7942a8f57ad8442e9fca2fb68d041904962e18ed588704bc2098175f",
            "typed_qa_event_ids": typed_ids,
            "all_required_gates": "pass",
        },
    ]


def correction_records() -> list[dict]:
    shared = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "correction",
        "unit_id": CHAPTER_ID,
        "target_disposition": "corrected",
        "ledger_path": "provenance/SOURCE_CORRECTIONS.md",
        "ledger_sha256": "26708cf62c00202ad224a5d5413069e7bd376497a96e3c7c30487b66214d5c16",
        "qa_receipt_id": ADMISSION_QA_ID,
        "upstream_report": "deferred_until_complete_and_separately_authorized",
    }
    specifications = [
        (
            "categories.tex:78--84",
            "index_hook_scope",
            "Attach the small and locally-small index hooks to the definitions they describe.",
        ),
        (
            "categories.tex:305--316",
            "false_nonconcreteness_claim",
            "Replace the false non-concrete claim with the accurate not-presented-concretely distinction.",
        ),
        (
            "categories.tex:262",
            "typed_identity_notation",
            r"Use the codomain identity \\vc 1_B consistently with \\vc 1_A.",
        ),
        (
            "categories.tex:537--548",
            "domain_and_missing_arrow_action",
            r"Qualify element notation to concrete categories and supply \\ftr D(f):=(f,f).",
        ),
        (
            [
                "categories.tex:25",
                "categories.tex:190",
                "categories.tex:217",
                "categories.tex:458",
                "categories.tex:488",
            ],
            "source_language",
            "Repair five source-language agreement or wording slips naturally in translation.",
        ),
        (
            "categories.tex:384",
            "future_cross_reference",
            "Represent C069414 as a typed future cross-reference at the Chapter 2 boundary.",
        ),
    ]
    return [
        shared
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
        ("CATEGORY", "category", "kategori", [], [], "categorical language"),
        ("OBJECT", "object", "objek", [], [], "object of a category"),
        ("MORPHISM", "morphism", "morfisme", ["panah"], [], "categorical language"),
        ("COMPOSITION", "composition", "komposisi", [], [], "composition of morphisms"),
        ("LOCALLY-SMALL-CATEGORY", "locally small category", "kategori kecil secara lokal", [], [], "categorical size"),
        ("SMALL-CATEGORY", "small category", "kategori kecil", [], [], "categorical size"),
        ("CONCRETE-CATEGORY", "concrete category", "kategori konkret", [], [], "categorical language"),
        ("ISOMORPHISM", "isomorphism", "isomorfisme", [], [], "categorical language"),
        ("MONOMORPHISM", "monomorphism", "monomorfisme", [], [], "Erdman concrete-category convention"),
        ("EPIMORPHISM", "epimorphism", "epimorfisme", [], [], "Erdman concrete-category convention"),
        ("FUNCTOR", "functor", "funktor", [], [], "categorical language"),
        ("COVARIANT-FUNCTOR", "covariant functor", "funktor kovarian", [], [], "functors"),
        ("CONTRAVARIANT-FUNCTOR", "contravariant functor", "funktor kontravarian", [], [], "functors"),
        ("OBJECT-MAP", "object map", "pemetaan objek", [], [], "functors"),
        ("MORPHISM-MAP", "morphism map", "pemetaan morfisme", [], [], "functors"),
        ("FORGETFUL-FUNCTOR", "forgetful functor", "funktor pelupa", [], [], "functors"),
        ("POWER-SET", "power set", "himpunan kuasa", [], [], "power-set functors"),
        ("DIAGONAL-FUNCTOR", "diagonal functor", "funktor diagonal", [], [], "functors"),
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
            "evidence": "FAOA-2015-CH02 and backend/index_terms.csv",
        }
        for stable_id, source_term, preferred, variants, rejected, scope in specifications
    ]


def main() -> None:
    source_bytes = SOURCE_PATH.read_bytes()
    target_bytes = TARGET_PATH.read_bytes()
    source = source_bytes.decode(SOURCE_ENCODING)
    target = target_bytes.decode(TARGET_ENCODING)
    if sha(source_bytes) != "6f5115e4058902e99ab7157ad59ea95f0e0013e2f4272c05ff421933f7255775":
        raise ValueError("Chapter 2 source authority hash changed")
    if sha(target_bytes) != "39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd":
        raise ValueError("Chapter 2 translated target hash changed")
    if (len(source_bytes), len(source.splitlines())) != (27446, 574):
        raise ValueError("Chapter 2 source size/line invariant failed")
    if (len(target_bytes), len(target.splitlines())) != (29254, 570):
        raise ValueError("Chapter 2 target size/line invariant failed")

    # Fail before the first write if any immutable admission evidence or
    # Chapter 1/non-Chapter-2 byte boundary has changed.
    verify_evidence()
    for name in PREFIX_LOCKS:
        locked_prefix(name)
    unit_boundaries()

    source_anchors = ch01.parse_anchors(source)
    target_anchors = ch01.parse_anchors(target)
    if [ch01.anchor_signature(a) for a in source_anchors] != [
        ch01.anchor_signature(a) for a in target_anchors
    ]:
        raise ValueError("Chapter 2 source/target anchor topology differs")
    if len(source_anchors) != 35:
        raise ValueError(f"expected 35 Chapter 2 anchors, found {len(source_anchors)}")

    source_labels = ch01.macro_occurrences(source, "label")
    target_labels = ch01.macro_occurrences(target, "label")
    if len(source_labels) != 12 or len(target_labels) != 12:
        raise ValueError("Chapter 2 label occurrence count changed")
    if [item["argument"] for item in source_labels] != [item["argument"] for item in target_labels]:
        raise ValueError("Chapter 2 source/target label sequence differs")

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
        if source_anchor["anchor_type"] != "chapter":
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
                    "source_path": "source/upstream/categories.tex",
                    "source_line_start": source_fragment["line_start"],
                    "source_line_end": source_fragment["line_end"],
                    "source_fragment_sha256": source_fragment["sha256"],
                    "target_path": "source/id-ID/categories-id.tex",
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
    if (len(semantic_units), section_number, node_number) != (34, 2, 32):
        raise ValueError("Chapter 2 semantic-unit topology invariant failed")

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
    if len(source_parts) != len(target_parts) or len(source_parts) != 41:
        raise ValueError("Chapter 2 source/target segment count differs from 41")

    for number, (source_part, target_part) in enumerate(zip(source_parts, target_parts), 1):
        source_start, source_end, role, parent_id = source_part
        target_start, target_end, target_role, target_parent = target_part
        if role != target_role or parent_id != target_parent:
            raise ValueError("Chapter 2 source/target segment role differs")
        segment_id = f"{CHAPTER_ID}-SEG-{number:04d}"
        source_fragment = ch01.fragment(source, source_start, source_end, SOURCE_ENCODING)
        target_fragment = ch01.fragment(target, target_start, target_end, TARGET_ENCODING)
        segment_records.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "segment",
                "id": segment_id,
                "parent_id": parent_id,
                "order": number,
                "segment_role": role,
                "source_path": "source/upstream/categories.tex",
                "source_line_start": source_fragment["line_start"],
                "source_line_end": source_fragment["line_end"],
                "source_bytes": source_fragment["bytes"],
                "source_sha256": source_fragment["sha256"],
                "target_path": "source/id-ID/categories-id.tex",
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
    if [item["argument"] for item in source_refs] != ["C069414", "C015127"]:
        raise ValueError("Chapter 2 source reference topology changed")
    if [item["argument"] for item in target_refs] != ["C015127"]:
        raise ValueError("Chapter 2 target local-reference topology changed")
    if target.count(r"\futurexref{6.3.4}{C069414}") != 1:
        raise ValueError("Chapter 2 futurexref endpoint changed")
    local_reference_count = 0
    future_reference_count = 0
    for number, occurrence in enumerate(source_refs, 1):
        label = occurrence["argument"]
        is_local = label in label_to_id
        local_reference_count += int(is_local)
        future_reference_count += int(not is_local)
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}",
                "relation_type": "xref",
                "from_id": ch01.containing_segment(segment_records, occurrence["start"], "source"),
                "to_id": label_to_id.get(label, f"ERDMAN-FAOA-2015-LABEL-{label}"),
                "source_local_id": label,
                "resolution": "local" if is_local else "pending_later_source_unit",
                "target_surface": "ref" if is_local else "futurexref",
            }
        )
    if (local_reference_count, future_reference_count) != (1, 1):
        raise ValueError("Chapter 2 local/future reference invariant failed")

    source_cites = ch01.macro_occurrences(source, "cite")
    target_cites = ch01.macro_occurrences(target, "cite")
    if len(source_cites) != 4 or [item["argument"] for item in source_cites] != [
        item["argument"] for item in target_cites
    ]:
        raise ValueError("Chapter 2 citation topology changed")
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
    if cite_key_count != 4:
        raise ValueError("Chapter 2 citation key count changed")
    if any(record["unit_kind"] == "exer" for record in semantic_units):
        raise ValueError("Chapter 2 unexpectedly contains an exercise environment")
    if len(relations) != 121:
        raise ValueError(f"expected 121 Chapter 2 relations, found {len(relations)}")

    source_terms = ch01.macro_occurrences(source, "index")
    target_terms = ch01.macro_occurrences(target, "index")
    if len(source_terms) != 137 or len(target_terms) != 137:
        raise ValueError("Chapter 2 index occurrence count changed")
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
    (BACKEND / "index_terms.csv").write_bytes(
        locked_prefix("index_terms.csv") + term_buffer.getvalue().encode("utf-8")
    )

    source_math = ch01.extract_math(source, SOURCE_ENCODING)
    target_math = ch01.extract_math(target, TARGET_ENCODING)
    if (len(source_math), len(target_math)) != (396, 397):
        raise ValueError("Chapter 2 math surface count changed")
    matcher = difflib.SequenceMatcher(
        a=[item["normalized"] for item in source_math],
        b=[item["normalized"] for item in target_math],
        autojunk=False,
    )
    deviations = [opcode for opcode in matcher.get_opcodes() if opcode[0] != "equal"]
    if deviations != [("replace", 180, 181, 180, 181), ("insert", 385, 385, 385, 386)]:
        raise ValueError(f"unexpected Chapter 2 math deviations: {deviations}")
    if source_math[180]["normalized"] != r"f(\vc1_A)=1_B":
        raise ValueError("Chapter 2 source formula replacement origin changed")
    if target_math[180]["normalized"] != r"f(\vc1_A)=\vc1_B":
        raise ValueError("Chapter 2 target formula replacement changed")
    if target_math[385]["normalized"] != r"\ftrD(f):=(f,f)":
        raise ValueError("Chapter 2 target formula insertion changed")

    formula_records: list[dict] = []
    formula_map_number = 0
    exact_formula_count = 0
    for tag, source_start, source_end, target_start, target_end in matcher.get_opcodes():
        if tag == "equal":
            for source_index, target_index in zip(
                range(source_start, source_end), range(target_start, target_end)
            ):
                formula_map_number += 1
                exact_formula_count += 1
                source_formula = source_math[source_index]
                target_formula = target_math[target_index]
                formula_records.append(
                    {
                        "schema": SCHEMA,
                        "schema_version": VERSION,
                        "record_type": "formula_map",
                        "id": f"{CHAPTER_ID}-MATHMAP-{formula_map_number:04d}",
                        "alignment": "preserved_exact_after_whitespace_normalization",
                        "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{source_index+1:04d}"],
                        "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{target_index+1:04d}"],
                        "source_lines": [[source_formula["line_start"], source_formula["line_end"]]],
                        "target_lines": [[target_formula["line_start"], target_formula["line_end"]]],
                        "source_sha256": [source_formula["sha256"]],
                        "target_sha256": [target_formula["sha256"]],
                    }
                )
        else:
            formula_map_number += 1
            formula_records.append(
                {
                    "schema": SCHEMA,
                    "schema_version": VERSION,
                    "record_type": "formula_map",
                    "id": f"{CHAPTER_ID}-MATHMAP-{formula_map_number:04d}",
                    "alignment": "reviewed_source_correction_or_target_clarity_insertion",
                    "sequence_opcode": tag,
                    "source_formula_ids": [
                        f"{CHAPTER_ID}-SRC-MATH-{index+1:04d}"
                        for index in range(source_start, source_end)
                    ],
                    "target_formula_ids": [
                        f"{CHAPTER_ID}-ID-MATH-{index+1:04d}"
                        for index in range(target_start, target_end)
                    ],
                    "source_lines": [
                        [source_math[index]["line_start"], source_math[index]["line_end"]]
                        for index in range(source_start, source_end)
                    ],
                    "target_lines": [
                        [target_math[index]["line_start"], target_math[index]["line_end"]]
                        for index in range(target_start, target_end)
                    ],
                    "source_sha256": [
                        source_math[index]["sha256"] for index in range(source_start, source_end)
                    ],
                    "target_sha256": [
                        target_math[index]["sha256"] for index in range(target_start, target_end)
                    ],
                    "qa_state": QA_STATE,
                    "review_witness": "locked source/target SHA-256 comparison",
                }
            )
    if (exact_formula_count, len(formula_records)) != (395, 397):
        raise ValueError("Chapter 2 formula-map alignment invariant failed")

    for record in segment_records:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            del record[key]
    append_jsonl("semantic_units.jsonl", semantic_units)
    append_jsonl("segments.jsonl", segment_records)
    append_jsonl("relations.jsonl", relations)
    append_jsonl("formula_map.jsonl", formula_records)
    append_jsonl("exercise_support.jsonl", [])
    rewrite_units()
    append_jsonl("artifacts.jsonl", artifact_records())
    append_jsonl("qa_events.jsonl", qa_records())
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
                "references": len(source_refs),
                "local_references": local_reference_count,
                "future_references": future_reference_count,
                "cites": cite_key_count,
                "index_terms": len(source_terms),
                "source_math": len(source_math),
                "target_math": len(target_math),
                "exact_math": exact_formula_count,
                "formula_map_records": len(formula_records),
                "exercises": 0,
                "translation_state": TRANSLATION_STATE,
                "qa_state": QA_STATE,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
