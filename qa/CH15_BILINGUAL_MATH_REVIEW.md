# Chapter 15 bilingual and mathematical review

Date: 2026-08-24  
Unit: `FAOA-2015-CH15`  
Result: **pass for admission**, subject to the cumulative build/backend gates

The complete 444-record upstream chapter and complete 444-record Indonesian
target were independently reread in source order. The byte bindings are:

- source: 16,977 bytes, 444 CRLF records, SHA-256
  `0ef2e5be3c716a099e8609a84528d77ad6387ec531c52f9890d4e34175c57d91`;
- target: 17,672 bytes, 444 LF records, SHA-256
  `174b1ad2557f7dfa10e8171bd7482d907f858389b509f4d55de9cc785e2b43ba`;
- cumulative Chapter 1--15 master: 10,541 bytes, 344 LF records, SHA-256
  `f2df36c70dcca86f44687efe450ea46a5611be2d1170a9ded16dbfbfcdb73a33`.

The review covered all four sections; 60 environment openings and closings (50
reader-semantic environments, six `align` environments, and four `enumerate`
environments); 33 unique labels; 27 references; 17 citations; 46 index hooks;
11 defined terms; 12 manual equation tags; eight examples; and 13 proof
environments. There are no formal exercise, answer, or solution environments.

## Linguistic and terminology decisions

- Reader prose is natural id-ID and consistently reuses the admitted edition
  forms `ruang Hilbert`, `ruang Banach`, `operator kompak`, `adjoin`,
  `swaadjoin`, `kernel`, `kokernel`, `kodimensi`, `jangkauan`, `padat`,
  `invertibel`, `pemetaan hasil bagi`, `barisan eksak`, and `semigrup`.
- The Chapter 15 controlled forms are present and coherent: `persamaan
  integral`, `persamaan tak homogen`, `kontinuitas lengkap`, `operator
  Riesz--Schauder`, `jangkauan tak tertutup`, `aljabar Calkin`, `operator
  Fredholm`, `perturbasi kompak`, `Teorema Atkinson`, `indeks Fredholm`,
  `isometri parsial berperingkat hingga`, `lintasan`, `terhubung oleh
  lintasan`, `homotop`, and `komponen lintasan`.
- The manually tagged Fredholm systems retain tags `(1)` through `(6)` and
  `(1')` through `(6')`. English `and` embedded in those six `align` surfaces
  is localized as `dan` without changing a formula, label, or visible tag.
- The source does not specify the function space for Alternative I. The target
  preserves that limitation and does not silently choose between
  `C([0,1])` and `L^2([0,1])`. This is a documented source-scope omission, not
  missing translated content.
- No active English instructional prose, rejected `nonhomogen`, English
  `range`, `rapat`, mojibake, private path, credential marker, or placeholder
  remains.
- A final typography-only reflow removes the redundant word `suatu` from
  Proposition 15.2.3. This preserves its ambient-space repair and formula while
  eliminating the chapter's 1.39676 pt overfull line.

The bounded Indonesian external witness already preserved for Chapter 11
supports the edition's core functional-analysis terminology but does not prove
frequency for every Fredholm-specific compound. The specialized choices here
rest on mathematical meaning, Indonesian morphology, and internal edition
consistency; no unsupported frequency claim is made.

## Mathematical decisions and complete surface accounting

The upstream inventory contains 190 inline math spans, seven `\[...\]`
displays, and six whole `align` environments: 203 ordered top-level math
surfaces. The derivative contains 191 inline spans, seven displays, and six
whole `align` environments: 204 ordered top-level surfaces. A deterministic
transformation program proves that all differences are exhausted by twelve
classified operations:

1. Alternative I gains the previously missing fixed surface
   `\lambda\in\C\setminus\{0\}`.
2. The six English conjunctions inside the six tagged `align` systems become
   Indonesian `dan`.
3. The historical ordinal surface `20^{\text{th}}` becomes natural Indonesian
   `20`.
4. Alternatives II and IIIa each replace the overbroad
   `\lambda\in\C` by `\lambda\in\C\setminus\{0\}`.
5. The false commuting-condition surface `SK=KS` is removed from Definition
   `004034`.
6. The missing ambient-space identifier `B` is inserted in the
   annihilator/quotient-dual proposition.

The first, fourth, fifth, and sixth items are mathematical source repairs; the
six conjunction changes and ordinal localization preserve mathematical
content. Every other ordered top-level math surface is byte-identical after
line-ending normalization. The raw delimiter and brace inventories are
balanced, and all labels, references, citations, and manual tags retain their
original order.

Nine source decisions are bound by inclusive source/target ranges, normalized
snippets, and SHA-256 hashes in
`provenance/SOURCE_CORRECTIONS_CH15.json`:

1. add the nonzero scalar to Alternative I;
2. restrict the scalar in Alternative II;
3. restrict the scalar in Alternative IIIa;
4. remove `SK=KS` from the Riesz--Schauder definition so the definition agrees
   with the chapter's proved invertible-plus-compact characterization;
5. name the ambient Banach space `B`;
6. correct the claim about sums of subspaces: the example shows that a sum of
   two **closed** subspaces need not be **closed**;
7. remove the extra parenthesis in the Fredholm-index index hook;
8. state the standard closed-range, finite-kernel, finite-cokernel convention
   before the finite-dimensional cross-space example; and
9. add the infinite-dimensional hypothesis needed for index surjectivity onto
   `\Z`.

The ledger classifies seven as mathematical source repairs, one as a mechanical
prose/index repair, and one as a formal-scope clarification. The frozen English
authority remains byte-identical. The two source proof hints are translated;
the other proof environments retain their citation-only, cross-reference, or
immediate-implication roles. Because the chapter has no formal exercises or
solutions, no such surface is inferred or invented. No source author or
maintainer was contacted.

## Structure, linkage, rights, and provenance

The source and target retain exact 444-record closure, all four sections, all
60 environment openings and closings, the complete label/reference/citation
order, and the single terminal `\endinput`. All 27 references resolve in the
cumulative Chapter 1--15 reader, and all 17 citation occurrences resolve to
the seven bibliography keys used by the chapter.

The cumulative master retains John M. Erdman's authorship, component credits,
CC BY-SA 4.0 notice, change notice, ShareAlike boundary, non-endorsement, and
the exact model provenance `OpenAI Codex gpt-5.6-sol, Ultra`. Excluded
`TABLE.TEX`, badge artwork, and quotation surfaces remain absent.
