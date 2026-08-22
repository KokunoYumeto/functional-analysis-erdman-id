#!/usr/bin/env python3
"""Locked structural, mathematical, rights, correction, and residue audit for CH07."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qa"))
sys.path.insert(0, str(ROOT / "backend"))
import check_ch05_translation as common  # noqa: E402
import ch03_math  # noqa: E402


SOURCE = ROOT / "source" / "upstream" / "compact_operators.tex"
TARGET = ROOT / "source" / "id-ID" / "compact_operators-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch07.tex"
CORRECTIONS = ROOT / "provenance" / "SOURCE_CORRECTIONS.md"

SOURCE_BYTES = 21_755
SOURCE_LINES = 517
SOURCE_SHA256 = "a1f55b061f526f3e536e5a812f073781777b6f990b662f4a1dba07475152d663"

TARGET_BYTES = 22_735
TARGET_LINES = 517
TARGET_SHA256 = "8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a"

EXPECTED_CHAPTER_TITLE = "OPERATOR KOMPAK"
EXPECTED_SECTION_TITLES = [
    "Definisi dan Sifat-Sifat Dasar",
    "Isometri Parsial",
    "Operator Kelas Jejak",
    "Operator Hilbert--Schmidt",
]

EXPECTED_ENVIRONMENT_BEGIN_COUNTS = {
    "cor": 2,
    "defn": 11,
    "enumerate": 2,
    "exam": 17,
    "exer": 1,
    "proof": 9,
    "prop": 28,
    "thm": 2,
}

EXPECTED_COUNTS = {
    "environment_pairs": 72,
    "labels": 20,
    "references": 13,
    "ordinary_target_references": 10,
    "future_target_references": 3,
    "equation_references": 0,
    "citations": 8,
    "indexes": 91,
    "defined_terms": 26,
    "exercises": 1,
    "proofs": 9,
    "proof_hints": 7,
    "citation_only_proofs": 2,
    "source_math_surfaces": 309,
    "target_math_surfaces": 309,
}

EXPECTED_FUTURE_REFERENCES = [
    ("12.3.16", "00152171"),
    ("12.3.17", "00152181"),
    ("11.5.7", "X_sqroot_op"),
]

# SequenceMatcher edits over text-aware math keys.  Fields are:
# tag, source-first, source-last, target-first, target-last,
# source delimiters, source key hashes, target delimiters, target key hashes,
# classification.  No unclassified mathematical edit is accepted.
EXPECTED_MATH_EDITS = [
    (
        "replace", 69, 69, 69, 69,
        ("dollar-inline",),
        ("db49ba8771d730e93dd579b030bc7fdf9b527b5912193df4ecd4fe425550e8b1",),
        ("dollar-inline",),
        ("886fa50b0d2a45607558cdc3611b0b7eb2a749c5e1afe2f1407c7622761a36da",),
        "source correction: K(H) -> K(B) in the Banach-space example",
    ),
    (
        "delete", 91, 91, 91, 90,
        ("dollar-inline",),
        ("6851ca5100c70ea737dab8af1d3a2dc4a49dde4dc4cb3a32cd305c9c4179769a",),
        (), (),
        "localization reordering, paired with the identical CSA insertion",
    ),
    (
        "insert", 94, 93, 93, 93,
        (), (),
        ("dollar-inline",),
        ("6851ca5100c70ea737dab8af1d3a2dc4a49dde4dc4cb3a32cd305c9c4179769a",),
        "localization reordering, paired with the identical CSA deletion",
    ),
    (
        "replace", 249, 249, 249, 249,
        ("dollar-inline",),
        ("eb928c603e86839785e7a486d06f462b050ec54274e0c944580fd8058bdf0d26",),
        ("dollar-inline",),
        ("a5aa09bdceb3a9e08fd21e65a6d25f95b44edf58cf86878ba34f9e85724b18c6",),
        "source correction: positive scalar alpha >= 0",
    ),
    (
        "replace", 263, 263, 263, 263,
        ("dollar-inline",),
        ("80dbdc39f2abaa2306ed13c3e8d601bf21105ea10c3ad7f56d2f39da67dfd4b4",),
        ("dollar-inline",),
        ("c61014ec1aefa668fe1ca9ee23665d41d0931a343725c482411ff15f1020b205",),
        "source correction: the introduced unitary U maps the bases",
    ),
    (
        "delete", 267, 267, 267, 266,
        ("dollar-inline",),
        ("de5a6f78116eca62d7fc5ce159d23ae6b889b365a1739ad2cf36f925a140d0cc",),
        (), (),
        "source-language repair: remove redundant second V in malformed cone definition",
    ),
    (
        "insert", 276, 275, 275, 275,
        (), (),
        ("dollar-inline",),
        ("44bd7ae60f478fae1061e11a7739f4b94d1daf917982d33b6fc8a01a63f89c21",),
        "source correction: bind the Hilbert space H used by B(H)",
    ),
    (
        "replace", 309, 309, 309, 309,
        ("dollar-inline",),
        ("f74a2620878c8894faff20a2db3668a8dfb49d99bb32cf4ae326d95f3202a30b",),
        ("dollar-inline",),
        ("056b0b65ead12e6625cfe50812834ba13bff8e9872fd43bea6d639e7e8b37717",),
        "source correction: restore comma after e_1",
    ),
]

REQUIRED_CONTROLLED_TERMS = (
    "operator kompak",
    "isometri parsial",
    "ruang awal",
    "ruang akhir",
    "dekomposisi polar",
    "kelas jejak",
    "Hilbert--Schmidt",
    "kerucut konveks proper",
    "ideal\ndua sisi",
    "masalah aproksimasi",
    "operator integral",
    "terintegralkan kuadrat",
    "operator diagonal",
)

FORBIDDEN_TERM_VARIANTS = (
    "kerucut wajar",
    "konus",
    "operator berjejak",
    "isometri sebagian",
    "ruang inisial",
    "ruang final",
    "dekomposisi kutub",
    "kelas trace",
    "masalah pendekatan",
)

EXTRA_RESIDUE_RE = re.compile(
    r"\b(?:totally bounded|weakly|strongly|compactness|compact|"
    r"partial isometr(?:y|ies)|polar decomposition|trace class|trace|"
    r"two-sided|square-integrable|approximation problem|finite rank|"
    r"bounded linear map|unitary|self-adjoint|projection|range)\b",
    re.IGNORECASE,
)


def key_sha(item: dict) -> str:
    key = ch03_math.math_key(item["normalized"])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def math_edit_signature(source_math: list[dict], target_math: list[dict]) -> list[tuple]:
    source_keys = [ch03_math.math_key(item["normalized"]) for item in source_math]
    target_keys = [ch03_math.math_key(item["normalized"]) for item in target_math]
    output: list[tuple] = []
    matcher = SequenceMatcher(None, source_keys, target_keys, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        output.append(
            (
                tag,
                i1 + 1,
                i2,
                j1 + 1,
                j2,
                tuple(item["delimiter"] for item in source_math[i1:i2]),
                tuple(key_sha(item) for item in source_math[i1:i2]),
                tuple(item["delimiter"] for item in target_math[j1:j2]),
                tuple(key_sha(item) for item in target_math[j1:j2]),
            )
        )
    return output


def future_reference_sequence(text: str) -> list[tuple[str, str]]:
    active = common.shared.active_same_length(text)
    return [
        (match.group(1), match.group(2))
        for match in re.finditer(r"\\futurexref\{([^{}]+)\}\{([^{}]+)\}", active)
    ]


def environment_begin_counts(sequence: list[tuple[str, str]]) -> dict[str, int]:
    names = sorted({name for kind, name in sequence if kind == "begin"})
    return {
        name: sum(kind == "begin" and candidate == name for kind, candidate in sequence)
        for name in names
    }


def chapter_seven_ledger_block(text: str) -> str:
    match = re.search(r"(?ms)^## Chapter 7\s*$\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def main() -> int:
    errors: list[str] = []
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    source = source_bytes.decode("ascii")
    target = target_bytes.decode("utf-8")

    source_identity = (
        len(source_bytes), common.line_count(source_bytes), common.sha256(source_bytes)
    )
    target_identity = (
        len(target_bytes), common.line_count(target_bytes), common.sha256(target_bytes)
    )
    if source_identity != (SOURCE_BYTES, SOURCE_LINES, SOURCE_SHA256):
        errors.append(f"source identity mismatch: {source_identity!r}")
    if target_identity != (TARGET_BYTES, TARGET_LINES, TARGET_SHA256):
        errors.append(f"target identity mismatch: {target_identity!r}")

    if (
        source_bytes.startswith(b"\xef\xbb\xbf")
        or source_bytes.count(b"\r\n") != SOURCE_LINES
        or source_bytes.count(b"\n") != SOURCE_LINES
        or source_bytes.count(b"\r") != SOURCE_LINES
        or not source_bytes.endswith(b"\r\n")
    ):
        errors.append("source must retain the frozen BOM-free 517-line CRLF form")
    if (
        target_bytes.startswith(b"\xef\xbb\xbf")
        or b"\r" in target_bytes
        or target_bytes.count(b"\n") != TARGET_LINES
        or not target_bytes.endswith(b"\n")
    ):
        errors.append("target must be BOM-free UTF-8 with 517 LF-terminated lines")

    chapter, sections = common.chapter_and_sections(target)
    if chapter != EXPECTED_CHAPTER_TITLE or sections != EXPECTED_SECTION_TITLES:
        errors.append(f"chapter/section titles differ: {chapter!r}, {sections!r}")

    source_env = common.env_sequence(source)
    target_env = common.env_sequence(target)
    if source_env != target_env:
        errors.append("ordered begin/end environment topology differs")
    pairs = len(target_env) // 2
    if pairs != EXPECTED_COUNTS["environment_pairs"]:
        errors.append(f"environment pair count {pairs}")
    begin_counts = environment_begin_counts(target_env)
    if begin_counts != EXPECTED_ENVIRONMENT_BEGIN_COUNTS:
        errors.append(f"environment opening census differs: {begin_counts!r}")

    for name, expected in (("label", 20), ("cite", 8)):
        source_args = common.command_arguments(source, name)
        target_args = common.command_arguments(target, name)
        if source_args != target_args:
            errors.append(f"ordered {name} closure differs")
        if len(target_args) != expected:
            errors.append(f"{name} count {len(target_args)} != {expected}")

    source_refs = common.reference_sequence(source)
    target_refs = common.reference_sequence(target)
    source_ref_values = [(kind, value) for _, kind, value in source_refs]
    target_ref_values = [(kind, value) for _, kind, value in target_refs]
    if source_ref_values != target_ref_values:
        errors.append("ordered ref/eqref/futurexref endpoint closure differs")
    source_ref_count = sum(kind == "ref" for _, kind, _ in source_refs)
    source_eqref_count = sum(kind == "eqref" for _, kind, _ in source_refs)
    ordinary_target_refs = len(common.command_arguments(target, "ref"))
    future_refs = future_reference_sequence(target)
    if (
        source_ref_count != EXPECTED_COUNTS["references"]
        or source_eqref_count != EXPECTED_COUNTS["equation_references"]
        or ordinary_target_refs != EXPECTED_COUNTS["ordinary_target_references"]
        or len(future_refs) != EXPECTED_COUNTS["future_target_references"]
    ):
        errors.append(
            "reference census differs: "
            f"source ref/eqref={source_ref_count}/{source_eqref_count}, "
            f"target ordinary/future={ordinary_target_refs}/{len(future_refs)}"
        )
    if future_refs != EXPECTED_FUTURE_REFERENCES:
        errors.append(f"futurexref surfaces differ: {future_refs!r}")

    source_index = common.command_arguments(source, "index")
    target_index = common.command_arguments(target, "index")
    if len(source_index) != 91 or len(target_index) != 91:
        errors.append(f"index count source/target {len(source_index)}/{len(target_index)}")
    if [common.index_signature(item) for item in source_index] != [
        common.index_signature(item) for item in target_index
    ]:
        errors.append("ordered MakeIndex operator signatures differ")

    source_df = common.command_arguments(source, "df")
    target_df = common.command_arguments(target, "df")
    if len(source_df) != 26 or len(target_df) != 26:
        errors.append(f"defined-term count source/target {len(source_df)}/{len(target_df)}")

    target_exercises = sum(kind == "begin" and env == "exer" for kind, env in target_env)
    target_proofs = sum(kind == "begin" and env == "proof" for kind, env in target_env)
    source_hint = re.compile(r"\\begin\{proof\}\[\\emph\{Hint for proof\}\]")
    target_hint = re.compile(r"\\begin\{proof\}\[\\emph\{Petunjuk untuk bukti\}\]")
    source_hints = len(source_hint.findall(source))
    target_hints = len(target_hint.findall(target))
    source_citation_only = source.count(r"\begin{proof} See ")
    target_citation_only = target.count(r"\begin{proof} Lihat ")
    if (
        target_exercises != EXPECTED_COUNTS["exercises"]
        or target_proofs != EXPECTED_COUNTS["proofs"]
        or source_hints != EXPECTED_COUNTS["proof_hints"]
        or target_hints != EXPECTED_COUNTS["proof_hints"]
        or source_citation_only != EXPECTED_COUNTS["citation_only_proofs"]
        or target_citation_only != EXPECTED_COUNTS["citation_only_proofs"]
    ):
        errors.append(
            "exercise/proof/hint closure differs: "
            f"exercise={target_exercises}, proof={target_proofs}, "
            f"hints={source_hints}/{target_hints}, "
            f"citation-only={source_citation_only}/{target_citation_only}"
        )

    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (309, 309):
        errors.append(f"math count source/target {len(source_math)}/{len(target_math)}")
    if [item["delimiter"] for item in source_math] != [
        item["delimiter"] for item in target_math
    ]:
        errors.append("ordered math delimiter topology differs")
    math_edits = math_edit_signature(source_math, target_math)
    expected_math_signatures = [item[:-1] for item in EXPECTED_MATH_EDITS]
    if math_edits != expected_math_signatures:
        errors.append(f"math edit lock differs: {math_edits!r}")

    duplicate_prop = (
        "\\begin{prop} Suatu ruang metrik bersifat kompak jika dan hanya jika "
        "ruang itu lengkap dan terbatas total.\n\\end{prop}"
    )
    if target.count(duplicate_prop) != 2:
        errors.append("the two published compactness proposition environments were not retained")

    required_target_fragments = (
        "melanjutkan pembahasan dari akhir Bab 5",
        "$k$ suatu fungsi yang terintegralkan kuadrat",
        "(Lihat contoh~\\ref{X_l2ball_not_cpt}.)",
        "Jika $B$ berdimensi tak hingga, ideal $\\ofml K(B)$ adalah sejati.",
        "objek-objeknya memiliki sifat aljabar sekaligus topologis,\nmorfismenya hanya disyaratkan",
        "\\df{ruang akhir} dari~$V$.",
        "$\\alpha \\ge 0$",
        "$e^k = Uf^k$",
        "\\df{kerucut} jika $\\alpha C \\subseteq C$",
        "\\df{proper} jika $C \\cap (-C) = \\{\\vc 0\\}$.",
        "Pada suatu ruang Hilbert separabel $H$",
        "$\\{e_1, \\dots, e_n\\}$",
    )
    for fragment in required_target_fragments:
        if fragment not in target:
            errors.append(f"required correction/control fragment absent: {fragment}")
    if target.count(r"\allowbreak") != 3:
        errors.append(f"citation reflow allowbreak count {target.count(r'\allowbreak')} != 3")

    forbidden_target_fragments = (
        "$e^k = Tf^k$",
        "$\\alpha \\in  \\K$",
        "$\\{e_1 \\dots, e_n\\}$",
        "\\df{ruang akhir} dari~$V$.)",
        "Jika $B$ berdimensi tak hingga, ideal $\\ofml K(H)$",
        "C:\\Users",
        "codex://",
        "Github Tokens",
        "Zenodo token",
    )
    for fragment in forbidden_target_fragments:
        if fragment.lower() in target.lower():
            errors.append(f"forbidden source/private residue present: {fragment}")

    for term in REQUIRED_CONTROLLED_TERMS:
        if term.lower() not in target.lower():
            errors.append(f"controlled term absent: {term}")
    for term in FORBIDDEN_TERM_VARIANTS:
        if term.lower() in target.lower():
            errors.append(f"forbidden terminology variant present: {term}")

    residue = common.visible_residue(target, target_math)
    visible = common.blank_spans(
        common.shared.active_same_length(target),
        [(item["start"], item["end"]) for item in target_math]
        + [
            (item["start"], item["end"])
            for name in ("label", "ref", "eqref", "cite", "futurexref")
            for item in common.macro(target, name)
        ],
    )
    visible = re.sub(r"\\(?:begin|end)\{[^{}]+\}", " ", visible)
    visible = re.sub(r"\\[A-Za-z@]+\*?", " ", visible)
    extra_residue: list[dict] = []
    for line_no, line in enumerate(visible.splitlines(), 1):
        words = sorted({match.group(0) for match in EXTRA_RESIDUE_RE.finditer(line)})
        if words:
            extra_residue.append({"line": line_no, "words": words, "text": line.strip()})
    if residue or extra_residue:
        errors.append(f"visible English residue: {residue + extra_residue!r}")
    for marker in ("\ufffd", "Ã", "Â", "â€", "ðŸ", "ï»¿"):
        if marker in target:
            errors.append(f"mojibake marker present: {marker!r}")

    if target.count(r"\endinput") != 1 or not target.rstrip().endswith(r"\endinput"):
        errors.append("target must end with one terminal endinput")

    master = MASTER.read_text(encoding="utf-8")
    required_rights = (
        "Karya sumber John M. Erdman ini berlisensi Creative Commons",
        "Attribution--ShareAlike 4.0 International (CC BY-SA 4.0):",
        r"\url{https://creativecommons.org/licenses/by-sa/4.0/}.",
        "Terjemahan Bahasa Indonesia dan adaptasi teknis ini juga diterbitkan dengan",
        "lisensi CC BY-SA 4.0.",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University.",
        r"\input{DIAGXY.TEX}",
        r"\include{compact_operators-id}",
        "Epigraf pihak ketiga, gambar lencana lisensi, dan makro tabel yang",
        "status komponennya tidak cukup jelas tidak digunakan.",
    )
    for fragment in required_rights:
        if fragment not in master:
            errors.append(f"cumulative-reader rights closure absent: {fragment}")
    for fragment in (r"\input{TABLE.TEX}", "by-sa.eps", "by-sa.pdf"):
        if fragment.lower() in master.lower():
            errors.append(f"excluded component is active in cumulative reader: {fragment}")

    ledger = CORRECTIONS.read_text(encoding="utf-8")
    ledger_block = chapter_seven_ledger_block(ledger)
    if not ledger_block:
        errors.append("Chapter 7 correction-ledger block absent")
    else:
        required_ledger_fragments = (
            "compact_operators.tex:22--26",
            "compact_operators.tex:117",
            "compact_operators.tex:127--129",
            "compact_operators.tex:137",
            "compact_operators.tex:162--165",
            "compact_operators.tex:299",
            "compact_operators.tex:397--400",
            "compact_operators.tex:422",
            "compact_operators.tex:425--430",
            "compact_operators.tex:436--437",
            "compact_operators.tex:497",
            r"\futurexref{12.3.16}{00152171}",
            r"\futurexref{12.3.17}{00152181}",
            r"\futurexref{11.5.7}{X_sqroot_op}",
            r"TeX-only `\allowbreak` opportunities",
            "No upstream contact occurs during production.",
        )
        for fragment in required_ledger_fragments:
            if fragment not in ledger_block:
                errors.append(f"Chapter 7 correction-ledger item absent: {fragment}")

    result = {
        "result": "pass" if not errors else "fail",
        "source": {
            "bytes": len(source_bytes),
            "lines": common.line_count(source_bytes),
            "line_endings": "CRLF",
            "sha256": common.sha256(source_bytes),
        },
        "target": {
            "bytes": len(target_bytes),
            "lines": common.line_count(target_bytes),
            "line_endings": "LF",
            "sha256": common.sha256(target_bytes),
        },
        "counts": {
            "environment_pairs": pairs,
            "environment_openings": begin_counts,
            "labels": len(common.command_arguments(target, "label")),
            "references_including_futurexref": sum(kind == "ref" for _, kind, _ in target_refs),
            "ordinary_references": ordinary_target_refs,
            "future_references": len(future_refs),
            "equation_references": sum(kind == "eqref" for _, kind, _ in target_refs),
            "citations": len(common.command_arguments(target, "cite")),
            "indexes": len(target_index),
            "defined_terms": len(target_df),
            "exercises": target_exercises,
            "proofs": target_proofs,
            "proof_hints": target_hints,
            "citation_only_proofs": target_citation_only,
            "source_math_surfaces": len(source_math),
            "target_math_surfaces": len(target_math),
            "classified_math_edit_blocks": len(math_edits),
            "visible_english_residue": len(residue) + len(extra_residue),
        },
        "future_references": future_refs,
        "classified_math_edits": [
            {
                "signature": list(signature),
                "classification": expected[-1],
            }
            for signature, expected in zip(math_edits, EXPECTED_MATH_EDITS)
        ],
        "rights_wrapper_checked": str(MASTER.relative_to(ROOT)),
        "correction_ledger_checked": str(CORRECTIONS.relative_to(ROOT)),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
