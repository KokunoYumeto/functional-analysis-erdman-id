#!/usr/bin/env python3
"""Locked structural, mathematical, reference, rights, and residue audit for CH08."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qa"))
sys.path.insert(0, str(ROOT / "backend"))
import check_ch05_translation as common  # noqa: E402
import ch03_math  # noqa: E402


SOURCE = ROOT / "source" / "upstream" / "spectrum.tex"
TARGET = ROOT / "source" / "id-ID" / "spectrum-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch08.tex"
CORRECTIONS = ROOT / "provenance" / "SOURCE_CORRECTIONS.md"

SOURCE_BYTES = 25_716
SOURCE_LINES = 611
SOURCE_SHA256 = "ae68cf224c6218ecd501cc983428cf924a3c361c6324a6b40793b1e9ba44b4dd"
SOURCE_ACTIVE_BYTES = 25_698
SOURCE_ACTIVE_LINES = 603
SOURCE_ACTIVE_SHA256 = "2c4dea4be2cfb89eb507742b4052619c7cf09904d54921884f88be49b19ba05b"
SOURCE_TAIL_SHA256 = "2441ab53ba42405bf33990cd03799fe967666cb0d78de821577c7c876a9e4919"

TARGET_BYTES = 26_947
TARGET_LINES = 603
TARGET_SHA256 = "1120da36ebd0793690ecb47b33b921c81376d1bf7d2f03d9821b79356dfd03bc"
TARGET_ACTIVE_BYTES = 26_946
TARGET_ACTIVE_SHA256 = "596c74549f38600a8a96c251189f2c43d11980bc1df61b63dc7e9ccd82a745ae"

MASTER_BYTES = 9_714
MASTER_LINES = 334
MASTER_SHA256 = "d0b4130b9fa6f85baef22f316ea914d5519bf30d6e82d8e6d824f2cf211c1998"

EXPECTED_CHAPTER_TITLE = "BEBERAPA TEORI SPEKTRAL"
EXPECTED_SECTION_TITLES = [
    "Spektrum",
    "Spektrum Operator Ruang Hilbert",
]

EXPECTED_ENVIRONMENT_BEGIN_COUNTS = {
    "bmatrix": 2,
    "cor": 8,
    "defn": 8,
    "enumerate": 10,
    "exam": 14,
    "exer": 2,
    "notn": 1,
    "proof": 14,
    "prop": 33,
    "thm": 4,
}

EXPECTED_COUNTS = {
    "environment_pairs": 96,
    "labels": 28,
    "references": 16,
    "equation_references": 0,
    "future_references": 0,
    "citations": 3,
    "indexes": 73,
    "defined_terms": 20,
    "exercises": 2,
    "proofs": 14,
    "proof_hints": 12,
    "proof_comments": 1,
    "plain_proofs": 1,
    "exercise_hints": 1,
    "source_math_surfaces": 414,
    "target_math_surfaces": 416,
}

EXPECTED_LABELS = (
    "spectrum",
    "000521",
    "000524",
    "000526",
    "000532",
    "000533",
    "000533a",
    "000534",
    "000535",
    "0005712",
    "000575",
    "C035854",
    "prop_Neumann_series",
    "cor_Neumann_series",
    "cor2_Neumann_series",
    "000644fa",
    "000646fa",
    "000661",
    "C073131",
    "C073134",
    "C073141",
    "C073147",
    "0006703fa",
    "C073154",
    "0006703",
    "C073157",
    "SMThm",
    "defn_similar_Hsp_ops",
)

EXPECTED_REFERENCES = (
    ("ref", "spectrum"),
    ("ref", "C073131"),
    ("ref", "C073134"),
    ("ref", "000521"),
    ("ref", "000526"),
    ("ref", "C023414"),
    ("ref", "C073131"),
    ("ref", "C073134"),
    ("ref", "C073141"),
    ("ref", "C037821"),
    ("ref", "000319"),
    ("ref", "prop_Neumann_series"),
    ("ref", "defn_similar_vs_ops"),
    ("ref", "prop_nasc_op_invert"),
    ("ref", "C063526"),
    ("ref", "C063527"),
)

EXPECTED_CITATIONS = ("Erdman:2007", "Rudin:1987", "Conway:1990")

EXPECTED_TARGET_DEFINED_TERMS = (
    "invertibel kiri",
    "invers kiri",
    "invertibel kanan",
    "invers\nkanan",
    "invertibel",
    "spektrum",
    "idempoten",
    "homomorfisme (aljabar Banach)",
    "jumlah langsung",
    "Pemetaan resolven",
    "analitik",
    "entire",
    "radius spektral",
    "himpunan resolven",
    "spektrum titik",
    "nilai eigen",
    "spektrum titik aproksimatif",
    "spektrum kompresi",
    "spektrum residual",
    "serupa",
)

EXPECTED_PROOF_ROLES = (
    "hint",
    "plain",
    "hint",
    "hint",
    "hint",
    "hint",
    "hint",
    "hint",
    "hint",
    "hint",
    "comment",
    "hint",
    "hint",
    "hint",
)

EXPECTED_EXERCISE_PROOF_SEQUENCE = (
    "proof:hint",
    "proof:plain",
    "proof:hint",
    "proof:hint",
    "exercise",
    "proof:hint",
    "proof:hint",
    "proof:hint",
    "proof:hint",
    "proof:hint",
    "proof:hint",
    "proof:comment",
    "proof:hint",
    "proof:hint",
    "exercise",
    "proof:hint",
)

# SHA-256 values below hash compact UTF-8 JSON arrays.  They lock exact ordered
# source and target control surfaces without embedding 73 translated index calls
# or all 416 math records in this checker.
EXPECTED_SEQUENCE_SHA256 = {
    "environment_topology": "7d217832d8b441446041532af74caf20c5e6d845fa00fe90661446b1ebd35942",
    "source_begin_shapes": "458f4910e0ecfdaafec03b97e5b35352f14f30b2cf504813fdaab6d2b7ae572c",
    "target_begin_shapes": "7d8e7a500e105a1345f3edf16aa9d1f1d9d8cc23850ba00704852878e14d82ed",
    "labels": "71dbbacdf4eb2b677af586131a692bf7132a70180a169f334c56916b4938b52a",
    "references": "fc0e25bde96aae332891d08850d5e1e0bb43ad283d6c4d5c7f891f9141f03539",
    "citations": "55f249e5229f4632822745345dc397259a08f9d23a8223f91c2bfd0e4e223e11",
    "source_indexes": "235b8dcf5516d7b5f16cbbd53cd052602c5eb9cd640d7e7042ca8e863a860f5b",
    "target_indexes": "26bdd910beb617890fcf686e2ed0b59a2c156b43435a23f1b362c60aa782a027",
    "index_operator_shapes": "ff6654465870bdcc65274de183c2296532d682d6c8e5154f3050b0e070a0dcbf",
    "source_defined_terms": "15d207193adab175ea48fbdff7be5a2a9c27cbefd7423970063baac88b30854c",
    "target_defined_terms": "90d8b5078ee60646856c3df5a73f6174d47b7a9b3bf389213c96dd537f704cff",
    "source_proof_openings": "3279057376cb78c3c97a3451c8faa6fa8c8f467a9b4fd24fe698078d8a1eb0d3",
    "target_proof_openings": "e52c1460a55e4660fdd695832d58bff2cf6bbe10add13c53544e126a2e7ab192",
    "proof_roles": "fd88cb6369440d5a30f9d239980e6d4c38b367774197f30bfd42a7271e7e3c26",
    "exercise_proof_sequence": "f338d8df11345524f2687c6b07893a1f77f0a979411835c38a281adbbc341f12",
    "source_math_records": "3f7a97d5870b946f8724a47a1b4baad42c07e517edb9ac698c604953de07a324",
    "target_math_records": "799ce89c673cc706533af74094e067423a0daaa641d05874d328fca3ac0d0b81",
    "source_math_delimiters": "79d136b70b34e01f3b27f2bb97dbd563d9797681548e4d7cc648aec6ae369f3d",
    "target_math_delimiters": "06db0da7abd427af582d5925213b5553b14ac1a7295f1bf0f31986951eb0a13f",
    "master_includes": "9c27175029f447770aee10a6fafe1b36adb1c47a5280c8f6d04a3e87bccf148c",
}

# SequenceMatcher edits over (environment name, immediate argument shape).
# This deliberately ignores translated option text; its exact source and target
# sequences are locked separately above.
EXPECTED_CONTROL_EDITS = [
    (
        "replace",
        84,
        84,
        84,
        84,
        (("thm", "mandatory"),),
        (("thm", "optional"),),
        "source correction 7: make the Spectral Mapping Theorem an optional theorem title",
    ),
]

# SequenceMatcher edits over text-aware math keys.  Fields are:
# tag, source-first, source-last, target-first, target-last,
# source delimiters, source key hashes, target delimiters, target key hashes,
# classification.  No unclassified mathematical edit is accepted.
EXPECTED_MATH_EDITS = [
    (
        "insert", 64, 63, 64, 64,
        (), (),
        ("dollar-inline",),
        ("559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd",),
        "localization reordering, paired with the identical A deletion",
    ),
    (
        "delete", 65, 65, 66, 65,
        ("dollar-inline",),
        ("559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd",),
        (), (),
        "localization reordering, paired with the identical A insertion",
    ),
    (
        "replace", 263, 263, 263, 263,
        ("dollar-inline",),
        ("1e85269c7cb38a9b68c5065636e82e7cd91802198b3f58d78c82ba95347baf9e",),
        ("dollar-inline",),
        ("fa12190e72acda477cd2b89e31ae73bf33a60772806f458db206df4ca49fb640",),
        "source correction 4: repair the mismatched opening delimiter bigr( to bigl(",
    ),
    (
        "insert", 280, 279, 280, 280,
        (), (),
        ("dollar-inline",),
        ("39cfc53306fa41ef342a5ea7e7aeefa1dc418b211b2e42b17ede70b82d6d2c40",),
        "source correction 5: define the Volterra operator on C([0,1]) explicitly",
    ),
    (
        "replace", 302, 302, 303, 304,
        ("dollar-inline",),
        ("e632b7095b0bf32c260fa4c539e9fd7b852d0de454e9be26f24d0d6f91d069d3",),
        ("dollar-inline", "dollar-inline"),
        (
            "44bd7ae60f478fae1061e11a7739f4b94d1daf917982d33b6fc8a01a63f89c21",
            "eff40d5dd1f289f730e3fe14f1b2a76e0a574984395192cd41d8bfa9ae2285a0",
        ),
        "source correction 6: bind H and T in B(H) before using T=S^*S",
    ),
    (
        "replace", 389, 389, 391, 391,
        ("dollar-inline",),
        ("a3fcee32896ef00e3d7c28198ff5f2a4b5091b1e95eca7b490d8bc9022c48961",),
        ("dollar-inline",),
        ("451e6e653d28c123ad903a7c5e5e8e52d795a8487b1ea40ea13141291ca81bf2",),
        "source correction 8: define A as the set of diagonal entries",
    ),
]

CORRECTION_TARGET_ANCHORS = (
    (
        1,
        17,
        "kanan} dari~$a$) sedemikian sehingga",
        ("kanan} dari~$a$)sedemikian sehingga",),
        "restore the missing word boundary",
    ),
    (
        2,
        179,
        "tak nol $\\lambda$ termasuk dalam spektrum $a$",
        ("suatu bilangan kompleks\n$\\lambda$ termasuk dalam spektrum",),
        "restrict the reciprocal equivalence to nonzero lambda",
    ),
    (
        3,
        348,
        "proposisi sebelumnya~\\ref{C073134} untuk menunjukkan",
        ("\\ref{C073134})",),
        "remove the stray closing parenthesis",
    ),
    (
        4,
        372,
        "$\\rho(a^n) = \\bigl(\\rho(a)\\bigr)^n$",
        ("$\\rho(a^n) = \\bigr(\\rho(a)\\bigr)^n$",),
        "repair the mismatched scalable delimiter",
    ),
    (
        5,
        399,
        "$Vf(x)=\\int_0^x f(t)\\,dt$",
        ("operator Volterra $V$ (didefinisikan",),
        "define the Volterra operator on C([0,1])",
    ),
    (
        6,
        443,
        "Misalkan $H$ ruang Hilbert dan $T \\in \\ofml B(H)$ suatu operator swaadjoin.",
        ("Untuk suatu operator swaadjoin $T$ pada ruang Hilbert",),
        "bind the Hilbert space and operator",
    ),
    (
        7,
        509,
        "\\begin{thm}[Teorema Pemetaan Spektral]\\label{SMThm}",
        ("\\begin{thm}{Teorema Pemetaan Spektral}",),
        "make the theorem name an optional title",
    ),
    (
        8,
        547,
        "$A = \\{a_k\\colon k\\in\\N\\}$",
        ("$A = \\cup_{k=1}^\\infty a_k$", "$A = \\{a_k:k\\in\\mathbb N\\}$"),
        "define the diagonal-entry set",
    ),
)

PROSE_REFLOW_ANCHORS = (
    (
        1,
        399,
        r"acuan, pada ruang Banach~$\fml C([0,1])$ definisikan operator integral melalui rumus",
        "natural Indonesian reordering of the Volterra exercise opening",
    ),
    (
        2,
        525,
        r"Jika $T$ operator invertibel pada ruang Hilbert, maka",
        "natural Indonesian shortening without a semantic or mathematical change",
    ),
)

REQUIRED_CONTROLLED_TERMS = (
    "aljabar beridentitas",
    "invertibel kiri",
    "invertibel kanan",
    "jumlah langsung",
    "deret Neumann",
    "pemetaan resolven",
    "fungsi entire",
    "radius spektral",
    "operator Volterra",
    "himpunan resolven",
    "spektrum titik aproksimatif",
    "spektrum kompresi",
    "spektrum residual",
    "operator swaadjoin",
    "Teorema Pemetaan Spektral",
    "operator pergeseran unilateral",
    "operator perkalian",
)

FORBIDDEN_TERM_VARIANTS = (
    "aljabar unital",
    "inversibel",
    "left inverse",
    "right inverse",
    "resolvent",
    "spectral radius",
    "point spectrum",
    "approximate point spectrum",
    "compression spectrum",
    "self-adjoint",
    "swa-adjoin",
    "adjoin-diri",
    "similar operators",
    "multiplication operator",
    "unilateral shift operator",
)

EXTRA_RESIDUE_RE = re.compile(
    r"\b(?:spectrum|spectra|spectral|resolvent|invertible|unital|idempotent|"
    r"homomorphism|commutative|coproduct|eigenvalue|self-adjoint|"
    r"similarity|neighborhood|multiplication|compression)\b",
    re.IGNORECASE,
)

PRIVATE_RESIDUE = (
    "c:\\users",
    "c:/users",
    "/users/",
    "codex://",
    "file://",
    "github tokens",
    "zenodo token",
    "obsidian notes",
    "\\appdata\\",
)

LEDGER_BLOCK_SHA256 = "bb76200eee25a2a5e8305f7e62570ae4eab4a50c3785a11c78cdc4a4007c409c"

EXPECTED_MASTER_INCLUDES = (
    "linalg-id",
    "categories-id",
    "normlinspaces-id",
    "Hilbert_spaces-id",
    "Hilbert_space_operators-id",
    "Banach_spaces-id",
    "compact_operators-id",
    "spectrum-id",
)


def sequence_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def split_at_endinput(data: bytes) -> tuple[bytes, bytes]:
    token = b"\\endinput"
    if data.count(token) != 1:
        raise ValueError(f"expected one endinput token, got {data.count(token)}")
    end = data.index(token) + len(token)
    return data[:end], data[end:]


def key_sha(item: dict) -> str:
    key = ch03_math.math_key(item["normalized"])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def math_records(math: list[dict]) -> list[tuple[str, str]]:
    return [(item["delimiter"], key_sha(item)) for item in math]


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


def begin_shape_sequence(text: str) -> list[tuple[str, str]]:
    active = common.shared.active_same_length(text)
    output: list[tuple[str, str]] = []
    for match in re.finditer(r"\\begin\{([^{}]+)\}", active):
        cursor = match.end()
        shape = "plain"
        if cursor < len(active) and active[cursor] == "[":
            shape = "optional"
        elif cursor < len(active) and active[cursor] == "{":
            shape = "mandatory"
        output.append((match.group(1), shape))
    return output


def control_edit_signature(source: list[tuple[str, str]], target: list[tuple[str, str]]) -> list[tuple]:
    output: list[tuple] = []
    matcher = SequenceMatcher(None, source, target, autojunk=False)
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
                tuple(source[i1:i2]),
                tuple(target[j1:j2]),
            )
        )
    return output


def proof_opening_sequence(text: str) -> list[str]:
    active = common.shared.active_same_length(text)
    pattern = re.compile(r"\\begin\{proof\}(?:\[[^\]]*\])?")
    return [match.group(0) for match in pattern.finditer(active)]


def proof_roles(text: str, language: str) -> list[str]:
    hint = "Hint for proof" if language == "source" else "Petunjuk untuk bukti"
    comment = "Comment on proof" if language == "source" else "Komentar tentang bukti"
    roles: list[str] = []
    for opening in proof_opening_sequence(text):
        if opening == r"\begin{proof}":
            roles.append("plain")
        elif hint in opening:
            roles.append("hint")
        elif comment in opening:
            roles.append("comment")
        else:
            roles.append("unknown")
    return roles


def exercise_proof_sequence(text: str, language: str) -> list[str]:
    active = common.shared.active_same_length(text)
    roles = iter(proof_roles(text, language))
    output: list[str] = []
    for match in re.finditer(r"\\begin\{(proof|exer)\}", active):
        if match.group(1) == "exer":
            output.append("exercise")
        else:
            output.append("proof:" + next(roles))
    return output


def future_reference_sequence(text: str) -> list[tuple[str, str]]:
    active = common.shared.active_same_length(text)
    return [
        (match.group(1), match.group(2))
        for match in re.finditer(r"\\futurexref\{([^{}]+)\}\{([^{}]+)\}", active)
    ]


def environment_begin_counts(sequence: list[tuple[str, str]]) -> dict[str, int]:
    return dict(sorted(Counter(name for kind, name in sequence if kind == "begin").items()))


def chapter_eight_ledger_block(text: str) -> str:
    match = re.search(r"(?ms)^## Chapter 8\s*$\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def line_of_fragment(text: str, fragment: str) -> int:
    offset = text.find(fragment)
    return -1 if offset < 0 else text.count("\n", 0, offset) + 1


def visible_english_residue(target: str, target_math: list[dict]) -> list[dict]:
    findings = common.visible_residue(target, target_math)
    visible = common.blank_spans(
        common.shared.active_same_length(target),
        [(item["start"], item["end"]) for item in target_math]
        + [
            (item["start"], item["end"])
            for name in ("label", "ref", "eqref", "cite", "futurexref")
            for item in common.macro(target, name)
        ],
    )
    visible = re.sub(r"\\(?:begin|end)\{[^{}]+\}", " ", visible)
    visible = re.sub(r"\\[A-Za-z@]+\*?", " ", visible)
    for line_no, line in enumerate(visible.splitlines(), 1):
        words = sorted({match.group(0) for match in EXTRA_RESIDUE_RE.finditer(line)})
        if words:
            findings.append({"line": line_no, "words": words, "text": line.strip()})
    return findings


def math_edit_report(
    signatures: list[tuple],
    source_math: list[dict],
    target_math: list[dict],
    source: str,
    target: str,
) -> list[dict]:
    classifications = {item[:-1]: item[-1] for item in EXPECTED_MATH_EDITS}
    output: list[dict] = []
    for signature in signatures:
        source_first, source_last = signature[1], signature[2]
        target_first, target_last = signature[3], signature[4]
        source_slice = source_math[source_first - 1 : source_last]
        target_slice = target_math[target_first - 1 : target_last]
        output.append(
            {
                "tag": signature[0],
                "source_ordinals": [source_first, source_last],
                "target_ordinals": [target_first, target_last],
                "source_surfaces": [source[item["start"] : item["end"]] for item in source_slice],
                "target_surfaces": [target[item["start"] : item["end"]] for item in target_slice],
                "source_key_sha256": list(signature[6]),
                "target_key_sha256": list(signature[8]),
                "classification": classifications.get(signature, "UNCLASSIFIED"),
            }
        )
    return output


def main() -> int:
    errors: list[str] = []

    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    master_bytes = MASTER.read_bytes()

    try:
        source_active_bytes, source_tail = split_at_endinput(source_bytes)
    except ValueError as exc:
        errors.append(f"source endinput boundary: {exc}")
        source_active_bytes, source_tail = source_bytes, b""
    try:
        target_active_bytes, target_tail = split_at_endinput(target_bytes)
    except ValueError as exc:
        errors.append(f"target endinput boundary: {exc}")
        target_active_bytes, target_tail = target_bytes, b""

    source_identity = (
        len(source_bytes), common.line_count(source_bytes), common.sha256(source_bytes)
    )
    target_identity = (
        len(target_bytes), common.line_count(target_bytes), common.sha256(target_bytes)
    )
    master_identity = (
        len(master_bytes), common.line_count(master_bytes), common.sha256(master_bytes)
    )
    if source_identity != (SOURCE_BYTES, SOURCE_LINES, SOURCE_SHA256):
        errors.append(f"source identity mismatch: {source_identity!r}")
    if target_identity != (TARGET_BYTES, TARGET_LINES, TARGET_SHA256):
        errors.append(f"target identity mismatch: {target_identity!r}")
    if master_identity != (MASTER_BYTES, MASTER_LINES, MASTER_SHA256):
        errors.append(f"master identity mismatch: {master_identity!r}")

    source_active_identity = (
        len(source_active_bytes),
        common.line_count(source_active_bytes),
        common.sha256(source_active_bytes),
    )
    target_active_identity = (
        len(target_active_bytes),
        common.line_count(target_active_bytes),
        common.sha256(target_active_bytes),
    )
    if source_active_identity != (
        SOURCE_ACTIVE_BYTES, SOURCE_ACTIVE_LINES, SOURCE_ACTIVE_SHA256
    ):
        errors.append(f"source active identity mismatch: {source_active_identity!r}")
    if target_active_identity != (
        TARGET_ACTIVE_BYTES, TARGET_LINES, TARGET_ACTIVE_SHA256
    ):
        errors.append(f"target active identity mismatch: {target_active_identity!r}")
    if source_tail != b"\r\n" * 9 or common.sha256(source_tail) != SOURCE_TAIL_SHA256:
        errors.append("source inactive tail is not the frozen nine-CRLF suffix")
    if target_tail != b"\n":
        errors.append("target must have only one LF after terminal endinput")

    if (
        source_bytes.startswith(b"\xef\xbb\xbf")
        or source_bytes.count(b"\r\n") != SOURCE_LINES
        or source_bytes.count(b"\n") != SOURCE_LINES
        or source_bytes.count(b"\r") != SOURCE_LINES
        or not source_bytes.endswith(b"\r\n")
    ):
        errors.append("source must retain the frozen BOM-free 611-line CRLF form")
    if (
        target_bytes.startswith(b"\xef\xbb\xbf")
        or b"\r" in target_bytes
        or target_bytes.count(b"\n") != TARGET_LINES
        or not target_bytes.endswith(b"\n")
    ):
        errors.append("target must be BOM-free UTF-8 with 603 LF-terminated lines")
    if (
        master_bytes.startswith(b"\xef\xbb\xbf")
        or b"\r" in master_bytes
        or master_bytes.count(b"\n") != MASTER_LINES
        or not master_bytes.endswith(b"\n")
    ):
        errors.append("master must be BOM-free UTF-8 with 334 LF-terminated lines")

    source = source_active_bytes.decode("ascii")
    target = target_active_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")

    chapter, sections = common.chapter_and_sections(target)
    if chapter != EXPECTED_CHAPTER_TITLE or sections != EXPECTED_SECTION_TITLES:
        errors.append(f"chapter/section titles differ: {chapter!r}, {sections!r}")

    source_env = common.env_sequence(source)
    target_env = common.env_sequence(target)
    if source_env != target_env:
        errors.append("ordered begin/end environment topology differs")
    if sequence_sha256(source_env) != EXPECTED_SEQUENCE_SHA256["environment_topology"]:
        errors.append("source environment sequence digest differs")
    if sequence_sha256(target_env) != EXPECTED_SEQUENCE_SHA256["environment_topology"]:
        errors.append("target environment sequence digest differs")
    pairs = len(target_env) // 2
    if pairs != EXPECTED_COUNTS["environment_pairs"]:
        errors.append(f"environment pair count {pairs}")
    begin_counts = environment_begin_counts(target_env)
    if begin_counts != EXPECTED_ENVIRONMENT_BEGIN_COUNTS:
        errors.append(f"environment opening census differs: {begin_counts!r}")

    source_shapes = begin_shape_sequence(source)
    target_shapes = begin_shape_sequence(target)
    if sequence_sha256(source_shapes) != EXPECTED_SEQUENCE_SHA256["source_begin_shapes"]:
        errors.append("source begin-control shape sequence differs")
    if sequence_sha256(target_shapes) != EXPECTED_SEQUENCE_SHA256["target_begin_shapes"]:
        errors.append("target begin-control shape sequence differs")
    control_edits = control_edit_signature(source_shapes, target_shapes)
    if control_edits != [item[:-1] for item in EXPECTED_CONTROL_EDITS]:
        errors.append(f"control edit lock differs: {control_edits!r}")

    source_labels = common.command_arguments(source, "label")
    target_labels = common.command_arguments(target, "label")
    if tuple(source_labels) != EXPECTED_LABELS or tuple(target_labels) != EXPECTED_LABELS:
        errors.append("ordered label sequence differs")
    if sequence_sha256(target_labels) != EXPECTED_SEQUENCE_SHA256["labels"]:
        errors.append("label sequence digest differs")

    source_refs = [(kind, value) for _, kind, value in common.reference_sequence(source)]
    target_refs = [(kind, value) for _, kind, value in common.reference_sequence(target)]
    if tuple(source_refs) != EXPECTED_REFERENCES or tuple(target_refs) != EXPECTED_REFERENCES:
        errors.append("ordered ref/eqref/futurexref endpoint sequence differs")
    if sequence_sha256(target_refs) != EXPECTED_SEQUENCE_SHA256["references"]:
        errors.append("reference sequence digest differs")
    future_refs = future_reference_sequence(target)
    ordinary_refs = common.command_arguments(target, "ref")
    equation_refs = common.command_arguments(target, "eqref")
    if (
        len(ordinary_refs) != EXPECTED_COUNTS["references"]
        or len(equation_refs) != EXPECTED_COUNTS["equation_references"]
        or len(future_refs) != EXPECTED_COUNTS["future_references"]
    ):
        errors.append(
            "reference census differs: "
            f"ordinary/eqref/future={len(ordinary_refs)}/{len(equation_refs)}/{len(future_refs)}"
        )

    source_cites = common.command_arguments(source, "cite")
    target_cites = common.command_arguments(target, "cite")
    if tuple(source_cites) != EXPECTED_CITATIONS or tuple(target_cites) != EXPECTED_CITATIONS:
        errors.append("ordered citation sequence differs")
    if sequence_sha256(target_cites) != EXPECTED_SEQUENCE_SHA256["citations"]:
        errors.append("citation sequence digest differs")

    source_index = common.command_arguments(source, "index")
    target_index = common.command_arguments(target, "index")
    source_index_shapes = [common.index_signature(item) for item in source_index]
    target_index_shapes = [common.index_signature(item) for item in target_index]
    if len(source_index) != EXPECTED_COUNTS["indexes"] or len(target_index) != EXPECTED_COUNTS["indexes"]:
        errors.append(f"index count source/target {len(source_index)}/{len(target_index)}")
    if source_index_shapes != target_index_shapes:
        errors.append("ordered MakeIndex operator-shape sequence differs")
    for name, sequence in (
        ("source_indexes", source_index),
        ("target_indexes", target_index),
        ("index_operator_shapes", target_index_shapes),
    ):
        if sequence_sha256(sequence) != EXPECTED_SEQUENCE_SHA256[name]:
            errors.append(f"{name.replace('_', ' ')} sequence digest differs")

    source_df = common.command_arguments(source, "df")
    target_df = common.command_arguments(target, "df")
    if len(source_df) != EXPECTED_COUNTS["defined_terms"]:
        errors.append(f"source defined-term count {len(source_df)}")
    if tuple(target_df) != EXPECTED_TARGET_DEFINED_TERMS:
        errors.append(f"ordered target defined-term sequence differs: {target_df!r}")
    if sequence_sha256(source_df) != EXPECTED_SEQUENCE_SHA256["source_defined_terms"]:
        errors.append("source defined-term sequence digest differs")
    if sequence_sha256(target_df) != EXPECTED_SEQUENCE_SHA256["target_defined_terms"]:
        errors.append("target defined-term sequence digest differs")

    source_proof_openings = proof_opening_sequence(source)
    target_proof_openings = proof_opening_sequence(target)
    source_roles = proof_roles(source, "source")
    target_roles = proof_roles(target, "target")
    source_events = exercise_proof_sequence(source, "source")
    target_events = exercise_proof_sequence(target, "target")
    if tuple(source_roles) != EXPECTED_PROOF_ROLES or tuple(target_roles) != EXPECTED_PROOF_ROLES:
        errors.append(f"ordered proof/hint roles differ: {source_roles!r}, {target_roles!r}")
    if (
        tuple(source_events) != EXPECTED_EXERCISE_PROOF_SEQUENCE
        or tuple(target_events) != EXPECTED_EXERCISE_PROOF_SEQUENCE
    ):
        errors.append("ordered exercise/proof/hint sequence differs")
    for name, sequence in (
        ("source_proof_openings", source_proof_openings),
        ("target_proof_openings", target_proof_openings),
        ("proof_roles", target_roles),
        ("exercise_proof_sequence", target_events),
    ):
        if sequence_sha256(sequence) != EXPECTED_SEQUENCE_SHA256[name]:
            errors.append(f"{name.replace('_', ' ')} digest differs")
    if source.count(r"\emph{Hint.}") != 1 or target.count(r"\emph{Petunjuk.}") != 1:
        errors.append("inline exercise-hint sequence differs")

    target_exercises = Counter(target_events)["exercise"]
    target_proofs = len(target_roles)
    role_counts = Counter(target_roles)
    if (
        target_exercises != EXPECTED_COUNTS["exercises"]
        or target_proofs != EXPECTED_COUNTS["proofs"]
        or role_counts["hint"] != EXPECTED_COUNTS["proof_hints"]
        or role_counts["comment"] != EXPECTED_COUNTS["proof_comments"]
        or role_counts["plain"] != EXPECTED_COUNTS["plain_proofs"]
    ):
        errors.append(
            "exercise/proof/hint census differs: "
            f"exercise={target_exercises}, proof={target_proofs}, roles={dict(role_counts)!r}"
        )

    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (
        EXPECTED_COUNTS["source_math_surfaces"],
        EXPECTED_COUNTS["target_math_surfaces"],
    ):
        errors.append(f"math count source/target {len(source_math)}/{len(target_math)}")
    source_delimiters = [item["delimiter"] for item in source_math]
    target_delimiters = [item["delimiter"] for item in target_math]
    for name, sequence in (
        ("source_math_records", math_records(source_math)),
        ("target_math_records", math_records(target_math)),
        ("source_math_delimiters", source_delimiters),
        ("target_math_delimiters", target_delimiters),
    ):
        if sequence_sha256(sequence) != EXPECTED_SEQUENCE_SHA256[name]:
            errors.append(f"{name.replace('_', ' ')} digest differs")
    math_edits = math_edit_signature(source_math, target_math)
    if math_edits != [item[:-1] for item in EXPECTED_MATH_EDITS]:
        errors.append(f"math edit lock differs: {math_edits!r}")

    correction_results: list[dict] = []
    for number, expected_line, required, forbidden, classification in CORRECTION_TARGET_ANCHORS:
        occurrences = target.count(required)
        actual_line = line_of_fragment(target, required)
        correction_results.append(
            {
                "number": number,
                "target_line": actual_line,
                "classification": classification,
            }
        )
        if occurrences != 1 or actual_line != expected_line:
            errors.append(
                f"correction {number} target anchor differs: occurrences={occurrences}, line={actual_line}"
            )
        for fragment in forbidden:
            if fragment.lower() in target.lower():
                errors.append(f"correction {number} source-defect residue present: {fragment}")

    prose_reflow_results: list[dict] = []
    for number, expected_line, required, classification in PROSE_REFLOW_ANCHORS:
        occurrences = target.count(required)
        actual_line = line_of_fragment(target, required)
        prose_reflow_results.append(
            {
                "number": number,
                "target_line": actual_line,
                "classification": classification,
            }
        )
        if occurrences != 1 or actual_line != expected_line:
            errors.append(
                f"prose reflow {number} differs: occurrences={occurrences}, line={actual_line}"
            )
    source_allowbreak = source.count(r"\allowbreak")
    target_allowbreak = target.count(r"\allowbreak")
    if source_allowbreak != 0 or target_allowbreak != 0:
        errors.append(
            "allowbreak census differs: "
            f"source/target={source_allowbreak}/{target_allowbreak}"
        )

    for term in REQUIRED_CONTROLLED_TERMS:
        if term.lower() not in target.lower():
            errors.append(f"controlled term absent: {term}")
    for term in FORBIDDEN_TERM_VARIANTS:
        if term.lower() in target.lower():
            errors.append(f"forbidden terminology variant present: {term}")

    residue = visible_english_residue(target, target_math)
    if residue:
        errors.append(f"visible English residue: {residue!r}")
    for marker in ("\ufffd", "Ã", "Â", "â€", "ðŸ", "ï»¿"):
        if marker in target:
            errors.append(f"mojibake marker present: {marker!r}")
    for marker in PRIVATE_RESIDUE:
        if marker in common.shared.active_same_length(target).lower():
            errors.append(f"active private-path residue present: {marker}")

    ledger = CORRECTIONS.read_text(encoding="utf-8")
    ledger_block = chapter_eight_ledger_block(ledger)
    if not ledger_block:
        errors.append("Chapter 8 correction-ledger block absent")
    else:
        if hashlib.sha256(ledger_block.encode("utf-8")).hexdigest() != LEDGER_BLOCK_SHA256:
            errors.append("Chapter 8 correction-ledger block digest differs")
        ledger_numbers = re.findall(r"(?m)^(\d+)\. `spectrum\.tex:", ledger_block)
        if ledger_numbers != [str(number) for number in range(1, 9)]:
            errors.append(f"Chapter 8 correction numbering differs: {ledger_numbers!r}")
        required_ledger_fragments = (
            "spectrum.tex:17",
            "spectrum.tex:178--181",
            "spectrum.tex:348",
            "spectrum.tex:372",
            "spectrum.tex:396--412",
            "spectrum.tex:443--450",
            "spectrum.tex:509",
            "spectrum.tex:547",
            "same displayed formula used in Example `000319`",
            "Hilbert space `H`",
            "*Teorema Pemetaan Spektral*",
            r"\begin{thm}[...]",
            r"A=\{a_k\colon k\in\N\}",
            "No upstream contact occurs during production.",
        )
        for fragment in required_ledger_fragments:
            if fragment not in ledger_block:
                errors.append(f"Chapter 8 correction-ledger item absent: {fragment}")

    required_rights = (
        "Karya sumber John M. Erdman ini berlisensi Creative Commons",
        "Attribution--ShareAlike 4.0 International (CC BY-SA 4.0):",
        r"\url{https://creativecommons.org/licenses/by-sa/4.0/}.",
        "Terjemahan Bahasa Indonesia dan adaptasi teknis ini juga diterbitkan dengan",
        "lisensi CC BY-SA 4.0.",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University.",
        r"\input{DIAGXY.TEX}",
        r"\include{spectrum-id}",
        "Epigraf pihak ketiga, gambar lencana lisensi, dan makro tabel yang",
        "status komponennya tidak cukup jelas tidak digunakan.",
    )
    for fragment in required_rights:
        if fragment not in master:
            errors.append(f"cumulative-reader rights closure absent: {fragment}")
    master_includes = common.command_arguments(master, "include")
    if tuple(master_includes) != EXPECTED_MASTER_INCLUDES:
        errors.append(f"cumulative-reader include sequence differs: {master_includes!r}")
    if sequence_sha256(master_includes) != EXPECTED_SEQUENCE_SHA256["master_includes"]:
        errors.append("cumulative-reader include sequence digest differs")
    for fragment in (r"\input{TABLE.TEX}", "by-sa.eps", "by-sa.pdf"):
        if fragment.lower() in master.lower():
            errors.append(f"excluded component is active in cumulative reader: {fragment}")
    for marker in PRIVATE_RESIDUE:
        if marker in common.shared.active_same_length(master).lower():
            errors.append(f"active private-path residue present in wrapper: {marker}")

    sequence_locks = {
        "environment_topology": sequence_sha256(target_env),
        "source_begin_shapes": sequence_sha256(source_shapes),
        "target_begin_shapes": sequence_sha256(target_shapes),
        "labels": sequence_sha256(target_labels),
        "references": sequence_sha256(target_refs),
        "citations": sequence_sha256(target_cites),
        "source_indexes": sequence_sha256(source_index),
        "target_indexes": sequence_sha256(target_index),
        "index_operator_shapes": sequence_sha256(target_index_shapes),
        "source_defined_terms": sequence_sha256(source_df),
        "target_defined_terms": sequence_sha256(target_df),
        "source_proof_openings": sequence_sha256(source_proof_openings),
        "target_proof_openings": sequence_sha256(target_proof_openings),
        "proof_roles": sequence_sha256(target_roles),
        "exercise_proof_sequence": sequence_sha256(target_events),
        "source_math_records": sequence_sha256(math_records(source_math)),
        "target_math_records": sequence_sha256(math_records(target_math)),
        "source_math_delimiters": sequence_sha256(source_delimiters),
        "target_math_delimiters": sequence_sha256(target_delimiters),
        "master_includes": sequence_sha256(master_includes),
    }

    result = {
        "result": "pass" if not errors else "fail",
        "source": {
            "bytes": len(source_bytes),
            "lines": common.line_count(source_bytes),
            "line_endings": "CRLF",
            "sha256": common.sha256(source_bytes),
            "active_through_endinput": {
                "bytes": len(source_active_bytes),
                "lines": common.line_count(source_active_bytes),
                "sha256": common.sha256(source_active_bytes),
            },
        },
        "target": {
            "bytes": len(target_bytes),
            "lines": common.line_count(target_bytes),
            "line_endings": "LF",
            "sha256": common.sha256(target_bytes),
            "active_through_endinput": {
                "bytes": len(target_active_bytes),
                "lines": common.line_count(target_active_bytes),
                "sha256": common.sha256(target_active_bytes),
            },
        },
        "master": {
            "bytes": len(master_bytes),
            "lines": common.line_count(master_bytes),
            "line_endings": "LF",
            "sha256": common.sha256(master_bytes),
        },
        "counts": {
            "environment_pairs": pairs,
            "environment_openings": begin_counts,
            "labels": len(target_labels),
            "ordinary_references": len(ordinary_refs),
            "equation_references": len(equation_refs),
            "future_references": len(future_refs),
            "citations": len(target_cites),
            "indexes": len(target_index),
            "defined_terms": len(target_df),
            "exercises": target_exercises,
            "proofs": target_proofs,
            "proof_hints": role_counts["hint"],
            "proof_comments": role_counts["comment"],
            "plain_proofs": role_counts["plain"],
            "exercise_hints": target.count(r"\emph{Petunjuk.}"),
            "source_math_surfaces": len(source_math),
            "target_math_surfaces": len(target_math),
            "source_math_delimiters": dict(sorted(Counter(source_delimiters).items())),
            "target_math_delimiters": dict(sorted(Counter(target_delimiters).items())),
            "classified_math_edit_blocks": len(math_edits),
            "classified_control_edit_blocks": len(control_edits),
            "classified_prose_reflows": len(prose_reflow_results),
            "documented_source_corrections": len(correction_results),
            "visible_english_residue": len(residue),
        },
        "sequence_sha256": sequence_locks,
        "classified_math_edits": math_edit_report(
            math_edits, source_math, target_math, source, target
        ),
        "classified_control_edits": [
            {
                "signature": list(signature),
                "classification": expected[-1],
            }
            for signature, expected in zip(control_edits, EXPECTED_CONTROL_EDITS)
        ],
        "classified_prose_reflows": prose_reflow_results,
        "documented_source_corrections": correction_results,
        "correction_ledger": {
            "path": str(CORRECTIONS.relative_to(ROOT)),
            "chapter_8_block_sha256": (
                hashlib.sha256(ledger_block.encode("utf-8")).hexdigest()
                if ledger_block
                else None
            ),
        },
        "rights_wrapper_checked": str(MASTER.relative_to(ROOT)),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
