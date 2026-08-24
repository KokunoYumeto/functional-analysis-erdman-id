# Chapter 15 source inventory

## Scope and source identity

- Unit: `FAOA-2015-CH15`.
- Source: `source/upstream/fredholm_theory.tex`.
- Source bytes: **16,977**.
- SHA-256: `0ef2e5be3c716a099e8609a84528d77ad6387ec531c52f9890d4e34175c57d91`.
- Encoding surface: 7-bit ASCII; no BOM; no NUL bytes.
- Line endings: **444 CRLF**, 0 lone LF, 0 lone CR.
- Logical record count: **444**. The source ends in CRLF.
- Terminal command: `\endinput` at line 444.

The authority file was read only. This inventory does not normalize or alter
its bytes.

## Ordered document structure

| Line | Level | Title | Span |
|---:|---|---|---:|
| 1 | chapter | `FREDHOLM THEORY` | 1–444 |
| 3 | section | `The Fredholm Alternative` | 3–99 |
| 100 | section | `The Fredholm Alternative -- continued` | 100–206 |
| 207 | section | `Fredholm Operators` | 207–328 |
| 329 | section | `The Fredholm Alternative -- Concluded` | 329–444 |

There are no subsections and no chapter-level `\label` in this fragment.

## Environment census

There are **60** `\begin{...}` occurrences and 60 matching
`\end{...}` occurrences. Fifty are reader-semantic environments and ten are
structural mathematics/list environments.

| Environment | Count |
|---|---:|
| `prop` | 16 |
| `proof` | 13 |
| `exam` | 8 |
| `defn` | 6 |
| `lem` | 3 |
| `cor` | 2 |
| `thm` | 1 |
| `notn` | 1 |
| `align` | 6 |
| `enumerate` | 4 |

## Semantic, support, and cross-reference surfaces

- Labels: **33 occurrences, 33 unique, no duplicates**. Fifteen occur in the
  first section because the six manually tagged Fredholm systems carry their
  own equation labels.
- References: **27 occurrences using 24 keys**: 8 `\eqref` and 19 `\ref`.
  Twenty-four occurrences use 21 chapter-local labels. Three occurrences are
  cross-chapter references: `sec_onbases`, `001902`, and
  `cor2_Neumann_series`.
- Citations: **17 occurrences using seven keys**: `Arveson:2002`,
  `Blackadar:2006`, `Conway:1990`, `Douglas:1972`, `HigsonR:2000`,
  `Pedersen:1995`, and `Wegge-Olsen:1993`.
- Index hooks: **46**.
- Defined-term commands (`\df`): **11**.
- Exercises: **0**. There are eight `exam` environments, but no formal
  `exer`, answer, or solution environment.
- Proof environments: **13**. Eight are citation-only; two are explicit proof
  hints (lines 305–307 and 414–415); three give internal cross-reference or
  immediate-implication arguments. The chapter supplies no exercise solution
  layer.

## Math surface

The reproducible top-level math-surface count is **203**:

- 190 inline `$...$` spans (380 unescaped dollar delimiters);
- 7 `\[...\]` display spans;
- 6 top-level `align` environments.

There are no equation, gather, or multline environments. The six `align`
blocks contain manually assigned visible tags `(1)` through `(6)` and
`(1')` through `(6')`; all twelve associated labels are distinct. Opening and
closing display brackets are both seven. Unescaped brace counts are balanced
at 309/309.

## Assets, dependencies, and build risks

- `\input`: 0; `\include`: 0; `\includegraphics`: 0. There are no
  chapter-local assets.
- The fragment depends on the cumulative wrapper for theorem environments,
  `amsmath` (`align`, `\tag`, `\eqref`), bibliography, index, and custom
  macros including `\conj`, `\vc`, `\ran`, `\ker`, `\coker`, `\codim`,
  `\ofml`, `\cat`, `\ind`, `\inv`, `\sim_h`, and `\ns`.
- All three cross-chapter labels and all seven bibliography keys must resolve
  in the cumulative build. Manual equation tags and their labels must be
  preserved exactly rather than renumbered independently by a translator.
- The index hook at line 249 has an extra closing parenthesis in
  `Fredholm!index (\seeonly{index}))`; this is a mechanical source defect.
- Several long one-record propositions and proofs, particularly lines 164,
  177, 268, 341, 389, 410, 414, 417, 422, and 432, are reflow/build risks but
  are not mathematical defects.
- The fragment has no standalone rights notice or third-party asset. Its
  derivative treatment inherits the frozen corpus CC BY-SA 4.0 boundary and
  must retain attribution, change notices, ShareAlike, non-endorsement, and
  exact model provenance.
- The missing nonzero-scalar hypotheses, the false subspace statement, the
  finite-dimensional surjectivity overclaim, and the conflict between the
  Riesz–Schauder definition and Alternative VI are mathematical defects, not
  typography. They are independently adjudicated in
  `qa/CH15_PRETRANSLATION_MATH_REVIEW.md`.

## Safe non-overlapping translation partition

These four ranges cover all 444 records exactly once and coincide with whole
section boundaries. No environment, paragraph, display, sentence, label, or
manual equation-tag system crosses a join.

| Part | Inclusive source records | Records | Boundary |
|---|---:|---:|---|
| A | 1–99 | 99 | chapter opening and complete first Fredholm-alternative section |
| B | 100–206 | 107 | complete continued Fredholm-alternative section |
| C | 207–328 | 122 | complete `Fredholm Operators` section |
| D | 329–444 | 116 | complete concluding section, including `\endinput` |

Reassembly order is strictly A, B, C, D. Part A alone owns the chapter command;
each part owns exactly one section command.
