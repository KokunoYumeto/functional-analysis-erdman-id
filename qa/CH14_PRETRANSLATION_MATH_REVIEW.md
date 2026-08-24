# Chapter 14 pretranslation mathematical review

Date: 2026-08-24  
Unit: `FAOA-2015-CH14`  
Source: `source/upstream/multiplier_algebras.tex`

## Scope

This is a bounded, line-by-line mathematical review of the complete frozen
Chapter 14 source before translation. It records source-facing decisions but
does not alter the authority bytes. Every applied change must later receive a
line-bounded entry in the Chapter 14 correction ledger and must be checked
against the assembled target.

## Substantive correction required

At lines 229–234 the source sets `V=A` and `W=J_0`, then calls
`\iota\colon V \sto W` an inclusion. Since `J_0` is the proper ideal of
functions vanishing at zero, there is no inclusion from `A` into `J_0`. The
intended standard example is the bounded `A`-linear inclusion
`\iota\colon W\sto V`, namely `J_0\hookrightarrow A`, which is not
adjointable. The non-adjointability assertion is correct after that reversal:
an adjoint would have to send the constant function one to a member of `J_0`
that agrees with one on `(0,1]`, contradicting continuity at zero.

The derivative must therefore reverse the displayed domain and codomain while
preserving `V=A`, `W=J_0`, the example role, and all nearby references. This is
a mathematical correction, not a translation choice.

## Semantic identifier repair

The antihomomorphism definition at lines 75–78 introduces
`\phi\colon A\sto B` but then says that the function `f\colon A\sto
B^{\mathrm{op}}` is a homomorphism. No `f` has been defined in that
environment. Replace `f` by `\phi`; the intended definition and the following
anti-isomorphism sentence are otherwise correct.

## Mechanical source repairs

- Insert the missing space in `means,when` at line 103.
- Replace the literal equals sign in `$C^*$=algebra` at line 231 with the
  normal hyphenated `$C^*$-algebra` form.
- Supply the missing sentence stop after “Hilbert `$A$`-modules” at line 209.
- Render “has lead” at line 312 as the intended past tense “has led” in the
  Indonesian prose.
- Join the sentence fragment at lines 413–414: “If `$A$` and `$B$` are
  nonempty subsets of an algebra, by `$AB$` ...”.
- Add the grammatically required commas around “if it exists” in the two
  propositions at lines 641 and 645.

These repairs change neither mathematical content nor source topology. The
frozen English source remains byte-identical.

## Nontrivial statements independently checked and preserved

1. The right-Hilbert-module convention is internally consistent: the
   `$A$`-valued inner product is linear in its second variable, conjugate
   linear in its first, and satisfies
   `\langle va\mid w\rangle=a^*\langle v\mid w\rangle`.
2. The Schwarz-inequality hint is sound. After normalizing
   `\lVert\langle x\mid x\rangle\rVert=1`, positivity and
   `0\leq\langle x\mid x\rangle\leq 1` applied to
   `\langle xa-y\mid xa-y\rangle` with
   `a=\langle x\mid y\rangle` yield the stated order inequality.
3. The adjointable-map definition legitimately begins with an arbitrary
   function: the adjoint identity forces linearity and `$A$`-linearity, while
   the following proposition supplies boundedness. Do not silently add those
   properties to the definition.
4. `\Theta_{v,w}` maps `W` to `V`; consequently the text's
   `\ofml K(W,V)` at lines 279–283 is correct. The generic index token
   `\ofml K(V,W)` does not authorize reversing the mathematical arguments.
5. The formula defining `I_c` does not explicitly contain a scalar multiple
   of `c` in a nonunital algebra. This is not a defect in the subsequent
   `$C^*$`-algebra proposition: an approximate identity places `c` in
   `\overline{Ac}`, so `J_c=\overline{I_c}` remains correct. Do not add an
   unproven algebraic equality or alter the displayed set.
6. For ideals of a `$C^*$`-algebra,
   `\overline{IJ}=I\cap J`, the annihilator criterion for essentiality, and
   `(J\oplus J^\perp)^\perp=0` are correct as stated.
7. Extending each `f\in C_0(X)` by zero from an open locally compact `X` in a
   compact Hausdorff `Y` is continuous. The correspondence “essential ideal
   iff `X` is dense in `Y`” is therefore valid in the stated setting.
8. The broader use of “unitization” for any unital embedding is explicitly
   declared nonstandard. Preserve both that warning and the later distinction
   between an arbitrary unitization, an essential unitization, and a maximal
   essential unitization.
9. The extension proposition at lines 657–662 is type-consistent, and the
   final identification `M(A)=\ofml L(A)` is the standard multiplier-algebra
   construction for the Hilbert `A`-module `A`. No restriction to nonunital
   `A` should be inserted: for unital `A`, the construction reduces to `A`.

No additional mathematical correction was found in the 650 top-level math
surfaces.

## Terminology and backend safeguards

The admitted backend through Chapter 13 fixes the following relevant forms:

- `adjoint` → `adjoin` (`TERM-ADJOINT`);
- `morphism` → `morfisme` (`TERM-MORPHISM`);
- `compact` → `kompak` (`TERM-COMPACT`);
- `Hilbert space` → `ruang Hilbert` (`TERM-HILBERT-SPACE`);
- `semi-inner product` → `hasil kali dalam semu`
  (`TERM-SEMI-INNER-PRODUCT`);
- `closed linear span` → `rentang linear tertutup`
  (`TERM-CLOSED-LINEAR-SPAN`);
- `unitization` → `unitalisasi` (`TERM-UNITIZATION`);
- `algebraic ideal` → `ideal aljabar` (`TERM-ALGEBRAIC-IDEAL`);
- `annihilator` → `anihilator` (`TERM-ANNIHILATOR`);
- `direct sum` → `jumlah langsung` (`TERM-DIRECT-SUM`);
- `nondegenerate` → `tak terdegenerasi`
  (`TERM-NONDEGENERATE-REPRESENTATION`);
- `dense` → `padat`; do not reintroduce the rejected alternate `rapat`.

Chapter 14 will need new, separately registered stable terms for the Hilbert
`A`-module, `$A$`-valued inner product, adjointable map, compact module
operator, essential ideal, essential compactification, and multiplier algebra.
Their final Indonesian forms belong in the Chapter 14 terminology plan rather
than being improvised independently by parallel translators. In particular,
“compact operator” in the Hilbert-module passage must retain the author's
warning that it need not be compact as a Banach-space operator.

All 20 labels, 31 references, four citations, 79 index hooks, two exercises,
three proof environments, and the source's lack of answers/solutions must be
preserved. No upstream contact is made during production. Source authorship,
component credits, CC BY-SA 4.0 obligations, non-endorsement, and the exact
edition provenance string `OpenAI Codex gpt-5.6-sol, Ultra` remain intact.
