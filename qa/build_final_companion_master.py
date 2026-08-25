#!/usr/bin/env python3
"""Derive the final TeX master without changing the admitted source-text master."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "source" / "id-ID" / "functional-analysis-id-complete-source.tex"
OUTPUT = ROOT / "source" / "id-ID" / "functional-analysis-id-complete-with-companions.tex"
REPORT = ROOT / "qa" / "FINAL_COMPANION_MASTER_RESULT.json"
EXPECTED_SOLUTIONS = [
    "solutions-ch01.tex",
    "solutions-ch03.tex",
    "solutions-ch04.tex",
    "solutions-ch05.tex",
    "solutions-ch06.tex",
    "solutions-ch07.tex",
    "solutions-ch08.tex",
    "solutions-ch09.tex",
    "solutions-ch10.tex",
    "solutions-ch13.tex",
    "solutions-ch14.tex",
    "solutions-ch17.tex",
]

ENVIRONMENTS = r"""

% Separately authored companion-layer presentation environments.
% Repeated source statements remain exact in component files, while duplicate
% labels and index hooks are suppressed locally in the compiled companion copy.
\makeatletter
\newenvironment{o001solution}[3]{%
  \par\bigskip\hrule\medskip
  \phantomsection\hypertarget{#1}{}%
  \noindent{\footnotesize\textbf{ID solusi:} \path{#1}\\
  \textbf{Latihan sumber:} \path{#2}}\par\smallskip
}{\par\medskip\hrule\bigskip}
\newenvironment{o001statement}{%
  \begingroup\let\label\@gobble\let\label@in@display\@gobble\let\index\@gobble
  \begin{quote}\small\noindent\textbf{Pernyataan latihan sumber.}\par\smallskip
}{\end{quote}\endgroup}
\newenvironment{o001answer}{%
  \begin{quote}\noindent\textbf{Jawaban ringkas.}\par\smallskip
}{\end{quote}}
\newenvironment{o001proof}{%
  \begin{quote}\noindent\textbf{Solusi lengkap.}\par\smallskip
}{\hfill\ensuremath{\blacksquare}\end{quote}}
\newenvironment{o001readerwork}[5]{%
  \par\bigskip\hrule\medskip
  \phantomsection\hypertarget{#1}{}%
  \noindent{\footnotesize\textbf{ID dukungan:} \path{#1}\\
  \textbf{Hasil sumber:} \path{#2}; \textbf{petunjuk sumber:} \path{#3}}%
  \par\smallskip
}{\par\medskip\hrule\bigskip}
\newenvironment{o001result}{%
  \begingroup\let\label\@gobble\let\label@in@display\@gobble\let\index\@gobble
  \begin{quote}\small\noindent\textbf{Hasil sumber terpilih.}\par\smallskip
}{\end{quote}\endgroup}
\newenvironment{o001sourcehint}{%
  \begingroup\let\label\@gobble\let\label@in@display\@gobble\let\index\@gobble
  \begin{quote}\small\noindent\textbf{Petunjuk sumber.}\par\smallskip
}{\end{quote}\endgroup}
\makeatother
"""

COMPANIONS = r"""

\part{PENDAMPING PENGUASAAN DAN JEMBATAN SPEKTRAL}

\input{../../bridge/id-ID/compact-spectral-svd.tex}

\input{../../mastery/id-ID/reader-work-selected.tex}

\chapter{SOLUSI UNTUK SELURUH LATIHAN SUMBER}

Pernyataan latihan berikut tetap merupakan materi sumber John M. Erdman.
Solusi lengkap merupakan komponen asli terpisah berlisensi CC BY-SA 4.0,
ditulis dengan bantuan OpenAI Codex gpt-5.6-sol, Ultra atas arahan pengguna.
Solusi bukan tulisan Erdman dan tidak menyiratkan dukungan beliau atau
Portland State University.

\input{../../mastery/id-ID/solutions-ch01.tex}
\input{../../mastery/id-ID/solutions-ch03.tex}
\input{../../mastery/id-ID/solutions-ch04.tex}
\input{../../mastery/id-ID/solutions-ch05.tex}
\input{../../mastery/id-ID/solutions-ch06.tex}
\input{../../mastery/id-ID/solutions-ch07.tex}
\input{../../mastery/id-ID/solutions-ch08.tex}
\input{../../mastery/id-ID/solutions-ch09.tex}
\input{../../mastery/id-ID/solutions-ch10.tex}
\input{../../mastery/id-ID/solutions-ch13.tex}
\input{../../mastery/id-ID/solutions-ch14.tex}
\input{../../mastery/id-ID/solutions-ch17.tex}
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    missing = [
        name
        for name in EXPECTED_SOLUTIONS
        if not (ROOT / "mastery" / "id-ID" / name).is_file()
    ]
    if missing:
        raise RuntimeError(f"missing solution components: {missing}")
    for path in (
        ROOT / "mastery" / "id-ID" / "reader-work-selected.tex",
        ROOT / "bridge" / "id-ID" / "compact-spectral-svd.tex",
    ):
        if not path.is_file():
            raise RuntimeError(f"missing companion component: {path}")

    base_bytes = BASE.read_bytes()
    base = base_bytes.decode("utf-8")
    marker = "\\begin{document}"
    if base.count(marker) != 1 or base.count("\\backmatter") != 1:
        raise RuntimeError("base master insertion markers are not unique")
    rendered = base.replace(marker, ENVIRONMENTS + "\n" + marker, 1)
    rendered = rendered.replace("\n\\backmatter", "\n" + COMPANIONS + "\n\n\\backmatter", 1)
    if COMPANIONS not in rendered:
        raise RuntimeError("companion insertion failed")
    rendered = rendered.replace(
        r"\large Teks Sumber Lengkap Bahasa Indonesia",
        r"\large Edisi Lengkap Bahasa Indonesia dengan Pendamping Penguasaan",
        1,
    )
    rendered = rendered.replace(
        "Batas ini melengkapi terjemahan teks sumber. Lapisan HTML semantik, dukungan\n"
        "penguasaan dan solusi, serta jembatan spektral-kompak/SVD merupakan komponen\n"
        "tambahan berprovenans terpisah yang masih dalam produksi.",
        "Batas ini memuat terjemahan teks sumber lengkap, pendamping HTML semantik,\n"
        "solusi terpisah untuk seluruh 52 latihan, sepuluh pembuktian penguasaan\n"
        "terpilih, serta jembatan spektral-kompak/SVD. Semua komponen tambahan\n"
        "mempertahankan provenans dan hak terpisah dan bukan tulisan Erdman.",
        1,
    )
    output_bytes = rendered.encode("utf-8")
    OUTPUT.write_bytes(output_bytes)
    if OUTPUT.read_bytes() != output_bytes:
        raise RuntimeError("generated master byte replay differs")
    if sha256(base_bytes) != "7f06919a8ec9088a3bc812fab962a48b5f1b3b0d5d3bce80eb21055f65089041":
        raise RuntimeError("admitted base master identity differs")
    report = {
        "schema_version": "o008.final-companion-master.v1",
        "result": "pass",
        "base_path": str(BASE.relative_to(ROOT)).replace("\\", "/"),
        "base_bytes": len(base_bytes),
        "base_sha256": sha256(base_bytes),
        "output_path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "output_bytes": len(output_bytes),
        "output_sha256": sha256(output_bytes),
        "solution_component_count": len(EXPECTED_SOLUTIONS),
        "selected_reader_work_count": 10,
        "explicit_exercise_solution_count": 52,
        "bridge_component": "bridge/id-ID/compact-spectral-svd.tex",
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
