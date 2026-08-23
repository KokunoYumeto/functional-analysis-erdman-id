#!/usr/bin/env python3
"""Generate the deterministic Chapter 12 backend slice.

The default mode records the translated/structurally checked chapter without
claiming a final PDF or admission receipt.  After those artifacts are frozen,
run this same program with ``--bind-final-artifacts``.  That mode replaces only
the Chapter 12 placeholder fields and keeps every stable ID unchanged.

The operation is idempotent.  It removes a prior Chapter 12 projection in
memory, verifies the locked Chapter 1--11 prefix, reapplies the one authorized
Chapter 11 ``swadjoin`` -> ``swaadjoin`` derived-record reconciliation, and
then emits Chapter 12 in source order.
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
import ch03_math  # noqa: E402
import generate_ch01_backend as ch01  # noqa: E402
import generate_ch11_backend as ch11  # noqa: E402
import check_ch05_translation as common  # noqa: E402
import check_ch09_translation as ch09  # noqa: E402
import check_ch12_translation as ch12check  # noqa: E402


SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH12"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_REL = "source/upstream/no_identity.tex"
TARGET_REL = "source/id-ID/no_identity-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-through-ch12.tex"
REPORT_REL = "qa/ch12-translation-report.json"
LEDGER_REL = "provenance/SOURCE_CORRECTIONS_CH12.json"
ADJUDICATION_REL = "provenance/SELF_ADJOINT_TERMINOLOGY_ADJUDICATION.md"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-12.pdf"
RECEIPT_REL = "provenance/CH12_BUILD_AND_QA_RECEIPT.md"
RENDER_MANIFEST_REL = "provenance/CH12_RENDER_MANIFEST.csv"
RENDER_AUDIT_REL = "qa/CH12_RENDER_AUDIT.json"
ACCESSIBILITY_AUDIT_REL = "qa/CH12_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
BUILD_RESULT_REL = "qa/CH12_FINAL_BUILD_RESULT.json"
PREFIX_LOCK_REL = "backend/CH12_PREFIX_LOCKS.json"

SOURCE_PATH = ROOT / SOURCE_REL
TARGET_PATH = ROOT / TARGET_REL

EXPECTED_SOURCE = (47994, 1158, "8da3ffa45bcc07cbe1897a09f309db51e1c5c38080459ffb1f6947bf45a20b6c")
EXPECTED_TARGET = (49730, 1173, "da74193601c80828c8bebb59f20f82481c47627a746fc6c841602d538837d884")
EXPECTED_MASTER = (10275, 341, "d84965e27ee26d71575838a42a8410cf5956b967d188d77a040c0f018fd007de")

# Exact state at the start of this append.  The terminology file already has
# the authorized whole-edition preferred-form correction; its remaining
# Chapter 11 derived projections are intentionally reconciled below.
INITIAL_LOCKS = {
    "units.jsonl": (18253, "97e725193cf78027cfe211bcd18c728f71446e82501a91985c4fde568f0e8e6d"),
    "semantic_units.jsonl": (1068293, "7d8db0c21f4ddc07556ba2c93d0190a8eac505493420dfd18ec11a9d9aba4e3b"),
    "segments.jsonl": (1196279, "8a54137956bd437dc44214752d5904a91e1811daa39acafe47aa3312df246c0c"),
    "relations.jsonl": (1488346, "9f0a6550c5e4daaad2ade44e3da58cc6321f2ff80563aa52dffc8fecffffc97a"),
    "formula_map.jsonl": (4962217, "07f58f091281a733e005c0d67cf2b35266ddb1a221ea886615a902862e161f1c"),
    "exercise_support.jsonl": (25503, "45b128f45d61057837c2eddcf1e45024e62b231e7d4b46e2b2dfb7c849a44925"),
    "index_terms.csv": (407542, "baf4566deae65f961ce6758ace10411406f8c4e8f8bbd6cbf3b593eca01b5cd5"),
    "artifacts.jsonl": (61207, "767c016233daacf7b55004c806d9e8c746cb9e4573b0199107fa6dff59911a16"),
    "qa_events.jsonl": (81106, "9a9e72a424db3203828a94102f42848848fe5aec6fd9721bc0d0994eeafbd51c"),
    "corrections.jsonl": (151576, "4244c4510ab9bcbd0f96f6c7d8c7d48749acb97564e79ae4529f204f998e60d5"),
    "terminology.jsonl": (122922, "12a78639db653c612758b8e20c2600dac3c4a065bf1cd7cbb9b35a4944f9afee"),
}

JSONL_FILES = (
    "units.jsonl",
    "semantic_units.jsonl",
    "segments.jsonl",
    "relations.jsonl",
    "formula_map.jsonl",
    "exercise_support.jsonl",
    "artifacts.jsonl",
    "qa_events.jsonl",
    "corrections.jsonl",
    "terminology.jsonl",
)

QUEUED_CH12 = {
    "schema": SCHEMA,
    "schema_version": VERSION,
    "record_type": "unit",
    "id": CHAPTER_ID,
    "edition_id": EDITION,
    "order": 12,
    "source_path": "no_identity.tex",
    "source_bytes": EXPECTED_SOURCE[0],
    "source_lines": EXPECTED_SOURCE[1],
    "source_sha256": EXPECTED_SOURCE[2],
    "source_title": "SURVIVAL WITHOUT IDENTITY",
    "course_role": "advanced_continuation",
    "translation_state": "queued",
    "rights_id": RIGHTS,
}

SEMANTIC_ENVS = ch01.SEMANTIC_ENVS


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")


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


def csv_bytes(fieldnames: list[str], rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


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


def strip_ch12(
    records: dict[str, list[dict[str, Any]]], index_rows: list[dict[str, str]]
) -> None:
    for name, values in records.items():
        if name == "units.jsonl":
            values[:] = [QUEUED_CH12.copy() if item.get("id") == CHAPTER_ID else item for item in values]
            continue
        values[:] = [
            item
            for item in values
            if not (
                str(item.get("id", "")).startswith(CHAPTER_ID + "-")
                or item.get("unit_id") == CHAPTER_ID
                or item.get("introduced_in_unit") == CHAPTER_ID
            )
        ]
    index_rows[:] = [row for row in index_rows if not row.get("id", "").startswith(CHAPTER_ID + "-")]


def assert_unit_order(units: list[dict[str, Any]]) -> None:
    expected = [f"FAOA-2015-CH{i:02d}" for i in range(1, 18)] + ["FAOA-ID-BRIDGE-CS"]
    actual = [record.get("id") for record in units]
    if actual != expected:
        raise RuntimeError(f"unit order changed: {actual}")


def update_artifact_identity(record: dict[str, Any]) -> None:
    path = ROOT / record["path"]
    info = identity(path)
    record.update(bytes=info["bytes"], sha256=info["sha256"])
    if path.suffix.lower() not in {".png", ".pdf"}:
        record["lines"] = info["lines"]


def reconcile_ch11(records: dict[str, list[dict[str, Any]]], index_rows: list[dict[str, str]]) -> dict[str, int]:
    """Refresh only fields derived from the authorized spelling update."""
    source = (ROOT / ch11.SOURCE_REL).read_text(encoding="ascii")
    target = (ROOT / ch11.TARGET_REL).read_text(encoding="utf-8")
    fresh_semantic, fresh_segments, _, _, _, _ = ch11.unit_and_segments(source, target)
    fresh_semantic_by_id = {item["id"]: item for item in fresh_semantic}
    fresh_segments_by_id = {item["id"]: item for item in fresh_segments}
    changed_semantic = changed_segments = changed_indexes = 0

    for record in records["semantic_units.jsonl"]:
        if not str(record.get("id", "")).startswith("FAOA-2015-CH11-"):
            continue
        fresh = fresh_semantic_by_id[record["id"]]
        before = record.get("target_fragment_sha256")
        for key in ("target_path", "target_line_start", "target_line_end", "target_fragment_sha256", "target_title_tex"):
            record[key] = fresh.get(key)
        changed_semantic += before != record.get("target_fragment_sha256")

    for record in records["segments.jsonl"]:
        if not str(record.get("id", "")).startswith("FAOA-2015-CH11-"):
            continue
        fresh = fresh_segments_by_id[record["id"]]
        before = (record.get("target_bytes"), record.get("target_sha256"))
        for key in ("target_path", "target_line_start", "target_line_end", "target_bytes", "target_sha256"):
            record[key] = fresh[key]
        changed_segments += before != (record.get("target_bytes"), record.get("target_sha256"))

    ch11_target = identity(ROOT / ch11.TARGET_REL)
    adjudication_sha = identity(ROOT / ADJUDICATION_REL)["sha256"]
    for unit in records["units.jsonl"]:
        if unit.get("id") == "FAOA-2015-CH11":
            unit.update(
                target_bytes=ch11_target["bytes"],
                target_lines=ch11_target["lines"],
                target_sha256=ch11_target["sha256"],
                post_admission_terminology_reconciliation=ADJUDICATION_REL,
                post_admission_terminology_reconciliation_sha256=adjudication_sha,
                rebound_at_unit=CHAPTER_ID,
            )

    source_indexes = common.macro(source, "index")
    target_indexes = common.macro(target, "index")
    chapter_rows = [row for row in index_rows if row.get("id", "").startswith("FAOA-2015-CH11-")]
    if len(chapter_rows) != len(source_indexes) or len(source_indexes) != len(target_indexes):
        raise RuntimeError("Chapter 11 index closure changed during spelling reconciliation")
    for row, source_index, target_index in zip(chapter_rows, source_indexes, target_indexes, strict=True):
        before = (row["target_index_tex"], row["target_sha256"])
        row.update(
            target_line=str(target_index["line"]),
            target_index_tex=target_index["argument"],
            target_sha256=sha(target_index["argument"].encode("utf-8")),
        )
        changed_indexes += before != (row["target_index_tex"], row["target_sha256"])

    artifact_ids = {
        "ARTIFACT-FAOA-ID-CH11-TARGET-TEX",
        "ARTIFACT-FAOA-ID-CH11-TERM-QA",
        "ARTIFACT-FAOA-ID-CH11-CORRECTIONS-LEDGER",
        "ARTIFACT-FAOA-ID-CH11-TERMINOLOGY-DECISIONS",
    }
    for record in records["artifacts.jsonl"]:
        if record.get("id") in artifact_ids:
            update_artifact_identity(record)

    ch11_ledger_sha = sha((ROOT / "provenance/SOURCE_CORRECTIONS_CH11.json").read_bytes())
    for record in records["corrections.jsonl"]:
        if record.get("unit_id") == "FAOA-2015-CH11":
            record["ledger_sha256"] = ch11_ledger_sha

    decision_sha = sha((ROOT / "provenance/CH11_TERMINOLOGY_DECISIONS.md").read_bytes())
    for record in records["terminology.jsonl"]:
        if record.get("terminology_decision_path") == "provenance/CH11_TERMINOLOGY_DECISIONS.md":
            record["terminology_decision_sha256"] = decision_sha

    for record in records["qa_events.jsonl"]:
        if record.get("unit_id") != "FAOA-2015-CH11" or not record.get("witness"):
            continue
        witness = ROOT / record["witness"]
        if witness.is_file():
            record["witness_sha256"] = sha(witness.read_bytes())

    preferred = [item for item in records["terminology.jsonl"] if item.get("id") == "TERM-SELF-ADJOINT"]
    if len(preferred) != 1 or preferred[0].get("preferred") != "swaadjoin" or preferred[0].get("variants") != ["swadjoin", "adjoin-diri"]:
        raise RuntimeError("TERM-SELF-ADJOINT is not the adjudicated whole-edition form")
    if changed_semantic not in {0, 5} or changed_segments not in {0, 5} or changed_indexes not in {0, 2}:
        raise RuntimeError(
            "Chapter 11 spelling reconciliation changed an unexpected derived-record set: "
            f"{changed_semantic}/{changed_segments}/{changed_indexes}"
        )
    return {
        "semantic_fragment_hashes_reconciled": 5,
        "segment_hashes_reconciled": 5,
        "index_rows_reconciled": 2,
        "fields_changed_this_run": changed_semantic + changed_segments + changed_indexes,
    }


def nested_anchors(text: str) -> list[dict[str, Any]]:
    active = ch01.active_same_length(text)
    anchors: list[dict[str, Any]] = []
    for command in ("chapter", "section"):
        for match in re.finditer(r"\\" + command + r"\s*\{", active):
            brace = active.find("{", match.start())
            end = ch01.balanced_end(active, brace)
            anchors.append({
                "anchor_type": command,
                "start": match.start(),
                "end": end,
                "title": text[brace + 1 : end - 1].strip(),
                "label": None,
            })
    stack: list[tuple[str, int]] = []
    token_re = re.compile(r"\\(begin|end)\{([^}]+)\}")
    for match in token_re.finditer(active):
        action, environment = match.group(1), match.group(2)
        if action == "begin":
            stack.append((environment, match.start()))
            continue
        if not stack or stack[-1][0] != environment:
            raise RuntimeError(f"environment stack mismatch at line {ch01.line_of(text, match.start())}")
        _, start = stack.pop()
        if environment in SEMANTIC_ENVS:
            end = match.end()
            raw = text[start:end]
            anchors.append({
                "anchor_type": "environment",
                "environment": environment,
                "start": start,
                "end": end,
                "title": ch01.optional_env_title(raw),
                "label": ch01.first_label(raw),
            })
    if stack:
        raise RuntimeError("unclosed environment in Chapter 12")
    anchors.sort(key=lambda item: (item["start"], -item["end"]))
    return anchors


def anchor_signature(anchor: dict[str, Any]) -> tuple[str, str | None]:
    return anchor["anchor_type"], anchor.get("environment")


def build_units_and_segments(source: str, target: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    source_anchors = nested_anchors(source)
    target_anchors = nested_anchors(target)
    if [anchor_signature(item) for item in source_anchors] != [anchor_signature(item) for item in target_anchors]:
        raise RuntimeError("Chapter 12 anchor topology differs")

    ids: list[str] = []
    section_ids: list[tuple[int, str]] = []
    node_number = section_number = 0
    for anchor in source_anchors:
        if anchor["anchor_type"] == "chapter":
            unit_id = CHAPTER_ID
        elif anchor["anchor_type"] == "section":
            section_number += 1
            unit_id = f"{CHAPTER_ID}-SEC-{section_number:03d}"
            section_ids.append((anchor["start"], unit_id))
        else:
            node_number += 1
            unit_id = f"{CHAPTER_ID}-NODE-{node_number:04d}"
        ids.append(unit_id)

    semantic: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    for index, (source_anchor, target_anchor, unit_id) in enumerate(zip(source_anchors, target_anchors, ids, strict=True)):
        if source_anchor["anchor_type"] == "chapter":
            continue
        if source_anchor["anchor_type"] == "section":
            parent = CHAPTER_ID
            kind = "section"
        else:
            enclosing = [
                (other["end"] - other["start"], ids[position])
                for position, other in enumerate(source_anchors)
                if other["anchor_type"] == "environment"
                and other["start"] < source_anchor["start"]
                and source_anchor["end"] < other["end"]
            ]
            if enclosing:
                parent = min(enclosing)[1]
            else:
                prior_sections = [value for start, value in section_ids if start < source_anchor["start"]]
                parent = prior_sections[-1] if prior_sections else CHAPTER_ID
            kind = source_anchor["environment"]
        source_fragment = ch01.fragment(source, source_anchor["start"], source_anchor["end"], "ascii")
        target_fragment = ch01.fragment(target, target_anchor["start"], target_anchor["end"], "utf-8")
        semantic.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "unit",
            "id": unit_id,
            "unit_kind": kind,
            "parent_id": parent,
            "order_in_chapter": len(semantic) + 1,
            "edition_id": EDITION,
            "target_edition_id": TARGET_EDITION,
            "source_path": SOURCE_REL,
            "source_line_start": source_fragment["line_start"],
            "source_line_end": source_fragment["line_end"],
            "source_fragment_sha256": source_fragment["sha256"],
            "target_path": TARGET_REL,
            "target_line_start": target_fragment["line_start"],
            "target_line_end": target_fragment["line_end"],
            "target_fragment_sha256": target_fragment["sha256"],
            "source_local_id": source_anchor.get("label"),
            "source_title_tex": source_anchor.get("title"),
            "target_title_tex": target_anchor.get("title"),
            "locale": "id-ID",
            "translation_state": "qa_passed_pending_artifact_binding",
            "qa_state": "passed",
            "rights_id": RIGHTS,
        })
        relations.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-CONTAINS-{len(semantic):04d}",
            "relation_type": "contains",
            "from_id": parent,
            "to_id": unit_id,
        })

    # Partition using only non-overlapping outer anchors.  Nested theorem-like
    # units remain explicit semantic records and inherit the smallest enclosing
    # segment for occurrence relations.
    partition: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    for source_anchor, target_anchor, unit_id in zip(source_anchors, target_anchors, ids, strict=True):
        if any(item[0]["start"] <= source_anchor["start"] and source_anchor["end"] <= item[0]["end"] for item in partition):
            continue
        partition.append((source_anchor, target_anchor, unit_id))

    source_parts: list[tuple[int, int, str, str]] = []
    target_parts: list[tuple[int, int, str, str]] = []
    source_cursor = target_cursor = 0
    previous_parent = CHAPTER_ID
    for source_anchor, target_anchor, unit_id in partition:
        if source_anchor["start"] > source_cursor or target_anchor["start"] > target_cursor:
            source_gap = ch01.active_same_length(source[source_cursor : source_anchor["start"]]).strip()
            target_gap = ch01.active_same_length(target[target_cursor : target_anchor["start"]]).strip()
            if source_gap or target_gap:
                source_parts.append((source_cursor, source_anchor["start"], "prose", previous_parent))
                target_parts.append((target_cursor, target_anchor["start"], "prose", previous_parent))
        role = "title" if source_anchor["anchor_type"] in {"chapter", "section"} else "semantic_environment"
        source_parts.append((source_anchor["start"], source_anchor["end"], role, unit_id))
        target_parts.append((target_anchor["start"], target_anchor["end"], role, unit_id))
        source_cursor, target_cursor = source_anchor["end"], target_anchor["end"]
        prior_sections = [value for start, value in section_ids if start <= source_anchor["start"]]
        previous_parent = prior_sections[-1] if prior_sections else CHAPTER_ID
    if source_cursor < len(source) or target_cursor < len(target):
        source_gap = ch01.active_same_length(source[source_cursor:]).strip()
        target_gap = ch01.active_same_length(target[target_cursor:]).strip()
        if source_gap or target_gap:
            source_parts.append((source_cursor, len(source), "prose", previous_parent))
            target_parts.append((target_cursor, len(target), "prose", previous_parent))
    if len(source_parts) != len(target_parts):
        raise RuntimeError("Chapter 12 source/target segment partition differs")

    segments: list[dict[str, Any]] = []
    for number, (source_part, target_part) in enumerate(zip(source_parts, target_parts, strict=True), 1):
        ss, se, role, parent = source_part
        ts, te, target_role, target_parent = target_part
        if (role, parent) != (target_role, target_parent):
            raise RuntimeError("Chapter 12 segment role/parent mismatch")
        source_fragment = ch01.fragment(source, ss, se, "ascii")
        target_fragment = ch01.fragment(target, ts, te, "utf-8")
        segment_id = f"{CHAPTER_ID}-SEG-{number:04d}"
        segments.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "segment",
            "id": segment_id,
            "parent_id": parent,
            "order": number,
            "segment_role": role,
            "source_path": SOURCE_REL,
            "source_line_start": source_fragment["line_start"],
            "source_line_end": source_fragment["line_end"],
            "source_bytes": source_fragment["bytes"],
            "source_sha256": source_fragment["sha256"],
            "target_path": TARGET_REL,
            "target_line_start": target_fragment["line_start"],
            "target_line_end": target_fragment["line_end"],
            "target_bytes": target_fragment["bytes"],
            "target_sha256": target_fragment["sha256"],
            "source_edition_id": EDITION,
            "target_edition_id": TARGET_EDITION,
            "locale": "id-ID",
            "translation_state": "qa_passed_pending_artifact_binding",
            "qa_state": "passed",
            "rights_id": RIGHTS,
            "_source_start": ss,
            "_source_end": se,
            "_target_start": ts,
            "_target_end": te,
        })
        relations.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-TRANSLATES-{number:04d}",
            "relation_type": "translates",
            "from_id": segment_id,
            "to_id": segment_id,
            "source_edition_id": EDITION,
            "target_edition_id": TARGET_EDITION,
        })
        if number > 1:
            relations.append({
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-PRECEDES-{number - 1:04d}",
                "relation_type": "precedes",
                "from_id": f"{CHAPTER_ID}-SEG-{number - 1:04d}",
                "to_id": segment_id,
            })
    return semantic, segments, relations, source_anchors, target_anchors


def chapter_unit(ids: dict[str, dict[str, Any]], corrections: list[dict[str, Any]], bind_final: bool) -> dict[str, Any]:
    record = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "unit",
        "id": CHAPTER_ID,
        "edition_id": EDITION,
        "order": 12,
        "source_path": "no_identity.tex",
        "source_bytes": ids["source"]["bytes"],
        "source_lines": ids["source"]["lines"],
        "source_sha256": ids["source"]["sha256"],
        "source_title": "SURVIVAL WITHOUT IDENTITY",
        "target_path": TARGET_REL,
        "target_bytes": ids["target"]["bytes"],
        "target_lines": ids["target"]["lines"],
        "target_sha256": ids["target"]["sha256"],
        "target_title": common.macro(TARGET_PATH.read_text(encoding="utf-8"), "chapter")[0]["argument"],
        "course_role": "advanced_continuation",
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
        "rights_id": RIGHTS,
    }
    if bind_final:
        record.update(
            artifact_bytes=ids["pdf"]["bytes"],
            artifact_pages=ids["pdf"]["pages"],
            artifact_sha256=ids["pdf"]["sha256"],
            admission_state="admitted",
            qa_receipt_id="QA-CH12-ADMISSION-20260823",
            receipt_path=RECEIPT_REL,
            receipt_sha256=ids["receipt"]["sha256"],
        )
    else:
        record.update(admission_state="pending_final_artifact_binding", receipt_path=RECEIPT_REL)
    return record


def correction_records(ledger: dict[str, Any], ledger_sha: str, bind_final: bool, receipt_sha: str | None) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for item in ledger["records"]:
        source_lines = item["source_lines"]
        target_lines = item["target_lines"]
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "correction",
            "id": item["id"],
            "unit_id": CHAPTER_ID,
            "source_locator": f"no_identity.tex:{source_lines['start']}--{source_lines['end']}",
            "target_locator": f"no_identity-id.tex:{target_lines['start']}--{target_lines['end']}",
            "correction_type": str(item.get("classification", "mechanical")).lower(),
            "decision": item.get("decision", ""),
            "source_normalized_snippet_sha256": item.get("source_normalized_snippet_sha256"),
            "target_normalized_snippet_sha256": item.get("target_normalized_snippet_sha256"),
            "required_target_anchor": item.get("required_target_anchor", ""),
            "target_disposition": "corrected",
            "ledger_path": LEDGER_REL,
            "ledger_sha256": ledger_sha,
            "qa_state": "passed",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
            "upstream_report": "deferred_until_complete_and_separately_authorized",
        }
        if bind_final:
            record.update(
                qa_receipt_id="QA-CH12-ADMISSION-20260823",
                receipt_document_state="present",
                receipt_path=RECEIPT_REL,
                receipt_sha256=receipt_sha,
            )
        else:
            record.update(receipt_document_state="pending", receipt_path=RECEIPT_REL)
        output.append(record)
    return output


NEW_TERM_IDS = {
    "unitization": "TERM-UNITIZATION",
    "modular left ideal": "TERM-MODULAR-LEFT-IDEAL",
    "right identity with respect to $J$": "TERM-RIGHT-IDENTITY-RELATIVE-IDEAL",
    "modular right ideal": "TERM-MODULAR-RIGHT-IDEAL",
    "left identity with respect to $J$": "TERM-LEFT-IDENTITY-RELATIVE-IDEAL",
    "modular ideal": "TERM-MODULAR-IDEAL",
    "split exact": "TERM-SPLIT-EXACT",
    "extension": "TERM-ALGEBRA-EXTENSION",
    "algebraic ideal": "TERM-ALGEBRAIC-IDEAL",
    "algebraic $\\ast$-ideal": "TERM-ALGEBRAIC-STAR-IDEAL",
    "(external) direct sum": "TERM-EXTERNAL-DIRECT-SUM",
    "direct sum extension": "TERM-DIRECT-SUM-EXTENSION",
    "strongly equivalent": "TERM-STRONGLY-EQUIVALENT-EXTENSIONS",
    "left multiplication by~$a$": "TERM-LEFT-MULTIPLICATION",
    "left quasi-inverse": "TERM-LEFT-QUASI-INVERSE",
    "right quasi-inverse": "TERM-RIGHT-QUASI-INVERSE",
    "quasi-inverse": "TERM-QUASI-INVERSE",
    "q-spectrum": "TERM-Q-SPECTRUM",
    "positive cone": "TERM-POSITIVE-CONE",
    "preordering": "TERM-PREORDERING",
    "partial ordering": "TERM-PARTIAL-ORDERING",
    "respects": "TERM-ORDER-RESPECTS-VECTOR-OPERATIONS",
    "ordered vector space": "TERM-ORDERED-VECTOR-SPACE",
    "positive elements": "TERM-POSITIVE-ELEMENTS",
    "approximate identity": "TERM-APPROXIMATE-IDENTITY",
    "approximate unit": "TERM-APPROXIMATE-UNIT",
    "sequential approximate identity": "TERM-SEQUENTIAL-APPROXIMATE-IDENTITY",
    "order isomorphism": "TERM-ORDER-ISOMORPHISM",
    "hereditary": "TERM-HEREDITARY-SUBALGEBRA",
    "inverse closed": "TERM-INVERSE-CLOSED",
}


def term_id(source_term: str, prior: dict[str, list[dict[str, Any]]]) -> str:
    if source_term == "partial ordering induced by":
        return "TERM-PARTIAL-ORDER-INDUCED-BY-PROPER-CONE"
    if source_term == "proper":
        return "TERM-PROPER-CONE"
    if source_term == "extension":
        return NEW_TERM_IDS[source_term]
    existing = prior.get(source_term, [])
    if existing:
        if len(existing) == 1:
            return existing[0]["id"]
        proper_cone = [item for item in existing if item["id"] == "TERM-PROPER-CONE"]
        if proper_cone:
            return proper_cone[0]["id"]
        raise RuntimeError(f"ambiguous prior term ID: {source_term!r}")
    if source_term not in NEW_TERM_IDS:
        raise RuntimeError(f"no stable Chapter 12 term ID: {source_term!r}")
    return NEW_TERM_IDS[source_term]


def clean_defined_term(argument: str) -> str:
    """Remove index hooks embedded inside a multiline ``\\df`` argument."""
    without_indexes = re.sub(r"\s*\\index\{[^{}]*\}%?\s*", " ", argument)
    return " ".join(without_indexes.split())


def terminology_records(
    source: str, target: str, prior_records: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    source_terms = common.macro(source, "df")
    target_terms = common.macro(target, "df")
    if len(source_terms) != 42 or len(target_terms) != 42:
        raise RuntimeError("Chapter 12 defined-term count changed")
    prior: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    prior_ids = {item["id"] for item in prior_records}
    for item in prior_records:
        prior[item.get("source_term", "")].append(item)
    mapping: dict[str, str] = {}
    preferred: dict[str, str] = {}
    for source_occurrence, target_occurrence in zip(source_terms, target_terms, strict=True):
        raw_source_term = source_occurrence["argument"]
        source_term = clean_defined_term(raw_source_term)
        target_term = clean_defined_term(target_occurrence["argument"])
        stable_id = term_id(source_term, prior)
        if raw_source_term in mapping and mapping[raw_source_term] != stable_id:
            raise RuntimeError(f"unstable repeated term mapping: {source_term!r}")
        if raw_source_term in preferred and preferred[raw_source_term] != target_term:
            raise RuntimeError(f"inconsistent repeated target term: {source_term!r}")
        mapping[raw_source_term] = stable_id
        preferred[raw_source_term] = target_term
    if len(set(mapping.values())) != len(mapping):
        duplicates = [item for item, count in collections.Counter(mapping.values()).items() if count > 1]
        raise RuntimeError(f"distinct Chapter 12 source terms share IDs: {duplicates}")
    output = []
    for raw_source_term, stable_id in mapping.items():
        if stable_id in prior_ids:
            continue
        source_term = clean_defined_term(raw_source_term)
        output.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "term",
            "id": stable_id,
            "source_term": source_term,
            "locale": "id-ID",
            "preferred": preferred[raw_source_term],
            "variants": [],
            "rejected": [],
            "scope": "nonunital Banach and C-star algebras, extensions, quasi-inverses, positive elements, and approximate identities",
            "evidence": f"{CHAPTER_ID} target; provenance/CH12_TERMINOLOGY_PLAN.md; {ADJUDICATION_REL}",
            "introduced_in_unit": CHAPTER_ID,
        })
    return output, mapping


def formula_records(
    source: str, target: str, ledger: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (927, 931):
        raise RuntimeError(f"Chapter 12 math closure changed: {len(source_math)}/{len(target_math)}")
    source_keys = [ch03_math.math_key(item["normalized"]) for item in source_math]
    target_keys = [ch03_math.math_key(item["normalized"]) for item in target_math]
    opcodes = SequenceMatcher(None, source_keys, target_keys, autojunk=False).get_opcodes()

    mapping: list[list[int] | None] = [None] * len(target_math)
    alignment: dict[int, str] = {}
    handled: set[int] = set()
    for position, left in enumerate(opcodes):
        if left[0] not in {"insert", "delete"} or position in handled:
            continue
        candidate_positions = [
            other_position
            for other_position in range(position + 1, min(position + 4, len(opcodes)))
            if opcodes[other_position][0] in {"insert", "delete"}
            and opcodes[other_position][0] != left[0]
            and other_position not in handled
        ]
        if not candidate_positions:
            continue
        other_position = candidate_positions[0]
        right = opcodes[other_position]
        inserted = left if left[0] == "insert" else right
        deleted = left if left[0] == "delete" else right
        source_values = [source_math[index]["normalized"] for index in range(deleted[1], deleted[2])]
        target_values = [target_math[index]["normalized"] for index in range(inserted[3], inserted[4])]
        if collections.Counter(source_values) != collections.Counter(target_values):
            continue
        remaining: dict[str, list[int]] = collections.defaultdict(list)
        for index in range(deleted[1], deleted[2]):
            remaining[source_math[index]["normalized"]].append(index)
        for index in range(inserted[3], inserted[4]):
            mapping[index] = [remaining[target_math[index]["normalized"]].pop(0)]
            alignment[index] = "preserved_exact_after_text_aware_whitespace_normalization_reordered"
        handled.update({position, other_position})

    for position, (tag, i1, i2, j1, j2) in enumerate(opcodes):
        if position in handled:
            continue
        if tag == "equal":
            for source_index, target_index in zip(range(i1, i2), range(j1, j2), strict=True):
                mapping[target_index] = [source_index]
        elif tag == "replace":
            if i2 - i1 == j2 - j1:
                for source_index, target_index in zip(range(i1, i2), range(j1, j2), strict=True):
                    mapping[target_index] = [source_index]
            elif i2 - i1 == 1:
                for target_index in range(j1, j2):
                    mapping[target_index] = [i1]
            else:
                raise RuntimeError(f"unsupported Chapter 12 formula replacement opcode: {(tag, i1, i2, j1, j2)}")
        elif tag == "insert":
            for target_index in range(j1, j2):
                mapping[target_index] = []
        elif tag == "delete":
            raise RuntimeError(f"unmapped Chapter 12 source formula deletion: {(tag, i1, i2, j1, j2)}")
    if any(value is None for value in mapping):
        raise RuntimeError("Chapter 12 formula mapping is incomplete")
    source_coverage = {index for group in mapping for index in (group or [])}
    if source_coverage != set(range(len(source_math))):
        raise RuntimeError("Chapter 12 source formula coverage is incomplete")

    corrections = ledger["records"]
    def correction_for(source_group: list[int], target_index: int) -> str | None:
        source_lines = set()
        for index in source_group:
            source_lines.update(range(source_math[index]["line_start"], source_math[index]["line_end"] + 1))
        target_lines = set(range(target_math[target_index]["line_start"], target_math[target_index]["line_end"] + 1))
        matches = []
        for record in corrections:
            source_range = set(range(record["source_lines"]["start"], record["source_lines"]["end"] + 1))
            target_range = set(range(record["target_lines"]["start"], record["target_lines"]["end"] + 1))
            if source_lines.intersection(source_range) or target_lines.intersection(target_range):
                if "MATHEMATICAL" in record["classification"] or record.get("affects_math") is True:
                    matches.append(record["id"])
        return matches[0] if matches else None

    records: list[dict[str, Any]] = []
    counts: collections.Counter[str] = collections.Counter()
    for target_index, source_group_value in enumerate(mapping):
        source_group = source_group_value or []
        target_item = target_math[target_index]
        exact = (
            len(source_group) == 1
            and source_math[source_group[0]]["normalized"] == target_item["normalized"]
        )
        if target_index in alignment:
            state = alignment[target_index]
        elif exact:
            state = "preserved_exact_after_text_aware_whitespace_normalization"
        elif not source_group:
            state = "reviewed_target_insertion_from_source_correction"
        elif len(source_group) == 1 and sum(1 for group in mapping if group == source_group) > 1:
            state = "reviewed_source_correction_split"
        else:
            state = "reviewed_source_correction_or_localized_math_text"
        counts[state] += 1
        source_items = [source_math[index] for index in source_group]
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "formula_map",
            "id": f"{CHAPTER_ID}-MATHMAP-{target_index + 1:04d}",
            "alignment": state,
            "ordinal_alignment": "reordered" if "reordered" in state else ("target_insertion" if not source_group else "mapped"),
            "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{index + 1:04d}" for index in source_group],
            "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{target_index + 1:04d}"],
            "source_lines": [[item["line_start"], item["line_end"]] for item in source_items],
            "target_lines": [[target_item["line_start"], target_item["line_end"]]],
            "source_sha256": [item["sha256"] for item in source_items],
            "target_sha256": [target_item["sha256"]],
            "source_delimiters": [item["delimiter"] for item in source_items],
            "delimiter": target_item["delimiter"],
        }
        if not exact and "reordered" not in state:
            correction_id = correction_for(source_group, target_index)
            if not correction_id:
                raise RuntimeError(f"formula delta lacks a correction record: target ordinal {target_index + 1}")
            record.update(
                sequence_opcode="insert" if not source_group else "replace",
                delta_class="classified_source_correction_or_math_localization",
                correction_id=correction_id,
                correction_disposition="corrected",
                qa_state="passed",
            )
        records.append(record)
    return records, {
        "source_math_surfaces": len(source_math),
        "target_math_surfaces": len(target_math),
        "formula_map_records": len(records),
        "exact_or_reordered": counts["preserved_exact_after_text_aware_whitespace_normalization"] + counts["preserved_exact_after_text_aware_whitespace_normalization_reordered"],
        "classified_delta_maps": len(records) - counts["preserved_exact_after_text_aware_whitespace_normalization"] - counts["preserved_exact_after_text_aware_whitespace_normalization_reordered"],
    }


def artifact_records(ids: dict[str, dict[str, Any]], bind_final: bool) -> list[dict[str, Any]]:
    present_specs = [
        ("ARTIFACT-FAOA-ID-CH12-TARGET-TEX", "translation_source", TARGET_REL, "id-ID"),
        ("ARTIFACT-FAOA-ID-THROUGH-CH12-MASTER", "cumulative_TeX_master", MASTER_REL, "id-ID"),
        ("ARTIFACT-FAOA-ID-CH12-CENSUS", "source_census", "qa/CH12_CENSUS.json", None),
        ("ARTIFACT-FAOA-ID-CH12-SOURCE-INVENTORY", "source_inventory", "qa/CH12_SOURCE_INVENTORY.md", None),
        ("ARTIFACT-FAOA-ID-CH12-MATH-REVIEW", "pretranslation_mathematical_review", "qa/CH12_PRETRANSLATION_MATH_REVIEW.md", None),
        ("ARTIFACT-FAOA-ID-CH12-TRANSLATION-REPORT", "translation_QA_report", REPORT_REL, None),
        ("ARTIFACT-FAOA-ID-CH12-TERM-PLAN", "terminology_plan", "provenance/CH12_TERMINOLOGY_PLAN.md", None),
        ("ARTIFACT-FAOA-ID-CH12-CORRECTIONS-LEDGER", "chapter_source_corrections_ledger", LEDGER_REL, None),
        ("ARTIFACT-FAOA-ID-CH12-SELF-ADJOINT-ADJUDICATION", "whole_edition_terminology_adjudication", ADJUDICATION_REL, None),
    ]
    pending_specs = [
        ("ARTIFACT-FAOA-ID-THROUGH-CH12-PDF", "canonical_cumulative_reader_pdf", PDF_REL),
        ("ARTIFACT-FAOA-ID-CH12-FINAL-BUILD-RESULT", "deterministic_build_result", BUILD_RESULT_REL),
        ("ARTIFACT-FAOA-ID-CH12-RENDER-MANIFEST", "visual_QA_render_manifest", RENDER_MANIFEST_REL),
        ("ARTIFACT-FAOA-ID-CH12-RENDER-AUDIT", "visual_QA_audit", RENDER_AUDIT_REL),
        ("ARTIFACT-FAOA-ID-CH12-QA-RECEIPT", "admission_receipt", RECEIPT_REL),
    ]
    output: list[dict[str, Any]] = []
    for stable_id, kind, relative_path, locale in present_specs:
        info = identity(ROOT / relative_path)
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": stable_id,
            "unit_id": CHAPTER_ID,
            "artifact_kind": kind,
            "path": relative_path,
            "bytes": info["bytes"],
            "lines": info["lines"],
            "sha256": info["sha256"],
            "binding_state": "bound",
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if locale:
            record["locale"] = locale
        if kind == "cumulative_TeX_master":
            record["cumulative_through_unit_id"] = CHAPTER_ID
        output.append(record)
    for stable_id, kind, relative_path in pending_specs:
        record = {
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "artifact",
            "id": stable_id,
            "unit_id": CHAPTER_ID,
            "artifact_kind": kind,
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
                record.update(pages=ids["pdf"]["pages"], page_size="US Letter", pdf_lang="id-ID", publication_state="pending")
            if kind == "visual_QA_render_manifest":
                record["render_pages"] = ids["pdf"]["pages"]
            if kind == "admission_receipt":
                record["decision"] = "admitted"
        output.append(record)
    return output


def qa_records(ids: dict[str, dict[str, Any]], formula_summary: dict[str, int], bind_final: bool) -> list[dict[str, Any]]:
    base = {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "qa_event",
        "unit_id": CHAPTER_ID,
        "timestamp": "2026-08-23",
        "responsible_workflow": "Codex",
        "model_id": MODEL_ID,
    }
    specs = [
        ("QA-CH12-STRUCTURAL-20260823", "unit_structural", REPORT_REL, "pass"),
        ("QA-CH12-MATH-20260823", "unit_mathematical", REPORT_REL, "pass"),
        ("QA-CH12-LANGUAGE-20260823", "unit_language_terminology", "provenance/CH12_TERMINOLOGY_PLAN.md", "pass"),
        ("QA-CH12-CH11-TERM-RECONCILIATION-20260823", "historical_derived_record_reconciliation", ADJUDICATION_REL, "pass"),
        ("QA-CH12-RIGHTS-20260823", "unit_rights_privacy", TARGET_REL, "pass"),
        ("QA-CH12-BUILD-20260823", "cumulative_build", BUILD_RESULT_REL, "pass" if bind_final else "pending"),
        ("QA-CH12-VISUAL-20260823", "cumulative_visual", RENDER_AUDIT_REL, "pass" if bind_final else "pending"),
        ("QA-CH12-ACCESSIBILITY-20260823", "cumulative_accessibility", ACCESSIBILITY_AUDIT_REL, "pass" if bind_final else "pending"),
        ("QA-CH12-BACKEND-20260823", "backend_reconciliation", PREFIX_LOCK_REL, "pass"),
        ("QA-CH12-ADMISSION-20260823", "unit_admission", RECEIPT_REL, "pass" if bind_final else "pending"),
    ]
    output = []
    for stable_id, kind, witness, result in specs:
        record = base | {
            "id": stable_id,
            "qa_type": kind,
            "result": result,
            "witness": witness,
            "admission_state": "admitted" if bind_final else "pending_final_artifact_binding",
        }
        if result == "pass" and (ROOT / witness).is_file():
            record["witness_sha256"] = sha((ROOT / witness).read_bytes())
        else:
            record["witness_state"] = "pending_final_artifact_binding"
        output.append(record)
    output[0].update(
        sections=6,
        environment_begins=154,
        labels=65,
        references=46,
        citations=17,
        index_terms=102,
        defined_terms=42,
        exercise_environments=0,
        proof_environments=12,
        proof_hints=8,
        citation_only_proofs=2,
    )
    output[1].update(formula_summary | {"unexplained_deltas": 0, "extractor": "backend/ch03_math.py"})
    output[2].update(
        severity_counts={"P1": 0, "P2": 0, "P3": 0},
        unintended_english_prose=0,
        placeholders=0,
        preferred_self_adjoint_term="swaadjoin",
    )
    output[3].update(
        changed_reader_occurrences=7,
        changed_index_occurrences=2,
        prior_public_checkpoint_state="preserved_as_historical_release",
    )
    output[4].update(
        rights_id=RIGHTS,
        attribution_change_notice_sharealike_nonendorsement="present",
        credential_or_token_residue=0,
    )
    if bind_final:
        output[5].update(
            master_artifact_id="ARTIFACT-FAOA-ID-THROUGH-CH12-MASTER",
            pdf_artifact_id="ARTIFACT-FAOA-ID-THROUGH-CH12-PDF",
            pages=ids["pdf"]["pages"],
        )
        output[6].update(pages_rendered=ids["pdf"]["pages"], pages_inspected=ids["pdf"]["pages"], visual_defects=0)
        output[7].update(
            tagged_pdf=False,
            fully_accessible_pdf_claim=False,
            semantic_accessibility_state="remediation_required",
            accessible_html_or_tagged_pdf_state="pending",
            admission_blocker_for_chapter_boundary=False,
        )
        output[9].update(
            decision="admitted",
            source_sha256=ids["source"]["sha256"],
            target_sha256=ids["target"]["sha256"],
            build_master_sha256=ids["master"]["sha256"],
            artifact_sha256=ids["pdf"]["sha256"],
            correction_ledger_sha256=ids["ledger"]["sha256"],
            receipt_sha256=ids["receipt"]["sha256"],
            all_required_admission_gates="pass",
            publication_state="pending",
        )
    return output


def page_count(pdf: Path) -> int:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf)).pages)
    except Exception:
        return len(re.findall(rb"/Type\s*/Page(?:\s|/|>)", pdf.read_bytes()))


def evidence(bind_final: bool) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    ids = {
        "source": identity(SOURCE_PATH, EXPECTED_SOURCE),
        "target": identity(TARGET_PATH, EXPECTED_TARGET),
        "master": identity(ROOT / MASTER_REL, EXPECTED_MASTER),
        "report": identity(ROOT / REPORT_REL),
        "ledger": identity(ROOT / LEDGER_REL),
        "adjudication": identity(ROOT / ADJUDICATION_REL),
    }
    report = json.loads((ROOT / REPORT_REL).read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / LEDGER_REL).read_text(encoding="utf-8"))
    if report.get("status") != "pass" or report.get("unit_id") != CHAPTER_ID:
        raise RuntimeError("Chapter 12 translation report is not a passing bound witness")
    if report.get("target", {}).get("sha256") != EXPECTED_TARGET[2]:
        raise RuntimeError("Chapter 12 report target identity is stale")
    if ledger.get("unit_id") != CHAPTER_ID or ledger.get("record_count") != 29 or len(ledger.get("records", [])) != 29:
        raise RuntimeError("Chapter 12 correction ledger closure changed")
    if ledger.get("target", {}).get("sha256") != EXPECTED_TARGET[2]:
        raise RuntimeError("Chapter 12 correction ledger target identity is stale")
    if bind_final:
        required = [PDF_REL, RECEIPT_REL, RENDER_MANIFEST_REL, RENDER_AUDIT_REL, BUILD_RESULT_REL]
        missing = [relative for relative in required if not (ROOT / relative).is_file()]
        if missing:
            raise RuntimeError("final artifact binding inputs missing: " + ", ".join(missing))
        receipt_text = (ROOT / RECEIPT_REL).read_text(encoding="utf-8")
        if not re.search(r"Decision:\s*\*\*admitted\*\*", receipt_text, re.I):
            raise RuntimeError("Chapter 12 receipt does not assert admitted")
        ids["pdf"] = identity(ROOT / PDF_REL)
        ids["pdf"]["pages"] = page_count(ROOT / PDF_REL)
        ids["receipt"] = identity(ROOT / RECEIPT_REL)
    return ids, ledger


def prefix_payload(
    records: dict[str, list[dict[str, Any]]], fields: list[str], index_rows: list[dict[str, str]]
) -> tuple[dict[str, bytes], dict[str, Any]]:
    payload = {name: jsonl_bytes(records[name]) for name in JSONL_FILES}
    payload["index_terms.csv"] = csv_bytes(fields, index_rows)
    locks = {
        "schema_version": "o008.ch12-prefix-locks.v1",
        "unit_id": CHAPTER_ID,
        "scope": "Chapter 1--11 after the authorized Chapter 11 swaadjoin derived-record reconciliation; excludes all Chapter 12 records",
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


def manifest_bytes(overrides: dict[str, bytes] | None = None) -> bytes:
    overrides = overrides or {}
    names = {path.name for path in BACKEND.iterdir() if path.is_file() and path.name != "BACKEND_MANIFEST.csv" and path.suffix != ".pyc"}
    names.update(overrides)
    rows = []
    for name in sorted(names, key=str.casefold):
        data = overrides.get(name)
        if data is None:
            data = (BACKEND / name).read_bytes()
        rows.append((name, len(data), sha(data)))
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["relative_path", "bytes", "sha256"])
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def build_outputs(bind_final: bool) -> tuple[dict[str, bytes], dict[str, Any]]:
    was_initial = initial_state()
    records, index_fields, index_rows = load_data()
    strip_ch12(records, index_rows)
    assert_unit_order(records["units.jsonl"])
    reconciliation = reconcile_ch11(records, index_rows)

    base_payload, locks = prefix_payload(records, index_fields, index_rows)
    lock_path = ROOT / PREFIX_LOCK_REL
    lock_bytes = (json.dumps(locks, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if lock_path.is_file() and not was_initial:
        stored = lock_path.read_bytes()
        if stored != lock_bytes:
            raise RuntimeError("Chapter 1--11 prefix lock differs after stripping Chapter 12")
    elif not was_initial:
        raise RuntimeError("backend is neither the exact initial state nor a locked Chapter 12 state")

    ids, ledger = evidence(bind_final)
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    semantic, segments, relations, source_anchors, _ = build_units_and_segments(source, target)
    if bind_final:
        for record in semantic + segments:
            record["translation_state"] = "admitted"
            record["admission_state"] = "admitted"

    # Map labels to the smallest containing semantic unit, with the segment as
    # the source-facing occurrence surface.
    semantic_offsets = []
    semantic_by_id = {record["id"]: record for record in semantic}
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
    for anchor, stable_id in zip(source_anchors, anchor_ids, strict=True):
        if anchor["anchor_type"] != "chapter":
            semantic_offsets.append((anchor["start"], anchor["end"], stable_id))

    prior_labels = {
        item.get("source_local_id"): item["id"]
        for item in records["semantic_units.jsonl"]
        if item.get("source_local_id")
    }
    local_labels: dict[str, str] = {}
    source_labels = common.macro(source, "label")
    target_labels = common.macro(target, "label")
    if len(source_labels) != 65 or [item["argument"] for item in source_labels] != [item["argument"] for item in target_labels]:
        raise RuntimeError("Chapter 12 label sequence differs")
    for number, occurrence in enumerate(source_labels, 1):
        candidates = [(end - start, stable_id) for start, end, stable_id in semantic_offsets if start <= occurrence["start"] < end]
        owner = min(candidates)[1] if candidates else CHAPTER_ID
        segment_id = ch01.containing_segment(segments, occurrence["start"], "source")
        local_labels[occurrence["argument"]] = owner
        relations.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-LABEL-{number:04d}",
            "relation_type": "declares_label",
            "from_id": segment_id,
            "to_id": owner,
            "source_local_id": occurrence["argument"],
            "label_id": f"ERDMAN-FAOA-2015-LABEL-{occurrence['argument']}",
        })

    source_refs = common.reference_sequence(source)
    target_refs = common.reference_sequence(target)
    if len(source_refs) != 46 or len(target_refs) != 46:
        raise RuntimeError("Chapter 12 reference count changed")
    resolution_counts: collections.Counter[str] = collections.Counter()
    for number, (source_ref, target_ref) in enumerate(zip(source_refs, target_refs, strict=True), 1):
        source_position, source_kind, source_label = source_ref
        _, target_kind, target_label = target_ref
        if target_label in local_labels:
            endpoint, resolution = local_labels[target_label], "local"
        elif target_label in prior_labels:
            endpoint, resolution = prior_labels[target_label], "admitted_prior_unit"
        elif target_label == "0038614":
            endpoint, resolution = "FAOA-2015-CH14", "queued_future_unit"
        else:
            raise RuntimeError(f"unresolved Chapter 12 reference: {source_label!r} -> {target_label!r}")
        resolution_counts[resolution] += 1
        relations.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-XREF-{number:04d}",
            "relation_type": "xref",
            "from_id": ch01.containing_segment(segments, source_position, "source"),
            "to_id": endpoint,
            "source_local_id": source_label,
            "target_local_id": target_label,
            "resolution": resolution,
            "source_surface": source_kind,
            "target_surface": target_kind,
        })

    source_citations = common.macro(source, "cite")
    target_citations = common.macro(target, "cite")
    if len(source_citations) != 17 or [item["argument"] for item in source_citations] != [item["argument"] for item in target_citations]:
        raise RuntimeError("Chapter 12 citation sequence differs")
    citation_relation_number = 0
    for occurrence in source_citations:
        for key in [item.strip() for item in occurrence["argument"].split(",")]:
            citation_relation_number += 1
            relations.append({
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-CITE-{citation_relation_number:04d}",
                "relation_type": "cites",
                "from_id": ch01.containing_segment(segments, occurrence["start"], "source"),
                "to_id": f"ERDMAN-FAOA-BIB-{key}",
                "source_local_id": key,
            })

    hint_number = 0
    proof_number = 0
    proof_roles = ch12check.proof_roles(source)
    previous_result: str | None = None
    for record in semantic:
        if record["unit_kind"] != "proof":
            if record["unit_kind"] not in {"section"}:
                previous_result = record["id"]
            continue
        proof_number += 1
        if proof_roles[proof_number - 1] == "hint":
            if previous_result is None:
                raise RuntimeError("Chapter 12 proof hint lacks a preceding result")
            hint_number += 1
            relations.append({
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"{CHAPTER_ID}-REL-HINTS-{hint_number:04d}",
                "relation_type": "hints",
                "from_id": record["id"],
                "to_id": previous_result,
            })
    if hint_number != 8:
        raise RuntimeError(f"Chapter 12 proof-hint count changed: {hint_number}")

    terms, term_mapping = terminology_records(source, target, records["terminology.jsonl"])
    source_terms = common.macro(source, "df")
    target_terms = common.macro(target, "df")
    for number, (source_term, target_term) in enumerate(zip(source_terms, target_terms, strict=True), 1):
        relations.append({
            "schema": SCHEMA,
            "schema_version": VERSION,
            "record_type": "relation",
            "id": f"{CHAPTER_ID}-REL-TERM-{number:04d}",
            "relation_type": "uses_term",
            "from_id": ch01.containing_segment(segments, source_term["start"], "source"),
            "to_id": term_mapping[source_term["argument"]],
            "source_term_tex": source_term["argument"],
            "target_term_tex": target_term["argument"],
            "locale": "id-ID",
        })

    source_indexes = common.macro(source, "index")
    target_indexes = common.macro(target, "index")
    if len(source_indexes) != 102 or len(target_indexes) != 102:
        raise RuntimeError("Chapter 12 index count changed")
    new_index_rows = []
    for number, (source_index, target_index) in enumerate(zip(source_indexes, target_indexes, strict=True), 1):
        new_index_rows.append({
            "id": f"{CHAPTER_ID}-TERM-OCC-{number:04d}",
            "parent_segment_id": ch01.containing_segment(segments, source_index["start"], "source"),
            "source_order": str(number),
            "source_line": str(source_index["line"]),
            "source_index_tex": source_index["argument"],
            "target_line": str(target_index["line"]),
            "target_index_tex": target_index["argument"],
            "source_sha256": sha(source_index["argument"].encode("ascii")),
            "target_sha256": sha(target_index["argument"].encode("utf-8")),
            "locale": "id-ID",
        })

    receipt_sha = ids.get("receipt", {}).get("sha256")
    corrections = correction_records(ledger, ids["ledger"]["sha256"], bind_final, receipt_sha)
    formulas, formula_summary = formula_records(source, target, ledger)
    artifacts = artifact_records(ids, bind_final)
    qa = qa_records(ids, formula_summary, bind_final)
    common_relation = {"schema": SCHEMA, "schema_version": VERSION, "record_type": "relation", "from_id": CHAPTER_ID}
    relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-RIGHTS-0001", "relation_type": "licensed_under", "to_id": RIGHTS})
    for number, artifact in enumerate(artifacts, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-ARTIFACT-{number:04d}", "relation_type": "has_artifact", "to_id": artifact["id"]})
    for number, event in enumerate(qa, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-QA-{number:04d}", "relation_type": "has_qa_event", "to_id": event["id"]})
    for number, correction in enumerate(corrections, 1):
        relations.append(common_relation | {"id": f"{CHAPTER_ID}-REL-CORRECTION-{number:04d}", "relation_type": "documents_correction", "to_id": correction["id"]})

    for segment in segments:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            segment.pop(key, None)
    records["semantic_units.jsonl"].extend(semantic)
    records["segments.jsonl"].extend(segments)
    records["relations.jsonl"].extend(relations)
    records["formula_map.jsonl"].extend(formulas)
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
    outputs["CH12_PREFIX_LOCKS.json"] = lock_bytes
    outputs["BACKEND_MANIFEST.csv"] = manifest_bytes(outputs)
    summary = {
        "unit": CHAPTER_ID,
        "binding_state": "bound" if bind_final else "pending_final_artifact_binding",
        "semantic_units": len(semantic),
        "segments": len(segments),
        "relations": len(relations),
        "formula_maps": len(formulas),
        "index_rows": len(new_index_rows),
        "new_terms": len(terms),
        "corrections": len(corrections),
        "qa_events": len(qa),
        "artifacts": len(artifacts),
        "reference_resolution": dict(resolution_counts),
        "ch11_reconciliation": reconciliation,
        "target_sha256": ids["target"]["sha256"],
    }
    return outputs, summary


def reconciliation_report(summary: dict[str, Any], outputs: dict[str, bytes]) -> bytes:
    names = [
        "units.jsonl", "semantic_units.jsonl", "segments.jsonl", "relations.jsonl",
        "formula_map.jsonl", "exercise_support.jsonl", "index_terms.csv",
        "artifacts.jsonl", "qa_events.jsonl", "corrections.jsonl",
        "terminology.jsonl", "CH12_PREFIX_LOCKS.json", "BACKEND_MANIFEST.csv",
    ]
    if summary["binding_state"] == "bound":
        boundary_line = (
            "Generated from the passing Chapter 12 translation report and the frozen final PDF, "
            "render evidence, deterministic-build result, and admission receipt."
        )
        artifact_line = (
            "- The Chapter 12 PDF byte count, page count, SHA-256 identity, and admission-receipt "
            "identity are bound in the admitted slice."
        )
    else:
        boundary_line = (
            "Generated from the passing Chapter 12 translation report. The final PDF and admission "
            "receipt are deliberately unbound in this boundary; run "
            "`python backend/generate_ch12_backend.py --bind-final-artifacts` only after both are frozen."
        )
        artifact_line = "- No final PDF byte count, page count, or cryptographic hash is present in the pending Chapter 12 slice."
    lines = [
        "# FAOA-2015-CH12 backend reconciliation",
        "",
        boundary_line,
        "",
        f"- Target: `{TARGET_REL}` — {EXPECTED_TARGET[0]} bytes, SHA-256 `{EXPECTED_TARGET[2]}`.",
        f"- Semantic units: {summary['semantic_units']}; segments: {summary['segments']}; relations: {summary['relations']}; formula maps: {summary['formula_maps']}; index rows: {summary['index_rows']}.",
        f"- New terminology records: {summary['new_terms']}; correction records: {summary['corrections']}; QA events: {summary['qa_events']}; artifacts/placeholders: {summary['artifacts']}.",
        f"- Chapter 11 authorized reconciliation: {summary['ch11_reconciliation']}.",
        "- Relation endpoint validation is performed by `backend/validate_ch12_backend.py`.",
        artifact_line,
        "",
        "Generated backend file identities:",
        "",
    ]
    lines.extend(f"- `{name}` — {len(outputs[name])} bytes, SHA-256 `{sha(outputs[name])}`" for name in names)
    return ("\n".join(lines) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind-final-artifacts", action="store_true")
    parser.add_argument("--check", action="store_true", help="compare generated bytes without writing")
    args = parser.parse_args()
    outputs, summary = build_outputs(args.bind_final_artifacts)
    if args.check:
        mismatches = []
        for name, expected in outputs.items():
            path = BACKEND / name
            if not path.is_file() or path.read_bytes() != expected:
                mismatches.append(name)
        if mismatches:
            raise RuntimeError("deterministic backend replay differs: " + ", ".join(mismatches))
        print(json.dumps(summary | {"deterministic_replay": "pass"}, sort_keys=True))
        return
    for name, data in outputs.items():
        (BACKEND / name).write_bytes(data)
    report = reconciliation_report(summary, outputs)
    (ROOT / "qa/CH12_BACKEND_RECONCILIATION.md").write_bytes(report)
    print(json.dumps(summary | {"backend_report": "qa/CH12_BACKEND_RECONCILIATION.md"}, sort_keys=True))


if __name__ == "__main__":
    main()
