#!/usr/bin/env python3
"""Inventory every complete-source render and create all-page contact sheets."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BUILD_RESULT = ROOT / "qa" / "COMPLETE_SOURCE_FINAL_BUILD_RESULT.json"
PDF = ROOT / "qa" / "build-complete-source-final" / "functional-analysis-id-complete-source.pdf"
RENDER = ROOT / "qa" / "render-complete-source-final"
MANIFEST = ROOT / "provenance" / "COMPLETE_SOURCE_RENDER_MANIFEST.csv"
SUMMARY = ROOT / "qa" / "COMPLETE_SOURCE_RENDER_AUDIT.json"
SHEETS = RENDER / "contact-sheets"
EXPECTED_SIZE = (935, 1210)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads(BUILD_RESULT.read_text(encoding="utf-8-sig"))
    expected_pages = int(result["pages"])
    expected_pdf_bytes = int(result["pdf"]["bytes"])
    expected_pdf_sha256 = str(result["pdf"]["sha256"])
    if PDF.stat().st_size != expected_pdf_bytes or sha256(PDF) != expected_pdf_sha256:
        raise SystemExit("final PDF identity differs")
    pages = sorted(RENDER.glob("pages/page-*.png"))
    if len(pages) != expected_pages:
        raise SystemExit(f"render count differs: {len(pages)}")
    if SHEETS.exists():
        raise SystemExit(f"fresh contact-sheet directory required: {SHEETS}")
    SHEETS.mkdir()

    rows: list[dict[str, object]] = []
    blank_pages: list[int] = []
    edge_ink_pages: list[int] = []
    font = ImageFont.load_default()
    for number, path in enumerate(pages, 1):
        with Image.open(path) as image:
            image.load()
            if image.size != EXPECTED_SIZE:
                raise SystemExit(f"page {number} size differs: {image.size}")
            gray = image.convert("L")
            mask = gray.point(lambda value: 255 if value < 245 else 0, mode="1")
            bbox = mask.getbbox()
            if bbox is None:
                blank_pages.append(number)
                left = top = right = bottom = None
                edge_ink = 0
            else:
                x0, y0, x1, y1 = bbox
                left, top = x0, y0
                right, bottom = image.width - x1, image.height - y1
                edge_mask = mask.convert("L")
                edge_regions = (
                    (0, 0, image.width, 5),
                    (0, image.height - 5, image.width, image.height),
                    (0, 5, 5, image.height - 5),
                    (image.width - 5, 5, image.width, image.height - 5),
                )
                edge_ink = sum(
                    edge_mask.crop(region).histogram()[255] for region in edge_regions
                )
                if edge_ink:
                    edge_ink_pages.append(number)
            rows.append(
                {
                    "page": number,
                    "file": path.name,
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "width_px": image.width,
                    "height_px": image.height,
                    "ink_left_px": left,
                    "ink_top_px": top,
                    "ink_right_px": right,
                    "ink_bottom_px": bottom,
                    "outer_5px_ink": edge_ink,
                }
            )

    with MANIFEST.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    sheet_records: list[dict[str, object]] = []
    per_sheet = 12
    thumb_size = (234, 303)
    cell_size = (254, 337)
    for start in range(0, len(pages), per_sheet):
        selected = pages[start : start + per_sheet]
        sheet = Image.new("RGB", (cell_size[0] * 4, cell_size[1] * 3), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, page_path in enumerate(selected):
            page_number = start + offset + 1
            with Image.open(page_path) as page:
                thumb = page.convert("RGB")
                thumb.thumbnail(thumb_size, Image.Resampling.LANCZOS)
                col, row = offset % 4, offset // 4
                x = col * cell_size[0] + (cell_size[0] - thumb.width) // 2
                y = row * cell_size[1] + 22
                sheet.paste(thumb, (x, y))
                draw.text(
                    (col * cell_size[0] + 7, row * cell_size[1] + 5),
                    f"Page {page_number}",
                    fill="black",
                    font=font,
                )
                draw.rectangle(
                    (x - 1, y - 1, x + thumb.width, y + thumb.height), outline="#777777"
                )
        first = start + 1
        last = start + len(selected)
        path = SHEETS / f"contact-{first:03d}-{last:03d}.png"
        sheet.save(path, format="PNG", optimize=True)
        sheet_records.append(
            {
                "file": path.name,
                "pages": [first, last],
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    nonblank = [row for row in rows if row["ink_left_px"] is not None]
    summary = {
        "schema_version": "o008.complete-source-render-audit.v1",
        "pdf": {
            "path": PDF.relative_to(ROOT).as_posix(),
            "bytes": PDF.stat().st_size,
            "sha256": sha256(PDF),
        },
        "page_count": len(rows),
        "render_dimensions_px": list(EXPECTED_SIZE),
        "aggregate_png_bytes": sum(int(row["bytes"]) for row in rows),
        "blank_pages": blank_pages,
        "outer_5px_ink_pages": edge_ink_pages,
        "minimum_nonblank_margins_px": {
            "left": min(int(row["ink_left_px"]) for row in nonblank),
            "top": min(int(row["ink_top_px"]) for row in nonblank),
            "right": min(int(row["ink_right_px"]) for row in nonblank),
            "bottom": min(int(row["ink_bottom_px"]) for row in nonblank),
        },
        "manifest": {
            "path": MANIFEST.relative_to(ROOT).as_posix(),
            "bytes": MANIFEST.stat().st_size,
            "sha256": sha256(MANIFEST),
        },
        "contact_sheets": sheet_records,
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
