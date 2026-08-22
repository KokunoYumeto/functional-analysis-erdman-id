#!/usr/bin/env python3
"""Audit Poppler word boxes without trusting diagram control bytes as XML."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BBOX = ROOT / "qa" / "renders" / "ch06-final" / "functional-analysis-id-through-ch06-bbox.html"

PAGE_RE = re.compile(
    r'<page width="(?P<width>[0-9.]+)" height="(?P<height>[0-9.]+)">(?P<body>.*?)</page>',
    re.DOTALL,
)
WORD_RE = re.compile(
    r'<word xMin="(?P<x_min>-?[0-9.]+)" yMin="(?P<y_min>-?[0-9.]+)" '
    r'xMax="(?P<x_max>-?[0-9.]+)" yMax="(?P<y_max>-?[0-9.]+)">',
)


def main() -> None:
    raw = BBOX.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    pages = list(PAGE_RE.finditer(text))
    if len(pages) != 114:
        raise SystemExit(f"Expected 114 page records, found {len(pages)}")

    word_count = 0
    outside_count = 0
    zero_word_pages: list[int] = []
    minimum = {"left": float("inf"), "right": float("inf"), "top": float("inf"), "bottom": float("inf")}

    for page_number, page in enumerate(pages, start=1):
        width = float(page.group("width"))
        height = float(page.group("height"))
        words = list(WORD_RE.finditer(page.group("body")))
        if not words:
            zero_word_pages.append(page_number)
        for word in words:
            word_count += 1
            x_min = float(word.group("x_min"))
            y_min = float(word.group("y_min"))
            x_max = float(word.group("x_max"))
            y_max = float(word.group("y_max"))
            outside_count += int(x_min < 0 or y_min < 0 or x_max > width or y_max > height)
            minimum["left"] = min(minimum["left"], x_min)
            minimum["right"] = min(minimum["right"], width - x_max)
            minimum["top"] = min(minimum["top"], y_min)
            minimum["bottom"] = min(minimum["bottom"], height - y_max)

    print(json.dumps({
        "bbox_file": BBOX.relative_to(ROOT).as_posix(),
        "bbox_bytes": len(raw),
        "bbox_sha256": hashlib.sha256(raw).hexdigest(),
        "pages": len(pages),
        "word_boxes": word_count,
        "outside_page_boxes": outside_count,
        "minimum_clearance_points": {key: round(value, 6) for key, value in minimum.items()},
        "zero_word_pages": zero_word_pages,
        "replacement_decode_characters": text.count("\ufffd"),
    }, indent=2))


if __name__ == "__main__":
    main()
