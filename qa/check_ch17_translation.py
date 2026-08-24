#!/usr/bin/env python3
"""Locked structural, mathematical, language, rights, and linkage QA for CH17."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "K0_functor.tex"
TARGET = ROOT / "source" / "id-ID" / "K0_functor-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch17.tex"
LEDGER = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH17.json"
REPORT = ROOT / "qa" / "ch17-translation-report.json"
EXPECTED = {
    "source_bytes": 59_639,
    "source_sha256": "e8ebcaa4e5dbc1cc9b907edb235465610f3bd61e0bfa1ce2f1b5b26e9abf8c6a",
    "target_bytes": 61_673,
    "target_sha256": "061ffd28907e2251fc8b01077888de3e11b3bce67fec1ba52b080c924a241059",
    "master_bytes": 10_820,
    "master_sha256": "51b3f4d790e3d09ac6ac4c160284510e4827140ecaa5a961a46c880ae5c8bb39",
}
EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 3,
        "bmatrix": 46,
        "cor": 2,
        "defn": 22,
        "enumerate": 4,
        "equation": 4,
        "exam": 31,
        "exer": 1,
        "notn": 7,
        "proof": 22,
        "prop": 63,
        "rem": 1,
    }
)
EXPECTED_INCLUDES = [
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
EXPECTED_SECTIONS = [
    "Relasi Ekuivalensi pada Proyeksi",
    "Semigrup Proyeksi",
    "Konstruksi Grothendieck",
    r"Grup $\mathbf{\emph{K}_0}$ untuk Aljabar-$C^*$ Beridentitas",
    r"$\mathbf{\emph{K}_0}(A)$---Kasus Tak Beridentitas",
    r"Sifat Keeksakan dan Stabilitas Funktor $K_0$",
    "Limit Induktif",
    "Diagram Bratteli",
]
MATH_CORRECTION_RANGES = {
    "FAOA-2015-CH17-CORR-005": (101, 103),
    "FAOA-2015-CH17-CORR-013": (741, 752),
    "FAOA-2015-CH17-CORR-014": (793, 850),
    "FAOA-2015-CH17-CORR-017": (860, 866),
    "FAOA-2015-CH17-CORR-019": (1032, 1036),
    "FAOA-2015-CH17-CORR-021": (1093, 1104),
    "FAOA-2015-CH17-CORR-024": (144, 145),
    "FAOA-2015-CH17-CORR-025": (175, 177),
    "FAOA-2015-CH17-CORR-026": (651, 652),
}
MATH_ALLOWED_RANGES = {
    "LOCALIZED_ORDINAL": (275, 275),
    "LOCALIZED_EXPLICIT_OBJECTS": (710, 710),
    "LOCALIZED_AF_COMPOUND": (1235, 1236),
    "LOCALIZED_STAR_HOMOMORPHISM_1127": (1127, 1127),
    "LOCALIZED_STAR_HOMOMORPHISM_1221": (1221, 1221),
    "FAOA-2015-CH17-CORR-005": (101, 103),
    "FAOA-2015-CH17-CORR-006": (367, 369),
    "FAOA-2015-CH17-CORR-012": (655, 658),
    "FAOA-2015-CH17-CORR-013": (741, 752),
    "FAOA-2015-CH17-CORR-014": (793, 850),
    "FAOA-2015-CH17-CORR-017": (860, 866),
    "FAOA-2015-CH17-CORR-019": (1032, 1036),
    "FAOA-2015-CH17-CORR-021": (1093, 1104),
    "FAOA-2015-CH17-CORR-024": (144, 145),
    "FAOA-2015-CH17-CORR-025": (175, 177),
    "FAOA-2015-CH17-CORR-026": (651, 652),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_comments(text: str) -> str:
    output: list[str] = []
    for line in text.splitlines(keepends=True):
        cut = len(line)
        search = 0
        while True:
            position = line.find("%", search)
            if position < 0:
                break
            backslashes = 0
            cursor = position - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = position
                break
            search = position + 1
        fragment = line[:cut]
        if line.endswith("\n") and not fragment.endswith("\n"):
            fragment += "\n"
        output.append(fragment)
    return "".join(output)


def extract_cites(text: str) -> list[str]:
    keys: list[str] = []
    for argument in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", text):
        keys.extend(value.strip() for value in argument.split(",") if value.strip())
    return keys


def extract_math(text: str) -> list[dict[str, object]]:
    """Return active top-level inline/display/equation/align surfaces in order."""

    active = strip_comments(text)
    surfaces: list[dict[str, object]] = []
    index = 0
    environments = (("equation", r"\begin{equation}", r"\end{equation}"), ("align", r"\begin{align*}", r"\end{align*}"))
    while index < len(active):
        matched_environment = False
        for kind, opening, closing in environments:
            if active.startswith(opening, index):
                start = index + len(opening)
                end = active.find(closing, start)
                if end < 0:
                    raise ValueError(f"unclosed {kind} environment")
                surfaces.append(
                    {
                        "kind": kind,
                        "line": active.count("\n", 0, start) + 1,
                        "value": re.sub(r"\s+", " ", active[start:end]).strip(),
                    }
                )
                index = end + len(closing)
                matched_environment = True
                break
        if matched_environment:
            continue
        if active.startswith(r"\[", index):
            start = index + 2
            end = active.find(r"\]", start)
            if end < 0:
                raise ValueError("unclosed display math")
            kind = "display"
            next_index = end + 2
        elif active[index] == "$" and (index == 0 or active[index - 1] != "\\"):
            start = index + 1
            end = start
            while end < len(active):
                if active[end] == "$" and active[end - 1] != "\\":
                    break
                end += 1
            if end >= len(active):
                raise ValueError("unclosed inline math")
            kind = "inline"
            next_index = end + 1
        else:
            index += 1
            continue
        surfaces.append(
            {
                "kind": kind,
                "line": active.count("\n", 0, start) + 1,
                "value": re.sub(r"\s+", " ", active[start:end]).strip(),
            }
        )
        index = next_index
    return surfaces


def mask_command_arguments(value: str, command: str) -> str:
    needle = "\\" + command + "{"
    output: list[str] = []
    cursor = 0
    while cursor < len(value):
        start = value.find(needle, cursor)
        if start < 0:
            output.append(value[cursor:])
            break
        output.append(value[cursor:start])
        depth = 1
        index = start + len(needle)
        while index < len(value) and depth:
            if value[index] == "{" and (index == 0 or value[index - 1] != "\\"):
                depth += 1
            elif value[index] == "}" and (index == 0 or value[index - 1] != "\\"):
                depth -= 1
            index += 1
        if depth:
            output.append(value[start:])
            break
        output.append(f"\\{command}{{<LOCALIZED-TEXT>}}")
        cursor = index
    return "".join(output)


def canonical_math(value: str) -> str:
    for command in ("text", "mbox", "textrm"):
        value = mask_command_arguments(value, command)
    return re.sub(r"\s+", " ", value).strip()


def validate_environment_stack(text: str) -> list[str]:
    errors: list[str] = []
    stack: list[str] = []
    for match in re.finditer(r"\\(begin|end)\{([^}]+)\}", text):
        operation, environment = match.groups()
        if operation == "begin":
            stack.append(environment)
        elif not stack or stack[-1] != environment:
            errors.append(f"environment stack mismatch at {environment}")
        else:
            stack.pop()
    if stack:
        errors.append(f"unclosed environments: {stack!r}")
    return errors


def normalize(lines: list[str], start: int, end: int) -> str:
    selected = [line.rstrip() for line in lines[start - 1 : end] if line.strip()]
    text = unicodedata.normalize("NFC", "\n".join(selected))
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    errors: list[str] = []
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    master_bytes = MASTER.read_bytes()
    ledger_bytes = LEDGER.read_bytes()
    identities = {
        "source_bytes": len(source_bytes),
        "source_sha256": digest(source_bytes),
        "target_bytes": len(target_bytes),
        "target_sha256": digest(target_bytes),
        "master_bytes": len(master_bytes),
        "master_sha256": digest(master_bytes),
        "ledger_bytes": len(ledger_bytes),
        "ledger_sha256": digest(ledger_bytes),
    }
    for key, expected in EXPECTED.items():
        if identities[key] != expected:
            errors.append(f"identity mismatch {key}: {identities[key]!r} != {expected!r}")
    if source_bytes.count(b"\r\n") != 1_362 or source_bytes.count(b"\n") != 1_362:
        errors.append("source CRLF topology differs")
    if b"\r" in target_bytes or target_bytes.count(b"\n") != 1_362:
        errors.append("target LF topology differs")
    if b"\r" in master_bytes or master_bytes.count(b"\n") != 346:
        errors.append("master LF topology differs")
    if any(data.startswith(b"\xef\xbb\xbf") for data in (target_bytes, master_bytes, ledger_bytes)):
        errors.append("UTF-8 BOM is forbidden")

    source = source_bytes.decode("ascii").replace("\r\n", "\n")
    target = target_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")
    active_source = strip_comments(source)
    active_target = strip_comments(target)
    source_lines = source.splitlines()
    target_lines = target.splitlines()
    if len(source_lines) != 1_362 or len(target_lines) != 1_362:
        errors.append("logical record count differs from 1362/1362")
    if not source.rstrip().endswith(r"\endinput") or not target.rstrip().endswith(r"\endinput"):
        errors.append("terminal endinput closure differs")
    if not active_source.startswith(r"\chapter{THE $\mathbf{\emph{K}_0}$-FUNCTOR}"):
        errors.append("source chapter opening differs")
    if not active_target.startswith(r"\chapter{FUNKTOR $\mathbf{\emph{K}_0}$}"):
        errors.append("target chapter opening differs")

    target_sections = re.findall(r"^\\section\{(.+)\}$", active_target, re.MULTILINE)
    if target_sections != EXPECTED_SECTIONS:
        errors.append(f"target section sequence differs: {target_sections!r}")
    if len(re.findall(r"^\\section\{", active_source, re.MULTILINE)) != 8:
        errors.append("source section count differs from eight")

    source_begins = re.findall(r"\\begin\{([^}]+)\}", active_source)
    source_ends = re.findall(r"\\end\{([^}]+)\}", active_source)
    target_begins = re.findall(r"\\begin\{([^}]+)\}", active_target)
    target_ends = re.findall(r"\\end\{([^}]+)\}", active_target)
    if len(source_begins) != 206 or len(target_begins) != 206:
        errors.append(f"environment opening count differs from 206/206: {len(source_begins)}/{len(target_begins)}")
    if Counter(source_begins) != EXPECTED_ENVIRONMENTS or Counter(target_begins) != EXPECTED_ENVIRONMENTS:
        errors.append("environment census differs")
    if source_begins != target_begins or source_ends != target_ends:
        errors.append("source/target environment topology differs")
    errors.extend(f"source {value}" for value in validate_environment_stack(active_source))
    errors.extend(f"target {value}" for value in validate_environment_stack(active_target))
    semantic_openings = len([value for value in target_begins if value not in {"align*", "bmatrix", "enumerate", "equation"}])
    if semantic_openings != 149:
        errors.append(f"reader-semantic environment count differs: {semantic_openings}")

    source_labels = re.findall(r"\\label\{([^}]+)\}", active_source)
    target_labels = re.findall(r"\\label\{([^}]+)\}", active_target)
    source_refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", active_source)
    target_refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", active_target)
    source_cites = extract_cites(active_source)
    target_cites = extract_cites(active_target)
    for name, source_values, target_values, expected_count in (
        ("labels", source_labels, target_labels, 73),
        ("references", source_refs, target_refs, 47),
        ("citations", source_cites, target_cites, 12),
    ):
        if len(source_values) != expected_count or len(target_values) != expected_count:
            errors.append(f"{name} count differs from {expected_count}/{expected_count}")
        if source_values != target_values:
            errors.append(f"{name} ordered topology differs")
    if len(set(target_labels)) != 73:
        errors.append("target labels are not 73 unique identifiers")
    if active_source.count(r"\index{") != 100 or active_target.count(r"\index{") != 100:
        errors.append("index-hook census differs from 100/100")
    if active_source.count(r"\df{") != 24 or active_target.count(r"\df{") != 24:
        errors.append("defined-term-hook census differs from 24/24")

    source_math: list[dict[str, object]] = []
    target_math: list[dict[str, object]] = []
    math_census: dict[str, dict[str, int]] = {}
    for name, text in (("source", source), ("target", target)):
        try:
            surfaces = extract_math(text)
        except ValueError as exc:
            errors.append(f"{name} math parser: {exc}")
            surfaces = []
        counts = Counter(str(surface["kind"]) for surface in surfaces)
        math_census[name] = {
            "inline": counts["inline"],
            "display": counts["display"],
            "equation": counts["equation"],
            "align": counts["align"],
            "total": len(surfaces),
        }
        active = strip_comments(text)
        raw_inline = len(re.findall(r"(?<!\\)\$", active)) // 2
        math_census[name]["raw_inline_delimiter_spans"] = raw_inline
        expected_math_census = {
            "source": {
                "inline": 969,
                "display": 71,
                "equation": 4,
                "align": 3,
                "total": 1_047,
                "raw_inline_delimiter_spans": 973,
            },
            "target": {
                "inline": 970,
                "display": 71,
                "equation": 4,
                "align": 3,
                "total": 1_048,
                "raw_inline_delimiter_spans": 974,
            },
        }
        if math_census[name] != expected_math_census[name]:
            errors.append(f"{name} active math census differs: {math_census[name]!r}")
        if active.count(r"\[") != active.count(r"\]"):
            errors.append(f"{name} display delimiter balance differs")
        if name == "source":
            source_math = surfaces
        else:
            target_math = surfaces

    math_differences: list[dict[str, object]] = []
    if len(source_math) == 1_047 and len(target_math) == 1_048:
        source_keys = [
            (surface["kind"], canonical_math(str(surface["value"])))
            for surface in source_math
        ]
        target_keys = [
            (surface["kind"], canonical_math(str(surface["value"])))
            for surface in target_math
        ]
        matcher = SequenceMatcher(a=source_keys, b=target_keys, autojunk=False)
        for tag, source_start, source_end, target_start, target_end in matcher.get_opcodes():
            if tag == "equal":
                continue
            source_slice = source_math[source_start:source_end]
            target_slice = target_math[target_start:target_end]
            source_lines_for_change = sorted({int(item["line"]) for item in source_slice})
            target_lines_for_change = sorted({int(item["line"]) for item in target_slice})
            classifications = [
                classification
                for classification, (start, end) in MATH_ALLOWED_RANGES.items()
                if any(start <= line <= end for line in source_lines_for_change + target_lines_for_change)
            ]
            math_differences.append(
                {
                    "operation": tag,
                    "source_ordinals": [source_start, source_end],
                    "target_ordinals": [target_start, target_end],
                    "source_lines": source_lines_for_change,
                    "target_lines": target_lines_for_change,
                    "source_values": [item["value"] for item in source_slice],
                    "target_values": [item["value"] for item in target_slice],
                    "classifications": classifications,
                }
            )
        unclassified = [item for item in math_differences if not item["classifications"]]
        if unclassified:
            errors.append(
                "math differs outside classified correction ranges: "
                + repr(
                    [
                        (item["operation"], item["source_lines"], item["target_lines"])
                        for item in unclassified[:30]
                    ]
                )
            )
    else:
        unclassified = []

    diagram_tokens = (r"\xy", r"\endxy", r"\xymatrix", r"\qtriangle", r"\Square", r"\hSquares")
    diagram_census = {
        "source": {token: active_source.count(token) for token in diagram_tokens},
        "target": {token: active_target.count(token) for token in diagram_tokens},
    }
    if diagram_census["source"] != diagram_census["target"]:
        errors.append(f"diagram token census differs: {diagram_census!r}")
    if active_source.count(r"\begin{bmatrix}") != 46 or active_target.count(r"\begin{bmatrix}") != 46:
        errors.append("bmatrix census differs from 46/46")

    if active_target.count(r"\begin{exer}") != 1:
        errors.append("formal exercise census differs from one")
    if active_target.count(r"\begin{proof}") != 22 or active_target.count(r"\begin{exam}") != 31:
        errors.append("proof/example census differs from 22/31")
    proof_hints = len(re.findall(r"\\begin\{proof\}\[\\emph\{Petunjuk untuk bukti\}\]", active_target))
    if proof_hints != 16:
        errors.append(f"proof-hint census differs from 16: {proof_hints}")
    if re.search(r"\\begin\{(?:answer|solution|hint)\}", active_target, re.I):
        errors.append("unsupported answer/solution/hint environment entered target")

    residue_pattern = re.compile(
        r"\b(?:Let|Suppose|Then|If|For every|For each|There exists|We say|We define|We write|"
        r"Notice that|Clearly|Recall that|The next|The preceding|The following|is called|"
        r"if and only if|See|where there|will be denoted|commutative semigroup under|"
        r"positive integers|nonzero algebra homomorphisms)\b",
        re.I,
    )
    residues = sorted(set(match.group(0) for match in residue_pattern.finditer(active_target)))
    if residues:
        errors.append(f"active English instructional residue: {residues!r}")
    for marker in ("Ã", "Â", "â€", "�", "C:\\Users\\", "/Users/", "/home/", "api_key", "access_token"):
        if marker in target or marker in master:
            errors.append(f"forbidden encoding/private/credential marker: {marker!r}")
    required_terms = (
        r"\df{serupa}",
        r"\df{ekuivalen secara uniter}",
        r"\df{ekuivalen Murray--von Neumann}",
        r"\df{isometri}",
        r"\df{grup Grothendieck}",
        r"\df{pemetaan Grothendieck}",
        r"\df{sifat pembatalan}",
        r"\df{ekuivalen secara stabil}",
        r"\df{topologi norma-titik}",
        r"\df{homotop}",
        r"\df{ekuivalen secara homotopi}",
        r"\df{kontraktibel}",
        r"\df{pemetaan skalar}",
        r"\df{elemen skalar}",
        r"\df{eksak terbelah}",
        r"\df{eksak separuh}",
        r"\df{barisan induktif}",
        r"\df{limit induktif}",
        r"\df{limit langsung}",
        r"\df{aljabar-$C^*$ berdimensi hingga secara aproksimatif}",
        r"\df{multiplisitas}",
        r"\df{diagram Bratteli}",
        r"\df{aljabar Fibonacci}",
        "aljabar CAR (CAR = Relasi Antikomutasi Kanonik)",
    )
    for anchor in required_terms:
        if anchor not in active_target:
            errors.append(f"required Indonesian terminology anchor missing: {anchor!r}")
    rejected_terms = re.compile(
        r"(?<!\\)\b(?:K-theory|equivalence relation|unitarily equivalent|Murray-von Neumann equivalent|"
        r"partial isometry|Grothendieck group|cancellation property|point-norm topology|"
        r"homotopically equivalent|contractible|scalar mapping|half exact|inductive limit|"
        r"approximately finite dimensional|multiplicity|Bratteli diagram)\b",
        re.I,
    )
    rejected_matches = sorted(set(match.group(0) for match in rejected_terms.finditer(active_target)))
    if rejected_matches:
        errors.append(f"rejected terminology remains: {rejected_matches!r}")

    expected_markers = [f"% SOURCE-CORRECTION: CH17-C{number:03d}" for number in range(1, 27)]
    actual_markers = re.findall(r"% SOURCE-CORRECTION: CH17-C\d{3}", target)
    if sorted(actual_markers) != sorted(expected_markers) or len(actual_markers) != 26:
        errors.append("correction-marker closure differs")

    try:
        ledger = json.loads(ledger_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"correction ledger unreadable: {exc}")
        ledger = {}
    records = ledger.get("records", []) if isinstance(ledger, dict) else []
    if ledger.get("schema_version") != "o008.source-corrections.v1" or ledger.get("unit_id") != "FAOA-2015-CH17":
        errors.append("correction ledger schema/unit binding differs")
    if ledger.get("status") != "adjudicated_and_applied" or ledger.get("record_count") != 26 or len(records) != 26:
        errors.append("correction ledger status/count differs")
    if ledger.get("math_surface_affecting_record_ids") != list(MATH_CORRECTION_RANGES):
        errors.append("ledger formula-affecting correction IDs differ")
    expected_ledger_source = {
        "path": "source/upstream/K0_functor.tex",
        "bytes": EXPECTED["source_bytes"],
        "logical_records": 1_362,
        "line_endings": "CRLF",
        "sha256": EXPECTED["source_sha256"],
    }
    expected_ledger_target = {
        "path": "source/id-ID/K0_functor-id.tex",
        "bytes": EXPECTED["target_bytes"],
        "logical_records": 1_362,
        "line_endings": "LF",
        "sha256": EXPECTED["target_sha256"],
    }
    if ledger.get("source") != expected_ledger_source or ledger.get("target") != expected_ledger_target:
        errors.append("correction ledger source/target binding differs")
    if records and ledger_bytes != (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8"):
        errors.append("correction ledger canonical serialization differs")
    ledger_ids: list[str] = []
    for number, record in enumerate(records, 1):
        record_id = f"FAOA-2015-CH17-CORR-{number:03d}"
        ledger_ids.append(str(record.get("id")))
        try:
            source_range = record["source_lines"]
            target_range = record["target_lines"]
            if record.get("id") != record_id or target_range != source_range:
                errors.append(f"ledger identity/range differs: {record_id}")
            start, end = source_range["start"], source_range["end"]
            source_snippet = normalize(source_lines, start, end)
            target_snippet = normalize(target_lines, start, end)
            if record.get("source_normalized_snippet") != source_snippet or record.get("target_normalized_snippet") != target_snippet:
                errors.append(f"ledger normalized snippet differs: {record_id}")
            if record.get("source_normalized_snippet_sha256") != digest(source_snippet.encode("utf-8")):
                errors.append(f"ledger source snippet hash differs: {record_id}")
            if record.get("target_normalized_snippet_sha256") != digest(target_snippet.encode("utf-8")):
                errors.append(f"ledger target snippet hash differs: {record_id}")
            marker = f"% SOURCE-CORRECTION: CH17-C{number:03d}"
            marker_line = target[: target.index(marker)].count("\n") + 1
            if record.get("target_marker") != marker or record.get("target_marker_line") != marker_line or not start <= marker_line <= end:
                errors.append(f"ledger correction marker binding differs: {record_id}")
            for anchor in record.get("source_required_anchors", []):
                if anchor not in source_snippet:
                    errors.append(f"ledger source anchor missing: {record_id} {anchor!r}")
            for anchor in record.get("forbidden_target_anchors", []):
                if anchor in target:
                    errors.append(f"ledger forbidden target anchor remains: {record_id} {anchor!r}")
            for anchor in record.get("required_target_anchors", []):
                if anchor not in target_snippet:
                    errors.append(f"ledger required target anchor missing: {record_id} {anchor!r}")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"ledger record malformed: {record_id}: {exc}")
    if ledger_ids != [f"FAOA-2015-CH17-CORR-{number:03d}" for number in range(1, 27)]:
        errors.append("correction ledger ID order differs")

    includes = re.findall(r"\\include\{([^}]+)\}", master)
    if includes != EXPECTED_INCLUDES:
        errors.append(f"master include sequence differs: {includes!r}")
    required_master = (
        "pdfauthor={John M Erdman}",
        r"\author{John M. Erdman",
        "Unit Pembaca Kumulatif Bab 1--17",
        "batas produksi Bab 1--17",
        "Bab 1 sampai Bab 17",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "Creative Commons",
        "CC BY-SA 4.0",
        "kredit John M. Erdman dan kontributor komponen tetap dipertahankan",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University",
        r"\input{DIAGXY.TEX}",
        r"\include{K0_functor-id}",
    )
    for anchor in required_master:
        if anchor not in master:
            errors.append(f"required master rights/provenance/author anchor missing: {anchor!r}")
    if master.count("OpenAI Codex gpt-5.6-sol, Ultra") != 2:
        errors.append("exact model-provenance occurrence count differs from two")
    for forbidden in ("TABLE.TEX", "Wiener_quote", "by-sa.eps", "by-sa.pdf"):
        if forbidden in master:
            errors.append(f"excluded component entered master: {forbidden}")

    all_labels: set[str] = set()
    for include in includes:
        path = MASTER.parent / f"{include}.tex"
        if not path.is_file():
            errors.append(f"included target missing: {path.relative_to(ROOT).as_posix()}")
            continue
        all_labels.update(re.findall(r"\\label\{([^}]+)\}", path.read_text(encoding="utf-8")))
    unresolved_refs = [value for value in target_refs if value not in all_labels]
    if unresolved_refs:
        errors.append(f"unresolved cumulative target references: {unresolved_refs!r}")
    bib = (MASTER.parent / "functional_analysis_op_algs_bib.bib").read_text(encoding="ascii")
    bib_keys = set(re.findall(r"@[A-Za-z]+\s*\{\s*([^,\s]+)", bib))
    unresolved_cites = [value for value in target_cites if value not in bib_keys]
    if unresolved_cites:
        errors.append(f"unresolved bibliography keys: {unresolved_cites!r}")

    report = {
        "schema_version": "o008.ch17-translation-qa.v1",
        "unit_id": "FAOA-2015-CH17",
        "status": "pass" if not errors else "fail",
        "identities": identities,
        "structure": {
            "source_records": len(source_lines),
            "target_records": len(target_lines),
            "sections": len(target_sections),
            "environment_openings": len(target_begins),
            "reader_semantic_environment_openings": semantic_openings,
            "environment_counts": dict(sorted(Counter(target_begins).items())),
            "labels": len(target_labels),
            "references": len(target_refs),
            "citations": len(target_cites),
            "index_hooks": active_target.count(r"\index{"),
            "defined_term_hooks": active_target.count(r"\df{"),
            "examples": active_target.count(r"\begin{exam}"),
            "exercises": active_target.count(r"\begin{exer}"),
            "proofs": active_target.count(r"\begin{proof}"),
            "proof_hints": proof_hints,
            "bmatrices": active_target.count(r"\begin{bmatrix}"),
            "diagram_tokens": diagram_census,
        },
        "math": {
            "active_census": math_census,
            "classified_differences": math_differences,
            "unclassified_differences": len([item for item in math_differences if not item["classifications"]]),
            "classified_correction_ranges": MATH_ALLOWED_RANGES,
        },
        "corrections": {
            "records": len(records),
            "class_counts": ledger.get("class_counts", {}),
            "math_surface_affecting_record_ids": ledger.get("math_surface_affecting_record_ids", []),
            "ledger_sha256": digest(ledger_bytes),
        },
        "linkage": {
            "cumulative_labels": len(all_labels),
            "unresolved_references": unresolved_refs,
            "unresolved_citations": unresolved_cites,
        },
        "rights_and_provenance": {
            "author": "John M. Erdman",
            "license": "CC BY-SA 4.0",
            "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
            "excluded_components_absent": True,
            "nonendorsement_present": True,
        },
        "errors": errors,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
