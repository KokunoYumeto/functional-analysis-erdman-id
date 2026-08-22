#!/usr/bin/env python3
"""Audit Chapter 1--7 text extraction and Poppler font inventory."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "qa" / "renders" / "ch07-final"
PDF = ROOT / "qa" / "build-through-ch07-a" / "functional-analysis-id-through-ch07.pdf"
TEXT = RENDER_DIR / "functional-analysis-id-through-ch07-layout.txt"
FONTS = RENDER_DIR / "functional-analysis-id-through-ch07-fonts.txt"
INFO = RENDER_DIR / "functional-analysis-id-through-ch07-pdfinfo.txt"
EXPECTED_PAGES = 121
EXPECTED_PDF_BYTES = 1_530_677
EXPECTED_PDF_SHA256 = "a7ddaef324bd356d258cb47195f524e027ba54a696cb8d38a8358bb8d0a2d7ff"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if PDF.stat().st_size != EXPECTED_PDF_BYTES or sha256(PDF) != EXPECTED_PDF_SHA256:
        raise SystemExit("Chapter 7 PDF identity does not match the frozen audit target")
    subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(PDF), str(TEXT)],
        check=True,
    )
    font_result = subprocess.run(
        ["pdffonts", str(PDF)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    FONTS.write_text(font_result.stdout, encoding="utf-8", newline="\n")
    info_result = subprocess.run(
        ["pdfinfo", str(PDF)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
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
        font_rows.append(
            {
                "name": columns[0],
                "type": " ".join(columns[1:-6]),
                "encoding": columns[-6],
                "emb": columns[-5],
                "sub": columns[-4],
                "uni": columns[-3],
                "object": columns[-2],
                "generation": columns[-1],
            }
        )

    mojibake_signatures = ["Ã", "Â", "â€", "ï¿½", "�"]
    local_path_patterns = [r"[A-Za-z]:\\", r"file:/+", r"Users[/\\]Floris"]
    info_fields = {}
    for line in INFO.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info_fields[key.strip()] = value.strip()
    result = {
        "text_file": TEXT.relative_to(ROOT).as_posix(),
        "text_bytes": len(raw),
        "text_sha256": sha256(TEXT),
        "form_feed_count": text.count("\f"),
        "expected_form_feed_count": EXPECTED_PAGES,
        "replacement_characters": text.count("\ufffd"),
        "mojibake_hits": {
            signature: text.count(signature)
            for signature in mojibake_signatures
            if text.count(signature)
        },
        "local_path_hits": {
            pattern: len(re.findall(pattern, text, flags=re.IGNORECASE))
            for pattern in local_path_patterns
            if re.search(pattern, text, flags=re.IGNORECASE)
        },
        "font_file": FONTS.relative_to(ROOT).as_posix(),
        "font_file_bytes": FONTS.stat().st_size,
        "font_file_sha256": sha256(FONTS),
        "font_resources": len(font_rows),
        "embedded_yes": sum(row["emb"] == "yes" for row in font_rows),
        "subset_yes": sum(row["sub"] == "yes" for row in font_rows),
        "unicode_yes": sum(row["uni"] == "yes" for row in font_rows),
        "unicode_no_names": [row["name"] for row in font_rows if row["uni"] != "yes"],
        "pdfinfo_file": INFO.relative_to(ROOT).as_posix(),
        "pdfinfo_file_bytes": INFO.stat().st_size,
        "pdfinfo_file_sha256": sha256(INFO),
        "pdfinfo_pages": info_fields.get("Pages", ""),
        "pdfinfo_page_size": info_fields.get("Page size", ""),
        "pdfinfo_tagged": info_fields.get("Tagged", ""),
        "pdfinfo_encrypted": info_fields.get("Encrypted", ""),
        "pdfinfo_metadata_stream": info_fields.get("Metadata Stream", ""),
    }
    if result["form_feed_count"] != EXPECTED_PAGES:
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
