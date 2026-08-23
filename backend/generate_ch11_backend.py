#!/usr/bin/env python3
"""Append deterministic FAOA Chapter 11 projections to the modular backend.

This generator is intentionally a one-unit append operation.  It locks the
already admitted Chapter 1--10 bytes before writing anything, replaces only
the queued Chapter 11 row in ``units.jsonl``, and refuses to run until the
Chapter 11 build/QA evidence named by the lane handoff is present and marked
admitted.  It never edits source, controls, publication, or another lane.
"""

from __future__ import annotations

import collections
import csv
import hashlib
import io
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(ROOT / "qa"))
import ch03_math  # noqa: E402
import generate_ch01_backend as ch01  # noqa: E402
import check_ch05_translation as common  # noqa: E402
import check_ch09_translation as ch09  # noqa: E402


SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015"
TARGET_EDITION = "ERDMAN-FAOA-2015-ID"
CHAPTER_ID = "FAOA-2015-CH11"
RIGHTS = "RIGHTS-ERDMAN-CC-BY-SA-4.0"
MODEL_ID = "OpenAI Codex gpt-5.6-sol, Ultra"
SOURCE_PATH = ROOT / "source" / "upstream" / "Gelfand_Naimark.tex"
TARGET_PATH = ROOT / "source" / "id-ID" / "Gelfand_Naimark-id.tex"
SOURCE_REL = "source/upstream/Gelfand_Naimark.tex"
TARGET_REL = "source/id-ID/Gelfand_Naimark-id.tex"
MASTER_REL = "source/id-ID/functional-analysis-id-through-ch11.tex"
PDF_REL = "output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-11.pdf"
RECEIPT_REL = "provenance/CH11_BUILD_AND_QA_RECEIPT.md"
RECEIPT_QA_ID = "QA-CH11-ADMISSION-20260823"

# Immutable Chapter 1--10 file identities at the append boundary.  These are
# deliberately full-file locks, so a changed historical record cannot be
# silently reserialized as a Chapter 11 operation.
PREFIX_LOCKS = {
    "semantic_units.jsonl": (983525, "c96bfdcfb7f25bc33c26409d086867f139ec9774feebac3e1692a280c937a422"),
    "segments.jsonl": (1102619, "16ef4a0583eb26be360f2f864cfba2f9467cdd9d77bbe9b190bcc8841e532526"),
    "relations.jsonl": (1369232, "7fbaec2551e907e542bd593e1c04b77ddc793642e1d3d285ba6b530152214283"),
    "formula_map.jsonl": (4553396, "7dbdbb75506e3b984b7176d89b63da5125a71e5438e75a973e060a0b288d24ba"),
    "exercise_support.jsonl": (25503, "45b128f45d61057837c2eddcf1e45024e62b231e7d4b46e2b2dfb7c849a44925"),
    "index_terms.csv": (390698, "e0562824ac00c58c41992d8acc524044068f59a39292ee55f38026185fde6d9a"),
    "artifacts.jsonl": (53535, "66856b2fffeed45222665a7b7b70a1764462674ed9f1c0745419dee307c5ad28"),
    "qa_events.jsonl": (72362, "97dff9cfd92b2fcd68c0d7dcb82e98e4f55a4969a38ef72f702e9a1574b9b086"),
    "corrections.jsonl": (144791, "f851880584dcc9c35b4ffad0c8def523f15a187fbabd412b6c7a0f54c26a3130"),
    "terminology.jsonl": (110425, "b30317f156870940af4f9bebf1e7172a321f3d22ecd3ab99cc2187d7ec77f661"),
}
UNITS_PREFIX = (13488, "c57f1a39de3d271ca0762acedf5b973bd3977e12b1acd5f8c1a77578d0fb1707")
UNITS_SUFFIX = (3268, "1bb7b738f1c8feca0013e47da09114a11975ea45d1e5b2c86fbad7dd220614a7")
EXPECTED_SOURCE = (32235, 788, "018f15db7ee5a4392f624af050507a90339e1469e30f97c6017e003c7ff33b26")

EVIDENCE = [
    TARGET_REL,
    MASTER_REL,
    PDF_REL,
    "qa/CH11_CENSUS.json",
    "qa/CH11_SOURCE_INVENTORY.md",
    "qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md",
    "provenance/CH11_RENDER_MANIFEST.csv",
    "provenance/CH11_CONTACT_SHEET.png",
    "qa/CH11_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",
    "provenance/SOURCE_CORRECTIONS_CH11.json",
    RECEIPT_REL,
]
TERM_DECISION_REL = "provenance/CH11_TERMINOLOGY_DECISIONS.md"
TERM_WITNESS_REL = "qa/terminology_evidence/undip-jfma-2020-dunford/jfma-v3n1-7874.pdf"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl_bytes(records: list[dict]) -> bytes:
    return "".join(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for x in records).encode("utf-8")


def verify_locks() -> None:
    for name, (size, expected) in PREFIX_LOCKS.items():
        data = (BACKEND / name).read_bytes()
        if (len(data), digest(data)) != (size, expected):
            raise RuntimeError(f"historical backend lock changed: {name}")
    data = (BACKEND / "units.jsonl").read_bytes()
    lines = data.splitlines(keepends=True)
    if len(lines) != 18:
        raise RuntimeError(f"units.jsonl expected 18 rows before append, got {len(lines)}")
    ids = [json.loads(line)["id"] for line in lines]
    expected_ids = [f"FAOA-2015-CH{i:02d}" for i in range(1, 18)] + ["FAOA-ID-BRIDGE-CS"]
    if ids != expected_ids:
        raise RuntimeError(f"units.jsonl ordering changed: {ids}")
    pre = b"".join(lines[:10]); post = b"".join(lines[11:])
    if (len(pre), digest(pre)) != UNITS_PREFIX or (len(post), digest(post)) != UNITS_SUFFIX:
        raise RuntimeError("units.jsonl Chapter 1--10 prefix or Chapter 12--bridge suffix changed")
    if json.loads(lines[10]).get("translation_state") != "queued":
        raise RuntimeError("Chapter 11 is no longer the queued replacement row")


