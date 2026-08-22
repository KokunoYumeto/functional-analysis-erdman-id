# Chapter 8 cumulative PDF visual and accessibility audit

Date: 2026-08-22  
Artifact: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-8.pdf`  
Decision: **zero visual/render/navigation defects; semantic accessibility blocker remains**

## Exact audit target

- PDF: 1,593,249 bytes / 129 US-Letter pages / SHA-256
  `fb6488691e2127bc0b8e3f94f38033eb3bdbe0c61efedc66c07de8f3b3444fbd`.
- `pdfinfo` reports PDF 1.5, 612 by 792 point pages, zero rotation, no
  encryption, no form, no JavaScript, and fixed creation/modification times of
  2026-08-22 00:00:00 +02:00.
- The five Chapter-8-specific audit entry points verify or bind the frozen
  target: `qa/audit_ch08_pdf.py` (939 bytes / SHA-256
  `ea4ea9008145ef5447ae271d50b5e1a9e4ba3aa79db15976326c0ea0c55e8bbb`),
  `qa/audit_ch08_render.py` (7,709 bytes / SHA-256
  `d289348593ff6767838f939eaad78fb1a05217012b99a1549a7c0c53012b6980`),
  `qa/audit_ch08_bbox.py` (3,293 bytes / SHA-256
  `71ead82b25e0fe5aee98cd0732ee4b28d67de9031dfd1cc4bbfc63108bc0c490`),
  `qa/audit_ch08_text_fonts.py` (4,708 bytes / SHA-256
  `22ab549191f7ff10ccc1e482831080d202bc19219048f5198959baa8bf0a8e8e`),
  and `qa/make_ch08_public_evidence.py` (2,226 bytes / SHA-256
  `4a622692f067ee6a0eafc1a7d8eafbb0c07b5dbcd3884a3287c0b0f69e3b983c`).

## Complete render closure

The existing frozen Poppler render was reused; no rerender was necessary. It
contains exactly the ordered sequence `page-001.png` through `page-129.png`,
produced with `pdftoppm -png -r 150 -cropbox`. All 129 page images are 1,275 by
1,650 pixels and total 45,549,537 bytes. Every manifest record was independently
checked against the corresponding PNG's byte count, SHA-256, dimensions, ink
count, ink bounding box, margins, and outer-edge ink count, with zero
discrepancies. No page has ink in the outer five raster pixels.

The only blank-page candidates are physical pages 20, 48, 78, 100, 114, and
116. Each has zero ink pixels and no ink bounding box. They are intentional
blank versos between book components: Chapters 1/2, 3/4, 5/6, 6/7, Chapter 8
and the bibliography, and the bibliography and index, respectively.

The private JSON manifest is 68,659 bytes / SHA-256
`080a5cf78300472a940f95fe99be499040046f327169543dafc68588a3fb9ef1`.
The private CSV and exact public copy are each 25,114 bytes / SHA-256
`796f36332ef748a4b1a7d8f01b7d75c7ec9da5236640f059d31df14fa3ec3e71`;
their bytes are identical. The public copy is
`provenance/CH08_RENDER_MANIFEST.csv`.

Eleven detailed 3-by-4 contact sheets cover consecutive physical pages 1--129
and total 8,191,934 bytes. Their filenames, page ranges, byte counts, and
SHA-256 identities are bound in the private JSON manifest. Each decoded sheet
was independently reconstructed from the 129 source PNGs and matched pixel for
pixel. The complete compact sheet,
`provenance/CH08_CONTACT_SHEET.png`, is 1,876 by 4,330 pixels, 3,781,079 bytes,
and has SHA-256
`5d53f2c381f8108dd3a947e2ad85c744c21f2070c6397611b525af978690b6cf`;
it also matches an independent pixel reconstruction exactly.

## Visual inspection

Every physical page was inspected through the eleven detailed contact sheets;
the compact public all-page sheet was also inspected. Full-size 1,275-by-1,650
renders of every Chapter 8 page, physical pages 107--113 (printed pages
103--109), received a second inspection.

The full-size span includes the Chapter 8 opener, all of section 8.1 on the
spectrum, the section 8.2 transition and Hilbert-space operator spectrum, and
the final chapter page. The long inline resolvent hint on physical page 109
wraps within the text block and remains complete and legible. Spectral-radius
limits, inverse and adjoint notation, matrices, overbars, subscripts,
superscripts, Greek letters, set inclusions, numbered cross-references, and the
end-of-proof square render sharply. The Chapter 8 opener and section heading
are centered consistently, running headers and printed page numbers are
correct, and the intentionally sparse final chapter page retains balanced
whitespace.

No clipping, overlap, damaged or missing glyph, unreadable formula, broken
diagram, header/footer defect, unexpected blank, off-center body block, edge
collision, or margin violation was found anywhere in the 129-page reader.

Poppler bounding-box extraction contains 61,064 word boxes across all 129
pages and zero boxes outside the 612-by-792-point page bounds. Minimum
clearances are 72.000 points left, 71.254988 right, 49.278601 top, and
37.803801 bottom. The zero-word pages are exactly the six zero-ink versos
above. The bbox witness is 7,250,084 bytes / SHA-256
`a8a283e00b28523d60ecfcef4073e9b238aba260b1323f6c109fcf2baf13c3fb`
and contains zero replacement decode characters.

## Navigation, links, and executable-surface audit

The catalog language is `id-ID`. The reader contains 50 outline entries, 1,241
named destinations, and 1,718 internal `GoTo` links; every internal link
resolves. There are 1,726 `/Link` annotations in total. Eight URI annotations
point to six unique external targets: the two official Erdman source surfaces,
CC BY-SA 4.0, the Erdman DOI, and two inherited informational HTTP links. No
URI or extracted text exposes a local filesystem path.

The PDF is unencrypted and contains no AcroForm, widget, JavaScript, launch
action, embedded file, file attachment, rich media, movie, sound, screen
annotation, or executable action. The sole document open action is an internal
`GoTo` view.

## Text, fonts, and honest accessibility boundary

All 43 font resources are embedded subsets and report Unicode maps. The exact
font inventory is 4,230 bytes / SHA-256
`49f2e03e766e232568953cda284eeabbc9b31504221487b34f16767039a9839d`.
Layout-preserving Poppler text extraction is 491,578 bytes / SHA-256
`ee477d952cb150428f39dba08acdff3ce43820f63dd462fcf5d8eb3136c7817e`.
Its 129 form-feed boundaries cover the complete physical-page sequence, with
zero replacement characters, mojibake signatures, or local path hits. The
`pdfinfo` witness is 824 bytes / SHA-256
`744d884812d23165de09bce140ef87cbe682e3f31b244d9c5a4a70faa6febafb`.

The semantic accessibility blocker is explicit: `pdfinfo` reports
`Tagged: no`, and the catalog has no structure tree, `MarkInfo`, or XMP
metadata stream. It therefore provides no semantic heading/list/equation/index
roles, alternative-text framework, or guaranteed assistive-technology reading
order. This is a visually sound, searchable, and navigable reader with strong
Unicode text extraction, but it is not a fully accessible PDF. Accessible
semantic HTML and/or a later tagged-PDF derivative with explicit mathematical
semantics remains an edition-level requirement.
