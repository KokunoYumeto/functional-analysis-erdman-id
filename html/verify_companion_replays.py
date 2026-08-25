#!/usr/bin/env python3
"""Compare two clean companion builds byte-for-byte with the canonical site."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from build_companion_reader import EXPECTED_SOURCE_READER_INVENTORY, ROOT, source_reader_inventory


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path) -> dict[str, tuple[int, str]]:
    return {
        path.relative_to(root).as_posix(): (path.stat().st_size, sha256(path))
        for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.relative_to(root).as_posix())
    }


def inventory_digest(rows: dict[str, tuple[int, str]]) -> str:
    material = "".join(f"{path}\0{size}\0{digest}\n" for path, (size, digest) in sorted(rows.items())).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def differences(left: dict[str, tuple[int, str]], right: dict[str, tuple[int, str]]) -> dict[str, object]:
    return {
        "missing": sorted(set(left) - set(right)),
        "extra": sorted(set(right) - set(left)),
        "identity_mismatch": sorted(path for path in set(left) & set(right) if left[path] != right[path]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical", type=Path)
    parser.add_argument("replay_a", type=Path)
    parser.add_argument("replay_b", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "qa" / "HTML_COMPANION_REPRODUCIBILITY.json")
    args = parser.parse_args()
    roots = [path if path.is_absolute() else ROOT / path for path in (args.canonical, args.replay_a, args.replay_b)]
    rows = [inventory(root) for root in roots]
    comparisons = {
        "canonical_vs_replay_a": differences(rows[0], rows[1]),
        "canonical_vs_replay_b": differences(rows[0], rows[2]),
        "replay_a_vs_replay_b": differences(rows[1], rows[2]),
    }
    source_inventory = source_reader_inventory()
    passed = source_inventory == EXPECTED_SOURCE_READER_INVENTORY and all(
        not result["missing"] and not result["extra"] and not result["identity_mismatch"]
        for result in comparisons.values()
    )
    report = {
        "schema_version": "o008.html-companion-reproducibility.v1",
        "passed": passed,
        "source_reader_inventory_sha256": source_inventory,
        "builds": [
            {
                "role": role,
                "files": len(data),
                "bytes": sum(size for size, _ in data.values()),
                "inventory_sha256_including_manifest": inventory_digest(data),
            }
            for role, data in zip(("canonical", "replay_a", "replay_b"), rows)
        ],
        "comparisons": comparisons,
    }
    encoded = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.write_bytes(encoded)
    sys.stdout.buffer.write(encoded)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
