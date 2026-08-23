# FAOA-2015-CH11 build and QA receipt

Date: 2026-08-23  
Decision: **admitted**  
Course role: `advanced_continuation`

This receipt admits the complete Indonesian Chapter 11, *Teorema
Gelfand--Naimark*, and the cumulative Chapter 1--11 reader. Translation,
mathematics, source topology, references, terminology, build determinism,
visual layout, navigation, component rights, privacy, and the evidence needed
for the append-only backend operation pass. This decision does not claim that
Chapters 12--17, semantic HTML, the O001 solved-mastery layer, or the original
compact-spectral/SVD bridge are complete; the whole edition remains
`in_progress`.

## Exact source and target identity

- Frozen source: `source/upstream/Gelfand_Naimark.tex`, 32,235 bytes / 788
  CRLF records / SHA-256
  `018f15db7ee5a4392f624af050507a90339e1469e30f97c6017e003c7ff33b26`.
  Its single `\endinput` is the final nonblank source record.
- Admitted target: `source/id-ID/Gelfand_Naimark-id.tex`, 32,551 bytes / 764
  LF records / SHA-256
  `69bd9ba794ef0d5eb74e444cf2676878b7797e5dd5b75fcfc4abdd247b1b5ee5`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch11.tex`, 10,167 bytes / 340
  LF records / SHA-256
  `1836320f0e1a03705ff8e1dbbd2724d9e484ce03e10fde5f575967e2dd6e9796`.
- The admitted Chapter 1--10 targets and locked backend prefixes are not
  rewritten by this unit operation.

The target contains all five source sections in their original order:
maximal ideals in `C(X)`, character space, Gelfand transform, unital
`C*`-algebras, and the Gelfand--Naimark theorem. The source inventory is
`qa/CH11_SOURCE_INVENTORY.md`, 8,834 bytes / SHA-256
`86b3bf2a62b4d0a70a21dcda9cb66a515c9da014eba7f6b13a732624ca17119f`.

## Structural, mathematical, and language replay

The frozen census `qa/CH11_CENSUS.json` is 6,097 bytes / SHA-256
`c613491552a1f53aa152268fe06c9cef07245f3b94e65e1406746bdf0022e3dd`.
Independent source/target replay passes with:

- 102 ordered semantic anchors and identical anchor signatures;
- 107 balanced begin/end environment pairs in each surface;
- 38 labels, 15 references, five citation calls, 65 index hooks, and 21
  defined-term hooks with their ordered source identifiers preserved;
- 625 source and 625 target mathematical surfaces with a complete one-to-one
  mapping; and
- one `\endinput` in each source and target.

Chapter 11 contains 84 theorem-like surfaces, 12 proofs, nine proof hints,
three citation-only proof pointers, and no exercise, answer, or solution
environment. The occurrence of “exercise 18.45” is only a bibliographic
locator and is not projected as learner support. The target has zero active
placeholder markers, mojibake signatures, private/local paths, or unintended
English prose. Mathematical localization differences and the six source
repairs are classified rather than silently normalized.

The six high-confidence corrections are locked in
`provenance/SOURCE_CORRECTIONS_CH11.json`, 6,918 bytes / SHA-256
`aca046b4e471a5bbd5a383e34da36ee64726103c4d015c3f844ec777b5c90dc3`.
They include five mechanical repairs and the mathematical replacement of the
inconsistent summand `a_n z^n` under a `k`-indexed sum by `a_k z^k`. The
append-only human-readable correction ledger is
`provenance/SOURCE_CORRECTIONS.md`, 33,720 bytes / SHA-256
`7eece95494fc98ec45824ea6bf2c26d2ddb5b8642aa7acee75d4d26a24b89c32`.
No upstream contact occurred.

## Indonesian terminology gate and provenance

The bounded official arXiv search found no suitable Indonesian-language
functional-analysis TeX source. The honest fallback inspected the official
UNDIP JFMA article PDF and an official ITB functional-analysis curriculum
surface directly. Its PDF witness is 1,007,587 bytes / SHA-256
`6bc61be69f974e1598ec168504aa7b1925cf55a75dfc15100139bfcd586b0ff8`.
The comparison supports the existing core forms (*Analisis Fungsional*,
*ruang Banach*, *ruang Hilbert*, *operator linear terbatas*, *operator
kompak*, *teori spektral*) and does not justify replacing the Chapter 11
specialized choices. Evidence and decisions are recorded in:

- `qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md`, 7,948 bytes / SHA-256
  `78195240227ca257ff9f0b5d5132e4afe0e20d46a166fad471305246818d9451`;
- `provenance/CH11_TERMINOLOGY_DECISIONS.md`, 7,558 bytes / SHA-256
  `95255750208191727b8a8b4341b8acf6be88b6ddb5cf34f18fb9add84ba6e678`.

The reader and durable provenance use the exact model identification
**OpenAI Codex gpt-5.6-sol, Ultra**. John M. Erdman's authorship, Michael
Barr's component notice, and all other source and contributor credits remain
intact; the model identification does not replace those credits.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex,
  and Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two fully cleaned fixed-output-directory replays produced byte-identical
  PDFs: 1,873,719 bytes / 164 US-Letter pages / SHA-256
  `21a3b8c8fa2f5f68cba8a9b5c1fdbbb9f1feb906090159e8a2755f54fa177971`.
- Final TeX log: 55,547 bytes / SHA-256
  `ad29498791ba8fa9dcc33acb6b0599c2fe2bcbf39347e5c48077db607246fc75`.
- Blocking counts are zero: TeX/package errors, unresolved references or
  citations, rerun-required notices, multiply defined labels, missing
  characters, and underfull vboxes. Four inherited underfull hboxes occur in
  the long front-matter authority URLs/hashes. Two bounded Chapter 11
  overfull hboxes (7.30707 pt and 11.09703 pt) were inspected and do not clip,
  overlap, or cross the page edge.
- MakeIndex accepts 1,589 entries, rejects zero, writes 1,938 lines, and emits
  zero warnings.

The canonical reader is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-11.pdf`; it is
byte-identical to the fixed-path build witness. Its metadata retains John M.
Erdman as author and records `OpenAI Codex gpt-5.6-sol, Ultra` as creator.

