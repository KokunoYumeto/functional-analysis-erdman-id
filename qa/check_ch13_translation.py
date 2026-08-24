#!/usr/bin/env python3
"""Locked structural, mathematical, language, rights, and linkage QA for CH13."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "GNS_construction.tex"
TARGET = ROOT / "source" / "id-ID" / "GNS_construction-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch13.tex"
LEDGER = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH13.json"
REPORT = ROOT / "qa" / "ch13-translation-report.json"

EXPECTED = {
    "source_bytes": 11_965,
    "source_sha256": "fcc774cecc607d9860540da7b757ae04a3c43afe9d9a17e8c881e077f02682c1",
    "target_bytes": 12_601,
    "target_sha256": "4c95b339702180ef8f2ea42cfba9e19a60a1740ca7d25a0568a6290f0170371f",
    "master_bytes": 10_345,
    "master_sha256": "d1734ea09a576c9e5c8f38bb9430a132e8cd38551c9b0c6cbd9bf65b4923c87e",
}

EXPECTED_ENVIRONMENTS = Counter(
    {
        "prop": 10,
        "defn": 7,
        "exam": 5,
        "cor": 2,
        "proof": 2,
        "thm": 2,
        "cau": 1,
        "conv": 1,
        "exer": 1,
        "notn": 1,
    }
)
EXPECTED_LABELS = [
    "gelfand_naimark_segal",
    "0025105",
    "0028",
    "002802",
    "0029",
    "thm_exist_faith_rep",
    "002973",
]
EXPECTED_REFS = ["C063527", "0025105"]
EXPECTED_CITES = [
    "KadisonR:1983",
    "Blackadar:2006",
    "Conway:1990",
    "DoranB:1986",
    "Fillmore:1996",
    "KadisonR:1983",
    "Murphy:1990",
]
EXPECTED_SOURCE_TERMS = [
    "Hermitian",
    "positive",
    "state",
    "vector state",
    "representation",
    "nondegenerate",
    "faithful",
    "cyclic",
    "cyclic vector",
    "left kernel",
    "direct sum",
    "direct sum",
    "direct sum",
]
EXPECTED_TARGET_TERMS = [
    "Hermitian",
    "positif",
    "keadaan",
    "keadaan vektor",
    "representasi",
    "tak terdegenerasi",
    "setia",
    "siklik",
    "vektor siklik",
    "kernel kiri",
    "jumlah langsung",
    "jumlah langsung",
    "jumlah langsung",
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
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_cites(text: str) -> list[str]:
    keys: list[str] = []
    for argument in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", text):
        keys.extend(value.strip() for value in argument.split(",") if value.strip())
    return keys


def extract_math(text: str) -> list[str]:
    pattern = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$|\\\[(.*?)\\\]", re.S)
    return [next(value for value in match.groups() if value is not None) for match in pattern.finditer(text)]


def math_edit_blocks(source: list[str], target: list[str]) -> list[dict[str, object]]:
    blocks = []
    for operation, i1, i2, j1, j2 in SequenceMatcher(a=source, b=target, autojunk=False).get_opcodes():
        if operation == "equal":
            continue
        blocks.append(
            {
                "operation": operation,
                "source_start": i1,
                "source_end": i2,
                "target_start": j1,
                "target_end": j2,
                "source": source[i1:i2],
                "target": target[j1:j2],
            }
        )
    return blocks


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
    if source_bytes.count(b"\r\n") != 289 or source_bytes.count(b"\n") != 289:
        errors.append("source CRLF topology differs")
    if b"\r" in target_bytes or target_bytes.count(b"\n") != 289:
        errors.append("target LF topology differs")
    if target_bytes.startswith(b"\xef\xbb\xbf") or master_bytes.startswith(b"\xef\xbb\xbf"):
        errors.append("UTF-8 BOM is forbidden")

    source = source_bytes.decode("ascii").replace("\r\n", "\n")
    target = target_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")
    if len(source.splitlines()) != 289 or len(target.splitlines()) != 289:
        errors.append("logical record count differs from 289/289")

    source_sections = re.findall(r"\\section\{([^}]*)\}", source)
    target_sections = re.findall(r"\\section\{([^}]*)\}", target)
    if source_sections != [
        "Positive Linear Functionals",
        "Representations",
        "The GNS-Construction and the Third Gelfand-Naimark Theorem",
    ]:
        errors.append(f"source section sequence differs: {source_sections!r}")
    if target_sections != [
        "Fungsional Linear Positif",
        "Representasi",
        "Konstruksi GNS dan Teorema Gelfand-Naimark Ketiga",
    ]:
        errors.append(f"target section sequence differs: {target_sections!r}")

    source_begins = re.findall(r"\\begin\{([^}]+)\}", source)
    source_ends = re.findall(r"\\end\{([^}]+)\}", source)
    target_begins = re.findall(r"\\begin\{([^}]+)\}", target)
    target_ends = re.findall(r"\\end\{([^}]+)\}", target)
    if Counter(source_begins) != EXPECTED_ENVIRONMENTS or source_begins != target_begins:
        errors.append("environment opening topology differs")
    if source_ends != source_begins or target_ends != target_begins:
        # These chapters do not nest environments, so exact opening/closing order is valid.
        errors.append("environment closing topology differs")

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
    if target.count("\\index{") != 28 or target.count("\\df{") != 13:
        errors.append("index/defined-term census differs")
    source_terms = re.findall(r"\\df\{([^{}]*)\}", source)
    target_terms = re.findall(r"\\df\{([^{}]*)\}", target)
    if source_terms != EXPECTED_SOURCE_TERMS:
        errors.append(f"source defined terms differ: {source_terms!r}")
    if target_terms != EXPECTED_TARGET_TERMS:
        errors.append(f"target defined terms differ: {target_terms!r}")

    source_math = extract_math(source)
    target_math = extract_math(target)
    edits = math_edit_blocks(source_math, target_math)
    expected_edits = [
        {
            "operation": "insert",
            "source_start": 24,
            "source_end": 24,
            "target_start": 24,
            "target_end": 25,
            "source": [],
            "target": ["a \\in A"],
        },
        {
            "operation": "delete",
            "source_start": 25,
            "source_end": 27,
            "target_start": 26,
            "target_end": 26,
            "source": ["A", "a \\in A"],
            "target": [],
        },
        {
            "operation": "replace",
            "source_start": 35,
            "source_end": 36,
            "target_start": 34,
            "target_end": 37,
            "source": ["\\tau(\\vc 1) = 1"],
            "target": ["\\norm\\tau = 1", "A", "\\tau(\\vc 1_A) = 1"],
        },
        {
            "operation": "insert",
            "source_start": 174,
            "source_end": 174,
            "target_start": 175,
            "target_end": 176,
            "source": [],
            "target": ["A"],
        },
    ]
    if len(source_math) != 237 or len(target_math) != 239 or edits != expected_edits:
        errors.append(f"math surface differs outside four classified edit blocks: {edits!r}")
    if target.count(r"\[") != 4 or target.count(r"\]") != 4:
        errors.append("display-math delimiter count differs")

    if target.count("\\begin{exer}") != 1 or re.search(r"\\begin\{(?:answer|solution|hint)\}", target):
        errors.append("exercise/support provenance surface differs")
    if target.count("\\endinput") != 1 or not target.rstrip().endswith("\\endinput"):
        errors.append("target endinput closure differs")

    forbidden_residue = re.compile(
        r"\b(?:Let|Suppose|Then|Whenever|Every|There exists|is called|is a|if and only if|for all|See|pages?|Theorem|Corollary|representation|faithful|cyclic|state|positive linear functional|left kernel|direct sum|Hilbert space)\b"
    )
    residues = sorted(set(match.group(0) for match in forbidden_residue.finditer(target)))
    if residues:
        errors.append(f"active English residue: {residues!r}")
    for marker in ("Ã", "Â", "â€", "�", "C:\\Users\\", "/Users/", "/home/"):
        if marker in target or marker in master:
            errors.append(f"forbidden encoding/private-path marker: {marker!r}")
    if re.search(r"\brapat\b", target, re.I):
        errors.append("rejected dense-translation variant 'rapat' remains")
    if ".." in target:
        errors.append("doubled period remains")

    required_corrections = (
        r"\df{positif} jika $\tau(a) \ge 0$ untuk setiap $a \in A$ yang memenuhi $a \ge \vc 0$.",
        r"$\norm\tau = 1$. Jika $A$ beridentitas, syarat ini ekuivalen dengan $\tau(\vc 1_A) = 1$.",
        r"pada aljabar-$C^*$ beridentitas $A$ bersifat positif jika dan hanya jika",
        r"suatu aljabar-$C^*$ $A$.",
        "skalar secara titik demi titik; yaitu,",
    )
    for anchor in required_corrections:
        if anchor not in target:
            errors.append(f"required correction missing: {anchor!r}")

    includes = re.findall(r"\\include\{([^}]+)\}", master)
    if includes != EXPECTED_INCLUDES:
        errors.append(f"master include sequence differs: {includes!r}")
    required_master = (
        "Unit Pembaca Kumulatif Bab 1--13",
        "batas produksi Bab 1--13",
        "Bab 1 sampai Bab 13",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "Creative Commons",
        "CC BY-SA 4.0",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University",
        "\\input{DIAGXY.TEX}",
    )
    for anchor in required_master:
        if anchor not in master:
            errors.append(f"required master rights/provenance anchor missing: {anchor!r}")
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

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if ledger.get("record_count") != 6 or ledger.get("target", {}).get("sha256") != EXPECTED["target_sha256"]:
        errors.append("correction ledger is not bound to the locked target")

    report = {
        "schema_version": "o008.ch13-translation-qa.v1",
        "unit_id": "FAOA-2015-CH13",
        "status": "pass" if not errors else "fail",
        "identities": identities,
        "structure": {
            "source_records": len(source.splitlines()),
            "target_records": len(target.splitlines()),
            "sections": len(target_sections),
            "environment_openings": len(target_begins),
            "environment_counts": dict(sorted(Counter(target_begins).items())),
            "labels": len(target_labels),
            "references": len(target_refs),
            "citations": len(target_cites),
            "index_hooks": target.count("\\index{"),
            "defined_terms": len(target_terms),
            "exercises": target.count("\\begin{exer}"),
            "proofs": target.count("\\begin{proof}"),
        },
        "math": {
            "source_surfaces": len(source_math),
            "target_surfaces": len(target_math),
            "classified_edit_blocks": edits,
        },
        "linkage": {
            "cumulative_labels": len(all_labels),
            "unresolved_references": unresolved_refs,
            "unresolved_citations": unresolved_cites,
        },
        "rights_and_provenance": {
            "license": "CC BY-SA 4.0",
            "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
            "excluded_components_absent": True,
            "nonendorsement_present": True,
        },
        "errors": errors,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
