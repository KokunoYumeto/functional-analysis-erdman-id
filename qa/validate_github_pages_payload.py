#!/usr/bin/env python3
"""Validate exact bytes, routes, rights, privacy, and reproducibility of the Pages payload."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import posixpath
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "PAGES_DEPLOYMENT_MANIFEST.csv"
MANIFEST_FIELDS = ["public_path", "role", "source_path", "bytes", "sha256"]


class ValidationError(RuntimeError):
    pass


class SurfaceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: set[str] = set()
        self.references: list[tuple[str, str]] = []
        self.meta_refresh: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value for name, value in attrs if value is not None}
        for key in ("id", "name"):
            if key in values:
                self.anchors.add(values[key])
        for key in ("href", "src", "xlink:href"):
            if key in values:
                self.references.append((key, values[key]))
        if tag.lower() == "meta" and values.get("http-equiv", "").lower() == "refresh":
            content = values.get("content", "")
            match = re.search(r"(?:^|;)\s*url\s*=\s*['\"]?([^'\";]+)", content, re.I)
            if match:
                self.meta_refresh.append(match.group(1).strip())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(raw: str) -> PurePosixPath:
    if not raw or "\\" in raw:
        raise ValidationError(f"unsafe public path: {raw!r}")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValidationError(f"unsafe public path: {raw!r}")
    return path


def read_manifest(payload: Path) -> tuple[bytes, list[dict[str, str]]]:
    manifest_path = payload / MANIFEST_NAME
    raw = manifest_path.read_bytes()
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != MANIFEST_FIELDS:
            raise ValidationError(f"unexpected public manifest schema: {reader.fieldnames}")
        rows = list(reader)
    paths = [safe_path(row["public_path"]) for row in rows]
    if len(paths) != len(set(paths)):
        raise ValidationError("duplicate public path")
    if paths != sorted(paths, key=lambda item: item.as_posix()):
        raise ValidationError("public manifest is not path-sorted")
    return raw, rows


def tree_identity(payload: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((p for p in payload.rglob("*") if p.is_file()), key=lambda p: p.relative_to(payload).as_posix()):
        rel = path.relative_to(payload).as_posix()
        data = path.read_bytes()
        digest.update(rel.encode("utf-8") + b"\0" + str(len(data)).encode("ascii") + b"\0" + hashlib.sha256(data).digest())
    return digest.hexdigest()


def resolve_internal(source: PurePosixPath, raw_url: str) -> tuple[PurePosixPath, str] | None:
    split = urlsplit(raw_url.strip())
    if split.scheme.lower() in {"http", "https", "mailto", "tel"} or split.netloc:
        return None
    if split.scheme:
        raise ValidationError(f"unsafe URL scheme in {source}: {raw_url}")
    if split.path.startswith("/"):
        raise ValidationError(f"domain-root URL would escape the repository base path in {source}: {raw_url}")
    decoded = unquote(split.path)
    joined = posixpath.normpath(posixpath.join(source.parent.as_posix(), decoded or source.name))
    if joined == ".." or joined.startswith("../"):
        raise ValidationError(f"relative URL escapes payload in {source}: {raw_url}")
    target = PurePosixPath(joined)
    if decoded.endswith("/"):
        target /= "index.html"
    return target, unquote(split.fragment)


def validate_payload(payload: Path, expected_manifest: Path | None) -> dict[str, object]:
    payload = payload.resolve()
    manifest_bytes, rows = read_manifest(payload)
    if expected_manifest is not None and expected_manifest.read_bytes() != manifest_bytes:
        raise ValidationError("payload manifest differs from tracked public manifest")

    declared = {PurePosixPath(row["public_path"]): row for row in rows}
    actual = {
        PurePosixPath(path.relative_to(payload).as_posix())
        for path in payload.rglob("*")
        if path.is_file() and path.name != MANIFEST_NAME
    }
    if actual != set(declared):
        raise ValidationError(
            f"payload inventory mismatch: missing={sorted(str(p) for p in set(declared)-actual)}, "
            f"extra={sorted(str(p) for p in actual-set(declared))}"
        )

    total_bytes = 0
    source_bytes_verified = 0
    for public_path, row in declared.items():
        data = (payload / Path(public_path.as_posix())).read_bytes()
        if len(data) != int(row["bytes"]) or sha256_bytes(data) != row["sha256"].lower():
            raise ValidationError(f"public manifest replay failed: {public_path}")
        total_bytes += len(data)
        source_path = row["source_path"]
        if source_path != "generated":
            local = (ROOT / source_path).resolve()
            if ROOT.resolve() not in local.parents:
                raise ValidationError(f"source path escapes lane: {source_path}")
            if local.read_bytes() != data:
                raise ValidationError(f"payload differs from canonical source: {public_path}")
            source_bytes_verified += len(data)

    html_paths = sorted(path for path in declared if path.suffix.lower() == ".html")
    surfaces: dict[PurePosixPath, SurfaceParser] = {}
    mathml_count = 0
    script_count = 0
    private_findings: list[str] = []
    secret_patterns = (
        re.compile(rb"C:\\Users\\", re.I),
        re.compile(rb"/Users/", re.I),
        re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
        re.compile(rb"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"),
    )
    for public_path in sorted(declared):
        data = (payload / Path(public_path.as_posix())).read_bytes()
        for pattern in secret_patterns:
            if pattern.search(data):
                private_findings.append(public_path.as_posix())
        if public_path.suffix.lower() == ".html":
            text = data.decode("utf-8")
            parser = SurfaceParser()
            parser.feed(text)
            surfaces[public_path] = parser
            mathml_count += text.count("<math")
            script_count += len(re.findall(r"<script\b", text, re.I))
    if private_findings:
        raise ValidationError(f"private-path or credential patterns found: {sorted(set(private_findings))}")
    if script_count:
        raise ValidationError(f"unexpected script elements: {script_count}")

    checked_references = 0
    for source, parser in surfaces.items():
        refs = parser.references + [("meta-refresh", url) for url in parser.meta_refresh]
        for _, raw_url in refs:
            resolved = resolve_internal(source, raw_url)
            if resolved is None:
                continue
            target, fragment = resolved
            if target not in declared:
                candidate = target / "index.html"
                if candidate in declared:
                    target = candidate
                else:
                    raise ValidationError(f"broken internal route in {source}: {raw_url} -> {target}")
            if fragment and target.suffix.lower() == ".html":
                target_parser = surfaces.get(target)
                if target_parser is None or fragment not in target_parser.anchors:
                    raise ValidationError(f"missing fragment target in {source}: {raw_url}")
            checked_references += 1

    css_url_pattern = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)
    for public_path in sorted(path for path in declared if path.suffix.lower() == ".css"):
        text = (payload / Path(public_path.as_posix())).read_text(encoding="utf-8")
        for _, raw_url in css_url_pattern.findall(text):
            if raw_url.startswith("data:"):
                continue
            resolved = resolve_internal(public_path, raw_url)
            if resolved is not None and resolved[0] not in declared:
                raise ValidationError(f"broken CSS route in {public_path}: {raw_url}")
            checked_references += 1

    source_index = (payload / "output" / "html" / "index.html").read_text(encoding="utf-8")
    companion_index = (payload / "output" / "html-companion" / "index.html").read_text(encoding="utf-8")
    for label, text in (("source", source_index), ("companion", companion_index)):
        for marker in ("CC BY-SA 4.0", "OpenAI Codex gpt-5.6-sol, Ultra", "tidak menyiratkan dukungan"):
            if marker not in text:
                raise ValidationError(f"missing {label} rights/provenance marker: {marker}")

    metadata = json.loads((payload / "PAGES_DEPLOYMENT_METADATA.json").read_text(encoding="utf-8"))
    if metadata.get("schema") != "o008.github-pages.deployment-metadata.v1" or metadata.get("status") != "complete":
        raise ValidationError("deployment metadata contract failed")
    if metadata.get("substantive_reader_bytes_changed") is not False:
        raise ValidationError("deployment metadata does not preserve reader-byte boundary")

    required = {
        PurePosixPath("index.html"),
        PurePosixPath("companion/index.html"),
        PurePosixPath("output/html/index.html"),
        PurePosixPath("output/html-companion/index.html"),
    }
    if not required.issubset(declared):
        raise ValidationError("required entry routes are absent")
    svg_count = sum(1 for path in declared if path.suffix.lower() == ".svg")
    if mathml_count < 10_000 or svg_count < 80:
        raise ValidationError(f"semantic surface census too small: mathml={mathml_count}, svg={svg_count}")

    return {
        "schema": "o008.github-pages.payload-validation.v1",
        "status": "pass",
        "payload": payload.relative_to(ROOT.resolve()).as_posix(),
        "manifest_rows": len(rows),
        "manifested_bytes": total_bytes,
        "manifest_bytes": len(manifest_bytes),
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "payload_file_count": len(rows) + 1,
        "payload_tree_sha256": tree_identity(payload),
        "canonical_source_bytes_verified": source_bytes_verified,
        "html_documents": len(html_paths),
        "mathml_elements": mathml_count,
        "svg_assets": svg_count,
        "internal_references_checked": checked_references,
        "script_elements": script_count,
        "findings": [],
    }


def compare_payloads(first: Path, second: Path) -> None:
    first_files = {p.relative_to(first).as_posix(): p for p in first.rglob("*") if p.is_file()}
    second_files = {p.relative_to(second).as_posix(): p for p in second.rglob("*") if p.is_file()}
    if set(first_files) != set(second_files):
        raise ValidationError("replay payload inventory differs")
    for rel in sorted(first_files):
        if first_files[rel].read_bytes() != second_files[rel].read_bytes():
            raise ValidationError(f"replay payload bytes differ: {rel}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True, type=Path)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--expected-manifest", type=Path, default=ROOT / "qa" / "GITHUB_PAGES_PUBLIC_MANIFEST.csv")
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    payload = args.payload if args.payload.is_absolute() else ROOT / args.payload
    compare = None if args.compare is None else (args.compare if args.compare.is_absolute() else ROOT / args.compare)
    expected = args.expected_manifest if args.expected_manifest.is_absolute() else ROOT / args.expected_manifest
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    try:
        report = validate_payload(payload, expected)
        if compare is not None:
            second = validate_payload(compare, expected)
            compare_payloads(payload.resolve(), compare.resolve())
            report["replay_payload_tree_sha256"] = second["payload_tree_sha256"]
            report["byte_identical_replay"] = True
    except Exception as exc:
        report = {
            "schema": "o008.github-pages.payload-validation.v1",
            "status": "fail",
            "error": f"{type(exc).__name__}: {exc}",
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 1
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
