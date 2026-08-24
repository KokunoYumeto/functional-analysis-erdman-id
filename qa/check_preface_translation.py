#!/usr/bin/env python3
"""Fail-closed, deterministic QA for the translated FAOA preface.

This checker is deliberately bounded to the frozen preface authority, its
Indonesian target, the complete-source wrapper, the applied correction ledger,
and the inherited Chapter 17 build-input snapshot.  It writes one stable JSON
report and performs no build, source mutation, Git operation, or network call.
"""

from __future__ import annotations

import csv
import difflib
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "qa" / "preface-translation-report.json"

SOURCE_REL = "source/upstream/preface.tex"
TARGET_REL = "source/id-ID/preface-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-complete-source.tex"
LEDGER_REL = "provenance/SOURCE_CORRECTIONS_PREFACE.json"
SNAPSHOT_REL = "qa/build-through-ch17-final/input-snapshot.csv"
PRIOR_MASTER_REL = "source/id-ID/functional-analysis-id-through-ch17.tex"

EXPECTED_IDENTITIES = {
    SOURCE_REL: {
        "bytes": 18107,
        "logical_records": 351,
        "line_endings": "CRLF",
        "encoding": "ASCII",
        "sha256": "0976042bbb6ae3b8d1e5bb113a93d51169fada9d3e41f2d01435c76b6729edb9",
    },
    TARGET_REL: {
        "bytes": 18140,
        "logical_records": 394,
        "line_endings": "LF",
        "encoding": "UTF-8 without BOM",
        "sha256": "c622dc9d9c1af4e5b1a6112c84eeff7328c778e8ef8643fc267f6fc6e3e7d564",
    },
    MASTER_REL: {
        "bytes": 11176,
        "logical_records": 353,
        "line_endings": "LF",
        "encoding": "UTF-8 without BOM",
        "sha256": "7f06919a8ec9088a3bc812fab962a48b5f1b3b0d5d3bce80eb21055f65089041",
    },
    SNAPSHOT_REL: {
        "bytes": 2302,
        "logical_records": 21,
        "line_endings": "CRLF",
        "encoding": "ASCII",
        "sha256": "be4af8b068adb360f3768e74244397bae5cd874bf0b3db031d90e302c18259e8",
    },
}

EXPECTED_CITATIONS = [
    "Halmos:1982",
    "BrownDF:1973",
    "Erdman:2010",
    "Erdman:2005",
    "Erdman:2007",
]

EXPECTED_GREEK = [
    "Alpha (AL-fuh)",
    "Beta (BAY-tuh)",
    "Gamma (GAM-uh)",
    "Delta (DEL-tuh)",
    "Epsilon (EPP-suh-lon)",
    "Zeta (ZAY-tuh)",
    "Eta (AY-tuh)",
    "Theta (THAY-tuh)",
    "Iota (eye-OH-tuh)",
    "Kappa (KAP-uh)",
    "Lambda (LAM-duh)",
    "Mu (MYOO)",
    "Nu (NOO)",
    "Xi (KSEE)",
    "Omicron (OHM-ih-kron)",
    "Pi (PIE)",
    "Rho (ROH)",
    "Sigma (SIG-muh)",
    "Tau (TAU)",
    "Upsilon (OOP-suh-lon)",
    "Phi (FEE or FAHY)",
    "Chi (KHAY)",
    "Psi (PSEE or PSAHY)",
    "Omega (oh-MAY-guh)",
]

EXPECTED_HEADINGS_SOURCE = [
    "chapter*:PREFACE",
    "section*:Greek Letters",
    "section*:Fraktur Fonts",
    "section*:Notation for Sets of Numbers",
    "section*:Notation for Functions",
]
EXPECTED_HEADINGS_TARGET = [
    "chapter*:Prakata",
    "section*:Huruf Yunani",
    "section*:Font Fraktur",
    "section*:Notasi untuk Himpunan Bilangan",
    "section*:Notasi untuk Fungsi",
]

EXPECTED_ENV_SOURCE = ["enumerate", "align*", "enumerate"]
EXPECTED_ENV_TARGET = [
    "enumerate",
    "center",
    "tabularx",
    "center",
    "tabularx",
    "align*",
    "enumerate",
]

EXPECTED_DIAGRAMS = [
    r"\square[R`U`S`T;j`f`h`k]",
    r"\btriangle[R`S`T;f`g`k]",
]

