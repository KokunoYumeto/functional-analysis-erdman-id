#!/usr/bin/env python3
"""Build the additive semantic HTML companion for the id-ID FAOA reader.

This builder never mutates ``output/html``.  It converts the separately
provenanced O001 solution/mastery components and the O008 compact-spectral/SVD
bridge to native MathML, binds their stable IDs, and emits a self-contained
static companion tree beside the admitted source reader.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Iterable

from lxml import etree, html

from build_reader import (
    LICENSE_URL,
    MODEL,
    ROOT,
    SOURCE_DATE_EPOCH,
    CSS_SOURCE,
    extract_article,
    normalize_legacy_tex,
    normalize_math,
    pandoc_macro_prelude,
    qualify_external_links,
    relative_href,
    run_pandoc,
    safe_reset,
    sha256_bytes,
    sha256_file,
    stable_json,
    visible_text,
    write_manifest,
    write_text,
)


SOURCE_READER = ROOT / "output" / "html"
SOURCE_ROUTE_MAP = ROOT / "backend" / "html_routes.jsonl"
COMPANION_CSS = ROOT / "html" / "static" / "companion.css"
EXPECTED_SOURCE_READER_INVENTORY = "f04bb3f5ee883c794474b191faf0e724987ebc01c4711bac8f6dc5421e543f32"

CHAPTERS: list[tuple[int, str]] = [
    (1, "Aljabar Linear dan Teorema Spektral"),
    (3, "Ruang Linear Bernorma"),
    (4, "Ruang Hilbert"),
    (5, "Operator pada Ruang Hilbert"),
    (6, "Ruang Banach"),
    (7, "Operator Kompak"),
    (8, "Beberapa Teori Spektral"),
    (9, "Ruang Vektor Topologis"),
    (10, "Distribusi"),
    (13, "Konstruksi Gelfand–Naimark–Segal"),
    (14, "Aljabar Pengali"),
    (17, "Funktor K0"),
]

ROUTES: list[dict[str, Any]] = [
    {
        "slug": "jembatan-spektral-kompak-svd",
        "title": "Jembatan spektral-kompak dan SVD",
        "route_id": "O008-BRIDGE-CS-CHAPTER",
        "kind": "bridge",
        "path": ROOT / "bridge" / "id-ID" / "compact-spectral-svd.tex",
    },
    {
        "slug": "hasil-kerja-pembaca",
        "title": "Hasil kerja-pembaca terpilih",
        "route_id": "O001-FAOA-2015-READER-WORK-SELECTED",
        "kind": "reader_work",
        "path": ROOT / "mastery" / "id-ID" / "reader-work-selected.tex",
    },
]
for chapter, title in CHAPTERS:
    ROUTES.append(
        {
            "slug": f"solusi-bab-{chapter:02d}",
            "title": f"Solusi Bab {chapter}: {title}",
            "route_id": f"O001-FAOA-2015-CH{chapter:02d}-SOLUTIONS",
            "kind": "solutions",
            "chapter": chapter,
            "path": ROOT / "mastery" / "id-ID" / f"solutions-ch{chapter:02d}.tex",
        }
    )

GENERIC_KINDS = ("defn", "thm", "rem", "exam", "lem", "cor", "prop", "proof")
GENERIC_LABELS = {
    "defn": "Definisi",
    "thm": "Teorema",
    "rem": "Catatan",
    "exam": "Contoh",
    "lem": "Lema",
    "cor": "Akibat",
    "prop": "Proposisi",
    "proof": "Bukti",
}
GENERIC_BEGIN_RE = re.compile(
    r"\\begin\{(?P<kind>" + "|".join(GENERIC_KINDS) + r")\}(?:\[(?P<title>[^\]]*)\])?"
)
BRIDGE_ID_RE = re.compile(r"(?m)^% O008-BRIDGE-ID: (O008-BRIDGE-CS-[A-Z]+-[0-9]{3})\s*$")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def source_reader_inventory() -> str:
    manifest = SOURCE_READER / "MANIFEST.csv"
    rows = list(csv.DictReader(manifest.open(encoding="utf-8", newline="")))
    material: list[str] = []
    for row in rows:
        path = SOURCE_READER / row["path"]
        size = path.stat().st_size
        digest = sha256_file(path)
        if size != int(row["bytes"]) or digest != row["sha256"]:
            raise RuntimeError(f"admitted source-reader manifest mismatch: {row['path']}")
        material.append(f"{row['path']}\0{size}\0{digest}\n")
    return sha256_bytes("".join(material).encode("utf-8"))


def plain_tex(value: str | None) -> str:
    if not value:
        return ""
    text = value
    for command in ("emph", "textit", "textbf", "rm"):
        text = re.sub(rf"\\{command}\{{([^{{}}]*)\}}", r"\1", text)
    replacements = {
        r"\'e": "é",
        r"\`a": "à",
        r"\`A": "À",
        "--": "–",
        "~": " ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"\\[a-zA-Z]+\s*", "", text)
    return " ".join(text.split())


def transform_generic_environments(text: str) -> tuple[str, list[dict[str, str]]]:
    specs: list[dict[str, str]] = []

    def replace_begin(match: re.Match[str]) -> str:
        kind = match.group("kind")
        specs.append({"kind": kind, "title": plain_tex(match.group("title"))})
        return rf"\begin{{companion{kind}}}"

    transformed = GENERIC_BEGIN_RE.sub(replace_begin, text)
    for kind in GENERIC_KINDS:
        transformed = transformed.replace(rf"\end{{{kind}}}", rf"\end{{companion{kind}}}")
    return transformed, specs


def shadow_document(source: str) -> tuple[str, list[dict[str, str]]]:
    transformed, specs = transform_generic_environments(source)
    transformed = re.sub(
        r"\\\[\s*\\xy(?=[\s\S]*?\\qtriangle)[\s\S]*?\\endxy\s*\\\]",
        r"\\textbf{[[COMPANION-DIAGRAM:O001-FAOA-2015-CH04-EX-010-STATEMENT-DIAGRAM-001]]}",
        transformed,
    )
    transformed = normalize_legacy_tex(transformed)
    transformed = re.sub(r"\\hbox\{([^{}]*)\}", r"\\text{\1}", transformed)
    return (
        "\n".join(
            [
                r"\documentclass{amsbook}",
                pandoc_macro_prelude(),
                r"\begin{document}",
                transformed,
                r"\end{document}",
                "",
            ]
        ),
        specs,
    )


def remove_generated_title(article: etree._Element) -> None:
    candidates = article.xpath("./h1 | ./h2")
    if candidates:
        candidates[0].getparent().remove(candidates[0])


def install_page_title(article: etree._Element, route: dict[str, Any]) -> None:
    title = html.Element("h1", {"id": route["route_id"]})
    title.text = route["title"]
    article.insert(0, title)


def generic_nodes(article: etree._Element) -> list[etree._Element]:
    names = {f"companion{kind}" for kind in GENERIC_KINDS}
    return [
        node
        for node in article.xpath(".//div")
        if names.intersection((node.get("class") or "").split())
    ]


def decorate_generic_environments(
    article: etree._Element,
    specs: list[dict[str, str]],
    heading_level: int,
) -> list[etree._Element]:
    nodes = generic_nodes(article)
    if len(nodes) != len(specs):
        raise RuntimeError(f"generic environment closure mismatch: DOM={len(nodes)} source={len(specs)}")
    for node, spec in zip(nodes, specs):
        kind = spec["kind"]
        classes = set((node.get("class") or "").split())
        classes.update({kind, "companion-environment"})
        node.set("class", " ".join(sorted(classes)))
        heading = html.Element(f"h{heading_level}", {"class": "block-heading"})
        heading.text = GENERIC_LABELS[kind]
        if spec["title"]:
            heading.text += f": {spec['title']}"
        node.insert(0, heading)
    return nodes


def first_argument_paragraph(node: etree._Element, expected: int) -> list[str]:
    if not len(node) or node[0].tag != "p":
        raise RuntimeError("component argument paragraph is missing")
    paragraph = node[0]
    spans = paragraph.xpath("./span")
    values = [visible_text(span) for span in spans]
    if len(values) != expected or any(not value for value in values):
        raise RuntimeError(f"component argument closure mismatch: expected {expected}, got {values}")
    node.remove(paragraph)
    return values


def append_link(paragraph: etree._Element, prefix: str, text: str, href: str) -> etree._Element:
    if len(paragraph):
        paragraph[-1].tail = (paragraph[-1].tail or "") + prefix
    else:
        paragraph.text = (paragraph.text or "") + prefix
    link = html.Element("a", {"href": href, "class": "source-reader-link"})
    link.text = text
    paragraph.append(link)
    return link


def source_href(current_slug: str, source_route_href: str) -> str:
    prefix = "../../html/" if current_slug else "../html/"
    return prefix + source_route_href


def provenance_details(rows: Iterable[tuple[str, str]]) -> etree._Element:
    details = html.Element("details", {"class": "provenance-details"})
    summary = html.Element("summary")
    summary.text = "Identitas dan ikatan provenans"
    details.append(summary)
    listing = html.Element("dl")
    for key, value in rows:
        term = html.Element("dt")
        term.text = key
        definition = html.Element("dd")
        code = html.Element("code")
        code.text = value
        definition.append(code)
        listing.extend([term, definition])
    details.append(listing)
    return details


def add_block_heading(node: etree._Element, stable_id: str, title: str, css_class: str) -> str:
    block_id = f"{stable_id}-{css_class.upper()}"
    node.set("id", block_id)
    classes = set((node.get("class") or "").split())
    classes.add(css_class)
    node.set("class", " ".join(sorted(classes)))
    heading = html.Element("h3", {"id": f"{block_id}-TITLE", "class": "block-heading"})
    heading.text = title
    node.set("role", "region")
    node.set("aria-labelledby", heading.get("id"))
    node.insert(0, heading)
    return block_id


def process_solutions(
    article: etree._Element,
    route: dict[str, Any],
    source_routes: dict[str, str],
) -> tuple[list[str], int]:
    solution_nodes = article.xpath(".//div[contains(concat(' ', normalize-space(@class), ' '), ' o001solution ')]")
    stable_ids = [route["route_id"]]
    for order, node in enumerate(solution_nodes, start=1):
        solution_id, source_id, statement_hash = first_argument_paragraph(node, 3)
        expected_prefix = f"O001-FAOA-2015-CH{route['chapter']:02d}-EX-"
        if not solution_id.startswith(expected_prefix) or source_id not in source_routes:
            raise RuntimeError(f"invalid solution binding: {solution_id} -> {source_id}")
        node.set("id", solution_id)
        node.set("data-component-kind", "o001-solution")
        node.set("data-source-exercise-id", source_id)
        node.set("data-statement-target-sha256", statement_hash)
        node.set("data-license", "CC BY-SA 4.0")
        node.set("data-provenance", "separately-authored-not-Erdman")
        heading = html.Element("h2", {"id": f"{solution_id}-TITLE", "class": "component-heading"})
        heading.text = f"Solusi {order}"
        node.set("aria-labelledby", heading.get("id"))
        meta = html.Element("p", {"class": "component-meta"})
        meta.text = "Terhubung ke "
        append_link(meta, "", "latihan pada reader teks sumber", source_href(route["slug"], source_routes[source_id]))
        meta[-1].tail = ". Solusi ini merupakan komponen asli terpisah."
        details = provenance_details(
            [
                ("ID solusi", solution_id),
                ("ID latihan sumber", source_id),
                ("SHA-256 pernyataan terjemahan", statement_hash),
            ]
        )
        for index, item in enumerate((heading, meta, details)):
            node.insert(index, item)
        blocks = {
            "o001statement": ("Pernyataan latihan sumber", "statement"),
            "o001answer": ("Jawaban ringkas", "answer"),
            "o001proof": ("Penyelesaian lengkap", "proof"),
        }
        for class_name, (title, suffix) in blocks.items():
            matches = node.xpath(f".//div[contains(concat(' ', normalize-space(@class), ' '), ' {class_name} ')]")
            if len(matches) != 1:
                raise RuntimeError(f"{solution_id}: expected one {class_name}, got {len(matches)}")
            stable_ids.append(add_block_heading(matches[0], solution_id, title, suffix))
        stable_ids.append(solution_id)
    return stable_ids, len(solution_nodes)


def process_reader_work(
    article: etree._Element,
    route: dict[str, Any],
    source_routes: dict[str, str],
) -> tuple[list[str], int]:
    nodes = article.xpath(".//div[contains(concat(' ', normalize-space(@class), ' '), ' o001readerwork ')]")
    stable_ids = [route["route_id"]]
    for order, node in enumerate(nodes, start=1):
        solution_id, result_id, hint_id, result_hash, hint_hash = first_argument_paragraph(node, 5)
        if result_id not in source_routes or hint_id not in source_routes:
            raise RuntimeError(f"reader-work source binding is absent: {solution_id}")
        node.set("id", solution_id)
        node.set("data-component-kind", "o001-reader-work")
        node.set("data-source-result-id", result_id)
        node.set("data-source-hint-id", hint_id)
        node.set("data-license", "CC BY-SA 4.0")
        node.set("data-provenance", "separately-authored-not-Erdman")
        heading = html.Element("h2", {"id": f"{solution_id}-TITLE", "class": "component-heading"})
        heading.text = f"Hasil kerja-pembaca {order}"
        node.set("aria-labelledby", heading.get("id"))
        meta = html.Element("p", {"class": "component-meta"})
        meta.text = "Baca "
        append_link(meta, "", "hasil sumber", source_href(route["slug"], source_routes[result_id]))
        append_link(meta, " dan ", "petunjuk sumber", source_href(route["slug"], source_routes[hint_id]))
        meta[-1].tail = ". Bukti lengkap di sini merupakan komponen asli terpisah."
        details = provenance_details(
            [
                ("ID solusi", solution_id),
                ("ID hasil sumber", result_id),
                ("ID petunjuk sumber", hint_id),
                ("SHA-256 hasil terjemahan", result_hash),
                ("SHA-256 petunjuk terjemahan", hint_hash),
            ]
        )
        for index, item in enumerate((heading, meta, details)):
            node.insert(index, item)
        blocks = {
            "o001result": ("Pernyataan hasil sumber", "result"),
            "o001sourcehint": ("Petunjuk pembuktian sumber", "sourcehint"),
            "o001answer": ("Jawaban ringkas", "answer"),
            "o001proof": ("Pembuktian lengkap", "proof"),
        }
        for class_name, (title, suffix) in blocks.items():
            matches = node.xpath(f".//div[contains(concat(' ', normalize-space(@class), ' '), ' {class_name} ')]")
            if len(matches) != 1:
                raise RuntimeError(f"{solution_id}: expected one {class_name}, got {len(matches)}")
            stable_ids.append(add_block_heading(matches[0], solution_id, title, suffix))
        stable_ids.append(solution_id)
    return stable_ids, len(nodes)


def process_bridge(
    article: etree._Element,
    route: dict[str, Any],
    source_text: str,
    generic: list[etree._Element],
) -> tuple[list[str], int, dict[str, str]]:
    expected_ids = BRIDGE_ID_RE.findall(source_text)
    units = [node for node in generic if "proof" not in (node.get("class") or "").split()]
    if len(expected_ids) != 13 or len(units) != len(expected_ids):
        raise RuntimeError(f"bridge stable-ID closure mismatch: IDs={len(expected_ids)} units={len(units)}")
    local_display: dict[str, str] = {}
    stable_ids = [route["route_id"]]
    for node, stable_id in zip(units, expected_ids):
        node.set("id", stable_id)
        node.set("data-component-kind", "bridge-unit")
        node.set("data-license", "CC BY-SA 4.0")
        node.set("data-provenance", "separately-authored-not-Erdman")
        heading = node.xpath("./h3 | ./h4")[0]
        heading.set("id", f"{stable_id}-TITLE")
        node.set("aria-labelledby", heading.get("id"))
        short = "-".join(stable_id.split("-")[-3:])
        for label in node.xpath(".//*[@data-label]/@data-label"):
            local_display[label] = short
        stable_ids.append(stable_id)
    for order, section in enumerate(article.xpath("./h2"), start=1):
        section_id = f"O008-BRIDGE-CS-SECTION-{order:03d}"
        section.set("id", section_id)
        stable_ids.append(section_id)
    return stable_ids, len(units), local_display


def load_aux_numbers() -> dict[str, str]:
    numbers: dict[str, str] = {}
    for aux in sorted((ROOT / "qa" / "build-complete-source-final").glob("*.aux")):
        for line in aux.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", line)
            if match:
                numbers.setdefault(match.group(1), match.group(2))
    return numbers


def extend_source_reference_bindings(
    source_routes: dict[str, str],
    displays: dict[str, str],
) -> None:
    """Add source-local label aliases exactly as the admitted reader resolves them."""
    for filename in ("semantic_units.jsonl", "segments.jsonl"):
        for record in read_jsonl(ROOT / "backend" / filename):
            local_id = record.get("source_local_id")
            stable_id = record.get("id")
            if not local_id or stable_id not in source_routes:
                continue
            destination = source_routes[stable_id]
            previous = source_routes.get(local_id)
            if previous is None:
                source_routes[local_id] = destination
    for document_path in sorted(SOURCE_READER.glob("*/index.html")):
        document = html.parse(str(document_path)).getroot()
        for anchor in document.xpath("//a[@data-reference]"):
            target = anchor.get("data-reference")
            display = visible_text(anchor).strip()
            if target and display:
                displays.setdefault(target, display.strip("()"))


def rewrite_references(
    article: etree._Element,
    current_slug: str,
    source_routes: dict[str, str],
    aux_numbers: dict[str, str],
    local_display: dict[str, str],
) -> tuple[int, list[str]]:
    local_ids = set(article.xpath(".//@id"))
    rewritten = 0
    unresolved: list[str] = []
    for anchor in article.xpath(".//a[@data-reference]"):
        target = anchor.get("data-reference", "")
        reference_type = anchor.get("data-reference-type", "ref")
        if target in local_ids:
            anchor.set("href", f"#{target}")
        elif target in source_routes:
            anchor.set("href", source_href(current_slug, source_routes[target]))
        else:
            unresolved.append(target)
            continue
        display = aux_numbers.get(target) or local_display.get(target) or target
        anchor.text = f"({display})" if reference_type == "eqref" else display
        rewritten += 1
    return rewritten, sorted(set(unresolved))


def install_known_text_diagrams(article: etree._Element, route: dict[str, Any]) -> list[str]:
    """Replace the one copied XY-pic triangle with an accessible HTML surface."""
    installed: list[str] = []
    candidates: list[tuple[etree._Element, str]] = []
    for node in list(article.xpath(".//strong")):
        match = re.fullmatch(r"\[\[COMPANION-DIAGRAM:([^\]]+)\]\]", visible_text(node))
        if match:
            candidates.append((node, match.group(1)))
    for node in list(article.xpath(".//*[contains(concat(' ', normalize-space(@class), ' '), ' math ') and not(.//*[local-name()='math'])]")):
        tex = visible_text(node)
        if r"\qtriangle" in tex:
            candidates.append((node, "O001-FAOA-2015-CH04-EX-010-STATEMENT-DIAGRAM-001"))
    for node, diagram_id in candidates:
        if route.get("chapter") != 4 or diagram_id != "O001-FAOA-2015-CH04-EX-010-STATEMENT-DIAGRAM-001":
            raise RuntimeError(f"unrecognized diagram marker in {route['slug']}: {diagram_id}")
        figure = html.Element("span", {"id": diagram_id, "class": "text-diagram", "role": "img", "aria-labelledby": f"{diagram_id}-CAPTION"})
        visual = html.Element("span", {"class": "text-diagram-visual", "aria-hidden": "true"})
        visual.text = "S ──ι──▶ F\n ╲        │\n  f       │ f̃ᵢ\n   ╲      ▼\n     ───▶ A"
        caption = html.Element("span", {"id": f"{diagram_id}-CAPTION", "class": "text-diagram-caption"})
        caption.text = "Diagram segitiga komutatif ringkas: ι memetakan S ke F, f memetakan S ke A, dan f̃ᵢ memetakan F ke A; lintasan melalui F sama dengan f."
        figure.extend([visual, caption])
        parent = node.getparent()
        if parent is None:
            raise RuntimeError("diagram fallback has no parent")
        parent.replace(node, figure)
        installed.append(diagram_id)
    return installed


def local_toc(article: etree._Element) -> None:
    sections = article.xpath("./h2")
    if not sections:
        return
    nav = html.Element("nav", {"class": "local-toc", "aria-label": "Daftar bagian pada unit pendamping ini"})
    heading = html.Element("h2", {"id": f"{article.xpath('./h1/@id')[0]}-TOC"})
    heading.text = "Dalam unit ini"
    nav.append(heading)
    listing = html.Element("ol")
    for section in sections:
        item = html.Element("li")
        link = html.Element("a", {"href": f"#{section.get('id')}"})
        link.text = visible_text(section)
        item.append(link)
        listing.append(item)
    nav.append(listing)
    article.xpath("./h1")[0].addnext(nav)


def companion_navigation(current_slug: str) -> etree._Element:
    nav = html.Element("nav", {"class": "book-nav", "aria-label": "Daftar isi pendamping"})
    heading = html.Element("p", {"class": "book-nav__title"})
    heading.text = "Isi pendamping"
    nav.append(heading)
    listing = html.Element("ol")
    home = html.Element("li")
    home_link = html.Element("a", {"href": "../index.html" if current_slug else "index.html"})
    home_link.text = "Beranda pendamping"
    if not current_slug:
        home_link.set("aria-current", "page")
    home.append(home_link)
    listing.append(home)
    for route in ROUTES:
        item = html.Element("li")
        link = html.Element("a", {"href": relative_href(current_slug, route["slug"])})
        link.text = route["title"]
        if current_slug == route["slug"]:
            link.set("aria-current", "page")
        item.append(link)
        listing.append(item)
    source_item = html.Element("li", {"class": "nav-divider"})
    source_link = html.Element("a", {"href": source_href(current_slug, "index.html"), "class": "source-reader-link"})
    source_link.text = "← Reader teks sumber lengkap"
    source_item.append(source_link)
    listing.append(source_item)
    nav.append(listing)
    return nav


def page_document(
    article: etree._Element,
    slug: str,
    title: str,
    previous_item: tuple[str, str] | None,
    next_item: tuple[str, str] | None,
) -> str:
    qualify_external_links(article)
    document = html.Element("html", {"lang": "id"})
    head = html.Element("head")
    head.append(html.Element("meta", {"charset": "utf-8"}))
    head.append(html.Element("meta", {"name": "viewport", "content": "width=device-width, initial-scale=1"}))
    title_element = html.Element("title")
    title_element.text = f"{title} — Pendamping Analisis Fungsional"
    head.append(title_element)
    head.append(html.Element("meta", {"name": "description", "content": "Solusi O001 dan jembatan O008 berbahasa Indonesia dengan MathML semantik dan navigasi luring."}))
    prefix = "../assets/" if slug else "assets/"
    head.append(html.Element("link", {"rel": "stylesheet", "href": prefix + "reader.css"}))
    head.append(html.Element("link", {"rel": "stylesheet", "href": prefix + "companion.css"}))
    document.append(head)
    body = html.Element("body")
    skip = html.Element("a", {"class": "skip-link", "href": "#konten-utama"})
    skip.text = "Lewati ke isi utama"
    body.append(skip)
    header = html.Element("header", {"class": "site-header"})
    header_inner = html.Element("div", {"class": "site-header__inner"})
    site_link = html.Element("a", {"class": "site-title", "href": "../index.html" if slug else "index.html"})
    site_link.text = "Pendamping Analisis Fungsional — Bahasa Indonesia"
    header_inner.append(site_link)
    badge = html.Element("span", {"class": "edition-badge"})
    badge.text = "O001 + O008"
    header_inner.append(badge)
    header.append(header_inner)
    body.append(header)
    layout = html.Element("div", {"class": "reader-layout"})
    layout.append(companion_navigation(slug))
    main = html.Element("main", {"id": "konten-utama", "tabindex": "-1"})
    crumbs = html.Element("nav", {"class": "breadcrumbs", "aria-label": "Jejak navigasi"})
    crumb_list = html.Element("ol")
    first = html.Element("li")
    first_link = html.Element("a", {"href": "../index.html" if slug else "index.html"})
    first_link.text = "Pendamping"
    first.append(first_link)
    crumb_list.append(first)
    current = html.Element("li")
    current.text = title
    crumb_list.append(current)
    crumbs.append(crumb_list)
    main.extend([crumbs, article])
    if previous_item or next_item:
        unit_nav = html.Element("nav", {"class": "unit-navigation", "aria-label": "Navigasi unit pendamping"})
        if previous_item:
            previous = html.Element("a", {"class": "previous", "href": relative_href(slug, previous_item[0])})
            previous.text = f"← {previous_item[1]}"
            unit_nav.append(previous)
        else:
            unit_nav.append(html.Element("span"))
        if next_item:
            nxt = html.Element("a", {"class": "next", "href": relative_href(slug, next_item[0])})
            nxt.text = f"{next_item[1]} →"
            unit_nav.append(nxt)
        main.append(unit_nav)
    layout.append(main)
    body.append(layout)
    footer = html.Element("footer", {"class": "site-footer"})
    inner = html.Element("div", {"class": "site-footer__inner"})
    paragraph = html.Element("p")
    paragraph.text = "Pernyataan sumber: John M. Erdman; terjemahan dan komponen asli terpisah: "
    license_link = html.Element("a", {"href": LICENSE_URL, "rel": "license external noopener noreferrer"})
    license_link.text = "CC BY-SA 4.0"
    paragraph.append(license_link)
    license_link.tail = f". Komponen pendamping dibuat dengan bantuan {MODEL} atas arahan pengguna. Materi ini bukan tulisan Erdman dan tidak menyiratkan dukungan, sponsor, atau persetujuan beliau maupun Portland State University."
    inner.append(paragraph)
    footer.append(inner)
    body.append(footer)
    document.append(body)
    return "<!doctype html>\n" + etree.tostring(document, method="html", encoding="unicode", pretty_print=False) + "\n"


def home_article(solution_counts: dict[int, int]) -> tuple[etree._Element, list[str]]:
    article = html.Element("article", {"class": "reader-article"})
    title = html.Element("h1", {"id": "O008-COMPANION-HTML-READER"})
    title.text = "Pendamping penguasaan dan jembatan spektral"
    article.append(title)
    summary = html.Element("div", {"class": "companion-summary"})
    lead = html.Element("p")
    lead.text = "Permukaan ini menambahkan 52 solusi latihan O001, 10 pembuktian untuk hasil kerja-pembaca terpilih, dan 13 unit jembatan spektral-kompak/SVD tanpa mengubah reader teks sumber."
    summary.append(lead)
    status = html.Element("p", {"class": "status-note"})
    status.text = (
        "Status: edisi lengkap; pemeriksaan matematis, integrasi PDF/HTML, "
        "build deterministik, dan aksesibilitas dicatat dalam bukti QA edisi."
    )
    summary.append(status)
    source = html.Element("p")
    source.text = "Mulai dari "
    append_link(source, "", "reader teks sumber lengkap", source_href("", "index.html"))
    source[-1].tail = ", lalu kembali ke pendamping ini untuk pembuktian dan latihan."
    summary.append(source)
    article.append(summary)
    stable_ids = ["O008-COMPANION-HTML-READER"]
    groups = [
        ("O008-COMPANION-BRIDGE-INDEX", "Jembatan konsep", ROUTES[:1]),
        ("O008-COMPANION-READER-WORK-INDEX", "Pembuktian kerja-pembaca", ROUTES[1:2]),
        ("O008-COMPANION-SOLUTIONS-INDEX", "Solusi per bab", ROUTES[2:]),
    ]
    for group_id, heading_text, routes in groups:
        group = html.Element("section", {"class": "companion-group", "aria-labelledby": group_id})
        heading = html.Element("h2", {"id": group_id})
        heading.text = heading_text
        group.append(heading)
        listing = html.Element("ul", {"class": "companion-route-list"})
        for route in routes:
            item = html.Element("li")
            link = html.Element("a", {"href": relative_href("", route["slug"])})
            link.text = route["title"]
            if route["kind"] == "solutions":
                link.text += f" — {solution_counts[route['chapter']]} solusi"
            item.append(link)
            listing.append(item)
        group.append(listing)
        article.append(group)
        stable_ids.append(group_id)
    return article, stable_ids


def canonical_route_records(page_ids: dict[str, list[str]]) -> bytes:
    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for slug, identifiers in page_ids.items():
        output_path = f"{slug}/index.html" if slug else "index.html"
        for identifier in identifiers:
            if identifier in seen:
                raise RuntimeError(f"duplicate companion stable ID: {identifier}")
            seen.add(identifier)
            records.append(
                {
                    "href": f"{output_path}#{identifier}",
                    "id": identifier,
                    "locale": "id-ID",
                    "output_path": output_path,
                    "record_type": "html_route",
                    "route": slug,
                }
            )
    records.sort(key=lambda record: record["id"])
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=ROOT / "output" / "html-companion")
    parser.add_argument("--build-root", type=Path, default=ROOT / "qa" / "build-html-companion")
    parser.add_argument("--report", type=Path, default=ROOT / "qa" / "HTML_COMPANION_BUILD_RESULT.json")
    args = parser.parse_args()
    site_root = args.site_root if args.site_root.is_absolute() else ROOT / args.site_root
    build_root = args.build_root if args.build_root.is_absolute() else ROOT / args.build_root
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    if site_root.resolve() == SOURCE_READER.resolve():
        raise RuntimeError("companion builder refuses to overwrite output/html")
    before = source_reader_inventory()
    if before != EXPECTED_SOURCE_READER_INVENTORY:
        raise RuntimeError(f"unexpected admitted source-reader inventory: {before}")
    for route in ROUTES:
        if not route["path"].is_file():
            raise FileNotFoundError(route["path"])
    safe_reset(site_root, ROOT)
    safe_reset(build_root, ROOT)
    (site_root / "assets").mkdir()
    (build_root / "shadow").mkdir()
    (build_root / "raw").mkdir()
    shutil.copyfile(CSS_SOURCE, site_root / "assets" / "reader.css")
    shutil.copyfile(COMPANION_CSS, site_root / "assets" / "companion.css")
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("pandoc is unavailable")
    pandoc_version = subprocess.run([pandoc, "--version"], capture_output=True, text=True, encoding="utf-8", check=True).stdout.splitlines()[0]
    source_routes = {record["id"]: record["href"] for record in read_jsonl(SOURCE_ROUTE_MAP)}
    aux_numbers = load_aux_numbers()
    extend_source_reference_bindings(source_routes, aux_numbers)
    articles: dict[str, etree._Element] = {}
    page_ids: dict[str, list[str]] = {}
    diagnostics: list[dict[str, Any]] = []
    solution_counts: dict[int, int] = {}
    totals = {"solutions": 0, "reader_work": 0, "bridge_units": 0, "mathml": 0, "references": 0}
    input_receipts: list[dict[str, Any]] = []
    for route in ROUTES:
        source_text = route["path"].read_text(encoding="utf-8")
        input_receipts.append({"path": route["path"].relative_to(ROOT).as_posix(), "bytes": route["path"].stat().st_size, "sha256": sha256_file(route["path"])})
        shadow_text, specs = shadow_document(source_text)
        shadow = build_root / "shadow" / f"{route['slug']}.tex"
        raw = build_root / "raw" / f"{route['slug']}.html"
        write_text(shadow, shadow_text)
        _, stderr = run_pandoc(pandoc, shadow, raw)
        article = extract_article(raw)
        remove_generated_title(article)
        install_page_title(article, route)
        heading_level = 4 if route["kind"] == "reader_work" else 3
        decorated = decorate_generic_environments(article, specs, heading_level)
        local_display: dict[str, str] = {}
        if route["kind"] == "solutions":
            identifiers, count = process_solutions(article, route, source_routes)
            solution_counts[route["chapter"]] = count
            totals["solutions"] += count
        elif route["kind"] == "reader_work":
            identifiers, count = process_reader_work(article, route, source_routes)
            totals["reader_work"] += count
        else:
            identifiers, count, local_display = process_bridge(article, route, source_text, decorated)
            totals["bridge_units"] += count
        references, unresolved = rewrite_references(article, route["slug"], source_routes, aux_numbers, local_display)
        if unresolved:
            raise RuntimeError(f"unresolved references in {route['slug']}: {unresolved}")
        totals["references"] += references
        diagram_ids = install_known_text_diagrams(article, route)
        identifiers.extend(diagram_ids)
        local_toc(article)
        math_count, fallbacks = normalize_math(article)
        if fallbacks:
            raise RuntimeError(f"MathML fallbacks in {route['slug']}: {fallbacks[:5]}")
        totals["mathml"] += math_count
        articles[route["slug"]] = article
        page_ids[route["slug"]] = identifiers
        diagnostics.append(
            {
                "route": route["slug"],
                "pandoc_warning_count": stderr.count("[WARNING]"),
                "mathml_count": math_count,
                "reference_count": references,
                "stable_id_count": len(identifiers),
            }
        )
    if totals["solutions"] != 52 or totals["reader_work"] != 10 or totals["bridge_units"] != 13:
        raise RuntimeError(f"component closure mismatch: {totals}")
    home, home_ids = home_article(solution_counts)
    page_ids[""] = home_ids
    route_order = [(route["slug"], route["title"]) for route in ROUTES]
    for index, route in enumerate(ROUTES):
        previous_item = route_order[index - 1] if index else None
        next_item = route_order[index + 1] if index + 1 < len(route_order) else None
        write_text(site_root / route["slug"] / "index.html", page_document(articles[route["slug"]], route["slug"], route["title"], previous_item, next_item))
    write_text(site_root / "index.html", page_document(home, "", "Beranda pendamping", None, route_order[0]))
    route_bytes = canonical_route_records(page_ids)
    route_map = site_root / "COMPANION_ROUTES.jsonl"
    route_map.write_bytes(route_bytes)
    manifest_rows, inventory_sha256 = write_manifest(site_root)
    after = source_reader_inventory()
    if after != before:
        raise RuntimeError(f"admitted source reader changed during companion build: {before} -> {after}")
    report = {
        "schema_version": "o008.html-companion-build.v1",
        "result": "pass",
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "pandoc": pandoc_version,
        "source_reader": {"before_inventory_sha256": before, "after_inventory_sha256": after, "unchanged": before == after},
        "inputs": input_receipts,
        "counts": {
            "html_documents": len(ROUTES) + 1,
            "routes": len(ROUTES),
            "manifested_files": len(manifest_rows),
            "route_records": sum(len(values) for values in page_ids.values()),
            **totals,
        },
        "solution_counts_by_chapter": {f"CH{chapter:02d}": count for chapter, count in sorted(solution_counts.items())},
        "artifacts": {
            "site_inventory_sha256": inventory_sha256,
            "manifest_sha256": sha256_file(site_root / "MANIFEST.csv"),
            "route_map_sha256": sha256_file(route_map),
        },
        "routes": diagnostics,
    }
    write_text(report_path, stable_json(report))
    print(stable_json(report), end="")


if __name__ == "__main__":
    main()
