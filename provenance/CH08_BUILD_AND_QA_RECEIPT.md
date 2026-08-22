# FAOA-2015-CH08 build and QA receipt

Date: 2026-08-22  
Decision: **admitted**  
Course role: `D20_core`

This receipt admits the complete Indonesian Chapter 8, *Beberapa Teori
Spektral*, and the cumulative Chapter 1--8 reader. Translation, mathematics,
structure, references, build determinism, visual layout, navigation, component
rights, privacy, and append-only backend gates pass. It does not claim that
Chapters 9--17, the semantic HTML reader, the O001 solved mastery layer, or the
original compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Frozen source: `source/upstream/spectrum.tex`, 25,716 bytes / 611
  CRLF-terminated lines / SHA-256
  `ae68cf224c6218ecd501cc983428cf924a3c361c6324a6b40793b1e9ba44b4dd`.
  Its sole active `\endinput` is line 603; the last eight records are inert
  blanks and are not copied into the derivative.
- Active source through `\endinput`: 25,698 bytes / 603 lines / SHA-256
  `2c4dea4be2cfb89eb507742b4052619c7cf09904d54921884f88be49b19ba05b`.
- Admitted target: `source/id-ID/spectrum-id.tex`, 26,947 bytes / 603 LF lines /
  SHA-256
  `1120da36ebd0793690ecb47b33b921c81376d1bf7d2f03d9821b79356dfd03bc`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch08.tex`, 9,714 bytes / 334 LF
  lines / SHA-256
  `d0b4130b9fa6f85baef22f316ea914d5519bf30d6e82d8e6d824f2cf211c1998`.
- The admitted Chapter 1--7 targets and every locked backend prefix remain
  unchanged.

## Structural, mathematical, reference, and language replay

The locked checker preserves 96 balanced environment pairs: 33 propositions,
14 examples, 14 proofs, eight definitions, eight corollaries, four theorems,
two exercises, one notation block, ten enumerations, and two matrix
environments. It preserves all 28 labels, 16 ordinary references, three
citations, 73 index hooks, 20 defined-term hooks, and 34 item markers. All
references resolve locally or to admitted Chapters 1--7; Chapter 8 introduces
no future-reference surface. Twelve proof blocks remain explicit hints, one is
a proof comment, and one remains a full proof. Neither exercise is falsely
given an upstream answer or solution.

The source has 414 mathematical surfaces and the target 416. All six sequence
edit blocks are classified: one paired Indonesian-order movement; the corrected
scalable delimiter; the explicit Volterra formula on `C([0,1])`; the inserted
Hilbert-space binding and typed operator; and the corrected diagonal-entry set.
The only control-shape edit repairs the Spectral Mapping Theorem's malformed
mandatory body group to an optional theorem title. Two prose-only reflows at
target lines 399 and 525 preserve every mathematical surface.

The final checker is `qa/check_ch08_translation.py`, 41,639 bytes / SHA-256
`2720ec3cbe46060d65079a496e5fc550744c25863c11bdb1b5bb84047b14d54f`.
Its durable classified inventory is
`qa/CH08_CLASSIFIED_DELTA_INVENTORY.md`, 10,143 bytes / SHA-256
`efb89e83e3bc66861f941175e9abdc40d02e93c7b1d1e0fbe6e9afcadd1c0a4f`.
Repeated runs return `pass`, with zero visible English, mojibake, private path,
or unclassified structural/math residue.

An independent bilingual rereview read all 603 active source and target lines,
every mathematical and control surface, and the complete exercise/hint and
terminology surface. It normalized the corrected diagonal set to project
macros and changed one inconsistent `spektrum titik hampiran` occurrence to
the controlled `spektrum titik aproksimatif`. No remaining mathematical,
semantic, terminology, or prose defect was found. The final review record is
`qa/CH08_INDEPENDENT_BILINGUAL_REVIEW.md`, 5,504 bytes / SHA-256
`74647e7a65f10026601cb6b54c97badf6528809620d4d2ef93e9b690d96c078f`.

Eight bounded source corrections are append-only in
`provenance/SOURCE_CORRECTIONS.md`, 25,794 bytes / SHA-256
`93836f6e440e81cb606a55a25c837318b620348379f4690923ab700bb6b3d23b`:
the missing word boundary; nonzero reciprocal parameter; stray parenthesis;
scalable-delimiter direction; Volterra domain/formula binding; Hilbert-space
binding; theorem-title syntax; and diagonal-entry set notation. The complete
admitted Chapter 1--7 ledger prefix is byte-identical to the previous receipt.
No upstream contact occurred.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex, and
  Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two fully cleaned builds in the same fixed output directory produced directly
  byte-identical PDFs: 1,593,249 bytes / 129 US-Letter pages / SHA-256
  `fb6488691e2127bc0b8e3f94f38033eb3bdbe0c61efedc66c07de8f3b3444fbd`.
- Final TeX log: 49,859 bytes / SHA-256
  `2a877bda83d7631523cea63cd8c5b1393ccb92180d462088513db1ede1c31c43`.
- Blocking log counts are zero: TeX/package errors, unresolved references or
  citations, rerun notices, multiply defined labels, overfull boxes, vbox
  warnings, and missing characters. Four inherited underfull hboxes arise from
  long authority URLs/hashes in the wrapper. Ninety-nine legacy small-caps
  italic substitutions use small-caps slanted and do not alter content.
- BibTeX uses 30 entries with zero warnings. MakeIndex accepts all 1,332
  entries, rejects zero, makes 14,778 comparisons, writes 1,625 lines, and
  reports zero warnings.

The canonical reader is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-8.pdf`; its
fixed-path build copy is byte-identical.

