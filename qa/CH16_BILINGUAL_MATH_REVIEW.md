# Chapter 16 bilingual and mathematical review

Date: 2026-08-24  
Unit: `FAOA-2015-CH16`  
Result: **pass for admission**, subject to the cumulative build/backend gates

The complete source and Indonesian target were checked in source order and by
an exhaustive deterministic topology/formula comparison. The locked byte
bindings are:

- source `source/upstream/extensions.tex`: 42,614 bytes, 1,000 CRLF records,
  SHA-256
  `e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318`;
- target `source/id-ID/extensions-id.tex`: 43,804 bytes, 1,000 LF records,
  SHA-256
  `59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3`;
- cumulative Chapter 1--16 master
  `source/id-ID/functional-analysis-id-through-ch16.tex`: 10,679 bytes, 345
  LF records, SHA-256
  `6e528b0193d3179b58e44169430d043fa5399f7c860f09d832eb3ccd954a5388`.

The active reader surface has exactly four sections in both languages. The
commented prospective tensor-product heading at record 676 remains commented
and is not counted as a fifth section. Both source and target retain 142
environment openings and closings, including 124 reader-semantic
environments; 36 unique labels; 28 references; 59 citations; 107 index hooks;
29 defined-term hooks; one manual equation tag `(1)`; 15 examples; 31 proofs;
and zero formal exercises, hints, answers, or solutions. All environment
stacks close in the same order.

## Reader language and terminology

The target uses natural Indonesian prose while keeping mathematical names,
symbols, identifiers, and diagram topology stable. The controlled vocabulary
from `provenance/CH16_TERMINOLOGY_PLAN.md` is applied consistently:

- `spektrum esensial`, `ekuivalen uniter secara esensial`, `kompalen`,
  `normal secara esensial`, and `swaadjoin secara esensial` remain distinct
  from exact unitary equivalence and ordinary normality/self-adjointness;
- the Toeplitz family consistently uses `operator Toeplitz`, `simbol`,
  `matriks Toeplitz`, `aljabar Toeplitz`, `ekstensi Toeplitz`, `bilangan
  lilit`, and the corresponding abstract forms;
- `ekstensi` is used for exact-sequence/Busby extensions, while `tarik balik`
  and `pengangkatan` retain their different categorical meanings;
- `positif`, `2-positif`, `n-positif`, `positif lengkap`, and `terbatas
  lengkap` remain separate levels, and `semiterbelah` is not confused with
  `terbelah`;
- `pemetaan linear beridentitas dan positif lengkap` is used for both the
  repaired Voiculescu hypothesis and the semisplit lifting criterion;
- `nuklir`, `praurutan`, `urutan parsial`, `unit matriks standar`, and
  `aljabar Calkin` are preserved consistently with the preceding chapters.

The active target contains no detected English instructional residue,
rejected English technical term, mojibake, private path, credential marker,
or placeholder. The bounded external Indonesian terminology witness already
recorded for Chapter 11 supports the edition's general functional-analysis
vocabulary. It does not establish frequency for every BDF, Toeplitz, or
complete-positivity compound; those specialized choices are therefore
justified by mathematical meaning, Indonesian morphology, and internal
edition consistency rather than by an invented frequency claim.

## Exhaustive mathematical-surface accounting

After TeX comments are removed, the source has 672 inline, 26 bracket-display,
and four `equation` surfaces: **702 active ordered math surfaces**. The target
has 670 inline, 26 bracket-display, and four `equation` surfaces: **700 active
ordered math surfaces**. A source-ordinal-bound transformation program in
`qa/check_ch16_translation.py` proves that every difference is exhausted by
15 classified operations; there are zero unclassified differences.

Eleven operations implement eight correction groups:

1. `CH16-CORR-002`: source ordinals 29 and 37 replace the two ill-typed
   `UTU^*` conjugations by `U^*TU`.
2. `CH16-CORR-004`: ordinal 149 restores `\ofml Q(H^2)`.
3. `CH16-CORR-006`: ordinal 179 replaces the misidentified section `\beta`
   by `T`.
4. `CH16-CORR-008`: ordinals 198 and 200 replace
   `\pi^1(\C\setminus0)` by `\pi_1(\C\setminus\{0\})`.
