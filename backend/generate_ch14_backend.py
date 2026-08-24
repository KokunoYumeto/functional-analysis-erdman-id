#!/usr/bin/env python3
"""Deterministically append the FAOA-2015-CH14 backend slice."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path[:0] = [str(BACKEND), str(ROOT / "qa")]
import ch03_math  # noqa: E402
import check_ch05_translation as common  # noqa: E402
import generate_ch12_backend as base  # noqa: E402


SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH14"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_REL = "source/upstream/multiplier_algebras.tex"
TARGET_REL = "source/id-ID/multiplier_algebras-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-through-ch14.tex"
INVENTORY_REL = "qa/CH14_SOURCE_INVENTORY.md"
PRE_REVIEW_REL = "qa/CH14_PRETRANSLATION_MATH_REVIEW.md"
REPORT_REL = "qa/ch14-translation-report.json"
BILINGUAL_REVIEW_REL = "qa/CH14_BILINGUAL_MATH_REVIEW.md"
LEDGER_REL = "provenance/SOURCE_CORRECTIONS_CH14.json"
TERM_PLAN_REL = "provenance/CH14_TERMINOLOGY_PLAN.md"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-14.pdf"
RECEIPT_REL = "provenance/CH14_BUILD_AND_QA_RECEIPT.md"
RENDER_MANIFEST_REL = "provenance/CH14_RENDER_MANIFEST.csv"
RENDER_AUDIT_REL = "qa/CH14_RENDER_AUDIT.json"
ACCESSIBILITY_AUDIT_REL = "qa/CH14_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
BUILD_RESULT_REL = "qa/CH14_FINAL_BUILD_RESULT.json"
PREFIX_LOCK_REL = "backend/CH14_PREFIX_LOCKS.json"

SOURCE_PATH = ROOT / SOURCE_REL
TARGET_PATH = ROOT / TARGET_REL

EXPECTED_SOURCE = (30_579, 687, "d9bf8cf31a6e18a779863dcb397863430fe2daac9031a86354ce2274b42def7c")
EXPECTED_TARGET = (31_900, 687, "2688ec9c2370371060aada680f5f95e9511ecb61cb99c2a126385f525a3c9142")
EXPECTED_MASTER = (10_443, 343, "f04180a796707c6cb0c5f74082a8b4c25721d20ff3ea9235819939b11e1e50c9")
EXPECTED_INVENTORY = (5_191, 120, "7d8d6592087684260db482829233eef71f53cbab65289079134f06b706a42835")
EXPECTED_PRE_REVIEW = (6_622, 127, "b56703971436cfb15123a0d9d4f82e5b5c189989c3c9a52747b6544af6898c30")
EXPECTED_TERM_PLAN = (6_151, 106, "60116f0b282504d12b2a9313364f16c2cbec0f4544b715188ab06455e1ed05cf")

JSONL_FILES = base.JSONL_FILES
INITIAL_LOCKS = {
    "units.jsonl": (20_511, "e5e2c5e17f5e297ea0ced767a7bc8c0defd2831d02271f0e722b842b37407ef3"),
    "semantic_units.jsonl": (1_216_332, "3ee1ee6d4b8d5a136b991c81ed76e1de9518aa9efd89c12b29809afcf6f5e37e"),
    "segments.jsonl": (1_356_584, "8761fec68fc4266e74fac1abb8cd882444cb442d7c92c3c205c6c1a13dc64a6f"),
    "relations.jsonl": (1_716_580, "b527d46df8b2faaa3cedae38c2712a72954b38e30d595924ad471bad17ccbc44"),
    "formula_map.jsonl": (5_697_297, "6b1f102eea28ffba0abee8abc2132aa323910aa40d46bc82c2bb330d8db051a1"),
    "exercise_support.jsonl": (26_047, "0c719db21027ee9c67b87b94c964a259bdac6f9c663356f9f2ee2704990af065"),
    "index_terms.csv": (440_765, "cff7a3b456bd7415eebf21d49a3f9598cc1d6ad165fb90985df11ef2a74f3063"),
    "artifacts.jsonl": (73_370, "e5e0e3da0ae637de776cf2eb70b63d2e6311d123de878d43495e053cc1cede2a"),
    "qa_events.jsonl": (93_966, "0e3039233cf8da4e1d1b2e8e4f3292b3571ee9b9e58eca549b85ceedd667cd34"),
    "corrections.jsonl": (192_865, "90601002223cf5879c21d9594df750788f3f70675cf539d71d743bc96febcd6b"),
    "terminology.jsonl": (142_221, "27ef79812d95b9432c7a1a054884e7281a1d7175bbb4a884b6dc8cdbe20ffcee"),
}

QUEUED_CH14 = {
    "schema": SCHEMA,
    "schema_version": VERSION,
    "record_type": "unit",
    "id": CHAPTER_ID,
    "edition_id": EDITION,
    "order": 14,
    "source_path": "multiplier_algebras.tex",
    "source_bytes": EXPECTED_SOURCE[0],
    "source_lines": EXPECTED_SOURCE[1],
    "source_sha256": EXPECTED_SOURCE[2],
    "source_title": "MULTIPLIER ALGEBRAS",
    "course_role": "advanced_continuation",
    "translation_state": "queued",
    "rights_id": RIGHTS,
}

EXPECTED_SOURCE_TERMS = [
    "$A$-module", "bilinear", "(complex) vector space", "algebra", "opposite algebra",
    "antihomomorphism", "anti-isomorphism", "$A$-module", "semi-inner product $A$-module",
    "inner product $A$-module", "pre-Hilbert $A$-module", "$A$-valued (semi-)inner product",
    "Hilbert $A$-module", "$A$-linear", "Hilbert $A$-module morphism", "adjointable",
    "adjoint", "principal ideal", "essential", "annihilator", "zero set", "unitization",
    "essential unitization", "compactification", "essential compactification", "embedded",
    "embedding", "unitization", "essential", "embedded", "embedding", "compactification",
    "essential", "maximal", "nondegenerate", "multiplier algebra",
]
EXPECTED_TARGET_TERMS = [
    "modul-$A$", "bilinear", "ruang vektor (kompleks)", "aljabar", "aljabar lawan",
    "antihomomorfisme", "antiisomorfisme", "modul-$A$", "modul-$A$ hasil kali dalam semu",
    "modul-$A$ hasil kali dalam", "modul pra-Hilbert-$A$", "hasil kali dalam (semu) bernilai-$A$",
    "modul Hilbert-$A$", "linear-$A$", "morfisme modul Hilbert-$A$", "dapat diadjoinkan",
    "adjoin", "ideal utama", "esensial", "anihilator", "himpunan nol", "unitalisasi",
    "unitalisasi esensial", "kompaktifikasi", "kompaktifikasi esensial", "dibenamkan",
    "pembenaman", "unitalisasi", "esensial", "dibenamkan", "pembenaman", "kompaktifikasi",
    "esensial", "maksimal", "tak terdegenerasi", "aljabar pengali",
]
TERM_OCCURRENCE_IDS = [
    "TERM-A-MODULE", "TERM-BILINEAR", "TERM-VECTOR-SPACE", "TERM-ALGEBRA",
    "TERM-OPPOSITE-ALGEBRA", "TERM-ANTIHOMOMORPHISM", "TERM-ANTI-ISOMORPHISM",
    "TERM-A-MODULE", "TERM-SEMI-INNER-PRODUCT-A-MODULE", "TERM-INNER-PRODUCT-A-MODULE",
    "TERM-PRE-HILBERT-A-MODULE", "TERM-A-VALUED-SEMI-INNER-PRODUCT",
    "TERM-HILBERT-A-MODULE", "TERM-A-LINEAR", "TERM-HILBERT-A-MODULE-MORPHISM",
    "TERM-ADJOINTABLE", "TERM-ADJOINT", "TERM-PRINCIPAL-IDEAL", "TERM-ESSENTIAL-IDEAL",
    "TERM-ANNIHILATOR", "TERM-ZERO-SET", "TERM-UNITIZATION", "TERM-ESSENTIAL-UNITIZATION",
    "TERM-COMPACTIFICATION", "TERM-ESSENTIAL-COMPACTIFICATION", "TERM-EMBEDDED",
    "TERM-EMBEDDING", "TERM-UNITIZATION", "TERM-ESSENTIAL-UNITIZATION", "TERM-EMBEDDED",
    "TERM-EMBEDDING", "TERM-COMPACTIFICATION", "TERM-ESSENTIAL-COMPACTIFICATION",
    "TERM-MAXIMAL", "TERM-NONDEGENERATE-REPRESENTATION", "TERM-MULTIPLIER-ALGEBRA",
]
NEW_TERM_SPECS = {
    "TERM-A-MODULE": ("$A$-module", "modul-$A$", [], []),
    "TERM-BILINEAR": ("bilinear", "bilinear", [], []),
    "TERM-ALGEBRA": ("algebra", "aljabar", [], []),
    "TERM-OPPOSITE-ALGEBRA": ("opposite algebra", "aljabar lawan", ["aljabar oposisi"], []),
    "TERM-ANTIHOMOMORPHISM": ("antihomomorphism", "antihomomorfisme", [], []),
    "TERM-SEMI-INNER-PRODUCT-A-MODULE": ("semi-inner product $A$-module", "modul-$A$ hasil kali dalam semu", [], []),
    "TERM-INNER-PRODUCT-A-MODULE": ("inner product $A$-module", "modul-$A$ hasil kali dalam", [], []),
    "TERM-PRE-HILBERT-A-MODULE": ("pre-Hilbert $A$-module", "modul pra-Hilbert-$A$", ["modul pre-Hilbert-$A$"], []),
    "TERM-A-VALUED-SEMI-INNER-PRODUCT": ("$A$-valued (semi-)inner product", "hasil kali dalam (semu) bernilai-$A$", [], []),
    "TERM-HILBERT-A-MODULE": ("Hilbert $A$-module", "modul Hilbert-$A$", [], []),
    "TERM-A-LINEAR": ("$A$-linear", "linear-$A$", [], []),
    "TERM-HILBERT-A-MODULE-MORPHISM": ("Hilbert $A$-module morphism", "morfisme modul Hilbert-$A$", [], []),
    "TERM-ADJOINTABLE": ("adjointable", "dapat diadjoinkan", [], []),
    "TERM-ESSENTIAL-IDEAL": ("essential ideal", "ideal esensial", [], []),
    "TERM-ZERO-SET": ("zero set", "himpunan nol", [], []),
    "TERM-ESSENTIAL-UNITIZATION": ("essential unitization", "unitalisasi esensial", [], []),
    "TERM-COMPACTIFICATION": ("compactification", "kompaktifikasi", [], ["pemadatan"]),
    "TERM-ESSENTIAL-COMPACTIFICATION": ("essential compactification", "kompaktifikasi esensial", [], []),
    "TERM-EMBEDDED": ("embedded", "dibenamkan", ["ditanamkan"], []),
    "TERM-EMBEDDING": ("embedding", "pembenaman", ["penanaman"], []),
    "TERM-MULTIPLIER-ALGEBRA": ("multiplier algebra", "aljabar pengali", ["aljabar multiplier"], []),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")


def csv_bytes(fieldnames: list[str], rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def identity(path: Path, expected: tuple[int, int, str] | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    value = {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "lines": len(data.splitlines()),
        "sha256": sha(data),
    }
    if expected and (value["bytes"], value["lines"], value["sha256"]) != expected:
        raise RuntimeError(f"identity mismatch: {value}")
    return value


def page_count(pdf: Path) -> int:
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(pdf)).pages)
    except Exception:
        return len(re.findall(rb"/Type\s*/Page(?:\s|/|>)", pdf.read_bytes()))


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


def strip_ch14(records: dict[str, list[dict[str, Any]]], index_rows: list[dict[str, str]]) -> None:
    for name, values in records.items():
        if name == "units.jsonl":
            values[:] = [QUEUED_CH14.copy() if item.get("id") == CHAPTER_ID else item for item in values]
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
    records: dict[str, list[dict[str, Any]]], fields: list[str], index_rows: list[dict[str, str]]
) -> tuple[dict[str, bytes], dict[str, Any]]:
    payload = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    payload["index_terms.csv"] = csv_bytes(fields, index_rows)
    locks = {
        "schema_version": "o008.ch14-prefix-locks.v1",
        "unit_id": CHAPTER_ID,
        "scope": "complete admitted Chapters 1--13 backend; excludes every Chapter 14-derived record",
        "files": {
            name: {
                "bytes": len(data),
                "sha256": sha(data),
                "records": len(records[name]) if name in records else len(index_rows),
            }
            for name, data in payload.items()
        },
    }
    return payload, locks


def stripped_prefix() -> tuple[
    dict[str, list[dict[str, Any]]], list[str], list[dict[str, str]], bytes, bool
]:
    configure_base()
    was_initial = initial_state()
    records, fields, index_rows = load_data()
    strip_ch14(records, index_rows)
    base.assert_unit_order(records["units.jsonl"])
    _, locks = prefix_payload(records, fields, index_rows)
    lock_bytes = (json.dumps(locks, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    lock_path = ROOT / PREFIX_LOCK_REL
    if not was_initial:
        if not lock_path.is_file() or lock_path.read_bytes() != lock_bytes:
            raise RuntimeError("backend is neither the exact Chapter 13 state nor a locked Chapter 14 state")
    return records, fields, index_rows, lock_bytes, was_initial


def target_sha(document: dict[str, Any]) -> str | None:
    values = [
        document.get("target_sha256"),
        document.get("identities", {}).get("target_sha256"),
        document.get("target", {}).get("sha256"),
        document.get("identities", {}).get("target", {}).get("sha256"),
    ]
    return next((value for value in values if isinstance(value, str)), None)


def ledger_records(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    records = ledger.get("records")
    if not isinstance(records, list) or len(records) < 2:
        raise RuntimeError("Chapter 14 correction ledger has no complete correction closure")
    if ledger.get("record_count", len(records)) != len(records):
        raise RuntimeError("Chapter 14 correction ledger count differs")
    ids = [item.get("id") for item in records]
    if any(not isinstance(item, str) or not item.startswith(CHAPTER_ID + "-CORR-") for item in ids):
        raise RuntimeError("Chapter 14 correction IDs differ")
    if len(ids) != len(set(ids)):
        raise RuntimeError("Chapter 14 correction IDs are not unique")
    return records


def evidence(bind_final: bool) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    ids = {
        "source": identity(SOURCE_PATH, EXPECTED_SOURCE),
        "target": identity(TARGET_PATH, EXPECTED_TARGET),
        "master": identity(ROOT / MASTER_REL, EXPECTED_MASTER),
        "inventory": identity(ROOT / INVENTORY_REL, EXPECTED_INVENTORY),
        "pre_review": identity(ROOT / PRE_REVIEW_REL, EXPECTED_PRE_REVIEW),
        "term_plan": identity(ROOT / TERM_PLAN_REL, EXPECTED_TERM_PLAN),
        "report": identity(ROOT / REPORT_REL),
        "bilingual_review": identity(ROOT / BILINGUAL_REVIEW_REL),
        "ledger": identity(ROOT / LEDGER_REL),
    }
    report = json.loads((ROOT / REPORT_REL).read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / LEDGER_REL).read_text(encoding="utf-8"))
    if report.get("status") != "pass" or report.get("unit_id") != CHAPTER_ID:
        raise RuntimeError("Chapter 14 translation report is not passing")
    if target_sha(report) != EXPECTED_TARGET[2]:
        raise RuntimeError("Chapter 14 translation report target identity is stale")
    if ledger.get("unit_id") != CHAPTER_ID or target_sha(ledger) != EXPECTED_TARGET[2]:
        raise RuntimeError("Chapter 14 correction ledger identity is stale")
    ledger_records(ledger)
    if bind_final:
        required = [
            PDF_REL, RECEIPT_REL, RENDER_MANIFEST_REL, RENDER_AUDIT_REL,
            ACCESSIBILITY_AUDIT_REL, BUILD_RESULT_REL,
        ]
        missing = [relative for relative in required if not (ROOT / relative).is_file()]
        if missing:
            raise RuntimeError("final artifact binding inputs missing: " + ", ".join(missing))
        receipt_text = (ROOT / RECEIPT_REL).read_text(encoding="utf-8")
        if not re.search(r"Decision:\s*\*\*admitted\*\*", receipt_text, re.I):
            raise RuntimeError("Chapter 14 receipt does not assert admitted")
        ids["pdf"] = identity(ROOT / PDF_REL)
        ids["pdf"]["pages"] = page_count(ROOT / PDF_REL)
        ids["receipt"] = identity(ROOT / RECEIPT_REL)
    return ids, ledger


def preflight() -> dict[str, Any]:
    _, _, _, lock_bytes, was_initial = stripped_prefix()
    identities = {
        "source": identity(SOURCE_PATH, EXPECTED_SOURCE),
        "target": identity(TARGET_PATH, EXPECTED_TARGET),
        "master": identity(ROOT / MASTER_REL, EXPECTED_MASTER),
        "inventory": identity(ROOT / INVENTORY_REL, EXPECTED_INVENTORY),
        "pre_review": identity(ROOT / PRE_REVIEW_REL, EXPECTED_PRE_REVIEW),
        "term_plan": identity(ROOT / TERM_PLAN_REL, EXPECTED_TERM_PLAN),
    }
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    checks = {
        "source_records": len(source.splitlines()),
        "target_records": len(target.splitlines()),
        "labels": len(common.macro(source, "label")),
        "references": len(common.reference_sequence(source)),
        "citations": len(common.macro(source, "cite")),
        "index_terms": len(common.macro(source, "index")),
        "defined_terms": len(common.macro(source, "df")),
        "source_math_surfaces": len(ch03_math.extract_math(source, "ascii")),
        "target_math_surfaces": len(ch03_math.extract_math(target, "utf-8")),
    }
    if checks != {
        "source_records": 687, "target_records": 687, "labels": 20, "references": 31,
        "citations": 4, "index_terms": 79, "defined_terms": 36,
        "source_math_surfaces": 642, "target_math_surfaces": 642,
    }:
        raise RuntimeError(f"Chapter 14 preflight closure differs: {checks}")
    optional = [REPORT_REL, BILINGUAL_REVIEW_REL, LEDGER_REL, PDF_REL, RECEIPT_REL,
                RENDER_MANIFEST_REL, RENDER_AUDIT_REL, ACCESSIBILITY_AUDIT_REL, BUILD_RESULT_REL]
    return {
        "status": "pass",
        "unit_id": CHAPTER_ID,
        "backend_prefix_state": "exact_chapter13" if was_initial else "stripped_locked_chapter14",
        "prefix_lock_sha256": sha(lock_bytes),
        "identities": identities,
        "structural_closure": checks,
        "evidence_state": {relative: "present" if (ROOT / relative).is_file() else "pending" for relative in optional},
        "writes_performed": False,
    }


def chapter_unit(
    ids: dict[str, dict[str, Any]], corrections: list[dict[str, Any]], bind_final: bool
) -> dict[str, Any]:
    record = QUEUED_CH14 | {
        "target_path": TARGET_REL,
        "target_bytes": ids["target"]["bytes"],
        "target_lines": ids["target"]["lines"],
        "target_sha256": ids["target"]["sha256"],
        "target_title": common.macro(TARGET_PATH.read_text(encoding="utf-8"), "chapter")[0]["argument"],
        "translation_state": "admitted" if bind_final else "qa_passed_pending_artifact_binding",
        "qa_state": "passed",
        "source_corrections": len(corrections),
        "build_master_path": MASTER_REL,
        "build_master_bytes": ids["master"]["bytes"],
        "build_master_lines": ids["master"]["lines"],
        "build_master_sha256": ids["master"]["sha256"],
        "artifact_path": PDF_REL,
        "artifact_state": "canonical_output_copy_present_and_frozen" if bind_final else "pending_final_artifact_binding",
        "publication_state": "pending",
        "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        "receipt_path": RECEIPT_REL,
    }
    if bind_final:
        record.update(
            artifact_bytes=ids["pdf"]["bytes"], artifact_pages=ids["pdf"]["pages"],
            artifact_sha256=ids["pdf"]["sha256"], qa_receipt_id="QA-CH14-ADMISSION-20260824",
            receipt_sha256=ids["receipt"]["sha256"],
        )
    return record


def correction_records(
    ledger: dict[str, Any], ledger_sha: str, bind_final: bool, receipt_sha: str | None
) -> list[dict[str, Any]]:
    output = []
    for item in ledger_records(ledger):
        source_lines, target_lines = item["source_lines"], item["target_lines"]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "correction",
            "id": item["id"], "unit_id": CHAPTER_ID,
            "source_locator": f"multiplier_algebras.tex:{source_lines['start']}--{source_lines['end']}",
            "target_locator": f"multiplier_algebras-id.tex:{target_lines['start']}--{target_lines['end']}",
            "correction_type": str(item.get("classification", "mechanical")).lower(),
            "decision": item.get("decision", ""),
            "source_normalized_snippet_sha256": item.get("source_normalized_snippet_sha256"),
            "target_normalized_snippet_sha256": item.get("target_normalized_snippet_sha256"),
            "required_target_anchors": item.get("required_target_anchors", []),
            "forbidden_target_anchors": item.get("forbidden_target_anchors", []),
            "target_disposition": "corrected", "ledger_path": LEDGER_REL,
            "ledger_sha256": ledger_sha, "qa_state": "passed",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
            "upstream_report": "deferred_until_complete_and_separately_authorized",
            "receipt_document_state": "present" if bind_final else "pending",
            "receipt_path": RECEIPT_REL,
        }
        if bind_final:
            record.update(qa_receipt_id="QA-CH14-ADMISSION-20260824", receipt_sha256=receipt_sha)
        output.append(record)
    return output


def terminology_records(
    source: str, target: str, prior_records: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    source_terms = [item["argument"] for item in common.macro(source, "df")]
    target_terms = [item["argument"] for item in common.macro(target, "df")]
    if source_terms != EXPECTED_SOURCE_TERMS or target_terms != EXPECTED_TARGET_TERMS:
        raise RuntimeError("Chapter 14 defined-term sequence differs")
    if len(TERM_OCCURRENCE_IDS) != len(source_terms):
        raise RuntimeError("Chapter 14 term occurrence mapping differs")
    prior_by_id = {item["id"]: item for item in prior_records}
    inherited = set(TERM_OCCURRENCE_IDS) - set(NEW_TERM_SPECS)
    for stable_id in inherited:
        if stable_id not in prior_by_id:
            raise RuntimeError(f"inherited term missing: {stable_id}")
    output = []
    for stable_id, (source_term, preferred, variants, rejected) in NEW_TERM_SPECS.items():
        if stable_id in prior_by_id:
            record = prior_by_id[stable_id]
            if record.get("preferred") != preferred:
                raise RuntimeError(f"existing Chapter 14 term conflicts: {stable_id}")
            continue
        output.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "term", "id": stable_id,
            "source_term": source_term, "locale": "id-ID", "preferred": preferred,
            "variants": variants, "rejected": rejected,
            "scope": "Hilbert modules, essential ideals, compactifications, unitizations, and multiplier algebras",
            "evidence": f"{CHAPTER_ID} target; {TERM_PLAN_REL}", "introduced_in_unit": CHAPTER_ID,
        })
    if len(output) != 21:
        raise RuntimeError(f"Chapter 14 new-term closure differs: {len(output)}")
    return output, TERM_OCCURRENCE_IDS.copy()


def correction_for_source_line(ledger: dict[str, Any], line: int) -> str:
    matches = [
        item["id"] for item in ledger_records(ledger)
        if item.get("affects_math") is True
        and item["source_lines"]["start"] <= line <= item["source_lines"]["end"]
    ]
    if len(matches) != 1:
        raise RuntimeError(f"source line {line} does not resolve to one correction: {matches}")
    return matches[0]


def formula_records(
    source: str, target: str, ledger: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (642, 642):
        raise RuntimeError("Chapter 14 math closure changed")
    mapping = [[index] for index in range(642)]
    mapping[58], mapping[59], mapping[60] = [59], [60], [58]
    mapping[605], mapping[606] = [606], [605]
    if {index for group in mapping for index in group} != set(range(642)):
        raise RuntimeError("Chapter 14 formula mapping does not cover the source exactly once")
    correction_lines = {
        54: correction_for_source_line(ledger, 78),
        232: correction_for_source_line(ledger, 233),
    }
    records = []
    reordered = correction_deltas = internal_prose = 0
    for target_index, source_group in enumerate(mapping):
        source_index = source_group[0]
        source_item, target_item = source_math[source_index], target_math[target_index]
        exact = source_item["normalized"] == target_item["normalized"]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{target_index + 1:04d}",
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{source_index + 1:04d}"],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{target_index + 1:04d}"],
            "source_lines": [[source_item["line_start"], source_item["line_end"]]],
            "target_lines": [[target_item["line_start"], target_item["line_end"]]],
            "source_sha256": [source_item["sha256"]], "target_sha256": [target_item["sha256"]],
            "source_delimiters": [source_item["delimiter"]], "delimiter": target_item["delimiter"],
            "ordinal_alignment": "mapped",
        }
        if exact and source_index == target_index:
            record["alignment"] = "preserved_exact_after_text_aware_whitespace_normalization"
        elif exact:
            record["alignment"] = "preserved_exact_after_text_aware_whitespace_normalization_reordered"
            reordered += 1
        elif target_index in correction_lines:
            record.update(
                alignment="reviewed_source_correction_replacement", sequence_opcode="replace",
                delta_class="classified_source_correction", correction_id=correction_lines[target_index],
                correction_disposition="corrected", qa_state="passed",
            )
            correction_deltas += 1
        elif target_index in {277, 300, 387, 465}:
            record.update(
                alignment="translated_internal_prose_preserving_formula_structure",
                sequence_opcode="replace", delta_class="localized_prose_translation",
                qa_state="passed",
            )
            internal_prose += 1
        else:
            raise RuntimeError(f"unclassified Chapter 14 formula delta: {target_index + 1}")
        records.append(record)
    if (reordered, correction_deltas, internal_prose) != (5, 2, 4):
        raise RuntimeError("Chapter 14 formula delta closure differs")
    return records, {
        "source_math_surfaces": 642, "target_math_surfaces": 642,
        "formula_map_records": 642, "exact_reordered_maps": reordered,
        "classified_source_correction_maps": correction_deltas,
        "localized_prose_translation_maps": internal_prose, "target_insertions": 0,
    }


def artifact_records(ids: dict[str, dict[str, Any]], bind_final: bool) -> list[dict[str, Any]]:
    present_specs = [
        ("ARTIFACT-FAOA-ID-CH14-TARGET-TEX", "translation_source", TARGET_REL, "id-ID"),
        ("ARTIFACT-FAOA-ID-THROUGH-CH14-MASTER", "cumulative_TeX_master", MASTER_REL, "id-ID"),
        ("ARTIFACT-FAOA-ID-CH14-SOURCE-INVENTORY", "source_inventory", INVENTORY_REL, None),
        ("ARTIFACT-FAOA-ID-CH14-PRETRANSLATION-REVIEW", "pretranslation_mathematical_review", PRE_REVIEW_REL, None),
        ("ARTIFACT-FAOA-ID-CH14-BILINGUAL-REVIEW", "bilingual_mathematical_review", BILINGUAL_REVIEW_REL, None),
        ("ARTIFACT-FAOA-ID-CH14-TRANSLATION-REPORT", "translation_QA_report", REPORT_REL, None),
        ("ARTIFACT-FAOA-ID-CH14-TERM-PLAN", "terminology_plan", TERM_PLAN_REL, None),
        ("ARTIFACT-FAOA-ID-CH14-CORRECTIONS-LEDGER", "chapter_source_corrections_ledger", LEDGER_REL, None),
        ("ARTIFACT-FAOA-ID-SOURCE-CORRECTIONS-AGGREGATE-CH14", "aggregate_source_corrections_log", "provenance/SOURCE_CORRECTIONS.md", None),
    ]
    final_specs = [
        ("ARTIFACT-FAOA-ID-THROUGH-CH14-PDF", "canonical_cumulative_reader_pdf", PDF_REL),
        ("ARTIFACT-FAOA-ID-CH14-FINAL-BUILD-RESULT", "deterministic_build_result", BUILD_RESULT_REL),
        ("ARTIFACT-FAOA-ID-CH14-RENDER-MANIFEST", "visual_QA_render_manifest", RENDER_MANIFEST_REL),
        ("ARTIFACT-FAOA-ID-CH14-RENDER-AUDIT", "visual_QA_audit", RENDER_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH14-ACCESSIBILITY-AUDIT", "visual_accessibility_audit", ACCESSIBILITY_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH14-QA-RECEIPT", "admission_receipt", RECEIPT_REL),
    ]
    output = []
    for stable_id, kind, relative_path, locale in present_specs:
        info = identity(ROOT / relative_path)
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "artifact",
            "id": stable_id, "unit_id": CHAPTER_ID, "artifact_kind": kind,
            "path": relative_path, "bytes": info["bytes"], "lines": info["lines"],
            "sha256": info["sha256"], "binding_state": "bound",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if locale:
            record["locale"] = locale
        if kind == "cumulative_TeX_master":
            record["cumulative_through_unit_id"] = CHAPTER_ID
        output.append(record)
    for stable_id, kind, relative_path in final_specs:
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "artifact",
            "id": stable_id, "unit_id": CHAPTER_ID, "artifact_kind": kind,
            "path": relative_path,
            "binding_state": "bound" if bind_final else "pending_final_artifact_binding",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if bind_final:
            info = identity(ROOT / relative_path)
            record.update(bytes=info["bytes"], sha256=info["sha256"])
            if not relative_path.endswith(".pdf"):
                record["lines"] = info["lines"]
            if kind == "canonical_cumulative_reader_pdf":
                record.update(
                    pages=ids["pdf"]["pages"], page_size="US Letter", pdf_lang="id-ID",
                    publication_state="pending",
                )
            if kind == "visual_QA_render_manifest":
                record["render_pages"] = ids["pdf"]["pages"]
            if kind == "admission_receipt":
                record["decision"] = "admitted"
        output.append(record)
    if len(output) != 15:
        raise RuntimeError("Chapter 14 artifact closure differs")
    return output


def qa_records(
    ids: dict[str, dict[str, Any]],
    formula_summary: dict[str, int],
    bind_final: bool,
    prefix_lock_sha256: str,
) -> list[dict[str, Any]]:
    base_record = {
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "qa_event",
        "unit_id": CHAPTER_ID, "timestamp": "2026-08-24",
        "responsible_workflow": "Codex", "model_id": MODEL_ID,
    }
    specs = [
        ("QA-CH14-STRUCTURAL-20260824", "unit_structural", REPORT_REL, "pass"),
        ("QA-CH14-MATH-20260824", "unit_mathematical", BILINGUAL_REVIEW_REL, "pass"),
        ("QA-CH14-LANGUAGE-20260824", "unit_language_terminology", TERM_PLAN_REL, "pass"),
        ("QA-CH14-EXERCISE-SUPPORT-20260824", "exercise_support_provenance", INVENTORY_REL, "pass"),
        ("QA-CH14-RIGHTS-20260824", "unit_rights_privacy", RECEIPT_REL, "pass" if bind_final else "pending"),
        ("QA-CH14-BUILD-20260824", "cumulative_build", BUILD_RESULT_REL, "pass" if bind_final else "pending"),
        ("QA-CH14-VISUAL-20260824", "cumulative_visual", RENDER_AUDIT_REL, "pass" if bind_final else "pending"),
        ("QA-CH14-ACCESSIBILITY-20260824", "cumulative_accessibility", ACCESSIBILITY_AUDIT_REL, "pass" if bind_final else "pending"),
        ("QA-CH14-BACKEND-20260824", "backend_reconciliation", PREFIX_LOCK_REL, "pass"),
        ("QA-CH14-ADMISSION-20260824", "unit_admission", RECEIPT_REL, "pass" if bind_final else "pending"),
    ]
    output = []
    for stable_id, kind, witness, result in specs:
        record = base_record | {
            "id": stable_id, "qa_type": kind, "result": result, "witness": witness,
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if stable_id == "QA-CH14-BACKEND-20260824":
            record["witness_sha256"] = prefix_lock_sha256
        elif result == "pass" and (ROOT / witness).is_file():
            record["witness_sha256"] = sha((ROOT / witness).read_bytes())
        else:
            record["witness_state"] = "pending_final_artifact_binding"
        output.append(record)
    output[0].update(
        sections=3, environment_begins=70, semantic_environment_begins=66,
        labels=20, references=31, citations=4, index_terms=79, defined_terms=36,
        exercise_environments=2, proof_environments=3, proof_hints=2,
        citation_only_proofs=1,
    )
    output[1].update(formula_summary | {"unexplained_deltas": 0, "extractor": "backend/ch03_math.py"})
    output[2].update(
        severity_counts={"P1": 0, "P2": 0, "P3": 0}, unintended_english_prose=0,
        placeholders=0, defined_term_occurrences=36, new_controlled_terms=21,
    )
    output[3].update(
        source_exercises=2, upstream_exercise_hints=0, upstream_proof_hints=2,
        upstream_answers=0, upstream_solutions=0,
        original_solution_state="queued_in_O001", provenance="separately_authored_not_Erdman",
    )
    output[4].update(
        rights_id=RIGHTS,
        attribution_change_notice_sharealike_nonendorsement="present",
        credential_or_token_residue=0,
    )
    if bind_final:
        output[5].update(
            master_artifact_id="ARTIFACT-FAOA-ID-THROUGH-CH14-MASTER",
            pdf_artifact_id="ARTIFACT-FAOA-ID-THROUGH-CH14-PDF", pages=ids["pdf"]["pages"],
        )
        output[6].update(
            pages_rendered=ids["pdf"]["pages"], pages_inspected=ids["pdf"]["pages"],
            visual_defects=0,
        )
        output[7].update(
            tagged_pdf=False, fully_accessible_pdf_claim=False,
            semantic_accessibility_state="remediation_required",
            accessible_html_or_tagged_pdf_state="pending",
            admission_blocker_for_chapter_boundary=False,
        )
        output[9].update(
            decision="admitted", source_sha256=ids["source"]["sha256"],
            target_sha256=ids["target"]["sha256"], build_master_sha256=ids["master"]["sha256"],
            artifact_sha256=ids["pdf"]["sha256"], correction_ledger_sha256=ids["ledger"]["sha256"],
            receipt_sha256=ids["receipt"]["sha256"], all_required_admission_gates="pass",
            publication_state="pending",
        )
    return output


def exercise_support_records(exercises: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(exercises) != 2:
        raise RuntimeError("Chapter 14 exercise semantic closure differs")
    output = []
    for number, exercise in enumerate(exercises, 1):
        output.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "exercise_support",
            "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-{number:03d}",
            "exercise_unit_id": exercise["id"], "source_exercise_order": number,
            "upstream_hint_ids": [], "upstream_inline_hint_state": "absent",
            "upstream_answer_state": "absent", "upstream_solution_state": "absent",
            "original_solution_id": f"O001-{CHAPTER_ID}-EX-{number:03d}-SOLUTION",
            "original_solution_state": "queued_in_O001",
            "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0",
            "provenance": "separately_authored_not_Erdman",
        })
    return output


def build_outputs(bind_final: bool) -> tuple[dict[str, bytes], dict[str, Any]]:
    records, index_fields, index_rows, lock_bytes, _ = stripped_prefix()
    ids, ledger = evidence(bind_final)
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    semantic, segments, relations, source_anchors, _ = base.build_units_and_segments(source, target)
    kinds = collections.Counter(record["unit_kind"] for record in semantic)
    expected_kinds = {
        "section": 3, "conv": 2, "defn": 19, "exam": 9, "exer": 2,
        "notn": 6, "prop": 24, "proof": 3, "cor": 1,
    }
    if len(semantic) != 69 or dict(kinds) != expected_kinds or len(segments) != 86 or len(relations) != 240:
        raise RuntimeError(f"Chapter 14 semantic closure differs: {len(semantic)}/{kinds}/{len(segments)}/{len(relations)}")
    if bind_final:
        for record in semantic + segments:
            record["translation_state"] = "admitted"
            record["admission_state"] = "admitted"

    semantic_offsets = []
    anchor_ids = []
    section_number = node_number = 0
    for anchor in source_anchors:
        if anchor["anchor_type"] == "chapter":
            anchor_ids.append(CHAPTER_ID)
        elif anchor["anchor_type"] == "section":
            section_number += 1
            anchor_ids.append(f"{CHAPTER_ID}-SEC-{section_number:03d}")
        else:
            node_number += 1
            anchor_ids.append(f"{CHAPTER_ID}-NODE-{node_number:04d}")
    if len(source_anchors) != 70 or (section_number, node_number) != (3, 66):
        raise RuntimeError("Chapter 14 anchor closure differs")
    for anchor, stable_id in zip(source_anchors, anchor_ids, strict=True):
        if anchor["anchor_type"] != "chapter":
            semantic_offsets.append((anchor["start"], anchor["end"], stable_id))

    prior_labels = {
        item.get("source_local_id"): item["id"]
        for item in records["semantic_units.jsonl"] if item.get("source_local_id")
    }
    local_labels: dict[str, str] = {}
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 20 or [item["argument"] for item in source_labels] != [item["argument"] for item in target_labels]:
        raise RuntimeError("Chapter 14 label sequence differs")
    for number, occurrence in enumerate(source_labels, 1):
        candidates = [
            (end - start, stable_id)
            for start, end, stable_id in semantic_offsets if start <= occurrence["start"] < end
        ]
        owner = min(candidates)[1] if candidates else CHAPTER_ID
        segment_id = base.ch01.containing_segment(segments, occurrence["start"], "source")
        local_labels[occurrence["argument"]] = owner
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-LABEL-{number:04d}", "relation_type": "declares_label",
            "from_id": segment_id, "to_id": owner, "source_local_id": occurrence["argument"],
            "label_id": f"ERDMAN-FAOA-2015-LABEL-{occurrence['argument']}",
        })

    source_refs = common.reference_sequence(source)
    target_refs = common.reference_sequence(target)
    if len(source_refs) != 31 or len(target_refs) != 31:
        raise RuntimeError("Chapter 14 reference count changed")
    if [(kind, label) for _, kind, label in source_refs] != [(kind, label) for _, kind, label in target_refs]:
        raise RuntimeError("Chapter 14 reference sequence differs")
    resolution_counts: collections.Counter[str] = collections.Counter()
    for number, (source_ref, target_ref) in enumerate(zip(source_refs, target_refs, strict=True), 1):
        source_position, source_kind, source_label = source_ref
        _, target_kind, target_label = target_ref
        if target_label in local_labels:
            endpoint, resolution = local_labels[target_label], "local"
        elif target_label in prior_labels:
            endpoint, resolution = prior_labels[target_label], "admitted_prior_unit"
        else:
            raise RuntimeError(f"unresolved Chapter 14 reference: {source_label!r} -> {target_label!r}")
        resolution_counts[resolution] += 1
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}", "relation_type": "xref",
            "from_id": base.ch01.containing_segment(segments, source_position, "source"),
            "to_id": endpoint, "source_local_id": source_label, "target_local_id": target_label,
            "resolution": resolution, "source_surface": source_kind, "target_surface": target_kind,
        })

    source_citations = common.macro(source, "cite")
    target_citations = common.macro(target, "cite")
    if len(source_citations) != 4 or [item["argument"] for item in source_citations] != [item["argument"] for item in target_citations]:
        raise RuntimeError("Chapter 14 citation sequence differs")
    for number, occurrence in enumerate(source_citations, 1):
        key = occurrence["argument"]
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-CITE-{number:04d}", "relation_type": "cites",
            "from_id": base.ch01.containing_segment(segments, occurrence["start"], "source"),
            "to_id": f"ERDMAN-FAOA-BIB-{key}", "source_local_id": key,
        })

    terms, term_mapping = terminology_records(source, target, records["terminology.jsonl"])
    source_terms = common.macro(source, "df")
    target_terms = common.macro(target, "df")
    for number, (source_term, target_term, term_id) in enumerate(
        zip(source_terms, target_terms, term_mapping, strict=True), 1
    ):
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}", "relation_type": "uses_term",
            "from_id": base.ch01.containing_segment(segments, source_term["start"], "source"),
            "to_id": term_id, "source_term_tex": source_term["argument"],
            "target_term_tex": target_term["argument"], "locale": "id-ID",
        })

    source_indexes = common.macro(source, "index")
    target_indexes = common.macro(target, "index")
    if len(source_indexes) != 79 or len(target_indexes) != 79:
        raise RuntimeError("Chapter 14 index count changed")
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

    receipt_sha = ids.get("receipt", {}).get("sha256")
    corrections = correction_records(ledger, ids["ledger"]["sha256"], bind_final, receipt_sha)
    formulas, formula_summary = formula_records(source, target, ledger)
    artifacts = artifact_records(ids, bind_final)
    qa = qa_records(ids, formula_summary, bind_final, sha(lock_bytes))
    exercises = [record for record in semantic if record["unit_kind"] == "exer"]
    support = exercise_support_records(exercises)

    common_relation = {
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "from_id": CHAPTER_ID,
    }
    relations.append(common_relation | {
        "id": f"{CHAPTER_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS,
    })
    for number, artifact in enumerate(artifacts, 1):
        relations.append(common_relation | {
            "id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}", "relation_type": "has_artifact",
            "to_id": artifact["id"],
        })
    for number, event in enumerate(qa, 1):
        relations.append(common_relation | {
            "id": f"{CHAPTER_ID}-REL-QA-{number:04d}", "relation_type": "has_qa_event",
            "to_id": event["id"],
        })
    for number, correction in enumerate(corrections, 1):
        relations.append(common_relation | {
            "id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}",
            "relation_type": "documents_correction", "to_id": correction["id"],
        })
    for number, (exercise, support_record) in enumerate(zip(exercises, support, strict=True), 1):
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-EXERCISE-SUPPORT-{number:04d}",
            "relation_type": "has_exercise_support", "from_id": exercise["id"],
            "to_id": support_record["id"],
        })

    for segment in segments:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            segment.pop(key, None)
    records["semantic_units.jsonl"].extend(semantic)
    records["segments.jsonl"].extend(segments)
    records["relations.jsonl"].extend(relations)
    records["formula_map.jsonl"].extend(formulas)
    records["exercise_support.jsonl"].extend(support)
    records["artifacts.jsonl"].extend(artifacts)
    records["qa_events.jsonl"].extend(qa)
    records["corrections.jsonl"].extend(corrections)
    records["terminology.jsonl"].extend(terms)
    index_rows.extend(new_index_rows)
    records["units.jsonl"] = [
        chapter_unit(ids, corrections, bind_final) if item.get("id") == CHAPTER_ID else item
        for item in records["units.jsonl"]
    ]

    outputs = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    outputs["index_terms.csv"] = csv_bytes(index_fields, index_rows)
    outputs["CH14_PREFIX_LOCKS.json"] = lock_bytes
    outputs["BACKEND_MANIFEST.csv"] = base.manifest_bytes(outputs)
    summary = {
        "unit": CHAPTER_ID,
        "binding_state": "bound" if bind_final else "pending_final_artifact_binding",
        "semantic_units": len(semantic), "segments": len(segments), "relations": len(relations),
        "formula_maps": len(formulas), "index_rows": len(new_index_rows), "new_terms": len(terms),
        "corrections": len(corrections), "exercise_support": len(support),
        "qa_events": len(qa), "artifacts": len(artifacts),
        "reference_resolution": dict(resolution_counts), "target_sha256": ids["target"]["sha256"],
        "model_id": MODEL_ID,
    }
    return outputs, summary


def reconciliation_report(summary: dict[str, Any], outputs: dict[str, bytes]) -> bytes:
    names = [
        "units.jsonl", "semantic_units.jsonl", "segments.jsonl", "relations.jsonl",
        "formula_map.jsonl", "exercise_support.jsonl", "index_terms.csv", "artifacts.jsonl",
        "qa_events.jsonl", "corrections.jsonl", "terminology.jsonl", "CH14_PREFIX_LOCKS.json",
        "BACKEND_MANIFEST.csv",
    ]
    if summary["binding_state"] == "bound":
        boundary_line = (
            "Generated from the passing Chapter 14 translation report, correction ledger, frozen PDF, "
            "render evidence, deterministic-build result, and admission receipt."
        )
        artifact_line = (
            "- The Chapter 14 cumulative PDF byte count, page count, SHA-256 identity, and admission-receipt "
            "identity are bound in the admitted slice."
        )
    else:
        boundary_line = (
            "Generated from the passing Chapter 14 translation report and correction ledger. The final PDF "
            "and admission receipt are deliberately unbound; run `python backend/generate_ch14_backend.py "
            "--bind-final-artifacts` only after all final evidence is frozen."
        )
        artifact_line = "- No final PDF byte count, page count, or cryptographic hash is present in the pending Chapter 14 slice."
    lines = [
        "# FAOA-2015-CH14 backend reconciliation", "", boundary_line, "",
        f"- Target: `{TARGET_REL}` — {EXPECTED_TARGET[0]} bytes, SHA-256 `{EXPECTED_TARGET[2]}`.",
        f"- Semantic units: {summary['semantic_units']}; segments: {summary['segments']}; relations: {summary['relations']}; formula maps: {summary['formula_maps']}; index rows: {summary['index_rows']}.",
        f"- New terminology records: {summary['new_terms']}; correction records: {summary['corrections']}; exercise-support records: {summary['exercise_support']}; QA events: {summary['qa_events']}; artifacts: {summary['artifacts']}.",
        "- The complete admitted Chapter 1--13 prefix is locked in `backend/CH14_PREFIX_LOCKS.json`.",
        "- Relation endpoint, stable-ID, formula, index, exercise-support, manifest, and deterministic round-trip validation is performed by `backend/validate_ch14_backend.py`.",
        f"- Model provenance: `{MODEL_ID}`.", artifact_line, "", "Generated backend file identities:", "",
    ]
    lines.extend(f"- `{name}` — {len(outputs[name])} bytes, SHA-256 `{sha(outputs[name])}`" for name in names)
    return ("\n".join(lines) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true", help="verify the frozen prefix and source closure without writing")
    parser.add_argument("--bind-final-artifacts", action="store_true")
    parser.add_argument("--check", action="store_true", help="compare generated bytes without writing")
    args = parser.parse_args()
    if args.preflight:
        if args.bind_final_artifacts or args.check:
            parser.error("--preflight cannot be combined with output modes")
        print(json.dumps(preflight(), ensure_ascii=False, sort_keys=True))
        return
    outputs, summary = build_outputs(args.bind_final_artifacts)
    if args.check:
        mismatches = [
            name for name, expected in outputs.items()
            if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != expected
        ]
        if mismatches:
            raise RuntimeError("deterministic backend replay differs: " + ", ".join(mismatches))
        print(json.dumps(summary | {"deterministic_replay": "pass"}, sort_keys=True))
        return
    for name, data in outputs.items():
        (BACKEND / name).write_bytes(data)
    report = reconciliation_report(summary, outputs)
    (ROOT / "qa/CH14_BACKEND_RECONCILIATION.md").write_bytes(report)
    print(json.dumps(summary | {"backend_report": "qa/CH14_BACKEND_RECONCILIATION.md"}, sort_keys=True))


if __name__ == "__main__":
    main()
