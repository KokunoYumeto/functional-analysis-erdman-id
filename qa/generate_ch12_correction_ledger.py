#!/usr/bin/env python3
"""Generate the exact, line-bound Chapter 12 correction/localization ledger."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "no_identity.tex"
TARGET = ROOT / "source" / "id-ID" / "no_identity-id.tex"
OUTPUT = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH12.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized(lines: list[str], start: int, end: int) -> str:
    selected = [line.rstrip() for line in lines[start - 1 : end] if line.strip()]
    text = unicodedata.normalize("NFC", "\n".join(selected))
    return re.sub(r"\s+", " ", text).strip()


def identity(path: Path, relative: str, line_endings: str) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": relative,
        "bytes": len(data),
        "logical_records": data.count(b"\n"),
        "line_endings": line_endings,
        "sha256": digest(data),
    }


# Each entry binds a source defect or a mathematically visible localization to
# the exact source and target records. The latter category is explicit so the
# formula audit never mistakes translated text inside math for a silent change.
SPECS: list[dict[str, object]] = [
    {
        "source": (89, 90), "target": (90, 91),
        "classification": "MECHANICAL_INDEX_SOURCE_REPAIR",
        "decision": "index the defined object as a right, not left, identity relative to an ideal",
        "forbidden": r"\index{identity!left!with respect to an ideal}%",
        "required": r"\index{identitas!kanan!terhadap suatu ideal}%",
    },
    {
        "source": (175, 179), "target": (178, 183),
        "classification": "MATHEMATICAL_SOURCE_REPAIR", "affects_math": True,
        "decision": "restore the omitted domain and mapping arrow in the nonunital Gelfand-transform signature",
        "forbidden": r"\Gamma = \Gamma_A\colon \fml C_0(\Delta A)\colon a \mapsto",
        "required": r"\Gamma = \Gamma_A\colon A \sto \fml C_0(\Delta A)\colon a \mapsto",
    },
    {
        "source": (226, 226), "target": (230, 230),
        "classification": "CROSS_REFERENCE_SOURCE_REPAIR",
        "decision": "point the first local short-exact-sequence reference to the globally unique Chapter 12 label",
        "forbidden": r"\eqref{001500202i}", "required": r"\eqref{001500202i2}",
    },
    {
        "source": (240, 240), "target": (243, 243),
        "classification": "CROSS_REFERENCE_SOURCE_REPAIR",
        "decision": "point the second local short-exact-sequence reference to the globally unique Chapter 12 label",
        "forbidden": r"\eqref{001500202i}", "required": r"\eqref{001500202i2}",
    },
    {
        "source": (247, 247), "target": (249, 249),
        "classification": "CROSS_REFERENCE_SOURCE_REPAIR",
        "decision": "point the third local reference to the Chapter 12 label and use equation-reference typography",
        "forbidden": r"\ref{001500202i}", "required": r"\eqref{001500202i2}",
    },
    {
        "source": (323, 324), "target": (327, 328),
        "classification": "MATHEMATICAL_TEXT_LOCALIZATION", "affects_math": True,
        "decision": "translate the conjunction embedded in the displayed map pair without changing either map",
        "forbidden": r"\text{and}", "required": r"\text{dan}",
    },
    {
        "source": (431, 431), "target": (437, 437),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "supply the missing preposition in the proof-hint opening",
        "forbidden": "The proof this result is a little complicated.",
        "required": "Pembuktian hasil ini agak rumit.",
    },
    {
        "source": (435, 436), "target": (441, 443),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "supply the missing article before C-star algebra in the source sentence",
        "forbidden": r"the unitization of $C^*$-algebra $A$",
        "required": r"unitalisasi dari suatu aljabar-$C^*$ $A$",
    },
    {
        "source": (448, 448), "target": (455, 456),
        "classification": "MECHANICAL_TEX_SOURCE_REPAIR", "affects_math": True,
        "decision": "typeset the star as a superscript in C-star norm",
        "forbidden": r"$C*$-norm", "required": r"norma-$C^*$",
    },
    {
        "source": (471, 473), "target": (480, 482),
        "classification": "MATHEMATICAL_TEXT_LOCALIZATION", "affects_math": True,
        "decision": "translate the conjunction inside the A-sharp set-builder formula",
        "forbidden": r"\text{ and } \lambda", "required": r"\text{ dan } \lambda",
    },
    {
        "source": (483, 483), "target": (491, 493),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "close the enumerated instruction with a period",
        "forbidden": r"with the norm pulled back by $\phi$ from $A^\sharp$",
        "required": r"norma yang ditarik balik oleh $\phi$ dari $A^\sharp$.",
    },
    {
        "source": (505, 505), "target": (516, 516),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": "use the proposition's precise not-isomorphic conclusion instead of an undefined equivalence",
        "forbidden": r"\emph{not} equivalent to $A \oplus \C$",
        "required": r"\emph{tidak} isomorfik dengan $A \oplus \C$",
    },
    {
        "source": (536, 537), "target": (547, 549),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "repair the source article in given an algebra",
        "forbidden": "given a algebra $A$ with involution",
        "required": "diberikan suatu aljabar $A$ dengan involusi",
    },
    {
        "source": (554, 559), "target": (567, 572),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": "remove unitally from the general nonunital Gelfand--Naimark II description",
        "forbidden": r"isometrically unitally $*\,$-isomorphic",
        "required": r"isomorfik-$*\,$ secara isometrik",
    },
    {
        "source": (561, 565), "target": (574, 579),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": "remove unital from the theorem's isomorphism for a general commutative C-star algebra",
        "forbidden": r"isometric unital $*\,$-isomorphism",
        "required": r"isomorfisme-$*\,$ isometrik dari $A$ pada $\fml C_0(\Delta A)$",
    },
    {
        "source": (591, 596), "target": (605, 610),
        "classification": "MATHEMATICAL_TEXT_LOCALIZATION", "affects_math": True,
        "decision": "translate the two conditional labels inside the piecewise display",
        "forbidden": r"\hbox{if $x", "required": r"\hbox{jika $x",
    },
    {
        "source": (611, 611), "target": (625, 626),
        "classification": "PARTIAL_READER_NAVIGATION_ADAPTATION",
        "decision": "show the official future printed locator until Chapter 14 supplies the live label",
        "forbidden": r"\ref{0038614}", "required": r"\futurexref{14.3.1}{0038614}",
    },
    {
        "source": (659, 663), "target": (674, 678),
        "classification": "MATHEMATICAL_TEXT_LOCALIZATION", "affects_math": True,
        "decision": "repeat the variable b explicitly where Indonesian grammar requires the subject",
        "forbidden": "If $b$ is both a",
        "required": "maka $b$ adalah",
    },
    {
        "source": (670, 670), "target": (685, 685),
        "classification": "MECHANICAL_TEX_SOURCE_REPAIR",
        "decision": "insert the missing space after the proposition opener",
        "forbidden": r"\begin{prop}Let $A$ be a unital algebra",
        "required": r"\begin{prop} Misalkan $A$ aljabar beridentitas",
    },
    {
        "source": (689, 689), "target": (704, 704),
        "classification": "MECHANICAL_TEX_SOURCE_REPAIR",
        "decision": "insert the missing space after the proposition opener",
        "forbidden": r"\begin{prop}Let $A$ be a Banach algebra",
        "required": r"\begin{prop} Misalkan $A$ aljabar Banach dan $a \in A$. Jika $\norm{a} < 1$",
    },
    {
        "source": (709, 710), "target": (723, 726),
        "classification": "MECHANICAL_INDEX_SOURCE_REPAIR",
        "decision": "close the unmatched explanatory parenthesis in the Q_A index entry",
        "forbidden": r"\index{q@$Q_A$ (quasi-invertible elements}%",
        "required": r"\index{q@$Q_A$ (elemen kuasi-invertibel)}%",
    },
    {
        "source": (728, 733), "target": (743, 748),
        "classification": "MATHEMATICAL_TEXT_LOCALIZATION", "affects_math": True,
        "decision": "repair the source article and translate the conjunction inside the q-spectrum display",
        "forbidden": "If $A$ is a algebra", "required": r"Jika $A$ aljabar dan $a \in A$",
    },
    {
        "source": (858, 860), "target": (873, 875),
        "classification": "MATHEMATICAL_TEXT_LOCALIZATION", "affects_math": True,
        "decision": "render nth root idiomatically as akar pangkat n while preserving the quantified symbol",
        "forbidden": r"$n^{\text{th}}$ root", "required": "akar pangkat\n$n$ positif",
    },
    {
        "source": (887, 893), "target": (902, 908),
        "classification": "MATHEMATICAL_SOURCE_REPAIR", "affects_math": True,
        "decision": "name the ambient C-star algebra A before item (iii) quantifies an element of A",
        "forbidden": "If $c$ is an element of a $C^*$-algebra, then the following",
        "required": "Jika $c$ adalah elemen dari suatu aljabar-$C^*$ $A$",
    },
    {
        "source": (907, 907), "target": (921, 922),
        "classification": "MECHANICAL_TEX_SOURCE_REPAIR",
        "decision": "insert protected spacing before the Jordan-decomposition reference",
        "forbidden": r"theorem}\ref{001807}", "required": r"Jordan}~\ref{001807}",
    },
    {
        "source": (945, 947), "target": (960, 962),
        "classification": "MATHEMATICAL_SOURCE_REPAIR", "affects_math": True,
        "decision": "state the positivity inequality in the unitization because a general C-star algebra has no 1_A",
        "forbidden": r"\norm a \vc 1_A \pm a \ge \vc 0",
        "required": r"\norm a\,\vc 1_{\wt A} \pm a \ge \vc 0$ dalam~$\wt A$",
    },
    {
        "source": (961, 962), "target": (976, 977),
        "classification": "MECHANICAL_TEX_SOURCE_REPAIR",
        "decision": "insert the missing space after the proposition opener",
        "forbidden": r"\begin{prop}Let $A$ be a unital $C^*$-algebra",
        "required": r"\begin{prop} Misalkan $A$ aljabar-$C^*$ beridentitas",
    },
    {
        "source": (1033, 1035), "target": (1048, 1050),
        "classification": "MECHANICAL_INDEX_SOURCE_REPAIR",
        "decision": "correct the approximate spelling in the sequential approximate identity index",
        "forbidden": "sequential!approxiamte identity",
        "required": "sekuensial!identitas aproksimatif",
    },
    {
        "source": (1062, 1069), "target": (1077, 1084),
        "classification": "MATHEMATICAL_TEXT_LOCALIZATION", "affects_math": True,
        "decision": "retain the named algebra A explicitly in idiomatic Indonesian proposition and corollary prose",
        "forbidden": "Every $C^*$-algebra $A$ has an approximate identity.",
        "required": "Setiap aljabar-$C^*$ $A$ memiliki identitas aproksimatif.",
    },
]


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    source_lines = source_bytes.decode("ascii").splitlines()
    target_lines = target_bytes.decode("utf-8").splitlines()
    records: list[dict[str, object]] = []
    for ordinal, spec in enumerate(SPECS, 1):
        s0, s1 = spec["source"]
        t0, t1 = spec["target"]
        source_snippet = normalized(source_lines, s0, s1)
        target_snippet = normalized(target_lines, t0, t1)
        record: dict[str, object] = {
            "id": f"FAOA-2015-CH12-CORR-{ordinal:03d}",
            "source_lines": {"start": s0, "end": s1},
            "target_lines": {"start": t0, "end": t1},
            "classification": spec["classification"],
            "decision": spec["decision"],
            "source_normalized_snippet": source_snippet,
            "target_normalized_snippet": target_snippet,
            "source_normalized_snippet_sha256": digest(source_snippet.encode("utf-8")),
            "target_normalized_snippet_sha256": digest(target_snippet.encode("utf-8")),
            "forbidden_source_anchor": spec["forbidden"],
            "required_target_anchor": spec["required"],
        }
        if spec.get("affects_math") is True:
            record["affects_math"] = True
        records.append(record)

    class_counts = dict(sorted(Counter(str(r["classification"]) for r in records).items()))
    ledger = {
        "schema_version": "o008.source-corrections.v1",
        "unit_id": "FAOA-2015-CH12",
        "chapter": 12,
        "status": "adjudicated_and_applied",
        "source": identity(SOURCE, "source/upstream/no_identity.tex", "CRLF"),
        "target": identity(TARGET, "source/id-ID/no_identity-id.tex", "LF"),
        "normalization": {
            "id": "explicit-range-nfc-whitespace-v1",
            "source_selection": "inclusive physical source-line range",
            "target_mapping": "inclusive physical target-line range after translation and bounded repair",
            "steps": [
                "discard blank records and strip trailing whitespace",
                "join selected records with LF",
                "normalize Unicode NFC",
                "collapse Unicode whitespace runs, including indentation and line boundaries, to ASCII spaces",
                "trim leading and trailing ASCII space after collapse",
                "hash UTF-8 bytes with SHA-256",
            ],
        },
        "record_count": len(records),
        "class_counts": class_counts,
        "independent_review": {
            "pretranslation_math_review": "qa/CH12_PRETRANSLATION_MATH_REVIEW.md",
            "formula_policy": "source repairs and translated text inside math are separately classified",
            "upstream_contact": "none during production",
        },
        "records": records,
    }
    OUTPUT.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
