# Chapter 16 cumulative PDF visual and accessibility audit

Date: 2026-08-24  
Reader boundary: Chapters 1-16  
Result: **pass for this PDF checkpoint; honestly untagged**

## Exact reader and deterministic build

- Path: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-16.pdf`
- Bytes: **2,278,823**
- SHA-256: `8af194778cd60630ec767cfb381e4798253aa5d2ee205d2e72489cf3b5d90ef5`
- Pages: **213**, US Letter, no rotation.
- Exact Chapter 16 target: `source/id-ID/extensions-id.tex`, 43,804 bytes,
  1,000 LF records, SHA-256
  `59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3`.
- Exact cumulative master: `source/id-ID/functional-analysis-id-through-ch16.tex`,
  10,679 bytes, 345 LF records, SHA-256
  `6e528b0193d3179b58e44169430d043fa5399f7c860f09d832eb3ccd954a5388`.

Two clean fixed-path builds with `SOURCE_DATE_EPOCH=1444126743` produced
byte-identical PDFs. The pass-1 witness, fixed-path PDF, and canonical reader
all have the exact byte count and SHA-256 above. All 19 snapshotted inputs
remained unchanged through both builds and still match the snapshot after the
render audit.

The final log has zero TeX errors, undefined references, undefined citations,
unresolved-reference summaries, rerun requests, multiply defined labels, or
missing-character warnings. It honestly retains the two previously admitted
Chapter 11 overfull boxes, **7.30707 pt** and **11.09703 pt**; Chapter 16 adds
**zero** overfull boxes. Four underfull hboxes and one underfull vbox are
harmless URL/page-layout effects. The 132 font warnings are inherited
small-caps-italic fallbacks. Hyperref emits 13 PDF-string warnings for
mathematical title tokens; visible outlines are readable.

The build result is `qa/CH16_FINAL_BUILD_RESULT.json`, 1,441 bytes, SHA-256
`fb38212312f2b17b68934398e563f82128035d6717a85aa6687f7a684b8ccaae`.
The locked build driver is `qa/run_ch16_final_build.ps1`, 8,451 bytes, SHA-256
`1971e9aec764a18e53875de3b3192ee6caec1a8fd4dcf607eb637d7fc8f83f25`.

## Every-page render review

All 213 pages were freshly rendered at 110 dpi to 935x1210 PNGs. Every page
was inspected through all 18 numbered contact sheets. The entire new Chapter
16 surface, physical PDF pages **181-191** (printed pages 175-185), was also
inspected page by page at full render resolution. Physical page **192** is the
intentional blank verso; the bibliography occupies pages 193-194 and the
updated index occupies pages 195-213.

- No clipped text, formula, commutative diagram, header, footer, bibliography
  entry, index column, link marker, or page number was observed.
- No overlapping text, black rectangle, missing glyph, damaged equation, or
  unreadable page was observed.
- The boxed scope notice on physical page 185 is fully inside the text block
  and legible.
- No page has ink in the outer five-pixel border. Minimum detected nonblank
  margins are 109 px left, 72 px top, 93 px right, and 60 px bottom.
- Blank physical pages 6, 22, 50, 80, 102, 116, 138, 148, 162, 166, 180, and
  192 are intentional front-matter or chapter-transition verso pages.
- Chapter 16 is centered, page-filling, and consistent with the established
  reader design. Its matrices, Toeplitz extension, pullback and lifting
  diagrams, exact sequences, long formulas, citations, and cross-references
  are not clipped.

The render manifest covers all 213 PNGs:
`provenance/CH16_RENDER_MANIFEST.csv`, 24,385 bytes, SHA-256
`930d84c8b15c5b2c352538ee40e923cca5642cccd2229179a7366d28c310db1b`.
The machine render audit is `qa/CH16_RENDER_AUDIT.json`, 4,529 bytes, SHA-256
`1262a4702d243b693891ebe39c75d8ec7f60290a770f7dbfa15e241f93bc72ec`.
The render-evidence generator is `qa/make_ch16_render_evidence.py`, 6,476
bytes, SHA-256
`7eea038a9a451cae649fc2d8767c22080acac024b43d99d87e10a3be45899e8c`.

## Navigation, fonts, and interactive-surface audit

The PDF metadata reports author John M Erdman and creator
`OpenAI Codex gpt-5.6-sol, Ultra`. The catalog language is `id-ID`.

- 95 outline entries.
- 2,796 link annotations: 2,787 internal GoTo actions and 9 URI actions.
- 2,141 named destinations and **zero unresolved internal links**.
- 47 referenced font objects; every one is an embedded subset and every one
  has a Unicode map.
- Extractable and searchable Indonesian text, including the complete Chapter
  16 surface.
- No encryption, AcroForm, embedded file/name tree, file-attachment
  annotation, JavaScript/name tree, JavaScript or Launch action, RichMedia,
  movie, sound, or screen annotation.

The PDF has no structure tree or marked-content catalog flag and is therefore
correctly reported as **untagged**, not falsely described as fully accessible.
This checkpoint supplies working navigation and Unicode text extraction, but
the goal's final semantic accessible-reader surface remains a separate
full-corpus deliverable.
