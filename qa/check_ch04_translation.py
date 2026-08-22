#!/usr/bin/env python3
"""Bounded structural, mathematical, and residue audit for FAOA-2015-CH04."""

from __future__ import annotations

import bisect
import collections
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


SOURCE = ROOT / "source" / "upstream" / "Hilbert_spaces.tex"
TARGET = ROOT / "source" / "id-ID" / "Hilbert_spaces-id.tex"
CORRECTIONS = ROOT / "provenance" / "SOURCE_CORRECTIONS.md"

SOURCE_BYTES = 60_217
SOURCE_LINES = 1_340
SOURCE_SHA = "80fd8fd190beefde7787139be67ce29b9d9cce2d68ff66489aa1e4a93b54c740"
TARGET_BYTES = 62_947
TARGET_LINES = 1_351
TARGET_SHA = "b8e728e1f26a66ec2a420373e6104e3db4e5c954d7001acda1c13eb348322215"
CH04_CORRECTIONS_SHA = (
    "961806d5d229310c8063dc8941c8d4fd1caeabafe65bb9fa7df9045c17f53fe3"
)

EXPECTED_CHAPTER_TITLE = "RUANG HILBERT"
EXPECTED_SECTION_TITLES = [
    "Definisi dan Contoh",
    "Penjumlahan Tak Berurutan",
    "Geometri Ruang Hilbert",
    "Himpunan Ortonormal dan Basis",
    r"Teorema Riesz--Fr\'echet",
    "Topologi Kuat dan Lemah pada Ruang Hilbert",
    "Morfisme Universal",
    "Pelengkapan Ruang Hasil Kali Dalam",
]

MOVED_INDEX_SOURCE_ARGUMENTS = [
    r"l@$l_2 = l_2(\N)$!square summable sequences",
    r"l@$l_2 = l_2(\N)$!as an inner product space",
    r"inner product!space!$l_2$ as a",
]
MOVED_INDEX_SOURCE_POSITIONS = [144, 145, 146]
MOVED_INDEX_TARGET_POSITIONS = [11, 12, 13]
MOVED_INDEX_TARGET_CONTEXT = 6
MOVED_INDEX_TARGET_ARGUMENTS = [
    r"l@$l_2 = l_2(\N)$!barisan yang kuadratnya dapat dijumlahkan",
    r"l@$l_2 = l_2(\N)$!sebagai ruang hasil kali dalam",
    r"hasil kali dalam!ruang!$l_2$ sebagai",
]

# Each tuple is:
# structural-region, source ordinal, target ordinal, source line, target line,
# delimiter, SHA-256(source normalized payload), SHA-256(target normalized payload).
EXPECTED_MATH_CORRECTIONS = [
    (
        10,
        6,
        6,
        49,
        52,
        "bracket-display",
        "7fc7b16833607159d94a931e346883f92307fd33bc39f90d6eb7e5152c5b8362",
        "9a5d4f24f4b875407ca498db7cb8a944f12195c6f4f01f6e6a21a130cccdf086",
    ),
    (
        31,
        130,
        130,
        220,
        223,
        "dollar-inline",
        "b8326ac3949d6bb579c9feba89245f06130e258bd0cc347ab52404dcfd84fdea",
        "34c17efb56009232204dde7288b1bf205737d52dd806fe0bb9a8a825bc0f6ea9",
    ),
    (
        97,
        262,
        262,
        435,
        438,
        "dollar-inline",
        "98a822bbf6a078b322ca21540e00e0f88d659835d53168cfd78ff1f8f13735c2",
        "fc77f510b6e744edc35549b1dea16d2dfc3795888cbb36affe4888656fc6c897",
    ),
    (
        128,
        356,
        356,
        562,
        565,
        "dollar-inline",
        "716937f5ca7e5e0dac4b0cdf5c7a4ef11240714c29c75177987ee7d9b333ea86",
        "9b9ff44315dd324b69ef54f8936c7c651066f554a32630612fcea1dabd84a943",
    ),
    (
        203,
        517,
        517,
        847,
        850,
        "bracket-display",
        "cf1f9c14a514a416a71a9ac570e08b1037bdd7d5d758dd92970420159695101c",
        "d04bc5f22ab93c9cc17b2bae26d69b602643db72cc9721c4a323851f32541d40",
    ),
    (
        203,
        520,
        520,
        849,
        852,
        "dollar-inline",
        "bba7635e3ec0411a54164c3416b0cafdfdf9e6b04de30ef8eedf09f18a4c3b97",
        "30e52f88ba60c98e8ab097db8e33cba3916e0170ae1a79a3655b9ac83f103294",
    ),
    (
        246,
        657,
        657,
        1076,
        1077,
        "bracket-display",
        "35f88b21c295be6df38656cc128d5bedb251e24619f01974d9f18735e43176bd",
        "b8aa36e60225614c559c0847466d5523bd4473ac10257ed1ce245cb8b93e002e",
    ),
    (
        250,
        699,
        699,
        1119,
        1121,
        "dollar-inline",
        "b1e30575d0dd3bbb403131779f8e8fc9cce3d64dc00b127d2479e84d7ba383ac",
        "3c5a3cb3688370e74eddfb42d53c9262c3521e57eec881a01e8d9b88035e9184",
    ),
    (
        266,
        756,
        756,
        1192,
        1201,
        "dollar-inline",
        "21b0f22e0fed31e1cfe587e512826a92b1628de0b7f6e9b646ec15ba17ea9468",
        "f2d8846ff4775f90ce2e46398bdd02ea35468e60a94229c5c5dcf27386cc80fc",
    ),
]

