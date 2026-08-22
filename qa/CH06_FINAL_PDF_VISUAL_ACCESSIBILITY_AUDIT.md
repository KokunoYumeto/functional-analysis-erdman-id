# Chapter 6 cumulative PDF visual and accessibility audit

Date: 2026-08-22  
Artifact: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-6.pdf`  
Decision: **visual/render/navigation pass; semantic accessibility remediation remains required**

## Exact artifact and deterministic build

- PDF: 1,468,946 bytes / 114 US-Letter pages / SHA-256
  `93cfdf76515205ca259c91537a58cfa2b0ae7cab67e4b1b818ac9f5784aaa55c`.
- Two independently cleaned builds in the same fixed output directory with
  `SOURCE_DATE_EPOCH=1444126743` produced byte-identical PDFs.
- Cumulative master: 9,660 bytes / SHA-256
  `92ab981f81488472f2c45271727b6652bfa62227533107725bff08f4416e738a`.
- Final build log: 46,285 bytes / SHA-256
  `d3f234b73aa71121a463b752dd68fa558309ad2056df31d956c2e060814bfeef`.
- Final log findings: zero TeX errors, unresolved references or citations,
  rerun-required warnings, multiply defined labels, overfull boxes, underfull
  vboxes, or missing characters. Four front-matter underfull hboxes arise from
  the long authority URLs and source hashes. Seventy-seven legacy
  small-caps-italic substitutions are reader-content neutral.
- BibTeX used 25 entries and emitted zero warnings. MakeIndex accepted all
  1,168 entries, rejected zero, wrote 1,445 lines, and emitted zero warnings.

The wrapper fixes derivative `/CreationDate` and `/ModDate` at
2026-08-22 00:00:00 +02:00 and retains the single `#005A9C` link color, whose
contrast against white is 7.137:1. The frozen upstream bibliography remains
unchanged; the derivative's documented `Erdman:2010` link repair uses DOI
`10.1142/11896` without altering the cited year.

## Complete render closure

All 114 physical pages were freshly rendered from the final reviewed PDF at
150 dpi. The PNG set contains exactly 114 files / 40,224,010 aggregate bytes,
all 1,275 by 1,650 pixels. No page has ink in the outer five raster pixels. The
exact public manifest is `provenance/CH06_RENDER_MANIFEST.csv`, 22,218 bytes /
SHA-256
`ba63bc106be574414792ac6bc37b76483a01491822fca4745962e8ff9e407db8`.
Manifest generation found the exact page sequence 1--114 with no missing,
extra, duplicate, dimension-mismatched, or unbound page.

The complete all-page public contact sheet is
`provenance/CH06_CONTACT_SHEET.png`, 3,339,772 bytes / SHA-256
`1b5aaad85c2c13651c51d92d6452eb21fca892b641abe87c3991e95bc4f1bedf`.
Ten higher-resolution local contact sheets cover consecutive twelve-page
windows. The complete public sheet, all ten detailed sheets, and full-size
physical pages 1, 2, 79, 83, 85, 88, 90, 95, 98, 99, 103, and 114 were
inspected after the final independent rereview and rebuild. These cover the
cover, attribution and rights, the Chapter 6 opening, every accepted prose
polish, dense formulas, commutative diagrams, the intentionally sparse chapter
ending, bibliography, and the first and last index pages. No clipping,
overlap, off-center body block, damaged glyph, unreadable formula, broken page
header, or margin violation was found. The reader uses the available width
consistently.

Poppler bounding-box extraction contains 54,378 word boxes across 114 pages
and zero boxes outside the 612-by-792-point media bounds. Minimum clearances
are 72.000 points left, 71.255 right, 49.279 top, and 37.804 bottom. The five
zero-word pages are exactly the intentional blank versos 20, 48, 78, 100, and
102. The private bounding-box witness is 6,456,899 bytes / SHA-256
`737cd4af70d39aec8f654afe3f7fc8c301d2d49ae561894560b5c5705ffc87d0`.

## Navigation, link, and safety audit

The bounded entry point is `qa/audit_ch06_pdf.py`, 173 bytes / SHA-256
`0a0202265983431cc94a6775c21f75f84c6648fe342e4f08affe166a70ca73d5`;
it invokes the already admitted shared auditor. It reports:

- catalog language `id-ID`, 42 outline entries, and 1,052 named destinations;
- 1,500 internal `GoTo` links, all resolved, plus eight URI annotations over
  six unique external targets;
- no encryption, form, widget, JavaScript, launch action, embedded file, file
  attachment, rich media, or executable action;
- the sole open action is an internal `GoTo` view.

The exact source authority URLs, CC BY-SA 4.0 license link, repaired DOI, and
two inherited informational HTTP links account for the six URI targets. The
PDF contains no local filesystem path.

## Honest accessibility boundary

All 43 font resources report Unicode maps. Layout-preserving Poppler text
extraction is 436,932 bytes / SHA-256
`d9fa66b1ec42ede6ab4247f81eb70361c274922cb5d3eeaacf0616fc30235c4c`.
It contains zero replacement characters, mojibake signature, or local path;
its 114 form-feed boundaries cover the complete physical-page sequence.

`pdfinfo` still reports `Tagged: no`; the catalog has no structure tree,
semantic heading/list/equation/index roles, alternative-text framework, XMP
stream, or guaranteed screen-reader reading order. The PDF is therefore a
visually usable, searchable, navigable reader with strong text extraction, not
a fully accessible edition. Semantic HTML and/or a later tagged-PDF derivative
with explicit mathematical and diagram accessibility remains an edition-level
deliverable and is nonblocking only for this chapter-boundary publication.
