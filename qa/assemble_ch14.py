#!/usr/bin/env python3
"""Assemble reviewed FAOA-2015-CH14 fragments and the cumulative master."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = (
    (
        ROOT / "qa" / "ch14_translation_part_a.tex",
        17_010,
        361,
        "a61c98687619ea81badd7c9442ede74fa78a3d8c10ecfab3d3e235b8d29c5670",
    ),
    (
        ROOT / "qa" / "ch14_translation_part_bc.tex",
        14_887,
        323,
        "a692e19732a8b7ec1482c5be22d630f3ae7ccdbfb9093ce341eddfc45348a13c",
    ),
)
SOURCE_RANGES = ((1, 364), (365, 687))
# apply_patch removes redundant terminal blank records from a fragment. Restore
# the three source blank records exactly at the safe top-level join.
INTERPART_LF = 3
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch13.tex"
SOURCE_MASTER_BYTES = 10_345
SOURCE_MASTER_SHA256 = "d1734ea09a576c9e5c8f38bb9430a132e8cd38551c9b0c6cbd9bf65b4923c87e"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "multiplier_algebras-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch14.tex"
EXPECTED_SECTIONS = (
    b"\\section{Modul Hilbert}",
    b"\\section{Ideal Esensial}",
    b"\\section{Kompaktifikasi dan Unitalisasi}",
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
        if data.count(b"\n") != expected_lf:
            raise SystemExit(f"fragment LF closure mismatch: {path}")
        data.decode("utf-8")
        payloads.append(data)

    if SOURCE_RANGES != ((1, 364), (365, 687)):
        raise SystemExit("source-range lock differs")
    chapter = payloads[0] + (b"\n" * INTERPART_LF) + payloads[1]
    if not chapter.startswith(b"\\chapter{ALJABAR PENGALI}\\label{multiplier_algebras}\n"):
        raise SystemExit("assembled chapter title differs")
    sections = tuple(line for line in chapter.splitlines() if line.startswith(b"\\section{"))
    if sections != EXPECTED_SECTIONS:
        raise SystemExit(f"assembled section sequence differs: {sections!r}")
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit("assembled chapter must end at its single active \\endinput")
    if chapter.count(b"\n") != 687:
        raise SystemExit("assembled chapter must retain the 687-record source topology")
    TARGET_CHAPTER.write_bytes(chapter)

    master_bytes = SOURCE_MASTER.read_bytes()
    if len(master_bytes) != SOURCE_MASTER_BYTES or digest(master_bytes) != SOURCE_MASTER_SHA256:
        raise SystemExit("Chapter 1-13 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1-13 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(master, "Unit Pembaca Kumulatif Bab 1--13", "Unit Pembaca Kumulatif Bab 1--14")
    master = replace_once(master, "batas produksi Bab 1--13", "batas produksi Bab 1--14")
    master = replace_once(master, "Bab 1 sampai Bab 13", "Bab 1 sampai Bab 14")
    master = replace_once(
        master,
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier, aljabar C bintang, transformasi Gelfand, unitalisasi, barisan eksak, kuasi-invers, elemen positif, identitas aproksimatif, konstruksi GNS, keadaan, representasi},",
        "pdfkeywords={aljabar linear, analisis fungsional, operator, ruang Hilbert, ruang Banach, spektrum, operator kompak, teorema spektral, ruang vektor topologis, ruang Frechet, distribusi, ruang LF, konvolusi, transformasi Fourier, aljabar C bintang, transformasi Gelfand, unitalisasi, barisan eksak, kuasi-invers, elemen positif, identitas aproksimatif, konstruksi GNS, keadaan, representasi, modul Hilbert, ideal esensial, kompaktifikasi, aljabar pengali},",
    )
    master = replace_once(
        master,
        " \\include{GNS_construction-id}\n",
        " \\include{GNS_construction-id}\n \\include{multiplier_algebras-id}\n",
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