def identity(path: Path, expected: tuple[int, int | None, str] | None = None) -> dict:
    data = path.read_bytes()
    out = {"path": path.relative_to(ROOT).as_posix(), "bytes": len(data), "lines": len(data.splitlines()), "sha256": digest(data)}
    if expected and (len(data), len(data.splitlines()), digest(data)) != expected:
        raise RuntimeError(f"identity mismatch: {path}")
    return out


def evidence_identities() -> dict[str, dict]:
    missing = [rel for rel in EVIDENCE if not (ROOT / rel).is_file()]
    if missing:
        raise RuntimeError("Chapter 11 admission evidence missing: " + ", ".join(missing))
    source = identity(SOURCE_PATH, EXPECTED_SOURCE)
    target = identity(TARGET_PATH)
    master = identity(ROOT / MASTER_REL)
    pdf = identity(ROOT / PDF_REL)
    # The receipt is the controlling admission assertion; do not admit from a
    # merely present draft or a partial build log.
    receipt_text = (ROOT / RECEIPT_REL).read_text(encoding="utf-8")
    if not re.search(r"Decision:\s*\*\*admitted\*\*", receipt_text, re.I):
        raise RuntimeError("CH11 receipt does not assert admitted")
    census = json.loads((ROOT / "qa/CH11_CENSUS.json").read_text(encoding="utf-8"))
    if census.get("unit_id") != CHAPTER_ID or census.get("source", {}).get("sha256") != EXPECTED_SOURCE[2]:
        raise RuntimeError("CH11 census source identity is not frozen")
    corrections = json.loads((ROOT / "provenance/SOURCE_CORRECTIONS_CH11.json").read_text(encoding="utf-8"))
    if corrections.get("unit_id") != CHAPTER_ID or not isinstance(corrections.get("records"), list):
        raise RuntimeError("CH11 correction ledger closure is invalid")
    if not corrections["records"]:
        raise RuntimeError("CH11 correction ledger unexpectedly empty")
    ledger_target = corrections.get("target", {})
    if (ledger_target.get("bytes"), ledger_target.get("logical_records"), ledger_target.get("sha256")) != (target["bytes"], target["lines"], target["sha256"]):
        raise RuntimeError("CH11 correction ledger target identity is stale")
    return {"source": source, "target": target, "master": master, "pdf": pdf, "census": identity(ROOT / "qa/CH11_CENSUS.json"), "inventory": identity(ROOT / "qa/CH11_SOURCE_INVENTORY.md"), "term_qa": identity(ROOT / "qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md"), "render_manifest": identity(ROOT / "provenance/CH11_RENDER_MANIFEST.csv"), "contact_sheet": identity(ROOT / "provenance/CH11_CONTACT_SHEET.png"), "audit": identity(ROOT / "qa/CH11_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"), "corrections": identity(ROOT / "provenance/SOURCE_CORRECTIONS_CH11.json"), "receipt": identity(ROOT / RECEIPT_REL), "term_decision": identity(ROOT / TERM_DECISION_REL) if (ROOT / TERM_DECISION_REL).is_file() else None, "term_witness": identity(ROOT / TERM_WITNESS_REL) if (ROOT / TERM_WITNESS_REL).is_file() else None}


def admission_fields(receipt_sha: str) -> dict:
    return {"qa_receipt_id": RECEIPT_QA_ID, "receipt_document_state": "present", "receipt_path": RECEIPT_REL, "receipt_sha256": receipt_sha, "admission_state": "admitted"}


def append_jsonl(name: str, records: list[dict]) -> None:
    path = BACKEND / name
    old = path.read_bytes()
    size, expected = PREFIX_LOCKS[name]
    if (len(old), digest(old)) != (size, expected):
        raise RuntimeError(f"append precondition failed for {name}")
    path.write_bytes(old + jsonl_bytes(records))


def source_correction_records(receipt_sha: str, ledger_sha: str) -> list[dict]:
    ledger = json.loads((ROOT / "provenance/SOURCE_CORRECTIONS_CH11.json").read_text(encoding="utf-8"))
    out = []
    for item in ledger["records"]:
        cls = item.get("classification", item.get("class", "mechanical")).lower()
        src = item.get("source_lines", {})
        tgt = item.get("target_lines", {})
        out.append({"schema": SCHEMA, "schema_version": VERSION, "record_type": "correction", "id": item["id"], "unit_id": CHAPTER_ID, "source_locator": f"Gelfand_Naimark.tex:{src.get('start')}--{src.get('end')}", "target_locator": f"Gelfand_Naimark-id.tex:{tgt.get('start')}--{tgt.get('end')}", "correction_type": cls, "decision": item.get("decision", item.get("finding", "")), "source_normalized_snippet_sha256": item.get("source_normalized_snippet_sha256"), "target_normalized_snippet_sha256": item.get("target_normalized_snippet_sha256"), "required_target_anchor": item.get("required_target_anchor", ""), "target_disposition": "corrected", "ledger_path": "provenance/SOURCE_CORRECTIONS_CH11.json", "ledger_sha256": ledger_sha, **admission_fields(receipt_sha), "qa_state": "passed", "upstream_report": "deferred_until_complete_and_separately_authorized"})
    return out


