#!/usr/bin/env python3
"""Generate and self-check the line-bounded Chapter 15 correction ledger."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "fredholm_theory.tex"
TARGET = ROOT / "source" / "id-ID" / "fredholm_theory-id.tex"
OUTPUT = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH15.json"
SOURCE_BYTES = 16_977
SOURCE_RECORDS = 444
SOURCE_SHA = "0ef2e5be3c716a099e8609a84528d77ad6387ec531c52f9890d4e34175c57d91"
TARGET_BYTES = 17_672
TARGET_RECORDS = 444
TARGET_SHA = "174b1ad2557f7dfa10e8171bd7482d907f858389b509f4d55de9cc785e2b43ba"


RECORDS = (
    {
        "id": "FAOA-2015-CH15-CORR-001",
        "source_lines": (10, 32),
        "target_lines": (10, 32),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": (
            "quantify the scalar in Fredholm Alternative I as fixed and nonzero; "
            "lambda=0 makes the stated finite-dimensional alternative false"
        ),
        "source_required": [r"\begin{prop}[Fredholm Alternative I]\label{004011} Let $k$"],
        "target_forbidden": [r"\begin{prop}[Alternatif Fredholm I]\label{004011} Misalkan $k$"],
        "target_required": [
            r"\begin{prop}[Alternatif Fredholm I]\label{004011} Tetapkan $\lambda \in \C\setminus\{0\}$"
        ],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH15-CORR-002",
        "source_lines": (43, 66),
        "target_lines": (43, 66),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": (
            "restrict lambda to the nonzero complex scalars in Fredholm Alternative II; "
            "the assertion fails for lambda=0"
        ),
        "source_required": [r"space operator, $\lambda \in \C$, and $T = \lambda I - K$"],
        "target_forbidden": [r"Hilbert, $\lambda \in \C$, dan $T = \lambda I - K$"],
        "target_required": [r"Hilbert, $\lambda \in \C\setminus\{0\}$, dan $T = \lambda I - K$"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH15-CORR-003",
        "source_lines": (72, 81),
        "target_lines": (72, 81),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": (
            "restrict lambda to the nonzero complex scalars in Fredholm Alternative IIIa; "
            "the injective-surjective equivalence fails for lambda=0"
        ),
        "source_required": [r"$K$ is a compact Hilbert space operator and $\lambda \in \C$, then"],
        "target_forbidden": [r"ruang Hilbert dan $\lambda \in \C$, maka"],
        "target_required": [r"ruang Hilbert dan $\lambda \in \C\setminus\{0\}$, maka"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH15-CORR-004",
        "source_lines": (101, 106),
        "target_lines": (101, 106),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": (
            "remove the commuting condition SK=KS from the Riesz--Schauder definition so "
            "that it agrees with the chapter's proved invertible-plus-compact characterization"
        ),
        "source_required": [r"invertible, $K$ is compact, and $SK = KS$."],
        "target_forbidden": [r"$SK = KS$"],
        "target_required": [r"invertibel dan $K$ kompak."],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH15-CORR-005",
        "source_lines": (123, 125),
        "target_lines": (123, 125),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": "name the ambient Banach space B so that the quotient (B/M)^* is defined",
        "source_required": [r"If $M$ is a closed subspace of a Banach space, then $M^\perp \cong (B/M)^*$"],
        "target_forbidden": [r"subruang tertutup dari suatu ruang Banach, maka $M^\perp"],
        "target_required": [r"subruang tertutup dari ruang Banach $B$, maka $M^\perp \cong (B/M)^*$"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH15-CORR-006",
        "source_lines": (150, 157),
        "target_lines": (150, 157),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": (
            "correct the false claim that a sum of subspaces need not be a subspace: "
            "the example instead shows that a sum of closed subspaces need not be closed"
        ),
        "source_required": [
            "the sum of two subspaces of a Hilbert space need not be a subspace",
            "but $M + N$ is\nnot.",
        ],
        "target_forbidden": ["jumlah dua subruang dari suatu ruang Hilbert tidak harus menjadi subruang"],
        "target_required": [
            "jumlah dua subruang tertutup dari suatu ruang Hilbert tidak harus tertutup",
            r"\index{subruang!jumlah subruang tertutup tidak harus tertutup}%",
            "dan $N$ keduanya merupakan subruang tertutup",
            "$M + N$\ntidak tertutup.",
        ],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH15-CORR-007",
        "source_lines": (247, 252),
        "target_lines": (247, 252),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "remove the extra closing parenthesis from the Fredholm-index index hook",
        "source_required": [r"\index{Fredholm!index (\seeonly{index}))}%"],
        "target_forbidden": [r"\seeonly{indeks}))"],
        "target_required": [r"\index{Fredholm!indeks (\seeonly{indeks})}%"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH15-CORR-008",
        "source_lines": (268, 270),
        "target_lines": (268, 270),
        "classification": "FORMAL_SCOPE_CLARIFICATION",
        "decision": (
            "state the standard cross-space Fredholm convention before applying it to maps V to W; "
            "the earlier Calkin-algebra definition covers endomorphisms only"
        ),
        "source_required": [
            r"\begin{exam} Every linear map $T\colon V \sto W$ between finite dimensional vector spaces is"
        ],
        "target_forbidden": [r"\begin{exam} Setiap pemetaan linear $T\colon V \sto W$"],
        "target_required": [
            "Untuk pemetaan antar-ruang, kita memakai konvensi standar: pemetaan linear disebut Fredholm jika",
            "jangkauannya tertutup serta kernel dan kokernelnya berdimensi hingga. Dengan konvensi ini",
            r"$\ind T = \dim V - \dim W$. \end{exam}",
        ],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH15-CORR-009",
        "source_lines": (300, 303),
        "target_lines": (300, 303),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": (
            "add the infinite-dimensional hypothesis required for the Fredholm index to be "
            "surjective onto the integers"
        ),
        "source_required": [r"\begin{prop} Let $H$ be a Hilbert space. Then the set $\ofml F(H)$"],
        "target_forbidden": [r"\begin{prop} Misalkan $H$ ruang Hilbert. Maka himpunan $\ofml F(H)$"],
        "target_required": [
            r"\begin{prop} Misalkan $H$ ruang Hilbert berdimensi tak hingga. Maka himpunan $\ofml F(H)$"
        ],
        "affects_math": False,
    },
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(lines: list[str], start: int, end: int) -> str:
    selected = [line.rstrip() for line in lines[start - 1 : end] if line.strip()]
    text = unicodedata.normalize("NFC", "\n".join(selected))
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    if len(source_bytes) != SOURCE_BYTES or sha(source_bytes) != SOURCE_SHA:
        raise SystemExit("source identity mismatch")
    if len(target_bytes) != TARGET_BYTES or sha(target_bytes) != TARGET_SHA:
        raise SystemExit("target identity mismatch")
    if source_bytes.count(b"\r\n") != SOURCE_RECORDS or source_bytes.count(b"\n") != SOURCE_RECORDS:
        raise SystemExit("source CRLF topology mismatch")
    if b"\r" in target_bytes or target_bytes.count(b"\n") != TARGET_RECORDS:
        raise SystemExit("target LF topology mismatch")

    source_text = source_bytes.decode("ascii").replace("\r\n", "\n")
    target_text = target_bytes.decode("utf-8")
    source_lines = source_text.splitlines()
    target_lines = target_text.splitlines()
    if len(source_lines) != SOURCE_RECORDS or len(target_lines) != TARGET_RECORDS:
        raise SystemExit("logical-record topology mismatch")

    records = []
    for spec in RECORDS:
        s0, s1 = spec["source_lines"]
        t0, t1 = spec["target_lines"]
        for value in spec["source_required"]:
            if value not in source_text:
                raise SystemExit(f"source anchor missing: {spec['id']} {value!r}")
        for value in spec["target_forbidden"]:
            if value in target_text:
                raise SystemExit(f"forbidden target anchor remains: {spec['id']} {value!r}")
        for value in spec["target_required"]:
            if value not in target_text:
                raise SystemExit(f"required target anchor missing: {spec['id']} {value!r}")
        source_snippet = normalize(source_lines, s0, s1)
        target_snippet = normalize(target_lines, t0, t1)
        records.append(
            {
                "id": spec["id"],
                "source_lines": {"start": s0, "end": s1},
                "target_lines": {"start": t0, "end": t1},
                "classification": spec["classification"],
                "decision": spec["decision"],
                "source_normalized_snippet": source_snippet,
                "target_normalized_snippet": target_snippet,
                "source_normalized_snippet_sha256": sha(source_snippet.encode("utf-8")),
                "target_normalized_snippet_sha256": sha(target_snippet.encode("utf-8")),
                "source_required_anchors": spec["source_required"],
                "forbidden_target_anchors": spec["target_forbidden"],
                "required_target_anchors": spec["target_required"],
                "affects_math": spec["affects_math"],
            }
        )

    class_counts: dict[str, int] = {}
    for record in records:
        classification = record["classification"]
        class_counts[classification] = class_counts.get(classification, 0) + 1
    payload = {
        "schema_version": "o008.source-corrections.v1",
        "unit_id": "FAOA-2015-CH15",
        "chapter": 15,
        "status": "adjudicated_and_applied",
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "bytes": len(source_bytes),
            "logical_records": SOURCE_RECORDS,
            "line_endings": "CRLF",
            "sha256": SOURCE_SHA,
        },
        "target": {
            "path": TARGET.relative_to(ROOT).as_posix(),
            "bytes": len(target_bytes),
            "logical_records": TARGET_RECORDS,
            "line_endings": "LF",
            "sha256": TARGET_SHA,
        },
        "normalization": {
            "id": "explicit-range-nfc-whitespace-v1",
            "source_selection": "inclusive physical source-line range",
            "target_mapping": "inclusive physical target-line range",
            "steps": [
                "discard blank records and strip trailing whitespace",
                "join selected records with LF",
                "normalize Unicode NFC",
                "collapse Unicode whitespace runs to ASCII spaces",
                "trim leading and trailing ASCII space",
                "hash UTF-8 bytes with SHA-256",
            ],
        },
        "record_count": len(records),
        "class_counts": class_counts,
        "independent_review": {
            "source_inventory": "qa/CH15_SOURCE_INVENTORY.md",
            "pretranslation_math_review": "qa/CH15_PRETRANSLATION_MATH_REVIEW.md",
            "terminology_plan": "provenance/CH15_TERMINOLOGY_PLAN.md",
            "bilingual_math_review": "qa/CH15_BILINGUAL_MATH_REVIEW.md",
            "upstream_contact": "none during production",
        },
        "records": records,
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_bytes(rendered.encode("utf-8"))
    replay = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if replay != payload:
        raise SystemExit("ledger round-trip mismatch")
    print(f"path={OUTPUT.relative_to(ROOT).as_posix()}")
    print(f"records={len(records)}")
    print(f"bytes={OUTPUT.stat().st_size}")
    print(f"sha256={sha(OUTPUT.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
