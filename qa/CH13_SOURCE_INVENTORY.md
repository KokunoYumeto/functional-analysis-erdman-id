# Chapter 13 source inventory

## Scope and source identity

- Source: `source/upstream/GNS_construction.tex`
- Source bytes: **11,965**
- SHA-256: `fcc774cecc607d9860540da7b757ae04a3c43afe9d9a17e8c881e077f02682c1`
- Encoding surface: 7-bit ASCII; no BOM; no NUL bytes.
- Line endings: **289 CRLF**, 0 lone LF, 0 lone CR.
- Logical record count: **289**. The source ends in CRLF.
- Terminal command: `\endinput` at line 289.

The authority file was read only. This inventory does not normalize or alter
its bytes.

## Ordered document structure

| Line | Level | Title | Span |
|---:|---|---|---:|
| 1 | chapter | `THE GELFAND-NAIMARK-SEGAL CONSTRUCTION` | 1–289 |
| 3 | section | `Positive Linear Functionals` | 3–90 |
| 91 | section | `Representations` | 91–203 |
| 204 | section | `The GNS-Construction and the Third Gelfand-Naimark Theorem` | 204–289 |

There are no subsections or external includes.

## Environment census

There are **32** `\begin{...}` occurrences and 32 matching `\end{...}`
occurrences.

| Environment | Count |
|---|---:|
| `prop` | 10 |
| `defn` | 7 |
| `exam` | 5 |
| `cor` | 2 |
| `proof` | 2 |
| `thm` | 2 |
| `cau` | 1 |
| `conv` | 1 |
| `exer` | 1 |
| `notn` | 1 |

## Semantic and cross-reference surface

- Labels: **7 occurrences, 7 unique, no duplicates**:
  `gelfand_naimark_segal`, `0025105`, `0028`, `002802`, `0029`,
  `thm_exist_faith_rep`, and `002973`.
- References: **2**: cross-chapter `C063527` and local `0025105`.
- Citations: **7 occurrences** using six keys: `KadisonR:1983` twice, plus
  `Blackadar:2006`, `Conway:1990`, `DoranB:1986`, `Fillmore:1996`, and
  `Murphy:1990`.
- Index hooks: **28**.
- Defined-term commands (`\df`): **13**.
- Exercises: **1**, at source lines 146–149.
- Proof environments: **2**, both citation-only; there are no source exercise
  answers, solutions, or explicit hints in this chapter.

## Math surface

The reproducible top-level math-surface count is **237**:

- 233 inline `$...$` spans (466 unescaped dollar delimiters);
- 4 `\[...\]` display spans;
- no top-level equation/align/gather/multline environments.

Opening and closing display brackets are both four. Unescaped brace counts are
balanced at 152/152.

## Assets, dependencies, and build risks

- `\input`: 0; `\include`: 0; `\includegraphics`: 0.
- External chapter assets: none.
- The chapter is a fragment and depends on the cumulative wrapper for theorem
  environments, custom math macros, bibliography, index, and cross-chapter
  label `C063527`.
- The single exercise has no upstream support surface and must remain linked
  to the separately provenanced O001 mastery layer rather than being presented
  as source-supplied solution content.
- The definition of a state and the following norm criterion use an identity
  in an unrestricted `$C^*$`-algebra context even though Chapter 12 admits
  nonunital algebras. The derivative correction is adjudicated in
  `qa/CH13_PRETRANSLATION_MATH_REVIEW.md`.
- Mechanical source anomalies include the redundant positivity quantifier at
  line 30, doubled exercise period at line 148, missing algebra name and final
  punctuation in the notation environment ending at line 219, and `that is.`
  at line 233.

The frozen source remains unchanged. All derivative repairs must be explicit
in the Chapter 13 correction ledger and checked against the final target.
