#!/usr/bin/env python3
"""Assemble the reviewed FAOA-2015-CH16 fragments and cumulative master."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "source" / "upstream" / "extensions.tex"
AUTHORITY_BYTES = 42_614
AUTHORITY_LF = 1_000
AUTHORITY_SHA256 = "e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318"
PARTS = (
    (
        ROOT / "qa" / "ch16_translation_part_ab.tex",
        16_831,
        402,
        "a109d0517d7625731b25ba6e7eb5d157f0341bc73b9e47f23143ca18abde8f6d",
    ),
    (
        ROOT / "qa" / "ch16_translation_part_cd.tex",
        26_971,
        596,
        "f46e4a63721ae5ad327b1032ab374e945110317cc8f7710f9ec61d425e853896",
    ),
)
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch15.tex"
SOURCE_MASTER_BYTES = 10_541
SOURCE_MASTER_LF = 344
SOURCE_MASTER_SHA256 = "f2df36c70dcca86f44687efe450ea46a5611be2d1170a9ded16dbfbfcdb73a33"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "extensions-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch16.tex"
EXPECTED_CHAPTER_BYTES = 43_804
EXPECTED_CHAPTER_SHA256 = "59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3"
EXPECTED_MASTER_BYTES = 10_679
EXPECTED_MASTER_SHA256 = "6e528b0193d3179b58e44169430d043fa5399f7c860f09d832eb3ccd954a5388"
EXPECTED_SECTIONS = (
    b"\\section{Operator Normal secara Esensial}",
    b"\\section{Operator Toeplitz}",
    b"\\section{Penjumlahan Ekstensi}",
    b"\\section{Pemetaan Positif Lengkap}",
)
EXPECTED_INCLUDES = (
    "linalg-id", "categories-id", "normlinspaces-id", "Hilbert_spaces-id",
    "Hilbert_space_operators-id", "Banach_spaces-id", "compact_operators-id",
    "spectrum-id", "topvecspaces-id", "distributions-id", "Gelfand_Naimark-id",
    "no_identity-id", "GNS_construction-id", "multiplier_algebras-id",
    "fredholm_theory-id", "extensions-id",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"master replacement count for {old!r} is not one")
    return text.replace(old, new, 1)


def macro_args(name: bytes, data: bytes) -> list[bytes]:
    return re.findall(rb"\\" + name + rb"\{([^{}]+)\}", data)


def build_chapter() -> bytes:
    authority = AUTHORITY.read_bytes()
    if (len(authority), authority.count(b"\n"), digest(authority)) != (
        AUTHORITY_BYTES, AUTHORITY_LF, AUTHORITY_SHA256
    ):
        raise SystemExit("Chapter 16 authority identity differs")
    if authority.startswith(b"\xef\xbb\xbf") or authority.count(b"\r\n") != AUTHORITY_LF:
        raise SystemExit("Chapter 16 authority encoding/record closure differs")

    payloads: list[bytes] = []
    for path, expected_bytes, expected_lf, expected_sha in PARTS:
        data = path.read_bytes()
        if (len(data), data.count(b"\n"), digest(data)) != (
            expected_bytes, expected_lf, expected_sha
        ):
            raise SystemExit(f"fragment identity mismatch: {path}")
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
            raise SystemExit(f"fragment encoding/line-ending mismatch: {path}")
        data.decode("utf-8")
        payloads.append(data)

    # Part AB contains source records 1--404; apply_patch normalizes its
    # terminal blank-run to 402 LF records. Restore the two blank records
    # before part CD so that its first section remains exact record 405.
    chapter = payloads[0] + b"\n\n" + payloads[1]
    if (len(chapter), chapter.count(b"\n"), digest(chapter)) != (
        EXPECTED_CHAPTER_BYTES, AUTHORITY_LF, EXPECTED_CHAPTER_SHA256
    ):
        raise SystemExit("assembled Chapter 16 identity differs")
    if not chapter.startswith(b"\\chapter{EKSTENSI}\n"):
        raise SystemExit("assembled chapter title differs")
    sections = tuple(line for line in chapter.splitlines() if line.startswith(b"\\section{"))
    if sections != EXPECTED_SECTIONS:
        raise SystemExit(f"assembled section sequence differs: {sections!r}")
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit("assembled chapter must end at its single active \\endinput")

    source_lf = authority.replace(b"\r\n", b"\n")
    for name in (b"label", b"ref", b"eqref", b"cite"):
        if macro_args(name, source_lf) != macro_args(name, chapter):
            raise SystemExit(f"Chapter 16 {name.decode()} sequence differs from authority")
    source_env = re.findall(rb"\\(?:begin|end)\{([^}]+)\}", source_lf)
    target_env = re.findall(rb"\\(?:begin|end)\{([^}]+)\}", chapter)
    if source_env != target_env:
        raise SystemExit("Chapter 16 environment sequence differs from authority")

    expected_counts = {
        b"\\begin{": 142, b"\\end{": 142, b"\\label{": 36,
        b"\\ref{": 27, b"\\eqref{": 1, b"\\cite{": 59,
        b"\\index{": 107, b"\\df{": 29, b"\\tag{": 1,
        b"\\[": 26, b"\\]": 26, b"\\begin{exer}": 0,
    }
    for token, count in expected_counts.items():
        if chapter.count(token) != count:
            raise SystemExit(f"Chapter 16 count mismatch for {token!r}")

    required = (
        b"S - U^*TU", b"\\ofml Q(H^2)",
        b"pemetaan $T$ sebagai", b"teorema 7.26", b"$\\pi_1(\\C \\setminus \\{0\\})$",
        b"mulai bagian Penjumlahan Ekstensi", b"\\psi|_{\\ofml K}",
        b"\\pi_2\\colon \\ofml E \\sto A", b"pemetaan linear beridentitas dan positif lengkap",
    )
    for witness in required:
        if witness not in chapter:
            raise SystemExit(f"required Chapter 16 correction missing: {witness!r}")
    if chapter.count(b"U^*TU") != 2:
        raise SystemExit("typed unitary-conjugation repairs differ")
    rejected = (b"S-UTU^*", b"S = UTU^*", b"Topelitz", b"after section 9.2")
    for witness in rejected:
        if witness in chapter:
            raise SystemExit(f"rejected Chapter 16 source defect remains: {witness!r}")
    return chapter


def build_master() -> bytes:
    master_bytes = SOURCE_MASTER.read_bytes()
    if (len(master_bytes), master_bytes.count(b"\n"), digest(master_bytes)) != (
        SOURCE_MASTER_BYTES, SOURCE_MASTER_LF, SOURCE_MASTER_SHA256
    ):
        raise SystemExit("Chapter 1-15 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1-15 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(master, "Unit Pembaca Kumulatif Bab 1--15", "Unit Pembaca Kumulatif Bab 1--16")
    master = replace_once(master, "batas produksi Bab 1--15", "batas produksi Bab 1--16")
    master = replace_once(master, "Bab 1 sampai Bab 15", "Bab 1 sampai Bab 16")
    master = replace_once(
        master,
        "indeks Fredholm},",
        "indeks Fredholm, ekstensi, ekstensi semiterbelah, operator Toeplitz, spektrum esensial, pemetaan positif lengkap, aljabar nuklir},",
    )
    master = replace_once(
        master,
        " \\include{fredholm_theory-id}\n",
        " \\include{fredholm_theory-id}\n \\include{extensions-id}\n",
    )
    payload = master.encode("utf-8")
    if (len(payload), payload.count(b"\n"), digest(payload)) != (
        EXPECTED_MASTER_BYTES, SOURCE_MASTER_LF + 1, EXPECTED_MASTER_SHA256
    ):
        raise SystemExit("assembled Chapter 1-16 master identity differs")
    includes = tuple(re.findall(r"^ \\include\{([^}]+)\}$", master, re.MULTILINE))
    if includes != EXPECTED_INCLUDES:
        raise SystemExit(f"cumulative include sequence differs: {includes!r}")
    for witness in (
        "Creative Commons", "CC BY-SA 4.0", "OpenAI Codex gpt-5.6-sol, Ultra",
        "tidak\ndisponsori atau didukung",
    ):
        if witness not in master:
            raise SystemExit(f"rights/model/non-endorsement witness missing: {witness!r}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    chapter = build_chapter()
    master = build_master()
    outputs = ((TARGET_CHAPTER, chapter), (TARGET_MASTER, master))
    if args.check:
        for path, payload in outputs:
            if not path.is_file() or path.read_bytes() != payload:
                raise SystemExit(f"assembled output differs: {path}")
    else:
        for path, payload in outputs:
            path.write_bytes(payload)
    print(f"mode={'check' if args.check else 'write'}")
    print(f"chapter_bytes={len(chapter)} chapter_lf={chapter.count(bytes([10]))} chapter_sha256={digest(chapter)}")
    print(f"master_bytes={len(master)} master_lf={master.count(bytes([10]))} master_sha256={digest(master)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
