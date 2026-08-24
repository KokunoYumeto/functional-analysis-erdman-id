#!/usr/bin/env python3
"""Audit Chapter 1--17 text extraction and Poppler font inventory."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "qa" / "render-through-ch17-final"
PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-17.pdf"
TEXT = AUDIT_DIR / "functional-analysis-id-through-ch17-layout.txt"
FONTS = AUDIT_DIR / "functional-analysis-id-through-ch17-fonts.txt"
INFO = AUDIT_DIR / "functional-analysis-id-through-ch17-pdfinfo.txt"
RESULT = ROOT / "qa" / "CH17_TEXT_FONT_AUDIT.json"
EXPECTED_PAGES = 232
EXPECTED_PDF_BYTES = 2_432_395
EXPECTED_PDF_SHA256 = "22fda5f25205f2a442c2b907db015fb4c93cb46cfcba6a1fa8814449469073f1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if PDF.stat().st_size != EXPECTED_PDF_BYTES or sha256(PDF) != EXPECTED_PDF_SHA256:
        raise SystemExit("Chapter 17 PDF identity does not match the frozen audit target")
    subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(PDF), str(TEXT)],
        check=True,
    )
    font_result = subprocess.run(
        ["pdffonts", str(PDF)], check=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    FONTS.write_text(font_result.stdout, encoding="utf-8", newline="\n")
    info_result = subprocess.run(
        ["pdfinfo", str(PDF)], check=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    INFO.write_text(info_result.stdout, encoding="utf-8", newline="\n")

    raw = TEXT.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    font_lines = [line.rstrip() for line in FONTS.read_text(encoding="utf-8").splitlines()]
    data_lines = [line for line in font_lines[2:] if line.strip()]
    font_rows = []
    for line in data_lines:
        columns = re.split(r"\s+", line.strip())
        if len(columns) < 8:
            raise SystemExit(f"Unexpected pdffonts row: {line!r}")
        font_rows.append({
            "name": columns[0], "type": " ".join(columns[1:-6]),
            "encoding": columns[-6], "emb": columns[-5], "sub": columns[-4],
            "uni": columns[-3], "object": columns[-2], "generation": columns[-1],
        })

    mojibake_signatures = ["Ã", "Â", "â€", "ï¿½", "�"]
    local_path_patterns = [r"[A-Za-z]:\\", r"file:/+", r"Users[/\\][^/\\]+"]
    info_fields = {}
    for line in INFO.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info_fields[key.strip()] = value.strip()
    result = {
        "schema_version": "o008.ch17-text-font-audit.v1",
        "pdf": {"path": PDF.relative_to(ROOT).as_posix(), "bytes": PDF.stat().st_size,
                "sha256": sha256(PDF)},
        "text_file": TEXT.relative_to(ROOT).as_posix(), "text_bytes": len(raw),
        "text_sha256": sha256(TEXT), "form_feed_count": text.count("\f"),
        "expected_form_feed_count": EXPECTED_PAGES,
        "replacement_characters": text.count("\ufffd"),
        "mojibake_hits": {s: text.count(s) for s in mojibake_signatures if text.count(s)},
        "local_path_hits": {p: len(re.findall(p, text, flags=re.IGNORECASE))
                            for p in local_path_patterns if re.search(p, text, flags=re.IGNORECASE)},
        "font_file": FONTS.relative_to(ROOT).as_posix(),
        "font_file_bytes": FONTS.stat().st_size, "font_file_sha256": sha256(FONTS),
        "font_resources": len(font_rows),
        "embedded_yes": sum(row["emb"] == "yes" for row in font_rows),
        "subset_yes": sum(row["sub"] == "yes" for row in font_rows),
        "unicode_yes": sum(row["uni"] == "yes" for row in font_rows),
        "unicode_no_names": [row["name"] for row in font_rows if row["uni"] != "yes"],
        "pdfinfo_file": INFO.relative_to(ROOT).as_posix(),
        "pdfinfo_file_bytes": INFO.stat().st_size, "pdfinfo_file_sha256": sha256(INFO),
        "pdfinfo_pages": info_fields.get("Pages", ""),
        "pdfinfo_page_size": info_fields.get("Page size", ""),
        "pdfinfo_tagged": info_fields.get("Tagged", ""),
        "pdfinfo_encrypted": info_fields.get("Encrypted", ""),
        "pdfinfo_metadata_stream": info_fields.get("Metadata Stream", ""),
    }
    failures = []
    if result["form_feed_count"] != EXPECTED_PAGES:
        failures.append("form-feed count")
    if result["replacement_characters"] or result["mojibake_hits"] or result["local_path_hits"]:
        failures.append("text extraction residue")
    if result["font_resources"] != result["embedded_yes"]:
        failures.append("unembedded fonts")
    if result["font_resources"] != result["subset_yes"]:
        failures.append("non-subset fonts")
    if result["font_resources"] != result["unicode_yes"]:
        failures.append("fonts without Unicode maps")
    result["failures"] = failures
    result["status"] = "pass" if not failures else "fail"
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
