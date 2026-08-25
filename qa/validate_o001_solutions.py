#!/usr/bin/env python3
"""Validate the complete, separately provenanced O001 exercise-solution layer."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "mastery" / "O001_EXERCISE_INVENTORY.jsonl"
SOLUTION_DIR = ROOT / "mastery" / "id-ID"
REPORT = ROOT / "qa" / "O001_SOLUTION_VALIDATION.json"
EXPECTED_CHAPTER_COUNTS = {
    "CH01": 6,
    "CH03": 7,
    "CH04": 10,
    "CH05": 4,
    "CH06": 6,
    "CH07": 1,
    "CH08": 2,
    "CH09": 1,
    "CH10": 11,
    "CH13": 1,
    "CH14": 2,
    "CH17": 1,
}
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

SOLUTION_BLOCK = re.compile(
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_inventory() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(
        INVENTORY.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line:
            raise RuntimeError(f"blank inventory row at line {line_number}")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"non-object inventory row at line {line_number}")
        rows.append(value)
    return rows


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


def fail(findings: list[dict[str, object]], code: str, **evidence: object) -> None:
    findings.append({"code": code, **evidence})


def main() -> None:
    inventory = read_inventory()
    findings: list[dict[str, object]] = []
    expected_by_id = {str(row["solution_id"]): row for row in inventory}
    if len(inventory) != 52:
        fail(findings, "INVENTORY_COUNT", expected=52, actual=len(inventory))
    if len(expected_by_id) != len(inventory):
        fail(findings, "INVENTORY_DUPLICATE_SOLUTION_ID")

    expected_distribution = Counter(
        str(row["chapter_id"]).rsplit("-", 1)[-1] for row in inventory
    )
    if dict(expected_distribution) != EXPECTED_CHAPTER_COUNTS:
        fail(
            findings,
            "INVENTORY_CHAPTER_DISTRIBUTION",
            expected=EXPECTED_CHAPTER_COUNTS,
            actual=dict(expected_distribution),
        )

    parsed: dict[str, dict[str, object]] = {}
    file_inventory: list[dict[str, object]] = []
    for chapter, expected_count in EXPECTED_CHAPTER_COUNTS.items():
        path = SOLUTION_DIR / f"solutions-ch{chapter[2:]}.tex"
        if not path.is_file():
            fail(findings, "MISSING_SOLUTION_FILE", path=str(path.relative_to(ROOT)))
            continue
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            fail(
                findings,
                "NON_UTF8_SOLUTION_FILE",
                path=str(path.relative_to(ROOT)),
                error=str(exc),
            )
            continue
        if "\r" in text:
            fail(findings, "NON_LF_LINE_ENDINGS", path=str(path.relative_to(ROOT)))
        for required in (MODEL, "CC BY-SA 4.0", "bukan tulisan", "tidak menyiratkan dukungan"):
            if required not in text:
                fail(
                    findings,
                    "MISSING_VISIBLE_PROVENANCE_OR_RIGHTS",
                    path=str(path.relative_to(ROOT)),
                    required=required,
                )
        matches = list(SOLUTION_BLOCK.finditer(text))
        if len(matches) != expected_count:
            fail(
                findings,
                "FILE_SOLUTION_COUNT",
                path=str(path.relative_to(ROOT)),
                expected=expected_count,
                actual=len(matches),
            )
        if text.count(r"\begin{o001solution}") != text.count(r"\end{o001solution}"):
            fail(findings, "UNBALANCED_SOLUTION_ENVIRONMENT", path=str(path.relative_to(ROOT)))
        for environment in ("o001statement", "o001answer", "o001proof"):
            if text.count(rf"\begin{{{environment}}}") != text.count(
                rf"\end{{{environment}}}"
            ):
                fail(
                    findings,
                    "UNBALANCED_INNER_ENVIRONMENT",
                    path=str(path.relative_to(ROOT)),
                    environment=environment,
                )

        file_ids: list[str] = []
        for match in matches:
            values = match.groupdict()
            solution_id = values["solution"].strip()
            file_ids.append(solution_id)
            if solution_id in parsed:
                fail(findings, "DUPLICATE_SOLUTION", solution_id=solution_id)
                continue
            parsed[solution_id] = {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "exercise_id": values["exercise"].strip(),
                "statement_hash": values["hash"],
                "statement": values["statement"],
                "answer": values["answer"],
                "proof": values["proof"],
            }
            for field, actual in (
                ("comment_solution", values["comment_solution"].strip()),
                ("comment_exercise", values["comment_exercise"].strip()),
                ("comment_hash", values["comment_hash"]),
            ):
                expected = {
                    "comment_solution": solution_id,
                    "comment_exercise": values["exercise"].strip(),
                    "comment_hash": values["hash"],
                }[field]
                if actual != expected:
                    fail(
                        findings,
                        "COMMENT_ARGUMENT_MISMATCH",
                        solution_id=solution_id,
                        field=field,
                        expected=expected,
                        actual=actual,
                    )
            if not values["answer"].strip() or not values["proof"].strip():
                fail(findings, "EMPTY_ANSWER_OR_PROOF", solution_id=solution_id)
            if re.search(r"(?i)\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b", values["answer"] + values["proof"]):
                fail(findings, "PLACEHOLDER_RESIDUE", solution_id=solution_id)

        expected_file_ids = [
            str(row["solution_id"])
            for row in inventory
            if str(row["chapter_id"]).endswith(chapter)
        ]
        if file_ids != expected_file_ids:
            fail(
                findings,
                "SOURCE_ORDER_MISMATCH",
                path=str(path.relative_to(ROOT)),
                expected=expected_file_ids,
                actual=file_ids,
            )
        file_inventory.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": len(raw),
                "sha256": sha256(raw),
                "solution_records": len(matches),
            }
        )

    for solution_id, row in expected_by_id.items():
        actual = parsed.get(solution_id)
        if actual is None:
            fail(findings, "MISSING_SOLUTION", solution_id=solution_id)
            continue
        expected_exercise = str(row["exercise_unit_id"])
        expected_hash = str(row["statement_target_fragment_sha256"])
        expected_statement = statement_body(str(row["statement_tex"]))
        if actual["exercise_id"] != expected_exercise:
            fail(
                findings,
                "EXERCISE_ID_MISMATCH",
                solution_id=solution_id,
                expected=expected_exercise,
                actual=actual["exercise_id"],
            )
        if actual["statement_hash"] != expected_hash:
            fail(
                findings,
                "STATEMENT_HASH_ARGUMENT_MISMATCH",
                solution_id=solution_id,
                expected=expected_hash,
                actual=actual["statement_hash"],
            )
        if actual["statement"] != expected_statement:
            fail(
                findings,
                "STATEMENT_COPY_MISMATCH",
                solution_id=solution_id,
                expected_chars=len(expected_statement),
                actual_chars=len(str(actual["statement"])),
            )

    extras = sorted(set(parsed) - set(expected_by_id))
    for solution_id in extras:
        fail(findings, "UNEXPECTED_SOLUTION", solution_id=solution_id)

    report = {
        "schema_version": "o008.o001-solution-validation.v1",
        "result": "pass" if not findings else "fail",
        "inventory_path": str(INVENTORY.relative_to(ROOT)).replace("\\", "/"),
        "inventory_bytes": INVENTORY.stat().st_size,
        "inventory_sha256": sha256(INVENTORY.read_bytes()),
        "expected_solutions": len(inventory),
        "parsed_solutions": len(parsed),
        "chapter_counts": EXPECTED_CHAPTER_COUNTS,
        "solution_files": file_inventory,
        "findings": findings,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(rendered, encoding="utf-8", newline="\n")
    replay = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if REPORT.read_text(encoding="utf-8") != replay:
        raise RuntimeError("validation report deterministic replay differs")
    print(rendered, end="")
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
