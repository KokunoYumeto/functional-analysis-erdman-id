#!/usr/bin/env python3
"""Validate scope, stable IDs, rights, and structural closure of the O008 bridge."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bridge" / "id-ID" / "compact-spectral-svd.tex"
REPORT = ROOT / "qa" / "COMPACT_SPECTRAL_BRIDGE_VALIDATION.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
EXPECTED_IDS = [
    "O008-BRIDGE-CS-DEF-001",
    "O008-BRIDGE-CS-THM-001",
    "O008-BRIDGE-CS-REM-001",
    "O008-BRIDGE-CS-EXAM-001",
    "O008-BRIDGE-CS-LEM-001",
    "O008-BRIDGE-CS-LEM-002",
    "O008-BRIDGE-CS-THM-002",
    "O008-BRIDGE-CS-COR-001",
    "O008-BRIDGE-CS-DEF-002",
    "O008-BRIDGE-CS-THM-003",
    "O008-BRIDGE-CS-COR-002",
    "O008-BRIDGE-CS-PROP-001",
    "O008-BRIDGE-CS-EXAM-002",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    raw = SOURCE.read_bytes()
    text = raw.decode("utf-8")
    findings: list[dict[str, object]] = []
    if "\r" in text:
        findings.append({"code": "NON_LF_LINE_ENDINGS"})
    for required in (
        MODEL,
        "CC BY-SA 4.0",
        "bukan tulisan John M.",
        "tidak menyiratkan dukungan",
        "Konsekuensi spektral Riesz--Schauder",
        "Teorema spektral untuk operator kompak swaadjoin",
        "Dekomposisi nilai singular untuk operator kompak",
        "Pendekatan peringkat hingga terbaik",
        "Hubungan dengan dekomposisi polar",
        r"\ref{0040343}",
    ):
        if required not in text:
            findings.append({"code": "MISSING_REQUIRED_SURFACE", "required": required})
    ids = re.findall(r"^% O008-BRIDGE-ID: (\S+)$", text, flags=re.MULTILINE)
    if ids != EXPECTED_IDS:
        findings.append({"code": "STABLE_ID_ORDER", "expected": EXPECTED_IDS, "actual": ids})
    if len(ids) != len(set(ids)):
        findings.append({"code": "DUPLICATE_STABLE_ID"})
    labels = re.findall(r"\\label\{([^{}]+)\}", text)
    if len(labels) != len(set(labels)):
        findings.append({"code": "DUPLICATE_BRIDGE_LABEL"})
    bridge_labels = {label for label in labels if label.startswith("o008bridge:")}
    bridge_refs = {
        ref
        for ref in re.findall(r"\\(?:ref|eqref)\{([^{}]+)\}", text)
        if ref.startswith("o008bridge:")
    }
    if bridge_refs - bridge_labels:
        findings.append(
            {"code": "UNRESOLVED_BRIDGE_REFERENCE", "targets": sorted(bridge_refs - bridge_labels)}
        )
    for environment in ("defn", "thm", "lem", "rem", "exam", "cor", "prop", "proof"):
        opens = text.count(rf"\begin{{{environment}}}")
        closes = text.count(rf"\end{{{environment}}}")
        if opens != closes:
            findings.append(
                {"code": "UNBALANCED_ENVIRONMENT", "environment": environment, "opens": opens, "closes": closes}
            )
    for forbidden in (
        r"\begin{defn}\label{o008bridge:calkin",
        r"\begin{thm}[Teorema Atkinson]",
        r"\df{indeks Fredholm}",
    ):
        if forbidden in text:
            findings.append({"code": "CHAPTER15_DUPLICATION", "surface": forbidden})
    if re.search(r"(?i)\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b", text):
        findings.append({"code": "PLACEHOLDER_RESIDUE"})

    report = {
        "schema_version": "o008.compact-spectral-bridge-validation.v1",
        "result": "pass" if not findings else "fail",
        "source_path": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_bytes": len(raw),
        "source_sha256": sha256(raw),
        "stable_ids": ids,
        "stable_id_count": len(ids),
        "labels": len(labels),
        "bridge_internal_references": len(bridge_refs),
        "findings": findings,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(rendered, encoding="utf-8", newline="\n")
    if REPORT.read_text(encoding="utf-8") != rendered:
        raise RuntimeError("bridge validation report replay differs")
    print(rendered, end="")
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
