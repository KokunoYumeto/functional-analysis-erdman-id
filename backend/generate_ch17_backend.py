#!/usr/bin/env python3
"""Deterministically append the FAOA-2015-CH17 locale-neutral backend slice."""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path[:0] = [str(BACKEND), str(ROOT / "qa")]
import generate_ch16_backend as prior  # noqa: E402


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
CHAPTER_ID = "FAOA-2015-CH17"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_REL = "source/upstream/K0_functor.tex"
TARGET_REL = "source/id-ID/K0_functor-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-through-ch17.tex"
INVENTORY_REL = "qa/CH17_SOURCE_INVENTORY.md"
PRE_REVIEW_REL = "qa/CH17_PRETRANSLATION_MATH_REVIEW.md"
REPORT_REL = "qa/ch17-translation-report.json"
BILINGUAL_REVIEW_REL = "qa/CH17_BILINGUAL_MATH_REVIEW.md"
LEDGER_REL = "provenance/SOURCE_CORRECTIONS_CH17.json"
TERM_PLAN_REL = "provenance/CH17_TERMINOLOGY_PLAN.md"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-17.pdf"
RECEIPT_REL = "provenance/CH17_BUILD_AND_QA_RECEIPT.md"
BUILD_RESULT_REL = "qa/CH17_FINAL_BUILD_RESULT.json"
RENDER_MANIFEST_REL = "provenance/CH17_RENDER_MANIFEST.csv"
RENDER_AUDIT_REL = "qa/CH17_RENDER_AUDIT.json"
ACCESSIBILITY_AUDIT_REL = "qa/CH17_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
AGGREGATE_CORRECTIONS_REL = "provenance/SOURCE_CORRECTIONS.md"
PREFIX_LOCK_REL = "backend/CH17_PREFIX_LOCKS.json"

SOURCE_PATH = ROOT / SOURCE_REL
TARGET_PATH = ROOT / TARGET_REL

# (bytes, logical records, SHA-256)
EXPECTED_SOURCE = (59_639, 1_362, "e8ebcaa4e5dbc1cc9b907edb235465610f3bd61e0bfa1ce2f1b5b26e9abf8c6a")
EXPECTED_TARGET = (61_673, 1_362, "061ffd28907e2251fc8b01077888de3e11b3bce67fec1ba52b080c924a241059")
EXPECTED_MASTER = (10_820, 346, "51b3f4d790e3d09ac6ac4c160284510e4827140ecaa5a961a46c880ae5c8bb39")
EXPECTED_INVENTORY = (13_441, 258, "96bd447b7629b428f51382a74bed5eb93425cb90b8d3ad1c371f202996f27e2f")
EXPECTED_PRE_REVIEW = (17_583, 314, "696b3610fc0799811492b77fe57affcb743aff38596a9fc6f8da39131d10a305")
EXPECTED_REPORT = (15_667, 738, "1948b0b3298e70c3fd87df0075b32d6f5db439a44cdc4d1add89096af877697d")
EXPECTED_BILINGUAL = (5_296, 104, "53fe4a4165cc3352fa7e29e5ff6f44e69e622d6bdd8dd85b6953ae38f4d3be21")
EXPECTED_LEDGER = (53_256, 833, "a2b84cfb272a22669920ee0ef4fd015929b353be651cc80700e370c91329257d")
EXPECTED_TERM_PLAN = (15_048, 254, "e57fe4efe837403e3f9fa130297403d48a9f9c7788647f671ef2d2dcf456b299")

JSONL_FILES = prior.JSONL_FILES
INITIAL_LOCKS = {
    "units.jsonl": (23_583, "d392ae51bc2722b9fafb6f4ade28e6f86c57e1b2810d12f4f028c68f7cbda9c3"),
    "semantic_units.jsonl": (1_431_899, "403fc20586c45019f0693ece4beaa627e1b50f7447f6ea7a6dc8ed529f910319"),
    "segments.jsonl": (1_598_607, "b38a228ded09e12a34e48c945a546e2bb592c9c3bcac81e9faf0676c0bfee93e"),
    "relations.jsonl": (2_059_296, "f4f32cd06df7e97db82a29f8b76887ea9bcb3a2954541bb477280ea2f0cfd69b"),
    "formula_map.jsonl": (6_670_181, "ae729d8948fbfc2aa8894633d71f1b2dc1ce95e021fd714f2a5be257e3695588"),
    "exercise_support.jsonl": (27_135, "da1bd2f951ec0982cefce076ea5bd64a69c14613102ce1d7e17ed056a1763ffc"),
    "index_terms.csv": (499_785, "691ed53a07998aaea922f3f2d61d316eb5178d065c165d233481fc26d3ef1847"),
    "artifacts.jsonl": (92_146, "463aa01410e11d1d1508a0614ca9427d8f09a6697c3767c3a0aaedb485b61862"),
    "qa_events.jsonl": (113_597, "fbcdad8ec4567dd478704c8979a03fb9585d25aefb62a3d6a54c21299c344032"),
    "corrections.jsonl": (233_724, "420b1fda2575e259db4f94b866e27a5bb781cc782dc4cb7920497a037585b516"),
    "terminology.jsonl": (163_798, "bea26b0446b3709d8748dc043e7ec6aa17eda6d0df5cec3157f8003242f42683"),
}