## Complete visual and accessibility closure

All 164 pages were freshly rendered with Poppler at 110 dpi. The render set is
164 PNGs / 41,135,648 aggregate bytes, each 935 by 1,210 pixels. The exact
manifest is `provenance/CH11_RENDER_MANIFEST.csv`, 32,958 bytes / SHA-256
`498d67b3260a12b8645f3d4b3021cf0222077284840f3ae644f5a24a881c979a`.
The all-page contact sheet is `provenance/CH11_CONTACT_SHEET.png`, 3,255,188
bytes / SHA-256
`269fc039e483b17d6e3c019c5d003df3753515f6795d5d85554747d599b074bc`.

Nine consecutive contact sheets cover every physical page. Pages 137--145,
the complete Chapter 11 surface, were also inspected at full resolution. No
clipping, overlap, damaged glyph, broken diagram, unexpected blank, edge
collision, header/footer defect, or unreadable formula was found. Minimum
nonblank clear margins are 109/72/93/60 pixels (left/top/right/bottom), and
every page has zero ink in the outer five pixels. The only zero-ink pages are
20, 48, 78, 100, 114, 136, 146, and 148, all intentional blank versos.

The formal audit is `qa/CH11_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 3,953
bytes / SHA-256
`66e3350118aa0907408db13a1d36f60398e50c5cd2de005c278c6a283e4fb059`.
The PDF is searchable, navigable, unencrypted, and free of unsafe actions,
embedded files, forms, local paths, or replacement characters. It contains
24 top-level outline entries, 2,111 annotations/actions, eight URI actions
over six unique public targets, and 45 embedded font resources with Unicode
maps. It remains honestly untagged and lacks a structure tree; semantic HTML
and/or a tagged derivative remains a required edition-level deliverable and
is nonblocking only for this chapter checkpoint.

## Rights, privacy, and append-only backend boundary

The wrapper preserves Erdman attribution, the CC BY-SA 4.0 link, translation
and technical-change notices, ShareAlike, no additional restrictions, and
non-endorsement. `DIAGXY.TEX` remains byte-identical under Michael Barr's
notice. `TABLE.TEX`, badge artwork, and excluded quotation components are not
introduced. No separately authored mastery support or compact-spectral/SVD
bridge material is represented as Erdman-authored content.

The append-only Chapter 11 generator and independent validator lock the exact
Chapter 1--10 backend prefixes and Chapter 12--bridge queued suffix. After
this controlling receipt exists, they must append/project only Chapter 11,
validate global stable-ID uniqueness, relation endpoints, formulas, index
rows, terminology, corrections, artifacts and QA events, then write the
aggregate backend manifest and reconciliation report. Aggregate identities
belong in that post-receipt report and the durable state, avoiding a circular
receipt hash.

Chapter 11 is admitted. The whole edition remains `in_progress`; after backend
reconciliation and checkpoint publication, the source-order translation
cursor advances to `FAOA-2015-CH12`, `source/upstream/no_identity.tex`.
