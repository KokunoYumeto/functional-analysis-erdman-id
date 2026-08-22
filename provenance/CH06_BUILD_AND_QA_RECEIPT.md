# FAOA-2015-CH06 build and QA receipt

Date: 2026-08-22  
Decision: **admitted**  
Course role: `D20_core`

This receipt admits the complete Indonesian Chapter 6, *Ruang Banach*, and the
cumulative Chapter 1--6 reader. Translation, mathematics, structure, build,
visual, navigation, component-rights, privacy, and append-only backend gates
pass. It does not claim that Chapters 7--17, the semantic HTML reader, the O001
solved mastery layer, or the original compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Source: `source/upstream/Banach_spaces.tex`, 79,549 bytes / 1,605
  CRLF-terminated lines / SHA-256
  `0f401d088ec3e2d3f2ca4dafa2595a7f0049193a097b6b27af7b247fd433df51`.
- Target: `source/id-ID/Banach_spaces-id.tex`, 82,940 bytes / 1,569 LF lines /
  SHA-256
  `ca32547e4b47af3444d454476beac71ad8870e88b436dc008e1cb5dbb6755e9c`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch06.tex`, 9,660 bytes / 333
  LF lines / SHA-256
  `92ab981f81488472f2c45271727b6652bfa62227533107725bff08f4416e738a`.
- Derivative bibliography: `source/id-ID/functional_analysis_op_algs_bib.bib`,
  17,409 bytes / SHA-256
  `72b33be29e0728654e4b623e454639927046f425fb81e5b13b8c05e1888fd6fa`.
- The admitted Chapter 1--5 targets and their backend byte prefixes are
  unchanged.

## Structural, mathematical, and language replay

The locked source/target checker preserves the complete ordered topology:
seven sections, 178 balanced environment pairs, six exercises, 29 proof
blocks, 28 semantic proof hints, 56 labels, 80 ordinary references, two
equation references, 13 citations, 155 index hooks, and 47 defined-term hooks.
Forty-seven ordinary references resolve within Chapter 6, 32 resolve to
admitted prior units, and one points forward to source label `000731`; the
partial reader renders the last reference honestly as a future reference. Two
previously pending cross-references become resolved by Chapter 6 declarations.

The mathematical projection contains 1,155 source surfaces and 1,156 target
surfaces. All 22 nontrivial edit blocks are classified as language-bearing
mathematical text, a source correction, or a necessary additive localization;
there is no unexplained formula deletion, reorder, or semantic change. The
final checker is `qa/check_ch06_translation.py`, 15,728 bytes / SHA-256
`88412b9799d25e3342894dfb2ecba7e3a90d59232c837ef6d0913689c6778391`.
Repeated runs return `pass`, with zero visible English residue and no
structural error.

An independent bilingual rereview read all 1,605 source and 1,569 target lines,
including every theorem-like environment, proof, hint, exercise, formula,
label, reference, citation, and index entry. It found no mathematical,
semantic, quantifier, negation, reference, or exercise defect. Three low-level
Indonesian prose improvements were accepted before the final target was
frozen: a more natural rendering of “much slicker,” restoration of the
preposition before `$(\ast)$`, and a clearer noun phrase for a bounded family
of Hilbert-space operators.

Twenty bounded source corrections are applied and individually recorded. The
append-only cumulative ledger is `provenance/SOURCE_CORRECTIONS.md`, 20,716
bytes / SHA-256
`7de8a5892b865af84c9f5d1d4c37ec6b3112b3e099685dae243108006dc94b01`.
Its admitted Chapter 1--5 prefix remains byte-identical at 16,450 bytes /
SHA-256
`2408e045efb307602fbe8540efcb6307944d01d7ace610d78e4341856a0e35b7`;
the 4,266-byte Chapter 6 suffix has SHA-256
`51c26be9d5346ced5707d0ce91e2ed27f313c60666aab81155dafd572cde2118`.
No upstream contact occurs during production.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex,
  and Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two independently cleaned builds in the same fixed output directory produced
  byte-identical PDFs: 1,468,946 bytes / 114 US-Letter pages / SHA-256
  `93cfdf76515205ca259c91537a58cfa2b0ae7cab67e4b1b818ac9f5784aaa55c`.
- Latest final TeX log: 46,285 bytes / SHA-256
  `d3f234b73aa71121a463b752dd68fa558309ad2056df31d956c2e060814bfeef`.
- Final log: zero TeX errors, unresolved references or citations,
  rerun-required warnings, multiply defined labels, overfull boxes, underfull
  vboxes, or missing characters. Four benign front-matter underfull hboxes
  arise from long authority URLs and hashes; 77 legacy small-caps-italic font
  substitutions do not alter reader content.
- BibTeX uses 25 entries and reports zero warnings. MakeIndex accepts all 1,168
  entries, rejects zero, writes 1,445 lines, and reports zero warnings.

The canonical reader is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-6.pdf`; its
build-tree copy is byte-identical. The catalog language is `id-ID`; the PDF has
42 outline entries, 1,052 named destinations, 1,500 resolved internal links,
and eight URI annotations over six unique external targets. It has no
encryption, form, widget, JavaScript, launch action, embedded attachment, rich
media, or executable action. Its sole open action is an internal `GoTo` view.