QUEUED_CH17 = {
    "schema": SCHEMA, "schema_version": VERSION, "record_type": "unit",
    "id": CHAPTER_ID, "edition_id": EDITION, "order": 17,
    "source_path": "K0_functor.tex", "source_bytes": EXPECTED_SOURCE[0],
    "source_lines": EXPECTED_SOURCE[1], "source_sha256": EXPECTED_SOURCE[2],
    "source_title": "THE K0-FUNCTOR", "course_role": "advanced_continuation",
    "translation_state": "queued", "rights_id": RIGHTS,
}

SOURCE_TERMS = [
    "similar", "unitarily equivalent", "Murray-von Neumann equivalent", "isometry",
    "Grothendieck group", "Grothendieck map", "cancellation property", "stably equivalent",
    "point-norm topology", "homotopic", "homotopically equivalent", "contractible",
    "contractible", "scalar mapping", "scalar element", "split exact", "half exact",
    "inductive sequence", "inductive limit", "direct limit",
    "approximately finite dimensional $C^*$-algebra", "multiplicity", "Bratteli diagram",
    "Fibonacci algebra",
]
TARGET_TERMS = [
    "serupa", "ekuivalen secara uniter", "ekuivalen Murray--von Neumann", "isometri",
    "grup Grothendieck", "pemetaan Grothendieck", "sifat pembatalan", "ekuivalen secara stabil",
    "topologi norma-titik", "homotop", "ekuivalen secara homotopi", "kontraktibel",
    "kontraktibel", "pemetaan skalar", "elemen skalar", "eksak terbelah", "eksak separuh",
    "barisan induktif", "limit induktif", "limit langsung",
    "aljabar-$C^*$ berdimensi hingga secara aproksimatif", "multiplisitas", "diagram Bratteli",
    "aljabar Fibonacci",
]
TERM_MAPPING = [
    "TERM-SIMILAR", "TERM-UNITARILY-EQUIVALENT", "TERM-MURRAY-VON-NEUMANN-EQUIVALENT",
    "TERM-ISOMETRY", "TERM-GROTHENDIECK-GROUP", "TERM-GROTHENDIECK-MAP",
    "TERM-CANCELLATION-PROPERTY", "TERM-STABLY-EQUIVALENT", "TERM-POINT-NORM-TOPOLOGY",
    "TERM-HOMOTOPIC", "TERM-HOMOTOPICALLY-EQUIVALENT-ALGEBRAS", "TERM-CONTRACTIBLE",
    "TERM-CONTRACTIBLE", "TERM-SCALAR-MAPPING", "TERM-SCALAR-ELEMENT", "TERM-SPLIT-EXACT",
    "TERM-HALF-EXACT", "TERM-INDUCTIVE-SEQUENCE", "TERM-INDUCTIVE-LIMIT", "TERM-DIRECT-LIMIT",
    "TERM-APPROXIMATELY-FINITE-DIMENSIONAL-CSTAR-ALGEBRA", "TERM-MULTIPLICITY",
    "TERM-BRATTELI-DIAGRAM", "TERM-FIBONACCI-ALGEBRA",
]
NEW_TERM_SPECS = {
    "TERM-MURRAY-VON-NEUMANN-EQUIVALENT": ("Murray-von Neumann equivalent", "ekuivalen Murray--von Neumann", ["ekuivalen dalam pengertian Murray--von Neumann"], []),
    "TERM-ISOMETRY": ("isometry", "isometri", [], []),
    "TERM-GROTHENDIECK-GROUP": ("Grothendieck group", "grup Grothendieck", [], []),
    "TERM-GROTHENDIECK-MAP": ("Grothendieck map", "pemetaan Grothendieck", [], []),
    "TERM-CANCELLATION-PROPERTY": ("cancellation property", "sifat pembatalan", [], []),
    "TERM-STABLY-EQUIVALENT": ("stably equivalent", "ekuivalen secara stabil", ["ekuivalensi stabil"], []),
    "TERM-POINT-NORM-TOPOLOGY": ("point-norm topology", "topologi norma-titik", [], []),
    "TERM-HOMOTOPICALLY-EQUIVALENT-ALGEBRAS": ("homotopically equivalent", "ekuivalen secara homotopi", [], []),
    "TERM-CONTRACTIBLE": ("contractible", "kontraktibel", [], []),
    "TERM-SCALAR-MAPPING": ("scalar mapping", "pemetaan skalar", [], []),
    "TERM-SCALAR-ELEMENT": ("scalar element", "elemen skalar", [], []),
    "TERM-HALF-EXACT": ("half exact", "eksak separuh", ["setengah eksak"], []),
    "TERM-INDUCTIVE-SEQUENCE": ("inductive sequence", "barisan induktif", [], []),
    "TERM-APPROXIMATELY-FINITE-DIMENSIONAL-CSTAR-ALGEBRA": ("approximately finite dimensional $C^*$-algebra", "aljabar-$C^*$ berdimensi hingga secara aproksimatif", ["aljabar-AF"], []),
    "TERM-MULTIPLICITY": ("multiplicity", "multiplisitas", [], []),
    "TERM-BRATTELI-DIAGRAM": ("Bratteli diagram", "diagram Bratteli", [], []),
    "TERM-FIBONACCI-ALGEBRA": ("Fibonacci algebra", "aljabar Fibonacci", [], []),
}

