#!/usr/bin/env python3
"""Validate the deterministic Chapter 1--7 backend and its manifest."""

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
GENERATED = [
    "units.jsonl",
    "artifacts.jsonl",
    "qa_events.jsonl",
    "corrections.jsonl",
    "terminology.jsonl",
    "semantic_units.jsonl",
    "segments.jsonl",
    "relations.jsonl",
    "formula_map.jsonl",
    "exercise_support.jsonl",
    "index_terms.csv",
]
CH01_PREFIX_LOCKS = {
    "units.jsonl": (957, "d58c211c782422004d0d144b779a75dce09a964052026d2525352169456440d4"),
    "artifacts.jsonl": (1394, "804a07178df0b03611f29c9aad15464e4123d30ea5f761367132dd39bfe50e3d"),
    "qa_events.jsonl": (2533, "c4bfa226d77ec9b7df67629c610e036dc03ba64f10a1dd048743ac18bebec4a2"),
    "corrections.jsonl": (6074, "a3663f1999eee34e4e0535f46cc4a5c33a78e46885ed99900bb587327fbe7b05"),
    "terminology.jsonl": (6030, "be3b6689fbc7bd5c1453bc71755257041df34d3c83c9af7bfe6386177fbeb39d"),
    "semantic_units.jsonl": (102130, "a8847fbac37ccbb008643df8dab994c56b2ccf007f165d9160e1d6242a056608"),
    "segments.jsonl": (116663, "4d04b9459f546ed18a865c544c3c39c1b6f6f4628ae66c157e3f869bc6d73f7a"),
    "relations.jsonl": (120798, "0fac179bf89231cafb7f3120335b9f972febf1346c67b8d7035c55e1f99488dd"),
    "formula_map.jsonl": (487668, "7337ec874b039527e44ea476cc57a453b04015343f193685ea75418d46dcf381"),
    "exercise_support.jsonl": (3062, "185420e94dbf748f3617a462b8f03936e7cf33a66b9f47b65dcf2c9a242bf4af"),
    "index_terms.csv": (47079, "e5d733d2d61493f392cc384e7d67219eb21ccb08d50e06a434654b0d1c10545b"),
}
CH04_PREFIX_LOCKS = {
    "semantic_units.jsonl": (393119, "54cca57d75ee8cb8b46ea6ea46876c14207acf2e99a1eee04bd310223320b7d5"),
    "segments.jsonl": (456214, "82f44070f44944e8dd2496e87fe5dfdffbf4cd0d2b5bd71d23447e9e41d09a61"),
    "relations.jsonl": (513115, "ef9b559648ea060c691a242a0ef492437efa5cd087bf57ca659a1be418e67b07"),
    "formula_map.jsonl": (1972193, "7ec7935fc97003a5977b480e4965dea805305a126e9cbf9cf1123bf714f88805"),
    "exercise_support.jsonl": (11665, "3411cc479cfe6ba27396e9e7e05a84f2b95f72e98195bfe3601f4517c11a6b4f"),
    "index_terms.csv": (214509, "74755e7af6c4f1e06200580eb324c56461098d791def101a0a707b767cfb15bb"),
    "artifacts.jsonl": (12956, "90d6b44eb75134ce828a7c5a25657d435dd2a59f941f091485139cabf613d9e2"),
    "qa_events.jsonl": (20773, "36c816002e3a205b70bfdb5845503f598f81021a91b87eaf86bbf461007794fc"),
    "corrections.jsonl": (43201, "7d02b1e02e929cebfbb2c6a3398f74a77c801cd58ed3e8545f9dd9801a995bb2"),
    "terminology.jsonl": (39107, "09bcc4d8bc83505e22c1c13cf33a3fa39ae3384a091224d0e323eac1dd9ed630"),
}
CH04_UNIT_PREFIX_LOCK = (
    4769,
    "bf26c0f69bf69b1ef63e785de2c2649424d3aa9f50faebb8043b3b0df51c33c4",
)
CH05_PREFIX_LOCKS = {
    "semantic_units.jsonl": (510448, "566655e3f1a662b94156a4316d2915f9d332948e60ab7f6ee337ebdc1d1287ce"),
    "segments.jsonl": (584376, "8e474b281db34de922c5fddb017ab6229bba5f6538acf1170c63ef382e854ade"),
    "relations.jsonl": (679917, "d0bc5aecb93cdef3b0c8b8727f2b4414187119d45b6cee7fbe1c4cce8168c0ef"),
    "formula_map.jsonl": (2482098, "4864f830135cb60bd00144eae55e5d93f093cd3c6c01ad2474d092faa77ed22e"),
    "exercise_support.jsonl": (13689, "5f77abb0d5b396a3e747d5906a750acac1b0c200c3858aeebc93581f487a704b"),
    "index_terms.csv": (257545, "99e0e2354f6866448f1b9e0c1bc5ea8357bfa130e8fad72efb7a2dddf30ad1c6"),
    "artifacts.jsonl": (18795, "cdb9459ce39642e8a9199c7a16e2e8bcb9e368722e187e01c13103cb5302f7fa"),
    "qa_events.jsonl": (28862, "fc69b8098bd3acd909e665a17ec40b7a20208fe14d74e8ac7b84dba0845033c8"),
    "corrections.jsonl": (63360, "770b70c91d7dd85801059e4add075961270689f94a63fa96b1c2ae753461f275"),
    "terminology.jsonl": (57228, "255890655e18f76ca4df8d3a9e02180b8fa99aa51129b3c9e73290b75f8f3a21"),
}
CH05_UNIT_PREFIX_LOCK = (
    6179,
    "06bd36d86a525d3e0669081e2a3b9a41e6ea826ac21317778028eab55f5402d7",
)
CH06_UNIT_SUFFIX_LOCK = (
    5511,
    "2bd13cb93dffbaa5903d15779ec5191ad22b1c9a7b6dd52235edd50f8f5613b1",
)
CH06_PREFIX_LOCKS = {
    "semantic_units.jsonl": (650_244, "2fa15e508b1aa18e707484b7c5109b643900dcc8f59f4dae1e8543b0159c4ed2"),
    "segments.jsonl": (747_490, "7f65fe4d47ffdbb902235ad1fbb8c574c51b8f2154ab8e02564cf1a00aba39d3"),
    "relations.jsonl": (905_248, "6716f53995ec4da47e68bef0dde091820f9968e7a486bdda15a924fe91870e7e"),
    "formula_map.jsonl": (3_243_961, "82e264d01ce8174973eb19b2079ac69ed613af36984ed967beb0ab5ca2f9b0fe"),
    "exercise_support.jsonl": (17_083, "f13f4e3f23495100508057b19e4e49fc6674f3a7126a13e50d804165d3a284f1"),
    "index_terms.csv": (298_201, "5a3630fc62e82ef04ca2c6ae58b500b1881b0b607c5c5540ca30ccda1e3080fe"),
    "artifacts.jsonl": (24_928, "a09bfa4b671574a140652d5ae5a7a67d9b63a50622a71bc72347c00e4412e199"),
    "qa_events.jsonl": (38_259, "9e65e57fdbcc2b566c63bfc8c2683d3b08418c9c36512d1ccf0f887c4daf50d6"),
    "corrections.jsonl": (80_587, "ad8e7a2d8837f09182ccedc5a875bef0b7285b5fa3e6ddab64c8252b6cbe37b4"),
    "terminology.jsonl": (71_021, "e82539683deb4d4ab46c5f0e1f3613ede9ba9cc7fb4b0700f08673108b2f653a"),
}
CH06_UNIT_PREFIX_LOCK = (
    7_621,
    "30d340d0d1070d18d8999ab929c36234b89ef7b762e04b185631e4ad3d0f6d0f",
)
CH07_UNIT_SUFFIX_LOCK = (
    5_070,
    "85461fc1bc771ed2b472f63a50424c51a12da34faa5336a26fb7ae658c74101a",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    data = path.read_bytes()
    text = data.decode("utf-8")
    if data and not data.endswith(b"\n"):
        raise ValueError(f"{path.name} lacks final LF")
    records: list[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise ValueError(f"{path.name}:{number} is an empty record")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number} is not an object")
        if value.get("schema") != "interlanguage-modular-math":
            raise ValueError(f"{path.name}:{number} has wrong schema")
        if value.get("schema_version") != "0.1.0":
            raise ValueError(f"{path.name}:{number} has wrong schema version")
        round_trip = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        if round_trip != line:
            raise ValueError(f"{path.name}:{number} failed exact JSON round trip")
        records.append(value)
    if json.loads(json.dumps(records, ensure_ascii=False)) != records:
        raise ValueError(f"{path.name} failed semantic JSON round trip")
    return records


def load_csv_exact(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_bytes().decode("utf-8")
    if text and not text.endswith("\n"):
        raise ValueError(f"{path.name} lacks final LF")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise ValueError(f"{path.name} lacks a header")
    rows = list(reader)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    if buffer.getvalue() != text:
        raise ValueError(f"{path.name} failed exact CSV round trip")
    return reader.fieldnames, rows


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


def render_manifest(paths: list[Path]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["relative_path", "bytes", "sha256"])
    for path in paths:
        writer.writerow([path.name, path.stat().st_size, sha(path)])
    return buffer.getvalue()


def verify_ch01_prefixes() -> None:
    for name, (size, expected_sha) in CH01_PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size:
            raise ValueError(f"{name} is shorter than its Chapter 1 prefix")
        if sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1 byte prefix changed")


def verify_ch04_prefixes() -> None:
    for name, (size, expected_sha) in CH04_PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size or sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1--4 byte prefix changed")
    unit_lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    prefix = b"".join(unit_lines[:4])
    if (len(prefix), sha_bytes(prefix)) != CH04_UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--4 byte prefix changed")


def verify_ch05_prefixes() -> None:
    for name, (size, expected_sha) in CH05_PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size or sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1--5 byte prefix changed")
    unit_lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    prefix = b"".join(unit_lines[:5])
    if (len(prefix), sha_bytes(prefix)) != CH05_UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--5 byte prefix changed")


def verify_ch06_prefixes() -> None:
    for name, (size, expected_sha) in CH06_PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size or sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1--6 byte prefix changed")
    unit_lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    prefix = b"".join(unit_lines[:6])
    suffix = b"".join(unit_lines[7:])
    if (len(prefix), sha_bytes(prefix)) != CH06_UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--6 byte prefix changed")
    if (len(suffix), sha_bytes(suffix)) != CH07_UNIT_SUFFIX_LOCK:
        raise ValueError("units.jsonl Chapter 8--bridge byte suffix changed")


def register_id(ids: dict[str, str], record_id: str, location: str) -> None:
    if not record_id:
        raise ValueError(f"record in {location} lacks a stable ID")
    if record_id in ids:
        raise ValueError(f"duplicate ID {record_id} in {ids[record_id]} and {location}")
    ids[record_id] = location


def main() -> None:
    if sha(BACKEND / "generate_ch01_backend.py") != (
        "dab8c5be6f44041606efaf7dd138a66f0344a491af5eac92415d96de32553275"
    ):
        raise ValueError("locked Chapter 1 generator changed")
    schema = json.loads((BACKEND / "schema.json").read_text(encoding="utf-8"))
    expected_sets = schema["record_sets"]
    missing = [
        name for name in expected_sets if not (BACKEND / name).is_file() and name != MANIFEST.name
    ]
    if missing:
        raise ValueError(f"missing record sets: {missing}")

    verify_ch01_prefixes()
    verify_ch04_prefixes()
    verify_ch05_prefixes()
    verify_ch06_prefixes()
    generated_paths = [BACKEND / name for name in GENERATED]
    before = hashes(generated_paths)
    run_one = subprocess.run(
        [sys.executable, str(BACKEND / "generate_backend.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    after_one = hashes(generated_paths)
    verify_ch01_prefixes()
    verify_ch04_prefixes()
    verify_ch05_prefixes()
    verify_ch06_prefixes()
    run_two = subprocess.run(
        [sys.executable, str(BACKEND / "generate_backend.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    after_two = hashes(generated_paths)
    verify_ch01_prefixes()
    verify_ch04_prefixes()
    verify_ch05_prefixes()
    verify_ch06_prefixes()
    if before != after_one:
        raise ValueError("canonical generator differs from checked-in backend outputs")
    if after_one != after_two or run_one.stdout != run_two.stdout:
        raise ValueError("canonical generator failed deterministic two-run validation")

    jsonl_paths = sorted(BACKEND.glob("*.jsonl"), key=lambda path: path.name.casefold())
    records_by_file = {path.name: load_jsonl(path) for path in jsonl_paths}
    all_records = [record for records in records_by_file.values() for record in records]
    index_fieldnames, term_rows = load_csv_exact(BACKEND / "index_terms.csv")
    expected_index_fields = [
        "id",
        "parent_segment_id",
        "source_order",
        "source_line",
        "source_index_tex",
        "target_line",
        "target_index_tex",
        "source_sha256",
        "target_sha256",
        "locale",
    ]
    if index_fieldnames != expected_index_fields:
        raise ValueError("index_terms.csv header changed")

    ids: dict[str, str] = {}
    for path_name, records in records_by_file.items():
        for number, record in enumerate(records, 1):
            record_id = record.get("id")
            if not isinstance(record_id, str):
                raise ValueError(f"record in {path_name}:{number} lacks a string ID")
            register_id(ids, record_id, f"{path_name}:{number}")
    for number, row in enumerate(term_rows, 2):
        register_id(ids, row["id"], f"index_terms.csv:{number}")

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
    relation_records = records_by_file["relations.jsonl"] + records_by_file[
        "concept_relations.jsonl"
    ]
    for relation in relation_records:
        for field in ("from_id", "to_id"):
            endpoint = relation[field]
            if endpoint not in ids and not endpoint.startswith(external_prefixes):
                raise ValueError(f"unresolved relation endpoint {endpoint} on {relation['id']}")
    for number, row in enumerate(term_rows, 2):
        if row["parent_segment_id"] not in ids:
            raise ValueError(f"unresolved parent segment in index_terms.csv:{number}")

    units = records_by_file["units.jsonl"]
    chapter_units = [record for record in units if record["record_type"] == "unit"]
    if len(chapter_units) != 17 or [record["order"] for record in chapter_units] != list(
        range(1, 18)
    ):
        raise ValueError("17-chapter order invariant failed")
    chapter_one = chapter_units[0]
    if chapter_one["translation_state"] != "admitted":
        raise ValueError("Chapter 1 is not admitted")
    if chapter_one["source_sha256"] != (
        "a15cabf306adf5457cedce046f98b9474c72b38ab50197b0dc4288e942772096"
    ):
        raise ValueError("Chapter 1 authority mismatch")
    if chapter_one["target_sha256"] != (
        "4ab3098cab358f425190bfe6defa20d3ec7b2a81653e0e61bbfa67e497e2654d"
    ):
        raise ValueError("Chapter 1 target mismatch")
    chapter_two = chapter_units[1]
    chapter_two_expected = {
        "source_bytes": 27446,
        "source_lines": 574,
        "source_sha256": "6f5115e4058902e99ab7157ad59ea95f0e0013e2f4272c05ff421933f7255775",
        "target_bytes": 29254,
        "target_lines": 570,
        "target_sha256": "39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd",
        "course_role": "D20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 6,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch02.tex",
        "build_master_bytes": 9437,
        "build_master_sha256": "1ca424e166df692e8bf69421a0a1720d5dfb2540c52053bb036be99ecdde9ecd",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-2.pdf",
        "artifact_bytes": 795305,
        "artifact_pages": 32,
        "artifact_sha256": "7a04eb72ef5445ee06e429e7552b8e14a02a993c916b4632cdb9219a928a3bdb",
        "qa_receipt_id": "QA-CH02-ADMISSION-20260821",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_two_expected.items():
        if chapter_two.get(field) != expected:
            raise ValueError(f"Chapter 2 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "categories.tex"
    target_path = ROOT / "source" / "id-ID" / "categories-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        27446,
        574,
        "6f5115e4058902e99ab7157ad59ea95f0e0013e2f4272c05ff421933f7255775",
    ):
        raise ValueError("Chapter 2 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        29254,
        570,
        "39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd",
    ):
        raise ValueError("Chapter 2 target authority file mismatch")

    chapter_three = chapter_units[2]
    chapter_three_expected = {
        "source_bytes": 87537,
        "source_lines": 1920,
        "source_sha256": "01548b8e80e14f6eb66703579ed7020e68cc65bd8d30538c13a3533a5ba777e7",
        "target_bytes": 94040,
        "target_lines": 1913,
        "target_sha256": "c44f20890d5fb6b7445f0b2eeca8f477cc970d147d5c54aa4bc5df709f6b1f9d",
        "course_role": "D20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 25,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch03.tex",
        "build_master_bytes": 9311,
        "build_master_sha256": "f36da75492209ba8f4df1d8982bc5a7eae79d75a5dfeb87267715c998aeed8c7",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-3.pdf",
        "artifact_bytes": 1076473,
        "artifact_pages": 57,
        "artifact_sha256": "7a921e1f9678b0a698de237a0a0e5629f24f5b6f0798d2638d9c0a70a499b4f5",
        "qa_receipt_id": "QA-CH03-ADMISSION-20260821",
        "receipt_document_state": "present",
        "receipt_sha256": "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_three_expected.items():
        if chapter_three.get(field) != expected:
            raise ValueError(f"Chapter 3 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "normlinspaces.tex"
    target_path = ROOT / "source" / "id-ID" / "normlinspaces-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        87537,
        1920,
        "01548b8e80e14f6eb66703579ed7020e68cc65bd8d30538c13a3533a5ba777e7",
    ):
        raise ValueError("Chapter 3 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        94040,
        1913,
        "c44f20890d5fb6b7445f0b2eeca8f477cc970d147d5c54aa4bc5df709f6b1f9d",
    ):
        raise ValueError("Chapter 3 target authority file mismatch")

    chapter_four = chapter_units[3]
    chapter_four_expected = {
        "source_bytes": 60217,
        "source_lines": 1340,
        "source_sha256": "80fd8fd190beefde7787139be67ce29b9d9cce2d68ff66489aa1e4a93b54c740",
        "target_bytes": 62947,
        "target_lines": 1351,
        "target_sha256": "b8e728e1f26a66ec2a420373e6104e3db4e5c954d7001acda1c13eb348322215",
        "course_role": "D20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 22,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch04.tex",
        "build_master_bytes": 9348,
        "build_master_sha256": "598bd1f91096a2e0e19314995f44f79f246ca06cad6328ce9e996af074ceff6c",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf",
        "artifact_bytes": 1249703,
        "artifact_pages": 75,
        "artifact_sha256": "716e3524060f64e4728b4d3d8c1a2b906f377ec4e3b3a3cd1ef3e61759a3dd94",
        "qa_receipt_id": "QA-CH04-ADMISSION-20260822",
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH04_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07",
        "publication_state": "pending",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_four_expected.items():
        if chapter_four.get(field) != expected:
            raise ValueError(f"Chapter 4 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "Hilbert_spaces.tex"
    target_path = ROOT / "source" / "id-ID" / "Hilbert_spaces-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        60217,
        1340,
        "80fd8fd190beefde7787139be67ce29b9d9cce2d68ff66489aa1e4a93b54c740",
    ):
        raise ValueError("Chapter 4 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        62947,
        1351,
        "b8e728e1f26a66ec2a420373e6104e3db4e5c954d7001acda1c13eb348322215",
    ):
        raise ValueError("Chapter 4 target authority file mismatch")

    chapter_five = chapter_units[4]
    chapter_five_expected = {
        "source_bytes": 48838,
        "source_lines": 1147,
        "source_sha256": "93293a89c9a9f34315a43d6f114084490ceb370119fb09aeaccabe634efb96b1",
        "target_bytes": 51529,
        "target_lines": 1147,
        "target_sha256": "323f0b156eb6e945e3b6ed273da298af4e0e2b2d9abb73514a9018cbe0d0b29f",
        "course_role": "D20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 23,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch05.tex",
        "build_master_bytes": 9630,
        "build_master_lines": 330,
        "build_master_sha256": "2b8987e70b08b7b7045b50569667e0ab06634767645401a8c1d95712c48d80e2",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf",
        "artifact_bytes": 1271325,
        "artifact_pages": 90,
        "artifact_sha256": "850310f11cb7ab8c83cb52347aad43bc311cc1d2a811bef476038c61c8698af0",
        "qa_receipt_id": "QA-CH05-ADMISSION-20260822",
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH05_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "11ea57ad7a5f73f806846d7303246e7391b7c2aca37ce5a7fc2d53d7013b7ca5",
        "publication_state": "pending",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_five_expected.items():
        if chapter_five.get(field) != expected:
            raise ValueError(f"Chapter 5 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "Hilbert_space_operators.tex"
    target_path = ROOT / "source" / "id-ID" / "Hilbert_space_operators-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        48838,
        1147,
        "93293a89c9a9f34315a43d6f114084490ceb370119fb09aeaccabe634efb96b1",
    ):
        raise ValueError("Chapter 5 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        51529,
        1147,
        "323f0b156eb6e945e3b6ed273da298af4e0e2b2d9abb73514a9018cbe0d0b29f",
    ):
        raise ValueError("Chapter 5 target authority file mismatch")

    chapter_six = chapter_units[5]
    chapter_six_expected = {
        "source_bytes": 79549,
        "source_lines": 1605,
        "source_sha256": "0f401d088ec3e2d3f2ca4dafa2595a7f0049193a097b6b27af7b247fd433df51",
        "target_bytes": 82940,
        "target_lines": 1569,
        "target_sha256": "ca32547e4b47af3444d454476beac71ad8870e88b436dc008e1cb5dbb6755e9c",
        "course_role": "d20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 20,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch06.tex",
        "build_master_bytes": 9660,
        "build_master_lines": 333,
        "build_master_sha256": "92ab981f81488472f2c45271727b6652bfa62227533107725bff08f4416e738a",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-6.pdf",
        "artifact_bytes": 1468946,
        "artifact_pages": 114,
        "artifact_sha256": "93cfdf76515205ca259c91537a58cfa2b0ae7cab67e4b1b818ac9f5784aaa55c",
        "artifact_state": "canonical_output_copy_present_and_fixed_path_gate_passed",
        "qa_receipt_id": "QA-CH06-ADMISSION-20260822",
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH06_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "acc110923270c2918ca7aa1a6a2c839ae4c99504133e60c20d44a906b5830293",
        "publication_state": "pending",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_six_expected.items():
        if chapter_six.get(field) != expected:
            raise ValueError(f"Chapter 6 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "Banach_spaces.tex"
    target_path = ROOT / "source" / "id-ID" / "Banach_spaces-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        79549,
        1605,
        "0f401d088ec3e2d3f2ca4dafa2595a7f0049193a097b6b27af7b247fd433df51",
    ):
        raise ValueError("Chapter 6 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        82940,
        1569,
        "ca32547e4b47af3444d454476beac71ad8870e88b436dc008e1cb5dbb6755e9c",
    ):
        raise ValueError("Chapter 6 target authority file mismatch")

    chapter_seven = chapter_units[6]
    chapter_seven_expected = {
        "source_bytes": 21755,
        "source_lines": 517,
        "source_sha256": "a1f55b061f526f3e536e5a812f073781777b6f990b662f4a1dba07475152d663",
        "target_bytes": 22735,
        "target_lines": 517,
        "target_sha256": "8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a",
        "target_title": "Operator Kompak",
        "course_role": "d20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 11,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch07.tex",
        "build_master_bytes": 9691,
        "build_master_lines": 333,
        "build_master_sha256": "c639253fab59df7b51002058b414d8d64c92d77f12e95e88068decafd0d138b9",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-7.pdf",
        "artifact_bytes": 1530677,
        "artifact_pages": 121,
        "artifact_sha256": "a7ddaef324bd356d258cb47195f524e027ba54a696cb8d38a8358bb8d0a2d7ff",
        "artifact_state": "canonical_output_copy_present_and_fixed_path_gate_passed",
        "qa_receipt_id": "QA-CH07-ADMISSION-20260822",
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH07_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "8c9e7afa90c27a748de6b2f44c1725ed467ba7f8e4f3960a0009459a25b0b525",
        "publication_state": "pending",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_seven_expected.items():
        if chapter_seven.get(field) != expected:
            raise ValueError(f"Chapter 7 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "compact_operators.tex"
    target_path = ROOT / "source" / "id-ID" / "compact_operators-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        21755,
        517,
        "a1f55b061f526f3e536e5a812f073781777b6f990b662f4a1dba07475152d663",
    ):
        raise ValueError("Chapter 7 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        22735,
        517,
        "8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a",
    ):
        raise ValueError("Chapter 7 target authority file mismatch")

    expected_counts = {
        "units.jsonl": 18,
        "semantic_units.jsonl": 852,
        "segments.jsonl": 1032,
        "relations.jsonl": 3791,
        "formula_map.jsonl": 5847,
        "exercise_support.jsonl": 34,
        "artifacts.jsonl": 55,
        "qa_events.jsonl": 52,
        "corrections.jsonl": 122,
        "terminology.jsonl": 203,
    }
    for name, count in expected_counts.items():
        if len(records_by_file[name]) != count:
            raise ValueError(f"{name} expected {count}, got {len(records_by_file[name])}")
    if len(term_rows) != 1259:
        raise ValueError(f"index_terms.csv expected 1259 rows, got {len(term_rows)}")

    chapter_two_counts = {
        "semantic_units.jsonl": 34,
        "segments.jsonl": 41,
        "relations.jsonl": 121,
        "formula_map.jsonl": 397,
        "exercise_support.jsonl": 0,
    }
    for name, count in chapter_two_counts.items():
        actual = sum(record["id"].startswith("FAOA-2015-CH02-") for record in records_by_file[name])
        if actual != count:
            raise ValueError(f"{name} Chapter 2 expected {count}, got {actual}")
    chapter_two_terms = [row for row in term_rows if row["id"].startswith("FAOA-2015-CH02-")]
    if len(chapter_two_terms) != 137:
        raise ValueError("Chapter 2 index-term projection invariant failed")

    chapter_two_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH02-")
    ]
    chapter_two_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH02-")
    ]
    if any(
        record.get("translation_state") != "admitted" or record.get("qa_state") != "passed"
        for record in chapter_two_semantic + chapter_two_segments
    ):
        raise ValueError("Chapter 2 semantic/segment admission state is not reconciled")

    chapter_three_counts = {
        "semantic_units.jsonl": 184,
        "segments.jsonl": 228,
        "relations.jsonl": 703,
        "formula_map.jsonl": 1410,
        "exercise_support.jsonl": 7,
    }
    for name, count in chapter_three_counts.items():
        actual = sum(record["id"].startswith("FAOA-2015-CH03-") for record in records_by_file[name])
        if actual != count:
            raise ValueError(f"{name} Chapter 3 expected {count}, got {actual}")
    chapter_three_terms = [row for row in term_rows if row["id"].startswith("FAOA-2015-CH03-")]
    if len(chapter_three_terms) != 344:
        raise ValueError("Chapter 3 index-term projection invariant failed")
    chapter_three_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH03-")
    ]
    chapter_three_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH03-")
    ]
    if any(
        record.get("translation_state") != "admitted" or record.get("qa_state") != "passed"
        for record in chapter_three_semantic + chapter_three_segments
    ):
        raise ValueError("Chapter 3 semantic/segment admission state is not reconciled")

    chapter_four_counts = {
        "semantic_units.jsonl": 130,
        "segments.jsonl": 160,
        "relations.jsonl": 670,
        "formula_map.jsonl": 817,
        "exercise_support.jsonl": 10,
    }
    for name, count in chapter_four_counts.items():
        actual = sum(record["id"].startswith("FAOA-2015-CH04-") for record in records_by_file[name])
        if actual != count:
            raise ValueError(f"{name} Chapter 4 expected {count}, got {actual}")
    chapter_four_terms = [row for row in term_rows if row["id"].startswith("FAOA-2015-CH04-")]
    if len(chapter_four_terms) != 177:
        raise ValueError("Chapter 4 index-term projection invariant failed")
    chapter_four_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH04-")
    ]
    chapter_four_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH04-")
    ]
    if any(
        record.get("translation_state") != "admitted"
        or record.get("qa_state") != "passed"
        for record in chapter_four_semantic + chapter_four_segments
    ):
        raise ValueError("Chapter 4 semantic/segment admission state is not reconciled")

    chapter_five_counts = {
        "semantic_units.jsonl": 137,
        "segments.jsonl": 158,
        "relations.jsonl": 633,
        "formula_map.jsonl": 827,
        "exercise_support.jsonl": 4,
    }
    for name, count in chapter_five_counts.items():
        actual = sum(
            record["id"].startswith("FAOA-2015-CH05-")
            for record in records_by_file[name]
        )
        if actual != count:
            raise ValueError(f"{name} Chapter 5 expected {count}, got {actual}")
    chapter_five_terms = [
        row for row in term_rows if row["id"].startswith("FAOA-2015-CH05-")
    ]
    if len(chapter_five_terms) != 168:
        raise ValueError("Chapter 5 index-term projection invariant failed")
    chapter_five_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH05-")
    ]
    chapter_five_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH05-")
    ]
    if any(
        record.get("translation_state") != "admitted"
        or record.get("qa_state") != "passed"
        for record in chapter_five_semantic + chapter_five_segments
    ):
        raise ValueError("Chapter 5 semantic/segment admission state is not reconciled")

    chapter_six_counts = {
        "semantic_units.jsonl": 166,
        "segments.jsonl": 206,
        "relations.jsonl": 845,
        "formula_map.jsonl": 1156,
        "exercise_support.jsonl": 6,
    }
    for name, count in chapter_six_counts.items():
        actual = sum(
            record["id"].startswith("FAOA-2015-CH06-")
            for record in records_by_file[name]
        )
        if actual != count:
            raise ValueError(f"{name} Chapter 6 expected {count}, got {actual}")
    chapter_six_terms = [
        row for row in term_rows if row["id"].startswith("FAOA-2015-CH06-")
    ]
    if len(chapter_six_terms) != 155:
        raise ValueError("Chapter 6 index-term projection invariant failed")
    chapter_six_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH06-")
    ]
    chapter_six_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH06-")
    ]
    if any(
        record.get("translation_state") != "admitted"
        or record.get("qa_state") != "passed"
        for record in chapter_six_semantic + chapter_six_segments
    ):
        raise ValueError("Chapter 6 semantic/segment admission state is not reconciled")
    if [record["unit_kind"] for record in chapter_six_semantic].count("section") != 7:
        raise ValueError("Chapter 6 section count changed")
    expected_chapter_six_sections = [
        ("Natural Transformations", "Transformasi Alami"),
        ("Alaoglu's Theorem", "Teorema Alaoglu"),
        ("The Open Mapping Theorem", "Teorema Pemetaan Terbuka"),
        ("The Closed Graph Theorem", "Teorema Graf Tertutup"),
        ("Banach Space Duality", "Dualitas Ruang Banach"),
        ("Projections and Complemented Subspaces", "Proyeksi dan Subruang Terkomplemen"),
        ("The Principle of Uniform Boundedness", "Prinsip Keterbatasan Seragam"),
    ]
    chapter_six_sections = [
        (record.get("source_title_tex"), record.get("target_title_tex"))
        for record in chapter_six_semantic
        if record["unit_kind"] == "section"
    ]
    if chapter_six_sections != expected_chapter_six_sections:
        raise ValueError("Chapter 6 ordered section titles changed")

    chapter_seven_counts = {
        "semantic_units.jsonl": 74,
        "segments.jsonl": 85,
        "relations.jsonl": 349,
        "formula_map.jsonl": 309,
        "exercise_support.jsonl": 1,
    }
    for name, count in chapter_seven_counts.items():
        actual = sum(
            record["id"].startswith("FAOA-2015-CH07-")
            for record in records_by_file[name]
        )
        if actual != count:
            raise ValueError(f"{name} Chapter 7 expected {count}, got {actual}")
    chapter_seven_terms = [
        row for row in term_rows if row["id"].startswith("FAOA-2015-CH07-")
    ]
    if len(chapter_seven_terms) != 91:
        raise ValueError("Chapter 7 index-term projection invariant failed")
    chapter_seven_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH07-")
    ]
    chapter_seven_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH07-")
    ]
    if any(
        record.get("translation_state") != "admitted"
        or record.get("qa_state") != "passed"
        for record in chapter_seven_semantic + chapter_seven_segments
    ):
        raise ValueError("Chapter 7 semantic/segment admitted state is not reconciled")
    expected_chapter_seven_sections = [
        ("Definition and Elementary Properties", "Definisi dan Sifat-Sifat Dasar"),
        ("Partial Isometries", "Isometri Parsial"),
        ("Trace Class Operators", "Operator Kelas Jejak"),
        ("Hilbert-Schmidt Operators", "Operator Hilbert--Schmidt"),
    ]
    chapter_seven_sections = [
        (record.get("source_title_tex"), record.get("target_title_tex"))
        for record in chapter_seven_semantic
        if record["unit_kind"] == "section"
    ]
    if chapter_seven_sections != expected_chapter_seven_sections:
        raise ValueError("Chapter 7 ordered section titles changed")

    formula_records = records_by_file["formula_map.jsonl"]
    source_formula_count = sum(len(record["source_formula_ids"]) for record in formula_records)
    target_formula_count = sum(len(record["target_formula_ids"]) for record in formula_records)
    exact_alignment_kinds = {
        "preserved_exact_after_whitespace_normalization",
        "preserved_exact_after_text_aware_whitespace_normalization",
        "preserved_exact_after_text_aware_whitespace_normalization_reordered",
    }
    exact_formula_count = sum(record["alignment"] in exact_alignment_kinds for record in formula_records)
    if (source_formula_count, target_formula_count, exact_formula_count) != (5850, 5852, 5747):
        raise ValueError("combined formula-map coverage invariant failed")
    chapter_two_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH02-")
    ]
    chapter_two_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_two_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_two_formula),
        sum(
            record["alignment"] == "preserved_exact_after_whitespace_normalization"
            for record in chapter_two_formula
        ),
    )
    if chapter_two_formula_counts != (396, 397, 395):
        raise ValueError("Chapter 2 formula-map coverage invariant failed")
    chapter_two_deviations = [
        record for record in chapter_two_formula if record.get("sequence_opcode")
    ]
    if [record["sequence_opcode"] for record in chapter_two_deviations] != ["replace", "insert"]:
        raise ValueError("Chapter 2 formula deviations differ from replace+insert")
    if chapter_two_deviations[0]["id"] != "FAOA-2015-CH02-MATHMAP-0181":
        raise ValueError("Chapter 2 formula replacement stable ID changed")
    if chapter_two_deviations[1]["id"] != "FAOA-2015-CH02-MATHMAP-0386":
        raise ValueError("Chapter 2 formula insertion stable ID changed")

    chapter_three_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH03-")
    ]
    chapter_three_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_three_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_three_formula),
        sum(
            record["alignment"] == "preserved_exact_after_text_aware_whitespace_normalization"
            for record in chapter_three_formula
        ),
    )
    if chapter_three_formula_counts != (1414, 1414, 1394):
        raise ValueError("Chapter 3 formula-map coverage invariant failed")
    chapter_three_deviations = [
        record for record in chapter_three_formula if record.get("sequence_opcode")
    ]
    if len(chapter_three_deviations) != 16 or any(
        record["sequence_opcode"] != "replace" for record in chapter_three_deviations
    ):
        raise ValueError("Chapter 3 reviewed formula-deviation inventory changed")

    chapter_four_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH04-")
    ]
    chapter_four_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_four_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_four_formula),
        sum(record["alignment"] in exact_alignment_kinds for record in chapter_four_formula),
        sum(record.get("math_key_alignment") == "equal" for record in chapter_four_formula),
    )
    if chapter_four_formula_counts != (817, 817, 802, 807):
        raise ValueError("Chapter 4 formula-map coverage invariant failed")
    chapter_four_alignment_counts = {
        alignment: sum(record["alignment"] == alignment for record in chapter_four_formula)
        for alignment in {
            "preserved_exact_after_text_aware_whitespace_normalization",
            "preserved_exact_after_text_aware_whitespace_normalization_reordered",
            "localized_math_text_preserved_math_key",
            "localized_math_key_reviewed",
            "reviewed_source_correction",
        }
    }
    if chapter_four_alignment_counts != {
        "preserved_exact_after_text_aware_whitespace_normalization": 787,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 15,
        "localized_math_text_preserved_math_key": 5,
        "localized_math_key_reviewed": 1,
        "reviewed_source_correction": 9,
    }:
        raise ValueError("Chapter 4 reviewed formula-alignment inventory changed")
    if any(
        len(record["source_formula_ids"]) != 1 or len(record["target_formula_ids"]) != 1
        for record in chapter_four_formula
    ):
        raise ValueError("Chapter 4 formula map is not one-to-one")

    chapter_five_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH05-")
    ]
    chapter_five_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_five_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_five_formula),
        sum(record["alignment"] in exact_alignment_kinds for record in chapter_five_formula),
        sum(record.get("math_key_alignment") == "equal" for record in chapter_five_formula),
    )
    if chapter_five_formula_counts != (827, 827, 816, 821):
        raise ValueError("Chapter 5 formula-map coverage invariant failed")
    chapter_five_alignment_counts = {
        alignment: sum(record["alignment"] == alignment for record in chapter_five_formula)
        for alignment in {
            "preserved_exact_after_text_aware_whitespace_normalization",
            "localized_math_text_preserved_math_key",
            "reviewed_source_correction",
        }
    }
    if chapter_five_alignment_counts != {
        "preserved_exact_after_text_aware_whitespace_normalization": 816,
        "localized_math_text_preserved_math_key": 5,
        "reviewed_source_correction": 6,
    }:
        raise ValueError("Chapter 5 reviewed formula-alignment inventory changed")
    chapter_five_deviations = [
        record for record in chapter_five_formula if record.get("sequence_opcode")
    ]
    if [record["id"] for record in chapter_five_deviations] != [
        "FAOA-2015-CH05-MATHMAP-0104",
        "FAOA-2015-CH05-MATHMAP-0304",
        "FAOA-2015-CH05-MATHMAP-0550",
        "FAOA-2015-CH05-MATHMAP-0553",
        "FAOA-2015-CH05-MATHMAP-0639",
        "FAOA-2015-CH05-MATHMAP-0810",
    ] or any(record.get("sequence_opcode") != "replace" for record in chapter_five_deviations):
        raise ValueError("Chapter 5 locked formula-correction IDs changed")
    if any(
        len(record["source_formula_ids"]) != 1
        or len(record["target_formula_ids"]) != 1
        or record.get("ordinal_alignment") != "same"
        for record in chapter_five_formula
    ):
        raise ValueError("Chapter 5 formula map is not one-to-one and same-ordinal")

    chapter_six_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH06-")
    ]
    chapter_six_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_six_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_six_formula),
        sum(record["alignment"] in exact_alignment_kinds for record in chapter_six_formula),
        sum(record.get("math_key_alignment") == "equal" for record in chapter_six_formula),
    )
    if chapter_six_formula_counts != (1155, 1156, 1131, 1138):
        raise ValueError("Chapter 6 formula-map coverage invariant failed")
    chapter_six_alignment_counts = {
        alignment: sum(record["alignment"] == alignment for record in chapter_six_formula)
        for alignment in {
            "preserved_exact_after_text_aware_whitespace_normalization",
            "preserved_exact_after_text_aware_whitespace_normalization_reordered",
            "localized_math_text_preserved_math_key",
            "localized_math_key_reviewed",
            "reviewed_source_correction",
            "reviewed_target_only_source_correction",
            "reviewed_consolidated_source_correction",
        }
    }
    if chapter_six_alignment_counts != {
        "preserved_exact_after_text_aware_whitespace_normalization": 1128,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 3,
        "localized_math_text_preserved_math_key": 7,
        "localized_math_key_reviewed": 6,
        "reviewed_source_correction": 9,
        "reviewed_target_only_source_correction": 2,
        "reviewed_consolidated_source_correction": 1,
    }:
        raise ValueError("Chapter 6 reviewed formula-alignment inventory changed")
    source_formula_ids = [
        formula_id
        for record in chapter_six_formula
        for formula_id in record["source_formula_ids"]
    ]
    target_formula_ids = [
        formula_id
        for record in chapter_six_formula
        for formula_id in record["target_formula_ids"]
    ]
    if sorted(source_formula_ids) != [
        f"FAOA-2015-CH06-SRC-MATH-{number:04d}" for number in range(1, 1156)
    ] or target_formula_ids != [
        f"FAOA-2015-CH06-ID-MATH-{number:04d}" for number in range(1, 1157)
    ]:
        raise ValueError("Chapter 6 stable source/target formula coverage changed")
    correction_formula_ids = {
        165: "FAOA-2015-CH06-CORR-003",
        167: "FAOA-2015-CH06-CORR-003",
        316: "FAOA-2015-CH06-CORR-006",
        330: "FAOA-2015-CH06-CORR-007",
        531: "FAOA-2015-CH06-CORR-010",
        686: "FAOA-2015-CH06-CORR-011",
        710: "FAOA-2015-CH06-CORR-012",
        894: "FAOA-2015-CH06-CORR-013",
        927: "FAOA-2015-CH06-CORR-015",
        965: "FAOA-2015-CH06-CORR-016",
        1065: "FAOA-2015-CH06-CORR-018",
        1093: "FAOA-2015-CH06-CORR-019",
    }
    if {
        int(record["id"].rsplit("-", 1)[1]): record.get("correction_id")
        for record in chapter_six_formula
        if record.get("correction_id")
    } != correction_formula_ids:
        raise ValueError("Chapter 6 formula-to-correction binding changed")
    if [
        int(record["id"].rsplit("-", 1)[1])
        for record in chapter_six_formula
        if record.get("sequence_opcode") == "reorder"
    ] != [834, 857, 906]:
        raise ValueError("Chapter 6 localization-only formula reorderings changed")
    if any(
        record.get("correction_id")
        for record in chapter_six_formula
        if record.get("delta_class") == "localized_math_text"
        or record.get("delta_class") == "localization_phrase_reordering"
    ):
        raise ValueError("Chapter 6 localization-only math deltas became corrections")

    chapter_seven_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH07-")
    ]
    chapter_seven_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_seven_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_seven_formula),
        sum(record["alignment"] in exact_alignment_kinds for record in chapter_seven_formula),
        sum(record.get("math_key_alignment") == "equal" for record in chapter_seven_formula),
    )
    if chapter_seven_formula_counts != (309, 309, 303, 303):
        raise ValueError("Chapter 7 formula-map coverage invariant failed")
    chapter_seven_alignment_counts = {
        alignment: sum(record["alignment"] == alignment for record in chapter_seven_formula)
        for alignment in {
            "preserved_exact_after_text_aware_whitespace_normalization",
            "preserved_exact_after_text_aware_whitespace_normalization_reordered",
            "reviewed_source_correction",
            "reviewed_target_only_source_correction",
            "reviewed_consolidated_source_correction",
        }
    }
    if chapter_seven_alignment_counts != {
        "preserved_exact_after_text_aware_whitespace_normalization": 300,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 3,
        "reviewed_source_correction": 4,
        "reviewed_target_only_source_correction": 1,
        "reviewed_consolidated_source_correction": 1,
    }:
        raise ValueError("Chapter 7 reviewed formula-alignment inventory changed")
    chapter_seven_source_formula_ids = [
        formula_id
        for record in chapter_seven_formula
        for formula_id in record["source_formula_ids"]
    ]
    chapter_seven_target_formula_ids = [
        formula_id
        for record in chapter_seven_formula
        for formula_id in record["target_formula_ids"]
    ]
    if sorted(chapter_seven_source_formula_ids) != [
        f"FAOA-2015-CH07-SRC-MATH-{number:04d}" for number in range(1, 310)
    ] or chapter_seven_target_formula_ids != [
        f"FAOA-2015-CH07-ID-MATH-{number:04d}" for number in range(1, 310)
    ]:
        raise ValueError("Chapter 7 stable source/target formula coverage changed")
    chapter_seven_correction_formula_ids = {
        69: "FAOA-2015-CH07-CORR-004",
        249: "FAOA-2015-CH07-CORR-007",
        263: "FAOA-2015-CH07-CORR-008",
        267: "FAOA-2015-CH07-CORR-009",
        275: "FAOA-2015-CH07-CORR-010",
        309: "FAOA-2015-CH07-CORR-011",
    }
    if {
        int(record["id"].rsplit("-", 1)[1]): record.get("correction_id")
        for record in chapter_seven_formula
        if record.get("correction_id")
    } != chapter_seven_correction_formula_ids:
        raise ValueError("Chapter 7 formula-to-correction binding changed")
    if [
        int(record["id"].rsplit("-", 1)[1])
        for record in chapter_seven_formula
        if record.get("sequence_opcode") == "reorder"
    ] != [91, 92, 93]:
        raise ValueError("Chapter 7 localization-only formula reorderings changed")
    if any(
        record.get("correction_id")
        for record in chapter_seven_formula
        if record.get("delta_class") == "localization_phrase_reordering"
    ):
        raise ValueError("Chapter 7 localization-only formula reorderings became corrections")

    chapter_two_xrefs = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH02-REL-XREF-")
    ]
    if [(record["source_local_id"], record["resolution"]) for record in chapter_two_xrefs] != [
        ("C069414", "pending_later_source_unit"),
        ("C015127", "local"),
    ]:
        raise ValueError("Chapter 2 xref resolution invariant failed")
    if chapter_two_xrefs[0]["to_id"] != "ERDMAN-FAOA-2015-LABEL-C069414":
        raise ValueError("Chapter 2 future xref endpoint changed")
    if chapter_two_xrefs[1]["to_id"] not in ids:
        raise ValueError("Chapter 2 local xref endpoint is unresolved")

    chapter_three_xrefs = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH03-REL-XREF-")
    ]
    resolution_counts = {
        resolution: sum(record["resolution"] == resolution for record in chapter_three_xrefs)
        for resolution in ("local", "admitted_prior_unit", "pending_later_source_unit")
    }
    if len(chapter_three_xrefs) != 47 or resolution_counts != {
        "local": 39,
        "admitted_prior_unit": 7,
        "pending_later_source_unit": 1,
    }:
        raise ValueError("Chapter 3 reference-resolution inventory changed")
    future_xrefs = [
        record for record in chapter_three_xrefs if record["resolution"] == "pending_later_source_unit"
    ]
    if (
        future_xrefs[0].get("source_local_id") != "exam_ran_nonclosed"
        or future_xrefs[0].get("to_id") != "ERDMAN-FAOA-2015-LABEL-exam_ran_nonclosed"
    ):
        raise ValueError("Chapter 3 future reference endpoint changed")
    if any(
        record["to_id"] not in ids
        for record in chapter_three_xrefs
        if record["resolution"] != "pending_later_source_unit"
    ):
        raise ValueError("Chapter 3 admitted reference endpoint is unresolved")
    chapter_three_eqrefs = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH03-REL-EQREF-")
    ]
    if len(chapter_three_eqrefs) != 1 or chapter_three_eqrefs[0].get("source_local_id") != "eq_HBTI":
        raise ValueError("Chapter 3 equation-reference invariant failed")

    chapter_four_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH04-")
    ]
    chapter_four_xrefs = [
        record
        for record in chapter_four_relations
        if record["id"].startswith("FAOA-2015-CH04-REL-XREF-")
    ]
    chapter_four_resolution_counts = {
        resolution: sum(record["resolution"] == resolution for record in chapter_four_xrefs)
        for resolution in ("local", "admitted_prior_unit", "pending_later_source_unit")
    }
    if len(chapter_four_xrefs) != 51 or chapter_four_resolution_counts != {
        "local": 27,
        "admitted_prior_unit": 23,
        "pending_later_source_unit": 1,
    }:
        raise ValueError("Chapter 4 reference-resolution inventory changed")
    chapter_four_future = [
        record
        for record in chapter_four_xrefs
        if record["resolution"] == "pending_later_source_unit"
    ]
    if (
        chapter_four_future[0].get("source_local_id") != "C067441"
        or chapter_four_future[0].get("to_id") != "ERDMAN-FAOA-2015-LABEL-C067441"
        or chapter_four_future[0].get("target_surface") != "futurexref"
    ):
        raise ValueError("Chapter 4 future reference endpoint changed")
    if any(
        record["to_id"] not in ids
        for record in chapter_four_xrefs
        if record["resolution"] != "pending_later_source_unit"
    ):
        raise ValueError("Chapter 4 admitted/local reference endpoint is unresolved")
    chapter_four_eqrefs = [
        record
        for record in chapter_four_relations
        if record["id"].startswith("FAOA-2015-CH04-REL-EQREF-")
    ]
    if len(chapter_four_eqrefs) != 2 or any(
        record.get("source_local_id") != "00078i"
        or record.get("resolution") != "local"
        or record.get("to_id") not in ids
        for record in chapter_four_eqrefs
    ):
        raise ValueError("Chapter 4 equation-reference invariant failed")
    chapter_four_relation_type_counts = {
        relation_type: sum(record["relation_type"] == relation_type for record in chapter_four_relations)
        for relation_type in {
            "contains",
            "translates",
            "precedes",
            "declares_label",
            "xref",
            "cites",
            "hints",
            "uses_term",
            "licensed_under",
            "has_artifact",
            "terminology_evidence",
            "has_qa_event",
            "documents_correction",
        }
    }
    if chapter_four_relation_type_counts != {
        "contains": 130,
        "translates": 160,
        "precedes": 159,
        "declares_label": 44,
        "xref": 53,
        "cites": 12,
        "hints": 11,
        "uses_term": 59,
        "licensed_under": 1,
        "has_artifact": 9,
        "terminology_evidence": 2,
        "has_qa_event": 8,
        "documents_correction": 22,
    }:
        raise ValueError("Chapter 4 relation-type inventory changed")
    chapter_four_term_evidence = [
        record
        for record in chapter_four_relations
        if record.get("relation_type") == "terminology_evidence"
    ]
    if [
        (record["id"], record["to_id"]) for record in chapter_four_term_evidence
    ] != [
        (
            "FAOA-2015-CH04-REL-TERM-EVIDENCE-0001",
            "ARTIFACT-FAOA-ID-CH04-TARGET-TEX",
        ),
        (
            "FAOA-2015-CH04-REL-TERM-EVIDENCE-0002",
            "ARTIFACT-FAOA-ID-CH04-QA-RECEIPT",
        ),
    ]:
        raise ValueError("Chapter 4 public terminology-evidence links changed")

    chapter_five_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH05-")
    ]
    chapter_five_xrefs = [
        record
        for record in chapter_five_relations
        if record["id"].startswith("FAOA-2015-CH05-REL-XREF-")
    ]
    chapter_five_resolution_counts = {
        resolution: sum(record["resolution"] == resolution for record in chapter_five_xrefs)
        for resolution in ("local", "admitted_prior_unit", "pending_later_source_unit")
    }
    if len(chapter_five_xrefs) != 24 or chapter_five_resolution_counts != {
        "local": 13,
        "admitted_prior_unit": 10,
        "pending_later_source_unit": 1,
    }:
        raise ValueError("Chapter 5 reference-resolution inventory changed")
    chapter_five_future = [
        record
        for record in chapter_five_xrefs
        if record["resolution"] == "pending_later_source_unit"
    ]
    if [
        (
            record.get("source_local_id"),
            record.get("to_id"),
            record.get("target_surface"),
        )
        for record in chapter_five_future
    ] != [
        (
            "chap_cpt_ops",
            "ERDMAN-FAOA-2015-LABEL-chap_cpt_ops",
            "futurexref",
        )
    ]:
        raise ValueError("Chapter 5 future reference endpoint changed")
    section_reference = next(
        record
        for record in chapter_five_xrefs
        if record.get("source_local_id") == "sec_bdd_lin_maps"
    )
    if (
        section_reference.get("resolution") != "admitted_prior_unit"
        or section_reference.get("to_id")
        != "ERDMAN-FAOA-2015-LABEL-sec_bdd_lin_maps"
    ):
        raise ValueError("Chapter 5 prior section reference endpoint changed")
    if any(
        record["to_id"] not in ids
        for record in chapter_five_xrefs
        if record["resolution"] == "local"
    ):
        raise ValueError("Chapter 5 local reference endpoint is unresolved")
    chapter_five_eqrefs = [
        record
        for record in chapter_five_relations
        if record["id"].startswith("FAOA-2015-CH05-REL-EQREF-")
    ]
    if len(chapter_five_eqrefs) != 1 or any(
        record.get("source_local_id") != "num_ran_saop_eqn2"
        or record.get("resolution") != "local"
        or record.get("to_id") not in ids
        for record in chapter_five_eqrefs
    ):
        raise ValueError("Chapter 5 equation-reference invariant failed")
    chapter_five_relation_type_counts = {
        relation_type: sum(
            record["relation_type"] == relation_type for record in chapter_five_relations
        )
        for relation_type in {
            "contains",
            "translates",
            "precedes",
            "declares_label",
            "xref",
            "cites",
            "hints",
            "uses_term",
            "licensed_under",
            "has_artifact",
            "terminology_evidence",
            "has_qa_event",
            "documents_correction",
        }
    }
    if chapter_five_relation_type_counts != {
        "contains": 137,
        "translates": 158,
        "precedes": 157,
        "declares_label": 39,
        "xref": 25,
        "cites": 1,
        "hints": 17,
        "uses_term": 56,
        "licensed_under": 1,
        "has_artifact": 9,
        "terminology_evidence": 2,
        "has_qa_event": 8,
        "documents_correction": 23,
    }:
        raise ValueError("Chapter 5 relation-type inventory changed")
    chapter_five_term_evidence = [
        record
        for record in chapter_five_relations
        if record.get("relation_type") == "terminology_evidence"
    ]
    if [(record["id"], record["to_id"]) for record in chapter_five_term_evidence] != [
        (
            "FAOA-2015-CH05-REL-TERM-EVIDENCE-0001",
            "ARTIFACT-FAOA-ID-CH05-TARGET-TEX",
        ),
        (
            "FAOA-2015-CH05-REL-TERM-EVIDENCE-0002",
            "ARTIFACT-FAOA-ID-CH05-STRUCTURAL-CHECKER",
        ),
    ]:
        raise ValueError("Chapter 5 public terminology-evidence links changed")

    chapter_six_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH06-")
    ]
    chapter_six_relation_type_counts = {
        relation_type: sum(
            record["relation_type"] == relation_type for record in chapter_six_relations
        )
        for relation_type in {
            "contains",
            "translates",
            "precedes",
            "declares_label",
            "xref",
            "cites",
            "hints",
            "uses_term",
            "resolves_pending_reference",
            "licensed_under",
            "has_artifact",
            "terminology_evidence",
            "has_qa_event",
            "documents_correction",
        }
    }
    if chapter_six_relation_type_counts != {
        "contains": 166,
        "translates": 206,
        "precedes": 205,
        "declares_label": 56,
        "xref": 82,
        "cites": 13,
        "hints": 28,
        "uses_term": 47,
        "resolves_pending_reference": 2,
        "licensed_under": 1,
        "has_artifact": 9,
        "terminology_evidence": 2,
        "has_qa_event": 8,
        "documents_correction": 20,
    }:
        raise ValueError("Chapter 6 relation-type inventory changed")
    chapter_six_xrefs = [
        record
        for record in chapter_six_relations
        if record["id"].startswith("FAOA-2015-CH06-REL-XREF-")
    ]
    chapter_six_resolution_counts = {
        resolution: sum(record["resolution"] == resolution for record in chapter_six_xrefs)
        for resolution in ("local", "admitted_prior_unit", "pending_later_source_unit")
    }
    if len(chapter_six_xrefs) != 80 or chapter_six_resolution_counts != {
        "local": 47,
        "admitted_prior_unit": 32,
        "pending_later_source_unit": 1,
    }:
        raise ValueError("Chapter 6 reference-resolution inventory changed")
    chapter_six_future = [
        record
        for record in chapter_six_xrefs
        if record["resolution"] == "pending_later_source_unit"
    ]
    if [
        (
            record.get("source_local_id"),
            record.get("to_id"),
            record.get("target_surface"),
        )
        for record in chapter_six_future
    ] != [("000731", "ERDMAN-FAOA-2015-LABEL-000731", "futurexref")]:
        raise ValueError("Chapter 6 future reference endpoint changed")
    if any(
        record["to_id"] not in ids
        for record in chapter_six_xrefs
        if record["resolution"] != "pending_later_source_unit"
    ):
        raise ValueError("Chapter 6 admitted/local reference endpoint is unresolved")
    chapter_six_eqrefs = [
        record
        for record in chapter_six_relations
        if record["id"].startswith("FAOA-2015-CH06-REL-EQREF-")
    ]
    if len(chapter_six_eqrefs) != 2 or any(
        record.get("source_local_id") != "eqn_exactCD_Bbar"
        or record.get("resolution") != "local"
        or record.get("to_id") not in ids
        for record in chapter_six_eqrefs
    ):
        raise ValueError("Chapter 6 equation-reference invariant failed")
    pending_closures = [
        record
        for record in chapter_six_relations
        if record.get("relation_type") == "resolves_pending_reference"
    ]
    if [
        (record.get("source_local_id"), record.get("to_id"), record.get("resolution"))
        for record in pending_closures
    ] != [
        ("C069414", "FAOA-2015-CH02-REL-XREF-0001", "declared_in_current_unit"),
        ("C067441", "FAOA-2015-CH04-REL-XREF-0034", "declared_in_current_unit"),
    ] or any(record.get("from_id") not in ids for record in pending_closures):
        raise ValueError("Chapter 6 append-only prior-xref closure changed")
    chapter_six_term_evidence = [
        record
        for record in chapter_six_relations
        if record.get("relation_type") == "terminology_evidence"
    ]
    if [(record["id"], record["to_id"]) for record in chapter_six_term_evidence] != [
        (
            "FAOA-2015-CH06-REL-TERM-EVIDENCE-0001",
            "ARTIFACT-FAOA-ID-CH06-TARGET-TEX",
        ),
        (
            "FAOA-2015-CH06-REL-TERM-EVIDENCE-0002",
            "ARTIFACT-FAOA-ID-CH06-STRUCTURAL-CHECKER",
        ),
    ]:
        raise ValueError("Chapter 6 terminology-evidence links changed")

    artifact_records = records_by_file["artifacts.jsonl"]
    chapter_two_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH02"
    ]
    expected_chapter_two_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH02-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH02-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH02-PDF",
        "ARTIFACT-FAOA-ID-CH02-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH02-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH02-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH02-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_two_artifacts] != expected_chapter_two_artifact_ids:
        raise ValueError("Chapter 2 admitted artifact inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH02-ADMISSION-20260821"
        for record in chapter_two_artifacts
    ):
        raise ValueError("Chapter 2 artifacts are not bound to the admission receipt")
    chapter_three_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH03"
    ]
    expected_chapter_three_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH03-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH03-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH03-PDF",
        "ARTIFACT-FAOA-ID-CH03-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH03-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH03-MATH-EXTRACTOR",
        "ARTIFACT-FAOA-ID-CH03-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH03-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH03-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_three_artifacts] != expected_chapter_three_artifact_ids:
        raise ValueError("Chapter 3 admitted artifact inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH03-ADMISSION-20260821"
        for record in chapter_three_artifacts
    ):
        raise ValueError("Chapter 3 artifacts are not bound to the admission receipt")
    chapter_four_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH04"
    ]
    expected_chapter_four_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH04-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH04-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH04-PDF",
        "ARTIFACT-FAOA-ID-CH04-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH04-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH04-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH04-VISUAL-ACCESSIBILITY-AUDIT",
        "ARTIFACT-FAOA-ID-CH04-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH04-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_four_artifacts] != expected_chapter_four_artifact_ids:
        raise ValueError("Chapter 4 admitted artifact inventory changed")
    if len(chapter_four_artifacts) != 9 or any(
        record.get("path", "").startswith("00_control/") for record in chapter_four_artifacts
    ):
        raise ValueError("Chapter 4 public artifact closure includes a private control")
    if any(
        record.get("qa_receipt_id") != "QA-CH04-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        for record in chapter_four_artifacts
    ):
        raise ValueError("Chapter 4 artifacts are not bound to the admission receipt")
    accessibility_artifact = chapter_four_artifacts[6]
    if (
        accessibility_artifact.get("visual_result") != "pass"
        or accessibility_artifact.get("fully_accessible_pdf_claim") != "fail"
        or accessibility_artifact.get("accessible_html_or_tagged_pdf_state") != "pending"
    ):
        raise ValueError("Chapter 4 accessibility limitation is not represented honestly")
    chapter_five_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH05"
    ]
    expected_chapter_five_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH05-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH05-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH05-PDF",
        "ARTIFACT-FAOA-ID-CH05-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH05-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH05-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH05-VISUAL-ACCESSIBILITY-AUDIT",
        "ARTIFACT-FAOA-ID-CH05-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH05-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_five_artifacts] != expected_chapter_five_artifact_ids:
        raise ValueError("Chapter 5 admitted artifact inventory changed")
    if len(chapter_five_artifacts) != 9 or any(
        record.get("path", "").startswith(("00_control/", "qa/build-through-ch05/"))
        for record in chapter_five_artifacts
    ):
        raise ValueError("Chapter 5 public artifact closure includes a private/local path")
    if any(
        record.get("qa_receipt_id") != "QA-CH05-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH05_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "11ea57ad7a5f73f806846d7303246e7391b7c2aca37ce5a7fc2d53d7013b7ca5"
        for record in chapter_five_artifacts
    ):
        raise ValueError("Chapter 5 artifacts are not bound to the exact admission receipt")
    chapter_five_accessibility_artifact = chapter_five_artifacts[6]
    if (
        chapter_five_accessibility_artifact.get("visual_result") != "pass"
        or chapter_five_accessibility_artifact.get("fully_accessible_pdf_claim") != "fail"
        or chapter_five_accessibility_artifact.get("accessibility_remediation_state")
        != "partial_nonblocking"
        or chapter_five_accessibility_artifact.get("accessible_html_or_tagged_pdf_state")
        != "pending"
    ):
        raise ValueError("Chapter 5 accessibility limitation is not represented honestly")

    chapter_six_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH06"
    ]
    expected_chapter_six_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH06-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH06-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH06-PDF",
        "ARTIFACT-FAOA-ID-CH06-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH06-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH06-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH06-VISUAL-ACCESSIBILITY-AUDIT",
        "ARTIFACT-FAOA-ID-CH06-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH06-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_six_artifacts] != expected_chapter_six_artifact_ids:
        raise ValueError("Chapter 6 artifact inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH06-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH06_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "acc110923270c2918ca7aa1a6a2c839ae4c99504133e60c20d44a906b5830293"
        for record in chapter_six_artifacts
    ):
        raise ValueError("Chapter 6 artifacts are not bound to the admission receipt")
    chapter_six_actual_artifacts = {
        record["id"]: (record.get("path"), record.get("bytes"), record.get("sha256"))
        for record in chapter_six_artifacts
        if record.get("path")
    }
    if chapter_six_actual_artifacts != {
        "ARTIFACT-FAOA-ID-CH06-TARGET-TEX": (
            "source/id-ID/Banach_spaces-id.tex",
            82940,
            "ca32547e4b47af3444d454476beac71ad8870e88b436dc008e1cb5dbb6755e9c",
        ),
        "ARTIFACT-FAOA-ID-THROUGH-CH06-MASTER": (
            "source/id-ID/functional-analysis-id-through-ch06.tex",
            9660,
            "92ab981f81488472f2c45271727b6652bfa62227533107725bff08f4416e738a",
        ),
        "ARTIFACT-FAOA-ID-THROUGH-CH06-PDF": (
            "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-6.pdf",
            1468946,
            "93cfdf76515205ca259c91537a58cfa2b0ae7cab67e4b1b818ac9f5784aaa55c",
        ),
        "ARTIFACT-FAOA-ID-CH06-STRUCTURAL-CHECKER": (
            "qa/check_ch06_translation.py",
            15728,
            "88412b9799d25e3342894dfb2ecba7e3a90d59232c837ef6d0913689c6778391",
        ),
        "ARTIFACT-FAOA-ID-CH06-RENDER-MANIFEST": (
            "provenance/CH06_RENDER_MANIFEST.csv",
            22218,
            "ba63bc106be574414792ac6bc37b76483a01491822fca4745962e8ff9e407db8",
        ),
        "ARTIFACT-FAOA-ID-CH06-CONTACT-SHEET": (
            "provenance/CH06_CONTACT_SHEET.png",
            3339772,
            "1b5aaad85c2c13651c51d92d6452eb21fca892b641abe87c3991e95bc4f1bedf",
        ),
        "ARTIFACT-FAOA-ID-CH06-VISUAL-ACCESSIBILITY-AUDIT": (
            "qa/CH06_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
            5197,
            "3da448996dba97de722ccc48eaa7590a5a9d2f462dcaa4766aecd153139d528b",
        ),
        "ARTIFACT-FAOA-ID-CH06-QA-RECEIPT": (
            "provenance/CH06_BUILD_AND_QA_RECEIPT.md",
            9867,
            "acc110923270c2918ca7aa1a6a2c839ae4c99504133e60c20d44a906b5830293",
        ),
        "ARTIFACT-FAOA-ID-CH06-CORRECTIONS-LEDGER": (
            "provenance/SOURCE_CORRECTIONS.md",
            20716,
            "7de8a5892b865af84c9f5d1d4c37ec6b3112b3e099685dae243108006dc94b01",
        ),
    }:
        raise ValueError("Chapter 6 bound artifact identities changed")
    chapter_six_accessibility_artifact = chapter_six_artifacts[6]
    if (
        chapter_six_accessibility_artifact.get("visual_result") != "pass"
        or chapter_six_accessibility_artifact.get("accessibility_gate_result") != "pass"
        or chapter_six_accessibility_artifact.get("fully_accessible_pdf_claim") != "fail"
        or chapter_six_accessibility_artifact.get("tagged_pdf") is not False
        or chapter_six_accessibility_artifact.get("accessibility_remediation_state")
        != "pending_nonblocking"
        or chapter_six_accessibility_artifact.get("accessible_html_or_tagged_pdf_state")
        != "pending"
    ):
        raise ValueError("Chapter 6 accessibility limitation is not represented honestly")
    if (
        chapter_six_artifacts[7].get("decision") != "admitted"
        or chapter_six_artifacts[7].get("lines") != 178
    ):
        raise ValueError("Chapter 6 admission-receipt artifact metadata changed")

    for artifact in artifact_records:
        if "path" not in artifact:
            if (
                artifact.get("unit_id") == "FAOA-2015-CH06"
                and artifact.get("path_state") == "pending_assignment"
            ):
                continue
            raise ValueError(f"artifact without a path is not an admitted placeholder: {artifact['id']}")
        path = ROOT / artifact["path"]
        if not path.is_file():
            raise ValueError(f"missing artifact {artifact['path']}")
        if artifact.get("artifact_kind") == "source_corrections_ledger":
            data = path.read_bytes()
            historical_size = artifact["bytes"]
            if len(data) < historical_size or sha_bytes(data[:historical_size]) != artifact["sha256"]:
                raise ValueError(f"append-only artifact prefix mismatch {artifact['id']}")
            continue
        if path.stat().st_size != artifact["bytes"] or sha(path) != artifact["sha256"]:
            raise ValueError(f"artifact mismatch {artifact['id']}")

    chapter_two_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH02"
    ]
    expected_chapter_two_qa_ids = [
        "QA-CH02-STRUCTURAL-20260821",
        "QA-CH02-MATH-20260821",
        "QA-CH02-LANGUAGE-20260821",
        "QA-CH02-BUILD-20260821",
        "QA-CH02-VISUAL-20260821",
        "QA-CH02-RIGHTS-20260821",
        "QA-CH02-ADMISSION-20260821",
    ]
    expected_chapter_two_qa_types = [
        "unit_structural",
        "unit_mathematical",
        "unit_language",
        "cumulative_build",
        "cumulative_visual",
        "unit_rights_privacy",
        "unit_admission",
    ]
    if [record["id"] for record in chapter_two_qa] != expected_chapter_two_qa_ids:
        raise ValueError("Chapter 2 typed QA event inventory changed")
    if [record["qa_type"] for record in chapter_two_qa] != expected_chapter_two_qa_types:
        raise ValueError("Chapter 2 typed QA event kinds changed")
    if any(
        record.get("result") != "pass"
        or record.get("witness") != "provenance/CH02_BUILD_AND_QA_RECEIPT.md"
        or record.get("witness_sha256")
        != "4acd8a6e7942a8f57ad8442e9fca2fb68d041904962e18ed588704bc2098175f"
        for record in chapter_two_qa
    ):
        raise ValueError("Chapter 2 QA events are not bound to the exact passed receipt")
    admission = chapter_two_qa[-1]
    if (
        admission.get("decision") != "admitted"
        or admission.get("all_required_gates") != "pass"
        or admission.get("typed_qa_event_ids") != expected_chapter_two_qa_ids[:-1]
        or admission.get("receipt_sha256")
        != "4acd8a6e7942a8f57ad8442e9fca2fb68d041904962e18ed588704bc2098175f"
    ):
        raise ValueError("Chapter 2 admission event is incomplete")

    chapter_three_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH03"
    ]
    expected_chapter_three_qa_ids = [
        "QA-CH03-STRUCTURAL-20260821",
        "QA-CH03-MATH-20260821",
        "QA-CH03-LANGUAGE-20260821",
        "QA-CH03-BUILD-20260821",
        "QA-CH03-VISUAL-20260821",
        "QA-CH03-RIGHTS-20260821",
        "QA-CH03-ADMISSION-20260821",
    ]
    expected_chapter_three_qa_types = [
        "unit_structural",
        "unit_mathematical",
        "unit_language",
        "cumulative_build",
        "cumulative_visual",
        "unit_rights_privacy",
        "unit_admission",
    ]
    if [record["id"] for record in chapter_three_qa] != expected_chapter_three_qa_ids:
        raise ValueError("Chapter 3 typed QA event inventory changed")
    if [record["qa_type"] for record in chapter_three_qa] != expected_chapter_three_qa_types:
        raise ValueError("Chapter 3 typed QA event kinds changed")
    if any(
        record.get("result") != "pass"
        or record.get("qa_receipt_id") != "QA-CH03-ADMISSION-20260821"
        or record.get("receipt_path") != "provenance/CH03_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a"
        for record in chapter_three_qa
    ):
        raise ValueError("Chapter 3 QA events are not bound to the exact passed receipt")
    structural_event = chapter_three_qa[0]
    if (
        structural_event.get("references") != 48
        or structural_event.get("ordinary_target_references") != 46
        or structural_event.get("future_target_references") != 1
        or structural_event.get("equation_references") != 1
    ):
        raise ValueError("Chapter 3 reference-surface metadata is inconsistent")
    math_event = chapter_three_qa[1]
    if (
        math_event.get("source_math_surfaces") != 1414
        or math_event.get("target_math_surfaces") != 1414
        or math_event.get("exact_normalized_alignments") != 1394
        or math_event.get("reviewed_deviation_opcodes") != 16
        or math_event.get("extractor") != "backend/ch03_math.py"
        or math_event.get("extractor_sha256")
        != "6f94fd3d4cf65ac8509544b2dfd381798ea7251b4557dbdf8165b3a6ebcea0f3"
    ):
        raise ValueError("Chapter 3 text-aware math evidence is inconsistent")
    admission = chapter_three_qa[-1]
    if (
        admission.get("decision") != "admitted"
        or admission.get("all_required_gates") != "pass"
        or admission.get("typed_qa_event_ids") != expected_chapter_three_qa_ids[:-1]
        or admission.get("receipt_document_state") != "present"
        or admission.get("witness") != "provenance/CH03_BUILD_AND_QA_RECEIPT.md"
        or admission.get("witness_sha256")
        != "145a426a86faf8f5fcc7d1f88cfa2a09bacd1c9bd8382203045236932c07bb1a"
    ):
        raise ValueError("Chapter 3 admission event is incomplete")

    chapter_four_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH04"
    ]
    expected_chapter_four_qa_ids = [
        "QA-CH04-STRUCTURAL-20260822",
        "QA-CH04-MATH-20260822",
        "QA-CH04-LANGUAGE-20260822",
        "QA-CH04-BUILD-20260822",
        "QA-CH04-VISUAL-20260822",
        "QA-CH04-ACCESSIBILITY-20260822",
        "QA-CH04-RIGHTS-20260822",
        "QA-CH04-ADMISSION-20260822",
    ]
    expected_chapter_four_qa_types = [
        "unit_structural",
        "unit_mathematical",
        "unit_language",
        "cumulative_build",
        "cumulative_visual",
        "cumulative_accessibility",
        "unit_rights_privacy",
        "unit_admission",
    ]
    if [record["id"] for record in chapter_four_qa] != expected_chapter_four_qa_ids:
        raise ValueError("Chapter 4 typed QA event inventory changed")
    if [record["qa_type"] for record in chapter_four_qa] != expected_chapter_four_qa_types:
        raise ValueError("Chapter 4 typed QA event kinds changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH04-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH04_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07"
        for record in chapter_four_qa
    ):
        raise ValueError("Chapter 4 QA events are not bound to the admission receipt")
    if any(record.get("result") != "pass" for record in chapter_four_qa[:5]):
        raise ValueError("Chapter 4 structural/math/language/build/visual gates did not pass")
    accessibility_event = chapter_four_qa[5]
    if (
        accessibility_event.get("result") != "fail"
        or accessibility_event.get("failure_scope") != "claim_of_fully_accessible_pdf"
        or accessibility_event.get("tagged_pdf") is not False
        or accessibility_event.get("math_diagram_unicode_maps_complete") is not False
        or accessibility_event.get("admission_blocker_for_visual_pdf_boundary") is not False
        or accessibility_event.get("accessible_html_or_tagged_pdf_state") != "pending"
    ):
        raise ValueError("Chapter 4 accessibility QA event is incomplete")
    if chapter_four_qa[6].get("result") != "pass":
        raise ValueError("Chapter 4 rights/privacy gate did not pass")
    structural_event = chapter_four_qa[0]
    if (
        structural_event.get("semantic_anchors") != 131
        or structural_event.get("semantic_units") != 130
        or structural_event.get("segments") != 160
        or structural_event.get("labels") != 44
        or structural_event.get("references") != 53
        or structural_event.get("ordinary_target_references") != 50
        or structural_event.get("future_target_references") != 1
        or structural_event.get("equation_references") != 2
        or structural_event.get("index_terms") != 177
        or structural_event.get("defined_terms") != 59
    ):
        raise ValueError("Chapter 4 structural QA metadata is inconsistent")
    math_event = chapter_four_qa[1]
    if (
        math_event.get("source_math_surfaces") != 817
        or math_event.get("target_math_surfaces") != 817
        or math_event.get("exact_normalized_alignments") != 802
        or math_event.get("math_key_equal_alignments") != 807
        or math_event.get("localized_reorderings") != 15
        or math_event.get("localized_math_text_alignments") != 6
        or math_event.get("reviewed_source_corrections") != 9
        or math_event.get("formula_map_records") != 817
    ):
        raise ValueError("Chapter 4 mathematical QA metadata is inconsistent")
    admission = chapter_four_qa[-1]
    if (
        admission.get("result") != "pass"
        or admission.get("decision") != "admitted"
        or admission.get("typed_qa_event_ids") != expected_chapter_four_qa_ids[:-1]
        or admission.get("all_required_admission_gates") != "pass"
        or admission.get("accessibility_remediation_state") != "pending_nonblocking"
        or admission.get("publication_state") != "pending"
        or admission.get("receipt_document_state") != "present"
        or admission.get("receipt_sha256")
        != "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07"
    ):
        raise ValueError("Chapter 4 admission event is incomplete")

    chapter_five_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH05"
    ]
    expected_chapter_five_qa_ids = [
        "QA-CH05-STRUCTURAL-20260822",
        "QA-CH05-MATH-20260822",
        "QA-CH05-LANGUAGE-20260822",
        "QA-CH05-BUILD-20260822",
        "QA-CH05-VISUAL-20260822",
        "QA-CH05-ACCESSIBILITY-20260822",
        "QA-CH05-RIGHTS-20260822",
        "QA-CH05-ADMISSION-20260822",
    ]
    expected_chapter_five_qa_types = [
        "unit_structural",
        "unit_mathematical",
        "unit_language",
        "cumulative_build",
        "cumulative_visual",
        "cumulative_accessibility",
        "unit_rights_privacy",
        "unit_admission",
    ]
    if [record["id"] for record in chapter_five_qa] != expected_chapter_five_qa_ids:
        raise ValueError("Chapter 5 typed QA event inventory changed")
    if [record["qa_type"] for record in chapter_five_qa] != expected_chapter_five_qa_types:
        raise ValueError("Chapter 5 typed QA event kinds changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH05-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH05_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "11ea57ad7a5f73f806846d7303246e7391b7c2aca37ce5a7fc2d53d7013b7ca5"
        for record in chapter_five_qa
    ):
        raise ValueError("Chapter 5 QA events are not bound to the admission receipt")
    if any(record.get("result") != "pass" for record in chapter_five_qa[:5]):
        raise ValueError("Chapter 5 structural/math/language/build/visual gates did not pass")
    chapter_five_accessibility = chapter_five_qa[5]
    if (
        chapter_five_accessibility.get("result") != "fail"
        or chapter_five_accessibility.get("failure_scope")
        != "claim_of_fully_accessible_pdf"
        or chapter_five_accessibility.get("tagged_pdf") is not False
        or chapter_five_accessibility.get("unicode_mapped_font_resources") != 38
        or chapter_five_accessibility.get("total_font_resources") != 40
        or chapter_five_accessibility.get("remaining_c0_controls") != 24
        or chapter_five_accessibility.get("affected_xy_diagram_pages") != 6
        or chapter_five_accessibility.get("resolved_internal_links") != 1228
        or chapter_five_accessibility.get("named_destinations") != 861
        or chapter_five_accessibility.get("outline_entries") != 34
        or chapter_five_accessibility.get("admission_blocker_for_visual_pdf_boundary")
        is not False
        or chapter_five_accessibility.get("accessibility_remediation_state")
        != "partial_nonblocking"
    ):
        raise ValueError("Chapter 5 accessibility QA event is incomplete")
    if chapter_five_qa[6].get("result") != "pass":
        raise ValueError("Chapter 5 rights/privacy gate did not pass")
    chapter_five_structural = chapter_five_qa[0]
    if (
        chapter_five_structural.get("semantic_anchors") != 138
        or chapter_five_structural.get("semantic_units") != 137
        or chapter_five_structural.get("segments") != 158
        or chapter_five_structural.get("all_environment_pairs") != 152
        or chapter_five_structural.get("semantic_environment_anchors") != 130
        or chapter_five_structural.get("sections") != 7
        or chapter_five_structural.get("labels") != 39
        or chapter_five_structural.get("references") != 25
        or chapter_five_structural.get("ordinary_target_references") != 23
        or chapter_five_structural.get("future_target_references") != 1
        or chapter_five_structural.get("equation_references") != 1
        or chapter_five_structural.get("citations") != 1
        or chapter_five_structural.get("index_terms") != 168
        or chapter_five_structural.get("defined_terms") != 56
        or chapter_five_structural.get("exercise_environments") != 4
        or chapter_five_structural.get("proof_hints") != 17
    ):
        raise ValueError("Chapter 5 structural QA metadata is inconsistent")
    chapter_five_math = chapter_five_qa[1]
    if (
        chapter_five_math.get("source_math_surfaces") != 827
        or chapter_five_math.get("target_math_surfaces") != 827
        or chapter_five_math.get("exact_normalized_alignments") != 816
        or chapter_five_math.get("math_key_equal_alignments") != 821
        or chapter_five_math.get("localized_math_text_alignments") != 5
        or chapter_five_math.get("reviewed_source_corrections") != 6
        or chapter_five_math.get("formula_map_records") != 827
        or chapter_five_math.get("locked_source_correction_surfaces") != 6
    ):
        raise ValueError("Chapter 5 mathematical QA metadata is inconsistent")
    chapter_five_admission = chapter_five_qa[-1]
    if (
        chapter_five_admission.get("result") != "pass"
        or chapter_five_admission.get("decision") != "admitted"
        or chapter_five_admission.get("typed_qa_event_ids")
        != expected_chapter_five_qa_ids[:-1]
        or chapter_five_admission.get("all_required_admission_gates") != "pass"
        or chapter_five_admission.get("accessibility_remediation_state")
        != "partial_nonblocking"
        or chapter_five_admission.get("publication_state") != "pending"
        or chapter_five_admission.get("receipt_document_state") != "present"
        or chapter_five_admission.get("receipt_sha256")
        != "11ea57ad7a5f73f806846d7303246e7391b7c2aca37ce5a7fc2d53d7013b7ca5"
        or chapter_five_admission.get("required_admission_gate_results", {}).get(
            "cumulative_accessibility"
        )
        != "fail_nonblocking"
    ):
        raise ValueError("Chapter 5 admission event is incomplete")

    chapter_six_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH06"
    ]
    expected_chapter_six_qa_ids = [
        "QA-CH06-STRUCTURAL-20260822",
        "QA-CH06-MATH-20260822",
        "QA-CH06-LANGUAGE-20260822",
        "QA-CH06-BUILD-20260822",
        "QA-CH06-VISUAL-20260822",
        "QA-CH06-ACCESSIBILITY-20260822",
        "QA-CH06-RIGHTS-20260822",
        "QA-CH06-ADMISSION-20260822",
    ]
    expected_chapter_six_qa_types = [
        "unit_structural",
        "unit_mathematical",
        "unit_language",
        "cumulative_build",
        "cumulative_visual",
        "cumulative_accessibility",
        "unit_rights_privacy",
        "unit_admission",
    ]
    if [record["id"] for record in chapter_six_qa] != expected_chapter_six_qa_ids:
        raise ValueError("Chapter 6 typed QA event inventory changed")
    if [record["qa_type"] for record in chapter_six_qa] != expected_chapter_six_qa_types:
        raise ValueError("Chapter 6 typed QA event kinds changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH06-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH06_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "acc110923270c2918ca7aa1a6a2c839ae4c99504133e60c20d44a906b5830293"
        for record in chapter_six_qa
    ):
        raise ValueError("Chapter 6 QA events are not bound to the admission receipt")
    if [record.get("result") for record in chapter_six_qa] != [
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
    ]:
        raise ValueError("Chapter 6 QA gate states changed")
    chapter_six_structural = chapter_six_qa[0]
    if (
        chapter_six_structural.get("semantic_anchors") != 167
        or chapter_six_structural.get("semantic_units") != 166
        or chapter_six_structural.get("segments") != 206
        or chapter_six_structural.get("all_environment_pairs") != 178
        or chapter_six_structural.get("semantic_environment_anchors") != 159
        or chapter_six_structural.get("sections") != 7
        or chapter_six_structural.get("labels") != 56
        or chapter_six_structural.get("references") != 80
        or chapter_six_structural.get("ordinary_target_references") != 79
        or chapter_six_structural.get("future_target_references") != 1
        or chapter_six_structural.get("equation_references") != 2
        or chapter_six_structural.get("citations") != 13
        or chapter_six_structural.get("index_terms") != 155
        or chapter_six_structural.get("defined_terms") != 47
        or chapter_six_structural.get("exercise_environments") != 6
        or chapter_six_structural.get("proof_environments") != 29
        or chapter_six_structural.get("proof_hints") != 28
        or chapter_six_structural.get("ordinary_proofs") != 1
    ):
        raise ValueError("Chapter 6 structural QA metadata is inconsistent")
    chapter_six_math = chapter_six_qa[1]
    if (
        chapter_six_math.get("source_math_surfaces") != 1155
        or chapter_six_math.get("target_math_surfaces") != 1156
        or chapter_six_math.get("exact_normalized_alignments") != 1131
        or chapter_six_math.get("math_key_equal_alignments") != 1138
        or chapter_six_math.get("localized_math_text_alignments") != 7
        or chapter_six_math.get("localized_math_key_differences") != 6
        or chapter_six_math.get("reviewed_source_correction_maps") != 12
        or chapter_six_math.get("target_only_source_corrections") != 2
        or chapter_six_math.get("consolidated_source_corrections") != 1
        or chapter_six_math.get("localization_phrase_reorderings") != 3
        or chapter_six_math.get("formula_map_records") != 1156
        or chapter_six_math.get("classified_math_edit_blocks") != 22
        or chapter_six_math.get("unexplained_deltas") != 0
    ):
        raise ValueError("Chapter 6 mathematical QA metadata is inconsistent")
    chapter_six_build = chapter_six_qa[3]
    if (
        chapter_six_build.get("witness")
        != "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-6.pdf"
        or chapter_six_build.get("witness_sha256")
        != "93cfdf76515205ca259c91537a58cfa2b0ae7cab67e4b1b818ac9f5784aaa55c"
        or chapter_six_build.get("local_build_log_bytes") != 46285
        or chapter_six_build.get("local_build_log_sha256")
        != "d3f234b73aa71121a463b752dd68fa558309ad2056df31d956c2e060814bfeef"
        or chapter_six_build.get("pages") != 114
        or chapter_six_build.get("fixed_path_clean_builds_byte_identical") is not True
        or chapter_six_build.get("fixed_path_build_pdf_path")
        != "qa/build-through-ch06-a/functional-analysis-id-through-ch06.pdf"
        or chapter_six_build.get("final_output_copy_state") != "present_byte_identical"
    ):
        raise ValueError("Chapter 6 deterministic build gate is inconsistent")
    chapter_six_visual = chapter_six_qa[4]
    if (
        chapter_six_visual.get("decision") != "visual_render_navigation_pass"
        or chapter_six_visual.get("witness")
        != "qa/CH06_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
        or chapter_six_visual.get("witness_sha256")
        != "3da448996dba97de722ccc48eaa7590a5a9d2f462dcaa4766aecd153139d528b"
        or chapter_six_visual.get("pages_rendered") != 114
        or chapter_six_visual.get("pages_inspected") != 114
        or chapter_six_visual.get("uniform_pixel_dimensions") != "1275x1650"
        or chapter_six_visual.get("outer_5px_edge_ink_pages") != 0
        or chapter_six_visual.get("rendered_png_bytes") != 40224010
        or chapter_six_visual.get("word_boxes") != 54378
        or chapter_six_visual.get("out_of_bounds_word_boxes") != 0
        or chapter_six_visual.get("visual_defects") != 0
    ):
        raise ValueError("Chapter 6 visual QA event is inconsistent")
    chapter_six_accessibility = chapter_six_qa[5]
    if (
        chapter_six_accessibility.get("decision")
        != "honest_chapter_boundary_accessibility_pass"
        or chapter_six_accessibility.get("witness")
        != "qa/CH06_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"
        or chapter_six_accessibility.get("witness_sha256")
        != "3da448996dba97de722ccc48eaa7590a5a9d2f462dcaa4766aecd153139d528b"
        or chapter_six_accessibility.get("tagged_pdf") is not False
        or chapter_six_accessibility.get("fully_accessible_pdf_claim") is not False
        or chapter_six_accessibility.get("unicode_mapped_font_resources") != 43
        or chapter_six_accessibility.get("total_font_resources") != 43
        or chapter_six_accessibility.get("text_extraction_bytes") != 436932
        or chapter_six_accessibility.get("text_extraction_sha256")
        != "d9fa66b1ec42ede6ab4247f81eb70361c274922cb5d3eeaacf0616fc30235c4c"
        or chapter_six_accessibility.get("resolved_internal_links") != 1500
        or chapter_six_accessibility.get("named_destinations") != 1052
        or chapter_six_accessibility.get("outline_entries") != 42
        or chapter_six_accessibility.get("semantic_accessibility_state")
        != "remediation_required"
        or chapter_six_accessibility.get("accessibility_remediation_state")
        != "pending_nonblocking"
        or chapter_six_accessibility.get("accessible_html_or_tagged_pdf_state")
        != "pending"
        or chapter_six_accessibility.get("admission_blocker_for_chapter_boundary")
        is not False
    ):
        raise ValueError("Chapter 6 accessibility QA event is inconsistent")
    chapter_six_rights = chapter_six_qa[6]
    if (
        chapter_six_rights.get("decision") != "rights_component_privacy_closure_pass"
        or chapter_six_rights.get("witness")
        != "provenance/CH06_BUILD_AND_QA_RECEIPT.md"
        or chapter_six_rights.get("witness_sha256")
        != "acc110923270c2918ca7aa1a6a2c839ae4c99504133e60c20d44a906b5830293"
        or chapter_six_rights.get("rights_id") != "RIGHTS-ERDMAN-CC-BY-SA-4.0"
        or chapter_six_rights.get("excluded_components_absent") is not True
        or chapter_six_rights.get("private_control_paths_absent_from_public_artifacts")
        is not True
        or chapter_six_rights.get("credential_or_token_residue") != 0
    ):
        raise ValueError("Chapter 6 rights/privacy QA event is inconsistent")
    chapter_six_admission = chapter_six_qa[-1]
    if (
        chapter_six_admission.get("decision") != "admitted"
        or chapter_six_admission.get("typed_qa_event_ids")
        != expected_chapter_six_qa_ids[:-1]
        or chapter_six_admission.get("all_required_admission_gates") != "pass"
        or chapter_six_admission.get("required_admission_gate_results")
        != {
            "unit_structural": "pass",
            "unit_mathematical": "pass",
            "unit_language": "pass",
            "cumulative_build": "pass",
            "cumulative_visual": "pass",
            "cumulative_accessibility": "pass",
            "unit_rights_privacy": "pass",
        }
        or chapter_six_admission.get("accessibility_remediation_state")
        != "pending_nonblocking"
        or chapter_six_admission.get("accessible_html_or_tagged_pdf_state") != "pending"
        or chapter_six_admission.get("visual_accessibility_audit_sha256")
        != "3da448996dba97de722ccc48eaa7590a5a9d2f462dcaa4766aecd153139d528b"
        or chapter_six_admission.get("publication_state") != "pending"
    ):
        raise ValueError("Chapter 6 admission event is incomplete")

    chapter_two_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH02"
    ]
    if [record["id"] for record in chapter_two_corrections] != [
        f"FAOA-2015-CH02-CORR-{number:03d}" for number in range(1, 7)
    ]:
        raise ValueError("Chapter 2 correction inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH02-ADMISSION-20260821"
        or record.get("ledger_sha256")
        != "26708cf62c00202ad224a5d5413069e7bd376497a96e3c7c30487b66214d5c16"
        or record.get("upstream_report")
        != "deferred_until_complete_and_separately_authorized"
        for record in chapter_two_corrections
    ):
        raise ValueError("Chapter 2 corrections are not bound to the admitted evidence")

    chapter_three_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH03"
    ]
    if [record["id"] for record in chapter_three_corrections] != [
        f"FAOA-2015-CH03-CORR-{number:03d}" for number in range(1, 26)
    ]:
        raise ValueError("Chapter 3 correction inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH03-ADMISSION-20260821"
        or record.get("ledger_sha256")
        != "bb1ef771876b2c1ef0063c3fd9e28c27f20db4049f434d27f8b333fd5f3477c2"
        or record.get("upstream_report")
        != "deferred_until_complete_and_separately_authorized"
        for record in chapter_three_corrections
    ):
        raise ValueError("Chapter 3 corrections are not bound to the admitted evidence")

    chapter_four_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH04"
    ]
    if [record["id"] for record in chapter_four_corrections] != [
        f"FAOA-2015-CH04-CORR-{number:03d}" for number in range(1, 23)
    ]:
        raise ValueError("Chapter 4 correction inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH04-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH04_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "5f82abac5f7283e95ea20699b437234a4ef3b2f60520dc1b10c7a2dc9187ba07"
        or record.get("ledger_sha256")
        != "8909a33f5ed5dd37065fb4c3afb08e4e0659d17ef1d1a2b8f1d7f307ed1eef2d"
        or record.get("ledger_section_sha256")
        != "961806d5d229310c8063dc8941c8d4fd1caeabafe65bb9fa7df9045c17f53fe3"
        or record.get("upstream_report")
        != "deferred_until_complete_and_separately_authorized"
        for record in chapter_four_corrections
    ):
        raise ValueError("Chapter 4 corrections are not bound to admitted evidence")

    chapter_five_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH05"
    ]
    if [record["id"] for record in chapter_five_corrections] != [
        f"FAOA-2015-CH05-CORR-{number:03d}" for number in range(1, 24)
    ]:
        raise ValueError("Chapter 5 correction inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH05-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH05_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "11ea57ad7a5f73f806846d7303246e7391b7c2aca37ce5a7fc2d53d7013b7ca5"
        or record.get("ledger_sha256")
        != "2408e045efb307602fbe8540efcb6307944d01d7ace610d78e4341856a0e35b7"
        or record.get("ledger_section_sha256")
        != "95f76df166278c995fe031f65f1b4dc4a6740b5776f579bd8970faee9b526f79"
        or record.get("upstream_report")
        != "deferred_until_complete_and_separately_authorized"
        for record in chapter_five_corrections
    ):
        raise ValueError("Chapter 5 corrections are not bound to admitted evidence")

    chapter_six_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH06"
    ]
    if [record["id"] for record in chapter_six_corrections] != [
        f"FAOA-2015-CH06-CORR-{number:03d}" for number in range(1, 21)
    ]:
        raise ValueError("Chapter 6 correction inventory changed")
    expected_chapter_six_correction_types = [
        "source_language_and_punctuation",
        "future_reference_resolution",
        "annihilator_empty_subset",
        "weak_star_convergence_wording",
        "alaoglu_dual_ball",
        "unbound_sequence_term",
        "category_index",
        "environment_kind",
        "proof_hint_markup",
        "undefined_ambient_algebra",
        "sequence_space_and_norm_limit",
        "undefined_ambient_banach_space",
        "subspace_order_symbol",
        "functor_morphism_linearity",
        "dual_superscript",
        "ambient_space_name",
        "nonempty_baire_hypothesis",
        "missing_modulus",
        "piecewise_right_delimiter",
        "operator_topology_index_sort_keys",
    ]
    expected_chapter_six_correction_locators = [
        "Banach_spaces.tex:16,60--62,330,403,423,496,502,684,797,909,912,932,1055,1171",
        "Banach_spaces.tex:128",
        "Banach_spaces.tex:213--214",
        "Banach_spaces.tex:275",
        "Banach_spaces.tex:303--305",
        "Banach_spaces.tex:396",
        "Banach_spaces.tex:407--410",
        "Banach_spaces.tex:476",
        "Banach_spaces.tex:546--549",
        "Banach_spaces.tex:661--665",
        "Banach_spaces.tex:924--925",
        "Banach_spaces.tex:955",
        "Banach_spaces.tex:1205",
        "Banach_spaces.tex:1253",
        "Banach_spaces.tex:1254",
        "Banach_spaces.tex:1327",
        "Banach_spaces.tex:1384",
        "Banach_spaces.tex:1447",
        "Banach_spaces.tex:1490--1495",
        "Banach_spaces.tex:1566,1574",
    ]
    if [record.get("correction_type") for record in chapter_six_corrections] != (
        expected_chapter_six_correction_types
    ) or [record.get("source_locator") for record in chapter_six_corrections] != (
        expected_chapter_six_correction_locators
    ):
        raise ValueError("Chapter 6 correction type/locator lock changed")
    if any(
        record.get("target_disposition") != "corrected"
        or record.get("qa_receipt_id") != "QA-CH06-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH06_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "acc110923270c2918ca7aa1a6a2c839ae4c99504133e60c20d44a906b5830293"
        or record.get("ledger_sha256")
        != "7de8a5892b865af84c9f5d1d4c37ec6b3112b3e099685dae243108006dc94b01"
        or record.get("ledger_section_sha256")
        != "51c26be9d5346ced5707d0ce91e2ed27f313c60666aab81155dafd572cde2118"
        or record.get("upstream_report")
        != "deferred_until_complete_and_separately_authorized"
        for record in chapter_six_corrections
    ):
        raise ValueError("Chapter 6 corrections are not bound to admitted evidence")

    expected_chapter_two_term_ids = [
        "TERM-CATEGORY",
        "TERM-OBJECT",
        "TERM-MORPHISM",
        "TERM-COMPOSITION",
        "TERM-LOCALLY-SMALL-CATEGORY",
        "TERM-SMALL-CATEGORY",
        "TERM-CONCRETE-CATEGORY",
        "TERM-ISOMORPHISM",
        "TERM-MONOMORPHISM",
        "TERM-EPIMORPHISM",
        "TERM-FUNCTOR",
        "TERM-COVARIANT-FUNCTOR",
        "TERM-CONTRAVARIANT-FUNCTOR",
        "TERM-OBJECT-MAP",
        "TERM-MORPHISM-MAP",
        "TERM-FORGETFUL-FUNCTOR",
        "TERM-POWER-SET",
        "TERM-DIAGONAL-FUNCTOR",
    ]
    chapter_two_terminology = [
        record
        for record in records_by_file["terminology.jsonl"]
        if record["id"] in expected_chapter_two_term_ids
    ]
    if [record["id"] for record in chapter_two_terminology] != expected_chapter_two_term_ids:
        raise ValueError("Chapter 2 bounded terminology inventory changed")
    if any(
        record.get("locale") != "id-ID"
        or record.get("evidence") != "FAOA-2015-CH02 and backend/index_terms.csv"
        for record in chapter_two_terminology
    ):
        raise ValueError("Chapter 2 terminology provenance changed")

    expected_chapter_three_term_ids = [
        "TERM-NORMED-LINEAR-SPACE",
        "TERM-BOUNDED-LINEAR-MAP",
        "TERM-OPERATOR-NORM",
        "TERM-NORM-PRESERVING",
        "TERM-QUOTIENT-SPACE",
        "TERM-PRODUCT-SPACE",
        "TERM-COPRODUCT",
        "TERM-NET",
        "TERM-DIRECTED-SET",
        "TERM-SUBNET",
        "TERM-CLOSURE",
        "TERM-INTERIOR",
        "TERM-CONTINUITY",
        "TERM-FUNCTIONAL-EXTENSION",
        "TERM-HAUSDORFF",
        "TERM-COMPACT",
        "TERM-HAHN-BANACH-THEOREM",
        "TERM-SCALAR-VALUED",
    ]
    chapter_three_terminology = [
        record
        for record in records_by_file["terminology.jsonl"]
        if record["id"] in expected_chapter_three_term_ids
    ]
    if [record["id"] for record in chapter_three_terminology] != expected_chapter_three_term_ids:
        raise ValueError("Chapter 3 bounded terminology inventory changed")
    if any(
        record.get("locale") != "id-ID"
        or record.get("evidence") != "FAOA-2015-CH03 and backend/index_terms.csv"
        for record in chapter_three_terminology
    ):
        raise ValueError("Chapter 3 terminology provenance changed")

    expected_chapter_four_term_ids = [
        "TERM-HILBERT-SPACE",
        "TERM-BANACH-SPACE",
        "TERM-BANACH-ALGEBRA",
        "TERM-UNIFORM-NORM",
        "TERM-MEASURABLE",
        "TERM-SQUARE-INTEGRABLE",
        "TERM-INTEGRABLE",
        "TERM-ABSOLUTELY-CONTINUOUS",
        "TERM-SUMMABLE",
        "TERM-SUM",
        "TERM-ABSOLUTELY-SUMMABLE",
        "TERM-CONVERGES",
        "TERM-EXISTS",
        "TERM-ABSOLUTELY-CONVERGENT",
        "TERM-CONVERGENT-SERIES",
        "TERM-EXTERNAL-ORTHOGONAL-DIRECT-SUM",
        "TERM-CLOSED-LINEAR-SPAN",
        "TERM-ORTHONORMAL",
        "TERM-ORTHONORMAL-BASIS",
        "TERM-COMPLETE-ORTHONORMAL-SET",
        "TERM-HILBERT-SPACE-BASIS",
        "TERM-USUAL",
        "TERM-STANDARD",
        "TERM-TRIGONOMETRIC-POLYNOMIAL",
        "TERM-DIMENSION",
        "TERM-CODIMENSION",
        "TERM-CONJUGATE-LINEAR",
        "TERM-ANTI-ISOMORPHISM",
        "TERM-CONJUGATION",
        "TERM-WEAK-TOPOLOGY",
        "TERM-PRODUCT-TOPOLOGY",
        "TERM-CONVERGE-WEAKLY",
        "TERM-CONVERGE-STRONGLY",
        "TERM-CONVERGE-IN-NORM",
        "TERM-WEAKLY-CLOSED",
        "TERM-WEAKLY-COMPACT",
        "TERM-WEAKLY-CONTINUOUS",
        "TERM-UNIVERSAL-MAPPING-DIAGRAM",
        "TERM-UNIVERSAL-PROPERTY",
        "TERM-UNIVERSAL-MORPHISM",
        "TERM-UNIVERSAL-OBJECT",
        "TERM-FREE-ON",
        "TERM-FREE-OBJECT-GENERATED-BY",
        "TERM-FREE-VECTOR-SPACES",
        "TERM-CHARACTERISTIC-FUNCTION",
        "TERM-WORD",
        "TERM-EMPTY-WORD",
        "TERM-CONCATENATION",
        "TERM-FREE-MONOID",
        "TERM-FREE-SEMIGROUP",
        "TERM-CO-UNIVERSAL-MORPHISM",
        "TERM-CATEGORICAL-PRODUCT",
        "TERM-COMPLETION",
    ]
    chapter_four_terminology = [
        record
        for record in records_by_file["terminology.jsonl"]
        if record["id"] in expected_chapter_four_term_ids
    ]
    if [record["id"] for record in chapter_four_terminology] != expected_chapter_four_term_ids:
        raise ValueError("Chapter 4 bounded terminology inventory changed")
    if any(
        record.get("locale") != "id-ID"
        or record.get("evidence")
        != "FAOA-2015-CH04 admitted target source/id-ID/Hilbert_spaces-id.tex; backend/index_terms.csv; provenance/CH04_BUILD_AND_QA_RECEIPT.md"
        for record in chapter_four_terminology
    ):
        raise ValueError("Chapter 4 terminology provenance changed")
    chapter_four_term_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record.get("relation_type") == "uses_term"
        and record["id"].startswith("FAOA-2015-CH04-REL-TERM-")
    ]
    if len(chapter_four_term_relations) != 59 or any(
        record.get("to_id") not in ids for record in chapter_four_term_relations
    ):
        raise ValueError("Chapter 4 defined-term relationships changed")

    expected_chapter_five_term_ids = [
        "TERM-INNER-PRODUCT-PRESERVING",
        "TERM-CURVE",
        "TERM-SIMPLE",
        "TERM-CHORD",
        "TERM-NON-OVERLAPPING",
        "TERM-ASSOCIATED-QUADRATIC-FORM",
        "TERM-SESQUILINEAR-FUNCTIONAL",
        "TERM-BOUNDED",
        "TERM-UNILATERAL-SHIFT-OPERATOR",
        "TERM-DIAGONAL-OPERATOR",
        "TERM-MULTIPLICATION-OPERATOR",
        "TERM-UNITARILY-EQUIVALENT",
        "TERM-INTEGRAL-OPERATOR",
        "TERM-KERNEL",
        "TERM-VOLTERRA-OPERATOR",
        "TERM-BOUNDED-AWAY-FROM-ZERO",
        "TERM-BOUNDED-BELOW",
        "TERM-INVOLUTION",
        "TERM-STAR-ALGEBRA",
        "TERM-STAR-HOMOMORPHISM",
        "TERM-UNITAL",
        "TERM-STAR-ISOMORPHISM",
        "TERM-HERMITIAN",
        "TERM-NORMAL",
        "TERM-STAR-SUBALGEBRA",
        "TERM-NUMERICAL-RANGE",
        "TERM-NUMERICAL-RADIUS",
        "TERM-POSITIVE",
        "TERM-ABSTRACT",
        "TERM-SPATIAL",
        "TERM-CONCRETE",
        "TERM-FINITE-RANK",
        "TERM-LEFT-IDEAL",
        "TERM-RIGHT-IDEAL",
        "TERM-IDEAL",
        "TERM-PROPER",
        "TERM-TRIVIAL-IDEAL",
        "TERM-MAXIMAL",
        "TERM-MINIMAL",
        "TERM-PRINCIPAL-IDEAL",
        "TERM-QUOTIENT-ALGEBRA",
        "TERM-QUOTIENT-MAP",
        "TERM-STAR-IDEAL",
        "TERM-QUOTIENT",
    ]
    chapter_five_terminology = records_by_file["terminology.jsonl"][109:153]
    if [record["id"] for record in chapter_five_terminology] != expected_chapter_five_term_ids:
        raise ValueError("Chapter 5 bounded terminology inventory changed")
    if any(
        record.get("locale") != "id-ID"
        or record.get("evidence")
        != "FAOA-2015-CH05 final target source/id-ID/Hilbert_space_operators-id.tex; backend/index_terms.csv; qa/check_ch05_translation.py"
        for record in chapter_five_terminology
    ):
        raise ValueError("Chapter 5 terminology provenance changed")
    chapter_five_term_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record.get("relation_type") == "uses_term"
        and record["id"].startswith("FAOA-2015-CH05-REL-TERM-")
    ]
    if len(chapter_five_term_relations) != 56 or any(
        record.get("to_id") not in ids for record in chapter_five_term_relations
    ):
        raise ValueError("Chapter 5 defined-term relationships changed")
    star_subalgebra_relations = [
        record
        for record in chapter_five_term_relations
        if record.get("source_term_tex") in {"$*\\,$-subalgebra", "sub-$*\\,$-algebra"}
    ]
    if len(star_subalgebra_relations) != 2 or any(
        record.get("to_id") != "TERM-STAR-SUBALGEBRA"
        for record in star_subalgebra_relations
    ):
        raise ValueError("Chapter 5 synonymous star-subalgebra term mapping changed")

    expected_chapter_six_term_ids = [
        "TERM-SECOND-DUAL",
        "TERM-SECOND-DUAL-FUNCTOR",
        "TERM-NATURAL-TRANSFORMATION",
        "TERM-NATURAL-EQUIVALENCE",
        "TERM-NATURAL-EMBEDDING",
        "TERM-REFLEXIVE",
        "TERM-ANNIHILATOR",
        "TERM-PRE-ANNIHILATOR",
        "TERM-WEAK-STAR-TOPOLOGY",
        "TERM-UNIVERSAL",
        "TERM-OPEN",
        "TERM-IDEMPOTENT",
        "TERM-EXACT-AT",
        "TERM-EXACT",
        "TERM-SHORT-EXACT-SEQUENCE",
        "TERM-COKERNEL",
        "TERM-SCHAUDER-BASIS",
        "TERM-BASIS-VECTORS",
        "TERM-LOCALLY-COMPACT",
        "TERM-PROJECTION-ALONG-KERNEL-ONTO-RANGE",
        "TERM-COMPLEMENTED",
        "TERM-BANACH-SPACE-COMPLEMENT",
        "TERM-COMPLEMENTARY",
        "TERM-POINTWISE-BOUNDED",
        "TERM-UNIFORMLY-BOUNDED",
        "TERM-WEAKLY-BOUNDED",
        "TERM-WEAKLY-CAUCHY",
        "TERM-WEAKLY-SEQUENTIALLY-COMPLETE",
        "TERM-CONVERGES-IN-WEAK-OPERATOR-TOPOLOGY",
        "TERM-BOUNDED-IN-WEAK-OPERATOR-TOPOLOGY",
        "TERM-CONVERGES-IN-STRONG-OPERATOR-TOPOLOGY",
        "TERM-UNIFORM-CONVERGENCE",
        "TERM-CONVERGENCE-IN-UNIFORM-OPERATOR-TOPOLOGY",
    ]
    chapter_six_terminology = records_by_file["terminology.jsonl"][153:186]
    if [record["id"] for record in chapter_six_terminology] != expected_chapter_six_term_ids:
        raise ValueError("Chapter 6 bounded terminology inventory changed")
    if any(
        record.get("locale") != "id-ID"
        or record.get("evidence")
        != "FAOA-2015-CH06 final target source/id-ID/Banach_spaces-id.tex; backend/index_terms.csv; qa/check_ch06_translation.py"
        for record in chapter_six_terminology
    ):
        raise ValueError("Chapter 6 terminology provenance changed")
    chapter_six_term_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record.get("relation_type") == "uses_term"
        and record["id"].startswith("FAOA-2015-CH06-REL-TERM-")
    ]
    if len(chapter_six_term_relations) != 47 or any(
        record.get("to_id") not in ids for record in chapter_six_term_relations
    ):
        raise ValueError("Chapter 6 defined-term relationships changed")
    reused_chapter_six_terms = {
        "adjoint": "TERM-ADJOINT",
        "weak topology": "TERM-WEAK-TOPOLOGY",
        "bounded away from zero": "TERM-BOUNDED-AWAY-FROM-ZERO",
        "bounded below": "TERM-BOUNDED-BELOW",
        "standard": "TERM-STANDARD",
        "usual": "TERM-USUAL",
        "projection": "TERM-PROJECTION",
        "codimension": "TERM-CODIMENSION",
        "converges weakly": "TERM-CONVERGE-WEAKLY",
        "converges strongly": "TERM-CONVERGE-STRONGLY",
    }
    if any(
        record.get("to_id") != reused_chapter_six_terms[record["source_term_tex"]]
        for record in chapter_six_term_relations
        if record.get("source_term_tex") in reused_chapter_six_terms
    ):
        raise ValueError("Chapter 6 established terminology IDs were not reused")

    chapter_five_exercises = [
        record
        for record in records_by_file["exercise_support.jsonl"]
        if record["id"].startswith("FAOA-2015-CH05-")
    ]
    if [record["id"] for record in chapter_five_exercises] != [
        f"FAOA-2015-CH05-EXERCISE-SUPPORT-{number:03d}" for number in range(1, 5)
    ] or any(
        record.get("upstream_hint_ids")
        or record.get("upstream_answer_state") != "absent"
        or record.get("upstream_solution_state") != "absent"
        or record.get("provenance") != "separately_authored_not_Erdman"
        for record in chapter_five_exercises
    ):
        raise ValueError("Chapter 5 exercise-support semantics changed")

    chapter_six_exercises = [
        record
        for record in records_by_file["exercise_support.jsonl"]
        if record["id"].startswith("FAOA-2015-CH06-")
    ]
    if [record["id"] for record in chapter_six_exercises] != [
        f"FAOA-2015-CH06-EXERCISE-SUPPORT-{number:03d}" for number in range(1, 7)
    ]:
        raise ValueError("Chapter 6 exercise-support inventory changed")
    if [record.get("upstream_inline_hint_state") for record in chapter_six_exercises] != [
        "absent",
        "present",
        "present",
        "absent",
        "absent",
        "present",
    ]:
        raise ValueError("Chapter 6 inline exercise-hint inventory changed")
    if [record.get("upstream_inline_hint_source_lines") for record in chapter_six_exercises] != [
        None,
        [464],
        [489],
        None,
        None,
        [1461],
    ]:
        raise ValueError("Chapter 6 inline exercise-hint locators changed")
    if any(
        record.get("upstream_hint_ids")
        or record.get("upstream_answer_state") != "absent"
        or record.get("upstream_solution_state") != "absent"
        or record.get("provenance") != "separately_authored_not_Erdman"
        or record.get("exercise_unit_id") not in ids
        for record in chapter_six_exercises
    ):
        raise ValueError("Chapter 6 exercise-support semantics changed")

    chapter_seven_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH07-")
    ]
    chapter_seven_relation_type_counts = {
        relation_type: sum(
            record["relation_type"] == relation_type
            for record in chapter_seven_relations
        )
        for relation_type in {
            "contains", "translates", "precedes", "declares_label", "xref",
            "cites", "hints", "uses_term", "resolves_pending_reference",
            "licensed_under", "has_artifact", "terminology_evidence",
            "has_qa_event", "documents_correction",
        }
    }
    if chapter_seven_relation_type_counts != {
        "contains": 74,
        "translates": 85,
        "precedes": 84,
        "declares_label": 20,
        "xref": 13,
        "cites": 8,
        "hints": 7,
        "uses_term": 26,
        "resolves_pending_reference": 1,
        "licensed_under": 1,
        "has_artifact": 9,
        "terminology_evidence": 2,
        "has_qa_event": 8,
        "documents_correction": 11,
    }:
        raise ValueError("Chapter 7 relation-type inventory changed")
    chapter_seven_xrefs = [
        record
        for record in chapter_seven_relations
        if record["id"].startswith("FAOA-2015-CH07-REL-XREF-")
    ]
    chapter_seven_resolution_counts = {
        resolution: sum(record["resolution"] == resolution for record in chapter_seven_xrefs)
        for resolution in ("local", "admitted_prior_unit", "pending_later_source_unit")
    }
    if chapter_seven_resolution_counts != {
        "local": 4,
        "admitted_prior_unit": 6,
        "pending_later_source_unit": 3,
    }:
        raise ValueError("Chapter 7 reference-resolution inventory changed")
    chapter_seven_future = [
        record
        for record in chapter_seven_xrefs
        if record["resolution"] == "pending_later_source_unit"
    ]
    if [
        (record["source_local_id"], record["to_id"], record["target_surface"])
        for record in chapter_seven_future
    ] != [
        ("00152171", "ERDMAN-FAOA-2015-LABEL-00152171", "futurexref"),
        ("00152181", "ERDMAN-FAOA-2015-LABEL-00152181", "futurexref"),
        ("X_sqroot_op", "ERDMAN-FAOA-2015-LABEL-X_sqroot_op", "futurexref"),
    ]:
        raise ValueError("Chapter 7 future reference endpoints changed")
    if any(
        record["to_id"] not in ids
        for record in chapter_seven_xrefs
        if record["resolution"] != "pending_later_source_unit"
    ):
        raise ValueError("Chapter 7 admitted/local reference endpoint is unresolved")
    chapter_seven_pending_closures = [
        record
        for record in chapter_seven_relations
        if record.get("relation_type") == "resolves_pending_reference"
    ]
    if [
        (record.get("source_local_id"), record.get("to_id"), record.get("resolution"))
        for record in chapter_seven_pending_closures
    ] != [
        ("chap_cpt_ops", "FAOA-2015-CH05-REL-XREF-0010", "declared_in_current_unit")
    ] or chapter_seven_pending_closures[0].get("from_id") not in ids:
        raise ValueError("Chapter 7 append-only prior-xref closure changed")
    chapter_seven_term_evidence = [
        record
        for record in chapter_seven_relations
        if record.get("relation_type") == "terminology_evidence"
    ]
    if [(record["id"], record["to_id"]) for record in chapter_seven_term_evidence] != [
        ("FAOA-2015-CH07-REL-TERM-EVIDENCE-0001", "ARTIFACT-FAOA-ID-CH07-TARGET-TEX"),
        ("FAOA-2015-CH07-REL-TERM-EVIDENCE-0002", "ARTIFACT-FAOA-ID-CH07-STRUCTURAL-CHECKER"),
    ]:
        raise ValueError("Chapter 7 terminology-evidence links changed")

    chapter_seven_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH07"
    ]
    expected_chapter_seven_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH07-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH07-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH07-PDF",
        "ARTIFACT-FAOA-ID-CH07-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH07-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH07-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH07-VISUAL-ACCESSIBILITY-AUDIT",
        "ARTIFACT-FAOA-ID-CH07-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH07-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_seven_artifacts] != expected_chapter_seven_artifact_ids:
        raise ValueError("Chapter 7 artifact inventory changed")
    if any(
        record.get("receipt_document_state") != "present"
        or record.get("qa_receipt_id") != "QA-CH07-ADMISSION-20260822"
        or record.get("receipt_path") != "provenance/CH07_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "8c9e7afa90c27a748de6b2f44c1725ed467ba7f8e4f3960a0009459a25b0b525"
        for record in chapter_seven_artifacts
    ):
        raise ValueError("Chapter 7 artifacts are not bound to the admission receipt")
    chapter_seven_artifact_identities = {
        record["id"]: (record["path"], record["bytes"], record["sha256"])
        for record in chapter_seven_artifacts
    }
    fixed_chapter_seven_artifacts = {
        "ARTIFACT-FAOA-ID-CH07-TARGET-TEX": (
            "source/id-ID/compact_operators-id.tex", 22735,
            "8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a",
        ),
        "ARTIFACT-FAOA-ID-THROUGH-CH07-MASTER": (
            "source/id-ID/functional-analysis-id-through-ch07.tex", 9691,
            "c639253fab59df7b51002058b414d8d64c92d77f12e95e88068decafd0d138b9",
        ),
        "ARTIFACT-FAOA-ID-THROUGH-CH07-PDF": (
            "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-7.pdf", 1530677,
            "a7ddaef324bd356d258cb47195f524e027ba54a696cb8d38a8358bb8d0a2d7ff",
        ),
        "ARTIFACT-FAOA-ID-CH07-STRUCTURAL-CHECKER": (
            "qa/check_ch07_translation.py", 21468,
            "392d2842c99fd1a54faaf671b2256ef41a896335edd2c2fe5d973f13d63e1363",
        ),
        "ARTIFACT-FAOA-ID-CH07-RENDER-MANIFEST": (
            "provenance/CH07_RENDER_MANIFEST.csv", 23608,
            "b2fa453d7b96b51826aadddf2e8151144d6deae1d093dfa34841ab589ef464ed",
        ),
        "ARTIFACT-FAOA-ID-CH07-CONTACT-SHEET": (
            "provenance/CH07_CONTACT_SHEET.png", 3549427,
            "b52f348c29cdaa1cebd87c280ac0c01fad919e72a8f595ba2c48cb78ac283564",
        ),
        "ARTIFACT-FAOA-ID-CH07-VISUAL-ACCESSIBILITY-AUDIT": (
            "qa/CH07_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md", 6182,
            "c71c7b9bce1133d7c10bab8cf2e3bb4c310a8ceb701672ced87bbd6a412012f5",
        ),
        "ARTIFACT-FAOA-ID-CH07-QA-RECEIPT": (
            "provenance/CH07_BUILD_AND_QA_RECEIPT.md", 9855,
            "8c9e7afa90c27a748de6b2f44c1725ed467ba7f8e4f3960a0009459a25b0b525",
        ),
        "ARTIFACT-FAOA-ID-CH07-CORRECTIONS-LEDGER": (
            "provenance/SOURCE_CORRECTIONS.md", 23661,
            "285f20b012926002bb9085dab91b06cee3e0808bf7881b598a276c643ad8eea7",
        ),
    }
    if any(
        chapter_seven_artifact_identities[artifact_id] != identity
        for artifact_id, identity in fixed_chapter_seven_artifacts.items()
    ):
        raise ValueError("Chapter 7 bound artifact identities changed")
    chapter_seven_accessibility_artifact = chapter_seven_artifacts[6]
    if (
        chapter_seven_accessibility_artifact.get("visual_result") != "pass"
        or chapter_seven_accessibility_artifact.get("accessibility_gate_result") != "pass"
        or chapter_seven_accessibility_artifact.get("fully_accessible_pdf_claim") != "fail"
        or chapter_seven_accessibility_artifact.get("tagged_pdf") is not False
        or chapter_seven_accessibility_artifact.get("accessible_html_or_tagged_pdf_state") != "pending"
    ):
        raise ValueError("Chapter 7 accessibility limitation is not represented honestly")
    chapter_seven_pdf_artifact = chapter_seven_artifacts[2]
    if (
        chapter_seven_pdf_artifact.get("fixed_path_replays_byte_identical") is not True
        or chapter_seven_pdf_artifact.get("fixed_path_build_path")
        != "qa/build-through-ch07-a/functional-analysis-id-through-ch07.pdf"
        or chapter_seven_pdf_artifact.get("final_output_copy_state")
        != "present_byte_identical"
    ):
        raise ValueError("Chapter 7 fixed-path PDF replay binding changed")
    chapter_seven_receipt_artifact = chapter_seven_artifacts[7]
    if (
        chapter_seven_receipt_artifact.get("artifact_kind") != "admission_receipt"
        or chapter_seven_receipt_artifact.get("decision") != "admitted"
        or chapter_seven_receipt_artifact.get("lines") != 181
    ):
        raise ValueError("Chapter 7 admission-receipt artifact metadata changed")

    chapter_seven_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH07"
    ]
    expected_chapter_seven_qa_ids = [
        "QA-CH07-STRUCTURAL-20260822",
        "QA-CH07-MATH-20260822",
        "QA-CH07-LANGUAGE-20260822",
        "QA-CH07-BUILD-20260822",
        "QA-CH07-VISUAL-20260822",
        "QA-CH07-ACCESSIBILITY-20260822",
        "QA-CH07-RIGHTS-20260822",
        "QA-CH07-ADMISSION-20260822",
    ]
    if [record["id"] for record in chapter_seven_qa] != expected_chapter_seven_qa_ids:
        raise ValueError("Chapter 7 typed QA event inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH07-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH07_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "8c9e7afa90c27a748de6b2f44c1725ed467ba7f8e4f3960a0009459a25b0b525"
        for record in chapter_seven_qa
    ):
        raise ValueError("Chapter 7 QA events are not bound to the admission receipt")
    if any(record.get("result") != "pass" for record in chapter_seven_qa):
        raise ValueError("Chapter 7 QA gates are not passed")
    chapter_seven_admission = chapter_seven_qa[-1]
    if (
        chapter_seven_admission.get("result") != "pass"
        or chapter_seven_admission.get("decision") != "admitted"
        or chapter_seven_admission.get("all_required_admission_gates") != "pass"
        or chapter_seven_admission.get("typed_qa_event_ids") != expected_chapter_seven_qa_ids[:-1]
        or chapter_seven_admission.get("required_admission_gate_results", {}).get(
            "admission_receipt"
        ) != "pass"
        or chapter_seven_admission.get("receipt_path")
        != "provenance/CH07_BUILD_AND_QA_RECEIPT.md"
        or chapter_seven_admission.get("receipt_sha256")
        != "8c9e7afa90c27a748de6b2f44c1725ed467ba7f8e4f3960a0009459a25b0b525"
    ):
        raise ValueError("Chapter 7 admission event is not fully receipt-bound")
    if (
        chapter_seven_qa[0].get("semantic_units") != 74
        or chapter_seven_qa[0].get("segments") != 85
        or chapter_seven_qa[0].get("proof_hints") != 7
        or chapter_seven_qa[1].get("formula_map_records") != 309
        or chapter_seven_qa[1].get("reviewed_source_correction_maps") != 6
        or chapter_seven_qa[3].get("fixed_path_clean_builds_byte_identical") is not True
        or chapter_seven_qa[3].get("local_build_log_bytes") != 47575
        or chapter_seven_qa[3].get("local_build_log_sha256")
        != "35cf19763a0e6b8336ad962f49940791d17dad89d4b55451e10dd65e8f923af5"
        or chapter_seven_qa[4].get("pages_inspected") != 121
        or chapter_seven_qa[5].get("tagged_pdf") is not False
    ):
        raise ValueError("Chapter 7 QA metadata is inconsistent")

    chapter_seven_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH07"
    ]
    if [record["id"] for record in chapter_seven_corrections] != [
        f"FAOA-2015-CH07-CORR-{number:03d}" for number in range(1, 12)
    ]:
        raise ValueError("Chapter 7 correction inventory changed")
    expected_chapter_seven_locators = [
        "compact_operators.tex:22--26",
        "compact_operators.tex:117",
        "compact_operators.tex:127--129",
        "compact_operators.tex:137",
        "compact_operators.tex:162--165",
        "compact_operators.tex:299",
        "compact_operators.tex:397--400",
        "compact_operators.tex:422",
        "compact_operators.tex:425--430",
        "compact_operators.tex:436--437",
        "compact_operators.tex:497",
    ]
    if [record["source_locator"] for record in chapter_seven_corrections] != expected_chapter_seven_locators:
        raise ValueError("Chapter 7 correction locators changed")
    if any(
        record.get("ledger_sha256")
        != "285f20b012926002bb9085dab91b06cee3e0808bf7881b598a276c643ad8eea7"
        or record.get("ledger_section_sha256")
        != "9f262ed1003bf8824a0485c68caf117170458fb27651491a86d7b911797a4c6d"
        or record.get("qa_receipt_id") != "QA-CH07-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("receipt_path") != "provenance/CH07_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "8c9e7afa90c27a748de6b2f44c1725ed467ba7f8e4f3960a0009459a25b0b525"
        for record in chapter_seven_corrections
    ):
        raise ValueError("Chapter 7 correction evidence binding changed")

    chapter_seven_new_term_ids = [
        "TERM-TOTALLY-BOUNDED",
        "TERM-RELATIVELY-COMPACT",
        "TERM-CSTAR-ALGEBRA",
        "TERM-CSTAR-NORM",
        "TERM-CSTAR-SUBALGEBRA",
        "TERM-PARTIAL-ISOMETRY",
        "TERM-INITIAL",
        "TERM-SUPPORT",
        "TERM-FINAL",
        "TERM-SPACE",
        "TERM-FINAL-SPACE",
        "TERM-TRACE",
        "TERM-SIMILAR",
        "TERM-CONE",
        "TERM-PROPER-CONE",
        "TERM-TRACE-CLASS",
        "TERM-HILBERT-SCHMIDT",
    ]
    terminology_records = records_by_file["terminology.jsonl"]
    chapter_seven_new_terms = [
        record for record in terminology_records if record["id"] in chapter_seven_new_term_ids
    ]
    if [record["id"] for record in chapter_seven_new_terms] != chapter_seven_new_term_ids:
        raise ValueError("Chapter 7 bounded terminology inventory changed")
    proper_cone = next(
        record for record in chapter_seven_new_terms if record["id"] == "TERM-PROPER-CONE"
    )
    if proper_cone.get("preferred") != "proper" or proper_cone.get("rejected") != ["wajar"]:
        raise ValueError("Chapter 7 proper-cone terminology decision changed")
    chapter_seven_term_relations = [
        record
        for record in chapter_seven_relations
        if record["id"].startswith("FAOA-2015-CH07-REL-TERM-")
        and "EVIDENCE" not in record["id"]
    ]
    if len(chapter_seven_term_relations) != 26 or any(
        record["to_id"] not in ids for record in chapter_seven_term_relations
    ):
        raise ValueError("Chapter 7 defined-term relationships changed")

    chapter_seven_exercises = [
        record
        for record in records_by_file["exercise_support.jsonl"]
        if record["id"].startswith("FAOA-2015-CH07-")
    ]
    if [record["id"] for record in chapter_seven_exercises] != [
        "FAOA-2015-CH07-EXERCISE-SUPPORT-001"
    ]:
        raise ValueError("Chapter 7 exercise-support inventory changed")
    if (
        chapter_seven_exercises[0].get("upstream_hint_ids") != []
        or chapter_seven_exercises[0].get("upstream_inline_hint_state") != "absent"
        or chapter_seven_exercises[0].get("upstream_answer_state") != "absent"
        or chapter_seven_exercises[0].get("upstream_solution_state") != "absent"
        or chapter_seven_exercises[0].get("original_solution_state") != "queued_in_O001"
        or chapter_seven_exercises[0].get("provenance") != "separately_authored_not_Erdman"
    ):
        raise ValueError("Chapter 7 exercise-support semantics changed")

    canonical_text = json.dumps(all_records, ensure_ascii=False) + json.dumps(
        term_rows, ensure_ascii=False
    )
    if "00_control" in canonical_text or str(ROOT) in canonical_text or r"C:\Users" in canonical_text:
        raise ValueError("private or absolute task-local path leaked into canonical backend exports")

    for path in backend_files():
        data = path.read_bytes()
        data.decode("utf-8")
        if b"\r\n" in data:
            raise ValueError(f"CRLF found in deterministic backend file {path.name}")

    paths = backend_files()
    expected_manifest = render_manifest(paths)
    if MANIFEST.read_bytes().decode("utf-8") != expected_manifest:
        raise ValueError("checked-in backend manifest is stale or incorrect")
    manifest_fields, manifest_rows = load_csv_exact(MANIFEST)
    if manifest_fields != ["relative_path", "bytes", "sha256"]:
        raise ValueError("backend manifest header mismatch")
    if len(manifest_rows) != len(paths):
        raise ValueError("backend manifest row count mismatch")
    for row, path in zip(manifest_rows, paths):
        if (
            row["relative_path"] != path.name
            or int(row["bytes"]) != path.stat().st_size
            or row["sha256"] != sha(path)
        ):
            raise ValueError(f"backend manifest mismatch for {path.name}")

    print(run_one.stdout.strip())
    print(
        json.dumps(
            {
                "jsonl_files": len(jsonl_paths),
                "jsonl_records": len(all_records),
                "index_term_records": len(term_rows),
                "records_with_globally_unique_ids": len(ids),
                "relation_endpoints_checked": 2 * len(relation_records),
                "json_roundtrip_files": len(jsonl_paths),
                "csv_roundtrip_files": 2,
                "deterministic_generator_runs": 2,
                "backend_manifest_rows": len(manifest_rows),
                "backend_manifest_sha256": sha(MANIFEST),
                "result": "pass",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
