#!/usr/bin/env python3
"""Audit navigation, fonts, actions, security, and accessibility truth of the final reader."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.generic import ArrayObject, IndirectObject


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "qa" / "FINAL_COMPANION_BUILD_RESULT.json"
PDF = ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf"
RESULT = ROOT / "qa" / "FINAL_COMPANION_PDF_SECURITY_NAVIGATION_AUDIT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dereference(value: Any) -> Any:
    return value.get_object() if isinstance(value, IndirectObject) else value


def outline_count(items: list[Any]) -> int:
    return sum(outline_count(item) if isinstance(item, list) else 1 for item in items)


def font_audit() -> dict[str, Any]:
    completed = subprocess.run(
        ["pdffonts", str(PDF)], check=True, capture_output=True, text=True
    )
    rows = []
    for line in completed.stdout.splitlines()[2:]:
        if not line.strip():
            continue
        match = re.match(
            r"^(?P<name>.{36}) (?P<type>.{17}) (?P<encoding>.{16}) "
            r"(?P<embedded>yes|no) (?P<subset>yes|no) (?P<unicode>yes|no)\s+"
            r"(?P<object>\d+)\s+(?P<generation>\d+)\s*$",
            line,
        )
        if match is None:
            raise SystemExit(f"could not parse pdffonts row: {line!r}")
        rows.append({key: value.strip() for key, value in match.groupdict().items()})
    return {
        "font_rows": len(rows),
        "all_embedded": all(row["embedded"] == "yes" for row in rows),
        "all_subset": all(row["subset"] == "yes" for row in rows),
        "all_unicode_mapped": all(row["unicode"] == "yes" for row in rows),
        "nonembedded": [row["name"] for row in rows if row["embedded"] != "yes"],
        "nonsubset": [row["name"] for row in rows if row["subset"] != "yes"],
        "without_unicode_map": [row["name"] for row in rows if row["unicode"] != "yes"],
    }


def main() -> None:
    build = json.loads(BUILD.read_text(encoding="utf-8-sig"))
    expected = build["pdf"]
    if PDF.stat().st_size != int(expected["bytes"]) or sha256(PDF) != expected["sha256"]:
        raise SystemExit("final PDF identity differs from deterministic build")
    reader = PdfReader(PDF)
    root = dereference(reader.trailer["/Root"])
    page_refs = {
        (page.indirect_reference.idnum, page.indirect_reference.generation): number
        for number, page in enumerate(reader.pages, start=1)
    }
    named = reader.named_destinations

    def destination_resolves(destination: Any) -> bool:
        destination = dereference(destination)
        if isinstance(destination, str):
            return destination in named or destination.lstrip("/") in named
        if isinstance(destination, ArrayObject) and destination:
            target = destination[0]
            if isinstance(target, IndirectObject):
                return (target.idnum, target.generation) in page_refs
            try:
                page_number = int(target)
            except (TypeError, ValueError):
                return False
            return 0 <= page_number < len(reader.pages)
        return False

    annotation_subtypes: Counter[str] = Counter()
    action_types: Counter[str] = Counter()
    uri_targets: set[str] = set()
    internal_links = unresolved = file_attachments = rich_media = 0
    for page in reader.pages:
        for annotation_ref in dereference(page.get("/Annots", [])) or []:
            annotation = dereference(annotation_ref)
            subtype = str(annotation.get("/Subtype", ""))
            annotation_subtypes[subtype] += 1
            file_attachments += int(subtype == "/FileAttachment")
            rich_media += int(subtype in {"/RichMedia", "/Movie", "/Sound", "/Screen"})
            action = dereference(annotation.get("/A"))
            destination = annotation.get("/Dest")
            if action:
                action_type = str(action.get("/S", ""))
                action_types[action_type] += 1
                if action_type == "/URI":
                    uri_targets.add(str(action.get("/URI", "")))
                elif action_type == "/GoTo":
                    destination = action.get("/D")
            if destination is not None:
                internal_links += 1
                unresolved += int(not destination_resolves(destination))

    names = dereference(root.get("/Names")) or {}
    mark_info = dereference(root.get("/MarkInfo")) or {}
    open_action = dereference(root.get("/OpenAction"))
    if isinstance(open_action, ArrayObject):
        open_action_kind = "GoTo-array"
    elif open_action:
        open_action_kind = str(open_action.get("/S", "dictionary"))
    else:
        open_action_kind = "none"
    fonts = font_audit()
    result = {
        "schema_version": "o008.final-companion-pdf-security-navigation-audit.v1",
        "pdf": {"path": PDF.relative_to(ROOT).as_posix(), "bytes": PDF.stat().st_size, "sha256": sha256(PDF)},
        "pages": len(reader.pages),
        "encrypted": reader.is_encrypted,
        "catalog_language": str(root.get("/Lang", "")),
        "metadata_stream": "/Metadata" in root,
        "tagged": "/StructTreeRoot" in root and bool(mark_info.get("/Marked", False)),
        "struct_tree_root": "/StructTreeRoot" in root,
        "mark_info": "/MarkInfo" in root,
        "outline_entries": outline_count(reader.outline),
        "named_destinations": len(named),
        "internal_links": internal_links,
        "unresolved_internal_links": unresolved,
        "unique_uri_targets": sorted(uri_targets),
        "annotation_subtypes": dict(sorted(annotation_subtypes.items())),
        "action_types": dict(sorted(action_types.items())),
        "open_action": open_action_kind,
        "acroform": "/AcroForm" in root,
        "embedded_files_name_tree": "/EmbeddedFiles" in names,
        "javascript_name_tree": "/JavaScript" in names,
        "file_attachment_annotations": file_attachments,
        "rich_media_annotations": rich_media,
        "launch_actions": action_types.get("/Launch", 0),
        "javascript_actions": action_types.get("/JavaScript", 0),
        "fonts": fonts,
    }
    failures = []
    if len(reader.pages) != int(build["pages"]) or reader.is_encrypted or unresolved:
        failures.append("page, encryption, or destination failure")
    if result["catalog_language"] != "id-ID":
        failures.append("catalog language")
    if any((result["acroform"], result["embedded_files_name_tree"], result["javascript_name_tree"], file_attachments, rich_media, result["launch_actions"], result["javascript_actions"])):
        failures.append("unexpected active or embedded content")
    if not (fonts["all_embedded"] and fonts["all_subset"] and fonts["all_unicode_mapped"]):
        failures.append("font embedding, subsetting, or Unicode mapping")
    result["accessibility_limitation"] = (
        "PDF is honestly untagged; the semantic MathML HTML readers are the accessible companion surfaces."
    )
    result["failures"] = failures
    result["status"] = "pass" if not failures else "fail"
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
