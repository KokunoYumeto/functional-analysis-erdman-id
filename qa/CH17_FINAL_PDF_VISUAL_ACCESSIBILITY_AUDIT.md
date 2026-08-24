# Chapter 17 cumulative PDF visual and accessibility audit

Date: 2026-08-24  
Reader boundary: Chapters 1--17  
Result: **pass for this PDF checkpoint; honestly untagged**

## Exact reader and deterministic build

- Path: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-17.pdf`
- Bytes: **2,432,395**
- SHA-256: `22fda5f25205f2a442c2b907db015fb4c93cb46cfcba6a1fa8814449469073f1`
- Pages: **232**, US Letter, no rotation.
- Exact Chapter 17 target: `source/id-ID/K0_functor-id.tex`, 61,673 bytes,
  1,362 LF records, SHA-256
  `061ffd28907e2251fc8b01077888de3e11b3bce67fec1ba52b080c924a241059`.
- Exact cumulative master:
  `source/id-ID/functional-analysis-id-through-ch17.tex`, 10,820 bytes,
  346 LF records, SHA-256
  `51b3f4d790e3d09ac6ac4c160284510e4827140ecaa5a961a46c880ae5c8bb39`.

Two clean fixed-path builds with `SOURCE_DATE_EPOCH=1444126743` produced
byte-identical PDFs. The pass-1 witness, fixed-path PDF, and canonical reader
all have the exact byte count and SHA-256 above. All 20 snapshotted inputs
remained unchanged through both builds and still match the snapshot after the
render, extraction, font, and navigation audits.

The final log has zero TeX errors, undefined references, undefined citations,
unresolved-reference summaries, rerun requests, multiply defined labels, or
missing-character warnings. It retains the two previously admitted Chapter 11
overfull boxes, **7.30707 pt** and **11.09703 pt**. Chapter 17 adds three
overfull hboxes: **21.73163 pt**, **14.48381 pt**, and **3.32439 pt**. Their
physical surfaces are pages 195--197; each was rendered at 300 dpi and checked
at full resolution, and no text, symbol, matrix, or rule is clipped or overlaps
the margin. Four underfull hboxes and three underfull vboxes are harmless
URL/page-layout effects. The 150 font warnings are inherited small-caps-italic
fallbacks. Hyperref emits 28 PDF-string warnings for mathematical title tokens;
the visible outlines are readable.

The build result is `qa/CH17_FINAL_BUILD_RESULT.json`, 1,719 bytes, SHA-256
`b88e5a0d12455ee78f04cb05fd2f27cb1f59f3ea25af1815a063ec561d8fd4e7`.
The locked build driver is `qa/run_ch17_final_build.ps1`, 8,481 bytes, SHA-256
`79dd08c455767f1c760ab8d6b0a102dd792002409ba6fe9a63d820dea95ed9d6`.

## Every-page render review

All 232 pages were freshly rendered at 110 dpi to 935x1210 PNGs. Three
independent, non-overlapping review passes inspected physical pages 1--80,
81--160, and 161--232 respectively. The last pass separately inspected the
entire new Chapter 17 surface, physical pages **193--210**, and the 300-dpi
renders of pages 195--197. The bibliography occupies pages 211--212 and the
updated index occupies pages 213--232.

- No clipped text, formula, matrix, commutative diagram, header, footer,
  bibliography entry, index column, link marker, or page number was observed.
- No overlapping text, black rectangle, missing glyph, damaged equation, or
  unreadable page was observed.
- No page has ink in the outer five-pixel border. Minimum detected nonblank
  margins are 109 px left, 72 px top, 78 px right, and 60 px bottom.
- Blank physical pages 6, 22, 50, 80, 102, 116, 138, 148, 162, 166, 180, and
  192 are intentional front-matter or chapter-transition verso pages.
- Chapter 17 is centered, page-filling, and consistent with the established
  reader design. Its 46 matrices, 15 diagram surfaces, long exact sequences,
  equivalence symbols, implication repairs, Bratteli diagrams, citations, and
  cross-references are all legible and unclipped.

The render manifest covers all 232 PNGs:
`provenance/CH17_RENDER_MANIFEST.csv`, 26,569 bytes, SHA-256
`2b3401c99ed6c81fe52f9094122fc48124b08df975dc323efd0a9410de2fcfd1`.
The machine render audit is `qa/CH17_RENDER_AUDIT.json`, 4,943 bytes, SHA-256
`d2c6d27efaabdd38995531c906a64c57509d99871e1486b3e12c1035a23f9549`.
The render-evidence generator is `qa/make_ch17_render_evidence.py`, 6,482
bytes, SHA-256
`e385401ea7aa606fb68b53384e2383b935dfd9cfc57a5b930482a87679e11dc2`.

## Navigation, fonts, and interactive-surface audit

The PDF metadata reports author John M Erdman and creator
`OpenAI Codex gpt-5.6-sol, Ultra`. The catalog language is `id-ID`.

- 104 outline entries.
- 2,974 link annotations: 2,965 internal GoTo actions and 9 URI actions.
- 2,312 named destinations and **zero unresolved internal links**.
- 48 referenced font objects; every one is an embedded subset and every one
  has a Unicode map.
- Extractable and searchable Indonesian text, including the complete Chapter
  17 surface: 874,692 extracted bytes, 232 page delimiters, zero replacement
  characters, zero recognized mojibake signatures, and zero local-path leaks.
- No encryption, AcroForm, embedded file/name tree, file-attachment
  annotation, JavaScript/name tree, JavaScript or Launch action, RichMedia,
  movie, sound, or screen annotation.

The text/font result is `qa/CH17_TEXT_FONT_AUDIT.json`, 1,347 bytes, SHA-256
`70bd4707887587ad30c7c941b9fd94e6aeb57a2a631ba726c2424eef0f00160e`.
The navigation/security result is
`qa/CH17_PDF_SECURITY_NAVIGATION_AUDIT.json`, 1,372 bytes, SHA-256
`3d82cabcf8ecdeee1cae0d23628253a54f7598ff205bbdc32eb6cf7d34aa2c57`.

The PDF has no structure tree or marked-content catalog flag and is therefore
correctly reported as **untagged**, not falsely described as fully accessible.
This checkpoint supplies working navigation and Unicode text extraction, but
the goal's final semantic accessible-reader surface remains a separate
full-corpus deliverable.