## Visual and accessibility evidence

All 129 physical pages were rendered at 150 dpi. The exact render set contains
129 PNGs / 45,549,537 aggregate bytes, each 1,275 by 1,650 pixels. The public
render manifest is 25,114 bytes / SHA-256
`796f36332ef748a4b1a7d8f01b7d75c7ec9da5236640f059d31df14fa3ec3e71`;
replay finds no missing, extra, duplicate, dimension-mismatched, or
hash-mismatched page. The public all-page contact sheet is 3,781,079 bytes /
SHA-256
`5d53f2c381f8108dd3a947e2ad85c744c21f2070c6397611b525af978690b6cf`.

Every page was inspected through eleven detailed consecutive contact sheets
and the public all-page sheet. Full-size physical pages 107--113 received a
second inspection covering the Chapter 8 theorem sequence, spectral-radius
formula, Volterra exercise, Hilbert-space spectrum definitions, Spectral
Mapping Theorem, and final model-operator examples. No clipping, overlap,
off-center body block, damaged glyph, unreadable formula, broken header, or
margin violation was found.

Bounding-box replay finds 61,064 words and zero boxes outside page bounds, with
minimum clearances of 72.000 points left, 71.254988 right, 49.278601 top, and
37.803801 bottom. The six zero-word pages are intentional blank versos 20, 48,
78, 100, 114, and 116. The formal report is
`qa/CH08_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 6,668 bytes / SHA-256
`4ee0a948e108e905594c0bcc1858f050a001db1c60136a7e2c8135d64cf9520b`.

The PDF has language `id-ID`, 50 outline entries, 1,241 named destinations,
1,718 resolved internal links, eight URI annotations over six unique external
targets, and zero unresolved internal links. It has no encryption, form,
widget, JavaScript, launch action, embedded attachment, rich media, or unsafe
action. All 43 font resources are embedded subsets with Unicode maps. Extracted
text is 491,578 bytes / SHA-256
`ee477d952cb150428f39dba08acdff3ce43820f63dd462fcf5d8eb3136c7817e`
and contains no replacement character, mojibake signature, or local path.

The PDF remains honestly untagged and lacks a structure tree, semantic roles,
alternative-text framework, and guaranteed screen-reader order. It is a
visually usable, searchable, navigable reader, not the final accessible
edition. Semantic HTML and/or a later tagged-PDF derivative remains a required
edition-level deliverable and is nonblocking only for this chapter boundary.

## Rights, component, privacy, and backend closure

The wrapper supplies Erdman attribution, a CC BY-SA 4.0 link, translation and
technical-change notices, ShareAlike terms, and non-endorsement. `DIAGXY.TEX`
remains byte-identical under Michael Barr's embedded notice. `TABLE.TEX`, badge
artwork, and uncleared quotation components remain absent. Separately authored
solutions, mastery support, and the compact-spectral/SVD bridge are not
represented as Erdman-authored content. A bounded public-surface scan finds no
credential, live local path, unrelated-lane reference, or private control
artifact.

The Chapter 8 projection appends 86 semantic units, 96 segments, 387 relations,
416 formula maps, 73 index rows, two exercise-support records, 12 proof-hint
links, eight correction records, 16 new terminology records over 20 defined
term occurrences, ten exact public artifact bindings, and eight typed QA
events. It preserves every admitted Chapter 1--7 byte prefix and ID; Chapter 8
closes no earlier pending reference because none targets its labels.

Before this receipt was bound, the canonical validator ran the complete
generator twice with byte-identical outputs, validated exact JSON/CSV round
trips, globally unique IDs, relation endpoints, public artifact bytes,
private-control exclusion, and append-only closure: 13,084 JSONL records,
1,332 index rows, 14,416 globally unique IDs, 8,400 checked relation endpoints,
and a 28-row / 2,548-byte manifest with SHA-256
`a4ec6cb73b0adf1a262c4bf201c07db8bd3b1f06165c460897145253f2b5adf9`.
The final post-receipt validator promotes Chapter 8 to `admitted` / `passed`
and binds this exact receipt; its final manifest identity is recorded in
durable state and the root handoff rather than circularly embedded here.

Chapter 8 is admitted. The whole edition remains `in_progress`, and the active
source-order cursor advances to `FAOA-2015-CH09`,
`source/upstream/topvecspaces.tex`.
