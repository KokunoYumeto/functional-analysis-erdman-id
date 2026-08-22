#!/usr/bin/env python3
"""Assemble the six independently reviewed FAOA-2015-CH08 slices exactly."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    (
        ROOT / "qa" / "ch08_translation_parts" / "part_0001_0129.tex",
        "fb667da0c0ebf21caab7e4a4cc058184cf79ec6d23643e9ffe5005066cd7d051",
    ),
    (
        ROOT / "qa" / "ch08_translation_parts" / "part_0130_0229.tex",
        "4365fc9305c302429528e2f7299b7bf6efb3769f8dafb197e79e5b3b23aacc23",
    ),
    (
        ROOT / "qa" / "ch08_translation_parts" / "part_0230_0332.tex",
        "ba7901369ae580d1e05c115a39290dcdd3d05d6d074b25e389bf14e6ace11f2b",
    ),
    (
        ROOT / "qa" / "ch08_translation_parts" / "part_0333_0426.tex",
        "dd9fa50c84771cb708ccddc89f9d8248c4e408905cf14c39e5579d1f4c10b640",
    ),
    (
        ROOT / "qa" / "ch08_translation_parts" / "part_0427_0526.tex",
        "1b1b719a240b473b89589ef9e8a302ee066435ec2c6e1419f3d9434d96412c01",
    ),
    (
        ROOT / "qa" / "ch08_translation_parts" / "part_0527_0603.tex",
        "5f73a02638be685d46b7e5620247a373ef383361168c2b5fecb6d1212f6af3ac",
    ),
]
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch07.tex"
SOURCE_MASTER_SHA256 = "c639253fab59df7b51002058b414d8d64c92d77f12e95e88068decafd0d138b9"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "spectrum-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch08.tex"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"master replacement count for {old!r} is not one")
    return text.replace(old, new, 1)


def main() -> int:
    payloads: list[bytes] = []
    total_lines = 0
    for path, expected_sha in PARTS:
        data = path.read_bytes()
        if digest(data) != expected_sha:
            raise SystemExit(f"slice SHA-256 mismatch: {path}")
        if data.startswith(b"\xef\xbb\xbf"):
            raise SystemExit(f"UTF-8 BOM is forbidden: {path}")
        if b"\r" in data:
            raise SystemExit(f"non-LF line ending in: {path}")
        if not data.endswith(b"\n"):
            raise SystemExit(f"missing terminal LF: {path}")
        data.decode("utf-8")
        total_lines += data.count(b"\n")
        payloads.append(data)

    if total_lines != 603:
        raise SystemExit(f"active slice line coverage mismatch: {total_lines}")

    chapter = b"".join(payloads)
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit("assembled chapter must end at its single active \\endinput")
    TARGET_CHAPTER.write_bytes(chapter)

    master_bytes = SOURCE_MASTER.read_bytes()
    if digest(master_bytes) != SOURCE_MASTER_SHA256:
        raise SystemExit("Chapter 1--7 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1--7 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(
        master,
        "Unit Pembaca Kumulatif Bab 1--7",
        "Unit Pembaca Kumulatif Bab 1--8",
    )
    master = replace_once(
        master,
        "batas produksi Bab 1--7",
        "batas produksi Bab 1--8",
    )
    master = replace_once(
        master,
        "Bab 1 sampai Bab 7",
        "Bab 1 sampai Bab 8",
    )
    master = replace_once(
        master,
        " \\include{compact_operators-id}\n",
        " \\include{compact_operators-id}\n \\include{spectrum-id}\n",
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
