# Chapter 15 pretranslation mathematical review

Date: 2026-08-24  
Unit: `FAOA-2015-CH15`  
Source: `source/upstream/fredholm_theory.tex`

## Scope and decision classes

This is a bounded mathematical review of every source record and all 203
top-level math surfaces. It does not alter the frozen authority bytes. The
items below distinguish certain mathematical defects, formal scope gaps, and
mere style. Every substantive derivative change must receive a line-bounded
correction-ledger record and be verified against the assembled target.

## Certain defect 1: the scalar must be nonzero

Fredholm Alternative I (lines 10–32) uses `\lambda` without quantifying it.
Alternatives II (lines 43–66) and IIIa (lines 72–81) explicitly allow every
`\lambda\in\mathbb C`. All three statements require
`\lambda\in\mathbb C\setminus\{0\}`.

This is necessary, not cosmetic. For Alternative I, choose the zero kernel and
`\lambda=0`; the homogeneous equation then has an infinite-dimensional
solution space, contrary to the stated finite alternative. For II and IIIa,
let `K` on `\ell^2` be the compact diagonal operator
`K(x_n)=(x_n/n)`. With `\lambda=0`, `T=-K` is injective but not surjective and
has dense nonclosed range. This directly contradicts both the
injective-if-and-only-if-surjective claim and
`\operatorname{ran}T^*=(\ker T)^\perp`.

Required correction:

- add a fixed `\lambda\in\mathbb C\setminus\{0\}` to Alternative I;
- replace `\lambda\in\mathbb C` by
  `\lambda\in\mathbb C\setminus\{0\}` in Alternatives II and IIIa.

All twelve manually tagged equations and their labels remain unchanged.

## Certain defect 2: undefined ambient Banach space

At line 123, `M` is said to be a closed subspace of “a Banach space,” but the
conclusion uses the undefined symbol `B` in `(B/M)^*`. The proposition must
begin: “If `M` is a closed subspace of a Banach space `B`, then ...”. The
canonical annihilator/quotient-dual isomorphism is correct after `B` is named.

## Certain defect 3: the sum is a nonclosed subspace, not a non-subspace

Lines 150–157 assert that the sum of two subspaces may fail to be a subspace.
The sum of any two linear subspaces is always a linear subspace. In the stated
example, with `M=H\oplus0` and `N=\operatorname{graph}T`, direct calculation
gives

`M+N=H\oplus\operatorname{ran}T`.

The diagonal operator in lines 142–148 has dense, proper, nonclosed range.
Thus `M+N` is a dense nonclosed linear subspace of `H\oplus H`. Required
correction:

- line 151: “the sum of two **closed** subspaces ... need not be **closed**”;
- lines 153–157: `M` and `N` are closed subspaces, but `M+N` is not closed;
- line 154 index hook: index nonclosed sums of closed subspaces, rather than
  claiming that their sum is not a subspace.

The four-part proposition at lines 164–172 is correct and supplies the same
verification.

## Certain defect 4: index surjectivity needs an infinite-dimensional space

The proposition at lines 300–303 says for every Hilbert space `H` that the
index maps `\mathfrak F(H)` onto `\mathbb Z`. This fails in finite dimension:
rank-nullity gives index zero for every endomorphism of a finite-dimensional
space. The proof hint's unilateral shift also lives on an infinite-dimensional
space. Add the hypothesis that `H` is infinite-dimensional. The semigroup law
and additivity of the index are otherwise correct.

## Certain defect 5: the Riesz–Schauder definition conflicts with Alternative VI

Definition `004034` (lines 101–106) requires
`T=S+K`, with `S` invertible, `K` compact, **and `SK=KS`**. Corollary
`0047253` (lines 372–378) claims conversely that every index-zero Fredholm
operator is Riesz–Schauder. Proposition `004712` yields only an
invertible-plus-finite-rank decomposition; it does not supply commutation, so
the displayed proof does not prove the converse.

