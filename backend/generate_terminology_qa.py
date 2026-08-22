#!/usr/bin/env python3
"""Generate the additive Indonesian terminology-QA provenance projection."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
OUTPUT = BACKEND / "terminology_qa.jsonl"
SCHEMA = "interlanguage-modular-math"
VERSION = "0.1.0"
EDITION = "ERDMAN-FAOA-2015-ID"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
QA_ID = "TERM-QA-O008-ID-20260822"

REPORT_PATH = (
    "qa/terminology_evidence/undip-jfma-2020-dunford/"
    "TERMINOLOGY_QA_REPORT.md"
)
REPORT_BYTES = 9_317
REPORT_SHA256 = "c7618249a3d9f273044a408e44438e2db710d5b5f46856ea5280bf247583858d"

TERMINOLOGY_BYTES = 98_578
TERMINOLOGY_SHA256 = "98d69653ba962b1f88f84e9de28e13b9fa1c8f3fcbfbdc319e89b182f68a2144"
CH10_SOURCE_PATH = "source/upstream/distributions.tex"
CH10_SOURCE_BYTES = 42_703
CH10_SOURCE_LINES = 894
CH10_SOURCE_SHA256 = "31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8"

EVIDENCE_LOCKS = (
    (
        "qa/terminology_evidence/undip-jfma-2020-dunford/jfma-v3n1-7874.pdf",
        1_007_587,
        "6bc61be69f974e1598ec168504aa7b1925cf55a75dfc15100139bfcd586b0ff8",
    ),
    (
        "qa/terminology_evidence/undip-jfma-2020-dunford/jfma-v3n1-7874.txt",
        24_923,
        "2a74c776f17891e80d2b5da88e2d00233a8990c969bac0e36451a703dd9f8c91",
    ),
    (
        "qa/terminology_evidence/undip-jfma-2020-dunford/"
        "jfma-v3n1-7874-contact-sheet.png",
        2_622_328,
        "94545c3ad7770d39b69132c4c0fae37a6487e4aa0b1c77ef58073fe061ed20a9",
    ),
    (
        "qa/terminology_evidence/undip-jfma-2020-dunford/"
        "undip-jfma-7874-article.html",
        49_084,
        "bb8bfeb1e799b479288c1857406d480ecb00b82118a74728985a0d7a9aaf78b9",
    ),
    (
        "qa/terminology_evidence/undip-jfma-2020-dunford/"
        "ugm-etd-89480-metadata.html",
        35_075,
        "3499fe641f9127357395c1d1bcd8467f848804208803db31ec0eb9f720c0c9e2",
    ),
    (
        "qa/terminology_evidence/undip-jfma-2020-dunford/"
        "itb-ma6131-2024.html",
        6_739,
        "5f9de3cc9dbcf3429ce45464aa08831d958466f5b5db6249fa3fe0f3eda94fb3",
    ),
    (
        "qa/terminology_evidence/undip-jfma-2020-dunford/"
        "itb-ma5022-2024-adjoin.html",
        7_943,
        "cce7931eba1388395a504d83275f2846b7c3ac9031066bc27258c7abbc62724e",
    ),
    (
        "qa/terminology_evidence/undip-jfma-2020-dunford/"
        "ugm-etd-36096-operator-pendamping.html",
        22_532,
        "677165f202f8d7f32eb13f3ebe5b18052a20765ae32354209034d1ed8c3cf3f4",
    ),
)

CURRENT_VARIANT_GROUPS = (
    {
        "id": "TERM-QA-O008-ID-VARIANT-001",
        "term_id": "TERM-NORMED-LINEAR-SPACE",
        "source_term": "normed linear space",
        "preferred": "ruang linear bernorma",
        "variants": ["ruang bernorma"],
        "scope": "recognition variant; retain source-sensitive preferred form",
        "evidence_basis": "UNDIP JFMA 3(1), 47-55 (2020)",
    },
    {
        "id": "TERM-QA-O008-ID-VARIANT-002",
        "term_id": "TERM-BOUNDED-LINEAR-MAP",
        "source_term": "bounded linear map",
        "preferred": "pemetaan linear terbatas",
        "variants": ["operator linear terbatas"],
        "scope": "operator objects only; never a global replacement for map",
        "evidence_basis": "UNDIP JFMA 3(1), 47-55 (2020)",
    },
    {
        "id": "TERM-QA-O008-ID-VARIANT-003",
        "term_id": "TERM-ADJOINT",
        "source_term": "adjoint",
        "preferred": "adjoin",
        "variants": ["adjoint", "operator pendamping"],
        "scope": "recognition and search variants; retain edition-wide preferred form",
        "evidence_basis": "UNDIP adjoint usage; ITB MA5022 preferred adjoin; UGM ETD 36096 operator pendamping",
    },
    {
        "id": "TERM-QA-O008-ID-VARIANT-004",
        "term_id": "TERM-WEAKLY-COMPACT",
        "source_term": "weakly compact",
        "preferred": "kompak secara lemah",
        "variants": ["kompak lemah"],
        "scope": "recognition variant; retain grammatically explicit preferred form",
        "evidence_basis": "UNDIP JFMA 3(1), 47-55 (2020)",
    },
    {
        "id": "TERM-QA-O008-ID-VARIANT-005",
        "term_id": "TERM-CONVERGE-WEAKLY",
        "source_term": "converge weakly",
        "preferred": "konvergen secara lemah",
        "variants": ["konvergen lemah"],
        "scope": "recognition variant; retain edition-wide preferred form",
        "evidence_basis": "UNDIP JFMA 3(1), 47-55 (2020)",
    },
)

FUTURE_DOMAIN_VARIANT = {
    "id": "TERM-QA-O008-ID-FUTURE-DOMAIN-001",
    "candidate_term_id": "TERM-WEAKLY-MEASURABLE",
    "source_term": "weakly measurable",
    "preferred": "terukur secara lemah",
    "variants": ["terukur lemah"],
    "scope": "non-instantiated future/domain recognition candidate",
    "evidence_basis": "UNDIP JFMA 3(1), 47-55 (2020)",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_file(relative_path: str, expected_bytes: int, expected_sha256: str) -> None:
    path = ROOT / relative_path
    if not path.is_file():
        raise ValueError(f"missing terminology-QA evidence: {relative_path}")
    data = path.read_bytes()
    if (len(data), sha(data)) != (expected_bytes, expected_sha256):
        raise ValueError(f"terminology-QA evidence changed: {relative_path}")


def verify_ch10_source_absence() -> None:
    path = ROOT / CH10_SOURCE_PATH
    data = path.read_bytes()
    text = data.decode("ascii")
    if (
        len(data) != CH10_SOURCE_BYTES
        or len(data.splitlines()) != CH10_SOURCE_LINES
        or sha(data) != CH10_SOURCE_SHA256
        or len(re.findall(r"weakly[ -]measurable", text, flags=re.IGNORECASE)) != 0
        or len(re.findall(r"measur", text, flags=re.IGNORECASE)) != 14
    ):
        raise ValueError("frozen Chapter 10 weakly-measurable presence check changed")


def term_records() -> dict[str, dict]:
    path = BACKEND / "terminology.jsonl"
    data = path.read_bytes()
    if (len(data), sha(data)) != (TERMINOLOGY_BYTES, TERMINOLOGY_SHA256):
        raise ValueError("frozen Chapter 1--9 terminology projection changed")
    records = [json.loads(line) for line in data.decode("utf-8").splitlines()]
    return {record["id"]: record for record in records}


def verify_preferred_terms(terms: dict[str, dict]) -> None:
    for spec in CURRENT_VARIANT_GROUPS:
        record = terms.get(spec["term_id"])
        if record is None:
            raise ValueError(f"missing preferred term {spec['term_id']}")
        expected = (spec["source_term"], spec["preferred"], [])
        actual = (record.get("source_term"), record.get("preferred"), record.get("variants"))
        if actual != expected:
            raise ValueError(f"preferred term or frozen variants changed: {spec['term_id']}")
    if "TERM-WEAKLY-MEASURABLE" in terms:
        raise ValueError("future/domain candidate was instantiated prematurely")


def provenance_record() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "terminology_qa_provenance",
        "id": QA_ID,
        "edition_id": EDITION,
        "locale": "id-ID",
        "qa_date": "2026-08-22",
        "qa_scope": "bounded Indonesian functional-analysis terminology comparison",
        "model": MODEL,
        "decision": "no_prose_change",
        "preferred_terms_preserved": True,
        "current_variant_groups": 5,
        "current_variant_spellings": 6,
        "future_domain_candidate_groups": 1,
        "arxiv_search": {
            "state": "bounded_no_suitable_indonesian_tex_source_found",
            "exact_queries": [
                "analisis fungsional",
                "ruang Banach",
                "ruang vektor topologis",
                "operator kompak",
            ],
            "official_search_url": (
                "https://arxiv.org/search/?query=%22analisis+fungsional%22&"
                "searchtype=all&abstracts=show&order=-announced_date_first&size=50"
            ),
            "limitation": "some repeat official arXiv/API requests returned HTTP 429",
            "claim_scope": "bounded search result, not a universal nonexistence claim",
        },
        "fallback_source": {
            "source_id": "UNDIP-JFMA-2020-3-1-7874",
            "title": (
                "Ruang Bernorma Lengkap atas Operator Linear Terbatas pada "
                "Ruang Fungsi Terintegral Dunford"
            ),
            "authors": [
                "Solikhin",
                "YD Sumanto",
                "Abdul Aziz",
                "Susilo Hariyanto",
                "R. Heri Soelistyo Utomo",
            ],
            "journal": "Journal of Fundamental Mathematics and Applications (JFMA)",
            "volume": "3",
            "issue": "1",
            "pages": "47-55",
            "year": 2020,
            "doi": "10.14710/jfma.v3i1.7874",
            "article_url": "https://ejournal2.undip.ac.id/index.php/jfma/article/view/7874",
            "pdf_url": "https://ejournal2.undip.ac.id/index.php/jfma/article/download/7874/4246",
            "publisher": "Department of Mathematics, Universitas Diponegoro",
            "license": "CC BY 4.0",
            "pdf_pages": 9,
            "pdf_bytes": 1_007_587,
            "pdf_sha256": "6bc61be69f974e1598ec168504aa7b1925cf55a75dfc15100139bfcd586b0ff8",
        },
        "supplemental_sources": [
            {
                "source_id": "UGM-ETD-89480",
                "title": "Representasi Linear Kontinu dari Grup Topologis ke dalam Ruang Vektor Topologis",
                "year": 2015,
                "url": "https://etd.repository.ugm.ac.id/penelitian/detail/89480",
                "frozen_path": (
                    "qa/terminology_evidence/undip-jfma-2020-dunford/"
                    "ugm-etd-89480-metadata.html"
                ),
                "bytes": 35_075,
                "sha256": "3499fe641f9127357395c1d1bcd8467f848804208803db31ec0eb9f720c0c9e2",
            },
            {
                "source_id": "ITB-MA6131-2024",
                "title": "MA6131 Analisis Fungsional",
                "year": 2024,
                "url": "https://six.itb.ac.id/pub/kur2024/matakuliah/50833",
                "frozen_path": (
                    "qa/terminology_evidence/undip-jfma-2020-dunford/"
                    "itb-ma6131-2024.html"
                ),
                "bytes": 6_739,
                "sha256": "5f9de3cc9dbcf3429ce45464aa08831d958466f5b5db6249fa3fe0f3eda94fb3",
            },
            {
                "source_id": "ITB-MA5022-2024",
                "title": "MA5022 Aljabar I",
                "year": 2024,
                "terminology_evidence": "Operator Normal dan Adjoin dengan Diri Sendiri",
                "url": "https://six.itb.ac.id/pub/kur2024/matakuliah/50585",
                "frozen_path": (
                    "qa/terminology_evidence/undip-jfma-2020-dunford/"
                    "itb-ma5022-2024-adjoin.html"
                ),
                "bytes": 7_943,
                "sha256": "cce7931eba1388395a504d83275f2846b7c3ac9031066bc27258c7abbc62724e",
            },
            {
                "source_id": "UGM-ETD-36096",
                "title": "Beberapa sifat operator normal pada ruang Hilbert",
                "year": 2007,
                "terminology_evidence": "operator pendamping",
                "url": "https://etd.repository.ugm.ac.id/penelitian/detail/36096",
                "frozen_path": (
                    "qa/terminology_evidence/undip-jfma-2020-dunford/"
                    "ugm-etd-36096-operator-pendamping.html"
                ),
                "bytes": 22_532,
                "sha256": "677165f202f8d7f32eb13f3ebe5b18052a20765ae32354209034d1ed8c3cf3f4",
            },
        ],
        "qa_report": {
            "path": REPORT_PATH,
            "bytes": REPORT_BYTES,
            "sha256": REPORT_SHA256,
        },
        "compared_inputs": [
            {
                "path": "source/id-ID/topvecspaces-id.tex",
                "bytes": 37_705,
                "sha256": "791868776a07f4c854f1c13d295da23a2559b88dcac48523fb0390e1e5330ee1",
            },
            {
                "path": CH10_SOURCE_PATH,
                "bytes": CH10_SOURCE_BYTES,
                "lines": CH10_SOURCE_LINES,
                "sha256": CH10_SOURCE_SHA256,
                "weakly_measurable_occurrences": 0,
                "generic_measur_stem_occurrences": 14,
            },
            {
                "path": "backend/terminology.jsonl",
                "bytes": TERMINOLOGY_BYTES,
                "sha256": TERMINOLOGY_SHA256,
            },
        ],
    }


def current_variant_record(spec: dict) -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "term_variant_evidence",
        "id": spec["id"],
        "qa_provenance_id": QA_ID,
        "edition_id": EDITION,
        "locale": "id-ID",
        "term_id": spec["term_id"],
        "source_term": spec["source_term"],
        "preferred": spec["preferred"],
        "variants": spec["variants"],
        "variant_state": "accepted_recognition_variant",
        "instantiation_state": "backend_evidence_only",
        "preferred_changed": False,
        "prose_change": "none",
        "scope": spec["scope"],
        "evidence_basis": spec["evidence_basis"],
        "qa_report_path": REPORT_PATH,
        "qa_report_sha256": REPORT_SHA256,
    }


def future_domain_variant_record() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": VERSION,
        "record_type": "future_domain_term_variant",
        "id": FUTURE_DOMAIN_VARIANT["id"],
        "qa_provenance_id": QA_ID,
        "edition_id": EDITION,
        "locale": "id-ID",
        "candidate_term_id": FUTURE_DOMAIN_VARIANT["candidate_term_id"],
        "source_term": FUTURE_DOMAIN_VARIANT["source_term"],
        "preferred": FUTURE_DOMAIN_VARIANT["preferred"],
        "variants": FUTURE_DOMAIN_VARIANT["variants"],
        "variant_state": "non_instantiated_future_domain_recognition_candidate",
        "instantiation_state": "not_present_in_frozen_ch10_source",
        "source_presence": False,
        "source_presence_check": {
            "path": CH10_SOURCE_PATH,
            "bytes": CH10_SOURCE_BYTES,
            "lines": CH10_SOURCE_LINES,
            "sha256": CH10_SOURCE_SHA256,
            "query": "weakly[ -]measurable",
            "occurrences": 0,
        },
        "instantiation_condition": (
            "only_if_later_or_original_source_introduces_weakly_measurable"
        ),
        "preferred_changed": False,
        "prose_change": "not_applicable_no_existing_occurrence",
        "scope": FUTURE_DOMAIN_VARIANT["scope"],
        "evidence_basis": FUTURE_DOMAIN_VARIANT["evidence_basis"],
        "qa_report_path": REPORT_PATH,
        "qa_report_sha256": REPORT_SHA256,
    }


def write_manifest() -> None:
    paths = sorted(
        [
            path
            for path in BACKEND.iterdir()
            if path.is_file()
            and path.name != "BACKEND_MANIFEST.csv"
            and not path.name.endswith(".pyc")
        ],
        key=lambda path: path.name.casefold(),
    )
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["relative_path", "bytes", "sha256"])
    for path in paths:
        data = path.read_bytes()
        writer.writerow([path.name, len(data), sha(data)])
    (BACKEND / "BACKEND_MANIFEST.csv").write_text(
        buffer.getvalue(), encoding="utf-8", newline=""
    )


def main() -> None:
    verify_file(REPORT_PATH, REPORT_BYTES, REPORT_SHA256)
    for relative_path, expected_bytes, expected_sha256 in EVIDENCE_LOCKS:
        verify_file(relative_path, expected_bytes, expected_sha256)
    verify_ch10_source_absence()
    terms = term_records()
    verify_preferred_terms(terms)
    records = [provenance_record()]
    records.extend(current_variant_record(spec) for spec in CURRENT_VARIANT_GROUPS)
    records.append(future_domain_variant_record())
    OUTPUT.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            for record in records
        ),
        encoding="utf-8",
        newline="",
    )
    write_manifest()
    print(
        json.dumps(
            {
                "current_variant_groups": len(CURRENT_VARIANT_GROUPS),
                "current_variant_spellings": sum(
                    len(spec["variants"]) for spec in CURRENT_VARIANT_GROUPS
                ),
                "decision": "no_prose_change",
                "model": MODEL,
                "future_domain_candidate_groups": 1,
                "preferred_terms_preserved": True,
                "records": len(records),
                "result": "pass",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