## Visual and accessibility evidence

All 114 physical pages were freshly rendered at 150 dpi. The exact render set
contains 114 PNGs / 40,224,010 aggregate bytes, each 1,275 by 1,650 pixels.
The public render manifest is 22,218 bytes / SHA-256
`ba63bc106be574414792ac6bc37b76483a01491822fca4745962e8ff9e407db8`;
replay finds no missing, extra, duplicate, dimension-mismatched, or
hash-mismatched page. The all-page public contact sheet is 3,339,772 bytes /
SHA-256
`1b5aaad85c2c13651c51d92d6452eb21fca892b641abe87c3991e95bc4f1bedf`.

The complete public sheet, ten detailed consecutive contact sheets, and
full-size physical pages 1, 2, 79, 83, 85, 88, 90, 95, 98, 99, 103, and 114
were inspected after the final rereview and build. No clipping, overlap,
off-center body block, damaged glyph, unreadable formula, broken header, or
margin violation was found. Bounding-box replay finds 54,378 words and zero
boxes outside the page bounds, with minimum clearances of 72.000 points left,
71.255 right, 49.279 top, and 37.804 bottom. The five zero-word pages are the
intentional blank versos 20, 48, 78, 100, and 102.

The formal report is
`qa/CH06_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 5,197 bytes / SHA-256
`3da448996dba97de722ccc48eaa7590a5a9d2f462dcaa4766aecd153139d528b`.
The bounded PDF entry point is `qa/audit_ch06_pdf.py`, 173 bytes / SHA-256
`0a0202265983431cc94a6775c21f75f84c6648fe342e4f08affe166a70ca73d5`.
All 43 font resources report Unicode maps. Extracted text is 436,932 bytes /
SHA-256
`d9fa66b1ec42ede6ab4247f81eb70361c274922cb5d3eeaacf0616fc30235c4c`
and contains no replacement character, mojibake signature, or local path. The
single link color has 7.137:1 contrast against white.

The PDF remains honestly untagged: it has no structure tree, semantic
heading/list/equation/index roles, alternative-text framework, XMP stream, or
guaranteed screen-reader order. It is a visually usable, searchable,
navigable reader with strong text extraction, not a fully accessible edition.
Semantic HTML and/or a later tagged-PDF derivative with mathematical and
diagram accessibility remains an edition-level deliverable and is nonblocking
only for this chapter boundary.

## Rights, component, and privacy closure

The wrapper supplies Erdman attribution, a CC BY-SA 4.0 link, a translation and
technical-change notice, ShareAlike terms, and non-endorsement. `DIAGXY.TEX`
remains byte-identical to the frozen source copy at 41,908 bytes / SHA-256
`3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb`
under Michael Barr's embedded notice. `TABLE.TEX`, badge artwork, and uncleared
quotation components are absent from the build closure; the Halmos reference
in Chapter 6 is a bibliographic reference and paraphrase, not a reproduced
quotation. Separately authored solutions, mastery support, and the
compact-spectral/SVD bridge are not represented as Erdman-authored content.

A bounded scan of the prospective public Chapter 6 text, QA, provenance, and
reader surfaces finds no credential or token, no live local filesystem path,
no unrelated-lane reference, and no private control artifact embedded in the
canonical backend or PDF. The checker's literal `C:\Users` string is a
negative-test pattern, and `.gitignore` names the private `00_control/` and
`authority/` directories only to exclude them from publication.

## Backend admission and deterministic replay

The Chapter 6 projection appends stable locale-neutral unit, semantic, segment,
formula, relation, exercise-support, index, terminology, correction, artifact,
and typed-QA records while preserving the complete admitted Chapter 1--5 byte
prefixes and IDs. It adds 166 semantic units, 206 segments, 845 relations,
1,156 formula maps, 155 index rows, six exercise-support records, 20 correction
records, 33 new global terminology records, nine public artifacts, and eight
typed QA events.

The canonical validator runs the complete generator twice with byte-identical
outputs. It validates 18 ordered units, 778 semantic units, 947 segments, 3,442
relations, 5,538 formula maps, 33 exercise-support records, 1,168 index rows,
46 artifacts, 44 typed QA events, 111 corrections, and 186 terminology
records. Across all JSONL projections it checks 11,192 records, 12,360 globally
unique IDs, 6,928 relation endpoints, exact JSON/CSV round trips, public
artifact bytes, private-control exclusion, receipt binding, and append-only
closure of two prior pending references. The resulting backend manifest hash
is recorded in durable state and the publication handoff rather than
circularly embedded in this receipt.

Chapter 6 is admitted. The whole edition remains `in_progress`, and the active
source-order cursor advances to `FAOA-2015-CH07`,
`source/upstream/compact_operators.tex`.