The converse is false under the stated commutation requirement. Let `U` be the
unilateral shift and set `T=U\oplus U^*` on `\ell^2\oplus\ell^2`. Then `T` is
Fredholm of index `-1+1=0`. If `T=S+K`, `S` were invertible, `K` compact, and
`SK=KS`, then `K` would commute with `T`. In block form its upper-left block
`A` would be a compact operator commuting with `U`, hence `A=0`, while its
upper-right block `B` would satisfy `UB=BU^*`, hence `B=0` by induction from
`U^*e_0=0`. The first component of `(T-K)(x,y)` would therefore always be
`Ux`, so `S=T-K` could not be surjective. This is a contradiction.

The source cannot be admitted with both statements unchanged. The correction
most consistent with the chapter's later phrase “invertible plus compact” is
to remove `SK=KS` from definition `004034` and transparently define the class
used here as compact perturbations of invertibles. Then Alternatives IIIb–VI
follow from index-zero Fredholm theory. If the commuting definition must be
preserved instead, Alternative VI must be weakened to the one-way implication
already stated in Alternative V. This is a substantive editorial decision,
not a translation variant.

## Formal scope gaps requiring explicit handling

- Alternative I never states the function space containing `f`, `g`, `h`, and
  `j`. The continuous-kernel formula works in standard Fredholm settings, but
  the derivative must not silently alternate between `C([0,1])` and
  `L^2([0,1])`. Bind one intended setting in a transparent editorial note or
  preserve the omission as a documented source limitation.
- The definition at lines 208–225 introduces Fredholm operators only as
  endomorphisms of one Hilbert space via its Calkin algebra. Lines 268–270 then
  call every map `V\to W` between finite-dimensional spaces Fredholm. The
  formula is mathematically correct under the standard broader definition
  (closed range with finite-dimensional kernel and cokernel), but that broader
  convention has not been introduced. Add an explicit scope sentence rather
  than leaving the term formally unsupported.
- In finite dimension the Calkin algebra is the zero quotient, so the exact
  convention for invertibility in the zero algebra affects the quotient-based
  wording. Atkinson's finite-kernel/cokernel characterization and the index
  formula avoid that convention issue.

## Checked statements that should not be altered

1. With `\lambda\ne0`, Alternatives II and IIIa have closed range and the
   kernel/range/adjoint identities stated in the source.
2. Alternative IIIb and IV are valid for an invertible-plus-compact operator;
   commutation is unnecessary for those conclusions.
3. A bounded Hilbert-space map with finite-dimensional cokernel has closed
   range, so Atkinson's theorem does not need a separate closed-range clause in
   this chapter's sequence of results.
4. The exact kernel–cokernel sequence at lines 286–291 and its alternating
   dimension formula are correct; the connecting maps are canonical even
   though the source does not spell them out.
5. Normal Fredholm operators have index zero, and compact perturbations
   preserve both Fredholmness and index.
6. The norm-ball path at lines 410–415 stays inside the invertible group by the
   Neumann-series estimate. Path connectedness is an equivalence relation, and
   the Fredholm path components are classified by index in the intended
   infinite-dimensional complex Hilbert-space setting.

## Mechanical and stylistic matters

- Remove the extra closing parenthesis from the index hook at line 249.
- “Their difference however” at line 245 may receive normal Indonesian
  punctuation; this is style only.
- The doubled spaces and long physical source records may be reflowed without
  correction-ledger status provided labels, formula tokens, and source-record
  mappings remain lossless.
- The historical prose and the author's names for Alternatives I–VI are
  preserved, but a false theorem may not be retained merely to keep its title.

There are no formal exercises, answers, or solutions to preserve. All 33
labels, 27 references, 17 citations, 46 index hooks, eight examples, thirteen
proof environments, and two explicit proof hints remain mapped. No upstream
contact is made during production; the frozen source, attribution, CC BY-SA
4.0 obligations, non-endorsement, and exact model provenance remain intact.
