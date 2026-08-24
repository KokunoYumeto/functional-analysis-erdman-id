from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable

try:
    from lxml import etree, html
except ImportError as exc:  # pragma: no cover - exercised by the external QA gate
    raise SystemExit("lxml is required for the semantic HTML build") from exc


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-complete-source.tex"
FINAL_BUILD = ROOT / "qa" / "build-complete-source-final"
DIAGRAM_TEXT = ROOT / "html" / "accessibility" / "diagram_text.jsonl"
CSS_SOURCE = ROOT / "html" / "static" / "reader.css"
DIAGXY = ROOT / "source" / "id-ID" / "DIAGXY.TEX"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
SOURCE_DATE_EPOCH = "1444126743"
DIAGXY_SHA256 = "3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb"
DIAGRAM_ID_RE = re.compile(r"FAOA-2015-DIAGRAM-(?:PREFACE|CH(?:0[1-9]|1[0-7]))-[0-9]{3}\Z")
SVG_NS = "http://www.w3.org/2000/svg"

ROUTES: list[dict[str, Any]] = [
    {"slug": "prakata", "file": "preface-id.tex", "unit_id": "FAOA-2015-PREFACE", "number": None, "title": "Prakata", "role": "Materi awal"},
    {"slug": "bab-01", "file": "linalg-id.tex", "unit_id": "FAOA-2015-CH01", "number": 1, "title": "Aljabar Linear dan Teorema Spektral", "role": "D20 inti"},
    {"slug": "bab-02", "file": "categories-id.tex", "unit_id": "FAOA-2015-CH02", "number": 2, "title": "Selingan Sangat Singkat tentang Bahasa Kategori", "role": "D20 inti"},
    {"slug": "bab-03", "file": "normlinspaces-id.tex", "unit_id": "FAOA-2015-CH03", "number": 3, "title": "Ruang Linear Bernorma", "role": "D20 inti"},
    {"slug": "bab-04", "file": "Hilbert_spaces-id.tex", "unit_id": "FAOA-2015-CH04", "number": 4, "title": "Ruang Hilbert", "role": "D20 inti"},
    {"slug": "bab-05", "file": "Hilbert_space_operators-id.tex", "unit_id": "FAOA-2015-CH05", "number": 5, "title": "Operator pada Ruang Hilbert", "role": "D20 inti"},
    {"slug": "bab-06", "file": "Banach_spaces-id.tex", "unit_id": "FAOA-2015-CH06", "number": 6, "title": "Ruang Banach", "role": "D20 inti"},
    {"slug": "bab-07", "file": "compact_operators-id.tex", "unit_id": "FAOA-2015-CH07", "number": 7, "title": "Operator Kompak", "role": "D20 inti"},
    {"slug": "bab-08", "file": "spectrum-id.tex", "unit_id": "FAOA-2015-CH08", "number": 8, "title": "Beberapa Teori Spektral", "role": "D20 inti"},
    {"slug": "bab-09", "file": "topvecspaces-id.tex", "unit_id": "FAOA-2015-CH09", "number": 9, "title": "Ruang Vektor Topologis", "role": "Lanjutan"},
    {"slug": "bab-10", "file": "distributions-id.tex", "unit_id": "FAOA-2015-CH10", "number": 10, "title": "Distribusi", "role": "Lanjutan"},
    {"slug": "bab-11", "file": "Gelfand_Naimark-id.tex", "unit_id": "FAOA-2015-CH11", "number": 11, "title": "Teorema Gelfand–Naimark", "role": "Lanjutan"},
    {"slug": "bab-12", "file": "no_identity-id.tex", "unit_id": "FAOA-2015-CH12", "number": 12, "title": "Bertahan Tanpa Identitas", "role": "Lanjutan"},
    {"slug": "bab-13", "file": "GNS_construction-id.tex", "unit_id": "FAOA-2015-CH13", "number": 13, "title": "Konstruksi Gelfand–Naimark–Segal", "role": "Lanjutan"},
    {"slug": "bab-14", "file": "multiplier_algebras-id.tex", "unit_id": "FAOA-2015-CH14", "number": 14, "title": "Aljabar Pengali", "role": "Lanjutan"},
    {"slug": "bab-15", "file": "fredholm_theory-id.tex", "unit_id": "FAOA-2015-CH15", "number": 15, "title": "Teori Fredholm", "role": "Lanjutan"},
    {"slug": "bab-16", "file": "extensions-id.tex", "unit_id": "FAOA-2015-CH16", "number": 16, "title": "Ekstensi", "role": "Lanjutan"},
    {"slug": "bab-17", "file": "K0_functor-id.tex", "unit_id": "FAOA-2015-CH17", "number": 17, "title": "Funktor K0", "role": "Lanjutan"},
]

