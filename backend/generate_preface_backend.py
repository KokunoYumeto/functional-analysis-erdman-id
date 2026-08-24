#!/usr/bin/env python3
"""Deterministically append the FAOA-2015-PREFACE backend slice.

The complete Chapter 1--17 backend is treated as an immutable byte prefix.
The preface is front matter, so its source order is recorded as zero even
though its records are appended after the already admitted corpus.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path[:0] = [str(BACKEND), str(ROOT / "qa")]
import generate_ch17_backend as prior  # noqa: E402


SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
UNIT_ID = "FAOA-2015-PREFACE"
RIGHTS_ID = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_REL = "source/upstream/preface.tex"
TARGET_REL = "source/id-ID/preface-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-complete-source.tex"
LEDGER_REL = "provenance/SOURCE_CORRECTIONS_PREFACE.json"
INVENTORY_REL = "qa/PREFACE_SOURCE_INVENTORY.md"
PRE_REVIEW_REL = "qa/PREFACE_PRETRANSLATION_REVIEW.md"
BILINGUAL_REL = "qa/PREFACE_BILINGUAL_REVIEW.md"
TERM_PLAN_REL = "provenance/PREFACE_TERMINOLOGY_PLAN.md"
PREFIX_LOCK_REL = "backend/PREFACE_PREFIX_LOCKS.json"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf"
RECEIPT_REL = "provenance/PREFACE_BUILD_AND_QA_RECEIPT.md"
BUILD_RESULT_REL = "qa/COMPLETE_SOURCE_FINAL_BUILD_RESULT.json"
RENDER_MANIFEST_REL = "provenance/COMPLETE_SOURCE_RENDER_MANIFEST.csv"
RENDER_AUDIT_REL = "qa/COMPLETE_SOURCE_RENDER_AUDIT.json"
ACCESSIBILITY_AUDIT_REL = "qa/COMPLETE_SOURCE_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
TEXT_FONT_AUDIT_REL = "qa/COMPLETE_SOURCE_TEXT_FONT_AUDIT.json"
NAVIGATION_AUDIT_REL = "qa/COMPLETE_SOURCE_PDF_SECURITY_NAVIGATION_AUDIT.json"
TRANSLATION_REPORT_REL = "qa/preface-translation-report.json"
AGGREGATE_CORRECTIONS_REL = "provenance/SOURCE_CORRECTIONS.md"

SOURCE_PATH = ROOT / SOURCE_REL
TARGET_PATH = ROOT / TARGET_REL

# (bytes, logical records, SHA-256)
EXPECTED_SOURCE = (18_107, 351, "0976042bbb6ae3b8d1e5bb113a93d51169fada9d3e41f2d01435c76b6729edb9")
EXPECTED_TARGET = (18_140, 394, "c622dc9d9c1af4e5b1a6112c84eeff7328c778e8ef8643fc267f6fc6e3e7d564")
EXPECTED_MASTER = (11_176, 353, "7f06919a8ec9088a3bc812fab962a48b5f1b3b0d5d3bce80eb21055f65089041")
EXPECTED_LEDGER = (12_159, 355, "927a74c63cbbc625fb910bfd9a30915179e689d0b5eac64545d2aafcd0bb62ce")
EXPECTED_INVENTORY = (10_739, 206, "b8685b3f58bc548c71e4370ab69ab66089ef544216469a78bace511fe9e1b7a3")
EXPECTED_PRE_REVIEW = (10_535, 203, "98cc77df1e922d465f5e8f3e920568db2bc98946c5f77554c3ba69fd875f7b79")
EXPECTED_BILINGUAL = (2_912, 56, "a58cdf3232204d91a8640934f3d464f3e832578438318cc543a4dc4cb72c12cd")
EXPECTED_TERM_PLAN = (8_538, 145, "6509ba644608e8c9cb6a43a466bc36c34f8caa71c611ca553367bae9e9f8c267")
EXPECTED_FINAL: dict[str, tuple[int, int, str]] = {
    "pdf": (2_480_109, 69_670, "efa2358b3c3e6e8c47e0caee9a02f6afe78d15bea1b0f1822ea8449d801b2b10"),
    "receipt": (8_834, 169, "76a5b4ecd113b7f3f6cbeaa9dd5613e2d93874baab4506d13ddc5577c92129fc"),
    "build_result": (1_913, 66, "db8f799e2a42d6921db50580d6bcb668a8d374f7192a7ce47b542435b3dbf1e3"),
    "render_manifest": (27_263, 239, "2379f5eb5b3b5944be1f70500ea60bb236ec4e0e05f08f679952207d146399e3"),
    "render_audit": (4_971, 222, "92bb17327f1cbf4de707585f1356e29e5d7c086c309a931a08492f94685e3c85"),
    "accessibility_audit": (5_483, 104, "82c0205fa11a71a61db858cd31654c80408e30f5e492b410e619ee6f72605ace"),
    "text_font_audit": (1_387, 34, "dee4ef50646d5841845a61f0e0f18b23b37946bf848ca847aca73448f4d6520d"),
    "navigation_audit": (1_786, 56, "1a3a692d6302351d545f4238e60e5463c8f7856256e69006dfe320075d42e0b5"),
    "translation_report": (69_035, 2_820, "7091f4a505b6c69abbe706cdd4fe849c93f71406160ec97130302031b91b9c8b"),
    "aggregate_corrections": (52_309, 955, "21a911086fab387dcf7291e098a68dcdce64539a3dba86cbbea6012719fa0222"),
}

JSONL_FILES = prior.JSONL_FILES
INDEX_FIELDS = [
    "id", "parent_segment_id", "source_order", "source_line", "source_index_tex",
    "target_line", "target_index_tex", "source_sha256", "target_sha256", "locale",
]

# Exact complete Chapter 1--17 aggregate state.  Record counts exclude the CSV
# header.  The bridge queue record is intentionally part of this frozen prefix.
PREFIX_LOCKS: dict[str, tuple[int, int, str]] = {
    "units.jsonl": (24_619, 18, "1b022e83fa5a5f8aef32403e9ee1343f8dbad91eff86cb156e532027904d04ed"),
    "semantic_units.jsonl": (1_566_276, 1_858, "26ec130a54380ba309631be9a7d42326a856d34957612d369e096adf8310079a"),
    "segments.jsonl": (1_749_183, 2_191, "add457ecd4367183e2f42a4eebd247066f5371a5d84f9f6029b6e2a563542de7"),
    "relations.jsonl": (2_255_697, 8_539, "77a97bee7d19df54403a61395e9beb7f90ef5590d75847e50b91544bd16c3a2f"),
    "formula_map.jsonl": (7_331_945, 11_911, "40c2b21772d74cb3f96eaf965a9b258854027c6911e857ec8dccd43495f413d6"),
    "exercise_support.jsonl": (27_679, 52, "415c30bfc50b4525897f11ce50b1d6e56cfb2f1d519e51a060746adb9abcebaf"),
    "artifacts.jsonl": (98_305, 189, "f053dbafd49b7a208c48af81318bfbdb74c4624d55c4606f98995814191fad29"),
    "qa_events.jsonl": (120_032, 145, "be1ebda4900c30714ad8242f376476753eff6a07a14d0b439007b28f2558b4d5"),
    "corrections.jsonl": (266_999, 272, "f70cc7931e8a90c22fc58f89bcf80d3a16425cadccb5487d322f3ce72f21e605"),
    "terminology.jsonl": (171_497, 407, "2464af7ef8add6e5e01c95a73e967c64f47eacf20d4146e432e1378be890fb2a"),
    "index_terms.csv": (527_164, 2_051, "2fda60dbb12c80cf5db5c9bbead70d904c0012fcf1674f473346a22dc27d457d"),
}

SOURCE_DF = [
    "function", "domain", "input space", "codomain", "target space", "output space",
    "graph", "image", "restriction", "image", "range", "image", "inverse image",
    "injective", "one-to-one", "surjective", "onto", "bijective",
    "a one-to-one correspondence", "commute", "commutative diagram",
]
TARGET_DF = [
    "fungsi", "domain", "ruang masukan", "kodomain", "ruang sasaran", "ruang keluaran",
    "graf", "citra", "pembatasan", "citra", "jangkauan", "citra", "pracitra",
    "injektif", "satu-satu", "surjektif", "onto", "bijektif",
    "korespondensi satu-satu", "berkomutasi", "diagram komutatif",
]
TERM_MAPPING = [
    "TERM-FUNCTION", "TERM-DOMAIN", "TERM-INPUT-SPACE", "TERM-CODOMAIN",
    "TERM-TARGET-SPACE", "TERM-OUTPUT-SPACE", "TERM-GRAPH", "TERM-IMAGE",
    "TERM-RESTRICTION", "TERM-IMAGE", "TERM-RANGE", "TERM-IMAGE",
    "TERM-INVERSE-IMAGE", "TERM-INJECTIVE", "TERM-ONE-TO-ONE", "TERM-SURJECTIVE",
    "TERM-ONTO", "TERM-BIJECTIVE", "TERM-ONE-TO-ONE-CORRESPONDENCE", "TERM-COMMUTE",
    "TERM-COMMUTATIVE-DIAGRAM",
]
NEW_TERM_SPECS: dict[str, tuple[str, str, list[str], list[str]]] = {
    "TERM-FUNCTION": ("function", "fungsi", [], []),
    "TERM-DOMAIN": ("domain", "domain", [], []),
    "TERM-INPUT-SPACE": ("input space", "ruang masukan", [], []),
    "TERM-CODOMAIN": ("codomain", "kodomain", [], []),
    "TERM-TARGET-SPACE": ("target space", "ruang sasaran", [], []),
    "TERM-OUTPUT-SPACE": ("output space", "ruang keluaran", [], []),
    "TERM-GRAPH": ("graph", "graf", [], []),
    "TERM-IMAGE": ("image", "citra", [], []),
    "TERM-RESTRICTION": ("restriction", "pembatasan", ["restriksi"], []),
    "TERM-INVERSE-IMAGE": ("inverse image", "pracitra", ["citra invers"], []),
    "TERM-INJECTIVE": ("injective", "injektif", ["satu-satu"], []),
    "TERM-ONE-TO-ONE": ("one-to-one", "satu-satu", ["injektif"], []),
    "TERM-SURJECTIVE": ("surjective", "surjektif", ["onto"], []),
    "TERM-ONTO": ("onto", "onto", ["surjektif"], []),
    "TERM-BIJECTIVE": ("bijective", "bijektif", ["korespondensi satu-satu"], []),
    "TERM-ONE-TO-ONE-CORRESPONDENCE": (
        "a one-to-one correspondence", "korespondensi satu-satu", ["bijeksi"], [],
    ),
    "TERM-COMMUTE": ("commute", "berkomutasi", [], []),
    "TERM-COMMUTATIVE-DIAGRAM": ("commutative diagram", "diagram komutatif", [], []),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: Path, encoding: str) -> str:
    with path.open("r", encoding=encoding, newline="") as stream:
        return stream.read()


def identity(path: Path, expected: tuple[int, int, str] | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    result = {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "logical_records": len(data.splitlines()),
        "sha256": sha(data),
    }
    if expected and (result["bytes"], result["logical_records"], result["sha256"]) != expected:
        raise RuntimeError(f"identity mismatch: {result}")
    return result


def line_of(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def fragment(text: str, start: int, end: int, encoding: str) -> dict[str, Any]:
    raw = text[start:end]
    return {
        "line_start": line_of(text, start),
        "line_end": line_of(text, max(start, end - 1)),
        "bytes": len(raw.encode(encoding)),
        "sha256": sha(raw.encode(encoding)),
    }


def prefix_bytes(name: str) -> bytes:
    expected_bytes, _, expected_sha = PREFIX_LOCKS[name]
    data = (BACKEND / name).read_bytes()
    if len(data) < expected_bytes:
        raise RuntimeError(f"backend shorter than frozen Chapter 17 prefix: {name}")
    prefix = data[:expected_bytes]
    if sha(prefix) != expected_sha:
        raise RuntimeError(f"Chapter 17 byte prefix differs: {name}")
    if len(data) != expected_bytes and not data.startswith(prefix):
        raise RuntimeError(f"backend append does not preserve prefix: {name}")
    return prefix


def prefix_records(name: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in prefix_bytes(name).decode("utf-8").splitlines()]


def index_prefix() -> tuple[list[str], list[dict[str, str]], bytes]:
    data = prefix_bytes("index_terms.csv")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    fields = list(reader.fieldnames or [])
    rows = list(reader)
    if fields != INDEX_FIELDS or len(rows) != PREFIX_LOCKS["index_terms.csv"][1]:
        raise RuntimeError("Chapter 17 index prefix schema/count differs")
    return fields, rows, data


def jsonl_append(prefix: bytes, records: list[dict[str, Any]]) -> bytes:
    return prefix + prior.jsonl_bytes(records)


def csv_append(prefix: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writerows(rows)
    return prefix + buffer.getvalue().encode("utf-8")


def prefix_lock_bytes() -> bytes:
    payload = {
        "schema_version": "o008.preface-prefix-locks.v1",
        "unit_id": UNIT_ID,
        "scope": (
            "exact complete admitted Chapters 1--17 aggregate backend plus the existing "
            "queued original bridge record; excludes every preface-derived record"
        ),
        "append_policy": "all preface records follow the byte-identical frozen prefix",
        "files": {
            name: {"bytes": values[0], "records": values[1], "sha256": values[2]}
            for name, values in PREFIX_LOCKS.items()
        },
    }
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def evidence_identities() -> dict[str, dict[str, Any]]:
    return {
        "source": identity(SOURCE_PATH, EXPECTED_SOURCE),
        "target": identity(TARGET_PATH, EXPECTED_TARGET),
        "master": identity(ROOT / MASTER_REL, EXPECTED_MASTER),
        "ledger": identity(ROOT / LEDGER_REL, EXPECTED_LEDGER),
        "inventory": identity(ROOT / INVENTORY_REL, EXPECTED_INVENTORY),
        "pre_review": identity(ROOT / PRE_REVIEW_REL, EXPECTED_PRE_REVIEW),
        "bilingual_review": identity(ROOT / BILINGUAL_REL, EXPECTED_BILINGUAL),
        "term_plan": identity(ROOT / TERM_PLAN_REL, EXPECTED_TERM_PLAN),
    }


def final_evidence(ids: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    specs = {
        "pdf": PDF_REL,
        "receipt": RECEIPT_REL,
        "build_result": BUILD_RESULT_REL,
        "render_manifest": RENDER_MANIFEST_REL,
        "render_audit": RENDER_AUDIT_REL,
        "accessibility_audit": ACCESSIBILITY_AUDIT_REL,
        "text_font_audit": TEXT_FONT_AUDIT_REL,
        "navigation_audit": NAVIGATION_AUDIT_REL,
        "translation_report": TRANSLATION_REPORT_REL,
        "aggregate_corrections": AGGREGATE_CORRECTIONS_REL,
    }
    for key, path in specs.items():
        ids[key] = identity(ROOT / path, EXPECTED_FINAL[key])
    ids["pdf"]["pages"] = prior.page_count(ROOT / PDF_REL)
    if ids["pdf"]["pages"] != 238:
        raise RuntimeError("complete-source reader page count differs")

    receipt = (ROOT / RECEIPT_REL).read_text(encoding="utf-8")
    if UNIT_ID not in receipt or not re.search(r"Decision:\s*\*\*admitted\*\*", receipt):
        raise RuntimeError("preface receipt does not assert admission")
    build = json.loads((ROOT / BUILD_RESULT_REL).read_text(encoding="utf-8"))
    if not build.get("byte_identical") or build.get("pages") != 238:
        raise RuntimeError("complete-source final build result differs")
    if build.get("reader", {}).get("sha256") != EXPECTED_FINAL["pdf"][2]:
        raise RuntimeError("complete-source build is not bound to canonical reader")
    render = json.loads((ROOT / RENDER_AUDIT_REL).read_text(encoding="utf-8"))
    if render.get("page_count") != 238 or render.get("outer_5px_ink_pages") != []:
        raise RuntimeError("complete-source render audit differs")
    text_font = json.loads((ROOT / TEXT_FONT_AUDIT_REL).read_text(encoding="utf-8"))
    if text_font.get("status") != "pass" or text_font.get("pdfinfo_tagged") != "no":
        raise RuntimeError("complete-source text/font audit differs")
    navigation = json.loads((ROOT / NAVIGATION_AUDIT_REL).read_text(encoding="utf-8"))
    if navigation.get("status") != "pass" or navigation.get("tagged") is not False:
        raise RuntimeError("complete-source navigation/accessibility truth differs")
    report = json.loads((ROOT / TRANSLATION_REPORT_REL).read_text(encoding="utf-8"))
    if report.get("status") != "pass" or report.get("unit_id") != UNIT_ID:
        raise RuntimeError("preface translation report differs")
    aggregate = (ROOT / AGGREGATE_CORRECTIONS_REL).read_text(encoding="utf-8")
    if "## Preface" not in aggregate or "SOURCE_CORRECTIONS_PREFACE.json" not in aggregate:
        raise RuntimeError("aggregate source-correction log lacks preface closure")
    return ids


def starred_commands(text: str, command: str) -> list[dict[str, Any]]:
    active = prior.common.shared.active_same_length(text)
    pattern = re.compile(r"\\" + re.escape(command) + r"\*\s*\{")
    result: list[dict[str, Any]] = []
    for match in pattern.finditer(active):
        brace = active.find("{", match.start())
        end = prior.common.shared.balanced_end(active, brace)
        result.append({
            "start": match.start(), "end": end,
            "title": text[brace + 1:end - 1].strip(),
        })
    return result


def table_spans(source: str, target: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    source_active = prior.common.shared.active_same_length(source)
    source_starts = [item.start() for item in re.finditer(r"\\\[\s*\\table\{\}", source_active)]
    source_spans: list[tuple[int, int]] = []
    for start in source_starts:
        match = re.search(r"\\caption\{\}\s*\\\]", source_active[start:], flags=re.S)
        if not match:
            raise RuntimeError("unclosed legacy preface table")
        source_spans.append((start, start + match.end()))
    target_spans: list[tuple[int, int]] = []
    for marker in ("PREFACE-C005", "PREFACE-C006"):
        start = target.find(f"% SOURCE-CORRECTION: {marker}")
        if start < 0:
            raise RuntimeError(f"missing target table marker: {marker}")
        end_start = target.find(r"\end{center}", start)
        if end_start < 0:
            raise RuntimeError(f"unclosed target replacement table: {marker}")
        target_spans.append((start, end_start + len(r"\end{center}")))
    if len(source_spans) != 2:
        raise RuntimeError("preface legacy table count differs")
    return source_spans, target_spans


def environment_span(text: str, environment: str) -> tuple[int, int]:
    active = prior.common.shared.active_same_length(text)
    start_match = re.search(r"\\begin\{" + re.escape(environment) + r"\}", active)
    if not start_match:
        raise RuntimeError(f"missing environment: {environment}")
    end_match = re.search(r"\\end\{" + re.escape(environment) + r"\}", active[start_match.end():])
    if not end_match:
        raise RuntimeError(f"unclosed environment: {environment}")
    return start_match.start(), start_match.end() + end_match.end()


def diagram_spans(text: str) -> list[tuple[int, int]]:
    active = prior.common.shared.active_same_length(text)
    return [
        (match.start(), match.end())
        for match in re.finditer(r"\\\[\s*\\xy.*?\\endxy\s*\\\]", active, flags=re.S)
    ]


def structural_records(source: str, target: str, bound: bool) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    source_chapters = starred_commands(source, "chapter")
    target_chapters = starred_commands(target, "chapter")
    source_sections = starred_commands(source, "section")
    target_sections = starred_commands(target, "section")
    if len(source_chapters) != 1 or len(target_chapters) != 1:
        raise RuntimeError("preface starred-chapter topology differs")
    if [item["title"] for item in source_sections] != [
        "Greek Letters", "Fraktur Fonts", "Notation for Sets of Numbers", "Notation for Functions",
    ]:
        raise RuntimeError("source preface section topology differs")
    if [item["title"] for item in target_sections] != [
        "Huruf Yunani", "Font Fraktur", "Notasi untuk Himpunan Bilangan", "Notasi untuk Fungsi",
    ]:
        raise RuntimeError("target preface section topology differs")

    semantic_specs: list[dict[str, Any]] = []
    for number, (source_item, target_item) in enumerate(zip(source_sections, target_sections, strict=True), 1):
        semantic_specs.append({
            "id": f"{UNIT_ID}-SEC-{number:03d}", "kind": "section", "parent": UNIT_ID,
            "source_span": (source_item["start"], source_item["end"]),
            "target_span": (target_item["start"], target_item["end"]),
            "source_title": source_item["title"], "target_title": target_item["title"],
            "source_local_id": "C0009" if number == 3 else None,
        })

    source_tables, target_tables = table_spans(source, target)
    source_align = environment_span(source, "align*")
    target_align = environment_span(target, "align*")
    source_diagrams = diagram_spans(source)
    target_diagrams = diagram_spans(target)
    if len(source_diagrams) != 2 or len(target_diagrams) != 2:
        raise RuntimeError("preface diagram topology differs")
    node_specs = [
        ("NOTATION-001", "alphabet_table_greek", 1, source_tables[0], target_tables[0], "legacy_table_replaced"),
        ("NOTATION-002", "fraktur_table", 2, source_tables[1], target_tables[1], "legacy_table_replaced"),
        ("NOTATION-003", "number_set_notation", 3, source_align, target_align, "translated_notation_block"),
        ("NOTATION-004", "commutative_diagram_rectangular", 4, source_diagrams[0], target_diagrams[0], "preserved_diagram"),
        ("NOTATION-005", "commutative_diagram_triangular", 4, source_diagrams[1], target_diagrams[1], "preserved_diagram"),
    ]
    for suffix, kind, section_number, source_span, target_span, adaptation in node_specs:
        semantic_specs.append({
            "id": f"{UNIT_ID}-{suffix}", "kind": kind,
            "parent": f"{UNIT_ID}-SEC-{section_number:03d}",
            "source_span": source_span, "target_span": target_span,
            "source_title": None, "target_title": None,
            "source_local_id": None, "adaptation_class": adaptation,
        })
    semantic_specs.sort(key=lambda item: item["source_span"][0])

    semantic: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    for order, spec in enumerate(semantic_specs, 1):
        ss, se = spec["source_span"]
        ts, te = spec["target_span"]
        sf = fragment(source, ss, se, "ascii")
        tf = fragment(target, ts, te, "utf-8")
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "unit",
            "id": spec["id"], "unit_kind": spec["kind"], "parent_id": spec["parent"],
            "order_in_front_matter": order, "edition_id": EDITION,
            "target_edition_id": TARGET_EDITION, "source_path": SOURCE_REL,
            "source_line_start": sf["line_start"], "source_line_end": sf["line_end"],
            "source_bytes": sf["bytes"], "source_fragment_sha256": sf["sha256"],
            "target_path": TARGET_REL, "target_line_start": tf["line_start"],
            "target_line_end": tf["line_end"], "target_bytes": tf["bytes"],
            "target_fragment_sha256": tf["sha256"],
            "source_local_id": spec["source_local_id"],
            "source_title_tex": spec["source_title"], "target_title_tex": spec["target_title"],
            "locale": "id-ID", "translation_state": "admitted" if bound else "translated_pending_final_build_and_admission",
            "qa_state": "passed" if bound else "preflight_passed",
            "admission_state": "admitted" if bound else "pending_final_build_visual_qa_and_receipt",
            "rights_id": RIGHTS_ID,
        }
        if spec.get("adaptation_class"):
            record["adaptation_class"] = spec["adaptation_class"]
        semantic.append(record)
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{UNIT_ID}-REL-CONTAINS-{order:04d}", "relation_type": "contains",
            "from_id": spec["parent"], "to_id": spec["id"],
        })

    source_boundaries = [0] + [item["start"] for item in source_sections] + [len(source)]
    target_boundaries = [0] + [item["start"] for item in target_sections] + [len(target)]
    segments: list[dict[str, Any]] = []
    for number in range(5):
        ss, se = source_boundaries[number], source_boundaries[number + 1]
        ts, te = target_boundaries[number], target_boundaries[number + 1]
        sf = fragment(source, ss, se, "ascii")
        tf = fragment(target, ts, te, "utf-8")
        segment_id = f"{UNIT_ID}-SEG-{number + 1:04d}"
        parent = UNIT_ID if number == 0 else f"{UNIT_ID}-SEC-{number:03d}"
        segments.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "segment",
            "id": segment_id, "parent_id": parent, "order": number + 1,
            "segment_role": "preface_prose" if number == 0 else "section_block",
            "source_path": SOURCE_REL, "source_line_start": sf["line_start"],
            "source_line_end": sf["line_end"], "source_bytes": sf["bytes"],
            "source_sha256": sf["sha256"], "target_path": TARGET_REL,
            "target_line_start": tf["line_start"], "target_line_end": tf["line_end"],
            "target_bytes": tf["bytes"], "target_sha256": tf["sha256"],
            "source_edition_id": EDITION, "target_edition_id": TARGET_EDITION,
            "locale": "id-ID", "translation_state": "admitted" if bound else "translated_pending_final_build_and_admission",
            "qa_state": "passed" if bound else "preflight_passed",
            "admission_state": "admitted" if bound else "pending_final_build_visual_qa_and_receipt",
            "rights_id": RIGHTS_ID, "_source_start": ss, "_source_end": se,
            "_target_start": ts, "_target_end": te,
        })
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{UNIT_ID}-REL-TRANSLATES-{number + 1:04d}",
            "relation_type": "translates", "from_id": segment_id, "to_id": segment_id,
            "source_edition_id": EDITION, "target_edition_id": TARGET_EDITION,
        })
        if number:
            relations.append({
                "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
                "id": f"{UNIT_ID}-REL-PRECEDES-{number:04d}", "relation_type": "precedes",
                "from_id": f"{UNIT_ID}-SEG-{number:04d}", "to_id": segment_id,
            })
    return semantic, segments, relations


def containing_segment(segments: list[dict[str, Any]], position: int, side: str) -> str:
    matches = [
        item["id"] for item in segments
        if item[f"_{side}_start"] <= position < item[f"_{side}_end"]
    ]
    if len(matches) != 1:
        raise RuntimeError(f"preface position lacks one segment: {side}/{position}/{matches}")
    return matches[0]


def active_dollar_surfaces(text: str, encoding: str) -> list[dict[str, Any]]:
    active = prior.common.shared.active_same_length(text)
    pattern = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$", flags=re.S)
    output: list[dict[str, Any]] = []
    for match in pattern.finditer(active):
        raw = text[match.start(1):match.end(1)]
        normalized = re.sub(r"\s+", " ", raw).strip()
        output.append({
            "kind": "dollar-inline", "start": match.start(), "end": match.end(),
            "line_start": line_of(text, match.start()), "line_end": line_of(text, match.end() - 1),
            "raw": raw, "normalized": normalized, "sha256": sha(raw.encode(encoding)),
        })
    return output


def align_row_surfaces(text: str, encoding: str) -> list[dict[str, Any]]:
    start, end = environment_span(text, "align*")
    active = prior.common.shared.active_same_length(text)
    output: list[dict[str, Any]] = []
    pattern = re.compile(r"^[ \t]*&.*?\\\\", flags=re.M)
    for match in pattern.finditer(active, start, end):
        raw = text[match.start():match.end()]
        output.append({
            "kind": "align-row", "start": match.start(), "end": match.end(),
            "line_start": line_of(text, match.start()), "line_end": line_of(text, match.end() - 1),
            "raw": raw, "normalized": re.sub(r"\s+", " ", raw).strip(),
            "sha256": sha(raw.encode(encoding)),
        })
    if len(output) != 20:
        raise RuntimeError(f"preface align-row census differs: {len(output)}")
    return output


def diagram_surfaces(text: str, encoding: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for start, end in diagram_spans(text):
        raw = text[start:end]
        output.append({
            "kind": "display-diagram", "start": start, "end": end,
            "line_start": line_of(text, start), "line_end": line_of(text, end - 1),
            "raw": raw, "normalized": re.sub(r"\s+", " ", raw).strip(),
            "sha256": sha(raw.encode(encoding)),
        })
    return output


def formula_records(
    source: str, target: str, segments: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    source_inline = active_dollar_surfaces(source, "ascii")
    target_inline = active_dollar_surfaces(target, "utf-8")
    if (len(source_inline), len(target_inline)) != (201, 202):
        raise RuntimeError("preface active inline-math census differs")

    mappings: list[dict[str, Any]] = []
    matcher = SequenceMatcher(
        None, [item["normalized"] for item in source_inline],
        [item["normalized"] for item in target_inline], autojunk=False,
    )
    opcodes = matcher.get_opcodes()
    if [(tag, i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in opcodes] != [
        ("equal", 113, 113), ("insert", 0, 1), ("equal", 88, 88),
    ]:
        raise RuntimeError(f"preface inline-math alignment differs: {opcodes}")
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            for source_item, target_item in zip(source_inline[i1:i2], target_inline[j1:j2], strict=True):
                mappings.append({
                    "source": source_item, "target": target_item,
                    "sequence_opcode": "equal", "alignment": "preserved_exact",
                    "delta_class": "none",
                })
        else:
            if tag != "insert" or j2 - j1 != 1 or target_inline[j1]["normalized"] != "G":
                raise RuntimeError("unexpected preface inline-math delta")
            mappings.append({
                "source": None, "target": target_inline[j1], "sequence_opcode": "insert",
                "alignment": "reviewed_source_tex_repair_insertion",
                "delta_class": "classified_source_correction",
                "correction_id": f"{UNIT_ID}-CORR-014",
            })

    source_align = align_row_surfaces(source, "ascii")
    target_align = align_row_surfaces(target, "utf-8")
    correction_rows = {
        4: f"{UNIT_ID}-CORR-008", 6: f"{UNIT_ID}-CORR-009",
        8: f"{UNIT_ID}-CORR-010", 10: f"{UNIT_ID}-CORR-011",
    }
    for number, (source_item, target_item) in enumerate(zip(source_align, target_align, strict=True), 1):
        if number in correction_rows:
            delta_class = "classified_source_correction"
            alignment = "reviewed_source_correction"
        elif source_item["normalized"] == target_item["normalized"]:
            delta_class = "none"
            alignment = "preserved_exact"
        else:
            delta_class = "localized_prose_translation"
            alignment = "preserved_mathematical_notation_with_localized_text"
        mapping = {
            "source": source_item, "target": target_item, "sequence_opcode": "equal",
            "alignment": alignment, "delta_class": delta_class,
        }
        if number in correction_rows:
            mapping["correction_id"] = correction_rows[number]
        mappings.append(mapping)

    source_diagrams = diagram_surfaces(source, "ascii")
    target_diagrams = diagram_surfaces(target, "utf-8")
    if len(source_diagrams) != 2 or len(target_diagrams) != 2:
        raise RuntimeError("preface diagram-surface census differs")
    for source_item, target_item in zip(source_diagrams, target_diagrams, strict=True):
        if source_item["normalized"] != target_item["normalized"]:
            raise RuntimeError("preface diagram mathematics differs")
        mappings.append({
            "source": source_item, "target": target_item, "sequence_opcode": "equal",
            "alignment": "preserved_exact", "delta_class": "none",
        })

    source_surfaces = sorted(source_inline + source_align + source_diagrams, key=lambda item: item["start"])
    target_surfaces = sorted(target_inline + target_align + target_diagrams, key=lambda item: item["start"])
    if (len(source_surfaces), len(target_surfaces)) != (223, 224):
        raise RuntimeError("preface composite math-surface census differs")
    for number, item in enumerate(source_surfaces, 1):
        item["ordinal"] = number
        item["id"] = f"{UNIT_ID}-SRC-MATH-{number:04d}"
    for number, item in enumerate(target_surfaces, 1):
        item["ordinal"] = number
        item["id"] = f"{UNIT_ID}-ID-MATH-{number:04d}"
    mappings.sort(key=lambda item: item["target"]["ordinal"])

    output: list[dict[str, Any]] = []
    for number, mapping in enumerate(mappings, 1):
        source_item = mapping["source"]
        target_item = mapping["target"]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map",
            "id": f"{UNIT_ID}-MATHMAP-{number:04d}",
            "source_formula_ids": [source_item["id"]] if source_item else [],
            "target_formula_ids": [target_item["id"]],
            "source_lines": [[source_item["line_start"], source_item["line_end"]]] if source_item else [],
            "target_lines": [[target_item["line_start"], target_item["line_end"]]],
            "source_sha256": [source_item["sha256"]] if source_item else [],
            "target_sha256": [target_item["sha256"]],
            "source_delimiters": [source_item["kind"]] if source_item else [],
            "target_delimiters": [target_item["kind"]],
            "sequence_opcode": mapping["sequence_opcode"],
            "alignment": mapping["alignment"], "delta_class": mapping["delta_class"],
            "parent_segment_id": containing_segment(
                segments, source_item["start"] if source_item else target_item["start"],
                "source" if source_item else "target",
            ),
            "source_provenance": SOURCE_REL, "target_provenance": TARGET_REL,
            "qa_state": "passed",
        }
        if mapping.get("correction_id"):
            record["correction_id"] = mapping["correction_id"]
            record["correction_disposition"] = "applied_verified"
        output.append(record)
    if len(output) != 224:
        raise RuntimeError("preface formula-map record count differs")
    counters = collections.Counter(item["delta_class"] for item in output)
    return output, {
        "records": len(output), "source_surfaces_covered": len(source_surfaces),
        "target_surfaces_covered": len(target_surfaces),
        "exact": counters["none"], "localized_prose_translation": counters["localized_prose_translation"],
        "classified_source_correction": counters["classified_source_correction"],
    }


def terminology_records(
    source: str, target: str, segments: list[dict[str, Any]], prior_terms: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_defs = prior.common.macro(source, "df")
    target_defs = prior.common.macro(target, "df")
    if [item["argument"] for item in source_defs] != SOURCE_DF:
        raise RuntimeError("source preface defined-term sequence differs")
    if [item["argument"] for item in target_defs] != TARGET_DF:
        raise RuntimeError("target preface defined-term sequence differs")
    prior_ids = {item["id"] for item in prior_terms}
    if "TERM-RANGE" not in prior_ids or set(NEW_TERM_SPECS) & prior_ids:
        raise RuntimeError("preface inherited/new terminology boundary differs")
    terms = []
    for stable_id, (source_term, preferred, variants, rejected) in NEW_TERM_SPECS.items():
        terms.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "term",
            "id": stable_id, "source_term": source_term, "locale": "id-ID",
            "preferred": preferred, "variants": variants, "rejected": rejected,
            "scope": "foundational function and notation vocabulary",
            "evidence": f"{UNIT_ID} target; {TERM_PLAN_REL}", "introduced_in_unit": UNIT_ID,
            "source_provenance": SOURCE_REL, "target_provenance": TARGET_REL,
        })
    relations = []
    image_senses = {
        8: "image_of_point", 10: "image_of_set", 12: "image_of_function_synonymous_with_range",
    }
    for number, (source_item, target_item, term_id) in enumerate(
        zip(source_defs, target_defs, TERM_MAPPING, strict=True), 1,
    ):
        relation = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{UNIT_ID}-REL-TERM-{number:04d}", "relation_type": "uses_term",
            "from_id": containing_segment(segments, source_item["start"], "source"),
            "to_id": term_id, "source_term_tex": source_item["argument"],
            "target_term_tex": target_item["argument"], "source_line": source_item["line"],
            "target_line": target_item["line"], "locale": "id-ID",
            "source_provenance": SOURCE_REL, "target_provenance": TARGET_REL,
        }
        if number in image_senses:
            relation["term_sense"] = image_senses[number]
        relations.append(relation)
    return terms, relations


def index_records(
    source: str, target: str, segments: list[dict[str, Any]],
) -> list[dict[str, str]]:
    source_items = prior.common.macro(source, "index")
    target_items = prior.common.macro(target, "index")
    if len(source_items) != 53 or len(target_items) != 53:
        raise RuntimeError("preface active index census differs")
    output = []
    for number, (source_item, target_item) in enumerate(zip(source_items, target_items, strict=True), 1):
        output.append({
            "id": f"{UNIT_ID}-TERM-OCC-{number:04d}",
            "parent_segment_id": containing_segment(segments, source_item["start"], "source"),
            "source_order": str(number), "source_line": str(source_item["line"]),
            "source_index_tex": source_item["argument"], "target_line": str(target_item["line"]),
            "target_index_tex": target_item["argument"],
            "source_sha256": sha(source_item["argument"].encode("ascii")),
            "target_sha256": sha(target_item["argument"].encode("utf-8")), "locale": "id-ID",
        })
    return output


def correction_records(bound: bool, ids: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    path = ROOT / LEDGER_REL
    document = json.loads(path.read_text(encoding="utf-8"))
    items = document.get("records")
    expected_ids = [f"{UNIT_ID}-CORR-{number:03d}" for number in range(1, 15)]
    if (
        document.get("schema_version") != "o008.source-corrections.v1"
        or document.get("unit_id") != UNIT_ID
        or document.get("status") != "applied_verified"
        or not isinstance(items, list)
        or [item.get("id") for item in items] != expected_ids
        or document.get("target", {}).get("sha256") != EXPECTED_TARGET[2]
    ):
        raise RuntimeError("preface correction-ledger closure differs")
    ledger_sha = sha(path.read_bytes())
    output = []
    for item in items:
        source_lines = item["source_lines"]
        target_line = item["target_marker_line"]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "correction",
            "id": item["id"], "unit_id": UNIT_ID,
            "source_locator": f"preface.tex:{source_lines['start']}--{source_lines['end']}",
            "target_locator": f"preface-id.tex:{target_line}",
            "correction_type": str(item["classification"]).lower(),
            "decision": item["decision"], "affects_math": bool(item.get("affects_math", False)),
            "affects_math_surface": bool(item.get("affects_math_surface", False)),
            "target_disposition": "applied_verified", "target_marker": item["target_marker"],
            "target_marker_line": target_line, "ledger_path": LEDGER_REL,
            "ledger_sha256": ledger_sha, "qa_state": "passed",
            "admission_state": "admitted" if bound else "pending_final_build_visual_qa_and_receipt",
            "upstream_report": "deferred_until_complete_and_separately_authorized",
            "source_provenance": SOURCE_REL, "target_provenance": TARGET_REL,
        }
        if bound:
            record.update(
                receipt_document_state="present", receipt_path=RECEIPT_REL,
                receipt_sha256=ids["receipt"]["sha256"],
            )
        for key in (
            "source_required_anchors", "required_target_anchors", "required_target_semantics",
            "forbidden_target_anchors",
        ):
            if key in item:
                record[key] = item[key]
        output.append(record)
    return output, ledger_sha


def artifact_records(ids: dict[str, dict[str, Any]], bound: bool) -> list[dict[str, Any]]:
    specs = [
        ("SOURCE", "official_preface_source", "source"),
        ("TARGET", "indonesian_preface_target", "target"),
        ("MASTER", "complete_source_build_master", "master"),
        ("LEDGER", "source_correction_ledger", "ledger"),
        ("INVENTORY", "source_inventory", "inventory"),
        ("PRE-REVIEW", "pretranslation_review", "pre_review"),
        ("BILINGUAL-REVIEW", "bilingual_review", "bilingual_review"),
        ("TERM-PLAN", "terminology_plan", "term_plan"),
    ]
    if bound:
        specs.extend([
            ("TRANSLATION-REPORT", "translation_validation_report", "translation_report"),
            ("READER-PDF", "canonical_complete_source_reader_pdf", "pdf"),
            ("RECEIPT", "admission_receipt", "receipt"),
            ("BUILD-RESULT", "deterministic_build_result", "build_result"),
            ("RENDER-MANIFEST", "all_page_render_manifest", "render_manifest"),
            ("RENDER-AUDIT", "all_page_render_audit", "render_audit"),
            ("ACCESSIBILITY-AUDIT", "visual_accessibility_narrative_audit", "accessibility_audit"),
            ("TEXT-FONT-AUDIT", "text_font_accessibility_audit", "text_font_audit"),
            ("NAVIGATION-AUDIT", "pdf_navigation_security_audit", "navigation_audit"),
            ("AGGREGATE-CORRECTIONS", "aggregate_source_corrections_log", "aggregate_corrections"),
        ])
    output = []
    for suffix, kind, key in specs:
        info = ids[key]
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "artifact",
            "id": f"{UNIT_ID}-ARTIFACT-{suffix}", "unit_id": UNIT_ID,
            "artifact_kind": kind, "path": info["path"], "bytes": info["bytes"],
            "sha256": info["sha256"],
            "binding_state": "bound", "admission_state": "admitted" if bound else "pending_final_build_visual_qa_and_receipt",
        }
        if key == "pdf":
            record.update(pages=info["pages"], page_size="US Letter", pdf_lang="id-ID", tagged=False)
        else:
            record["lines"] = info["logical_records"]
        output.append(record)
    return output


def qa_records(
    ids: dict[str, dict[str, Any]], lock_sha: str, formula_summary: dict[str, int], bound: bool,
) -> list[dict[str, Any]]:
    common_specs = [
        ("STRUCTURAL", "front_matter_structural", TRANSLATION_REPORT_REL, "pass"),
        ("MATH", "front_matter_mathematical", BILINGUAL_REL, "pass"),
        ("LANGUAGE", "front_matter_language_terminology", TERM_PLAN_REL, "pass"),
        ("RIGHTS", "front_matter_rights", LEDGER_REL, "pass"),
    ]
    specs = common_specs + (
        [
            ("BUILD", "cumulative_build", BUILD_RESULT_REL, "pass"),
            ("VISUAL", "cumulative_visual", RENDER_AUDIT_REL, "pass"),
            ("ACCESSIBILITY", "cumulative_accessibility", ACCESSIBILITY_AUDIT_REL, "pass"),
            ("SECURITY-NAVIGATION", "pdf_security_navigation", NAVIGATION_AUDIT_REL, "pass"),
            ("BACKEND", "backend_reconciliation", PREFIX_LOCK_REL, "pass"),
            ("ADMISSION", "unit_admission", RECEIPT_REL, "pass"),
        ]
        if bound else
        [
            ("BACKEND", "backend_reconciliation", PREFIX_LOCK_REL, "pass"),
            ("ADMISSION", "unit_admission", None, "pending"),
        ]
    )
    output = []
    for suffix, kind, witness, result in specs:
        record = {
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "qa_event",
            "id": f"QA-PREFACE-{suffix}-20260824", "unit_id": UNIT_ID,
            "timestamp": "2026-08-24", "responsible_workflow": "Codex",
            "model_id": MODEL_ID, "qa_type": kind, "result": result,
            "admission_state": "admitted" if bound else "pending_final_build_visual_qa_and_receipt",
        }
        if witness:
            record["witness"] = witness
            record["witness_sha256"] = lock_sha if suffix == "BACKEND" else sha((ROOT / witness).read_bytes())
        else:
            record["pending_reason"] = "final locked build, all-page visual QA, receipt, and admission not yet complete"
        output.append(record)
    output[0].update(sections=4, notation_nodes=5, labels=1, citations=5, index_terms=53, defined_terms=21)
    output[1].update(formula_summary | {"unclassified_deltas": 0, "surface_model": "active dollar math plus align rows plus XY diagrams"})
    output[2].update(defined_term_occurrences=21, new_controlled_terms=18, inherited_terms=1)
    output[3].update(
        rights_id=RIGHTS_ID, excluded_legacy_table_component="replaced_not_redistributed",
        excluded_third_party_quote="paraphrased_with_attribution", nonendorsement="present",
    )
    if bound:
        output[4].update(pages=238, deterministic_replays=2, byte_identical=True, artifact_sha256=ids["pdf"]["sha256"])
        output[5].update(pages_rendered=238, pages_inspected=238, visual_defects=0)
        output[6].update(
            tagged_pdf=False, fully_accessible_pdf_claim=False,
            semantic_accessibility_state="remediation_required", html_state="pending",
            searchable_navigation_state="pass", text_font_witness=TEXT_FONT_AUDIT_REL,
            text_font_witness_sha256=ids["text_font_audit"]["sha256"],
        )
        output[7].update(
            outlines=109, links=3043, named_destinations=2331,
            unresolved_internal_links=0, unsafe_active_content=0,
        )
        output[9].update(
            decision="admitted", source_sha256=EXPECTED_SOURCE[2],
            target_sha256=EXPECTED_TARGET[2], build_master_sha256=EXPECTED_MASTER[2],
            artifact_sha256=ids["pdf"]["sha256"], correction_ledger_sha256=ids["ledger"]["sha256"],
            receipt_sha256=ids["receipt"]["sha256"], all_required_admission_gates="pass",
            publication_state="pending", whole_edition_state="in_progress",
        )
        output[8].update(chapter1_ch17_byte_prefix="pass", deterministic_round_trip="pass")
    else:
        output[4].update(chapter1_ch17_byte_prefix="pass", deterministic_round_trip="pass")
    return output


def unit_record(ids: dict[str, dict[str, Any]], bound: bool) -> dict[str, Any]:
    record = {
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "unit",
        "id": UNIT_ID, "edition_id": EDITION, "target_edition_id": TARGET_EDITION,
        "order": 0, "source_order": 0, "course_role": "front_matter",
        "source_path": SOURCE_REL, "source_bytes": EXPECTED_SOURCE[0],
        "source_lines": EXPECTED_SOURCE[1], "source_sha256": EXPECTED_SOURCE[2],
        "source_title": "PREFACE", "target_path": TARGET_REL,
        "target_bytes": EXPECTED_TARGET[0], "target_lines": EXPECTED_TARGET[1],
        "target_sha256": EXPECTED_TARGET[2], "target_title": "Prakata",
        "translation_state": "admitted" if bound else "translated_pending_final_build_and_admission",
        "qa_state": "passed" if bound else "preflight_passed",
        "admission_state": "admitted" if bound else "pending_final_build_visual_qa_and_receipt",
        "source_corrections": 14, "build_master_path": MASTER_REL,
        "build_master_bytes": EXPECTED_MASTER[0], "build_master_lines": EXPECTED_MASTER[1],
        "build_master_sha256": EXPECTED_MASTER[2],
        "artifact_state": "canonical_output_copy_present_and_frozen" if bound else "pending_final_locked_reader",
        "publication_state": "pending" if bound else "not_admitted", "rights_id": RIGHTS_ID,
        "model_provenance": MODEL_ID, "correction_ledger_sha256": ids["ledger"]["sha256"],
    }
    if bound:
        record.update(
            artifact_path=PDF_REL, artifact_bytes=ids["pdf"]["bytes"],
            artifact_pages=ids["pdf"]["pages"], artifact_sha256=ids["pdf"]["sha256"],
            qa_receipt_id="QA-PREFACE-ADMISSION-20260824", receipt_path=RECEIPT_REL,
            receipt_sha256=ids["receipt"]["sha256"],
            semantic_accessibility_state="remediation_required", html_state="pending",
        )
    return record


def build_outputs(bind_final: bool) -> tuple[dict[str, bytes], dict[str, Any], dict[str, list[dict[str, Any]]]]:
    ids = evidence_identities()
    if bind_final:
        ids = final_evidence(ids)
    source = read_text(SOURCE_PATH, "ascii")
    target = read_text(TARGET_PATH, "utf-8")
    semantic, segments, relations = structural_records(source, target, bind_final)
    formulas, formula_summary = formula_records(source, target, segments)
    prior_terms = prefix_records("terminology.jsonl")
    terms, term_relations = terminology_records(source, target, segments, prior_terms)
    relations.extend(term_relations)
    index_rows = index_records(source, target, segments)
    corrections, ledger_sha = correction_records(bind_final, ids)
    if ledger_sha != ids["ledger"]["sha256"]:
        raise RuntimeError("preface ledger identity differs internally")
    artifacts = artifact_records(ids, bind_final)
    lock_bytes = prefix_lock_bytes()
    qa = qa_records(ids, sha(lock_bytes), formula_summary, bind_final)

    source_labels = prior.common.macro(source, "label")
    target_labels = prior.common.macro(target, "label")
    if [item["argument"] for item in source_labels] != ["C0009"] or [item["argument"] for item in target_labels] != ["C0009"]:
        raise RuntimeError("preface label closure differs")
    relations.append({
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
        "id": f"{UNIT_ID}-REL-LABEL-0001", "relation_type": "declares_label",
        "from_id": containing_segment(segments, source_labels[0]["start"], "source"),
        "to_id": f"{UNIT_ID}-SEC-003", "source_local_id": "C0009",
        "target_local_id": "C0009", "label_id": "ERDMAN-FAOA-2015-LABEL-C0009",
    })

    source_cites = prior.common.macro(source, "cite")
    target_cites = prior.common.macro(target, "cite")
    if [item["argument"] for item in source_cites] != [item["argument"] for item in target_cites] or len(source_cites) != 5:
        raise RuntimeError("preface citation closure differs")
    for number, (source_item, target_item) in enumerate(zip(source_cites, target_cites, strict=True), 1):
        relations.append({
            "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation",
            "id": f"{UNIT_ID}-REL-CITE-{number:04d}", "relation_type": "cites",
            "from_id": containing_segment(segments, source_item["start"], "source"),
            "to_id": f"ERDMAN-FAOA-BIB-{source_item['argument']}",
            "source_local_id": source_item["argument"], "target_local_id": target_item["argument"],
            "source_line": source_item["line"], "target_line": target_item["line"],
            "source_provenance": SOURCE_REL, "target_provenance": TARGET_REL,
        })
    common_relation = {
        "schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "from_id": UNIT_ID,
    }
    relations.append(common_relation | {
        "id": f"{UNIT_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS_ID,
    })
    for number, artifact in enumerate(artifacts, 1):
        relations.append(common_relation | {
            "id": f"{UNIT_ID}-REL-ARTIFACT-{number:04d}",
            "relation_type": "has_artifact", "to_id": artifact["id"],
        })
    for number, event in enumerate(qa, 1):
        relations.append(common_relation | {
            "id": f"{UNIT_ID}-REL-QA-{number:04d}",
            "relation_type": "has_qa_event", "to_id": event["id"],
        })
    for number, correction in enumerate(corrections, 1):
        relations.append(common_relation | {
            "id": f"{UNIT_ID}-REL-CORRECTION-{number:04d}",
            "relation_type": "documents_correction", "to_id": correction["id"],
        })

    expected_relations = 88 if bind_final else 74
    expected_artifacts = 18 if bind_final else 8
    expected_qa = 10 if bind_final else 6
    if len(semantic) != 9 or len(segments) != 5 or len(relations) != expected_relations:
        raise RuntimeError(f"preface structural backend closure differs: {len(semantic)}/{len(segments)}/{len(relations)}")
    if (
        len(terms) != 18 or len(index_rows) != 53 or len(corrections) != 14
        or len(artifacts) != expected_artifacts or len(qa) != expected_qa
    ):
        raise RuntimeError("preface supporting backend closure differs")
    for item in segments:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            item.pop(key, None)

    new_records: dict[str, list[dict[str, Any]]] = {name: [] for name in JSONL_FILES}
    new_records["units.jsonl"] = [unit_record(ids, bind_final)]
    new_records["semantic_units.jsonl"] = semantic
    new_records["segments.jsonl"] = segments
    new_records["relations.jsonl"] = relations
    new_records["formula_map.jsonl"] = formulas
    new_records["artifacts.jsonl"] = artifacts
    new_records["qa_events.jsonl"] = qa
    new_records["corrections.jsonl"] = corrections
    new_records["terminology.jsonl"] = terms

    outputs = {
        name: jsonl_append(prefix_bytes(name), new_records[name])
        for name in JSONL_FILES
    }
    index_fields, _, index_data = index_prefix()
    outputs["index_terms.csv"] = csv_append(index_data, index_fields, index_rows)
    outputs["PREFACE_PREFIX_LOCKS.json"] = lock_bytes
    outputs["BACKEND_MANIFEST.csv"] = prior.base.manifest_bytes(outputs)
    summary = {
        "unit_id": UNIT_ID, "binding_state": "bound" if bind_final else "pending_final_build_visual_qa_and_receipt",
        "semantic_units": len(semantic), "segments": len(segments), "relations": len(relations),
        "formula_map": formula_summary, "index_terms": len(index_rows),
        "new_terms": len(terms), "term_uses": len(TERM_MAPPING), "citations": len(source_cites),
        "corrections": len(corrections), "artifacts": len(artifacts), "qa_events": len(qa),
        "prefix_records": 27_633, "aggregate_records": 28_073 if bind_final else 28_045,
        "source_sha256": EXPECTED_SOURCE[2], "target_sha256": EXPECTED_TARGET[2],
        "master_sha256": EXPECTED_MASTER[2], "ledger_sha256": ledger_sha,
        "model_id": MODEL_ID,
    }
    if bind_final:
        summary.update(
            pdf_sha256=ids["pdf"]["sha256"], receipt_sha256=ids["receipt"]["sha256"],
            pages=ids["pdf"]["pages"], semantic_accessibility_state="remediation_required",
            html_state="pending",
        )
    return outputs, summary, new_records


def preflight() -> dict[str, Any]:
    for name, (_, records, _) in PREFIX_LOCKS.items():
        data = prefix_bytes(name)
        actual_records = len(data.splitlines()) - (1 if name == "index_terms.csv" else 0)
        if actual_records != records:
            raise RuntimeError(f"prefix record count differs: {name}")
    ids = evidence_identities()
    outputs, summary, _ = build_outputs(False)
    return {
        "status": "pass", "unit_id": UNIT_ID, "writes_performed": False,
        "prefix_state": "exact_chapter17_prefix", "identities": ids,
        "summary": summary, "prospective_manifest_sha256": sha(outputs["BACKEND_MANIFEST.csv"]),
    }


def reconciliation_report(summary: dict[str, Any], outputs: dict[str, bytes]) -> bytes:
    state_line = (
        "- Binding state: `bound`; final reader, receipt, build, render, accessibility, text/font, navigation/security, translation, and aggregate-correction witnesses are exact-bound."
        if summary["binding_state"] == "bound"
        else "- The unit remains pending final locked build, all-page visual QA, receipt, and admission."
    )
    lines = [
        "# FAOA-2015-PREFACE backend reconciliation", "",
        "The preface append preserves every complete Chapter 1--17 aggregate backend file as an exact byte prefix.", "",
        f"- Source: `{SOURCE_REL}` — {EXPECTED_SOURCE[0]} bytes, SHA-256 `{EXPECTED_SOURCE[2]}`.",
        f"- Target: `{TARGET_REL}` — {EXPECTED_TARGET[0]} bytes, SHA-256 `{EXPECTED_TARGET[2]}`.",
        f"- Semantic units: {summary['semantic_units']}; segments: {summary['segments']}; relations: {summary['relations']}.",
        f"- Formula maps: {summary['formula_map']['records']} covering {summary['formula_map']['source_surfaces_covered']} source and {summary['formula_map']['target_surfaces_covered']} target surfaces.",
        f"- Index occurrences: {summary['index_terms']}; term uses: {summary['term_uses']}; citations: {summary['citations']}; corrections: {summary['corrections']}.",
        state_line,
        "- The PDF remains honestly untagged; semantic accessibility is `remediation_required` and HTML remains `pending`." if summary["binding_state"] == "bound" else "",
        f"- Model provenance: `{MODEL_ID}`.", "", "Generated aggregate identities:", "",
    ]
    for name in sorted(outputs, key=str.casefold):
        lines.append(f"- `backend/{name}` — {len(outputs[name])} bytes, SHA-256 `{sha(outputs[name])}`")
    return ("\n".join(lines) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--bind-final-artifacts", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.preflight or not (args.write or args.bind_final_artifacts or args.check):
        print(json.dumps(preflight(), ensure_ascii=False, sort_keys=True))
        return
    current_bound = False
    for line in (BACKEND / "units.jsonl").read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if item.get("id") == UNIT_ID:
            current_bound = item.get("admission_state") == "admitted"
            break
    bound = args.bind_final_artifacts or current_bound
    outputs, summary, _ = build_outputs(bound)
    if args.check:
        mismatches = [
            name for name, data in outputs.items()
            if not (BACKEND / name).is_file() or (BACKEND / name).read_bytes() != data
        ]
        if mismatches:
            raise RuntimeError("deterministic preface backend replay differs: " + ", ".join(mismatches))
        print(json.dumps(summary | {"deterministic_replay": "pass"}, ensure_ascii=False, sort_keys=True))
        return
    for name, data in outputs.items():
        (BACKEND / name).write_bytes(data)
    report = reconciliation_report(summary, outputs)
    (ROOT / "qa/PREFACE_BACKEND_RECONCILIATION.md").write_bytes(report)
    print(json.dumps(summary | {"backend_report": "qa/PREFACE_BACKEND_RECONCILIATION.md"}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
