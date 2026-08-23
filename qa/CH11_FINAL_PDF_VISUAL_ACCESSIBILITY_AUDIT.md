# Chapter 11 cumulative PDF visual and accessibility audit

Date: 2026-08-23  
Unit: FAOA-2015-CH11 / cumulative Indonesian reader through Chapter 11  
Decision: **visual/render gate passed; semantic accessibility remains an
edition-level follow-up**

## Exact target and build replay

- PDF build witness:
  qa/build-through-ch11-a/functional-analysis-id-through-ch11.pdf
- 164 US-Letter pages (612 x 792 points), 1,873,719 bytes.
- SHA-256:
  21a3b8c8fa2f5f68cba8a9b5c1fdbbb9f1feb906090159e8a2755f54fa177971.
- Two clean replays in the same fixed directory with
  SOURCE_DATE_EPOCH=1444126743 produced byte-identical PDFs.
- The final TeX log is 55,547 bytes, SHA-256
  ad29498791ba8fa9dcc33acb6b0599c2fe2bcbf39347e5c48077db607246fc75.
  It records zero TeX/package errors, unresolved references, unresolved
  citations, rerun-required warnings, multiply-defined labels, missing
  characters, or underfull vboxes. Two bounded overfull hboxes remain in the
  Chapter 11 character-space definitions (7.31 pt and 11.10 pt); the
  implicated text was rendered and is not clipped or overlapping.
- pdfinfo reports author John M Erdman, fixed dates, and creator metadata
  OpenAI Codex gpt-5.6-sol, Ultra. The PDF is unencrypted and US Letter.

## Structural and reader-surface checks

The Chapter 11 source/target replay preserves 107 begin/end environment pairs,
38 labels, 15 references, five citation calls, 65 index hooks, and 625 math
surfaces. The cumulative build includes the single Xy-pic Gelfand-transform
triangle; its nodes and arrows remain visible on the rendered page.

The PDF surface contains 24 outline entries, 2,111 annotations, 2,005 internal
navigation actions, and six unique external URI targets. No URI, extracted
text, or action contains a local filesystem path. No JavaScript, launch action,
embedded file, rich media, AcroForm, or widget is present. Forty-five font
resources are embedded and text extraction has no replacement-character
signatures.

## Complete all-page render closure

The final PDF was rendered with Poppler pdftoppm -png -r 110 for physical
pages 1--164. The render contains exactly 164 PNGs, all 935 x 1,210 pixels,
total 41,136,062 bytes. The machine-checkable manifest is
provenance/CH11_RENDER_MANIFEST.csv (32,958 bytes; SHA-256
498d67b3260a12b8645f3d4b3021cf0222077284840f3ae644f5a24a881c979a).
The compact all-page contact sheet is
provenance/CH11_CONTACT_SHEET.png (3,255,188 bytes; SHA-256
269fc039e483b17d6e3c019c5d003df3753515f6795d5d85554747d599b074bc).

All nonblank pages have positive clear margins: at this rasterization the
minimum left/top/right/bottom margins are 109/72/93/60 pixels. Ink in the
outer five pixels is zero on every page. The only zero-ink pages are 20, 48,
78, 100, 114, 136, 146, and 148; these are intentional blank versos at
chapter, bibliography, or index transitions, confirmed on the all-page sheets.

Every page was inspected through nine consecutive contact sheets. Pages
137--145 (the complete Chapter 11 reader surface, including the diagram,
character-space definitions, Fourier material, C*-algebra section, theorem,
and final hint) were then inspected again at full resolution. No clipping,
overlap, damaged glyph, broken diagram, unexpected blank, edge collision,
header/footer defect, or unreadable formula was found.

## Accessibility boundary

The current pdfTeX artifact is a clean, navigable, Unicode-mapped but untagged
PDF. A semantic accessible HTML/reader surface and, if feasible, a tagged-PDF
derivative remain required for the complete edition. This audit does not
claim that the untagged PDF alone satisfies that requirement.

The external Indonesian terminology QA is recorded separately in
qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md; it found no justified
terminology replacement. The translation/build provenance string is
OpenAI Codex gpt-5.6-sol, Ultra; Erdman's authorship, component notices, and
human-direction credits remain intact.
