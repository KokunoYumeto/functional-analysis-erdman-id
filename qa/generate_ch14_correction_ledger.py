#!/usr/bin/env python3
"""Generate and self-check the line-bounded Chapter 14 correction ledger."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "multiplier_algebras.tex"
TARGET = ROOT / "source" / "id-ID" / "multiplier_algebras-id.tex"
OUTPUT = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH14.json"
SOURCE_BYTES = 30_579
SOURCE_RECORDS = 687
SOURCE_SHA = "d9bf8cf31a6e18a779863dcb397863430fe2daac9031a86354ce2274b42def7c"
TARGET_BYTES = 31_900
TARGET_RECORDS = 687
TARGET_SHA = "2688ec9c2370371060aada680f5f95e9511ecb61cb99c2a126385f525a3c9142"


RECORDS = (
    {
        "id": "FAOA-2015-CH14-CORR-001",
        "source_lines": (75, 79),
        "target_lines": (75, 79),
        "classification": "SEMANTIC_IDENTIFIER_SOURCE_REPAIR",
        "decision": "replace the undefined f in the antihomomorphism definition by the phi introduced by that definition",
        "source_required": [r"$f\colon A \sto B^{\textrm{op}}$ is a homomorphism"],
        "target_forbidden": [r"fungsi $f\colon A \sto B^{\textrm{op}}$"],
        "target_required": [r"fungsi $\phi\colon A \sto B^{\textrm{op}}$ merupakan suatu homomorfisme"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH14-CORR-002",
        "source_lines": (102, 104),
        "target_lines": (102, 104),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "repair the missing space in 'means,when' while translating the sentence",
        "source_required": ["means,when"],
        "target_forbidden": ["artinya,ketika"],
        "target_required": [r"apa artinya, ketika $A$ suatu aljabar-$C^*$"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH14-CORR-003",
        "source_lines": (208, 210),
        "target_lines": (209, 210),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "supply the missing sentence stop after the statement about Hilbert A-modules",
        "source_required": ["This is not true for Hilbert $A$-modules\n"],
        "target_forbidden": ["Hal ini tidak berlaku untuk modul Hilbert-$A$\n"],
        "target_required": ["Hal ini tidak berlaku untuk modul Hilbert-$A$."],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH14-CORR-004",
        "source_lines": (229, 233),
        "target_lines": (230, 233),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "replace the literal equals sign in the malformed C-star-algebra compound by normal derivative typography",
        "source_required": [r"$C^*$=algebra $\fml C(X)$"],
        "target_forbidden": [r"aljabar-$C^*$="],
        "target_required": [r"aljabar-$C^*$ $\fml C(X)$"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH14-CORR-005",
        "source_lines": (229, 234),
        "target_lines": (230, 235),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": "reverse the displayed inclusion so that the proper ideal W=J_0 includes into V=A",
        "source_required": [r"$\iota\colon V \sto W$ is a Hilbert"],
        "target_forbidden": [r"$\iota\colon V \sto W$"],
        "target_required": [r"$\iota\colon W \sto V$ merupakan morfisme modul Hilbert-$A$"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH14-CORR-006",
        "source_lines": (312, 317),
        "target_lines": (313, 318),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "render the erroneous past participle 'has lead' with its intended past-tense meaning",
        "source_required": ["The preceding example has lead many researchers"],
        "target_forbidden": ["telah memimpin banyak peneliti"],
        "target_required": ["Contoh sebelumnya telah mendorong banyak peneliti"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH14-CORR-007",
        "source_lines": (413, 420),
        "target_lines": (413, 420),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "join the period-fragment pair after 'subsets of an algebra' into one conditional notation sentence",
        "source_required": ["subsets of an algebra. By $AB$ we mean"],
        "target_forbidden": ["dari suatu aljabar. Dengan $AB$"],
        "target_required": ["dari suatu aljabar, maka $AB$ berarti"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH14-CORR-008",
        "source_lines": (641, 643),
        "target_lines": (641, 643),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "supply the second comma around 'if it exists' in the injectivity proposition",
        "source_required": ["$\\phi$, if it exists must\nbe injective."],
        "target_forbidden": [r"$\phi$, jika ada harus"],
        "target_required": ["$\\phi$, jika ada, harus\ninjektif."],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH14-CORR-009",
        "source_lines": (645, 647),
        "target_lines": (645, 647),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "supply the second comma around 'if it exists' in the uniqueness proposition",
        "source_required": ["$\\phi$, if it exists must\nbe unique."],
        "target_forbidden": [r"$\phi$, jika ada harus"],
        "target_required": ["$\\phi$, jika ada, harus\ntunggal."],
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
        key = record["classification"]
        class_counts[key] = class_counts.get(key, 0) + 1
    payload = {
        "schema_version": "o008.source-corrections.v1",
        "unit_id": "FAOA-2015-CH14",
        "chapter": 14,
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
            "pretranslation_math_review": "qa/CH14_PRETRANSLATION_MATH_REVIEW.md",
            "terminology_plan": "provenance/CH14_TERMINOLOGY_PLAN.md",
            "bilingual_math_review": "qa/CH14_BILINGUAL_MATH_REVIEW.md",
            "upstream_contact": "none during production",
        },
        "records": records,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