# Reader-facing Indonesian writes the ordinal as ``ke-$n$`` rather than
# retaining the English-only math payload ``$n^{\text{th}}$``.  This changes
# the normalized math key, so it is locked separately from source corrections.
EXPECTED_MATH_KEY_LOCALIZATIONS = [
    (
        125,
        343,
        343,
        541,
        544,
        "dollar-inline",
        "a5baf4650be252b07d2ff891e41921b8ec99d06d0a82d72c6ace173469135a4e",
        "1b16b1df538ba12dc3f97edbb85caa7050d46c148134290feba80f8236c83db9",
    )
]

EXPECTED_MATH_LOCALIZATIONS = [
    (
        26,
        120,
        120,
        209,
        212,
        "environment:equation",
        "2e00e4b339245e20e014bac07934864b874e64ee35e47051f15da4e9e77dde7e",
        "a96aa2bd9ada1f771abf4e53d3e4ea4f7a3311ccb7c577126ff6212ec5a7ce2b",
    ),
    (
        70,
        216,
        216,
        378,
        381,
        "bracket-display",
        "a1dee87b0fa3a94f825da3debeac23716fe362724e6b2bbbe43b2a01cabd75ca",
        "98f95f8c70ce2f39b0ae9f73005ac625bbf6bb4c0f1a3ad9e98de952fb65fa70",
    ),
    (
        187,
        478,
        478,
        790,
        793,
        "bracket-display",
        "f488e8e0ebe78ee2792593c71d458c7e6b729d4b10f0754303d9e2da9721741a",
        "9b7b38de90ee3fd2d6a12d74aa80e43f18b970883686d4cd345952d040d0e14c",
    ),
    (
        203,
        522,
        522,
        850,
        853,
        "bracket-display",
        "f7bf5b86b4eef78005cd270b7150b800d419f220e0676e94998e2750faa58f86",
        "0315b3b6d54142e637262b57ca98e0753583a1e0d1c4c733c9b8361662430ed1",
    ),
    (
        234,
        619,
        619,
        1030,
        1033,
        "bracket-display",
        "49bf5c339a57fdd31950960e18be91b2972c8eaf37b71f57ec80eb3802658fe9",
        "266058dc4e1cf6f8a9424d0de6867d184cd874947a4464f0a9fca3c7cd2b2191",
    ),
]

