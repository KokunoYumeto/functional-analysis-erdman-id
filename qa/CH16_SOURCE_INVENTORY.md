# Chapter 16 source inventory

## Scope and frozen authority

- Unit: `FAOA-2015-CH16`.
- Source: `source/upstream/extensions.tex`.
- Source bytes: **42,614**.
- SHA-256:
  `e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318`.
- Encoding surface: 7-bit ASCII; no BOM; no NUL bytes.
- Line endings: **1,000 CRLF**, 0 lone LF, 0 lone CR.
- Logical record count: **1,000**. The source ends in CRLF.
- Terminal command: `\endinput` at record 1,000.

The authority file was read only. This inventory covers the complete chapter,
records 1--1,000, and does not normalize or alter its bytes.

## Ordered document structure and exact range identities

There are four active sections and no active subsections. The commented-out
prospective heading `Tensor Products of $C^*$-algebras` at record 676 is not
part of the reader surface and is not counted as a fifth section.

| Records | Bytes with authority CRLF | SHA-256 | Level/title |
|---:|---:|---|---|
| 1--1,000 | 42,614 | `e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318` | chapter, `EXTENSIONS` |
| 1--108 | 3,747 | `3e2be077d3053bdfd1f15965ce10feafc22ffe6a433c6a4fa030c172567125a0` | chapter opening and `Essentially Normal Operators` (section begins at 3) |
| 109--404 | 12,648 | `18c5bd54661e5e04fc461f4ce786bf48010c8f6b58f0d695b0f62e8b221bb698` | `Toeplitz Operators` |
| 405--697 | 12,771 | `875a164e6e761f0433e5464e5c9fbe0607320b8e4e7a6a27e8b222d890a5a228` | `Addition of Extensions` |
| 698--1,000 | 13,448 | `70be3f5261713c60e756cfc8e0ab3e44565bcf1c6dc3cdbb52875993726cf013` | `Completely Positive Maps`, including `\endinput` |

The four contiguous range byte counts sum to 42,614 and cover every authority
record exactly once.

## Environment census

There are **142** active `\begin{...}` occurrences and 142 matching
`\end{...}` occurrences. Their nesting stack is valid. Of these, **124** are
reader-semantic environments and 18 are structural math/list/layout
environments.

| Environment | Count | Class |
|---|---:|---|
| `prop` | 38 | semantic |
| `proof` | 31 | semantic |
| `defn` | 21 | semantic |
| `exam` | 15 | semantic |
| `thm` | 8 | semantic |
| `cor` | 6 | semantic |
| `notn` | 3 | semantic |
| `conv` | 1 | semantic |
| `rem` | 1 | semantic |
| `bmatrix` | 12 | structural math |
| `equation` | 4 | structural math |
| `center` | 1 | layout |
| `enumerate` | 1 | list |

Section-local counts provide an independent sum check:

| Active span | Environments | Labels | References | Citations | Index hooks | `\df` | Active math surfaces |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3--108 | 12 | 3 | 3 | 5 | 22 | 7 | 50 |
| 109--404 | 44 | 7 | 11 | 37 | 33 | 6 | 168 |
| 405--697 | 33 | 10 | 8 | 4 | 22 | 10 | 237 |
| 698--1,000 | 53 | 16 | 6 | 13 | 30 | 6 | 247 |
| **Total** | **142** | **36** | **28** | **59** | **107** | **29** | **702** |

## Labels, references, citations, and defined terms

- Labels: **36 occurrences, 36 unique, no duplicates**.
  - Section 1: `005121`, `005124`, `005134`.
  - Section 2: `005216`, `005217`, `005251`, `005253`, `0052531`,
    `005271`, `005274`.
  - Section 3: `005414`, `005431i`, `005431ii`, `005436`, `005464i`,
    `005466`, `0054702`, `0054715`, `0054715i`, `0054811`.
  - Section 4: `005824`, `00582811`, `0058283`, `00582921`, `005831`,
    `0058335`, `0058338`, `0058339`, `0058411`, `0058513`, `0058514`,
    `0058515`, `0058517`, `0058519`, `0058541`, `0058543`.
- References: **28 occurrences using 24 keys**: 27 `\ref` and one
  `\eqref`. Sixteen occurrences use 12 chapter-local keys. The 12
  cross-chapter keys are `000161`, `0001612`, `000533a`, `001306`,
  `00131104`, `00144`, `0015151`, `0018201`, `002802`, `002973`,
  `C063526`, and `C063527`.
- Citations: **59 occurrences using 15 keys**: `Arveson:2002`,
  `Blackadar:2006`, `Conway:2000`, `Davidson:1996`, `Douglas:1972`,
  `Douglas:1980`, `Fillmore:1996`, `Halmos:1982`, `HigsonR:2000`,
  `Massey:1967`, `Murphy:1990`, `Paulsen:2002`, `Wallace:1970`,
  `Wegge-Olsen:1993`, and `Willard:1968`.
