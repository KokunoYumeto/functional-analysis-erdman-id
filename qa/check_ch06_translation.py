#!/usr/bin/env python3
"""Bounded structural, mathematical, correction, and residue audit for CH06."""

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


SOURCE = ROOT / "source" / "upstream" / "Banach_spaces.tex"
TARGET = ROOT / "source" / "id-ID" / "Banach_spaces-id.tex"

SOURCE_BYTES = 79_549
SOURCE_LINES = 1_605
SOURCE_SHA256 = "0f401d088ec3e2d3f2ca4dafa2595a7f0049193a097b6b27af7b247fd433df51"

# Rebind after independent rereview and final prose polish.
TARGET_BYTES: int | None = 82_940
TARGET_LINES: int | None = 1_569
TARGET_SHA256: str | None = "ca32547e4b47af3444d454476beac71ad8870e88b436dc008e1cb5dbb6755e9c"

EXPECTED_CHAPTER_TITLE = "RUANG BANACH"
EXPECTED_SECTION_TITLES = [
    "Transformasi Alami",
    "Teorema Alaoglu",
    "Teorema Pemetaan Terbuka",
    "Teorema Graf Tertutup",
    "Dualitas Ruang Banach",
    "Proyeksi dan Subruang Terkomplemen",
    "Prinsip Keterbatasan Seragam",
]

EXPECTED_COUNTS = {
    "environment_pairs": 178,
    "labels": 56,
    "references": 80,
    "equation_references": 2,
    "citations": 13,
    "indexes": 155,
    "defined_terms": 47,
    "exercises": 6,
    "proofs": 29,
    "semantic_proof_hints": 28,
    "source_math_surfaces": 1_155,
    "target_math_surfaces": 1_156,
}

