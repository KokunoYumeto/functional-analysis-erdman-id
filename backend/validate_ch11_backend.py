#!/usr/bin/env python3
"""Independently validate the admitted FAOA-2015-CH11 backend append.

The validator is read-only.  It does not invoke a generator and it refuses a
pre-admission/partial backend.  Its authority boundary is the frozen Chapter
1--10 byte prefix plus the live Chapter 11 source, target, build, admission
receipt, and machine-readable correction evidence.
"""

from __future__ import annotations

import collections
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
sys.path.insert(0, str(BACKEND))
import ch03_math  # noqa: E402


SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
CHAPTER_ID = "FAOA-2015-CH11"
RIGHTS_ID = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
RECEIPT_ID = "QA-CH11-ADMISSION-20260823"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_REL = "source/upstream/Gelfand_Naimark.tex"
TARGET_REL = "source/id-ID/Gelfand_Naimark-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-through-ch11.tex"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-11.pdf"
RECEIPT_REL = "provenance/CH11_BUILD_AND_QA_RECEIPT.md"
CORRECTIONS_REL = "provenance/SOURCE_CORRECTIONS_CH11.json"

SOURCE_IDENTITY = (
    32_235,
    788,
    "018f15db7ee5a4392f624af050507a90339e1469e30f97c6017e003c7ff33b26",
)

# Exact checked-in Chapter 1--10 files before the Chapter 11 append.  The
# no-exercise Chapter 11 projection leaves exercise_support.jsonl byte-exact.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (983_525, "c96bfdcfb7f25bc33c26409d086867f139ec9774feebac3e1692a280c937a422"),
    "segments.jsonl": (1_102_619, "16ef4a0583eb26be360f2f864cfba2f9467cdd9d77bbe9b190bcc8841e532526"),
    "relations.jsonl": (1_369_232, "7fbaec2551e907e542bd593e1c04b77ddc793642e1d3d285ba6b530152214283"),
    "formula_map.jsonl": (4_553_396, "7dbdbb75506e3b984b7176d89b63da5125a71e5438e75a973e060a0b288d24ba"),
    "exercise_support.jsonl": (25_503, "45b128f45d61057837c2eddcf1e45024e62b231e7d4b46e2b2dfb7c849a44925"),
    "index_terms.csv": (390_698, "e0562824ac00c58c41992d8acc524044068f59a39292ee55f38026185fde6d9a"),
    "artifacts.jsonl": (53_535, "66856b2fffeed45222665a7b7b70a1764462674ed9f1c0745419dee307c5ad28"),
    "qa_events.jsonl": (72_362, "97dff9cfd92b2fcd68c0d7dcb82e98e4f55a4969a38ef72f702e9a1574b9b086"),
    "corrections.jsonl": (144_791, "f851880584dcc9c35b4ffad0c8def523f15a187fbabd412b6c7a0f54c26a3130"),
    "terminology.jsonl": (110_425, "b30317f156870940af4f9bebf1e7172a321f3d22ecd3ab99cc2187d7ec77f661"),
}
UNITS_PREFIX = (13_488, "c57f1a39de3d271ca0762acedf5b973bd3977e12b1acd5f8c1a77578d0fb1707")
UNITS_SUFFIX = (3_268, "1bb7b738f1c8feca0013e47da09114a11975ea45d1e5b2c86fbad7dd220614a7")

AGGREGATE_COUNTS = {
    "units.jsonl": 18,
    "semantic_units.jsonl": 1_280,
    "segments.jsonl": 1_515,
    "relations.jsonl": 5_668,
    "formula_map.jsonl": 8_142,
    "exercise_support.jsonl": 48,
    "artifacts.jsonl": 100,
    "qa_events.jsonl": 85,
    "corrections.jsonl": 178,
    "terminology.jsonl": 300,
    "terminology_qa.jsonl": 7,
}

CH11_COUNTS = {
    "semantic_units.jsonl": 101,
    "segments.jsonl": 118,
    "relations.jsonl": 453,
    "formula_map.jsonl": 625,
    "exercise_support.jsonl": 0,
    "artifacts.jsonl": 12,
    "qa_events.jsonl": 9,
    "corrections.jsonl": 6,
    "terminology.jsonl": 17,
    "index_terms.csv": 65,
}

