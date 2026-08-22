#!/usr/bin/env python3
"""Locked structural, mathematical, terminology, rights, and residue audit for CH10."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qa"))
sys.path.insert(0, str(ROOT / "backend"))
import check_ch05_translation as common  # noqa: E402
import check_ch09_translation as ch09  # noqa: E402
import ch03_math  # noqa: E402


SOURCE = ROOT / "source" / "upstream" / "distributions.tex"
TARGET = ROOT / "source" / "id-ID" / "distributions-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch10.tex"
CORRECTIONS = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH10.json"
TERM_DECISION = ROOT / "provenance" / "CH10_TERMINOLOGY_DECISIONS.md"
TERM_WITNESS = ROOT / "qa" / "terminology_evidence" / "itb-distribusi-tempered-2018-bab2.pdf"
MODEL_PROVENANCE = ROOT / "provenance" / "TRANSLATION_MODEL_PROVENANCE.md"
README = ROOT / "README.md"
REPORT = ROOT / "qa" / "ch10-translation-report.json"

IDENTITIES = {
    "source": (42_703, 894, "31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8"),
    "target": (42_627, 876, "6456f9def822da572e117f3ec368931f0bfb441840aa0785be1df6080bbb6840"),
    "master": (9_866, 336, "5de05f7a154bea99d11924fc21dbbf7495c8642d5a3c58e48e0fdd053dd400b4"),
    "corrections": (11_858, 301, "c5010ce91ae98d3c9b3637fe6a553f4df7d1ba524faa75b1f4fb42b0b036c948"),
    "term_decision": (1_756, 36, "03005aa60200768a05c700e7d9d8cfa969034204e37ecffbd8b67126c5c66329"),
    "term_witness": (283_518, None, "830a241c8ace73290a4c613cc6478bb17698d835b781b1fec332fa09838ddf02"),
}
EXPECTED_CHAPTER = "DISTRIBUSI"
EXPECTED_SECTIONS = [
    "Limit Induktif",
    "Ruang-$LF$",
    "Distribusi",
    "Konvolusi",
    "Solusi Distribusional untuk Persamaan Diferensial Biasa",
    "Transformasi Fourier",
]
EXPECTED_BEGIN_COUNTS = {
    "array": 3,
    "cases": 1,
    "cau": 1,
    "defn": 19,
    "enumerate": 4,
    "equation": 5,
    "exam": 25,
    "exer": 11,
    "notn": 4,
    "proof": 18,
    "prop": 31,
    "rem": 1,
    "thm": 1,
}
EXPECTED_MASTER_INCLUDES = (
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
)
EXPECTED_DIGESTS = {
    "source_env": "817980afcdd19bb25d0aa0385492d82459fb2ede5f888637540ae44e6c88422c",
    "target_env": "15af4e00110538b37355330d91179479fa1f1554b8a004d117793039544501f8",
    "source_shapes": "d6f7c0a239a8376f65e7bac83d9d0cfb17e7ee128659aabd2d95b4d9d7064d0b",
    "target_shapes": "39429ff1f604f99fb2f64c7cfb4787511f6cc6e918c83608044648565b83685d",
    "labels": "2a369eab5a3a169348344d7d9f222ea86ea5f23c0e844d234d7260ebd2725b84",
    "references": "cb8c2af05153f043e57b25e16bc462fec1fc778331926d64edd325a872477bae",
    "citations": "5c57f39e712f21a1c83d07fb1ae69728ee5dd970786a5936885af95013c1ad83",
    "source_indexes": "0d98fb5d935ac729e0ee1d69564037f26c2796c9340b9e73ecf1dcb960c10bb0",
    "target_indexes": "72df53023037c3f4deac768d99be506f6bd72f9bc9c6a99121f6e5c78715b854",
    "index_shapes": "e2f4f780d13dcb42328334d3d496fa777dd5466581064fd4e0da61c97db36b3d",
    "source_df": "4c6e7b7c4f05d692721ea22f3c580568817fb45837720255f5579915bed6e2bc",
    "target_df": "c2b77e892f57d9ae45a241200581b10cb0d2463f5cc4d60b70c3b47553f43496",
    "source_math": "c21e165b00044ae77c380422735550d2aa27fea0cd7098d6a261948009c90d10",
    "target_math": "e3b67aea3045fa2d0cea3b26951f0d734efdf4dbbd4e478b4c473cc142562f89",
    "math_edits": "eb32b119fe600c65a5b79653b1a5b1747c275a0c1fede7faf7586c5c27e456fd",
    "proof_roles": "8125f83e60316697b811ccf48119749cf72a4e803de879ec33b22c9147488f91",
    "learning_sequence": "8e0194da1b7f02645e9779274ad11698ef980876ded75c7934f0f6008852a333",
}
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"
PRIVATE_RESIDUE = ("c:\\users\\", "documents\\interlanguage", "obsidian notes", "\\appdata\\")
MOJIBAKE = ("Ã", "Â", "â€", "ï»¿", "�")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sequence_sha(value: object) -> str:
    return ch09.sequence_sha256(value)


def file_identity(path: Path, key: str, errors: list[str]) -> bytes:
    data = path.read_bytes()
    expected_bytes, expected_lf, expected_sha = IDENTITIES[key]
    if len(data) != expected_bytes or sha(data) != expected_sha:
        errors.append(f"{key} byte identity differs")
    if expected_lf is not None and data.count(b"\n") != expected_lf:
        errors.append(f"{key} LF count differs")
    return data


def main() -> int:
    errors: list[str] = []
    source_bytes = file_identity(SOURCE, "source", errors)
    target_bytes = file_identity(TARGET, "target", errors)
    master_bytes = file_identity(MASTER, "master", errors)
    correction_bytes = file_identity(CORRECTIONS, "corrections", errors)
    term_decision_bytes = file_identity(TERM_DECISION, "term_decision", errors)
    file_identity(TERM_WITNESS, "term_witness", errors)

    if source_bytes.count(b"\r\n") != 894 or source_bytes.replace(b"\r\n", b"") .find(b"\r") >= 0:
        errors.append("source CRLF closure differs")
    for name, data in (("target", target_bytes), ("master", master_bytes), ("corrections", correction_bytes), ("term_decision", term_decision_bytes)):
        if b"\r" in data or data.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{name} encoding/line endings differ")

    source = source_bytes.decode("ascii")
    target = target_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")
    chapter, sections = common.chapter_and_sections(target)
    if chapter != EXPECTED_CHAPTER or sections != EXPECTED_SECTIONS:
        errors.append(f"chapter/section titles differ: {chapter!r}, {sections!r}")
    if common.command_arguments(target, "subsection"):
        errors.append("unexpected subsection or lower heading")

    source_env = common.env_sequence(source)
    target_env = common.env_sequence(target)
    if (len(source_env), len(target_env)) != (250, 248):
        errors.append("environment token census differs")
    if sequence_sha(source_env) != EXPECTED_DIGESTS["source_env"] or sequence_sha(target_env) != EXPECTED_DIGESTS["target_env"]:
        errors.append("environment topology digest differs")
    repaired_source_env = list(source_env)
    first_begin = repaired_source_env.index(("begin", "array"))
    first_end = repaired_source_env.index(("end", "array"), first_begin)
    del repaired_source_env[first_end]
    del repaired_source_env[first_begin]
    if repaired_source_env != target_env:
        errors.append("environment delta exceeds classified direct-limit repair")
    errors.extend(ch09.environment_stack_errors(target_env))
    begin_counts = dict(sorted(Counter(name for action, name in target_env if action == "begin").items()))
    if begin_counts != EXPECTED_BEGIN_COUNTS:
        errors.append(f"environment opening census differs: {begin_counts!r}")

    source_shapes = ch09.begin_shape_sequence(source)
    target_shapes = ch09.begin_shape_sequence(target)
    if sequence_sha(source_shapes) != EXPECTED_DIGESTS["source_shapes"] or sequence_sha(target_shapes) != EXPECTED_DIGESTS["target_shapes"]:
        errors.append("begin-control shape digest differs")
    repaired_source_shapes = list(source_shapes)
    repaired_source_shapes.remove(("array", "mandatory"))
    if repaired_source_shapes != target_shapes:
        errors.append("begin-control shape delta exceeds direct-limit repair")

    source_labels = common.command_arguments(source, "label")
    target_labels = common.command_arguments(target, "label")
    source_refs = [(kind, value) for _, kind, value in common.reference_sequence(source)]
    target_refs = [(kind, value) for _, kind, value in common.reference_sequence(target)]
    source_cites = common.command_arguments(source, "cite")
    target_cites = common.command_arguments(target, "cite")
    for name, left, right, expected_count in (
        ("labels", source_labels, target_labels, 18),
        ("references", source_refs, target_refs, 20),
        ("citations", source_cites, target_cites, 29),
    ):
        if left != right or len(right) != expected_count or sequence_sha(right) != EXPECTED_DIGESTS[name]:
            errors.append(f"ordered {name} sequence differs")

    source_indexes = common.command_arguments(source, "index")
    target_indexes = common.command_arguments(target, "index")
    source_index_shapes = [common.index_signature(item) for item in source_indexes]
    target_index_shapes = [common.index_signature(item) for item in target_indexes]
    if len(source_indexes) != 101 or len(target_indexes) != 101:
        errors.append("index count differs")
    if source_index_shapes != target_index_shapes:
        errors.append("MakeIndex operator-shape sequence differs")
    if sequence_sha(source_indexes) != EXPECTED_DIGESTS["source_indexes"] or sequence_sha(target_indexes) != EXPECTED_DIGESTS["target_indexes"]:
        errors.append("index sequence digest differs")
    if sequence_sha(target_index_shapes) != EXPECTED_DIGESTS["index_shapes"]:
        errors.append("index operator-shape digest differs")

    source_df = common.command_arguments(source, "df")
    target_df = common.command_arguments(target, "df")
    if len(source_df) != 35 or len(target_df) != 35:
        errors.append("defined-term count differs")
    if sequence_sha(source_df) != EXPECTED_DIGESTS["source_df"] or sequence_sha(target_df) != EXPECTED_DIGESTS["target_df"]:
        errors.append("defined-term sequence digest differs")
    if target.count(r"\df{distribusi tempered}") != 1 or target.count(r"\df{distribusi temperate}") != 1:
        errors.append("tempered-distribution terminology decision not instantiated exactly")
    if "distribusi temper}" in target:
        errors.append("superseded provisional term remains")

    source_proof_roles = [item["role"] for item in ch09.proof_records(source)]
    target_proof_roles = [item["role"] for item in ch09.proof_records(target)]
    if source_proof_roles != target_proof_roles or Counter(target_proof_roles) != Counter({"hint": 3, "citation": 15}):
        errors.append("proof-role sequence differs")
    source_learning = ch09.exercise_proof_sequence(source)
    target_learning = ch09.exercise_proof_sequence(target)
    if source_learning != target_learning:
        errors.append("exercise/proof topology differs")
    if sequence_sha(target_proof_roles) != EXPECTED_DIGESTS["proof_roles"] or sequence_sha(target_learning) != EXPECTED_DIGESTS["learning_sequence"]:
        errors.append("learning-support digest differs")
    if target.count(r"\begin{exer}") != 11 or target.count(r"\begin{proof}") != 18 or target.count(r"\ns") != 17:
        errors.append("exercise/proof/stub census differs")
    if target.count(r"\emph{Petunjuk.}") != 5:
        errors.append("inline exercise-hint census differs")
    if r"\begin{answer}" in target or r"\begin{solution}" in target:
        errors.append("unprovenanced answer or solution surface present")

    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (651, 648):
        errors.append("mathematical-surface census differs")
    if sequence_sha(ch09.math_records(source_math)) != EXPECTED_DIGESTS["source_math"]:
        errors.append("source math digest differs")
    if sequence_sha(ch09.math_records(target_math)) != EXPECTED_DIGESTS["target_math"]:
        errors.append("target math digest differs")
    math_edits = ch09.math_edit_signature(source_math, target_math)
    if sequence_sha(math_edits) != EXPECTED_DIGESTS["math_edits"]:
        errors.append("unclassified mathematical edit signature")

    residue = common.visible_residue(target, target_math)
    residue = [
        item for item in residue
        if "Topological Vector Spaces, Distributions, and Kernels" not in item["text"]
        and "Functional Analysis" not in item["text"]
    ]
    if residue:
        errors.append(f"visible English residue: {residue!r}")
    for marker in MOJIBAKE:
        if marker in target:
            errors.append(f"mojibake marker present: {marker!r}")
    active_lower = common.shared.active_same_length(target).lower()
    for marker in PRIVATE_RESIDUE:
        if marker in active_lower:
            errors.append(f"private-path residue present: {marker}")
    if target.count(r"\endinput") != 1 or target.rstrip().splitlines()[-1] != r"\endinput":
        errors.append("endinput is not the sole final nonblank record")

    master_includes = tuple(common.command_arguments(master, "include"))
    if master_includes != EXPECTED_MASTER_INCLUDES:
        errors.append(f"master include sequence differs: {master_includes!r}")
    for required in (
        "Unit Pembaca Kumulatif Bab 1--10",
        "batas produksi Bab 1--10",
        "Bab 1 sampai Bab 10",
        "Creative Commons",
        "Attribution--ShareAlike 4.0 International",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University",
        "DIAGXY.TEX",
        "status komponennya tidak cukup jelas tidak digunakan",
    ):
        if required not in master:
            errors.append(f"master rights/scope anchor missing: {required!r}")
    for forbidden in ("TABLE.TEX", "by-sa.eps", "by-sa.pdf", "Wiener_quote.tex"):
        if rf"\input{{{forbidden}}}" in master or rf"\includegraphics{{{forbidden}}}" in master:
            errors.append(f"excluded component is active: {forbidden}")

    correction_data = json.loads(correction_bytes.decode("utf-8"))
    if correction_data.get("record_count") != 16 or len(correction_data.get("records", [])) != 16:
        errors.append("correction ledger record count differs")
    if correction_data.get("source", {}).get("sha256") != IDENTITIES["source"][2] or correction_data.get("target", {}).get("sha256") != IDENTITIES["target"][2]:
        errors.append("correction ledger identity binding differs")
    for record in correction_data.get("records", []):
        if record.get("required_target_anchor") not in target:
            errors.append(f"correction anchor missing: {record.get('id')}")

    term_decision = term_decision_bytes.decode("utf-8")
    if "preferred Indonesian term = `distribusi tempered`" not in term_decision or IDENTITIES["term_witness"][2] not in term_decision:
        errors.append("terminology decision does not bind the inspected witness")
    if MODEL_ID not in README.read_text(encoding="utf-8") or MODEL_ID not in MODEL_PROVENANCE.read_text(encoding="utf-8"):
        errors.append("explicit model provenance is missing")

    report = {
        "schema_version": "o008.ch10-translation-qa.v1",
        "unit_id": "FAOA-2015-CH10",
        "status": "pass" if not errors else "fail",
        "source": {"bytes": len(source_bytes), "lines": 894, "sha256": sha(source_bytes)},
        "target": {"bytes": len(target_bytes), "lines": 876, "sha256": sha(target_bytes)},
        "master": {"bytes": len(master_bytes), "lines": 336, "sha256": sha(master_bytes)},
        "counts": {
            "sections": len(sections),
            "environment_begins": sum(EXPECTED_BEGIN_COUNTS.values()),
            "labels": len(target_labels),
            "references": len(target_refs),
            "citations": len(target_cites),
            "indexes": len(target_indexes),
            "defined_terms": len(target_df),
            "exercises": target.count(r"\begin{exer}"),
            "proof_hints": Counter(target_proof_roles)["hint"],
            "citation_only_proofs": Counter(target_proof_roles)["citation"],
            "math_surfaces": len(target_math),
            "source_corrections": correction_data.get("record_count"),
        },
        "classified_math_edit_sha256": sequence_sha(math_edits),
        "terminology_witness_sha256": IDENTITIES["term_witness"][2],
        "model_id": MODEL_ID,
        "errors": errors,
    }
    REPORT.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
