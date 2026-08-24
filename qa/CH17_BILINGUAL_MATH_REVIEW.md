# Chapter 17 Bilingual and Mathematical Review

Date: 2026-08-24  
Unit: `FAOA-2015-CH17`  
Status: passed; ready for the fixed-path build gate

## Bound identities

- Authority: `source/upstream/K0_functor.tex`, 59,639 bytes, 1,362 CRLF
  records, SHA-256
  `e8ebcaa4e5dbc1cc9b907edb235465610f3bd61e0bfa1ce2f1b5b26e9abf8c6a`.
- Reviewed target: `source/id-ID/K0_functor-id.tex`, 61,673 bytes, 1,362
  LF records, SHA-256
  `061ffd28907e2251fc8b01077888de3e11b3bce67fec1ba52b080c924a241059`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch17.tex`, 10,820 bytes,
  346 LF records, SHA-256
  `51b3f4d790e3d09ac6ac4c160284510e4827140ecaa5a961a46c880ae5c8bb39`.
- Deterministic correction ledger:
  `provenance/SOURCE_CORRECTIONS_CH17.json`, 53,256 bytes, 26 records,
  SHA-256
  `a2b84cfb272a22669920ee0ef4fd015929b353be651cc80700e370c91329257d`.
- Locked translation report: `qa/ch17-translation-report.json`, SHA-256
  `1948b0b3298e70c3fd87df0075b32d6f5db439a44cdc4d1add89096af877697d`.

The fragment assembler, ledger generator, and translation checker each passed
two consecutive replays; the two ledger bytes and the two report bytes were
respectively identical.

## Independent review method

Two read-only reviews were performed after the two contiguous translation
fragments had been assembled. One reviewer read all 1,362 authority/target
record pairs for mathematical meaning, natural Indonesian, controlled terms,
and residue. A second reviewer independently compared structure, formulas,
matrices, diagrams, references, and citations. Neither reviewer edited the
target. Confirmed findings were adjudicated and then applied only to the owned
translation fragments; the assembler regenerated the chapter and cumulative
master.

## Structural and mathematical closure

- Record topology remains exactly 1,362 to 1,362, including the same blank
  record pattern.
- The source and target retain eight sections; 206 balanced environments; 73
  labels; 43 `\ref` calls; four `\eqref` calls; 12 citations; 100 index hooks;
  and 24 defined-term hooks in the same order.
- Environment census is unchanged: 63 propositions, 31 examples, 22
  definitions, 22 proofs, seven notation blocks, two corollaries, one remark,
  one exercise, 46 `bmatrix` blocks, four equations, three `align*` blocks, and
  four enumerations.
- All 46 matrix payloads are token-identical after whitespace normalization.
  All 15 XY diagrams are exact after line-ending normalization.
- The authority has 1,047 parsed math surfaces and the target has 1,048. The
  single additional surface explicitly supplies the corrected
  star-homomorphism category in the example at record 1,104. Every other
  formula delta is classified by a source-correction or localization range;
  the locked checker reports zero unclassified differences.
- All 47 Chapter 17 reference occurrences resolve uniquely in the cumulative
  638-label master. All 12 citation occurrences, using five distinct keys,
  resolve uniquely. The bibliography's duplicate uncited placeholder key is
  unrelated to Chapter 17.

## Confirmed repairs applied

The review repaired natural-language defects at records 4, 256, 636, 657,
667, 741, 794, 828, 847, 1,008, 1,048, 1,052, 1,104, 1,127, 1,221, and 1,306.
It also standardized all 16 hint headings to `Petunjuk untuk bukti`, all
applicable Abelian-group references to `grup Abelian`, the controlled index
form `aljabar-$C^*$`, and the controlled TeX form `homomorfisme-$*\,$`.

The review discovered three substantive source defects not present in the
pretranslation ledger. They are now explicit, independently checkable source
corrections:

1. `FAOA-2015-CH17-CORR-024` (records 144--145): the prose calls the formula
   the converse of the second implication in Proposition `0060221`, but the
   source repeats the forward implication. The target correctly states
   `p \sim q \implies p \sim_u q`.
2. `FAOA-2015-CH17-CORR-025` (records 175--177): the prose calls the formula
   the converse of the first implication, but the source repeats the forward
   implication. The target correctly states
   `p \sim_u q \implies p \sim_h q`.
3. `FAOA-2015-CH17-CORR-026` (records 651--652): the source gives `\tau` the
   codomain `K_0(A)` although its value is `\nu(p)` and `\nu` maps into the
   underlying semigroup of `G`. The target correctly uses `\abs G`.

The review also sharpened existing correction `C006`: block sum is strictly
associative, whereas commutativity holds only up to Murray--von Neumann
equivalence. Existing correction `C021` now consistently identifies the
classified maps and the following example as star-homomorphisms.

Readability-only improvements were accepted at records 180, 209, 323, 1,032,
1,041, 1,094, 1,237, and 1,239. They remove literal English syntax without
changing mathematics, identifiers, or record topology.

## Result

`qa/check_ch17_translation.py` reports `status: pass`, no active English
instructional residue, no mojibake/private-path/credential marker, no missing
or invented exercise/answer/solution surface, no unresolved relation, and
complete rights/model/non-endorsement witnesses. Chapter 17 may proceed to the
two-replay deterministic PDF build and fresh all-page visual inspection. It is
not admitted merely by this review.