EXPECTED_OPCODE_SHA256 = "5f6c8bc1b303a655f4ec1728aed39df881392df4282cc2c55366d707403d1e90"


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


def strip_ch17(records: dict[str, list[dict[str, Any]]], index_rows: list[dict[str, str]]) -> None:
    for name, values in records.items():
        if name == "units.jsonl":
            values[:] = [QUEUED_CH17.copy() if item.get("id") == CHAPTER_ID else item for item in values]
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
        "schema_version": "o008.ch17-prefix-locks.v1", "unit_id": CHAPTER_ID,
        "scope": "complete admitted Chapters 1--16 backend; excludes every Chapter 17-derived record",
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
    strip_ch17(records, index_rows)
    base.assert_unit_order(records["units.jsonl"])
    payload, locks = prefix_payload(records, fields, index_rows)
    for name, expected in INITIAL_LOCKS.items():
        if (len(payload[name]), sha(payload[name])) != expected:
            raise RuntimeError(f"Chapter 1--16 prefix identity differs: {name}")
    lock_bytes = (json.dumps(locks, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    lock_path = ROOT / PREFIX_LOCK_REL
    if not was_initial and (not lock_path.is_file() or lock_path.read_bytes() != lock_bytes):
        raise RuntimeError("backend is neither exact Chapter 16 state nor locked Chapter 17 state")
    return records, fields, index_rows, lock_bytes, was_initial


def ledger_records() -> tuple[list[dict[str, Any]], str]:
    path = ROOT / LEDGER_REL
    document = json.loads(path.read_text(encoding="utf-8"))
    values = document.get("records")
    expected_ids = [f"{CHAPTER_ID}-CORR-{number:03d}" for number in range(1, 27)]
    if (
        document.get("schema_version") != "o008.source-corrections.v1"
        or document.get("unit_id") != CHAPTER_ID
        or document.get("status") != "adjudicated_and_applied"
        or not isinstance(values, list)
        or [item.get("id") for item in values] != expected_ids
    ):
        raise RuntimeError("Chapter 17 correction ledger closure differs")
    target = document.get("target", {})
    if target.get("sha256") != EXPECTED_TARGET[2] or target.get("bytes") != EXPECTED_TARGET[0]:
        raise RuntimeError("Chapter 17 correction ledger is not bound to the final target")
    return values, sha(path.read_bytes())


def aggregate_corrections_available() -> bool:
    path = ROOT / AGGREGATE_CORRECTIONS_REL
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return "## Chapter 17" in text and "SOURCE_CORRECTIONS_CH17.json" in text


def core_evidence() -> dict[str, dict[str, Any]]:
    return {
        "source": identity(SOURCE_PATH, EXPECTED_SOURCE),
        "target": identity(TARGET_PATH, EXPECTED_TARGET),
        "master": identity(ROOT / MASTER_REL, EXPECTED_MASTER),
        "inventory": identity(ROOT / INVENTORY_REL, EXPECTED_INVENTORY),
        "pre_review": identity(ROOT / PRE_REVIEW_REL, EXPECTED_PRE_REVIEW),
        "report": identity(ROOT / REPORT_REL, EXPECTED_REPORT),
        "bilingual_review": identity(ROOT / BILINGUAL_REVIEW_REL, EXPECTED_BILINGUAL),
        "ledger": identity(ROOT / LEDGER_REL, EXPECTED_LEDGER),
        "term_plan": identity(ROOT / TERM_PLAN_REL, EXPECTED_TERM_PLAN),
    }


def final_available() -> bool:
    return aggregate_corrections_available() and all((ROOT / path).is_file() for path in (
        PDF_REL, RECEIPT_REL, BUILD_RESULT_REL, RENDER_MANIFEST_REL, RENDER_AUDIT_REL,
        ACCESSIBILITY_AUDIT_REL,
    ))


def final_evidence(ids: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if not final_available():
        raise RuntimeError("final Chapter 17 artifact set or aggregate correction entry is incomplete")
    for key, path in (
        ("pdf", PDF_REL), ("receipt", RECEIPT_REL), ("build_result", BUILD_RESULT_REL),
        ("render_manifest", RENDER_MANIFEST_REL), ("render_audit", RENDER_AUDIT_REL),
        ("accessibility", ACCESSIBILITY_AUDIT_REL), ("aggregate_corrections", AGGREGATE_CORRECTIONS_REL),
    ):
        ids[key] = identity(ROOT / path)
    ids["pdf"]["pages"] = page_count(ROOT / PDF_REL)
    receipt = (ROOT / RECEIPT_REL).read_text(encoding="utf-8")
    if CHAPTER_ID not in receipt or not re.search(r"\badmitted\b", receipt, re.I):
        raise RuntimeError("Chapter 17 receipt does not assert admission")
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
        "source_records": 1362, "target_records": 1362, "sections": 8, "labels": 73,
        "references": 47, "citations": 12, "index_terms": 100, "defined_terms": 24,
        "source_math_surfaces": 1047, "target_math_surfaces": 1048, "corrections": 26,
    }
    if checks != expected:
        raise RuntimeError(f"Chapter 17 preflight closure differs: {checks}")
    return {
        "status": "pass", "unit_id": CHAPTER_ID,
        "backend_prefix_state": "exact_chapter16" if was_initial else "stripped_locked_chapter17",
        "prefix_lock_sha256": sha(lock_bytes), "identities": ids,
        "structural_closure": checks, "final_artifacts_available": final_available(),
        "aggregate_corrections_has_ch17": aggregate_corrections_available(), "writes_performed": False,
    }


def terminology_records(source: str, target: str, prior_terms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if [x["argument"] for x in common.macro(source, "df")] != SOURCE_TERMS:
        raise RuntimeError("Chapter 17 source defined-term sequence differs")
    if [x["argument"] for x in common.macro(target, "df")] != TARGET_TERMS:
        raise RuntimeError("Chapter 17 target defined-term sequence differs")
    prior_ids = {item["id"] for item in prior_terms}
    inherited = set(TERM_MAPPING) - set(NEW_TERM_SPECS)
    if not inherited.issubset(prior_ids) or set(NEW_TERM_SPECS) & prior_ids:
        raise RuntimeError("Chapter 17 inherited/new terminology boundary differs")
    output = []
    for stable_id, (source_term, preferred, variants, rejected) in NEW_TERM_SPECS.items():
        output.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "term", "id": stable_id,
            "source_term": source_term, "locale": "id-ID", "preferred": preferred,
            "variants": variants, "rejected": rejected,
            "scope": "K-theory, projection equivalence, Grothendieck groups, inductive limits, and Bratteli diagrams",
            "evidence": f"{CHAPTER_ID} target; {TERM_PLAN_REL}", "introduced_in_unit": CHAPTER_ID,
        })
    return output


def correction_records(items: list[dict[str, Any]], ledger_sha: str, bound: bool) -> list[dict[str, Any]]:
    output = []
    for item in items:
        source_lines = item["source_lines"]
        target_lines = item["target_lines"]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "correction",
            "id": item["id"], "unit_id": CHAPTER_ID,
            "source_locator": f"K0_functor.tex:{source_lines['start']}--{source_lines['end']}",
            "target_locator": f"K0_functor-id.tex:{target_lines['start']}--{target_lines['end']}",
            "correction_type": str(item.get("classification", "source_correction")).lower(),
            "decision": item.get("decision", ""), "affects_math": bool(item.get("affects_math", False)),
            "target_disposition": "corrected", "ledger_path": LEDGER_REL,
            "ledger_sha256": ledger_sha, "qa_state": "passed",
            "admission_state": "admitted" if bound else "pending_final_artifact_binding",
            "upstream_report": "deferred_until_complete_and_separately_authorized",
            "receipt_document_state": "present" if bound else "pending", "receipt_path": RECEIPT_REL,
        }
        for key in (
            "source_normalized_snippet_sha256", "target_normalized_snippet_sha256",
            "source_required_anchors", "required_target_anchors", "forbidden_target_anchors",
            "target_marker", "target_marker_line",
        ):
            if key in item:
                record[key] = item[key]
        output.append(record)
    return output


