# FAOA-2015-CH11 source inventory

Date: 2026-08-23  
State: **source frozen; complete target prepared; admission evidence recorded
and awaiting backend reconciliation**  
Unit: FAOA-2015-CH11 / advanced continuation (the complete corpus remains
17 chapters)

This is a bounded Chapter 11 inventory. It does not translate or normalize the
upstream member, does not edit the backend or lane controls, and does not
contact the author. The source-order cursor after the admitted Chapter 10
boundary is this unit.

## Exact source identity

- Source path: source/upstream/Gelfand_Naimark.tex.
- Upstream title: THE GELFAND-NAIMARK THEOREM.
- Source member identity: **32,235 bytes, 788 CRLF records, ASCII,
  SHA-256 018f15db7ee5a4392f624af050507a90339e1469e30f97c6017e003c7ff33b26**.
- The final physical record is line 788, \endinput, terminated by CRLF. No
  source content follows it.
- The frozen authority row is also present in provenance/SOURCE_MANIFEST.csv
  (2,443 bytes; SHA-256
  e222e326d8ff5fcd30b66b3b44642043295e1cb39920c58ff353eaafafd276d1).
- The existing backend unit record is FAOA-2015-CH11, order 11,
  translation_state queued, rights_id RIGHTS-ERDMAN-CC-BY-SA-4.0. Its current
  source identity is 32,235 bytes / 788 lines / the hash above.

The current contiguous target is retained as the Chapter 11 admission
candidate:

- source/id-ID/Gelfand_Naimark-id.tex;
- 32,551 bytes, 764 LF records, SHA-256
  69bd9ba794ef0d5eb74e444cf2676878b7797e5dd5b75fcfc4abdd247b1b5ee5;
- it covers all five source sections (including the Gelfand transform,
  unital C*-algebra, and final theorem sections). Structural math replay and
  the cumulative PDF visual/build gate pass; final admission remains gated on
  backend reconciliation and the signed Chapter 11 receipt.

## Source order and section boundaries

The chapter title and five sections occur in this exact order:

1. THE GELFAND-NAIMARK THEOREM, line 1, controlled title **Teorema
   Gelfand--Naimark**;
2. Maximal Ideals in C(X), lines 9--62, controlled title **Ideal-Ideal
   Maksimal dalam C(X)** (the provisional target uses this plural form);
3. The Character Space, lines 63--334, controlled title **Ruang Karakter**;
4. The Gelfand Transform, lines 335--555, controlled title **Transformasi
   Gelfand**;
5. Unital C*-algebras, lines 556--656, controlled title **Aljabar-C*
   Beridentitas**;
6. The Gelfand-Naimark Theorem, lines 657--788, controlled title **Teorema
   Gelfand--Naimark**.

The complete target preserves all five sections in source order. The source
correction ledger is provenance/SOURCE_CORRECTIONS_CH11.json; the external
Indonesian terminology witness and reader audit are recorded separately under
qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md and
qa/CH11_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md.

## Structural and mathematical census

The source has 107 balanced begin/end environment pairs. The ordered begin
census is:

| Environment | Count |
|---|---:|
| prop | 35 |
| cor | 19 |
| exam | 15 |
| defn | 10 |
| thm | 4 |
| proof | 12 |
| enumerate | 7 |
| bmatrix | 4 |
| notn | 1 |
| **total** | **107** |

Thus there are 83 theorem-like surfaces (35 propositions, 19 corollaries,
15 examples, 10 definitions, and four theorems). There are 604 inline-dollar
math pairs and 21 bracket-display surfaces, for 625 mathematical surfaces;
there are no equation environments. The source contains 38 unique labels,
15 unique reference calls (11 labels local to this chapter and four
cross-chapter endpoints: spectrum, C073147, C029717, and def_norm_alg), five
citation calls over four keys, 65 index calls (65 distinct raw hooks), and 21
defined-term calls (21 distinct \df terms).

Citation call census:

- Semadeni:1971 — one call;
- BaggettF:1979 — two calls;
- HewittS:1965 — one call;
- Douglas:1972 — one call.

Every label and reference must remain stable in the Indonesian target. The
cross-chapter endpoints already have source-order owners in Chapters 2, 3, and
8; no later-chapter endpoint is introduced here.

## Learning-support and proof census

