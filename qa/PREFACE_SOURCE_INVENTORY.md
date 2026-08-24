# FAOA-2015-PREFACE source inventory

Date: 2026-08-24  
State: **source frozen; pretranslation inventory complete; no target created**  
Unit: `FAOA-2015-PREFACE` / front matter

## Exact source identity

- Path: `source/upstream/preface.tex`.
- Upstream heading: `PREFACE`.
- Controlled Indonesian heading: `Prakata`.
- Identity: 18,107 bytes / 351 CRLF-terminated physical records / ASCII /
  SHA-256
  `0976042bbb6ae3b8d1e5bb113a93d51169fada9d3e41f2d01435c76b6729edb9`.
- `\endinput` is physical line 350; line 351 is an empty CRLF-terminated
  record. No source content follows it.
- The frozen manifest independently records this exact member at
  `authority/SOURCE_MANIFEST.csv` row 26. The authoritative source ZIP is
  262,556 bytes / SHA-256
  `0c667cfa7420b61dda8f8cb4ed9d619db8abbd1b53d17eafe7d4a2e153342e53`.
- This inventory does not normalize, repair, or modify the frozen source.

## Ordered document topology

The source contains one unnumbered chapter and four unnumbered sections:

| Surface | Source line | Controlled Indonesian heading |
|---|---:|---|
| `\chapter*{PREFACE}` | 1 | `Prakata` |
| `\section*{Greek Letters}` | 80 | `Huruf Yunani` |
| `\section*{Fraktur Fonts}` | 126 | `Font Fraktur` |
| `\section*{Notation for Sets of Numbers}` | 168 | `Notasi untuk Himpunan Bilangan` |
| `\section*{Notation for Functions}` | 220 | `Notasi untuk Fungsi` |

The ordered `chapter*`/`section*` name sequence, serialized as the five exact
`kind:title` strings joined with LF and no terminal LF, has SHA-256
`e611347567606e5a9348e5352e2e9f14d54f288cb40db19bfeb8d6996d1519c5`.
There are five explicit `\vfill\eject` page boundaries, at lines 77, 118,
165, 209, and 337. There are no numbered chapters, numbered sections,
subsections, theorem-like environments, proofs, exercises, hints, answers, or
solutions in this unit.

Balanced source control surfaces are:

- two `enumerate` pairs and five `\item` calls: the three pivotal Chapter 1
  observations at lines 31--36 and the two defining conditions for a function
  at lines 233--237;
- one `align*` pair at lines 183--205, containing 20 ordered notation rows;
- five `\[` / `\]` display pairs: the author email, two custom tables, and two
  diagrams;
- two `\xy` / `\endxy` pairs;
- one terminal `\endinput`.

## Mathematical and semantic surface census

After stripping TeX comments, the lexical math census is 207 active surfaces:
201 paired dollar-delimited spans (402 dollar delimiters), five bracket-display
containers, and one `align*`
container. This lexical definition intentionally counts mathematical material
inside index arguments and the two custom-table containers; it is a topology
lock, not a claim that every span is a distinct mathematical assertion.

The principal mathematical surfaces are:

1. three finite-dimensional spectral observations at lines 31--36;
2. the 24-letter Greek table at lines 83--109;
3. the 26-letter Fraktur table at lines 132--162;
4. 20 definitions of standard number-set and interval notation at lines
   183--204;
5. the ordered-triple definition of a function and its two conditions at
   lines 229--237;
6. domain, codomain, graph, image, restriction, range, inverse image,
   injective/surjective/bijective, and function-family notation at lines
   238--313;
7. a commutative square at lines 315--328 and a commutative triangle at lines
   330--334.

The square has nodes `R,U,S,T` and arrows `j:R->U`, `f:R->S`, `h:U->T`, and
`k:S->T`; its asserted equality is `h \circ j = k \circ f`. The triangle has
nodes `R,S,T` and arrows `f:R->S`, `g:R->T`, and `k:S->T`; its asserted
equality is `g = k \circ f`. These relationships must become text alternatives
in the future semantic reader without replacing the visible diagrams.