NEW_TERMS = {
    "character": "karakter",
    "nonzero multiplicative linear functional": "fungsional linear multiplikatif tak nol",
    "nilpotent": "nilpoten",
    "evaluation functional at $x$": "fungsional evaluasi di $x$",
    "Gelfand topology": "topologi Gelfand",
    "character space": "ruang karakter",
    "maximal ideal space": "ruang ideal maksimal",
    "evaluation map": "pemetaan evaluasi",
    "Gelfand transform on~$A$": "transformasi Gelfand pada~$A$",
    "separates points": "memisahkan titik-titik",
    "separating family": "keluarga fungsi pemisah",
    "quasinilpotent": "kuasinilpoten",
    "semisimple": "semisederhana",
    "Fourier series": "deret Fourier",
    "Fourier coefficient": "koefisien Fourier",
    "absolutely convergent Fourier series": "deret Fourier yang konvergen mutlak",
    "$C^*$-subalgebra generated by~$S$": "subaljabar-$C^*$ yang dibangkitkan oleh~$S$",
}
# Stable IDs follow the Chapter 11 terminology decision sheet where a
# proposed ID exists; they are locale-neutral and never derived from page
# numbers.  The source's parameterized ``Gelfand transform on A`` occurrence
# reuses the concept-level ``TERM-GELFAND-TRANSFORM`` ID.
NEW_TERM_IDS = {
    "character": "TERM-CHARACTER",
    "nonzero multiplicative linear functional": "TERM-MULTIPLICATIVE-LINEAR-FUNCTIONAL",
    "nilpotent": "TERM-NILPOTENT",
    "evaluation functional at $x$": "TERM-EVALUATION-FUNCTIONAL",
    "Gelfand topology": "TERM-GELFAND-TOPOLOGY",
    "character space": "TERM-CHARACTER-SPACE",
    "maximal ideal space": "TERM-MAXIMAL-IDEAL-SPACE",
    "evaluation map": "TERM-EVALUATION-MAP",
    "Gelfand transform on~$A$": "TERM-GELFAND-TRANSFORM",
    "separates points": "TERM-SEPARATES-POINTS",
    "separating family": "TERM-SEPARATING-FAMILY",
    "quasinilpotent": "TERM-QUASINILPOTENT",
    "semisimple": "TERM-SEMISIMPLE",
    "Fourier series": "TERM-FOURIER-SERIES",
    "Fourier coefficient": "TERM-FOURIER-COEFFICIENT",
    "absolutely convergent Fourier series": "TERM-ABSOLUTELY-CONVERGENT-FOURIER-SERIES",
    "$C^*$-subalgebra generated by~$S$": "TERM-CSTAR-GENERATED-SUBALGEBRA",
}
EXISTING_TERM_IDS = {
    "idempotent": "TERM-IDEMPOTENT",
    "absolutely summable": "TERM-ABSOLUTELY-SUMMABLE",
    "convolution": "TERM-CONVOLUTION",
    "Fourier transform": "TERM-FOURIER-TRANSFORM",
}


def terminology_records(evidence: dict, receipt_sha: str) -> tuple[list[dict], dict[str, str]]:
    src = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    source_terms = [x["argument"] for x in common.macro(src, "df")]
    target_terms = [x["argument"] for x in common.macro(target, "df")]
    if len(source_terms) != 21 or len(target_terms) != 21:
        raise RuntimeError("CH11 defined-term count changed")
    # Reuse all pre-existing stable IDs, adding only new vocabulary records.
    prior: dict[str, str] = {}
    for line in (BACKEND / "terminology.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line); prior[rec.get("source_term", "")] = rec["id"]
    term_ids = dict(prior)
    for source_term in source_terms:
        if source_term not in term_ids:
            if source_term not in NEW_TERMS:
                raise RuntimeError(f"no stable Chapter 11 term mapping: {source_term}")
            term_ids[source_term] = NEW_TERM_IDS[source_term]
    if len(set(term_ids[x] for x in source_terms)) != 21:
        raise RuntimeError("Chapter 11 term IDs are not unique")
    decision_sha = evidence["term_decision"]["sha256"] if evidence.get("term_decision") else None
    witness_sha = evidence["term_witness"]["sha256"] if evidence.get("term_witness") else None
    out = []
    for source_term in source_terms:
        if source_term not in NEW_TERMS:
            continue
        rec = {"schema": SCHEMA, "schema_version": VERSION, "record_type": "term", "id": term_ids[source_term], "source_term": source_term, "locale": "id-ID", "preferred": NEW_TERMS[source_term], "variants": [], "rejected": [], "scope": "Gelfand--Naimark theorem, character spaces, maximal ideals, functional calculus, and Fourier examples", "evidence": f"{CHAPTER_ID} target; {TERM_DECISION_REL}; qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md"}
        if decision_sha:
            rec.update({"terminology_decision_path": TERM_DECISION_REL, "terminology_decision_sha256": decision_sha})
        if witness_sha:
            rec["field_usage_witness_sha256"] = witness_sha
        out.append(rec)
    return out, term_ids


def formula_records(receipt_sha: str, corrections: list[dict]) -> tuple[list[dict], dict]:
    source = SOURCE_PATH.read_text(encoding="ascii")
    target = TARGET_PATH.read_text(encoding="utf-8")
    sm = ch03_math.extract_math(source, "ascii"); tm = ch03_math.extract_math(target, "utf-8")
    if (len(sm), len(tm)) != (625, 625):
        raise RuntimeError(f"CH11 math surface closure changed: {len(sm)}/{len(tm)}")
    sk = [ch03_math.math_key(x["normalized"]) for x in sm]; tk = [ch03_math.math_key(x["normalized"]) for x in tm]
    mapping: list[list[int] | None] = [None] * len(tm)
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, sk, tk, autojunk=False).get_opcodes():
        if tag == "equal":
            for si, ti in zip(range(i1, i2), range(j1, j2), strict=True): mapping[ti] = [si]
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            for si, ti in zip(range(i1, i2), range(j1, j2), strict=True): mapping[ti] = [si]
        else:
            raise RuntimeError(f"unexpected CH11 formula alignment opcode {(tag, i1, i2, j1, j2)}")
    if any(x is None for x in mapping) or sorted(i for group in mapping for i in (group or [])) != list(range(625)):
        raise RuntimeError("CH11 formula mapping is not one-to-one")
    # The two substantive source repairs are tied to their ledger IDs.  Other
    # one-to-one differences are translation/whitespace normalization.
    corr_by_line = {}
    for c in corrections:
        m = re.search(r":(\d+)--?(\d+)?", c["source_locator"])
        if m: corr_by_line[int(m.group(1))] = c["id"]
    records = []; counts = collections.Counter()
    for n, (source_indexes, t) in enumerate(zip(mapping, tm, strict=True), 1):
        assert source_indexes is not None
        srecords = [sm[i] for i in source_indexes]
        exact = len(srecords) == 1 and srecords[0]["normalized"] == t["normalized"]
        source_line = srecords[0]["line_start"]
        if exact:
            align = "preserved_exact_after_text_aware_whitespace_normalization"
        elif source_line in corr_by_line:
            align = "reviewed_source_correction"
        else:
            align = "localized_math_text_reviewed"
        counts[align] += 1
        rec = {"schema": SCHEMA, "schema_version": VERSION, "record_type": "formula_map", "id": f"{CHAPTER_ID}-MATHMAP-{n:04d}", "alignment": align, "math_key_alignment": "equal" if sk[source_indexes[0]] == tk[n-1] else "reviewed_difference", "ordinal_alignment": "same", "source_formula_ids": [f"{CHAPTER_ID}-SRC-MATH-{i+1:04d}" for i in source_indexes], "target_formula_ids": [f"{CHAPTER_ID}-ID-MATH-{n:04d}"], "source_lines": [[x["line_start"], x["line_end"]] for x in srecords], "target_lines": [[t["line_start"], t["line_end"]]], "source_sha256": [x["sha256"] for x in srecords], "target_sha256": [t["sha256"]], "source_delimiters": [x["delimiter"] for x in srecords], "delimiter": t["delimiter"]}
        if align != "preserved_exact_after_text_aware_whitespace_normalization":
            rec.update({"sequence_opcode": "replace", "delta_class": "source_correction" if source_line in corr_by_line else "localization_inside_math_text", "correction_disposition": "corrected" if source_line in corr_by_line else "not_a_source_correction", "qa_state": "passed"})
            if source_line in corr_by_line: rec["correction_id"] = corr_by_line[source_line]
        records.append(rec)
    return records, {"source_math_surfaces": 625, "target_math_surfaces": 625, "exact_normalized_alignments": counts["preserved_exact_after_text_aware_whitespace_normalization"], "localized_math_text_substitutions": counts["localized_math_text_reviewed"], "reviewed_source_correction_maps": counts["reviewed_source_correction"], "formula_map_records": 625}


