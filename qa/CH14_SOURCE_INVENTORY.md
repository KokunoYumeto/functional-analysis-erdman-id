# Chapter 14 source inventory

## Scope and source identity

- Unit: `FAOA-2015-CH14`.
- Source: `source/upstream/multiplier_algebras.tex`.
- Source bytes: **30,579**.
- SHA-256: `d9bf8cf31a6e18a779863dcb397863430fe2daac9031a86354ce2274b42def7c`.
- Encoding surface: 7-bit ASCII; no BOM; no NUL bytes.
- Line endings: **687 CRLF**, 0 lone LF, 0 lone CR.
- Logical record count: **687**. The source ends in CRLF.
- Terminal command: `\endinput` at line 687.

The authority file was read only. This inventory does not normalize or alter
its bytes.

## Ordered document structure

| Line | Level | Title | Span |
|---:|---|---|---:|
| 1 | chapter | `MULTIPLIER ALGEBRAS` | 1–687 |
| 3 | section | `Hilbert Modules` | 3–364 |
| 365 | section | `Essential Ideals` | 365–528 |
| 529 | section | `Compactifications and Unitizations` | 529–687 |

There are no subsections or external includes.

## Environment census

There are **70** `\begin{...}` occurrences and 70 matching
`\end{...}` occurrences. Of these, 66 are reader-semantic environments and
four are structural math/list environments.

| Environment | Count |
|---|---:|
| `prop` | 24 |
| `defn` | 19 |
| `exam` | 9 |
| `notn` | 6 |
| `proof` | 3 |
| `conv` | 2 |
| `exer` | 2 |
| `cor` | 1 |
| `enumerate` | 3 |
| `array` | 1 |

## Semantic and cross-reference surface

- Labels: **20 occurrences, 20 unique, no duplicates**:
  `multiplier_algebras`, `0038014`, `0038017`, `0038021`, `0038027`,
  `0038031`, `0038038`, `0038041`, `0038111`, `0038244`, `0038331`,
  `0038334`, `0038337`, `0038341`, `0038465`, `0038468`, `0038474`,
  `0038614`, `0038621`, and `0038641`.
- References: **31 occurrences using 28 keys**. Eight occurrences resolve to
  six local labels; 23 occurrences use 22 cross-chapter labels and therefore
  require the cumulative reader wrapper.
- Citations: **4 occurrences, four unique keys**: `RaeburnW:1998`,
  `Frank:2010`, `Willard:1968`, and `Conway:1990`.
- Index hooks: **79**.
- Defined-term commands (`\df`): **36**.
- Exercises: **2**, at source lines 59–61 and 99–101.
- Proof environments: **3**. Two are explicitly titled `Hint for proof`
  (lines 152–156 and 297–303); the third is a citation-only proof at line
  310. There are no upstream exercise answers or solutions.

## Math surface

The reproducible top-level math-surface count is **650**:

- 635 inline `$...$` spans (1,270 unescaped dollar delimiters);
- 15 `\[...\]` display spans;
- no top-level equation, align, gather, or multline environments.

The single `array` is nested inside the display at lines 490–495 and is not a
separate top-level surface. Opening and closing display brackets are both 15.
Unescaped brace counts are balanced at 395/395.

## Assets, dependencies, rights, and build risks

- `\input`: 0; `\include`: 0; `\includegraphics`: 0. The chapter has no
  chapter-local asset.
- This is a fragment, not a standalone document. It depends on the cumulative
  wrapper for theorem environments, custom macros (including `\vc`, `\ofml`,
  `\sto`, `\to`, `\df`, and `\cstariso`), bibliography, index, and the 22
  cross-chapter reference keys.
- The two exercises have no upstream answer/solution surface. Any mastery
  support must remain separately provenanced and must not be represented as
  Erdman-authored content.
- The fragment contains no standalone license notice. Its derivative rights
  inherit the frozen corpus CC BY-SA 4.0 boundary; attribution, change notice,
  ShareAlike, non-endorsement, and the edition's exact model-provenance string
  remain required. There are no third-party chapter assets to relicense.
- A definite direction error at lines 229–234 and a variable-name error at
  lines 75–78 require explicit derivative corrections. Mechanical source
  anomalies include `C^*$=algebra` (line 231), `means,when` (line 103), the
  missing sentence stop at line 209, `has lead` (line 312), the sentence break
  after `algebra` (lines 413–414), and missing commas around `if it exists` at
  lines 641 and 645. Their mathematical adjudication is recorded in
  `qa/CH14_PRETRANSLATION_MATH_REVIEW.md`.
- The notation `\ofml K(W,V)` is direction-sensitive: its generators
  `\Theta_{v,w}` map `W` to `V`. Translation/backend extraction must not swap
  its arguments merely because the generic index display at line 281 reads
  `\ofml K(V,W)`.

## Safe non-overlapping translation partition

The following four ranges cover every record exactly once and split only at
blank, top-level boundaries; no environment, display, paragraph, or sentence
crosses a boundary.

| Part | Inclusive source records | Records | Boundary |
|---|---:|---:|---|
| A | 1–194 | 194 | chapter opening through the example that `A` is a Hilbert `A`-module |
| B | 195–364 | 170 | Hilbert-module morphisms through the end of `Hilbert Modules` |
| C | 365–528 | 164 | complete `Essential Ideals` section |
| D | 529–687 | 159 | complete `Compactifications and Unitizations` section, including `\endinput` |

Reassembly order is strictly A, B, C, D with no inserted or dropped newline at
the joins. Part A alone owns the chapter and first-section commands; Parts C
and D each own their section command.