def formula_records(source: str, target: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (1047, 1048):
        raise RuntimeError("Chapter 17 math closure changed")
    source_keys = [ch03_math.math_key(item["normalized"]) for item in source_math]
    target_keys = [ch03_math.math_key(item["normalized"]) for item in target_math]
    opcodes = SequenceMatcher(None, source_keys, target_keys, autojunk=False).get_opcodes()
    opcode_bytes = json.dumps(opcodes, separators=(",", ":")).encode("utf-8")
    if sha(opcode_bytes) != EXPECTED_OPCODE_SHA256:
        raise RuntimeError(f"Chapter 17 math opcode closure changed: {opcodes}")

    mapping: list[list[int] | None] = [None] * len(target_math)
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            for source_index, target_index in zip(range(i1, i2), range(j1, j2), strict=True):
                mapping[target_index] = [source_index]
    manual = {
        107: [107], 157: [157], 188: [188], 306: [306], 382: [383], 583: [583],
        665: [], 666: [], 698: [697], 728: [727], 765: [765], 766: [766],
        791: [791], 872: [872], 899: [], 903: [902], 911: [], 913: [],
        927: [924], 976: [973], 1006: [1005],
    }
    for target_index, source_group in manual.items():
        mapping[target_index] = source_group
    if any(group is None for group in mapping):
        raise RuntimeError("Chapter 17 formula mapping is incomplete")
    source_coverage = [index for group in mapping for index in (group or [])]
    deleted_groups = [
        ([591], f"{CHAPTER_ID}-CORR-012", "classified_source_correction"),
        ([741], f"{CHAPTER_ID}-CORR-014", "classified_source_correction"),
        ([980, 981], None, "localized_source_deletion"),
    ]
    complete_coverage = source_coverage + [index for group, _, _ in deleted_groups for index in group]
    if sorted(complete_coverage) != list(range(1047)) or len(complete_coverage) != len(set(complete_coverage)):
        raise RuntimeError("Chapter 17 source formula coverage is not exact-once")

    correction_by_target = {
        108: f"{CHAPTER_ID}-CORR-005", 158: f"{CHAPTER_ID}-CORR-024",
        189: f"{CHAPTER_ID}-CORR-025", 383: f"{CHAPTER_ID}-CORR-006",
        584: f"{CHAPTER_ID}-CORR-026", 699: f"{CHAPTER_ID}-CORR-013",
        729: f"{CHAPTER_ID}-CORR-014", 766: f"{CHAPTER_ID}-CORR-014",
        767: f"{CHAPTER_ID}-CORR-014", 792: f"{CHAPTER_ID}-CORR-017",
        873: f"{CHAPTER_ID}-CORR-019", 900: f"{CHAPTER_ID}-CORR-021",
        904: f"{CHAPTER_ID}-CORR-021", 912: f"{CHAPTER_ID}-CORR-021",
        914: f"{CHAPTER_ID}-CORR-021", 1007: f"{CHAPTER_ID}-CORR-023",
    }
    localized_replacements = {307, 928, 977}
    localized_insertions = {666, 667}
    mathkey_localized = {217, 266, 322, 337, 421, 541, 926, 1038}
    records = []
    counters: collections.Counter[str] = collections.Counter()
    for target_index, source_group_value in enumerate(mapping):
        source_group = source_group_value or []
        ordinal = target_index + 1
        target_item = target_math[target_index]
        source_items = [source_math[index] for index in source_group]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{ordinal:04d}",
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{index + 1:04d}" for index in source_group],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{ordinal:04d}"],
            "source_lines": [[item["line_start"], item["line_end"]] for item in source_items],
            "target_lines": [[target_item["line_start"], target_item["line_end"]]],
            "source_sha256": [item["sha256"] for item in source_items],
            "target_sha256": [target_item["sha256"]],
            "source_delimiters": [item["delimiter"] for item in source_items],
            "delimiter": target_item["delimiter"],
            "ordinal_alignment": "target_insertion" if not source_group else "mapped",
        }
        correction_id = correction_by_target.get(ordinal)
        exact = len(source_group) == 1 and source_items[0]["normalized"] == target_item["normalized"]
        key_equal = len(source_group) == 1 and source_keys[source_group[0]] == target_keys[target_index]
        if ordinal == 383:
            record.update(
                alignment="preserved_exact_relocated_by_classified_source_correction",
                sequence_opcode="move", delta_class="classified_source_correction",
                correction_id=correction_id, correction_disposition="corrected", qa_state="passed",
            )
            counters["correction_relocations"] += 1
        elif exact:
            record["alignment"] = "preserved_exact_after_text_aware_whitespace_normalization"
            counters["exact"] += 1
        elif ordinal in mathkey_localized and key_equal:
            record.update(
                alignment="localized_math_text_preserved_math_key", sequence_opcode="replace",
                delta_class="localized_prose_translation", qa_state="passed",
            )
            counters["mathkey_localized"] += 1
        elif ordinal in localized_replacements:
            record.update(
                alignment="reviewed_localized_notation_replacement", sequence_opcode="replace",
                delta_class="localized_notation_normalization", qa_state="passed",
            )
            counters["localized_replacements"] += 1
        elif ordinal in localized_insertions and not source_group:
            record.update(
                alignment="reviewed_localized_explicit_object_insertion", sequence_opcode="insert",
                delta_class="localized_target_insertion", qa_state="passed",
            )
            counters["localized_insertions"] += 1
        elif correction_id:
            comment_only = ordinal == 1007
            record.update(
                alignment=("reviewed_correction_marker_comment_preserving_TeX_math" if comment_only
                           else "reviewed_source_correction_insertion" if not source_group
                           else "reviewed_source_correction_replacement"),
                sequence_opcode="insert" if not source_group else "replace",
                delta_class=("classified_source_correction_comment_only" if comment_only
                             else "classified_source_correction"),
                correction_id=correction_id, correction_disposition="corrected", qa_state="passed",
            )
            counters["correction_comment_only" if comment_only else
                     "correction_insertions" if not source_group else "correction_replacements"] += 1
        else:
            raise RuntimeError(f"unclassified Chapter 17 formula delta: target {ordinal}")
        records.append(record)

    for number, (source_group, correction_id, delta_class) in enumerate(deleted_groups, 1):
        source_items = [source_math[index] for index in source_group]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-SOURCE-DELETION-{number:04d}",
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{index + 1:04d}" for index in source_group],
            "target_formula_ids": [],
            "source_lines": [[item["line_start"], item["line_end"]] for item in source_items],
            "target_lines": [], "source_sha256": [item["sha256"] for item in source_items],
            "target_sha256": [], "source_delimiters": [item["delimiter"] for item in source_items],
            "delimiter": None, "ordinal_alignment": "source_deletion", "sequence_opcode": "delete",
            "delta_class": delta_class, "qa_state": "passed",
        }
        if correction_id:
            record.update(
                alignment="reviewed_source_correction_deletion", correction_id=correction_id,
                correction_disposition="corrected",
            )
            counters["correction_deletions"] += 1
        else:
            record["alignment"] = "reviewed_localized_compound_source_deletion"
            counters["localized_source_deletions"] += 1
        records.append(record)

    expected_counters = collections.Counter({
        "exact": 1019, "mathkey_localized": 8, "correction_replacements": 11,
        "localized_replacements": 3, "correction_comment_only": 1,
        "correction_insertions": 3, "localized_insertions": 2,
        "correction_relocations": 1, "correction_deletions": 2,
        "localized_source_deletions": 1,
    })
    if counters != expected_counters or len(records) != 1051:
        raise RuntimeError(f"Chapter 17 formula classification differs: {counters}/{len(records)}")
    return records, {
        "source_math_surfaces": 1047, "target_math_surfaces": 1048,
        "formula_map_records": 1051, **dict(expected_counters),
    }


