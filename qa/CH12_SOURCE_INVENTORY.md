# Chapter 12 source inventory

## Scope and source identity

- Source: `source/upstream/no_identity.tex`
- Source bytes: **47,994**
- SHA-256: `8da3ffa45bcc07cbe1897a09f309db51e1c5c38080459ffb1f6947bf45a20b6c`
- Encoding surface: 7-bit ASCII; no BOM; no NUL bytes.
- Line endings: **1,158 CRLF**, 0 lone LF, 0 lone CR.
- Logical record count: **1,158**, counting line-ending-delimited records and a final unterminated record only when present. The source ends in CRLF, so there is no extra unterminated record.
- Terminal command: `\endinput` at line 1,158.

The source file was read only. This inventory does not translate it and does not normalize its bytes or line endings.

## Ordered document structure

| Line | Level | Title | Span |
|---:|---|---|---:|
| 1 | chapter | `SURVIVAL WITHOUT IDENTITY` | 1–1,158 |
| 3 | section | `Unitization of Banach Algebras` | 3–197 |
| 198 | section | `Exact Sequences and Extensions` | 198–391 |
| 392 | section | `Unitization of $C^*$-algebras` | 392–657 |
| 658 | section | `Quasi-inverses` | 658–766 |
| 767 | section | `Positive Elements in $C^*$-algebras` | 767–1,021 |
| 1,022 | section | `Approximate Identities` | 1,022–1,158 |

There are no `\subsection` or `\subsubsection` commands.

## Environment census

There are **154** `\begin{...}` occurrences and 154 matching `\end{...}` occurrences by environment-command count.

| Environment | Count |
|---|---:|
| `prop` | 71 |
| `defn` | 17 |
| `proof` | 12 |
| `cor` | 11 |
| `exam` | 10 |
| `enumerate` | 9 |
| `bmatrix` | 6 |
| `equation` | 5 |
| `thm` | 5 |
| `align*` | 2 |
| `lem` | 2 |
| `notn` | 2 |
| `array` | 1 |
| `conv` | 1 |

The exact source order and signatures (environment name, optional title, and immediately attached label) are in `CH12_CENSUS.json`.

## Semantic and cross-reference surface

- Labels: **65 occurrences, 65 unique, no duplicates**.
- References: **46 occurrences**: 41 `\ref` and 5 `\eqref`; 21 occurrences resolve to labels in this file and 25 do not.
- Citations: **17 occurrences**, using 8 unique keys.
- Index entries: **102**.
- Defined-term commands (`\df`): **42**.
- Exercises/problem environments or commands: **0**.
- Proof environments: **12**.
- Hint-style proofs: **8** (lines 107, 431, 677, 703, 863, 901, 994, and 1,052).
- Citation-only proofs: **2** (lines 1,081 and 1,103).
- Other proofs: **2** (lines 121 and 625).

All occurrence-level labels, references, citations, index entries, and defined terms are recorded with source lines in the JSON census. The line-836 `\df` argument intentionally spans lines 836–839 and contains two `\index` commands; the census preserves that argument exactly with CRLF escapes.

## Math surface

The reproducible math-surface count is **929** top-level math spans:

- 884 inline `$...$` spans (1,768 unescaped dollar delimiters),
- 38 `\[...\]` display spans,
- 5 `equation` environments,
- 2 `align*` environments.

Nested `array` (1) and `bmatrix` (6) environments are counted in the environment census but not again as top-level math spans. Opening and closing `\[`/`\]` counts are both 38.

## Assets, includes, and termination

- `\input`: 0
- `\include`: 0
- `\includegraphics`: 0
- External asset paths: none
- `\endinput`: 1, at line 1,158
- Inline `\xymatrix` diagrams: 13; these are source code, not external assets.

## Scope and build risks

- This is a chapter fragment, not a standalone document: it has no document class, preamble, or `document` environment and depends on parent-defined theorem environments and many custom macros.
- The 13 `\xymatrix` uses require the parent build's XY-pic support.
- Citations require a parent bibliography containing all 8 keys.
- Twenty-five reference occurrences are nonlocal or unresolved in this file. Likely local identifier mismatches include references to `001500202i` against local label `001500202i2`, and references to `00151231`/`00151232` against local labels `00151231c`/`00151232c`. The remaining targets may be valid cross-chapter references in the parent book.
- `\endinput` at line 1,158 deliberately terminates TeX input; appended material in the same input stream would not be read.
- Source-visible editorial anomalies worth preserving during translation include `approxiamte` (line 1,033), `The proof this result` (line 431), and `given a algebra` (line 536). They are source facts, not corrections made here.
- Delimiter checks are balanced for `\begin`/`\end` (154/154), display brackets (38/38), and unescaped braces (787/787). No standalone build was attempted because the scoped source is a fragment and the task is inventory-only.
