# Chapter 4 final PDF, visual, and accessibility audit

Date: 2026-08-22

Scope: read-only audit of the cumulative Indonesian Chapters 1-4 PDF, its
75-page render set, render manifest, and contact sheet. No rebuild, source or
backend edit, Git operation, or publication was performed.

## Exact artifact identity

- PDF: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf`
- Bytes: 1,249,703
- SHA-256: `716e3524060f64e4728b4d3d8c1a2b906f377ec4e3b3a3cd1ef3e61759a3dd94`
- The build-tree copy at
  `qa/build-through-ch04/functional-analysis-id-through-ch04.pdf` is
  byte-identical.
- PDF version 1.5; 75 pages; every MediaBox, CropBox, BleedBox, TrimBox, and
  ArtBox is 612 x 792 points (US Letter); every rotation is zero.
- Page labels are `i` through `iv`, then `1` through `71`.

The document-information dictionary contains the Indonesian title
`Analisis Fungsional dan Aljabar Operator: Suatu Pengantar`, author
`John M Erdman`, Indonesian subject and keywords, creator
`LaTeX with hyperref`, producer `MiKTeX pdfTeX-1.40.29`, and creation and
modification timestamps `2015-10-06T10:19:03Z`. There is no XMP metadata
stream. The catalog language is `id-ID`.

## Render-manifest replay

- Manifest: `provenance/CH04_RENDER_MANIFEST.csv`
- Bytes / SHA-256: 7,134 /
  `9f8b88e46823e91920d27ade8f32af30ce347dccd0ab5d759afb2b07f0f64390`
- Exactly 75 data rows in exact page order 1-75 and exact filename order
  `page-01.png` through `page-75.png`; no duplicate filenames.
- `qa/render-through-ch04` contains exactly those 75 files: zero missing,
  extra, byte-size-mismatched, or SHA-256-mismatched files.
- Total rendered bytes: 25,021,587. Every page render is 1,224 x 1,584 RGB
  pixels.
- Contact sheet: `provenance/CH04_CONTACT_SHEET.png`, 2,535,154 bytes,
  1,098 x 4,568 RGB pixels, SHA-256
  `4712840f42f3fc988e90eeb80cdc5725ecc7db16383a339f5b98144008ecdc4d`.

## Navigation, interaction, and security

- Six top-level outline entries and 26 total outline entries correctly expose
  Chapters 1-4, all translated section headings, Bibliografi, and Indeks.
  Chapter 4 points to physical page 49; Bibliografi to 65; Indeks to 67.
- `/PageMode /UseOutlines`; the opening action is a safe `/GoTo` `/Fit`
  action, not executable content.
- 687 named destinations and 1,038 link annotations: 1,030 internal `/GoTo`
  links and 8 URI actions. All link rectangles are positive, within their page
  boxes, and all named destinations and URIs resolve structurally. No unsafe
  JavaScript, Launch, SubmitForm, or ImportData actions were found.
- No encryption, AcroForm, form fields, widget annotations, JavaScript,
  embedded files, page actions, catalog additional actions, or raster images.
  Diagrams are vector content.

## Visual inspection

The contact sheet was inspected across all 75 pages. Full-size renders were
then inspected for physical pages 49, 50, 53-56, 58-67, and 75, covering the
Chapter 4 opening, dense prose, displayed mathematics, the geometric figure,
exercises, all universal-morphism diagram pages, the Chapter 4 close,
bibliography, blank verso, and index start/end.

No clipped or overlapping prose, formulas, diagrams, page numbers, headings,
or links were found. Mathematical glyphs and vector arrows are sharp and
legible; the dense exercise and index pages preserve usable leading and
margins. Automated bounding-box replay found all 8,038 extracted word boxes on
physical pages 49-64 within the page bounds. Minimum observed distances were
72.0 pt left, 49.278601 pt top, 71.993065 pt right, and 37.803801 pt bottom.

Physical pages 4, 20, 48, and 66 are intentional blank versos. Their renders
are byte-identical: 7,944 bytes, SHA-256
`abeea15a8f407e9ba59f3f43ccc17f9a3786ef7ad701507542008a73617f96e5`.

Visual/render verdict: **PASS**, with no visual defect found in the audited
surfaces.

## Accessibility findings

Positive evidence:

- Catalog language `id-ID`, correct page labels, and complete translated
  bookmarks are present.
- All 44 unique font resources are embedded and subset. All 44 contain a
  `/ToUnicode` object, and ordinary Indonesian prose, headings, and accented
  names extract without U+FFFD replacement characters.
- The eight Chapter 4 section headings all occur correctly in extracted text.

Defects:

1. **Major - the PDF is untagged.** `pdfinfo` reports `Tagged: no`; the catalog
   has no `/StructTreeRoot` or `/MarkInfo`. Consequently, paragraphs, headings,
   lists, formulas, diagrams, and links have no semantic reading-order tree.
   The 1,038 link annotations also have no `/Contents` strings. This PDF must
   not be described as a tagged or fully accessible PDF.
2. **Material - math/diagram Unicode maps are incomplete despite the aggregate
   font report saying `uni yes`.** The XY-pic fonts
   `XYATIP-Medium` and `XYBTIP-Medium` have present but empty `/ToUnicode`
   CMaps (zero mappings). `CMEX10` has only 32 mapping records and omits used
   extensible delimiter glyphs. Poppler extraction therefore emits 96 C0
   control characters over the 75-page reader, including 47 on physical pages
   49-64. The affected Chapter 4 pages are 50-53, 58, and 60-64; diagram arrow
   tips and extensible mathematical delimiters are the principal surfaces.
   Prose extraction remains intact, but mathematical screen-reader fidelity is
   not complete.

Accessibility verdict: **FAIL for a claim of fully accessible PDF**. The PDF
is visually sound and navigable, but accessible HTML or a later tagged-PDF and
corrected math/XY Unicode layer remains necessary.
