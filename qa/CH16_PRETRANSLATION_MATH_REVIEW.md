# Chapter 16 pretranslation mathematical review

Date: 2026-08-24  
Unit: `FAOA-2015-CH16`  
Source: `source/upstream/extensions.tex`, records 1--1,000

## Scope and method

This review covers every source record, all four active sections, all 124
reader-semantic environments, and all 702 active top-level math surfaces. It
does not alter the frozen authority bytes. The review checks type consistency,
hypotheses, map directions, categorical roles, internal theorem dependencies,
formula notation, and exact cross-reference/citation surfaces. It distinguishes
certain defects, formal scope gaps, mechanical repairs, and style-only matters.

The target must preserve all 142 environments, 36 unique labels, 28 references,
59 citations, 107 index hooks, 29 `\df` hooks, 26 bracket displays, four
equation environments, four active sections, and the source order. Every
substantive derivative change below needs a source-correction ledger record.

## Certain defect 1: the unitary conjugation is ill-typed

Records 42--58 declare

- `S\in\ofml B(H)`;
- `T\in\ofml B(K)`; and
- `U:H\to K`, hence `U^*:K\to H`.

The source then writes `S-UTU^*` and `S=UTU^*`. But `UTU^*` acts on `K`
(and, under right-to-left composition, the middle composition is not even
typeable as written with this direction of `U`), whereas `S` acts on `H`.
The conjugate of `T` acting on `H` is `U^*TU`.

Required correction in both the essential and ordinary unitary-equivalence
clauses:

- `S-UTU^*` -> `S-U^*TU`;
- `S=UTU^*` -> `S=U^*TU`.

The alternative repair would reverse the declared direction of `U`, but that
would conflict with `U\in\ofml B(H,K)`, `U^*U=I_H`, and `UU^*=I_K` in the
same definition. Correcting the two conjugation formulas is therefore the
minimal coherent repair.

## Formal scope defect 2: proposition `005134` needs equal Hilbert dimension

Records 61--63 say that self-adjoint operators on separable Hilbert spaces are
essentially unitarily equivalent exactly when their essential spectra agree.
The statement cannot include arbitrary finite-dimensional spaces of different
dimensions: for example, self-adjoint operators on `\mathbb C` and
`\mathbb C^2` have empty essential spectrum under the finite-dimensional
Calkin convention, but no unitary map exists between the spaces.

The standard intended setting is two separable infinite-dimensional Hilbert
spaces, which are unitarily isomorphic. The derivative should state that scope
explicitly in proposition `005134`. Merely relying on the boxed convention at
records 407--411 is insufficient because that convention begins only in the
third section, after this proposition.

## Certain defect 3: Voiculescu's theorem omits the map class

Records 886--891 introduce `\phi:A\to\ofml B(H)` with no linearity,
positivity, or normalization hypothesis and conclude `\phi\lesssim\mathbf r`.
As written, this is false. Take `A=\mathbb C`, let `H_0=H` be infinite
dimensional, set `\mathbf r(\lambda)=\lambda I`, and set
`\phi(\lambda)=2\lambda I`. The antecedent holds because `\lambda I` is
compact only for `\lambda=0`. But any isometry `V` satisfies

`\phi(1)-V^*\mathbf r(1)V=2I-I=I`,

which is not compact. Even complete positivity without unitality is therefore
insufficient. The surrounding Stinespring/absorption development and the
standard Voiculescu formulation require `\phi` to be a **unital completely
positive linear map**. Add that exact hypothesis; preserve all other
hypotheses and the relation `\lesssim`.

## Certain defect 4: a semisplit lifting is completely positive, not multiplicative

The prose at records 909--912 correctly announces a “completely positive
lifting.” Proposition `0058411` at records 914--924 instead asks for a unital
star-homomorphism `\widetilde\tau:A\to\ofml B(H)`. A star-homomorphic
lifting would make the extension split, not merely semisplit.

The chapter itself supplies an internal contradiction if the displayed
statement is retained: the concrete Toeplitz extension is an abstract Toeplitz
extension and hence semisplit, while proposition `005253` states that it does
not split. The criterion must be:

