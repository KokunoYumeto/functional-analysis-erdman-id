#!/usr/bin/env python3
"""Generate deterministic, locale-neutral Chapter 1 backend projections.

The source authority remains immutable.  Generated records contain locators and
hashes, not rewritten source content.  Run from any working directory.
"""

from __future__ import annotations

import csv
import difflib
import hashlib
import io
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SOURCE_PATH = ROOT / "source" / "upstream" / "linalg.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "linalg-id.tex"
SOURCE_ENCODING = "ascii"
TARGET_ENCODING = "utf-8"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH01"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"

SEMANTIC_ENVS = {
    "conv",
    "defn",
    "notn",
    "thm",
    "lem",
    "prop",
    "cor",
    "fact",
    "exam",
    "exer",
    "prob",
    "proj",
    "proof",
    "cau",
}
MATH_ENVS = {
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "eqnarray",
    "eqnarray*",
    "displaymath",
    "math",
    "CD",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump_jsonl(path: Path, records: list[dict]) -> None:
    payload = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    )
    path.write_text(payload, encoding="utf-8", newline="\n")


def active_same_length(text: str) -> str:
    """Blank TeX comments while retaining every offset and newline."""
    chars = list(text)
    escaped = False
    in_comment = False
    for i, char in enumerate(chars):
        if char in "\r\n":
            in_comment = False
            escaped = False
            continue
        if in_comment:
            chars[i] = " "
            continue
        if char == "%" and not escaped:
            chars[i] = " "
            in_comment = True
            continue
        if char == "\\":
            escaped = not escaped
        else:
            escaped = False
    return "".join(chars)


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def balanced_end(text: str, open_brace: int) -> int:
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == "{" and (i == 0 or text[i - 1] != "\\"):
            depth += 1
        elif text[i] == "}" and (i == 0 or text[i - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError(f"unclosed brace at offset {open_brace}")


def macro_occurrences(text: str, macro: str) -> list[dict]:
    active = active_same_length(text)
    needle = "\\" + macro
    out: list[dict] = []
    cursor = 0
    while True:
        start = active.find(needle, cursor)
        if start < 0:
            break
        brace = active.find("{", start + len(needle))
        if brace < 0:
            break
        end = balanced_end(active, brace)
        out.append(
            {
                "start": start,
                "end": end,
                "argument": text[brace + 1 : end - 1],
                "line": line_of(text, start),
            }
        )
        cursor = end
    return out


def first_label(raw: str) -> str | None:
    labels = macro_occurrences(raw, "label")
    return labels[0]["argument"] if labels else None


def command_title(raw: str, command: str) -> str:
    active = active_same_length(raw)
    start = active.find("\\" + command)
    brace = active.find("{", start)
    end = balanced_end(active, brace)
    return raw[brace + 1 : end - 1].strip()


def optional_env_title(raw: str) -> str | None:
    begin_end = raw.find("}")
    if begin_end < 0:
        return None
    rest = raw[begin_end + 1 :].lstrip()
    if not rest.startswith("["):
        return None
    close = rest.find("]")
    return rest[1:close].strip() if close >= 0 else None


def parse_anchors(text: str) -> list[dict]:
    active = active_same_length(text)
    anchors: list[dict] = []
    for command in ("chapter", "section"):
        for match in re.finditer(r"\\" + command + r"\s*\{", active):
            brace = active.find("{", match.start())
            end = balanced_end(active, brace)
            anchors.append(
                {
                    "anchor_type": command,
                    "start": match.start(),
                    "end": end,
                    "line_start": line_of(text, match.start()),
                    "line_end": line_of(text, end - 1),
                    "title": text[brace + 1 : end - 1].strip(),
                    "label": None,
                }
            )

    token_re = re.compile(r"\\(begin|end)\{([^}]+)\}")
    stack: list[tuple[str, int, int]] = []
    for match in token_re.finditer(active):
        action, env = match.group(1), match.group(2)
        if action == "begin":
            stack.append((env, match.start(), match.end()))
            continue
        if not stack or stack[-1][0] != env:
            raise ValueError(f"environment stack mismatch at line {line_of(text, match.start())}")
        begin_env, start, begin_end = stack.pop()
        if begin_env in SEMANTIC_ENVS:
            end = match.end()
            raw = text[start:end]
            anchors.append(
                {
                    "anchor_type": "environment",
                    "environment": begin_env,
                    "start": start,
                    "end": end,
                    "line_start": line_of(text, start),
                    "line_end": line_of(text, end - 1),
                    "title": optional_env_title(raw),
                    "label": first_label(raw),
                }
            )
    if stack:
        raise ValueError("unclosed TeX environment")
    anchors.sort(key=lambda item: (item["start"], -item["end"]))
    for left, right in zip(anchors, anchors[1:]):
        if right["start"] < left["end"]:
            raise ValueError("nested semantic anchors are not supported")
    return anchors


def anchor_signature(anchor: dict) -> tuple[str, str | None]:
    return anchor["anchor_type"], anchor.get("environment")


def fragment(text: str, start: int, end: int, encoding: str) -> dict:
    raw = text[start:end]
    return {
        "line_start": line_of(text, start),
        "line_end": line_of(text, max(start, end - 1)),
        "bytes": len(raw.encode(encoding)),
        "sha256": sha(raw.encode(encoding)),
    }


def containing_segment(segments: list[dict], offset: int, side: str) -> str:
    start_key = "_source_start" if side == "source" else "_target_start"
    end_key = "_source_end" if side == "source" else "_target_end"
    candidates = [s for s in segments if s[start_key] <= offset < s[end_key]]
    if not candidates:
        raise ValueError(f"no {side} segment contains offset {offset}")
    return min(candidates, key=lambda s: s[end_key] - s[start_key])["id"]


def extract_math(text: str, encoding: str) -> list[dict]:
    active = active_same_length(text)
    chunks: list[dict] = []
    i = 0
    while i < len(active):
        content_start = content_end = end = None
        delimiter = None
        if active.startswith("\\[", i):
            content_start = i + 2
            content_end = active.find("\\]", content_start)
            end = content_end + 2
            delimiter = "bracket-display"
        elif active.startswith("\\(", i):
            content_start = i + 2
            content_end = active.find("\\)", content_start)
            end = content_end + 2
            delimiter = "paren-inline"
        elif active.startswith("\\begin{", i):
            brace_end = active.find("}", i + 7)
            env = active[i + 7 : brace_end]
            if env in MATH_ENVS:
                close = "\\end{" + env + "}"
                content_start = brace_end + 1
                content_end = active.find(close, content_start)
                end = content_end + len(close)
                delimiter = "environment:" + env
        elif active[i] == "$" and (i == 0 or active[i - 1] != "\\"):
            marker = "$$" if active.startswith("$$", i) else "$"
            content_start = i + len(marker)
            content_end = content_start
            while True:
                content_end = active.find(marker, content_end)
                if content_end < 0 or active[content_end - 1] != "\\":
                    break
                content_end += len(marker)
            end = content_end + len(marker)
            delimiter = "dollar-display" if marker == "$$" else "dollar-inline"
        if content_start is None:
            i += 1
            continue
        if content_end is None or content_end < 0 or end is None:
            raise ValueError(f"unclosed math surface at line {line_of(text, i)}")
        raw = text[content_start:content_end]
        chunks.append(
            {
                "start": i,
                "end": end,
                "line_start": line_of(text, i),
                "line_end": line_of(text, end - 1),
                "delimiter": delimiter,
                "bytes": len(raw.encode(encoding)),
                "sha256": sha(raw.encode(encoding)),
                "normalized_sha256": sha(re.sub(r"\s+", "", raw).encode(encoding)),
                "normalized": re.sub(r"\s+", "", raw),
            }
        )
        i = end
    return chunks


def main() -> None:
    source_bytes = SOURCE_PATH.read_bytes()
    target_bytes = TARGET_PATH.read_bytes()
    source = source_bytes.decode(SOURCE_ENCODING)
    target = target_bytes.decode(TARGET_ENCODING)
    if sha(source_bytes) != "a15cabf306adf5457cedce046f98b9474c72b38ab50197b0dc4288e942772096":
        raise ValueError("source authority hash changed")
    if sha(target_bytes) != "4ab3098cab358f425190bfe6defa20d3ec7b2a81653e0e61bbfa67e497e2654d":
        raise ValueError("admitted target hash changed")

    source_anchors = parse_anchors(source)
    target_anchors = parse_anchors(target)
    if [anchor_signature(a) for a in source_anchors] != [anchor_signature(a) for a in target_anchors]:
        raise ValueError("source/target anchor topology differs")
    if len(source_anchors) != 128:
        raise ValueError(f"expected 128 anchors, found {len(source_anchors)}")

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
            sfrag = fragment(source, source_anchor["start"], source_anchor["end"], SOURCE_ENCODING)
            tfrag = fragment(target, target_anchor["start"], target_anchor["end"], TARGET_ENCODING)
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
                    "source_path": "source/upstream/linalg.tex",
                    "source_line_start": sfrag["line_start"],
                    "source_line_end": sfrag["line_end"],
                    "source_fragment_sha256": sfrag["sha256"],
                    "target_path": "source/id-ID/linalg-id.tex",
                    "target_line_start": tfrag["line_start"],
                    "target_line_end": tfrag["line_end"],
                    "target_fragment_sha256": tfrag["sha256"],
                    "source_local_id": source_anchor.get("label"),
                    "source_title_tex": source_anchor.get("title"),
                    "target_title_tex": target_anchor.get("title"),
                    "locale": "id-ID",
                    "translation_state": "admitted",
                    "rights_id": RIGHTS,
                }
            )
            relations.append(
                {
                    "schema": SCHEMA,
                    "schema_version": VERSION,
                    "record_type": "relation",
                    "id": f"FAOA-2015-CH01-REL-CONTAINS-{len(relations)+1:04d}",
                    "relation_type": "contains",
                    "from_id": parent_id,
                    "to_id": unit_id,
                }
            )

    # Build a complete reader-facing segment map from anchors and the gaps
    # between them.  The exact anchor topology makes each source/target gap a
    # deterministic translation pair without relying on page numbers.
    source_parts: list[tuple[int, int, str, str]] = []
    target_parts: list[tuple[int, int, str, str]] = []
    previous_source = previous_target = 0
    previous_parent = CHAPTER_ID
    for index, (sa, ta, unit_id) in enumerate(zip(source_anchors, target_anchors, anchor_ids)):
        if sa["start"] > previous_source or ta["start"] > previous_target:
            sraw = active_same_length(source[previous_source : sa["start"]]).strip()
            traw = active_same_length(target[previous_target : ta["start"]]).strip()
            if sraw or traw:
                source_parts.append((previous_source, sa["start"], "prose", previous_parent))
                target_parts.append((previous_target, ta["start"], "prose", previous_parent))
        role = "title" if sa["anchor_type"] in {"chapter", "section"} else "semantic_environment"
        source_parts.append((sa["start"], sa["end"], role, unit_id))
        target_parts.append((ta["start"], ta["end"], role, unit_id))
        previous_source, previous_target = sa["end"], ta["end"]
        previous_parent = current_section_by_anchor[index]
    if previous_source < len(source) or previous_target < len(target):
        sraw = active_same_length(source[previous_source:]).strip()
        traw = active_same_length(target[previous_target:]).strip()
        if sraw or traw:
            source_parts.append((previous_source, len(source), "prose", previous_parent))
            target_parts.append((previous_target, len(target), "prose", previous_parent))
    if len(source_parts) != len(target_parts):
        raise ValueError("source/target segment count differs")

    for number, (source_part, target_part) in enumerate(zip(source_parts, target_parts), 1):
        ss, se, role, parent_id = source_part
        ts, te, target_role, target_parent = target_part
        if role != target_role or parent_id != target_parent:
            raise ValueError("source/target segment role differs")
        segment_id = f"{CHAPTER_ID}-SEG-{number:04d}"
        sfrag = fragment(source, ss, se, SOURCE_ENCODING)
        tfrag = fragment(target, ts, te, TARGET_ENCODING)
        segment_records.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "segment",
                "id": segment_id,
                "parent_id": parent_id,
                "order": number,
                "segment_role": role,
                "source_path": "source/upstream/linalg.tex",
                "source_line_start": sfrag["line_start"],
                "source_line_end": sfrag["line_end"],
                "source_bytes": sfrag["bytes"],
                "source_sha256": sfrag["sha256"],
                "target_path": "source/id-ID/linalg-id.tex",
                "target_line_start": tfrag["line_start"],
                "target_line_end": tfrag["line_end"],
                "target_bytes": tfrag["bytes"],
                "target_sha256": tfrag["sha256"],
                "source_edition_id": EDITION,
                "target_edition_id": TARGET_EDITION,
                "locale": "id-ID",
                "translation_state": "admitted",
                "rights_id": RIGHTS,
                "_source_start": ss,
                "_source_end": se,
                "_target_start": ts,
                "_target_end": te,
            }
        )
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"FAOA-2015-CH01-REL-TRANSLATES-{number:04d}",
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
                    "id": f"FAOA-2015-CH01-REL-PRECEDES-{number-1:04d}",
                    "relation_type": "precedes",
                    "from_id": f"{CHAPTER_ID}-SEG-{number-1:04d}",
                    "to_id": segment_id,
                }
            )

    # References and citations are taken from source authority.  Two references
    # intentionally point into later chapters and are represented by futurexref
    # in the standalone Indonesian Unit 1 wrapper.
    for number, occurrence in enumerate(macro_occurrences(source, "ref"), 1):
        label = occurrence["argument"]
        target_id = label_to_id.get(label, f"ERDMAN-FAOA-2015-LABEL-{label}")
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"FAOA-2015-CH01-REL-XREF-{number:04d}",
                "relation_type": "xref",
                "from_id": containing_segment(segment_records, occurrence["start"], "source"),
                "to_id": target_id,
                "source_local_id": label,
                "resolution": "local" if label in label_to_id else "pending_later_source_unit",
            }
        )
    for number, occurrence in enumerate(macro_occurrences(source, "cite"), 1):
        for key in [item.strip() for item in occurrence["argument"].split(",")]:
            relations.append(
                {
                    "schema": SCHEMA,
                    "schema_version": VERSION,
                    "record_type": "relation",
                    "id": f"FAOA-2015-CH01-REL-CITE-{number:04d}-{key}",
                    "relation_type": "cites",
                    "from_id": containing_segment(segment_records, occurrence["start"], "source"),
                    "to_id": f"ERDMAN-FAOA-BIB-{key}",
                    "source_local_id": key,
                }
            )

    # Link each proof or proof hint to the preceding theorem-like source unit.
    previous_statement: str | None = None
    hint_ids_by_exercise: dict[str, list[str]] = defaultdict(list)
    for record in semantic_units:
        kind = record["unit_kind"]
        if kind != "proof":
            previous_statement = record["id"]
            continue
        if previous_statement is None:
            raise ValueError("proof without preceding statement")
        is_hint = "Hint for proof" in (record.get("source_title_tex") or "")
        relation_type = "hints" if is_hint else "proves"
        relations.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "relation",
                "id": f"FAOA-2015-CH01-REL-{relation_type.upper()}-{record['id'].split('-')[-1]}",
                "relation_type": relation_type,
                "from_id": record["id"],
                "to_id": previous_statement,
            }
        )
        if is_hint:
            hint_ids_by_exercise[previous_statement].append(record["id"])

    source_terms = macro_occurrences(source, "index")
    target_terms = macro_occurrences(target, "index")
    if len(source_terms) != 187 or len(target_terms) != 187:
        raise ValueError("index occurrence count changed")
    term_buffer = io.StringIO(newline="")
    term_writer = csv.writer(term_buffer, lineterminator="\n")
    term_writer.writerow(
        [
            "id",
            "parent_segment_id",
            "source_order",
            "source_line",
            "source_index_tex",
            "target_line",
            "target_index_tex",
            "source_sha256",
            "target_sha256",
            "locale",
        ]
    )
    for number, (source_term, target_term) in enumerate(zip(source_terms, target_terms), 1):
        term_writer.writerow(
            [
                f"{CHAPTER_ID}-TERM-OCC-{number:04d}",
                containing_segment(segment_records, source_term["start"], "source"),
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
    (BACKEND / "index_terms.csv").write_text(term_buffer.getvalue(), encoding="utf-8", newline="\n")

    source_math = extract_math(source, SOURCE_ENCODING)
    target_math = extract_math(target, TARGET_ENCODING)
    if len(source_math) != 932 or len(target_math) != 932:
        raise ValueError("math surface count changed")
    matcher = difflib.SequenceMatcher(
        a=[item["normalized"] for item in source_math],
        b=[item["normalized"] for item in target_math],
        autojunk=False,
    )
    formula_records: list[dict] = []
    formula_map_number = 0
    exact_formula_count = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for source_index, target_index in zip(range(i1, i2), range(j1, j2)):
                formula_map_number += 1
                exact_formula_count += 1
                sm, tm = source_math[source_index], target_math[target_index]
                formula_records.append(
                    {
                        "schema": SCHEMA,
                        "schema_version": VERSION,
                        "record_type": "formula_map",
                        "id": f"{CHAPTER_ID}-MATHMAP-{formula_map_number:04d}",
                        "alignment": "preserved_exact_after_whitespace_normalization",
                        "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{source_index+1:04d}"],
                        "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{target_index+1:04d}"],
                        "source_lines": [[sm["line_start"], sm["line_end"]]],
                        "target_lines": [[tm["line_start"], tm["line_end"]]],
                        "source_sha256": [sm["sha256"]],
                        "target_sha256": [tm["sha256"]],
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
                    "alignment": "reviewed_localization_source_correction_or_reflow_boundary",
                    "sequence_opcode": tag,
                    "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{i+1:04d}" for i in range(i1, i2)],
                    "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{j+1:04d}" for j in range(j1, j2)],
                    "source_lines": [[source_math[i]["line_start"], source_math[i]["line_end"]] for i in range(i1, i2)],
                    "target_lines": [[target_math[j]["line_start"], target_math[j]["line_end"]] for j in range(j1, j2)],
                    "source_sha256": [source_math[i]["sha256"] for i in range(i1, i2)],
                    "target_sha256": [target_math[j]["sha256"] for j in range(j1, j2)],
                    "review_witness": "provenance/SOURCE_CORRECTIONS.md and QA-CH01-ADMISSION-20260821",
                }
            )
    if exact_formula_count != 906:
        raise ValueError(f"expected 906 exact formula alignments, found {exact_formula_count}")

    exercises: list[dict] = []
    exercise_number = 0
    for record in semantic_units:
        if record["unit_kind"] != "exer":
            continue
        exercise_number += 1
        exercises.append(
            {
                "schema": SCHEMA,
                "schema_version": VERSION,
                "record_type": "exercise_support",
                "id": f"{CHAPTER_ID}-EXERCISE-SUPPORT-{exercise_number:03d}",
                "exercise_unit_id": record["id"],
                "source_exercise_order": exercise_number,
                "upstream_hint_ids": hint_ids_by_exercise.get(record["id"], []),
                "upstream_answer_state": "absent",
                "upstream_solution_state": "absent",
                "original_solution_id": f"O001-{CHAPTER_ID}-EX-{exercise_number:03d}-SOLUTION",
                "original_solution_state": "queued_in_O001",
                "original_rights_id": "RIGHTS-ORIGINAL-CC-BY-SA-4.0",
                "provenance": "separately_authored_not_Erdman",
            }
        )
    if len(exercises) != 6:
        raise ValueError("exercise count changed")

    for record in segment_records:
        for key in ("_source_start", "_source_end", "_target_start", "_target_end"):
            del record[key]
    dump_jsonl(BACKEND / "semantic_units.jsonl", semantic_units)
    dump_jsonl(BACKEND / "segments.jsonl", segment_records)
    dump_jsonl(BACKEND / "relations.jsonl", relations)
    dump_jsonl(BACKEND / "formula_map.jsonl", formula_records)
    dump_jsonl(BACKEND / "exercise_support.jsonl", exercises)
    print(
        json.dumps(
            {
                "anchors": len(source_anchors),
                "semantic_units": len(semantic_units),
                "segments": len(segment_records),
                "relations": len(relations),
                "index_terms": len(source_terms),
                "source_math": len(source_math),
                "target_math": len(target_math),
                "exact_math": exact_formula_count,
                "formula_map_records": len(formula_records),
                "exercises": len(exercises),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