## Labels, references, citations, index hooks, and defined terms

- Labels: one, `C0009`, attached to the starred number-set section at line
  168. Its ordered-argument digest is
  `521d0c3909abf08aaf64d9a7ff258637ce529ac8e93f99681749aa1a8e4565c0`.
- Inbound reference calls: zero `\ref`, `\eqref`, or `\pageref` calls in this
  file, and no other frozen upstream file refers to `C0009`. The label is still
  a source identifier and must be preserved.
- Citation calls: five, in source order: `Halmos:1982`, `BrownDF:1973`,
  `Erdman:2010`, `Erdman:2005`, and `Erdman:2007`. The ordered keys joined by LF
  have SHA-256
  `81f314e176335459d6767e3c7966eb6ccac628d17c1dee580ad3755622aaa5c2`.
- Active index calls: 53. One commented candidate at line 274 is excluded from
  this count. Exact balanced arguments, in source order and joined by LF, have
  SHA-256
  `ea0611af97cb060961ff51e6fca78d2a5b8a44e6ee100fa4f98fb91d0062643b`.
- Defined-term calls: 21. In order they are `function`, `domain`, `input
  space`, `codomain`, `target space`, `output space`, `graph`, `image`,
  `restriction`, `image`, `range`, `image`, `inverse image`, `injective`,
  `one-to-one`, `surjective`, `onto`, `bijective`, `a one-to-one
  correspondence`, `commute`, and `commutative diagram`. The ordered arguments
  joined by LF have SHA-256
  `d21d97581be264dae0d1c8f412f00dab2500b8d9243d703519515739b67e4505`.

All five citation keys already resolve in the frozen bibliography database.
No citation text is imported into this unit.

## Two table surfaces and their component boundary

The Greek surface uses one `\table{}`, one `\rr`, 23 ordinary `\r` row
terminators, a final `\hfil` row, and one empty `\caption{}`. It has three
columns, one header row, and 24 data rows (`Alpha` through `Omega`).

The Fraktur surface uses one `\table{}`, one ordinary header `\r`, one `\rr`,
25 ordinary data-row `\r` terminators, a final `\hfill` row, and one empty
`\caption{}`. It has three columns, two header rows, and 26 data rows (`A`
through `Z`). Across both surfaces the raw source therefore contains two
`\table{}` calls, 49 single-`\r` calls, two `\rr` calls, and two empty custom
captions.

These commands are defined only by upstream `TABLE.TEX`, 2,614 bytes /
SHA-256
`df97d544e9d7a82a65f8292eaaf37eef053adb23f737a7f64d28e957b70d006f`.
That component has no embedded author, provenance, or license notice and is
excluded by `00_control/SOURCE_AUTHORITY.md`. The future target must reproduce
the two tables with ordinary, locally authored LaTeX (`tabular`/`array` and
standard rules), preserving column order, all 50 data rows, glyphs, and the
explicitly English pronunciation strings. It must contain none of `\table{}`,
`\rr`, the custom row-level `\r`, or the custom empty `\caption{}`.

## Includes, diagrams, and active dependencies

The preface file itself has zero `\input`, `\include`, `\includegraphics`,
`\epsfbox`, `figure`, or standard `table` calls. It nevertheless relies on
master-defined notation macros and on two external macro components:

- `TABLE.TEX` for the two table surfaces: excluded and to be replaced;
- `DIAGXY.TEX` for `\square` and `\btriangle`: required, already retained
  byte-identically under Michael Barr's embedded notice at 41,908 bytes /
  SHA-256
  `3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb`.

No badge art, Wiener epigraph, raster image, EPS image, or PDF image is called
from `preface.tex`.

## Relationship to the current Indonesian wrapper

