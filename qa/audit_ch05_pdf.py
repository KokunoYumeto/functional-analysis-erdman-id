#!/usr/bin/env python3
"""Bounded machine audit for the cumulative Chapter 1--5 PDF."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.generic import ArrayObject, IndirectObject


def dereference(value: Any) -> Any:
    return value.get_object() if isinstance(value, IndirectObject) else value


def outline_count(items: list[Any]) -> int:
    count = 0
    for item in items:
        if isinstance(item, list):
            count += outline_count(item)
        else:
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    args = parser.parse_args()

    reader = PdfReader(args.pdf)
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
    internal_links = 0
    unresolved_internal_links = 0
    file_attachments = 0
    rich_media = 0

    for page in reader.pages:
        for annotation_ref in dereference(page.get("/Annots", [])) or []:
            annotation = dereference(annotation_ref)
            subtype = str(annotation.get("/Subtype", ""))
            annotation_subtypes[subtype] += 1
            if subtype == "/FileAttachment":
                file_attachments += 1
            if subtype in {"/RichMedia", "/Movie", "/Sound", "/Screen"}:
                rich_media += 1

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
                if not destination_resolves(destination):
                    unresolved_internal_links += 1

    names = dereference(root.get("/Names")) or {}
    mark_info = dereference(root.get("/MarkInfo")) or {}
    open_action = dereference(root.get("/OpenAction"))
    if isinstance(open_action, ArrayObject):
        open_action_kind = "GoTo-array"
    elif open_action:
        open_action_kind = str(open_action.get("/S", "dictionary"))
    else:
        open_action_kind = "none"

    result = {
        "pdf": str(args.pdf.resolve()),
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
        "unresolved_internal_links": unresolved_internal_links,
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
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
