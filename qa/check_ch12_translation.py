#!/usr/bin/env python3
"""Bounded structural, mathematical, provenance, and residue audit for CH12."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qa"))
sys.path.insert(0, str(ROOT / "backend"))
import check_ch05_translation as common  # noqa: E402
import check_ch09_translation as ch09  # noqa: E402
import check_ch10_translation as ch10  # noqa: E402
import ch03_math  # noqa: E402


SOURCE = ROOT / "source" / "upstream" / "no_identity.tex"
TARGET = ROOT / "source" / "id-ID" / "no_identity-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch12.tex"
CORRECTIONS = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH12.json"
MODEL_PROVENANCE = ROOT / "provenance" / "TRANSLATION_MODEL_PROVENANCE.md"
README = ROOT / "README.md"
REPORT = ROOT / "qa" / "ch12-translation-report.json"

UNIT_ID = "FAOA-2015-CH12"
SOURCE_BYTES = 47_994
SOURCE_RECORDS = 1_158
SOURCE_SHA256 = "8da3ffa45bcc07cbe1897a09f309db51e1c5c38080459ffb1f6947bf45a20b6c"
MODEL_ID = ch10.MODEL_ID

EXPECTED_CHAPTER_TITLE = "BERTAHAN TANPA IDENTITAS"
EXPECTED_SECTION_TITLES = [
    "Unitalisasi Aljabar Banach",
    "Barisan Eksak dan Ekstensi",
    "Unitalisasi Aljabar-$C^*$",
    "Kuasi-Invers",
    "Elemen Positif dalam Aljabar-$C^*$",
    "Identitas Aproksimatif",
]
EXPECTED_BEGIN_COUNTS = {
    "align*": 2,
    "array": 1,
    "bmatrix": 6,
    "conv": 1,
    "cor": 11,
    "defn": 17,
    "enumerate": 9,
    "equation": 5,
    "exam": 10,
    "lem": 2,
    "notn": 2,
    "proof": 12,
    "prop": 71,
    "thm": 5,
}
EXPECTED_MASTER_INCLUDES = (
    "linalg-id",
    "categories-id",
    "normlinspaces-id",
    "Hilbert_spaces-id",
    "Hilbert_space_operators-id",
    "Banach_spaces-id",
    "compact_operators-id",
    "spectrum-id",
    "topvecspaces-id",
    "distributions-id",
    "Gelfand_Naimark-id",
    "no_identity-id",
)
MASTER_ANCHORS = (
    "Unit Pembaca Kumulatif Bab 1--12",
    "batas produksi Bab 1--12",
    "Bab 1 sampai Bab 12",
    "Creative Commons",
    "Attribution--ShareAlike 4.0 International",
    "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University",
    "DIAGXY.TEX",
    "status komponennya tidak cukup jelas tidak digunakan",
    MODEL_ID,
)
FORBIDDEN_MASTER_COMPONENTS = (
    r"\input{TABLE.TEX}",
    "by-sa.eps",
    "by-sa.pdf",
    "Wiener_quote.tex",
)
PRIVATE_RESIDUE = tuple(ch10.PRIVATE_RESIDUE) + (
    "codex://",
    "github tokens",
    "zenodo token",
)
MOJIBAKE = tuple(ch10.MOJIBAKE)
PLACEHOLDER_RE = re.compile(
    r"(?i)(?:\b(?:todo|tbd|fixme|placeholder|lorem ipsum)\b|"
    r"\[\s*(?:translate|translation pending|isi nanti)\s*\]|"
    r"<\s*(?:translate|placeholder)\s*>|\?\?\?)"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_summary(path: Path, data: bytes) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "lf": data.count(b"\n"),
        "sha256": sha256(data),
    }


def write_report(report: dict[str, Any]) -> None:
    REPORT.write_bytes(
        (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


def source_identity_errors(data: bytes) -> list[str]:
    errors: list[str] = []
    if len(data) != SOURCE_BYTES:
        errors.append(f"source byte count differs: {len(data)} != {SOURCE_BYTES}")
    if sha256(data) != SOURCE_SHA256:
        errors.append("source SHA-256 differs")
    if data.count(b"\r\n") != SOURCE_RECORDS:
        errors.append("source CRLF record count differs")
    if data.replace(b"\r\n", b"").find(b"\r") >= 0:
        errors.append("source contains a lone CR")
    if data.replace(b"\r\n", b"").find(b"\n") >= 0:
        errors.append("source contains a lone LF")
    if not data.endswith(b"\r\n"):
        errors.append("source lacks its terminal CRLF")
    if data.startswith(b"\xef\xbb\xbf") or b"\x00" in data:
        errors.append("source contains a BOM or NUL")
    try:
        data.decode("ascii")
    except UnicodeDecodeError as exc:
        errors.append(f"source is not 7-bit ASCII: {exc}")
    return errors


def decode_lf_utf8(name: str, data: bytes, errors: list[str]) -> str:
    if data.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{name} has a UTF-8 BOM")
    if b"\r" in data:
        errors.append(f"{name} is not LF-only")
    if b"\x00" in data:
        errors.append(f"{name} contains NUL")
    if not data.endswith(b"\n"):
        errors.append(f"{name} lacks a terminal LF")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{name} is not strict UTF-8: {exc}")
        return data.decode("utf-8", errors="replace")


def identity_record_count(identity: dict[str, Any]) -> Any:
    for key in ("logical_records", "lines", "lf"):
        if key in identity:
            return identity[key]
    return None


def validate_identity_binding(
    name: str,
    identity: Any,
    expected_path: str,
    data: bytes,
    errors: list[str],
) -> None:
    if not isinstance(identity, dict):
        errors.append(f"correction ledger {name} identity is absent")
        return
    if identity.get("path") != expected_path:
        errors.append(f"correction ledger {name} path binding differs")
    if identity.get("bytes") != len(data):
        errors.append(f"correction ledger {name} byte binding differs")
    if identity.get("sha256") != sha256(data):
        errors.append(f"correction ledger {name} SHA-256 binding differs")
    if identity_record_count(identity) != data.count(b"\n"):
        errors.append(f"correction ledger {name} record binding differs")


def source_range(record: dict[str, Any]) -> tuple[int, int] | None:
    value = record.get("source_lines")
    if not isinstance(value, dict):
        return None
    start, end = value.get("start"), value.get("end")
    if not isinstance(start, int) or not isinstance(end, int) or not (1 <= start <= end):
        return None
    return start, end


def explicit_reference_repairs(
    records: list[dict[str, Any]], source: str, target: str, errors: list[str]
) -> bool:
    """Validate ledger coverage for the three known bad reference targets.

    Return whether the prose reference at source line 247 is explicitly allowed to
    become an equation reference.
    """

    repair_lines = (226, 240, 247)
    covered: set[int] = set()
    third_to_eqref = False
    for record in records:
        span = source_range(record)
        if span is None:
            continue
        forbidden = record.get("forbidden_source_anchor", "")
        required = record.get("required_target_anchor", "")
        if not isinstance(forbidden, str) or not isinstance(required, str):
            continue
        if "001500202i" not in forbidden or "001500202i2" not in required:
            continue
        for line in repair_lines:
            if span[0] <= line <= span[1]:
                covered.add(line)
        if span[0] <= 247 <= span[1]:
            third_to_eqref = (
                r"\ref{001500202i}" in forbidden
                and r"\eqref{001500202i2}" in required
            )
    if covered != set(repair_lines):
        errors.append(
            "correction ledger does not separately anchor all three "
            "001500202i -> 001500202i2 repairs"
        )
    if source.count("001500202i") != 4:
        errors.append("locked source reference/label typo surface differs")
    if target.count("001500202i2") < 4:
        errors.append("target lacks the repaired reference/label anchors")
    return third_to_eqref


def validate_correction_ledger(
    ledger_bytes: bytes,
    source_bytes: bytes,
    target_bytes: bytes,
    source: str,
    target: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    try:
        ledger = json.loads(ledger_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, [], [f"source-correction ledger cannot be decoded: {exc}"]
    if not isinstance(ledger, dict):
        return {}, [], ["source-correction ledger root is not an object"]
    if ledger.get("schema_version") != "o008.source-corrections.v1":
        errors.append("source-correction ledger schema differs")
    if ledger.get("unit_id") != UNIT_ID or ledger.get("chapter") != 12:
        errors.append("source-correction ledger unit identity differs")
    if ledger.get("status") != "adjudicated_and_applied":
        errors.append("source-correction ledger is not adjudicated_and_applied")
    validate_identity_binding(
        "source",
        ledger.get("source"),
        "source/upstream/no_identity.tex",
        source_bytes,
        errors,
    )
    validate_identity_binding(
        "target",
        ledger.get("target"),
        "source/id-ID/no_identity-id.tex",
        target_bytes,
        errors,
    )
    source_identity = ledger.get("source", {})
    if isinstance(source_identity, dict) and source_identity.get("line_endings") != "CRLF":
        errors.append("correction ledger source line-ending binding differs")
    target_identity = ledger.get("target", {})
    if isinstance(target_identity, dict) and target_identity.get("line_endings") != "LF":
        errors.append("correction ledger target line-ending binding differs")

    raw_records = ledger.get("records")
    records = raw_records if isinstance(raw_records, list) else []
    if not isinstance(raw_records, list):
        errors.append("source-correction ledger records are absent")
    if ledger.get("record_count") != len(records):
        errors.append("source-correction ledger record_count differs")
    seen_ids: set[str] = set()
    for ordinal, value in enumerate(records, 1):
        if not isinstance(value, dict):
            errors.append(f"correction record {ordinal} is not an object")
            continue
        record_id = value.get("id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"correction record {ordinal} has no id")
        elif record_id in seen_ids:
            errors.append(f"duplicate correction record id: {record_id}")
        else:
            seen_ids.add(record_id)
        span = source_range(value)
        if span is None or span[1] > SOURCE_RECORDS:
            errors.append(f"invalid source range in correction record {record_id!r}")
        required = value.get("required_target_anchor")
        forbidden = value.get("forbidden_source_anchor")
        if not isinstance(required, str) or not required or required not in target:
            errors.append(f"required target anchor absent: {record_id!r}")
        if not isinstance(forbidden, str) or not forbidden or forbidden not in source:
            errors.append(f"forbidden source anchor absent from source: {record_id!r}")
        elif forbidden in target:
            errors.append(f"forbidden source anchor survives in target: {record_id!r}")
    return ledger, [item for item in records if isinstance(item, dict)], errors


def proof_roles(text: str) -> list[str]:
    active = common.shared.active_same_length(text)
    pattern = re.compile(r"\\begin\{proof\}(?:\[([^\]]*)\])?(.*?)\\end\{proof\}", re.S)
    roles: list[str] = []
    for match in pattern.finditer(active):
        title = match.group(1) or ""
        body = match.group(2)
        hint = bool(
            re.search(
                r"(?i)(?:Hint for proof|Petunjuk untuk (?:bukti|pembuktian)|"
                r"Petunjuk (?:bukti|pembuktian)|\\emph\{Hint\.\}|"
                r"\\emph\{Petunjuk\.\})",
                title + "\n" + body,
            )
        )
        citation_only = bool(
            not hint
            and re.match(r"\s*(?:See|Lihat)\b", body)
            and re.search(r"\\cite\{", body)
        )
        roles.append("hint" if hint else "citation_only" if citation_only else "plain")
    return roles


def math_ledger_ranges(records: list[dict[str, Any]]) -> list[tuple[int, int]]:
    output: list[tuple[int, int]] = []
    for record in records:
        classification = str(record.get("classification", "")).upper()
        affects_math = record.get("affects_math") is True
        category = str(record.get("category", "")).lower()
        if "MATHEMATICAL" in classification or affects_math or category == "math":
            span = source_range(record)
            if span is not None:
                output.append(span)
    return output


def edit_source_lines(
    edit: tuple[Any, ...], source_math: list[dict[str, Any]]
) -> set[int]:
    _, first, last, *_ = edit
    if first <= last:
        selected = source_math[first - 1 : last]
    else:
        neighbor = min(max(first - 1, 0), len(source_math) - 1)
        selected = source_math[neighbor : neighbor + 1]
    lines: set[int] = set()
    for item in selected:
        lines.update(range(item["line_start"], item["line_end"] + 1))
    return lines


def validate_math_deltas(
    source_math: list[dict[str, Any]],
    target_math: list[dict[str, Any]],
    records: list[dict[str, Any]],
    errors: list[str],
) -> list[tuple[Any, ...]]:
    edits = ch09.math_edit_signature(source_math, target_math)
    # SequenceMatcher can express one unchanged surface that moved by a
    # single ordinal as an adjacent insertion/deletion pair. Cancel only
    # exact normalized multisets across such a pair; every genuine change
    # remains subject to the line-bounded correction ledger below.
    filtered: list[tuple[Any, ...]] = []
    index = 0
    while index < len(edits):
        current = edits[index]
        if (
            index + 1 < len(edits)
            and {current[0], edits[index + 1][0]} == {"insert", "delete"}
        ):
            pair = (current, edits[index + 1])
            inserted = next(item for item in pair if item[0] == "insert")
            deleted = next(item for item in pair if item[0] == "delete")
            inserted_values = Counter(
                item["normalized"]
                for item in target_math[inserted[3] - 1 : inserted[4]]
            )
            deleted_values = Counter(
                item["normalized"]
                for item in source_math[deleted[1] - 1 : deleted[2]]
            )
            if inserted_values == deleted_values:
                index += 2
                continue
        filtered.append(current)
        index += 1
    edits = filtered
    allowed_ranges = math_ledger_ranges(records)
    allowed_lines = {
        line for start, end in allowed_ranges for line in range(start, end + 1)
    }
    uncovered = []
    for edit in edits:
        lines = edit_source_lines(edit, source_math)
        if not lines.intersection(allowed_lines):
            uncovered.append(
                {
                    "tag": edit[0],
                    "source_ordinals": [edit[1], edit[2]],
                    "source_lines": sorted(lines),
                }
            )
    if uncovered:
        errors.append(f"math deltas lack correction-ledger coverage: {uncovered!r}")
    return edits


def main() -> int:
    source_errors: list[str] = []
    if not SOURCE.exists():
        report = {
            "schema_version": "o008.ch12-translation-report.v1",
            "unit_id": UNIT_ID,
            "status": "fail",
            "errors": [f"locked source absent: {SOURCE.relative_to(ROOT).as_posix()}"],
        }
        write_report(report)
        return 2
    source_bytes = SOURCE.read_bytes()
    source_errors.extend(source_identity_errors(source_bytes))
    missing = [
        path.relative_to(ROOT).as_posix()
        for path in (TARGET, MASTER, CORRECTIONS)
        if not path.exists()
    ]
    if missing:
        report = {
            "schema_version": "o008.ch12-translation-report.v1",
            "unit_id": UNIT_ID,
            "status": "fail" if source_errors else "waiting",
            "reason": "production inputs are not complete",
            "missing": missing,
            "source": file_summary(SOURCE, source_bytes),
            "report_path": REPORT.relative_to(ROOT).as_posix(),
            "errors": source_errors,
        }
        write_report(report)
        return 2

    errors = list(source_errors)
    target_bytes = TARGET.read_bytes()
    master_bytes = MASTER.read_bytes()
    ledger_bytes = CORRECTIONS.read_bytes()
    source = source_bytes.decode("ascii")
    target = decode_lf_utf8("target", target_bytes, errors)
    master = decode_lf_utf8("master", master_bytes, errors)
    decode_lf_utf8("source-correction ledger", ledger_bytes, errors)

    ledger, correction_records, correction_errors = validate_correction_ledger(
        ledger_bytes, source_bytes, target_bytes, source, target
    )
    errors.extend(correction_errors)

    try:
        chapter, sections = common.chapter_and_sections(target)
    except ValueError as exc:
        chapter, sections = "", []
        errors.append(f"chapter/section parse failed: {exc}")
    if chapter != EXPECTED_CHAPTER_TITLE:
        errors.append(f"chapter title differs: {chapter!r}")
    if sections != EXPECTED_SECTION_TITLES:
        errors.append(f"six id-ID section headings differ: {sections!r}")
    if common.command_arguments(target, "subsection") or common.command_arguments(
        target, "subsubsection"
    ):
        errors.append("unexpected subsection or lower heading")

    source_env = common.env_sequence(source)
    target_env = common.env_sequence(target)
    if source_env != target_env:
        errors.append("ordered begin/end environment topology differs")
    errors.extend(ch09.environment_stack_errors(target_env))
    source_begins = [name for action, name in source_env if action == "begin"]
    target_begins = [name for action, name in target_env if action == "begin"]
    if len(source_begins) != 154 or len(target_begins) != 154:
        errors.append(
            f"environment begin count differs: {len(source_begins)}/{len(target_begins)}"
        )
    if len(target_env) != 308:
        errors.append(f"environment begin/end token count differs: {len(target_env)}")
    begin_counts = dict(sorted(Counter(target_begins).items()))
    if begin_counts != EXPECTED_BEGIN_COUNTS:
        errors.append(f"environment opening census differs: {begin_counts!r}")
    if ch09.begin_shape_sequence(source) != ch09.begin_shape_sequence(target):
        errors.append("begin-control shape topology differs")

    source_labels = common.command_arguments(source, "label")
    target_labels = common.command_arguments(target, "label")
    if len(source_labels) != 65 or len(set(source_labels)) != 65:
        errors.append("locked source label census differs")
    if target_labels != source_labels:
        errors.append("ordered target label sequence differs from source")
    if len(target_labels) != 65 or len(set(target_labels)) != 65:
        errors.append("target must contain exactly 65 unique labels")

    source_refs = [(kind, value) for _, kind, value in common.reference_sequence(source)]
    target_refs = [(kind, value) for _, kind, value in common.reference_sequence(target)]
    allow_third_eqref = explicit_reference_repairs(
        correction_records, source, target, errors
    )
    expected_refs = [
        (kind, "001500202i2" if value == "001500202i" else value)
        for kind, value in source_refs
    ]
    if allow_third_eqref:
        repaired_positions = [
            index
            for index, (_, value) in enumerate(source_refs)
            if value == "001500202i"
        ]
        if len(repaired_positions) == 3:
            index = repaired_positions[2]
            expected_refs[index] = ("eqref", "001500202i2")
    if len(source_refs) != 46 or len(target_refs) != 46:
        errors.append(f"reference count differs: {len(source_refs)}/{len(target_refs)}")
    if target_refs != expected_refs:
        errors.append(
            "reference sequence differs beyond the three adjudicated "
            "001500202i -> 001500202i2 repairs"
        )

    source_cites = common.command_arguments(source, "cite")
    target_cites = common.command_arguments(target, "cite")
    if len(source_cites) != 17 or len(target_cites) != 17 or target_cites != source_cites:
        errors.append("ordered 17-citation sequence differs")

    source_indexes = common.command_arguments(source, "index")
    target_indexes = common.command_arguments(target, "index")
    source_index_shapes = [common.index_signature(item) for item in source_indexes]
    target_index_shapes = [common.index_signature(item) for item in target_indexes]
    if len(source_indexes) != 102 or len(target_indexes) != 102:
        errors.append(f"index count differs: {len(source_indexes)}/{len(target_indexes)}")
    if target_index_shapes != source_index_shapes:
        errors.append("ordered MakeIndex operator-shape sequence differs")

    source_df = common.command_arguments(source, "df")
    target_df = common.command_arguments(target, "df")
    if len(source_df) != 42 or len(target_df) != 42:
        errors.append(f"defined-term count differs: {len(source_df)}/{len(target_df)}")

    try:
        source_math = ch03_math.extract_math(source, "ascii")
        target_math = ch03_math.extract_math(target, "utf-8")
    except ValueError as exc:
        source_math, target_math = [], []
        errors.append(f"math extraction failed: {exc}")
    if len(source_math) != 927 or len(target_math) != 931:
        errors.append(
            "math-surface count differs from the robust extractor lock: "
            f"{len(source_math)}/{len(target_math)}"
        )
    math_edits = validate_math_deltas(
        source_math, target_math, correction_records, errors
    ) if source_math and target_math else []

    source_roles = proof_roles(source)
    target_roles = proof_roles(target)
    expected_role_counts = Counter({"hint": 8, "citation_only": 2, "plain": 2})
    if len(source_roles) != 12 or Counter(source_roles) != expected_role_counts:
        errors.append(f"locked source proof roles differ: {source_roles!r}")
    if len(target_roles) != 12 or Counter(target_roles) != expected_role_counts:
        errors.append(f"target proof roles differ: {target_roles!r}")
    if target_roles != source_roles:
        errors.append("ordered proof-role topology differs")
    exercise_envs = sum(
        target.count(rf"\begin{{{name}}}")
        for name in ("exer", "exercise", "exercises", "problem", "problems")
    )
    if exercise_envs:
        errors.append(f"unexpected exercise/problem environments: {exercise_envs}")
    if any(
        rf"\begin{{{name}}}" in target
        for name in ("answer", "answers", "solution", "solutions")
    ):
        errors.append("unprovenanced answer or solution surface present")

    try:
        residue = common.visible_residue(target, target_math)
    except Exception as exc:  # keep audit failures reportable rather than traceback-only
        residue = []
        errors.append(f"English-residue scan failed: {exc}")
    if residue:
        errors.append(f"visible English residue: {residue!r}")
    for marker in MOJIBAKE:
        if marker in target:
            errors.append(f"mojibake marker present: {marker!r}")
    active = common.shared.active_same_length(target)
    active_lower = active.lower()
    for marker in PRIVATE_RESIDUE:
        if marker.lower() in active_lower:
            errors.append(f"private-path residue present: {marker}")
    placeholders = [
        {"line": active.count("\n", 0, match.start()) + 1, "text": match.group(0)}
        for match in PLACEHOLDER_RE.finditer(active)
    ]
    if placeholders:
        errors.append(f"placeholder residue present: {placeholders!r}")
    if target.count(r"\endinput") != 1 or target.rstrip().splitlines()[-1] != r"\endinput":
        errors.append("endinput is not the sole final nonblank record")

    master_includes = tuple(common.command_arguments(master, "include"))
    if master_includes != EXPECTED_MASTER_INCLUDES:
        errors.append(f"master Chapter 1--12 include order differs: {master_includes!r}")
    for anchor in MASTER_ANCHORS:
        if anchor not in master:
            errors.append(f"master rights/model anchor absent: {anchor!r}")
    for forbidden in FORBIDDEN_MASTER_COMPONENTS:
        if forbidden.lower() in master.lower():
            errors.append(f"excluded component is active in master: {forbidden}")

    for path, label in (
        (README, "README"),
        (MODEL_PROVENANCE, "translation model provenance"),
    ):
        if not path.exists():
            errors.append(f"{label} file absent")
            continue
        try:
            credit_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{label} is not UTF-8: {exc}")
            continue
        if MODEL_ID not in credit_text:
            errors.append(f"explicit model credit absent from {label}")

    report = {
        "schema_version": "o008.ch12-translation-report.v1",
        "unit_id": UNIT_ID,
        "status": "pass" if not errors else "fail",
        "report_path": REPORT.relative_to(ROOT).as_posix(),
        "source": file_summary(SOURCE, source_bytes),
        "target": file_summary(TARGET, target_bytes),
        "master": file_summary(MASTER, master_bytes),
        "source_correction_ledger": {
            **file_summary(CORRECTIONS, ledger_bytes),
            "record_count": len(correction_records),
            "declared_status": ledger.get("status"),
        },
        "counts": {
            "sections": len(sections),
            "environment_begins": len(target_begins),
            "environment_tokens": len(target_env),
            "labels": len(target_labels),
            "references": len(target_refs),
            "citations": len(target_cites),
            "indexes": len(target_indexes),
            "defined_terms": len(target_df),
            "math_surfaces": len(target_math),
            "classified_math_edit_blocks": len(math_edits),
            "proofs": len(target_roles),
            "proof_hints": Counter(target_roles)["hint"],
            "citation_only_proofs": Counter(target_roles)["citation_only"],
            "exercises_or_problems": exercise_envs,
            "visible_english_residue": len(residue),
            "placeholders": len(placeholders),
        },
        "digests": {
            "environment_topology": ch09.sequence_sha256(target_env),
            "labels": ch09.sequence_sha256(target_labels),
            "references": ch09.sequence_sha256(target_refs),
            "citations": ch09.sequence_sha256(target_cites),
            "index_shapes": ch09.sequence_sha256(target_index_shapes),
            "math_records": ch09.sequence_sha256(ch09.math_records(target_math)),
            "math_edits": ch09.sequence_sha256(math_edits),
            "proof_roles": ch09.sequence_sha256(target_roles),
        },
        "model_id": MODEL_ID,
        "errors": errors,
    }
    write_report(report)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