# These are exact-key surfaces reordered only within their unchanged structural
# region so natural Indonesian grammar does not masquerade as a math edit.
EXPECTED_MATH_REORDERS = [
    (224, 591, 590, 968, 971, "d3b6610c0efcd89dba917396dbbf99846d1b6538b8304ae50967dccab739d063"),
    (224, 589, 588, 967, 970, "b2d2d8983c52ae8ea6ea1b982127d9e20734aa1f139e284fb1a73d4b8a2b36d8"),
    (224, 590, 591, 968, 971, "d2c2d881bc19477af2da8b5b8f5fdaaadc423fcaa88729fee89e2bc99f755761"),
    (224, 588, 589, 967, 970, "6066c7e52cd5a5335ba10b2d0b5de729d48bc2b32dc6b8f0e02f4a48c29dec06"),
    (248, 686, 685, 1106, 1108, "93d570fa26aa5455eb2d36d4fb31f15ce994c6654a51095c9ce2e78c83fb367e"),
    (248, 685, 686, 1105, 1108, "b833ff110a1f3aa91cce5e29b7c3c4be83e3750a2c35aace551a91a82db6a788"),
    (250, 693, 692, 1117, 1118, "47b34af59b56e5550dbe28446da9847997b6f54b755d54f4d9ffffab91c0743b"),
    (250, 694, 693, 1117, 1118, "f75dd322f11ad636343cfddc0ab015be9f05026792947176930e78f68d1126bd"),
    (250, 692, 694, 1116, 1118, "b833ff110a1f3aa91cce5e29b7c3c4be83e3750a2c35aace551a91a82db6a788"),
    (260, 746, 745, 1171, 1177, "2677331410aadc25164efbcb18609148f8add2da024e2f6104b5458ff5ab3edf"),
    (260, 745, 746, 1170, 1177, "d2c2d881bc19477af2da8b5b8f5fdaaadc423fcaa88729fee89e2bc99f755761"),
    (260, 743, 744, 1170, 1176, "6066c7e52cd5a5335ba10b2d0b5de729d48bc2b32dc6b8f0e02f4a48c29dec06"),
    (260, 744, 743, 1170, 1176, "3e824bdfdb6ffbbd54f17e5b4941878dc8aba362a9c0268878f0e17f1bffddc3"),
    (266, 765, 764, 1195, 1204, "438ec08ce3682422c2f16386f8a3ce8dc91617b02f95de8f75c60529b87622a6"),
    (266, 764, 765, 1194, 1204, "b833ff110a1f3aa91cce5e29b7c3c4be83e3750a2c35aace551a91a82db6a788"),
]