NUMBERED_KINDS = ("thm", "lem", "prop", "cor", "ax", "defn", "notn", "conv", "rem", "fact", "exam", "exer", "prob", "proj")
ALL_ENV_KINDS = NUMBERED_KINDS + ("cau", "proof")
KIND_LABELS = {
    "thm": "Teorema", "lem": "Lema", "prop": "Proposisi", "cor": "Akibat", "ax": "Aksioma",
    "defn": "Definisi", "notn": "Notasi", "conv": "Konvensi", "rem": "Catatan", "fact": "Fakta",
    "exam": "Contoh", "exer": "Latihan", "prob": "Soal", "proj": "Proyek", "cau": "Perhatian", "proof": "Bukti",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def safe_reset(path: Path, allowed_parent: Path) -> None:
    resolved = path.resolve()
    parent = allowed_parent.resolve()
    if resolved == parent or parent not in resolved.parents:
        raise RuntimeError(f"unsafe reset target: {resolved}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=False)


def pandoc_macro_prelude() -> str:
    lines = MASTER.read_text(encoding="utf-8").splitlines()[102:226]
    filtered: list[str] = []
    skipping = False
    for line in lines:
        if line.lstrip().startswith("\\makeatletter"):
            skipping = True
            continue
        if skipping:
            if line.lstrip().startswith("\\makeatother"):
                skipping = False
            continue
        filtered.append(line)
    if skipping:
        raise RuntimeError("unterminated futurexref macro block")
    filtered.append(r"\newcommand{\futurexref}[2]{\ref{#2}}")
    return normalize_legacy_tex("\n".join(filtered))


def route_for_target_path(target_path: str) -> str:
    filename = Path(target_path.replace("\\", "/")).name
    for route in ROUTES:
        if route["file"] == filename:
            return route["slug"]
    raise KeyError(f"no route for {target_path}")


def load_aux_numbers() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    numbers: dict[str, str] = {}
    routes: dict[str, str] = {}
    kinds: dict[str, str] = {}
    aux_by_route = {route["slug"]: FINAL_BUILD / f"{Path(route['file']).stem}.aux" for route in ROUTES}
    for slug, path in aux_by_route.items():
        if not path.exists():
            raise FileNotFoundError(path)
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", line)
            if not match:
                continue
            label, number = match.groups()
            if label in numbers and numbers[label] != number:
                raise RuntimeError(f"conflicting label number for {label}")
            numbers[label] = number
            routes[label] = slug
            if "{thm." in line:
                kinds[label] = "theorem"
            elif "{equation." in line:
                kinds[label] = "equation"
            elif "{section." in line:
                kinds[label] = "section"
            elif "{chapter." in line:
                kinds[label] = "chapter"
            else:
                kinds[label] = "other"
    return numbers, routes, kinds


def bibliography_entries() -> list[tuple[str, str]]:
    bbl = (FINAL_BUILD / "functional-analysis-id-complete-source.bbl").read_text(encoding="utf-8")
    matches = list(re.finditer(r"\\bibitem\{([^}]+)\}\s*", bbl))
    entries: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else bbl.find(r"\end{thebibliography}", match.end())
        value = bbl[match.end():end].strip()
        value = value.replace(r"\bysame", "—")
        entries.append((match.group(1), value))
    if not entries:
        raise RuntimeError("bibliography closure is empty")
    return entries


def normalize_legacy_tex(text: str) -> str:
    text = re.sub(r"\\hphantom\s*\{[^{}]*\}", r"\\mathord{\\cdot}", text)
    text = re.sub(r"\\hphantom\s+([A-Za-z])", r"\\mathord{\\cdot}", text)
    text = text.replace(r"\thickspace{}", r"\,")
    text = text.replace(r"\strut", "")
    text = re.sub(r"\\intertext\{([^{}]*)\}", r"&\\text{\1}\\\\", text)
    text = re.sub(r"\\hbox\{jika \$([^$]+)\$;\}", r"\\text{jika } \1;", text)
    text = re.sub(r"\\hbox\{jika \$([^$]+)\$\.\}", r"\\text{jika } \1.", text)
    text = text.replace(r"\hbox{selain itu.}", r"\text{selain itu.}")
    text = text.replace(r"\tag{$\ast$}", r"\qquad(\ast)")
    text = text.replace(r"\tag{\ast}", r"\qquad(\ast)")
    text = text.replace(r"\hbox{selainnya.}", r"\text{selainnya.}")
    text = text.replace(r"\mathbf{\emph{K}_0}", r"\mathbf{K}_0")
    text = text.replace(r"\not\!\!\!\!\implies", r"\nRightarrow")
    text = text.replace(
        r"\text{$p \in \N$, $a_0$, \dots, $a_p$, $b_0$, \dots, $b_p \in A$}",
        r"p \in \N,\ a_0, \dots, a_p, b_0, \dots, b_p \in A",
    )

    def align_heuristic_product(match: re.Match[str]) -> str:
        body = match.group("body")
        body = body.replace(r"pq \sim", r"pq &\sim", 1)
        body = re.sub(r"(?m)^(\s*)=", r"\1&=", body)
        body = body.replace(r"\sim qp\,.", r"&\sim qp\,.", 1)
        return r"\[\begin{aligned}" + body + r"\end{aligned}\]"

    text = re.sub(
        r"\\\[\s*(?P<body>pq \\sim[\s\S]*?\\sim qp\\,\.)\s*\\\]",
        align_heuristic_product,
        text,
        count=1,
    )
    return text


def extract_balanced_command(text: str, command: str) -> str:
    start = text.find(command)
    if start < 0:
        raise ValueError(command)
    brace = text.find("{", start + len(command))
    if brace < 0:
        raise ValueError(f"missing opening brace for {command}")
    depth = 0
    escaped = False
    for index in range(brace, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise ValueError(f"unbalanced {command}")


def diagram_is_inline(record: dict[str, Any], lines: list[str]) -> bool:
    if int(record["source_line"]) != int(record["source_end_line"]):
        return False
    line = lines[int(record["source_line"]) - 1]
    return r"\xymatrix" in line and r"\[" not in line and r"\begin{equation" not in line


def diagram_effective_range(record: dict[str, Any], lines: list[str]) -> tuple[int, int]:
    r"""Include a display opener when the source ledger starts at its diagram body.

    Several authoritative line ranges intentionally identify only the diagram command,
    while the closing display delimiter shares the command's last line.  Replacing that
    literal range would leave an unmatched ``equation`` or ``\[`` in the Pandoc shadow.
    We expand only over a standalone immediately preceding opener, and fail closed if the
    source has a less constrained shape so surrounding prose can never be discarded.
    """
    start = int(record["source_line"])
    end = int(record["source_end_line"])
    block = "\n".join(lines[start - 1:end])
    equation_opener = r"^\s*\\begin\{equation\*?\}(?:\\label\{[^}]+\})?\s*$"
    display_opener = r"^\s*\\\[\s*$"
    equation_closer = r"^\s*\\end\{equation\*?\}\s*$"
    display_closer = r"^\s*\\\]\s*$"

    # Some ledgers isolate the diagram body while the display wrappers occupy the
    # immediately adjacent lines.  Consume that exact pair so the HTML marker is a
    # normal block rather than raw TeX embedded in a math fallback.
    if start > 1 and end < len(lines):
        before = lines[start - 2]
        after = lines[end]
        if (
            re.fullmatch(equation_opener, before)
            and re.fullmatch(equation_closer, after)
        ) or (
            re.fullmatch(display_opener, before)
            and re.fullmatch(display_closer, after)
        ):
            return start - 1, end + 1

    needs_equation_opener = block.count(r"\end{equation}") > block.count(r"\begin{equation}")
    needs_display_opener = block.count(r"\]") > block.count(r"\[")
    if needs_equation_opener and needs_display_opener:
        raise RuntimeError(f"ambiguous display wrappers for {record['diagram_id']}")
    if not (needs_equation_opener or needs_display_opener):
        return start, end
    if start <= 1:
        raise RuntimeError(f"missing display opener for {record['diagram_id']}")
    opener = lines[start - 2]
    if needs_equation_opener:
        pattern = equation_opener
    else:
        pattern = display_opener
    if not re.fullmatch(pattern, opener):
        raise RuntimeError(
            f"non-standalone display opener before {record['diagram_id']}: {opener!r}"
        )
    return start - 1, end


def diagram_source_blocks(route: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, str]:
    source_path = ROOT / "source" / "id-ID" / route["file"]
    lines = source_path.read_text(encoding="utf-8").splitlines()
    result: dict[str, str] = {}
    for record in records:
        start, end = diagram_effective_range(record, lines)
        block = "\n".join(lines[start - 1:end])
        if diagram_is_inline(record, lines):
            block = extract_balanced_command(block, r"\xymatrix")
        result[record["diagram_id"]] = block
    return result


def make_shadow(
    route: dict[str, Any],
    segments: list[dict[str, Any]],
    diagram_records: list[dict[str, Any]],
    special_units: list[dict[str, Any]],
) -> tuple[str, dict[str, str]]:
    source_path = ROOT / "source" / "id-ID" / route["file"]
    lines = source_path.read_text(encoding="utf-8").splitlines()
    anchors: dict[int, list[str]] = {}
    for segment in segments:
        anchors.setdefault(int(segment["target_line_start"]), []).append(segment["id"])

    replacements: list[tuple[int, int, str, str]] = []
    inline_by_line: dict[int, list[dict[str, Any]]] = {}
    diagram_blocks = diagram_source_blocks(route, diagram_records)
    for record in diagram_records:
        if diagram_is_inline(record, lines):
            inline_by_line.setdefault(int(record["source_line"]), []).append(record)
        else:
            start, end = diagram_effective_range(record, lines)
            replacements.append((start, end, "diagram", record["diagram_id"]))
    for unit in special_units:
        if unit["unit_kind"] == "number_set_notation":
            replacements.append((int(unit["target_line_start"]), int(unit["target_line_end"]), "number-notation", unit["id"]))
    replacements.sort()
    for left, right in zip(replacements, replacements[1:]):
        if right[0] <= left[1]:
            raise RuntimeError(f"overlapping HTML shadow replacement in {route['file']}: {left} / {right}")
    replacement_by_start = {r[0]: r for r in replacements}

    output: list[str] = []
    line_number = 1
    while line_number <= len(lines):
        replacement = replacement_by_start.get(line_number)
        if replacement:
            start, end, kind, identifier = replacement
            block = "\n".join(lines[start - 1:end])
            for anchor_line in range(start, end + 1):
                for anchor in anchors.get(anchor_line, []):
                    output.append(f"\\label{{{anchor}}}")
            for label in re.findall(r"\\label\{([^}]+)\}", block):
                output.append(f"\\label{{{label}}}")
            marker = f"[[DIAGRAM:{identifier}]]" if kind == "diagram" else f"[[NUMBER-NOTATION:{identifier}]]"
            output.extend([r"\begin{quote}", f"\\textbf{{{marker}}}", r"\end{quote}"])
            line_number = end + 1
            continue
        for anchor in anchors.get(line_number, []):
            output.append(f"\\label{{{anchor}}}")
        line = lines[line_number - 1]
        for record in inline_by_line.get(line_number, []):
            source = diagram_blocks[record["diagram_id"]]
            marker = f"\\textbf{{[[DIAGRAM:{record['diagram_id']}]]}}"
            delimited_source = f"${source}$"
            if delimited_source in line:
                line = line.replace(delimited_source, marker, 1)
            elif source in line:
                line = line.replace(source, marker, 1)
            else:
                raise RuntimeError(f"inline diagram source not found: {record['diagram_id']}")
        output.append(line)
        line_number += 1
    chapter = "\n".join(output).rsplit(r"\endinput", 1)[0]
    chapter = normalize_legacy_tex(chapter)
    shadow = "\n".join([
        r"\documentclass{amsbook}",
        pandoc_macro_prelude(),
        r"\begin{document}",
        chapter,
        r"\end{document}",
        "",
    ])
    return shadow, diagram_blocks


def render_diagram_svg(
    record: dict[str, Any],
    source_tex: str,
    build_dir: Path,
    destination: Path,
    macro_prelude: str,
) -> dict[str, Any]:
    diagram_id = record.get("diagram_id")
    if not isinstance(diagram_id, str) or DIAGRAM_ID_RE.fullmatch(diagram_id) is None:
        raise RuntimeError(f"unsafe diagram ID: {diagram_id!r}")

    root_resolved = ROOT.resolve()
    build_root = build_dir.resolve()
    output_root = destination.parent.resolve()
    for label, candidate in (("diagram build root", build_root), ("diagram output root", output_root)):
        if candidate == root_resolved or root_resolved not in candidate.parents:
            raise RuntimeError(f"unsafe {label}: {candidate}")
    work = (build_root / diagram_id).resolve()
    destination_resolved = destination.resolve()
    if work.parent != build_root:
        raise RuntimeError(f"diagram work path escaped its root: {work}")
    if destination_resolved.parent != output_root or destination_resolved.name != f"{diagram_id}.svg":
        raise RuntimeError(f"diagram output path escaped its root: {destination_resolved}")
    work.mkdir(parents=True, exist_ok=True)

    canonical_diagxy_sha256 = sha256_file(DIAGXY)
    if canonical_diagxy_sha256 != DIAGXY_SHA256:
        raise RuntimeError(
            f"DIAGXY authority mismatch: expected {DIAGXY_SHA256}, got {canonical_diagxy_sha256}"
        )
    body = re.sub(r"\s*\\ns\s*$", "", source_tex)
    if not re.search(r"\\begin\{(?:equation\*?|CD|displaymath)\}|\\\[|\$\$", body):
        body = "\\[\n" + body + "\n\\]"
    tex = "\n".join([
        r"\documentclass[11pt]{article}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{lmodern}",
        r"\usepackage{amsmath}",
        r"\usepackage{amssymb}",
        r"\usepackage{amscd}",
        r"\usepackage[all]{xy}",
        r"\pagestyle{empty}",
        macro_prelude,
        r"\input{DIAGXY.TEX}",
        r"\begin{document}",
        body,
        r"\end{document}",
        "",
    ])
    tex_path = work / f"{diagram_id}.tex"
    write_text(tex_path, tex)
    wrapper_sha256 = sha256_file(tex_path)
    scratch_diagxy = work / "DIAGXY.TEX"
    shutil.copyfile(DIAGXY, scratch_diagxy)
    scratch_diagxy_sha256 = sha256_file(scratch_diagxy)
    if scratch_diagxy_sha256 != DIAGXY_SHA256:
        raise RuntimeError(
            f"scratch DIAGXY mismatch for {diagram_id}: expected {DIAGXY_SHA256}, got {scratch_diagxy_sha256}"
        )
    env = dict(**__import__("os").environ)
    env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    env["FORCE_SOURCE_DATE"] = "1"
    latex_run = subprocess.run(
        ["latex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", tex_path.name],
        cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=60, check=False,
    )
    if latex_run.returncode:
        raise RuntimeError(f"diagram LaTeX failed for {diagram_id}:\n{latex_run.stdout[-3000:]}\n{latex_run.stderr[-1000:]}")
    dvi_path = work / f"{diagram_id}.dvi"
    if not dvi_path.is_file():
        raise RuntimeError(f"diagram LaTeX produced no DVI for {diagram_id}")
    raw_pattern = f"{diagram_id}.page-%p.raw.svg"
    for stale_page in work.glob(f"{diagram_id}.page-*.raw.svg"):
        stale_page.unlink()
    dvisvgm_run = subprocess.run(
        [
            "dvisvgm", "--page=1-", "--no-fonts", "--exact-bbox", "--bbox=min",
            "--precision=6", "--optimize=all", f"--output={raw_pattern}", dvi_path.name,
        ],
        cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=60, check=False,
    )
    if dvisvgm_run.returncode:
        raise RuntimeError(f"dvisvgm failed for {diagram_id}:\n{dvisvgm_run.stdout[-2000:]}\n{dvisvgm_run.stderr[-2000:]}")
    raw_pages = sorted(work.glob(f"{diagram_id}.page-*.raw.svg"), key=lambda path: path.name)
    if len(raw_pages) != 1:
        raise RuntimeError(f"diagram page closure mismatch for {diagram_id}: {len(raw_pages)} pages")
    raw_svg = raw_pages[0]

    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        remove_comments=True,
        remove_pis=True,
        recover=False,
        huge_tree=False,
    )
    try:
        svg_tree = etree.parse(str(raw_svg), parser)
    except etree.XMLSyntaxError as exc:
        raise RuntimeError(f"malformed SVG for {diagram_id}: {exc}") from exc
    svg_root = svg_tree.getroot()
    root_name = etree.QName(svg_root)
    if root_name.namespace != SVG_NS or root_name.localname != "svg":
        raise RuntimeError(f"non-SVG root for {diagram_id}: {svg_root.tag!r}")

    for metadata in list(svg_root.xpath(".//*[local-name()='metadata']")):
        parent = metadata.getparent()
        if parent is not None:
            parent.remove(metadata)

    ids: set[str] = set()
    internal_references: list[str] = []
    path_count = 0
    use_count = 0
    forbidden_elements = {"script", "image", "foreignobject", "style", "text", "font"}
    css_url_re = re.compile(r"url\(\s*(?:['\"])?([^'\"\s)]+)(?:['\"])?\s*\)", flags=re.IGNORECASE)
    for element in svg_root.iter():
        name = etree.QName(element)
        local_name = name.localname.lower()
        if name.namespace != SVG_NS:
            raise RuntimeError(f"foreign SVG namespace in {diagram_id}: {element.tag!r}")
        if local_name in forbidden_elements:
            raise RuntimeError(f"unsafe SVG element in {diagram_id}: {name.localname}")
        if local_name == "path":
            path_count += 1
        elif local_name == "use":
            use_count += 1
        element_id = element.get("id")
        if element_id:
            if element_id in ids:
                raise RuntimeError(f"duplicate SVG ID in {diagram_id}: {element_id}")
            ids.add(element_id)
        for raw_name, value in element.attrib.items():
            attribute_name = etree.QName(raw_name).localname.lower()
            if attribute_name.startswith("on") or attribute_name == "style":
                raise RuntimeError(f"unsafe SVG attribute in {diagram_id}: {attribute_name}")
            if "@import" in value.lower():
                raise RuntimeError(f"CSS import in SVG {diagram_id}")
            if attribute_name in {"href", "src"}:
                if not value.startswith("#") or len(value) == 1:
                    raise RuntimeError(f"external SVG reference in {diagram_id}: {value!r}")
                internal_references.append(value[1:])
            css_targets = css_url_re.findall(value)
            if "url(" in value.lower() and not css_targets:
                raise RuntimeError(f"malformed CSS URL in SVG {diagram_id}: {value!r}")
            for target in css_targets:
                if not target.startswith("#") or len(target) == 1:
                    raise RuntimeError(f"external CSS reference in SVG {diagram_id}: {target!r}")
                internal_references.append(target[1:])
    unresolved_ids = sorted(set(internal_references) - ids)
    if unresolved_ids:
        raise RuntimeError(f"unresolved internal SVG references in {diagram_id}: {unresolved_ids}")
    if path_count == 0 or use_count == 0:
        raise RuntimeError(f"empty SVG graphics closure for {diagram_id}: paths={path_count}, uses={use_count}")

    view_box = svg_root.get("viewBox")
    if view_box is None:
        raise RuntimeError(f"missing SVG viewBox for {diagram_id}")
    try:
        view_box_values = [float(value) for value in re.split(r"[\s,]+", view_box.strip()) if value]
    except ValueError as exc:
        raise RuntimeError(f"invalid SVG viewBox for {diagram_id}: {view_box!r}") from exc
    if len(view_box_values) != 4 or not all(math.isfinite(value) for value in view_box_values):
        raise RuntimeError(f"invalid SVG viewBox for {diagram_id}: {view_box!r}")
    if view_box_values[2] <= 0 or view_box_values[3] <= 0:
        raise RuntimeError(f"non-positive SVG viewBox for {diagram_id}: {view_box!r}")
    dimension_re = re.compile(
        r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)(?:pt|px|bp|mm|cm|in)?\s*$"
    )
    dimensions: dict[str, float] = {}
    for attribute_name in ("width", "height"):
        raw_value = svg_root.get(attribute_name)
        match = dimension_re.fullmatch(raw_value or "")
        if match is None:
            raise RuntimeError(f"invalid SVG {attribute_name} for {diagram_id}: {raw_value!r}")
        numeric_value = float(match.group(1))
        if not math.isfinite(numeric_value) or numeric_value <= 0:
            raise RuntimeError(f"non-positive SVG {attribute_name} for {diagram_id}: {raw_value!r}")
        dimensions[attribute_name] = numeric_value

    description = record["description_id"]
    if not isinstance(description, str) or not description.strip():
        raise RuntimeError(f"missing SVG description for {diagram_id}")
    title = f"Diagram {diagram_id}"
    title_id = f"{diagram_id}-title"
    description_id = f"{diagram_id}-desc"
    if title_id in ids or description_id in ids:
        raise RuntimeError(f"SVG accessibility ID collision for {diagram_id}")
    svg_root.set("role", "img")
    svg_root.set("aria-labelledby", f"{title_id} {description_id}")
    title_element = etree.Element(etree.QName(SVG_NS, "title"))
    title_element.set("id", title_id)
    title_element.text = title
    description_element = etree.Element(etree.QName(SVG_NS, "desc"))
    description_element.set("id", description_id)
    description_element.text = description
    svg_root.insert(0, title_element)
    svg_root.insert(1, description_element)

    normalized = etree.tostring(svg_root, encoding="unicode", xml_declaration=False, pretty_print=False)
    normalized = "\n".join(line.rstrip() for line in normalized.splitlines()).strip() + "\n"
    write_text(destination_resolved, normalized)
    etree.parse(
        str(destination_resolved),
        etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, recover=False),
    )
    normalized_sha256 = sha256_file(destination_resolved)
    return {
        "id": diagram_id,
        "bytes": destination_resolved.stat().st_size,
        "sha256": normalized_sha256,
        "source_tex_sha256": sha256_bytes(source_tex.encode("utf-8")),
        "wrapper_sha256": wrapper_sha256,
        "diagxy_sha256": scratch_diagxy_sha256,
        "dvi_sha256": sha256_file(dvi_path),
        "raw_svg_sha256": sha256_file(raw_svg),
        "normalized_svg_sha256": normalized_sha256,
        "page_count": len(raw_pages),
        "path_count": path_count,
        "use_count": use_count,
        "view_box": view_box_values,
        "width": dimensions["width"],
        "height": dimensions["height"],
    }


