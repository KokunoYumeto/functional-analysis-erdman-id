#!/usr/bin/env python3
"""Locked structural, mathematical, language, rights, and linkage QA for CH16."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "extensions.tex"
TARGET = ROOT / "source" / "id-ID" / "extensions-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch16.tex"
LEDGER = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH16.json"
REPORT = ROOT / "qa" / "ch16-translation-report.json"

EXPECTED = {
    "source_bytes": 42_614,
    "source_sha256": "e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318",
    "target_bytes": 43_804,
    "target_sha256": "59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3",
    "master_bytes": 10_679,
    "master_sha256": "6e528b0193d3179b58e44169430d043fa5399f7c860f09d832eb3ccd954a5388",
}
EXPECTED_ENVIRONMENTS = Counter(
    {
        "bmatrix": 12,
        "center": 1,
        "conv": 1,
        "cor": 6,
        "defn": 21,
        "enumerate": 1,
        "equation": 4,
        "exam": 15,
        "notn": 3,
        "proof": 31,
        "prop": 38,
        "rem": 1,
        "thm": 8,
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
]
EXPECTED_CORRECTION_SPECS = [
    (f"FAOA-2015-CH16-CORR-{number:03d}", line_range, classification, affects_math)
    for number, line_range, classification, affects_math in (
        (1, (13, 15), "MECHANICAL_TEX_SOURCE_REPAIR", False),
        (2, (42, 58), "MATHEMATICAL_SOURCE_REPAIR", True),
        (3, (61, 63), "FORMAL_SCOPE_CLARIFICATION", False),
        (4, (254, 258), "MATHEMATICAL_NOTATION_SOURCE_REPAIR", True),
        (5, (254, 258), "MECHANICAL_PROSE_SOURCE_REPAIR", False),
        (6, (298, 305), "MAP_IDENTITY_SOURCE_REPAIR", True),
        (7, (312, 314), "BIBLIOGRAPHIC_TYPO_SOURCE_REPAIR", False),
        (8, (340, 357), "MATHEMATICAL_NOTATION_SOURCE_REPAIR", True),
        (9, (405, 411), "STALE_LOCATOR_SOURCE_REPAIR", False),
        (10, (444, 449), "DIAGRAM_TYPO_SOURCE_REPAIR", True),
        (11, (547, 551), "MATHEMATICAL_NOTATION_SOURCE_REPAIR", True),
        (12, (559, 566), "MISSING_VARIABLE_SOURCE_REPAIR", True),
        (13, (620, 634), "INDEX_TYPO_SOURCE_REPAIR", False),
        (14, (886, 891), "MISSING_THEOREM_HYPOTHESIS", False),
        (15, (909, 924), "MATHEMATICAL_CATEGORY_SOURCE_REPAIR", True),
    )
]
EXPECTED_CLASS_COUNTS = {
    "MECHANICAL_TEX_SOURCE_REPAIR": 1,
    "MATHEMATICAL_SOURCE_REPAIR": 1,
    "FORMAL_SCOPE_CLARIFICATION": 1,
    "MATHEMATICAL_NOTATION_SOURCE_REPAIR": 3,
    "MECHANICAL_PROSE_SOURCE_REPAIR": 1,
    "MAP_IDENTITY_SOURCE_REPAIR": 1,
    "BIBLIOGRAPHIC_TYPO_SOURCE_REPAIR": 1,
    "STALE_LOCATOR_SOURCE_REPAIR": 1,
    "DIAGRAM_TYPO_SOURCE_REPAIR": 1,
    "MISSING_VARIABLE_SOURCE_REPAIR": 1,
    "INDEX_TYPO_SOURCE_REPAIR": 1,
    "MISSING_THEOREM_HYPOTHESIS": 1,
    "MATHEMATICAL_CATEGORY_SOURCE_REPAIR": 1,
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_comments(text: str) -> str:
    """Strip TeX comments while retaining record topology."""

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
    """Return active top-level inline/display/equation surfaces in source order."""

    active = strip_comments(text)
    surfaces: list[dict[str, object]] = []
    index = 0
    equation_open = r"\begin{equation}"
    equation_close = r"\end{equation}"
    while index < len(active):
        if active.startswith(equation_open, index):
            start = index + len(equation_open)
            end = active.find(equation_close, start)
            if end < 0:
                raise ValueError("unclosed equation environment")
            kind = "equation"
            next_index = end + len(equation_close)
        elif active.startswith(r"\[", index):
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


def transformed_source_math(source_math: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Apply the exhaustive, source-ordinal-bound CH16 math transformation program."""

    operations: dict[int, tuple[int, list[tuple[str, str]], str, str | None]] = {
        29: (1, [("inline", r"S - U^*TU")], "mathematical_source_repair", "FAOA-2015-CH16-CORR-002"),
        37: (1, [("inline", r"S = U^*TU")], "mathematical_source_repair", "FAOA-2015-CH16-CORR-002"),
        74: (1, [("inline", r"\norm{T_\phi} \le \norm {\phi}_\infty")], "semantic_tex_normalization", None),
        141: (
            1,
            [("display", r"\ofml T = \{ T_\phi + K\colon \phi \in \fml C(\T) \text{ dan } K \in \ofml K(H^2)\} \,.")],
            "localized_math_text",
            None,
        ),
        149: (
            1,
            [("inline", r"\pi \circ T\colon \fml C(\T) \sto \ofml Q(H^2)\colon \phi \mapsto \pi(T_\phi)")],
            "mathematical_source_repair",
            "FAOA-2015-CH16-CORR-004",
        ),
        179: (1, [("inline", "T")], "mathematical_source_repair", "FAOA-2015-CH16-CORR-006"),
        198: (
            1,
            [("inline", r"\pi_1(\C \setminus \{0\})")],
            "mathematical_source_repair",
            "FAOA-2015-CH16-CORR-008",
        ),
        200: (
            1,
            [("inline", r"\pi_1(\C \setminus \{0\})")],
            "mathematical_source_repair",
            "FAOA-2015-CH16-CORR-008",
        ),
        244: (
            1,
            [(
                "equation",
                r"\label{005431ii} \xymatrix{ \vc 0\ar[r] & \ofml K\ar[r]^\iota\ar[d]_{\psi|_{\ofml K}} & \ofml E\ar[r]^\phi\ar[d]^\psi & A\ar[r]\ar@{=}[d] & \vc 0 \\ \vc 0\ar[r] & \ofml K\ar[r]^\iota & \ofml E\,'\ar[r]^{\phi\,'} & A\ar[r] & \vc 0 }",
            )],
            "mathematical_source_repair",
            "FAOA-2015-CH16-CORR-010",
        ),
        353: (
            1,
            [("inline", r"\pi_2\colon \ofml E \sto A\colon T \oplus a \mapsto a")],
            "mathematical_source_repair",
            "FAOA-2015-CH16-CORR-011",
        ),
        365: (
            5,
            [("inline", "j=1,2"), ("inline", r"\tau_j\colon A \sto \ofml Q(H)"), ("inline", r"*\,")],
            "mathematical_source_repair_restructure",
            "FAOA-2015-CH16-CORR-012",
        ),
        372: (
            1,
            [("inline", "U"), ("inline", "H")],
            "mathematical_source_repair_insert",
            "FAOA-2015-CH16-CORR-012",
        ),
        542: (1, [("inline", "j")], "localized_ordinal", None),
        543: (1, [("inline", "k")], "localized_ordinal", None),
        659: (1, [], "mathematical_source_repair_delete", "FAOA-2015-CH16-CORR-015"),
    }
    expected: list[dict[str, object]] = []
    transformations: list[dict[str, object]] = []
    source_index = 0
    while source_index < len(source_math):
        operation = operations.get(source_index)
        if operation is None:
            expected.append(dict(source_math[source_index]))
            source_index += 1
            continue
        consume, outputs, kind, correction = operation
        source_slice = source_math[source_index : source_index + consume]
        target_start = len(expected)
        target_line = int(source_slice[0]["line"])
        for output_kind, value in outputs:
            expected.append({"kind": output_kind, "line": target_line, "value": value})
        transformations.append(
            {
                "kind": kind,
                "source_ordinals": list(range(source_index, source_index + consume)),
                "target_ordinals": list(range(target_start, target_start + len(outputs))),
                "source_values": [surface["value"] for surface in source_slice],
                "target_values": [value for _, value in outputs],
                "correction": correction,
            }
        )
        source_index += consume
    return expected, transformations


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
    identities = {
        "source_bytes": len(source_bytes),
        "source_sha256": digest(source_bytes),
        "target_bytes": len(target_bytes),
        "target_sha256": digest(target_bytes),
        "master_bytes": len(master_bytes),
        "master_sha256": digest(master_bytes),
    }
    for key, expected in EXPECTED.items():
        if identities[key] != expected:
            errors.append(f"identity mismatch {key}: {identities[key]!r} != {expected!r}")
    if source_bytes.count(b"\r\n") != 1_000 or source_bytes.count(b"\n") != 1_000:
        errors.append("source CRLF topology differs")
    if b"\r" in target_bytes or target_bytes.count(b"\n") != 1_000:
        errors.append("target LF topology differs")
    if b"\r" in master_bytes or master_bytes.count(b"\n") != 345:
        errors.append("master LF topology differs")
    if any(data.startswith(b"\xef\xbb\xbf") for data in (target_bytes, master_bytes)):
        errors.append("UTF-8 BOM is forbidden")

    source = source_bytes.decode("ascii").replace("\r\n", "\n")
    target = target_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")
    active_source = strip_comments(source)
    active_target = strip_comments(target)
    source_lines = source.splitlines()
    target_lines = target.splitlines()
    if len(source_lines) != 1_000 or len(target_lines) != 1_000:
        errors.append("logical record count differs from 1000/1000")
    if not source.rstrip().endswith(r"\endinput") or not target.rstrip().endswith(r"\endinput"):
        errors.append("terminal endinput closure differs")

    source_sections = re.findall(r"\\section\{([^}]*)\}", active_source)
    target_sections = re.findall(r"\\section\{([^}]*)\}", active_target)
    if source_sections != [
        "Essentially Normal Operators",
        "Toeplitz Operators",
        "Addition of Extensions",
        "Completely Positive Maps",
    ]:
        errors.append(f"source section sequence differs: {source_sections!r}")
    if target_sections != [
        "Operator Normal secara Esensial",
        "Operator Toeplitz",
        "Penjumlahan Ekstensi",
        "Pemetaan Positif Lengkap",
    ]:
        errors.append(f"target section sequence differs: {target_sections!r}")
    if not active_source.startswith(r"\chapter{EXTENSIONS}"):
        errors.append("source chapter opening differs")
    if not active_target.startswith(r"\chapter{EKSTENSI}"):
        errors.append("target chapter opening differs")
    if r"%\section{Tensor Products of $C^*$-algebras}" not in source:
        errors.append("commented prospective tensor-product heading missing from source")
    if r"%\section{Hasil Kali Tensor Aljabar-$C^*$}" not in target:
        errors.append("localized prospective tensor-product heading not preserved inactive in target")
    if "Hasil Kali Tensor Aljabar" in active_target:
        errors.append("prospective tensor-product heading became active in target")

    source_begins = re.findall(r"\\begin\{([^}]+)\}", active_source)
    source_ends = re.findall(r"\\end\{([^}]+)\}", active_source)
    target_begins = re.findall(r"\\begin\{([^}]+)\}", active_target)
    target_ends = re.findall(r"\\end\{([^}]+)\}", active_target)
    if len(source_begins) != 142 or len(target_begins) != 142:
        errors.append(f"environment opening count differs from 142/142: {len(source_begins)}/{len(target_begins)}")
    if Counter(source_begins) != EXPECTED_ENVIRONMENTS or Counter(target_begins) != EXPECTED_ENVIRONMENTS:
        errors.append("environment census differs")
    if source_begins != target_begins or source_ends != target_ends:
        errors.append("source/target environment topology differs")
    errors.extend(f"source {value}" for value in validate_environment_stack(active_source))
    errors.extend(f"target {value}" for value in validate_environment_stack(active_target))
    semantic_openings = len([value for value in target_begins if value not in {"bmatrix", "center", "enumerate", "equation"}])
    if semantic_openings != 124:
        errors.append(f"reader-semantic environment count differs: {semantic_openings}")

    source_labels = re.findall(r"\\label\{([^}]+)\}", active_source)
    target_labels = re.findall(r"\\label\{([^}]+)\}", active_target)
    source_refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", active_source)
    target_refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", active_target)
    source_cites = extract_cites(active_source)
    target_cites = extract_cites(active_target)
    for name, source_values, target_values, expected_count in (
        ("labels", source_labels, target_labels, 36),
        ("references", source_refs, target_refs, 28),
        ("citations", source_cites, target_cites, 59),
    ):
        if len(source_values) != expected_count or len(target_values) != expected_count:
            errors.append(f"{name} count differs from {expected_count}/{expected_count}")
        if source_values != target_values:
            errors.append(f"{name} ordered topology differs")
    if len(set(target_labels)) != 36:
        errors.append("target labels are not 36 unique identifiers")
    if active_source.count(r"\index{") != 107 or active_target.count(r"\index{") != 107:
        errors.append("index-hook census differs from 107/107")
    if active_source.count(r"\df{") != 29 or active_target.count(r"\df{") != 29:
        errors.append("defined-term-hook census differs from 29/29")
    if active_source.count(r"\tag{1}") != 1 or active_target.count(r"\tag{1}") != 1:
        errors.append("manual equation tag (1) differs")

    raw_census: dict[str, dict[str, int]] = {}
    source_math: list[dict[str, object]] = []
    target_math: list[dict[str, object]] = []
    for name, text, expected in (("source", source, (672, 26, 4, 702)), ("target", target, (670, 26, 4, 700))):
        try:
            surfaces = extract_math(text)
        except ValueError as exc:
            errors.append(f"{name} math parser: {exc}")
            surfaces = []
        counts = Counter(str(surface["kind"]) for surface in surfaces)
        census = {
            "inline": counts["inline"],
            "display": counts["display"],
            "equation": counts["equation"],
            "total": len(surfaces),
        }
        raw_census[name] = census
        if tuple(census[key] for key in ("inline", "display", "equation", "total")) != expected:
            errors.append(f"{name} active math census differs: {census!r}")
        active = strip_comments(text)
        if active.count(r"\[") != active.count(r"\]"):
            errors.append(f"{name} display delimiter balance differs")
        brace_open = len(re.findall(r"(?<!\\)\{", active))
        brace_close = len(re.findall(r"(?<!\\)\}", active))
        if brace_open != brace_close:
            errors.append(f"{name} unescaped brace balance differs: {brace_open}/{brace_close}")
        if name == "source":
            source_math = surfaces
        else:
            target_math = surfaces

    transformations: list[dict[str, object]] = []
    if len(source_math) == 702 and len(target_math) == 700:
        expected_math, transformations = transformed_source_math(source_math)
        comparable_expected = [(entry["kind"], entry["value"]) for entry in expected_math]
        comparable_target = [(entry["kind"], entry["value"]) for entry in target_math]
        if comparable_expected != comparable_target:
            limit = min(len(comparable_expected), len(comparable_target))
            mismatch = [index for index in range(limit) if comparable_expected[index] != comparable_target[index]]
            errors.append(f"math differs outside classified transformation program: {mismatch[:20]!r}")
    if len(transformations) != 15:
        errors.append(f"classified math transformation count differs from 15: {len(transformations)}")
    correction_formula_ids = sorted({str(item["correction"]) for item in transformations if item["correction"]})
    expected_formula_ids = [
        "FAOA-2015-CH16-CORR-002",
        "FAOA-2015-CH16-CORR-004",
        "FAOA-2015-CH16-CORR-006",
        "FAOA-2015-CH16-CORR-008",
        "FAOA-2015-CH16-CORR-010",
        "FAOA-2015-CH16-CORR-011",
        "FAOA-2015-CH16-CORR-012",
        "FAOA-2015-CH16-CORR-015",
    ]
    if correction_formula_ids != expected_formula_ids:
        errors.append(f"formula-affecting correction closure differs: {correction_formula_ids!r}")

    if active_target.count(r"\begin{exer}") != 0:
        errors.append("unsupported formal exercise entered target")
    if active_target.count(r"\begin{proof}") != 31 or active_target.count(r"\begin{exam}") != 15:
        errors.append("proof/example census differs from 31/15")
    if re.search(r"\\begin\{(?:answer|solution|hint)\}", active_target):
        errors.append("unsupported answer/solution/hint environment entered target")
    if "Hint for proof" in active_source or "Petunjuk bukti" in active_target:
        errors.append("unexpected explicit proof hint entered source/target")

    residue_pattern = re.compile(
        r"\b(?:Let|Suppose|Then|If|Every|For every|For each|There exists|We say|We define|We write|"
        r"Notice that|Clearly|This is|is called|if and only if|See|Compare|Recall|The next|"
        r"The preceding|The following|from now on|completely positive lifting)\b",
        re.I,
    )
    residues = sorted(set(match.group(0) for match in residue_pattern.finditer(active_target)))
    if residues:
        errors.append(f"active English instructional residue: {residues!r}")
    for marker in ("Ã", "Â", "â€", "�", "C:\\Users\\", "/Users/", "/home/", "api_key", "access_token"):
        if marker in target or marker in master:
            errors.append(f"forbidden encoding/private/credential marker: {marker!r}")
    required_terms = (
        r"\df{spektrum esensial}",
        r"\df{ekuivalen uniter secara esensial}",
        r"\df{kompalen}",
        r"\df{normal secara esensial}",
        r"\df{swaadjoin secara esensial}",
        r"\df{operator Toeplitz}",
        r"\df{matriks Toeplitz}",
        r"\df{aljabar Toeplitz}",
        r"\df{ekstensi Toeplitz}",
        r"\df{bilangan lilit}",
        r"\df{konjugasi}",
        r"\df{tarik balik",
        r"\df{operator Toeplitz abstrak}",
        r"\df{ekstensi Toeplitz abstrak",
        r"\df{semiterbelah}",
        r"\df{positif}",
        r"\df{unit matriks standar}",
        r"\df{$n$-positif}",
        r"\df{positif lengkap}",
        r"\df{terbatas lengkap}",
        r"\df{nuklir}",
        "pemetaan linear beridentitas dan positif lengkap",
        "pengangkatan positif lengkap",
        "praurutan",
        "urutan parsial",
        "aljabar Calkin",
    )
    for anchor in required_terms:
        if anchor not in active_target:
            errors.append(f"required Indonesian terminology anchor missing: {anchor!r}")
    rejected_terms = re.compile(
        r"(?<!\\)\b(?:essential spectrum|essentially normal|self-adjoint|winding number|fundamental group|"
        r"pullback|lifting|completely positive|completely bounded|nuclear|semisplit|range)\b",
        re.I,
    )
    rejected_matches = sorted(set(match.group(0) for match in rejected_terms.finditer(active_target)))
    if rejected_matches:
        errors.append(f"rejected terminology remains: {rejected_matches!r}")

    required_corrections = (
        r"\begin{prop} Jika $T$",
        r"$S - U^*TU$",
        "$S =\nU^*TU$",
        "terpisahkan berdimensi tak hingga",
        r"\sto \ofml Q(H^2)\colon \phi",
        r"menyebut pemetaan $T$ sebagai",
        "teorema 7.26",
        r"$\pi_1(\C \setminus \{0\})$",
        "mulai bagian Penjumlahan Ekstensi",
        r"\psi|_{\ofml K}",
        r"\pi_2\colon \ofml E \sto A\colon",
        "operator uniter $U$ pada $H$",
        r"\index{abstrak!operator!Toeplitz}",
        r"\index{abstrak!ekstensi!Toeplitz}",
        "pemetaan linear beridentitas dan positif lengkap",
        r"monomorfisme-$*\,$ beridentitas $\tau",
        r"pemetaan linear beridentitas dan positif lengkap $\wt\tau",
    )
    for anchor in required_corrections:
        if anchor not in target:
            errors.append(f"required correction anchor missing: {anchor!r}")
    for forbidden in (
        "$S - UTU^*$",
        "$S =\nUTU^*$",
        r"\sto Q(H^2)\colon \phi",
        r"menyebut pemetaan $\beta$ sebagai",
        "teorema 7.2 6",
        r"$\pi^1(\C \setminus 0)$",
        "setelah bagian 9.2",
        r"\psi|_{\ofml K)}",
        r"\pi_2\colon \ofml E \sto \ofml A\colon",
        "Topelitz",
        r"homomorfisme-$*\,$ beridentitas $\wt\tau",
    ):
        if forbidden in target:
            errors.append(f"forbidden source defect remains: {forbidden!r}")

    includes = re.findall(r"\\include\{([^}]+)\}", master)
    if includes != EXPECTED_INCLUDES:
        errors.append(f"master include sequence differs: {includes!r}")
    required_master = (
        "pdfauthor={John M Erdman}",
        r"\author{John M. Erdman",
        "Unit Pembaca Kumulatif Bab 1--16",
        "batas produksi Bab 1--16",
        "Bab 1 sampai Bab 16",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "Creative Commons",
        "CC BY-SA 4.0",
        "kredit John M. Erdman dan kontributor komponen tetap dipertahankan",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University",
        r"\input{DIAGXY.TEX}",
        r"\include{extensions-id}",
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

    try:
        ledger_bytes = LEDGER.read_bytes()
        ledger = json.loads(ledger_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"correction ledger unreadable: {exc}")
        ledger_bytes = b""
        ledger = {}
    records = ledger.get("records", []) if isinstance(ledger, dict) else []
    if ledger.get("schema_version") != "o008.source-corrections.v1" or ledger.get("unit_id") != "FAOA-2015-CH16":
        errors.append("correction ledger schema/unit binding differs")
    if ledger.get("status") != "adjudicated_and_applied" or ledger.get("record_count") != 15:
        errors.append("correction ledger status/count differs")
    if ledger.get("class_counts") != EXPECTED_CLASS_COUNTS:
        errors.append("correction ledger class census differs")
    expected_ledger_source = {
        "path": "source/upstream/extensions.tex",
        "bytes": EXPECTED["source_bytes"],
        "logical_records": 1_000,
        "line_endings": "CRLF",
        "sha256": EXPECTED["source_sha256"],
    }
    expected_ledger_target = {
        "path": "source/id-ID/extensions-id.tex",
        "bytes": EXPECTED["target_bytes"],
        "logical_records": 1_000,
        "line_endings": "LF",
        "sha256": EXPECTED["target_sha256"],
    }
    if ledger.get("source") != expected_ledger_source or ledger.get("target") != expected_ledger_target:
        errors.append("correction ledger source/target binding differs")
    if records and ledger_bytes != (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8"):
        errors.append("correction ledger canonical serialization differs")
    actual_specs: list[tuple[object, object, object, object]] = []
    for record in records:
        try:
            source_range = record["source_lines"]
            target_range = record["target_lines"]
            spec = (
                record.get("id"),
                (source_range["start"], source_range["end"]),
                record.get("classification"),
                record.get("affects_math"),
            )
            actual_specs.append(spec)
            if target_range != source_range:
                errors.append(f"ledger source/target record range differs: {record.get('id')}")
            source_snippet = normalize(source_lines, source_range["start"], source_range["end"])
            target_snippet = normalize(target_lines, target_range["start"], target_range["end"])
            if record.get("source_normalized_snippet") != source_snippet:
                errors.append(f"ledger source snippet differs: {record.get('id')}")
            if record.get("target_normalized_snippet") != target_snippet:
                errors.append(f"ledger target snippet differs: {record.get('id')}")
            if record.get("source_normalized_snippet_sha256") != digest(source_snippet.encode("utf-8")):
                errors.append(f"ledger source snippet hash differs: {record.get('id')}")
            if record.get("target_normalized_snippet_sha256") != digest(target_snippet.encode("utf-8")):
                errors.append(f"ledger target snippet hash differs: {record.get('id')}")
            for anchor in record.get("source_required_anchors", []):
                if anchor not in source:
                    errors.append(f"ledger source anchor missing: {record.get('id')} {anchor!r}")
            for anchor in record.get("forbidden_target_anchors", []):
                if anchor in target:
                    errors.append(f"ledger forbidden target anchor remains: {record.get('id')} {anchor!r}")
            for anchor in record.get("required_target_anchors", []):
                if anchor not in target:
                    errors.append(f"ledger required target anchor missing: {record.get('id')} {anchor!r}")
        except (KeyError, TypeError) as exc:
            errors.append(f"ledger record malformed: {record!r}: {exc}")
    if actual_specs != EXPECTED_CORRECTION_SPECS:
        errors.append(f"correction ledger identity/order/classification differs: {actual_specs!r}")
    if ledger.get("math_surface_affecting_record_ids") != expected_formula_ids:
        errors.append("ledger formula-affecting correction IDs differ")

    report = {
        "schema_version": "o008.ch16-translation-qa.v1",
        "unit_id": "FAOA-2015-CH16",
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
            "manual_equation_tags": active_target.count(r"\tag{1}"),
            "examples": active_target.count(r"\begin{exam}"),
            "exercises": active_target.count(r"\begin{exer}"),
            "proofs": active_target.count(r"\begin{proof}"),
            "proof_hints": 0,
        },
        "math": {
            "active_census": raw_census,
            "classified_transformations": transformations,
            "formula_affecting_correction_ids": correction_formula_ids,
            "unclassified_differences": 0 if not any("math differs outside" in error for error in errors) else None,
        },
        "corrections": {
            "records": len(records),
            "class_counts": ledger.get("class_counts", {}),
            "ledger_sha256": digest(ledger_bytes) if ledger_bytes else None,
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
