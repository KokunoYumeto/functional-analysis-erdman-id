#!/usr/bin/env python3
"""Assemble the four independently reviewed FAOA-2015-CH09 fragments."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    (
        ROOT / "qa" / "ch09_translation_parts" / "part_0001_0166.tex",
        "100fd17dc0f0e137ffc0e5b20af4d2583c8c1b81d2822d9d14785cc7da0a5b60",
    ),
    (
        ROOT / "qa" / "ch09_translation_parts" / "part_0167_0398.tex",
        "4d77924fe2b322726e48ebcbfa7de7bd84b41dd860540f1dd569d52971723a6d",
    ),
    (
        ROOT / "qa" / "ch09_translation_parts" / "part_0399_0614.tex",
        "cffe3384d11cbcec1560b14146de13b41d3d302c46582c897e35a64a6003d319",
    ),
    (
        ROOT / "qa" / "ch09_translation_parts" / "part_0615_0806.tex",
        "ed9d6a1464a57aff79c9da7495cb29f9595d0fe94f1c793da1627f287d8ea001",
    ),
]
EXPECTED_PART_LF = (165, 231, 216, 192)
SOURCE_RANGES = ((1, 166), (167, 398), (399, 614), (615, 806))
EXPECTED_NONBLANK_RECORDS = (113, 163, 142, 133)
EXPECTED_SECTION_OPENERS = (
    b"\\section{Himpunan Seimbang dan Himpunan Penyerap}",
    b"\\section{Filter}",
    b"\\section{Topologi Kompatibel}",
    b"\\section{Hasil Bagi}",
    b"\\section{Ruang Konveks Lokal dan Seminorma}",
    b"\\section{Ruang Fr\\'echet}",
)
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch08.tex"
SOURCE_MASTER_SHA256 = "d0b4130b9fa6f85baef22f316ea914d5519bf30d6e82d8e6d824f2cf211c1998"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "topvecspaces-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch09.tex"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"master replacement count for {old!r} is not one")
    return text.replace(old, new, 1)


def main() -> int:
    if SOURCE_RANGES[0][0] != 1 or SOURCE_RANGES[-1][1] != 806:
        raise SystemExit("source-range endpoints differ")
    if any(left[1] + 1 != right[0] for left, right in zip(SOURCE_RANGES, SOURCE_RANGES[1:])):
        raise SystemExit("source ranges are not contiguous")
    if sum(last - first + 1 for first, last in SOURCE_RANGES) != 806:
        raise SystemExit("source-range coverage differs")

    payloads: list[bytes] = []
    for position, ((path, expected_sha), expected_lf, expected_nonblank) in enumerate(
        zip(PARTS, EXPECTED_PART_LF, EXPECTED_NONBLANK_RECORDS, strict=True), start=1
    ):
        data = path.read_bytes()
        if digest(data) != expected_sha:
            raise SystemExit(f"fragment SHA-256 mismatch: {path}")
        if data.startswith(b"\xef\xbb\xbf"):
            raise SystemExit(f"UTF-8 BOM is forbidden: {path}")
        if b"\r" in data:
            raise SystemExit(f"non-LF line ending in: {path}")
        if not data.endswith(b"\n"):
            raise SystemExit(f"missing terminal LF: {path}")
        data.decode("utf-8")
        if data.count(b"\n") != expected_lf:
            raise SystemExit(f"fragment LF count differs at position {position}")
        if sum(bool(line.strip()) for line in data.splitlines()) != expected_nonblank:
            raise SystemExit(f"fragment nonblank-record count differs at position {position}")
        payloads.append(data)

    chapter = b"".join(payloads)
    if chapter.count(b"\n") != sum(EXPECTED_PART_LF):
        raise SystemExit("assembled target LF count differs")
    if not chapter.startswith(b"\\chapter{RUANG VEKTOR TOPOLOGIS}\n"):
        raise SystemExit("assembled chapter title differs")
    if tuple(
        line for line in chapter.splitlines() if line.startswith(b"\\section{")
    ) != EXPECTED_SECTION_OPENERS:
        raise SystemExit("assembled section sequence differs")
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit("assembled chapter must end at its single active \\endinput")
    TARGET_CHAPTER.write_bytes(chapter)

    master_bytes = SOURCE_MASTER.read_bytes()
    if digest(master_bytes) != SOURCE_MASTER_SHA256:
        raise SystemExit("Chapter 1--8 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1--8 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(
        master,
        "Unit Pembaca Kumulatif Bab 1--8",
        "Unit Pembaca Kumulatif Bab 1--9",
    )
    master = replace_once(
        master,
        "batas produksi Bab 1--8",
        "batas produksi Bab 1--9",
    )
    master = replace_once(
        master,
        "Bab 1 sampai Bab 8",
        "Bab 1 sampai Bab 9",
    )
    master = replace_once(
        master,
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral},",
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet},",
    )
    master = replace_once(
        master,
        " \\include{spectrum-id}\n",
        " \\include{spectrum-id}\n \\include{topvecspaces-id}\n",
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