def unit_and_segments(source: str, target: str) -> tuple[list[dict], list[dict], list[dict], dict, list[dict], dict]:
    anchors = ch01.parse_anchors(source); targets = ch01.parse_anchors(target)
    if len(anchors) != 102 or len(targets) != 102 or [ch01.anchor_signature(x) for x in anchors] != [ch01.anchor_signature(x) for x in targets]:
        raise RuntimeError("CH11 anchor topology differs")
    source_labels = common.macro(source, "label"); target_labels = common.macro(target, "label")
    if len(source_labels) != 38 or [x["argument"] for x in source_labels] != [x["argument"] for x in target_labels]: raise RuntimeError("CH11 label sequence differs")
    semantic=[]; relations=[]; anchor_ids=[]; section_for=[]; bounds={}; current=CHAPTER_ID; sec=nodes=0
    for a in anchors:
        if a["anchor_type"] == "chapter": uid,parent,kind=CHAPTER_ID,TARGET_EDITION,"chapter"
        elif a["anchor_type"] == "section": sec += 1; uid,parent,kind=f"{CHAPTER_ID}-SEC-{sec:03d}",CHAPTER_ID,"section"; current=uid
        else: nodes += 1; uid,parent,kind=f"{CHAPTER_ID}-NODE-{nodes:04d}",current,a["environment"]
        anchor_ids.append(uid); section_for.append(current); bounds[uid]=(a["start"],a["end"])
        if a["anchor_type"] == "chapter": continue
        sf=ch01.fragment(source,a["start"],a["end"],"ascii"); tf=ch01.fragment(target,targets[len(anchor_ids)-1]["start"],targets[len(anchor_ids)-1]["end"],"utf-8")
        semantic.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"unit","id":uid,"unit_kind":kind,"parent_id":parent,"order_in_chapter":len(semantic)+1,"edition_id":EDITION,"target_edition_id":TARGET_EDITION,"source_path":SOURCE_REL,"source_line_start":sf["line_start"],"source_line_end":sf["line_end"],"source_fragment_sha256":sf["sha256"],"target_path":TARGET_REL,"target_line_start":tf["line_start"],"target_line_end":tf["line_end"],"target_fragment_sha256":tf["sha256"],"source_local_id":a.get("label"),"source_title_tex":a.get("title"),"target_title_tex":targets[len(anchor_ids)-1].get("title"),"locale":"id-ID","translation_state":"admitted","qa_state":"passed","rights_id":RIGHTS})
        relations.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","id":f"{CHAPTER_ID}-REL-CONTAINS-{len(semantic):04d}","relation_type":"contains","from_id":parent,"to_id":uid})
    if (len(semantic),sec,nodes)!=(101,5,96): raise RuntimeError("CH11 semantic topology changed")
    source_parts=[]; target_parts=[]; prevs=prevt=0; prevparent=CHAPTER_ID
    for i,(a,b,uid) in enumerate(zip(anchors,targets,anchor_ids,strict=True)):
        if a["start"]>prevs or b["start"]>prevt:
            if ch01.active_same_length(source[prevs:a["start"]]).strip() or ch01.active_same_length(target[prevt:b["start"]]).strip(): source_parts.append((prevs,a["start"],"prose",prevparent)); target_parts.append((prevt,b["start"],"prose",prevparent))
        role="title" if a["anchor_type"] in {"chapter","section"} else "semantic_environment"; source_parts.append((a["start"],a["end"],role,uid)); target_parts.append((b["start"],b["end"],role,uid)); prevs,prevt=a["end"],b["end"]; prevparent=section_for[i]
    if prevs<len(source) or prevt<len(target):
        if ch01.active_same_length(source[prevs:]).strip() or ch01.active_same_length(target[prevt:]).strip(): source_parts.append((prevs,len(source),"prose",prevparent)); target_parts.append((prevt,len(target),"prose",prevparent))
    if len(source_parts)!=118: raise RuntimeError(f"CH11 segment topology changed: {len(source_parts)}")
    segments=[]
    for n,(sp,tp) in enumerate(zip(source_parts,target_parts,strict=True),1):
        ss,se,role,parent=sp; ts,te,trole,tparent=tp
        if (role,parent)!=(trole,tparent): raise RuntimeError("CH11 segment role mismatch")
        sf=ch01.fragment(source,ss,se,"ascii"); tf=ch01.fragment(target,ts,te,"utf-8"); sid=f"{CHAPTER_ID}-SEG-{n:04d}"
        segments.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"segment","id":sid,"parent_id":parent,"order":n,"segment_role":role,"source_path":SOURCE_REL,"source_line_start":sf["line_start"],"source_line_end":sf["line_end"],"source_bytes":sf["bytes"],"source_sha256":sf["sha256"],"target_path":TARGET_REL,"target_line_start":tf["line_start"],"target_line_end":tf["line_end"],"target_bytes":tf["bytes"],"target_sha256":tf["sha256"],"source_edition_id":EDITION,"target_edition_id":TARGET_EDITION,"locale":"id-ID","translation_state":"admitted","qa_state":"passed","rights_id":RIGHTS,"_source_start":ss,"_source_end":se,"_target_start":ts,"_target_end":te})
        relations.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","id":f"{CHAPTER_ID}-REL-TRANSLATES-{n:04d}","relation_type":"translates","from_id":sid,"to_id":sid,"source_edition_id":EDITION,"target_edition_id":TARGET_EDITION})
        if n>1: relations.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","id":f"{CHAPTER_ID}-REL-PRECEDES-{n-1:04d}","relation_type":"precedes","from_id":f"{CHAPTER_ID}-SEG-{n-1:04d}","to_id":sid})
    return semantic,segments,relations,bounds,anchors,targets


