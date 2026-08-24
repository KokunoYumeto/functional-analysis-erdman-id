# Chapter 17 pretranslation mathematical review

Date: 2026-08-24  
Unit: `FAOA-2015-CH17`  
Source: `source/upstream/K0_functor.tex`, records 1--1,362

## Scope and method

This review covers every source record, all eight active sections, all 149
reader-semantic environments, and all 1,051 active top-level math surfaces. It
does not alter the frozen authority bytes. The review checks typing,
hypotheses, equivalence relations, categorical roles, exactness, functorial
directions, matrix sizes, inductive-limit closures, diagram arrows, and
cross-chapter dependencies. It distinguishes certain mathematical defects,
formal scope gaps, mechanical repairs, and source rhetoric that must not be
mistaken for proof.

The target must preserve all 206 environments, 73 unique labels, 47
references, 12 active citations, 100 index hooks, 24 `\df` hooks, 71 bracket
displays, four equations, three align blocks, eight active sections, and the
source order. Every substantive derivative change below needs a source-
correction ledger record.

## Certain defect 1: the opening display is heuristic, not a congruence proof

Records 13--19 say that an equivalence relation identifying a projection with
its two stabilized block placements solves noncommutativity, and display

`pq \sim \operatorname{diag}(p,0)\operatorname{diag}(0,q)=0=
\operatorname{diag}(0,q)\operatorname{diag}(p,0)\sim qp`.

That conclusion does not follow from the stated identification alone. An
arbitrary equivalence relation need not be compatible with multiplication,
and the Murray--von Neumann relation developed later is a relation on
projections while `pq` need not itself be a projection. The passage is
explicitly motivational, but its display can be mistaken for a formal
calculation. The derivative should retain the source's pedagogical idea and
formula while explicitly framing it as heuristic anticipation of stabilization,
not as a proved congruence statement.

## Certain defect 2: the homotopy path has the wrong codomain

Example `0060116` concerns a self-adjoint `h` in a unital C-star-algebra and
states that `exp(ih)` is a unitary element. Its proof hint at record 101 writes

`c:[0,1]\to\mathbb T,\quad t\mapsto\exp(ith)`.

For general operator/algebra-valued `h`, `exp(ith)` lies in the unitary group
`\ofml U(A)`, not in the scalar unit circle `\mathbb T`. The required repair is

`c:[0,1]\to\ofml U(A),\quad t\mapsto\exp(ith)`.

The endpoints and the use of proposition `001449` remain unchanged.

## Certain defect 3: strict block sum is not commutative on projections

Proposition `0060337` at records 367--369 claims that
`\fml P_\infty(A)` is a commutative semigroup under `\oplus`. Strictly,

`p\oplus q=\operatorname{diag}(p,q)` and
`q\oplus p=\operatorname{diag}(q,p)`

are usually different matrices. Proposition `0060331` proves only that they
are Murray--von Neumann equivalent. Thus `\oplus` is associative on the
stabilized projection family and commutative **up to** `\sim`; the quotient
`\fml D(A)` becomes a genuinely commutative semigroup in proposition
`0060417`. The target statement must say exactly that and must not make strict
equality or strict commutativity out of equivalence.

## Certain scope defect 4: the projection semigroup of B(H)

Example `0060424` at records 397--401 asserts

`\fml D(\ofml B(H))\cong\mathbb Z^+\cup\{\infty\}`

for an arbitrary Hilbert space `H`. It fails for finite-dimensional `H` (no
infinite-rank projection class), and for nonseparable `H` there can be several
infinite cardinal-dimension classes rather than one undifferentiated
`\infty`. The intended standard scope is a **separable infinite-dimensional**
Hilbert space. Add that scope explicitly.

## Certain category defects 5 and 6: induced maps have the wrong kind

Records 655--657 correctly extend a star-homomorphism entrywise to matrix
algebras, but then call its restriction from `\fml P_\infty(A)` to
`\fml P_\infty(B)` another star-homomorphism. Projection families are not
star-algebras, so this restricted arrow is simply a map preserving projections,
block sums, and Murray--von Neumann equivalence.

Likewise, proposition `0062424` at records 814--822 calls
`K_0(\phi):K_0(A)\to K_0(B)` a star-homomorphism. Its source and target are
Abelian groups, so it is a **group homomorphism**. Both category repairs are
mandatory; no formulas or functorial directions change.