- `\tau` is a **unital** star-monomorphism (the class for which “semisplit”
  was defined); and
- there exists a **unital completely positive linear map**
  `\widetilde\tau:A\to\ofml B(H)` such that
  `\pi\circ\widetilde\tau=\tau`.

This repair restores agreement among the preceding sentence, the semisplit
definition, Stinespring dilation, and the later nuclear lifting theorem.

## Complete correction-ledger candidate table

| Candidate | Source records | Class | Exact target action |
|---|---:|---|---|
| `CH16-C001` | 13 | mechanical TeX | insert separation after `\begin{prop}` before translating `If` |
| `CH16-C002` | 42--58 | mathematical/type | replace both `UTU^*` conjugations by `U^*TU` while retaining `U:H\to K` |
| `CH16-C003` | 61--63 | formal scope | state that the two separable Hilbert spaces are infinite-dimensional (or, equivalently for the theorem, unitarily isomorphic) |
| `CH16-C004` | 254--257 | notation | use the established Calkin-algebra form `\ofml Q(H^2)`, not plain `Q(H^2)` |
| `CH16-C005` | 256 | mechanical prose | translate “establishes **and** isomorphism” as the intended “establishes **an** isomorphism” |
| `CH16-C006` | 298--305, especially 301 | map identity | call `T`, not `\beta`, the continuous/isometric section; `\beta\circ T=I` makes `T` the right inverse |
| `CH16-C007` | 312--314 | bibliography | normalize the visibly split Douglas theorem number `7.2 6` to `7.26`, also cited coherently at record 354 |
| `CH16-C008` | 344--345 | mathematical notation | replace both `\pi^1(\C\setminus0)` forms by `\pi_1(\C\setminus\{0\})` |
| `CH16-C009` | 407 | stale index locator | replace “after section 9.2” by a locale-neutral locator such as “from Addition of Extensions onward” (current edition location: after section 16.2) |
| `CH16-C010` | 444--449, especially 446 | diagram typography | remove the extra `)` from `\psi|_{\ofml K)}` without changing the vertical map |
| `CH16-C011` | 547--551, especially 549 | codomain notation | write `\pi_2:\ofml E\to A`, matching the proposition and pullback, not `\ofml A` |
| `CH16-C012` | 559--566, especially 563 | missing variable | introduce the unitary as `U`: “there exists a unitary operator `U` on `H` such that `\tau_2=\ad_U\tau_1`” |
| `CH16-C013` | 620--634, especially 622 and 633 | index spelling | repair both index-only spellings `Topelitz` to `Toeplitz` |
| `CH16-C014` | 886--891 | missing theorem hypothesis | declare `\phi` a unital completely positive linear map before concluding `\phi\lesssim\mathbf r` |
| `CH16-C015` | 909--924 | mathematical/category | make `\tau` unital and replace the star-homomorphic lift by a unital completely positive linear lift |

These are candidate groups, not edits to authority. One group may produce
multiple exact before/after records in the eventual JSON correction ledger.

## Checked mathematical spine that should be preserved

### Essential spectra and Toeplitz operators

1. The essential spectrum is correctly the spectrum of `\pi(T)` in the
   Calkin algebra and equivalently the scalars for which `T-\lambda I` is not
   Fredholm.
2. The self-adjoint characterization by accumulation points and
   infinite-multiplicity eigenvalues is correct. Weyl and Weyl--von Neumann
   are retained after the unitary-comparison scope repair above.
3. Essential normality is equivalently normality modulo compacts; essential
   self-adjointness is equivalently self-adjointness modulo compacts. The
   unilateral shift example is correct.
4. The Hardy-space compression `T_\phi=P_+M_\phi`, positivity, linearity,
   involution preservation, multiplication identities, and matrix
   characterization are coherent.
5. The Hartman--Wintner equality
   `\rho(T_\phi)=\|T_\phi\|=\|\phi\|_\infty` is not a source defect:
   spectral inclusion supplies the lower bound and compression supplies the
   upper norm bound.
6. Compact semicommutators for continuous symbols, essential normality,
   `\ofml K(H^2)` as an ideal, and the unique
   continuous-symbol-plus-compact decomposition are consistent.
