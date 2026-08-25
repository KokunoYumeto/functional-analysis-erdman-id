#!/usr/bin/env python3
"""Build the deterministic, curated GitHub Pages payload for O008."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MANIFEST_NAME = "PAGES_DEPLOYMENT_MANIFEST.csv"
TRACKED_MANIFEST = ROOT / "qa" / "GITHUB_PAGES_PUBLIC_MANIFEST.csv"


@dataclass(frozen=True)
class ReaderSpec:
    role: str
    source_dir: Path
    public_prefix: PurePosixPath


READERS = (
    ReaderSpec("source_reader", ROOT / "output" / "html", PurePosixPath("output/html")),
    ReaderSpec(
        "companion_reader",
        ROOT / "output" / "html-companion",
        PurePosixPath("output/html-companion"),
    ),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative_path(raw: str) -> PurePosixPath:
    if not raw or "\\" in raw:
        raise ValueError(f"unsafe manifest path: {raw!r}")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe manifest path: {raw!r}")
    return path


def replay_reader_manifest(spec: ReaderSpec) -> list[tuple[PurePosixPath, bytes]]:
    manifest_path = spec.source_dir / "MANIFEST.csv"
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["path", "bytes", "sha256"]:
            raise ValueError(f"unexpected schema in {manifest_path}")
        declared: dict[PurePosixPath, tuple[int, str]] = {}
        declaration_order: list[PurePosixPath] = []
        for row in reader:
            rel = safe_relative_path(row["path"])
            if rel in declared:
                raise ValueError(f"duplicate path in {manifest_path}: {rel}")
            declared[rel] = (int(row["bytes"]), row["sha256"].lower())
            declaration_order.append(rel)

    if declaration_order != sorted(declaration_order, key=lambda item: item.as_posix()):
        raise ValueError(f"manifest is not path-sorted: {manifest_path}")

    actual = {
        PurePosixPath(path.relative_to(spec.source_dir).as_posix())
        for path in spec.source_dir.rglob("*")
        if path.is_file() and path.name != "MANIFEST.csv"
    }
    if actual != set(declared):
        missing = sorted(str(path) for path in set(declared) - actual)
        extra = sorted(str(path) for path in actual - set(declared))
        raise ValueError(f"reader inventory mismatch for {spec.role}: missing={missing}, extra={extra}")

    replayed: list[tuple[PurePosixPath, bytes]] = []
    for rel in declaration_order:
        data = (spec.source_dir / Path(rel.as_posix())).read_bytes()
        expected_bytes, expected_hash = declared[rel]
        if len(data) != expected_bytes or sha256_bytes(data) != expected_hash:
            raise ValueError(f"manifest replay failed for {spec.source_dir / Path(rel.as_posix())}")
        replayed.append((rel, data))
    return replayed


def validate_output_target(path: Path) -> Path:
    resolved = path.resolve()
    qa_dir = (ROOT / "qa").resolve()
    allowed = (
        (resolved.parent == ROOT.resolve() and resolved.name.startswith("_site"))
        or (resolved.parent == qa_dir and resolved.name.startswith("pages-build-"))
    )
    if not allowed:
        raise ValueError(f"refusing output outside bounded Pages build locations: {resolved}")
    return resolved


def write_bytes(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def manifest_csv(rows: list[dict[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=["public_path", "role", "source_path", "bytes", "sha256"],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest-copy", type=Path)
    args = parser.parse_args()

    output = validate_output_target(args.output if args.output.is_absolute() else ROOT / args.output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    replayed = {spec.role: replay_reader_manifest(spec) for spec in READERS}
    rows: list[dict[str, object]] = []

    def add(public_path: PurePosixPath, role: str, source_path: str, data: bytes) -> None:
        write_bytes(output / Path(public_path.as_posix()), data)
        rows.append(
            {
                "public_path": public_path.as_posix(),
                "role": role,
                "source_path": source_path,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )

    for public_path, local_path, role in (
        (PurePosixPath(".nojekyll"), ROOT / "pages" / ".nojekyll", "routing"),
        (PurePosixPath("index.html"), ROOT / "pages" / "index.html", "routing"),
        (
            PurePosixPath("companion/index.html"),
            ROOT / "pages" / "companion" / "index.html",
            "routing",
        ),
    ):
        add(public_path, role, local_path.relative_to(ROOT).as_posix(), local_path.read_bytes())

    reader_metadata: list[dict[str, object]] = []
    for spec in READERS:
        for rel, data in replayed[spec.role]:
            public_path = spec.public_prefix / rel
            source_path = (spec.source_dir.relative_to(ROOT) / Path(rel.as_posix())).as_posix()
            add(public_path, spec.role, source_path, data)
        source_manifest = spec.source_dir / "MANIFEST.csv"
        manifest_data = source_manifest.read_bytes()
        add(
            spec.public_prefix / "MANIFEST.csv",
            f"{spec.role}_manifest",
            source_manifest.relative_to(ROOT).as_posix(),
            manifest_data,
        )
        reader_metadata.append(
            {
                "role": spec.role,
                "public_prefix": spec.public_prefix.as_posix() + "/",
                "manifested_files": len(replayed[spec.role]),
                "manifested_bytes": sum(len(data) for _, data in replayed[spec.role]),
                "manifest_bytes": len(manifest_data),
                "manifest_sha256": sha256_bytes(manifest_data),
            }
        )

    metadata_source = ROOT / "pages" / "PAGES_DEPLOYMENT_METADATA.json"
    metadata_bytes = metadata_source.read_bytes()
    metadata = json.loads(metadata_bytes.decode("utf-8"))
    if metadata.get("readers") != reader_metadata:
        raise ValueError("tracked deployment metadata does not match the replayed reader manifests")
    add(
        PurePosixPath("PAGES_DEPLOYMENT_METADATA.json"),
        "deployment_metadata",
        metadata_source.relative_to(ROOT).as_posix(),
        metadata_bytes,
    )

    rows.sort(key=lambda row: str(row["public_path"]))
    manifest_bytes = manifest_csv(rows)
    write_bytes(output / PUBLIC_MANIFEST_NAME, manifest_bytes)

    if args.manifest_copy is not None:
        manifest_copy = (args.manifest_copy if args.manifest_copy.is_absolute() else ROOT / args.manifest_copy).resolve()
        if manifest_copy != TRACKED_MANIFEST.resolve():
            raise ValueError(f"refusing unexpected tracked manifest destination: {manifest_copy}")
        write_bytes(manifest_copy, manifest_bytes)

    summary = {
        "status": "pass",
        "output": str(output),
        "manifest_rows": len(rows),
        "manifested_bytes": sum(int(row["bytes"]) for row in rows),
        "manifest_bytes": len(manifest_bytes),
        "manifest_sha256": sha256_bytes(manifest_bytes),
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