EXPECTED_DIAGRAMS = [
    ("xymatrix", "d5be8d90ab85d717c357f8a3102095d5c0fe55db2f826c251dbf93db4b9c00f7"),
    ("xy", "f95f473814e7dd749ddd09dc1c6be75057b0456d0661a8bce716168cf4c0c536"),
    ("xy", "407041b56c8a26b0aff8043e702774e802bad57f87f782c1d8c402c79d634e72"),
    ("xy", "34837f70c564af1111365f9e04d06800a11877f1ccbf25581a08af901e06858f"),
    ("xy", "f7e390dfc4528543e77930d36531b5aeb6dcd8f9ae0815cb392f8e2f19dc0780"),
    ("xy", "7b15e7607a1c11563ec8f2675f7ec9a33e5da27461ef8e8885e2263e5d536ef5"),
    ("xy", "e6352e8295a6c0a55c8e1adfa961c21d57f24e85ca977b569026a4ff94a3be8b"),
    ("xy", "932dc1d848acded068270e7b7465f6b6400bc150c82b416934b67bc233d2ee07"),
    ("xy", "7467647b15ecb9880583760109993bb14edd1889883773a3334457a5698f0c42"),
    ("xy", "19734821d0caf12a562e423037e2c690950226eb3c1f12c46b492765a9a2c2e6"),
    ("xy", "5563b65d878f889c1683bd3a6b22c4e58546417b51ee593032c7153be4cba642"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_sha(value: str) -> str:
    return sha(value.encode("utf-8"))


def exact_macro_occurrences(text: str, macro: str) -> list[dict]:
    """Parse only the exact braced macro, never longer prefix-sharing names."""

    active = shared.active_same_length(text)
    pattern = re.compile(r"\\" + re.escape(macro) + r"(?=\s*\{)")
    output: list[dict] = []
    for match in pattern.finditer(active):
        brace = active.find("{", match.end())
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


def futurexref_occurrences(text: str) -> list[dict]:
    active = shared.active_same_length(text)
    output: list[dict] = []
    for match in re.finditer(r"\\futurexref(?=\s*\{)", active):
        first_brace = active.find("{", match.end())
        first_end = shared.balanced_end(active, first_brace)
        second_brace = active.find("{", first_end)
        if second_brace < 0:
            raise ValueError("Chapter 4 futurexref lacks its second argument")
        second_end = shared.balanced_end(active, second_brace)
        output.append(
            {
                "start": match.start(),
                "end": second_end,
                "printed": text[first_brace + 1 : first_end - 1],
                "source_label": text[second_brace + 1 : second_end - 1],
                "line": shared.line_of(text, match.start()),
            }
        )
    return output


def structural_boundaries(text: str) -> list[tuple[int, tuple[str, ...]]]:
    active = shared.active_same_length(text)
    output: list[tuple[int, tuple[str, ...]]] = []
    pattern = re.compile(
        r"\\(chapter|section)\s*\{|\\(begin|end)\{([^{}]+)\}"
    )
    for match in pattern.finditer(active):
        if match.group(1):
            signature = ("heading", match.group(1))
        else:
            signature = ("environment", match.group(2), match.group(3))
        output.append((match.start(), signature))
    return output


def occurrence_contexts(
    occurrences: list[dict], boundaries: list[tuple[int, tuple[str, ...]]]
) -> list[int]:
    offsets = [offset for offset, _ in boundaries]
    return [bisect.bisect_right(offsets, row["start"]) - 1 for row in occurrences]


def blank_range(chars: list[str], start: int, end: int) -> None:
    for position in range(start, end):
        if chars[position] not in "\r\n":
            chars[position] = " "


def blank_index_macros(text: str) -> str:
    """Blank balanced index payloads and their trailing TeX comment marker."""

    chars = list(text)
    for occurrence in exact_macro_occurrences(text, "index"):
        end = occurrence["end"]
        if end < len(chars) and chars[end] == "%":
            end += 1
        blank_range(chars, occurrence["start"], end)
    return "".join(chars)


def index_operator_shape(argument: str) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    operators = "".join(char for char in argument if char in "@!|")
    at_prefixes = tuple(
        segment.split("@", 1)[0]
        for segment in argument.split("!")
        if "@" in segment
    )
    math_keys = tuple(
        ch03_math.math_key(record["normalized"])
        for record in ch03_math.extract_math(argument, "utf-8")
    )
    return operators, at_prefixes, math_keys


def diagram_signatures(text: str) -> list[tuple[str, str]]:
    active = shared.active_same_length(blank_index_macros(text))
    output: list[tuple[str, str]] = []
    for match in re.finditer(r"\\xymatrix\s*\{|\\xy\b", active):
        if match.group(0).startswith("\\xymatrix"):
            brace = active.find("{", match.start())
            end = shared.balanced_end(active, brace)
            kind = "xymatrix"
        else:
            close = active.find("\\endxy", match.end())
            if close < 0:
                raise ValueError("Chapter 4 has an unclosed XY-pic block")
            end = close + len("\\endxy")
            kind = "xy"
        normalized = re.sub(r"\s+", "", active[match.start() : end])
        output.append((kind, normalized_sha(normalized)))
    return output


def group_math_by_region(
    math: list[dict], boundaries: list[tuple[int, tuple[str, ...]]]
) -> dict[int, list[int]]:
    offsets = [offset for offset, _ in boundaries]
    groups: dict[int, list[int]] = collections.defaultdict(list)
    for ordinal, record in enumerate(math):
        region = bisect.bisect_right(offsets, record["start"]) - 1
        groups[region].append(ordinal)
    return groups


def math_review_signatures(
    source_math: list[dict],
    target_math: list[dict],
    source_boundaries: list[tuple[int, tuple[str, ...]]],
    target_boundaries: list[tuple[int, tuple[str, ...]]],
) -> tuple[list[tuple], list[tuple], list[tuple], int]:
    """Anchor duplicate formulas by structural region before comparing them."""

    source_groups = group_math_by_region(source_math, source_boundaries)
    target_groups = group_math_by_region(target_math, target_boundaries)
    exact_pairs: list[tuple[int, int, int]] = []
    corrections: list[tuple] = []

    for region in sorted(set(source_groups) | set(target_groups)):
        source_by_key: dict[str, list[int]] = collections.defaultdict(list)
        target_by_key: dict[str, list[int]] = collections.defaultdict(list)
        for ordinal in source_groups[region]:
            source_by_key[ch03_math.math_key(source_math[ordinal]["normalized"])].append(
                ordinal
            )
        for ordinal in target_groups[region]:
            target_by_key[ch03_math.math_key(target_math[ordinal]["normalized"])].append(
                ordinal
            )

        unmatched_source: list[int] = []
        unmatched_target: list[int] = []
        for key in sorted(set(source_by_key) | set(target_by_key)):
            source_ordinals = source_by_key[key]
            target_ordinals = target_by_key[key]
            shared_count = min(len(source_ordinals), len(target_ordinals))
            exact_pairs.extend(
                (region, source_ordinals[index], target_ordinals[index])
                for index in range(shared_count)
            )
            unmatched_source.extend(source_ordinals[shared_count:])
            unmatched_target.extend(target_ordinals[shared_count:])

        unmatched_source.sort()
        unmatched_target.sort()
        if len(unmatched_source) != len(unmatched_target):
            raise ValueError(
                f"Chapter 4 region {region} has unpaired math corrections"
            )
        for source_ordinal, target_ordinal in zip(
            unmatched_source, unmatched_target, strict=True
        ):
            source_record = source_math[source_ordinal]
            target_record = target_math[target_ordinal]
            if source_record["delimiter"] != target_record["delimiter"]:
                raise ValueError(
                    f"Chapter 4 corrected math delimiter differs in region {region}"
                )
            corrections.append(
                (
                    region,
                    source_ordinal,
                    target_ordinal,
                    source_record["line_start"],
                    target_record["line_start"],
                    source_record["delimiter"],
                    normalized_sha(source_record["normalized"]),
                    normalized_sha(target_record["normalized"]),
                )
            )

    localizations: list[tuple] = []
    reorders: list[tuple] = []
    for region, source_ordinal, target_ordinal in exact_pairs:
        source_record = source_math[source_ordinal]
        target_record = target_math[target_ordinal]
        if source_record["normalized"] != target_record["normalized"]:
            localizations.append(
                (
                    region,
                    source_ordinal,
                    target_ordinal,
                    source_record["line_start"],
                    target_record["line_start"],
                    source_record["delimiter"],
                    normalized_sha(source_record["normalized"]),
                    normalized_sha(target_record["normalized"]),
                )
            )
        if source_ordinal != target_ordinal:
            reorders.append(
                (
                    region,
                    source_ordinal,
                    target_ordinal,
                    source_record["line_start"],
                    target_record["line_start"],
                    normalized_sha(ch03_math.math_key(source_record["normalized"])),
                )
            )
    return corrections, localizations, reorders, len(exact_pairs)


def correction_section(text: str) -> str:
    start = text.find("## Chapter 4")
    if start < 0:
        raise ValueError("SOURCE_CORRECTIONS lacks its Chapter 4 section")
    next_heading = re.search(r"(?m)^## ", text[start + 1 :])
    end = start + 1 + next_heading.start() if next_heading else len(text)
    return text[start:end]


def residue_and_placeholder_lines(target: str) -> tuple[list[int], list[int]]:
    active = shared.active_same_length(target)
    placeholder_pattern = re.compile(
        r"(?i)(TODO|FIXME|TRANSLATE|PLACEHOLDER|Lorem ipsum|\[TBD\]|�)"
    )
    placeholders = [
        line_number
        for line_number, line in enumerate(active.splitlines(), 1)
        if placeholder_pattern.search(line)
    ]

    work = blank_index_macros(target)
    chars = list(shared.active_same_length(work))
    for record in ch03_math.extract_math(work, "utf-8"):
        blank_range(chars, record["start"], record["end"])
    for macro in ("label", "ref", "eqref", "cite", "index"):
        for occurrence in exact_macro_occurrences(target, macro):
            blank_range(chars, occurrence["start"], occurrence["end"])
    for occurrence in futurexref_occurrences(target):
        blank_range(chars, occurrence["start"], occurrence["end"])
    for match in re.finditer(r"\\(?:begin|end)\{[^{}]+\}", active):
        blank_range(chars, match.start(), match.end())

    scrubbed = "".join(chars)
    for match in re.finditer(r"\\(?:[A-Za-z@]+|.)", scrubbed):
        blank_range(chars, match.start(), match.end())
    scrubbed = "".join(chars)

    # This exact English query is deliberately retained from the source search
    # suggestion and is separately recorded as a citation-quality warning.
    scrubbed = re.sub(r"(?i)universal\s+property", " ", scrubbed)
    english_pattern = re.compile(
        r"(?i)\b(?:the|and|or|if|then|let|suppose|show|prove|explain|where|"
        r"which|what|why|this|that|these|those|with|without|for|from|into|"
        r"onto|under|above|below|following|preceding|every|some|any|all|only|"
        r"called|defined|denoted|belongs|exists|unique|space|function|mapping|"
        r"map|set|subset|vector|sequence|series|topology|weakly|strongly|"
        r"continuous|closed|compact|proof|exercise|example|proposition|theorem|"
        r"definition|property)\b"
    )
    residue = [
        line_number
        for line_number, line in enumerate(scrubbed.splitlines(), 1)
        if english_pattern.search(line)
    ]
    return placeholders, residue


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha(source_bytes)) != (
        SOURCE_BYTES,
        SOURCE_LINES,
        SOURCE_SHA,
    ):
        raise ValueError("Chapter 4 source authority changed")
    if (len(target_bytes), len(target_bytes.splitlines()), sha(target_bytes)) != (
        TARGET_BYTES,
        TARGET_LINES,
        TARGET_SHA,
    ):
        raise ValueError("Chapter 4 admitted target candidate changed")

    source = source_bytes.decode("ascii")
    target = target_bytes.decode("utf-8")
    source_active = shared.active_same_length(source)
    target_active = shared.active_same_length(target)

    chapter_titles = [
        row["argument"] for row in exact_macro_occurrences(target, "chapter")
    ]
    section_titles = [
        row["argument"] for row in exact_macro_occurrences(target, "section")
    ]
    if chapter_titles != [EXPECTED_CHAPTER_TITLE] or section_titles != EXPECTED_SECTION_TITLES:
        raise ValueError("Chapter 4 controlled heading sequence differs")

    source_boundaries = structural_boundaries(source)
    target_boundaries = structural_boundaries(target)
    if [signature for _, signature in source_boundaries] != [
        signature for _, signature in target_boundaries
    ]:
        raise ValueError("Chapter 4 structural boundary topology differs")
    if len(source_boundaries) != 297:
        raise ValueError("Chapter 4 structural boundary count changed")

    environment_pattern = re.compile(r"\\(begin|end)\{([^{}]+)\}")
    source_environments = environment_pattern.findall(source_active)
    target_environments = environment_pattern.findall(target_active)
    if source_environments != target_environments:
        raise ValueError("Chapter 4 ordered environment topology differs")
    if sum(action == "begin" for action, _ in source_environments) != 144:
        raise ValueError("Chapter 4 environment count changed")

    source_anchors = shared.parse_anchors(source)
    target_anchors = shared.parse_anchors(target)
    if len(source_anchors) != 131 or [
        shared.anchor_signature(anchor) for anchor in source_anchors
    ] != [shared.anchor_signature(anchor) for anchor in target_anchors]:
        raise ValueError("Chapter 4 semantic anchor topology differs")

    exact_macros = {"label": 44, "eqref": 2, "cite": 12}
    for macro, expected_count in exact_macros.items():
        source_rows = exact_macro_occurrences(source, macro)
        target_rows = exact_macro_occurrences(target, macro)
        if len(source_rows) != expected_count or [
            row["argument"] for row in source_rows
        ] != [row["argument"] for row in target_rows]:
            raise ValueError(f"Chapter 4 ordered {macro} topology differs")
        if occurrence_contexts(source_rows, source_boundaries) != occurrence_contexts(
            target_rows, target_boundaries
        ):
            raise ValueError(f"Chapter 4 {macro} structural contexts differ")

    source_refs = exact_macro_occurrences(source, "ref")
    target_refs = exact_macro_occurrences(target, "ref")
    if len(source_refs) != 51 or len(target_refs) != 50:
        raise ValueError("Chapter 4 reference count differs")
    future_position = [row["argument"] for row in source_refs].index("C067441")
    if future_position != 33:
        raise ValueError("Chapter 4 future reference source position changed")
    expected_refs = source_refs.copy()
    source_future = expected_refs.pop(future_position)
    if [row["argument"] for row in expected_refs] != [
        row["argument"] for row in target_refs
    ]:
        raise ValueError("Chapter 4 ordered local-reference projection differs")
    expected_ref_contexts = occurrence_contexts(expected_refs, source_boundaries)
    if expected_ref_contexts != occurrence_contexts(target_refs, target_boundaries):
        raise ValueError("Chapter 4 projected reference contexts differ")
    future_refs = futurexref_occurrences(target)
    if [
        (row["printed"], row["source_label"]) for row in future_refs
    ] != [("6.2.9", "C067441")]:
        raise ValueError("Chapter 4 future-reference projection differs")
    if occurrence_contexts(future_refs, target_boundaries) != occurrence_contexts(
        [source_future], source_boundaries
    ):
        raise ValueError("Chapter 4 future-reference context differs")

    source_df = exact_macro_occurrences(source, "df")
    target_df = exact_macro_occurrences(target, "df")
    if len(source_df) != 59 or len(target_df) != 59:
        raise ValueError("Chapter 4 defined-term count differs")
    if occurrence_contexts(source_df, source_boundaries) != occurrence_contexts(
        target_df, target_boundaries
    ):
        raise ValueError("Chapter 4 defined-term topology differs")
    if target_df[56]["argument"] != r"morfisme kouniversal untuk $B$ (terhadap~$\ftr F$)":
        raise ValueError("Chapter 4 co-universal defined-term correction differs")

    source_index = exact_macro_occurrences(source, "index")
    target_index = exact_macro_occurrences(target, "index")
    if len(source_index) != 177 or len(target_index) != 177:
        raise ValueError("Chapter 4 index occurrence count differs")
    source_positions = [
        [row["argument"] for row in source_index].index(argument)
        for argument in MOVED_INDEX_SOURCE_ARGUMENTS
    ]
    if source_positions != MOVED_INDEX_SOURCE_POSITIONS:
        raise ValueError("Chapter 4 relocated index source positions changed")
    if [target_index[position]["argument"] for position in MOVED_INDEX_TARGET_POSITIONS] != (
        MOVED_INDEX_TARGET_ARGUMENTS
    ):
        raise ValueError("Chapter 4 relocated index target payloads differ")

    source_index_shapes = [index_operator_shape(row["argument"]) for row in source_index]
    target_index_shapes = [index_operator_shape(row["argument"]) for row in target_index]
    moved_shapes = [source_index_shapes[position] for position in source_positions]
    expected_index_shapes = [
        shape
        for position, shape in enumerate(source_index_shapes)
        if position not in source_positions
    ]
    for target_position, shape in zip(
        MOVED_INDEX_TARGET_POSITIONS, moved_shapes, strict=True
    ):
        expected_index_shapes.insert(target_position, shape)
    if expected_index_shapes != target_index_shapes:
        raise ValueError("Chapter 4 ordered MakeIndex operator/math topology differs")

    source_index_contexts = occurrence_contexts(source_index, source_boundaries)
    target_index_contexts = occurrence_contexts(target_index, target_boundaries)
    expected_index_contexts = [
        context
        for position, context in enumerate(source_index_contexts)
        if position not in source_positions
    ]
    for target_position in MOVED_INDEX_TARGET_POSITIONS:
        expected_index_contexts.insert(target_position, MOVED_INDEX_TARGET_CONTEXT)
    if expected_index_contexts != target_index_contexts:
        raise ValueError("Chapter 4 ordered MakeIndex structural contexts differ")
    source_operator_totals = tuple(
        sum(row["argument"].count(operator) for row in source_index)
        for operator in "@!|"
    )
    target_operator_totals = tuple(
        sum(row["argument"].count(operator) for row in target_index)
        for operator in "@!|"
    )
    if source_operator_totals != (29, 185, 0) or target_operator_totals != (
        29,
        185,
        0,
    ):
        raise ValueError("Chapter 4 MakeIndex operator totals differ")

    source_diagrams = diagram_signatures(source)
    target_diagrams = diagram_signatures(target)
    if source_diagrams != EXPECTED_DIAGRAMS or target_diagrams != EXPECTED_DIAGRAMS:
        raise ValueError("Chapter 4 ordered diagram topology differs")
    diagram_active = shared.active_same_length(blank_index_macros(target))
    diagram_macro_counts = {
        "xymatrix": len(re.findall(r"\\xymatrix\b", diagram_active)),
        "xy": len(re.findall(r"\\xy\b", diagram_active)),
        "endxy": len(re.findall(r"\\endxy\b", diagram_active)),
        "qtriangle": len(re.findall(r"\\qtriangle\b", diagram_active)),
        "Atrianglepair": len(re.findall(r"\\Atrianglepair\b", diagram_active)),
    }
    if diagram_macro_counts != {
        "xymatrix": 1,
        "xy": 10,
        "endxy": 10,
        "qtriangle": 8,
        "Atrianglepair": 2,
    }:
        raise ValueError("Chapter 4 diagram macro census differs")

    source_math = ch03_math.extract_math(blank_index_macros(source), "ascii")
    target_math = ch03_math.extract_math(blank_index_macros(target), "utf-8")
    if len(source_math) != 817 or len(target_math) != 817:
        raise ValueError(
            f"Chapter 4 math count differs: {len(source_math)} source / "
            f"{len(target_math)} target"
        )
    if [row["delimiter"] for row in source_math] != [
        row["delimiter"] for row in target_math
    ]:
        raise ValueError("Chapter 4 math delimiter topology differs")
    raw_corrections, localizations, reorders, exact_math_pairs = math_review_signatures(
        source_math,
        target_math,
        source_boundaries,
        target_boundaries,
    )
    key_localizations = [
        row for row in raw_corrections if row in EXPECTED_MATH_KEY_LOCALIZATIONS
    ]
    corrections = [
        row for row in raw_corrections if row not in EXPECTED_MATH_KEY_LOCALIZATIONS
    ]
    if corrections != EXPECTED_MATH_CORRECTIONS:
        raise ValueError(f"unexpected Chapter 4 math corrections: {corrections}")
    if key_localizations != EXPECTED_MATH_KEY_LOCALIZATIONS:
        raise ValueError(
            f"unexpected Chapter 4 math-key localizations: {key_localizations}"
        )
    if localizations != EXPECTED_MATH_LOCALIZATIONS:
        raise ValueError(f"unexpected Chapter 4 math localizations: {localizations}")
    if reorders != EXPECTED_MATH_REORDERS:
        raise ValueError(f"unexpected Chapter 4 localized math reorderings: {reorders}")
    if exact_math_pairs != 807:
        raise ValueError("Chapter 4 exact math-pair count differs")

    corrections_text = CORRECTIONS.read_text(encoding="utf-8")
    chapter4_corrections = correction_section(corrections_text)
    if sha(chapter4_corrections.encode("utf-8")) != CH04_CORRECTIONS_SHA:
        raise ValueError("Chapter 4 source-correction ledger section changed")
    if len(re.findall(r"(?m)^\d+\.", chapter4_corrections)) != 22:
        raise ValueError("Chapter 4 source-correction ledger census differs")

    placeholder_lines, residue_lines = residue_and_placeholder_lines(target)
    if placeholder_lines:
        raise ValueError(f"Chapter 4 target contains placeholders at {placeholder_lines}")
    if residue_lines:
        raise ValueError(f"Chapter 4 target contains English residue at {residue_lines}")

    print(
        json.dumps(
            {
                "all_environment_pairs": 144,
                "citations": 12,
                "correction_ledger_ch04_sha256": CH04_CORRECTIONS_SHA,
                "defined_terms": 59,
                "diagram_blocks": len(target_diagrams),
                "diagram_macro_counts": diagram_macro_counts,
                "english_residue_lines": residue_lines,
                "exact_math_pairs": exact_math_pairs,
                "future_references": [
                    {
                        "printed": row["printed"],
                        "source_label": row["source_label"],
                    }
                    for row in future_refs
                ],
                "index_operator_totals": {
                    "at": target_operator_totals[0],
                    "hierarchy": target_operator_totals[1],
                    "encapsulation": target_operator_totals[2],
                },
                "index_terms": len(target_index),
                "labels": 44,
                "local_references": len(target_refs),
                "math_corrections": len(corrections),
                "math_key_localizations": len(key_localizations),
                "math_localizations": len(localizations) + len(key_localizations),
                "math_reorders": len(reorders),
                "placeholder_lines": placeholder_lines,
                "result": "pass_reviewed_ch04_translation_locked",
                "semantic_anchors": len(source_anchors),
                "source_bytes": len(source_bytes),
                "source_lines": len(source_bytes.splitlines()),
                "source_math": len(source_math),
                "source_sha256": sha(source_bytes),
                "structural_boundaries": len(source_boundaries),
                "target_bytes": len(target_bytes),
                "target_lines": len(target_bytes.splitlines()),
                "target_math": len(target_math),
                "target_sha256": sha(target_bytes),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