## Certain identifier defect 7: the unitalization maps are unnamed aliases

The cited split exact sequence `0062334i` and its Chapter 12 authority use the
quotient/section pair `Q,\psi`. Records 793--850 later use `\pi,\lambda`
without binding these as aliases, and record 847 even says that `\pi` and
`\lambda` are “the” maps displayed in `0062334i`. A deterministic target must
bind the aliases explicitly:

- at first use, `\pi:=Q` for the quotient map; and
- before the scalar map, `\lambda:=\psi` for the canonical scalar section.

Then `s=\lambda\circ\pi=\psi\circ Q` is type-correct. This is preferable to
silently changing only one of the several later symbols.

## Certain identifier defect 8: the newly defined section is not used

The proof hint at records 741--752 defines
`\psi'(\lambda)=\lambda\mathbf j` and uses it in
`\iota\mu+\psi'Q=\id_{\widetilde A}`. Its final identity is printed as
`Q\circ\psi=\id_\mathbb C`, although the locally introduced map is `\psi'`.
The old identity with `\psi` is true, but does not verify the newly used
splitting. The last item should be `Q\circ\psi'=\id_\mathbb C`.

## Certain defect 9: an unused variable corrupts the standard-picture set

Proposition `0062544` at records 860--866 prints

`K_0(A)=\{[p]-[s(p)]:p,q\in\fml P_\infty(\widetilde A)\}`.

The variable `q` does not occur in the element being described. The standard
picture uses only `p`:

`K_0(A)=\{[p]-[s(p)]:p\in\fml P_\infty(\widetilde A)\}`.

This repair removes no mathematical degree of freedom because `q` was wholly
unbound to the expression.

## Certain scope defect 10: the Calkin exact-sequence counterexample

Example `0062679` at records 930--934 says that for a Hilbert space `H`, the
map induced by `\ofml K(H)\hookrightarrow\ofml B(H)` is not injective. For
finite-dimensional `H`, `\ofml K(H)=\ofml B(H)` and the induced K0 map is the
identity. Add the intended hypothesis that `H` is infinite-dimensional. No
separability hypothesis is needed for this specific finite-versus-infinite
correction.

## Certain defect 11: a C-star inductive limit needs closure

Records 1,032--1,036 take an increasing sequence of C-star-subalgebras and
claim its inductive limit has `B=\bigcup_n A_n`. That union need not be norm
closed and therefore need not be a C-star-algebra. This contradicts the
chapter's own general formula at records 1,015--1,019. The target must use

`B=\overline{\bigcup_{n=1}^{\infty} A_n}`.

The canonical maps remain inclusions into this closure.

## Certain scope defect 12: the compact-operator inductive limit

The system `M_n\to M_{n+1}`, `a\mapsto\operatorname{diag}(a,0)`, at records
1,038--1,042 has inductive limit the compact operators on a **separable
infinite-dimensional** Hilbert space. It is not the compact-operator algebra
on an arbitrary finite- or nonseparable-dimensional `H`. State the exact scope
while preserving the system and connecting maps.

## Certain category defect 13: matrix maps need to be star-homomorphisms

Records 1,093--1,100 classify “algebra homomorphisms” from `M_k` to `M_n` as
unitary conjugates of repeated diagonal copies. For arbitrary complex algebra
homomorphisms the conjugating matrix need only be invertible; unitary
conjugacy is the C-star classification of **star-homomorphisms**. The section's
context and the following proposition confirm the intended category.

The target must say “nonzero star-homomorphisms,” explicitly call the displayed
map `\phi`, and then define its multiplicity `m`. The zero block and the
equation `n=mk+r` remain unchanged.

## Certain defect 14: multiplicity matrices may contain zero

Proposition `0068117` at records 1,121--1,137 calls every entry `m_{ij}` a
positive integer. The examples at records 1,185 and 1,215 immediately use zero
entries. The correct range is the **nonnegative integers**. For a unital map,
the additional constraint `\mathbf m\mathbf k=\mathbf n` prevents an entire
target row from being zero; it does not force each individual entry positive.

## Complete correction-ledger candidate table

