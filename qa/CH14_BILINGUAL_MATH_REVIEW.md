# Chapter 14 bilingual and mathematical review

Date: 2026-08-24  
Unit: `FAOA-2015-CH14`  
Result: **pass for admission**, subject to the cumulative build/backend gates

The complete 687-record upstream chapter and complete 687-record Indonesian
target were reread in source order. The review covered all three sections, 70
environment openings and closings (66 reader-semantic environments plus three
`enumerate` and one `array` environment), 20 labels, 31 references, four
citations, 79 index hooks, 36 defined terms, two exercises, and three proof
environments.

## Linguistic decisions

- Reader prose is natural id-ID and uses the established edition forms
  `aljabar-$C^*$`, `ruang Hilbert`, `modul Hilbert-$A$`, `hasil kali dalam
  semu`, `adjoin`, `operator kompak`, `ideal utama`, `anihilator`, `padat`,
  `unitalisasi`, and `pembenaman`.
- The Chapter 14 terms are internally coherent and meaning-preserving:
  `dapat diadjoinkan`, `aljabar lawan`, `antihomomorfisme`, `ideal esensial`,
  `himpunan nol`, `kompaktifikasi esensial`, `tak terdegenerasi`, and
  `aljabar pengali`.
- The source's warning about calling members of `\ofml K(V)` “compact
  operators” remains explicit: these module operators need not be compact as
  Banach-space operators. The direction-sensitive convention
  `\Theta_{v,w}\colon W\to V` and the family `\ofml K(W,V)` are intact.
- The broader, expressly nonstandard use of “unitization” and
  “compactification” is preserved, including the distinctions among ordinary,
  essential, and maximal essential constructions.
- The permitted English residue is only the cited title *Hilbert C*-modules
  and related subjects---a guided reference overview*. No active English
  instructional prose, rejected `rapat`, mojibake, private path, credential
  marker, or placeholder remains.

The bounded Indonesian external witness already preserved for Chapter 11
supports the edition's core functional-analysis terminology but does not
establish field frequency for every specialized Hilbert-module or
multiplier-algebra compound. Those specialized forms are retained on
mathematical, morphological, and edition-consistency grounds; no unsupported
frequency claim is made.

## Mathematical decisions

The delimiter inventory contains 635 dollar-delimited pairs and 15 display
surfaces, the established 650-surface census. Treating each display as one
nonoverlapping surface (and therefore not double-counting dollar pairs nested
inside display text boxes) gives 644 ordered source surfaces and 644 ordered
target surfaces. Their differences are exhausted by eight machine-checked
transformations:

1. the undefined `f` in the antihomomorphism definition becomes the declared
   `\phi`;
2. one `$A$` surface moves within the same module definition solely to permit
   natural Indonesian predicate order;
3. the impossible inclusion `\iota\colon V\to W` becomes the intended
   inclusion `\iota\colon W\to V`, with `V=A` and `W=J_0` unchanged;
4. three English connectives inside math text become Indonesian `dan`;
5. `if` and `otherwise` inside the displayed piecewise formula become `jika`
   and `selainnya`; and
6. the map surface and the homomorphism-`$*$` descriptor exchange adjacent
   positions solely to express the nondegenerate-homomorphism definition in
   natural Indonesian order.

Every other ordered math surface is byte-identical after line-ending
normalization. The first and third transformations are source corrections;
the other six preserve formulas while localizing embedded prose or reordering
unchanged surfaces for Indonesian grammar.

Nine source repairs are bound by inclusive source/target ranges, normalized
snippets, and SHA-256 hashes in
`provenance/SOURCE_CORRECTIONS_CH14.json`: the `f`/`\phi` identifier repair,
the inclusion reversal, and seven mechanical spacing, punctuation, typography,
grammar, or sentence-joining repairs. The frozen English authority remains
byte-identical.

The two exercises and both proof hints are translated. The third proof remains
the source's citation-only proof. There is no upstream answer or solution
surface; any later mastery support belongs to the separately provenanced O001
layer. No source author or maintainer was contacted.

## Structure, linkage, rights, and provenance

The source and target retain exact 687-record closure, all 70 environment
openings/closings, the complete label/reference/citation order, and the single
terminal `\endinput`. All 31 references resolve in the cumulative Chapter
1--14 reader and all four bibliography keys resolve. The cumulative master
retains John M. Erdman's authorship, component credits, CC BY-SA 4.0 notice,
change notice, ShareAlike boundary, non-endorsement, and the exact model
provenance `OpenAI Codex gpt-5.6-sol, Ultra`. Excluded component surfaces remain
absent.
