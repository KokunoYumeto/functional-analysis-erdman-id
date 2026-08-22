#!/usr/bin/env python3
"""Inventory and contact-sheet the frozen cumulative Chapter 1--8 render."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-bab-1-8.pdf"
RENDER_DIR = ROOT / "qa" / "renders" / "ch08-final"
CONTACT_DIR = RENDER_DIR / "contact-sheets"
MANIFEST_JSON = RENDER_DIR / "RENDER_MANIFEST.json"
MANIFEST_CSV = RENDER_DIR / "RENDER_MANIFEST.csv"

EXPECTED_PDF_BYTES = 1_593_249
EXPECTED_PDF_SHA256 = "fb6488691e2127bc0b8e3f94f38033eb3bdbe0c61efedc66c07de8f3b3444fbd"
EXPECTED_PAGES = 129
EXPECTED_DIMENSIONS = (1275, 1650)
THUMB_SIZE = (306, 396)
GRID = (3, 4)
LABEL_HEIGHT = 28
SHEET_MARGIN = 24
PAGE_RE = re.compile(r"page-(\d+)\.png\Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_number(path: Path) -> int:
    match = PAGE_RE.fullmatch(path.name)
    if not match:
        raise ValueError(f"Unexpected render filename: {path.name}")
    return int(match.group(1))


def inspect_page(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        image.load()
        width, height = image.size
        if (width, height) != EXPECTED_DIMENSIONS:
            raise SystemExit(f"Unexpected dimensions for {path.name}: {(width, height)}")
        gray = ImageOps.grayscale(image)
        ink = gray.point(lambda value: 255 if value < 245 else 0)
        bbox = ink.getbbox()
        ink_pixels = ink.histogram()[255]
        edge_width = 5
        edge_ink = sum(
            region.histogram()[255]
            for region in (
                ink.crop((0, 0, width, edge_width)),
                ink.crop((0, height - edge_width, width, height)),
                ink.crop((0, 0, edge_width, height)),
                ink.crop((width - edge_width, 0, width, height)),
            )
        )
        margins = None
        if bbox:
            margins = {
                "left": bbox[0],
                "top": bbox[1],
                "right": width - bbox[2],
                "bottom": height - bbox[3],
            }
        return {
            "page": page_number(path),
            "file": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "width_px": width,
            "height_px": height,
            "ink_pixels_lt245": ink_pixels,
            "ink_fraction": round(ink_pixels / (width * height), 8),
            "ink_bbox": list(bbox) if bbox else None,
            "margins_px": margins,
            "edge_ink_pixels_5px": edge_ink,
        }


def make_contact_sheets(pages: list[Path]) -> list[dict[str, object]]:
    CONTACT_DIR.mkdir(parents=True, exist_ok=True)
    cols, rows = GRID
    cell_width = THUMB_SIZE[0]
    cell_height = THUMB_SIZE[1] + LABEL_HEIGHT
    sheet_size = (
        SHEET_MARGIN * 2 + cols * cell_width,
        SHEET_MARGIN * 2 + rows * cell_height,
    )
    records: list[dict[str, object]] = []
    batch_size = cols * rows
    for batch_index, start in enumerate(range(0, len(pages), batch_size), 1):
        batch = pages[start : start + batch_size]
        sheet = Image.new("RGB", sheet_size, "#d9d9d9")
        draw = ImageDraw.Draw(sheet)
        for position, page_path in enumerate(batch):
            row, col = divmod(position, cols)
            x = SHEET_MARGIN + col * cell_width
            y = SHEET_MARGIN + row * cell_height
            with Image.open(page_path) as page_image:
                thumb = ImageOps.contain(page_image.convert("RGB"), THUMB_SIZE)
            paste_x = x + (cell_width - thumb.width) // 2
            paste_y = y + (THUMB_SIZE[1] - thumb.height) // 2
            sheet.paste(thumb, (paste_x, paste_y))
            draw.text(
                (x + 4, y + THUMB_SIZE[1] + 6),
                f"Page {page_number(page_path)}",
                fill="black",
            )
        first_page = page_number(batch[0])
        last_page = page_number(batch[-1])
        output = CONTACT_DIR / f"contact-{batch_index:02d}-pages-{first_page:03d}-{last_page:03d}.png"
        sheet.save(output, format="PNG", optimize=True)
        records.append(
            {
                "file": output.relative_to(ROOT).as_posix(),
                "first_page": first_page,
                "last_page": last_page,
                "bytes": output.stat().st_size,
                "sha256": sha256(output),
            }
        )
    return records


def main() -> None:
    if PDF.stat().st_size != EXPECTED_PDF_BYTES or sha256(PDF) != EXPECTED_PDF_SHA256:
        raise SystemExit("Chapter 8 PDF identity does not match the frozen audit target")

    pages = sorted(RENDER_DIR.glob("page-*.png"), key=page_number)
    actual_numbers = [page_number(path) for path in pages]
    expected_numbers = list(range(1, EXPECTED_PAGES + 1))
    if actual_numbers != expected_numbers:
        raise SystemExit(
            f"Render closure failed: expected pages 1..{EXPECTED_PAGES}; got {actual_numbers}"
        )

    page_records = [inspect_page(path) for path in pages]
    dimensions = sorted({(row["width_px"], row["height_px"]) for row in page_records})
    edge_pages = [row["page"] for row in page_records if row["edge_ink_pixels_5px"]]
    blank_candidates = [row["page"] for row in page_records if row["ink_fraction"] < 0.0005]
    contacts = make_contact_sheets(pages)

    manifest = {
        "schema_version": "o008-render-manifest-1.0.0",
        "source_pdf": PDF.relative_to(ROOT).as_posix(),
        "source_pdf_bytes": PDF.stat().st_size,
        "source_pdf_sha256": sha256(PDF),
        "renderer": "Poppler pdftoppm -png -r 150 -cropbox",
        "expected_pages": EXPECTED_PAGES,
        "rendered_pages": len(page_records),
        "dimensions_px": [list(item) for item in dimensions],
        "edge_ink_pages_5px": edge_pages,
        "blank_page_candidates": blank_candidates,
        "total_page_png_bytes": sum(int(row["bytes"]) for row in page_records),
        "pages": page_records,
        "contact_sheets": contacts,
    }
    MANIFEST_JSON.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    fieldnames = list(page_records[0])
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in page_records:
            csv_row = dict(row)
            csv_row["ink_bbox"] = json.dumps(csv_row["ink_bbox"], separators=(",", ":"))
            csv_row["margins_px"] = json.dumps(csv_row["margins_px"], separators=(",", ":"))
            writer.writerow(csv_row)

    print(
        json.dumps(
            {
                "pages": len(page_records),
                "dimensions_px": manifest["dimensions_px"],
                "edge_ink_pages_5px": edge_pages,
                "blank_page_candidates": blank_candidates,
                "page_png_bytes": manifest["total_page_png_bytes"],
                "contact_sheets": len(contacts),
                "manifest_json_bytes": MANIFEST_JSON.stat().st_size,
                "manifest_json_sha256": sha256(MANIFEST_JSON),
                "manifest_csv_bytes": MANIFEST_CSV.stat().st_size,
                "manifest_csv_sha256": sha256(MANIFEST_CSV),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