def run_pandoc(pandoc: str, shadow: Path, raw_html: Path) -> tuple[str, str]:
    proc = subprocess.run(
        [
            pandoc,
            str(shadow),
            "--from=latex",
            "--to=html5",
            "--standalone",
            "--mathml",
            "--wrap=none",
            "--metadata=lang:id-ID",
            f"--output={raw_html}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError(f"Pandoc failed for {shadow.name}:\n{proc.stdout[-2000:]}\n{proc.stderr[-5000:]}")
    return proc.stdout, proc.stderr


def alias_before(element: etree._Element, alias_id: str) -> None:
    if not alias_id:
        return
    alias = html.Element("span", {"id": alias_id, "class": "anchor-alias", "aria-hidden": "true"})
    element.addprevious(alias)


def add_environment_title(element: etree._Element, kind: str, number: str | None) -> None:
    title = html.Element("p", {"class": "environment-title"})
    label = KIND_LABELS[kind]
    title.text = f"{label} {number}." if number else f"{label}."
    element.insert(0, title)


def visible_text(element: etree._Element) -> str:
    return " ".join(element.text_content().split())


def nearest_marker_block(element: etree._Element) -> etree._Element:
    current = element
    while current.getparent() is not None and current.tag not in {"blockquote", "p", "div"}:
        current = current.getparent()
    if current.tag == "p" and current.getparent() is not None and current.getparent().tag == "blockquote":
        return current.getparent()
    return current


def install_diagram_figures(
    article: etree._Element,
    diagram_records: dict[str, dict[str, Any]],
    diagram_sources: dict[str, str],
    svg_href_prefix: str,
    svg_ids: set[str],
) -> list[str]:
    installed: list[str] = []
    for strong in list(article.xpath(".//strong")):
        match = re.fullmatch(r"\[\[DIAGRAM:([^\]]+)\]\]", visible_text(strong))
        if not match:
            continue
        diagram_id = match.group(1)
        record = diagram_records[diagram_id]
        provenance = record["component_provenance"]
        rights = record["component_rights"]
        figure = html.Element(
            "figure",
            {
                "class": "diagram",
                "id": diagram_id,
                "data-source-file": record["source_file"],
                "data-source-lines": f"{record['source_line']}-{record['source_end_line']}",
                "data-source-form": record["source_form"],
                "data-source-creator": provenance["source_diagram_creator"],
                "data-description-creator": provenance["accessible_description_creator"],
                "data-source-license": rights["source_diagram_license"],
                "data-description-license": rights["accessible_description_license"],
                "data-rendering-component": rights["rendering_component"],
                "data-nonendorsement": "true" if rights["nonendorsement"] else "false",
            },
        )
        description = record["description_id"]
        if diagram_id in svg_ids:
            image = html.Element(
                "img",
                {
                    "src": f"{svg_href_prefix}{diagram_id}.svg",
                    "alt": description,
                    "loading": "lazy",
                    "decoding": "async",
                },
            )
            figure.append(image)
        transcript = html.Element("p", {"class": "diagram-transcript"})
        transcript.text = description
        figure.append(transcript)
        caption = html.Element("figcaption")
        caption.text = (
            "Diagram sumber: John M. Erdman, CC BY-SA 4.0. Deskripsi aksesibilitas "
            f"ditambahkan oleh {MODEL}; perubahan ini tidak menyiratkan dukungan."
        )
        figure.append(caption)
        source_file = ROOT / record["source_file"]
        source_lines = source_file.read_text(encoding="utf-8").splitlines()
        if diagram_is_inline(record, source_lines):
            link = html.Element("a", {"class": "diagram-inline-link", "href": f"#{diagram_id}"})
            link.text = "diagram visual dan transkrip"
            strong.getparent().replace(strong, link)
            container = link.getparent()
            while container.getparent() is not None:
                classes = set((container.get("class") or "").split())
                if classes.intersection(ALL_ENV_KINDS):
                    break
                container = container.getparent()
            container.append(figure)
        else:
            block = nearest_marker_block(strong)
            block.getparent().replace(block, figure)
        installed.append(diagram_id)
    return installed


NUMBER_NOTATION_ROWS = [
    (r"\mathbb{C}", "himpunan bilangan kompleks"),
    (r"\mathbb{R}", "himpunan bilangan real"),
    (r"\mathbb{R}^n", "semua tupel-n bilangan real"),
    (r"\mathbb{R}^{+}=\{x\in\mathbb{R}:x\geq0\}", "bilangan real tak negatif"),
    (r"\mathbb{Q}", "himpunan bilangan rasional"),
    (r"\mathbb{Q}^{+}=\{x\in\mathbb{Q}:x\geq0\}", "bilangan rasional tak negatif"),
    (r"\mathbb{Z}", "himpunan bilangan bulat"),
    (r"\mathbb{Z}^{+}=\{0,1,2,\ldots\}", "bilangan bulat tak negatif"),
    (r"\mathbb{N}=\{1,2,3,\ldots\}", "himpunan bilangan asli"),
    (r"\mathbb{N}_n=\{1,2,3,\ldots,n\}", "n bilangan asli pertama"),
    (r"[a,b]", "interval tertutup: a ≤ x ≤ b"),
    (r"[a,b)", "interval: a ≤ x < b"),
    (r"(a,b]", "interval: a < x ≤ b"),
    (r"(a,b)", "interval terbuka: a < x < b"),
    (r"[a,\infty)", "sinar: a ≤ x"),
    (r"(a,\infty)", "sinar: a < x"),
    (r"(-\infty,b]", "sinar: x ≤ b"),
    (r"(-\infty,b)", "sinar: x < b"),
    (r"\mathbb{D}=\{(x,y)\in\mathbb{R}^2:x^2+y^2<1\}", "cakram satuan terbuka"),
    (r"\mathbb{T}=\mathbb{S}^1=\{(x,y)\in\mathbb{R}^2:x^2+y^2=1\}", "lingkaran satuan"),
]


def mathml_fragment(pandoc: str, tex: str) -> etree._Element:
    proc = subprocess.run(
        [pandoc, "--from=latex", "--to=html5", "--mathml", "--wrap=none"],
        cwd=ROOT,
        input=f"${tex}$",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    if proc.returncode or "Could not convert TeX math" in proc.stderr:
        raise RuntimeError(f"notation MathML conversion failed: {tex}: {proc.stderr}")
    fragments = html.fragments_fromstring(proc.stdout)
    container = html.Element("div")
    for fragment in fragments:
        if isinstance(fragment, str):
            if container.text:
                container.text += fragment
            else:
                container.text = fragment
        else:
            container.append(fragment)
    math_nodes = container.xpath(".//*[local-name()='math']")
    if len(math_nodes) != 1:
        raise RuntimeError(f"expected one MathML node for {tex}")
    node = math_nodes[0]
    node.getparent().remove(node)
    return node


def install_number_notation(article: etree._Element, pandoc: str, semantic_id: str) -> bool:
    for strong in list(article.xpath(".//strong")):
        if visible_text(strong) != f"[[NUMBER-NOTATION:{semantic_id}]]":
            continue
        wrapper = html.Element("div", {"class": "table-scroll", "tabindex": "0", "aria-label": "Tabel notasi himpunan bilangan"})
        table = html.Element("table", {"id": semantic_id})
        caption = html.Element("caption")
        caption.text = "Notasi untuk himpunan bilangan"
        table.append(caption)
        thead = html.Element("thead")
        header_row = html.Element("tr")
        for value in ("Notasi", "Arti"):
            cell = html.Element("th", {"scope": "col"})
            cell.text = value
            header_row.append(cell)
        thead.append(header_row)
        table.append(thead)
        tbody = html.Element("tbody")
        for tex, meaning in NUMBER_NOTATION_ROWS:
            row = html.Element("tr")
            notation = html.Element("td")
            notation.append(mathml_fragment(pandoc, tex))
            description = html.Element("td")
            description.text = meaning
            row.extend([notation, description])
            tbody.append(row)
        table.append(tbody)
        wrapper.append(table)
        block = nearest_marker_block(strong)
        block.getparent().replace(block, wrapper)
        return True
    return False


def normalize_table(table: etree._Element, caption_text: str, table_id: str) -> None:
    table.set("id", table_id)
    captions = table.xpath("./caption")
    if captions:
        captions[0].text = caption_text
    else:
        caption = html.Element("caption")
        caption.text = caption_text
        table.insert(0, caption)
    rows = table.xpath(".//tr")
    if rows:
        for cell in list(rows[0]):
            if cell.tag == "td":
                cell.tag = "th"
            if cell.tag == "th":
                cell.set("scope", "col")
    parent = table.getparent()
    if parent is not None and not (parent.tag == "div" and "table-scroll" in (parent.get("class") or "").split()):
        wrapper = html.Element("div", {"class": "table-scroll", "tabindex": "0", "aria-label": caption_text})
        parent.replace(table, wrapper)
        wrapper.append(table)


def assign_semantic_units(
    article: etree._Element,
    route: dict[str, Any],
    units: list[dict[str, Any]],
    aux_numbers: dict[str, str],
    aux_kinds: dict[str, str],
) -> dict[str, str]:
    assigned: dict[str, str] = {route["unit_id"]: route["slug"]}
    headings = article.xpath(".//h1")
    if not headings:
        raise RuntimeError(f"missing chapter heading for {route['slug']}")
    heading = headings[0]
    old_heading_id = heading.get("id")
    if old_heading_id:
        alias_before(heading, old_heading_id)
    heading.set("id", route["unit_id"])
    if route["number"] is not None:
        heading.text = f"Bab {route['number']} · {route['title']}"
    else:
        heading.text = route["title"]

    by_kind: dict[str, list[dict[str, Any]]] = {}
    for unit in units:
        by_kind.setdefault(unit["unit_kind"], []).append(unit)
    for values in by_kind.values():
        values.sort(key=lambda item: item.get("order_in_chapter", item.get("order_in_front_matter", 0)))

    section_nodes = article.xpath(".//h2")
    sections = by_kind.get("section", [])
    if len(section_nodes) != len(sections):
        raise RuntimeError(f"section mismatch for {route['slug']}: DOM {len(section_nodes)} / backend {len(sections)}")
    for node, record in zip(section_nodes, sections):
        old_id = node.get("id")
        if old_id:
            alias_before(node, old_id)
        node.set("id", record["id"])
        assigned[record["id"]] = route["slug"]

    records_by_id: dict[str, dict[str, Any]] = {}
    for kind in ALL_ENV_KINDS:
        nodes = article.xpath(f".//*[contains(concat(' ',normalize-space(@class),' '),' {kind} ')]")
        records = by_kind.get(kind, [])
        if records and len(nodes) != len(records):
            raise RuntimeError(f"{kind} mismatch for {route['slug']}: DOM {len(nodes)} / backend {len(records)}")
        if not records and nodes:
            records = [
                {
                    "id": f"{route['unit_id']}-HTML-{kind.upper()}-{index:04d}",
                    "unit_kind": kind,
                    "source_local_id": None,
                }
                for index in range(1, len(nodes) + 1)
            ]
        for node, record in zip(nodes, records):
            old_id = node.get("id")
            if old_id:
                alias_before(node, old_id)
            node.set("id", record["id"])
            node.set("data-unit-record", record["id"])
            records_by_id[record["id"]] = record
            assigned[record["id"]] = route["slug"]

    current_section = 0
    theorem_counter = 0
    for node in list(article.iterdescendants()):
        if node.tag == "h2":
            current_section += 1
            theorem_counter = 0
            continue
        classes = set((node.get("class") or "").split())
        kind = next((candidate for candidate in ALL_ENV_KINDS if candidate in classes), None)
        if not kind:
            continue
        number: str | None = None
        if kind in NUMBERED_KINDS:
            theorem_counter += 1
            if route["number"] is None:
                raise RuntimeError(f"numbered environment in unnumbered route {route['slug']}")
            number = f"{route['number']}.{current_section}.{theorem_counter}"
            record_id = node.get("data-unit-record")
            if not record_id:
                raise RuntimeError(f"missing backend record binding for {route['slug']} {kind}")
            record = records_by_id[record_id]
            label = record.get("source_local_id")
            if (
                label
                and label in aux_numbers
                and aux_kinds.get(label) == "theorem"
                and aux_numbers[label] != number
            ):
                raise RuntimeError(f"number mismatch {label}: computed {number} / aux {aux_numbers[label]}")
            node.set("data-number", number)
        add_environment_title(node, kind, number)
    return assigned


def add_local_toc(article: etree._Element) -> None:
    sections = article.xpath(".//h2")
    if not sections:
        return
    nav = html.Element("nav", {"class": "local-toc", "aria-label": "Daftar bagian pada unit ini"})
    heading = html.Element("h2")
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
    title = article.xpath("./h1")[0]
    title.addnext(nav)


def normalize_math(article: etree._Element) -> tuple[int, list[str]]:
    math_nodes = article.xpath(".//*[local-name()='math']")
    for index, node in enumerate(math_nodes, start=1):
        annotations = node.xpath(".//*[local-name()='annotation' and @encoding='application/x-tex']")
        if annotations:
            tex = " ".join(annotations[0].text_content().split())
            node.set("aria-label", f"Rumus matematika: {tex}")
            node.set("data-math-order", str(index))
        node.set("role", "math")
        parent = node.getparent()
        if parent is not None and "display" in (parent.get("class") or "").split():
            parent.set("tabindex", "0")
            parent.set("aria-label", "Rumus matematika; gulir mendatar bila perlu")
    fallbacks = []
    for node in article.xpath(".//*[contains(concat(' ',normalize-space(@class),' '),' math ')]"):
        if node.xpath(".//*[local-name()='math']") or node.tag.endswith("math"):
            continue
        value = visible_text(node)
        if value:
            fallbacks.append(value[:500])
    return len(math_nodes), fallbacks


def install_preface_special_units(article: etree._Element, special_units: list[dict[str, Any]], pandoc: str) -> None:
    by_kind = {unit["unit_kind"]: unit for unit in special_units}
    notation = by_kind.get("number_set_notation")
    if notation and not install_number_notation(article, pandoc, notation["id"]):
        raise RuntimeError("number-set notation marker was not installed")
    tables = article.xpath(".//table")
    table_specs = [
        ("alphabet_table_greek", "Huruf Yunani: bentuk, nama, dan pelafalan"),
        ("fraktur_table", "Font Fraktur dan padanan huruf Latinnya"),
    ]
    if len(tables) < len(table_specs):
        raise RuntimeError(f"preface table closure mismatch: {len(tables)}")
    for table, (kind, caption) in zip(tables, table_specs):
        normalize_table(table, caption, by_kind[kind]["id"])
    figures = article.xpath(".//figure[contains(concat(' ',normalize-space(@class),' '),' diagram ')]")
    diagram_kinds = ("commutative_diagram_rectangular", "commutative_diagram_triangular")
    if len(figures) < len(diagram_kinds):
        raise RuntimeError(f"preface diagram closure mismatch: {len(figures)}")
    for figure, kind in zip(figures, diagram_kinds):
        alias_before(figure, by_kind[kind]["id"])


def label_maps(
    semantic_units: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for unit in semantic_units:
        label = unit.get("source_local_id")
        if label:
            result[label] = unit["id"]
    for relation in relations:
        if relation.get("relation_type") == "declares_label" and relation.get("source_local_id"):
            label = relation["source_local_id"]
            target = relation["to_id"]
            if label in result and result[label] != target:
                raise RuntimeError(f"conflicting stable label destination: {label}")
            result[label] = target
    return result


def relative_href(from_slug: str, target_slug: str, fragment: str | None = None) -> str:
    suffix = f"#{fragment}" if fragment else ""
    if from_slug == target_slug and fragment:
        return suffix
    if from_slug:
        return f"../{target_slug}/index.html{suffix}"
    return f"{target_slug}/index.html{suffix}"


def rewrite_references(
    article: etree._Element,
    current_slug: str,
    label_to_stable: dict[str, str],
    id_to_route: dict[str, str],
    label_numbers: dict[str, str],
    label_routes: dict[str, str],
    bibliography_numbers: dict[str, int],
) -> dict[str, int]:
    rewritten = 0
    unresolved = 0
    citations = 0
    for anchor in article.xpath(".//a[@href]"):
        href = anchor.get("href") or ""
        if not href.startswith("#"):
            continue
        label = href[1:]
        if not label:
            continue
        target = label_to_stable.get(label, label)
        target_route = id_to_route.get(target) or label_routes.get(label)
        if target_route:
            anchor.set("href", relative_href(current_slug, target_route, target))
            if label in label_numbers:
                anchor.text = label_numbers[label]
                for child in list(anchor):
                    anchor.remove(child)
            anchor.set("aria-label", f"Rujukan {label_numbers.get(label, label)}")
            rewritten += 1
        elif not article.xpath(f".//*[@id={json.dumps(label)}]"):
            unresolved += 1
    for citation in list(article.xpath(".//*[contains(concat(' ',normalize-space(@class),' '),' citation ')]")):
        keys = (citation.get("data-cites") or "").split()
        if not keys:
            continue
        citation.text = "["
        for index, key in enumerate(keys):
            if key not in bibliography_numbers:
                unresolved += 1
                continue
            if index:
                separator = html.Element("span")
                separator.text = ", "
                citation.append(separator)
            link = html.Element(
                "a",
                {
                    "href": relative_href(current_slug, "daftar-pustaka", f"BIB-{key}"),
                    "aria-label": f"Rujukan bibliografi {bibliography_numbers[key]}",
                },
            )
            link.text = str(bibliography_numbers[key])
            citation.append(link)
        tail = html.Element("span")
        tail.text = "]"
        citation.append(tail)
        citations += 1
    return {"references_rewritten": rewritten, "citations_rewritten": citations, "unresolved": unresolved}


def book_navigation(current_slug: str) -> etree._Element:
    nav = html.Element("nav", {"class": "book-nav", "aria-label": "Daftar isi buku"})
    heading = html.Element("p", {"class": "book-nav__title"})
    heading.text = "Isi buku"
    nav.append(heading)
    listing = html.Element("ol")
    home = html.Element("li")
    home_link = html.Element("a", {"href": "../index.html" if current_slug else "index.html"})
    home_link.text = "Beranda pembaca"
    if not current_slug:
        home_link.set("aria-current", "page")
    home.append(home_link)
    listing.append(home)
    for route in ROUTES:
        item = html.Element("li")
        link = html.Element("a", {"href": relative_href(current_slug, route["slug"])})
        prefix = f"Bab {route['number']}. " if route["number"] is not None else ""
        link.text = prefix + route["title"]
        if current_slug == route["slug"]:
            link.set("aria-current", "page")
        item.append(link)
        listing.append(item)
    for slug, title in (("daftar-pustaka", "Daftar Pustaka"), ("indeks", "Indeks"), ("tentang", "Tentang edisi")):
        item = html.Element("li")
        link = html.Element("a", {"href": relative_href(current_slug, slug)})
        link.text = title
        if current_slug == slug:
            link.set("aria-current", "page")
        item.append(link)
        listing.append(item)
    nav.append(listing)
    return nav


def qualify_external_links(article: etree._Element) -> None:
    """Mark optional outbound navigation without turning it into a dependency."""
    for anchor in list(article.xpath(".//a[@href]")):
        href = anchor.get("href", "")
        if re.match(r"^http://", href, flags=re.IGNORECASE):
            replacement = html.Element(
                "span",
                {
                    "class": "external-url-text",
                    "title": "Alamat HTTP sumber dipertahankan sebagai teks; tautan tidak diaktifkan.",
                },
            )
            replacement.text = visible_text(anchor) or href
            replacement.tail = anchor.tail
            parent = anchor.getparent()
            if parent is not None:
                parent.replace(anchor, replacement)
            continue
        if not re.match(r"^https://", href, flags=re.IGNORECASE):
            continue
        rel = {token.casefold() for token in anchor.get("rel", "").split()}
        rel.update({"external", "noopener", "noreferrer"})
        if href.rstrip("/") == LICENSE_URL.rstrip("/"):
            rel.add("license")
        anchor.set("rel", " ".join(sorted(rel)))


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
    title_element.text = f"{title} — Analisis Fungsional dan Aljabar Operator"
    head.append(title_element)
    description = html.Element("meta", {"name": "description", "content": "Edisi Bahasa Indonesia yang dapat dibaca luring, dengan MathML dan navigasi semantik."})
    head.append(description)
    css_href = "../assets/reader.css" if slug else "assets/reader.css"
    head.append(html.Element("link", {"rel": "stylesheet", "href": css_href}))
    document.append(head)
    body = html.Element("body")
    skip = html.Element("a", {"class": "skip-link", "href": "#konten-utama"})
    skip.text = "Lewati ke isi utama"
    body.append(skip)
    header = html.Element("header", {"class": "site-header"})
    header_inner = html.Element("div", {"class": "site-header__inner"})
    site_link = html.Element("a", {"class": "site-title", "href": "../index.html" if slug else "index.html"})
    site_link.text = "Analisis Fungsional dan Aljabar Operator — Bahasa Indonesia"
    header_inner.append(site_link)
    badge = html.Element("span", {"class": "edition-badge"})
    badge.text = "Teks sumber lengkap"
    header_inner.append(badge)
    header.append(header_inner)
    body.append(header)
    layout = html.Element("div", {"class": "reader-layout"})
    layout.append(book_navigation(slug))
    main = html.Element("main", {"id": "konten-utama", "tabindex": "-1"})
    breadcrumbs = html.Element("nav", {"class": "breadcrumbs", "aria-label": "Jejak navigasi"})
    crumbs = html.Element("ol")
    first = html.Element("li")
    first_link = html.Element("a", {"href": "../index.html" if slug else "index.html"})
    first_link.text = "Buku"
    first.append(first_link)
    crumbs.append(first)
    current = html.Element("li")
    current.text = title
    crumbs.append(current)
    breadcrumbs.append(crumbs)
    main.append(breadcrumbs)
    main.append(article)
    if previous_item or next_item:
        unit_nav = html.Element("nav", {"class": "unit-navigation", "aria-label": "Navigasi unit"})
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
    paragraph.text = "Karya sumber: John M. Erdman. Terjemahan dan adaptasi teknis: "
    license_link = html.Element(
        "a",
        {
            "href": LICENSE_URL,
            "rel": "license external noopener noreferrer",
        },
    )
    license_link.text = "CC BY-SA 4.0"
    paragraph.append(license_link)
    license_link.tail = f". Dibantu oleh {MODEL} atas arahan pengguna. Edisi ini tidak menyiratkan dukungan, sponsor, atau persetujuan dari John M. Erdman maupun Portland State University."
    inner.append(paragraph)
    footer.append(inner)
    body.append(footer)
    document.append(body)
    return "<!doctype html>\n" + etree.tostring(document, method="html", encoding="unicode", pretty_print=False) + "\n"


def extract_article(raw_html: Path) -> etree._Element:
    parsed = html.parse(str(raw_html)).getroot()
    bodies = parsed.xpath("//body")
    if len(bodies) != 1:
        raise RuntimeError(f"expected one body in {raw_html}")
    article = html.Element("article", {"class": "reader-article"})
    for child in list(bodies[0]):
        if child.tag == "header" and child.get("id") == "title-block-header" and not visible_text(child):
            continue
        bodies[0].remove(child)
        article.append(child)
    return article


def build_bibliography_article(pandoc: str, build_root: Path, entries: list[tuple[str, str]]) -> tuple[etree._Element, str]:
    lines = [
        r"\documentclass{amsbook}",
        pandoc_macro_prelude(),
        r"\newcommand{\MR}[1]{MR #1}",
        r"\newcommand{\MRhref}[2]{#2}",
        r"\begin{document}",
        r"\chapter*{Daftar Pustaka}",
        r"\begin{enumerate}",
    ]
    for _, value in entries:
        lines.append(r"\item " + value)
    lines.extend([r"\end{enumerate}", r"\end{document}", ""])
    shadow = build_root / "shadow" / "daftar-pustaka.tex"
    raw = build_root / "raw" / "daftar-pustaka.html"
    write_text(shadow, "\n".join(lines))
    _, stderr = run_pandoc(pandoc, shadow, raw)
    article = extract_article(raw)
    h1 = article.xpath(".//h1")
    if len(h1) != 1:
        raise RuntimeError("bibliography heading closure mismatch")
    h1[0].set("id", "FAOA-2015-BIBLIOGRAPHY")
    items = article.xpath(".//ol/li")
    if len(items) != len(entries):
        raise RuntimeError(f"bibliography entry mismatch: {len(items)} / {len(entries)}")
    for item, (key, _) in zip(items, entries):
        item.set("id", f"BIB-{key}")
    return article, stderr


GREEK_NAMES = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ϵ",
    "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "ϑ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "varpi": "ϖ", "rho": "ρ",
    "varrho": "ϱ", "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ", "varphi": "ϕ",
    "chi": "χ", "psi": "ψ", "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ",
    "Lambda": "Λ", "Xi": "Ξ", "Pi": "Π", "Sigma": "Σ", "Upsilon": "Υ", "Phi": "Φ",
    "Psi": "Ψ", "Omega": "Ω", "infty": "∞", "ast": "∗", "perp": "⊥", "oplus": "⊕",
    "otimes": "⊗", "subseteq": "⊆", "supseteq": "⊇", "le": "≤", "ge": "≥", "ne": "≠",
    "to": "→", "rightarrow": "→", "leftarrow": "←", "mapsto": "↦", "times": "×", "cap": "∩", "cup": "∪",
}


def humanize_index_component(value: str) -> str:
    if "@" in value:
        value = value.split("@", 1)[1]
    value = value.replace("$", "")
    for command, symbol in sorted(GREEK_NAMES.items(), key=lambda item: -len(item[0])):
        value = re.sub(rf"\\{re.escape(command)}\b", symbol, value)
    value = re.sub(r"\\(?:df|emph|textit|textbf|textsc|mathrm|mathbf|mathfrak|mathcal|mathsf|operatorname)\s*\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\(?:C|R|Q|Z|N|K)\b", lambda match: {"\\C": "ℂ", "\\R": "ℝ", "\\Q": "ℚ", "\\Z": "ℤ", "\\N": "ℕ", "\\K": "𝕂"}[match.group(0)], value)
    value = value.replace(r"\,", " ").replace(r"\!", "").replace("~", " ")
    value = re.sub(r"\\[A-Za-z@]+", "", value)
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\s+", " ", value).strip(" ,")
    return value or "entri tanpa label"


def build_index_article(index_rows: list[dict[str, str]], id_to_route: dict[str, str]) -> etree._Element:
    article = html.Element("article", {"class": "reader-article"})
    title = html.Element("h1", {"id": "FAOA-2015-INDEX"})
    title.text = "Indeks"
    article.append(title)
    introduction = html.Element("p")
    introduction.text = "Indeks semantik ini mempertahankan hierarki istilah sumber dan menautkan setiap kemunculan ke segmen stabil, bukan ke nomor halaman yang berubah saat teks mengalir ulang."
    article.append(introduction)
    grouped: dict[str, list[str]] = {}
    for row in index_rows:
        parts = [humanize_index_component(part) for part in row["target_index_tex"].split("!")]
        display = " › ".join(part for part in parts if part)
        grouped.setdefault(display, []).append(row["parent_segment_id"])
    listing = html.Element("ul", {"class": "index-list"})
    for display in sorted(grouped, key=lambda value: value.casefold()):
        item = html.Element("li")
        term = html.Element("span", {"class": "index-term"})
        term.text = display
        item.append(term)
        occurrences = html.Element("span", {"class": "index-occurrences"})
        occurrences.text = " — "
        seen: set[str] = set()
        position = 0
        for segment_id in grouped[display]:
            if segment_id in seen or segment_id not in id_to_route:
                continue
            seen.add(segment_id)
            if position:
                separator = html.Element("span")
                separator.text = ", "
                occurrences.append(separator)
            link = html.Element("a", {"href": relative_href("indeks", id_to_route[segment_id], segment_id)})
            position += 1
            link.text = str(position)
            occurrences.append(link)
        item.append(occurrences)
        listing.append(item)
    article.append(listing)
    return article


def simple_article(stable_id: str, title_text: str, paragraphs: Iterable[str]) -> etree._Element:
    article = html.Element("article", {"class": "reader-article"})
    title = html.Element("h1", {"id": stable_id})
    title.text = title_text
    article.append(title)
    for value in paragraphs:
        paragraph = html.Element("p")
        paragraph.text = value
        article.append(paragraph)
    return article


def write_manifest(site_root: Path) -> tuple[list[dict[str, Any]], str]:
    rows = []
    for path in sorted((item for item in site_root.rglob("*") if item.is_file() and item.name != "MANIFEST.csv"), key=lambda item: item.relative_to(site_root).as_posix()):
        rows.append({"path": path.relative_to(site_root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    from io import StringIO
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["path", "bytes", "sha256"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    write_text(site_root / "MANIFEST.csv", stream.getvalue())
    tree_material = "".join(f"{row['path']}\0{row['bytes']}\0{row['sha256']}\n" for row in rows).encode("utf-8")
    return rows, sha256_bytes(tree_material)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the deterministic semantic id-ID FAOA reader")
    parser.add_argument("--site-root", type=Path, default=ROOT / "output" / "html")
    parser.add_argument("--build-root", type=Path, default=ROOT / "qa" / "build-html")
    parser.add_argument("--route-map", type=Path, default=ROOT / "backend" / "html_routes.jsonl")
    parser.add_argument("--report", type=Path, default=ROOT / "qa" / "HTML_BUILD_RESULT.json")
    parser.add_argument("--no-svg", action="store_true", help="Use transcripts only; intended for bounded conversion diagnostics")
    args = parser.parse_args()

    site_root = args.site_root if args.site_root.is_absolute() else ROOT / args.site_root
    build_root = args.build_root if args.build_root.is_absolute() else ROOT / args.build_root
    route_map_path = args.route_map if args.route_map.is_absolute() else ROOT / args.route_map
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    safe_reset(site_root, ROOT)
    safe_reset(build_root, ROOT)
    (build_root / "shadow").mkdir()
    (build_root / "raw").mkdir()
    (site_root / "assets").mkdir()
    shutil.copyfile(CSS_SOURCE, site_root / "assets" / "reader.css")

    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("pandoc is unavailable")
    pandoc_version = subprocess.run([pandoc, "--version"], capture_output=True, text=True, encoding="utf-8", check=True).stdout.splitlines()[0]

    unit_records = read_jsonl(ROOT / "backend" / "units.jsonl")
    semantic_units = read_jsonl(ROOT / "backend" / "semantic_units.jsonl")
    segments = read_jsonl(ROOT / "backend" / "segments.jsonl")
    relations = read_jsonl(ROOT / "backend" / "relations.jsonl")
    diagram_records = read_jsonl(DIAGRAM_TEXT)
    diagram_by_id = {record["diagram_id"]: record for record in diagram_records}
    if len(diagram_by_id) != len(diagram_records):
        raise RuntimeError("duplicate diagram IDs")
    label_numbers, label_routes, label_kinds = load_aux_numbers()
    label_to_stable = label_maps(semantic_units, relations)
    bibliography = bibliography_entries()
    bibliography_numbers = {key: index for index, (key, _) in enumerate(bibliography, start=1)}

    route_by_filename = {route["file"]: route for route in ROUTES}
    expected_units = {record["id"]: record for record in unit_records if record.get("record_type") == "unit"}
    input_receipts = []
    for route in ROUTES:
        record = expected_units[route["unit_id"]]
        path = ROOT / record["target_path"]
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if actual != {"bytes": record["target_bytes"], "sha256": record["target_sha256"]}:
            raise RuntimeError(f"target authority mismatch: {path}")
        input_receipts.append({"path": record["target_path"], **actual})
    canonical_before = {
        "master": {"bytes": MASTER.stat().st_size, "sha256": sha256_file(MASTER)},
        "pdf": {
            "bytes": (ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf").stat().st_size,
            "sha256": sha256_file(ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf"),
        },
        "diagxy": {"bytes": DIAGXY.stat().st_size, "sha256": sha256_file(DIAGXY)},
        "diagram_text": {"bytes": DIAGRAM_TEXT.stat().st_size, "sha256": sha256_file(DIAGRAM_TEXT)},
    }

    id_to_route: dict[str, str] = {}
    for route in ROUTES:
        id_to_route[route["unit_id"]] = route["slug"]
    for record in semantic_units:
        id_to_route[record["id"]] = route_for_target_path(record["target_path"])
    for record in segments:
        id_to_route[record["id"]] = route_for_target_path(record["target_path"])
    for record in diagram_records:
        id_to_route[record["diagram_id"]] = route_for_target_path(record["source_file"])
    for label, slug in label_routes.items():
        id_to_route[label] = slug
    id_to_route.update({f"BIB-{key}": "daftar-pustaka" for key, _ in bibliography})
    id_to_route.update({
        "FAOA-2015-HTML-READER": "",
        "FAOA-2015-BIBLIOGRAPHY": "daftar-pustaka",
        "FAOA-2015-INDEX": "indeks",
        "FAOA-2015-ABOUT": "tentang",
    })

    diagram_sources: dict[str, str] = {}
    for route in ROUTES:
        source_key = f"source/id-ID/{route['file']}"
        local_records = [record for record in diagram_records if record["source_file"].replace("\\", "/") == source_key]
        diagram_sources.update(diagram_source_blocks(route, local_records))
    if set(diagram_sources) != set(diagram_by_id):
        raise RuntimeError("diagram source closure mismatch")

    svg_results = []
    svg_ids: set[str] = set()
    if not args.no_svg:
        diagram_asset_root = site_root / "assets" / "diagrams"
        diagram_asset_root.mkdir()
        svg_build_root = build_root / "diagrams"
        svg_build_root.mkdir()
        macro_prelude = pandoc_macro_prelude()
        for record in diagram_records:
            destination = diagram_asset_root / f"{record['diagram_id']}.svg"
            svg_results.append(render_diagram_svg(record, diagram_sources[record["diagram_id"]], svg_build_root, destination, macro_prelude))
            svg_ids.add(record["diagram_id"])

    articles: dict[str, etree._Element] = {}
    route_diagnostics: list[dict[str, Any]] = []
    installed_diagrams: set[str] = set()
    for route in ROUTES:
        filename = route["file"]
        local_segments = [record for record in segments if Path(record["target_path"]).name == filename]
        local_units = [record for record in semantic_units if Path(record["target_path"]).name == filename]
        local_diagrams = [record for record in diagram_records if Path(record["source_file"]).name == filename]
        shadow_text, local_diagram_sources = make_shadow(route, local_segments, local_diagrams, local_units)
        shadow = build_root / "shadow" / f"{route['slug']}.tex"
        raw = build_root / "raw" / f"{route['slug']}.html"
        write_text(shadow, shadow_text)
        _, stderr = run_pandoc(pandoc, shadow, raw)
        article = extract_article(raw)
        assigned_ids = assign_semantic_units(
            article, route, local_units, label_numbers, label_kinds
        )
        id_to_route.update(assigned_ids)
        installed = install_diagram_figures(article, diagram_by_id, local_diagram_sources, "../assets/diagrams/", svg_ids)
        installed_diagrams.update(installed)
        if route["slug"] == "prakata":
            install_preface_special_units(article, local_units, pandoc)
        add_local_toc(article)
        math_count, fallbacks = normalize_math(article)
        present_ids = [value for value in article.xpath(".//@id")]
        missing_segments = sorted(record["id"] for record in local_segments if record["id"] not in present_ids)
        duplicate_ids = sorted(identifier for identifier in set(present_ids) if present_ids.count(identifier) > 1)
        route_diagnostics.append({
            "route": route["slug"],
            "pandoc_warning_count": stderr.count("[WARNING]"),
            "pandoc_stderr": stderr,
            "mathml_count": math_count,
            "math_fallbacks": fallbacks,
            "segment_count": len(local_segments),
            "missing_segment_ids": missing_segments,
            "duplicate_ids": duplicate_ids,
            "diagram_count": len(installed),
        })
        articles[route["slug"]] = article

    if installed_diagrams != set(diagram_by_id):
        raise RuntimeError(f"diagram marker closure mismatch: {sorted(set(diagram_by_id) - installed_diagrams)}")

    reference_totals = {"references_rewritten": 0, "citations_rewritten": 0, "unresolved": 0}
    for route in ROUTES:
        result = rewrite_references(
            articles[route["slug"]], route["slug"], label_to_stable, id_to_route,
            label_numbers, label_routes, bibliography_numbers,
        )
        for key in reference_totals:
            reference_totals[key] += result[key]

    bibliography_article, bibliography_stderr = build_bibliography_article(pandoc, build_root, bibliography)
    bibliography_math, bibliography_fallbacks = normalize_math(bibliography_article)
    index_rows = list(csv.DictReader((ROOT / "backend" / "index_terms.csv").open(encoding="utf-8", newline="")))
    index_article = build_index_article(index_rows, id_to_route)
    about_article = simple_article(
        "FAOA-2015-ABOUT",
        "Tentang edisi ini",
        [
            "Ini adalah edisi Bahasa Indonesia lengkap dari teks sumber John M. Erdman, Functional Analysis and Operator Algebras: An Introduction, versi 4 Oktober 2015.",
            "Teks sumber, struktur matematis, latihan, petunjuk pembuktian, sitasi, dan indeks dipertahankan. Permukaan HTML ini menambahkan MathML, pengenal stabil, navigasi luring, diagram SVG, serta transkrip diagram berbahasa Indonesia.",
            f"Penerjemahan dan adaptasi teknis dibantu oleh {MODEL} atas arahan pengguna. Semua perubahan merupakan perubahan edisi turunan dan tidak menyiratkan dukungan dari penulis sumber atau institusinya.",
            "Karya sumber dan edisi turunan ini menggunakan CC BY-SA 4.0. DIAGXY.TEX milik Michael Barr dipakai tanpa perubahan untuk membangun diagram; kode paket tidak disajikan sebagai karya Erdman.",
        ],
    )
    home_article = simple_article(
        "FAOA-2015-HTML-READER",
        "Analisis Fungsional dan Aljabar Operator",
        [
            "Edisi keempat sumber, versi 4 Oktober 2015 — teks sumber lengkap Bahasa Indonesia.",
            "Pembaca ini memuat prakata, semua 17 bab, daftar pustaka, dan indeks. Bab 1–8 membentuk rute inti D20; Bab 9–17 merupakan lanjutan tingkat lanjut, bukan materi yang dihilangkan.",
            "Semua halaman dapat dibaca luring. Rumus disajikan sebagai MathML, rujukan memakai pengenal stabil, dan diagram mempunyai gambar SVG serta transkrip Bahasa Indonesia.",
        ],
    )
    status = html.Element("p", {"class": "status-note"})
    status.text = "Status: terjemahan teks sumber lengkap; lapisan penguasaan/solusi O001 dan jembatan spektral-kompak/SVD tetap merupakan komponen terpisah yang sedang disusun."
    home_article.append(status)
    chapter_list = html.Element("ol")
    for route in ROUTES:
        item = html.Element("li")
        link = html.Element("a", {"href": relative_href("", route["slug"])})
        prefix = f"Bab {route['number']}. " if route["number"] is not None else ""
        link.text = prefix + route["title"]
        item.append(link)
        role = html.Element("span", {"class": "course-badge"})
        role.text = route["role"]
        item.append(role)
        chapter_list.append(item)
    home_article.append(chapter_list)

    all_page_order = [(route["slug"], route["title"]) for route in ROUTES] + [
        ("daftar-pustaka", "Daftar Pustaka"), ("indeks", "Indeks"), ("tentang", "Tentang edisi")
    ]
    for index, route in enumerate(ROUTES):
        previous_item = all_page_order[index - 1] if index > 0 else None
        next_item = all_page_order[index + 1]
        page_path = site_root / route["slug"] / "index.html"
        write_text(page_path, page_document(articles[route["slug"]], route["slug"], route["title"], previous_item, next_item))
    auxiliary = [
        ("daftar-pustaka", "Daftar Pustaka", bibliography_article),
        ("indeks", "Indeks", index_article),
        ("tentang", "Tentang edisi", about_article),
    ]
    for offset, (slug, title, article) in enumerate(auxiliary, start=len(ROUTES)):
        previous_item = all_page_order[offset - 1]
        next_item = all_page_order[offset + 1] if offset + 1 < len(all_page_order) else None
        write_text(site_root / slug / "index.html", page_document(article, slug, title, previous_item, next_item))
    write_text(site_root / "index.html", page_document(home_article, "", "Beranda pembaca", None, all_page_order[0]))

    present_ids_by_route = {
        **{route["slug"]: set(articles[route["slug"]].xpath(".//@id")) for route in ROUTES},
        "daftar-pustaka": set(bibliography_article.xpath(".//@id")),
        "indeks": set(index_article.xpath(".//@id")),
        "tentang": set(about_article.xpath(".//@id")),
        "": set(home_article.xpath(".//@id")),
    }
    route_rows = []
    for identifier, slug in sorted(id_to_route.items()):
        if identifier not in present_ids_by_route.get(slug, set()):
            continue
        output_path = f"{slug}/index.html" if slug else "index.html"
        route_rows.append({
            "id": identifier,
            "record_type": "html_route",
            "route": slug,
            "output_path": output_path,
            "href": f"{output_path}#{identifier}",
            "locale": "id-ID",
        })
    write_text(route_map_path, "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in route_rows))
    site_route_map = site_root / "backend" / "html_routes.jsonl"
    write_text(site_route_map, route_map_path.read_text(encoding="utf-8"))
    manifest_rows, tree_hash = write_manifest(site_root)

    canonical_after = {
        "master": {"bytes": MASTER.stat().st_size, "sha256": sha256_file(MASTER)},
        "pdf": {
            "bytes": (ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf").stat().st_size,
            "sha256": sha256_file(ROOT / "output" / "pdf" / "analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf"),
        },
        "diagxy": {"bytes": DIAGXY.stat().st_size, "sha256": sha256_file(DIAGXY)},
        "diagram_text": {"bytes": DIAGRAM_TEXT.stat().st_size, "sha256": sha256_file(DIAGRAM_TEXT)},
    }
    if canonical_after != canonical_before:
        raise RuntimeError("canonical source/PDF changed during HTML build")
    failures = {
        "math_fallbacks": sum(len(route["math_fallbacks"]) for route in route_diagnostics) + len(bibliography_fallbacks),
        "missing_segment_ids": sum(len(route["missing_segment_ids"]) for route in route_diagnostics),
        "duplicate_ids": sum(len(route["duplicate_ids"]) for route in route_diagnostics),
        "unresolved_references": reference_totals["unresolved"],
        "pandoc_math_warnings": sum(route["pandoc_stderr"].count("Could not convert TeX math") for route in route_diagnostics) + bibliography_stderr.count("Could not convert TeX math"),
    }
    report = {
        "schema": "o008-html-build-result-v1",
        "status": "passed" if not any(failures.values()) else "failed",
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "toolchain": {
            "pandoc": pandoc_version,
            "python": sys.version.split()[0],
            "lxml": etree.LXML_VERSION,
            "latex": subprocess.run(["latex", "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines()[0] if not args.no_svg else "not invoked",
            "dvisvgm": subprocess.run(["dvisvgm", "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines()[0] if not args.no_svg else "not invoked",
        },
        "canonical_inputs_before": canonical_before,
        "canonical_inputs_after": canonical_after,
        "input_receipts": input_receipts,
        "routes": route_diagnostics,
        "route_count": len(all_page_order) + 1,
        "semantic_unit_count": len(semantic_units),
        "segment_count": len(segments),
        "diagram_count": len(diagram_records),
        "svg_count": len(svg_results),
        "svg_results": svg_results,
        "bibliography_entry_count": len(bibliography),
        "bibliography_mathml_count": bibliography_math,
        "index_occurrence_count": len(index_rows),
        "reference_totals": reference_totals,
        "failures": failures,
        "site_file_count_excluding_manifest": len(manifest_rows),
        "site_tree_sha256": tree_hash,
        "route_map_count": len(route_rows),
        "route_map_sha256": sha256_file(route_map_path),
        "manifest_sha256": sha256_file(site_root / "MANIFEST.csv"),
        "model_provenance": MODEL,
    }
    write_text(report_path, stable_json(report))
    print(stable_json({
        "status": report["status"],
        "routes": report["route_count"],
        "math_fallbacks": failures["math_fallbacks"],
        "pandoc_math_warnings": failures["pandoc_math_warnings"],
        "missing_segment_ids": failures["missing_segment_ids"],
        "duplicate_ids": failures["duplicate_ids"],
        "unresolved_references": failures["unresolved_references"],
        "site_tree_sha256": tree_hash,
        "report": str(report_path),
    }), end="")
    if report["status"] != "passed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
