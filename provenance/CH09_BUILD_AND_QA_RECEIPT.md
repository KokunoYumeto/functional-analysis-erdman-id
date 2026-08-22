# FAOA-2015-CH09 build and QA receipt

Date: 2026-08-22  
Decision: **admitted**  
Course role: `advanced_continuation`

This receipt admits the complete Indonesian Chapter 9, *Ruang Vektor
Topologis*, and the cumulative Chapter 1--9 reader. Translation, mathematics,
structure, references, build determinism, visual layout, navigation, component
rights, privacy, and append-only backend gates pass. It does not claim that
Chapters 10--17, the semantic HTML reader, the O001 solved mastery layer, or the
original compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Frozen source: `source/upstream/topvecspaces.tex`, 35,022 bytes / 806
  CRLF-terminated lines / SHA-256
  `62bc645c9d0972856913098d90d4baec7a8b0f470d4d380a880416f64cd5bce4`.
  Its sole `\endinput` is line 806 and only the final CRLF follows it.
- Admitted target: `source/id-ID/topvecspaces-id.tex`, 37,705 bytes / 804 LF
  lines / SHA-256
  `791868776a07f4c854f1c13d295da23a2559b88dcac48523fb0390e1e5330ee1`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch09.tex`, 9,780 bytes / 335
  LF lines / SHA-256
  `acba53fd01601ecd49516c01fb00e38af7bfcafbbbff0358a87dea864c591e3f`.
- The admitted Chapter 1--8 targets and every locked backend prefix remain
  unchanged.

## Structural, mathematical, reference, and language replay

The locked checker preserves 126 balanced environment pairs, including 57
propositions, 21 examples, 19 definitions, nine proof environments, eight
corollaries, seven enumerations with 20 items, three notation blocks, one
convention, and one exercise. It preserves all nine labels, seven reference
calls, five citations, 91 index hooks, and 40 defined-term calls. The two
forward labels consumed by Chapter 10, `prop_quotient_top_strong` and
`mi_notn`, remain exact stable anchors. The single exercise is not falsely
given an upstream answer or solution. Five explicit hint blocks and all
citation-only proof surfaces remain visibly distinguished from complete
proofs.

The source has 603 mathematical surfaces and the target 606. The backend
mapping classifies 585 normalized-byte exact maps, three math-key-preserving
Indonesian substitutions inside `\text{...}`, 15 reviewed source-correction
maps, and three target-only correction maps. Every non-exact mathematical
surface is bound to localization or the exact correction ledger; no
unclassified formula edit remains.
The final checker is `qa/check_ch09_translation.py`, 35,327 bytes / SHA-256
`de952960ea7e48d4085162a9f6f5239a29daf810cc22bf933df4031d13618425`.
Its deterministic report is `qa/ch09-translation-report.json`, 7,931 bytes /
SHA-256
`0865aa5e64ea9ed5893925c3cf0986e1fc38c5f8d1b2f529ded71e06af5efd40`.
Repeated replay returns `pass`, with zero visible English, mojibake, private
path, structural, or unclassified mathematical residue.

Twenty-six source corrections are locked in
`provenance/SOURCE_CORRECTIONS_CH09.json`, 14,917 bytes / SHA-256
`861b96347a0ab045861042c782209d284f2811f0eaa21c85200745d11de882e9`:
17 mechanical repairs and nine mathematical repairs. They bind exact source
line ranges, normalized snippet hashes, required target anchors, forbidden
malformed anchors, correction classes, and the source-to-target nonblank
ordinal map. The append-only human-readable Chapter 1--9 ledger is
`provenance/SOURCE_CORRECTIONS.md`, 29,933 bytes / SHA-256
`8854271d5a35eaddc3fc1141f7a2fc1e100796652a30fb52b257fb5b34c9d514`.
No upstream contact occurred.

The four contiguous translation fragments were assembled with a locked
deterministic assembler and reread against the complete source topology.
Reader-facing terminology consistently uses, among others, *ruang vektor
topologis*, *jaring*, *filter*, *himpunan menyerap*, *seminorma Minkowski*,
*ruang Fréchet*, and *ruang Schwartz*. Two final prose tightenings removed the
only Chapter-9 overfull lines without altering mathematical content.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex, and
  Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two fully cleaned fixed-path builds produced directly byte-identical PDFs:
  1,686,477 bytes / 140 US-Letter pages / SHA-256
  `99215ff5987f720600152da902cec8f521329692931a0dbf89e82ef2d4ff6076`.
- Final TeX log: 51,189 bytes / SHA-256
  `c914d345ca65037ae1b1290dd483993536cd6ce7b08986dd3ae7c17b302ea06f`.
- Blocking log counts are zero: TeX/package errors, unresolved references or
  citations, rerun notices, multiply defined labels, overfull boxes, vbox
  warnings, and missing characters. Four inherited underfull hboxes arise from
  long authority URL/hash material and do not omit or overlap content.
- BibTeX uses 31 entries with zero warnings. MakeIndex accepts all 1,423
  entries, rejects zero, makes 16,143 comparisons, writes 1,737 lines, and
  reports zero warnings.

The canonical reader is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf`; its
fixed-path build copy is byte-identical.

