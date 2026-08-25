#!/usr/bin/env python3
"""Validate the bounded ten-result O001 learner-work proof layer."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "mastery" / "O001_READER_WORK_INVENTORY.jsonl"
SOURCE = ROOT / "mastery" / "id-ID" / "reader-work-selected.tex"
REPORT = ROOT / "qa" / "O001_READER_WORK_VALIDATION.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

BLOCK = re.compile(
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    rows = [json.loads(line) for line in INVENTORY.read_text(encoding="utf-8").splitlines()]
    text = SOURCE.read_text(encoding="utf-8")
    findings: list[dict[str, object]] = []
    if "\r" in text:
        findings.append({"code": "NON_LF_LINE_ENDINGS"})
    for required in (MODEL, "CC BY-SA 4.0", "bukan tulisan", "tidak menyiratkan dukungan"):
        if required not in text:
            findings.append({"code": "MISSING_PROVENANCE_OR_RIGHTS", "required": required})
    matches = list(BLOCK.finditer(text))
    if len(rows) != 10 or len(matches) != 10:
        findings.append(
            {"code": "COUNT_MISMATCH", "inventory": len(rows), "parsed": len(matches), "expected": 10}
        )
    parsed_ids: list[str] = []
    for index, (row, match) in enumerate(zip(rows, matches, strict=False), 1):
        value = match.groupdict()
        solution_id = value["solution"].strip()
        parsed_ids.append(solution_id)
        expected = {
            "solution": str(row["solution_id"]),
            "result_id": str(row["result_unit_id"]),
            "hint_id": str(row["upstream_hint_unit_id"]),
            "result_hash": str(row["result_target_fragment_sha256"]),
            "hint_hash": str(row["upstream_hint_target_fragment_sha256"]),
            "result": str(row["result_tex"]),
            "hint": str(row["upstream_hint_tex"]),
        }
        for field, expected_value in expected.items():
            actual = value[field].strip() if field.endswith("_id") or field == "solution" else value[field]
            if actual != expected_value:
                findings.append(
                    {
                        "code": "BOUND_FIELD_MISMATCH",
                        "record": index,
                        "solution_id": solution_id,
                        "field": field,
                        "expected_chars": len(expected_value),
                        "actual_chars": len(actual),
                    }
                )
        comment_pairs = {
            "comment_solution": expected["solution"],
            "comment_result": expected["result_id"],
            "comment_hint": expected["hint_id"],
            "comment_result_hash": expected["result_hash"],
            "comment_hint_hash": expected["hint_hash"],
        }
        for field, expected_value in comment_pairs.items():
            if value[field].strip() != expected_value:
                findings.append(
                    {"code": "COMMENT_ARGUMENT_MISMATCH", "solution_id": solution_id, "field": field}
                )
        if not value["answer"].strip() or not value["proof"].strip():
            findings.append({"code": "EMPTY_ANSWER_OR_PROOF", "solution_id": solution_id})
        if re.search(r"(?i)\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b", value["answer"] + value["proof"]):
            findings.append({"code": "PLACEHOLDER_RESIDUE", "solution_id": solution_id})

    expected_ids = [str(row["solution_id"]) for row in rows]
    if parsed_ids != expected_ids:
        findings.append({"code": "ORDER_MISMATCH", "expected": expected_ids, "actual": parsed_ids})
    for environment in (
        "o001readerwork",
        "o001result",
        "o001sourcehint",
        "o001answer",
        "o001proof",
    ):
        if text.count(rf"\begin{{{environment}}}") != text.count(rf"\end{{{environment}}}"):
            findings.append({"code": "UNBALANCED_ENVIRONMENT", "environment": environment})

    raw = SOURCE.read_bytes()
    report = {
        "schema_version": "o008.o001-reader-work-validation.v1",
        "result": "pass" if not findings else "fail",
        "inventory_path": str(INVENTORY.relative_to(ROOT)).replace("\\", "/"),
        "inventory_bytes": INVENTORY.stat().st_size,
        "inventory_sha256": sha256(INVENTORY.read_bytes()),
        "source_path": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_bytes": len(raw),
        "source_sha256": sha256(raw),
        "expected_records": len(rows),
        "parsed_records": len(matches),
        "findings": findings,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(rendered, encoding="utf-8", newline="\n")
    if REPORT.read_text(encoding="utf-8") != rendered:
        raise RuntimeError("reader-work validation report replay differs")
    print(rendered, end="")
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