The admitted wrapper is
`source/id-ID/functional-analysis-id-through-ch17.tex`, 10,820 bytes / 346 LF
records / SHA-256
`51b3f4d790e3d09ac6ac4c160284510e4827140ecaa5a961a46c880ae5c8bb39`.
It currently has this front-matter order:

1. translated title and authorship/version surface;
2. visible CC BY-SA 4.0 attribution/change/non-endorsement notice;
3. source URLs and exact source hashes;
4. `\tableofcontents`;
5. `\mainmatter` and the 17 admitted chapter includes.

It already inputs exact-case `DIAGXY.TEX` but deliberately does not input
`TABLE.TEX`. It has no preface include. The lossless future insertion point is
after `\tableofcontents` and before `\mainmatter`, matching the official master.
The new include must point to a separate `source/id-ID/preface-id.tex`; no
admitted chapter include or chapter byte may change. A unique hyperlink/TOC
anchor for `Prakata` and for source label `C0009` may be added, but the source
identifier and front-matter status must remain explicit.

## Rights and adaptation locks

- Erdman's substantive preface is adapted under CC BY-SA 4.0. Preserve
  authorship, all five citation keys, the license link, the translation/change
  notice, ShareAlike, no added restriction, and explicit non-endorsement by
  Erdman and Portland State University.
- The short Halmos quotation at lines 3--4 is third-party material. Preserve
  Halmos attribution, book title, citation key, and the pedagogical idea, but
  render the idea as an Indonesian paraphrase without quotation marks or
  reproduced wording.
- Replace, rather than redistribute, the unlicensed `TABLE.TEX` machinery.
- Preserve `DIAGXY.TEX` byte-identically and retain Michael Barr's notice.
- Do not add the excluded badge artwork or Wiener epigraph.
- The source's author-email statement may be translated as Erdman's historical
  source statement. The edition-wide wrapper must continue to make clear that
  the derivative is not endorsed and that no upstream contact occurred during
  production.

## Exhaustive safe split

Each fragment below is the exact inclusive source-line range encoded as ASCII
with its original terminating CRLF on every record. The fragments are ordered,
nonoverlapping, exhaustive, and sum to 18,107 bytes.

| Fragment | Source lines | Bytes | SHA-256 | Scope |
|---|---:|---:|---|---|
| `PREFACE-F01` | 1--75 | 6,592 | `6e23b6aa5f3cf2ab6f0219baad4d90643413d707b010fb3f09cdfe38698ccce7` | narrative, pedagogy, prerequisites, scope, electronic-life/license discussion |
| `PREFACE-F02` | 76--117 | 2,521 | `ffe12d26fb09a060e629c28316e7bece6e6ee0bc931cbfa6732f88ae9839d3bf` | Greek-letter table |
| `PREFACE-F03` | 118--164 | 2,350 | `1cc1a82fb8f3637937fd24ee1a17f266ecfa8a74d8b8aca198dfec6b421e19fc` | Fraktur-font table |
| `PREFACE-F04` | 165--208 | 1,870 | `1b6997cecdf6a6f73a58ae62a70e0d5183249240b98db2239d1821013156ddcb` | number-set and interval notation |
| `PREFACE-F05` | 209--272 | 2,268 | `c57f657811c0a9953e0d889fb8a8eb583af42570339f28681f30c7a796d5ac34` | function definition through `\fml F(S,T)` |
| `PREFACE-F06` | 273--336 | 2,453 | `3edaa9d6cc90647f3f1c0d119a84d30161ba51f53e8f3b4e6b6562b4de1ef35f` | restriction, images, injectivity/surjectivity/bijectivity, diagrams |
| `PREFACE-F07` | 337--351 | 53 | `a4c2638c4bfa1d341a7b4963f33dc20c795934ccdcaa20b2ebd1f8ac9420b5b8` | terminal page boundary and `\endinput` |

The production target may use these fragments for review and assembly, but it
must remain one contiguous front-matter unit in source order.
