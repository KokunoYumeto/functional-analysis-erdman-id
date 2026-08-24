#!/usr/bin/env python3
"""Generate the deterministic Chapter 17 source-correction ledger."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "upstream" / "K0_functor.tex"
TARGET = ROOT / "source" / "id-ID" / "K0_functor-id.tex"
OUTPUT = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH17.json"
SOURCE_SHA256 = "e8ebcaa4e5dbc1cc9b907edb235465610f3bd61e0bfa1ce2f1b5b26e9abf8c6a"
TARGET_SHA256 = "061ffd28907e2251fc8b01077888de3e11b3bce67fec1ba52b080c924a241059"


SPECS = (
    (1, 12, 12, "MECHANICAL_PROSE_SOURCE_REPAIR", "remove the extra source verb in the intended invitation to let stabilized projections roam", ["to be roam about"], ["untuk menjelajah"], ["menjelajahi dunia matriks"], False),
    (2, 13, 19, "MATHEMATICAL_STATUS_CLARIFICATION", "retain the motivational stabilization display but identify it as heuristic rather than a proved multiplicative congruence", ["Then the problem is solved"], ["maka masalah itu terbukti selesai"], ["motivasi heuristik saja"], False),
    (3, 42, 46, "MECHANICAL_PROSE_SOURCE_REPAIR", "repair the source article while translating the unitary-equivalence definition", ["an unitary element"], ["sebuah suatu elemen uniter"], ["suatu elemen uniter"], False),
    (4, 63, 67, "MECHANICAL_PROSE_SOURCE_REPAIR", "repair the malformed every-then quantifier construction without changing its scope", ["For every invertible element", "then there exists"], ["untuk setiap elemen invertibel, maka"], ["terdapat suatu elemen uniter"], False),
    (5, 101, 103, "MATHEMATICAL_TYPE_SOURCE_REPAIR", "give the operator-valued exponential path its correct codomain in the unitary group of A", [r"\sto \T\colon t \mapsto \exp(ith)"], [r"\sto \T\colon t \mapsto \exp(ith)"], [r"\sto \ofml U(A)\colon t \mapsto \exp(ith)"], True),
    (6, 367, 369, "MATHEMATICAL_EQUALITY_SOURCE_REPAIR", "state that block sum is strictly associative and commutative only up to Murray--von Neumann equivalence on projections", ["commutative semigroup under the operation"], ["semigrup komutatif di bawah operasi"], ["asosiatif secara ketat dan komutatif hanya hingga ekuivalensi Murray--von Neumann"], False),
    (7, 390, 392, "MATHEMATICAL_CATEGORY_SOURCE_REPAIR", "identify D(C) as the additive semigroup of nonnegative integers, not a group of positive integers", ["additive group of positive integers"], ["grup aditif bilangan bulat positif"], ["semigrup aditif bilangan bulat tak negatif"], False),
    (8, 397, 401, "FORMAL_SCOPE_CLARIFICATION", "restrict the single-infinity projection-semigroup description to separable infinite-dimensional Hilbert space", ["If $H$ is a Hilbert space"], ["Jika $H$ suatu ruang Hilbert, maka"], ["ruang Hilbert terpisahkan berdimensi tak hingga"], False),
    (9, 446, 450, "MECHANICAL_PROSE_SOURCE_REPAIR", "translate the intended phrase will be denoted by", ["will be denote by"], ["akan dinotasi oleh akan"], ["akan dinotasikan dengan"], False),
    (10, 458, 460, "MECHANICAL_PROSE_SOURCE_REPAIR", "repair the source article in becomes an Abelian group", ["becomes and Abelian group"], ["menjadi dan grup Abelian"], ["menjadi grup Abelian"], False),
    (11, 543, 549, "MECHANICAL_CATEGORY_PROSE_REPAIR", "use the plural group homomorphisms for the image category", ["to group homomorphism"], ["ke homomorfisme grup merupakan"], ["homomorfisme-homomorfisme grup"], False),
    (12, 655, 657, "MATHEMATICAL_CATEGORY_SOURCE_REPAIR", "call the restriction to projection families a map rather than a star-homomorphism", [r"to a $*\,$-homomorphism $\phi$ from $\fml P_\infty(A)$"], [r"homomorfisme-$*\,$ $\phi$ dari $\fml P_\infty(A)$"], [r"memiliki pembatasan berupa pemetaan $\phi$ dari $\fml P_\infty(A)$"], False),
    (13, 741, 752, "MAP_IDENTITY_SOURCE_REPAIR", "use the newly defined section psi-prime in the final splitting identity", [r"Q \circ \psi = \id{\C}"], [r"Q \circ \psi = \id{\C}"], [r"Q \circ \psi' = \id{\C}"], True),
    (14, 793, 850, "IDENTIFIER_ALIAS_SOURCE_REPAIR", "bind pi to Q and lambda to psi so the nonunital quotient and scalar-section notation is closed", [r"K_0(A) = \ker(K_0(\pi))", r"Let $\pi$ and $\lambda$ be"], [r"Misalkan $\pi$ dan $\lambda$ adalah"], [r"\pi:=Q", r"\lambda:=\psi"], True),
    (15, 814, 822, "MATHEMATICAL_CATEGORY_SOURCE_REPAIR", "call K_0(phi) a group homomorphism between Abelian groups", [r"unique $*\,$-homomorphism"], [r"homomorfisme-$*\,$ tunggal"], ["homomorfisme grup tunggal"], False),
    (16, 847, 850, "MECHANICAL_PROSE_SOURCE_REPAIR", "repair the malformed phrase unitization of a C-star-algebra", ["unitization of as $C^*$-algebra"], ["unitalisasi dari sebagai aljabar"], ["unitalisasi suatu aljabar-$C^*$"], False),
    (17, 860, 866, "MATHEMATICAL_NOTATION_SOURCE_REPAIR", "remove the unused q variable from the standard-picture set builder", [r"p,q \in \fml P_\infty(\wt A)"], [r"p,q \in \fml P_\infty(\wt A)"], [r"p \in \fml P_\infty(\wt A)"], True),
    (18, 930, 934, "FORMAL_SCOPE_CLARIFICATION", "require infinite-dimensional H in the Calkin exact-sequence counterexample", ["If $H$ is a Hilbert space the exact sequence"], ["Jika $H$ ruang Hilbert, barisan eksak"], ["ruang Hilbert berdimensi tak hingga"], False),
    (19, 1032, 1036, "MATHEMATICAL_TOPOLOGY_SOURCE_REPAIR", "take the norm closure of the increasing union in the C-star inductive limit", [r"B = \bigcup_{n=1}^\infty A_n"], [r"B = \bigcup_{n=1}^\infty A_n"], [r"\clo{\bigcup_{n=1}^\infty A_n}"], True),
    (20, 1038, 1042, "FORMAL_SCOPE_CLARIFICATION", "identify the compact-operator limit space as separable and infinite-dimensional", ["compact operators on a Hilbert space~$H$"], ["operator kompak pada ruang Hilbert~$H$"], ["ruang Hilbert terpisahkan berdimensi tak hingga~$H$"], False),
    (21, 1093, 1104, "MATHEMATICAL_CATEGORY_SOURCE_REPAIR", "classify nonzero star-homomorphisms, explicitly name the displayed map phi, and preserve that category in the following example", ["Nonzero algebra homomorphisms", r"a \mapsto u\,\diag", "An example of a homomorphism from"], ["Homomorfisme aljabar tak nol", r"\[ a \mapsto u\,\diag", "Contoh homomorfisme dari"], [r"Homomorfisme-$*\,$ tak nol", r"\phi\colon a \mapsto u\,\diag", r"Contoh homomorfisme-$*\,$ dari"], True),
    (22, 1127, 1130, "MATHEMATICAL_RANGE_SOURCE_REPAIR", "allow zero entries in the multiplicity matrix by using nonnegative integers", [r"matrix $\vc m", "of positive integers"], ["berentri bilangan bulat positif"], ["berentri bilangan bulat tak negatif"], False),
    (23, 1271, 1275, "MECHANICAL_TEX_SOURCE_REPAIR", "remove the empty textbf command while localizing the CAR expansion", [r"CAR\textbf{}-algebra"], [r"CAR\textbf{}"], ["aljabar CAR (CAR = Relasi Antikomutasi Kanonik)"], False),
    (24, 144, 145, "MATHEMATICAL_IMPLICATION_SOURCE_REPAIR", "reverse the displayed implication so it actually states the converse of the second implication in proposition 0060221", [r"converse of the second implication, $p \sim_u q \implies p \sim q$"], [r"kebalikan dari implikasi kedua, $p \sim_u q \implies p \sim q$"], [r"kebalikan dari implikasi kedua, $p \sim q \implies p \sim_u q$"], True),
    (25, 175, 177, "MATHEMATICAL_IMPLICATION_SOURCE_REPAIR", "reverse the displayed implication so it actually states the converse of the first implication in proposition 0060221", [r"converse of the first implication, $p \sim_h q \implies p \sim_u q$"], [r"Kebalikan dari implikasi pertama, $p \sim_h q \implies p \sim_u q$"], [r"Kebalikan dari implikasi pertama, $p \sim_u q \implies p \sim_h q$"], True),
    (26, 651, 652, "MATHEMATICAL_TYPE_SOURCE_REPAIR", "give tau the underlying semigroup of G as codomain because its value nu(p) lies there", [r"\tau\colon \fml D(A) \sto K_0(A)"], [r"\tau\colon \fml D(A) \sto K_0(A)"], [r"\tau\colon \fml D(A) \sto \abs G"], True),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(lines: list[str], start: int, end: int) -> str:
    selected = [line.rstrip() for line in lines[start - 1 : end] if line.strip()]
    text = unicodedata.normalize("NFC", "\n".join(selected))
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    if (len(source_bytes), source_bytes.count(b"\r\n"), sha256(source_bytes)) != (
        59_639,
        1_362,
        SOURCE_SHA256,
    ):
        raise SystemExit("Chapter 17 source identity differs")
    if (len(target_bytes), target_bytes.count(b"\n"), sha256(target_bytes)) != (
        61_673,
        1_362,
        TARGET_SHA256,
    ) or b"\r" in target_bytes:
        raise SystemExit("Chapter 17 target identity differs")
    source = source_bytes.decode("ascii").replace("\r\n", "\n")
    target = target_bytes.decode("utf-8")
    source_lines = source.splitlines()
    target_lines = target.splitlines()
    if len(source_lines) != 1_362 or len(target_lines) != 1_362:
        raise SystemExit("Chapter 17 logical-record topology differs")

    records: list[dict[str, object]] = []
    for number, start, end, classification, decision, source_anchors, forbidden, required, affects_math in SPECS:
        record_id = f"FAOA-2015-CH17-CORR-{number:03d}"
        marker = f"% SOURCE-CORRECTION: CH17-C{number:03d}"
        if target.count(marker) != 1:
            raise SystemExit(f"correction marker closure differs: {marker}")
        marker_line = target[: target.index(marker)].count("\n") + 1
        if not start <= marker_line <= end:
            raise SystemExit(f"correction marker lies outside its source span: {record_id}")
        source_snippet = normalize(source_lines, start, end)
        target_snippet = normalize(target_lines, start, end)
        for anchor in source_anchors:
            if anchor not in source_snippet:
                raise SystemExit(f"source anchor missing for {record_id}: {anchor!r}")
        for anchor in forbidden:
            if anchor in target:
                raise SystemExit(f"forbidden target anchor remains for {record_id}: {anchor!r}")
        for anchor in required:
            if anchor not in target_snippet:
                raise SystemExit(f"required target anchor missing for {record_id}: {anchor!r}")
        records.append(
            {
                "id": record_id,
                "source_lines": {"start": start, "end": end},
                "target_lines": {"start": start, "end": end},
                "classification": classification,
                "decision": decision,
                "source_normalized_snippet": source_snippet,
                "target_normalized_snippet": target_snippet,
                "source_normalized_snippet_sha256": sha256(source_snippet.encode("utf-8")),
                "target_normalized_snippet_sha256": sha256(target_snippet.encode("utf-8")),
                "source_required_anchors": source_anchors,
                "forbidden_target_anchors": forbidden,
                "required_target_anchors": required,
                "affects_math": affects_math,
                "target_marker": marker,
                "target_marker_line": marker_line,
            }
        )

    class_counts = dict(Counter(record["classification"] for record in records))
    math_ids = [record["id"] for record in records if record["affects_math"]]
    payload = {
        "schema_version": "o008.source-corrections.v1",
        "unit_id": "FAOA-2015-CH17",
        "chapter": 17,
        "status": "adjudicated_and_applied",
        "source": {
            "path": "source/upstream/K0_functor.tex",
            "bytes": len(source_bytes),
            "logical_records": 1_362,
            "line_endings": "CRLF",
            "sha256": SOURCE_SHA256,
        },
        "target": {
            "path": "source/id-ID/K0_functor-id.tex",
            "bytes": len(target_bytes),
            "logical_records": 1_362,
            "line_endings": "LF",
            "sha256": TARGET_SHA256,
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
        "math_surface_affecting_record_ids": math_ids,
        "independent_review": {
            "source_inventory": "qa/CH17_SOURCE_INVENTORY.md",
            "pretranslation_math_review": "qa/CH17_PRETRANSLATION_MATH_REVIEW.md",
            "terminology_plan": "provenance/CH17_TERMINOLOGY_PLAN.md",
            "upstream_contact": "none during production",
        },
        "records": records,
    }
    rendered = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    OUTPUT.write_bytes(rendered)
    print(
        json.dumps(
            {
                "result": "pass",
                "records": len(records),
                "class_counts": class_counts,
                "math_surface_affecting_record_ids": math_ids,
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "bytes": len(rendered),
                "sha256": sha256(rendered),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
