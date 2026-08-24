#!/usr/bin/env python3
"""Deterministic QA gate for the static Indonesian FAOA HTML reader.

The command accepts a generated site root and the canonical backend-to-reader
JSONL route map::

    python html/qa_reader.py output/html backend/html_routes.jsonl

The default report is written to stdout.  ``--output`` may point to a JSON file
outside the site root.  The site root must contain ``MANIFEST.csv`` with the
exact header ``path,bytes,sha256``.  The manifest lists every regular site file
except itself, in ascending POSIX-path order.

This module deliberately uses only the Python standard library and ``lxml``.
If lxml is unavailable, the command emits a small JSON dependency error and
exits nonzero without inspecting the site.  Run ``--self-test`` to exercise a
passing fixture and prove that representative defects are rejected.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import posixpath
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator, Sequence
from urllib.parse import unquote, urlsplit

try:
    from lxml import etree
except Exception as exc:  # pragma: no cover - tested through the main guard
    etree = None  # type: ignore[assignment]
    _LXML_IMPORT_ERROR = exc
else:
    _LXML_IMPORT_ERROR = None


REPORT_SCHEMA = "o008-html-reader-qa-v1"
MANIFEST_HEADER = ["path", "bytes", "sha256"]
MODEL_MARKER = "OpenAI Codex gpt-5.6-sol, Ultra"
NONENDORSEMENT_MARKER = "tidak menyiratkan dukungan"
MATHML_NAMESPACE = "http://www.w3.org/1998/Math/MathML"
ROUTE_FIELDS = {"href", "id", "locale", "output_path", "record_type", "route"}
EXTERNAL_ANCHOR_REL = {"external", "noopener", "noreferrer"}
TEXT_EXTENSIONS = {
    ".css",
    ".csv",
    ".htm",
    ".html",
    ".js",
    ".json",
    ".jsonl",
    ".map",
    ".md",
    ".mjs",
    ".svg",
    ".txt",
    ".webmanifest",
    ".xhtml",
    ".xml",
}
RESIDUE_SUFFIXES = {
    ".4ct",
    ".4tc",
    ".aux",
    ".bak",
    ".dvi",
    ".fdb_latexmk",
    ".fls",
    ".idv",
    ".lg",
    ".log",
    ".out",
    ".tmp",
    ".toc",
    ".xref",
}
RESIDUE_PARTS = {
    "__pycache__",
    ".cache",
    "cache",
    "probe",
    "probes",
    "scratch",
    "temp",
    "tmp",
}
URI_ATTRIBUTES = {
    "action",
    "cite",
    "data",
    "formaction",
    "href",
    "longdesc",
    "manifest",
    "ping",
    "poster",
    "src",
}
NETWORK_URI_RE = re.compile(r"(?i)^(?:https?|ftp|ftps|ws|wss):|^//")
NETWORK_TEXT_RE = re.compile(r"(?i)(?:https?|ftp|ftps|ws|wss):\\?/\\?/|(?<!:)//[A-Za-z0-9]")
CSS_URL_RE = re.compile(r"(?is)url\(\s*(['\"]?)(.*?)\1\s*\)")
CSS_IMPORT_RE = re.compile(r"(?im)@import\s+(?:url\(\s*)?['\"]([^'\"]+)['\"]")
MATH_IMAGE_RE = re.compile(
    r"(?i)(?:^|[-_\s])(math|latex|formula|equation|rumus)(?:$|[-_\s])"
)
LOCAL_PATH_PATTERNS = [
    re.compile(
        r"(?i)(?<![A-Za-z0-9])[A-Z]:[\\/]"
        r"(?:Users|Documents|Downloads|Desktop|AppData|Windows|Temp|Program Files(?: \(x86\))?)[\\/]"
    ),
    re.compile(r"(?i)(?<![A-Za-z0-9])[A-Z]:[\\/](?:[A-Za-z0-9 ._-]+[\\/]){2,}"),
    re.compile(r"(?i)file:(?:/{2,3}|\\{2,3})"),
    re.compile(r"(?i)(?<![A-Za-z0-9])/(?:home|Users|tmp|var/tmp)/"),
    re.compile(r"\\\\[A-Za-z0-9._-]+\\"),
]
CREDENTIAL_PATTERNS = [
    re.compile(r"(?i)\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd)\b"
        r"\s*[:=]\s*['\"]?[^\s'\"<>]{8,}"
    ),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}={0,2}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
RESIDUE_TEXT_PATTERNS = [
    re.compile(r"(?i)\b(?:TODO|FIXME|TBD)\b"),
    re.compile(r"(?i)lorem\s+ipsum"),
    re.compile(r"(?i)translation\s+(?:needed|missing|pending)"),
    re.compile(r"(?i)belum\s+diterjemahkan"),
    re.compile(r"(?i)(?:\[\[|<)\s*PLACEHOLDER(?:\s+TEXT)?\s*(?:\]\]|>)"),
    re.compile(r"(?i)\[\[\s*(?:DIAGRAM|NUMBER-NOTATION)\s*:[^\]]*\]\]"),
    re.compile(r"\ufffd"),
]


@dataclass(frozen=True)
class Finding:
    code: str
    file: str
    line: int
    message: str

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "code": self.code,
            "file": self.file,
            "message": self.message,
        }
        if self.line:
            result["line"] = self.line
        return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _local_name(element: Any) -> str:
    tag = getattr(element, "tag", "")
    if not isinstance(tag, str):
        return ""
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1].lower()
    return tag.lower()


def _attribute_local_name(name: str) -> str:
    if name.startswith("{"):
        return name.rsplit("}", 1)[-1].lower()
    if ":" in name:
        return name.rsplit(":", 1)[-1].lower()
    return name.lower()


def _normalise_space(value: str) -> str:
    return " ".join(value.split())


def _normalise_marker_text(value: str) -> str:
    return _normalise_space(
        value.replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )


def _is_hidden(element: Any) -> bool:
    current = element
    while current is not None and hasattr(current, "attrib"):
        if _local_name(current) in {"head", "script", "style", "template"}:
            return True
        if "hidden" in current.attrib:
            return True
        if current.get("aria-hidden", "").strip().lower() == "true":
            return True
        style = current.get("style", "")
        if re.search(r"(?i)(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\b", style):
            return True
        current = current.getparent()
    return False


def _element_text(element: Any) -> str:
    return _normalise_space(" ".join(str(part) for part in element.itertext()))


def _visible_text(tree: Any) -> str:
    pieces: list[str] = []
    for text_node in tree.xpath("//body//text()"):
        parent = text_node.getparent()
        if parent is not None and not _is_hidden(parent):
            pieces.append(str(text_node))
    return _normalise_marker_text(" ".join(pieces))


def _line(element: Any) -> int:
    value = getattr(element, "sourceline", 0)
    return int(value or 0)


def _normalised_relative_path(raw: str) -> str | None:
    if not raw or "\\" in raw or "\x00" in raw:
        return None
    candidate = PurePosixPath(raw)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        return None
    normalised = candidate.as_posix()
    if posixpath.normpath(normalised) != normalised:
        return None
    return normalised


class ReaderAuditor:
    def __init__(self, site_root: Path, route_map: Path, manifest_name: str = "MANIFEST.csv"):
        self.root = site_root.resolve()
        self.route_map = route_map.resolve()
        self.manifest_path = (self.root / manifest_name).resolve()
        try:
            self.manifest_path.relative_to(self.root)
        except ValueError:
            self.manifest_is_local = False
        else:
            self.manifest_is_local = True
        self.findings: list[Finding] = []
        self.documents: dict[Path, Any] = {}
        self.document_ids: dict[Path, set[str]] = {}
        self.files: list[Path] = []
        self.math_count = 0
        self.route_count = 0
        self.link_count = 0
        self.image_count = 0
        self.svg_count = 0
        self.table_count = 0
        self.manifest_sha256 = ""
        self.inventory_sha256 = ""
        self.route_map_sha256 = ""

    def rel(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except (OSError, ValueError):
            return path.name

    def add(self, code: str, path: str | Path, message: str, line: int = 0) -> None:
        display = path if isinstance(path, str) else self.rel(path)
        self.findings.append(Finding(code, display, line, message))

    def audit(self) -> dict[str, Any]:
        self._inventory()
        self._audit_residue()
        self._parse_html_documents()
        for path in sorted(self.documents, key=self.rel):
            self._audit_document(path, self.documents[path])
        self._audit_static_code()
        if not self.documents:
            self.add("html.none", ".", "No HTML documents were found in the site root.")
        if self.math_count == 0:
            self.add("math.none_site", ".", "The reader contains no native MathML elements.")
        self._audit_standalone_svgs()
        self._audit_route_map()
        self._audit_manifest()
        findings = sorted(
            self.findings,
            key=lambda item: (item.code, item.file, item.line, item.message),
        )
        return {
            "artifacts": {
                "inventory_sha256": self.inventory_sha256,
                "manifest_sha256": self.manifest_sha256,
                "route_map_sha256": self.route_map_sha256,
            },
            "counts": {
                "files": len(self.files),
                "findings": len(findings),
                "html_documents": len(self.documents),
                "images": self.image_count,
                "internal_references": self.link_count,
                "mathml_elements": self.math_count,
                "route_records": self.route_count,
                "standalone_svgs": self.svg_count,
                "tables": self.table_count,
            },
            "findings": [item.as_dict() for item in findings],
            "passed": not findings,
            "schema_version": REPORT_SCHEMA,
        }

    def _inventory(self) -> None:
        if not self.root.is_dir():
            self.add("site.missing", ".", "The site root does not exist or is not a directory.")
            return
        if self.root.is_symlink():
            self.add("site.symlink", ".", "The site root must not be a symbolic link.")
        casefold_paths: dict[str, str] = {}
        try:
            candidates = sorted(self.root.rglob("*"), key=lambda value: self.rel(value))
        except OSError as exc:
            self.add("site.inventory_error", ".", f"Could not enumerate site files: {exc.__class__.__name__}.")
            return
        for path in candidates:
            relative = self.rel(path)
            if path.is_symlink():
                self.add("site.symlink", relative, "Symbolic links are not allowed in the static release.")
                continue
            if not path.is_file():
                continue
            try:
                path.resolve().relative_to(self.root)
            except (OSError, ValueError):
                self.add("site.path_escape", relative, "A site file resolves outside the site root.")
                continue
            folded = relative.casefold()
            if folded in casefold_paths and casefold_paths[folded] != relative:
                self.add(
                    "site.case_collision",
                    relative,
                    f"Path collides case-insensitively with {casefold_paths[folded]!r}.",
                )
            else:
                casefold_paths[folded] = relative
            self.files.append(path)

    def _audit_residue(self) -> None:
        for path in self.files:
            relative = self.rel(path)
            lower_parts = {part.casefold() for part in PurePosixPath(relative).parts[:-1]}
            if lower_parts & RESIDUE_PARTS:
                self.add("residue.path", relative, "A transient build/probe/cache directory is present in the site.")
            if path.suffix.casefold() in RESIDUE_SUFFIXES or path.name.endswith("~"):
                self.add("residue.file", relative, "A transient build or editor artifact is present in the site.")
            if path.name in {".DS_Store", "Thumbs.db"}:
                self.add("residue.file", relative, "An operating-system metadata artifact is present in the site.")
            if path.suffix.casefold() not in TEXT_EXTENSIONS and path.name != "MANIFEST.csv":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                self.add("text.utf8", relative, "Text release file is not valid UTF-8.")
                continue
            except OSError as exc:
                self.add("text.read_error", relative, f"Could not read text file: {exc.__class__.__name__}.")
                continue
            for pattern in LOCAL_PATH_PATTERNS:
                if pattern.search(text):
                    self.add("privacy.local_path", relative, "Release text contains an absolute or machine-local path.")
                    break
            for pattern in CREDENTIAL_PATTERNS:
                if pattern.search(text):
                    self.add("privacy.credential", relative, "Release text contains a credential-like secret.")
                    break
            for pattern in RESIDUE_TEXT_PATTERNS:
                match = pattern.search(text)
                if match:
                    line = text.count("\n", 0, match.start()) + 1
                    self.add("residue.text", relative, "Release text contains an unfinished-work marker.", line)
                    break

    def _parse_html_documents(self) -> None:
        if etree is None:
            return
        for path in (item for item in self.files if item.suffix.casefold() in {".htm", ".html", ".xhtml"}):
            relative = self.rel(path)
            try:
                raw = path.read_bytes()
            except OSError as exc:
                self.add("html.read_error", relative, f"Could not read HTML file: {exc.__class__.__name__}.")
                continue
            if not re.search(br"(?is)<html(?:\s|>)", raw):
                self.add("html.root_missing", relative, "Document does not contain an explicit html root element.")
            # libxml2's HTML parser targets legacy HTML and reports valid HTML5
            # elements (notably MathML) as syntax errors when recovery is off.
            # Recovery is therefore enabled here; explicit structural checks and
            # strict XML parsing of every MathML/SVG subtree provide the gate.
            parser = etree.HTMLParser(recover=True, no_network=True, encoding="utf-8")
            try:
                tree = etree.parse(io.BytesIO(raw), parser)
            except (etree.XMLSyntaxError, ValueError) as exc:
                line = int(getattr(exc, "position", (0, 0))[0] or 0)
                self.add("html.parse", relative, "Document is not parseable HTML.", line)
                continue
            for issue in parser.error_log:
                if issue.level_name in {"ERROR", "FATAL"} and issue.type_name != "HTML_UNKNOWN_TAG":
                    self.add(
                        "html.parse_issue",
                        relative,
                        f"HTML parser reported {issue.type_name}.",
                        int(issue.line or 0),
                    )
            self.documents[path.resolve()] = tree

    def _audit_document(self, path: Path, tree: Any) -> None:
        relative = self.rel(path)
        html_nodes = tree.xpath("/*[local-name()='html']")
        if len(html_nodes) != 1:
            self.add("html.root_count", relative, "Document must have exactly one html root element.")
        else:
            language = html_nodes[0].get("lang", "").strip().lower()
            if not (language == "id" or language.startswith("id-")):
                self.add("html.lang", relative, "The html lang value must be id or an id-* locale.", _line(html_nodes[0]))

        ids: dict[str, list[Any]] = {}
        for element in tree.xpath("//*[@id]"):
            identifier = element.get("id", "")
            if not identifier or identifier.strip() != identifier or re.search(r"\s", identifier):
                self.add("id.invalid", relative, "ID values must be nonempty and contain no whitespace.", _line(element))
                continue
            ids.setdefault(identifier, []).append(element)
        for identifier, elements in sorted(ids.items()):
            if len(elements) > 1:
                self.add(
                    "id.duplicate",
                    relative,
                    f"ID {identifier!r} occurs {len(elements)} times in one document.",
                    _line(elements[1]),
                )
        self.document_ids[path.resolve()] = set(ids)
        self._audit_aria_labelledby(path, tree, ids)

        mains: list[Any] = []
        for element in tree.xpath("//*[local-name()='main' or @role='main']"):
            if element not in mains:
                mains.append(element)
        if len(mains) != 1:
            self.add("landmark.main_count", relative, "Document must expose exactly one main landmark.")
        else:
            self._audit_skip_link(path, tree, mains[0], ids)

        nav_names: dict[str, Any] = {}
        for nav in tree.xpath("//*[local-name()='nav' or @role='navigation']"):
            name = self._accessible_name(nav, ids)
            if not name:
                self.add("landmark.nav_unlabelled", relative, "Every navigation landmark needs an accessible label.", _line(nav))
            elif name.casefold() in nav_names:
                self.add("landmark.nav_duplicate_label", relative, f"Navigation label {name!r} is not unique on the page.", _line(nav))
            else:
                nav_names[name.casefold()] = nav

        self._audit_headings(path, tree)
        self._audit_references(path, tree)
        self._audit_math(path, tree)
        self._audit_images(path, tree, ids)
        self._audit_tables(path, tree, ids)
        self._audit_markers(path, tree)

    def _accessible_name(self, element: Any, ids: dict[str, list[Any]]) -> str:
        aria_label = _normalise_space(element.get("aria-label", ""))
        if aria_label:
            return aria_label
        labelledby = element.get("aria-labelledby", "").split()
        if labelledby:
            parts: list[str] = []
            for identifier in labelledby:
                targets = ids.get(identifier, [])
                if len(targets) == 1:
                    text = _element_text(targets[0])
                    if text:
                        parts.append(text)
            return _normalise_space(" ".join(parts))
        return ""

    def _audit_aria_labelledby(self, path: Path, tree: Any, ids: dict[str, list[Any]]) -> None:
        relative = self.rel(path)
        for element in tree.xpath("//*[@aria-labelledby]"):
            references = element.get("aria-labelledby", "").split()
            if not references:
                self.add(
                    "aria.labelledby_empty",
                    relative,
                    "aria-labelledby must contain at least one ID reference.",
                    _line(element),
                )
                continue
            for identifier in references:
                targets = ids.get(identifier, [])
                if len(targets) != 1:
                    self.add(
                        "aria.labelledby_target",
                        relative,
                        f"aria-labelledby target {identifier!r} must resolve exactly once.",
                        _line(element),
                    )
                elif not _element_text(targets[0]):
                    self.add(
                        "aria.labelledby_text",
                        relative,
                        f"aria-labelledby target {identifier!r} has no accessible text.",
                        _line(element),
                    )

    @staticmethod
    def _is_focusable_target(element: Any) -> bool:
        tabindex = element.get("tabindex")
        if tabindex is not None:
            try:
                int(tabindex.strip())
            except (TypeError, ValueError):
                return False
            return True
        tag = _local_name(element)
        if element.get("disabled") is not None:
            return False
        if tag in {"button", "select", "textarea"}:
            return True
        if tag == "input" and element.get("type", "").lower() != "hidden":
            return True
        if tag in {"a", "area"} and element.get("href"):
            return True
        return False

    def _audit_skip_link(self, path: Path, tree: Any, main: Any, ids: dict[str, list[Any]]) -> None:
        relative = self.rel(path)
        # lxml may hand out different Python proxy objects for the same node on
        # separate XPath/iteration calls, so document order is keyed by XPath.
        order = {tree.getpath(element): index for index, element in enumerate(tree.iter())}
        main_order = order.get(tree.getpath(main), sys.maxsize)
        main_path = tree.getpath(main)
        functional = False
        for anchor in tree.xpath("//*[local-name()='a' and starts-with(@href, '#')]"):
            if order.get(tree.getpath(anchor), sys.maxsize) >= main_order:
                continue
            if _is_hidden(anchor) or anchor.get("tabindex", "").strip() == "-1":
                continue
            fragment = unquote(anchor.get("href", "")[1:])
            targets = ids.get(fragment, [])
            name = _element_text(anchor) or self._accessible_name(anchor, ids)
            if len(targets) != 1 or not name:
                continue
            target = targets[0]
            target_path = tree.getpath(target)
            is_main_target = target_path == main_path or target_path.startswith(main_path + "/")
            if is_main_target and not _is_hidden(target) and self._is_focusable_target(target):
                functional = True
                break
        if not functional:
            self.add(
                "navigation.skip_link",
                relative,
                "A visible, named, pre-main skip link must resolve to a focusable target in the sole main landmark.",
            )

    def _audit_headings(self, path: Path, tree: Any) -> None:
        relative = self.rel(path)
        headings: list[tuple[int, Any]] = []
        for element in tree.xpath("//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]"):
            if _is_hidden(element):
                continue
            level = int(_local_name(element)[1])
            headings.append((level, element))
            if not _element_text(element):
                self.add("heading.empty", relative, "Visible headings must have text.", _line(element))
        if not headings:
            self.add("heading.none", relative, "Document must have a visible heading hierarchy.")
            return
        if headings[0][0] != 1:
            self.add("heading.first_level", relative, "The first visible heading must be h1.", _line(headings[0][1]))
        h1_count = sum(level == 1 for level, _ in headings)
        if h1_count != 1:
            self.add("heading.h1_count", relative, "Document must have exactly one visible h1.")
        previous = headings[0][0]
        for level, element in headings[1:]:
            if level > previous + 1:
                self.add(
                    "heading.jump",
                    relative,
                    f"Heading level jumps from h{previous} to h{level}.",
                    _line(element),
                )
            previous = level

    def _audit_references(self, path: Path, tree: Any) -> None:
        relative = self.rel(path)
        for element in tree.iter():
            if not isinstance(getattr(element, "tag", None), str):
                continue
            if _local_name(element) == "base":
                self.add(
                    "html.base",
                    relative,
                    "base elements are forbidden because all reader links must resolve from their physical file.",
                    _line(element),
                )
            for raw_name, value in element.attrib.items():
                name = _attribute_local_name(raw_name)
                if name in URI_ATTRIBUTES:
                    if name == "href" and _local_name(element) == "a":
                        self._audit_anchor_href(path, element, value.strip(), relative)
                    else:
                        self._audit_uri(path, value.strip(), relative, _line(element))
                elif name == "srcset":
                    for candidate in self._srcset_candidates(value):
                        self._audit_uri(path, candidate, relative, _line(element))
            style = element.get("style", "")
            if style:
                self._audit_css_text(path, style, relative, _line(element))
            if _local_name(element) in {"script", "style"}:
                content = element.text or ""
                if NETWORK_TEXT_RE.search(content):
                    self.add("url.external", relative, "Executable style/script text contains a network URL.", _line(element))
                if _local_name(element) == "style":
                    self._audit_css_text(path, content, relative, _line(element))
        refresh_nodes = tree.xpath(
            "//*[local-name()='meta' and translate(@http-equiv, 'REFSH', 'refsh')='refresh']"
        )
        for element in refresh_nodes:
            content = element.get("content", "")
            match = re.search(r"(?i)\burl\s*=\s*([^;]+)$", content)
            if match:
                self._audit_uri(path, match.group(1).strip(" '\""), relative, _line(element))

    def _audit_static_code(self) -> None:
        for css_path in (item for item in self.files if item.suffix.casefold() == ".css"):
            try:
                css = css_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            self._audit_css_text(css_path, css, self.rel(css_path), 0)
        for script_path in (item for item in self.files if item.suffix.casefold() in {".js", ".mjs"}):
            try:
                script = script_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if NETWORK_TEXT_RE.search(script):
                self.add(
                    "url.external",
                    self.rel(script_path),
                    "Release JavaScript contains a network URL.",
                )

    @staticmethod
    def _srcset_candidates(value: str) -> Iterator[str]:
        if value.lstrip().lower().startswith("data:"):
            return
        for part in value.split(","):
            candidate = part.strip().split()
            if candidate:
                yield candidate[0]

    def _audit_css_text(self, base: Path, css: str, display: str, line: int) -> None:
        references = [match.group(2).strip() for match in CSS_URL_RE.finditer(css)]
        references.extend(match.group(1).strip() for match in CSS_IMPORT_RE.finditer(css))
        for reference in references:
            self._audit_uri(base, reference, display, line)

    def _audit_anchor_href(self, base: Path, anchor: Any, value: str, display: str) -> None:
        if not NETWORK_URI_RE.search(value):
            self._audit_uri(base, value, display, _line(anchor))
            return
        rel_tokens = {token.casefold() for token in anchor.get("rel", "").split()}
        missing = sorted(EXTERNAL_ANCHOR_REL - rel_tokens)
        parsed = urlsplit(value)
        safe_https_target = (
            parsed.scheme.casefold() == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
        )
        if missing:
            self.add(
                "url.external_anchor_rel",
                display,
                f"External anchors require rel tokens {sorted(EXTERNAL_ANCHOR_REL)}; missing={missing}.",
                _line(anchor),
            )
            return
        if not safe_https_target:
            self.add(
                "url.external",
                display,
                "Qualified external anchors must use an absolute credential-free HTTPS URL.",
                _line(anchor),
            )
            return
        # A qualified outbound anchor is optional navigation, not a
        # runtime dependency. It is deliberately not counted as an internal
        # reference and no network fetch is required to render the reader.

    def _audit_uri(self, base: Path, value: str, display: str, line: int) -> None:
        if not value:
            return
        if NETWORK_URI_RE.search(value):
            self.add("url.external", display, "Network URL is forbidden in the offline reader.", line)
            return
        parsed = urlsplit(value)
        scheme = parsed.scheme.lower()
        if scheme:
            if scheme == "data":
                if not re.match(r"(?i)^data:(?:image/(?:avif|gif|jpeg|png|svg\+xml|webp)|font/)", value):
                    self.add("url.data_type", display, "Only embedded image or font data URLs are allowed.", line)
                return
            self.add("url.scheme", display, f"Non-local URI scheme {scheme!r} is forbidden.", line)
            return
        if parsed.netloc:
            self.add("url.external", display, "Protocol-relative or authority-bearing URL is forbidden.", line)
            return
        if "\\" in parsed.path:
            self.add("url.backslash", display, "Internal URLs must use forward slashes.", line)
            return
        target = self._resolve_local_target(base, parsed.path)
        self.link_count += 1
        if target is None:
            self.add("link.escape", display, f"Internal reference {value!r} escapes or cannot resolve within the site.", line)
            return
        if not target.is_file():
            self.add("link.missing", display, f"Internal reference {value!r} has no release file target.", line)
            return
        if parsed.fragment:
            fragment = unquote(parsed.fragment)
            ids = self._ids_for_target(target)
            if fragment not in ids:
                self.add("link.fragment_missing", display, f"Fragment {fragment!r} does not exist in {self.rel(target)!r}.", line)

    def _resolve_local_target(self, base: Path, url_path: str) -> Path | None:
        decoded = unquote(url_path)
        if decoded.startswith("/"):
            candidate = self.root / decoded.lstrip("/")
        elif not decoded:
            candidate = base.resolve()
        else:
            candidate = base.resolve().parent / decoded
        try:
            candidate = candidate.resolve()
            candidate.relative_to(self.root)
        except (OSError, ValueError):
            return None
        if candidate.is_dir() or decoded.endswith("/"):
            candidate = candidate / "index.html"
        elif not candidate.exists() and not Path(decoded).suffix:
            directory_index = candidate / "index.html"
            html_sibling = candidate.with_suffix(".html")
            if directory_index.is_file():
                candidate = directory_index
            elif html_sibling.is_file():
                candidate = html_sibling
        try:
            candidate.resolve().relative_to(self.root)
        except (OSError, ValueError):
            return None
        return candidate.resolve()

    def _ids_for_target(self, target: Path) -> set[str]:
        target = target.resolve()
        if target in self.document_ids:
            return self.document_ids[target]
        suffix = target.suffix.casefold()
        if suffix in {".htm", ".html", ".xhtml"} and target in self.documents:
            ids = {element.get("id") for element in self.documents[target].xpath("//*[@id]")}
            self.document_ids[target] = {identifier for identifier in ids if identifier}
            return self.document_ids[target]
        if suffix in {".svg", ".xml"} and etree is not None:
            try:
                parser = etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True, recover=False)
                root = etree.parse(str(target), parser)
                return {element.get("id") for element in root.xpath("//*[@id]") if element.get("id")}
            except (OSError, etree.XMLSyntaxError):
                return set()
        return set()

    def _audit_math(self, path: Path, tree: Any) -> None:
        relative = self.rel(path)
        math_nodes = tree.xpath("//*[local-name()='math']")
        self.math_count += len(math_nodes)
        for math in math_nodes:
            tag = math.tag if isinstance(math.tag, str) else ""
            namespace = tag[1:].split("}", 1)[0] if tag.startswith("{") else math.get("xmlns", "")
            if namespace != MATHML_NAMESPACE:
                self.add(
                    "math.namespace",
                    relative,
                    f"Native MathML must declare the {MATHML_NAMESPACE!r} namespace.",
                    _line(math),
                )
            children = [child for child in math if isinstance(getattr(child, "tag", None), str)]
            if not children:
                self.add("math.empty", relative, "MathML math elements must contain structured child elements.", _line(math))
            if math.xpath(".//*[local-name()='img' or local-name()='mglyph']"):
                self.add("math.image_glyph", relative, "MathML must not depend on raster/image-only glyphs.", _line(math))
            try:
                serialised = etree.tostring(math, encoding="utf-8", method="xml", with_tail=False)
                parser = etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True, recover=False)
                parsed = etree.fromstring(serialised, parser)
                if _local_name(parsed) != "math":
                    raise etree.XMLSyntaxError("not a math root", 0, 0, 0)
            except (ValueError, etree.XMLSyntaxError):
                self.add("math.parse", relative, "MathML subtree is not well-formed XML.", _line(math))
        for candidate in tree.xpath(
            "//*[@role='math' or contains(concat(' ',normalize-space(@class),' '),' math ')]"
        ):
            if _local_name(candidate) == "math" or candidate.xpath(".//*[local-name()='math']"):
                continue
            self.add(
                "math.fallback",
                relative,
                "Math-designated content must contain native namespaced MathML, not a text or image fallback.",
                _line(candidate),
            )

    def _audit_images(self, path: Path, tree: Any, ids: dict[str, list[Any]]) -> None:
        relative = self.rel(path)
        for image in tree.xpath("//*[local-name()='img']"):
            self.image_count += 1
            alt = image.get("alt")
            decorative = image.get("role", "").lower() in {"none", "presentation"} or image.get("aria-hidden", "").lower() == "true"
            if alt is None:
                self.add("image.alt_missing", relative, "Every img needs alt text or explicit decorative semantics.", _line(image))
            elif not alt.strip() and not decorative:
                self.add("image.alt_empty", relative, "Empty img alt requires role=presentation/none or aria-hidden=true.", _line(image))
            token_source = " ".join(
                [
                    image.get("class", ""),
                    image.get("role", ""),
                    image.get("src", ""),
                    alt or "",
                ]
            )
            ancestor_math = any(
                _local_name(ancestor) == "math"
                or MATH_IMAGE_RE.search(ancestor.get("class", "") or "")
                or ancestor.get("role", "").lower() == "math"
                for ancestor in image.iterancestors()
            )
            latex_alt = bool(re.search(r"(?:\\(?:frac|sum|int|sqrt|begin)\b|\\\(|\\\)|\$[^$]+\$)", alt or ""))
            if ancestor_math or MATH_IMAGE_RE.search(token_source) or latex_alt:
                self.add("math.image_only", relative, "Image appears to encode mathematical notation instead of native MathML.", _line(image))

        for svg in tree.xpath("//*[local-name()='svg']"):
            name = self._accessible_name(svg, ids)
            if not name:
                titles = svg.xpath("./*[local-name()='title']")
                name = _element_text(titles[0]) if titles else ""
            decorative = svg.get("role", "").lower() in {"none", "presentation"} or svg.get("aria-hidden", "").lower() == "true"
            if not name and not decorative:
                self.add("svg.name_missing", relative, "Inline SVG needs an accessible name or explicit decorative semantics.", _line(svg))
            svg_tokens = " ".join([svg.get("class", ""), svg.get("role", ""), svg.get("id", "")])
            svg_math = svg.get("role", "").lower() == "math" or bool(MATH_IMAGE_RE.search(svg_tokens))
            svg_math = svg_math or any(
                ancestor.get("role", "").lower() == "math"
                or bool(MATH_IMAGE_RE.search(ancestor.get("class", "") or ""))
                for ancestor in svg.iterancestors()
            )
            if svg_math:
                self.add("math.image_only", relative, "SVG appears to encode mathematical notation instead of native MathML.", _line(svg))

        for control in tree.xpath("//*[local-name()='input' and translate(@type, 'IMAGE', 'image')='image']"):
            self.image_count += 1
            if not _normalise_space(control.get("alt", "")):
                self.add("image.input_alt", relative, "Image input controls require nonempty alt text.", _line(control))

        for obj in tree.xpath("//*[local-name()='object']"):
            media_type = obj.get("type", "").lower()
            data = obj.get("data", "").lower()
            object_tokens = " ".join([obj.get("class", ""), obj.get("role", ""), data])
            object_math = obj.get("role", "").lower() == "math" or bool(MATH_IMAGE_RE.search(object_tokens))
            object_math = object_math or any(
                ancestor.get("role", "").lower() == "math"
                or bool(MATH_IMAGE_RE.search(ancestor.get("class", "") or ""))
                for ancestor in obj.iterancestors()
            )
            if object_math:
                self.add("math.object_fallback", relative, "Object fallback appears to encode mathematics instead of native MathML.", _line(obj))
            if media_type.startswith("image/") or data.endswith(".svg"):
                self.image_count += 1
                name = self._accessible_name(obj, ids) or _normalise_space(obj.get("title", "")) or _element_text(obj)
                if not name:
                    self.add("image.object_name", relative, "Image objects require an accessible name or text fallback.", _line(obj))

    def _audit_tables(self, path: Path, tree: Any, ids: dict[str, list[Any]]) -> None:
        relative = self.rel(path)
        for table in tree.xpath("//*[local-name()='table']"):
            self.table_count += 1
            captions = table.xpath("./*[local-name()='caption']")
            if len(captions) != 1 or not _element_text(captions[0]):
                self.add("table.caption", relative, "Every table requires exactly one nonempty caption.", _line(table))
            headers = table.xpath(".//*[local-name()='th']")
            if not headers:
                self.add("table.headers_missing", relative, "Every table requires semantic th header cells.", _line(table))
            header_ids = {header.get("id") for header in headers if header.get("id")}
            used_header_ids = {
                identifier
                for cell in table.xpath(".//*[local-name()='td' or local-name()='th']")
                for identifier in cell.get("headers", "").split()
            }
            for header in headers:
                scope = header.get("scope", "").lower()
                identifier = header.get("id", "")
                if scope and scope not in {"row", "col", "rowgroup", "colgroup"}:
                    self.add("table.header_scope", relative, f"Invalid th scope value {scope!r}.", _line(header))
                elif not scope and (not identifier or identifier not in used_header_ids):
                    self.add("table.header_semantics", relative, "Each th requires a valid scope or an ID used by headers attributes.", _line(header))
            for cell in table.xpath(".//*[local-name()='td' or local-name()='th']"):
                referenced = cell.get("headers", "").split()
                for identifier in referenced:
                    if identifier not in header_ids:
                        self.add("table.headers_target", relative, f"Table headers reference {identifier!r}, which is not a th ID in this table.", _line(cell))

    def _audit_markers(self, path: Path, tree: Any) -> None:
        relative = self.rel(path)
        text = _visible_text(tree)
        if not re.search(r"(?i)\bCC\s+BY-SA\s+4\.0\b", text):
            self.add("provenance.license", relative, "Visible text must state CC BY-SA 4.0.")
        if MODEL_MARKER not in text:
            self.add("provenance.model", relative, f"Visible text must state {MODEL_MARKER!r}.")
        lower = text.casefold()
        if NONENDORSEMENT_MARKER not in lower:
            self.add(
                "provenance.nonendorsement",
                relative,
                f"Visible text must contain the standardized phrase {NONENDORSEMENT_MARKER!r}.",
            )

    def _audit_standalone_svgs(self) -> None:
        if etree is None:
            return
        for path in (item for item in self.files if item.suffix.casefold() == ".svg"):
            relative = self.rel(path)
            self.svg_count += 1
            try:
                parser = etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True, recover=False)
                tree = etree.parse(str(path), parser)
            except (OSError, etree.XMLSyntaxError):
                self.add("svg.parse", relative, "Standalone SVG is not well-formed XML.")
                continue
            root = tree.getroot()
            if _local_name(root) != "svg":
                self.add("svg.root", relative, "SVG asset must have an svg root element.")
                continue
            decorative = root.get("role", "").lower() in {"none", "presentation"} or root.get("aria-hidden", "").lower() == "true"
            aria = _normalise_space(root.get("aria-label", ""))
            titles = root.xpath("./*[local-name()='title']")
            title = _element_text(titles[0]) if titles else ""
            labelledby = root.get("aria-labelledby", "").split()
            id_elements: dict[str, list[Any]] = {}
            for element in tree.xpath("//*[@id]"):
                id_elements.setdefault(element.get("id"), []).append(element)
            for identifier, elements in sorted(id_elements.items()):
                if len(elements) > 1:
                    self.add("id.duplicate", relative, f"SVG ID {identifier!r} occurs more than once.", _line(elements[1]))
            labelled = bool(labelledby)
            for identifier in labelledby:
                targets = id_elements.get(identifier, [])
                if len(targets) != 1:
                    labelled = False
                    self.add(
                        "aria.labelledby_target",
                        relative,
                        f"SVG aria-labelledby target {identifier!r} must resolve exactly once.",
                        _line(root),
                    )
                elif not _element_text(targets[0]):
                    labelled = False
                    self.add(
                        "aria.labelledby_text",
                        relative,
                        f"SVG aria-labelledby target {identifier!r} has no accessible text.",
                        _line(root),
                    )
            if not (decorative or aria or title or labelled):
                self.add("svg.name_missing", relative, "Standalone SVG needs a title/ARIA name or explicit decorative semantics.")
            root_tokens = " ".join([root.get("class", ""), root.get("role", ""), root.get("id", ""), path.name])
            if root.get("role", "").lower() == "math" or MATH_IMAGE_RE.search(root_tokens):
                self.add("math.image_only", relative, "Standalone SVG appears to encode mathematics instead of native MathML.", _line(root))
            for element in tree.iter():
                if not isinstance(getattr(element, "tag", None), str):
                    continue
                for raw_name, value in element.attrib.items():
                    name = _attribute_local_name(raw_name)
                    if name in URI_ATTRIBUTES:
                        self._audit_uri(path, value.strip(), relative, _line(element))
                    elif name == "srcset":
                        for candidate in self._srcset_candidates(value):
                            self._audit_uri(path, candidate, relative, _line(element))
                style = element.get("style", "")
                if style:
                    self._audit_css_text(path, style, relative, _line(element))
                if _local_name(element) in {"script", "style"}:
                    content = element.text or ""
                    if NETWORK_TEXT_RE.search(content):
                        self.add("url.external", relative, "SVG style/script text contains a network URL.", _line(element))
                    if _local_name(element) == "style":
                        self._audit_css_text(path, content, relative, _line(element))

    def _audit_route_map(self) -> None:
        display = self.route_map.name
        if not self.route_map.is_file():
            self.add("routes.missing", display, "Backend route map does not exist.")
            return
        try:
            raw = self.route_map.read_bytes()
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            self.add("routes.utf8", display, "Backend route map is not valid UTF-8.")
            return
        except OSError as exc:
            self.add("routes.read_error", display, f"Could not read route map: {exc.__class__.__name__}.")
            return
        self.route_map_sha256 = _sha256_bytes(raw)
        if raw.startswith(b"\xef\xbb\xbf"):
            self.add("routes.bom", display, "Route map must be UTF-8 without a byte-order mark.")
        if b"\r" in raw:
            self.add("routes.newlines", display, "Route map must use LF newlines for cross-platform determinism.")
        if raw and not raw.endswith(b"\n"):
            self.add("routes.final_newline", display, "Route map must end with one LF newline.")

        scan_text = text + "\n" + text.replace("\\\\", "\\")
        for pattern in LOCAL_PATH_PATTERNS:
            if pattern.search(scan_text):
                self.add("routes.privacy.local_path", display, "Route map contains an absolute or machine-local path.")
                break
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(scan_text):
                self.add("routes.privacy.credential", display, "Route map contains a credential-like secret.")
                break
        for pattern in RESIDUE_TEXT_PATTERNS:
            if pattern.search(scan_text):
                self.add("routes.residue", display, "Route map contains an unfinished-work marker.")
                break

        records: list[Any] = []
        parse_failed = False
        lines = text.splitlines()
        for line_number, line in enumerate(lines, start=1):
            if not line:
                self.add("routes.blank_line", display, "Canonical JSONL must not contain blank lines.", line_number)
                parse_failed = True
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                self.add("routes.parse", display, "Each route-map line must be one valid JSON object.", line_number)
                parse_failed = True
        if not parse_failed:
            canonical = "".join(
                json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                for record in records
            ).encode("utf-8")
            if raw != canonical:
                self.add(
                    "routes.serialization",
                    display,
                    "Route map is not canonical compact UTF-8/LF JSONL with sorted object keys.",
                )
        if not records:
            self.add("routes.empty", display, "Backend route map contains no route records.")
            return

        order_ids = [record.get("id") for record in records if isinstance(record, dict) and isinstance(record.get("id"), str)]
        if len(order_ids) == len(records) and order_ids != sorted(order_ids):
            self.add("routes.order", display, "Route records must be ordered by ascending stable ID.")

        seen: dict[str, int] = {}
        routed_pages: set[Path] = set()
        route_base = self.root / "__route_map_base__.json"
        for index, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                self.add("routes.object", display, f"Route record {index} is not an object.", index)
                continue
            keys = set(record)
            if keys != ROUTE_FIELDS:
                missing = sorted(ROUTE_FIELDS - keys)
                extra = sorted(keys - ROUTE_FIELDS)
                self.add(
                    "routes.fields",
                    display,
                    f"Route record {index} field mismatch; missing={missing}, extra={extra}.",
                    index,
                )

            stable_id = record.get("id")
            if not isinstance(stable_id, str) or not stable_id or stable_id.strip() != stable_id or re.search(r"[\s#?]", stable_id):
                self.add("routes.id", display, f"Route record {index} has a noncanonical stable ID.", index)
                stable_id = ""
            elif stable_id in seen:
                self.add("routes.id_duplicate", display, f"Stable ID {stable_id!r} is duplicated in records {seen[stable_id]} and {index}.", index)
            else:
                seen[stable_id] = index

            if record.get("record_type") != "html_route":
                self.add("routes.record_type", display, f"Route record {index} must have record_type='html_route'.", index)
            if record.get("locale") != "id-ID":
                self.add("routes.locale", display, f"Route record {index} must have locale='id-ID'.", index)

            route = record.get("route")
            if not isinstance(route, str) or (route and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", route)):
                self.add("routes.route", display, f"Route record {index} has a noncanonical route slug.", index)
                route = None
            output_path = record.get("output_path")
            href = record.get("href")
            if not isinstance(output_path, str):
                self.add("routes.output_path", display, f"Route record {index} output_path must be a string.", index)
                output_path = ""
            if not isinstance(href, str):
                self.add("routes.href", display, f"Route record {index} href must be a string.", index)
                href = ""

            if route is not None:
                expected_output = f"{route}/index.html" if route else "index.html"
                if output_path != expected_output:
                    self.add(
                        "routes.output_path",
                        display,
                        f"Route record {index} output_path must be {expected_output!r}.",
                        index,
                    )
                expected_href = f"{expected_output}#{stable_id}" if stable_id else ""
                if href != expected_href:
                    self.add(
                        "routes.href",
                        display,
                        f"Route record {index} href must equal output_path plus its own stable-ID fragment.",
                        index,
                    )

            self.route_count += 1
            if href:
                self._audit_uri(route_base, href, display, index)
            if output_path:
                target = self._resolve_local_target(route_base, output_path)
                if target is not None and target.is_file() and target.suffix.casefold() in {".htm", ".html", ".xhtml"}:
                    routed_pages.add(target.resolve())

        for document_path in sorted(self.documents, key=self.rel):
            if document_path.resolve() not in routed_pages:
                self.add(
                    "routes.page_uncovered",
                    self.rel(document_path),
                    "Every HTML document must be represented by at least one canonical route record.",
                )

    def _audit_manifest(self) -> None:
        display = self.rel(self.manifest_path)
        if not self.manifest_is_local:
            self.add("manifest.path_escape", display, "Manifest path must remain inside the site root.")
            return
        if not self.manifest_path.is_file():
            self.add("manifest.missing", display, "Site root must contain MANIFEST.csv.")
            return
        try:
            raw = self.manifest_path.read_bytes()
        except OSError as exc:
            self.add("manifest.read_error", display, f"Could not read manifest: {exc.__class__.__name__}.")
            return
        self.manifest_sha256 = _sha256_bytes(raw)
        if raw.startswith(b"\xef\xbb\xbf"):
            self.add("manifest.bom", display, "Manifest must be UTF-8 without a byte-order mark.")
        if b"\r" in raw:
            self.add("manifest.newlines", display, "Manifest must use LF newlines for cross-platform determinism.")
        if raw and not raw.endswith(b"\n"):
            self.add("manifest.final_newline", display, "Manifest must end with one LF newline.")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            self.add("manifest.utf8", display, "Manifest is not valid UTF-8.")
            return
        reader = csv.DictReader(io.StringIO(text, newline=""))
        if reader.fieldnames != MANIFEST_HEADER:
            self.add("manifest.header", display, f"Manifest header must be exactly {','.join(MANIFEST_HEADER)!r}.")
            return
        entries: dict[str, tuple[int, str]] = {}
        row_paths: list[str] = []
        for row_number, row in enumerate(reader, start=2):
            raw_path = row.get("path", "")
            normalised = _normalised_relative_path(raw_path)
            if normalised is None:
                self.add("manifest.path", display, f"Row {row_number} has a noncanonical relative path.")
                continue
            if normalised == self.rel(self.manifest_path):
                self.add("manifest.self", display, "Manifest must not list itself.", row_number)
            if normalised in entries:
                self.add("manifest.duplicate", display, f"Manifest path {normalised!r} is duplicated.", row_number)
                continue
            try:
                size = int(row.get("bytes", ""))
                if str(size) != row.get("bytes", "") or size < 0:
                    raise ValueError
            except ValueError:
                self.add("manifest.bytes", display, f"Row {row_number} has a noncanonical byte count.")
                continue
            digest = row.get("sha256", "")
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                self.add("manifest.sha256", display, f"Row {row_number} has a noncanonical SHA-256 value.")
                continue
            entries[normalised] = (size, digest)
            row_paths.append(normalised)
        if row_paths != sorted(row_paths):
            self.add("manifest.order", display, "Manifest rows must be in ascending POSIX-path order.")
        canonical = io.StringIO(newline="")
        canonical_writer = csv.writer(canonical, lineterminator="\n")
        canonical_writer.writerow(MANIFEST_HEADER)
        for relative in row_paths:
            if relative in entries:
                size, digest = entries[relative]
                canonical_writer.writerow([relative, size, digest])
        if raw != canonical.getvalue().encode("utf-8"):
            self.add(
                "manifest.serialization",
                display,
                "Manifest bytes are not the canonical UTF-8/LF CSV serialization.",
            )

        actual_paths = {
            self.rel(path): path
            for path in self.files
            if path.resolve() != self.manifest_path
        }
        for relative in sorted(set(actual_paths) - set(entries)):
            self.add("manifest.unlisted", relative, "Release file is absent from MANIFEST.csv.")
        for relative in sorted(set(entries) - set(actual_paths)):
            self.add("manifest.missing_file", relative, "Manifest entry has no release file.")
        inventory_lines: list[str] = []
        for relative in sorted(set(entries) & set(actual_paths)):
            expected_size, expected_hash = entries[relative]
            target = actual_paths[relative]
            try:
                actual_size = target.stat().st_size
                actual_hash = _sha256(target)
            except OSError as exc:
                self.add("manifest.file_read", relative, f"Could not hash release file: {exc.__class__.__name__}.")
                continue
            if actual_size != expected_size:
                self.add("manifest.size_mismatch", relative, f"Manifest says {expected_size} bytes; file has {actual_size}.")
            if actual_hash != expected_hash:
                self.add("manifest.hash_mismatch", relative, "Manifest SHA-256 does not match release bytes.")
            inventory_lines.append(f"{relative}\0{actual_size}\0{actual_hash}\n")
        self.inventory_sha256 = _sha256_bytes("".join(inventory_lines).encode("utf-8"))


def _write_manifest(root: Path) -> None:
    rows: list[tuple[str, int, str]] = []
    manifest = root / "MANIFEST.csv"
    for path in sorted((item for item in root.rglob("*") if item.is_file() and item != manifest), key=lambda item: item.relative_to(root).as_posix()):
        rows.append((path.relative_to(root).as_posix(), path.stat().st_size, _sha256(path)))
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(MANIFEST_HEADER)
    writer.writerows(rows)
    manifest.write_bytes(buffer.getvalue().encode("utf-8"))


def self_test() -> dict[str, Any]:
    """Run a bounded passing fixture, then prove representative defects fail."""
    if etree is None:
        return dependency_report()
    with tempfile.TemporaryDirectory(prefix="o008-html-qa-") as temporary:
        base = Path(temporary)
        site = base / "site"
        site.mkdir()
        route_map = base / "routes.jsonl"
        html = """<!doctype html>