7. The Toeplitz sequence is exact and nonsplit in the category of
   C-star-algebras and star-homomorphisms, although its Toeplitz map is a
   positive bounded linear section at weaker levels.
8. The nowhere-zero Fredholm criterion, factorization
   `\phi=\zeta^n\exp\psi`, Toeplitz index formula, Wold decomposition, and
   Coburn universal property are retained.

### Extensions and their addition

1. Essential self-adjointness is equivalent to being a compact perturbation
   of a self-adjoint operator: take `(T+T^*)/2`.
2. After the explicit separable/infinite-dimensional convention, equal
   essential spectrum classifies essentially unitarily equivalent
   self-adjoint operators, while the Toeplitz-index example correctly shows
   failure for general essentially normal operators.
3. The exact-sequence definition of an extension, equivalence diagram,
   conjugation `\ad_U`, and spatial description of automorphisms of
   `\ofml K(H)` are type-consistent after candidates C010--C012.
4. An essentially normal operator determines an extension by continuous
   functions on its essential spectrum, and every member of such an extension
   algebra is essentially normal because the quotient is commutative.
5. The pullback universal property and the pullback realization of a Busby
   map are correct. Candidate C011 repairs only the accidental font/codomain
   mismatch in the proof.
6. The direct-sum operation on `\operatorname{Ext} A` is well defined up to
   unitary equivalence. The isomorphism `H\oplus H\cong H` should be understood
   as fixed when defining `\nu` and `\rho`; later well-definedness removes
   dependence on that choice.
7. Abstract Toeplitz extensions need not be injective. This does not conflict
   with the proposition about semisplit injective extensions: only an abstract
   Toeplitz map unitarily equivalent to the given monomorphism is thereby
   injective.

### Completely positive maps and nuclearity

1. The matrix-algebra realization, block-matrix norm, and independence from a
   faithful representation are correct.
2. The transpose on `\mathbf M_2` is positive but not 2-positive; the displayed
   partial-transpose matrix has a negative eigenvalue.
3. The 2-by-2 positivity criteria, contractivity of unital 2-positive maps,
   Kadison inequality, completely bounded norm, and equality of norms for a
   unital completely positive map are coherent.
4. Stinespring's theorem is stated in the correct unital form. Its isometry is
   essential and must not be weakened to an arbitrary bounded map.
5. The relation `\lesssim` is a preordering: composition of its witnessing
   isometries preserves compact-error terms. It is not antisymmetric.
6. Split extensions give the additive identity and semisplit extensions give
   invertible classes after candidates C014--C015 restore the actual
   completely-positive hypotheses.
7. Nuclearity as uniqueness of the C-star norm on every algebraic tensor
   product is a valid characterization. The finite-dimensional, matrix,
   compact-operator, continuous-function, and commutative examples are
   correct.
8. The completely positive lifting property and the conclusion that
   `\operatorname{Ext} A` is an Abelian group for nuclear separable unital
   `A` are consistent with the repaired semisplit criterion.

## Matters deliberately treated as style, not defects

- `\norm \phi_\infty` at records 131--132 parses with `\phi` as the norm
  argument and the infinity subscript outside; no semantic correction is
  inferred.
- Juxtaposed map notation such as `\phi'\ad_U` and `\ad_U\tau_1` is used
  consistently for composition. A target may insert `\circ` for readability
  only if the before/after mapping remains exact.
- `Douglas\cite{Douglas:1980}` at record 596 may receive normal Indonesian
  citation spacing; it is not a mathematical correction.
- The quoted phrase “abstract nonsense” may be translated naturally while
  retaining its quoted, informal register.
- Long physical records and blank vertical spacing may be reflowed without
  ledger status if formula order, identifiers, and source-record mapping stay
  lossless.
- The coined synonym `compalent` is preserved transparently as a coined term;
  it is not silently replaced by a different equivalence relation.

No source-attributed exercise, answer, solution, or hint layer exists in this
chapter. No author or maintainer is contacted. Frozen-source attribution,
CC BY-SA 4.0, change notices, ShareAlike, non-endorsement, and exact model
provenance remain intact.
