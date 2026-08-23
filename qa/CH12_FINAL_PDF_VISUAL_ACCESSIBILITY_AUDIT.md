# Chapter 12 cumulative PDF technical, navigation, and accessibility audit

Date: 2026-08-23  
Unit: FAOA-2015-CH12 / cumulative Indonesian reader through Chapter 12  
Decision: **no technical release blocker; semantic tagging remains a nonblocking
edition-level accessibility follow-up**

This is an independent, read-only audit of the final PDF object structure and
build diagnostics. The main production agent separately inspected the complete
all-page contact sheets and the relevant full-resolution page renders. This
audit does not substitute text extraction for that visual review.

## Exact target

- Build witness:
  `qa/build-through-ch12-final/functional-analysis-id-through-ch12.pdf`.
- 2,001,449 bytes; 179 pages; SHA-256
  `476b1f1fd6ca82deddeeb9edac1b07286567ede5663a6df32906a36dd3ea5ab6`.
- Every page is unrotated US Letter, 612 x 792 points. PDF version 1.5;
  unencrypted; no linearization.
- Title: *Analisis Fungsional dan Aljabar Operator: Suatu Pengantar*.
  Author: John M Erdman. Creator: `OpenAI Codex gpt-5.6-sol, Ultra`.
  Producer: `MiKTeX pdfTeX-1.40.29`. Creation and modification dates are both
  fixed at `2026-08-23 00:00:00 +02:00`.
- The catalog language is `id-ID`, the document-title display preference is
  enabled, and the initial viewer mode is `/UseOutlines`.

## Navigation and links

- The outline has 77 readable entries at two levels: 12 chapter entries, 63
  section entries, Bibliografi, and Indeks. All 77 destinations resolve; the
  outline contains zero U+FFFD replacement characters and zero NULs.
- There are 1,830 named destinations and 179 unique logical page labels. All
  2,287 annotation-level `/GoTo` actions resolve to existing named
  destinations. The catalog `/OpenAction` is one valid in-document `/GoTo`.
- The PDF has 2,295 annotations, all `/Link`: 2,287 internal links and eight
  `/URI` instances representing six unique HTTP(S) targets. Across all 5,483
  readable xref objects, the only action types are 2,365 `/GoTo`
  actions (links, outlines, and the opening destination) and eight `/URI`
  actions. There are no unresolved destinations or unsafe action types.

## Fonts, extraction, and accessibility boundary

- `pdffonts` and an independent object traversal agree on 45 Type 1 font
  objects. Every font is embedded and subsetted, and all 45 have a `/ToUnicode`
  map; zero font objects lack one.
- Poppler `pdftotext -enc UTF-8` exited zero with empty stderr and returned 179
  page segments, 545,326 UTF-8 bytes, 484,907 Unicode characters, and 391,590
  non-whitespace characters. It contains zero U+FFFD replacement characters,
  zero NULs, and zero local-file-path signatures.
- The PDF is honestly untagged: `pdfinfo` reports `Tagged: no`, and the catalog
  has neither `/StructTreeRoot` nor `/MarkInfo`. It therefore is not claimed as
  a standalone semantically accessible PDF. This is nonblocking for the
  Chapter 12 checkpoint; the planned semantic HTML/reader surface and possible
  tagged-PDF derivative remain required at the complete-edition boundary.

## Security and hidden-surface checks

All 5,483 xref objects opened without error. A traversal of 17,525 direct PDF
strings found no Windows drive path, `file://` URI, `/Users/` path, or equivalent
local-path disclosure. There is no encryption, AcroForm, XFA, field, widget,
attachment, embedded-file name tree, embedded-file stream, JavaScript name
tree, JavaScript action, launch action, remote-GoTo action, submit/import/reset
action, page or annotation additional action, rich media, movie, or sound.
`pdfdetach -list` independently reports zero embedded files.

## Intentional blank pages

Poppler and pypdf independently identify exactly eight text-empty pages: 20,
48, 78, 100, 114, 136, 146, and 160. Each has a 32-byte decoded content stream
containing only repeated nonpainting color-state operators (`0 g 0 G`). They
are intentional blank versos immediately before Chapters 2, 4, 6, 7, 9, 11,
12, and the bibliography respectively. The main agent's render inspection
confirmed these blanks and found no unexpected blank page.

## Final build diagnostics

The final TeX log is 58,542 bytes, SHA-256
`fa99ee3c6d778dc92b70ba9b0ab946e3aad4bf1b27f2aa481999d130efd19b34`.
It contains zero TeX/package errors, fatal or emergency stops, missing
characters, unresolved references or citations, rerun-required messages, or
multiply defined labels. BibTeX reports zero warnings; MakeIndex generated
2,050 index lines with zero warnings.

The bounded nonblocking diagnostics are:

- two inherited Chapter 11 overfull hboxes, 7.30707 pt and 11.09703 pt;
- four underfull hboxes in the front-matter source-URL/hash paragraph;
- one underfull vbox on the bibliography transition;
- 129 substitutions of unavailable small-caps italic with small-caps slanted;
- 13 hyperref PDF-string warnings (ten removed math shifts and three removed
  superscripts). All outline titles remain readable and resolve correctly; and
- a Perl locale fallback warning in the replay console wrappers. Both replay
  transcripts nevertheless finish with the 179-page, 2,001,449-byte target
  and `All targets ... are up-to-date`.

The main agent visually inspected the pages implicated by these diagnostics at
full resolution as part of the separate render gate. The independent technical
audit found no blocker.