| Candidate | Source records | Class | Exact target action |
|---|---:|---|---|
| `CH17-C001` | 12 | mechanical prose | translate the intended “allow them … to roam,” removing the source's extra “be” |
| `CH17-C002` | 13--19 | mathematical status | retain the stabilization display but identify it explicitly as heuristic motivation, not a consequence of a proved multiplicative congruence |
| `CH17-C003` | 42--46, especially 44 | mechanical prose | use the intended article “a unitary element” in natural Indonesian prose |
| `CH17-C004` | 63--67 | mechanical prose | remove the source's ungrammatical “for every … then” construction without changing quantifiers |
| `CH17-C005` | 101--103 | mathematical/type | replace path codomain `\mathbb T` by `\ofml U(A)` |
| `CH17-C006` | 367--369 | mathematical/equality | state associativity and commutativity up to Murray--von Neumann equivalence; reserve genuine commutativity for `\fml D(A)` |
| `CH17-C007` | 390--392 | mathematical/category | replace “additive group of positive integers” by “additive semigroup of nonnegative integers,” retaining the explicit set `\{0,1,2,\ldots\}` |
| `CH17-C008` | 397--401 | formal scope | require `H` to be separable and infinite-dimensional |
| `CH17-C009` | 446--450, especially 447 | mechanical prose | translate the intended “will be denoted by,” not the malformed “will be denote” |
| `CH17-C010` | 458--460 | mechanical prose | translate “becomes an Abelian group,” repairing “and Abelian” |
| `CH17-C011` | 543--549, especially 547 | mechanical/category prose | use plural “group homomorphisms” for the image category |
| `CH17-C012` | 655--657 | mathematical/category | call the induced arrow on projection families a map, not a star-homomorphism |
| `CH17-C013` | 741--752, especially 750 | identifier | use the newly defined `\psi'` in `Q\circ\psi'=\id_\C` |
| `CH17-C014` | 793--850 | identifier/notation | explicitly bind `\pi:=Q` and `\lambda:=\psi` before later uses; keep quotient and section roles distinct |
| `CH17-C015` | 814--822, especially 815--817 | mathematical/category | call `K_0(\phi)` the unique group homomorphism |
| `CH17-C016` | 847--850, especially 848 | mechanical prose | translate the intended “unitization of a C-star-algebra,” repairing “of as” |
| `CH17-C017` | 860--866, especially 865 | mathematical/notation | delete unused `q` from the set-builder domain |
| `CH17-C018` | 930--934 | formal scope | require `H` to be infinite-dimensional |
| `CH17-C019` | 1,032--1,036 | mathematical/topology | replace the raw union by its norm closure |
| `CH17-C020` | 1,038--1,042 | formal scope | identify `H` as separable and infinite-dimensional |
| `CH17-C021` | 1,093--1,100 | mathematical/category | use nonzero star-homomorphisms, name the displayed map `\phi`, and preserve unitary conjugation |
| `CH17-C022` | 1,127--1,130 and 1,185--1,215 | mathematical/range | call the multiplicities nonnegative integers; the examples' zeros remain authoritative |
| `CH17-C023` | 1,274 | mechanical TeX | remove the empty `\textbf{}` without changing “CAR-algebra” |

The table has twenty-three groups because the full rereview separated the
opening grammar repair from its mathematical-status repair. These are
candidates for the derivative ledger, not edits to authority.

## Checked mathematical spine that should be preserved

### Projection equivalences and stabilization

1. Similarity, unitary equivalence, homotopy through invertibles/unitaries,
   and Murray--von Neumann equivalence are distinct relations and remain so.
2. Polar decomposition of an invertible element and continuity of its unitary
   factor correctly transfer invertible homotopies to unitary homotopies.
3. For self-adjoint elements, similarity implies unitary equivalence by the
   polar-decomposition argument; the commutation with `|s|^2` is essential.
4. The implications “homotopic projections imply unitarily equivalent,
   which imply Murray--von Neumann equivalent” are preserved with the source's
   explicit nonconverse examples.
5. Stabilizing a partial isometry produces unitary equivalence of block
   projections, and unitary equivalence stabilizes to projection homotopy.
6. The matrix C-star norm and its entrywise bounds are type-consistent; the
   faithful-representation construction and all matrix sizes remain exact.

### Projection semigroup and Grothendieck construction

1. `\fml P_\infty(A)` gathers projections across all matrix sizes and
   `p\oplus q` is block sum. Candidate C006 repairs only the strict-
   commutativity overstatement.
