#!/usr/bin/env python3
r"""Chapter 3 math extraction with text-aware nested-dollar handling.

Erdman's source uses constructions such as
``$...\text{ for all $x \in V$}...$``.  The inner dollar pair is valid inside
the text payload but must not terminate the surrounding math surface.  This
module keeps the outer surface intact and retains embedded math in the
locale-neutral comparison key while discarding translatable prose.
"""

from __future__ import annotations

import re

import generate_ch01_backend as shared


def _is_unescaped(text: str, position: int) -> bool:
    backslashes = 0
    cursor = position - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 0


def _balanced_brace_end(text: str, opening_brace: int) -> int:
    if opening_brace >= len(text) or text[opening_brace] != "{":
        return -1
    depth = 1
    cursor = opening_brace + 1
    while cursor < len(text):
        if text[cursor] == "{" and _is_unescaped(text, cursor):
            depth += 1
        elif text[cursor] == "}" and _is_unescaped(text, cursor):
            depth -= 1
            if depth == 0:
                return cursor
        cursor += 1
    return -1


def _dollar_end(text: str, content_start: int, marker: str) -> int:
    cursor = content_start
    while cursor < len(text):
        skipped_text_macro = False
        for macro in ("text", "intertext"):
            token = "\\" + macro + "{"
            if text.startswith(token, cursor):
                brace_end = _balanced_brace_end(text, cursor + len(token) - 1)
                if brace_end < 0:
                    return -1
                cursor = brace_end + 1
                skipped_text_macro = True
                break
        if skipped_text_macro:
            continue
        if text.startswith(marker, cursor) and _is_unescaped(text, cursor):
            return cursor
        cursor += 1
    return -1


def extract_math(text: str, encoding: str) -> list[dict]:
    """Return math surfaces with the same record shape as the legacy extractor."""

    active = shared.active_same_length(text)
    chunks: list[dict] = []
    cursor = 0
    while cursor < len(active):
        content_start = content_end = end = None
        delimiter = None
        if active.startswith("\\[", cursor):
            content_start = cursor + 2
            content_end = active.find("\\]", content_start)
            end = content_end + 2
            delimiter = "bracket-display"
        elif active.startswith("\\(", cursor):
            content_start = cursor + 2
            content_end = active.find("\\)", content_start)
            end = content_end + 2
            delimiter = "paren-inline"
        elif active.startswith("\\begin{", cursor):
            brace_end = active.find("}", cursor + 7)
            environment = active[cursor + 7 : brace_end]
            if environment in shared.MATH_ENVS:
                close = "\\end{" + environment + "}"
                content_start = brace_end + 1
                content_end = active.find(close, content_start)
                end = content_end + len(close)
                delimiter = "environment:" + environment
        elif active[cursor] == "$" and _is_unescaped(active, cursor):
            marker = "$$" if active.startswith("$$", cursor) else "$"
            content_start = cursor + len(marker)
            content_end = _dollar_end(active, content_start, marker)
            end = content_end + len(marker)
            delimiter = "dollar-display" if marker == "$$" else "dollar-inline"
        if content_start is None:
            cursor += 1
            continue
        if content_end is None or content_end < 0 or end is None:
            raise ValueError(f"unclosed math surface at line {shared.line_of(text, cursor)}")
        raw = text[content_start:content_end]
        chunks.append(
            {
                "start": cursor,
                "end": end,
                "line_start": shared.line_of(text, cursor),
                "line_end": shared.line_of(text, end - 1),
                "delimiter": delimiter,
                "bytes": len(raw.encode(encoding)),
                "sha256": shared.sha(raw.encode(encoding)),
                "normalized_sha256": shared.sha(re.sub(r"\s+", "", raw).encode(encoding)),
                "normalized": re.sub(r"\s+", "", raw),
            }
        )
        cursor = end
    return chunks


def _embedded_math(payload: str) -> list[str]:
    embedded: list[str] = []
    cursor = 0
    while cursor < len(payload):
        if payload[cursor] == "$" and _is_unescaped(payload, cursor):
            marker = "$$" if payload.startswith("$$", cursor) else "$"
            end = cursor + len(marker)
            while end < len(payload):
                if payload.startswith(marker, end) and _is_unescaped(payload, end):
                    embedded.append(payload[cursor + len(marker) : end])
                    cursor = end + len(marker)
                    break
                end += 1
            else:
                return embedded
            continue
        if payload.startswith("\\(", cursor):
            end = payload.find("\\)", cursor + 2)
            if end >= 0:
                embedded.append(payload[cursor + 2 : end])
                cursor = end + 2
                continue
        cursor += 1
    return embedded


def _scrub_text_macro(value: str, macro: str) -> str:
    marker = "\\" + macro + "{"
    output: list[str] = []
    cursor = 0
    while True:
        start = value.find(marker, cursor)
        if start < 0:
            output.append(value[cursor:])
            return "".join(output)
        output.append(value[cursor:start])
        opening_brace = start + len(marker) - 1
        brace_end = _balanced_brace_end(value, opening_brace)
        if brace_end < 0:
            output.append(marker + "TEXT}")
            return "".join(output)
        payload = value[opening_brace + 1 : brace_end]
        retained_math = "".join("MATH{" + item + "}" for item in _embedded_math(payload))
        output.append(marker + "TEXT" + retained_math + "}")
        cursor = brace_end + 1


def math_key(value: str) -> str:
    for macro in ("text", "intertext"):
        value = _scrub_text_macro(value, macro)
    return re.sub(r"\s+", "", value)
