# Chapter 13 pretranslation mathematical review

Date: 2026-08-23  
Unit: `FAOA-2015-CH13`  
Source: `source/upstream/GNS_construction.tex`

## Scope

This is a bounded review of the complete frozen Chapter 13 source before
admission. It records source-facing decisions; it does not alter the frozen
authority bytes. Every applied change must later receive a line-bounded entry
in `provenance/SOURCE_CORRECTIONS_CH13.json` and be checked against the final
target.

## Substantive correction required

The source defines a state of an arbitrary `$C^*$`-algebra by
`$\tau(\vc 1)=1$` and shortly afterward states
`$\lVert\tau\rVert=\tau(\vc 1_A)$` for an arbitrary `$C^*$`-algebra. Chapter
12 explicitly admits nonunital `$C^*$`-algebras, where `\vc 1` need not exist.
The GNS theorem in this chapter is intended to cover the nonunital case as
well.

The Indonesian derivative will therefore use the standard general definition:
a state is a positive linear functional of norm one. It will add that, when
`A` is unital, this is equivalent to `$\tau(\vc 1_A)=1$`. The following
norm-at-the-identity proposition will be restricted explicitly to a unital
`$C^*$`-algebra. This preserves the intended theorem while making its domain
mathematically defined after Chapter 12. It is a transparent derivative
correction, not a claim that the frozen source already says this.

## Mechanical source repairs

- Remove the redundant tail “in `A` for all `a\in A`” from the positivity
  definition while preserving the quantified condition.
- Replace the exercise's doubled final period with one period.
- Complete the GNS notation paragraph with the missing algebra name `A` and
  terminal punctuation.
- Replace “that is.” in the direct-sum definition with ordinary Indonesian
  explanatory punctuation.

## Preserved source choices

- `\tau^\star` and the usual adjoint `\tau^*` remain distinct exactly as the
  caution states.
- `\pi^{\sto}(A)` is an established source macro for the image of `A`; it is
  not rewritten as a correction.
- The final corollary's index command interrupts the sentence typographically
  but does not duplicate the word “is”; the translation will preserve the
  index hook and produce one grammatical Indonesian sentence.
- All labels, references, citation keys, display mathematics, theorem roles,
  the single exercise, and the lack of source answers/solutions remain
  unchanged except for the explicitly classified repairs above.

No upstream contact is made during production. Source authorship, component
credits, CC BY-SA 4.0 obligations, non-endorsement, and the edition provenance
string `OpenAI Codex gpt-5.6-sol, Ultra` remain intact.
