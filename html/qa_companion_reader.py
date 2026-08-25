#!/usr/bin/env python3
"""Strict machine QA for the additive O001/O008 semantic HTML companion."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from lxml import etree, html

from build_companion_reader import (
    BRIDGE_ID_RE,
    EXPECTED_SOURCE_READER_INVENTORY,
    ROOT,
    SOURCE_READER,
    source_reader_inventory,
)


ROUTE_FIELDS = {"href", "id", "locale", "output_path", "record_type", "route"}
MATH_NS = "http://www.w3.org/1998/Math/MathML"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def inventory_hash(root: Path, include_manifest: bool = False) -> tuple[list[dict[str, object]], str]:
    rows: list[dict[str, object]] = []
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.relative_to(root).as_posix()):
        if not include_manifest and path.name == "MANIFEST.csv":
            continue
        rows.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    material = "".join(f"{row['path']}\0{row['bytes']}\0{row['sha256']}\n" for row in rows).encode("utf-8")
    return rows, sha256_bytes(material)


class Auditor:
    def __init__(self, site_root: Path) -> None:
        self.root = site_root.resolve()
        self.route_map = self.root / "COMPANION_ROUTES.jsonl"
        self.manifest = self.root / "MANIFEST.csv"
        self.findings: list[dict[str, object]] = []
        self.documents = sorted(self.root.glob("**/index.html"), key=lambda path: path.relative_to(self.root).as_posix())
        self.trees: dict[Path, etree._Element] = {}
        self.ids: dict[Path, set[str]] = {}
        self.counts = {
            "html_documents": 0,
            "mathml_elements": 0,
            "internal_references": 0,
            "source_reader_links": 0,
            "route_records": 0,
            "solutions": 0,
            "reader_work": 0,
            "bridge_units": 0,
            "text_diagrams": 0,
            "headings": 0,
        }

    def add(self, code: str, file: str, message: str, line: int | None = None) -> None:
        finding: dict[str, object] = {"code": code, "file": file, "message": message}
        if line is not None:
            finding["line"] = line
        self.findings.append(finding)

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def parse_documents(self) -> None:
        for path in self.documents:
            display = self.rel(path)
            raw = path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw or not raw.endswith(b"\n"):
                self.add("serialization", display, "HTML must be UTF-8 without BOM, use LF, and end with LF.")
            if not raw.lower().startswith(b"<!doctype html>\n"):
                self.add("doctype", display, "HTML5 doctype is missing.")
            try:
                tree = html.fromstring(raw)
            except (etree.ParserError, UnicodeDecodeError) as exc:
                self.add("parse", display, f"HTML parse failed: {exc.__class__.__name__}.")
                continue
            self.trees[path.resolve()] = tree
            identifiers = tree.xpath("//@id")
            duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
            if duplicates:
                self.add("id.duplicate", display, f"Duplicate IDs: {duplicates[:10]}")
            self.ids[path.resolve()] = set(identifiers)
            if tree.get("lang") != "id":
                self.add("lang", display, "Document language must be id.")
            if len(tree.xpath("//meta[@name='viewport' and @content='width=device-width, initial-scale=1']")) != 1:
                self.add("viewport", display, "Responsive viewport metadata is missing.")
            if len(tree.xpath("//main[@id='konten-utama' and @tabindex='-1']")) != 1:
                self.add("main", display, "Exactly one focusable main landmark is required.")
            if len(tree.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' skip-link ') and @href='#konten-utama']")) != 1:
                self.add("skip_link", display, "Visible-on-focus skip link is missing.")
            if len(tree.xpath("//main//h1")) != 1:
                self.add("heading.h1", display, "Exactly one main h1 is required.")
            if len(tree.xpath("//nav[@aria-label]")) < 3:
                self.add("navigation", display, "Expected contents, breadcrumb, and unit navigation landmarks.")
            for node in tree.xpath("//*[@aria-labelledby]"):
                for target in node.get("aria-labelledby", "").split():
                    if target not in self.ids[path.resolve()]:
                        self.add("aria.labelledby", display, f"Missing aria-labelledby target {target!r}.", node.sourceline)
            main_headings = tree.xpath("//main//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]")
            previous = 0
            for heading in main_headings:
                level = int(heading.tag[1])
                if previous and level > previous + 1:
                    self.add("heading.jump", display, f"Heading level jumps h{previous} to h{level}.", heading.sourceline)
                previous = level
            text = " ".join(tree.text_content().split())
            for required in (MODEL, "CC BY-SA 4.0", "tidak menyiratkan dukungan", "John M. Erdman"):
                if required not in text:
                    self.add("provenance.visible", display, f"Visible provenance text is missing {required!r}.")
            if re.search(r"\[\[(?:COMPANION-DIAGRAM|DIAGRAM):", text) or re.search(r"[A-Za-z]:\\Users\\", text):
                self.add("residue", display, "Unresolved marker or local Windows path is visible.")
            math_nodes = tree.xpath("//*[local-name()='math']")
            self.counts["mathml_elements"] += len(math_nodes)
            for node in math_nodes:
                namespace = etree.QName(node).namespace or node.get("xmlns")
                if namespace != MATH_NS:
                    self.add("math.namespace", display, "Math element lacks the MathML namespace.", node.sourceline)
                if node.get("role") != "math" or not node.get("aria-label"):
                    self.add("math.accessibility", display, "MathML needs role=math and an aria-label.", node.sourceline)
                if not node.xpath(".//*[local-name()='annotation' and @encoding='application/x-tex']"):
                    self.add("math.annotation", display, "MathML lacks its TeX annotation.", node.sourceline)
            for node in tree.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), ' math ') and not(.//*[local-name()='math'])]"):
                self.add("math.fallback", display, "A non-MathML formula fallback remains.", node.sourceline)
            self.counts["solutions"] += len(tree.xpath("//*[@data-component-kind='o001-solution']"))
            self.counts["reader_work"] += len(tree.xpath("//*[@data-component-kind='o001-reader-work']"))
            self.counts["bridge_units"] += len(tree.xpath("//*[@data-component-kind='bridge-unit']"))
            self.counts["text_diagrams"] += len(tree.xpath("//*[@class='text-diagram' and @role='img' and @aria-labelledby]"))
            self.counts["headings"] += len(main_headings)
            self.counts["html_documents"] += 1

    def resolve_link(self, base: Path, href: str, display: str, line: int | None) -> None:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc:
            return
        decoded = unquote(parsed.path)
        target = (base.parent / decoded).resolve() if decoded else base.resolve()
        if target.is_dir() or decoded.endswith("/"):
            target = target / "index.html"
        try:
            target.relative_to(self.root)
            inside_companion = True
        except ValueError:
            inside_companion = False
        try:
            target.relative_to(SOURCE_READER.resolve())
            inside_source = True
        except ValueError:
            inside_source = False
        if not inside_companion and not inside_source:
            self.add("link.escape", display, f"Link escapes both reader trees: {href!r}.", line)
            return
        if not target.is_file():
            self.add("link.missing", display, f"Missing link target: {href!r}.", line)
            return
        self.counts["internal_references"] += 1
        if inside_source:
            self.counts["source_reader_links"] += 1
        if parsed.fragment:
            resolved = target.resolve()
            if resolved not in self.ids:
                try:
                    target_tree = html.parse(str(target)).getroot()
                    self.ids[resolved] = set(target_tree.xpath("//@id"))
                except (OSError, etree.ParserError):
                    self.add("link.target_parse", display, f"Could not parse {href!r}.", line)
                    return
            if unquote(parsed.fragment) not in self.ids[resolved]:
                self.add("link.fragment", display, f"Missing fragment in {href!r}.", line)

    def audit_links(self) -> None:
        for path, tree in self.trees.items():
            display = self.rel(path)
            for anchor in tree.xpath("//a[@href]"):
                href = anchor.get("href", "")
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc:
                    rel = {token.casefold() for token in anchor.get("rel", "").split()}
                    if parsed.scheme != "https" or not {"external", "noopener", "noreferrer"}.issubset(rel):
                        self.add("link.external", display, "External links must be credential-free HTTPS and qualified.", anchor.sourceline)
                    continue
                self.resolve_link(path, href, display, anchor.sourceline)

    def audit_routes(self) -> None:
        display = self.rel(self.route_map)
        raw = self.route_map.read_bytes()
        if b"\r" in raw or not raw.endswith(b"\n") or raw.startswith(b"\xef\xbb\xbf"):
            self.add("routes.serialization", display, "Route map must be canonical UTF-8/LF JSONL.")
        records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line]
        canonical = "".join(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for record in records).encode("utf-8")
        if canonical != raw:
            self.add("routes.serialization", display, "Route-map JSON objects are not canonically serialized.")
        if [record.get("id") for record in records] != sorted(record.get("id") for record in records):
            self.add("routes.order", display, "Route records are not sorted by stable ID.")
        seen: set[str] = set()
        covered: set[Path] = set()
        for index, record in enumerate(records, start=1):
            if set(record) != ROUTE_FIELDS:
                self.add("routes.fields", display, f"Record {index} has an invalid field set.")
                continue
            identifier = record["id"]
            if identifier in seen:
                self.add("routes.duplicate", display, f"Duplicate route ID {identifier!r}.")
            seen.add(identifier)
            if record["locale"] != "id-ID" or record["record_type"] != "html_route":
                self.add("routes.type", display, f"Record {index} has invalid locale/type.")
            expected_path = f"{record['route']}/index.html" if record["route"] else "index.html"
            if record["output_path"] != expected_path or record["href"] != f"{expected_path}#{identifier}":
                self.add("routes.binding", display, f"Record {index} has a noncanonical path/href.")
                continue
            target = (self.root / expected_path).resolve()
            covered.add(target)
            if target not in self.ids or identifier not in self.ids[target]:
                self.add("routes.fragment", display, f"Record {index} does not resolve to its stable ID.")
        expected_pages = set(self.trees)
        if covered != expected_pages:
            self.add("routes.coverage", display, "Route map does not cover exactly every HTML document.")
        self.counts["route_records"] = len(records)

    def audit_manifest(self) -> tuple[str, str]:
        raw = self.manifest.read_bytes()
        if b"\r" in raw or not raw.endswith(b"\n") or raw.startswith(b"\xef\xbb\xbf"):
            self.add("manifest.serialization", "MANIFEST.csv", "Manifest must be canonical UTF-8/LF CSV.")
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
        rows = list(reader)
        if reader.fieldnames != ["path", "bytes", "sha256"]:
            self.add("manifest.header", "MANIFEST.csv", "Unexpected manifest header.")
        if [row["path"] for row in rows] != sorted(row["path"] for row in rows):
            self.add("manifest.order", "MANIFEST.csv", "Manifest rows are not path-sorted.")
        actual_rows, actual_inventory = inventory_hash(self.root)
        actual = {str(row["path"]): (int(row["bytes"]), str(row["sha256"])) for row in actual_rows}
        expected = {row["path"]: (int(row["bytes"]), row["sha256"]) for row in rows}
        if actual != expected:
            self.add("manifest.identity", "MANIFEST.csv", "Manifest paths, byte counts, or hashes differ from the site.")
        return sha256_file(self.manifest), actual_inventory

    def audit_components(self) -> None:
        solution_inventory = [json.loads(line) for line in (ROOT / "mastery" / "O001_EXERCISE_INVENTORY.jsonl").read_text(encoding="utf-8").splitlines() if line]
        reader_inventory = [json.loads(line) for line in (ROOT / "mastery" / "O001_READER_WORK_INVENTORY.jsonl").read_text(encoding="utf-8").splitlines() if line]
        expected_solutions = {record["solution_id"] for record in solution_inventory}
        expected_reader_work = {record["solution_id"] for record in reader_inventory}
        expected_bridge = set(BRIDGE_ID_RE.findall((ROOT / "bridge" / "id-ID" / "compact-spectral-svd.tex").read_text(encoding="utf-8")))
        observed_solutions: set[str] = set()
        observed_reader_work: set[str] = set()
        observed_bridge: set[str] = set()
        for tree in self.trees.values():
            observed_solutions.update(tree.xpath("//*[@data-component-kind='o001-solution']/@id"))
            observed_reader_work.update(tree.xpath("//*[@data-component-kind='o001-reader-work']/@id"))
            observed_bridge.update(tree.xpath("//*[@data-component-kind='bridge-unit']/@id"))
            for node in tree.xpath("//*[@data-component-kind='o001-solution']"):
                for suffix in ("STATEMENT", "ANSWER", "PROOF"):
                    if not node.xpath(f".//*[@id='{node.get('id')}-{suffix}']"):
                        self.add("solution.blocks", "component", f"{node.get('id')} lacks {suffix.lower()}.")
        for label, expected, observed in (
            ("solution", expected_solutions, observed_solutions),
            ("reader_work", expected_reader_work, observed_reader_work),
            ("bridge", expected_bridge, observed_bridge),
        ):
            if expected != observed:
                self.add(f"components.{label}", "component", f"ID mismatch; missing={sorted(expected-observed)}, extra={sorted(observed-expected)}")

    def audit_css(self) -> None:
        reader = (self.root / "assets" / "reader.css").read_text(encoding="utf-8")
        companion = (self.root / "assets" / "companion.css").read_text(encoding="utf-8")
        required = [
            ".reader-layout",
            "margin: 0 auto",
            ".reader-article",
            "max-width: var(--measure)",
            "@media (max-width: 58rem)",
            "@media (max-width: 36rem)",
        ]
        for marker in required:
            if marker not in reader:
                self.add("css.layout", "assets/reader.css", f"Missing centered/responsive rule marker {marker!r}.")
        for marker in (".o001solution", ".o001readerwork", ".companion-environment", ".text-diagram"):
            if marker not in companion:
                self.add("css.component", "assets/companion.css", f"Missing component style {marker!r}.")

    def run(self) -> dict[str, object]:
        if not self.root.is_dir():
            raise FileNotFoundError(self.root)
        self.parse_documents()
        self.audit_links()
        self.audit_routes()
        manifest_sha, site_inventory = self.audit_manifest()
        self.audit_components()
        self.audit_css()
        source_inventory = source_reader_inventory()
        if source_inventory != EXPECTED_SOURCE_READER_INVENTORY:
            self.add("source_reader.identity", "../html/MANIFEST.csv", "The admitted source reader changed.")
        if self.counts["html_documents"] != 15:
            self.add("counts.documents", ".", f"Expected 15 documents, got {self.counts['html_documents']}.")
        for key, expected in (("solutions", 52), ("reader_work", 10), ("bridge_units", 13), ("text_diagrams", 1)):
            if self.counts[key] != expected:
                self.add(f"counts.{key}", ".", f"Expected {expected}, got {self.counts[key]}.")
        self.findings.sort(key=lambda item: (str(item["file"]), int(item.get("line", 0)), str(item["code"])))
        return {
            "schema_version": "o008.html-companion-qa.v1",
            "passed": not self.findings,
            "counts": {**self.counts, "findings": len(self.findings)},
            "artifacts": {
                "manifest_sha256": manifest_sha,
                "route_map_sha256": sha256_file(self.route_map),
                "site_inventory_sha256": site_inventory,
                "source_reader_inventory_sha256": source_inventory,
            },
            "findings": self.findings,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_root", nargs="?", type=Path, default=ROOT / "output" / "html-companion")
    parser.add_argument("--output", type=Path, default=ROOT / "qa" / "HTML_COMPANION_QA.json")
    args = parser.parse_args()
    root = args.site_root if args.site_root.is_absolute() else ROOT / args.site_root
    output = args.output if args.output.is_absolute() else ROOT / args.output
    report = Auditor(root).run()
    encoded = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output.write_bytes(encoded)
    sys.stdout.buffer.write(encoded)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
