# FAOA-2015-CH05 build and QA receipt

Date: 2026-08-22  
Decision: **admitted**  
Course role: `D20_core`

This receipt admits the complete Indonesian Chapter 5, *Operator pada Ruang
Hilbert*, and the cumulative Chapter 1--5 reader. Translation, mathematics,
structure, build, visual, navigation, component-rights, privacy, and
append-only backend gates pass. It does not claim that Chapters 6--17, the
semantic HTML reader, the O001 solved mastery layer, or the original
compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Source: `source/upstream/Hilbert_space_operators.tex`, 48,838 bytes / 1,147
  CRLF-terminated lines / SHA-256
  `93293a89c9a9f34315a43d6f114084490ceb370119fb09aeaccabe634efb96b1`.
- Target: `source/id-ID/Hilbert_space_operators-id.tex`, 51,529 bytes / 1,147
  LF lines / SHA-256
  `323f0b156eb6e945e3b6ed273da298af4e0e2b2d9abb73514a9018cbe0d0b29f`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch05.tex`, 9,630 bytes / 330
  LF lines / SHA-256
  `2b8987e70b08b7b7045b50569667e0ab06634767645401a8c1d95712c48d80e2`.
- Derivative bibliography: `source/id-ID/functional_analysis_op_algs_bib.bib`,
  17,409 bytes / SHA-256
  `72b33be29e0728654e4b623e454639927046f425fb81e5b13b8c05e1888fd6fa`.
- The admitted Chapter 1--4 targets and their backend byte prefixes are
  unchanged.

## Structural, mathematical, and language replay

The locked source/target checker preserves the complete ordered topology:
seven sections, 152 balanced environment pairs, four exercises, 17 explicit
proof-hint blocks, 39 labels, 24 ordinary references, one equation reference,
one citation, 168 index hooks, 56 defined-term hooks, and 827 text-aware
mathematical surfaces. The backend derives 138 semantic anchors: the chapter,
seven sections, and 130 source semantic-environment anchors.

Of the 24 ordinary references, 13 resolve within Chapter 5, 10 resolve to
admitted prior units, and one points forward to `chap_cpt_ops`; the partial
reader renders that last reference honestly as a future reference while
retaining its exact source label. The equation reference is local. All label,
reference, citation, index, defined-term, exercise, and hint sequences retain
their source order.

The mathematical projection contains 827 one-to-one, same-ordinal mappings:
816 normalized-exact surfaces, five reviewed language-bearing math-text
localizations with equal translation-neutral keys, and six reviewed source
corrections. There is no unexplained insertion, deletion, reorder, or formula
delta. The final checker is `qa/check_ch05_translation.py`, 15,162 bytes /
SHA-256
`c04266c3924d7336cec886b687da99db25c4403b8f030ee8fd47e47f2b838e2`.
Repeated runs return `pass`, with zero visible English residue and no
structural error.

Twenty-three bounded corrections are applied and individually recorded. They
cover malformed or underspecified mathematical scopes, notation and
punctuation defects, index spelling, and one dead bibliography link. The
derivative bibliography replaces the dead `Erdman:2010` ELMA URL with
`https://doi.org/10.1142/11896` while retaining the source citation year; the
frozen upstream bibliography is unchanged. The append-only cumulative ledger
is `provenance/SOURCE_CORRECTIONS.md`, 16,450 bytes / SHA-256
`2408e045efb307602fbe8540efcb6307944d01d7ace610d78e4341856a0e35b7`.
Its first 11,058 bytes remain exactly the admitted Chapter 1--4 ledger,
SHA-256
`8909a33f5ed5dd37065fb4c3afb08e4e0659d17ef1d1a2b8f1d7f307ed1eef2d`;
the Chapter 5 suffix beginning at its heading has SHA-256
`95f76df166278c995fe031f65f1b4dc4a6740b5776f579bd8970faee9b526f79`.
No upstream contact occurs during production.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex,
  and Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two independently cleaned fixed-path replays produced byte-identical PDFs:
  1,271,325 bytes / 90 US-Letter pages / SHA-256
  `850310f11cb7ab8c83cb52347aad43bc311cc1d2a811bef476038c61c8698af0`.
- Latest final TeX log: 41,858 bytes / SHA-256
  `e026c44275a136495843ee3fa04b6e2ce4d12b75bd07612b3fad5b68a8c8d0ed`.
- Final log: zero TeX errors, unresolved references or citations,
  rerun-required warnings, multiply defined labels, overfull boxes, underfull
  vboxes, or missing characters. Four benign front-matter underfull hboxes
  arise from long authority URLs and hashes; 49 legacy small-caps-italic font
  substitutions do not alter reader content.
- BibTeX reports zero warnings. MakeIndex accepts all 1,013 entries, rejects
  zero, writes 1,264 lines, and reports zero warnings.

