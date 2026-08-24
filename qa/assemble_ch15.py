#!/usr/bin/env python3
"""Assemble reviewed FAOA-2015-CH15 fragments and the cumulative master."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "source" / "upstream" / "fredholm_theory.tex"
AUTHORITY_BYTES = 16_977
AUTHORITY_LF = 444
AUTHORITY_SHA256 = "0ef2e5be3c716a099e8609a84528d77ad6387ec531c52f9890d4e34175c57d91"
PARTS = (
    (
        ROOT / "qa" / "ch15_translation_part_ab.tex",
        8_602,
        206,
        "a456bebcdcf199e47dd695b051d7e074509c6485f813698ad404ce1044f7ba0b",
    ),
    (
        ROOT / "qa" / "ch15_translation_part_cd.tex",
        9_071,
        238,
        "6d0f26f20c9dc5cb77713905cf6f2bc5e1033e5f486c3e6767b81391483104d4",
    ),
)
SOURCE_RANGES = ((1, 206), (207, 444))
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch14.tex"
SOURCE_MASTER_BYTES = 10_443
SOURCE_MASTER_LF = 343
SOURCE_MASTER_SHA256 = "f04180a796707c6cb0c5f74082a8b4c25721d20ff3ea9235819939b11e1e50c9"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "fredholm_theory-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch15.tex"
EXPECTED_CHAPTER_BYTES = 17_672
EXPECTED_CHAPTER_SHA256 = "174b1ad2557f7dfa10e8171bd7482d907f858389b509f4d55de9cc785e2b43ba"
EXPECTED_MASTER_BYTES = 10_541
EXPECTED_MASTER_SHA256 = "f2df36c70dcca86f44687efe450ea46a5611be2d1170a9ded16dbfbfcdb73a33"
EXPECTED_SECTIONS = (
    b"\\section{Alternatif Fredholm}",
    b"\\section{Alternatif Fredholm -- lanjutan}",
    b"\\section{Operator Fredholm}",
    b"\\section{Alternatif Fredholm -- Penutup}",
)
EXPECTED_INCLUDES = (
    "linalg-id",
    "categories-id",
    "normlinspaces-id",
    "Hilbert_spaces-id",
    "Hilbert_space_operators-id",
    "Banach_spaces-id",
    "compact_operators-id",
    "spectrum-id",
    "topvecspaces-id",
    "distributions-id",
    "Gelfand_Naimark-id",
    "no_identity-id",
    "GNS_construction-id",
    "multiplier_algebras-id",
    "fredholm_theory-id",
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
    if (
        len(authority) != AUTHORITY_BYTES
        or authority.count(b"\n") != AUTHORITY_LF
        or digest(authority) != AUTHORITY_SHA256
    ):
        raise SystemExit("Chapter 15 authority identity differs")
    if authority.startswith(b"\xef\xbb\xbf") or authority.count(b"\r\n") != AUTHORITY_LF:
        raise SystemExit("Chapter 15 authority encoding/record closure differs")

    payloads: list[bytes] = []
    for path, expected_bytes, expected_lf, expected_sha in PARTS:
        data = path.read_bytes()
        if len(data) != expected_bytes or digest(data) != expected_sha:
            raise SystemExit(f"fragment identity mismatch: {path}")
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
            raise SystemExit(f"fragment encoding/line-ending mismatch: {path}")
        if data.count(b"\n") != expected_lf:
            raise SystemExit(f"fragment LF closure mismatch: {path}")
        data.decode("utf-8")
        payloads.append(data)

    if SOURCE_RANGES != ((1, 206), (207, 444)):
        raise SystemExit("source-range lock differs")
    if not payloads[0].endswith(b" \n"):
        raise SystemExit("Part AB terminal blank-record placeholder differs")
    part_ab = payloads[0][:-2] + b"\n"
    chapter = part_ab + payloads[1]

    if len(chapter) != EXPECTED_CHAPTER_BYTES or digest(chapter) != EXPECTED_CHAPTER_SHA256:
        raise SystemExit("assembled Chapter 15 identity differs")
    if chapter.count(b"\n") != 444 or b"\r" in chapter:
        raise SystemExit("assembled chapter must retain the 444-record LF topology")
    if not chapter.startswith(b"\\chapter{TEORI FREDHOLM}\n"):
        raise SystemExit("assembled chapter title differs")
    sections = tuple(line for line in chapter.splitlines() if line.startswith(b"\\section{"))
    if sections != EXPECTED_SECTIONS:
        raise SystemExit(f"assembled section sequence differs: {sections!r}")
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit("assembled chapter must end at its single active \\endinput")

    source_lf = authority.replace(b"\r\n", b"\n")
    for name in (b"label", b"ref", b"eqref", b"cite"):
        if macro_args(name, source_lf) != macro_args(name, chapter):
            raise SystemExit(f"Chapter 15 {name.decode()} sequence differs from authority")
    source_env = re.findall(rb"\\(?:begin|end)\{([^}]+)\}", source_lf)
    target_env = re.findall(rb"\\(?:begin|end)\{([^}]+)\}", chapter)
    if source_env != target_env:
        raise SystemExit("Chapter 15 environment sequence differs from authority")

    expected_counts = {
        b"\\begin{": 60,
        b"\\end{": 60,
        b"\\label{": 33,
        b"\\ref{": 19,
        b"\\eqref{": 8,
        b"\\cite{": 17,
        b"\\index{": 46,
        b"\\df{": 11,
        b"\\tag{": 12,
        b"\\begin{align}": 6,
        b"\\[": 7,
        b"\\]": 7,
        b"\\begin{exer}": 0,
    }
    for token, count in expected_counts.items():
        if chapter.count(token) != count:
            raise SystemExit(f"Chapter 15 count mismatch for {token!r}")

    required_corrections = (
        b"\\lambda \\in \\C\\setminus\\{0\\}",
        b"ruang Banach $B$",
        b"jumlah dua subruang tertutup dari suatu ruang Hilbert tidak harus tertutup",
        b"ruang Hilbert berdimensi tak hingga",
        b"Untuk pemetaan antar-ruang, kita memakai konvensi standar",
        b"\\index{Fredholm!indeks (\\seeonly{indeks})}%",
    )
    if chapter.count(required_corrections[0]) != 3:
        raise SystemExit("nonzero-scalar corrections differ")
    for witness in required_corrections[1:]:
        if witness not in chapter:
            raise SystemExit(f"required Chapter 15 correction missing: {witness!r}")
    if b"SK = KS" in chapter:
        raise SystemExit("rejected Riesz--Schauder commutation condition remains")
    if b"C([0,1])" in chapter or b"L^2([0,1])" in chapter:
        raise SystemExit("Alternative I function space was invented")

    inline = re.findall(rb"(?<!\\)\$(.*?)(?<!\\)\$", chapter, re.DOTALL)
    if len(inline) != 191:
        raise SystemExit("Chapter 15 corrected inline-math closure differs")
    return chapter


def build_master() -> bytes:
    master_bytes = SOURCE_MASTER.read_bytes()
    if (
        len(master_bytes) != SOURCE_MASTER_BYTES
        or master_bytes.count(b"\n") != SOURCE_MASTER_LF
        or digest(master_bytes) != SOURCE_MASTER_SHA256
    ):
        raise SystemExit("Chapter 1-14 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1-14 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(master, "Unit Pembaca Kumulatif Bab 1--14", "Unit Pembaca Kumulatif Bab 1--15")
    master = replace_once(master, "batas produksi Bab 1--14", "batas produksi Bab 1--15")
    master = replace_once(master, "Bab 1 sampai Bab 14", "Bab 1 sampai Bab 15")
    master = replace_once(
        master,
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier, aljabar C bintang, transformasi Gelfand, unitalisasi, barisan eksak, kuasi-invers, elemen positif, identitas aproksimatif, konstruksi GNS, keadaan, representasi, modul Hilbert, ideal esensial, kompaktifikasi, aljabar pengali},",
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier, aljabar C bintang, transformasi Gelfand, unitalisasi, barisan eksak, kuasi-invers, elemen positif, identitas aproksimatif, konstruksi GNS, keadaan, representasi, modul Hilbert, ideal esensial, kompaktifikasi, aljabar pengali, teori Fredholm, operator Fredholm, aljabar Calkin, indeks Fredholm},",
    )
    master = replace_once(
        master,
        " \\include{multiplier_algebras-id}\n",
        " \\include{multiplier_algebras-id}\n \\include{fredholm_theory-id}\n",
    )
    payload = master.encode("utf-8")
    if len(payload) != EXPECTED_MASTER_BYTES or digest(payload) != EXPECTED_MASTER_SHA256:
        raise SystemExit("assembled Chapter 1-15 master identity differs")
    includes = tuple(re.findall(r"^ \\include\{([^}]+)\}$", master, re.MULTILINE))
    if includes != EXPECTED_INCLUDES:
        raise SystemExit(f"cumulative include sequence differs: {includes!r}")
    for witness in (
        "Creative Commons",
        "CC BY-SA 4.0",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "tidak\ndisponsori atau didukung",
    ):
        if witness not in master:
            raise SystemExit(f"rights/model/non-endorsement witness missing: {witness!r}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify existing outputs without rewriting")
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
    print(f"chapter={TARGET_CHAPTER.relative_to(ROOT).as_posix()}")
    print(f"chapter_bytes={len(chapter)}")
    print(f"chapter_lf={chapter.count(bytes([10]))}")
    print(f"chapter_sha256={digest(chapter)}")
    print(f"master={TARGET_MASTER.relative_to(ROOT).as_posix()}")
    print(f"master_bytes={len(master)}")
    print(f"master_lf={master.count(bytes([10]))}")
    print(f"master_sha256={digest(master)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