- Index hooks: **107**.
- Defined-term commands (`\df`): **29**. In source order they define or
  mark: essential spectrum; essential unitary equivalence; compalence;
  unitary maps and unitary equivalence; essential normality and essential
  self-adjointness; Toeplitz operator, symbol, matrix, algebra, and extension;
  winding number; extensions and their equivalence; conjugation; the
  extension determined by an essentially normal operator; pullbacks; unitary
  equivalence of Busby maps; abstract Toeplitz operator/symbol/extension;
  semisplit; positive; standard matrix units; n-positive; completely
  positive; completely bounded; and nuclear.

## Exercises, proofs, and learner support

- Formal `exer` environments: **0**.
- Hint environments or explicit proof hints: **0**.
- Answer/solution environments: **0**.
- Examples: **15**.
- Proof environments: **31**. Twenty-eight are source-pointer proof blocks
  whose mathematical content is a citation or citation-led note. Three carry
  local expository or constructive content: the definition of the Toeplitz
  quotient map (records 272--276), the winding-number/fundamental-group route
  (340--357), and the pullback sketch (547--551).

The absence of formal exercises and solutions is a property of the source,
not permission to manufacture source-attributed learner material.

## Math surface and diagrams

The active, comment-stripped top-level math-surface count is **702**:

- 672 inline `$...$` spans (1,344 unescaped active dollar delimiters);
- 26 `\[...\]` display spans;
- 4 `equation` environments.

The raw lexical count is 703 because the inactive commented heading at record
676 contains one `$C^*$` span. That commented span is excluded from the active
reader count. Opening/closing active display brackets are 26/26 and active
unescaped braces are balanced at 702/702. There are no `align`, `gather`, or
`multline` environments.

The chapter contains one manual visible tag `(1)` at record 287; four labelled
`equation` environments; three `\xymatrix` diagrams; two `\Square` diagrams;
one `\pullback` diagram; and two `\dtriangle` diagrams. All map directions,
objects, labels, and tag identities are preservation-critical.

## Assets, dependencies, and build risks

- `\input`: 0; `\include`: 0; `\includegraphics`: 0. There are no
  chapter-local assets.
- The chapter depends on the cumulative wrapper for theorem environments,
  bibliography, indexing, `amsmath` matrices/equations/tags, and the frozen
  XY/DIAGXY diagram commands. `DIAGXY.TEX` must remain byte-identical under its
  component notice.
- Custom macros include, among others, `\ofml`, `\fml`, `\vc`, `\T`,
  `\M`, `\ext`, `\ad`, `\sbsb`, `\wt`, `\ind`, `\ran`, `\norm`,
  `\bignorm`, `\id`, and categorical/diagram commands. They are semantic,
  not decorative text.
- The large block matrix at records 742--764, the boxed convention at
  407--411, and the diagrams at 434--449, 539--544, 599--604, 918--923, and
  978--984 are the main reflow/build-risk surfaces.
- The commented prospective tensor-product heading at 676 must remain
  inactive. It is not an omitted active reader section.

## Actionable source-correction boundary

The complete mathematical review in `qa/CH16_PRETRANSLATION_MATH_REVIEW.md`
records fifteen candidate ledger groups. The high-impact items are:

1. records 42--58 use the ill-typed conjugation `UTU^*` although
   `U:H\to K`, `S\in B(H)`, and `T\in B(K)`; the expressions must be
   `U^*TU`;
2. proposition `005134` needs the intended equal-dimension scope, naturally
   separable infinite-dimensional Hilbert spaces;
3. the index hook at 407 carries the stale locator “after section 9.2”;
4. the Voiculescu theorem at 886--891 omits that `\phi` is a unital
   completely positive linear map;
5. proposition `0058411` at 914--924 must ask for a unital completely
   positive lifting, not a star-homomorphic lifting, and its `\tau` belongs to
   the already-defined unital class;
6. the remaining candidates repair the Toeplitz-section map identifier,
   fundamental-group notation, a missing variable, Calkin/codomain notation,
   stale/misspelled index text, a citation number, and mechanical punctuation.

The frozen authority is never edited. Every admitted derivative repair needs
an exact source-record span, before/after expression, rationale, and target
verification in the later correction ledger.

## Safe non-overlapping production partition

The four range identities above are safe translation joins: each ends at a
whole active section boundary; no semantic environment, display, sentence,
label, reference, citation, or diagram crosses a join. Reassembly order is
strictly `1--108`, `109--404`, `405--697`, `698--1000`. Only the first range
owns `\chapter`; only the final range owns `\endinput`.

The complete chapter inherits John M. Erdman's CC BY-SA 4.0 boundary,
attribution and change-notice duties, ShareAlike, non-endorsement, and exact
model provenance. No upstream contact occurs during production.
