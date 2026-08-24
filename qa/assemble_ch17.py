#!/usr/bin/env python3
"""Assemble the reviewed FAOA-2015-CH17 fragments and cumulative master."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "source" / "upstream" / "K0_functor.tex"
AUTHORITY_BYTES = 59_639
AUTHORITY_LF = 1_362
AUTHORITY_SHA256 = "e8ebcaa4e5dbc1cc9b907edb235465610f3bd61e0bfa1ce2f1b5b26e9abf8c6a"
PARTS = (
    (
        ROOT / "qa" / "ch17_translation_part_a.tex",
        29_398,
        567,
        "91197367b8b8248deb92456098ace93268d3459b75770249121fce40aee840af",
    ),
    (
        ROOT / "qa" / "ch17_translation_part_b.tex",
        32_270,
        790,
        "5ce962333756e11998d1d372b4228ef2604052ec92bf40dfef047c81a987986a",
    ),
)
SOURCE_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch16.tex"
SOURCE_MASTER_BYTES = 10_679
SOURCE_MASTER_LF = 345
SOURCE_MASTER_SHA256 = "6e528b0193d3179b58e44169430d043fa5399f7c860f09d832eb3ccd954a5388"
TARGET_CHAPTER = ROOT / "source" / "id-ID" / "K0_functor-id.tex"
TARGET_MASTER = ROOT / "source" / "id-ID" / "functional-analysis-id-through-ch17.tex"
EXPECTED_CHAPTER_BYTES = 61_673
EXPECTED_CHAPTER_SHA256 = "061ffd28907e2251fc8b01077888de3e11b3bce67fec1ba52b080c924a241059"
EXPECTED_MASTER_BYTES = 10_820
EXPECTED_MASTER_SHA256 = "51b3f4d790e3d09ac6ac4c160284510e4827140ecaa5a961a46c880ae5c8bb39"
EXPECTED_SECTIONS = (
    r"\section{Relasi Ekuivalensi pada Proyeksi}",
    r"\section{Semigrup Proyeksi}",
    r"\section{Konstruksi Grothendieck}",
    r"\section{Grup $\mathbf{\emph{K}_0}$ untuk Aljabar-$C^*$ Beridentitas}",
    r"\section{$\mathbf{\emph{K}_0}(A)$---Kasus Tak Beridentitas}",
    r"\section{Sifat Keeksakan dan Stabilitas Funktor $K_0$}",
    r"\section{Limit Induktif}",
    r"\section{Diagram Bratteli}",
)
EXPECTED_INCLUDES = (
    "linalg-id",
    "categories-id",
    "normlinspaces-id",
    "Hilbert_spaces-id",
    "Hilbert_space_operators-id",
    "Banach_spaces-id",
    "compact_operators-id",
    "spectrum-id",
    "topvecspaces-id",
    "distributions-id",
    "Gelfand_Naimark-id",
    "no_identity-id",
    "GNS_construction-id",
    "multiplier_algebras-id",
    "fredholm_theory-id",
    "extensions-id",
    "K0_functor-id",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"master replacement count for {old!r} is not one")
    return text.replace(old, new, 1)


def macro_args(name: bytes, data: bytes) -> list[bytes]:
    return re.findall(rb"\\" + name + rb"\{([^{}]+)\}", data)


def build_chapter() -> bytes:
    authority = AUTHORITY.read_bytes()
    if (len(authority), authority.count(b"\n"), digest(authority)) != (
        AUTHORITY_BYTES,
        AUTHORITY_LF,
        AUTHORITY_SHA256,
    ):
        raise SystemExit("Chapter 17 authority identity differs")
    if authority.startswith(b"\xef\xbb\xbf") or authority.count(b"\r\n") != AUTHORITY_LF:
        raise SystemExit("Chapter 17 authority encoding/record closure differs")

    payloads: list[bytes] = []
    for path, expected_bytes, expected_lf, expected_sha in PARTS:
        data = path.read_bytes()
        if (len(data), data.count(b"\n"), digest(data)) != (
            expected_bytes,
            expected_lf,
            expected_sha,
        ):
            raise SystemExit(f"fragment identity mismatch: {path}")
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
            raise SystemExit(f"fragment encoding/line-ending mismatch: {path}")
        data.decode("utf-8")
        payloads.append(data)

    # Part A owns source records 1--572, whose final five records are blank.
    # apply_patch preserves the substantive 567 records but normalizes that
    # terminal blank run. Restore its five LF records before the record-573
    # section that begins part B.
    chapter = payloads[0] + b"\n" * 5 + payloads[1]
    if (len(chapter), chapter.count(b"\n"), digest(chapter)) != (
        EXPECTED_CHAPTER_BYTES,
        AUTHORITY_LF,
        EXPECTED_CHAPTER_SHA256,
    ):
        raise SystemExit("assembled Chapter 17 identity differs")
    if not chapter.startswith(b"\\chapter{FUNKTOR $\\mathbf{\\emph{K}_0}$}\n"):
        raise SystemExit("assembled chapter title differs")
    text = chapter.decode("utf-8")
    sections = tuple(line for line in text.splitlines() if line.startswith(r"\section{"))
    if sections != EXPECTED_SECTIONS:
        raise SystemExit(f"assembled section sequence differs: {sections!r}")
    if chapter.count(b"\\endinput") != 1 or not chapter.rstrip().endswith(b"\\endinput"):
        raise SystemExit(r"assembled chapter must end at its single active \endinput")

    source_lf = authority.replace(b"\r\n", b"\n")
    for name in (b"label", b"ref", b"eqref", b"cite"):
        if macro_args(name, source_lf) != macro_args(name, chapter):
            raise SystemExit(f"Chapter 17 {name.decode()} sequence differs from authority")
    source_env = re.findall(rb"\\(?:begin|end)\{([^}]+)\}", source_lf)
    target_env = re.findall(rb"\\(?:begin|end)\{([^}]+)\}", chapter)
    if source_env != target_env:
        raise SystemExit("Chapter 17 environment sequence differs from authority")

    expected_counts = {
        b"\\begin{": 212,
        b"\\end{": 212,
        b"\\label{": 73,
        b"\\ref{": 43,
        b"\\eqref{": 4,
        b"\\cite{": 18,
        b"\\index{": 100,
        b"\\df{": 24,
        b"\\[": 71,
        b"\\]": 71,
        b"\\begin{exer}": 1,
        b"\\begin{proof}": 28,
    }
    for token, count in expected_counts.items():
        if chapter.count(token) != count:
            raise SystemExit(f"Chapter 17 count mismatch for {token!r}")

    expected_markers = {
        f"% SOURCE-CORRECTION: CH17-C{number:03d}" for number in range(1, 27)
    }
    markers = re.findall(r"% SOURCE-CORRECTION: CH17-C\d{3}", text)
    if len(markers) != 26 or set(markers) != expected_markers:
        raise SystemExit("Chapter 17 correction-marker closure differs")

    required = (
        "motivasi heuristik saja",
        r"c\colon [0,1] \sto \ofml U(A)",
        "asosiatif secara ketat dan komutatif hanya hingga ekuivalensi Murray--von Neumann",
        "semigrup aditif bilangan bulat tak negatif",
        "ruang Hilbert terpisahkan berdimensi tak hingga",
        "memiliki pembatasan berupa pemetaan $\\phi$",
        r"Q \circ \psi' = \id{\C}",
        r"\pi:=Q",
        r"\lambda:=\psi",
        "homomorfisme grup tunggal",
        r"p \in \fml P_\infty(\wt A)\}",
        r"\clo{\bigcup_{n=1}^\infty A_n}",
        r"Homomorfisme-$*\,$ tak nol",
        r"\phi\colon a \mapsto u\,\diag",
        "berentri bilangan bulat tak negatif",
        "aljabar CAR (CAR = Relasi Antikomutasi Kanonik)",
        r"$p \sim q \implies p \sim_u q$",
        r"$p \sim_u q \implies p \sim_h q$",
        r"\tau\colon \fml D(A) \sto \abs G",
    )
    for witness in required:
        if witness not in text:
            raise SystemExit(f"required Chapter 17 correction missing: {witness!r}")
    rejected = (
        r"\sto \T\colon t \mapsto \exp(ith)",
        "komutatif di bawah operasi~$\\oplus$",
        r"homomorfisme-$*\,$ tunggal",
        r"p,q \in \fml P_\infty(\wt A)",
        r"B = \bigcup_{n=1}^\infty A_n",
        "matriks $\\vc m$ dari bilangan bulat positif",
        r"CAR\textbf{}-algebra",
        r"kebalikan dari implikasi kedua, $p \sim_u q \implies p \sim q$",
        r"kebalikan dari implikasi pertama, $p \sim_h q \implies p \sim_u q$",
        r"\tau\colon \fml D(A) \sto K_0(A)",
    )
    for witness in rejected:
        if witness in text:
            raise SystemExit(f"rejected Chapter 17 source defect remains: {witness!r}")
    return chapter


def build_master() -> bytes:
    master_bytes = SOURCE_MASTER.read_bytes()
    if (len(master_bytes), master_bytes.count(b"\n"), digest(master_bytes)) != (
        SOURCE_MASTER_BYTES,
        SOURCE_MASTER_LF,
        SOURCE_MASTER_SHA256,
    ):
        raise SystemExit("Chapter 1-16 master identity mismatch")
    if b"\r" in master_bytes or master_bytes.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("Chapter 1-16 master encoding/line-ending mismatch")
    master = master_bytes.decode("utf-8")
    master = replace_once(
        master, "Unit Pembaca Kumulatif Bab 1--16", "Unit Pembaca Kumulatif Bab 1--17"
    )
    master = replace_once(master, "batas produksi Bab 1--16", "batas produksi Bab 1--17")
    master = replace_once(master, "Bab 1 sampai Bab 16", "Bab 1 sampai Bab 17")
    master = replace_once(
        master,
        "aljabar nuklir},",
        "aljabar nuklir, teori-K, funktor K nol, proyeksi, ekuivalensi "
        "Murray--von Neumann, grup Grothendieck, aljabar-AF, diagram Bratteli},",
    )
    master = replace_once(
        master,
        " \\include{extensions-id}\n",
        " \\include{extensions-id}\n \\include{K0_functor-id}\n",
    )
    payload = master.encode("utf-8")
    if (len(payload), payload.count(b"\n"), digest(payload)) != (
        EXPECTED_MASTER_BYTES,
        SOURCE_MASTER_LF + 1,
        EXPECTED_MASTER_SHA256,
    ):
        raise SystemExit("assembled Chapter 1-17 master identity differs")
    includes = tuple(re.findall(r"^ \\include\{([^}]+)\}$", master, re.MULTILINE))
    if includes != EXPECTED_INCLUDES:
        raise SystemExit(f"cumulative include sequence differs: {includes!r}")
    for witness in (
        "Creative Commons",
        "CC BY-SA 4.0",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "tidak\ndisponsori atau didukung",
    ):
        if witness not in master:
            raise SystemExit(f"rights/model/non-endorsement witness missing: {witness!r}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    chapter = build_chapter()
    master = build_master()
    outputs = ((TARGET_CHAPTER, chapter), (TARGET_MASTER, master))
    if args.check:
        for path, payload in outputs:
            if not path.is_file() or path.read_bytes() != payload:
                raise SystemExit(f"assembled output differs: {path}")
    else:
        for path, payload in outputs:
            path.write_bytes(payload)
    print(f"mode={'check' if args.check else 'write'}")
    print(
        f"chapter_bytes={len(chapter)} chapter_lf={chapter.count(bytes([10]))} "
        f"chapter_sha256={digest(chapter)}"
    )
    print(
        f"master_bytes={len(master)} master_lf={master.count(bytes([10]))} "
        f"master_sha256={digest(master)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
