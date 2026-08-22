# FAOA-2015-CH08 independent bilingual review

Date: 2026-08-22  
Reviewer scope: bounded Chapter 8 rereview only  
Disposition: PASS after two bounded repairs

## Exact coverage

- Read and compared every active line 1--603 of
  `source/upstream/spectrum.tex` against every line 1--603 of
  `source/id-ID/spectrum-id.tex`, including prose, inline and displayed
  mathematics, theorem-like environments, enumeration items, exercises,
  proof hints, labels, references, citations, index entries, defined-term
  hooks, and `\endinput`.
- Read `00_control/CH08_TERMINOLOGY.md` lines 1--70 and checked every locked
  carry-forward and Chapter 8 decision against the target.
- Read `00_control/CH08_PRETRANSLATION_INVENTORY.md` lines 1--91 and checked
  all eight adjudicated source corrections individually.
- Checked the six current assembly members with exact line coverage
  1--129, 130--229, 230--332, 333--426, 427--526, and 527--603.
- The frozen upstream identity independently matches 25,716 bytes, 611 LF
  records, and SHA-256
  `ae68cf224c6218ecd501cc983428cf924a3c361c6324a6b40793b1e9ba44b4dd`;
  active content ends at the single `\endinput` on line 603.

## Bilingual and mathematical findings

The Indonesian text is mathematically faithful and reads as natural,
professional id-ID. The complex-scalar convention, logical quantifiers,
hypotheses, conclusions, examples, both exercises, all twelve proof hints,
the one proof comment, and the one full proof are preserved. Controlled terms
remain distinct where required, notably `invertibel kiri/kanan` versus `invers
kiri/kanan`, `pemetaan resolven` versus `himpunan resolven`, and the four
operator-spectrum parts.

Two clear defects were repaired in both the target and the corresponding
`part_0527_0603.tex` assembly member:

1. Target line 547 now uses the correction-ledger canonical set notation
   `$A = \{a_k\colon k\in\N\}$.`, replacing `:` and `\mathbb N`.
2. Target line 578 now uses the locked term `spektrum titik aproksimatif`,
   replacing the inconsistent `spektrum titik hampiran`.

No other unambiguous fidelity, fluency, terminology, exercise/hint, or
mathematical defect remains in the active chapter.

## Eight source-correction checks

1. The missing source space at line 17 is repaired naturally in the Indonesian
   definition.
2. Target lines 178--180 explicitly quantify a nonzero complex `\lambda`.
3. Target line 348 has no stray parenthesis after `\ref{C073134}`.
4. Target line 372 uses the matched delimiter `\bigl(\rho(a)\bigr)^n`.
5. Target lines 396--399 treat Example `\ref{000319}` as the formula precedent
   and separately define the Volterra operator on `\fml C([0,1])` by
   `Vf(x)=\int_0^x f(t)\,dt`.
6. Target line 443 binds the Hilbert space `H` and places
   `T \in \ofml B(H)` before the equivalences involving `S` on `H`.
7. Target line 509 supplies `Teorema Pemetaan Spektral` as the optional theorem
   title and preserves `\label{SMThm}` and the statement.
8. Target line 547 uses exactly `A = \{a_k\colon k\in\N\}`.

## Control-surface and assembly verification

- Source and target have the same ordered sequence of 192 environment control
  tokens: 96 balanced openings and 96 closings. Openings comprise 33
  propositions, 14 examples, 14 proofs, 8 definitions, 8 corollaries, 4
  theorems, 2 exercises, 1 notation block, 10 enumerations, and 2 matrix
  environments.
- Ordered control sequences match for all 28 labels, all 16 reference calls,
  all 3 citations, and all 34 item markers. Counts also match for all 73 index
  hooks and all 20 defined-term hooks.
- The target retains 15 balanced displayed-math delimiter pairs and both matrix
  environments. A direct math-segment comparison found only translation-order
  movement and the explicitly adjudicated correction changes; there was no
  unexplained formula loss or alteration.
- `qa/assemble_ch08.py` was updated with the repaired final-slice hash and ran
  successfully. The assembled chapter is byte-for-byte the ordered
  concatenation of the six LF-only, BOM-free slices and has 603 LF records.
- After the bilingual review, deterministic build inspection identified two
  small overfull paragraphs at target lines 399 and 525. Both were rephrased
  more compactly in natural Indonesian without changing any mathematical
  surface: the Volterra operator is now introduced “melalui rumus”, and the
  redundant article before “operator invertibel” was removed. These are
  reader-facing layout reflows, not source corrections.

Final slice SHA-256 values:

1. `part_0001_0129.tex`:
   `fb667da0c0ebf21caab7e4a4cc058184cf79ec6d23643e9ffe5005066cd7d051`
2. `part_0130_0229.tex`:
   `4365fc9305c302429528e2f7299b7bf6efb3769f8dafb197e79e5b3b23aacc23`
3. `part_0230_0332.tex`:
   `ba7901369ae580d1e05c115a39290dcdd3d05d6d074b25e389bf14e6ace11f2b`
4. `part_0333_0426.tex`:
   `dd9fa50c84771cb708ccddc89f9d8248c4e408905cf14c39e5579d1f4c10b640`
5. `part_0427_0526.tex`:
   `1b1b719a240b473b89589ef9e8a302ee066435ec2c6e1419f3d9434d96412c01`
6. `part_0527_0603.tex`:
   `5f73a02638be685d46b7e5620247a373ef383361168c2b5fecb6d1212f6af3ac`

Final assembled identities:

- `source/id-ID/spectrum-id.tex`: 26,947 bytes, 603 LF records, SHA-256
  `1120da36ebd0793690ecb47b33b921c81376d1bf7d2f03d9821b79356dfd03bc`.
- `source/id-ID/functional-analysis-id-through-ch08.tex`: 9,714 bytes, 334 LF
  records, SHA-256
  `d0b4130b9fa6f85baef22f316ea914d5519bf30d6e82d8e6d824f2cf211c1998`.

No Git operation or upstream contact was performed.