RELATION_TYPE_COUNTS = {
    "contains": 101,
    "translates": 118,
    "precedes": 117,
    "declares_label": 38,
    "xref": 15,
    "cites": 5,
    "hints": 9,
    "uses_term": 21,
    "licensed_under": 1,
    "uses_asset": 1,
    "has_artifact": 12,
    "has_qa_event": 9,
    "documents_correction": 6,
}

NEW_TERMS = {
    "TERM-CHARACTER": ("character", "karakter"),
    "TERM-MULTIPLICATIVE-LINEAR-FUNCTIONAL": ("nonzero multiplicative linear functional", "fungsional linear multiplikatif tak nol"),
    "TERM-NILPOTENT": ("nilpotent", "nilpoten"),
    "TERM-EVALUATION-FUNCTIONAL": ("evaluation functional at $x$", "fungsional evaluasi di $x$"),
    "TERM-GELFAND-TOPOLOGY": ("Gelfand topology", "topologi Gelfand"),
    "TERM-CHARACTER-SPACE": ("character space", "ruang karakter"),
    "TERM-MAXIMAL-IDEAL-SPACE": ("maximal ideal space", "ruang ideal maksimal"),
    "TERM-EVALUATION-MAP": ("evaluation map", "pemetaan evaluasi"),
    "TERM-GELFAND-TRANSFORM": ("Gelfand transform on~$A$", "transformasi Gelfand pada~$A$"),
    "TERM-SEPARATES-POINTS": ("separates points", "memisahkan titik-titik"),
    "TERM-SEPARATING-FAMILY": ("separating family", "keluarga fungsi pemisah"),
    "TERM-QUASINILPOTENT": ("quasinilpotent", "kuasinilpoten"),
    "TERM-SEMISIMPLE": ("semisimple", "semisederhana"),
    "TERM-FOURIER-SERIES": ("Fourier series", "deret Fourier"),
    "TERM-FOURIER-COEFFICIENT": ("Fourier coefficient", "koefisien Fourier"),
    "TERM-ABSOLUTELY-CONVERGENT-FOURIER-SERIES": ("absolutely convergent Fourier series", "deret Fourier yang konvergen mutlak"),
    "TERM-CSTAR-GENERATED-SUBALGEBRA": ("$C^*$-subalgebra generated by~$S$", "subaljabar-$C^*$ yang dibangkitkan oleh~$S$"),
}

ARTIFACT_SPECS = {
    "ARTIFACT-FAOA-ID-CH11-TARGET-TEX": ("admitted_translation_source", TARGET_REL),
    "ARTIFACT-FAOA-ID-THROUGH-CH11-MASTER": ("cumulative_TeX_master", MASTER_REL),
    "ARTIFACT-FAOA-ID-THROUGH-CH11-PDF": ("canonical_cumulative_reader_pdf", PDF_REL),
    "ARTIFACT-FAOA-ID-CH11-CENSUS": ("source_census", "qa/CH11_CENSUS.json"),
    "ARTIFACT-FAOA-ID-CH11-SOURCE-INVENTORY": ("source_inventory", "qa/CH11_SOURCE_INVENTORY.md"),
    "ARTIFACT-FAOA-ID-CH11-TERM-QA": ("external_terminology_QA", "qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md"),
    "ARTIFACT-FAOA-ID-CH11-RENDER-MANIFEST": ("visual_QA_render_manifest", "provenance/CH11_RENDER_MANIFEST.csv"),
    "ARTIFACT-FAOA-ID-CH11-CONTACT-SHEET": ("visual_QA_contact_sheet", "provenance/CH11_CONTACT_SHEET.png"),
    "ARTIFACT-FAOA-ID-CH11-VISUAL-ACCESSIBILITY-AUDIT": ("visual_accessibility_audit", "qa/CH11_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"),
    "ARTIFACT-FAOA-ID-CH11-CORRECTIONS-LEDGER": ("chapter_source_corrections_ledger", CORRECTIONS_REL),
    "ARTIFACT-FAOA-ID-CH11-TERMINOLOGY-DECISIONS": ("terminology_decisions", "provenance/CH11_TERMINOLOGY_DECISIONS.md"),
    "ARTIFACT-FAOA-ID-CH11-QA-RECEIPT": ("admission_receipt", RECEIPT_REL),
}

