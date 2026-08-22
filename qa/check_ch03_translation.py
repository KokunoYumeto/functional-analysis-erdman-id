#!/usr/bin/env python3
"""Bounded structural and mathematical audit for FAOA-2015-CH03."""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
import generate_ch01_backend as shared  # noqa: E402
import ch03_math  # noqa: E402


SOURCE = ROOT / "source" / "upstream" / "normlinspaces.tex"
TARGET = ROOT / "source" / "id-ID" / "normlinspaces-id.tex"
SOURCE_SHA = "01548b8e80e14f6eb66703579ed7020e68cc65bd8d30538c13a3533a5ba777e7"
TARGET_SHA = "c44f20890d5fb6b7445f0b2eeca8f477cc970d147d5c54aa4bc5df709f6b1f9d"
EXPECTED_MATH_DEVIATIONS = [
    ("replace", 40, 41, 40, 41),
    ("replace", 58, 59, 58, 59),
    ("replace", 61, 62, 61, 62),
    ("replace", 125, 126, 125, 126),
    ("replace", 369, 370, 369, 370),
    ("replace", 583, 584, 583, 584),
    ("replace", 682, 685, 682, 685),
    ("replace", 730, 731, 730, 731),
    ("replace", 739, 741, 739, 741),
    ("replace", 837, 838, 837, 838),
    ("replace", 877, 878, 877, 878),
    ("replace", 919, 920, 919, 920),
    ("replace", 1070, 1071, 1070, 1071),
    ("replace", 1117, 1118, 1117, 1118),
    ("replace", 1300, 1302, 1300, 1302),
    ("replace", 1379, 1380, 1379, 1380),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def index_operator_shape(argument: str) -> tuple[int, int, int]:
    return argument.count("@"), argument.count("!"), argument.count("|")


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha(source_bytes)) != (
        87537,
        1920,
        SOURCE_SHA,
    ):
        raise ValueError("Chapter 3 source authority changed")
    if (len(target_bytes), len(target_bytes.splitlines()), sha(target_bytes)) != (
        94040,
        1913,
        TARGET_SHA,
    ):
        raise ValueError("Chapter 3 admitted target candidate changed")
    source = source_bytes.decode("ascii")
    target = target_bytes.decode("utf-8")
    source_active = shared.active_same_length(source)
    target_active = shared.active_same_length(target)

    source_anchors = shared.parse_anchors(source)
    target_anchors = shared.parse_anchors(target)
    if len(source_anchors) != 185:
        raise ValueError("Chapter 3 source anchor count changed")
    if [shared.anchor_signature(a) for a in source_anchors] != [
        shared.anchor_signature(a) for a in target_anchors
    ]:
        raise ValueError("Chapter 3 semantic anchor topology differs")

    begin_pattern = re.compile(r"\\begin\{([^{}]+)\}")
    end_pattern = re.compile(r"\\end\{([^{}]+)\}")
    source_begins = begin_pattern.findall(source_active)
    target_begins = begin_pattern.findall(target_active)
    source_ends = end_pattern.findall(source_active)
    target_ends = end_pattern.findall(target_active)
    if source_begins != target_begins or source_ends != target_ends:
        raise ValueError("Chapter 3 complete environment sequence differs")

    exact_macros: dict[str, int] = {
        "label": 91,
        "cite": 6,
        "eqref": 1,
    }
    for macro, expected_count in exact_macros.items():
        source_values = [r["argument"] for r in shared.macro_occurrences(source, macro)]
        target_values = [r["argument"] for r in shared.macro_occurrences(target, macro)]
        if len(source_values) != expected_count or source_values != target_values:
            raise ValueError(f"Chapter 3 {macro} sequence differs")

    source_refs = [r["argument"] for r in shared.macro_occurrences(source, "ref")]
    target_refs = [r["argument"] for r in shared.macro_occurrences(target, "ref")]
    expected_target_refs = source_refs.copy()
    expected_target_refs.remove("exam_ran_nonclosed")
    if len(source_refs) != 47 or target_refs != expected_target_refs:
        raise ValueError("Chapter 3 local-reference sequence differs")
    future_refs = re.findall(
        r"\\futurexref\{([^{}]+)\}\{([^{}]+)\}", target_active
    )
    if future_refs != [("5.2.14", "exam_ran_nonclosed")]:
        raise ValueError("Chapter 3 future-reference projection differs")

    source_index = shared.macro_occurrences(source, "index")
    target_index = shared.macro_occurrences(target, "index")
    if len(source_index) != 344 or len(target_index) != 344:
        raise ValueError("Chapter 3 index occurrence count differs")
    source_shapes = [index_operator_shape(r["argument"]) for r in source_index]
    target_shapes = [index_operator_shape(r["argument"]) for r in target_index]
    if source_shapes != target_shapes:
        raise ValueError("Chapter 3 MakeIndex operator topology differs")
    if len(shared.macro_occurrences(source, "df")) != 98 or len(
        shared.macro_occurrences(target, "df")
    ) != 98:
        raise ValueError("Chapter 3 defined-term count differs")

    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if len(source_math) != 1414 or len(target_math) != 1414:
        raise ValueError(
            f"Chapter 3 math count differs: {len(source_math)} source / "
            f"{len(target_math)} target"
        )
    if [r["delimiter"] for r in source_math] != [r["delimiter"] for r in target_math]:
        raise ValueError("Chapter 3 math delimiter topology differs")
    matcher = difflib.SequenceMatcher(
        a=[ch03_math.math_key(r["normalized"]) for r in source_math],
        b=[ch03_math.math_key(r["normalized"]) for r in target_math],
        autojunk=False,
    )
    deviations = [opcode for opcode in matcher.get_opcodes() if opcode[0] != "equal"]
    if deviations != EXPECTED_MATH_DEVIATIONS:
        raise ValueError(f"unexpected Chapter 3 math deviations: {deviations}")

    placeholder_pattern = re.compile(
        r"(?i)(TODO|FIXME|TRANSLATE|PLACEHOLDER|Lorem ipsum|\[TBD\]|�)"
    )
    placeholders = [
        number
        for number, line in enumerate(target_active.splitlines(), 1)
        if placeholder_pattern.search(line)
    ]
    if placeholders:
        raise ValueError(f"Chapter 3 target contains placeholders at {placeholders}")

    print(
        json.dumps(
            {
                "source_bytes": len(source_bytes),
                "source_lines": len(source_bytes.splitlines()),
                "source_sha256": sha(source_bytes),
                "target_bytes": len(target_bytes),
                "target_lines": len(target_bytes.splitlines()),
                "target_sha256": sha(target_bytes),
                "semantic_anchors": len(source_anchors),
                "all_environment_pairs": len(source_begins),
                "labels": 91,
                "local_references": len(target_refs),
                "future_references": len(future_refs),
                "citations": 6,
                "index_terms": len(target_index),
                "defined_terms": 98,
                "source_math": len(source_math),
                "target_math": len(target_math),
                "math_deviation_opcodes": deviations,
                "placeholder_lines": placeholders,
                "result": "pass_reviewed_math_deviations_locked",
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
