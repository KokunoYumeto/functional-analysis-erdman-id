# Chapter 9 cumulative PDF visual and accessibility audit

Date: 2026-08-22  
Artifact: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf`  
Decision: **zero visual/render/navigation defects; semantic accessibility blocker remains**

## Exact audit target

- PDF: 1,686,477 bytes / 140 US-Letter pages / SHA-256
  `99215ff5987f720600152da902cec8f521329692931a0dbf89e82ef2d4ff6076`.
- Two clean fixed-path builds with `SOURCE_DATE_EPOCH=1444126743` produced
  byte-identical PDFs. The final 51,189-byte log has SHA-256
  `c914d345ca65037ae1b1290dd483993536cd6ce7b08986dd3ae7c17b302ea06f`
  and contains zero TeX/package errors, unresolved references or citations,
  rerun notices, multiply defined labels, overfull boxes, vbox warnings, or
  missing characters. Four inherited underfull hboxes occur in long authority
  URL/hash material and do not omit or overlap content.
- `pdfinfo` reports 612 by 792 point pages, no encryption, and fixed
  creation/modification metadata. The five Chapter-9-specific audit entry
  points bind the frozen target: `qa/audit_ch09_pdf.py` (801 bytes / SHA-256
  `43201c6904577ef88653ae78f3e4e112e2b618530f5f7397098e85f8c987533f`),
  `qa/audit_ch09_render.py` (797 bytes / SHA-256
  `51b972eea852e35f3a86246fe3cbdcd9f7bcc854790253087a51cdb3438abec4`),
  `qa/audit_ch09_bbox.py` (654 bytes / SHA-256
  `de54fbb6b09cc038fa20e75c9954f2e61b843466dcb4da669e9c21663898e12a`),
  `qa/audit_ch09_text_fonts.py` (867 bytes / SHA-256
  `6b9fc24cb2737c42aa55f51d03c773e517d04beac3a87d9ee4338f8af4dce42b`),
  and `qa/make_ch09_public_evidence.py` (2,226 bytes / SHA-256
  `155598a0a08cc257058e1be28b66ba4cbd535d1a987d44b994c6848aa109971d`).

## Complete render closure

The frozen PDF was rendered with `pdftoppm -png -r 150 -cropbox`. The render
contains exactly ordered physical pages 1--140. All 140 PNGs are 1,275 by
1,650 pixels and total 49,729,623 bytes. Manifest replay finds no missing,
extra, duplicate, dimension-mismatched, or hash-mismatched page and no ink in
the outer five raster pixels.

The only blank-page candidates are physical pages 20, 48, 78, 100, 114, and
126. Each has zero ink and no ink bounding box. They are intentional blank
versos at chapter or back-matter transitions; page 126 separates the
bibliography from the index.

The private JSON manifest is 74,570 bytes / SHA-256
`74aed113925e9bdb5c889db381818c3650fc1e560084dbb3886f8d7d96c220db`.
The private CSV and exact public copy are each 27,298 bytes / SHA-256
`add426dfd81f96fb8adc838d8173436d64ea3b2a165cdc1ff4a732c2a0f6fb2d`;
the public copy is `provenance/CH09_RENDER_MANIFEST.csv`.

Twelve detailed 3-by-4 contact sheets cover consecutive pages 1--140 and total
8,924,999 bytes. The deterministic compact public all-page sheet is
`provenance/CH09_CONTACT_SHEET.png`, 4,114,399 bytes / SHA-256
`09b3bc4d70cc83d99cd376245c578e4c72fff6995e3392810e2d55e0302986dd`.
Running the public-evidence generator twice reproduced both public artifacts
byte-identically.

## Visual inspection

Every physical page was inspected through the twelve detailed consecutive
contact sheets; the compact public all-page sheet was also inspected. Every
Chapter 9 and transition page, physical pages 115--126 (printed pages
111--121 plus the blank verso), received a second full-size inspection.

The full-size span covers the centered Chapter 9 opener; balanced and absorbing
sets; filters; compatible topologies; quotient spaces; locally convex spaces
and seminorms; Fréchet and Schwartz spaces; the single exercise; every proof
hint and citation-only proof; the intentionally sparse final chapter page; the
bibliography; and its blank verso. Physical pages 127--140 were inspected as
the complete index tail on the detailed sheets.

Inline and displayed arrows, closures, set-family symbols, Greek letters,
multi-indices, derivatives, supremum/max formulas, fractions, subscripts,
superscripts, citation links, and cross-references render sharply. The two
prose lines polished after the first build now fit without overfull boxes.
Running headers and printed page numbers are correct, chapter and section
headings are consistently centered, facing-page margins are balanced, and the
sparse final chapter page uses ordinary end-of-component whitespace rather
than a truncated body.

No clipping, overlap, missing or damaged glyph, unreadable formula, broken
diagram, header/footer defect, unexpected blank, off-center body block, edge
collision, or margin violation was found anywhere in the 140-page reader.

Poppler bounding-box extraction contains 66,270 word boxes and zero boxes
outside page bounds. Minimum clearances are 72.000 points left, 71.254988
right, 49.278601 top, and 37.803801 bottom. The six zero-word pages are exactly
the intentional zero-ink versos above. The bbox witness is 7,860,980 bytes /
SHA-256
`c29b3cbf9750da03826f264914295bb5cea8592585f304c3a21011cea3aae586`
and has zero replacement decode characters.

## Navigation, links, and executable-surface audit

The catalog language is `id-ID`. The reader contains 57 outline entries,
1,387 named destinations, and 1,831 internal `GoTo` links; every internal link
resolves. There are 1,839 `/Link` annotations in total. Eight URI annotations
point to six unique external targets: the two official Erdman source surfaces,
CC BY-SA 4.0, the Erdman DOI, and two inherited informational HTTP links. No
URI or extracted text exposes a local filesystem path.

The PDF is unencrypted and contains no AcroForm, widget, JavaScript, launch
action, embedded file, file attachment, rich media, or executable action. The
sole document open action is an internal `GoTo` view.

## Text, fonts, and honest accessibility boundary

All 45 font resources are embedded subsets and report Unicode maps. The exact
font inventory is 4,418 bytes / SHA-256
`a8b0dd9abdb64507b05ce643c354a40eccd60a3334cd875f3626f09d1cab816d`.
Layout-preserving text extraction is 531,953 bytes / SHA-256
`73c6f363443b3349b8361684bc15a26751120f33c0d6d95ab4b64a52017736ef`.
Its 140 form-feed boundaries cover the complete physical-page sequence, with
zero replacement characters, mojibake signatures, or local-path hits. The
`pdfinfo` witness is 863 bytes / SHA-256
`644b45df745d47ed0697cd863d0fc0d2055b008518130983751dfe55bb11cc95`.

The semantic accessibility blocker remains explicit: `pdfinfo` reports
`Tagged: no`, and the catalog has no structure tree, `MarkInfo`, or XMP
metadata stream. The PDF therefore provides no semantic heading/list/equation/
index roles, alternative-text framework, or guaranteed assistive-technology
reading order. It is a visually sound, searchable, navigable reader with
strong Unicode extraction, not a fully accessible edition. Semantic HTML
and/or a later tagged-PDF derivative with explicit mathematical semantics
remains an edition-level requirement.
