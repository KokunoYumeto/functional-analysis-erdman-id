#!/usr/bin/env python3
"""Assemble the four reviewed FAOA-2015-CH06 translation slices exactly."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    (
        ROOT / "qa" / "ch06_translation_parts" / "part_0001_0350.tex",
        "e002ccc61a6e4790a9ad6cb009739c89d3dfaf23533d80bdab0205908d8adfb1",
    ),
    (
        ROOT / "qa" / "ch06_translation_parts" / "part_0351_0629.tex",
        "ae6c42366ca47f589308bd74a287030ab8bb728e03c5d31b3f51590e9f796a3b",
    ),
    (
        ROOT / "qa" / "ch06_translation_parts" / "part_0630_1130.tex",
        "00561be3b763efdc7391b7dc44d1f2c5ada50b79674f558b3c3c8b64e12d1ab6",
    ),
    (
        ROOT / "qa" / "ch06_translation_parts" / "part_1131_1605.tex",
        "b9b55211f6fc85174c954914635bcc5be48bd6861c1e209c327829b710913d90",
    ),
]
TARGET = ROOT / "source" / "id-ID" / "Banach_spaces-id.tex"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    payloads: list[bytes] = []
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
        payloads.append(data)

    target = b"".join(payloads)
    TARGET.write_bytes(target)
    print(f"target={TARGET.relative_to(ROOT).as_posix()}")
    print(f"bytes={len(target)}")
    print(f"lf={target.count(bytes([10]))}")
    print(f"sha256={digest(target)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