- Explicit exercise environments: **zero**. The word “exercise” occurs once
  only as the locator “exercise 18.45” in a citation-only proof pointer; that
  is not an Erdman exercise in this chapter.
- Upstream answers or solutions: **zero**.
- Proof environments: 12 total.
- Proof hints: nine, at source lines 99, 112, 172, 183, 192, 205, 607, 718,
  and 768.
- Citation-only proof pointers: three, at lines 452, 519, and 666
  (BaggettF:1979, HewittS:1965, and Douglas:1972 respectively).
- Inline exercise/hint surfaces outside environments: none.

The target must preserve the distinction between a hint, a citation-only
pointer, an example, and an absent solution. No Chapter 11 exercise should be
invented or attributed to Erdman. The global O001 mastery layer can add
separately provenanced support later, but this source contributes no explicit
exercise objects.

## Includes, diagrams, and accessibility

There are zero \input, \include, \includegraphics, or \epsfbox calls and no
external image member. The chapter contains one inline Xy-pic diagram at
lines 474--478: a btriangle with nodes \T, \Delta l_1(\Z), and \C, labelled
by \psi, G_a, and \Gamma_a. It depends on the established DIAGXY.TEX/Xy-pic
macro surface.

If used, DIAGXY.TEX remains byte-identical under its separate component
notice. The reader/HTML backend must retain the diagram's topology and add a
meaningful accessible text description of the character-space/Gelfand-
transform triangle; it must not flatten the diagram into an unlabelled image.
Standard TeX packages and fonts remain build dependencies rather than chapter
components.

## Source-review candidates (no repairs applied here)

These are high-confidence candidates for the later Chapter 11 correction
ledger. This inventory records them without changing authority bytes:

| Candidate | Class | Observation and proposed handling |
|---|---|---|
| Gelfand_Naimark.tex:205 | mechanical | “Use corollary \ref{C073147} Why...” lacks punctuation before the question. Insert a sentence boundary in the target/source-correction layer, preserving the reference. |
| Gelfand_Naimark.tex:470 | mechanical | “these two compact Hausdorff space” has singular agreement; render as “spaces” in the corrected target. |
| Gelfand_Naimark.tex:479--480 | mathematical/notation | The sum is indexed by k but the summand is a_n z^n. The displayed identity for G_a must use a_k z^k (the provisional target already reflects this, but it is not yet an admitted correction). |
| Gelfand_Naimark.tex:519 | mechanical | The citation closes as “exercise 18.45.)”, with an unmatched right parenthesis. Remove only the stray punctuation. |
| Gelfand_Naimark.tex:750 | mechanical | “whose spectrum is is contained” duplicates “is”; remove one copy. |

Review-only cautions, not presently classified as errors:

- The Fourier-series display at line 485 uses the closed endpoint \pi while
  the function is represented on [-\pi,\pi); this is an endpoint convention
  and should not be silently changed.
- The spectral-mapping proposition at lines 754--759 is deliberately stated
  for self-adjoint a; do not broaden it to all normal elements without a
  source-level decision.
- C*(I,T) at lines 739--740 is identity-operator notation for the established
  C*(1,T) construction; preserve the mathematical meaning and normalize only
  reader typography.

No candidate above has been sent upstream. Any eventual report remains
subject to the single post-corpus authorization.

## Rights and provenance boundary

The chapter is part of Erdman's substantive CC BY-SA 4.0 work. The derivative
must retain attribution to John M. Erdman, a license link, a clear change
notice, ShareAlike, no additional restrictions, and non-endorsement. No
separate chapter component notice occurs in this member. Preserve the
DIAGXY.TEX notice if the inline diagram is retained; do not relicense standard
packages or fonts as corpus text. No external quotation is imported by the
three citation-only proofs.

The lane's explicit model provenance remains
**OpenAI Codex gpt-5.6-sol, Ultra**, recorded in
provenance/TRANSLATION_MODEL_PROVENANCE.md. That model note does not replace
Erdman, component authors, or human-direction credits.

## Next executable boundary

Reconcile the Chapter 11 machine ledger against the complete target, bind the
build/render/terminology evidence into a signed Chapter 11 receipt, and run the
append-only backend validator before admission. Preserve all 107 environment
pairs, 38 labels, 15 references, five citation calls, 65 index hooks, 21
defined-term hooks, the single Xy-pic diagram, and the nine hint / three
citation-only proof roles. This inventory itself does not authorize upstream
contact or publication.