5. `CH16-CORR-010`: equation ordinal 244 removes the extra parenthesis in
   `\psi|_{\ofml K}` without changing any diagram object or arrow.
6. `CH16-CORR-011`: ordinal 353 changes the accidental codomain `\ofml A`
   to `A`.
7. `CH16-CORR-012`: source ordinals 365--369 become target ordinals 365--367
   through the typed family `\tau_j\colon A\to\ofml Q(H)`, `j=1,2`; source
   ordinal 372 becomes target ordinals 370--371 by naming the missing unitary
   `U` before the retained space `H`.
8. `CH16-CORR-015`: source ordinal 659, the star-homomorphism marker on the
   lift, is deleted because the correct lift is linear, unital, and completely
   positive rather than multiplicative.

The remaining four operations preserve mathematical meaning: ordinal 74 adds
braces around the norm argument `\phi`; ordinal 141 localizes `\text{and}` as
`\text{dan}`; and source ordinals 542--543 localize `j^{\text{th}}` and
`k^{\text{th}}` as `j` and `k`. Together with the compression/insertions in
the typed monomorphism family and deletion of the false multiplicativity
marker, these operations explain the net surface count change from 702 to
700 exactly.

The raw active display delimiters and braces are balanced. All four equation
environments, the three `\xymatrix` diagrams, two `\Square` diagrams, one
`\pullback` diagram, and two `\dtriangle` diagrams retain their source order,
labels, map directions, and objects except for the explicitly repaired typo at
equation ordinal 244. The inactive `$C^*$` in the commented heading is not
miscounted as reader mathematics.

## Complete source-correction closure

`provenance/SOURCE_CORRECTIONS_CH16.json` binds all 15 adjudicated groups to
inclusive source and target record ranges, normalized before/after snippets,
snippet SHA-256 values, required/forbidden anchors, classification, rationale,
and exact source/target identities:

1. separate `\begin{prop}` from its opening word;
2. repair both ill-typed unitary conjugations;
3. add the separable infinite-dimensional scope to proposition `005134`;
4. restore Fraktur Calkin notation;
5. repair “and isomorphism” to the intended “an isomorphism”;
6. identify `T`, not `\beta`, as the section;
7. join the Douglas theorem number as `7.26`;
8. restore fundamental-group notation in both occurrences;
9. replace the stale “after section 9.2” index locator with the current
   locale-neutral section locator;
10. remove the extra parenthesis in the extension-equivalence diagram;
11. repair the pullback projection codomain;
12. name the missing unitary `U` and type the pair of monomorphisms compactly;
13. repair both index-only `Topelitz` misspellings;
14. add the missing unital completely positive linear hypothesis to
   Voiculescu's theorem; and
15. make `\tau` explicitly unital and replace the false star-homomorphic lift
   by a unital completely positive linear lift.

The last correction was independently rechecked after the first complete
assembly: the initial target had repaired the lift but had not explicitly
made `\tau` unital. The target owner corrected that omission before this
review was locked. The final target identity above binds the complete repair;
no known mathematical or correction-ledger defect remains.

The repaired Voiculescu hypothesis rules out the concrete counterexample
`\phi(1)=2I`. The repaired lifting criterion agrees with the preceding prose,
the semisplit definition, Stinespring dilation, the nonsplit concrete Toeplitz
extension, and the later nuclear lifting theorem. No correction is applied to
the frozen English authority.

## Linkage, rights, and provenance

All 28 references resolve among the 565 labels in the cumulative Chapter
1--16 include closure. All 59 citation occurrences resolve in the frozen
bibliography. The master includes the 16 translated chapters in exact source
order and retains the terminal `\endinput` in this chapter.

The cumulative master retains John M. Erdman's authorship, component credits,
CC BY-SA 4.0 notice and link, adaptation/change notice, ShareAlike boundary,
non-endorsement, and exact model provenance `OpenAI Codex gpt-5.6-sol,
Ultra`. `DIAGXY.TEX` remains an unchanged dependency under Michael Barr's
notice. Excluded `TABLE.TEX`, badge artwork, and quotation surfaces remain
absent. No source-attributed exercise or solution material is invented, and
no author or maintainer was contacted.

The locked machine-readable result is
`qa/ch16-translation-report.json`; its status is `pass`. Admission still
depends on the separate cumulative build, visual, backend, receipt, and public
readback gates owned by the parent workflow.
