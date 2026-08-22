#!/usr/bin/env python3
"""Assemble the seven independently reviewed FAOA-2015-CH10 fragments."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = (
    (ROOT / "qa" / "ch10_translation_parts" / "part_0001_0094.tex", "c84f091e9f5226aafa2f3b89507855fa7df92b278c1c2742fed5e18b8bb9c0b0"),
    (ROOT / "qa" / "ch10_translation_parts" / "part_0095_0190.tex", "adfdcd3a4ee97faf5cc0261affe5b6d909ef5a1d37428c172462143d9d8f2a09"),
    (ROOT / "qa" / "ch10_translation_parts" / "part_0191_0386.tex", "0d7b8127b464546247966249996f781fdf6fe4e477deee5599cda6d1538c5170"),
    (ROOT / "qa" / "ch10_translation_parts" / "part_0387_0481.tex", "9477bccbba12c5e27b854b851b5ae08093c7b91f2c62e624b69cf9066c4a0cdd"),
    (ROOT / "qa" / "ch10_translation_parts" / "part_0482_0710.tex", "de59e7c34e0f56c2085b8af4839f681efb62faf12d331bad9845f7ad719f39ff"),
    (ROOT / "qa" / "ch10_translation_parts" / "part_0711_0796.tex", "226a0d26bdde4fa0d2ccb37426ae4db6189b1d655717e61c11989066b7b4db3b"),
    (ROOT / "qa" / "ch10_translation_parts" / "part_0797_0894.tex", "65c18dd37bdb7fa77cc08c9d7c7081ac3d57b3c85d6ee6057404c578470874ae"),
)
EXPECTED_PART_LF = (86, 94, 196, 96, 225, 83, 96)
EXPECTED_NONBLANK = (66, 63, 169, 62, 168, 65, 64)
SOURCE_RANGES = ((1, 94), (95, 190), (191, 386), (387, 481), (482, 710), (711, 796), (797, 894))
EXPECTED_SECTIONS = (
    b"\\section{Limit Induktif}\\label{sec_ind_limits}",
    b"\\section{Ruang-$LF$}\\label{sec_LFsps}",
    b"\\section{Distribusi}",
    b"\\section{Konvolusi}",
    b"\\section{Solusi Distribusional untuk Persamaan Diferensial Biasa}",
    b"\\section{Transformasi Fourier}\\label{section_Fourier_transform}",
)
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch09.tex"
SOURCE_MASTER_SHA256 = "acba53fd01601ecd49516c01fb00e38af7bfcafbbbff0358a87dea864c591e3f"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "distributions-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch10.tex"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"master replacement count for {old!r} is not one")
    return text.replace(old, new, 1)


def main() -> int:
    if SOURCE_RANGES[0][0] != 1 or SOURCE_RANGES[-1][1] != 894:
        raise SystemExit("source-range endpoints differ")
    if any(a[1] + 1 != b[0] for a, b in zip(SOURCE_RANGES, SOURCE_RANGES[1:])):
        raise SystemExit("source ranges are not contiguous")
    if sum(last - first + 1 for first, last in SOURCE_RANGES) != 894:
        raise SystemExit("source-range coverage differs")

    payloads: list[bytes] = []
    for position, ((path, expected_sha), expected_lf, expected_nonblank) in enumerate(
        zip(PARTS, EXPECTED_PART_LF, EXPECTED_NONBLANK, strict=True), start=1
    ):
        data = path.read_bytes()
        if digest(data) != expected_sha:
            raise SystemExit(f"fragment SHA-256 mismatch: {path}")
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
            raise SystemExit(f"fragment encoding/line-ending mismatch: {path}")
        if not data.endswith(b"\n"):
            raise SystemExit(f"missing terminal LF: {path}")
        data.decode("utf-8")
        if data.count(b"\n") != expected_lf:
            raise SystemExit(f"fragment LF count differs at position {position}")
        if sum(bool(line.strip()) for line in data.splitlines()) != expected_nonblank:
            raise SystemExit(f"fragment nonblank count differs at position {position}")
        payloads.append(data)

    chapter = b"".join(payloads)
    if not chapter.startswith(b"\\chapter{DISTRIBUSI}\n"):
        raise SystemExit("assembled chapter title differs")
    sections = tuple(line for line in chapter.splitlines() if line.startswith(b"\\section{"))
    if sections != EXPECTED_SECTIONS:
        raise SystemExit(f"assembled section sequence differs: {sections!r}")
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit("assembled chapter must end at its single active \\endinput")
    TARGET_CHAPTER.write_bytes(chapter)

    master_bytes = SOURCE_MASTER.read_bytes()
    if digest(master_bytes) != SOURCE_MASTER_SHA256:
        raise SystemExit("Chapter 1--9 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1--9 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(master, "Unit Pembaca Kumulatif Bab 1--9", "Unit Pembaca Kumulatif Bab 1--10")
    master = replace_once(master, "batas produksi Bab 1--9", "batas produksi Bab 1--10")
    master = replace_once(master, "Bab 1 sampai Bab 9", "Bab 1 sampai Bab 10")
    master = replace_once(
        master,
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet},",
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier},",
    )
    master = replace_once(
        master,
        " \\include{topvecspaces-id}\n",
        " \\include{topvecspaces-id}\n \\include{distributions-id}\n",
    )
    master_payload = master.encode("utf-8")
    TARGET_MASTER.write_bytes(master_payload)

    print(f"chapter={TARGET_CHAPTER.relative_to(ROOT).as_posix()}")
    print(f"chapter_bytes={len(chapter)}")
    print(f"chapter_lf={chapter.count(bytes([10]))}")
    print(f"chapter_sha256={digest(chapter)}")
    print(f"master={TARGET_MASTER.relative_to(ROOT).as_posix()}")
    print(f"master_bytes={len(master_payload)}")
    print(f"master_lf={master_payload.count(bytes([10]))}")
    print(f"master_sha256={digest(master_payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