def exercise_support_record(exercise_unit_id: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "exercise_support",
        "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-001", "exercise_unit_id": exercise_unit_id,
        "source_exercise_order": 1, "upstream_hint_ids": [],
        "upstream_inline_hint_state": "absent", "upstream_answer_state": "absent",
        "upstream_solution_state": "absent",
        "original_solution_id": f"O001-{CHAPTER_ID}-EX-001-SOLUTION",
        "original_solution_state": "queued_in_O001",
        "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0",
        "provenance": "separately_authored_not_Erdman",
    }


def artifact_records(ids: dict[str, dict[str, Any]], bound: bool) -> list[dict[str, Any]]:
    present_specs = [
        ("ARTIFACT-FAOA-ID-CH17-TARGET-TEX", "translation_source", TARGET_REL),
        ("ARTIFACT-FAOA-ID-THROUGH-CH17-MASTER", "cumulative_TeX_master", MASTER_REL),
        ("ARTIFACT-FAOA-ID-CH17-SOURCE-INVENTORY", "source_inventory", INVENTORY_REL),
        ("ARTIFACT-FAOA-ID-CH17-PRETRANSLATION-REVIEW", "pretranslation_mathematical_review", PRE_REVIEW_REL),
        ("ARTIFACT-FAOA-ID-CH17-TERM-PLAN", "terminology_plan", TERM_PLAN_REL),
        ("ARTIFACT-FAOA-ID-CH17-CORRECTIONS-LEDGER", "chapter_source_corrections_ledger", LEDGER_REL),
        ("ARTIFACT-FAOA-ID-CH17-TRANSLATION-REPORT", "translation_QA_report", REPORT_REL),
        ("ARTIFACT-FAOA-ID-CH17-BILINGUAL-REVIEW", "bilingual_mathematical_review", BILINGUAL_REVIEW_REL),
    ]
    final_specs = [
        ("ARTIFACT-FAOA-ID-SOURCE-CORRECTIONS-AGGREGATE-CH17", "aggregate_source_corrections_log", AGGREGATE_CORRECTIONS_REL),
        ("ARTIFACT-FAOA-ID-THROUGH-CH17-PDF", "canonical_cumulative_reader_pdf", PDF_REL),
        ("ARTIFACT-FAOA-ID-CH17-FINAL-BUILD-RESULT", "deterministic_build_result", BUILD_RESULT_REL),
        ("ARTIFACT-FAOA-ID-CH17-RENDER-MANIFEST", "visual_QA_render_manifest", RENDER_MANIFEST_REL),
        ("ARTIFACT-FAOA-ID-CH17-RENDER-AUDIT", "visual_QA_audit", RENDER_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH17-ACCESSIBILITY-AUDIT", "visual_accessibility_audit", ACCESSIBILITY_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH17-QA-RECEIPT", "admission_receipt", RECEIPT_REL),
    ]
    output = []
    for stable_id, kind, path in present_specs:
        info = identity(ROOT / path)
        output.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "artifact",
            "id": stable_id, "unit_id": CHAPTER_ID, "artifact_kind": kind, "path": path,
            "bytes": info["bytes"], "lines": info["lines"], "sha256": info["sha256"],
            "binding_state": "bound", "admission_state": "admitted" if bound else "pending_final_artifact_binding",
        })
    for stable_id, kind, path in final_specs:
        present = bound
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
        elif kind == "aggregate_source_corrections_log":
            record["binding_note"] = "Chapter 17 aggregate entry not yet present"
        output.append(record)
    if len(output) != 15:
        raise RuntimeError("Chapter 17 artifact closure differs")
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
            "id": f"QA-CH17-{label}-20260824", "unit_id": CHAPTER_ID,
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
        sections=8, environment_begins=206, semantic_environment_begins=149,
        labels=73, references=47, citations=12, index_terms=100, defined_terms=24,
        examples=31, exercise_environments=1, proof_environments=22, proof_hints=16,
    )
    output[1].update(formula_summary | {"unexplained_deltas": 0, "extractor": "backend/ch03_math.py"})
    output[2].update(defined_term_occurrences=24, new_controlled_terms=len(NEW_TERM_SPECS))
    output[3].update(
        source_exercises=1, upstream_exercise_hints=0, upstream_answers=0, upstream_solutions=0,
        exercise_support_records=1, provenance="original_solution_queued_in_O001_not_Erdman",
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
    record = QUEUED_CH17 | {
        "target_path": TARGET_REL, "target_bytes": EXPECTED_TARGET[0], "target_lines": EXPECTED_TARGET[1],
        "target_sha256": EXPECTED_TARGET[2], "target_title": "FUNKTOR K0",
        "translation_state": "admitted" if bound else "qa_passed_pending_artifact_binding",
        "qa_state": "passed", "source_corrections": 26,
        "build_master_path": MASTER_REL, "build_master_bytes": EXPECTED_MASTER[0],
        "build_master_lines": EXPECTED_MASTER[1], "build_master_sha256": EXPECTED_MASTER[2],
        "artifact_path": PDF_REL,
        "artifact_state": "canonical_output_copy_present_and_frozen" if bound else "pending_final_artifact_binding",
        "publication_state": "pending", "admission_state": "admitted" if bound else "pending_final_artifact_binding",
        "receipt_path": RECEIPT_REL, "model_provenance": MODEL_ID,
    }
    if bound:
        record.update(
            artifact_bytes=ids["pdf"]["bytes"], artifact_pages=ids["pdf"]["pages"],
            artifact_sha256=ids["pdf"]["sha256"], qa_receipt_id="QA-CH17-ADMISSION-20260824",
            receipt_sha256=ids["receipt"]["sha256"],
        )
    return record


def build_outputs(bind_final: bool) -> tuple[dict[str, bytes], dict[str, Any]]:
    records, index_fields, index_rows, lock_bytes, _ = stripped_prefix()
    ids = core_evidence()
    ledger, ledger_sha = ledger_records()
    if bind_final:
        ids = final_evidence(ids)
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    semantic, segments, relations, source_anchors, _ = base.build_units_and_segments(source, target)
    kinds = collections.Counter(item["unit_kind"] for item in semantic)
    expected_kinds = collections.Counter({
        "section": 8, "defn": 22, "prop": 63, "proof": 22, "exam": 31,
        "notn": 7, "exer": 1, "cor": 2,
    })
    if len(semantic) != 156 or kinds != expected_kinds or len(segments) != 185 or len(relations) != 525:
        raise RuntimeError(f"Chapter 17 semantic closure differs: {len(semantic)}/{kinds}/{len(segments)}/{len(relations)}")
    if bind_final:
        for item in semantic + segments:
            item["translation_state"] = "admitted"
            item["admission_state"] = "admitted"

    offsets: list[tuple[int, int, str]] = []
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
        if anchor["anchor_type"] != "chapter":
            offsets.append((anchor["start"], anchor["end"], stable_id))
    if len(source_anchors) != 157 or (section_number, node_number) != (8, 148):
        raise RuntimeError("Chapter 17 anchor closure differs")

    prior_labels = {
        item.get("source_local_id"): item["id"]
        for item in records["semantic_units.jsonl"] if item.get("source_local_id")
    }
    for relation in records["relations.jsonl"]:
        if relation.get("relation_type") == "declares_label" and relation.get("source_local_id"):
            prior_labels[relation["source_local_id"]] = relation["to_id"]
    local_labels: dict[str, str] = {}
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if [x["argument"] for x in source_labels] != [x["argument"] for x in target_labels] or len(source_labels) != 73:
        raise RuntimeError("Chapter 17 label sequence differs")
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
    if [(kind, label) for _, kind, label in source_refs] != [(kind, label) for _, kind, label in target_refs] or len(source_refs) != 47:
        raise RuntimeError("Chapter 17 reference sequence differs")
    resolution_counts: collections.Counter[str] = collections.Counter()
    for number, (source_ref, target_ref) in enumerate(zip(source_refs, target_refs, strict=True), 1):
        source_position, source_kind, source_label = source_ref
        _, target_kind, target_label = target_ref
        if target_label in local_labels:
            endpoint, resolution = local_labels[target_label], "local"
        elif target_label in prior_labels:
            endpoint, resolution = prior_labels[target_label], "admitted_prior_unit"
        else:
            raise RuntimeError(f"unresolved Chapter 17 reference: {target_label}")
        resolution_counts[resolution] += 1
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}", "relation_type": "xref",
            "from_id": base.ch01.containing_segment(segments, source_position, "source"), "to_id": endpoint,
            "source_local_id": source_label, "target_local_id": target_label, "resolution": resolution,
            "source_surface": source_kind, "target_surface": target_kind,
        })
    if resolution_counts != collections.Counter({"local": 28, "admitted_prior_unit": 19}):
        raise RuntimeError(f"Chapter 17 reference-resolution closure differs: {resolution_counts}")

    source_cites = common.macro(source, "cite")
    target_cites = common.macro(target, "cite")
    if [x["argument"] for x in source_cites] != [x["argument"] for x in target_cites] or len(source_cites) != 12:
        raise RuntimeError("Chapter 17 citation sequence differs")
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
    if len(source_indexes) != 100 or len(target_indexes) != 100:
        raise RuntimeError("Chapter 17 index count differs")
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
    exercises = [item for item in semantic if item["unit_kind"] == "exer"]
    if len(exercises) != 1:
        raise RuntimeError("Chapter 17 exercise semantic closure differs")
    support = exercise_support_record(exercises[0]["id"])
    common_relation = {"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "from_id": CHAPTER_ID}
    relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS})
    for number, artifact in enumerate(artifacts, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}", "relation_type": "has_artifact", "to_id": artifact["id"]})
    for number, event in enumerate(qa, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-QA-{number:04d}", "relation_type": "has_qa_event", "to_id": event["id"]})
    for number, correction in enumerate(corrections, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}", "relation_type": "documents_correction", "to_id": correction["id"]})
    relations.append({
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
        "id": f"{CHAPTER_ID}-REL-EXERCISE-SUPPORT-0001", "relation_type": "has_exercise_support",
        "from_id": exercises[0]["id"], "to_id": support["id"],
    })
    if len(relations) != 734:
        raise RuntimeError(f"Chapter 17 relation closure differs: {len(relations)}")

    for segment in segments:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            segment.pop(key, None)
    records["semantic_units.jsonl"].extend(semantic)
    records["segments.jsonl"].extend(segments)
    records["relations.jsonl"].extend(relations)
    records["formula_map.jsonl"].extend(formulas)
    records["exercise_support.jsonl"].append(support)
    records["artifacts.jsonl"].extend(artifacts)
    records["qa_events.jsonl"].extend(qa)
    records["corrections.jsonl"].extend(corrections)
    records["terminology.jsonl"].extend(new_terms)
    index_rows.extend(new_index_rows)
    records["units.jsonl"] = [chapter_unit(ids, bind_final) if item.get("id") == CHAPTER_ID else item for item in records["units.jsonl"]]

    outputs = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    outputs["index_terms.csv"] = csv_bytes(index_fields, index_rows)
    outputs["CH17_PREFIX_LOCKS.json"] = lock_bytes
    outputs["BACKEND_MANIFEST.csv"] = base.manifest_bytes(outputs)
    summary = {
        "unit": CHAPTER_ID, "binding_state": "bound" if bind_final else "pending_final_artifact_binding",
        "semantic_units": len(semantic), "segments": len(segments), "relations": len(relations),
        "formula_maps": len(formulas), "index_rows": len(new_index_rows), "new_terms": len(new_terms),
        "term_uses": len(TERM_MAPPING), "corrections": len(corrections), "exercise_support": 1,
        "qa_events": len(qa), "artifacts": len(artifacts),
        "reference_resolution": dict(resolution_counts), "target_sha256": EXPECTED_TARGET[2],
        "model_id": MODEL_ID, "formula_summary": formula_summary,
    }
    return outputs, summary


def reconciliation_report(summary: dict[str, Any], outputs: dict[str, bytes]) -> bytes:
    lines = [
        "# FAOA-2015-CH17 backend reconciliation", "",
        "The Chapter 17 append preserves the exact admitted Chapter 1--16 byte prefix and binds the complete K0-functor source/target topology.", "",
        f"- Target: `{TARGET_REL}` — {EXPECTED_TARGET[0]} bytes, SHA-256 `{EXPECTED_TARGET[2]}`.",
        f"- Semantic units: {summary['semantic_units']}; segments: {summary['segments']}; relations: {summary['relations']}.",
        f"- Formula maps: {summary['formula_maps']} covering 1,047 source and 1,048 target surfaces exactly once; index rows: {summary['index_rows']}.",
        f"- New terms: {summary['new_terms']}; term uses: {summary['term_uses']}; corrections: {summary['corrections']}; exercise-support records: 1.",
        "- `backend/CH17_PREFIX_LOCKS.json` locks the complete Chapter 1--16 prefix byte-for-byte.",
        "- `backend/validate_ch17_backend.py` checks stable-ID uniqueness, relation endpoints, formula/index closure, manifest identity, and deterministic replay.",
        f"- Binding state: `{summary['binding_state']}`; aggregate Chapter 17 correction entry and final admission artifacts remain required before bound admission." if summary["binding_state"] != "bound" else "- Binding state: `bound`.",
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
    current_unit = next(
        json.loads(line) for line in (BACKEND / "units.jsonl").read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("id") == CHAPTER_ID
    )
    bound = args.bind_final_artifacts or current_unit.get("admission_state") == "admitted"
    outputs, summary = build_outputs(bound)
    if args.check:
        mismatches = [
            name for name, data in outputs.items()
            if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != data
        ]
        if mismatches:
            raise RuntimeError("deterministic backend replay differs: " + ", ".join(mismatches))
        print(json.dumps(summary | {"deterministic_replay": "pass"}, ensure_ascii=False, sort_keys=True))
        return
    for name, data in outputs.items():
        (BACKEND / name).write_bytes(data)
    report = reconciliation_report(summary, outputs)
    (ROOT / "qa/CH17_BACKEND_RECONCILIATION.md").write_bytes(report)
    print(json.dumps(summary | {"backend_report": "qa/CH17_BACKEND_RECONCILIATION.md"}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
