# Chapter 15 cumulative PDF visual and accessibility audit

Date: 2026-08-24  
Reader boundary: Chapters 1-15  
Result: **pass for this PDF checkpoint; honestly untagged**

## Exact reader

- Path: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-15.pdf`
- Bytes: **2,156,827**
- SHA-256: `5b8d5d5f44671f4695dea7f470d6ea7bb63fd2a0ff459aa8e8fb1a0c0faac7c7`
- Pages: **200**, US Letter, no rotation, no encryption, no forms, no embedded
  files, no rich media, and no JavaScript.
- Catalog language: `id-ID`.
- Author metadata: John M Erdman.
- Creator metadata: `OpenAI Codex gpt-5.6-sol, Ultra`.

Two clean fixed-path builds with `SOURCE_DATE_EPOCH=1444126743` produced these
same bytes. The final log has zero TeX errors, undefined references or
citations, unresolved-reference summaries, rerun requests, multiply defined
labels, or missing-character warnings. The build result is
`qa/CH15_FINAL_BUILD_RESULT.json`, 1,148 bytes, SHA-256
`545cc604baf5cb720d7205eac83865a16af5629edc0b392e7dc79fba6e1a6ffe`.

## Every-page render review

All 200 pages were freshly rendered at 110 dpi to 935x1210 PNGs. Every page was
inspected through 17 numbered contact sheets; the complete new Chapter 15
surface, physical PDF pages 175-179 (printed pages 169-173), was additionally
inspected at full render resolution. Physical page 180 is its intentional blank
verso.

- No clipped text, formula, header, footer, bibliography entry, index column,
  link marker, or page number was observed.
- No overlapping text, black rectangle, missing glyph, damaged equation, or
  unreadable page was observed.
- No page has ink in the outer five-pixel border. Minimum detected nonblank
  margins are 109 px left, 72 px top, 93 px right, and 60 px bottom.
- Blank physical pages 6, 22, 50, 80, 102, 116, 138, 148, 162, 166, and 180
  are intentional front-matter or chapter-transition verso pages.
- Chapter 15 is centered, legible, consistently reflowed, and page-filling
  within the established reader design. Its tagged Fredholm systems, displayed
  exact sequence, formulas, citations, and cross-references are not clipped.

The render manifest covers all 200 PNGs:
`provenance/CH15_RENDER_MANIFEST.csv`, 22,901 bytes, SHA-256
`1b4aae6c68668641aa4f86eb6aba87720017df9676773b532dbcf7da06265567`.
The machine audit is `qa/CH15_RENDER_AUDIT.json`, 4,313 bytes, SHA-256
`294705139b6c1a8dd46cbb725579b0114633a0ed58740d0b41d2214414717048`.

## Typography and navigation

The final one-word reflow in Proposition 15.2.3 eliminated Chapter 15's sole
1.39676 pt overfull line. The cumulative log retains only two previously
admitted Chapter 11 overfull boxes, 7.30707 pt and 11.09703 pt; their implicated
pages remain visually unclipped. Four underfull hboxes and one underfull vbox
are harmless URL or page-layout effects. The 132 font warnings are inherited
small-caps-italic fallbacks; all affected text renders legibly. Hyperref emits
13 PDF-string warnings for mathematical title tokens, while the visible
outlines remain readable.

The PDF contains 90 outline entries, 2,568 link annotations, 2,021 named
destinations, and zero unresolved internal links. All 46 referenced font
objects are embedded subsets and have Unicode maps. The document has
extractable text, working destinations and links, and a complete searchable
Chapter 15 terminology surface.

The PDF has no structure tree and is therefore correctly reported as
**untagged**, not falsely described as fully accessible. This checkpoint
improves navigation and text extraction but does not satisfy the goal's final
semantic accessible-reader requirement; that remains a later full-corpus
surface.
