#!/usr/bin/env python3
"""Locked structural, mathematical, rights, and residue audit for CH09."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qa"))
sys.path.insert(0, str(ROOT / "backend"))
import check_ch05_translation as common  # noqa: E402
import ch03_math  # noqa: E402


SOURCE = ROOT / "source" / "upstream" / "topvecspaces.tex"
TARGET = ROOT / "source" / "id-ID" / "topvecspaces-id.tex"
MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch09.tex"
CORRECTION_LEDGER = ROOT / "provenance" / "SOURCE_CORRECTIONS_CH09.json"
REPORT = ROOT / "qa" / "ch09-translation-report.json"

SOURCE_BYTES = 35_022
SOURCE_LF = 806
SOURCE_SHA256 = "62bc645c9d0972856913098d90d4baec7a8b0f470d4d380a880416f64cd5bce4"
TARGET_BYTES = 37_705
TARGET_LF = 804
TARGET_SHA256 = "791868776a07f4c854f1c13d295da23a2559b88dcac48523fb0390e1e5330ee1"
MASTER_BYTES = 9_780
MASTER_LF = 335
MASTER_SHA256 = "acba53fd01601ecd49516c01fb00e38af7bfcafbbbff0358a87dea864c591e3f"
CORRECTION_LEDGER_BYTES = 14_917
CORRECTION_LEDGER_LF = 278
CORRECTION_LEDGER_SHA256 = "861b96347a0ab045861042c782209d284f2811f0eaa21c85200745d11de882e9"

EXPECTED_CHAPTER_TITLE = "RUANG VEKTOR TOPOLOGIS"
EXPECTED_SECTION_TITLES = [
    "Himpunan Seimbang dan Himpunan Penyerap",
    "Filter",
    "Topologi Kompatibel",
    "Hasil Bagi",
    "Ruang Konveks Lokal dan Seminorma",
    "Ruang Fr\\'echet",
]
EXPECTED_ENVIRONMENT_BEGIN_COUNTS = {
    "conv": 1,
    "cor": 8,
    "defn": 19,
    "enumerate": 7,
    "exam": 21,
    "exer": 1,
    "notn": 3,
    "proof": 9,
    "prop": 57,
}
EXPECTED_LABELS = (
    "prop_fbase_induces_top",
    "prop_quotient_top_strong",
    "prop_clbase_from_snorms",
    "X_LCS1",
    "X_metric_from_seminorms",
    "prop_open_lim_cpt",
    "mi_notn",
    "X_smooth_fcns_Frechet",
    "Schwartz_space",
)
EXPECTED_REFERENCES = (
    ("ref", "prop_fbase_induces_top"),
    ("ref", "prop_clbase_from_snorms"),
    ("ref", "X_LCS1"),
    ("ref", "prop_clbase_from_snorms"),
    ("ref", "X_metric_from_seminorms"),
    ("ref", "X_metric_from_seminorms"),
    ("ref", "prop_open_lim_cpt"),
)
EXPECTED_CITATIONS = (
    "Conway:1990",
    "Rudin:1991",
    "Rudin:1991",
    "Treves:1967",
    "Treves:1967",
)
EXPECTED_TARGET_DEFINED_TERMS = (
    "seimbang",
    "melingkar",
    "selubung seimbang",
    "menyerap",
    "menyerap",
    "radial",
    "filter",
    "filter lingkungan",
    "basis filter",
    "basis filter bagi",
    "dibangkitkan oleh",
    "konvergen",
    "dibangkitkan oleh",
    "dibangkitkan oleh",
    "didasarkan pada",
    "kompatibel",
    "ruang vektor topologis",
    "translasi",
    "basis lokal",
    "topologi konvergensi seragam pada himpunan-himpunan kompak",
    "regular",
    "terbatas",
    "terbatas",
    "filter Cauchy",
    "lengkap",
    "topologi hasil bagi",
    "konveks lokal",
    "ruang konveks lokal",
    "semibola terbuka",
    "semibola tertutup",
    "fungsional Minkowski",
    "pemisah",
    "dapat dimetrikkan",
    "invarian terhadap translasi",
    "ruang Fr\\'echet",
    "mulus",
    "fungsi uji",
    "multi-indeks",
    "orde",
    "ruang Schwartz",
)
EXPECTED_PROOF_ROLES = (
    "hint",
    "hint",
    "hint",
    "citation",
    "citation",
    "citation",
    "citation",
    "hint",
    "hint",
)
EXPECTED_EXERCISE_PROOF_SEQUENCE = (
    "proof:hint",
    "proof:hint",
    "exercise",
    "proof:hint",
    "proof:citation",
    "proof:citation",
    "proof:citation",
    "proof:citation",
    "proof:hint",
    "proof:hint",
)
EXPECTED_PROOF_ROLE_CANONICAL = (
    "261-262:PROOF_HINT|285-286:PROOF_HINT|440-442:EXERCISE|"
    "519-520:PROOF_HINT|592-593:PROOF_CITATION_ONLY:Conway:1990|"
    "635-636:PROOF_CITATION_ONLY:Rudin:1991|"
    "645-646:PROOF_CITATION_ONLY:Rudin:1991|"
    "673-674:PROOF_CITATION_ONLY:Treves:1967|734-736:PROOF_HINT|"
    "757-758:PROOF_HINT_WITH_CITATION:Treves:1967"
)
EXPECTED_PROOF_ROLE_BYTES = 295
EXPECTED_PROOF_ROLE_SHA256 = "3b7911927320fca619207eaccdb578d16c620f5e0be76c9848ca436dbc2cb3f8"
EXPECTED_CORRECTION_RECORDS = (
    ("FAOA-2015-CH09-CORR-001", 88, 88, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-002", 147, 147, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-003", 172, 172, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-004", 181, 184, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-005", 219, 219, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-006", 230, 232, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-007", 375, 375, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-008", 436, 437, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-009", 584, 584, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-010", 617, 620, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-011", 630, 632, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-012", 638, 638, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-013", 668, 668, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-014", 721, 721, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-015", 738, 738, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-016", 742, 742, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-017", 763, 765, "MECHANICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-018", 277, 278, "MATHEMATICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-019", 311, 312, "MATHEMATICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-020", 352, 356, "MATHEMATICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-021", 559, 561, "MATHEMATICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-022", 564, 566, "MATHEMATICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-023", 578, 581, "MATHEMATICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-024", 588, 590, "MATHEMATICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-025", 640, 642, "MATHEMATICAL_SOURCE_REPAIR"),
    ("FAOA-2015-CH09-CORR-026", 749, 751, "MATHEMATICAL_SOURCE_REPAIR"),
)
EXPECTED_MASTER_INCLUDES = (
    "linalg-id",
    "categories-id",
    "normlinspaces-id",
    "Hilbert_spaces-id",
    "Hilbert_space_operators-id",
    "Banach_spaces-id",
    "compact_operators-id",
    "spectrum-id",
    "topvecspaces-id",
)
EXPECTED_SEQUENCE_SHA256 = {
    "environment_topology": "d304cedf42f719226c2abb936771eada42538b9e6d6a05893d9909fc2eebfd67",
    "begin_shapes": "4bbd929c846b87576ef94100a2e21e8742492771ba7f81c87b3a1e802703b5d3",
    "labels": "8120ef568e7e636c4bc105195870a4b278af610fbc9746296400063a76252408",
    "references": "d1de6a287dba8336601082223f9a34f1defef96bf57ac6c61445d76e5f6880f3",
    "citations": "b098ad04d6c03c204b2a7da3cf6e35a796f2c8ddae278807fd6a95b85d2f32df",
    "source_indexes": "63f7af892356be1e6fbc3a9cb688ea0b5e0295de5458a5beda4132804f0bd510",
    "target_indexes": "cfdd0505d6aa25fbca80ca6888b824f4c911f619ef93e8543858fa6cb3872847",
    "index_operator_shapes": "17c958a4b3f6c9eca54385c9ea419194527539a65cabcd6e88604dddc3bfbeb0",
    "source_defined_terms": "f1bb467f2a9514c5598842f6d29d43bc8919a77071098434b3b4416444cce5bd",
    "target_defined_terms": "92a5c274d5df73489690778474cb72df845cf2c1254f8ca0ec8e58b075e6b323",
    "source_math_records": "409fce2e90512b5aefd17f546659e2ee43aea711496b068118b1c9bf9aaddc52",
    "target_math_records": "fab33466224e5da0815398545ae3b18c824d2fd0043d3fc7a0f1e33afaa9649c",
    "source_math_delimiters": "a3930b5336c1589b862cbc45d50e330b4e34a5a3eaa745cbe9329b97c305db07",
    "target_math_delimiters": "70c9f8e9afa1608b1266d3a760ef6e7c7488b35c73aea0ca65c84321ccb3cf98",
    "master_includes": "1bf76716936bb699e7466cc9b7d1eefbd2579075d67321134671cf4b8156d818",
}

# SequenceMatcher edit signatures over text-aware math keys. Each tuple is
# followed by its independently adjudicated correction class.
EXPECTED_MATH_EDITS = [
    (("replace", 139, 139, 139, 139,
      ("dollar-inline",),
      ("69a68e8c03928fa27f8b4dc0cfd4cb7e3e6f22b04147ca824ab9b7c7cc8c6d7b",),
      ("dollar-inline",),
      ("b5be4be6feb2ea2b4deb659f2f5ae5013827e740b6372d809039af77a227d8a3",)),
     "MECHANICAL_SOURCE_REPAIR"),
    (("replace", 186, 189, 186, 189,
      ("dollar-inline", "dollar-inline", "dollar-inline", "dollar-inline"),
      ("d6da38a8c2a5f916ec09a2c4963d0b127de1d580e2adf8315a67dd1ab337ba8a",
       "d6da38a8c2a5f916ec09a2c4963d0b127de1d580e2adf8315a67dd1ab337ba8a",
       "b37b747b1464466b16b228f30289e34ffda36d182a11a46dd22dfeb967a25f9f",
       "0eb6169ceb1bfa0ca369f9a14660be2f4e8a2d8e5a2d9aac2c8d4d87ce318d81"),
      ("dollar-inline", "dollar-inline", "dollar-inline", "dollar-inline"),
      ("0b3603ec8eba31106c573f01f3db67050a1ae2dc50c7912a830dfedbc243d579",
       "0b3603ec8eba31106c573f01f3db67050a1ae2dc50c7912a830dfedbc243d579",
       "4870269d4403344f46cc3fb912d9817b4ebdf48a5b2b90bcd8d4b8c60a1dd9e6",
       "dd55722ad10403d30c4de6022e28e9581713478c86b0df173729d4c5b6cbf690")),
     "MECHANICAL_SOURCE_REPAIR"),
    (("replace", 293, 293, 293, 293,
      ("dollar-inline",),
      ("6885a724018a3fee41b170646831e18a1edbf8907db9c0cff5c69cd9b3ba37de",),
      ("dollar-inline",),
      ("08d0d7c9a4f28a0f6b8a4b6e0ef16c83fe25ddf8e75c67ce08393540029a196e",)),
     "MATHEMATICAL_SOURCE_REPAIR"),
    (("replace", 439, 439, 439, 440,
      ("dollar-inline",),
      ("858979f0c33c5f45e30780b82e2fa00184311296fbb7ef6bf3f4a6007c9b9cb1",),
      ("dollar-inline", "dollar-inline"),
      ("42f6ec152799fc6e3b876ef24d1e070722a6faf171b6b4b7bf988e89731d6386",
       "500f66bd1674bb5da37498ca094209b2899fcd50ad889a5cb969ec3951dcb1b2")),
     "MATHEMATICAL_SOURCE_REPAIR"),
    (("replace", 458, 458, 459, 459,
      ("bracket-display",),
      ("f5a24ecbf8bf5bc355f5683180c88893ba9e838c5d9b42c67da36c3ef8a7a8c1",),
      ("bracket-display",),
      ("bf856c18e0de59addce51f3ce6e1e61a40fdbdea3ae24f986785193b4e64422b",)),
     "MATHEMATICAL_SOURCE_REPAIR"),
    (("replace", 469, 469, 470, 470,
      ("dollar-inline",),
      ("148de9c5a7a44d19e56cd9ae1a554bf67847afb0c58f6e12fa29ac7ddfca9940",),
      ("dollar-inline",),
      ("252f10c83610ebca1a059c0bae8255eba2f95be4d1d7bcfa89d7248a82d9f111",)),
     "MATHEMATICAL_SOURCE_REPAIR"),
    (("replace", 472, 472, 473, 473,
      ("dollar-inline",),
      ("148de9c5a7a44d19e56cd9ae1a554bf67847afb0c58f6e12fa29ac7ddfca9940",),
      ("dollar-inline",),
      ("252f10c83610ebca1a059c0bae8255eba2f95be4d1d7bcfa89d7248a82d9f111",)),
     "MATHEMATICAL_SOURCE_REPAIR"),
    (("replace", 476, 476, 477, 477,
      ("dollar-inline",),
      ("5c28c862257830e8f8c86fa87888b62aa241283f3632bf3f119cbce5bd31f20a",),
      ("dollar-inline",),
      ("4b68ab3847feda7d6c62c1fbcbeebfa35eab7351ed5e78f4ddadea5df64b8015",)),
     "MECHANICAL_SOURCE_REPAIR"),
    (("replace", 488, 488, 489, 489,
      ("dollar-inline",),
      ("de5a6f78116eca62d7fc5ce159d23ae6b889b365a1739ad2cf36f925a140d0cc",),
      ("dollar-inline",),
      ("4b68ab3847feda7d6c62c1fbcbeebfa35eab7351ed5e78f4ddadea5df64b8015",)),
     "MECHANICAL_SOURCE_REPAIR"),
    (("insert", 499, 498, 500, 501,
      (), (),
      ("dollar-inline", "dollar-inline"),
      ("381fe9d7a547de1891512eb62bfeec60dbfbc93380f7d8bfa76d9514a826efb5",
       "b5575ec9772b36edaf294ce02cf245c7901c90f58787f5ac3a4ed76e89ed279c")),
     "MATHEMATICAL_SOURCE_REPAIR"),
    (("replace", 583, 583, 586, 586,
      ("dollar-inline",),
      ("771b7e4ffe989355177c87a2e7affd08f7f9b8ddffb09ef01c5f2ab7faea1041",),
      ("dollar-inline",),
      ("44a58c3c1d63a65690e0364eb267a1d09e49955f060994f0b042d87ccd65741c",)),
     "MECHANICAL_SOURCE_REPAIR"),
    (("replace", 589, 589, 592, 592,
      ("dollar-inline",),
      ("ecd933270ba29506ebf966f6ffb143b9ca19ad20e0f4d15abc20130d88800b11",),
      ("dollar-inline",),
      ("385db61e36ff30ce3143fa5c4534cb7cc3f0638a44f905c1dc46a29099ab4247",)),
     "MECHANICAL_SOURCE_REPAIR"),
    (("replace", 592, 592, 595, 595,
      ("bracket-display",),
      ("be8c0bace0aae9b1b0d91258ca4f3ca000dfdf65f9c978482c5f9086ea1b9cfe",),
      ("bracket-display",),
      ("8b8b660e2e29a79e6d22944f9b5e56893ee31f2df2d81f78f675fa2e401af707",)),
     "MATHEMATICAL_SOURCE_REPAIR"),
]

PRIVATE_RESIDUE = (
    "c:\\users",
    "c:/users",
    "/users/",
    "codex://",
    "file://",
    "github tokens",
    "zenodo token",
    "figshare token",
    "obsidian notes",
    "\\appdata\\",
)
MOJIBAKE = ("Ã", "Â", "â€", "ï»¿", "�")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sequence_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def key_sha(item: dict) -> str:
    key = ch03_math.math_key(item["normalized"])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def math_records(math: list[dict]) -> list[tuple[str, str]]:
    return [(item["delimiter"], key_sha(item)) for item in math]


def math_edit_signature(source_math: list[dict], target_math: list[dict]) -> list[tuple]:
    source_keys = [ch03_math.math_key(item["normalized"]) for item in source_math]
    target_keys = [ch03_math.math_key(item["normalized"]) for item in target_math]
    output: list[tuple] = []
    matcher = SequenceMatcher(None, source_keys, target_keys, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        output.append(
            (
                tag,
                i1 + 1,
                i2,
                j1 + 1,
                j2,
                tuple(item["delimiter"] for item in source_math[i1:i2]),
                tuple(key_sha(item) for item in source_math[i1:i2]),
                tuple(item["delimiter"] for item in target_math[j1:j2]),
                tuple(key_sha(item) for item in target_math[j1:j2]),
            )
        )
    return output


def begin_shape_sequence(text: str) -> list[tuple[str, str]]:
    active = common.shared.active_same_length(text)
    output: list[tuple[str, str]] = []
    for match in re.finditer(r"\\begin\{([^{}]+)\}", active):
        cursor = match.end()
        shape = "plain"
        if cursor < len(active) and active[cursor] == "[":
            shape = "optional"
        elif cursor < len(active) and active[cursor] == "{":
            shape = "mandatory"
        output.append((match.group(1), shape))
    return output


def environment_stack_errors(sequence: list[tuple[str, str]]) -> list[str]:
    stack: list[str] = []
    errors: list[str] = []
    for action, name in sequence:
        if action == "begin":
            stack.append(name)
        elif not stack or stack[-1] != name:
            errors.append(f"environment close mismatch: {name}")
        else:
            stack.pop()
    if stack:
        errors.append(f"unclosed environments: {stack!r}")
    return errors


def proof_records(text: str) -> list[dict]:
    active = common.shared.active_same_length(text)
    pattern = re.compile(r"\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}", re.S)
    output: list[dict] = []
    for match in pattern.finditer(active):
        opening = active[match.start(): active.find("\n", match.start())]
        body = match.group(1)
        citations = tuple(re.findall(r"\\cite\{([^{}]+)\}", body))
        is_hint = "Hint for proof" in opening or "Petunjuk untuk bukti" in opening
        if is_hint:
            role = "hint"
        elif citations:
            role = "citation"
        else:
            role = "plain"
        if is_hint and citations:
            token = f"PROOF_HINT_WITH_CITATION:{','.join(citations)}"
        elif is_hint:
            token = "PROOF_HINT"
        elif citations:
            token = f"PROOF_CITATION_ONLY:{','.join(citations)}"
        else:
            token = "PROOF_PLAIN"
        output.append(
            {
                "start": match.start(),
                "end": match.end(),
                "role": role,
                "token": token,
            }
        )
    return output


def exercise_proof_sequence(text: str) -> list[str]:
    events = [(item["start"], f"proof:{item['role']}") for item in proof_records(text)]
    active = common.shared.active_same_length(text)
    events.extend((match.start(), "exercise") for match in re.finditer(r"\\begin\{exer\}", active))
    return [kind for _, kind in sorted(events)]


def proof_exercise_role_events(text: str) -> list[dict]:
    active = common.shared.active_same_length(text)
    events = [
        {"start": item["start"], "end": item["end"], "token": item["token"]}
        for item in proof_records(text)
    ]
    for match in re.finditer(r"\\begin\{exer\}.*?\\end\{exer\}", active, re.S):
        events.append({"start": match.start(), "end": match.end(), "token": "EXERCISE"})
    return sorted(events, key=lambda item: item["start"])


def proof_role_canonicals(source: str, target: str) -> tuple[str, str]:
    source_events = proof_exercise_role_events(source)
    target_events = proof_exercise_role_events(target)
    if len(source_events) != len(target_events):
        return "", ""
    source_records: list[str] = []
    target_records: list[str] = []
    for source_event, target_event in zip(source_events, target_events, strict=True):
        start_line = source.count("\n", 0, source_event["start"]) + 1
        end_line = source.count("\n", 0, source_event["end"]) + 1
        prefix = f"{start_line}-{end_line}:"
        source_records.append(prefix + source_event["token"])
        target_records.append(prefix + target_event["token"])
    return "|".join(source_records), "|".join(target_records)


def normalized_correction_snippet(records: list[str]) -> str:
    value = "\n".join(record.rstrip() for record in records).strip()
    value = unicodedata.normalize("NFC", value)
    return re.sub(r"\s+", " ", value).strip()


def validate_correction_ledger(
    ledger_bytes: bytes,
    source: str,
    target: str,
) -> tuple[dict, list[str], dict]:
    errors: list[str] = []
    try:
        ledger = json.loads(ledger_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, [f"source-correction ledger cannot be decoded: {exc}"], {}

    expected_source = {
        "path": "source/upstream/topvecspaces.tex",
        "bytes": SOURCE_BYTES,
        "logical_records": SOURCE_LF,
        "line_endings": "CRLF",
        "sha256": SOURCE_SHA256,
    }
    expected_target = {
        "path": "source/id-ID/topvecspaces-id.tex",
        "bytes": TARGET_BYTES,
        "logical_records": TARGET_LF,
        "line_endings": "LF",
        "sha256": TARGET_SHA256,
    }
    if ledger.get("schema_version") != "o008.source-corrections.v1":
        errors.append("source-correction ledger schema differs")
    if ledger.get("unit_id") != "FAOA-2015-CH09" or ledger.get("chapter") != 9:
        errors.append("source-correction ledger unit identity differs")
    if ledger.get("status") != "adjudicated_and_applied":
        errors.append("source-correction ledger status differs")
    if ledger.get("source") != expected_source:
        errors.append("source-correction ledger source identity differs")
    if ledger.get("target") != expected_target:
        errors.append("source-correction ledger target identity differs")
    normalization = ledger.get("normalization", {})
    if normalization.get("id") != "nonblank-ordinal-nfc-whitespace-v1":
        errors.append("source-correction normalization identity differs")

    source_lines = source.splitlines()
    target_lines = target.splitlines()
    source_nonblank = [
        (line_number, line)
        for line_number, line in enumerate(source_lines, start=1)
        if line.strip()
    ]
    target_nonblank = [line for line in target_lines if line.strip()]
    if len(source_nonblank) != 551 or len(target_nonblank) != 551:
        errors.append(
            f"source-correction nonblank mapping differs: "
            f"{len(source_nonblank)}/{len(target_nonblank)}"
        )

    records = ledger.get("records", [])
    if ledger.get("record_count") != 26 or len(records) != 26:
        errors.append(f"source-correction record count differs: {len(records)}")
    actual_metadata: list[tuple[str, int, int, str]] = []
    class_counts: Counter[str] = Counter()
    for record in records:
        source_range = record.get("source_lines", {})
        start = source_range.get("start")
        end = source_range.get("end")
        classification = record.get("classification")
        if not isinstance(start, int) or not isinstance(end, int):
            errors.append(f"invalid source range in {record.get('id')!r}")
            continue
        actual_metadata.append((record.get("id"), start, end, classification))
        class_counts[classification] += 1
        ordinals = [
            ordinal
            for ordinal, (line_number, _) in enumerate(source_nonblank)
            if start <= line_number <= end
        ]
        if not ordinals or any(ordinal >= len(target_nonblank) for ordinal in ordinals):
            errors.append(f"unmappable source range in {record.get('id')!r}")
            continue
        source_snippet = normalized_correction_snippet(
            [source_nonblank[ordinal][1] for ordinal in ordinals]
        )
        target_snippet = normalized_correction_snippet(
            [target_nonblank[ordinal] for ordinal in ordinals]
        )
        if digest(source_snippet.encode("utf-8")) != record.get(
            "source_normalized_snippet_sha256"
        ):
            errors.append(f"source snippet digest differs: {record.get('id')}")
        if digest(target_snippet.encode("utf-8")) != record.get(
            "target_normalized_snippet_sha256"
        ):
            errors.append(f"target snippet digest differs: {record.get('id')}")
        required = record.get("required_target_anchor", "")
        forbidden = record.get("forbidden_source_anchor", "")
        if not required or required not in target_snippet:
            errors.append(f"required target anchor absent: {record.get('id')}")
        if not forbidden or forbidden not in source_snippet:
            errors.append(f"forbidden-source anchor absent from source: {record.get('id')}")
        if forbidden and forbidden in target_snippet:
            errors.append(f"forbidden source anchor survives in target: {record.get('id')}")

    if tuple(actual_metadata) != EXPECTED_CORRECTION_RECORDS:
        errors.append("source-correction record identity/range/class sequence differs")
    expected_class_counts = {
        "MECHANICAL_SOURCE_REPAIR": 17,
        "MATHEMATICAL_SOURCE_REPAIR": 9,
    }
    if dict(class_counts) != expected_class_counts:
        errors.append(f"source-correction class census differs: {dict(class_counts)!r}")
    if ledger.get("class_counts") != expected_class_counts:
        errors.append("source-correction ledger class-count declaration differs")

    source_canonical, target_canonical = proof_role_canonicals(source, target)
    proof_digest = ledger.get("proof_role_digest", {})
    if proof_digest.get("canonical") != EXPECTED_PROOF_ROLE_CANONICAL:
        errors.append("ledger proof-role canonical sequence differs")
    if proof_digest.get("utf8_bytes") != EXPECTED_PROOF_ROLE_BYTES:
        errors.append("ledger proof-role byte count differs")
    if proof_digest.get("sha256") != EXPECTED_PROOF_ROLE_SHA256:
        errors.append("ledger proof-role digest differs")
    for name, canonical in (("source", source_canonical), ("target", target_canonical)):
        if canonical != EXPECTED_PROOF_ROLE_CANONICAL:
            errors.append(f"{name} proof-role canonical sequence differs")
        if len(canonical.encode("utf-8")) != EXPECTED_PROOF_ROLE_BYTES:
            errors.append(f"{name} proof-role canonical byte count differs")
        if digest(canonical.encode("utf-8")) != EXPECTED_PROOF_ROLE_SHA256:
            errors.append(f"{name} proof-role canonical digest differs")

    summary = {
        "path": CORRECTION_LEDGER.relative_to(ROOT).as_posix(),
        "bytes": len(ledger_bytes),
        "lf": ledger_bytes.count(b"\n"),
        "sha256": digest(ledger_bytes),
        "record_count": len(records),
        "class_counts": dict(class_counts),
        "proof_role_sha256": digest(target_canonical.encode("utf-8")),
    }
    return ledger, errors, summary


def main() -> int:
    errors: list[str] = []
    source_bytes = SOURCE.read_bytes()
    target_bytes = TARGET.read_bytes()
    master_bytes = MASTER.read_bytes()
    ledger_bytes = CORRECTION_LEDGER.read_bytes()
    source = source_bytes.decode("ascii")
    target = target_bytes.decode("utf-8")
    master = master_bytes.decode("utf-8")

    identities = (
        ("source", source_bytes, SOURCE_BYTES, SOURCE_LF, SOURCE_SHA256),
        ("target", target_bytes, TARGET_BYTES, TARGET_LF, TARGET_SHA256),
        ("master", master_bytes, MASTER_BYTES, MASTER_LF, MASTER_SHA256),
        (
            "source-correction ledger",
            ledger_bytes,
            CORRECTION_LEDGER_BYTES,
            CORRECTION_LEDGER_LF,
            CORRECTION_LEDGER_SHA256,
        ),
    )
    for name, data, expected_bytes, expected_lf, expected_sha in identities:
        if len(data) != expected_bytes:
            errors.append(f"{name} byte count differs: {len(data)}")
        if data.count(b"\n") != expected_lf:
            errors.append(f"{name} LF count differs: {data.count(bytes([10]))}")
        if digest(data) != expected_sha:
            errors.append(f"{name} SHA-256 differs")
        if data.startswith(b"\xef\xbb\xbf") or b"\x00" in data:
            errors.append(f"{name} contains BOM or NUL")
    if b"\r" in target_bytes or b"\r" in master_bytes or b"\r" in ledger_bytes:
        errors.append("target/master/source-correction ledger contain CR line endings")

    _, correction_errors, correction_summary = validate_correction_ledger(
        ledger_bytes,
        source,
        target,
    )
    errors.extend(correction_errors)

    chapter, sections = common.chapter_and_sections(target)
    if chapter != EXPECTED_CHAPTER_TITLE or sections != EXPECTED_SECTION_TITLES:
        errors.append(f"chapter/section titles differ: {chapter!r}, {sections!r}")
    if common.command_arguments(target, "subsection"):
        errors.append("unexpected subsection or lower heading")

    source_env = common.env_sequence(source)
    target_env = common.env_sequence(target)
    if source_env != target_env:
        errors.append("ordered environment topology differs")
    errors.extend(environment_stack_errors(target_env))
    if len(target_env) != 252:
        errors.append(f"environment token count differs: {len(target_env)}")
    begin_counts = Counter(name for action, name in target_env if action == "begin")
    if dict(sorted(begin_counts.items())) != EXPECTED_ENVIRONMENT_BEGIN_COUNTS:
        errors.append(f"environment opening census differs: {dict(begin_counts)!r}")
    if sequence_sha256(target_env) != EXPECTED_SEQUENCE_SHA256["environment_topology"]:
        errors.append("environment topology digest differs")
    source_shapes = begin_shape_sequence(source)
    target_shapes = begin_shape_sequence(target)
    if source_shapes != target_shapes:
        errors.append("begin-control shapes differ")
    if sequence_sha256(target_shapes) != EXPECTED_SEQUENCE_SHA256["begin_shapes"]:
        errors.append("begin-control shape digest differs")

    source_labels = common.command_arguments(source, "label")
    target_labels = common.command_arguments(target, "label")
    if tuple(source_labels) != EXPECTED_LABELS or tuple(target_labels) != EXPECTED_LABELS:
        errors.append("ordered label sequence differs")
    source_refs = [(kind, value) for _, kind, value in common.reference_sequence(source)]
    target_refs = [(kind, value) for _, kind, value in common.reference_sequence(target)]
    if tuple(source_refs) != EXPECTED_REFERENCES or tuple(target_refs) != EXPECTED_REFERENCES:
        errors.append("ordered reference sequence differs")
    source_cites = common.command_arguments(source, "cite")
    target_cites = common.command_arguments(target, "cite")
    if tuple(source_cites) != EXPECTED_CITATIONS or tuple(target_cites) != EXPECTED_CITATIONS:
        errors.append("ordered citation sequence differs")
    for name, sequence in (
        ("labels", target_labels),
        ("references", target_refs),
        ("citations", target_cites),
    ):
        if sequence_sha256(sequence) != EXPECTED_SEQUENCE_SHA256[name]:
            errors.append(f"{name} digest differs")

    source_indexes = common.command_arguments(source, "index")
    target_indexes = common.command_arguments(target, "index")
    source_index_shapes = [common.index_signature(item) for item in source_indexes]
    target_index_shapes = [common.index_signature(item) for item in target_indexes]
    if len(source_indexes) != 91 or len(target_indexes) != 91:
        errors.append(f"index count differs: {len(source_indexes)}/{len(target_indexes)}")
    if source_index_shapes != target_index_shapes:
        errors.append("MakeIndex operator-shape sequence differs")
    for name, sequence in (
        ("source_indexes", source_indexes),
        ("target_indexes", target_indexes),
        ("index_operator_shapes", target_index_shapes),
    ):
        if sequence_sha256(sequence) != EXPECTED_SEQUENCE_SHA256[name]:
            errors.append(f"{name} digest differs")

    source_df = common.command_arguments(source, "df")
    target_df = common.command_arguments(target, "df")
    if len(source_df) != 40 or tuple(target_df) != EXPECTED_TARGET_DEFINED_TERMS:
        errors.append("defined-term sequence differs")
    if sequence_sha256(source_df) != EXPECTED_SEQUENCE_SHA256["source_defined_terms"]:
        errors.append("source defined-term digest differs")
    if sequence_sha256(target_df) != EXPECTED_SEQUENCE_SHA256["target_defined_terms"]:
        errors.append("target defined-term digest differs")
    if target.count(r"\item") != 20:
        errors.append(f"item count differs: {target.count(r'\item')}")

    source_proofs = proof_records(source)
    target_proofs = proof_records(target)
    source_roles = tuple(item["role"] for item in source_proofs)
    target_roles = tuple(item["role"] for item in target_proofs)
    if source_roles != EXPECTED_PROOF_ROLES or target_roles != EXPECTED_PROOF_ROLES:
        errors.append(f"proof roles differ: {source_roles!r}, {target_roles!r}")
    if tuple(exercise_proof_sequence(source)) != EXPECTED_EXERCISE_PROOF_SEQUENCE:
        errors.append("source exercise/proof sequence differs")
    if tuple(exercise_proof_sequence(target)) != EXPECTED_EXERCISE_PROOF_SEQUENCE:
        errors.append("target exercise/proof sequence differs")
    if target.count(r"\begin{exer}") != 1 or target.count(r"\ns") != 9:
        errors.append("exercise or proof-stub census differs")

    source_math = ch03_math.extract_math(source, "ascii")
    target_math = ch03_math.extract_math(target, "utf-8")
    if (len(source_math), len(target_math)) != (603, 606):
        errors.append(f"math count differs: {len(source_math)}/{len(target_math)}")
    math_edits = math_edit_signature(source_math, target_math)
    expected_math_signatures = [item[0] for item in EXPECTED_MATH_EDITS]
    if math_edits != expected_math_signatures:
        errors.append(f"unclassified math edit signature: {math_edits!r}")
    for name, sequence in (
        ("source_math_records", math_records(source_math)),
        ("target_math_records", math_records(target_math)),
        ("source_math_delimiters", [item["delimiter"] for item in source_math]),
        ("target_math_delimiters", [item["delimiter"] for item in target_math]),
    ):
        if sequence_sha256(sequence) != EXPECTED_SEQUENCE_SHA256[name]:
            errors.append(f"{name} digest differs")

    residue = common.visible_residue(target, target_math)
    if residue:
        errors.append(f"visible English residue: {residue!r}")
    for marker in MOJIBAKE:
        if marker in target:
            errors.append(f"mojibake marker present: {marker!r}")
    active_lower = common.shared.active_same_length(target).lower()
    for marker in PRIVATE_RESIDUE:
        if marker in active_lower:
            errors.append(f"private-path residue present: {marker}")
    if target.count(r"\endinput") != 1 or target.rstrip().splitlines()[-1] != r"\endinput":
        errors.append("endinput is not the sole final nonblank record")

    master_includes = common.command_arguments(master, "include")
    if tuple(master_includes) != EXPECTED_MASTER_INCLUDES:
        errors.append(f"master include sequence differs: {master_includes!r}")
    if sequence_sha256(master_includes) != EXPECTED_SEQUENCE_SHA256["master_includes"]:
        errors.append("master include digest differs")
    for fragment in (
        "Unit Pembaca Kumulatif Bab 1--9",
        "batas produksi Bab 1--9",
        "Bab 1 sampai Bab 9",
        "Creative Commons",
        "Attribution--ShareAlike 4.0 International",
        "tidak\ndisponsori atau didukung oleh John M. Erdman maupun Portland State University",
        "DIAGXY.TEX",
        "status komponennya tidak cukup jelas tidak digunakan",
    ):
        if fragment not in master:
            errors.append(f"master rights/scope fragment absent: {fragment!r}")
    for forbidden in (r"\input{TABLE.TEX}", "by-sa.eps", "by-sa.pdf", "Wiener_quote.tex"):
        if forbidden.lower() in master.lower():
            errors.append(f"excluded component is active in master: {forbidden}")

    report = {
        "schema_version": "o008.ch09-translation-report.v2",
        "unit_id": "FAOA-2015-CH09",
        "source": {"bytes": len(source_bytes), "lf": source_bytes.count(b"\n"), "sha256": digest(source_bytes)},
        "target": {"bytes": len(target_bytes), "lf": target_bytes.count(b"\n"), "sha256": digest(target_bytes)},
        "master": {"bytes": len(master_bytes), "lf": master_bytes.count(b"\n"), "sha256": digest(master_bytes)},
        "source_correction_ledger": correction_summary,
        "counts": {
            "environment_pairs": len(target_env) // 2,
            "labels": len(target_labels),
            "references": len(target_refs),
            "citations": len(target_cites),
            "indexes": len(target_indexes),
            "defined_terms": len(target_df),
            "items": target.count(r"\item"),
            "exercises": target.count(r"\begin{exer}"),
            "proof_stubs": len(target_proofs),
            "source_math_surfaces": len(source_math),
            "target_math_surfaces": len(target_math),
        },
        "math_edits": [
            {"signature": list(signature), "classification": expected[1]}
            for signature, expected in zip(math_edits, EXPECTED_MATH_EDITS, strict=True)
        ],
        "visible_english_residue": residue,
        "errors": errors,
        "result": "pass" if not errors else "fail",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