EXPECTED_SNAPSHOT_PATHS = [
    PRIOR_MASTER_REL,
    "source/id-ID/DIAGXY.TEX",
    "source/id-ID/functional_analysis_op_algs_bib.bib",
    "source/id-ID/linalg-id.tex",
    "source/id-ID/categories-id.tex",
    "source/id-ID/normlinspaces-id.tex",
    "source/id-ID/Hilbert_spaces-id.tex",
    "source/id-ID/Hilbert_space_operators-id.tex",
    "source/id-ID/Banach_spaces-id.tex",
    "source/id-ID/compact_operators-id.tex",
    "source/id-ID/spectrum-id.tex",
    "source/id-ID/topvecspaces-id.tex",
    "source/id-ID/distributions-id.tex",
    "source/id-ID/Gelfand_Naimark-id.tex",
    "source/id-ID/no_identity-id.tex",
    "source/id-ID/GNS_construction-id.tex",
    "source/id-ID/multiplier_algebras-id.tex",
    "source/id-ID/fredholm_theory-id.tex",
    "source/id-ID/extensions-id.tex",
    "source/id-ID/K0_functor-id.tex",
]


def rel_path(relative: str) -> Path:
    """Resolve one frozen POSIX-style lane-relative path safely."""

    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError(f"unsafe relative path: {relative!r}")
    return ROOT.joinpath(*posix.parts)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(relative: str) -> dict[str, Any]:
    data = rel_path(relative).read_bytes()
    crlf = data.count(b"\r\n")
    bare_lf = data.count(b"\n") - crlf
    bare_cr = data.count(b"\r") - crlf
    if crlf and not bare_lf and not bare_cr:
        line_endings = "CRLF"
    elif bare_lf and not crlf and not bare_cr:
        line_endings = "LF"
    elif not crlf and not bare_lf and not bare_cr:
        line_endings = "none"
    else:
        line_endings = "mixed"
    return {
        "path": relative,
        "bytes": len(data),
        "logical_records": data.count(b"\n") + (0 if data.endswith(b"\n") else 1),
        "line_endings": line_endings,
        "sha256": sha256_bytes(data),
    }


def strip_tex_comments(text: str) -> str:
    """Strip TeX comments while respecting escaped percent signs."""

    output: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.endswith("\r\n"):
            body, ending = line[:-2], "\r\n"
        elif line.endswith("\n") or line.endswith("\r"):
            body, ending = line[:-1], line[-1]
        else:
            body, ending = line, ""
        cut = len(body)
        for index, char in enumerate(body):
            if char != "%":
                continue
            slash_count = 0
            cursor = index - 1
            while cursor >= 0 and body[cursor] == "\\":
                slash_count += 1
                cursor -= 1
            if slash_count % 2 == 0:
                cut = index
                break
        output.append(body[:cut] + ending)
    return "".join(output)


def macro_args(text: str, macro: str) -> list[str]:
    """Return ordered balanced braced arguments for a simple TeX macro."""

    pattern = re.compile(r"\\" + re.escape(macro) + r"(?![A-Za-z@])\s*\{")
    values: list[str] = []
    for match in pattern.finditer(text):
        opening = match.end() - 1
        depth = 0
        escaped = False
        for cursor in range(opening, len(text)):
            char = text[cursor]
            if char == "\\" and not escaped:
                escaped = True
                continue
            if char == "{" and not escaped:
                depth += 1
            elif char == "}" and not escaped:
                depth -= 1
                if depth == 0:
                    values.append(text[opening + 1 : cursor])
                    break
            escaped = False
        else:
            raise ValueError(f"unclosed argument for \\{macro}")
    return values


def normalized_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def headings(text: str) -> list[str]:
    events: list[tuple[int, str]] = []
    for macro in ("chapter*", "section*"):
        pattern = re.compile(r"\\" + re.escape(macro) + r"\s*\{([^{}]*)\}")
        events.extend((match.start(), f"{macro}:{match.group(1)}") for match in pattern.finditer(text))
    return [value for _, value in sorted(events)]


def environment_events(text: str) -> tuple[list[str], list[str], bool]:
    events = re.findall(r"\\(begin|end)\s*\{([^{}]+)\}", text)
    begins: list[str] = []
    ends: list[str] = []
    stack: list[str] = []
    balanced = True
    for kind, name in events:
        if kind == "begin":
            begins.append(name)
            stack.append(name)
        else:
            ends.append(name)
            if not stack or stack[-1] != name:
                balanced = False
            else:
                stack.pop()
    if stack:
        balanced = False
    return begins, ends, balanced


def section_between(text: str, start: str, end: str | None) -> str:
    if text.count(start) != 1:
        raise ValueError(f"section start is not unique: {start!r}")
    tail = text.split(start, 1)[1]
    if end is None:
        return tail
    if tail.count(end) != 1:
        raise ValueError(f"section end is not unique after start: {end!r}")
    return tail.split(end, 1)[0]


