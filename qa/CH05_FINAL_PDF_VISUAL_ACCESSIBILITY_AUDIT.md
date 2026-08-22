# Chapter 5 cumulative PDF visual and accessibility audit

Date: 2026-08-22  
Artifact: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf`  
Decision: **visual/render/navigation pass; semantic accessibility remediation remains required**

## Exact artifact and deterministic build

- PDF: 1,271,325 bytes / 90 US-Letter pages / SHA-256
  `850310f11cb7ab8c83cb52347aad43bc311cc1d2a811bef476038c61c8698af0`.
- Two independently cleaned builds in the same fixed output directory with
  `SOURCE_DATE_EPOCH=1444126743` produced byte-identical PDFs.
- Cumulative master: 9,630 bytes / 330 LF lines / SHA-256
  `2b8987e70b08b7b7045b50569667e0ab06634767645401a8c1d95712c48d80e2`.
- Final build log: 41,858 bytes / SHA-256
  `e026c44275a136495843ee3fa04b6e2ce4d12b75bd07612b3fad5b68a8c8d0ed`.
- Final log findings: zero TeX errors, unresolved references or citations,
  rerun-required warnings, multiply defined labels, overfull boxes, underfull
  vboxes, or missing characters. Four front-matter underfull hboxes arise from
  the two long official URLs and source hashes. Forty-nine legacy
  small-caps-italic substitutions remain visible-content neutral.
- BibTeX emitted zero warnings. MakeIndex accepted all 1,013 entries, rejected
  zero, wrote 1,264 lines, and emitted zero warnings.

The wrapper now fixes derivative `/CreationDate` and `/ModDate` at
2026-08-22 00:00:00 +02:00 rather than inheriting the 2015 source timestamp.
All link classes use `#005A9C`, whose independently recomputed contrast against
white is 7.137:1 (WCAG AAA for normal text). The derivative bibliography
replaces the dead `Erdman:2010` ELMA URL with DOI `10.1142/11896`; the DOI
resolver returned HTTP 302 to the registered publisher target. The source year
remains 2010 because this is a transparent link repair, not a substitution of
the later 2021 publisher edition. The frozen upstream bibliography is unchanged.

## Complete render closure

All 90 physical pages were freshly rendered at 144 dpi. The PNG set contains
90 files / 30,284,058 aggregate bytes. Its exact manifest is
`provenance/CH05_RENDER_MANIFEST.csv`, 8,656 bytes / SHA-256
`061bd3b31fcf2518d48fbd797fd85f19a0932fb8ae4f3b252099c7d54f9c2be2`.
Manifest replay finds 90 rows and 90 render files with zero missing, extra,
duplicate, byte-size-mismatched, or hash-mismatched pages.

The complete all-page contact sheet is
`provenance/CH05_CONTACT_SHEET.png`, 13,365,085 bytes / SHA-256
`5a65ee523e93e0c8bc3f34e8891ffc5a1b48547b715d94af38ad512788cf9e71`.
The Chapter 5 detail sheet is 6,759,069 bytes / SHA-256
`d6510d37e82a84f261cb86db32ebc3f250e975ffa8a3ed159161363d7894d8e1`;
the chapter-close/back-matter sheet is 4,045,888 bytes / SHA-256
`ad7e79225a28dfe523839c7ef8f6e29a7f8d09290b2b4767865e283bdc72ab40`.

The complete contact sheet and full-size physical pages 65, 66, 67, 70, 73,
77, 79, 81, and 90 were inspected after the final font and link-color build.
They cover the Chapter 5 opening, dense prose and mathematics, citations,
source corrections, chapter close, DOI-bearing bibliography, first and last
index pages, and page-backreference links. No clipping, overlap, off-center
body block, damaged glyph, unreadable formula, broken page header, or margin
violation was found. The reader uses the available width consistently.

Bounding-box extraction contains 42,251 word boxes across 90 pages and zero
boxes outside the 612-by-792-point media bounds. Minimum clearances are 72.000
points left, 71.255 right, 49.279 top, and 37.804 bottom. The five zero-word
pages are exactly intentional blank versos 4, 20, 48, 78, and 80.

## Navigation, link, and safety audit

The reproducible machine audit is `qa/audit_ch05_pdf.py`, 4,765 bytes /
SHA-256 `7577942fded7863dd0be76b6642ea7236085c338a025dbb6be499e4a9fb01cb3`.
It reports:

- catalog language `id-ID`, 34 outline entries, and 861 named destinations;
- 1,228 internal `GoTo` links, all resolved, plus eight URI annotations over
  six unique external targets;
- no encryption, forms, widgets, JavaScript, launch actions, embedded files,
  file attachments, rich media, or executable action;
- the sole open action is an internal `GoTo` view.

Five external endpoints returned HTTP 200, including both exact authority
files with their expected byte counts. The DOI resolver returned HTTP 302 to
the World Scientific record; that final site returned 403 only to the bounded
automated client. The DOI resolution itself is live and authoritative.

## Honest accessibility boundary

Adding `cmap` and Latin Modern reduced non-Unicode Type 3 fonts from 17 to the
two unavoidable XY-pic arrow fonts. Of 40 font resources, 38 now expose
Unicode maps. Layout-preserving Poppler extraction is 340,197 bytes / SHA-256
`cea3ea4f72e6a7513a49d498c7e292ce6b66cca37a22f646a28cbf1f7eed91e2`.
It contains zero replacement characters, mojibake signatures, or local paths.
Only 24 non-whitespace C0 controls remain, confined to six diagram-bearing
physical pages (36 and 60--64), instead of the pre-remediation 844 controls on
81 pages. The bounding-box witness is 4,026,417 bytes / SHA-256
`2abb4d712a35daf3878424ceb72152d1f5843e2ed1c8eed35f39c0be579efef1`.

`pdfinfo` still reports `Tagged: no`; the catalog has no structure tree,
semantic heading/list/equation/index roles, alternative-text framework, XMP
stream, or guaranteed screen-reader reading order. The PDF is therefore a
visually usable, searchable reader with materially improved extraction, not a
fully accessible edition. Semantic HTML and/or a later tagged-PDF derivative
with explicit mathematical and diagram accessibility remains an edition-level
deliverable and is nonblocking only for this chapter-boundary publication.