# SequenceMatcher edits over normalized text-aware math keys. Each tuple is:
# tag, source-first, source-last, target-first, target-last,
# source delimiters, source key hashes, target delimiters, target key hashes.
EXPECTED_MATH_EDITS = [
    ("replace", 133, 134, 133, 134,
     ("dollar-inline", "dollar-inline"),
     ("180e2d99f603f0f1bdb15871deda36095932281742b3fd446bfa9d717937704a", "b086ae762e0cb0e4337bd985a2ab173fa4371b0a004238fc4a644a7cb3dc0320"),
     ("dollar-inline", "dollar-inline"),
     ("aa8766479fadc0250ff31cb73d3cf8f487a1fda018a9661b896a18ee96d7fda3", "9ee13facf112d1a4469d18bd4a5ebcfd232c70c11ba5cc892b98c420ada22b5d")),
    ("replace", 165, 165, 165, 165, ("dollar-inline",),
     ("3174655537dfe20b0eba32c3b9fd25430734abf32fb7d6dee3fd90fa684dcf7f",),
     ("dollar-inline",), ("cf3a2a8ec03e17fd598fff01cf07e0e110732ec0a4222098c82706028f2f17ba",)),
    ("replace", 167, 167, 167, 167, ("dollar-inline",),
     ("8c03832d20f54a524339ce52a8bd7d709ba82efe755d0df7534828f8178ddba8",),
     ("dollar-inline",), ("69d916ebc964955f0aa24aa291b47e6065f60c8039987d699bdf9c125d0d3a48",)),
    ("replace", 316, 316, 316, 316, ("dollar-inline",),
     ("516ba82f59b018568a8b78021e005455e9b43b1f57444b44f2a5cff3e4a16b5f",),
     ("dollar-inline",), ("fa0fad2c42e1adfb3777aa97bc9006b19aee5ad43e7cccc8c1bf9d97eb1cbff1",)),
    ("replace", 330, 330, 330, 330, ("dollar-inline",),
     ("fd79ee3854526a30575658a615a86e18278f1524c17eefdb9bbee4c9b8ff1c7b",),
     ("dollar-inline",), ("2269ab98b73cdd7c65adc6dcfa6e984ecdef5db960403c315809ea37011d558a",)),
    ("insert", 531, 530, 531, 531, (), (), ("dollar-inline",),
     ("559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd",)),
    ("replace", 669, 669, 670, 670, ("dollar-inline",),
     ("5ae23f6d4b817b5897ac028f8d939e5378abca0e5390b45cfedd0053f7423fea",),
     ("dollar-inline",), ("8254c329a92850f6d539dd376f4816ee2764517da5e0235514af433164480d7a",)),
    ("insert", 685, 684, 686, 686, (), (), ("dollar-inline",),
     ("6278ae45a1b93fda379c46cb09471ff4cb5557adde727163ddd16a32cf88ad58",)),
    ("delete", 686, 687, 688, 687,
     ("dollar-inline", "dollar-inline"),
     ("175651834a5356f20944caa0598e84804b79cf97d0df5a596089da31b9b12897", "db8e84427c2e1e02f2b2c74d337ab8d69d80cbb28224cd7f85e0174f1f5ed5c7"),
     (), ()),
    ("insert", 710, 709, 710, 710, (), (), ("dollar-inline",),
     ("df7e70e5021544f4834bbee64a9e3789febc4be81470df629cad6ddb03320a5c",)),
    ("replace", 721, 721, 722, 722, ("dollar-inline",),
     ("99a2f49d2c37e889a1cad3e5e4ceb8e8fce02a61ce25e6b99b27f247d3215517",),
     ("dollar-inline",), ("1b16b1df538ba12dc3f97edbb85caa7050d46c148134290feba80f8236c83db9",)),
    ("insert", 833, 832, 834, 834, (), (), ("dollar-inline",),
     ("0ee9315cade9568c7830ae858b854d69552775d7720b4d57b706c0b5610a6cea",)),
    ("delete", 834, 834, 836, 835, ("dollar-inline",),
     ("0ee9315cade9568c7830ae858b854d69552775d7720b4d57b706c0b5610a6cea",), (), ()),
    ("insert", 856, 855, 857, 857, (), (), ("dollar-inline",),
     ("08f271887ce94707da822d5263bae19d5519cb3614e0daedc4c7ce5dab7473f1",)),
    ("delete", 857, 857, 859, 858, ("dollar-inline",),
     ("08f271887ce94707da822d5263bae19d5519cb3614e0daedc4c7ce5dab7473f1",), (), ()),
    ("replace", 893, 893, 894, 894, ("dollar-inline",),
     ("4474d05e7e3722504d0d1f8e4b6e367711f9ea744e10a6c2faacad27514d149c",),
     ("dollar-inline",), ("fc1ebaffebf51f418478240060a4767fe3a9b4acd4d9f6ec3c9ce679e7d62ea9",)),
    ("insert", 905, 904, 906, 906, (), (), ("dollar-inline",),
     ("32dc5ddd63ea107c3972abc72f57d09bea4b3e4c5e624eb0d9418495e8e92aa1",)),
    ("delete", 906, 906, 908, 907, ("dollar-inline",),
     ("32dc5ddd63ea107c3972abc72f57d09bea4b3e4c5e624eb0d9418495e8e92aa1",), (), ()),
    ("replace", 926, 926, 927, 927, ("dollar-inline",),
     ("ca2437e7e1fe83c5c89269a07df86e59c41e09091b4f64ee95cf6b6bf8857754",),
     ("dollar-inline",), ("59db512e08c86a0443cb5870fd2ec0a180d8cfd4042b101485fccc94e3cc2bd8",)),
    ("replace", 964, 964, 965, 965, ("dollar-inline",),
     ("08f271887ce94707da822d5263bae19d5519cb3614e0daedc4c7ce5dab7473f1",),
     ("dollar-inline",), ("df7e70e5021544f4834bbee64a9e3789febc4be81470df629cad6ddb03320a5c",)),
    ("replace", 1064, 1064, 1065, 1065, ("dollar-inline",),
     ("6ab534210f1624cb8da27d72358b26b00febdfbb4d59add41d9d5a24387ac3ea",),
     ("dollar-inline",), ("4ebad0f3daddab928bae3c07f4dc26e1994aac791ead938855bea168ad6323cb",)),
    ("replace", 1090, 1092, 1091, 1093,
     ("dollar-inline", "dollar-inline", "dollar-inline"),
     ("cdf1385b876eefcab2bfbff9bc565d914a07a7cd0ce47099241810b7fa211797", "b086ae762e0cb0e4337bd985a2ab173fa4371b0a004238fc4a644a7cb3dc0320", "44ef691e294112b7f4ee74efade73ed5066136dadff5816c13e1f316e1de55ea"),
     ("dollar-inline", "dollar-inline", "dollar-inline"),
     ("263c32e38a2751fd0a6f5b3eccfbd91b8c788f98d0e763d1cb88957a1cd919ae", "9ee13facf112d1a4469d18bd4a5ebcfd232c70c11ba5cc892b98c420ada22b5d", "76bd086d6652edb23dc1adb47b381fa8a64738236ee7938f8a9753868a280f37")),
]

