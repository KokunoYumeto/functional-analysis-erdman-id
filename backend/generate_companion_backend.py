#!/usr/bin/env python3
"""Generate the additive O001 mastery and O008 bridge backend overlays.

This generator is intentionally append-only with respect to the admitted base
backend.  It writes a separate schema, record sets, and manifest; it never
opens an admitted backend file for writing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
SCHEMA = "interlanguage-modular-math"
SCHEMA_VERSION = "0.1.0"
OVERLAY_VERSION = "o008.companion-backend.v1"
BASE_MANIFEST_SHA256 = "06ad5f9c6931ef1838a8307c60b8b3b94a4c89a25d6ddc12dbfb2a3ddc591cfc"
ORIGINAL_RIGHTS_ID = "RIGHTS-ORIGINAL-CC-BY-SA-4.0"
ERDMAN_RIGHTS_ID = "RIGHTS-ERDMAN-CC-BY-SA-4.0"

ROOT_COMPONENT = "O008-FAOA-2015-COMPANION"
EXERCISE_COMPONENT = "O001-FAOA-2015-EXERCISE-SOLUTIONS"
READER_WORK_COMPONENT = "O001-FAOA-2015-READER-WORK-SOLUTIONS"
BRIDGE_COMPONENT = "O008-FAOA-2015-COMPACT-SPECTRAL-SVD-BRIDGE"

EXERCISE_PROVENANCE = "PROV-O001-FAOA-2015-EXERCISE-SOLUTIONS"
READER_WORK_PROVENANCE = "PROV-O001-FAOA-2015-READER-WORK-SOLUTIONS"
BRIDGE_PROVENANCE = "PROV-O008-FAOA-2015-COMPACT-SPECTRAL-SVD-BRIDGE"
EDITION_PROVENANCE = "PROV-O008-FAOA-2015-COMPANION-EDITION"

PDF_SURFACE = "O008-FAOA-2015-COMPANION-PDF"
HTML_SURFACE = "O008-FAOA-2015-COMPANION-HTML"

OUTPUT_FILES = (
    "companion_schema.json",
    "companion_components.jsonl",
    "companion_provenance.jsonl",
    "o001_mastery.jsonl",
    "o001_status.jsonl",
    "bridge_units.jsonl",
    "companion_surfaces.jsonl",
    "companion_html_routes.jsonl",
    "companion_relations.jsonl",
    "companion_artifacts.jsonl",
)

EXERCISE_BLOCK = re.compile(
    r"% O001-SOLUTION-ID: (?P<comment_solution>[^\n]+)\n"
    r"% SOURCE-EXERCISE-ID: (?P<comment_exercise>[^\n]+)\n"
    r"% STATEMENT-TARGET-SHA256: (?P<comment_hash>[0-9a-f]{64})\n"
    r"\\begin\{o001solution\}\s*"
    r"\{(?P<solution>[^{}]+)\}\s*"
    r"\{(?P<exercise>[^{}]+)\}\s*"
    r"\{(?P<hash>[0-9a-f]{64})\}\s*"
    r"\\begin\{o001statement\}\n(?P<statement>.*?)\n"
    r"\\end\{o001statement\}\s*"
    r"\\begin\{o001answer\}\n(?P<answer>.*?)\n"
    r"\\end\{o001answer\}\s*"
    r"\\begin\{o001proof\}\n(?P<proof>.*?)\n"
    r"\\end\{o001proof\}\s*"
    r"\\end\{o001solution\}",
    re.DOTALL,
)

READER_WORK_BLOCK = re.compile(
    r"% O001-READER-WORK-SOLUTION-ID: (?P<comment_solution>[^\n]+)\n"
    r"% SOURCE-RESULT-ID: (?P<comment_result>[^\n]+)\n"
    r"% SOURCE-HINT-ID: (?P<comment_hint>[^\n]+)\n"
    r"% RESULT-TARGET-SHA256: (?P<comment_result_hash>[0-9a-f]{64})\n"
    r"% HINT-TARGET-SHA256: (?P<comment_hint_hash>[0-9a-f]{64})\n"
    r"\\begin\{o001readerwork\}\s*"
    r"\{(?P<solution>[^{}]+)\}\s*"
    r"\{(?P<result_id>[^{}]+)\}\s*"
    r"\{(?P<hint_id>[^{}]+)\}\s*"
    r"\{(?P<result_hash>[0-9a-f]{64})\}\s*"
    r"\{(?P<hint_hash>[0-9a-f]{64})\}\s*"
    r"\\begin\{o001result\}\n(?P<result>.*?)\n\\end\{o001result\}\s*"
    r"\\begin\{o001sourcehint\}\n(?P<hint>.*?)\n\\end\{o001sourcehint\}\s*"
    r"\\begin\{o001answer\}\n(?P<answer>.*?)\n\\end\{o001answer\}\s*"
    r"\\begin\{o001proof\}\n(?P<proof>.*?)\n\\end\{o001proof\}\s*"
    r"\\end\{o001readerwork\}",
    re.DOTALL,
)

BRIDGE_MARKER = re.compile(r"^% O008-BRIDGE-ID: (?P<id>\S+)$", re.MULTILINE)
BRIDGE_BEGIN = re.compile(
    r"\\begin\{(?P<environment>defn|thm|rem|exam|lem|cor|prop)\}"
    r"(?:\[(?P<title>[^\]]+)\])?"
)
BRIDGE_KIND = {
    "defn": "definition",
    "thm": "theorem",
    "rem": "remark",
    "exam": "example",
    "lem": "lemma",
    "cor": "corollary",
    "prop": "proposition",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            raise RuntimeError(f"blank JSONL row in {rel(path)}:{number}")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"non-object JSONL row in {rel(path)}:{number}")
        rows.append(value)
    return rows


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return (
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for row in rows
        )
    ).encode("utf-8")


def line_span(text: str, start: int, end: int) -> tuple[int, int]:
    fragment = text[start:end]
    first = text.count("\n", 0, start) + 1
    return first, first + fragment.count("\n")


def statement_body(statement_tex: str) -> str:
    begin = r"\begin{exer}"
    end = r"\end{exer}"
    if not statement_tex.startswith(begin) or not statement_tex.endswith(end):
        raise RuntimeError("inventory statement is not one exact exer environment")
    body = statement_tex[len(begin) : -len(end)]
    if body.startswith(" "):
        body = body[1:]
    if body.endswith("\n"):
        body = body[:-1]
    return body


def base_fields(record_type: str, record_id: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "record_type": record_type,
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
    }


def require_component_validation_reports() -> None:
    reports = (
        ROOT / "qa" / "O001_SOLUTION_VALIDATION.json",
        ROOT / "qa" / "O001_READER_WORK_VALIDATION.json",
        ROOT / "qa" / "COMPACT_SPECTRAL_BRIDGE_VALIDATION.json",
    )
    for path in reports:
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("result") != "pass" or value.get("findings") != []:
            raise RuntimeError(f"component validation has not passed: {rel(path)}")
    solution_report = json.loads(
        (ROOT / "qa" / "O001_SOLUTION_VALIDATION.json").read_text(encoding="utf-8")
    )
    for item in solution_report["solution_files"]:
        path = ROOT / str(item["path"])
        raw = path.read_bytes()
        if len(raw) != int(item["bytes"]) or sha256(raw) != item["sha256"]:
            raise RuntimeError(f"solution validation receipt is stale: {rel(path)}")
    for report_name, path_key, bytes_key, sha_key in (
        (
            "O001_READER_WORK_VALIDATION.json",
            "source_path",
            "source_bytes",
            "source_sha256",
        ),
        (
            "COMPACT_SPECTRAL_BRIDGE_VALIDATION.json",
            "source_path",
            "source_bytes",
            "source_sha256",
        ),
    ):
        report = json.loads((ROOT / "qa" / report_name).read_text(encoding="utf-8"))
        path = ROOT / str(report[path_key])
        raw = path.read_bytes()
        if len(raw) != int(report[bytes_key]) or sha256(raw) != report[sha_key]:
            raise RuntimeError(f"component validation receipt is stale: {rel(path)}")


def require_integrated_validation_reports() -> None:
    final_build = json.loads(
        (ROOT / "qa" / "FINAL_COMPANION_BUILD_RESULT.json").read_text(encoding="utf-8")
    )
    if (
        final_build.get("result") != "pass"
        or not final_build.get("byte_identical")
        or final_build.get("companion_overfull_box_count") != 0
        or any(final_build.get("final_log_forbidden_counts", {}).values())
        or final_build.get("pages") != 298
    ):
        raise RuntimeError("final integrated PDF build receipt has not passed")
    pdf = ROOT / str(final_build["pdf"]["path"])
    pdf_raw = pdf.read_bytes()
    if len(pdf_raw) != int(final_build["pdf"]["bytes"]) or sha256(pdf_raw) != final_build["pdf"]["sha256"]:
        raise RuntimeError("final integrated PDF does not match its build receipt")

    snapshot_path = ROOT / "qa" / "FINAL_COMPANION_INPUT_SNAPSHOT.csv"
    with snapshot_path.open("r", encoding="utf-8", newline="") as handle:
        snapshot = list(csv.DictReader(handle))
    if len(snapshot) != int(final_build["input_snapshot"]["rows"]):
        raise RuntimeError("final PDF input snapshot row count differs from build receipt")
    snapshot_raw = snapshot_path.read_bytes()
    if sha256(snapshot_raw) != final_build["input_snapshot"]["sha256"]:
        raise RuntimeError("final PDF input snapshot hash differs from build receipt")
    for row in snapshot:
        path = ROOT / str(row["relative_path"])
        raw = path.read_bytes()
        if len(raw) != int(row["bytes"]) or sha256(raw) != row["sha256"]:
            raise RuntimeError(f"final PDF input snapshot is stale: {rel(path)}")

    security = json.loads(
        (ROOT / "qa" / "FINAL_COMPANION_PDF_SECURITY_NAVIGATION_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    render = json.loads(
        (ROOT / "qa" / "FINAL_COMPANION_RENDER_AUDIT.json").read_text(encoding="utf-8")
    )
    for name, report in (("security", security), ("render", render)):
        bound = report["pdf"]
        if (
            int(bound["bytes"]) != len(pdf_raw)
            or bound["sha256"] != sha256(pdf_raw)
            or int(report.get("pages", report.get("page_count", -1))) != 298
        ):
            raise RuntimeError(f"final PDF {name} receipt is stale")
    if security.get("status") != "pass" or security.get("failures") != []:
        raise RuntimeError("final PDF security/navigation QA has not passed")
    if render.get("outer_5px_ink_pages") != []:
        raise RuntimeError("final PDF render QA found outer-edge ink")

    html_reports = {
        "build": json.loads(
            (ROOT / "qa" / "HTML_COMPANION_BUILD_RESULT.json").read_text(encoding="utf-8")
        ),
        "machine": json.loads(
            (ROOT / "qa" / "HTML_COMPANION_QA.json").read_text(encoding="utf-8")
        ),
        "reproducibility": json.loads(
            (ROOT / "qa" / "HTML_COMPANION_REPRODUCIBILITY.json").read_text(
                encoding="utf-8"
            )
        ),
        "visual": json.loads(
            (ROOT / "qa" / "HTML_COMPANION_VISUAL_QA.json").read_text(encoding="utf-8")
        ),
    }
    if html_reports["build"].get("result") != "pass":
        raise RuntimeError("semantic HTML build has not passed")
    for name in ("machine", "reproducibility", "visual"):
        if not html_reports[name].get("passed"):
            raise RuntimeError(f"semantic HTML {name} QA has not passed")
    if html_reports["machine"].get("findings") != [] or html_reports["visual"].get("findings") != []:
        raise RuntimeError("semantic HTML QA contains findings")
    build = html_reports["build"]
    expected_counts = {
        "html_documents": 15,
        "manifested_files": 18,
        "mathml": 2288,
        "reader_work": 10,
        "route_records": 294,
        "routes": 14,
        "solutions": 52,
        "bridge_units": 13,
    }
    for key, expected in expected_counts.items():
        if int(build["counts"].get(key, -1)) != expected:
            raise RuntimeError(f"semantic HTML build count mismatch: {key}")
    for item in build["inputs"]:
        input_path = ROOT / str(item["path"])
        input_raw = input_path.read_bytes()
        if len(input_raw) != int(item["bytes"]) or sha256(input_raw) != item["sha256"]:
            raise RuntimeError(f"semantic HTML build input receipt is stale: {rel(input_path)}")
    manifest_path = ROOT / "output" / "html-companion" / "MANIFEST.csv"
    if sha256(manifest_path.read_bytes()) != build["artifacts"]["manifest_sha256"]:
        raise RuntimeError("semantic HTML manifest receipt is stale")
    manifest_rows = html_manifest_rows()
    site_rows = [
        (str(row["path"]), int(row["bytes"]), str(row["sha256"]))
        for row in manifest_rows
    ]
    manifest_raw = manifest_path.read_bytes()
    all_rows = site_rows + [("MANIFEST.csv", len(manifest_raw), sha256(manifest_raw))]
    if inventory_digest(site_rows) != build["artifacts"]["site_inventory_sha256"]:
        raise RuntimeError("semantic HTML site inventory receipt is stale")
    expected_html_artifacts = {
        "manifest_sha256": sha256(manifest_raw),
        "route_map_sha256": sha256(
            (ROOT / "output" / "html-companion" / "COMPANION_ROUTES.jsonl").read_bytes()
        ),
        "site_inventory_sha256": inventory_digest(site_rows),
        "site_inventory_sha256_excluding_manifest": inventory_digest(site_rows),
        "inventory_sha256_including_manifest": inventory_digest(all_rows),
    }
    for report_name in ("machine", "visual"):
        artifacts = html_reports[report_name].get("artifacts", {})
        for key, expected in expected_html_artifacts.items():
            if key in artifacts and artifacts[key] != expected:
                raise RuntimeError(
                    f"semantic HTML {report_name} QA artifact identity is stale: {key}"
                )
    canonical_replay = html_reports["reproducibility"]["builds"][0]
    if (
        int(canonical_replay["files"]) != len(all_rows)
        or int(canonical_replay["bytes"]) != sum(size for _, size, _ in all_rows)
        or canonical_replay["inventory_sha256_including_manifest"]
        != inventory_digest(all_rows)
    ):
        raise RuntimeError("semantic HTML deterministic replay receipt is stale")


def build_exercise_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inventory = load_jsonl(ROOT / "mastery" / "O001_EXERCISE_INVENTORY.jsonl")
    support_path = BACKEND / "exercise_support.jsonl"
    support_lines = support_path.read_text(encoding="utf-8").splitlines()
    support_rows = [json.loads(line) for line in support_lines]
    support_by_id = {str(row["id"]): (row, line) for row, line in zip(support_rows, support_lines)}

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in inventory:
        grouped[str(row["chapter_id"])].append(row)

    parsed: dict[str, tuple[re.Match[str], Path, str, bytes]] = {}
    for chapter_id, rows in grouped.items():
        chapter_number = chapter_id.rsplit("CH", 1)[1]
        path = ROOT / "mastery" / "id-ID" / f"solutions-ch{chapter_number}.tex"
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        matches = list(EXERCISE_BLOCK.finditer(text))
        expected_ids = [str(row["solution_id"]) for row in rows]
        actual_ids = [match.group("solution").strip() for match in matches]
        if actual_ids != expected_ids:
            raise RuntimeError(f"solution order/closure mismatch in {rel(path)}")
        for match in matches:
            parsed[match.group("solution").strip()] = (match, path, text, raw)

    solution_rows: list[dict[str, Any]] = []
    status_rows: list[dict[str, Any]] = []
    for inventory_row in inventory:
        solution_id = str(inventory_row["solution_id"])
        match, path, text, raw = parsed[solution_id]
        values = match.groupdict()
        expected_statement = statement_body(str(inventory_row["statement_tex"]))
        if values["exercise"].strip() != inventory_row["exercise_unit_id"]:
            raise RuntimeError(f"exercise binding mismatch for {solution_id}")
        if values["hash"] != inventory_row["statement_target_fragment_sha256"]:
            raise RuntimeError(f"statement hash binding mismatch for {solution_id}")
        if values["statement"] != expected_statement:
            raise RuntimeError(f"statement byte copy mismatch for {solution_id}")
        first, last = line_span(text, match.start(), match.end())
        fragment = match.group(0).encode("utf-8")
        row = base_fields("o001_exercise_solution", solution_id)
        row.update(
            {
                "admission_state": "admitted",
                "answer_fragment_sha256": sha256(values["answer"].encode("utf-8")),
                "authorship": "separately_authored_not_Erdman",
                "chapter_id": inventory_row["chapter_id"],
                "component_id": EXERCISE_COMPONENT,
                "component_source_bytes": len(raw),
                "component_source_file_sha256": sha256(raw),
                "component_source_line_end": last,
                "component_source_line_start": first,
                "component_source_path": rel(path),
                "exercise_unit_id": inventory_row["exercise_unit_id"],
                "locale": "id-ID",
                "model_provenance": MODEL,
                "production_state": "complete",
                "proof_fragment_sha256": sha256(values["proof"].encode("utf-8")),
                "provenance_id": EXERCISE_PROVENANCE,
                "rights_id": ORIGINAL_RIGHTS_ID,
                "solution_fragment_bytes": len(fragment),
                "solution_fragment_sha256": sha256(fragment),
                "source_exercise_order": inventory_row["source_exercise_order"],
                "statement_rights_id": inventory_row["statement_rights_id"],
                "statement_source_fragment_sha256": inventory_row[
                    "statement_source_fragment_sha256"
                ],
                "statement_target_fragment_sha256": inventory_row[
                    "statement_target_fragment_sha256"
                ],
                "support_id": inventory_row["support_id"],
                "validation_state": "integrated_pdf_html_passed",
            }
        )
        solution_rows.append(row)

        support_id = str(inventory_row["support_id"])
        if support_id not in support_by_id:
            raise RuntimeError(f"base support missing for {solution_id}")
        base_support, base_line = support_by_id[support_id]
        if base_support.get("original_solution_id") != solution_id:
            raise RuntimeError(f"base support solution mismatch for {solution_id}")
        status_id = f"{support_id}-STATUS-O001-COMPANION-001"
        status = base_fields("exercise_support_status_overlay", status_id)
        status.update(
            {
                "admission_state": "admitted",
                "base_original_solution_state": base_support["original_solution_state"],
                "base_support_id": support_id,
                "base_support_line_sha256": sha256(base_line.encode("utf-8")),
                "effective_original_solution_state": "admitted_in_companion_readers",
                "exercise_unit_id": inventory_row["exercise_unit_id"],
                "locale": "id-ID",
                "solution_id": solution_id,
                "validation_state": "integrated_pdf_html_passed",
            }
        )
        status_rows.append(status)

    if len(solution_rows) != 52 or len(status_rows) != 52:
        raise RuntimeError("exercise solution/status closure must be exactly 52/52")
    return solution_rows, status_rows


def build_reader_work_records() -> list[dict[str, Any]]:
    inventory = load_jsonl(ROOT / "mastery" / "O001_READER_WORK_INVENTORY.jsonl")
    path = ROOT / "mastery" / "id-ID" / "reader-work-selected.tex"
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    matches = list(READER_WORK_BLOCK.finditer(text))
    if len(inventory) != 10 or len(matches) != 10:
        raise RuntimeError("reader-work closure must be exactly 10/10")

    rows: list[dict[str, Any]] = []
    for inventory_row, match in zip(inventory, matches, strict=True):
        values = match.groupdict()
        solution_id = str(inventory_row["solution_id"])
        checks = {
            "solution": solution_id,
            "result_id": str(inventory_row["result_unit_id"]),
            "hint_id": str(inventory_row["upstream_hint_unit_id"]),
            "result_hash": str(inventory_row["result_target_fragment_sha256"]),
            "hint_hash": str(inventory_row["upstream_hint_target_fragment_sha256"]),
            "result": str(inventory_row["result_tex"]),
            "hint": str(inventory_row["upstream_hint_tex"]),
        }
        for field, expected in checks.items():
            actual = values[field].strip() if field.endswith("_id") or field == "solution" else values[field]
            if actual != expected:
                raise RuntimeError(f"reader-work binding mismatch for {solution_id}: {field}")
        first, last = line_span(text, match.start(), match.end())
        fragment = match.group(0).encode("utf-8")
        row = base_fields("o001_reader_work_solution", solution_id)
        row.update(
            {
                "admission_state": "admitted",
                "answer_fragment_sha256": sha256(values["answer"].encode("utf-8")),
                "authorship": "separately_authored_not_Erdman",
                "chapter_id": inventory_row["chapter_id"],
                "component_id": READER_WORK_COMPONENT,
                "component_source_bytes": len(raw),
                "component_source_file_sha256": sha256(raw),
                "component_source_line_end": last,
                "component_source_line_start": first,
                "component_source_path": rel(path),
                "locale": "id-ID",
                "model_provenance": MODEL,
                "production_state": "complete",
                "proof_fragment_sha256": sha256(values["proof"].encode("utf-8")),
                "provenance_id": READER_WORK_PROVENANCE,
                "result_kind": inventory_row["result_kind"],
                "result_target_fragment_sha256": inventory_row[
                    "result_target_fragment_sha256"
                ],
                "result_unit_id": inventory_row["result_unit_id"],
                "rights_id": ORIGINAL_RIGHTS_ID,
                "selection_order_in_chapter": inventory_row["selection_order_in_chapter"],
                "selection_rationale": inventory_row["selection_rationale"],
                "solution_fragment_bytes": len(fragment),
                "solution_fragment_sha256": sha256(fragment),
                "source_result_and_hint_rights_id": inventory_row[
                    "result_and_hint_rights_id"
                ],
                "upstream_hint_target_fragment_sha256": inventory_row[
                    "upstream_hint_target_fragment_sha256"
                ],
                "upstream_hint_unit_id": inventory_row["upstream_hint_unit_id"],
                "validation_state": "integrated_pdf_html_passed",
            }
        )
        rows.append(row)
    return rows


def parse_bridge() -> tuple[list[dict[str, Any]], list[tuple[str, str, str, int]]]:
    path = ROOT / "bridge" / "id-ID" / "compact-spectral-svd.tex"
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    markers = list(BRIDGE_MARKER.finditer(text))
    semantic_units = load_jsonl(BACKEND / "semantic_units.jsonl")
    source_label_to_id = {
        str(row["source_local_id"]): str(row["id"])
        for row in semantic_units
        if row.get("source_local_id")
    }

    rows: list[dict[str, Any]] = []
    label_to_bridge_id: dict[str, str] = {}
    spans: list[tuple[str, int, int]] = []
    for order, marker in enumerate(markers, 1):
        begin = BRIDGE_BEGIN.search(text, marker.end())
        next_marker_start = markers[order].start() if order < len(markers) else len(text)
        if begin is None or begin.start() >= next_marker_start:
            raise RuntimeError(f"bridge environment missing after {marker.group('id')}")
        environment = begin.group("environment")
        close_token = rf"\end{{{environment}}}"
        close_start = text.find(close_token, begin.end())
        if close_start < 0 or close_start >= next_marker_start:
            raise RuntimeError(f"bridge environment not closed for {marker.group('id')}")
        close_end = close_start + len(close_token)
        fragment = text[begin.start() : close_end]
        labels = re.findall(r"\\label\{([^{}]+)\}", fragment)
        if len(labels) > 1:
            raise RuntimeError(f"multiple labels in bridge unit {marker.group('id')}")
        label = labels[0] if labels else None
        if label:
            if label in label_to_bridge_id:
                raise RuntimeError(f"duplicate bridge label: {label}")
            label_to_bridge_id[label] = marker.group("id")
        first, last = line_span(text, begin.start(), close_end)
        row = base_fields("o008_bridge_unit", marker.group("id"))
        row.update(
            {
                "admission_state": "admitted",
                "authorship": "separately_authored_not_Erdman",
                "component_id": BRIDGE_COMPONENT,
                "component_source_file_sha256": sha256(raw),
                "component_source_path": rel(path),
                "label": label,
                "locale": "id-ID",
                "model_provenance": MODEL,
                "order_in_component": order,
                "production_state": "complete",
                "provenance_id": BRIDGE_PROVENANCE,
                "rights_id": ORIGINAL_RIGHTS_ID,
                "target_fragment_bytes": len(fragment.encode("utf-8")),
                "target_fragment_sha256": sha256(fragment.encode("utf-8")),
                "target_line_end": last,
                "target_line_start": first,
                "title_tex": begin.group("title"),
                "unit_kind": BRIDGE_KIND[environment],
                "validation_state": "integrated_pdf_html_passed",
            }
        )
        rows.append(row)
        segment_end = next_marker_start
        peta = text.find(r"\section{Peta penggunaan}", close_end, segment_end)
        if peta >= 0:
            segment_end = peta
        spans.append((marker.group("id"), marker.start(), segment_end))

    references: list[tuple[str, str, str, int]] = []
    for bridge_id, start, end in spans:
        segment = text[start:end]
        for order, label in enumerate(
            re.findall(r"\\(?:ref|eqref)\{([^{}]+)\}", segment), 1
        ):
            target_id = label_to_bridge_id.get(label) or source_label_to_id.get(label)
            if target_id is None:
                raise RuntimeError(f"unresolved bridge reference {label!r} from {bridge_id}")
            references.append((bridge_id, target_id, label, order))

    if len(rows) != 13:
        raise RuntimeError("bridge closure must be exactly 13 stable units")
    return rows, references


def build_components() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    solution_paths = [
        f"mastery/id-ID/solutions-ch{chapter}.tex"
        for chapter in ("01", "03", "04", "05", "06", "07", "08", "09", "10", "13", "14", "17")
    ]
    components = [
        {
            **base_fields("companion_component", ROOT_COMPONENT),
            "admission_state": "admitted",
            "component_kind": "mixed_companion_collection",
            "component_record_count": 75,
            "locale": "id-ID",
            "production_state": "complete",
            "provenance_id": EDITION_PROVENANCE,
            "rights_ids": [ERDMAN_RIGHTS_ID, ORIGINAL_RIGHTS_ID],
            "title": "Pendamping penguasaan O001 dan jembatan spektral-kompak O008",
        },
        {
            **base_fields("companion_component", EXERCISE_COMPONENT),
            "admission_state": "admitted",
            "component_kind": "exercise_solution_layer",
            "component_record_count": 52,
            "locale": "id-ID",
            "production_state": "complete",
            "provenance_id": EXERCISE_PROVENANCE,
            "rights_id": ORIGINAL_RIGHTS_ID,
            "source_paths": solution_paths,
            "source_statement_rights_id": ERDMAN_RIGHTS_ID,
            "title": "Solusi lengkap untuk 52 latihan eksplisit",
        },
        {
            **base_fields("companion_component", READER_WORK_COMPONENT),
            "admission_state": "admitted",
            "component_kind": "selected_reader_work_solution_layer",
            "component_record_count": 10,
            "locale": "id-ID",
            "production_state": "complete",
            "provenance_id": READER_WORK_PROVENANCE,
            "rights_id": ORIGINAL_RIGHTS_ID,
            "source_paths": ["mastery/id-ID/reader-work-selected.tex"],
            "source_statement_rights_id": ERDMAN_RIGHTS_ID,
            "title": "Pembuktian lengkap untuk 10 hasil kerja-pembaca terpilih",
        },
        {
            **base_fields("companion_component", BRIDGE_COMPONENT),
            "admission_state": "admitted",
            "component_kind": "original_compact_spectral_svd_bridge",
            "component_record_count": 13,
            "locale": "id-ID",
            "production_state": "complete",
            "provenance_id": BRIDGE_PROVENANCE,
            "rights_id": ORIGINAL_RIGHTS_ID,
            "source_paths": ["bridge/id-ID/compact-spectral-svd.tex"],
            "title": "Jembatan spektral-kompak dan nilai singular",
        },
    ]
    provenance_common = {
        "admission_state": "admitted",
        "authorship": "separately_authored_not_Erdman",
        "creation_agent": MODEL,
        "creation_direction": "at_user_direction",
        "license": "CC BY-SA 4.0",
        "nonendorsement": "Not authored or endorsed by John M. Erdman or Portland State University",
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "source_author_credit_preserved": "John M. Erdman",
    }
    provenance = [
        {
            **provenance_common,
            "authorship": "mixed_Erdman_source_and_separately_authored_companions",
            "component_id": ROOT_COMPONENT,
            "id": EDITION_PROVENANCE,
            "record_type": "companion_provenance",
            "rights_ids": [ERDMAN_RIGHTS_ID, ORIGINAL_RIGHTS_ID],
            "source_material_boundary": "Erdman source statements remain under their source attribution; Indonesian adaptation and separately authored answers, proofs, bridge, metadata, and accessible surfaces preserve distinct provenance",
        },
        {
            **provenance_common,
            "component_id": EXERCISE_COMPONENT,
            "id": EXERCISE_PROVENANCE,
            "record_type": "companion_provenance",
            "rights_id": ORIGINAL_RIGHTS_ID,
            "source_material_boundary": "exercise statements remain Erdman; answers and proofs are separate original material",
        },
        {
            **provenance_common,
            "component_id": READER_WORK_COMPONENT,
            "id": READER_WORK_PROVENANCE,
            "record_type": "companion_provenance",
            "rights_id": ORIGINAL_RIGHTS_ID,
            "source_material_boundary": "result statements and hints remain Erdman; completed proofs are separate original material",
        },
        {
            **provenance_common,
            "component_id": BRIDGE_COMPONENT,
            "id": BRIDGE_PROVENANCE,
            "record_type": "companion_provenance",
            "rights_id": ORIGINAL_RIGHTS_ID,
            "source_material_boundary": "original bridge connected to, but not represented as part of, Erdman's source text",
        },
    ]
    return components, provenance


def artifact_record(
    artifact_id: str,
    path_string: str,
    kind: str,
    component_id: str,
    **extra: Any,
) -> dict[str, Any]:
    path = ROOT / path_string
    raw = path.read_bytes()
    row = base_fields("companion_artifact", artifact_id)
    row.update(
        {
            "admission_state": "admitted",
            "artifact_kind": kind,
            "binding_state": "bound",
            "bytes": len(raw),
            "component_id": component_id,
            "lines": len(raw.splitlines()),
            "path": path_string,
            "sha256": sha256(raw),
        }
    )
    row.update(extra)
    return row


def html_manifest_rows() -> list[dict[str, Any]]:
    path = ROOT / "output" / "html-companion" / "MANIFEST.csv"
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    rows = list(csv.DictReader(raw_lines))
    expected_order = sorted(str(row["path"]) for row in rows)
    if [str(row["path"]) for row in rows] != expected_order:
        raise RuntimeError("HTML companion manifest is not in stable path order")
    for row, raw_line in zip(rows, raw_lines[1:], strict=True):
        item = ROOT / "output" / "html-companion" / str(row["path"])
        raw = item.read_bytes()
        if len(raw) != int(row["bytes"]) or sha256(raw) != row["sha256"]:
            raise RuntimeError(f"HTML companion manifest mismatch: {row['path']}")
        row["manifest_line_sha256"] = sha256(raw_line.encode("utf-8"))
    if len(rows) != 18:
        raise RuntimeError(f"HTML companion manifest closure must be 18, got {len(rows)}")
    return rows


def inventory_digest(rows: list[tuple[str, int, str]]) -> str:
    material = "".join(
        f"{path}\0{size}\0{digest}\n" for path, size, digest in sorted(rows)
    ).encode("utf-8")
    return sha256(material)


def build_artifacts() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    chapter_counts = {
        "01": 6,
        "03": 7,
        "04": 10,
        "05": 4,
        "06": 6,
        "07": 1,
        "08": 2,
        "09": 1,
        "10": 11,
        "13": 1,
        "14": 2,
        "17": 1,
    }
    for chapter, count in chapter_counts.items():
        rows.append(
            artifact_record(
                f"ARTIFACT-O001-FAOA-2015-CH{chapter}-SOLUTIONS-TEX",
                f"mastery/id-ID/solutions-ch{chapter}.tex",
                "o001_exercise_solution_source",
                EXERCISE_COMPONENT,
                solution_records=count,
            )
        )
    rows.extend(
        [
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-READER-WORK-TEX",
                "mastery/id-ID/reader-work-selected.tex",
                "o001_reader_work_solution_source",
                READER_WORK_COMPONENT,
                solution_records=10,
            ),
            artifact_record(
                "ARTIFACT-O008-FAOA-2015-COMPACT-SPECTRAL-SVD-TEX",
                "bridge/id-ID/compact-spectral-svd.tex",
                "o008_original_bridge_source",
                BRIDGE_COMPONENT,
                stable_unit_records=13,
            ),
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-EXERCISE-INVENTORY",
                "mastery/O001_EXERCISE_INVENTORY.jsonl",
                "source_binding_inventory",
                EXERCISE_COMPONENT,
                inventory_records=52,
            ),
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-READER-WORK-INVENTORY",
                "mastery/O001_READER_WORK_INVENTORY.jsonl",
                "source_binding_inventory",
                READER_WORK_COMPONENT,
                inventory_records=10,
            ),
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-MASTERY-README",
                "mastery/README.md",
                "component_scope_and_rights_document",
                ROOT_COMPONENT,
            ),
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-SOLUTION-CONTRACT",
                "mastery/O001_SOLUTION_FILE_CONTRACT.md",
                "component_contract",
                EXERCISE_COMPONENT,
            ),
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-READER-WORK-CONTRACT",
                "mastery/O001_READER_WORK_CONTRACT.md",
                "component_contract",
                READER_WORK_COMPONENT,
            ),
            artifact_record(
                "ARTIFACT-O008-FAOA-2015-BRIDGE-README",
                "bridge/README.md",
                "component_scope_and_rights_document",
                BRIDGE_COMPONENT,
            ),
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-SOLUTION-VALIDATION",
                "qa/O001_SOLUTION_VALIDATION.json",
                "component_validation_evidence",
                EXERCISE_COMPONENT,
                result="pass",
            ),
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-READER-WORK-VALIDATION",
                "qa/O001_READER_WORK_VALIDATION.json",
                "component_validation_evidence",
                READER_WORK_COMPONENT,
                result="pass",
            ),
            artifact_record(
                "ARTIFACT-O008-FAOA-2015-BRIDGE-VALIDATION",
                "qa/COMPACT_SPECTRAL_BRIDGE_VALIDATION.json",
                "component_validation_evidence",
                BRIDGE_COMPONENT,
                result="pass",
            ),
            artifact_record(
                "ARTIFACT-O001-FAOA-2015-SOURCE-ADJUDICATIONS",
                "provenance/O001_SOURCE_ADJUDICATIONS.json",
                "source_adjudication_evidence",
                EXERCISE_COMPONENT,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-BACKEND-GENERATOR",
                "backend/generate_companion_backend.py",
                "deterministic_companion_backend_generator",
                ROOT_COMPONENT,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-BACKEND-VALIDATOR",
                "qa/validate_companion_backend.py",
                "strict_companion_backend_validator",
                ROOT_COMPONENT,
            ),
        ]
    )
    rows.extend(
        [
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-PDF",
                "output/pdf/analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf",
                "integrated_pdf_reader",
                ROOT_COMPONENT,
                pages=298,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-MASTER-TEX",
                "source/id-ID/functional-analysis-id-complete-with-companions.tex",
                "integrated_pdf_master_source",
                ROOT_COMPONENT,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-MASTER-RESULT",
                "qa/FINAL_COMPANION_MASTER_RESULT.json",
                "integrated_master_generation_receipt",
                ROOT_COMPONENT,
                result="pass",
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-MASTER-GENERATOR",
                "qa/build_final_companion_master.py",
                "integrated_master_generator",
                ROOT_COMPONENT,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-PDF-BUILD-RUNNER",
                "qa/run_final_companion_build.ps1",
                "deterministic_pdf_build_runner",
                ROOT_COMPONENT,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-PDF-BUILD-RESULT",
                "qa/FINAL_COMPANION_BUILD_RESULT.json",
                "deterministic_pdf_build_receipt",
                ROOT_COMPONENT,
                result="pass",
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-INPUT-SNAPSHOT",
                "qa/FINAL_COMPANION_INPUT_SNAPSHOT.csv",
                "deterministic_pdf_input_snapshot",
                ROOT_COMPONENT,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-PDF-BUILD-LOG-A",
                "qa/FINAL_COMPANION_BUILD_PASS1_LOG.txt",
                "deterministic_pdf_build_log",
                ROOT_COMPONENT,
                replay="a",
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-PDF-BUILD-LOG-B",
                "qa/FINAL_COMPANION_BUILD_PASS2_LOG.txt",
                "deterministic_pdf_build_log",
                ROOT_COMPONENT,
                replay="b",
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-COMPONENT-VALIDATION-CONSOLE",
                "qa/FINAL_COMPANION_COMPONENT_VALIDATION_CONSOLE.txt",
                "component_validation_console",
                ROOT_COMPONENT,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-MASTER-GENERATOR-CONSOLE",
                "qa/FINAL_COMPANION_GENERATOR_CONSOLE.txt",
                "integrated_master_generation_console",
                ROOT_COMPONENT,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-PDF-AUDITOR",
                "qa/audit_final_companion_pdf.py",
                "pdf_security_navigation_auditor",
                ROOT_COMPONENT,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-PDF-SECURITY-AUDIT",
                "qa/FINAL_COMPANION_PDF_SECURITY_NAVIGATION_AUDIT.json",
                "pdf_security_navigation_receipt",
                ROOT_COMPONENT,
                result="pass",
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-RENDER-AUDITOR",
                "qa/make_final_companion_render_evidence.py",
                "all_page_render_auditor",
                ROOT_COMPONENT,
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-RENDER-AUDIT",
                "qa/FINAL_COMPANION_RENDER_AUDIT.json",
                "all_page_render_receipt",
                ROOT_COMPONENT,
                result="pass",
                surface_id=PDF_SURFACE,
            ),
            artifact_record(
                "ARTIFACT-O008-COMPANION-FINAL-RENDER-MANIFEST",
                "provenance/FINAL_COMPANION_RENDER_MANIFEST.csv",
                "all_page_render_manifest",
                ROOT_COMPONENT,
                pages=298,
                surface_id=PDF_SURFACE,
            ),
        ]
    )
    html_tooling = [
        (
            "ARTIFACT-O008-COMPANION-HTML-BUILDER",
            "html/build_companion_reader.py",
            "semantic_html_builder",
        ),
        (
            "ARTIFACT-O008-COMPANION-HTML-QA-SCRIPT",
            "html/qa_companion_reader.py",
            "semantic_html_qa_script",
        ),
        (
            "ARTIFACT-O008-COMPANION-HTML-REPLAY-VERIFIER",
            "html/verify_companion_replays.py",
            "semantic_html_replay_verifier",
        ),
        (
            "ARTIFACT-O008-COMPANION-HTML-BUILD-RESULT",
            "qa/HTML_COMPANION_BUILD_RESULT.json",
            "semantic_html_build_receipt",
        ),
        (
            "ARTIFACT-O008-COMPANION-HTML-BUILD-REPLAY-A",
            "qa/HTML_COMPANION_BUILD_REPLAY_A.json",
            "semantic_html_build_replay_receipt",
        ),
        (
            "ARTIFACT-O008-COMPANION-HTML-BUILD-REPLAY-B",
            "qa/HTML_COMPANION_BUILD_REPLAY_B.json",
            "semantic_html_build_replay_receipt",
        ),
        (
            "ARTIFACT-O008-COMPANION-HTML-QA",
            "qa/HTML_COMPANION_QA.json",
            "semantic_html_machine_qa_receipt",
        ),
        (
            "ARTIFACT-O008-COMPANION-HTML-REPRODUCIBILITY",
            "qa/HTML_COMPANION_REPRODUCIBILITY.json",
            "semantic_html_reproducibility_receipt",
        ),
        (
            "ARTIFACT-O008-COMPANION-HTML-VISUAL-QA",
            "qa/HTML_COMPANION_VISUAL_QA.json",
            "semantic_html_responsive_visual_qa_receipt",
        ),
    ]
    for artifact_id, path_string, kind in html_tooling:
        rows.append(
            artifact_record(
                artifact_id,
                path_string,
                kind,
                ROOT_COMPONENT,
                surface_id=HTML_SURFACE,
            )
        )
    rows.append(
        artifact_record(
            "ARTIFACT-O008-COMPANION-HTML-MANIFEST",
            "output/html-companion/MANIFEST.csv",
            "semantic_html_site_manifest",
            ROOT_COMPONENT,
            manifested_files=18,
            surface_id=HTML_SURFACE,
        )
    )
    for order, manifest_row in enumerate(html_manifest_rows(), 1):
        path_string = f"output/html-companion/{manifest_row['path']}"
        suffix = Path(str(manifest_row["path"])).suffix.lower()
        if manifest_row["path"] == "COMPANION_ROUTES.jsonl":
            kind = "semantic_html_route_map"
        elif suffix == ".html":
            kind = "semantic_html_document"
        elif suffix == ".css":
            kind = "semantic_html_stylesheet"
        else:
            kind = "semantic_html_site_file"
        rows.append(
            artifact_record(
                f"ARTIFACT-O008-COMPANION-HTML-FILE-{order:03d}",
                path_string,
                kind,
                ROOT_COMPONENT,
                manifest_line_sha256=manifest_row["manifest_line_sha256"],
                manifest_order=order,
                surface_id=HTML_SURFACE,
            )
        )
    if len(rows) != 70:
        raise RuntimeError(f"companion artifact closure must be 70, got {len(rows)}")
    return rows


def build_surfaces(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pdf_path = (
        ROOT
        / "output"
        / "pdf"
        / "analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf"
    )
    pdf_raw = pdf_path.read_bytes()
    html_root = ROOT / "output" / "html-companion"
    manifest_path = html_root / "MANIFEST.csv"
    manifest_raw = manifest_path.read_bytes()
    manifest_rows = html_manifest_rows()
    site_rows = [
        (str(row["path"]), int(row["bytes"]), str(row["sha256"]))
        for row in manifest_rows
    ]
    all_rows = site_rows + [("MANIFEST.csv", len(manifest_raw), sha256(manifest_raw))]
    artifacts_by_surface: dict[str, list[str]] = defaultdict(list)
    for artifact in artifacts:
        if artifact.get("surface_id"):
            artifacts_by_surface[str(artifact["surface_id"])].append(str(artifact["id"]))
    build = json.loads((ROOT / "qa" / "HTML_COMPANION_BUILD_RESULT.json").read_text(encoding="utf-8"))
    surfaces = [
        {
            **base_fields("companion_surface", PDF_SURFACE),
            "accessible_alternative_surface_id": HTML_SURFACE,
            "admission_state": "admitted",
            "artifact_ids": artifacts_by_surface[PDF_SURFACE],
            "bytes": len(pdf_raw),
            "deterministic_replay": True,
            "locale": "id-ID",
            "pages": 298,
            "path": rel(pdf_path),
            "pdf_tagging_state": "untagged",
            "provenance_id": EDITION_PROVENANCE,
            "rights_ids": [ERDMAN_RIGHTS_ID, ORIGINAL_RIGHTS_ID],
            "sha256": sha256(pdf_raw),
            "surface_kind": "pdf_reader",
            "title": "Analisis Fungsional dan Aljabar Operator — edisi lengkap dengan pendamping",
            "validation_state": "deterministic_build_security_navigation_and_all_page_render_passed",
        },
        {
            **base_fields("companion_surface", HTML_SURFACE),
            "admission_state": "admitted",
            "artifact_ids": artifacts_by_surface[HTML_SURFACE],
            "bridge_units": 13,
            "bytes": sum(size for _, size, _ in all_rows),
            "deterministic_replay": True,
            "directory_path": rel(html_root),
            "files": len(all_rows),
            "html_documents": int(build["counts"]["html_documents"]),
            "inventory_sha256_excluding_manifest": inventory_digest(site_rows),
            "inventory_sha256_including_manifest": inventory_digest(all_rows),
            "locale": "id-ID",
            "manifest_path": rel(manifest_path),
            "manifest_sha256": sha256(manifest_raw),
            "math_surface": "native_MathML",
            "mathml_elements": int(build["counts"]["mathml"]),
            "provenance_id": EDITION_PROVENANCE,
            "reader_work_solutions": 10,
            "rights_ids": [ERDMAN_RIGHTS_ID, ORIGINAL_RIGHTS_ID],
            "route_map_path": "output/html-companion/COMPANION_ROUTES.jsonl",
            "route_map_sha256": str(build["artifacts"]["route_map_sha256"]),
            "route_records": int(build["counts"]["route_records"]),
            "routes": int(build["counts"]["routes"]),
            "source_reader_inventory_sha256": str(
                build["source_reader"]["after_inventory_sha256"]
            ),
            "source_reader_unchanged": bool(build["source_reader"]["unchanged"]),
            "surface_kind": "semantic_html_reader",
            "title": "Pendamping semantik: solusi, hasil kerja-pembaca, dan jembatan spektral-kompak",
            "validation_state": "deterministic_build_machine_accessibility_and_responsive_visual_QA_passed",
            "exercise_solutions": 52,
        },
    ]
    return surfaces


def build_html_routes(
    exercise_rows: list[dict[str, Any]],
    reader_rows: list[dict[str, Any]],
    bridge_rows: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    path = ROOT / "output" / "html-companion" / "COMPANION_ROUTES.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    file_artifact_by_path = {
        str(artifact["path"]).removeprefix("output/html-companion/"): str(artifact["id"])
        for artifact in artifacts
        if artifact.get("surface_id") == HTML_SURFACE
        and str(artifact["path"]).startswith("output/html-companion/")
    }
    route_map_artifact_id = file_artifact_by_path["COMPANION_ROUTES.jsonl"]
    primary_ids = {
        str(row["id"]) for row in exercise_rows + reader_rows + bridge_rows
    }
    rows: list[dict[str, Any]] = []
    prior_target = ""
    for order, line in enumerate(lines, 1):
        source = json.loads(line)
        target_id = str(source["id"])
        if target_id < prior_target:
            raise RuntimeError("HTML companion route map is not in stable target-ID order")
        prior_target = target_id
        output_path = str(source["output_path"])
        if output_path not in file_artifact_by_path:
            raise RuntimeError(f"HTML route output is not manifested: {output_path}")
        row = base_fields(
            "companion_html_route", f"O008-COMPANION-HTML-ROUTE-{order:04d}"
        )
        row.update(
            {
                "admission_state": "admitted",
                "href": source["href"],
                "locale": source["locale"],
                "output_artifact_id": file_artifact_by_path[output_path],
                "output_path": output_path,
                "route": source["route"],
                "route_map_artifact_id": route_map_artifact_id,
                "route_map_line_sha256": sha256(line.encode("utf-8")),
                "route_order": order,
                "surface_id": HTML_SURFACE,
                "target_binding_state": "registered_backend_unit"
                if target_id in primary_ids
                else "reader_subsurface_anchor",
                "target_stable_id": target_id,
            }
        )
        rows.append(row)
    if len(rows) != 294:
        raise RuntimeError(f"HTML companion route closure must be 294, got {len(rows)}")
    return rows


def build_relations(
    components: list[dict[str, Any]],
    provenance: list[dict[str, Any]],
    exercise_rows: list[dict[str, Any]],
    reader_rows: list[dict[str, Any]],
    status_rows: list[dict[str, Any]],
    bridge_rows: list[dict[str, Any]],
    bridge_references: list[tuple[str, str, str, int]],
    surfaces: list[dict[str, Any]],
    html_routes: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []

    def add(from_id: str, relation_type: str, to_id: str, **extra: Any) -> None:
        row = base_fields(
            "companion_relation", f"O008-COMPANION-REL-{len(relations) + 1:04d}"
        )
        row.update({"from_id": from_id, "relation_type": relation_type, "to_id": to_id})
        row.update(extra)
        relations.append(row)

    for component_id in (EXERCISE_COMPONENT, READER_WORK_COMPONENT, BRIDGE_COMPONENT):
        add(ROOT_COMPONENT, "contains_component", component_id)
    provenance_by_component = {row["component_id"]: row["id"] for row in provenance}
    for component in components:
        add(component["id"], "governed_by_provenance", provenance_by_component[component["id"]])
        for rights_id in component.get("rights_ids", [component.get("rights_id")]):
            add(component["id"], "licensed_under", str(rights_id))

    for artifact in artifacts:
        add(str(artifact["component_id"]), "represented_by_artifact", str(artifact["id"]))
        if artifact.get("surface_id"):
            add(str(artifact["surface_id"]), "represented_by_artifact", str(artifact["id"]))

    for surface in surfaces:
        add(ROOT_COMPONENT, "rendered_as", str(surface["id"]))
        add(str(surface["id"]), "governed_by_provenance", EDITION_PROVENANCE)
        for rights_id in surface["rights_ids"]:
            add(str(surface["id"]), "licensed_under", str(rights_id))
    for component_id in (EXERCISE_COMPONENT, READER_WORK_COMPONENT, BRIDGE_COMPONENT):
        for surface_id in (PDF_SURFACE, HTML_SURFACE):
            add(component_id, "available_on_surface", surface_id)

    primary_content_ids = {
        str(row["id"]) for row in exercise_rows + reader_rows + bridge_rows
    }
    for route in html_routes:
        route_id = str(route["id"])
        add(HTML_SURFACE, "exposes_route", route_id)
        target_id = str(route["target_stable_id"])
        if target_id in primary_content_ids:
            add(target_id, "available_at_route", route_id)

    inventory = load_jsonl(ROOT / "mastery" / "O001_EXERCISE_INVENTORY.jsonl")
    inventory_by_solution = {str(row["solution_id"]): row for row in inventory}
    status_by_solution = {str(row["solution_id"]): row for row in status_rows}
    for solution in exercise_rows:
        solution_id = str(solution["id"])
        source = inventory_by_solution[solution_id]
        status = status_by_solution[solution_id]
        add(EXERCISE_COMPONENT, "contains_solution", solution_id)
        add(EXERCISE_COMPONENT, "contains_status_overlay", str(status["id"]))
        add(solution_id, "solves", str(source["exercise_unit_id"]))
        for hint_order, hint in enumerate(source["upstream_hint_records"], 1):
            add(
                solution_id,
                "uses_source_hint",
                str(hint["hint_unit_id"]),
                hint_order=hint_order,
            )
        add(str(status["id"]), "overlays_support", str(source["support_id"]))
        add(str(status["id"]), "reports_solution", solution_id)

    reader_inventory = load_jsonl(ROOT / "mastery" / "O001_READER_WORK_INVENTORY.jsonl")
    reader_by_solution = {str(row["solution_id"]): row for row in reader_inventory}
    for solution in reader_rows:
        solution_id = str(solution["id"])
        source = reader_by_solution[solution_id]
        add(READER_WORK_COMPONENT, "contains_solution", solution_id)
        add(solution_id, "completes_source_proof", str(source["result_unit_id"]))
        add(solution_id, "uses_source_hint", str(source["upstream_hint_unit_id"]))

    for unit in bridge_rows:
        add(BRIDGE_COMPONENT, "contains_bridge_unit", str(unit["id"]))
    for source_id, target_id, label, order in bridge_references:
        add(source_id, "references", target_id, reference_label=label, reference_order=order)
    for order, chapter_id in enumerate(
        (
            "FAOA-2015-CH04",
            "FAOA-2015-CH07",
            "FAOA-2015-CH08",
            "FAOA-2015-CH11",
            "FAOA-2015-CH15",
        ),
        1,
    ):
        add(BRIDGE_COMPONENT, "requires_chapter", chapter_id, prerequisite_order=order)
    return relations


def build_schema() -> dict[str, Any]:
    return {
        "base_backend_manifest": "backend/BACKEND_MANIFEST.csv",
        "base_backend_manifest_sha256": BASE_MANIFEST_SHA256,
        "base_schema": SCHEMA,
        "base_schema_version": SCHEMA_VERSION,
        "encoding": "UTF-8",
        "identity_policy": "locale-neutral stable IDs; never page-derived",
        "overlay": OVERLAY_VERSION,
        "record_sets": [
            {"path": "companion_components.jsonl", "record_type": "companion_component"},
            {"path": "companion_provenance.jsonl", "record_type": "companion_provenance"},
            {
                "path": "o001_mastery.jsonl",
                "record_types": ["o001_exercise_solution", "o001_reader_work_solution"],
            },
            {"path": "o001_status.jsonl", "record_type": "exercise_support_status_overlay"},
            {"path": "bridge_units.jsonl", "record_type": "o008_bridge_unit"},
            {"path": "companion_surfaces.jsonl", "record_type": "companion_surface"},
            {"path": "companion_html_routes.jsonl", "record_type": "companion_html_route"},
            {"path": "companion_relations.jsonl", "record_type": "companion_relation"},
            {"path": "companion_artifacts.jsonl", "record_type": "companion_artifact"},
        ],
        "state_policy": {
            "admission_state": "admitted",
            "meaning": "component sources and their integrated deterministic PDF and semantic HTML readers passed their stated gates and are exactly bound here",
        },
        "write_policy": "additive overlay; admitted base backend files are read-only",
    }


def manifest_bytes(output_dir: Path) -> bytes:
    rows: list[tuple[str, int, str]] = []
    for name in OUTPUT_FILES:
        path = output_dir / name
        raw = path.read_bytes()
        rows.append((name, len(raw), sha256(raw)))
    generator = Path(__file__).resolve()
    raw = generator.read_bytes()
    rows.append(("generate_companion_backend.py", len(raw), sha256(raw)))
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(("relative_path", "bytes", "sha256"))
    for row in sorted(rows):
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def write_outputs(output_dir: Path) -> dict[str, int]:
    require_component_validation_reports()
    require_integrated_validation_reports()
    exercise_rows, status_rows = build_exercise_records()
    reader_rows = build_reader_work_records()
    bridge_rows, bridge_references = parse_bridge()
    components, provenance = build_components()
    artifacts = build_artifacts()
    surfaces = build_surfaces(artifacts)
    html_routes = build_html_routes(exercise_rows, reader_rows, bridge_rows, artifacts)
    relations = build_relations(
        components,
        provenance,
        exercise_rows,
        reader_rows,
        status_rows,
        bridge_rows,
        bridge_references,
        surfaces,
        html_routes,
        artifacts,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "companion_schema.json": json_bytes(build_schema()),
        "companion_components.jsonl": jsonl_bytes(components),
        "companion_provenance.jsonl": jsonl_bytes(provenance),
        "o001_mastery.jsonl": jsonl_bytes(exercise_rows + reader_rows),
        "o001_status.jsonl": jsonl_bytes(status_rows),
        "bridge_units.jsonl": jsonl_bytes(bridge_rows),
        "companion_surfaces.jsonl": jsonl_bytes(surfaces),
        "companion_html_routes.jsonl": jsonl_bytes(html_routes),
        "companion_relations.jsonl": jsonl_bytes(relations),
        "companion_artifacts.jsonl": jsonl_bytes(artifacts),
    }
    for name, raw in payloads.items():
        (output_dir / name).write_bytes(raw)
    (output_dir / "COMPANION_BACKEND_MANIFEST.csv").write_bytes(manifest_bytes(output_dir))
    return {
        "components": len(components),
        "provenance": len(provenance),
        "exercise_solutions": len(exercise_rows),
        "reader_work_solutions": len(reader_rows),
        "exercise_status_overlays": len(status_rows),
        "bridge_units": len(bridge_rows),
        "surfaces": len(surfaces),
        "html_routes": len(html_routes),
        "relations": len(relations),
        "artifacts": len(artifacts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=BACKEND)
    args = parser.parse_args()
    counts = write_outputs(args.output_dir.resolve())
    print(json.dumps(counts, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
