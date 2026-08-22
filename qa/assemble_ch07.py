#!/usr/bin/env python3
"""Assemble the four reviewed FAOA-2015-CH07 translation slices exactly."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    (
        ROOT / "qa" / "ch07_translation_parts" / "part_0001_0142.tex",
        "8b4bc94e20a1c4db86aaef2217a01154f9cabe7850a75e38b97ced86be7316a5",
    ),
    (
        ROOT / "qa" / "ch07_translation_parts" / "part_0143_0303.tex",
        "eb0c70ad1d45546b22fa2a92225dc60c8f9a29afce939c38b375ae09177b51e6",
    ),
    (
        ROOT / "qa" / "ch07_translation_parts" / "part_0304_0423.tex",
        "061700edc2188aee13b1fa9a54ee6c38b575c01f5f4753d29ce2b87ab4019332",
    ),
    (
        ROOT / "qa" / "ch07_translation_parts" / "part_0424_0517.tex",
        "8ad2da11c9fe86ce3dcb657ed4496b6947f7ff27f0e854d4e33a897a72913cb2",
    ),
]
TARGET = ROOT / "source" / "id-ID" / "compact_operators-id.tex"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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

    if total_lines != 517:
        raise SystemExit(f"slice line coverage mismatch: {total_lines}")

    target = b"".join(payloads)
    TARGET.write_bytes(target)
    print(f"target={TARGET.relative_to(ROOT).as_posix()}")
    print(f"bytes={len(target)}")
    print(f"lf={target.count(bytes([10]))}")
    print(f"sha256={digest(target)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