def greek_strings(section: str) -> list[str]:
    names = [entry.split(" ", 1)[0] for entry in EXPECTED_GREEK]
    name_pattern = "|".join(re.escape(name) for name in names)
    found: list[str] = []
    for line in section.splitlines():
        match = re.search(rf"\b({name_pattern})\s+\(([^)]*)\)", line)
        if match:
            found.append(f"{match.group(1)} ({normalized_space(match.group(2))})")
    return found


def fraktur_rows(section: str, separator: str) -> list[list[str]]:
    sep = re.escape(separator)
    pattern = re.compile(
        r"\$\\mathfrak\s+([A-Z])\$\s*"
        + sep
        + r"\s*\$\\mathfrak\s+([a-z])\$\s*"
        + sep
        + r"\s*([a-z])"
    )
    return [list(groups) for groups in pattern.findall(section)]


def align_formula_prefixes(text: str) -> list[str]:
    matches = re.findall(r"\\begin\{align\*\}(.*?)\\end\{align\*\}", text, flags=re.S)
    if len(matches) != 1:
        raise ValueError(f"expected one align* body, found {len(matches)}")
    kept_lines = [
        line
        for line in matches[0].splitlines()
        if not line.strip().startswith(r"\index{")
    ]
    statements = re.split(r"\\\\", "\n".join(kept_lines))
    prefixes: list[str] = []
    for statement in statements:
        value = normalized_space(statement)
        if not value:
            continue
        text_position = value.find(r"\text{")
        if text_position >= 0:
            value = value[:text_position].rstrip()
        if value.startswith("&"):
            value = value[1:].lstrip()
        prefixes.append(value)
    return prefixes


def diagrams(text: str) -> list[str]:
    return [
        normalized_space(match.group(0))
        for match in re.finditer(r"\\(?:square|btriangle)\[[^\]]+\]", text)
    ]


def dollar_spans(text: str) -> list[str]:
    return [
        normalized_space(value)
        for value in re.findall(r"(?<!\\)\$(.*?)(?<!\\)\$", text, flags=re.S)
    ]


def ordered_citations(text: str) -> list[str]:
    output: list[str] = []
    for argument in macro_args(text, "cite"):
        output.extend(key.strip() for key in argument.split(",") if key.strip())
    return output


