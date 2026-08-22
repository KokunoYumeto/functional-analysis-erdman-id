#!/usr/bin/env python3
"""Bounded structural, mathematical, and residue audit for FAOA-2015-CH05."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import generate_ch01_backend as shared  # noqa: E402
import ch03_math  # noqa: E402


SOURCE = ROOT / "source" / "upstream" / "Hilbert_space_operators.tex"
TARGET = ROOT / "source" / "id-ID" / "Hilbert_space_operators-id.tex"

SOURCE_BYTES = 48_838
SOURCE_LINES = 1_147
SOURCE_SHA256 = "93293a89c9a9f34315a43d6f114084490ceb370119fb09aeaccabe634efb96b1"

# Bound after the complete translation and source-correction adjudication.
TARGET_BYTES: int | None = 51529
TARGET_LINES: int | None = 1147
TARGET_SHA256: str | None = "323f0b156eb6e945e3b6ed273da298af4e0e2b2d9abb73514a9018cbe0d0b29f"

EXPECTED_CHAPTER_TITLE = "OPERATOR PADA RUANG HILBERT"
EXPECTED_SECTION_TITLES = [
    "Pemetaan Linear Invertibel dan Isometri",
    "Operator dan Adjoinnya",
    "Aljabar dengan Involusi",
    "Operator Swaadjoin",
    "Proyeksi",
    "Operator Normal",
    "Operator Berperingkat Hingga",
]

EXPECTED_COUNTS = {
    "environment_pairs": 152,
    "labels": 39,
    "references": 24,
    "equation_references": 1,
    "citations": 1,
    "indexes": 168,
    "defined_terms": 56,
    "exercises": 4,
    "proof_hints": 17,
    # The frozen inventory's 831 mechanical constructs count four nested
    # dollar pairs inside \text payloads separately.  The text-aware extractor
    # retains each such inner pair inside its outer surface, hence 827 records.
    "math_surfaces": 827,
}

# Each tuple locks one deliberate source/target mathematical delta:
# (source ordinal, target ordinal, source line, target line,
#  delimiter, source math-key SHA-256, target math-key SHA-256, disposition).
EXPECTED_MATH_MISMATCHES: list[tuple] = [
    (
        104,
        104,
        188,
        188,
        "dollar-inline",
        "0139a2294b3bd1c6dfd309bd1117f28ee8f93f5712db14b2ec8129069a3f99a3",
        "eb866dd8470e169e63eeea17ccf7a4d4c742e70a47568bcdbc54ac4ecea851d5",
        "sesquilinear_bound_uses_y_in_K",
    ),
    (
        304,
        304,
        481,
        481,
        "dollar-inline",
        "573057da010d25690f2da8d24243a1da045d307720248521b590e160e63ea51f",
        "8420cfccac87eb8a03db76c901855d2cfbe378823b2ce27a3032e7f920c17f5c",
        "conjugation_uses_conj_not_closure_macro",
    ),
    (
        550,
        550,
        791,
        791,
        "dollar-inline",
        "2171bce1de561fa038cf3fc7defb2d3e343bdfeced99ae68f8f40be72df60ecd",
        "cd6a51568c71e4ad0ae114e49f8cbef19206c281a98c6de234fbdded4f8835f2",
        "real_plane_uses_field_macro_first_occurrence",
    ),
    (
        553,
        553,
        792,
        792,
        "dollar-inline",
        "2171bce1de561fa038cf3fc7defb2d3e343bdfeced99ae68f8f40be72df60ecd",
        "cd6a51568c71e4ad0ae114e49f8cbef19206c281a98c6de234fbdded4f8835f2",
        "real_plane_uses_field_macro_second_occurrence",
    ),
    (
        639,
        639,
        864,
        864,
        "dollar-inline",
        "0496cc6d37df6383ddaf2c240749822cd1384984af24f98a76e60a66e7244536",
        "1e105b215fd2d4e7c99395aa9447b20db49916f38921e66c942de0ab5c834282",
        "positive_element_avoids_premature_A_plus_notation",
    ),
    (
        810,
        810,
        1106,
        1106,
        "dollar-inline",
        "44bd7ae60f478fae1061e11a7739f4b94d1daf917982d33b6fc8a01a63f89c21",
        "0b45fc027e165a02dc1fcabd03cfa38c33042b1c22a4a8e896d2533e51816335",
        "minimal_ideal_requires_nonzero_Hilbert_space",
    ),
]

RESIDUE_RE = re.compile(
    r"\b(?:the|this|these|those|and|or|if|then|let|suppose|where|which|"
    r"that|from|into|between|with|without|there|exists|unique|every|following|"
    r"preceding|proof|hint|example|definition|proposition|corollary|theorem|"
    r"exercise|called|denoted|said|such|when|while|although|because|hence|"
    r"therefore|respectively)\b",
    re.IGNORECASE,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def line_count(data: bytes) -> int:
    return len(data.splitlines())


def macro(text: str, name: str) -> list[dict]:
    """Return exact TeX macro calls, excluding prefixes such as df in dfrac."""

    active = shared.active_same_length(text)
    pattern = re.compile(r"\\" + re.escape(name) + r"(?![A-Za-z@])\s*\{")
    output: list[dict] = []
    for match in pattern.finditer(active):
        brace = active.find("{", match.start())
        end = shared.balanced_end(active, brace)
        output.append(
            {
                "start": match.start(),
                "end": end,
                "argument": text[brace + 1 : end - 1],
                "line": shared.line_of(text, match.start()),
            }
        )
    return output


def env_sequence(text: str) -> list[tuple[str, str]]:
    active = shared.active_same_length(text)
    return [
        (match.group(1), match.group(2))
        for match in re.finditer(r"\\(begin|end)\{([^{}]+)\}", active)
    ]


def command_arguments(text: str, command: str) -> list[str]:
    return [item["argument"] for item in macro(text, command)]


def chapter_and_sections(text: str) -> tuple[str, list[str]]:
    chapter = command_arguments(text, "chapter")
    sections = command_arguments(text, "section")
    if len(chapter) != 1:
        raise ValueError(f"expected one chapter title, got {len(chapter)}")
    return chapter[0], sections


def reference_sequence(text: str) -> list[tuple[int, str, str]]:
    records: list[tuple[int, str, str]] = []
    for name in ("ref", "eqref"):
        for item in macro(text, name):
            records.append((item["start"], name, item["argument"]))
    active = shared.active_same_length(text)
    future = re.compile(r"\\futurexref\{([^{}]*)\}\{([^{}]+)\}")
    for match in future.finditer(active):
        records.append((match.start(), "ref", match.group(2)))
    return sorted(records)


def index_signature(argument: str) -> tuple[str, ...]:
    return tuple(char for char in argument if char in "@!|")


def math_key_sha(surface: dict) -> str:
    key = ch03_math.math_key(surface["normalized"])
    return sha256(key.encode("utf-8"))


def blank_spans(text: str, spans: list[tuple[int, int]]) -> str:
    chars = list(text)
    for start, end in spans:
        for offset in range(start, min(end, len(chars))):
            if chars[offset] not in "\r\n":
                chars[offset] = " "
    return "".join(chars)


def visible_residue(text: str, math: list[dict]) -> list[dict]:
    spans = [(item["start"], item["end"]) for item in math]
    for name in ("label", "ref", "eqref", "cite", "futurexref"):
        spans.extend((item["start"], item["end"]) for item in macro(text, name))
    visible = blank_spans(shared.active_same_length(text), spans)
    visible = re.sub(r"\\(?:begin|end)\{[^{}]+\}", " ", visible)
    visible = re.sub(r"\\[A-Za-z@]+\*?", " ", visible)
    findings: list[dict] = []
    for line_number, line in enumerate(visible.splitlines(), 1):
        words = sorted({match.group(0) for match in RESIDUE_RE.finditer(line)})
        if words:
            findings.append({"line": line_number, "words": words, "text": line.strip()})
    return findings


def main() -> int:
    errors: list[str] = []
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    source = source_bytes.decode("ascii")
    target = target_bytes.decode("utf-8")

    if len(source_bytes) != SOURCE_BYTES:
        errors.append(f"source bytes {len(source_bytes)} != {SOURCE_BYTES}")
    if line_count(source_bytes) != SOURCE_LINES:
        errors.append(f"source lines {line_count(source_bytes)} != {SOURCE_LINES}")
    if sha256(source_bytes) != SOURCE_SHA256:
        errors.append("source SHA-256 mismatch")

    if TARGET_BYTES is not None and len(target_bytes) != TARGET_BYTES:
        errors.append(f"target bytes {len(target_bytes)} != {TARGET_BYTES}")
    if TARGET_LINES is not None and line_count(target_bytes) != TARGET_LINES:
        errors.append(f"target lines {line_count(target_bytes)} != {TARGET_LINES}")
    if TARGET_SHA256 is not None and sha256(target_bytes) != TARGET_SHA256:
        errors.append("target SHA-256 mismatch")

    chapter_title, section_titles = chapter_and_sections(target)
    if chapter_title != EXPECTED_CHAPTER_TITLE:
        errors.append(f"chapter title mismatch: {chapter_title!r}")
    if section_titles != EXPECTED_SECTION_TITLES:
        errors.append(f"section title mismatch: {section_titles!r}")

    source_env = env_sequence(source)
    target_env = env_sequence(target)
    if source_env != target_env:
        errors.append("ordered begin/end environment topology differs")
    source_pairs = len(source_env) // 2
    target_pairs = len(target_env) // 2
    if source_pairs != EXPECTED_COUNTS["environment_pairs"]:
        errors.append(f"source environment pairs {source_pairs}")
    if target_pairs != EXPECTED_COUNTS["environment_pairs"]:
        errors.append(f"target environment pairs {target_pairs}")

    for name, expected in (
        ("label", EXPECTED_COUNTS["labels"]),
        ("cite", EXPECTED_COUNTS["citations"]),
    ):
        source_args = command_arguments(source, name)
        target_args = command_arguments(target, name)
        if source_args != target_args:
            errors.append(f"ordered {name} arguments differ")
        if len(source_args) != expected or len(target_args) != expected:
            errors.append(f"{name} count source/target {len(source_args)}/{len(target_args)}")

    source_refs = reference_sequence(source)
    target_refs = reference_sequence(target)
    source_ref_values = [(kind, value) for _, kind, value in source_refs]
    target_ref_values = [(kind, value) for _, kind, value in target_refs]
    if source_ref_values != target_ref_values:
        errors.append("ordered ref/eqref/futurexref targets differ")
    ref_count = sum(kind == "ref" for _, kind, _ in source_refs)
    eqref_count = sum(kind == "eqref" for _, kind, _ in source_refs)
    if ref_count != EXPECTED_COUNTS["references"]:
        errors.append(f"source ref count {ref_count}")
    if eqref_count != EXPECTED_COUNTS["equation_references"]:
        errors.append(f"source eqref count {eqref_count}")

    source_index = command_arguments(source, "index")
    target_index = command_arguments(target, "index")
    if len(source_index) != EXPECTED_COUNTS["indexes"] or len(target_index) != EXPECTED_COUNTS["indexes"]:
        errors.append(f"index count source/target {len(source_index)}/{len(target_index)}")
    if [index_signature(item) for item in source_index] != [index_signature(item) for item in target_index]:
        errors.append("ordered MakeIndex operator signatures differ")

    source_df = command_arguments(source, "df")
    target_df = command_arguments(target, "df")
    if len(source_df) != EXPECTED_COUNTS["defined_terms"] or len(target_df) != EXPECTED_COUNTS["defined_terms"]:
        errors.append(f"defined-term count source/target {len(source_df)}/{len(target_df)}")

    source_exercises = sum(1 for kind, env in source_env if kind == "begin" and env == "exer")
    target_exercises = sum(1 for kind, env in target_env if kind == "begin" and env == "exer")
    if source_exercises != EXPECTED_COUNTS["exercises"] or target_exercises != EXPECTED_COUNTS["exercises"]:
        errors.append(f"exercise count source/target {source_exercises}/{target_exercises}")

    hint_pattern = re.compile(r"\\begin\{proof\}\[\\emph\{(?:Hint for proof|Petunjuk pembuktian)\}\]")
    source_hints = len(hint_pattern.findall(source))
    target_hints = len(hint_pattern.findall(target))
    if source_hints != EXPECTED_COUNTS["proof_hints"] or target_hints != EXPECTED_COUNTS["proof_hints"]:
        errors.append(f"proof-hint count source/target {source_hints}/{target_hints}")

    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if len(source_math) != EXPECTED_COUNTS["math_surfaces"] or len(target_math) != EXPECTED_COUNTS["math_surfaces"]:
        errors.append(f"math count source/target {len(source_math)}/{len(target_math)}")
    source_delimiters = [item["delimiter"] for item in source_math]
    target_delimiters = [item["delimiter"] for item in target_math]
    if source_delimiters != target_delimiters:
        errors.append("ordered math delimiter topology differs")

    mismatches: list[tuple] = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_math, target_math), 1):
        source_key = math_key_sha(source_item)
        target_key = math_key_sha(target_item)
        if source_key != target_key:
            mismatches.append(
                (
                    ordinal,
                    ordinal,
                    source_item["line_start"],
                    target_item["line_start"],
                    source_item["delimiter"],
                    source_key,
                    target_key,
                )
            )
    expected_mismatch_core = [item[:7] for item in EXPECTED_MATH_MISMATCHES]
    if mismatches != expected_mismatch_core:
        errors.append(f"math-key mismatch lock differs: {mismatches!r}")

    residue = visible_residue(target, target_math)
    if residue:
        errors.append(f"visible English residue: {residue!r}")
    for forbidden in ("C:\\Users", "codex://", "Github Tokens", "Zenodo token"):
        if forbidden.lower() in target.lower():
            errors.append(f"private residue present: {forbidden}")

    if target.count("\\endinput") != 1 or not target.rstrip().endswith("\\endinput"):
        errors.append("target must end with exactly one terminal \\endinput")

    result = {
        "result": "pass" if not errors else "fail",
        "source": {
            "bytes": len(source_bytes),
            "lines": line_count(source_bytes),
            "sha256": sha256(source_bytes),
        },
        "target": {
            "bytes": len(target_bytes),
            "lines": line_count(target_bytes),
            "sha256": sha256(target_bytes),
        },
        "counts": {
            "environment_pairs": target_pairs,
            "labels": len(command_arguments(target, "label")),
            "references": sum(kind == "ref" for _, kind, _ in target_refs),
            "equation_references": sum(kind == "eqref" for _, kind, _ in target_refs),
            "citations": len(command_arguments(target, "cite")),
            "indexes": len(target_index),
            "defined_terms": len(target_df),
            "exercises": target_exercises,
            "proof_hints": target_hints,
            "math_surfaces": len(target_math),
            "math_key_mismatches": len(mismatches),
            "visible_english_residue": len(residue),
        },
        "math_mismatches": mismatches,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
