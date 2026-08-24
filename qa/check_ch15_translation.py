#!/usr/bin/env python3
"""Locked structural, mathematical, language, rights, and linkage QA for CH15."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "fredholm_theory.tex"
TARGET = ROOT / "source" / "id-ID" / "fredholm_theory-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch15.tex"
LEDGER = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH15.json"
REPORT = ROOT / "qa" / "ch15-translation-report.json"

EXPECTED = {
    "source_bytes": 16_977,
    "source_sha256": "0ef2e5be3c716a099e8609a84528d77ad6387ec531c52f9890d4e34175c57d91",
    "target_bytes": 17_672,
    "target_sha256": "174b1ad2557f7dfa10e8171bd7482d907f858389b509f4d55de9cc785e2b43ba",
    "master_bytes": 10_541,
    "master_sha256": "f2df36c70dcca86f44687efe450ea46a5611be2d1170a9ded16dbfbfcdb73a33",
}
EXPECTED_ENVIRONMENTS = Counter(
    {
        "align": 6,
        "cor": 2,
        "defn": 6,
        "enumerate": 4,
        "exam": 8,
        "lem": 3,
        "notn": 1,
        "proof": 13,
        "prop": 16,
        "thm": 1,
    }
)
EXPECTED_LABELS = [
    "004011",
    "004011i",
    "004011ii",
    "004011iii",
    "004011iv",
    "004011v",
    "004011vi",
    "004031",
    "004031i",
    "004031ii",
    "004031iii",
    "004031iv",
    "004031v",
    "004031vi",
    "004033",
    "004034",
    "0040343",
    "004066",
    "004071",
    "00411",
    "00413",
    "004352",
    "0044125",
    "0044128",
    "004413",
    "004432",
    "004433",
    "004712",
    "004724",
    "004725",
    "0047253",
    "004735",
    "K002011",
]
EXPECTED_REFS = [
    "004011iii",
    "004011iv",
    "004011i",
    "004011ii",
    "004031iii",
    "004031iv",
    "004031i",
    "004031ii",
    "004031",
    "sec_onbases",
    "004033",
    "004066",
    "004071",
    "004066",
    "0040343",
    "0040343",
    "001902",
    "004432",
    "004433",
    "0044125",
    "0044128",
    "004413",
    "004724",
    "0044125",
    "004712",
    "004725",
    "cor2_Neumann_series",
]
EXPECTED_CITES = [
    "Conway:1990",
    "Arveson:2002",
    "Blackadar:2006",
    "Douglas:1972",
    "HigsonR:2000",
    "Wegge-Olsen:1993",
    "Pedersen:1995",
    "Wegge-Olsen:1993",
    "Pedersen:1995",
    "Wegge-Olsen:1993",
    "Douglas:1972",
    "Wegge-Olsen:1993",
    "HigsonR:2000",
    "Pedersen:1995",
    "Wegge-Olsen:1993",
    "Wegge-Olsen:1993",
    "Wegge-Olsen:1993",
]
EXPECTED_SOURCE_TERMS = [
    "Riesz-Schauder",
    "cokernel",
    "codimension",
    "Calkin algebra",
    "Fredholm operator",
    "Fredholm index",
    "index",
    "path",
    "connected by a path",
    "homotopic in~$X$",
    "path components",
]
EXPECTED_TARGET_TERMS = [
    "operator Riesz--Schauder",
    "kokernel",
    "kodimensi",
    "aljabar Calkin",
    "operator Fredholm",
    "indeks Fredholm",
    "indeks",
    "lintasan",
    "terhubung oleh lintasan",
    "homotop dalam~$X$",
    "komponen lintasan",
]
EXPECTED_TAGS = ["1", "2", "3", "4", "5", "6", "1'", "2'", "3'", "4'", "5'", "6'"]
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
]
EXPECTED_CORRECTION_SPECS = [
    (f"FAOA-2015-CH15-CORR-{number:03d}", source_range, target_range, classification, affects_math)
    for number, source_range, target_range, classification, affects_math in (
        (1, (10, 32), (10, 32), "MATHEMATICAL_SOURCE_REPAIR", True),
        (2, (43, 66), (43, 66), "MATHEMATICAL_SOURCE_REPAIR", True),
        (3, (72, 81), (72, 81), "MATHEMATICAL_SOURCE_REPAIR", True),
        (4, (101, 106), (101, 106), "MATHEMATICAL_SOURCE_REPAIR", True),
        (5, (123, 125), (123, 125), "MATHEMATICAL_SOURCE_REPAIR", True),
        (6, (150, 157), (150, 157), "MATHEMATICAL_SOURCE_REPAIR", False),
        (7, (247, 252), (247, 252), "MECHANICAL_PROSE_SOURCE_REPAIR", False),
        (8, (268, 270), (268, 270), "FORMAL_SCOPE_CLARIFICATION", False),
        (9, (300, 303), (300, 303), "MATHEMATICAL_SOURCE_REPAIR", False),
    )
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_cites(text: str) -> list[str]:
    keys: list[str] = []
    for argument in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", text):
        keys.extend(value.strip() for value in argument.split(",") if value.strip())
    return keys


def extract_top_level_math(text: str) -> list[str]:
    """Return ordered top-level inline, display, and whole-align math surfaces."""

    surfaces: list[str] = []
    index = 0
    align_open = r"\begin{align}"
    align_close = r"\end{align}"
    while index < len(text):
        if text.startswith(align_open, index):
            end = text.find(align_close, index + len(align_open))
            if end < 0:
                raise ValueError("unclosed align environment")
            surfaces.append(text[index + len(align_open) : end])
            index = end + len(align_close)
            continue
        if text.startswith(r"\[", index):
            end = text.find(r"\]", index + 2)
            if end < 0:
                raise ValueError("unclosed display math")
            surfaces.append(text[index + 2 : end])
            index = end + 2
            continue
        if text[index] == "$" and (index == 0 or text[index - 1] != "\\"):
            end = index + 1
            while end < len(text):
                if text[end] == "$" and text[end - 1] != "\\":
                    break
                end += 1
            if end >= len(text):
                raise ValueError("unclosed inline math")
            surfaces.append(text[index + 1 : end])
            index = end + 1
            continue
        index += 1
    return surfaces


def transformed_source_math(source_math: list[str]) -> tuple[list[str], list[dict[str, object]]]:
    expected = list(source_math)
    transformations: list[dict[str, object]] = []

    expected.insert(0, r"\lambda \in \C\setminus\{0\}")
    transformations.append(
        {
            "kind": "mathematical_source_repair_insert",
            "target_index": 0,
            "target": expected[0],
            "correction": "FAOA-2015-CH15-CORR-001",
        }
    )
    for index in (3, 8, 13, 20, 25, 30):
        old = expected[index]
        if r"\text{ and}" not in old:
            raise ValueError(f"expected align conjunction absent at math surface {index}")
        expected[index] = old.replace(r"\text{ and}", r"\text{ dan}")
        transformations.append(
            {"kind": "localized_math_text", "index": index, "source": old, "target": expected[index]}
        )
    if expected[15] != r"20^{\text{th}}":
        raise ValueError(f"historical ordinal surface shifted: {expected[15]!r}")
    expected[15] = "20"
    transformations.append(
        {"kind": "localized_math_text", "index": 15, "source": r"20^{\text{th}}", "target": "20"}
    )
    for index, correction in ((18, "FAOA-2015-CH15-CORR-002"), (34, "FAOA-2015-CH15-CORR-003")):
        old = expected[index]
        if old != r"\lambda \in \C":
            raise ValueError(f"lambda surface shifted at {index}: {old!r}")
        expected[index] = r"\lambda \in \C\setminus\{0\}"
        transformations.append(
            {
                "kind": "mathematical_source_repair_replace",
                "index": index,
                "source": old,
                "target": expected[index],
                "correction": correction,
            }
        )
    if expected[44] != "SK = KS":
        raise ValueError(f"commuting-condition surface shifted: {expected[44]!r}")
    removed = expected.pop(44)
    transformations.append(
        {
            "kind": "mathematical_source_repair_delete",
            "source_index": 44,
            "source": removed,
            "correction": "FAOA-2015-CH15-CORR-004",
        }
    )
    expected.insert(51, "B")
    transformations.append(
        {
            "kind": "mathematical_source_repair_insert",
            "target_index": 51,
            "target": "B",
            "correction": "FAOA-2015-CH15-CORR-005",
        }
    )
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
    if source_bytes.count(b"\r\n") != 444 or source_bytes.count(b"\n") != 444:
        errors.append("source CRLF topology differs")
    if b"\r" in target_bytes or target_bytes.count(b"\n") != 444:
        errors.append("target LF topology differs")
    if b"\r" in master_bytes or master_bytes.count(b"\n") != 344:
        errors.append("master LF topology differs")
    if any(data.startswith(b"\xef\xbb\xbf") for data in (target_bytes, master_bytes)):
        errors.append("UTF-8 BOM is forbidden")

    source = source_bytes.decode("ascii").replace("\r\n", "\n")
    target = target_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")
    source_lines = source.splitlines()
    target_lines = target.splitlines()
    if len(source_lines) != 444 or len(target_lines) != 444:
        errors.append("logical record count differs from 444/444")

    source_sections = re.findall(r"\\section\{([^}]*)\}", source)
    target_sections = re.findall(r"\\section\{([^}]*)\}", target)
    if source_sections != [
        "The Fredholm Alternative",
        "The Fredholm Alternative -- continued",
        "Fredholm Operators",
        "The Fredholm Alternative -- Concluded",
    ]:
        errors.append(f"source section sequence differs: {source_sections!r}")
    if target_sections != [
        "Alternatif Fredholm",
        "Alternatif Fredholm -- lanjutan",
        "Operator Fredholm",
        "Alternatif Fredholm -- Penutup",
    ]:
        errors.append(f"target section sequence differs: {target_sections!r}")
    if not source.startswith(r"\chapter{FREDHOLM THEORY}"):
        errors.append("source chapter opening differs")
    if not target.startswith(r"\chapter{TEORI FREDHOLM}"):
        errors.append("target chapter opening differs")

    source_begins = re.findall(r"\\begin\{([^}]+)\}", source)
    source_ends = re.findall(r"\\end\{([^}]+)\}", source)
    target_begins = re.findall(r"\\begin\{([^}]+)\}", target)
    target_ends = re.findall(r"\\end\{([^}]+)\}", target)
    if len(source_begins) != 60 or len(target_begins) != 60:
        errors.append("environment opening count differs from 60/60")
    if len(source_ends) != 60 or len(target_ends) != 60:
        errors.append("environment closing count differs from 60/60")
    if Counter(source_begins) != EXPECTED_ENVIRONMENTS or Counter(target_begins) != EXPECTED_ENVIRONMENTS:
        errors.append("environment census differs")
    if source_begins != target_begins or source_ends != target_ends:
        errors.append("source/target environment topology differs")
    errors.extend(f"source {value}" for value in validate_environment_stack(source))
    errors.extend(f"target {value}" for value in validate_environment_stack(target))
    semantic_openings = len([value for value in target_begins if value not in {"align", "enumerate"}])
    if semantic_openings != 50:
        errors.append(f"semantic environment count differs: {semantic_openings}")

    source_labels = re.findall(r"\\label\{([^}]+)\}", source)
    target_labels = re.findall(r"\\label\{([^}]+)\}", target)
    source_refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", source)
    target_refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", target)
    source_cites = extract_cites(source)
    target_cites = extract_cites(target)
    for name, actual, expected in (
        ("source labels", source_labels, EXPECTED_LABELS),
        ("target labels", target_labels, EXPECTED_LABELS),
        ("source refs", source_refs, EXPECTED_REFS),
        ("target refs", target_refs, EXPECTED_REFS),
        ("source citations", source_cites, EXPECTED_CITES),
        ("target citations", target_cites, EXPECTED_CITES),
    ):
        if actual != expected:
            errors.append(f"{name} differ: {actual!r}")
    if len(set(target_labels)) != len(target_labels):
        errors.append("duplicate target label")
    if source.count(r"\index{") != 46 or target.count(r"\index{") != 46:
        errors.append("index-hook census differs from 46/46")
    source_terms = re.findall(r"\\df\{([^{}]*)\}", source)
    target_terms = re.findall(r"\\df\{([^{}]*)\}", target)
    if source_terms != EXPECTED_SOURCE_TERMS:
        errors.append(f"source defined terms differ: {source_terms!r}")
    if target_terms != EXPECTED_TARGET_TERMS:
        errors.append(f"target defined terms differ: {target_terms!r}")
    source_tags = re.findall(r"\\tag\{([^}]+)\}", source)
    target_tags = re.findall(r"\\tag\{([^}]+)\}", target)
    if source_tags != EXPECTED_TAGS or target_tags != EXPECTED_TAGS:
        errors.append(f"manual equation-tag sequence differs: {source_tags!r}/{target_tags!r}")

    raw_census: dict[str, dict[str, int]] = {}
    for text_name, text, expected_raw in (
        ("source", source, (190, 7, 6, 309)),
        ("target", target, (191, 7, 6, 307)),
    ):
        dollar_pairs = len(re.findall(r"(?<!\\)\$", text)) // 2
        display_open = text.count(r"\[")
        display_close = text.count(r"\]")
        align_count = text.count(r"\begin{align}")
        brace_open = len(re.findall(r"(?<!\\)\{", text))
        brace_close = len(re.findall(r"(?<!\\)\}", text))
        raw_census[text_name] = {
            "inline_dollar_pairs": dollar_pairs,
            "display_surfaces": display_open,
            "align_surfaces": align_count,
            "inventory_surfaces": dollar_pairs + display_open + align_count,
            "unescaped_open_braces": brace_open,
            "unescaped_close_braces": brace_close,
        }
        if (dollar_pairs, display_open, align_count, brace_open) != expected_raw:
            errors.append(f"{text_name} raw math/brace census differs: {raw_census[text_name]!r}")
        if display_open != display_close or brace_open != brace_close:
            errors.append(f"{text_name} raw delimiter balance differs")
    try:
        source_math = extract_top_level_math(source)
        target_math = extract_top_level_math(target)
    except ValueError as exc:
        errors.append(str(exc))
        source_math, target_math = [], []
    transformations: list[dict[str, object]] = []
    if len(source_math) != 203 or len(target_math) != 204:
        errors.append(f"ordered top-level math count differs: {len(source_math)}/{len(target_math)}")
    elif source_math:
        try:
            expected_math, transformations = transformed_source_math(source_math)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if expected_math != target_math:
                limit = min(len(expected_math), len(target_math))
                mismatch = [index for index in range(limit) if expected_math[index] != target_math[index]]
                errors.append(f"math differs outside the classified transformation program: {mismatch[:20]!r}")
    if len(transformations) != 12:
        errors.append(f"classified math-transformation count differs: {len(transformations)}")

    if target.count(r"\begin{exer}") != 0 or target.count(r"\begin{proof}") != 13:
        errors.append("exercise/proof census differs from 0/13")
    source_hint_proofs = source.count(r"\emph{Hint.}") + source.count(r"\begin{proof}[\emph{Hint for proof}]")
    target_hint_proofs = target.count(r"\emph{Petunjuk.}") + target.count(r"\begin{proof}[\emph{Petunjuk bukti}]")
    if source_hint_proofs != 2 or target_hint_proofs != 2:
        errors.append(f"proof-hint census differs from 2/2: {source_hint_proofs}/{target_hint_proofs}")
    if re.search(r"\\begin\{(?:answer|solution|hint)\}", target):
        errors.append("unsupported answer/solution/hint environment entered target")
    if target.count(r"\endinput") != 1 or not target.rstrip().endswith(r"\endinput"):
        errors.append("target endinput closure differs")

    residue_pattern = re.compile(
        r"\b(?:Let|Suppose|Then|If|Every|For all|For each|There exists|We say|We define|We will|"
        r"Notice that|Clearly|This is|is called|if and only if|See|Compare|Recall|The next|"
        r"The preceding|The following|Hint for proof|Fredholm Alternative)\b"
    )
    residues = sorted(set(match.group(0) for match in residue_pattern.finditer(target)))
    if residues:
        errors.append(f"active English instructional residue: {residues!r}")
    for marker in ("Ã", "Â", "â€", "�", "C:\\Users\\", "/Users/", "/home/", "api_key", "access_token"):
        if marker in target or marker in master:
            errors.append(f"forbidden encoding/private/credential marker: {marker!r}")
    required_terms = (
        "persamaan integral",
        "persamaan tak homogen",
        "kontinuitas lengkap",
        r"\df{operator Riesz--Schauder}",
        r"\df{kokernel}",
        r"\df{kodimensi}",
        "jangkauan tak tertutup",
        r"\df{aljabar Calkin}",
        r"\df{operator Fredholm}",
        "perturbasi kompak",
        r"\begin{thm}[Teorema Atkinson]",
        r"\df{indeks Fredholm}",
        "isometri parsial berperingkat hingga",
        r"\df{lintasan}",
        r"\df{terhubung oleh lintasan}",
        r"\df{homotop dalam~$X$}",
        r"\df{komponen lintasan}",
        "operator geser unilateral",
        "barisan\nberikut eksak",
        "pemetaan hasil bagi",
        "swaadjoin",
        "padat dalam",
    )
    for anchor in required_terms:
        if anchor not in target:
            errors.append(f"required Indonesian terminology anchor missing: {anchor!r}")
    rejected_terms = re.compile(
        r"\bnonhomogen\b|\brange\b|\brapat\b|\badjoint\b|\bself-adjoint\b|\bpath components?\b|\bCalkin algebra\b",
        re.I,
    )
    rejected_matches = sorted(set(match.group(0) for match in rejected_terms.finditer(target)))
    if rejected_matches:
        errors.append(f"rejected terminology remains: {rejected_matches!r}")

    required_corrections = (
        r"Tetapkan $\lambda \in \C\setminus\{0\}$",
        r"Hilbert, $\lambda \in \C\setminus\{0\}$, dan $T = \lambda I - K$",
        r"ruang Hilbert dan $\lambda \in \C\setminus\{0\}$, maka",
        r"invertibel dan $K$ kompak.",
        r"ruang Banach $B$, maka $M^\perp \cong (B/M)^*$",
        "jumlah dua subruang tertutup dari suatu ruang Hilbert tidak harus tertutup",
        r"\index{subruang!jumlah subruang tertutup tidak harus tertutup}%",
        r"\index{Fredholm!indeks (\seeonly{indeks})}%",
        "Untuk pemetaan antar-ruang, kita memakai konvensi standar",
        "jangkauannya tertutup serta kernel dan kokernelnya berdimensi hingga",
        r"Misalkan $H$ ruang Hilbert berdimensi tak hingga.",
    )
    for anchor in required_corrections:
        if anchor not in target:
            errors.append(f"required correction anchor missing: {anchor!r}")
    for forbidden in (
        r"$SK = KS$",
        r"\seeonly{indeks}))",
        "jumlah dua subruang dari suatu ruang Hilbert tidak harus menjadi subruang",
        r"ruang Hilbert, $\lambda \in \C$, dan",
    ):
        if forbidden in target:
            errors.append(f"forbidden source defect remains: {forbidden!r}")
    for invented_space in ("C([0,1])", "L^2([0,1])", r"\fml C([0,1])"):
        if invented_space in target:
            errors.append(f"unsupported Alternative-I function-space choice entered target: {invented_space!r}")

    includes = re.findall(r"\\include\{([^}]+)\}", master)
    if includes != EXPECTED_INCLUDES:
        errors.append(f"master include sequence differs: {includes!r}")
    required_master = (
        "pdfauthor={John M Erdman}",
        r"\author{John M. Erdman",
        "Unit Pembaca Kumulatif Bab 1--15",
        "batas produksi Bab 1--15",
        "Bab 1 sampai Bab 15",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "Creative Commons",
        "CC BY-SA 4.0",
        "kredit John M. Erdman dan kontributor komponen tetap dipertahankan",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University",
        r"\input{DIAGXY.TEX}",
        r"\include{fredholm_theory-id}",
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
    if ledger.get("schema_version") != "o008.source-corrections.v1" or ledger.get("unit_id") != "FAOA-2015-CH15":
        errors.append("correction ledger schema/unit binding differs")
    if ledger.get("status") != "adjudicated_and_applied" or ledger.get("record_count") != 9:
        errors.append("correction ledger status/count differs")
    if ledger.get("class_counts") != {
        "MATHEMATICAL_SOURCE_REPAIR": 7,
        "MECHANICAL_PROSE_SOURCE_REPAIR": 1,
        "FORMAL_SCOPE_CLARIFICATION": 1,
    }:
        errors.append("correction ledger class census differs")
    if ledger.get("source", {}) != {
        "path": "source/upstream/fredholm_theory.tex",
        "bytes": EXPECTED["source_bytes"],
        "logical_records": 444,
        "line_endings": "CRLF",
        "sha256": EXPECTED["source_sha256"],
    }:
        errors.append("correction ledger source binding differs")
    if ledger.get("target", {}) != {
        "path": "source/id-ID/fredholm_theory-id.tex",
        "bytes": EXPECTED["target_bytes"],
        "logical_records": 444,
        "line_endings": "LF",
        "sha256": EXPECTED["target_sha256"],
    }:
        errors.append("correction ledger target binding differs")
    if records and ledger_bytes != (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8"):
        errors.append("correction ledger canonical serialization differs")
    actual_specs: list[tuple[object, object, object, object, object]] = []
    for record in records:
        try:
            source_range = record["source_lines"]
            target_range = record["target_lines"]
            spec = (
                record.get("id"),
                (source_range["start"], source_range["end"]),
                (target_range["start"], target_range["end"]),
                record.get("classification"),
                record.get("affects_math"),
            )
            actual_specs.append(spec)
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
        errors.append(f"correction ledger record identity/order/classification differs: {actual_specs!r}")

    report = {
        "schema_version": "o008.ch15-translation-qa.v1",
        "unit_id": "FAOA-2015-CH15",
        "status": "pass" if not errors else "fail",
        "identities": identities,
        "structure": {
            "source_records": len(source_lines),
            "target_records": len(target_lines),
            "sections": len(target_sections),
            "environment_openings": len(target_begins),
            "semantic_environment_openings": semantic_openings,
            "environment_counts": dict(sorted(Counter(target_begins).items())),
            "labels": len(target_labels),
            "references": len(target_refs),
            "citations": len(target_cites),
            "index_hooks": target.count(r"\index{"),
            "defined_terms": len(target_terms),
            "manual_equation_tags": len(target_tags),
            "examples": target.count(r"\begin{exam}"),
            "exercises": target.count(r"\begin{exer}"),
            "proofs": target.count(r"\begin{proof}"),
            "proof_hints": target_hint_proofs,
        },
        "math": {
            "raw_census": raw_census,
            "ordered_top_level_source_surfaces": len(source_math),
            "ordered_top_level_target_surfaces": len(target_math),
            "classified_transformations": transformations,
        },
        "corrections": {
            "records": len(records),
            "ledger_sha256": digest(ledger_bytes) if ledger_bytes else None,
            "function_space_omission_preserved": True,
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
