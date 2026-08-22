# Chapter 10 cumulative PDF visual and accessibility audit

Date: 2026-08-22  
Artifact: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf`  
Decision: **zero visual/render/navigation defects; semantic accessibility blocker remains**

## Exact audit target

- PDF: 1,796,056 bytes / 153 US-Letter pages / SHA-256
  `1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc`.
- Two fully cleaned replays in the same fixed output directory, with
  `SOURCE_DATE_EPOCH=1444126743`, produced byte-identical PDFs. A comparison
  build in a different directory differed only in the generated trailer ID and
  is not used as the determinism claim.
- The final 52,286-byte TeX log has SHA-256
  `993caf6e1602de89155464ba9f3f2d735e6db1f14b4a242f6ddbe31f2f65fef3`.
  It contains zero TeX/package errors, unresolved references or citations,
  rerun notices, multiply defined labels, overfull boxes, vbox warnings, or
  missing characters. Four inherited underfull hboxes occur in long authority
  URL/hash material and do not omit or overlap content. The 108 inherited
  small-caps-italic substitutions use the available small-caps-slanted Latin
  Modern shape. Two nonblocking `hyperref` notices remove the math shifts from
  the section-title bookmark `Ruang-$LF$`; the resulting bookmark is correctly
  `10.2. Ruang-LF`.
- BibTeX uses 36 entries with zero warnings. MakeIndex accepts all 1,524
  entries, rejects zero, makes 17,626 comparisons, writes 1,858 lines, and
  reports zero warnings.
- `pdfinfo` reports 612 by 792 point pages, no encryption, and fixed
  creation/modification metadata. The five Chapter-10 audit entry points bind
  the exact target:
  - `qa/audit_ch10_pdf.py`: 804 bytes / SHA-256
    `06bc2ac9ea7d3341d604baf282b50ee01a30dff925a97437ae4c6e13350ddd95`;
  - `qa/audit_ch10_render.py`: 799 bytes / SHA-256
    `7189b88bdd3af0ea40d01d506c0735a2abe29e794ef1f0c7f5027b63811636bf`;
  - `qa/audit_ch10_bbox.py`: 656 bytes / SHA-256
    `3b0d032f33a05ebdf17a42e91763015a650f744f4f50b06507ec2c7a8e0ae210`;
  - `qa/audit_ch10_text_fonts.py`: 869 bytes / SHA-256
    `5e3837a51836a2ca2b4f468395e6932dc331d7d9eb6b84fbe780b36edfd50864`;
  - `qa/make_ch10_public_evidence.py`: 2,227 bytes / SHA-256
    `4951f8d95fe261e0122674995c7f6da45020b8f28c96becd627c31fd81039776`.

## Complete render closure

The frozen PDF was rendered with `pdftoppm -png -r 150 -cropbox`. The render
contains exactly ordered physical pages 1--153. All 153 PNGs are 1,275 by
1,650 pixels and total 54,129,667 bytes. Manifest replay finds no missing,
extra, duplicate, dimension-mismatched, or hash-mismatched page and no ink in
the outer five raster pixels.

The blank-page candidates are physical pages 20, 48, 78, 100, 114, 136, and
138. Each has zero ink and no word box. They are intentional blank versos at
chapter or back-matter transitions; pages 136 and 138 respectively separate
Chapter 10 from the bibliography and the bibliography from the index.

The private JSON manifest is 81,361 bytes / SHA-256
`b74798a07bcc525c71cf0f6955edcbe186d45c748a48283b6d4d5be4a81c58d3`.
The private CSV and exact public copy are each 29,798 bytes / SHA-256
`b1dd863b6b2441e0a49bf9fe3248b759c9889f0a74654fbe060d868f60cfb7ca`;
the public copy is `provenance/CH10_RENDER_MANIFEST.csv`.

Thirteen detailed 3-by-4 contact sheets cover consecutive pages 1--153 and
total 9,700,220 bytes. The deterministic compact public all-page sheet is
`provenance/CH10_CONTACT_SHEET.png`, 4,463,573 bytes / SHA-256
`e5b14686ad4ce088d02ba819e3df14621936dd888b429b92a9506e53ce9d34f6`.

## Visual inspection

Every physical page was inspected through the thirteen detailed consecutive
contact sheets. Physical pages 124--139 were then inspected again at full
resolution. This second pass covers the Chapter 9 close, the centered Chapter
10 opener, all six Chapter 10 sections, every exercise/hint/citation-only proof
surface, the inductive-limit diagram, distributions, convolution,
distributional ODE solutions, tempered distributions, Fourier transforms, the
chapter close, both intentional blank versos, the bibliography, and the index
opener. All other blank candidates were also confirmed on their consecutive
all-page sheets.

Inline and displayed arrows, category diagrams, integrals, multi-indices,
derivatives, distributions, convolution products, Fourier symbols, Greek
letters, fractions, subscripts, superscripts, citation links, and
cross-references render sharply. Running headers and printed page numbers are
correct, chapter and section headings are centered consistently, facing-page
margins are balanced, and intentionally sparse end-of-chapter pages retain
ordinary whitespace rather than truncated content.

No clipping, overlap, missing or damaged glyph, unreadable formula, broken
diagram, header/footer defect, unexpected blank, off-center body block, edge
collision, or margin violation was found anywhere in the 153-page reader.

Poppler bounding-box extraction contains 72,104 word boxes and zero boxes
outside page bounds. Minimum clearances are 72.000 points left, 71.254988
right, 49.278601 top, and 37.803801 bottom. The seven zero-word pages are
exactly the intentional blank versos above. The bbox witness is 8,567,940
bytes / SHA-256
`efafcfa07efc6feed787213c98bfd9666155f80b625be0ea70f2923bc710966a`
and has zero replacement decode characters.

## Navigation, links, and executable-surface audit

The catalog language is `id-ID`. The reader contains 64 outline entries,
1,516 named destinations, and 2,005 internal `GoTo` links; every internal link
resolves. There are 2,013 `/Link` annotations in total. Eight URI annotations
point to six unique external targets: the two official Erdman source surfaces,
CC BY-SA 4.0, the Erdman DOI, and two inherited informational HTTP links. No
URI or extracted text exposes a local filesystem path.

The PDF is unencrypted and contains no AcroForm, widget, JavaScript, launch
action, embedded file, file attachment, rich media, or executable action. Its
document open action is an internal `GoTo` view.

## Text, fonts, and honest accessibility boundary

All 45 font resources are embedded subsets and report Unicode maps. The exact
font inventory is 4,418 bytes / SHA-256
`e51075591255f54d371cda4e16c4293033bdb835daefacd9c1d9e7804b41f880`.
Layout-preserving text extraction is 584,818 bytes / SHA-256
`7d33802d1a3cd9d9249facbde20ad719ac1342fbbd08d9b3588f20a82c1595c9`.
Its 153 form-feed boundaries cover the complete physical-page sequence, with
zero replacement characters, mojibake signatures, or local-path hits. The
`pdfinfo` witness is 918 bytes / SHA-256
`e912e68bf2e5f36f9ce261a6ee19cc970c487489f6d799b0efce5dd8a8998ec5`.

The semantic accessibility blocker remains explicit: `pdfinfo` reports
`Tagged: no`, and the catalog has no structure tree, `MarkInfo`, or XMP
metadata stream. The PDF therefore provides no semantic heading/list/equation/
index roles, alternative-text framework, or guaranteed assistive-technology
reading order. It is a visually sound, searchable, navigable reader with
strong Unicode extraction, not the final accessible edition. Semantic HTML
and/or a later tagged-PDF derivative remains an edition-level requirement.