EXTRA_RESIDUE_RE = re.compile(
    r"\b(?:range|net|subnet|continuous|mapping|bounded|weakly|strongly|"
    r"uniformly|closed|open|space|vector|projection)\b",
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


def main() -> int:
    errors: list[str] = []
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    source = source_bytes.decode("ascii")
    target = target_bytes.decode("utf-8")

    if (len(source_bytes), common.line_count(source_bytes), common.sha256(source_bytes)) != (
        SOURCE_BYTES, SOURCE_LINES, SOURCE_SHA256
    ):
        errors.append("source identity mismatch")
    if TARGET_BYTES is not None and len(target_bytes) != TARGET_BYTES:
        errors.append(f"target bytes {len(target_bytes)} != {TARGET_BYTES}")
    if TARGET_LINES is not None and common.line_count(target_bytes) != TARGET_LINES:
        errors.append(f"target lines {common.line_count(target_bytes)} != {TARGET_LINES}")
    if TARGET_SHA256 is not None and common.sha256(target_bytes) != TARGET_SHA256:
        errors.append("target SHA-256 mismatch")
    if target_bytes.startswith(b"\xef\xbb\xbf") or b"\r" in target_bytes:
        errors.append("target must be BOM-free UTF-8 with LF-only endings")

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

    for name, expected in (("label", 56), ("cite", 13)):
        source_args = common.command_arguments(source, name)
        target_args = common.command_arguments(target, name)
        if source_args != target_args or len(target_args) != expected:
            errors.append(f"ordered {name} closure differs")

    source_refs = common.reference_sequence(source)
    target_refs = common.reference_sequence(target)
    source_ref_values = [(kind, value) for _, kind, value in source_refs]
    target_ref_values = [(kind, value) for _, kind, value in target_refs]
    if source_ref_values != target_ref_values:
        errors.append("ordered ref/eqref/futurexref targets differ")
    source_ref_count = sum(kind == "ref" for _, kind, _ in source_refs)
    source_eqref_count = sum(kind == "eqref" for _, kind, _ in source_refs)
    if (source_ref_count, source_eqref_count) != (80, 2):
        errors.append("source reference census differs")
    if target.count(r"\futurexref{11.2.20}{000731}") != 1:
        errors.append("Chapter 11 futurexref endpoint differs")

    source_index = common.command_arguments(source, "index")
    target_index = common.command_arguments(target, "index")
    if len(source_index) != 155 or len(target_index) != 155:
        errors.append("index count differs")
    if [common.index_signature(item) for item in source_index] != [
        common.index_signature(item) for item in target_index
    ]:
        errors.append("ordered MakeIndex operator signatures differ")

    source_df = common.command_arguments(source, "df")
    target_df = common.command_arguments(target, "df")
    if len(source_df) != 47 or len(target_df) != 47:
        errors.append("defined-term count differs")

    source_exercises = sum(kind == "begin" and env == "exer" for kind, env in source_env)
    target_exercises = sum(kind == "begin" and env == "exer" for kind, env in target_env)
    source_proofs = sum(kind == "begin" and env == "proof" for kind, env in source_env)
    target_proofs = sum(kind == "begin" and env == "proof" for kind, env in target_env)
    if (source_exercises, target_exercises, source_proofs, target_proofs) != (6, 6, 29, 29):
        errors.append("exercise/proof closure differs")

    source_hint = re.compile(r"\\begin\{proof\}\[(?:\\emph\{)?Hint for proof\}?]")
    target_hint = re.compile(r"\\begin\{proof\}\[\\emph\{Petunjuk pembuktian\}\]")
    if len(source_hint.findall(source)) != 28 or len(target_hint.findall(target)) != 28:
        errors.append("semantic proof-hint closure differs")

    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (1_155, 1_156):
        errors.append(f"math count source/target {len(source_math)}/{len(target_math)}")
    math_edits = math_edit_signature(source_math, target_math)
    if math_edits != EXPECTED_MATH_EDITS:
        errors.append(f"math edit lock differs: {math_edits!r}")

    residue = common.visible_residue(target, target_math)
    extra_residue: list[dict] = []
    visible = common.blank_spans(
        common.shared.active_same_length(target),
        [(item["start"], item["end"]) for item in target_math]
        + [(item["start"], item["end"]) for name in ("label", "ref", "eqref", "cite", "futurexref") for item in common.macro(target, name)],
    )
    visible = re.sub(r"\\(?:begin|end)\{[^{}]+\}", " ", visible)
    visible = re.sub(r"\\[A-Za-z@]+\*?", " ", visible)
    for line_no, line in enumerate(visible.splitlines(), 1):
        words = sorted({m.group(0) for m in EXTRA_RESIDUE_RE.finditer(line)})
        if words:
            extra_residue.append({"line": line_no, "words": words, "text": line.strip()})
    if residue or extra_residue:
        errors.append(f"visible English residue: {residue + extra_residue!r}")

    required = (
        r"M \subseteq \{0\}",
        r"F \subseteq \{0\}",
        r"\cat{BAN_\infty}",
        r"Contoh~\ref{C069431}",
        r"\preccurlyeq C",
        r"B \mapsto B^*",
        r"\abs{a^{**}(f)}",
        r"\right.",
        r"<arrowtosot@",
        r"<arrowtouniform@",
    )
    for needle in required:
        if needle not in target:
            errors.append(f"required correction absent: {needle}")
    forbidden = (
        r"\cat{BAN_1}",
        r"exercise~\ref{C069431}",
        r"\norm{(y - v_0) - w_o}",
        r"B \mapsto B*",
        r"\sup\{a^{**}(f)\colon a \in A\}",
        r"\right\}",
        r"<arrowtowot@$T_\lambda~\to^{\textbf{SOT}}",
        r"<arrowtowot@$T_\lambda~\sto~S$",
        "C:\\Users",
        "codex://",
    )
    for needle in forbidden:
        if needle.lower() in target.lower():
            errors.append(f"forbidden residue present: {needle}")

    if target.count(r"\endinput") != 1 or not target.rstrip().endswith(r"\endinput"):
        errors.append("target must end with one terminal endinput")

    result = {
        "result": "pass" if not errors else "fail",
        "source": {"bytes": len(source_bytes), "lines": common.line_count(source_bytes), "sha256": common.sha256(source_bytes)},
        "target": {"bytes": len(target_bytes), "lines": common.line_count(target_bytes), "sha256": common.sha256(target_bytes)},
        "counts": {
            "environment_pairs": pairs,
            "labels": len(common.command_arguments(target, "label")),
            "references_including_futurexref": sum(kind == "ref" for _, kind, _ in target_refs),
            "equation_references": sum(kind == "eqref" for _, kind, _ in target_refs),
            "citations": len(common.command_arguments(target, "cite")),
            "indexes": len(target_index),
            "defined_terms": len(target_df),
            "exercises": target_exercises,
            "proofs": target_proofs,
            "semantic_proof_hints": len(target_hint.findall(target)),
            "source_math_surfaces": len(source_math),
            "target_math_surfaces": len(target_math),
            "classified_math_edit_blocks": len(math_edits),
            "visible_english_residue": len(residue) + len(extra_residue),
        },
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
