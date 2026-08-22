#!/usr/bin/env python3
"""Create compact public evidence from the complete private Chapter 9 render."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "qa" / "renders" / "ch09-final"
SOURCE_MANIFEST = RENDER_DIR / "RENDER_MANIFEST.csv"
PUBLIC_MANIFEST = ROOT / "provenance" / "CH09_RENDER_MANIFEST.csv"
CONTACT_SHEET = ROOT / "provenance" / "CH09_CONTACT_SHEET.png"

EXPECTED_PAGES = 140
COLS = 9
THUMB_SIZE = (204, 264)
LABEL_HEIGHT = 22
MARGIN = 20


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_number(path: Path) -> int:
    return int(path.stem.rsplit("-", 1)[1])


def main() -> None:
    pages = sorted(RENDER_DIR.glob("page-*.png"), key=page_number)
    if [page_number(path) for path in pages] != list(range(1, EXPECTED_PAGES + 1)):
        raise SystemExit("The private render is not the exact 140-page closure")

    PUBLIC_MANIFEST.write_bytes(SOURCE_MANIFEST.read_bytes())

    rows = math.ceil(EXPECTED_PAGES / COLS)
    cell_width = THUMB_SIZE[0]
    cell_height = THUMB_SIZE[1] + LABEL_HEIGHT
    sheet = Image.new(
        "RGB",
        (MARGIN * 2 + COLS * cell_width, MARGIN * 2 + rows * cell_height),
        "#d9d9d9",
    )
    draw = ImageDraw.Draw(sheet)
    for position, page_path in enumerate(pages):
        row, col = divmod(position, COLS)
        x = MARGIN + col * cell_width
        y = MARGIN + row * cell_height
        with Image.open(page_path) as source:
            thumb = ImageOps.contain(source.convert("RGB"), THUMB_SIZE)
        sheet.paste(
            thumb,
            (x + (cell_width - thumb.width) // 2, y + (THUMB_SIZE[1] - thumb.height) // 2),
        )
        draw.text((x + 3, y + THUMB_SIZE[1] + 4), f"{position + 1}", fill="black")
    sheet.save(CONTACT_SHEET, format="PNG", optimize=True)

    print(f"manifest_bytes={PUBLIC_MANIFEST.stat().st_size}")
    print(f"manifest_sha256={sha256(PUBLIC_MANIFEST)}")
    print(f"contact_bytes={CONTACT_SHEET.stat().st_size}")
    print(f"contact_sha256={sha256(CONTACT_SHEET)}")


if __name__ == "__main__":
    main()