## Visual and accessibility evidence

All 140 physical pages were rendered at 150 dpi. The exact render set contains
140 PNGs / 49,729,623 aggregate bytes, each 1,275 by 1,650 pixels. The public
render manifest is 27,298 bytes / SHA-256
`add426dfd81f96fb8adc838d8173436d64ea3b2a165cdc1ff4a732c2a0f6fb2d`;
replay finds no missing, extra, duplicate, dimension-mismatched, or
hash-mismatched page. The public all-page contact sheet is 4,114,399 bytes /
SHA-256
`09b3bc4d70cc83d99cd376245c578e4c72fff6995e3392810e2d55e0302986dd`.

Every page was inspected through twelve detailed consecutive contact sheets
and the compact public all-page sheet. Physical pages 115--126 received a
second full-size inspection covering the Chapter 9 opener; balanced,
absorbing, and barrelled sets; nets and filters; compatible and quotient
topologies; locally convex spaces; Minkowski functionals; Fréchet and Schwartz
spaces; the exercise and hints; the bibliography transition; and the blank
verso. No clipping, overlap, off-center body block, damaged glyph, unreadable
formula, broken header, unexpected blank, or margin violation was found.

Bounding-box replay finds 66,270 words and zero boxes outside page bounds,
with minimum clearances of 72.000 points left, 71.254988 right, 49.278601 top,
and 37.803801 bottom. The six zero-word pages are exactly the intentional blank
versos 20, 48, 78, 100, 114, and 126. The formal report is
`qa/CH09_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 6,825 bytes / SHA-256
`d5b3adc00a6aafd7da5ce1b76dc8e2d25fe877f1e46824596a947cd20e2f8287`.

The PDF has language `id-ID`, 57 outline entries, 1,387 named destinations,
1,831 resolved internal links, eight URI annotations over six unique external
targets, and zero unresolved internal links. It has no encryption, form,
widget, JavaScript, launch action, embedded attachment, rich media, or unsafe
action. All 45 font resources are embedded subsets with Unicode maps.
Extracted text is 531,953 bytes / SHA-256
`73c6f363443b3349b8361684bc15a26751120f33c0d6d95ab4b64a52017736ef`
and contains no replacement character, mojibake signature, or local path.

The PDF remains honestly untagged and lacks a structure tree, semantic roles,
alternative-text framework, and guaranteed screen-reader order. It is a
visually usable, searchable, navigable reader, not the final accessible
edition. Semantic HTML and/or a later tagged-PDF derivative remains a required
edition-level deliverable and is nonblocking only for this chapter boundary.

## Rights, component, privacy, and backend closure

The wrapper supplies Erdman attribution, a CC BY-SA 4.0 link, translation and
technical-change notices, ShareAlike terms, and non-endorsement. `DIAGXY.TEX`
remains byte-identical under Michael Barr's embedded notice. `TABLE.TEX`, badge
artwork, and uncleared quotation components remain absent. Separately authored
solutions, mastery support, and the compact-spectral/SVD bridge are not
represented as Erdman-authored content. A bounded public-surface scan finds no
credential, live local path, unrelated-lane reference, or private control
artifact.

The Chapter 9 projection appends 125 semantic units, 137 segments, 513
relations, 606 formula maps, one exercise-support record, 91 index rows, 40
term occurrences over 38 distinct concepts, 26 correction records, 11 exact
public artifact bindings, and eight typed QA events. Thirty-six terminology
records are new and two reuse existing concepts. Every admitted Chapter 1--8
byte prefix and stable ID remains unchanged.

The final post-receipt validator runs the complete generator twice, requires
byte-identical output, validates exact JSON/CSV round trips, globally unique
IDs, relation endpoints, public artifact bytes, private-control exclusion, and
append-only closure, and binds this exact receipt. Its final aggregate counts
and manifest identity are recorded in durable state and the root handoff rather
than circularly embedded here.

Chapter 9 is admitted. The whole edition remains `in_progress`, and the active
source-order cursor advances to `FAOA-2015-CH10`,
`source/upstream/distributions.tex`.