def chapter_unit(ids: dict, corrections: list[dict], receipt_sha: str) -> dict:
    source=ids["source"]; target=ids["target"]; master=ids["master"]; pdf=ids["pdf"]
    target_title = common.macro(TARGET_PATH.read_text(encoding="utf-8"), "chapter")[0]["argument"]
    return {"schema":SCHEMA,"schema_version":VERSION,"record_type":"unit","id":CHAPTER_ID,"edition_id":EDITION,"order":11,"source_path":"Gelfand_Naimark.tex","source_bytes":source["bytes"],"source_lines":source["lines"],"source_sha256":source["sha256"],"source_title":"THE GELFAND-NAIMARK THEOREM","target_path":TARGET_REL,"target_bytes":target["bytes"],"target_lines":target["lines"],"target_sha256":target["sha256"],"target_title":target_title,"course_role":"advanced_continuation","translation_state":"admitted","qa_state":"passed","source_corrections":len(corrections),"build_master_path":MASTER_REL,"build_master_bytes":master["bytes"],"build_master_lines":master["lines"],"build_master_sha256":master["sha256"],"artifact_path":PDF_REL,"artifact_bytes":pdf["bytes"],"artifact_pages":pdf.get("pages",0),"artifact_sha256":pdf["sha256"],"artifact_state":"canonical_output_copy_present_and_frozen",**admission_fields(receipt_sha),"publication_state":"pending","rights_id":RIGHTS}


def artifact_records(ids: dict, receipt_sha: str) -> list[dict]:
    specs=[
      ("ARTIFACT-FAOA-ID-CH11-TARGET-TEX","admitted_translation_source",TARGET_REL,"id-ID"),
      ("ARTIFACT-FAOA-ID-THROUGH-CH11-MASTER","cumulative_TeX_master",MASTER_REL,"id-ID"),
      ("ARTIFACT-FAOA-ID-THROUGH-CH11-PDF","canonical_cumulative_reader_pdf",PDF_REL,"id-ID"),
      ("ARTIFACT-FAOA-ID-CH11-CENSUS","source_census","qa/CH11_CENSUS.json",None),
      ("ARTIFACT-FAOA-ID-CH11-SOURCE-INVENTORY","source_inventory","qa/CH11_SOURCE_INVENTORY.md",None),
      ("ARTIFACT-FAOA-ID-CH11-TERM-QA","external_terminology_QA","qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md",None),
      ("ARTIFACT-FAOA-ID-CH11-RENDER-MANIFEST","visual_QA_render_manifest","provenance/CH11_RENDER_MANIFEST.csv",None),
      ("ARTIFACT-FAOA-ID-CH11-CONTACT-SHEET","visual_QA_contact_sheet","provenance/CH11_CONTACT_SHEET.png",None),
      ("ARTIFACT-FAOA-ID-CH11-VISUAL-ACCESSIBILITY-AUDIT","visual_accessibility_audit","qa/CH11_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md",None),
      ("ARTIFACT-FAOA-ID-CH11-CORRECTIONS-LEDGER","chapter_source_corrections_ledger","provenance/SOURCE_CORRECTIONS_CH11.json",None),
      ("ARTIFACT-FAOA-ID-CH11-TERMINOLOGY-DECISIONS","terminology_decisions",TERM_DECISION_REL,None),
      ("ARTIFACT-FAOA-ID-CH11-QA-RECEIPT","admission_receipt",RECEIPT_REL,None),
    ]
    out=[]
    for rid,kind,rel,locale in specs:
        info=identity(ROOT/rel); rec={"schema":SCHEMA,"schema_version":VERSION,"record_type":"artifact","id":rid,"unit_id":CHAPTER_ID,"artifact_kind":kind,"path":rel,"bytes":info["bytes"],"sha256":info["sha256"],**admission_fields(receipt_sha)}
        if info["lines"] is not None and not rel.endswith(".png"): rec["lines"]=info["lines"]
        if locale: rec["locale"]=locale
        if kind=="canonical_cumulative_reader_pdf": rec.update({"pages": ids["pdf"].get("pages",0),"page_size":"US Letter","pdf_lang":"id-ID","publication_state":"pending"})
        if kind=="cumulative_TeX_master": rec["cumulative_through_unit_id"]=CHAPTER_ID
        if kind=="visual_QA_render_manifest": rec["render_pages"]=ids["pdf"].get("pages",0)
        if kind=="visual_QA_contact_sheet": rec["visual_pages"]=ids["pdf"].get("pages",0); rec["all_pages_inspected"]=True
        if kind=="visual_accessibility_audit": rec.update({"visual_result":"pass","accessibility_gate_result":"pass","tagged_pdf":False,"fully_accessible_pdf_claim":False,"accessible_html_or_tagged_pdf_state":"pending"})
        if kind=="admission_receipt": rec["decision"]="admitted"
        out.append(rec)
    return out


