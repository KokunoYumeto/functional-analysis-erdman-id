#!/usr/bin/env python3
"""Assemble the two reviewed FAOA-2015-CH12 translation fragments."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PART_A = ROOT / "qa" / "ch12_translation_part_a.tex"
PART_B = ROOT / "qa" / "ch12_translation_part_b.tex"
PARTS = (
    (PART_A, 29_759, 654, "9bc9223ba47deaf9f74a40643a93c25ed6f0bd54527ba012d462c7534c23a80c"),
    (PART_B, 19_953, 501, "641d3f319de76fe535fc212445d31e9e533319c709953b55b945510023b87638"),
)
SOURCE_RANGES = ((1, 639), (658, 1158))
INTERPART_BLANK_RECORDS = 18
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch11.tex"
SOURCE_MASTER_SHA256 = "1836320f0e1a03705ff8e1dbbd2724d9e484ce03e10fde5f575967e2dd6e9796"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "no_identity-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch12.tex"
EXPECTED_SECTIONS = (
    b"\\section{Unitalisasi Aljabar Banach}",
    b"\\section{Barisan Eksak dan Ekstensi}",
    b"\\section{Unitalisasi Aljabar-$C^*$}",
    b"\\section{Kuasi-Invers}",
    b"\\section{Elemen Positif dalam Aljabar-$C^*$}",
    b"\\section{Identitas Aproksimatif}",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"master replacement count for {old!r} is not one")
    return text.replace(old, new, 1)


def main() -> int:
    payloads: list[bytes] = []
    for path, expected_bytes, expected_lf, expected_sha in PARTS:
        data = path.read_bytes()
        if len(data) != expected_bytes or digest(data) != expected_sha:
            raise SystemExit(f"fragment identity mismatch: {path}")
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
            raise SystemExit(f"fragment encoding/line-ending mismatch: {path}")
        if not data.endswith(b"\n") or data.count(b"\n") != expected_lf:
            raise SystemExit(f"fragment LF closure mismatch: {path}")
        data.decode("utf-8")
        payloads.append(data)

    if SOURCE_RANGES != ((1, 639), (658, 1158)):
        raise SystemExit("source-range lock differs")
    chapter = payloads[0] + (b"\n" * INTERPART_BLANK_RECORDS) + payloads[1]
    if not chapter.startswith(b"\\chapter{BERTAHAN TANPA IDENTITAS}\n"):
        raise SystemExit("assembled chapter title differs")
    sections = tuple(line for line in chapter.splitlines() if line.startswith(b"\\section{"))
    if sections != EXPECTED_SECTIONS:
        raise SystemExit(f"assembled section sequence differs: {sections!r}")
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit("assembled chapter must end at its single active \\endinput")
    TARGET_CHAPTER.write_bytes(chapter)

    master_bytes = SOURCE_MASTER.read_bytes()
    if len(master_bytes) != 10_167 or digest(master_bytes) != SOURCE_MASTER_SHA256:
        raise SystemExit("Chapter 1-11 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1-11 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(master, "Unit Pembaca Kumulatif Bab 1--11", "Unit Pembaca Kumulatif Bab 1--12")
    master = replace_once(master, "batas produksi Bab 1--11", "batas produksi Bab 1--12")
    master = replace_once(master, "Bab 1 sampai Bab 11", "Bab 1 sampai Bab 12")
    master = replace_once(
        master,
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier, aljabar C bintang, transformasi Gelfand},",
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier, aljabar C bintang, transformasi Gelfand, unitalisasi, barisan eksak, kuasi-invers, elemen positif, identitas aproksimatif},",
    )
    master = replace_once(
        master,
        " \\include{Gelfand_Naimark-id}\n",
        " \\include{Gelfand_Naimark-id}\n \\include{no_identity-id}\n",
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
