# Chapter 14 cumulative PDF visual and accessibility audit

Date: 2026-08-24  
Reader boundary: Chapters 1-14  
Result: **pass for this PDF checkpoint; honestly untagged**

## Exact reader

- Path: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-14.pdf`
- Bytes: **2,104,187**
- SHA-256: `3e82aca29ea623502e6ce5b2059238088d8e5b6f81d699463402aff16fe15b41`
- Pages: **193**, US Letter, no rotation, no encryption, no forms, and no
  JavaScript.
- Author metadata: John M Erdman.
- Creator metadata: `OpenAI Codex gpt-5.6-sol, Ultra`.

Two clean fixed-path builds with `SOURCE_DATE_EPOCH=1444126743` produced these
same bytes. The final log has zero TeX errors, undefined references or
citations, unresolved-reference summaries, rerun requests, multiply defined
labels, or missing-character warnings.

## Every-page render review

All 193 pages were freshly rendered at 110 dpi to 935x1210 PNGs. Every page was
inspected through 17 numbered contact sheets; the complete new Chapter 14
surface, physical PDF pages 167-174 (printed pages 161-168), was additionally
inspected at full render resolution.

- No clipped text, formula, header, footer, bibliography entry, index column,
  link marker, or page number was observed.
- No overlapping text, black rectangle, missing glyph, damaged equation, or
  unreadable page was observed.
- No page has ink in the outer five-pixel border. Minimum detected nonblank
  margins are 109 px left, 72 px top, 93 px right, and 60 px bottom.
- Blank physical pages 6, 22, 50, 80, 102, 116, 138, 148, 162, and 166 are
  intentional front-matter or chapter-transition verso pages.
- Chapter 14 is centered, legible, consistently reflowed, and page-filling
  within the established reader design. Its two exercises, displays, and
  cross-references are not clipped.

The render manifest covers all 193 PNGs:
`provenance/CH14_RENDER_MANIFEST.csv`, 22,105 bytes, SHA-256
`3c1fc7b1c45d1689a8b8d87541831b9102839e6e66416b60f660be9bf204bb9d`.
The machine audit is `qa/CH14_RENDER_AUDIT.json`, 4,303 bytes, SHA-256
`733a110197e4a2eca7cb60948e20c408e87b22a8f254fed4447753fe2bb13537`.

## Typography and navigation

Chapter 14 adds no overfull box. The final cumulative log retains two overfull
boxes (7.30707 pt and 11.09703 pt) in previously admitted Chapter 11 material;
their implicated pages were inspected and show no clipping. Four underfull
hboxes and one underfull vbox are harmless URL or layout effects. The 131
small-caps-italic font substitutions are inherited theorem-style fallbacks;
all affected text renders legibly. Hyperref emits 13 PDF-string warnings for
mathematical title tokens, while the visible outlines remain readable.

The PDF contains 85 outline entries and 2,461 link annotations. All 46
referenced font objects are embedded and have ToUnicode maps. The document has
extractable text, working destinations and links, and a complete searchable
Chapter 14 terminology surface.

The PDF has no structure tree and is therefore correctly reported as
**untagged**, not falsely described as fully accessible. This checkpoint
improves navigation and text extraction but does not satisfy the goal's final
semantic accessible-reader requirement; that remains a later full-corpus
surface.