<html lang="id"><head><meta charset="utf-8"><title>Uji</title></head><body>
<a href="#SELFTEST">Lewati ke isi utama</a>
<span id="nav-label">Navigasi utama</span><nav aria-labelledby="nav-label"><a href="#bagian">Bagian</a></nav>
<main id="SELFTEST" tabindex="-1"><h1>Uji pembaca</h1><h2 id="bagian">Bagian</h2>
<p><math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mi>x</mi><mo>+</mo><mn>1</mn></mrow></math></p>
<table><caption>Nilai uji</caption><tr><th id="header-x">x</th></tr><tr><td headers="header-x">1</td></tr></table>
</main><footer><p><a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="license external noopener noreferrer">CC BY-SA 4.0</a>. Publikasi ini tidak menyiratkan dukungan.</p>
<p>OpenAI Codex gpt-5.6-sol, Ultra</p></footer></body></html>
"""
        index = site / "index.html"
        index.write_bytes(html.encode("utf-8"))
        route_records = [
            {
                "href": "index.html#SELFTEST",
                "id": "SELFTEST",
                "locale": "id-ID",
                "output_path": "index.html",
                "record_type": "html_route",
                "route": "",
            },
            {
                "href": "index.html#bagian",
                "id": "bagian",
                "locale": "id-ID",
                "output_path": "index.html",
                "record_type": "html_route",
                "route": "",
            },
        ]
        valid_route_bytes = (
            "".join(
                json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                for record in route_records
            ).encode("utf-8")
        )
        route_map.write_bytes(valid_route_bytes)
        _write_manifest(site)
        passing = ReaderAuditor(site, route_map).audit()
        if not passing["passed"]:
            return {
                "details": passing,
                "passed": False,
                "schema_version": REPORT_SCHEMA,
                "self_test": "passing fixture was rejected",
            }

        route_map.write_bytes(valid_route_bytes.replace(b"\n", b"\r\n"))
        newline_rejected = ReaderAuditor(site, route_map).audit()
        newline_codes = {item["code"] for item in newline_rejected["findings"]}
        required_newline_codes = {"routes.newlines", "routes.serialization"}
        if newline_rejected["passed"] or not required_newline_codes.issubset(newline_codes):
            return {
                "observed_codes": sorted(newline_codes),
                "passed": False,
                "schema_version": REPORT_SCHEMA,
                "self_test": "noncanonical route-map newlines were not rejected",
            }
        route_map.write_bytes(valid_route_bytes)

        broken = html.replace(
            "<head>",
            '<head><base href="index.html"><script src="https://example.invalid/app.js"></script>',
        )
        broken = broken.replace('<a href="#SELFTEST"', '<a hidden href="#SELFTEST"')
        broken = broken.replace('aria-labelledby="nav-label"', 'aria-labelledby="missing-label"')
        broken = broken.replace(
            '<main id="SELFTEST"',
            '<a id="bagian" href="https://example.invalid/">rusak</a><main id="SELFTEST"',
        )
        broken = broken.replace(
            "</math></p>",
            '</math></p><math><mi>y</mi></math><span class="math">x + 1</span><svg role="math" aria-label="rumus"><title>rumus</title><path d="M0 0"/></svg><object role="math" aria-label="rumus"></object>',
        )
        broken = broken.replace(' headers="header-x"', "")
        broken = broken.replace("</main>", "<p>[[DIAGRAM:UNRESOLVED]]</p></main>")
        index.write_bytes(broken.encode("utf-8"))
        (site / "orphan").mkdir()
        (site / "orphan" / "index.html").write_bytes(html.encode("utf-8"))
        bad_routes = [dict(record) for record in reversed(route_records)]
        bad_routes[0]["locale"] = "en-US"
        bad_routes[0]["href"] = "index.html#SELFTEST"
        bad_routes[0]["debug_path"] = "C:" + "\\Users\\Selftest\\routes.jsonl"
        bad_routes[1]["record_type"] = "wrong_route_type"
        route_map.write_bytes(
            "".join(
                json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                for record in bad_routes
            ).encode("utf-8")
        )
        _write_manifest(site)
        rejected = ReaderAuditor(site, route_map).audit()
        codes = {item["code"] for item in rejected["findings"]}
        required = {
            "aria.labelledby_target",
            "html.base",
            "id.duplicate",
            "math.fallback",
            "math.image_only",
            "math.namespace",
            "math.object_fallback",
            "navigation.skip_link",
            "residue.text",
            "routes.fields",
            "routes.href",
            "routes.locale",
            "routes.order",
            "routes.page_uncovered",
            "routes.privacy.local_path",
            "routes.record_type",
            "table.header_semantics",
            "url.external",
            "url.external_anchor_rel",
        }
        all_codes = codes | newline_codes
        required |= required_newline_codes
        if rejected["passed"] or not required.issubset(all_codes):
            return {
                "observed_codes": sorted(all_codes),
                "passed": False,
                "schema_version": REPORT_SCHEMA,
                "self_test": "defective fixture was not rejected as expected",
            }
    return {
        "passed": True,
        "schema_version": REPORT_SCHEMA,
        "self_test": {
            "passing_fixture": "accepted",
            "representative_defects": sorted(required),
            "representative_fixture": "rejected",
        },
    }


def dependency_report() -> dict[str, Any]:
    return {
        "artifacts": {
            "inventory_sha256": "",
            "manifest_sha256": "",
            "route_map_sha256": "",
        },
        "counts": {
            "files": 0,
            "findings": 1,
            "html_documents": 0,
            "images": 0,
            "internal_references": 0,
            "mathml_elements": 0,
            "route_records": 0,
            "standalone_svgs": 0,
            "tables": 0,
        },
        "findings": [
            {
                "code": "dependency.lxml",
                "file": "html/qa_reader.py",
                "message": "lxml is required for strict offline HTML/MathML/SVG parsing; install lxml and rerun.",
            }
        ],
        "passed": False,
        "schema_version": REPORT_SCHEMA,
    }


def _emit(report: dict[str, Any], output: str) -> None:
    encoded = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if output == "-":
        sys.stdout.buffer.write(encoded)
    else:
        Path(output).write_bytes(encoded)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("site_root", nargs="?", type=Path, help="root of the generated static site")
    parser.add_argument("route_map", nargs="?", type=Path, help="canonical backend JSONL route map")
    parser.add_argument("--manifest", default="MANIFEST.csv", help="manifest filename relative to site root")
    parser.add_argument("--output", default="-", help="JSON report path, or - for stdout")
    parser.add_argument("--self-test", action="store_true", help="run bounded internal fixture tests")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if etree is None:
        report = dependency_report()
        _emit(report, arguments.output)
        return 2
    if arguments.self_test:
        report = self_test()
        _emit(report, arguments.output)
        return 0 if report.get("passed") else 1
    if arguments.site_root is None or arguments.route_map is None:
        build_parser().error("site_root and route_map are required unless --self-test is used")
    site_root = arguments.site_root.resolve()
    if arguments.output != "-":
        output = Path(arguments.output).resolve()
        try:
            output.relative_to(site_root)
        except ValueError:
            pass
        else:
            report = {
                "passed": False,
                "schema_version": REPORT_SCHEMA,
                "findings": [
                    {
                        "code": "output.inside_site",
                        "file": output.name,
                        "message": "Write the QA report outside the manifested site root.",
                    }
                ],
            }
            _emit(report, "-")
            return 2
    auditor = ReaderAuditor(site_root, arguments.route_map, arguments.manifest)
    report = auditor.audit()
    _emit(report, arguments.output)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
