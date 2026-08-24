# Chapter 13 cumulative PDF visual and accessibility audit

Date: 2026-08-24  
Reader boundary: Chapters 1–13  
Result: **pass for this PDF checkpoint; honestly untagged**

## Exact reader

- Path: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-13.pdf`
- Bytes: **2,031,973**
- SHA-256: `b7810718cb9a633c694aed126fc5c10786864650b076c2ad5bb7329191db3b65`
- Pages: **183**, US Letter, no rotation, no encryption, no forms, no
  JavaScript.
- Author metadata: John M Erdman.
- Creator metadata: `OpenAI Codex gpt-5.6-sol, Ultra`.

Two clean fixed-path builds with `SOURCE_DATE_EPOCH=1444126743` produced these
same bytes. The final log has zero TeX errors, undefined references or
citations, unresolved-reference summaries, rerun requests, multiply defined
labels, or missing-character warnings.

## Every-page render review

All 183 pages were freshly rendered at 110 dpi to 935×1210 PNGs. Every page was
inspected through 16 numbered contact sheets; the new Chapter 13 pages 161–164
were additionally inspected at full render resolution.

- No clipped text, formula, header, footer, index column, link marker, or page
  number was observed.
- No overlapping text, black rectangle, missing glyph, damaged equation, or
  unreadable page was observed.
- No page has ink in the outer five-pixel border. Minimum detected nonblank
  margins are 109 px left, 72 px top, 93 px right, and 60 px bottom.
- Blank pages 20, 48, 78, 100, 114, 136, 146, 160, and 164 are intentional
  verso/layout pages at chapter transitions; page 164 is the blank verso after
  Chapter 13.
- Chapter 13 occupies reader pages 157–159 (physical PDF pages 161–163) and is
  balanced, centered, legible, and page-filling within the established book
  design.

The render manifest covers all 183 PNGs:
`provenance/CH13_RENDER_MANIFEST.csv`, 20,966 bytes, SHA-256
`b7ab64c7ccaa059f972910f56d410ba5d133e960e3ed40aa8962bfe0f4bdd02a`.
The machine audit is `qa/CH13_RENDER_AUDIT.json`.

## Typography and navigation

The final log has two overfull boxes (7.30707 pt and 11.09703 pt) in previously
admitted Chapter 11 material, not Chapter 13; their implicated pages were
inspected and show no clipping. Five underfull notices are harmless URL/verso
layout effects. The 129 small-caps-italic font substitutions are inherited
from the source theorem typography; all affected text rendered legibly.

The PDF contains 81 outline entries and 2,343 link annotations. Cross-chapter
references and citations resolve in the cumulative build. All listed fonts are
embedded, subset, and have Unicode maps. The document has extractable text and
working outlines/destinations/links.

The PDF has no structure tree and is therefore correctly reported as
**untagged**, not falsely described as fully accessible. This checkpoint
improves navigation and text extraction but does not satisfy the goal's final
semantic accessible-reader requirement; that remains a later full-corpus
surface.

