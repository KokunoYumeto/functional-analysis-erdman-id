# FAOA-2015-CH03 build and QA receipt

Date: 2026-08-22  
Decision: **admitted**  
Course role: `D20_core`

This receipt admits the complete Indonesian Chapter 3, *Ruang Linear
Bernorma*, and the cumulative Chapter 1--3 reader. It does not claim that
Chapters 4--17, the semantic HTML reader, the O001 solved mastery layer, or the
original compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Source: `source/upstream/normlinspaces.tex`, 87,537 bytes / 1,920 lines /
  SHA-256
  `01548b8e80e14f6eb66703579ed7020e68cc65bd8d30538c13a3533a5ba777e7`.
- Admitted target: `source/id-ID/normlinspaces-id.tex`, 94,040 bytes / 1,913
  lines / SHA-256
  `c44f20890d5fb6b7445f0b2eeca8f477cc970d147d5c54aa4bc5df709f6b1f9d`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch03.tex`, 9,311 bytes /
  SHA-256
  `f36da75492209ba8f4df1d8982bc5a7eae79d75a5dfeb87267715c998aeed8c7`.
- The admitted Chapter 1 and Chapter 2 targets were not modified.

## Structural and mathematical replay

The source and target retain the same ordered topology:

- 189 balanced environment pairs in identical order and 185 semantic anchors,
  yielding 184 reader semantic units and 228 mapped segments;
- 91 labels, 6 citations, 344 index hooks, and 98 defined-term hooks in
  identical order;
- 47 reference-class occurrences: 46 ordinary local references and the later
  Chapter 5 endpoint `exam_ran_nonclosed`, preserved as
  `\futurexref{5.2.14}{exam_ran_nonclosed}`; the one equation reference is
  separately preserved, for 48 reference surfaces in total;
- 7 exercises, 10 explicit proof hints, and every theorem-like or learner-work
  surface remain in source order.

The deterministic text-aware math extractor finds 1,414 source and 1,414
target surfaces. Sequence alignment yields 1,394 exact normalized formula-map
records and 16
reviewed non-equal groups. Every non-equal group is confined to a logged source
correction or lossless localization decision; there are zero unexplained
mathematical deltas. The extractor correctly retains the embedded
`x \in V` in the source line 517 / target line 581 `\text{...}` payload as
part of one complete outer math surface rather than two broken fragments. The
final checker is `qa/check_ch03_translation.py`, 7,420 bytes / SHA-256
`9fed1e9c4d6111db8c10e19f05589b070e3508b2290c1a897a73a7eb04364386`,
and its result is `pass_reviewed_math_deviations_locked`.

## Translation and source-correction review

The complete source and target were read independently. Final review at the
admitted target hash found P1=0, P2=0, and P3=0. Active reader text contains no
unintended English prose, mojibake, replacement character, placeholder, local
path, task identifier, or credential surface. Terminology is reconciled with
Chapters 1--2, including `ruang linear bernorma`, `pemetaan linear terbatas`,
`norma operator`, `ruang dual`, `jaring`, and `Teorema Hahn--Banach`.

Twenty-five bounded source-backed corrections are applied and independently
reviewed. They include malformed notation and index entries, missing words,
scalar-field and codomain inconsistencies, incorrect product/coproduct symbols,
an incomplete bounded-net definition, the real-part variable in the complex
Hahn--Banach reduction, the missing nonzero hypothesis in the norm-one
functional corollary, pointed-metric shorthand, and zero-domain operator-norm
edge cases. Exact source and target loci are recorded in
`provenance/SOURCE_CORRECTIONS.md`, 7,325 bytes / SHA-256
`bb1ef771876b2c1ef0063c3fd9e28c27f20db4049f434d27f8b333fd5f3477c2`.
No upstream contact occurs during production.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex,
  and Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two independently cleaned runs at the same fixed output path produced
  byte-identical PDFs: 1,076,473 bytes / 57 US-Letter pages / SHA-256
  `7a921e1f9678b0a698de237a0a0e5629f24f5b6f0798d2638d9c0a70a499b4f5`.
- Pass-one final TeX log: 32,129 bytes / SHA-256
  `0078ba8d45b9812ac251c97a850d13ab0f8fcade2310a227100f95ac8f6aeac9`.
- Pass-two final TeX log: 32,129 bytes / SHA-256
  `cfdf14c1dd1df425cc756a82371448649737e1fe8e0e0953205c93f0251b8282`.
- Final log: zero TeX errors, unresolved references/citations,
  rerun-required warnings, multiply defined labels, overfull boxes, or missing
  characters. It retains two benign front-matter underfull hboxes and twenty
  legacy small-caps-italic substitutions; neither affects reader content.
- BibTeX reports zero warnings. MakeIndex accepts all 668 entries, rejects
  zero, and reports zero warnings.

The canonical reader PDF is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-3.pdf` with the
same exact byte identity above. It has Indonesian title/author/subject
metadata, `/Lang=id-ID`, 17 outline entries, links, and no encryption,
JavaScript, form, or AcroForm. It is honestly untagged; the required accessible
semantic HTML reader remains future edition work.

## Visual, rights, privacy, and backend evidence

All 57 pages were freshly rendered at 144 dpi and inspected. No clipping,
overlap, broken formula, missing glyph, damaged link text, or index collision
was found. The 57 page PNGs total 18,765,751 bytes. Their 57-row replay manifest
is 5,211 bytes / SHA-256
`162328427d9912347eeadb39c1c78f8cbad62f599904cc929e075ac109e96b73`,
with zero missing, extra, size-mismatched, or hash-mismatched pages. The
all-page contact sheet is 1,267,020 bytes / SHA-256
`bf4872e145c57768cc369cb748ef7d4cbc61a424414ee158a0a18572a381a284`;
Chapter 3 pages, equations, exercises, transitions, bibliography, and index
were additionally inspected at full rendered size.

The wrapper supplies attribution, a CC BY-SA 4.0 link, change notice,
ShareAlike terms, and non-endorsement. `DIAGXY.TEX` remains byte-identical at
41,908 bytes / SHA-256
`3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb`.
`TABLE.TEX`, badge artwork, and uncleared quotation components are absent from
the build closure. Bounded TeX, PDF-text, metadata, and credential/privacy
scans pass.

Before receipt binding, Chapter 3 backend generation replayed twice in isolated
copies with byte-identical outputs while retaining exact Chapter 1--2 byte
prefixes. The projection adds 184 semantic units, 228 segments, 703 relations,
1,410 formula-map records, 344 index rows, 7 exercise-support records, 25
corrections, and 18 terminology records. The final canonical reconciliation
binds this receipt, target, cumulative PDF, source corrections, typed QA events,
and admission state. Its final manifest hash is recorded in the durable state
and publication handoff to avoid a circular self-hash inside this receipt.

Chapter 3 is admitted. The active source-order cursor advances to
`FAOA-2015-CH04`, `source/upstream/Hilbert_spaces.tex`.
