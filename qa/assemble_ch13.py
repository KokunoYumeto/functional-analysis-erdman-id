#!/usr/bin/env python3
"""Assemble the reviewed FAOA-2015-CH13 fragments and cumulative master."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = (
    (
        ROOT / "qa" / "ch13_translation_part_ab.tex",
        7_652,
        201,
        "66218bedefec3515861b54cf6dd5d2b93a313ae7b40932fb5ddd58e0bcc10417",
    ),
    (
        ROOT / "qa" / "ch13_translation_part_c.tex",
        4_947,
        86,
        "85d3430281e929ef6d07c3d65ca5da419030337e0de6130efb18e7ee3bfe679b",
    ),
)
SOURCE_RANGES = ((1, 203), (204, 289))
INTERPART_LF = 2
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch12.tex"
SOURCE_MASTER_BYTES = 10_275
SOURCE_MASTER_SHA256 = "d84965e27ee26d71575838a42a8410cf5956b967d188d77a040c0f018fd007de"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "GNS_construction-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch13.tex"
EXPECTED_SECTIONS = (
    b"\\section{Fungsional Linear Positif}",
    b"\\section{Representasi}",
    b"\\section{Konstruksi GNS dan Teorema Gelfand-Naimark Ketiga}",
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

    if SOURCE_RANGES != ((1, 203), (204, 289)):
        raise SystemExit("source-range lock differs")
    chapter = payloads[0] + (b"\n" * INTERPART_LF) + payloads[1]
    if not chapter.startswith(b"\\chapter{KONSTRUKSI GELFAND-NAIMARK-SEGAL}\n"):
        # The source label is intentionally attached to the title line.
        if not chapter.startswith(
            b"\\chapter{KONSTRUKSI GELFAND-NAIMARK-SEGAL}\\label{gelfand_naimark_segal}\n"
        ):
            raise SystemExit("assembled chapter title differs")
    sections = tuple(line for line in chapter.splitlines() if line.startswith(b"\\section{"))
    if sections != EXPECTED_SECTIONS:
        raise SystemExit(f"assembled section sequence differs: {sections!r}")
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit("assembled chapter must end at its single active \\endinput")
    if chapter.count(b"\n") != 289:
        raise SystemExit("assembled chapter must retain the 289-record source topology")
    TARGET_CHAPTER.write_bytes(chapter)

    master_bytes = SOURCE_MASTER.read_bytes()
    if len(master_bytes) != SOURCE_MASTER_BYTES or digest(master_bytes) != SOURCE_MASTER_SHA256:
        raise SystemExit("Chapter 1-12 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1-12 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(master, "Unit Pembaca Kumulatif Bab 1--12", "Unit Pembaca Kumulatif Bab 1--13")
    master = replace_once(master, "batas produksi Bab 1--12", "batas produksi Bab 1--13")
    master = replace_once(master, "Bab 1 sampai Bab 12", "Bab 1 sampai Bab 13")
    master = replace_once(
        master,
        "pdfcreationdate={D:20260823000000+02'00'},",
        "pdfcreationdate={D:20260824000000+02'00'},",
    )
    master = replace_once(
        master,
        "pdfmoddate={D:20260823000000+02'00'},",
        "pdfmoddate={D:20260824000000+02'00'},",
    )
    master = replace_once(
        master,
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier, aljabar C bintang, transformasi Gelfand, unitalisasi, barisan eksak, kuasi-invers, elemen positif, identitas aproksimatif},",
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier, aljabar C bintang, transformasi Gelfand, unitalisasi, barisan eksak, kuasi-invers, elemen positif, identitas aproksimatif, konstruksi GNS, keadaan, representasi},",
    )
    master = replace_once(
        master,
        " \\include{no_identity-id}\n",
        " \\include{no_identity-id}\n \\include{GNS_construction-id}\n",
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