QA_SPECS = {
    "QA-CH11-STRUCTURAL-20260823": "unit_structural",
    "QA-CH11-MATH-20260823": "unit_mathematical",
    "QA-CH11-LANGUAGE-20260823": "unit_language_terminology",
    "QA-CH11-BUILD-20260823": "cumulative_build",
    "QA-CH11-VISUAL-20260823": "cumulative_visual",
    "QA-CH11-ACCESSIBILITY-20260823": "cumulative_accessibility",
    "QA-CH11-RIGHTS-20260823": "unit_rights_privacy",
    "QA-CH11-DIAGRAM-ACCESSIBILITY-20260823": "diagram_accessibility",
    RECEIPT_ID: "unit_admission",
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path) -> tuple[int, int, str]:
    data = path.read_bytes()
    return len(data), len(data.splitlines()), sha_bytes(data)


def active_same_length(text: str) -> str:
    chars = list(text)
    escaped = False
    comment = False
    for index, char in enumerate(chars):
        if char in "\r\n":
            comment = False
            escaped = False
        elif comment:
            chars[index] = " "
        elif char == "%" and not escaped:
            chars[index] = " "
            comment = True
        elif char == "\\":
            escaped = not escaped
        else:
            escaped = False
    return "".join(chars)


def balanced_end(text: str, brace: int) -> int:
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError(f"unclosed brace at offset {brace}")


def macros(text: str, name: str) -> list[dict]:
    active = active_same_length(text)
    pattern = re.compile(r"\\" + re.escape(name) + r"(?![A-Za-z@])\s*\{")
    out = []
    for match in pattern.finditer(active):
        brace = active.find("{", match.start())
        end = balanced_end(active, brace)
        out.append({
            "start": match.start(),
            "argument": text[brace + 1:end - 1],
            "line": text.count("\n", 0, match.start()) + 1,
        })
    return out


def load_jsonl(path: Path) -> list[dict]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError(f"{path.name} lacks final LF")
    text = data.decode("utf-8")
    records = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise ValueError(f"{path.name}:{line_number} is blank")
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"{path.name}:{line_number} is not an object")
        if record.get("schema") != SCHEMA or record.get("schema_version") != VERSION:
            raise ValueError(f"{path.name}:{line_number} schema mismatch")
        records.append(record)
    return records


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError(f"{path.name} lacks final LF")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if not reader.fieldnames:
        raise ValueError(f"{path.name} lacks header")
    return list(reader.fieldnames), list(reader)


def verify_historical_prefixes() -> None:
    for name, (size, expected_sha) in PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if len(data) < size or sha_bytes(data[:size]) != expected_sha:
            raise ValueError(f"{name} Chapter 1--10 byte prefix changed")
    lines = (BACKEND / "units.jsonl").read_bytes().splitlines(keepends=True)
    if len(lines) != 18:
        raise ValueError(f"units.jsonl expected 18 rows, got {len(lines)}")
    prefix = b"".join(lines[:10])
    suffix = b"".join(lines[11:])
    if (len(prefix), sha_bytes(prefix)) != UNITS_PREFIX:
        raise ValueError("units.jsonl Chapter 1--10 rows changed")
    if (len(suffix), sha_bytes(suffix)) != UNITS_SUFFIX:
        raise ValueError("units.jsonl Chapter 12--bridge rows changed")


def verify_backend_manifest() -> None:
    paths = sorted(
        [path for path in BACKEND.iterdir() if path.is_file() and path.name != "BACKEND_MANIFEST.csv" and path.suffix != ".pyc"],
        key=lambda path: path.name.casefold(),
    )
    fields, rows = load_csv(BACKEND / "BACKEND_MANIFEST.csv")
    if fields != ["relative_path", "bytes", "sha256"]:
        raise ValueError("BACKEND_MANIFEST.csv header changed")
    expected = [(path.name, str(path.stat().st_size), sha_bytes(path.read_bytes())) for path in paths]
    actual = [(row["relative_path"], row["bytes"], row["sha256"]) for row in rows]
    if actual != expected:
        raise ValueError("BACKEND_MANIFEST.csv does not match current backend files")


def pdf_pages(path: Path) -> int:
    try:
        result = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
        match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.M)
        if match:
            return int(match.group(1))
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    # Conservative fallback: /Type /Page objects, excluding /Pages.
    return len(re.findall(rb"/Type\s*/Page(?:\s|/|>)", path.read_bytes()))