2. Murray--von Neumann equivalence respects block sum, so the quotient
   `\fml D(A)` has a well-defined commutative-semigroup operation.
3. The Grothendieck relation with an auxiliary `k` is the correct construction
   for a possibly noncancellative commutative semigroup.
4. The map `\gamma_S`, cancellation criterion, universal property, induced
   group homomorphism `G(\phi)`, functoriality, and naturality square are
   coherent and must retain their arrow directions.
5. `G(\mathbb N)=G(\mathbb Z^+)=\mathbb Z`, the absorbing-infinity example,
   and the multiplicative nonzero-integer example are retained.

### Unital and nonunital K0

1. For unital `A`, `K_0(A)=G(\fml D(A))`; bracket notation maps stabilized
   projections into this group.
2. Stable equivalence matches equality of K0 projection classes, and the
   standard difference-of-projections picture is preserved.
3. The universal property of unital K0 and the entrywise action of a
   star-homomorphism produce a group homomorphism `K_0(\phi)`; categorical
   repairs C012 and C015 do not change its values.
4. Point-norm homotopy of star-homomorphisms induces equal K0 maps, hence
   homotopy-equivalent C-star-algebras have isomorphic K0 groups.
5. For arbitrary `A`, K0 is the kernel of the K0 map induced by the
   unitalization quotient. The scalar map subtracts the scalar projection in
   the standard picture. Candidate C014 makes the quotient/section aliases
   explicit rather than changing the construction.

### Exactness, stability, and inductive limits

1. Half exactness and split exactness are distinct from full exactness. The
   interval-endpoint and Calkin examples correctly demonstrate failure of
   full exactness after the Hilbert-dimension scope repair.
2. Matrix stability `K_0(A)\cong K_0(M_n(A))` and preservation of direct sums
   are retained.
3. The categorical definition of an inductive sequence and its universal
   limit property have correct compatibility directions.
4. Existence/uniqueness of C-star inductive limits, norm formula, K0
   continuity, rational/dyadic examples, and `K_0(\ofml K(H))\cong\mathbb Z`
   are coherent.
5. An increasing concrete union must be completed in norm; candidate C019
   restores the source's own general closure formula.

### Finite-dimensional systems and Bratteli diagrams

1. Finite-dimensional C-star-algebras are finite direct sums of full matrix
   algebras.
2. A star-homomorphism is encoded up to unitary equivalence by its matrix of
   component multiplicities; unitality gives `\mathbf m\mathbf k=\mathbf n`,
   while a nonunital map gives only `\mathbf m\mathbf k\le\mathbf n`.
3. Multiplicity entries may be zero, as the chapter's second and third finite-
   dimensional examples show.
4. Every drawn edge count, vertex label, matrix size, and connecting-map
   direction in the Bratteli diagrams is preservation-critical.
5. The Cantor-function algebra, CAR algebra, its alternative subsystem, and
   Fibonacci algebra examples illustrate nonunique Bratteli presentations and
   remain in the source order.

## Matters deliberately treated as style, not defects

- The opening uses intentionally colloquial metaphors (“more room,” “narrow
  world,” “simple-minded device”). Translate their register naturally but do
  not convert them into a formal proof.
- The source convention `\mathbb Z^+=\{0,1,2,\ldots\}` is explicit. The
  derivative may call these nonnegative integers for clarity while retaining
  the symbol and displayed set.
- Ordinal forms such as `j^{\text{th}}` may be localized as ordinary `j`-th
  component prose without altering indices.
- “Abusing language” and the quoted word “forgets” are informal categorical
  commentary and may be translated idiomatically.
- `M_n`, `\mathbf M_n`, and `\M nA` are source macro/style variants. Do not
  normalize them unless the formula map records the exact lexical reflow.
- The manual vertical skips, page enlargement, long physical records, and
  blank record runs may be reflowed without mathematical ledger status.
- Disabled proof-pointer comments remain disabled; translating active prose
  does not activate them or turn citations into complete proofs.

The sole source exercise, all sixteen proof hints, all six active proof
pointers, and the absence of answer/solution environments remain explicit.
No author or maintainer is contacted. Frozen-source attribution, CC BY-SA 4.0,
change notices, ShareAlike, non-endorsement, and exact model provenance remain
intact.
