#!/usr/bin/env python3
"""Locked structural, mathematical, language, rights, and linkage QA for CH14."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "multiplier_algebras.tex"
TARGET = ROOT / "source" / "id-ID" / "multiplier_algebras-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch14.tex"
LEDGER = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH14.json"
REPORT = ROOT / "qa" / "ch14-translation-report.json"

EXPECTED = {
    "source_bytes": 30_579,
    "source_sha256": "d9bf8cf31a6e18a779863dcb397863430fe2daac9031a86354ce2274b42def7c",
    "target_bytes": 31_900,
    "target_sha256": "2688ec9c2370371060aada680f5f95e9511ecb61cb99c2a126385f525a3c9142",
    "master_bytes": 10_443,
    "master_sha256": "f04180a796707c6cb0c5f74082a8b4c25721d20ff3ea9235819939b11e1e50c9",
}
EXPECTED_ENVIRONMENTS = Counter(
    {
        "array": 1,
        "conv": 2,
        "cor": 1,
        "defn": 19,
        "enumerate": 3,
        "exam": 9,
        "exer": 2,
        "notn": 6,
        "proof": 3,
        "prop": 24,
    }
)
EXPECTED_LABELS = [
    "multiplier_algebras",
    "0038014",
    "0038017",
    "0038021",
    "0038027",
    "0038031",
    "0038038",
    "0038041",
    "0038111",
    "0038244",
    "0038331",
    "0038334",
    "0038337",
    "0038341",
    "0038465",
    "0038468",
    "0038474",
    "0038614",
    "0038621",
    "0038641",
]
EXPECTED_REFS = [
    "defn_alg",
    "0022057",
    "0038017",
    "0038021",
    "0038017",
    "0038031",
    "0018203",
    "0018204",
    "0038041",
    "def000926",
    "0006836",
    "0038111",
    "0022431fa",
    "prop_op_act_otimes1",
    "prop_op_act_otimes2",
    "0038111",
    "0013151",
    "0038331",
    "prop_K_is_clo_FR",
    "cor_id_op_not_cpt",
    "0006801",
    "000551",
    "0015213",
    "00152156",
    "00152131",
    "0015213",
    "001924",
    "00152194",
    "0019023",
    "00152181",
    "0028",
]
EXPECTED_CITES = ["RaeburnW:1998", "Frank:2010", "Willard:1968", "Conway:1990"]
EXPECTED_SOURCE_TERMS = [
    "$A$-module",
    "bilinear",
    "(complex) vector space",
    "algebra",
    "opposite algebra",
    "antihomomorphism",
    "anti-isomorphism",
    "$A$-module",
    "semi-inner product $A$-module",
    "inner product $A$-module",
    "pre-Hilbert $A$-module",
    "$A$-valued (semi-)inner product",
    "Hilbert $A$-module",
    "$A$-linear",
    "Hilbert $A$-module morphism",
    "adjointable",
    "adjoint",
    "principal ideal",
    "essential",
    "annihilator",
    "zero set",
    "unitization",
    "essential unitization",
    "compactification",
    "essential compactification",
    "embedded",
    "embedding",
    "unitization",
    "essential",
    "embedded",
    "embedding",
    "compactification",
    "essential",
    "maximal",
    "nondegenerate",
    "multiplier algebra",
]
EXPECTED_TARGET_TERMS = [
    "modul-$A$",
    "bilinear",
    "ruang vektor (kompleks)",
    "aljabar",
    "aljabar lawan",
    "antihomomorfisme",
    "antiisomorfisme",
    "modul-$A$",
    "modul-$A$ hasil kali dalam semu",
    "modul-$A$ hasil kali dalam",
    "modul pra-Hilbert-$A$",
    "hasil kali dalam (semu) bernilai-$A$",
    "modul Hilbert-$A$",
    "linear-$A$",
    "morfisme modul Hilbert-$A$",
    "dapat diadjoinkan",
    "adjoin",
    "ideal utama",
    "esensial",
    "anihilator",
    "himpunan nol",
    "unitalisasi",
    "unitalisasi esensial",
    "kompaktifikasi",
    "kompaktifikasi esensial",
    "dibenamkan",
    "pembenaman",
    "unitalisasi",
    "esensial",
    "dibenamkan",
    "pembenaman",
    "kompaktifikasi",
    "esensial",
    "maksimal",
    "tak terdegenerasi",
    "aljabar pengali",
]
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
]
EXPECTED_CORRECTION_IDS = [f"FAOA-2015-CH14-CORR-{number:03d}" for number in range(1, 10)]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_cites(text: str) -> list[str]:
    keys: list[str] = []
    for argument in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", text):
        keys.extend(value.strip() for value in argument.split(",") if value.strip())
    return keys


def extract_math(text: str) -> list[str]:
    """Return ordered nonoverlapping inline/display surfaces.

    Dollar pairs nested inside a display's text boxes belong to that display and
    are therefore not counted again here. The raw delimiter census is checked
    separately to retain the source inventory's 635+15 convention.
    """

    surfaces: list[str] = []
    index = 0
    while index < len(text):
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

    old = expected[54]
    expected[54] = r"\phi\colon A \sto B^{\textrm{op}}"
    transformations.append({"kind": "source_identifier_repair", "index": 54, "source": old, "target": expected[54]})

    moved = expected.pop(58)
    expected.insert(60, moved)
    transformations.append({"kind": "locale_grammar_reorder", "source_index": 58, "target_index": 60, "surface": moved})

    old = expected[232]
    expected[232] = r"\iota\colon W \sto V"
    transformations.append({"kind": "mathematical_source_repair", "index": 232, "source": old, "target": expected[232]})

    for index in (277, 300):
        old = expected[index]
        expected[index] = old.replace(r"\text{ and }", r"\text{ dan }")
        transformations.append({"kind": "localized_math_text", "index": index, "source": old, "target": expected[index]})

    old = expected[388]
    expected[388] = " dan "
    transformations.append({"kind": "localized_math_text", "index": 388, "source": old, "target": expected[388]})

    old = expected[467]
    expected[467] = old.replace(r"\hbox{if $y \in X$;}", r"\hbox{jika $y \in X$;}").replace(
        r"\hbox{otherwise.}", r"\hbox{selainnya.}"
    )
    transformations.append({"kind": "localized_math_text", "index": 467, "source": old, "target": expected[467]})

    before = [expected[607], expected[608]]
    expected[607], expected[608] = expected[608], expected[607]
    transformations.append(
        {"kind": "locale_grammar_reorder", "source_indices": [607, 608], "target_indices": [608, 607], "surfaces": before}
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
    if source_bytes.count(b"\r\n") != 687 or source_bytes.count(b"\n") != 687:
        errors.append("source CRLF topology differs")
    if b"\r" in target_bytes or target_bytes.count(b"\n") != 687:
        errors.append("target LF topology differs")
    if b"\r" in master_bytes or master_bytes.count(b"\n") != 343:
        errors.append("master LF topology differs")
    if any(data.startswith(b"\xef\xbb\xbf") for data in (target_bytes, master_bytes)):
        errors.append("UTF-8 BOM is forbidden")

    source = source_bytes.decode("ascii").replace("\r\n", "\n")
    target = target_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")
    source_lines = source.splitlines()
    target_lines = target.splitlines()
    if len(source_lines) != 687 or len(target_lines) != 687:
        errors.append("logical record count differs from 687/687")

    source_sections = re.findall(r"\\section\{([^}]*)\}", source)
    target_sections = re.findall(r"\\section\{([^}]*)\}", target)
    if source_sections != ["Hilbert Modules", "Essential Ideals", "Compactifications and Unitizations"]:
        errors.append(f"source section sequence differs: {source_sections!r}")
    if target_sections != ["Modul Hilbert", "Ideal Esensial", "Kompaktifikasi dan Unitalisasi"]:
        errors.append(f"target section sequence differs: {target_sections!r}")
    if not source.startswith(r"\chapter{MULTIPLIER ALGEBRAS}\label{multiplier_algebras}"):
        errors.append("source chapter opening differs")
    if not target.startswith(r"\chapter{ALJABAR PENGALI}\label{multiplier_algebras}"):
        errors.append("target chapter opening differs")

    source_begins = re.findall(r"\\begin\{([^}]+)\}", source)
    source_ends = re.findall(r"\\end\{([^}]+)\}", source)
    target_begins = re.findall(r"\\begin\{([^}]+)\}", target)
    target_ends = re.findall(r"\\end\{([^}]+)\}", target)
    if len(source_begins) != 70 or len(target_begins) != 70:
        errors.append("environment opening count differs from 70/70")
    if len(source_ends) != 70 or len(target_ends) != 70:
        errors.append("environment closing count differs from 70/70")
    if Counter(source_begins) != EXPECTED_ENVIRONMENTS or Counter(target_begins) != EXPECTED_ENVIRONMENTS:
        errors.append("environment census differs")
    if source_begins != target_begins or source_ends != target_ends:
        errors.append("source/target environment topology differs")
    errors.extend(f"source {value}" for value in validate_environment_stack(source))
    errors.extend(f"target {value}" for value in validate_environment_stack(target))
    semantic_openings = len([value for value in target_begins if value not in {"array", "enumerate"}])
    if semantic_openings != 66:
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
    if source.count(r"\index{") != 79 or target.count(r"\index{") != 79:
        errors.append("index-hook census differs from 79/79")
    source_terms = re.findall(r"\\df\{([^{}]*)\}", source)
    target_terms = re.findall(r"\\df\{([^{}]*)\}", target)
    if source_terms != EXPECTED_SOURCE_TERMS:
        errors.append(f"source defined terms differ: {source_terms!r}")
    if target_terms != EXPECTED_TARGET_TERMS:
        errors.append(f"target defined terms differ: {target_terms!r}")

    for text_name, text in (("source", source), ("target", target)):
        dollar_delimiters = len(re.findall(r"(?<!\\)\$", text))
        display_open = text.count(r"\[")
        display_close = text.count(r"\]")
        brace_open = len(re.findall(r"(?<!\\)\{", text))
        brace_close = len(re.findall(r"(?<!\\)\}", text))
        if dollar_delimiters != 1_270 or display_open != 15 or display_close != 15:
            errors.append(f"{text_name} raw math-delimiter census differs")
        if brace_open != 395 or brace_close != 395:
            errors.append(f"{text_name} unescaped-brace census differs: {brace_open}/{brace_close}")
    try:
        source_math = extract_math(source)
        target_math = extract_math(target)
    except ValueError as exc:
        errors.append(str(exc))
        source_math, target_math = [], []
    transformations: list[dict[str, object]] = []
    if len(source_math) != 644 or len(target_math) != 644:
        errors.append(f"ordered nonoverlapping math count differs: {len(source_math)}/{len(target_math)}")
    elif source_math:
        expected_math, transformations = transformed_source_math(source_math)
        if expected_math != target_math:
            mismatch = [index for index, (left, right) in enumerate(zip(expected_math, target_math)) if left != right]
            errors.append(f"math differs outside eight classified transformations: {mismatch[:20]!r}")

    if target.count(r"\begin{exer}") != 2 or target.count(r"\begin{proof}") != 3:
        errors.append("exercise/proof census differs from 2/3")
    if target.count(r"\begin{proof}[\emph{Petunjuk pembuktian}]") != 2:
        errors.append("translated proof-hint census differs from two")
    if re.search(r"\\begin\{(?:answer|solution|hint)\}", target):
        errors.append("unsupported answer/solution/hint environment entered target")
    if target.count(r"\endinput") != 1 or not target.rstrip().endswith(r"\endinput"):
        errors.append("target endinput closure differs")

    permitted_title = "Hilbert C*-modules and related subjects---a guided\nreference overview"
    residue_surface = target.replace(permitted_title, "")
    residue_pattern = re.compile(
        r"\b(?:Let|Suppose|Then|If|Every|For all|For each|There exists|We say|We define|We will|"
        r"Notice that|Clearly|This is|is called|if and only if|See|Compare|Recall|"
        r"The next|The preceding|The following|Hint for proof)\b"
    )
    residues = sorted(set(match.group(0) for match in residue_pattern.finditer(residue_surface)))
    if residues:
        errors.append(f"active English instructional residue: {residues!r}")
    for marker in ("Ã", "Â", "â€", "�", "C:\\Users\\", "/Users/", "/home/", "api_key", "access_token"):
        if marker in target or marker in master:
            errors.append(f"forbidden encoding/private/credential marker: {marker!r}")

    required_terms = (
        r"\df{modul Hilbert-$A$}",
        r"\df{dapat diadjoinkan}",
        r"\df{adjoin}",
        r"\df{aljabar lawan}",
        r"\df{antihomomorfisme}",
        r"\df{antiisomorfisme}",
        r"\df{ideal utama}",
        r"\df{esensial}",
        r"\df{anihilator}",
        r"\df{himpunan nol}",
        r"\df{unitalisasi}",
        r"\df{kompaktifikasi}",
        r"\df{pembenaman}",
        r"\df{tak terdegenerasi}",
        r"\df{aljabar pengali}",
        "elemen $\\ofml K(V)$ sebagai \\emph{operator kompak}",
        "operator semacam itu belum tentu kompak",
        r"rentang linear tertutup",
        r"padat dalam~$V$",
    )
    for anchor in required_terms:
        if anchor not in target:
            errors.append(f"required Indonesian terminology anchor missing: {anchor!r}")
    forbidden_terms = re.compile(
        r"\brapat\b|\badjointable\b|modul pre-Hilbert|aljabar oposisi|\bpemadatan\b|\bpenanaman\b|\bmultiplier algebra\b",
        re.I,
    )
    forbidden_matches = sorted(set(match.group(0) for match in forbidden_terms.finditer(residue_surface)))
    if forbidden_matches:
        errors.append(f"rejected terminology remains: {forbidden_matches!r}")
    required_reflows = (
        r"$(V,+,M,\Phi)$ disebut \df{modul-$A$} jika $(V,+,M)$ suatu ruang vektor",
        "Pemetaan\n$\\phi\\colon B \\sto \\ofml L(V)$ yang merupakan homomorfisme-$*\\,$ disebut",
    )
    for anchor in required_reflows:
        if anchor not in target:
            errors.append(f"required target reflow missing: {anchor!r}")

    required_corrections = (
        r"fungsi $\phi\colon A \sto B^{\textrm{op}}$ merupakan suatu homomorfisme",
        r"apa artinya, ketika $A$ suatu aljabar-$C^*$",
        "Hal ini tidak berlaku untuk modul Hilbert-$A$.",
        r"aljabar-$C^*$ $\fml C(X)$",
        r"$\iota\colon W \sto V$ merupakan morfisme modul Hilbert-$A$",
        "Contoh sebelumnya telah mendorong banyak peneliti",
        r"dari suatu aljabar, maka $AB$ berarti",
        "$\\phi$, jika ada, harus\ninjektif.",
        "$\\phi$, jika ada, harus\ntunggal.",
    )
    for anchor in required_corrections:
        if anchor not in target:
            errors.append(f"required correction anchor missing: {anchor!r}")
    for forbidden in (r"fungsi $f\colon A \sto B^{\textrm{op}}$", r"aljabar-$C^*$=", r"$\iota\colon V \sto W$"):
        if forbidden in target:
            errors.append(f"forbidden source defect remains: {forbidden!r}")

    includes = re.findall(r"\\include\{([^}]+)\}", master)
    if includes != EXPECTED_INCLUDES:
        errors.append(f"master include sequence differs: {includes!r}")
    required_master = (
        "pdfauthor={John M Erdman}",
        "\\author{John M. Erdman",
        "Unit Pembaca Kumulatif Bab 1--14",
        "batas produksi Bab 1--14",
        "Bab 1 sampai Bab 14",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "Creative Commons",
        "CC BY-SA 4.0",
        "kredit John M. Erdman dan kontributor komponen tetap dipertahankan",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University",
        r"\input{DIAGXY.TEX}",
        r"\include{multiplier_algebras-id}",
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
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"correction ledger unreadable: {exc}")
        ledger = {}
    records = ledger.get("records", []) if isinstance(ledger, dict) else []
    if ledger.get("record_count") != 9 or [record.get("id") for record in records] != EXPECTED_CORRECTION_IDS:
        errors.append("correction ledger record identity/order differs")
    if ledger.get("class_counts") != {
        "SEMANTIC_IDENTIFIER_SOURCE_REPAIR": 1,
        "MECHANICAL_PROSE_SOURCE_REPAIR": 7,
        "MATHEMATICAL_SOURCE_REPAIR": 1,
    }:
        errors.append("correction ledger class census differs")
    if ledger.get("source", {}).get("sha256") != EXPECTED["source_sha256"]:
        errors.append("correction ledger source binding differs")
    if ledger.get("target", {}).get("sha256") != EXPECTED["target_sha256"]:
        errors.append("correction ledger target binding differs")
    for record in records:
        try:
            source_range = record["source_lines"]
            target_range = record["target_lines"]
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
        except (KeyError, TypeError) as exc:
            errors.append(f"ledger record malformed: {record!r}: {exc}")

    report = {
        "schema_version": "o008.ch14-translation-qa.v1",
        "unit_id": "FAOA-2015-CH14",
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
            "exercises": target.count(r"\begin{exer}"),
            "proofs": target.count(r"\begin{proof}"),
        },
        "math": {
            "raw_dollar_pairs": len(re.findall(r"(?<!\\)\$", target)) // 2,
            "display_surfaces": target.count(r"\["),
            "inventory_surface_count": len(re.findall(r"(?<!\\)\$", target)) // 2 + target.count(r"\["),
            "ordered_nonoverlapping_source_surfaces": len(source_math),
            "ordered_nonoverlapping_target_surfaces": len(target_math),
            "classified_transformations": transformations,
        },
        "corrections": {
            "records": len(records),
            "ledger_sha256": digest(LEDGER.read_bytes()) if LEDGER.is_file() else None,
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