def require_receipt(record: dict, receipt_sha: str, location: str) -> None:
    expected = {
        "qa_receipt_id": RECEIPT_ID,
        "receipt_document_state": "present",
        "receipt_path": RECEIPT_REL,
        "receipt_sha256": receipt_sha,
        "admission_state": "admitted",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            raise ValueError(f"{location} {field} is not receipt-bound")


def verify_tex_structure(source: str, target: str) -> None:
    source_active = active_same_length(source)
    target_active = active_same_length(target)
    begin_pattern = re.compile(r"\\begin\{([^{}]+)\}")
    source_env = [m.group(1) for m in begin_pattern.finditer(source_active)]
    target_env = [m.group(1) for m in begin_pattern.finditer(target_active)]
    expected = collections.Counter({"prop": 35, "cor": 19, "exam": 15, "proof": 12, "defn": 10, "enumerate": 7, "bmatrix": 4, "thm": 4, "notn": 1})
    if len(source_env) != 107 or collections.Counter(source_env) != expected or source_env != target_env:
        raise ValueError("Chapter 11 source/target environment topology differs")
    for name, count in (("chapter", 1), ("section", 5), ("label", 38), ("cite", 5), ("index", 65), ("df", 21)):
        source_items = macros(source, name)
        target_items = macros(target, name)
        if len(source_items) != count or len(target_items) != count:
            raise ValueError(f"Chapter 11 {name} count changed")
        if name in {"label", "cite"} and [x["argument"] for x in source_items] != [x["argument"] for x in target_items]:
            raise ValueError(f"Chapter 11 {name} sequence changed")
    source_refs = sorted(macros(source, "ref") + macros(source, "eqref"), key=lambda x: x["start"])
    target_refs = sorted(macros(target, "ref") + macros(target, "eqref"), key=lambda x: x["start"])
    if len(source_refs) != 15 or [x["argument"] for x in source_refs] != [x["argument"] for x in target_refs]:
        raise ValueError("Chapter 11 reference sequence changed")


def verify_formula_maps(records: list[dict], source: str, target: str) -> None:
    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (625, 625):
        raise ValueError("Chapter 11 source/target math-surface count changed")
    if collections.Counter(x["delimiter"] for x in source_math) != {"dollar-inline": 604, "bracket-display": 21}:
        raise ValueError("Chapter 11 source math delimiters changed")
    expected_ids = [f"{CHAPTER_ID}-MATHMAP-{n:04d}" for n in range(1, 626)]
    if [record["id"] for record in records] != expected_ids:
        raise ValueError("Chapter 11 formula-map IDs/order changed")
    source_seen = []
    target_seen = []
    for record in records:
        source_ids = record.get("source_formula_ids", [])
        target_ids = record.get("target_formula_ids", [])
        if len(source_ids) != 1 or len(target_ids) != 1:
            raise ValueError(f"non-bijective formula map {record['id']}")
        source_number = int(source_ids[0].rsplit("-", 1)[1])
        target_number = int(target_ids[0].rsplit("-", 1)[1])
        if record.get("source_sha256") != [source_math[source_number - 1]["sha256"]]:
            raise ValueError(f"source formula hash differs on {record['id']}")
        if record.get("target_sha256") != [target_math[target_number - 1]["sha256"]]:
            raise ValueError(f"target formula hash differs on {record['id']}")
        source_seen.append(source_number)
        target_seen.append(target_number)
    if sorted(source_seen) != list(range(1, 626)) or sorted(target_seen) != list(range(1, 626)):
        raise ValueError("Chapter 11 formula source/target closure is incomplete")
    alignments = collections.Counter(record["alignment"] for record in records)
    if alignments != {
        "preserved_exact_after_text_aware_whitespace_normalization": 618,
        "localized_math_text_reviewed": 5,
        "reviewed_source_correction": 2,
    }:
        raise ValueError(f"Chapter 11 formula alignment counts changed: {alignments}")
    corrected = {record.get("correction_id") for record in records if record.get("correction_id")}
    if corrected != {f"{CHAPTER_ID}-CORR-001", f"{CHAPTER_ID}-CORR-004"}:
        raise ValueError("Chapter 11 correction-bound formula maps changed")


def main() -> None:
    verify_historical_prefixes()

    required_paths = [SOURCE_REL, TARGET_REL, MASTER_REL, PDF_REL, RECEIPT_REL, CORRECTIONS_REL]
    missing = [rel for rel in required_paths if not (ROOT / rel).is_file()]
    if missing:
        raise ValueError(f"Chapter 11 admission evidence missing: {missing}")

    jsonl_paths = sorted(BACKEND.glob("*.jsonl"), key=lambda path: path.name.casefold())
    records_by_file = {path.name: load_jsonl(path) for path in jsonl_paths}
    for name, expected in AGGREGATE_COUNTS.items():
        actual = len(records_by_file[name])
        if actual != expected:
            raise ValueError(f"{name} expected {expected} records, got {actual}")

    index_fields, index_rows = load_csv(BACKEND / "index_terms.csv")
    expected_index_fields = ["id", "parent_segment_id", "source_order", "source_line", "source_index_tex", "target_line", "target_index_tex", "source_sha256", "target_sha256", "locale"]
    if index_fields != expected_index_fields or len(index_rows) != 1_589:
        raise ValueError("index_terms.csv schema/aggregate count changed")

    # Global stable-ID uniqueness and relation endpoint closure.
    ids: dict[str, str] = {}
    for filename, records in records_by_file.items():
        for line_number, record in enumerate(records, 1):
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id:
                raise ValueError(f"{filename}:{line_number} lacks stable ID")
            if record_id in ids:
                raise ValueError(f"duplicate ID {record_id} in {ids[record_id]} and {filename}:{line_number}")
            ids[record_id] = f"{filename}:{line_number}"
    for line_number, row in enumerate(index_rows, 2):
        record_id = row["id"]
        if record_id in ids:
            raise ValueError(f"duplicate ID {record_id} in {ids[record_id]} and index_terms.csv:{line_number}")
        ids[record_id] = f"index_terms.csv:{line_number}"
    external_prefixes = ("COURSE-O007", "ERDMAN-FAOA-2015-LABEL-", "ERDMAN-FAOA-BIB-")
    for relation in records_by_file["relations.jsonl"] + records_by_file["concept_relations.jsonl"]:
        for field in ("from_id", "to_id"):
            endpoint = relation.get(field)
            if endpoint not in ids and not any(str(endpoint).startswith(prefix) for prefix in external_prefixes):
                raise ValueError(f"unresolved endpoint {endpoint} on {relation['id']}")
    for line_number, row in enumerate(index_rows, 2):
        if row["parent_segment_id"] not in ids:
            raise ValueError(f"unresolved parent segment on index_terms.csv:{line_number}")
    rights_ids = {record["id"] for record in records_by_file["rights.jsonl"]}
    for records in records_by_file.values():
        for record in records:
            if record.get("rights_id") and record["rights_id"] not in rights_ids:
                raise ValueError(f"unresolved rights ID on {record['id']}")

    source_info = identity(ROOT / SOURCE_REL)
    if source_info != SOURCE_IDENTITY:
        raise ValueError("Chapter 11 source authority identity changed")
    target_info = identity(ROOT / TARGET_REL)
    master_info = identity(ROOT / MASTER_REL)
    pdf_info = identity(ROOT / PDF_REL)
    if target_info[1] != 764 or b"\r" in (ROOT / TARGET_REL).read_bytes():
        raise ValueError("Chapter 11 target line/line-ending closure changed")
    if master_info[1] != 340 or "\\include{Gelfand_Naimark-id}" not in (ROOT / MASTER_REL).read_text(encoding="utf-8"):
        raise ValueError("Chapter 11 cumulative master closure changed")
    pages = pdf_pages(ROOT / PDF_REL)
    if pages != 164:
        raise ValueError(f"Chapter 11 cumulative PDF expected 164 pages, got {pages}")

    source = (ROOT / SOURCE_REL).read_text(encoding="ascii")
    target = (ROOT / TARGET_REL).read_text(encoding="utf-8")
    verify_tex_structure(source, target)

    # Unit identity and receipt binding.
    units = records_by_file["units.jsonl"]
    expected_unit_ids = [f"FAOA-2015-CH{n:02d}" for n in range(1, 18)] + ["FAOA-ID-BRIDGE-CS"]
    if [record["id"] for record in units] != expected_unit_ids:
        raise ValueError("units.jsonl order/closure changed")
    unit = units[10]
    receipt_data = (ROOT / RECEIPT_REL).read_bytes()
    receipt_sha = sha_bytes(receipt_data)
    receipt_text = receipt_data.decode("utf-8")
    if not re.search(r"Decision:\s*\*\*admitted\*\*", receipt_text, re.I):
        raise ValueError("Chapter 11 receipt does not assert admitted")
    target_title = macros(target, "chapter")[0]["argument"]
    expected_unit = {
        "order": 11,
        "source_path": "Gelfand_Naimark.tex",
        "source_bytes": source_info[0],
        "source_lines": source_info[1],
        "source_sha256": source_info[2],
        "source_title": "THE GELFAND-NAIMARK THEOREM",
        "target_path": TARGET_REL,
        "target_bytes": target_info[0],
        "target_lines": target_info[1],
        "target_sha256": target_info[2],
        "target_title": target_title,
        "course_role": "advanced_continuation",
        "translation_state": "admitted",
        "qa_state": "passed",
        "source_corrections": 6,
        "build_master_path": MASTER_REL,
        "build_master_bytes": master_info[0],
        "build_master_lines": master_info[1],
        "build_master_sha256": master_info[2],
        "artifact_path": PDF_REL,
        "artifact_bytes": pdf_info[0],
        "artifact_pages": pages,
        "artifact_sha256": pdf_info[2],
        "artifact_state": "canonical_output_copy_present_and_frozen",
        "publication_state": "pending",
        "rights_id": RIGHTS_ID,
    }
    for field, value in expected_unit.items():
        if unit.get(field) != value:
            raise ValueError(f"Chapter 11 unit {field} invariant failed")
    require_receipt(unit, receipt_sha, "Chapter 11 unit")
    for required_hash in (source_info[2], target_info[2], master_info[2], pdf_info[2]):
        if required_hash not in receipt_text:
            raise ValueError(f"receipt omits admitted identity {required_hash}")
    if MODEL_ID not in receipt_text:
        raise ValueError("receipt omits exact model provenance")

    # Exact Chapter 11 record-set counts.
    chapter_records: dict[str, list[dict]] = {}
    for name in ("semantic_units.jsonl", "segments.jsonl", "relations.jsonl", "formula_map.jsonl", "exercise_support.jsonl"):
        chapter_records[name] = [record for record in records_by_file[name] if record["id"].startswith(CHAPTER_ID + "-")]
    chapter_records["artifacts.jsonl"] = [record for record in records_by_file["artifacts.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    chapter_records["qa_events.jsonl"] = [record for record in records_by_file["qa_events.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    chapter_records["corrections.jsonl"] = [record for record in records_by_file["corrections.jsonl"] if record.get("unit_id") == CHAPTER_ID]
    chapter_records["terminology.jsonl"] = [record for record in records_by_file["terminology.jsonl"] if record["id"] in NEW_TERMS]
    chapter_index = [row for row in index_rows if row["id"].startswith(CHAPTER_ID + "-")]
    for name, expected in CH11_COUNTS.items():
        actual = len(chapter_index) if name == "index_terms.csv" else len(chapter_records[name])
        if actual != expected:
            raise ValueError(f"Chapter 11 {name} expected {expected}, got {actual}")

    semantic = chapter_records["semantic_units.jsonl"]
    kind_counts = collections.Counter(record["unit_kind"] for record in semantic)
    expected_kinds = {"section": 5, "prop": 35, "cor": 19, "exam": 15, "proof": 12, "defn": 10, "thm": 4, "notn": 1}
    if kind_counts != expected_kinds:
        raise ValueError(f"Chapter 11 semantic unit kinds changed: {kind_counts}")
    if any(record.get("translation_state") != "admitted" or record.get("qa_state") != "passed" for record in semantic + chapter_records["segments.jsonl"]):
        raise ValueError("Chapter 11 semantic/segment admission state differs")
    segment_roles = collections.Counter(record["segment_role"] for record in chapter_records["segments.jsonl"])
    if segment_roles != {"title": 6, "semantic_environment": 96, "prose": 16}:
        raise ValueError(f"Chapter 11 segment roles changed: {segment_roles}")

    relations = chapter_records["relations.jsonl"]
    if collections.Counter(record["relation_type"] for record in relations) != RELATION_TYPE_COUNTS:
        raise ValueError("Chapter 11 relation-type counts changed")
    if not any(record.get("relation_type") == "uses_asset" and record.get("to_id") == "ASSET-DIAGXY" and record.get("topology_preserved") is True for record in relations):
        raise ValueError("Chapter 11 diagram asset relation is absent")

    verify_formula_maps(chapter_records["formula_map.jsonl"], source, target)
    all_formula = records_by_file["formula_map.jsonl"]
    aggregate_formula_counts = (
        sum(len(record.get("source_formula_ids", [])) for record in all_formula),
        sum(len(record.get("target_formula_ids", [])) for record in all_formula),
        sum(record.get("alignment") in {"preserved_exact_after_whitespace_normalization", "preserved_exact_after_text_aware_whitespace_normalization", "preserved_exact_after_text_aware_whitespace_normalization_reordered", "preserved_math_key_after_localized_text_substitution"} for record in all_formula),
    )
    if aggregate_formula_counts != (8_143, 8_147, 7_989):
        raise ValueError(f"aggregate formula-map coverage changed: {aggregate_formula_counts}")

    source_indexes = macros(source, "index")
    target_indexes = macros(target, "index")
    expected_index_ids = [f"{CHAPTER_ID}-TERM-OCC-{n:04d}" for n in range(1, 66)]
    if [row["id"] for row in chapter_index] != expected_index_ids:
        raise ValueError("Chapter 11 index IDs/order changed")
    for number, (row, source_index, target_index) in enumerate(zip(chapter_index, source_indexes, target_indexes, strict=True), 1):
        expected = {
            "source_order": str(number),
            "source_line": str(source_index["line"]),
            "source_index_tex": source_index["argument"],
            "target_line": str(target_index["line"]),
            "target_index_tex": target_index["argument"],
            "source_sha256": sha_bytes(source_index["argument"].encode("ascii")),
            "target_sha256": sha_bytes(target_index["argument"].encode("utf-8")),
            "locale": "id-ID",
        }
        if any(row[field] != value for field, value in expected.items()):
            raise ValueError(f"Chapter 11 index occurrence {number} differs")

    terms = {record["id"]: record for record in chapter_records["terminology.jsonl"]}
    if set(terms) != set(NEW_TERMS):
        raise ValueError("Chapter 11 new-term ID set changed")
    for term_id, (source_term, preferred) in NEW_TERMS.items():
        if terms[term_id].get("source_term") != source_term or terms[term_id].get("preferred") != preferred or terms[term_id].get("locale") != "id-ID":
            raise ValueError(f"Chapter 11 terminology record changed: {term_id}")
    term_relations = [record for record in relations if record["relation_type"] == "uses_term"]
    source_df = macros(source, "df")
    target_df = macros(target, "df")
    if len(term_relations) != 21 or [record.get("source_term_tex") for record in term_relations] != [item["argument"] for item in source_df] or [record.get("target_term_tex") for record in term_relations] != [item["argument"] for item in target_df]:
        raise ValueError("Chapter 11 defined-term relation alignment changed")

    ledger_data = (ROOT / CORRECTIONS_REL).read_bytes()
    ledger = json.loads(ledger_data.decode("utf-8"))
    if ledger.get("unit_id") != CHAPTER_ID or ledger.get("record_count") != 6 or len(ledger.get("records", [])) != 6:
        raise ValueError("Chapter 11 correction ledger closure changed")
    if (ledger.get("source", {}).get("bytes"), ledger.get("source", {}).get("logical_records"), ledger.get("source", {}).get("sha256")) != source_info:
        raise ValueError("Chapter 11 correction ledger source identity differs")
    if (ledger.get("target", {}).get("bytes"), ledger.get("target", {}).get("logical_records"), ledger.get("target", {}).get("sha256")) != target_info:
        raise ValueError("Chapter 11 correction ledger target identity differs")
    correction_records = {record["id"]: record for record in chapter_records["corrections.jsonl"]}
    ledger_ids = [record["id"] for record in ledger["records"]]
    if list(correction_records) != ledger_ids:
        raise ValueError("Chapter 11 correction record IDs/order differ")
    ledger_sha = sha_bytes(ledger_data)
    for correction_id, record in correction_records.items():
        if record.get("ledger_sha256") != ledger_sha or record.get("qa_state") != "passed" or record.get("target_disposition") != "corrected":
            raise ValueError(f"Chapter 11 correction binding differs: {correction_id}")
        require_receipt(record, receipt_sha, correction_id)

    artifacts = {record["id"]: record for record in chapter_records["artifacts.jsonl"]}
    if set(artifacts) != set(ARTIFACT_SPECS):
        raise ValueError("Chapter 11 artifact ID closure changed")
    for artifact_id, (kind, relative_path) in ARTIFACT_SPECS.items():
        artifact = artifacts[artifact_id]
        path = ROOT / relative_path
        if not path.is_file():
            raise ValueError(f"artifact target missing: {relative_path}")
        info = identity(path)
        if artifact.get("artifact_kind") != kind or artifact.get("path") != relative_path or artifact.get("bytes") != info[0] or artifact.get("sha256") != info[2]:
            raise ValueError(f"artifact identity differs: {artifact_id}")
        require_receipt(artifact, receipt_sha, artifact_id)
    if artifacts["ARTIFACT-FAOA-ID-THROUGH-CH11-PDF"].get("pages") != pages:
        raise ValueError("Chapter 11 PDF artifact page count differs")

    qa = {record["id"]: record for record in chapter_records["qa_events.jsonl"]}
    if set(qa) != set(QA_SPECS):
        raise ValueError("Chapter 11 QA ID closure changed")
    for qa_id, qa_type in QA_SPECS.items():
        record = qa[qa_id]
        if record.get("qa_type") != qa_type or record.get("result") != "pass" or record.get("model_id") != MODEL_ID:
            raise ValueError(f"Chapter 11 QA result differs: {qa_id}")
        witness = ROOT / record["witness"]
        if not witness.is_file() or record.get("witness_sha256") != sha_bytes(witness.read_bytes()):
            raise ValueError(f"Chapter 11 QA witness differs: {qa_id}")
        require_receipt(record, receipt_sha, qa_id)
    if qa["QA-CH11-DIAGRAM-ACCESSIBILITY-20260823"].get("asset_id") != "ASSET-DIAGXY" or qa["QA-CH11-DIAGRAM-ACCESSIBILITY-20260823"].get("topology_preserved") is not True:
        raise ValueError("Chapter 11 diagram accessibility QA differs")
    admission = qa[RECEIPT_ID]
    if admission.get("all_required_admission_gates") != "pass" or admission.get("decision") != "admitted" or admission.get("target_sha256") != target_info[2] or admission.get("artifact_sha256") != pdf_info[2]:
        raise ValueError("Chapter 11 admission QA identity differs")

    # Visual manifest is a bounded exact 164-page witness.
    render_fields, render_rows = load_csv(ROOT / "provenance/CH11_RENDER_MANIFEST.csv")
    if len(render_rows) != pages or [int(row["page"]) for row in render_rows] != list(range(1, pages + 1)):
        raise ValueError("Chapter 11 render manifest page closure differs")
    for row in render_rows:
        render = ROOT / "qa/render-through-ch11-a" / row["file"]
        if not render.is_file() or str(render.stat().st_size) != row["bytes"] or sha_bytes(render.read_bytes()) != row["sha256"]:
            raise ValueError(f"render identity differs: {row['file']}")

    report_path = ROOT / "qa/CH11_BACKEND_RECONCILIATION.md"
    if not report_path.is_file():
        raise ValueError("Chapter 11 backend reconciliation report is absent")
    report_text = report_path.read_text(encoding="utf-8")
    if target_info[2] not in report_text or "Relation endpoint validation: pass" not in report_text:
        raise ValueError("Chapter 11 backend reconciliation report is stale")

    verify_backend_manifest()
    print(json.dumps({
        "status": "pass",
        "unit_id": CHAPTER_ID,
        "source_sha256": source_info[2],
        "target_sha256": target_info[2],
        "master_sha256": master_info[2],
        "pdf_sha256": pdf_info[2],
        "pdf_pages": pages,
        "receipt_sha256": receipt_sha,
        "aggregate_records": sum(AGGREGATE_COUNTS.values()) + len(index_rows),
        "chapter11": CH11_COUNTS,
        "relation_endpoints": "resolved",
        "historical_prefixes": "unchanged",
        "manifest": "exact",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
