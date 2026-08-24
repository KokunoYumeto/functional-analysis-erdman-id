#!/usr/bin/env python3
"""Generate and self-check the line-bounded Chapter 16 correction ledger."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "extensions.tex"
TARGET = ROOT / "source" / "id-ID" / "extensions-id.tex"
OUTPUT = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH16.json"
SOURCE_BYTES = 42_614
SOURCE_RECORDS = 1_000
SOURCE_SHA = "e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318"
TARGET_BYTES = 43_804
TARGET_RECORDS = 1_000
TARGET_SHA = "59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3"


RECORDS = (
    {
        "id": "FAOA-2015-CH16-CORR-001",
        "source_lines": (13, 15),
        "classification": "MECHANICAL_TEX_SOURCE_REPAIR",
        "decision": "insert the missing separation after the proposition opening",
        "source_required": [r"\begin{prop}If $T$ is an operator"],
        "target_forbidden": [r"\begin{prop}Jika $T$"],
        "target_required": [r"\begin{prop} Jika $T$"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH16-CORR-002",
        "source_lines": (42, 58),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": (
            "with U:H to K, replace both ill-typed UTU* conjugations by U*TU, "
            "which acts on H like S"
        ),
        "source_required": ["$S - UTU^*$", "$S =\nUTU^*$"],
        "target_forbidden": ["$S - UTU^*$", "$S =\nUTU^*$"],
        "target_required": ["$S - U^*TU$", "$S =\nU^*TU$"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH16-CORR-003",
        "source_lines": (61, 63),
        "classification": "FORMAL_SCOPE_CLARIFICATION",
        "decision": (
            "state the intended separable infinite-dimensional Hilbert-space scope so "
            "equal essential spectrum can be compared by a unitary"
        ),
        "source_required": ["on separable Hilbert spaces are"],
        "target_forbidden": ["ruang-ruang Hilbert terpisahkan\nekuivalen"],
        "target_required": ["ruang-ruang Hilbert terpisahkan berdimensi tak hingga\nekuivalen"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH16-CORR-004",
        "source_lines": (254, 258),
        "classification": "MATHEMATICAL_NOTATION_SOURCE_REPAIR",
        "decision": "restore the established Fraktur notation for the Calkin algebra",
        "source_required": [r"\sto Q(H^2)\colon \phi"],
        "target_forbidden": [r"\sto Q(H^2)\colon \phi"],
        "target_required": [r"\sto \ofml Q(H^2)\colon \phi"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH16-CORR-005",
        "source_lines": (254, 258),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "repair the source typo 'and isomorphism' as the intended 'an isomorphism'",
        "source_required": ["establishes and isomorphism"],
        "target_forbidden": ["menghasilkan dan isomorfisme"],
        "target_required": ["menghasilkan isomorfisme"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH16-CORR-006",
        "source_lines": (298, 305),
        "classification": "MAP_IDENTITY_SOURCE_REPAIR",
        "decision": (
            "identify T, not beta, as the continuous/isometrical section because "
            "beta composed with T is the identity"
        ),
        "source_required": [r"refers to the mapping $\beta$ as"],
        "target_forbidden": [r"menyebut pemetaan $\beta$ sebagai"],
        "target_required": [r"menyebut pemetaan $T$ sebagai"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH16-CORR-007",
        "source_lines": (312, 314),
        "classification": "BIBLIOGRAPHIC_TYPO_SOURCE_REPAIR",
        "decision": "join the visibly split Douglas theorem number 7.2 6 as 7.26",
        "source_required": ["theorem 7.2 6"],
        "target_forbidden": ["teorema 7.2 6"],
        "target_required": ["teorema 7.26"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH16-CORR-008",
        "source_lines": (340, 357),
        "classification": "MATHEMATICAL_NOTATION_SOURCE_REPAIR",
        "decision": (
            "replace both cohomological-looking pi^1 expressions by the fundamental-group "
            "notation pi_1 and write the puncture as the set {0}"
        ),
        "source_required": [r"$\pi^1(\C \setminus 0)$"],
        "target_forbidden": [r"$\pi^1(\C \setminus 0)$"],
        "target_required": [r"$\pi_1(\C \setminus \{0\})$"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH16-CORR-009",
        "source_lines": (405, 411),
        "classification": "STALE_LOCATOR_SOURCE_REPAIR",
        "decision": (
            "replace the stale fixed reference to section 9.2 by a locale-neutral locator "
            "from the Addition of Extensions section onward"
        ),
        "source_required": ["after section 9.2"],
        "target_forbidden": ["setelah bagian 9.2"],
        "target_required": ["mulai bagian Penjumlahan Ekstensi"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH16-CORR-010",
        "source_lines": (444, 449),
        "classification": "DIAGRAM_TYPO_SOURCE_REPAIR",
        "decision": "remove the extra closing parenthesis from the restriction psi|_K",
        "source_required": [r"\psi|_{\ofml K)}"],
        "target_forbidden": [r"\psi|_{\ofml K)}"],
        "target_required": [r"\psi|_{\ofml K}"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH16-CORR-011",
        "source_lines": (547, 551),
        "classification": "MATHEMATICAL_NOTATION_SOURCE_REPAIR",
        "decision": "correct the pullback projection codomain from Fraktur A to A",
        "source_required": [r"\pi_2\colon \ofml E \sto \ofml A\colon"],
        "target_forbidden": [r"\pi_2\colon \ofml E \sto \ofml A\colon"],
        "target_required": [r"\pi_2\colon \ofml E \sto A\colon"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH16-CORR-012",
        "source_lines": (559, 566),
        "classification": "MISSING_VARIABLE_SOURCE_REPAIR",
        "decision": (
            "name the missing unitary operator U and express the two monomorphisms by the "
            "single typed family tau_j, j=1,2"
        ),
        "source_required": ["there exists a unitary operator on $H$ such that $\\tau_2 ="],
        "target_forbidden": ["terdapat suatu operator uniter pada $H$ sedemikian sehingga"],
        "target_required": ["Untuk $j=1,2$", r"$\tau_j\colon A \sto \ofml Q(H)$", "operator uniter $U$ pada $H$"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH16-CORR-013",
        "source_lines": (620, 634),
        "classification": "INDEX_TYPO_SOURCE_REPAIR",
        "decision": "repair both index-only misspellings Topelitz to Toeplitz",
        "source_required": ["Topelitz"],
        "target_forbidden": ["Topelitz"],
        "target_required": [r"\index{abstrak!operator!Toeplitz}", r"\index{abstrak!ekstensi!Toeplitz}"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH16-CORR-014",
        "source_lines": (886, 891),
        "classification": "MISSING_THEOREM_HYPOTHESIS",
        "decision": (
            "declare phi a unital completely positive linear map, the hypothesis required "
            "by the absorption theorem and the counterexample at phi(1)=2I"
        ),
        "source_required": [r"$\phi\colon A \sto \ofml B(H)$ (where"],
        "target_forbidden": [r"$\phi\colon A \sto \ofml B(H)$ (dengan"],
        "target_required": [r"$\phi\colon A \sto \ofml B(H)$ pemetaan linear beridentitas dan positif lengkap"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH16-CORR-015",
        "source_lines": (909, 924),
        "classification": "MATHEMATICAL_CATEGORY_SOURCE_REPAIR",
        "decision": (
            "make tau explicitly unital and replace the star-homomorphic lift, which would "
            "split the extension, by a unital completely positive linear lift"
        ),
        "source_required": [r"A $*\,$-monomorphism $\tau", r"unital $*\,$-homomorphism $\wt\tau"],
        "target_forbidden": [r"Suatu monomorfisme-$*\,$ $\tau", r"homomorfisme-$*\,$ beridentitas $\wt\tau"],
        "target_required": [r"monomorfisme-$*\,$ beridentitas $\tau", r"pemetaan linear beridentitas dan positif lengkap $\wt\tau"],
        "affects_math": True,
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
        target_snippet = normalize(target_lines, s0, s1)
        records.append(
            {
                "id": spec["id"],
                "source_lines": {"start": s0, "end": s1},
                "target_lines": {"start": s0, "end": s1},
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
        "unit_id": "FAOA-2015-CH16",
        "chapter": 16,
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
            "target_mapping": "same inclusive physical target-line range",
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
        "math_surface_affecting_record_ids": [record["id"] for record in records if record["affects_math"]],
        "independent_review": {
            "source_inventory": "qa/CH16_SOURCE_INVENTORY.md",
            "pretranslation_math_review": "qa/CH16_PRETRANSLATION_MATH_REVIEW.md",
            "terminology_plan": "provenance/CH16_TERMINOLOGY_PLAN.md",
            "bilingual_math_review": "qa/CH16_BILINGUAL_MATH_REVIEW.md",
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
