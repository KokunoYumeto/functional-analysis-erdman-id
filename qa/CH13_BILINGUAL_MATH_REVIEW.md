# Chapter 13 bilingual and mathematical review

Date: 2026-08-24  
Unit: `FAOA-2015-CH13`  
Result: **pass for admission**, subject to the cumulative build/backend gates

The complete 289-record upstream chapter and complete 289-record Indonesian
target were reread in source order. The review covered all three sections, 32
environment openings, seven labels, two references, seven citation
occurrences, 28 index hooks, 13 defined terms, two proofs, and the single
exercise.

## Linguistic decisions

- Reader prose is natural id-ID and uses the established edition forms
  `padat`, `swaadjoin`, `hasil kali dalam semu`, `jumlah langsung`, and
  `aljabar-$C^*$`.
- New specialized forms are internally coherent: `keadaan` (*state*),
  `keadaan vektor`, `representasi`, `tak terdegenerasi`, `setia`, `siklik`,
  `vektor siklik`, `kernel kiri`, and `konstruksi GNS`.
- `keadaan` receives a stable technical-term record and English recognition
  variant so that it is not confused in the backend with ordinary prose using
  the same word.
- No active English instructional prose, rejected `rapat` variant, mojibake,
  doubled period, private workstation path, or placeholder remains.

The bounded Indonesian external witness already preserved for Chapter 11 does
not attest these GNS-specific compounds. They are retained because they express
the mathematics directly and consistently; no unsupported field-frequency
claim is made.

## Mathematical decisions

The source has 237 top-level math surfaces and the target 239. All differences
are exhausted by four ordered, machine-checked edit blocks:

1. the redundant positivity quantifier is consolidated without changing its
   domain or order condition;
2. the undefined nonunital identity condition is replaced by the positive
   norm-one definition of a state, with the identity criterion retained as the
   unital equivalent;
3. the following norm-at-the-identity criterion is explicitly restricted to a
   unital algebra (no formula token changes);
4. the missing algebra name `A` is restored in the GNS notation paragraph.

Every other math span is byte-identical after line-ending normalization. The
source/target snippets and hashes for all six applied repairs are bound in
`provenance/SOURCE_CORRECTIONS_CH13.json`. `\tau^\star` remains distinct from
`\tau^*`; `\pi^{\sto}(A)` remains the source image notation; labels, references,
citation keys, and the three direct-sum constructions remain intact.

The single exercise is translated and still has no upstream hint, answer, or
solution. Its future support belongs to the separately provenanced O001 layer.
No source author or maintainer was contacted.

