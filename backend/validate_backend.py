#!/usr/bin/env python3
"""Validate the deterministic Chapter 1--10 backend and its manifest."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
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
    "terminology_qa.jsonl",
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
    6_095,
    "1de61dcc0f8e2de97feda39ddf8d56dd4f3b9460dfc01150735b4ac61bcc36a2",
)
CH08_PREFIX_LOCKS = {
    "semantic_units.jsonl": (712_537, "f21e580723ab03a093a0587212cdf385eaa61e5caabc27b369e584c8afc6dc0c"),
    "segments.jsonl": (815_244, "343b268786efaa066b89ac87ebf1c2de332faf9068d9fe5bd84b6a45b4b63fd0"),
    "relations.jsonl": (996_724, "fbd92656c8be43ccb5988e1940f73096c1eee8333bce178f9a8aaadd07e3934a"),
    "formula_map.jsonl": (3_447_333, "e9791f05b585f20852dff9fce229524b490578f1f673e03bad5dd96f51fc196a"),
    "exercise_support.jsonl": (17_627, "d4c47b75c65f60234d8eea0cca7cde7d958418877a4d55fb7b260e6e18ffed0d"),
    "index_terms.csv": (321_487, "eda03880449d80ca81878962619ff95e52c9bd5ca9bce9673775e3c10dc6d4e8"),
    "artifacts.jsonl": (31_117, "1a82e4e965370c86803820b7bda089f30fe7e7e40743b5c96aa976542066f132"),
    "qa_events.jsonl": (47_290, "503fa717ec78ab6692271a712901375ecf7c5ab2f46b4483d7c1221998ac6895"),
    "corrections.jsonl": (90_287, "1e30f208d8ad6f64f1871c90c54d2626115a0c3cbbb610062d76708303c654a9"),
    "terminology.jsonl": (77_363, "40a9c5dd0e85b2c972ef6491a51ab5b9387c1ba3ffd019874f9240da4fbb2245"),
}
CH08_UNIT_PREFIX_LOCK = (
    9_076,
    "491daaa1f4b594fd17afd79a57beb1eed32175e1c7f74b6f9476c6c088770851",
)
CH08_UNIT_SUFFIX_LOCK = (
    4_635,
    "be0a27dba0b8a51db9f8bcc8ea8465fe05ac00144ec491f7c6088943869b61c2",
)
CH09_PREFIX_LOCKS = {
    "semantic_units.jsonl": (783_607, "9b559d11a0477e91484d453ec89ced8cd8feb2735d861670d6e7730de45ebc37"),
    "segments.jsonl": (890_177, "6c81fb6f6c5a71916b1ae8e9f1a3d654d7addbfff500910a935d23ae55f5ab25"),
    "relations.jsonl": (1_098_306, "443cd0a583907111371da68eac8c96115cca0cd4393cef0552a02353d3b9acf0"),
    "formula_map.jsonl": (3_720_317, "1c34c2302d282a0304ce6d5ed27838da5d344e85c6c9950eedd296b88de49457"),
    "exercise_support.jsonl": (18_758, "266724595e7418b01bdd981c40d23fa31ea985ac5c4d7c2adfd2919c426b78ce"),
    "index_terms.csv": (340_701, "a4e899a0108c7afd309eb10d7b26818add37c477c291db36f2a1409c31b1b75c"),
    "artifacts.jsonl": (38_750, "8cd2aed17bd05eb01acefdf8fd077bed0b84e3024f3507c8cd5861ed93c9c9d7"),
    "qa_events.jsonl": (56_661, "b50ec3b0b53f8b31c8fd65eea61192a5b1b22b4967cb5c35a4271d8379a3db7e"),
    "corrections.jsonl": (98_338, "513452e092ccc2719599c570e77b06cd32779baed7237f4a660f2313f1a1c270"),
    "terminology.jsonl": (84_238, "429b39ae517ca81be3c37d1323046e0fa6246f00bcc85b1e76e5e47f4df7a932"),
}
CH09_UNIT_PREFIX_LOCK = (
    10_536,
    "864e0e6a2973092b2b4533465e297203e1013e9e5d74009423da6b3c0fe4503f",
)
CH09_UNIT_SUFFIX_LOCK = (
    4_178,
    "1812c471ebe0120e85ce9b533bc7adc537778c216d6549fe852ec8d1056a967c",
)
CH10_PREFIX_LOCKS = {
    "semantic_units.jsonl": (887_156, "69cb894f6bb796ab1195ec8a7f13614c8f80e37df1b33662baf6582ad997815f"),
    "segments.jsonl": (998_274, "b81f691f34a99d02652395a753a751e8794921d2bc779dee63f239717b5f83e8"),
    "relations.jsonl": (1_231_458, "6ade8249fca5a8d89e22f17bfbb427314a83997a0d5511bbf8c7900ef36c7d4b"),
    "formula_map.jsonl": (4_119_919, "1c7c702cde9cbd02d4246a35117e8129530559818ddcf5915933f8d287f14952"),
    "exercise_support.jsonl": (19_302, "396af34f24d13d81c98b698838d7ffc92ce403e822534df682b24bac05b76814"),
    "index_terms.csv": (364_586, "8b6be5ff9f2c48868feef6328e615efc0fd5b10d1b7e5645a23f281d4d7bed90"),
    "artifacts.jsonl": (46_109, "941a6e92c90182c33da4a0eaa2cc9d2a87046bdda1f3a054a83b9b770a45b56d"),
    "qa_events.jsonl": (64_088, "d6c6f48a9078dd2bed9e7417111bbe2c4308942c1cdd8e2e15c0640b379caed4"),
    "corrections.jsonl": (126_130, "319a20d4d18a632b71a93aed15b6e6f533b23fa622a73bb26cce6aff35ff7b91"),
    "terminology.jsonl": (98_578, "98d69653ba962b1f88f84e9de28e13b9fa1c8f3fcbfbdc319e89b182f68a2144"),
}
CH10_UNIT_PREFIX_LOCK = (
    12_022,
    "297418f7329522e269bb7c66997665167e1ce8034a60dd2b06b34ddfceff0e4f",
)
CH10_UNIT_SUFFIX_LOCK = (
    3_731,
    "cfdb40e6debfad35ab5a0adaf8c7f0e6c2a6518ce1d7d3193e90e8b7f09cf6bc",
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
    if (len(prefix), sha_bytes(prefix)) != CH06_UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--6 byte prefix changed")


def verify_ch08_prefixes() -> None:
    for name, (size, expected_sha) in CH08_PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size or sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1--7 byte prefix changed")
    unit_lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    prefix = b"".join(unit_lines[:7])
    if (len(prefix), sha_bytes(prefix)) != CH08_UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--7 byte prefix changed")


def verify_ch09_prefixes() -> None:
    for name, (size, expected_sha) in CH09_PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size or sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1--8 byte prefix changed")
    unit_lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    prefix = b"".join(unit_lines[:8])
    # Chapter 10 has now replaced its queued row; preserve only the still-queued
    # Chapter 11--bridge suffix while the Chapter 1--8/Chapter 9 boundaries are
    # independently locked by the historical and current prefix checks.
    suffix = b"".join(unit_lines[10:])
    if (len(prefix), sha_bytes(prefix)) != CH09_UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--8 byte prefix changed")
    if (len(suffix), sha_bytes(suffix)) != CH10_UNIT_SUFFIX_LOCK:
        raise ValueError("units.jsonl Chapter 11--bridge byte suffix changed")


def verify_ch10_prefixes() -> None:
    for name, (size, expected_sha) in CH10_PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size or sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1--9 byte prefix changed")
    unit_lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    prefix = b"".join(unit_lines[:9])
    suffix = b"".join(unit_lines[10:])
    if (len(prefix), sha_bytes(prefix)) != CH10_UNIT_PREFIX_LOCK:
        raise ValueError("units.jsonl Chapter 1--9 byte prefix changed")
    if (len(suffix), sha_bytes(suffix)) != CH10_UNIT_SUFFIX_LOCK:
        raise ValueError("units.jsonl Chapter 11--bridge byte suffix changed")


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
    verify_ch08_prefixes()
    verify_ch09_prefixes()
    verify_ch10_prefixes()
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
    verify_ch08_prefixes()
    verify_ch09_prefixes()
    verify_ch10_prefixes()
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
    verify_ch08_prefixes()
    verify_ch09_prefixes()
    verify_ch10_prefixes()
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

    chapter_eight = chapter_units[7]
    chapter_eight_expected = {
        "source_bytes": 25716,
        "source_lines": 611,
        "source_sha256": "ae68cf224c6218ecd501cc983428cf924a3c361c6324a6b40793b1e9ba44b4dd",
        "target_bytes": 26947,
        "target_lines": 603,
        "target_sha256": "1120da36ebd0793690ecb47b33b921c81376d1bf7d2f03d9821b79356dfd03bc",
        "target_title": "Beberapa Teori Spektral",
        "course_role": "d20_core",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 8,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch08.tex",
        "build_master_bytes": 9714,
        "build_master_lines": 334,
        "build_master_sha256": "d0b4130b9fa6f85baef22f316ea914d5519bf30d6e82d8e6d824f2cf211c1998",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-8.pdf",
        "artifact_bytes": 1593249,
        "artifact_pages": 129,
        "artifact_sha256": "fb6488691e2127bc0b8e3f94f38033eb3bdbe0c61efedc66c07de8f3b3444fbd",
        "artifact_state": "canonical_output_copy_present_and_frozen",
        "qa_receipt_id": "QA-CH08-ADMISSION-20260822",
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH08_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "fe74240d2ab6bb50fdc9ae3fb019c5dc77cee20250cfb5c46cd9a773b52cac83",
        "admission_state": "admitted",
        "publication_state": "pending",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_eight_expected.items():
        if chapter_eight.get(field) != expected:
            raise ValueError(f"Chapter 8 {field} invariant failed")
    source_path = ROOT / "source" / "upstream" / "spectrum.tex"
    target_path = ROOT / "source" / "id-ID" / "spectrum-id.tex"
    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        25716,
        611,
        "ae68cf224c6218ecd501cc983428cf924a3c361c6324a6b40793b1e9ba44b4dd",
    ):
        raise ValueError("Chapter 8 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        26947,
        603,
        "1120da36ebd0793690ecb47b33b921c81376d1bf7d2f03d9821b79356dfd03bc",
    ):
        raise ValueError("Chapter 8 target authority file mismatch")

    chapter_nine = chapter_units[8]
    chapter_nine_expected = {
        "source_bytes": 35022,
        "source_lines": 806,
        "source_sha256": "62bc645c9d0972856913098d90d4baec7a8b0f470d4d380a880416f64cd5bce4",
        "target_bytes": 37705,
        "target_lines": 804,
        "target_sha256": "791868776a07f4c854f1c13d295da23a2559b88dcac48523fb0390e1e5330ee1",
        "target_title": "Ruang Vektor Topologis",
        "course_role": "advanced_continuation",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 26,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch09.tex",
        "build_master_bytes": 9780,
        "build_master_lines": 335,
        "build_master_sha256": "acba53fd01601ecd49516c01fb00e38af7bfcafbbbff0358a87dea864c591e3f",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf",
        "artifact_bytes": 1686477,
        "artifact_pages": 140,
        "artifact_sha256": "99215ff5987f720600152da902cec8f521329692931a0dbf89e82ef2d4ff6076",
        "artifact_state": "canonical_output_copy_present_and_frozen",
        "qa_receipt_id": "QA-CH09-ADMISSION-20260822",
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH09_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "08a103ce79f1f9406ddb877c01e8f921cde0f323fd6d1e731650eedbf1bd8794",
        "admission_state": "admitted",
        "publication_state": "pending",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_nine_expected.items():
        if chapter_nine.get(field) != expected:
            raise ValueError(f"Chapter 9 {field} invariant failed")
    source_bytes = (ROOT / "source" / "upstream" / "topvecspaces.tex").read_bytes()
    target_bytes = (ROOT / "source" / "id-ID" / "topvecspaces-id.tex").read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        35022,
        806,
        "62bc645c9d0972856913098d90d4baec7a8b0f470d4d380a880416f64cd5bce4",
    ):
        raise ValueError("Chapter 9 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        37705,
        804,
        "791868776a07f4c854f1c13d295da23a2559b88dcac48523fb0390e1e5330ee1",
    ):
        raise ValueError("Chapter 9 target authority file mismatch")

    chapter_ten = chapter_units[9]
    chapter_ten_expected = {
        "source_bytes": 42703,
        "source_lines": 894,
        "source_sha256": "31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8",
        "target_bytes": 42627,
        "target_lines": 876,
        "target_sha256": "6456f9def822da572e117f3ec368931f0bfb441840aa0785be1df6080bbb6840",
        "target_title": "Distribusi",
        "course_role": "advanced_continuation",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 16,
        "build_master_path": "source/id-ID/functional-analysis-id-through-ch10.tex",
        "build_master_bytes": 9866,
        "build_master_lines": 336,
        "build_master_sha256": "5de05f7a154bea99d11924fc21dbbf7495c8642d5a3c58e48e0fdd053dd400b4",
        "artifact_path": "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf",
        "artifact_bytes": 1796056,
        "artifact_pages": 153,
        "artifact_sha256": "1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc",
        "artifact_state": "canonical_output_copy_present_and_frozen",
        "qa_receipt_id": "QA-CH10-ADMISSION-20260822",
        "receipt_document_state": "present",
        "receipt_path": "provenance/CH10_BUILD_AND_QA_RECEIPT.md",
        "receipt_sha256": "2a4d7a6379b1cc4f634fd45d75413133670c134d9b3ba55c363ff273645b9c1f",
        "admission_state": "admitted",
        "publication_state": "pending",
        "rights_id": "RIGHTS-ERDMAN-CC-BY-SA-4.0",
    }
    for field, expected in chapter_ten_expected.items():
        if chapter_ten.get(field) != expected:
            raise ValueError(f"Chapter 10 {field} invariant failed")
    source_bytes = (ROOT / "source" / "upstream" / "distributions.tex").read_bytes()
    target_bytes = (ROOT / "source" / "id-ID" / "distributions-id.tex").read_bytes()
    if (len(source_bytes), len(source_bytes.splitlines()), sha_bytes(source_bytes)) != (
        42703,
        894,
        "31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8",
    ):
        raise ValueError("Chapter 10 source authority file mismatch")
    if (len(target_bytes), len(target_bytes.splitlines()), sha_bytes(target_bytes)) != (
        42627,
        876,
        "6456f9def822da572e117f3ec368931f0bfb441840aa0785be1df6080bbb6840",
    ):
        raise ValueError("Chapter 10 target authority file mismatch")

    expected_counts = {
        "units.jsonl": 18,
        "semantic_units.jsonl": 1179,
        "segments.jsonl": 1397,
        "relations.jsonl": 5215,
        "formula_map.jsonl": 7517,
        "exercise_support.jsonl": 48,
        "artifacts.jsonl": 88,
        "qa_events.jsonl": 76,
        "corrections.jsonl": 172,
        "terminology.jsonl": 283,
        "terminology_qa.jsonl": 7,
    }
    for name, count in expected_counts.items():
        if len(records_by_file[name]) != count:
            raise ValueError(f"{name} expected {count}, got {len(records_by_file[name])}")
    if len(term_rows) != 1524:
        raise ValueError(f"index_terms.csv expected 1524 rows, got {len(term_rows)}")

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

    chapter_eight_counts = {
        "semantic_units.jsonl": 86,
        "segments.jsonl": 96,
        "relations.jsonl": 388,
        "formula_map.jsonl": 416,
        "exercise_support.jsonl": 2,
    }
    for name, count in chapter_eight_counts.items():
        actual = sum(
            record["id"].startswith("FAOA-2015-CH08-")
            for record in records_by_file[name]
        )
        if actual != count:
            raise ValueError(f"{name} Chapter 8 expected {count}, got {actual}")
    chapter_eight_terms = [
        row for row in term_rows if row["id"].startswith("FAOA-2015-CH08-")
    ]
    if len(chapter_eight_terms) != 73:
        raise ValueError("Chapter 8 index-term projection invariant failed")
    chapter_eight_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH08-")
    ]
    chapter_eight_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH08-")
    ]
    if any(
        record.get("translation_state") != "admitted"
        or record.get("qa_state") != "passed"
        for record in chapter_eight_semantic + chapter_eight_segments
    ):
        raise ValueError("Chapter 8 semantic/segment pending-admission state differs")
    chapter_eight_sections = [
        (record.get("source_title_tex"), record.get("target_title_tex"))
        for record in chapter_eight_semantic
        if record["unit_kind"] == "section"
    ]
    if chapter_eight_sections != [
        ("The Spectrum", "Spektrum"),
        ("Spectra of Hilbert Space Operators", "Spektrum Operator Ruang Hilbert"),
    ]:
        raise ValueError("Chapter 8 ordered section titles changed")

    chapter_nine_counts = {
        "semantic_units.jsonl": 125,
        "segments.jsonl": 137,
        "relations.jsonl": 513,
        "formula_map.jsonl": 606,
        "exercise_support.jsonl": 1,
    }
    for name, count in chapter_nine_counts.items():
        actual = sum(
            record["id"].startswith("FAOA-2015-CH09-")
            for record in records_by_file[name]
        )
        if actual != count:
            raise ValueError(f"{name} Chapter 9 expected {count}, got {actual}")
    chapter_nine_terms = [
        row for row in term_rows if row["id"].startswith("FAOA-2015-CH09-")
    ]
    if len(chapter_nine_terms) != 91:
        raise ValueError("Chapter 9 index-term projection invariant failed")
    chapter_nine_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH09-")
    ]
    chapter_nine_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH09-")
    ]
    if any(
        record.get("translation_state") != "admitted"
        or record.get("qa_state") != "passed"
        for record in chapter_nine_semantic + chapter_nine_segments
    ):
        raise ValueError("Chapter 9 semantic/segment admission state differs")
    chapter_nine_sections = [
        (record.get("source_title_tex"), record.get("target_title_tex"))
        for record in chapter_nine_semantic
        if record["unit_kind"] == "section"
    ]
    if chapter_nine_sections != [
        ("Balanced Sets and Absorbing Sets", "Himpunan Seimbang dan Himpunan Penyerap"),
        ("Filters", "Filter"),
        ("Compatible Topologies", "Topologi Kompatibel"),
        ("Quotients", "Hasil Bagi"),
        ("Locally Convex Spaces and Seminorms", "Ruang Konveks Lokal dan Seminorma"),
        ("Fr\\'echet Spaces", "Ruang Fr\\'echet"),
    ]:
        raise ValueError("Chapter 9 ordered section titles changed")

    chapter_ten_counts = {
        "semantic_units.jsonl": 116,
        "segments.jsonl": 132,
        "relations.jsonl": 523,
        "formula_map.jsonl": 648,
        "exercise_support.jsonl": 11,
    }
    for name, count in chapter_ten_counts.items():
        actual = sum(
            record["id"].startswith("FAOA-2015-CH10-")
            for record in records_by_file[name]
        )
        if actual != count:
            raise ValueError(f"{name} Chapter 10 expected {count}, got {actual}")
    chapter_ten_terms = [
        row for row in term_rows if row["id"].startswith("FAOA-2015-CH10-")
    ]
    if len(chapter_ten_terms) != 101:
        raise ValueError("Chapter 10 index-term projection invariant failed")
    chapter_ten_semantic = [
        record
        for record in records_by_file["semantic_units.jsonl"]
        if record["id"].startswith("FAOA-2015-CH10-")
    ]
    chapter_ten_segments = [
        record
        for record in records_by_file["segments.jsonl"]
        if record["id"].startswith("FAOA-2015-CH10-")
    ]
    if any(
        record.get("translation_state") != "admitted"
        or record.get("qa_state") != "passed"
        for record in chapter_ten_semantic + chapter_ten_segments
    ):
        raise ValueError("Chapter 10 semantic/segment admission state differs")
    chapter_ten_sections = [
        (record.get("source_title_tex"), record.get("target_title_tex"))
        for record in chapter_ten_semantic
        if record["unit_kind"] == "section"
    ]
    if chapter_ten_sections != [
        ("Inductive Limits", "Limit Induktif"),
        ("$LF$-spaces", "Ruang-$LF$"),
        ("Distributions", "Distribusi"),
        ("Convolution", "Konvolusi"),
        ("Distributional Solutions to Ordinary Differential Equations", "Solusi Distribusional untuk Persamaan Diferensial Biasa"),
        ("The Fourier Transform", "Transformasi Fourier"),
    ]:
        raise ValueError("Chapter 10 ordered section titles changed")

    formula_records = records_by_file["formula_map.jsonl"]
    source_formula_count = sum(len(record["source_formula_ids"]) for record in formula_records)
    target_formula_count = sum(len(record["target_formula_ids"]) for record in formula_records)
    exact_alignment_kinds = {
        "preserved_exact_after_whitespace_normalization",
        "preserved_exact_after_text_aware_whitespace_normalization",
        "preserved_exact_after_text_aware_whitespace_normalization_reordered",
        "preserved_math_key_after_localized_text_substitution",
    }
    exact_formula_count = sum(record["alignment"] in exact_alignment_kinds for record in formula_records)
    if (source_formula_count, target_formula_count, exact_formula_count) != (7518, 7522, 7371):
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

    chapter_eight_formula = [
        record for record in formula_records if record["id"].startswith("FAOA-2015-CH08-")
    ]
    chapter_eight_formula_counts = (
        sum(len(record["source_formula_ids"]) for record in chapter_eight_formula),
        sum(len(record["target_formula_ids"]) for record in chapter_eight_formula),
        sum(record["alignment"] in exact_alignment_kinds for record in chapter_eight_formula),
        sum(record.get("math_key_alignment") == "equal" for record in chapter_eight_formula),
    )
    if chapter_eight_formula_counts != (414, 416, 411, 411):
        raise ValueError("Chapter 8 formula-map coverage invariant failed")
    chapter_eight_alignment_counts = {
        alignment: sum(record["alignment"] == alignment for record in chapter_eight_formula)
        for alignment in {
            "preserved_exact_after_text_aware_whitespace_normalization",
            "preserved_exact_after_text_aware_whitespace_normalization_reordered",
            "reviewed_source_correction",
            "reviewed_target_only_source_correction",
        }
    }
    if chapter_eight_alignment_counts != {
        "preserved_exact_after_text_aware_whitespace_normalization": 409,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 2,
        "reviewed_source_correction": 3,
        "reviewed_target_only_source_correction": 2,
    }:
        raise ValueError("Chapter 8 reviewed formula-alignment inventory changed")
    chapter_eight_source_formula_ids = [
        formula_id
        for record in chapter_eight_formula
        for formula_id in record["source_formula_ids"]
    ]
    chapter_eight_target_formula_ids = [
        formula_id
        for record in chapter_eight_formula
        for formula_id in record["target_formula_ids"]
    ]
    if sorted(chapter_eight_source_formula_ids) != [
        f"FAOA-2015-CH08-SRC-MATH-{number:04d}" for number in range(1, 415)
    ] or chapter_eight_target_formula_ids != [
        f"FAOA-2015-CH08-ID-MATH-{number:04d}" for number in range(1, 417)
    ]:
        raise ValueError("Chapter 8 stable source/target formula coverage changed")
    chapter_eight_correction_formula_ids = {
        263: "FAOA-2015-CH08-CORR-004",
        280: "FAOA-2015-CH08-CORR-005",
        303: "FAOA-2015-CH08-CORR-006",
        304: "FAOA-2015-CH08-CORR-006",
        391: "FAOA-2015-CH08-CORR-008",
    }
    if {
        int(record["id"].rsplit("-", 1)[1]): record.get("correction_id")
        for record in chapter_eight_formula
        if record.get("correction_id")
    } != chapter_eight_correction_formula_ids:
        raise ValueError("Chapter 8 formula-to-correction binding changed")
    if [
        int(record["id"].rsplit("-", 1)[1])
        for record in chapter_eight_formula
        if record.get("sequence_opcode") == "reorder"
    ] != [64, 65]:
        raise ValueError("Chapter 8 localization-only formula reorderings changed")
    if any(
        record.get("correction_id")
        for record in chapter_eight_formula
        if record.get("delta_class") == "localization_phrase_reordering"
    ):
        raise ValueError("Chapter 8 localization-only formula reorderings became corrections")

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
            # Historical artifact records retain their boundary hashes, while
            # this cumulative human-readable ledger is rewritten into a
            # chapter-indexed document at later admissions. Validate the exact
            # current identity once rather than claiming byte-prefix continuity.
            headings = [
                line
                for line in data.decode("utf-8").splitlines()
                if line.startswith("## Chapter ")
            ]
            if (
                (len(data), sha_bytes(data))
                != (
                    32495,
                    "8bd1be45b70a5e2395e67c20f192f89fc658f3d158d8ff7bb9b1e9cef77b947b",
                )
                or headings != [
                    "## Chapter 1", "## Chapter 2", "## Chapter 3", "## Chapter 4",
                    "## Chapter 5", "## Chapter 6", "## Chapter 7", "## Chapter 8",
                    "## Chapter 9", "## Chapter 10",
                ]
            ):
                raise ValueError("chapter-indexed Chapters 1--10 correction ledger changed")
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

    chapter_eight_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH08-")
    ]
    chapter_eight_relation_type_counts = {
        relation_type: sum(
            record["relation_type"] == relation_type
            for record in chapter_eight_relations
        )
        for relation_type in {
            "contains", "translates", "precedes", "declares_label", "xref",
            "cites", "hints", "comments_on", "uses_term", "licensed_under",
            "has_artifact", "terminology_evidence", "has_qa_event",
            "documents_correction",
        }
    }
    if chapter_eight_relation_type_counts != {
        "contains": 86,
        "translates": 96,
        "precedes": 95,
        "declares_label": 28,
        "xref": 16,
        "cites": 3,
        "hints": 12,
        "comments_on": 1,
        "uses_term": 20,
        "licensed_under": 1,
        "has_artifact": 11,
        "terminology_evidence": 3,
        "has_qa_event": 8,
        "documents_correction": 8,
    }:
        raise ValueError("Chapter 8 relation-type inventory changed")
    chapter_eight_xrefs = [
        record
        for record in chapter_eight_relations
        if record["id"].startswith("FAOA-2015-CH08-REL-XREF-")
    ]
    if {
        resolution: sum(record["resolution"] == resolution for record in chapter_eight_xrefs)
        for resolution in ("local", "admitted_prior_unit", "pending_later_source_unit")
    } != {
        "local": 9,
        "admitted_prior_unit": 7,
        "pending_later_source_unit": 0,
    } or any(record["to_id"] not in ids for record in chapter_eight_xrefs):
        raise ValueError("Chapter 8 reference closure changed")
    if any(
        record.get("relation_type") == "resolves_pending_reference"
        for record in chapter_eight_relations
    ):
        raise ValueError("Chapter 8 falsely claims a prior pending-reference closure")
    chapter_eight_comments = [
        record for record in chapter_eight_relations if record["relation_type"] == "comments_on"
    ]
    if [(record["from_id"], record["to_id"]) for record in chapter_eight_comments] != [
        ("FAOA-2015-CH08-NODE-0051", "FAOA-2015-CH08-NODE-0050")
    ]:
        raise ValueError("Chapter 8 proof-comment relation changed")

    chapter_eight_artifacts = [
        record for record in artifact_records if record.get("unit_id") == "FAOA-2015-CH08"
    ]
    expected_chapter_eight_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH08-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH08-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH08-PDF",
        "ARTIFACT-FAOA-ID-CH08-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH08-DELTA-REPORT",
        "ARTIFACT-FAOA-ID-CH08-BILINGUAL-REVIEW",
        "ARTIFACT-FAOA-ID-CH08-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH08-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH08-VISUAL-ACCESSIBILITY-AUDIT",
        "ARTIFACT-FAOA-ID-CH08-QA-RECEIPT",
        "ARTIFACT-FAOA-ID-CH08-CORRECTIONS-LEDGER",
    ]
    if [record["id"] for record in chapter_eight_artifacts] != expected_chapter_eight_artifact_ids:
        raise ValueError("Chapter 8 artifact inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH08-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("admission_state") != "admitted"
        or record.get("receipt_path") != "provenance/CH08_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "fe74240d2ab6bb50fdc9ae3fb019c5dc77cee20250cfb5c46cd9a773b52cac83"
        for record in chapter_eight_artifacts
    ):
        raise ValueError("Chapter 8 artifacts are not bound to the admission receipt")
    chapter_eight_artifact_identities = {
        record["id"]: (record["path"], record["bytes"], record["sha256"])
        for record in chapter_eight_artifacts
    }
    fixed_chapter_eight_artifacts = {
        "ARTIFACT-FAOA-ID-CH08-TARGET-TEX": (
            "source/id-ID/spectrum-id.tex", 26947,
            "1120da36ebd0793690ecb47b33b921c81376d1bf7d2f03d9821b79356dfd03bc",
        ),
        "ARTIFACT-FAOA-ID-THROUGH-CH08-MASTER": (
            "source/id-ID/functional-analysis-id-through-ch08.tex", 9714,
            "d0b4130b9fa6f85baef22f316ea914d5519bf30d6e82d8e6d824f2cf211c1998",
        ),
        "ARTIFACT-FAOA-ID-THROUGH-CH08-PDF": (
            "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-8.pdf", 1593249,
            "fb6488691e2127bc0b8e3f94f38033eb3bdbe0c61efedc66c07de8f3b3444fbd",
        ),
        "ARTIFACT-FAOA-ID-CH08-STRUCTURAL-CHECKER": (
            "qa/check_ch08_translation.py", 41639,
            "2720ec3cbe46060d65079a496e5fc550744c25863c11bdb1b5bb84047b14d54f",
        ),
        "ARTIFACT-FAOA-ID-CH08-DELTA-REPORT": (
            "qa/CH08_CLASSIFIED_DELTA_INVENTORY.md", 10143,
            "efb89e83e3bc66861f941175e9abdc40d02e93c7b1d1e0fbe6e9afcadd1c0a4f",
        ),
        "ARTIFACT-FAOA-ID-CH08-BILINGUAL-REVIEW": (
            "qa/CH08_INDEPENDENT_BILINGUAL_REVIEW.md", 5504,
            "74647e7a65f10026601cb6b54c97badf6528809620d4d2ef93e9b690d96c078f",
        ),
        "ARTIFACT-FAOA-ID-CH08-RENDER-MANIFEST": (
            "provenance/CH08_RENDER_MANIFEST.csv", 25114,
            "796f36332ef748a4b1a7d8f01b7d75c7ec9da5236640f059d31df14fa3ec3e71",
        ),
        "ARTIFACT-FAOA-ID-CH08-CONTACT-SHEET": (
            "provenance/CH08_CONTACT_SHEET.png", 3781079,
            "5d53f2c381f8108dd3a947e2ad85c744c21f2070c6397611b525af978690b6cf",
        ),
        "ARTIFACT-FAOA-ID-CH08-VISUAL-ACCESSIBILITY-AUDIT": (
            "qa/CH08_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md", 6668,
            "4ee0a948e108e905594c0bcc1858f050a001db1c60136a7e2c8135d64cf9520b",
        ),
        "ARTIFACT-FAOA-ID-CH08-QA-RECEIPT": (
            "provenance/CH08_BUILD_AND_QA_RECEIPT.md", 9732,
            "fe74240d2ab6bb50fdc9ae3fb019c5dc77cee20250cfb5c46cd9a773b52cac83",
        ),
        "ARTIFACT-FAOA-ID-CH08-CORRECTIONS-LEDGER": (
            "provenance/SOURCE_CORRECTIONS.md", 25794,
            "93836f6e440e81cb606a55a25c837318b620348379f4690923ab700bb6b3d23b",
        ),
    }
    if chapter_eight_artifact_identities != fixed_chapter_eight_artifacts:
        raise ValueError("Chapter 8 bound artifact identities changed")
    chapter_eight_accessibility_artifact = chapter_eight_artifacts[8]
    if (
        chapter_eight_accessibility_artifact.get("visual_result") != "pass"
        or chapter_eight_accessibility_artifact.get("accessibility_gate_result") != "pass"
        or chapter_eight_accessibility_artifact.get("fully_accessible_pdf_claim") != "fail"
        or chapter_eight_accessibility_artifact.get("tagged_pdf") is not False
        or chapter_eight_accessibility_artifact.get("accessible_html_or_tagged_pdf_state")
        != "pending"
    ):
        raise ValueError("Chapter 8 accessibility limitation is not represented honestly")

    chapter_eight_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH08"
    ]
    expected_chapter_eight_qa_ids = [
        "QA-CH08-STRUCTURAL-20260822",
        "QA-CH08-MATH-20260822",
        "QA-CH08-LANGUAGE-20260822",
        "QA-CH08-BUILD-20260822",
        "QA-CH08-VISUAL-20260822",
        "QA-CH08-ACCESSIBILITY-20260822",
        "QA-CH08-RIGHTS-20260822",
        "QA-CH08-ADMISSION-20260822",
    ]
    if [record["id"] for record in chapter_eight_qa] != expected_chapter_eight_qa_ids:
        raise ValueError("Chapter 8 typed QA event inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH08-ADMISSION-20260822"
        or record.get("receipt_document_state") != "present"
        or record.get("admission_state") != "admitted"
        or record.get("receipt_path") != "provenance/CH08_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "fe74240d2ab6bb50fdc9ae3fb019c5dc77cee20250cfb5c46cd9a773b52cac83"
        for record in chapter_eight_qa
    ):
        raise ValueError("Chapter 8 QA events are not bound to the admission receipt")
    if any(record.get("result") != "pass" for record in chapter_eight_qa):
        raise ValueError("Chapter 8 QA gates are not passed")
    chapter_eight_admission = chapter_eight_qa[-1]
    if (
        chapter_eight_admission.get("result") != "pass"
        or chapter_eight_admission.get("decision") != "admitted"
        or chapter_eight_admission.get("all_nonreceipt_gates") != "pass"
        or chapter_eight_admission.get("all_required_admission_gates") != "pass"
        or chapter_eight_admission.get("typed_qa_event_ids")
        != expected_chapter_eight_qa_ids[:-1]
        or chapter_eight_admission.get("required_admission_gate_results", {}).get(
            "admission_receipt"
        ) != "pass"
    ):
        raise ValueError("Chapter 8 admission event is inconsistent")
    if (
        chapter_eight_qa[0].get("semantic_units") != 86
        or chapter_eight_qa[0].get("segments") != 96
        or chapter_eight_qa[0].get("proof_hints") != 12
        or chapter_eight_qa[0].get("proof_comments") != 1
        or chapter_eight_qa[1].get("formula_map_records") != 416
        or chapter_eight_qa[1].get("reviewed_source_correction_maps") != 5
        or chapter_eight_qa[4].get("pages_inspected") != 129
        or chapter_eight_qa[5].get("tagged_pdf") is not False
    ):
        raise ValueError("Chapter 8 QA metadata is inconsistent")

    chapter_eight_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH08"
    ]
    if [record["id"] for record in chapter_eight_corrections] != [
        f"FAOA-2015-CH08-CORR-{number:03d}" for number in range(1, 9)
    ] or [record["source_locator"] for record in chapter_eight_corrections] != [
        "spectrum.tex:17",
        "spectrum.tex:178--181",
        "spectrum.tex:348",
        "spectrum.tex:372",
        "spectrum.tex:396--412",
        "spectrum.tex:443--450",
        "spectrum.tex:509",
        "spectrum.tex:547",
    ]:
        raise ValueError("Chapter 8 correction inventory changed")
    if any(
        record.get("ledger_sha256")
        != "93836f6e440e81cb606a55a25c837318b620348379f4690923ab700bb6b3d23b"
        or record.get("ledger_section_sha256")
        != "8b83e5625e13d22c9edb3396230515d038d8fc3bd513b4a7866602bbf25e07da"
        or record.get("ledger_block_sha256")
        != "bb76200eee25a2a5e8305f7e62570ae4eab4a50c3785a11c78cdc4a4007c409c"
        or record.get("receipt_document_state") != "present"
        or record.get("admission_state") != "admitted"
        or record.get("receipt_path") != "provenance/CH08_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "fe74240d2ab6bb50fdc9ae3fb019c5dc77cee20250cfb5c46cd9a773b52cac83"
        for record in chapter_eight_corrections
    ):
        raise ValueError("Chapter 8 correction evidence binding changed")

    chapter_eight_new_term_ids = [
        "TERM-LEFT-INVERTIBLE",
        "TERM-LEFT-INVERSE",
        "TERM-RIGHT-INVERTIBLE",
        "TERM-RIGHT-INVERSE",
        "TERM-INVERTIBLE",
        "TERM-SPECTRUM",
        "TERM-BANACH-ALGEBRA-HOMOMORPHISM",
        "TERM-RESOLVENT-MAPPING",
        "TERM-ANALYTIC",
        "TERM-ENTIRE",
        "TERM-SPECTRAL-RADIUS",
        "TERM-RESOLVENT-SET",
        "TERM-POINT-SPECTRUM",
        "TERM-APPROXIMATE-POINT-SPECTRUM",
        "TERM-COMPRESSION-SPECTRUM",
        "TERM-RESIDUAL-SPECTRUM",
    ]
    chapter_eight_new_terms = [
        record for record in terminology_records if record["id"] in chapter_eight_new_term_ids
    ]
    if [record["id"] for record in chapter_eight_new_terms] != chapter_eight_new_term_ids:
        raise ValueError("Chapter 8 bounded terminology inventory changed")
    chapter_eight_term_relations = [
        record
        for record in chapter_eight_relations
        if record["id"].startswith("FAOA-2015-CH08-REL-TERM-")
        and "EVIDENCE" not in record["id"]
    ]
    if len(chapter_eight_term_relations) != 20 or any(
        record["to_id"] not in ids for record in chapter_eight_term_relations
    ):
        raise ValueError("Chapter 8 defined-term relationships changed")

    chapter_eight_exercises = [
        record
        for record in records_by_file["exercise_support.jsonl"]
        if record["id"].startswith("FAOA-2015-CH08-")
    ]
    if [record["id"] for record in chapter_eight_exercises] != [
        "FAOA-2015-CH08-EXERCISE-SUPPORT-001",
        "FAOA-2015-CH08-EXERCISE-SUPPORT-002",
    ] or [record.get("upstream_inline_hint_source_lines") for record in chapter_eight_exercises] != [
        None,
        [401],
    ] or any(
        record.get("upstream_hint_ids")
        or record.get("upstream_answer_state") != "absent"
        or record.get("upstream_solution_state") != "absent"
        or record.get("provenance") != "separately_authored_not_Erdman"
        for record in chapter_eight_exercises
    ):
        raise ValueError("Chapter 8 exercise-support semantics changed")

    chapter_nine_formula = [
        record
        for record in formula_records
        if record["id"].startswith("FAOA-2015-CH09-")
    ]
    chapter_nine_alignment_counts: dict[str, int] = {}
    for record in chapter_nine_formula:
        alignment = record["alignment"]
        chapter_nine_alignment_counts[alignment] = (
            chapter_nine_alignment_counts.get(alignment, 0) + 1
        )
    if chapter_nine_alignment_counts != {
        "preserved_exact_after_text_aware_whitespace_normalization": 585,
        "preserved_math_key_after_localized_text_substitution": 3,
        "reviewed_source_correction": 15,
        "reviewed_target_only_source_correction": 3,
    }:
        raise ValueError("Chapter 9 formula-alignment inventory changed")
    chapter_nine_source_formula_ids = {
        formula_id
        for record in chapter_nine_formula
        for formula_id in record["source_formula_ids"]
    }
    chapter_nine_target_formula_ids = {
        formula_id
        for record in chapter_nine_formula
        for formula_id in record["target_formula_ids"]
    }
    if chapter_nine_source_formula_ids != {
        f"FAOA-2015-CH09-SRC-MATH-{number:04d}" for number in range(1, 604)
    } or chapter_nine_target_formula_ids != {
        f"FAOA-2015-CH09-ID-MATH-{number:04d}" for number in range(1, 607)
    }:
        raise ValueError("Chapter 9 stable formula-ID closure changed")
    expected_chapter_nine_formula_corrections = {
        139: "FAOA-2015-CH09-CORR-003",
        **{number: "FAOA-2015-CH09-CORR-006" for number in range(186, 190)},
        293: "FAOA-2015-CH09-CORR-020",
        439: "FAOA-2015-CH09-CORR-021",
        440: "FAOA-2015-CH09-CORR-021",
        459: "FAOA-2015-CH09-CORR-023",
        470: "FAOA-2015-CH09-CORR-024",
        473: "FAOA-2015-CH09-CORR-024",
        477: "FAOA-2015-CH09-CORR-010",
        489: "FAOA-2015-CH09-CORR-011",
        500: "FAOA-2015-CH09-CORR-025",
        501: "FAOA-2015-CH09-CORR-025",
        586: "FAOA-2015-CH09-CORR-015",
        592: "FAOA-2015-CH09-CORR-016",
        595: "FAOA-2015-CH09-CORR-026",
    }
    actual_chapter_nine_formula_corrections = {
        int(record["id"].rsplit("-", 1)[1]): record["correction_id"]
        for record in chapter_nine_formula
        if record.get("correction_id")
    }
    if actual_chapter_nine_formula_corrections != expected_chapter_nine_formula_corrections:
        raise ValueError("Chapter 9 formula-to-correction binding changed")
    if {
        int(record["id"].rsplit("-", 1)[1])
        for record in chapter_nine_formula
        if record["alignment"] == "reviewed_target_only_source_correction"
    } != {440, 500, 501}:
        raise ValueError("Chapter 9 target-only correction maps changed")
    if {
        int(record["id"].rsplit("-", 1)[1])
        for record in chapter_nine_formula
        if record["alignment"] == "preserved_math_key_after_localized_text_substitution"
    } != {201, 427, 583}:
        raise ValueError("Chapter 9 localized math-text maps changed")

    chapter_nine_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH09-")
    ]
    chapter_nine_relation_types: dict[str, int] = {}
    for record in chapter_nine_relations:
        relation_type = record["relation_type"]
        chapter_nine_relation_types[relation_type] = (
            chapter_nine_relation_types.get(relation_type, 0) + 1
        )
    if chapter_nine_relation_types != {
        "contains": 125,
        "translates": 137,
        "precedes": 136,
        "declares_label": 9,
        "xref": 7,
        "cites": 5,
        "hints": 5,
        "uses_term": 40,
        "licensed_under": 1,
        "has_artifact": 11,
        "terminology_evidence": 3,
        "has_qa_event": 8,
        "documents_correction": 26,
    }:
        raise ValueError("Chapter 9 relation-type inventory changed")
    chapter_nine_xrefs = [
        record for record in chapter_nine_relations if record["relation_type"] == "xref"
    ]
    if len(chapter_nine_xrefs) != 7 or any(
        record.get("resolution") != "local" for record in chapter_nine_xrefs
    ):
        raise ValueError("Chapter 9 reference closure changed")
    if len([
        record for record in chapter_nine_relations if record["relation_type"] == "hints"
    ]) != 5:
        raise ValueError("Chapter 9 hint topology changed")

    chapter_nine_artifacts = [
        record
        for record in artifact_records
        if record.get("unit_id") == "FAOA-2015-CH09"
    ]
    expected_chapter_nine_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH09-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH09-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH09-PDF",
        "ARTIFACT-FAOA-ID-CH09-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH09-TRANSLATION-REPORT",
        "ARTIFACT-FAOA-ID-CH09-CORRECTIONS-LEDGER",
        "ARTIFACT-FAOA-ID-CH09-PROSE-CORRECTIONS-LEDGER",
        "ARTIFACT-FAOA-ID-CH09-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH09-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH09-VISUAL-ACCESSIBILITY-AUDIT",
        "ARTIFACT-FAOA-ID-CH09-QA-RECEIPT",
    ]
    if [record["id"] for record in chapter_nine_artifacts] != expected_chapter_nine_artifact_ids:
        raise ValueError("Chapter 9 artifact inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH09-ADMISSION-20260822"
        or record.get("receipt_path") != "provenance/CH09_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256")
        != "08a103ce79f1f9406ddb877c01e8f921cde0f323fd6d1e731650eedbf1bd8794"
        for record in chapter_nine_artifacts
    ):
        raise ValueError("Chapter 9 artifacts are not receipt-bound")
    chapter_nine_artifact_identities = {
        record["id"]: (record["path"], record["bytes"], record["sha256"])
        for record in chapter_nine_artifacts
    }
    if chapter_nine_artifact_identities != {
        "ARTIFACT-FAOA-ID-CH09-TARGET-TEX": ("source/id-ID/topvecspaces-id.tex", 37705, "791868776a07f4c854f1c13d295da23a2559b88dcac48523fb0390e1e5330ee1"),
        "ARTIFACT-FAOA-ID-THROUGH-CH09-MASTER": ("source/id-ID/functional-analysis-id-through-ch09.tex", 9780, "acba53fd01601ecd49516c01fb00e38af7bfcafbbbff0358a87dea864c591e3f"),
        "ARTIFACT-FAOA-ID-THROUGH-CH09-PDF": ("output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf", 1686477, "99215ff5987f720600152da902cec8f521329692931a0dbf89e82ef2d4ff6076"),
        "ARTIFACT-FAOA-ID-CH09-STRUCTURAL-CHECKER": ("qa/check_ch09_translation.py", 35327, "de952960ea7e48d4085162a9f6f5239a29daf810cc22bf933df4031d13618425"),
        "ARTIFACT-FAOA-ID-CH09-TRANSLATION-REPORT": ("qa/ch09-translation-report.json", 7931, "0865aa5e64ea9ed5893925c3cf0986e1fc38c5f8d1b2f529ded71e06af5efd40"),
        "ARTIFACT-FAOA-ID-CH09-CORRECTIONS-LEDGER": ("provenance/SOURCE_CORRECTIONS_CH09.json", 14917, "861b96347a0ab045861042c782209d284f2811f0eaa21c85200745d11de882e9"),
        "ARTIFACT-FAOA-ID-CH09-PROSE-CORRECTIONS-LEDGER": ("provenance/SOURCE_CORRECTIONS.md", 29933, "8854271d5a35eaddc3fc1141f7a2fc1e100796652a30fb52b257fb5b34c9d514"),
        "ARTIFACT-FAOA-ID-CH09-RENDER-MANIFEST": ("provenance/CH09_RENDER_MANIFEST.csv", 27298, "add426dfd81f96fb8adc838d8173436d64ea3b2a165cdc1ff4a732c2a0f6fb2d"),
        "ARTIFACT-FAOA-ID-CH09-CONTACT-SHEET": ("provenance/CH09_CONTACT_SHEET.png", 4114399, "09b3bc4d70cc83d99cd376245c578e4c72fff6995e3392810e2d55e0302986dd"),
        "ARTIFACT-FAOA-ID-CH09-VISUAL-ACCESSIBILITY-AUDIT": ("qa/CH09_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md", 6825, "d5b3adc00a6aafd7da5ce1b76dc8e2d25fe877f1e46824596a947cd20e2f8287"),
        "ARTIFACT-FAOA-ID-CH09-QA-RECEIPT": ("provenance/CH09_BUILD_AND_QA_RECEIPT.md", 9128, "08a103ce79f1f9406ddb877c01e8f921cde0f323fd6d1e731650eedbf1bd8794"),
    }:
        raise ValueError("Chapter 9 public/local artifact identities changed")

    chapter_nine_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH09"
    ]
    if [record["id"] for record in chapter_nine_qa] != [
        "QA-CH09-STRUCTURAL-20260822",
        "QA-CH09-MATH-20260822",
        "QA-CH09-LANGUAGE-20260822",
        "QA-CH09-BUILD-20260822",
        "QA-CH09-VISUAL-20260822",
        "QA-CH09-ACCESSIBILITY-20260822",
        "QA-CH09-RIGHTS-20260822",
        "QA-CH09-ADMISSION-20260822",
    ] or any(
        record.get("result") != "pass"
        or record.get("qa_receipt_id") != "QA-CH09-ADMISSION-20260822"
        for record in chapter_nine_qa
    ):
        raise ValueError("Chapter 9 typed QA event closure changed")
    if chapter_nine_qa[-1].get("decision") != "admitted" or chapter_nine_qa[-1].get(
        "all_required_admission_gates"
    ) != "pass":
        raise ValueError("Chapter 9 admission event changed")

    chapter_nine_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH09"
    ]
    if [record["id"] for record in chapter_nine_corrections] != [
        f"FAOA-2015-CH09-CORR-{number:03d}" for number in range(1, 27)
    ]:
        raise ValueError("Chapter 9 correction stable-ID sequence changed")
    chapter_nine_correction_classes: dict[str, int] = {}
    for record in chapter_nine_corrections:
        correction_type = record["correction_type"]
        chapter_nine_correction_classes[correction_type] = (
            chapter_nine_correction_classes.get(correction_type, 0) + 1
        )
    if chapter_nine_correction_classes != {
        "mechanical_source_repair": 17,
        "mathematical_source_repair": 9,
    } or any(
        record.get("ledger_sha256")
        != "861b96347a0ab045861042c782209d284f2811f0eaa21c85200745d11de882e9"
        for record in chapter_nine_corrections
    ):
        raise ValueError("Chapter 9 correction provenance changed")

    chapter_nine_new_term_ids = [
        "TERM-BALANCED", "TERM-CIRCLED", "TERM-BALANCED-HULL", "TERM-ABSORBS",
        "TERM-ABSORBING", "TERM-RADIAL", "TERM-FILTER", "TERM-NEIGHBORHOOD-FILTER",
        "TERM-FILTERBASE", "TERM-FILTERBASE-FOR", "TERM-FILTER-GENERATED-BY",
        "TERM-GENERATED-BY", "TERM-BASED-ON", "TERM-COMPATIBLE",
        "TERM-TOPOLOGICAL-VECTOR-SPACE", "TERM-TRANSLATION", "TERM-LOCAL-BASE",
        "TERM-UNIFORM-CONVERGENCE-ON-COMPACT-SETS-TOPOLOGY", "TERM-REGULAR",
        "TERM-CAUCHY-FILTER", "TERM-COMPLETE", "TERM-QUOTIENT-TOPOLOGY",
        "TERM-LOCALLY-CONVEX", "TERM-LOCALLY-CONVEX-SPACE", "TERM-OPEN-SEMIBALL",
        "TERM-CLOSED-SEMIBALL", "TERM-MINKOWSKI-FUNCTIONAL", "TERM-SEPARATING",
        "TERM-METRIZABLE", "TERM-TRANSLATION-INVARIANT", "TERM-FRECHET-SPACE",
        "TERM-SMOOTH", "TERM-TEST-FUNCTIONS", "TERM-MULTI-INDEX", "TERM-ORDER",
        "TERM-SCHWARTZ-SPACE",
    ]
    chapter_nine_new_terms = [
        record
        for record in records_by_file["terminology.jsonl"]
        if record["id"] in chapter_nine_new_term_ids
    ]
    if [record["id"] for record in chapter_nine_new_terms] != chapter_nine_new_term_ids:
        raise ValueError("Chapter 9 bounded terminology inventory changed")
    chapter_nine_term_relations = [
        record
        for record in chapter_nine_relations
        if record["id"].startswith("FAOA-2015-CH09-REL-TERM-")
        and "EVIDENCE" not in record["id"]
    ]
    if len(chapter_nine_term_relations) != 40 or any(
        record["to_id"] not in ids for record in chapter_nine_term_relations
    ):
        raise ValueError("Chapter 9 defined-term closure changed")
    if [int(row["source_order"]) for row in chapter_nine_terms] != list(range(1, 92)):
        raise ValueError("Chapter 9 index occurrence order changed")

    chapter_ten_formula = [
        record
        for record in formula_records
        if record["id"].startswith("FAOA-2015-CH10-")
    ]
    chapter_ten_alignment_counts: dict[str, int] = {}
    for record in chapter_ten_formula:
        alignment = record["alignment"]
        chapter_ten_alignment_counts[alignment] = (
            chapter_ten_alignment_counts.get(alignment, 0) + 1
        )
    if chapter_ten_alignment_counts != {
        "preserved_exact_after_text_aware_whitespace_normalization": 623,
        "preserved_exact_after_text_aware_whitespace_normalization_reordered": 1,
        "preserved_math_key_after_localized_text_substitution": 1,
        "localized_math_text_reviewed": 8,
        "reviewed_source_correction_group_primary": 1,
        "reviewed_target_only_source_correction_group_member": 5,
        "reviewed_source_correction": 9,
    }:
        raise ValueError("Chapter 10 formula-alignment inventory changed")
    chapter_ten_source_formula_list = [
        formula_id
        for record in chapter_ten_formula
        for formula_id in record["source_formula_ids"]
    ]
    chapter_ten_target_formula_list = [
        formula_id
        for record in chapter_ten_formula
        for formula_id in record["target_formula_ids"]
    ]
    if len(chapter_ten_source_formula_list) != 651 or set(chapter_ten_source_formula_list) != {
        f"FAOA-2015-CH10-SRC-MATH-{number:04d}" for number in range(1, 652)
    } or chapter_ten_target_formula_list != [
        f"FAOA-2015-CH10-ID-MATH-{number:04d}" for number in range(1, 649)
    ]:
        raise ValueError("Chapter 10 stable formula-ID closure changed")
    expected_chapter_ten_formula_corrections = {
        42: "FAOA-2015-CH10-CORR-001",
        **{number: "FAOA-2015-CH10-CORR-003" for number in range(63, 69)},
        86: "FAOA-2015-CH10-CORR-005",
        88: "FAOA-2015-CH10-CORR-006",
        330: "FAOA-2015-CH10-CORR-010",
        404: "FAOA-2015-CH10-CORR-012",
        438: "FAOA-2015-CH10-CORR-013",
        443: "FAOA-2015-CH10-CORR-014",
        592: "FAOA-2015-CH10-CORR-015",
        602: "FAOA-2015-CH10-CORR-016",
        603: "FAOA-2015-CH10-CORR-016",
    }
    actual_chapter_ten_formula_corrections = {
        int(record["id"].rsplit("-", 1)[1]): record["correction_id"]
        for record in chapter_ten_formula
        if record.get("correction_id")
    }
    if actual_chapter_ten_formula_corrections != expected_chapter_ten_formula_corrections:
        raise ValueError("Chapter 10 formula-to-correction binding changed")
    direct_group = [
        record
        for record in chapter_ten_formula
        if record.get("replacement_group_id") == "FAOA-2015-CH10-CORR-003-MATH-GROUP"
    ]
    expected_group_source_ids = [
        f"FAOA-2015-CH10-SRC-MATH-{number:04d}" for number in range(63, 72)
    ]
    expected_group_target_ids = [
        f"FAOA-2015-CH10-ID-MATH-{number:04d}" for number in range(63, 69)
    ]
    if [record["id"] for record in direct_group] != [
        f"FAOA-2015-CH10-MATHMAP-{number:04d}" for number in range(63, 69)
    ] or direct_group[0].get("source_formula_ids") != expected_group_source_ids or any(
        record.get("source_formula_ids") for record in direct_group[1:]
    ) or any(
        record.get("replacement_group_source_formula_ids") != expected_group_source_ids
        or record.get("replacement_group_target_formula_ids") != expected_group_target_ids
        for record in direct_group
    ):
        raise ValueError("Chapter 10 direct-limit formula replacement group changed")
    if {
        int(record["id"].rsplit("-", 1)[1])
        for record in chapter_ten_formula
        if record["alignment"] == "localized_math_text_reviewed"
    } != {251, 252, 259, 260, 261, 265, 266, 267} or {
        int(record["id"].rsplit("-", 1)[1])
        for record in chapter_ten_formula
        if record["alignment"] == "preserved_math_key_after_localized_text_substitution"
    } != {186}:
        raise ValueError("Chapter 10 localized math-text maps changed")
    moved_formula = chapter_ten_formula[85]
    if moved_formula["id"] != "FAOA-2015-CH10-MATHMAP-0086" or moved_formula.get(
        "source_formula_ids"
    ) != ["FAOA-2015-CH10-SRC-MATH-0090"] or moved_formula.get(
        "sequence_opcode"
    ) != "move":
        raise ValueError("Chapter 10 reordered topology formula changed")

    chapter_ten_relations = [
        record
        for record in records_by_file["relations.jsonl"]
        if record["id"].startswith("FAOA-2015-CH10-")
    ]
    chapter_ten_relation_types: dict[str, int] = {}
    for record in chapter_ten_relations:
        relation_type = record["relation_type"]
        chapter_ten_relation_types[relation_type] = (
            chapter_ten_relation_types.get(relation_type, 0) + 1
        )
    if chapter_ten_relation_types != {
        "contains": 116,
        "translates": 132,
        "precedes": 131,
        "declares_label": 18,
        "xref": 20,
        "cites": 29,
        "hints": 3,
        "uses_term": 35,
        "licensed_under": 1,
        "has_artifact": 11,
        "terminology_evidence": 3,
        "has_qa_event": 8,
        "documents_correction": 16,
    }:
        raise ValueError("Chapter 10 relation-type inventory changed")
    chapter_ten_xrefs = [
        record for record in chapter_ten_relations if record["relation_type"] == "xref"
    ]
    chapter_ten_xref_resolutions: dict[str, int] = {}
    chapter_ten_xref_surfaces: dict[str, int] = {}
    for record in chapter_ten_xrefs:
        resolution = record["resolution"]
        surface = record["target_surface"]
        chapter_ten_xref_resolutions[resolution] = chapter_ten_xref_resolutions.get(resolution, 0) + 1
        chapter_ten_xref_surfaces[surface] = chapter_ten_xref_surfaces.get(surface, 0) + 1
    if chapter_ten_xref_resolutions != {"local": 15, "admitted_prior_unit": 5} or chapter_ten_xref_surfaces != {"ref": 13, "eqref": 7}:
        raise ValueError("Chapter 10 reference closure changed")
    chapter_ten_hints = [
        (record["from_id"], record["to_id"])
        for record in chapter_ten_relations
        if record["relation_type"] == "hints"
    ]
    if chapter_ten_hints != [
        ("FAOA-2015-CH10-NODE-0006", "FAOA-2015-CH10-NODE-0005"),
        ("FAOA-2015-CH10-NODE-0031", "FAOA-2015-CH10-NODE-0030"),
        ("FAOA-2015-CH10-NODE-0095", "FAOA-2015-CH10-NODE-0094"),
    ]:
        raise ValueError("Chapter 10 proof-hint topology changed")

    chapter_ten_artifacts = [
        record
        for record in artifact_records
        if record.get("unit_id") == "FAOA-2015-CH10"
    ]
    expected_chapter_ten_artifact_ids = [
        "ARTIFACT-FAOA-ID-CH10-TARGET-TEX",
        "ARTIFACT-FAOA-ID-THROUGH-CH10-MASTER",
        "ARTIFACT-FAOA-ID-THROUGH-CH10-PDF",
        "ARTIFACT-FAOA-ID-CH10-STRUCTURAL-CHECKER",
        "ARTIFACT-FAOA-ID-CH10-TRANSLATION-REPORT",
        "ARTIFACT-FAOA-ID-CH10-CORRECTIONS-LEDGER",
        "ARTIFACT-FAOA-ID-CH10-PROSE-CORRECTIONS-LEDGER",
        "ARTIFACT-FAOA-ID-CH10-RENDER-MANIFEST",
        "ARTIFACT-FAOA-ID-CH10-CONTACT-SHEET",
        "ARTIFACT-FAOA-ID-CH10-VISUAL-ACCESSIBILITY-AUDIT",
        "ARTIFACT-FAOA-ID-CH10-QA-RECEIPT",
    ]
    if [record["id"] for record in chapter_ten_artifacts] != expected_chapter_ten_artifact_ids:
        raise ValueError("Chapter 10 artifact inventory changed")
    if any(
        record.get("qa_receipt_id") != "QA-CH10-ADMISSION-20260822"
        or record.get("receipt_path") != "provenance/CH10_BUILD_AND_QA_RECEIPT.md"
        or record.get("receipt_sha256") != "2a4d7a6379b1cc4f634fd45d75413133670c134d9b3ba55c363ff273645b9c1f"
        for record in chapter_ten_artifacts
    ):
        raise ValueError("Chapter 10 artifacts are not receipt-bound")
    chapter_ten_artifact_identities = {
        record["id"]: (record["path"], record["bytes"], record["sha256"])
        for record in chapter_ten_artifacts
    }
    if chapter_ten_artifact_identities != {
        "ARTIFACT-FAOA-ID-CH10-TARGET-TEX": ("source/id-ID/distributions-id.tex", 42627, "6456f9def822da572e117f3ec368931f0bfb441840aa0785be1df6080bbb6840"),
        "ARTIFACT-FAOA-ID-THROUGH-CH10-MASTER": ("source/id-ID/functional-analysis-id-through-ch10.tex", 9866, "5de05f7a154bea99d11924fc21dbbf7495c8642d5a3c58e48e0fdd053dd400b4"),
        "ARTIFACT-FAOA-ID-THROUGH-CH10-PDF": ("output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf", 1796056, "1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc"),
        "ARTIFACT-FAOA-ID-CH10-STRUCTURAL-CHECKER": ("qa/check_ch10_translation.py", 16387, "fa247c00608997da81d65bdcadc0bfa916060a0bb8858c24e5f0a54ac5aa75db"),
        "ARTIFACT-FAOA-ID-CH10-TRANSLATION-REPORT": ("qa/ch10-translation-report.json", 1089, "8b472e7b803cfb566e08c4ff3f1e464f7564520faf2f9115f3b57e7042c1218d"),
        "ARTIFACT-FAOA-ID-CH10-CORRECTIONS-LEDGER": ("provenance/SOURCE_CORRECTIONS_CH10.json", 11858, "c5010ce91ae98d3c9b3637fe6a553f4df7d1ba524faa75b1f4fb42b0b036c948"),
        "ARTIFACT-FAOA-ID-CH10-PROSE-CORRECTIONS-LEDGER": ("provenance/SOURCE_CORRECTIONS.md", 32495, "8bd1be45b70a5e2395e67c20f192f89fc658f3d158d8ff7bb9b1e9cef77b947b"),
        "ARTIFACT-FAOA-ID-CH10-RENDER-MANIFEST": ("provenance/CH10_RENDER_MANIFEST.csv", 29798, "b1dd863b6b2441e0a49bf9fe3248b759c9889f0a74654fbe060d868f60cfb7ca"),
        "ARTIFACT-FAOA-ID-CH10-CONTACT-SHEET": ("provenance/CH10_CONTACT_SHEET.png", 4463573, "e5b14686ad4ce088d02ba819e3df14621936dd888b429b92a9506e53ce9d34f6"),
        "ARTIFACT-FAOA-ID-CH10-VISUAL-ACCESSIBILITY-AUDIT": ("qa/CH10_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md", 7203, "5d5ff18e230a8fc1d2aace1b801b53487ebb409c5bdb3bc6e600056b73a75bea"),
        "ARTIFACT-FAOA-ID-CH10-QA-RECEIPT": ("provenance/CH10_BUILD_AND_QA_RECEIPT.md", 10338, "2a4d7a6379b1cc4f634fd45d75413133670c134d9b3ba55c363ff273645b9c1f"),
    }:
        raise ValueError("Chapter 10 public/local artifact identities changed")

    chapter_ten_qa = [
        record
        for record in records_by_file["qa_events.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH10"
    ]
    if [record["id"] for record in chapter_ten_qa] != [
        "QA-CH10-STRUCTURAL-20260822",
        "QA-CH10-MATH-20260822",
        "QA-CH10-LANGUAGE-20260822",
        "QA-CH10-BUILD-20260822",
        "QA-CH10-VISUAL-20260822",
        "QA-CH10-ACCESSIBILITY-20260822",
        "QA-CH10-RIGHTS-20260822",
        "QA-CH10-ADMISSION-20260822",
    ] or any(
        record.get("result") != "pass"
        or record.get("qa_receipt_id") != "QA-CH10-ADMISSION-20260822"
        or record.get("model_id") != "OpenAI Codex gpt-5.6-sol, Ultra"
        for record in chapter_ten_qa
    ):
        raise ValueError("Chapter 10 typed QA event closure changed")
    if chapter_ten_qa[-1].get("decision") != "admitted" or chapter_ten_qa[-1].get(
        "all_required_admission_gates"
    ) != "pass":
        raise ValueError("Chapter 10 admission event changed")

    chapter_ten_corrections = [
        record
        for record in records_by_file["corrections.jsonl"]
        if record.get("unit_id") == "FAOA-2015-CH10"
    ]
    if [record["id"] for record in chapter_ten_corrections] != [
        f"FAOA-2015-CH10-CORR-{number:03d}" for number in range(1, 17)
    ]:
        raise ValueError("Chapter 10 correction stable-ID sequence changed")
    chapter_ten_correction_classes: dict[str, int] = {}
    for record in chapter_ten_corrections:
        correction_type = record["correction_type"]
        chapter_ten_correction_classes[correction_type] = (
            chapter_ten_correction_classes.get(correction_type, 0) + 1
        )
    if chapter_ten_correction_classes != {
        "mathematical_source_repair": 9,
        "mechanical_source_repair": 5,
        "semantic_tex_source_repair": 1,
        "semantic_source_repair": 1,
    } or any(
        record.get("ledger_sha256") != "c5010ce91ae98d3c9b3637fe6a553f4df7d1ba524faa75b1f4fb42b0b036c948"
        for record in chapter_ten_corrections
    ):
        raise ValueError("Chapter 10 correction provenance changed")

    chapter_ten_new_term_ids = [
        "TERM-DIRECTED-SYSTEM", "TERM-INDUCTIVE-LIMIT", "TERM-DIRECT-LIMIT",
        "TERM-STRONG-TOPOLOGY", "TERM-STRICT-INDUCTIVE-SEQUENCE",
        "TERM-STRICT-INDUCTIVE-LIMIT", "TERM-INDUCTIVE-LIMIT-TOPOLOGY",
        "TERM-LF-SPACE", "TERM-LOCALLY-INTEGRABLE", "TERM-DISTRIBUTION",
        "TERM-SINGULAR", "TERM-DIRAC-MEASURE", "TERM-DIRAC-DELTA-DISTRIBUTION-AT-A",
        "TERM-HEAVISIDE-FUNCTION", "TERM-HEAVISIDE-DISTRIBUTION", "TERM-DERIVATIVE",
        "TERM-DIFFERENTIAL-OPERATOR", "TERM-DIPOLE", "TERM-NORMALIZED-LEBESGUE-MEASURE",
        "TERM-CONVOLUTION", "TERM-FOURIER-TRANSFORM", "TERM-FORMAL-ADJOINT",
        "TERM-CLASSICAL", "TERM-WEAK", "TERM-DISTRIBUTIONAL", "TERM-GENERALIZED",
        "TERM-TEMPERED-DISTRIBUTIONS", "TERM-TEMPERATE-DISTRIBUTIONS",
    ]
    chapter_ten_new_terms = [
        record
        for record in records_by_file["terminology.jsonl"]
        if record["id"] in chapter_ten_new_term_ids
    ]
    if [record["id"] for record in chapter_ten_new_terms] != chapter_ten_new_term_ids:
        raise ValueError("Chapter 10 bounded terminology inventory changed")
    terms_by_id_ch10 = {record["id"]: record for record in chapter_ten_new_terms}
    if terms_by_id_ch10["TERM-TEMPERED-DISTRIBUTIONS"].get("preferred") != "distribusi tempered" or terms_by_id_ch10["TERM-TEMPERATE-DISTRIBUTIONS"].get("preferred") != "distribusi temperate" or terms_by_id_ch10["TERM-TEMPERATE-DISTRIBUTIONS"].get("canonical_term_id") != "TERM-TEMPERED-DISTRIBUTIONS" or any(
        record.get("terminology_decision_sha256") != "03005aa60200768a05c700e7d9d8cfa969034204e37ecffbd8b67126c5c66329"
        for record in (
            terms_by_id_ch10["TERM-TEMPERED-DISTRIBUTIONS"],
            terms_by_id_ch10["TERM-TEMPERATE-DISTRIBUTIONS"],
        )
    ):
        raise ValueError("Chapter 10 tempered-distribution terminology binding changed")
    chapter_ten_term_relations = [
        record
        for record in chapter_ten_relations
        if record["id"].startswith("FAOA-2015-CH10-REL-TERM-")
        and "EVIDENCE" not in record["id"]
    ]
    if len(chapter_ten_term_relations) != 35 or any(
        record["to_id"] not in ids for record in chapter_ten_term_relations
    ):
        raise ValueError("Chapter 10 defined-term closure changed")
    if [int(row["source_order"]) for row in chapter_ten_terms] != list(range(1, 102)):
        raise ValueError("Chapter 10 index occurrence order changed")

    chapter_ten_exercises = [
        record
        for record in records_by_file["exercise_support.jsonl"]
        if record["id"].startswith("FAOA-2015-CH10-")
    ]
    expected_inline_hint_lines = [None, None, None, None, None, [383], [425], [432], [441], [670], None]
    if [record["id"] for record in chapter_ten_exercises] != [
        f"FAOA-2015-CH10-EXERCISE-SUPPORT-{number:03d}" for number in range(1, 12)
    ] or [record.get("upstream_inline_hint_source_lines") for record in chapter_ten_exercises] != expected_inline_hint_lines or any(
        record.get("upstream_hint_ids")
        or record.get("upstream_answer_state") != "absent"
        or record.get("upstream_solution_state") != "absent"
        or record.get("provenance") != "separately_authored_not_Erdman"
        for record in chapter_ten_exercises
    ):
        raise ValueError("Chapter 10 exercise-support semantics changed")

    terminology_qa = records_by_file["terminology_qa.jsonl"]
    expected_terminology_qa_ids = [
        "TERM-QA-O008-ID-20260822",
        *[f"TERM-QA-O008-ID-VARIANT-{number:03d}" for number in range(1, 6)],
        "TERM-QA-O008-ID-FUTURE-DOMAIN-001",
    ]
    if [record["id"] for record in terminology_qa] != expected_terminology_qa_ids:
        raise ValueError("terminology-QA stable-ID sequence changed")

    terminology_qa_provenance = terminology_qa[0]
    if (
        terminology_qa_provenance.get("record_type") != "terminology_qa_provenance"
        or terminology_qa_provenance.get("edition_id") != "ERDMAN-FAOA-2015-ID"
        or terminology_qa_provenance.get("locale") != "id-ID"
        or terminology_qa_provenance.get("qa_date") != "2026-08-22"
        or terminology_qa_provenance.get("model")
        != "OpenAI Codex gpt-5.6-sol, Ultra"
        or terminology_qa_provenance.get("decision") != "no_prose_change"
        or terminology_qa_provenance.get("preferred_terms_preserved") is not True
        or terminology_qa_provenance.get("current_variant_groups") != 5
        or terminology_qa_provenance.get("current_variant_spellings") != 6
        or terminology_qa_provenance.get("future_domain_candidate_groups") != 1
    ):
        raise ValueError("terminology-QA provenance boundary changed")
    arxiv_search = terminology_qa_provenance.get("arxiv_search", {})
    if (
        arxiv_search.get("state")
        != "bounded_no_suitable_indonesian_tex_source_found"
        or arxiv_search.get("claim_scope")
        != "bounded search result, not a universal nonexistence claim"
        or arxiv_search.get("exact_queries")
        != [
            "analisis fungsional",
            "ruang Banach",
            "ruang vektor topologis",
            "operator kompak",
        ]
    ):
        raise ValueError("terminology-QA bounded arXiv-search semantics changed")
    fallback_source = terminology_qa_provenance.get("fallback_source", {})
    if (
        fallback_source.get("source_id") != "UNDIP-JFMA-2020-3-1-7874"
        or fallback_source.get("doi") != "10.14710/jfma.v3i1.7874"
        or fallback_source.get("publisher")
        != "Department of Mathematics, Universitas Diponegoro"
        or fallback_source.get("license") != "CC BY 4.0"
        or fallback_source.get("pdf_pages") != 9
        or fallback_source.get("pdf_bytes") != 1_007_587
        or fallback_source.get("pdf_sha256")
        != "6bc61be69f974e1598ec168504aa7b1925cf55a75dfc15100139bfcd586b0ff8"
    ):
        raise ValueError("terminology-QA fallback-source identity changed")
    supplemental_sources = terminology_qa_provenance.get("supplemental_sources", [])
    if [source.get("source_id") for source in supplemental_sources] != [
        "UGM-ETD-89480",
        "ITB-MA6131-2024",
        "ITB-MA5022-2024",
        "UGM-ETD-36096",
    ]:
        raise ValueError("terminology-QA supplemental source sequence changed")
    if (
        supplemental_sources[2].get("terminology_evidence")
        != "Operator Normal dan Adjoin dengan Diri Sendiri"
        or supplemental_sources[2].get("bytes") != 7_943
        or supplemental_sources[2].get("sha256")
        != "cce7931eba1388395a504d83275f2846b7c3ac9031066bc27258c7abbc62724e"
        or supplemental_sources[3].get("terminology_evidence")
        != "operator pendamping"
        or supplemental_sources[3].get("bytes") != 22_532
        or supplemental_sources[3].get("sha256")
        != "677165f202f8d7f32eb13f3ebe5b18052a20765ae32354209034d1ed8c3cf3f4"
    ):
        raise ValueError("adjoin/pendamping supplemental evidence changed")
    if terminology_qa_provenance.get("qa_report") != {
        "path": (
            "qa/terminology_evidence/undip-jfma-2020-dunford/"
            "TERMINOLOGY_QA_REPORT.md"
        ),
        "bytes": 9_317,
        "sha256": "c7618249a3d9f273044a408e44438e2db710d5b5f46856ea5280bf247583858d",
    }:
        raise ValueError("terminology-QA report identity changed")

    terminology_qa_evidence = (
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/"
            "TERMINOLOGY_QA_REPORT.md",
            9_317,
            "c7618249a3d9f273044a408e44438e2db710d5b5f46856ea5280bf247583858d",
        ),
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/jfma-v3n1-7874.pdf",
            1_007_587,
            "6bc61be69f974e1598ec168504aa7b1925cf55a75dfc15100139bfcd586b0ff8",
        ),
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/jfma-v3n1-7874.txt",
            24_923,
            "2a74c776f17891e80d2b5da88e2d00233a8990c969bac0e36451a703dd9f8c91",
        ),
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/"
            "jfma-v3n1-7874-contact-sheet.png",
            2_622_328,
            "94545c3ad7770d39b69132c4c0fae37a6487e4aa0b1c77ef58073fe061ed20a9",
        ),
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/"
            "undip-jfma-7874-article.html",
            49_084,
            "bb8bfeb1e799b479288c1857406d480ecb00b82118a74728985a0d7a9aaf78b9",
        ),
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/"
            "ugm-etd-89480-metadata.html",
            35_075,
            "3499fe641f9127357395c1d1bcd8467f848804208803db31ec0eb9f720c0c9e2",
        ),
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/"
            "itb-ma6131-2024.html",
            6_739,
            "5f9de3cc9dbcf3429ce45464aa08831d958466f5b5db6249fa3fe0f3eda94fb3",
        ),
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/"
            "itb-ma5022-2024-adjoin.html",
            7_943,
            "cce7931eba1388395a504d83275f2846b7c3ac9031066bc27258c7abbc62724e",
        ),
        (
            "qa/terminology_evidence/undip-jfma-2020-dunford/"
            "ugm-etd-36096-operator-pendamping.html",
            22_532,
            "677165f202f8d7f32eb13f3ebe5b18052a20765ae32354209034d1ed8c3cf3f4",
        ),
    )
    for relative_path, expected_bytes, expected_sha256 in terminology_qa_evidence:
        evidence_path = ROOT / relative_path
        if (
            not evidence_path.is_file()
            or evidence_path.stat().st_size != expected_bytes
            or sha(evidence_path) != expected_sha256
        ):
            raise ValueError(f"terminology-QA evidence mismatch: {relative_path}")

    ch10_source_path = ROOT / "source/upstream/distributions.tex"
    ch10_source_data = ch10_source_path.read_bytes()
    ch10_source_text = ch10_source_data.decode("ascii")
    if (
        len(ch10_source_data) != 42_703
        or len(ch10_source_data.splitlines()) != 894
        or sha_bytes(ch10_source_data)
        != "31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8"
        or len(
            re.findall(
                r"weakly[ -]measurable", ch10_source_text, flags=re.IGNORECASE
            )
        )
        != 0
        or len(re.findall(r"measur", ch10_source_text, flags=re.IGNORECASE)) != 14
    ):
        raise ValueError("frozen Chapter 10 weakly-measurable absence check changed")

    expected_variant_groups = [
        (
            "TERM-NORMED-LINEAR-SPACE",
            "normed linear space",
            "ruang linear bernorma",
            ["ruang bernorma"],
        ),
        (
            "TERM-BOUNDED-LINEAR-MAP",
            "bounded linear map",
            "pemetaan linear terbatas",
            ["operator linear terbatas"],
        ),
        ("TERM-ADJOINT", "adjoint", "adjoin", ["adjoint", "operator pendamping"]),
        (
            "TERM-WEAKLY-COMPACT",
            "weakly compact",
            "kompak secara lemah",
            ["kompak lemah"],
        ),
        (
            "TERM-CONVERGE-WEAKLY",
            "converge weakly",
            "konvergen secara lemah",
            ["konvergen lemah"],
        ),
    ]
    terms_by_id = {record["id"]: record for record in records_by_file["terminology.jsonl"]}
    for record, (term_id, source_term, preferred, variants) in zip(
        terminology_qa[1:6], expected_variant_groups, strict=True
    ):
        if (
            record.get("record_type") != "term_variant_evidence"
            or record.get("qa_provenance_id") != "TERM-QA-O008-ID-20260822"
            or record.get("term_id") != term_id
            or record.get("source_term") != source_term
            or record.get("preferred") != preferred
            or record.get("variants") != variants
            or record.get("variant_state") != "accepted_recognition_variant"
            or record.get("instantiation_state") != "backend_evidence_only"
            or record.get("preferred_changed") is not False
            or record.get("prose_change") != "none"
        ):
            raise ValueError(f"terminology-QA variant record changed: {record['id']}")
        term = terms_by_id.get(term_id, {})
        if (
            term.get("source_term") != source_term
            or term.get("preferred") != preferred
            or term.get("variants") != []
        ):
            raise ValueError(f"frozen preferred terminology changed: {term_id}")

    future_domain_term = terminology_qa[6]
    if (
        future_domain_term.get("record_type") != "future_domain_term_variant"
        or future_domain_term.get("qa_provenance_id")
        != "TERM-QA-O008-ID-20260822"
        or future_domain_term.get("candidate_term_id") != "TERM-WEAKLY-MEASURABLE"
        or future_domain_term.get("source_term") != "weakly measurable"
        or future_domain_term.get("preferred") != "terukur secara lemah"
        or future_domain_term.get("variants") != ["terukur lemah"]
        or future_domain_term.get("variant_state")
        != "non_instantiated_future_domain_recognition_candidate"
        or future_domain_term.get("instantiation_state")
        != "not_present_in_frozen_ch10_source"
        or future_domain_term.get("source_presence") is not False
        or future_domain_term.get("source_presence_check")
        != {
            "path": "source/upstream/distributions.tex",
            "bytes": 42_703,
            "lines": 894,
            "sha256": "31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8",
            "query": "weakly[ -]measurable",
            "occurrences": 0,
        }
        or future_domain_term.get("instantiation_condition")
        != "only_if_later_or_original_source_introduces_weakly_measurable"
        or future_domain_term.get("prose_change")
        != "not_applicable_no_existing_occurrence"
        or "TERM-WEAKLY-MEASURABLE" in terms_by_id
    ):
        raise ValueError("future/domain terminology-QA boundary changed")

    chapter_nine_exercises = [
        record
        for record in records_by_file["exercise_support.jsonl"]
        if record["id"].startswith("FAOA-2015-CH09-")
    ]
    if len(chapter_nine_exercises) != 1 or any(
        record.get("upstream_hint_ids")
        or record.get("upstream_inline_hint_state") != "absent"
        or record.get("upstream_answer_state") != "absent"
        or record.get("upstream_solution_state") != "absent"
        or record.get("provenance") != "separately_authored_not_Erdman"
        for record in chapter_nine_exercises
    ):
        raise ValueError("Chapter 9 exercise-support semantics changed")

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
    # Historical chapter validators above remain as frozen evidence. The
    # current whole-backend entrypoint validates the complete source-text byte
    # prefix plus the additive semantic-HTML surface and auxiliary route map.
    from validate_html_backend import main as validate_latest_backend

    validate_latest_backend()
