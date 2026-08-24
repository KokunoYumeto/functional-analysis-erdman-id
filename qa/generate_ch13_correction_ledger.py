#!/usr/bin/env python3
"""Generate and self-check the line-bounded Chapter 13 correction ledger."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "GNS_construction.tex"
TARGET = ROOT / "source" / "id-ID" / "GNS_construction-id.tex"
OUTPUT = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH13.json"
SOURCE_SHA = "fcc774cecc607d9860540da7b757ae04a3c43afe9d9a17e8c881e077f02682c1"
TARGET_SHA = "4c95b339702180ef8f2ea42cfba9e19a60a1740ca7d25a0568a6290f0170371f"


RECORDS = (
    {
        "id": "FAOA-2015-CH13-CORR-001",
        "source_lines": (27, 31),
        "target_lines": (27, 31),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "remove the duplicated positivity quantifier while retaining the exact domain and order condition",
        "forbidden": ["dalam~$A$ untuk semua $a \\in A$"],
        "required": ["untuk setiap $a \\in A$ yang memenuhi $a \\ge \\vc 0$"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH13-CORR-002",
        "source_lines": (43, 47),
        "target_lines": (43, 47),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": "define a state on a possibly nonunital C-star algebra as a positive norm-one functional and state the identity criterion only as the unital equivalent",
        "forbidden": ["$\\tau(\\vc 1) = 1$"],
        "required": ["$\\norm\\tau = 1$", "$\\tau(\\vc 1_A) = 1$"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH13-CORR-003",
        "source_lines": (66, 68),
        "target_lines": (66, 68),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": "restrict the norm-at-the-identity positivity criterion to a unital C-star algebra so that the displayed identity exists",
        "forbidden": ["pada aljabar-$C^*$ $A$ bersifat positif jika dan hanya jika"],
        "required": ["pada aljabar-$C^*$ beridentitas $A$ bersifat positif jika dan hanya jika"],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH13-CORR-004",
        "source_lines": (146, 149),
        "target_lines": (146, 149),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "replace the doubled exercise-final period with one period",
        "forbidden": ["$H$.."],
        "required": ["$H$."],
        "affects_math": False,
    },
    {
        "id": "FAOA-2015-CH13-CORR-005",
        "source_lines": (215, 219),
        "target_lines": (215, 219),
        "classification": "MATHEMATICAL_SOURCE_REPAIR",
        "decision": "complete the notation sentence by naming the given C-star algebra A and adding terminal punctuation",
        "forbidden": ["suatu aljabar-$C^*$\n\\end{notn}"],
        "required": ["suatu aljabar-$C^*$ $A$.\n\\end{notn}"],
        "affects_math": True,
    },
    {
        "id": "FAOA-2015-CH13-CORR-006",
        "source_lines": (230, 237),
        "target_lines": (230, 237),
        "classification": "MECHANICAL_PROSE_SOURCE_REPAIR",
        "decision": "repair 'that is.' punctuation and remove intrusive parentheses without changing the well-definedness claim",
        "forbidden": ["yaitu.", "(terdefinisi dengan baik dan)"],
        "required": ["yaitu,", "Operasi-operasi ini terdefinisi dengan baik dan menjadikan"],
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
    if len(source_bytes) != 11_965 or sha(source_bytes) != SOURCE_SHA:
        raise SystemExit("source identity mismatch")
    if len(target_bytes) != 12_601 or sha(target_bytes) != TARGET_SHA:
        raise SystemExit("target identity mismatch")
    source_lines = source_bytes.decode("ascii").splitlines()
    target_text = target_bytes.decode("utf-8")
    target_lines = target_text.splitlines()
    if len(source_lines) != 289 or len(target_lines) != 289:
        raise SystemExit("record topology mismatch")

    records = []
    for spec in RECORDS:
        s0, s1 = spec["source_lines"]
        t0, t1 = spec["target_lines"]
        source_snippet = normalize(source_lines, s0, s1)
        target_snippet = normalize(target_lines, t0, t1)
        for value in spec["forbidden"]:
            if value in target_text:
                raise SystemExit(f"forbidden target anchor remains: {spec['id']} {value!r}")
        for value in spec["required"]:
            if value not in target_text:
                raise SystemExit(f"required target anchor missing: {spec['id']} {value!r}")
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
                "forbidden_target_anchors": spec["forbidden"],
                "required_target_anchors": spec["required"],
                "affects_math": spec["affects_math"],
            }
        )

    class_counts: dict[str, int] = {}
    for record in records:
        key = record["classification"]
        class_counts[key] = class_counts.get(key, 0) + 1
    payload = {
        "schema_version": "o008.source-corrections.v1",
        "unit_id": "FAOA-2015-CH13",
        "chapter": 13,
        "status": "adjudicated_and_applied",
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "bytes": len(source_bytes),
            "logical_records": 289,
            "line_endings": "CRLF",
            "sha256": SOURCE_SHA,
        },
        "target": {
            "path": TARGET.relative_to(ROOT).as_posix(),
            "bytes": len(target_bytes),
            "logical_records": 289,
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
            "pretranslation_math_review": "qa/CH13_PRETRANSLATION_MATH_REVIEW.md",
            "terminology_plan": "provenance/CH13_TERMINOLOGY_PLAN.md",
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
