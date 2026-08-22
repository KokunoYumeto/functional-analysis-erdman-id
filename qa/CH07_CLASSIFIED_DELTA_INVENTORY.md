# FAOA-2015-CH07 classified source-to-target delta inventory

Date: 2026-08-22  
Scope: exact bounded comparison of `source/upstream/compact_operators.tex` and
`source/id-ID/compact_operators-id.tex`

## Frozen identities

| Surface | Bytes | Lines/endings | SHA-256 |
|---|---:|---|---|
| Official source member | 21,755 | 517 CRLF | `a1f55b061f526f3e536e5a812f073781777b6f990b662f4a1dba07475152d663` |
| Indonesian target | 22,735 | 517 LF | `8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a` |

Both are BOM-free; the source remains byte-identical to authority. The target
is UTF-8 and ends with exactly one `\endinput`.

## Preserved topology

- Four ordered sections and 72 ordered environment pairs are identical.
- Environment openings: 28 propositions, 17 examples, 11 definitions, nine
  proofs, two theorems, two corollaries, two enumerations, and one exercise.
- The ordered closures retain 20 labels, 13 reference endpoints, eight
  citation calls, 91 index hooks, and 26 defined-term hooks.
- Seven proofs remain explicit proof hints; two remain citation-only proofs.
- Both surfaces contain 309 text-aware math surfaces in the same delimiter
  topology: 301 inline-dollar and eight bracket-display surfaces.
- Three later-source references preserve their identifiers while becoming
  honest pending links: `\futurexref{12.3.16}{00152171}`,
  `\futurexref{12.3.17}{00152181}`, and
  `\futurexref{11.5.7}{X_sqroot_op}`.

## Complete math-edit classification

The sequence comparison has eight edit blocks and no unclassified block.
The two `CSA` blocks form one movement caused solely by natural Indonesian
word order.

| Edit | Source ordinal/surface | Target ordinal/surface | Classification |
|---|---|---|---|
| replace | 69, `$\ofml K(H)$` | 69, `$\ofml K(B)$` | Source correction: the example binds Banach space `B`. |
| delete | 91, `$\cat{CSA}$` | — | First half of a localization-only movement. |
| insert | — | 93, `$\cat{CSA}$` | Second half of the same movement; the math key is byte-identical. |
| replace | 249, `$\alpha \in \K$` | 249, `$\alpha \ge 0$` | Source correction: trace is defined here only on positive operators. |
| replace | 263, `$e^k = Tf^k$` | 263, `$e^k = Uf^k$` | Source correction: the preceding sentence introduces unitary `U`. |
| delete | 267, redundant second `$V$` | — | Repair of the malformed doubled “is … in V is” cone definition. |
| insert | — | 275, `$H$` | Source correction: bind the Hilbert space used in `$\ofml B(H)$`. |
| replace | 309, `$\{e_1 \dots, e_n\}$` | 309, `$\{e_1, \dots, e_n\}$` | Source correction: restore the missing comma. |

The checker locks the exact delimiters and SHA-256 of every source and target
math key for these blocks. Translation inside `\text{...}` would be ignored by
the math key, but this chapter introduces no additional unclassified delta of
that kind.

## Non-math correction and layout closure

The derivative retains both duplicated compactness proposition environments,
but repairs the first copy's “its is complete” wording. It also repairs the
missing article at source line 117, closes the parenthesis at lines 127--129,
naturalizes the duplicated “that” construction at lines 162--165, removes the
stray closing parenthesis at line 299, and changes both malformed “is” clauses
in the cone definition to conditional clauses. The opening pointer to the end
of Chapter 5 is intentional and retained. Three `\allowbreak` controls in the
long polar-decomposition citation proof are invisible layout opportunities,
not content changes.

All eleven source corrections, the three future-reference localizations, and
the citation reflow are recorded in the append-only Chapter 7 block of
`provenance/SOURCE_CORRECTIONS.md`. The cumulative Chapter 1--7 wrapper carries
John M. Erdman's CC BY-SA 4.0 attribution, derivative license, modification
notice, and non-endorsement statement; it uses unchanged `DIAGXY.TEX` and does
not activate `TABLE.TEX` or badge artwork.

Machine authority for this inventory is `qa/check_ch07_translation.py`. The
checker rejects a changed source or target identity, structural drift, any new
math-edit block, endpoint drift, source-defect regression, terminology drift,
visible English or mojibake, local-path residue, or missing rights/correction
closure.