def main() -> int:
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def require(name: str, condition: bool, detail: Any) -> None:
        passed = bool(condition)
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            errors.append(name)

    source_bytes = rel_path(SOURCE_REL).read_bytes()
    target_bytes = rel_path(TARGET_REL).read_bytes()
    master_bytes = rel_path(MASTER_REL).read_bytes()
    snapshot_bytes = rel_path(SNAPSHOT_REL).read_bytes()

    require("source decodes as ASCII", _decodes(source_bytes, "ascii"), "ASCII")
    require("target has no UTF-8 BOM", not target_bytes.startswith(b"\xef\xbb\xbf"), "no BOM")
    require("master has no UTF-8 BOM", not master_bytes.startswith(b"\xef\xbb\xbf"), "no BOM")

    source = source_bytes.decode("ascii")
    target = target_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")
    source_active = strip_tex_comments(source)
    target_active = strip_tex_comments(target)
    master_active = strip_tex_comments(master)

    identities: dict[str, dict[str, Any]] = {}
    for relative, expected in EXPECTED_IDENTITIES.items():
        observed = identity(relative)
        observed["encoding"] = expected["encoding"]
        identities[relative] = observed
        for field in ("bytes", "logical_records", "line_endings", "sha256"):
            require(
                f"identity {relative} {field}",
                observed[field] == expected[field],
                {"expected": expected[field], "observed": observed[field]},
            )

    source_headings = headings(source_active)
    target_headings = headings(target_active)
    require("source heading topology", source_headings == EXPECTED_HEADINGS_SOURCE, source_headings)
    require("target heading topology", target_headings == EXPECTED_HEADINGS_TARGET, target_headings)

    reference_surfaces: dict[str, Any] = {}
    for macro in ("label", "ref", "eqref", "pageref"):
        source_values = macro_args(source_active, macro)
        target_values = macro_args(target_active, macro)
        reference_surfaces[macro] = {"source": source_values, "target": target_values}
        expected_values = ["C0009"] if macro == "label" else []
        require(f"source ordered {macro} calls", source_values == expected_values, source_values)
        require(f"target ordered {macro} calls", target_values == expected_values, target_values)

    source_citations = ordered_citations(source_active)
    target_citations = ordered_citations(target_active)
    reference_surfaces["cite"] = {"source": source_citations, "target": target_citations}
    require("source citation order", source_citations == EXPECTED_CITATIONS, source_citations)
    require("target citation order", target_citations == EXPECTED_CITATIONS, target_citations)

    source_index = macro_args(source_active, "index")
    target_index = macro_args(target_active, "index")
    source_index_raw = macro_args(source, "index")
    target_index_raw = macro_args(target, "index")
    source_df = macro_args(source_active, "df")
    target_df = macro_args(target_active, "df")
    source_items = len(re.findall(r"\\item\b", source_active))
    target_items = len(re.findall(r"\\item\b", target_active))
    require("source active index count", len(source_index) == 53, len(source_index))
    require("target active index count", len(target_index) == 53, len(target_index))
    require("source one commented index candidate", len(source_index_raw) - len(source_index) == 1, len(source_index_raw) - len(source_index))
    require("target one commented index candidate", len(target_index_raw) - len(target_index) == 1, len(target_index_raw) - len(target_index))
    require("source commented restriction index retained", r'%\index{<@$\bigl.f\bigr"|_A$ (restriction of $f$ to $A$)}%' in source, "exact source candidate")
    require("target commented restriction index retained", r'%\index{<@$\bigl.f\bigr"|_A$ (pembatasan $f$ pada $A$)}%' in target, "exact target candidate")
    require("source defined-term hook count", len(source_df) == 21, len(source_df))
    require("target defined-term hook count", len(target_df) == 21, len(target_df))
    require("source item count", source_items == 5, source_items)
    require("target item count", target_items == 5, target_items)

    source_begins, source_ends, source_env_balanced = environment_events(source_active)
    target_begins, target_ends, target_env_balanced = environment_events(target_active)
    require("source environment closure", source_env_balanced, {"begin": source_begins, "end": source_ends})
    require("target environment closure", target_env_balanced, {"begin": target_begins, "end": target_ends})
    require("source environment sequence", source_begins == EXPECTED_ENV_SOURCE, source_begins)
    require("target environment sequence", target_begins == EXPECTED_ENV_TARGET, target_begins)
    removed_table_envs = [name for name in target_begins if name not in {"center", "tabularx"}]
    require("target adds only table-layout environments", removed_table_envs == source_begins, removed_table_envs)
    require(
        "target adds exactly two center and two tabularx environments",
        Counter(target_begins) - Counter(source_begins) == Counter({"center": 2, "tabularx": 2}),
        dict(Counter(target_begins) - Counter(source_begins)),
    )

    source_greek_section = section_between(
        source_active,
        r"\section*{Greek Letters}",
        r"\section*{Fraktur Fonts}",
    )
    target_greek_section = section_between(
        target_active,
        r"\section*{Huruf Yunani}",
        r"\section*{Font Fraktur}",
    )
    source_greek = greek_strings(source_greek_section)
    target_greek = greek_strings(target_greek_section)
    require("source Greek name/pronunciation order", source_greek == EXPECTED_GREEK, source_greek)
    require("target preserves all Greek name/pronunciation strings", target_greek == EXPECTED_GREEK, target_greek)

    source_fraktur_section = section_between(
        source_active,
        r"\section*{Fraktur Fonts}",
        r"\section*{Notation for Sets of Numbers}",
    )
    target_fraktur_section = section_between(
        target_active,
        r"\section*{Font Fraktur}",
        r"\section*{Notasi untuk Himpunan Bilangan}",
    )
    expected_fraktur = [[chr(code), chr(code + 32), chr(code + 32)] for code in range(ord("A"), ord("Z") + 1)]
    source_fraktur = fraktur_rows(source_fraktur_section, "!")
    target_fraktur = fraktur_rows(target_fraktur_section, "&")
    target_header_lines = [line for line in target_fraktur_section.splitlines() if r"\textbf{" in line]
    target_header_values = macro_args("\n".join(target_header_lines), "textbf")
    source_header_lines = [
        normalized_space(line)
        for line in source_fraktur_section.splitlines()
        if "!" in line and r"\mathfrak" not in line
    ]
    require("source Fraktur rows A-Z", source_fraktur == expected_fraktur, source_fraktur)
    require("target Fraktur rows A-Z", target_fraktur == expected_fraktur, target_fraktur)
    require("source Fraktur has two header rows", len(source_header_lines) == 2, source_header_lines)
    require("target Fraktur has two header rows", len(target_header_lines) == 2, target_header_lines)
    require(
        "target Fraktur two-level header values",
        target_header_values == ["Fraktur", "Fraktur", "Roman", "Huruf kapital", "Huruf kecil", "Huruf kecil"],
        target_header_values,
    )

    source_formula_prefixes = align_formula_prefixes(source_active)
    target_formula_prefixes = align_formula_prefixes(target_active)
    require("source number-notation row count", len(source_formula_prefixes) == 20, len(source_formula_prefixes))
    require("target number-notation row count", len(target_formula_prefixes) == 20, len(target_formula_prefixes))
    require("number-notation formula prefixes preserved", target_formula_prefixes == source_formula_prefixes, target_formula_prefixes)

    source_diagrams = diagrams(source_active)
    target_diagrams = diagrams(target_active)
    require("source diagram topology", source_diagrams == EXPECTED_DIAGRAMS, source_diagrams)
    require("target diagram topology", target_diagrams == EXPECTED_DIAGRAMS, target_diagrams)
    require("source xy closure", source_active.count(r"\xy") == 2 and source_active.count(r"\endxy") == 2, {"xy": source_active.count(r"\xy"), "endxy": source_active.count(r"\endxy")})
    require("target xy closure", target_active.count(r"\xy") == 2 and target_active.count(r"\endxy") == 2, {"xy": target_active.count(r"\xy"), "endxy": target_active.count(r"\endxy")})
    for equality in (r"$h \circ j = k \circ f$", r"$g = k \circ f$"):
        require(f"diagram equality preserved: {equality}", source.count(equality) == 1 and target.count(equality) == 1, {"source": source.count(equality), "target": target.count(equality)})

    source_math = dollar_spans(source)
    target_math = dollar_spans(target)
    require("source raw dollar-math span count", len(source_math) == 204, len(source_math))
    require("target raw dollar-math span count", len(target_math) == 205, len(target_math))
    insertion_positions = [
        index
        for index, value in enumerate(target_math)
        if value == "G" and target_math[:index] == source_math[:index] and target_math[index + 1 :] == source_math[index:]
    ]
    require("sole math-sequence delta is inserted G", len(insertion_positions) == 1, insertion_positions)
    insertion_index = insertion_positions[0] if len(insertion_positions) == 1 else None
    insertion_context = None
    if insertion_index is not None and 0 < insertion_index < len(source_math):
        insertion_context = {
            "source_before": source_math[insertion_index - 1],
            "target_inserted": target_math[insertion_index],
            "source_after": source_math[insertion_index],
        }
        require(
            "C014 math delta has the exact function-condition context",
            insertion_context == {
                "source_before": "(s,t_2)",
                "target_inserted": "G",
                "source_after": "t_1 = t_2",
            },
            insertion_context,
        )
    else:
        require("C014 math delta has the exact function-condition context", False, insertion_context)
    diff_lines = list(difflib.unified_diff(source_math, target_math, fromfile="source", tofile="target", n=1))

    ledger = json.loads(rel_path(LEDGER_REL).read_text(encoding="utf-8"))
    require("ledger schema", ledger.get("schema_version") == "o008.source-corrections.v1", ledger.get("schema_version"))
    require("ledger unit", ledger.get("unit_id") == "FAOA-2015-PREFACE", ledger.get("unit_id"))
    require("ledger applied state", ledger.get("status") == "applied_verified", ledger.get("status"))
    records = ledger.get("records", [])
    require("ledger record count field", ledger.get("record_count") == 14, ledger.get("record_count"))
    require("ledger actual record count", len(records) == 14, len(records))
    expected_ids = [f"FAOA-2015-PREFACE-CORR-{number:03d}" for number in range(1, 15)]
    require("ledger stable record IDs", [record.get("id") for record in records] == expected_ids, [record.get("id") for record in records])
    require("ledger class counts", ledger.get("class_counts") == dict(Counter(record.get("classification") for record in records)), ledger.get("class_counts"))
    require("ledger source identity", _ledger_identity_matches(ledger.get("source", {}), EXPECTED_IDENTITIES[SOURCE_REL]), ledger.get("source"))
    require("ledger target identity", _ledger_identity_matches(ledger.get("target", {}), EXPECTED_IDENTITIES[TARGET_REL]), ledger.get("target"))

    ledger_results: list[dict[str, Any]] = []
    target_lines = target.splitlines()
    source_lines = source.splitlines()
    semantic_ids = {record["id"] for record in records if record.get("required_target_semantics")}
    supported_semantic_ids = {
        "FAOA-2015-PREFACE-CORR-001",
        "FAOA-2015-PREFACE-CORR-004",
        "FAOA-2015-PREFACE-CORR-005",
        "FAOA-2015-PREFACE-CORR-006",
        "FAOA-2015-PREFACE-CORR-007",
        "FAOA-2015-PREFACE-CORR-011",
    }
    require("every narrative ledger semantic has a deterministic check", semantic_ids == supported_semantic_ids, sorted(semantic_ids))

    for number, record in enumerate(records, 1):
        record_id = record["id"]
        marker = record.get("target_marker", "")
        marker_count = target.count(marker)
        actual_marker_line = next((index + 1 for index, line in enumerate(target_lines) if marker in line), None)
        line_range = record.get("source_lines", {})
        start = int(line_range.get("start", 0))
        end = int(line_range.get("end", 0))
        source_slice = "\n".join(source_lines[start - 1 : end]) if 1 <= start <= end <= len(source_lines) else ""
        source_anchor_results = {
            anchor: normalized_space(anchor) in normalized_space(source_slice)
            for anchor in record.get("source_required_anchors", [])
        }
        target_anchor_results = {
            anchor: normalized_space(anchor) in normalized_space(target)
            for anchor in record.get("required_target_anchors", [])
        }
        if number == 1:
            marker_tail = target.split(marker, 1)[1] if marker in target else ""
            forbidden_scope = marker_tail.split("\n\n", 1)[0]
        else:
            forbidden_scope = target
        forbidden_results = {
            anchor: anchor not in forbidden_scope
            for anchor in record.get("forbidden_target_anchors", [])
        }
        require(f"{record_id} marker occurs once", marker_count == 1, marker_count)
        require(f"{record_id} marker line", actual_marker_line == record.get("target_marker_line"), {"ledger": record.get("target_marker_line"), "actual": actual_marker_line})
        require(f"{record_id} source anchors", all(source_anchor_results.values()), source_anchor_results)
        require(f"{record_id} target anchors", all(target_anchor_results.values()), target_anchor_results)
        require(f"{record_id} forbidden anchors", all(forbidden_results.values()), forbidden_results)
        ledger_results.append(
            {
                "id": record_id,
                "classification": record.get("classification"),
                "marker": marker,
                "marker_count": marker_count,
                "marker_line": actual_marker_line,
                "source_anchors": source_anchor_results,
                "target_anchors": target_anchor_results,
                "forbidden_anchors_absent": forbidden_results,
            }
        )

    first_paragraph = target.split("% SOURCE-CORRECTION: PREFACE-C001", 1)[1].split("\n\n", 1)[0]
    normalized_first_paragraph = normalized_space(first_paragraph)
    semantic_checks = {
        "FAOA-2015-PREFACE-CORR-001": (
            "Paul Halmos" in normalized_first_paragraph
            and r"\emph{Hilbert Space Problem Book}" in normalized_first_paragraph
            and r"\cite{Halmos:1982}" in normalized_first_paragraph
            and "praktik aktif merupakan syarat mutlak untuk belajar matematika" in normalized_first_paragraph
            and "The only way to learn mathematics is to do mathematics" not in target
            and "``" not in first_paragraph
            and "''" not in first_paragraph
        ),
        "FAOA-2015-PREFACE-CORR-004": (
            "BerbagiSerupa" in target
            and "Attribution--ShareAlike 4.0 International (CC BY-SA 4.0)" in master
            and "https://creativecommons.org/licenses/by-sa/4.0/" in master
            and "tidak disponsori atau didukung oleh John M. Erdman maupun Portland State University" in normalized_space(master)
        ),
        "FAOA-2015-PREFACE-CORR-005": (
            len(target_greek) == 24
            and target_greek == EXPECTED_GREEK
            and r"\begin{tabularx}{\textwidth}" in target_greek_section
            and "Nama dalam bahasa Inggris (perkiraan pelafalan)" in target_greek_section
        ),
        "FAOA-2015-PREFACE-CORR-006": (
            len(target_fraktur) == 26
            and target_fraktur == expected_fraktur
            and len(target_header_lines) == 2
            and r"\begin{tabularx}{\textwidth}" in target_fraktur_section
        ),
        "FAOA-2015-PREFACE-CORR-007": (
            target.count(r"\label{C0009}") == 1
            and normalized_space(r"\phantomsection \section*{Notasi untuk Himpunan Bilangan}\label{C0009}")
            in normalized_space(target)
            and r"\section{Notasi untuk Himpunan Bilangan}" not in target
        ),
        "FAOA-2015-PREFACE-CORR-011": (
            r"&\N_n = \{1,2,3,\dots,n\}\text{, $n$ bilangan asli pertama}" in target
        ),
    }
    for record_id, passed in semantic_checks.items():
        require(f"{record_id} required semantics", passed, passed)

    c014 = records[-1] if records else {}
    require("C014 classifies only a TeX math-surface repair", c014.get("classification") == "MECHANICAL_TEX_SOURCE_REPAIR" and c014.get("affects_math") is False and c014.get("affects_math_surface") is True, {"classification": c014.get("classification"), "affects_math": c014.get("affects_math"), "affects_math_surface": c014.get("affects_math_surface")})

    excluded_anchors = {
        "legacy TABLE input": r"\input{TABLE.TEX}",
        "legacy TABLE call": r"\table{}",
        "legacy TABLE double-row macro": r"\rr",
        "legacy custom empty caption": r"\caption{}",
        "Wiener epigraph/name": "Wiener",
        "CC badge EPS": "by-sa.eps",
        "CC badge PDF": "by-sa.pdf",
        "direct Halmos sentence": "The only way to learn mathematics is to do mathematics",
    }
    exclusion_results: dict[str, dict[str, int]] = {}
    for label, anchor in excluded_anchors.items():
        counts = {"target": target_active.count(anchor), "master": master_active.count(anchor)}
        exclusion_results[label] = counts
        require(f"excluded surface absent: {label}", counts == {"target": 0, "master": 0}, counts)
    require("badge/image include commands absent from preface", not re.search(r"\\(?:includegraphics|epsfbox)\b", target_active), "none")

    wrapper_anchors = [
        "John M. Erdman",
        "Creative Commons",
        "Attribution--ShareAlike 4.0 International (CC BY-SA 4.0)",
        "https://creativecommons.org/licenses/by-sa/4.0/",
        "Terjemahan Bahasa Indonesia dan adaptasi teknis",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "kredit John M. Erdman dan kontributor komponen tetap dipertahankan",
        "Edisi ini tidak disponsori atau didukung oleh John M. Erdman maupun Portland State University",
    ]
    normalized_master = normalized_space(master_active)
    wrapper_anchor_results = {anchor: anchor in normalized_master for anchor in wrapper_anchors}
    require("wrapper attribution/license/model/nonendorsement anchors", all(wrapper_anchor_results.values()), wrapper_anchor_results)
    require("wrapper retains exact DIAGXY input", master_active.count(r"\input{DIAGXY.TEX}") == 1, master_active.count(r"\input{DIAGXY.TEX}"))
    require("wrapper loads tabularx", master_active.count(r"\usepackage{tabularx}") == 1, master_active.count(r"\usepackage{tabularx}"))

    placement_tokens = [r"\frontmatter", r"\tableofcontents", r"\include{preface-id}", r"\mainmatter"]
    placement_positions = {token: master_active.find(token) for token in placement_tokens}
    require("preface placement tokens unique", all(master_active.count(token) == 1 for token in placement_tokens), {token: master_active.count(token) for token in placement_tokens})
    require("preface is between ToC and main matter", [placement_positions[token] for token in placement_tokens] == sorted(placement_positions.values()) and all(position >= 0 for position in placement_positions.values()), placement_positions)

    expected_chapter_includes = [
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
        "GNS_construction-id",
        "multiplier_algebras-id",
        "fredholm_theory-id",
        "extensions-id",
        "K0_functor-id",
    ]
    master_includes = macro_args(master_active, "include")
    require("wrapper include order", master_includes == ["preface-id"] + expected_chapter_includes, master_includes)

    snapshot_text = snapshot_bytes.decode("ascii")
    snapshot_rows = list(csv.DictReader(io.StringIO(snapshot_text, newline="")))
    snapshot_paths = [row.get("relative_path", "") for row in snapshot_rows]
    require("snapshot row count", len(snapshot_rows) == 20, len(snapshot_rows))
    require("snapshot exact path order", snapshot_paths == EXPECTED_SNAPSHOT_PATHS, snapshot_paths)
    require("snapshot paths unique", len(snapshot_paths) == len(set(snapshot_paths)), snapshot_paths)
    prior_rows = [row for row in snapshot_rows if row.get("relative_path") == PRIOR_MASTER_REL]
    require("prior master occurs once and is intentionally excluded", len(prior_rows) == 1, prior_rows)

    inherited_results: list[dict[str, Any]] = []
    for row in snapshot_rows:
        relative = row.get("relative_path", "")
        if relative == PRIOR_MASTER_REL:
            continue
        try:
            expected_bytes = int(row.get("bytes", ""))
        except ValueError:
            expected_bytes = -1
        expected_sha = row.get("sha256", "")
        current_data = rel_path(relative).read_bytes()
        observed_bytes = len(current_data)
        observed_sha = sha256_bytes(current_data)
        matched = observed_bytes == expected_bytes and observed_sha == expected_sha
        require(f"inherited Chapter 17 input lock: {relative}", matched, {"expected_bytes": expected_bytes, "observed_bytes": observed_bytes, "expected_sha256": expected_sha, "observed_sha256": observed_sha})
        inherited_results.append(
            {
                "path": relative,
                "bytes": observed_bytes,
                "sha256": observed_sha,
                "snapshot_match": matched,
            }
        )
    require("all 19 non-master inherited inputs checked", len(inherited_results) == 19, len(inherited_results))

    report: dict[str, Any] = {
        "schema_version": "o008.preface-translation-qa.v1",
        "unit_id": "FAOA-2015-PREFACE",
        "status": "pass" if not errors else "fail",
        "determinism": {
            "generated_timestamp": None,
            "checker_path": "qa/check_preface_translation.py",
            "checker_sha256": sha256_bytes(Path(__file__).read_bytes()),
            "report_serialization": "UTF-8 without BOM; LF; JSON indent=2; insertion-order keys",
        },
        "identities": identities,
        "topology": {
            "source_headings": source_headings,
            "target_headings": target_headings,
            "source_environment_begins": source_begins,
            "source_environment_ends": source_ends,
            "target_environment_begins": target_begins,
            "target_environment_ends": target_ends,
            "additional_target_environments": {"center": 2, "tabularx": 2},
        },
        "references": reference_surfaces,
        "index_terms_and_items": {
            "source_active_indexes": len(source_index),
            "target_active_indexes": len(target_index),
            "source_commented_index_candidates": len(source_index_raw) - len(source_index),
            "target_commented_index_candidates": len(target_index_raw) - len(target_index),
            "source_defined_terms": len(source_df),
            "target_defined_terms": len(target_df),
            "source_items": source_items,
            "target_items": target_items,
        },
        "greek_table": {
            "row_count": len(target_greek),
            "source_english_name_pronunciation_order": source_greek,
            "target_english_name_pronunciation_order": target_greek,
            "exact_match": source_greek == target_greek == EXPECTED_GREEK,
        },
        "fraktur_table": {
            "row_count": len(target_fraktur),
            "header_rows": len(target_header_lines),
            "source_rows": source_fraktur,
            "target_rows": target_fraktur,
        },
        "number_notation": {
            "row_count": len(target_formula_prefixes),
            "formula_prefixes": target_formula_prefixes,
            "source_target_exact_match": target_formula_prefixes == source_formula_prefixes,
        },
        "diagrams": {
            "source": source_diagrams,
            "target": target_diagrams,
            "equalities": [r"h \circ j = k \circ f", r"g = k \circ f"],
        },
        "math_span_delta": {
            "source_count": len(source_math),
            "target_count": len(target_math),
            "sole_insertion_zero_based_index": insertion_index,
            "context": insertion_context,
            "classification": "PREFACE-C014 / MECHANICAL_TEX_SOURCE_REPAIR / no mathematical change",
            "unified_diff": diff_lines,
        },
        "correction_ledger": {
            "path": LEDGER_REL,
            "identity": identity(LEDGER_REL),
            "status": ledger.get("status"),
            "record_count": len(records),
            "records": ledger_results,
            "required_semantics": semantic_checks,
        },
        "exclusions": exclusion_results,
        "wrapper": {
            "required_anchors": wrapper_anchor_results,
            "preface_placement_positions": placement_positions,
            "ordered_includes": master_includes,
        },
        "inherited_chapter17_input_lock": {
            "snapshot_path": SNAPSHOT_REL,
            "snapshot_identity": identities[SNAPSHOT_REL],
            "excluded_prior_master": {
                "path": PRIOR_MASTER_REL,
                "reason": "superseded wrapper; snapshot metadata retained but current file deliberately not re-locked",
                "snapshot_record": prior_rows[0] if len(prior_rows) == 1 else None,
            },
            "verified_non_master_input_count": len(inherited_results),
            "inputs": inherited_results,
        },
        "checks": checks,
        "failed_checks": errors,
    }

    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(
        json.dumps(
            {
                "status": report["status"],
                "checks": len(checks),
                "failed_checks": errors,
                "source_sha256": identities[SOURCE_REL]["sha256"],
                "target_sha256": identities[TARGET_REL]["sha256"],
                "master_sha256": identities[MASTER_REL]["sha256"],
                "report_sha256": sha256_bytes(REPORT_PATH.read_bytes()),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


def _decodes(data: bytes, encoding: str) -> bool:
    try:
        data.decode(encoding)
    except UnicodeDecodeError:
        return False
    return True


def _ledger_identity_matches(observed: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        observed.get(field) == expected[field]
        for field in ("bytes", "logical_records", "line_endings", "encoding", "sha256")
    )


if __name__ == "__main__":
    raise SystemExit(main())