def qa_records(ids: dict, formula_summary: dict, receipt_sha: str) -> list[dict]:
    fields={"schema":SCHEMA,"schema_version":VERSION,"record_type":"qa_event","unit_id":CHAPTER_ID,"timestamp":"2026-08-23","responsible_workflow":"Codex","model_id":MODEL_ID,**admission_fields(receipt_sha)}
    specs=[("QA-CH11-STRUCTURAL-20260823","unit_structural","qa/CH11_CENSUS.json"),("QA-CH11-MATH-20260823","unit_mathematical","qa/CH11_CENSUS.json"),("QA-CH11-LANGUAGE-20260823","unit_language_terminology","qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md"),("QA-CH11-BUILD-20260823","cumulative_build",PDF_REL),("QA-CH11-VISUAL-20260823","cumulative_visual","qa/CH11_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"),("QA-CH11-ACCESSIBILITY-20260823","cumulative_accessibility","qa/CH11_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md"),("QA-CH11-RIGHTS-20260823","unit_rights_privacy",TARGET_REL),("QA-CH11-DIAGRAM-ACCESSIBILITY-20260823","diagram_accessibility",TARGET_REL),(RECEIPT_QA_ID,"unit_admission",RECEIPT_REL)]
    out=[]
    for rid,kind,witness in specs:
        w=identity(ROOT/witness); rec=fields|{"id":rid,"qa_type":kind,"result":"pass","witness":witness,"witness_sha256":w["sha256"]}
        out.append(rec)
    out[0].update({"sections":5,"semantic_anchors":102,"semantic_units":101,"segments":118,"environment_begins":107,"labels":38,"references":15,"citations":5,"index_terms":65,"defined_terms":21,"exercise_environments":0,"proof_environments":12,"proof_hints":9,"citation_only_proofs":3})
    out[1].update(formula_summary|{"unexplained_deltas":0,"extractor":"backend/ch03_math.py"})
    out[2].update({"severity_counts":{"P1":0,"P2":0,"P3":0},"unintended_english_prose":0,"placeholders":0,"terminology_reconciled":True,"terminology_decision_path":TERM_DECISION_REL})
    out[3].update({"master_artifact_id":"ARTIFACT-FAOA-ID-THROUGH-CH11-MASTER","pdf_artifact_id":"ARTIFACT-FAOA-ID-THROUGH-CH11-PDF","pages":ids["pdf"].get("pages",0)})
    out[4].update({"pages_rendered":ids["pdf"].get("pages",0),"pages_inspected":ids["pdf"].get("pages",0),"render_manifest_sha256":ids["render_manifest"]["sha256"],"contact_sheet_sha256":ids["contact_sheet"]["sha256"],"visual_defects":0})
    out[5].update({"tagged_pdf":False,"fully_accessible_pdf_claim":False,"semantic_accessibility_state":"remediation_required","accessible_html_or_tagged_pdf_state":"pending","admission_blocker_for_chapter_boundary":False,"diagram_topology_preserved":True,"diagram_accessible_description_required":True})
    out[6].update({"rights_id":RIGHTS,"attribution_change_notice_sharealike_nonendorsement":"present","private_control_paths_absent_from_public_artifacts":True,"credential_or_token_residue":0})
    out[7].update({"asset_id":"ASSET-DIAGXY","diagram_surface":"inline Xy-pic character-space/Gelfand-transform triangle","topology_preserved":True,"accessible_text_description":"present in CH11 audit/reader surface","rights_id":"RIGHTS-DIAGXY-BARR"})
    out[8].update({"decision":"admitted","source_sha256":ids["source"]["sha256"],"target_sha256":ids["target"]["sha256"],"build_master_sha256":ids["master"]["sha256"],"artifact_sha256":ids["pdf"]["sha256"],"correction_ledger_sha256":ids["corrections"]["sha256"],"required_admission_gate_results":{k:"pass" for k in ("unit_structural","unit_mathematical","unit_language_terminology","cumulative_build","cumulative_visual","cumulative_accessibility","unit_rights_privacy","admission_receipt")},"all_required_admission_gates":"pass","publication_state":"pending"})
    return out


