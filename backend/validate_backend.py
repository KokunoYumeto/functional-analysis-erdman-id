#!/usr/bin/env python3
"""Validate and manifest the deterministic O008 backend."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MANIFEST = BACKEND / "BACKEND_MANIFEST.csv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number} is not an object")
        if value.get("schema") != "interlanguage-modular-math":
            raise ValueError(f"{path.name}:{number} has wrong schema")
        if value.get("schema_version") != "0.1.0":
            raise ValueError(f"{path.name}:{number} has wrong schema version")
        records.append(value)
    # Lossless JSON round-trip proof.
    if json.loads(json.dumps(records, ensure_ascii=False)) != records:
        raise ValueError(f"{path.name} failed JSON round trip")
    return records


def backend_files() -> list[Path]:
    return sorted(
        [
            path
            for path in BACKEND.iterdir()
            if path.is_file() and path.name != MANIFEST.name and not path.name.endswith(".pyc")
        ],
        key=lambda path: path.name.casefold(),
    )


def hashes(paths: list[Path]) -> dict[str, str]:
    return {path.name: sha(path) for path in paths}


def write_manifest(paths: list[Path]) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["relative_path", "bytes", "sha256"])
    for path in paths:
        writer.writerow([path.name, path.stat().st_size, sha(path)])
    MANIFEST.write_text(buffer.getvalue(), encoding="utf-8", newline="\n")


def main() -> None:
    schema = json.loads((BACKEND / "schema.json").read_text(encoding="utf-8"))
    expected_sets = schema["record_sets"]
    missing = [name for name in expected_sets if not (BACKEND / name).is_file() and name != MANIFEST.name]
    if missing:
        raise ValueError(f"missing record sets: {missing}")

    generated = [
        "semantic_units.jsonl",
        "segments.jsonl",
        "relations.jsonl",
        "formula_map.jsonl",
        "exercise_support.jsonl",
        "index_terms.csv",
    ]
    before = hashes([BACKEND / name for name in generated])
    result = subprocess.run(
        [sys.executable, str(BACKEND / "generate_ch01_backend.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    after = hashes([BACKEND / name for name in generated])
    if before != after:
        raise ValueError("backend generator was not byte-deterministic against current outputs")

    jsonl_paths = sorted(BACKEND.glob("*.jsonl"), key=lambda path: path.name.casefold())
    records_by_file = {path.name: load_jsonl(path) for path in jsonl_paths}
    all_records = [record for records in records_by_file.values() for record in records]
    ids: dict[str, str] = {}
    for path_name, records in records_by_file.items():
        for record in records:
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id:
                raise ValueError(f"record in {path_name} lacks a stable ID")
            if record_id in ids:
                raise ValueError(f"duplicate ID {record_id} in {ids[record_id]} and {path_name}")
            ids[record_id] = path_name

    rights_ids = {record["id"] for record in records_by_file["rights.jsonl"]}
    for record in all_records:
        rights_id = record.get("rights_id")
        if rights_id and rights_id not in rights_ids:
            raise ValueError(f"unresolved rights ID {rights_id} on {record['id']}")

    external_prefixes = (
        "COURSE-O007",
        "ERDMAN-FAOA-2015-LABEL-",
        "ERDMAN-FAOA-BIB-",
    )
    relation_records = records_by_file["relations.jsonl"] + records_by_file["concept_relations.jsonl"]
    for relation in relation_records:
        for field in ("from_id", "to_id"):
            endpoint = relation[field]
            if endpoint not in ids and not endpoint.startswith(external_prefixes):
                raise ValueError(f"unresolved relation endpoint {endpoint} on {relation['id']}")

    units = records_by_file["units.jsonl"]
    chapter_units = [record for record in units if record["record_type"] == "unit"]
    if len(chapter_units) != 17 or [record["order"] for record in chapter_units] != list(range(1, 18)):
        raise ValueError("17-chapter order invariant failed")
    chapter_one = chapter_units[0]
    if chapter_one["translation_state"] != "admitted":
        raise ValueError("Chapter 1 is not admitted")
    if chapter_one["source_sha256"] != "a15cabf306adf5457cedce046f98b9474c72b38ab50197b0dc4288e942772096":
        raise ValueError("Chapter 1 authority mismatch")
    if chapter_one["target_sha256"] != "4ab3098cab358f425190bfe6defa20d3ec7b2a81653e0e61bbfa67e497e2654d":
        raise ValueError("Chapter 1 target mismatch")

    expected_counts = {
        "semantic_units.jsonl": 127,
        "segments.jsonl": 154,
        "formula_map.jsonl": 931,
        "exercise_support.jsonl": 6,
        "corrections.jsonl": 15,
    }
    for name, count in expected_counts.items():
        if len(records_by_file[name]) != count:
            raise ValueError(f"{name} expected {count}, got {len(records_by_file[name])}")

    formula_records = records_by_file["formula_map.jsonl"]
    source_formula_count = sum(len(record["source_formula_ids"]) for record in formula_records)
    target_formula_count = sum(len(record["target_formula_ids"]) for record in formula_records)
    exact_formula_count = sum(
        1 for record in formula_records if record["alignment"] == "preserved_exact_after_whitespace_normalization"
    )
    if (source_formula_count, target_formula_count, exact_formula_count) != (932, 932, 906):
        raise ValueError("formula map coverage invariant failed")

    with (BACKEND / "index_terms.csv").open("r", encoding="utf-8", newline="") as handle:
        term_rows = list(csv.DictReader(handle))
    if len(term_rows) != 187 or len({row["id"] for row in term_rows}) != 187:
        raise ValueError("index-term projection invariant failed")

    artifact_records = records_by_file["artifacts.jsonl"]
    for artifact in artifact_records:
        path = ROOT / artifact["path"]
        if not path.is_file():
            raise ValueError(f"missing artifact {artifact['path']}")
        if path.stat().st_size != artifact["bytes"] or sha(path) != artifact["sha256"]:
            raise ValueError(f"artifact mismatch {artifact['id']}")

    # Text exports use LF and strict UTF-8.  Binary artifacts are outside this
    # backend manifest.
    for path in backend_files():
        data = path.read_bytes()
        data.decode("utf-8")
        if b"\r\n" in data:
            raise ValueError(f"CRLF found in deterministic backend file {path.name}")

    paths = backend_files()
    write_manifest(paths)
    with MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    if len(manifest_rows) != len(paths):
        raise ValueError("backend manifest row count mismatch")
    for row, path in zip(manifest_rows, paths):
        if (
            row["relative_path"] != path.name
            or int(row["bytes"]) != path.stat().st_size
            or row["sha256"] != sha(path)
        ):
            raise ValueError(f"backend manifest mismatch for {path.name}")

    print(result.stdout.strip())
    print(
        json.dumps(
            {
                "jsonl_files": len(jsonl_paths),
                "records": len(all_records),
                "globally_unique_ids": len(ids),
                "relation_endpoints_checked": 2 * len(relation_records),
                "backend_manifest_rows": len(manifest_rows),
                "backend_manifest_sha256": sha(MANIFEST),
                "result": "pass",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
