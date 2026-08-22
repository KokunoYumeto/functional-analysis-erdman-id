# Chapter 7 cumulative PDF visual and accessibility audit

Date: 2026-08-22  
Artifact: `qa/build-through-ch07-a/functional-analysis-id-through-ch07.pdf`  
Decision: **visual/render/navigation pass; semantic accessibility remediation remains required**

## Exact audit target

- PDF: 1,530,677 bytes / 121 US-Letter pages / SHA-256
  `a7ddaef324bd356d258cb47195f524e027ba54a696cb8d38a8358bb8d0a2d7ff`.
- `pdfinfo` reports PDF 1.5, 612 by 792 point pages, zero rotation, no
  encryption, no form, no JavaScript, and fixed creation/modification times of
  2026-08-22 00:00:00 +02:00.
- The five Chapter-7-specific audit entry points verify or bind the exact target:
  `qa/audit_ch07_pdf.py` (936 bytes / SHA-256
  `fb5f426837e8e74ece8a62ef7cdea802c52613a15d53fec5b73213e269695ccf`),
  `qa/audit_ch07_render.py` (7,706 bytes / SHA-256
  `86da72b852db5409d4b8f2154c51781be767c1b0fa1d214d19e6090e253feab6`),
  `qa/audit_ch07_bbox.py` (3,290 bytes / SHA-256
  `bfdeb604accacdb8bcc74dedf4204741e0655323aa427cb95e0329242a72bc8c`),
  `qa/audit_ch07_text_fonts.py` (4,705 bytes / SHA-256
  `497457b10f1d1f485bba352c3771d1c1fd950abe3e37bb0398eed70ea49a81f7`),
  and `qa/make_ch07_public_evidence.py` (2,226 bytes / SHA-256
  `4765dbf41c056bc86b79ada2a9ff524582f1f245007cbd5ad3fa5cddec452dbc`).
  No Chapter 6 evidence file was altered.

## Complete render closure

All 121 physical pages were freshly rendered from the exact PDF with Poppler
`pdftoppm -png -r 150 -cropbox` into `qa/renders/ch07-final`. The closure is
exactly 121 PNGs / 42,779,126 aggregate bytes; every image is 1,275 by 1,650
pixels. No page has ink in the outer five raster pixels. The only blank-page
candidates are physical pages 20, 48, 78, 100, and 108. Each has zero ink
pixels and no ink bounding box, and each is an intentional blank verso between
book components.

The private JSON manifest is 64,690 bytes / SHA-256
`af7f93935b3f7105dae0178861b5bff753d6e013db4b1a08955036b0f7fee1ff`.
It binds the exact source PDF, ordered page sequence, dimensions, byte count,
SHA-256, ink bounding box, margins, edge-ink count, and blank-page decision for
every physical page. The exact public page manifest is
`provenance/CH07_RENDER_MANIFEST.csv`, 23,608 bytes / SHA-256
`b2fa453d7b96b51826aadddf2e8151144d6deae1d093dfa34841ab589ef464ed`.

Eleven detailed contact sheets cover consecutive physical pages 1--121 and
total 7,698,714 bytes. Their exact identities are bound in the private JSON
manifest. The complete public all-page sheet is
`provenance/CH07_CONTACT_SHEET.png`, 3,549,427 bytes / SHA-256
`b52f348c29cdaa1cebd87c280ac0c01fad919e72a8f595ba2c48cb78ac283564`.

## Visual inspection

Every page was inspected through the eleven detailed 3-by-4 contact sheets;
the compact all-page public sheet was also inspected. Full-size renders of
physical pages 96--107 received a second inspection. This span includes the
end of Chapter 6, its intentionally sparse final printed page and blank verso,
the Chapter 7 opener (physical 101 / printed 97), all Chapter 7 reader pages,
the long five-source polar-decomposition proof citation on physical page 104,
the trace-class formulas, the complete Hilbert--Schmidt surface on physical
page 106 / printed 102, and the bibliography transition.

The citation proof reflows across two lines without an overfull line or margin
intrusion. Hilbert--Schmidt notation, summation limits, superscripts,
calligraphic symbols, cross-reference links, and the section heading are sharp
and legible. Chapter opening and section headings are centered consistently;
the body block uses the available width with balanced raster margins (typically
148--150 pixels on each side in the reviewed Chapter 7 span). No clipping,
overlap, damaged or missing glyph, unreadable formula, broken diagram, page
header defect, unexpected blank, off-center body block, or margin violation was
found. Sparse chapter-ending and index pages retain intentional whitespace.

Poppler bounding-box extraction contains 57,431 word boxes across 121 pages
and zero boxes outside the 612-by-792-point media bounds. Minimum clearances
are 72.000 points left, 71.254988 right, 49.278601 top, and 37.803801 bottom.
The zero-word pages are exactly the five zero-ink versos above. The private
bbox witness is 6,821,610 bytes / SHA-256
`2dff8f65b0497903a6f8a8f07da291f7c039208e514787b76fb2305b7e6cfc9e`
and contains zero replacement decode characters.

## Navigation, links, and executable-surface audit

The catalog language is `id-ID`. The reader contains 47 outline entries,
1,132 named destinations, and 1,620 internal `GoTo` links; every internal link
resolves. Eight URI annotations point to six unique external targets: the two
official Erdman source surfaces, CC BY-SA 4.0, the repaired Erdman DOI, and two
inherited informational HTTP links. No URI exposes a local filesystem path.

The PDF is unencrypted and contains no AcroForm, widget, JavaScript, launch
action, embedded file, file attachment, rich media, movie, sound, screen
annotation, or executable action. The sole document open action is an internal
`GoTo` view.

## Text, fonts, and honest accessibility boundary

All 43 font resources are embedded subsets and report Unicode maps. The exact
font inventory is 4,230 bytes / SHA-256
`d13fc67651b42ecf7ac59f99a0331b9552560d520b74955a9b86dad19e4d41db`.
Layout-preserving Poppler text extraction is 463,585 bytes / SHA-256
`aad0d057d0a8bd51bc9e39ea90da922b635c590b0c3746d8c82b7181fda6d6c1`.
Its 121 form-feed boundaries cover the complete physical-page sequence, with
zero replacement characters, mojibake signatures, or local path hits.

`pdfinfo` reports `Tagged: no`; the catalog has no structure tree, marked
content declaration, XMP metadata stream, semantic heading/list/equation/index
roles, alternative-text framework, or guaranteed screen-reader reading order.
The PDF is therefore a visually usable, searchable, navigable reader with
strong text extraction, not a fully accessible edition. Accessible semantic
HTML and/or a later tagged-PDF derivative with explicit mathematical and
diagram semantics remains an edition-level requirement; this audit does not
misrepresent the current PDF as accessible.