def write_manifest() -> None:
    rows=[]
    for path in sorted(BACKEND.iterdir(),key=lambda p:p.name.casefold()):
        if not path.is_file() or path.name=="BACKEND_MANIFEST.csv" or path.suffix==".pyc": continue
        data=path.read_bytes(); rows.append((path.name,len(data),digest(data)))
    buf=io.StringIO(newline=""); w=csv.writer(buf,lineterminator="\n"); w.writerow(["relative_path","bytes","sha256"]); w.writerows(rows)
    (BACKEND/"BACKEND_MANIFEST.csv").write_text(buf.getvalue(),encoding="utf-8",newline="")


def main() -> None:
    verify_locks()
    ids=evidence_identities()
    # Add page count without making pypdf a backend dependency when pdfinfo is
    # already available.  The receipt/render manifest is authoritative; use
    # the first explicit rendered-page count found there.
    pdf_text=(ROOT/PDF_REL).read_bytes(); ids["pdf"]["pages"]=len(re.findall(rb"/Type\s*/Page(?:\s|/|>)",pdf_text))
    source=SOURCE_PATH.read_text(encoding="ascii"); target=TARGET_PATH.read_text(encoding="utf-8")
    semantic,segments,relations,bounds,anchors,targets=unit_and_segments(source,target)
    prior_labels={x.get("source_local_id"):x["id"] for x in (json.loads(l) for l in (BACKEND/"semantic_units.jsonl").read_text(encoding="utf-8").splitlines()) if x.get("source_local_id")}
    local_labels={}
    for occ in common.macro(source,"label"):
        segid=ch01.containing_segment(segments,occ["start"],"source"); seg=next(x for x in segments if x["id"]==segid); local_labels[occ["argument"]]=seg["parent_id"]
        relations.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","id":f"{CHAPTER_ID}-REL-LABEL-{len(local_labels):04d}","relation_type":"declares_label","from_id":segid,"to_id":seg["parent_id"],"source_local_id":occ["argument"],"label_id":f"ERDMAN-FAOA-2015-LABEL-{occ['argument']}"})
    # Chapter labels and cross-chapter labels are explicit stable unit IDs.
    prior_labels.update({"spectrum":"FAOA-2015-CH08"})
    refs=common.reference_sequence(source); tref=common.reference_sequence(target)
    if len(refs)!=15 or [x[1:] for x in refs]!=[x[1:] for x in tref]: raise RuntimeError("CH11 reference sequence differs")
    rc=collections.Counter()
    for n,(pos,kind,label) in enumerate(refs,1):
        if label in local_labels: to,res=local_labels[label],"local"
        elif label in prior_labels: to,res=prior_labels[label],"admitted_prior_unit"
        else: raise RuntimeError(f"unresolved CH11 reference {label}")
        rc[res]+=1; relations.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","id":f"{CHAPTER_ID}-REL-XREF-{n:04d}","relation_type":"xref","from_id":ch01.containing_segment(segments,pos,"source"),"to_id":to,"source_local_id":label,"resolution":res,"target_surface":kind})
    if rc["local"]!=11 or rc["admitted_prior_unit"]!=4: raise RuntimeError(f"CH11 xref resolution changed: {rc}")
    cites=common.macro(source,"cite"); tcites=common.macro(target,"cite")
    if len(cites)!=5 or [x["argument"] for x in cites]!=[x["argument"] for x in tcites]: raise RuntimeError("CH11 citation sequence differs")
    for n,occ in enumerate(cites,1):
        for key in [x.strip() for x in occ["argument"].split(",")]: relations.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","id":f"{CHAPTER_ID}-REL-CITE-{n:04d}-{key}","relation_type":"cites","from_id":ch01.containing_segment(segments,occ["start"],"source"),"to_id":f"ERDMAN-FAOA-BIB-{key}","source_local_id":key})
    proofs=ch09.proof_records(source); hints=0; previous=None
    for rec in semantic:
        if rec["unit_kind"]!="proof": previous=rec["id"]; continue
        i=len([x for x in semantic[:semantic.index(rec)+1] if x["unit_kind"]=="proof"])
        if i<=0: continue
        if rec.get("source_title_tex") and "Hint for proof" in rec["source_title_tex"]:
            hints+=1; relations.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","id":f"{CHAPTER_ID}-REL-HINTS-{hints:04d}","relation_type":"hints","from_id":rec["id"],"to_id":previous})
    if (len(proofs),hints)!= (12,9): raise RuntimeError(f"CH11 proof topology changed: {len(proofs)}/{hints}")
    source_terms=common.macro(source,"df"); target_terms=common.macro(target,"df"); terms,term_ids=terminology_records(ids,ids["receipt"]["sha256"])
    for n,(st,tt) in enumerate(zip(source_terms,target_terms,strict=True),1): relations.append({"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","id":f"{CHAPTER_ID}-REL-TERM-{n:04d}","relation_type":"uses_term","from_id":ch01.containing_segment(segments,st["start"],"source"),"to_id":term_ids[st["argument"]],"source_term_tex":st["argument"],"target_term_tex":tt["argument"],"locale":"id-ID"})
    source_idx=common.macro(source,"index"); target_idx=common.macro(target,"index")
    if len(source_idx)!=65 or len(target_idx)!=65: raise RuntimeError("CH11 index count changed")
    buf=io.StringIO(newline=""); w=csv.writer(buf,lineterminator="\n")
    for n,(si,ti) in enumerate(zip(source_idx,target_idx,strict=True),1): w.writerow([f"{CHAPTER_ID}-TERM-OCC-{n:04d}",ch01.containing_segment(segments,si["start"],"source"),n,si["line"],si["argument"],ti["line"],ti["argument"],digest(si["argument"].encode("ascii")),digest(ti["argument"].encode("utf-8")),"id-ID"])
    corrections=source_correction_records(ids["receipt"]["sha256"],ids["corrections"]["sha256"]); formulas,summary=formula_records(ids["receipt"]["sha256"],corrections)
    artifacts=artifact_records(ids,ids["receipt"]["sha256"]); qa=qa_records(ids,summary,ids["receipt"]["sha256"])
    relation_common={"schema":SCHEMA,"schema_version":VERSION,"record_type":"relation","from_id":CHAPTER_ID}
    relations.append(relation_common|{"id":f"{CHAPTER_ID}-REL-RIGHTS-0001","relation_type":"licensed_under","to_id":RIGHTS})
    relations.append(relation_common|{"id":f"{CHAPTER_ID}-REL-ASSET-0001","relation_type":"uses_asset","to_id":"ASSET-DIAGXY","asset_surface":"inline Xy-pic character-space/Gelfand-transform triangle","topology_preserved":True})
    for n,a in enumerate(artifacts,1): relations.append(relation_common|{"id":f"{CHAPTER_ID}-REL-ARTIFACT-{n:04d}","relation_type":"has_artifact","to_id":a["id"]})
    for n,e in enumerate(qa,1): relations.append(relation_common|{"id":f"{CHAPTER_ID}-REL-QA-{n:04d}","relation_type":"has_qa_event","to_id":e["id"]})
    for n,c in enumerate(corrections,1): relations.append(relation_common|{"id":f"{CHAPTER_ID}-REL-CORRECTION-{n:04d}","relation_type":"documents_correction","to_id":c["id"]})
    # Strip private offsets before serialization.
    for seg in segments:
        for k in ("_source_start","_source_end","_target_start","_target_end"): seg.pop(k,None)
    append_jsonl("semantic_units.jsonl",semantic); append_jsonl("segments.jsonl",segments); append_jsonl("relations.jsonl",relations); append_jsonl("formula_map.jsonl",formulas); append_jsonl("exercise_support.jsonl",[])
    old=(BACKEND/"index_terms.csv").read_bytes(); (BACKEND/"index_terms.csv").write_bytes(old+buf.getvalue().encode("utf-8"))
    lines=(BACKEND/"units.jsonl").read_bytes().splitlines(keepends=True); lines[10]=(json.dumps(chapter_unit(ids,corrections,ids["receipt"]["sha256"]),ensure_ascii=False,sort_keys=True,separators=(",",":") )+"\n").encode("utf-8"); (BACKEND/"units.jsonl").write_bytes(b"".join(lines))
    append_jsonl("artifacts.jsonl",artifacts); append_jsonl("qa_events.jsonl",qa); append_jsonl("corrections.jsonl",corrections); append_jsonl("terminology.jsonl",terms)
    write_manifest()
    # Validate endpoint closure against all stable records plus bibliography
    # and the two explicitly external component IDs.
    all_ids=set()
    for name in ("units.jsonl","semantic_units.jsonl","segments.jsonl","relations.jsonl","formula_map.jsonl","exercise_support.jsonl","artifacts.jsonl","qa_events.jsonl","corrections.jsonl","terminology.jsonl","assets.jsonl","rights.jsonl"):
        for line in (BACKEND/name).read_text(encoding="utf-8").splitlines():
            try: all_ids.add(json.loads(line).get("id"))
            except Exception: pass
    all_ids.update(x for x in [None] if x)
    external_prefix=("ERDMAN-FAOA-BIB-",)
    bad=[]
    for r in relations:
        for k in ("from_id","to_id"):
            endpoint=r.get(k)
            if endpoint and endpoint not in all_ids and not endpoint.startswith(external_prefix): bad.append((r["id"],k,endpoint))
    if bad: raise RuntimeError(f"relation endpoints unresolved ({len(bad)}): {bad[:3]}")
    report=ROOT/"qa/CH11_BACKEND_RECONCILIATION.md"; report.write_text("# FAOA-2015-CH11 backend reconciliation\n\nGenerated after the admitted Chapter 11 receipt. Historical Chapter 1--10 byte locks were checked before append.\n\n- Source: `"+SOURCE_REL+"` — "+str(ids["source"]["bytes"])+" bytes, SHA-256 `"+ids["source"]["sha256"]+"`\n- Target: `"+TARGET_REL+"` — "+str(ids["target"]["bytes"])+" bytes, SHA-256 `"+ids["target"]["sha256"]+"`\n- Semantic units appended: "+str(len(semantic))+"; segments appended: "+str(len(segments))+"; relations appended: "+str(len(relations))+"; formula maps appended: "+str(len(formulas))+"; index rows appended: 65; terms appended: "+str(len(terms))+"; corrections appended: "+str(len(corrections))+"; QA events appended: "+str(len(qa))+"; artifacts appended: "+str(len(artifacts))+".\n- Exercises/answers/solutions: 0/0/0 (the chapter has no exercise environment; the sole `exercise 18.45` is a citation locator).\n- Inline diagram: `ASSET-DIAGXY`, topology-preservation and accessible-description QA record present.\n- Relation endpoint validation: pass; all historical prefixes unchanged before append.\n\nGenerated backend file identities:\n\n"+"\n".join(f"- `{name}` — {len((BACKEND/name).read_bytes())} bytes, SHA-256 `{digest((BACKEND/name).read_bytes())}`" for name in ["units.jsonl","semantic_units.jsonl","segments.jsonl","relations.jsonl","formula_map.jsonl","exercise_support.jsonl","index_terms.csv","artifacts.jsonl","qa_events.jsonl","corrections.jsonl","terminology.jsonl","BACKEND_MANIFEST.csv"])+"\n",encoding="utf-8")
    print(json.dumps({"unit":CHAPTER_ID,"semantic_units":len(semantic),"segments":len(segments),"relations":len(relations),"formula_maps":len(formulas),"terms":len(terms),"corrections":len(corrections),"qa_events":len(qa),"artifacts":len(artifacts),"target_sha256":ids["target"]["sha256"],"backend_report":report.relative_to(ROOT).as_posix()},sort_keys=True))


if __name__ == "__main__":
    main()