The canonical reader is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf`; its
build-tree copy is byte-identical. The catalog language is `id-ID`; the PDF has
34 outline entries, 861 named destinations, 1,228 resolved internal links, and
eight URI annotations over six unique external targets. It has no encryption,
form, widget, JavaScript, launch action, embedded attachment, rich media, or
executable action. Its sole open action is an internal `GoTo` view.

## Visual and accessibility evidence

All 90 pages were freshly rendered at 144 dpi. Their 90-row manifest is 8,656
bytes / SHA-256
`061bd3b31fcf2518d48fbd797fd85f19a0932fb8ae4f3b252099c7d54f9c2be2`.
Replay finds exactly 90 PNGs / 30,284,058 aggregate bytes and zero missing,
extra, duplicate, size-mismatched, or hash-mismatched pages. The all-page
contact sheet is 13,365,085 bytes / SHA-256
`5a65ee523e93e0c8bc3f34e8891ffc5a1b48547b715d94af38ad512788cf9e71`.

The complete contact sheet and full-size physical pages 65, 66, 67, 70, 73,
77, 79, 81, and 90 were inspected after the final font and link-color build.
They cover the Chapter 5 opening, dense prose and mathematics, citations,
corrected surfaces, chapter close, DOI-bearing bibliography, and index
boundaries. No clipping, overlap, off-center body block, damaged glyph,
unreadable formula, broken header, or margin violation was found. Bounding-box
replay finds 42,251 words and zero boxes outside the page bounds, with minimum
clearances of 72.000 points left, 71.255 right, 49.279 top, and 37.804 bottom.
The five blank pages are intentional versos 4, 20, 48, 78, and 80.

The independent report is
`qa/CH05_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 5,693 bytes / SHA-256
`9b0f638cd7541952bdc3e16e8c9a1ad14db9904e0fc0c5ca46565a99dfc99a03`;
the machine auditor is `qa/audit_ch05_pdf.py`, 4,765 bytes / SHA-256
`7577942fded7863dd0be76b6642ea7236085c338a025dbb6be499e4a9fb01cb3`.
The wrapper uses one link color with 7.137:1 contrast against white. Adding
`cmap` and Latin Modern leaves 38 of 40 font resources with Unicode maps; only
the two XY-pic arrow fonts remain unmapped. Extracted text has no replacement
character, mojibake signature, or local path.

The PDF remains honestly untagged: it has no structure tree, semantic
heading/list/equation/index roles, alternative-text framework, XMP stream, or
guaranteed screen-reader order. It is therefore a visually usable, searchable
reader with materially improved extraction, not a fully accessible edition.
Semantic HTML and/or a later tagged PDF with mathematical and diagram
accessibility remains an edition-level deliverable and is nonblocking only for
this chapter boundary.

## Rights and component closure

The wrapper supplies Erdman attribution, a CC BY-SA 4.0 link, a translation and
technical-change notice, ShareAlike terms, and non-endorsement. `DIAGXY.TEX`
remains byte-identical at 41,908 bytes / SHA-256
`3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb`
under Michael Barr's embedded notice. `TABLE.TEX`, badge artwork, and uncleared
quotation components are absent from the build closure. Separately authored
solutions, mastery support, and the compact-spectral/SVD bridge are not
represented as Erdman-authored content.

## Backend admission and deterministic replay

The Chapter 5 projection appends stable locale-neutral unit, semantic, segment,
formula, relation, exercise-support, index, terminology, correction, artifact,
and typed-QA records while preserving the complete admitted Chapter 1--4 byte
prefixes and IDs. It adds 137 semantic units, 158 segments, 633 relations, 827
formula maps, 168 index rows, four exercise-support records, 23 correction
records, 44 new global terminology records, nine public artifacts, and eight
typed QA events. The 56 defined-term occurrences contain 53 distinct raw source
terms, reuse eight prior IDs, and map two synonymous star-subalgebra spellings
to one new stable term ID.

The canonical validator runs the complete generator twice with byte-identical
outputs. It validates 18 ordered units, 612 semantic units, 741 segments, 2,597
relations, 4,382 formula maps, 27 exercise-support records, 1,013 index rows,
37 artifacts, 36 typed QA events, 91 corrections, and 153 terminology records,
plus exact JSON/CSV round trips, global ID uniqueness, relation endpoints,
public artifact bytes, private-control exclusion, receipt binding, and a final
backend manifest. The resulting manifest hash is recorded in durable state and
the publication handoff rather than circularly embedded in this receipt.

Chapter 5 is admitted. The whole edition remains `in_progress`, and the active
source-order cursor advances to `FAOA-2015-CH06`,
`source/upstream/Banach_spaces.tex`.
