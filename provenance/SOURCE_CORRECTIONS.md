# Source corrections

## Chapter 1

These source-backed corrections are present in the Indonesian Chapter 1
target. Each was independently rereviewed against the exact source; labels and
mathematical topology remain intact.

1. `linalg.tex:109–112`: replace undefined spanning-set `B` with `A` in the
   coefficient convention.
2. `linalg.tex:137`: a Hamel basis for `V` spans `V`, not itself `B`.
3. `linalg.tex:465–467`: require eigenvalue `lambda` to belong to the scalar
   field `K`, so `T-lambda I_V` is defined for real spaces.
4. `linalg.tex:601`: use the typed identity `I_V` in primary decomposition.
5. `linalg.tex:666`: repair malformed `\item]`.
6. `linalg.tex:691–692`: conditions (a)–(d) define a positive-semidefinite
   conjugate-symmetric sesquilinear form; the extra strict condition makes it
   positive definite.
7. `linalg.tex:702–706`: scope `s(x,x)=0` iff `x=0` to an inner product, not a
   merely semidefinite form.
8. `linalg.tex:760–762`: handle `s(y,x)=0` before using polar form with `r>0`.
9. `linalg.tex:842–843`: norms and seminorms take nonnegative values.
10. `linalg.tex:876–877`: close the parenthetical metric-definition sentence.
11. `linalg.tex:934–939`: require both spaces to share a scalar field and use
    `alpha in K` for the external direct sum.
12. `linalg.tex:1050`: under the `k`-sum use `a_k conjugate(b_k)`, not index
    `n`.
13. `linalg.tex:1182–1184`: use `I_V` consistently in the orthogonal-resolution
    definition.
14. `linalg.tex:967–969`: map the inner product from `V \oplus V` to the scalar
    field `K`, not back into `V \oplus V`.
15. Four long inline mathematical surfaces are reflowed as displays without
    changing their formulas or order.

No upstream contact occurs during production. A later report, if separately
authorized after the complete corpus, is limited to one concise deduplicated
high-confidence submission.

## Chapter 2

These corrections are present in `source/id-ID/categories-id.tex`. They retain
the chapter's ordered topology, identifiers, citations, and intentional
Bourbaki convention for monomorphisms and epimorphisms.

1. `categories.tex:78--84`: attach the `small` and `locally small` index hooks
   to the definitions they actually describe; the source has the hooks in the
   opposite order.
2. `categories.tex:305--316`: replace the false claim that the one-object
   category built from a monoid is non-concrete with the accurate statement
   that the example is *not presented concretely*. The monoid has a faithful
   regular action on its underlying set, so the original non-concreteness claim
   cannot stand.
3. `categories.tex:262`: typeset the codomain identity as `\vc 1_B`, matching
   `\vc 1_A` and the book's identity-vector convention.
4. `categories.tex:537--548`: qualify the element formula
   `(f,g)(a,b)=(f(a),g(b))` by requiring a concrete category, and supply the
   missing morphism action of the diagonal functor,
   `\ftr D(f):=(f,f)`.
5. Repair source-language slips naturally in translation: `in many field
   terms`, `the morphism are`, `Such a function` where the subject is a
   morphism, `Forgetful functor can`, and `Composition of morphism`.
6. Represent the later Open Mapping Theorem reference `C069414` as a typed
   future cross-reference at this cumulative boundary; its source label is
   retained for resolution when Chapter 6 enters the reader.

## Chapter 3

These corrections are present in `source/id-ID/normlinspaces-id.tex`. They
were checked against the frozen source and preserve the ordered environment,
label, citation, reference, exercise, hint, diagram, and index topology.

1. `normlinspaces.tex:52` / target line 54: remove the stray comma in the
   sequence tuple.
2. `normlinspaces.tex:74` / target line 79: repair malformed index math
   `c)` to `c_0`.
3. `normlinspaces.tex:78--80` / target lines 85--87: use the scalar field
   `K` consistently for bounded scalar-valued functions.
4. `normlinspaces.tex:141` / target line 154: repair `(fn)` to `(f_n)`.
5. `normlinspaces.tex:388` / target line 448: supply the missing verb in the
   sequence hypothesis.
6. `normlinspaces.tex:482` / target line 543: repair `my help` naturally
   as “dapat membantu”.
7. `normlinspaces.tex:527` / target lines 592--593: refer to the preceding
   proposition, not a nonexistent preceding exercise.
8. `normlinspaces.tex:625` / target lines 699--701: remove the stray closing
   parenthesis in the norm-preserving definition.
9. `normlinspaces.tex:737` / target line 816: preserve
   `exam_ran_nonclosed` as the typed future cross-reference 5.2.14.
10. `normlinspaces.tex:798` / target line 856: use `alpha in K`, not
    unconditionally `R`, for quotient-space scalar multiplication.
11. `normlinspaces.tex:960--971` / target lines 972--988: repair the broken
    product sentence and use the defined spaces `V_1,V_2` consistently.
12. `normlinspaces.tex:974,1323` / target lines 991 and 1312: supply the
    missing verb naturally in translation.
13. `normlinspaces.tex:1039--1040` / target lines 1055--1057: replace the
    undefined product family `A_lambda` by `V_lambda` and use `K`.
14. `normlinspaces.tex:1086` / target lines 1102--1107: identify the
    selected product norm as the second, the 1-norm, not the first.
15. `normlinspaces.tex:1156--1216` / target lines 1172--1233: treat
    `B(S)`, `C(X)`, and `C_b(X)` consistently as scalar/`K`-valued
    and type the evaluation map into `K`.
16. `normlinspaces.tex:1260` / target lines 1249--1250: give the coproduct
    universal morphism domain `Q`, not product object `P`.
17. `normlinspaces.tex:1299--1300` / target lines 1288--1289: define the
    indexed disjoint union using pairs `(a,lambda)` with
    `a in A_lambda`.
18. `normlinspaces.tex:1607` / target line 1603: complete the bounded-net
    definition by requiring a bounded range.
19. `normlinspaces.tex:1702` / target lines 1696--1699: repair the index-key
    spelling and translate the controlled term as `tutupan`.
20. `normlinspaces.tex:1741--1742` / target lines 1737--1738: replace the
    English-only pronunciation cues with Indonesian sound examples.
21. `normlinspaces.tex:1798--1799` / target lines 1794--1795: use `u`,
    the real part of `f`, in the real-linearity equations.
22. `normlinspaces.tex:1820` / target lines 1801--1803: identify HBT III as
    a theorem, not a proposition.
23. `normlinspaces.tex:1859--1860` / target lines 1854--1855: require the
    vector to be nonzero in the norm-one-functional corollary.
24. `normlinspaces.tex:205--215` / target lines 221--237: condition the
    zero-centered ball/sphere shorthand on a distinguished zero point.
25. `normlinspaces.tex:527--541,594--598,1220--1222` / target lines
    575--593, 663--668, and 1236--1239: exclude the zero domain from the four
    equivalent operator-norm expressions, set its operator norm to zero, and
    restrict the unit-norm identity and unital operator-algebra claims to
    nonzero spaces.

Reader-facing terminology and syntax were also normalized after a complete
language audit: `tutupan`, `mempertahankan norma`, functional
`perpanjangan`, `kekontinuan`, Hausdorff uniqueness, coproduct phrasing,
interior/tutupan definitions, and isolated Indonesian grammar. Those
translation choices do not alter source mathematics.

## Chapter 4

The following source candidates have been adjudicated, applied, and
mechanically rechecked in `source/id-ID/Hilbert_spaces-id.tex`; identifiers,
citations, diagram grammar, and source order otherwise remain unchanged.

1. `Hilbert_spaces.tex:49`: take the supremum over `x in X`, not over the
   unrelated interval `[0,1]`, in the uniform norm on `C(X)`.
2. `Hilbert_spaces.tex:220`: use `x_{n_{j-1}}`, not the expression with the
   unbound index `i`, in the telescoping subsequence difference.
3. `Hilbert_spaces.tex:282`: repair the English article naturally in the
   Indonesian sentence; no mathematical surface changes.
4. `Hilbert_spaces.tex:286`: correct the index-key spelling of `orthogonal` and
   translate its reader-facing text.
5. `Hilbert_spaces.tex:380--381`: use plural agreement for the two claims,
   expressed naturally in Indonesian.
6. `Hilbert_spaces.tex:403`: restore the missing token boundary after the
   example environment opening.
7. `Hilbert_spaces.tex:432--436`: close the right-hand side of
   `(M cap N)^perp = M^perp + N^perp`; the sum of two closed subspaces need not
   be closed.
8. `Hilbert_spaces.tex:443--444`: remove the unmatched closing parenthesis at
   the end of the norm-induction sentence.
9. `Hilbert_spaces.tex:560--563`: quantify all coefficients
   `c_{-n},...,c_n`, not only `c_1,...,c_n`, for the displayed trigonometric
   polynomial.
10. `Hilbert_spaces.tex:728--729`: supply the missing sentence-ending period
    before the evaluation-functional construction.
11. `Hilbert_spaces.tex:747--748`: restore the missing relation in “wrong with
    his invocation,” expressed naturally in Indonesian.
12. `Hilbert_spaces.tex:847`: type the evaluation functional into `R`, not
    `[0,1]`, because the function family is real-valued.
13. `Hilbert_spaces.tex:849`: correct the finite-subset interval from `[0.1]`
    to `[0,1]`.
14. `Hilbert_spaces.tex:852`: supply the missing article in the parenthetical
    question, expressed naturally in Indonesian.
15. `Hilbert_spaces.tex:959`: retain the resolving bibliography key
    `wiki:xxx` and the source's search suggestion, but keep its mutable target
    and placeholder-like key recorded as a citation-quality warning.
16. `Hilbert_spaces.tex:1002`: call `ump001z` the following example, not an
    exercise; the label belongs to an `exam` environment.
17. `Hilbert_spaces.tex:1049--1051`: move the three misplaced `l_2` index hooks
    from the free-vector-space diagram to the Chapter 4 `l_2` discussion,
    retaining all three hooks rather than silently dropping them.
18. `Hilbert_spaces.tex:1074--1076`: define concatenation as `s ast t`, using
    the words introduced immediately before it, rather than undefined `x,y`.
19. `Hilbert_spaces.tex:1118--1119`: identify `(Q,iota)` as the universal pair;
    `Q` is the source-category object in the stated universal morphism.
20. `Hilbert_spaces.tex:1169`: include `F` within the defined-term boundary for
    “co-universal morphism for B (with respect to F).”
21. `Hilbert_spaces.tex:1188--1200`: use the declared product object and maps
    `P ->^{pi_k} A_k`, not the coproduct variables `Q,iota_k`.
22. `Hilbert_spaces.tex:1275`: supply the missing article in “a subspace,”
    expressed naturally in Indonesian.

The cumulative Chapter 1--4 reader also renders the intentional future
reference `C067441` as `\futurexref{6.2.9}{C067441}`. This preserves the exact
label target and the official printed theorem number while avoiding a broken
link until Chapter 6 enters the reader.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 17

The following 26 source-facing correction groups are adjudicated and applied
in `source/id-ID/K0_functor-id.tex`. The exact machine-verifiable ledger is
`provenance/SOURCE_CORRECTIONS_CH17.json`; it binds every inclusive source and
target line range, correction class, normalized snippet hash, and required or
forbidden target anchor.

Mechanical and category-prose repairs:

1. `K0_functor.tex:12`: remove the extra verb from “to be roam about.”
2. `K0_functor.tex:42--46`: repair the article in the unitary-equivalence
   definition.
3. `K0_functor.tex:63--67`: repair the malformed every-then quantifier
   construction without changing its scope.
4. `K0_functor.tex:446--450`: restore the intended phrase “will be denoted
   by.”
5. `K0_functor.tex:458--460`: repair the article in “becomes an Abelian
   group.”
6. `K0_functor.tex:543--549`: use plural “group homomorphisms” for the image
   category.
7. `K0_functor.tex:847--850`: repair “unitization of a C-star-algebra.”
8. `K0_functor.tex:1271--1275`: remove the empty `\textbf{}` command while
   preserving the CAR expansion.

Mathematical status, type, equality, scope, topology, and notation repairs:

9. `K0_functor.tex:13--19`: retain the stabilization calculation as
   heuristic motivation rather than presenting it as a proved multiplicative
   congruence.
10. `K0_functor.tex:101--103`: give the exponential path its correct codomain
    in the unitary group of `A`, not the scalar circle.
11. `K0_functor.tex:144--145`: reverse the implication so it actually states
    the converse of the second implication in Proposition `0060221`:
    `p\sim q\Rightarrow p\sim_u q`.
12. `K0_functor.tex:175--177`: reverse the implication so it actually states
    the converse of the first implication in Proposition `0060221`:
    `p\sim_u q\Rightarrow p\sim_h q`.
13. `K0_functor.tex:367--369`: block sum is strictly associative but
    commutative only up to Murray--von Neumann equivalence on projections.
14. `K0_functor.tex:390--392`: identify `D(C)` as the additive semigroup of
    nonnegative integers, not a group of positive integers.
15. `K0_functor.tex:397--401`: restrict the single-infinity
    projection-semigroup description to separable infinite-dimensional
    Hilbert space.
16. `K0_functor.tex:651--652`: give `\tau` the underlying semigroup of `G` as
    codomain because its value `\nu(p)` lies there, not in `K_0(A)`.
17. `K0_functor.tex:655--657`: call the restriction to projection families a
    map rather than a star-homomorphism.
18. `K0_functor.tex:741--752`: use the newly defined section `\psi'` in the
    final splitting identity.
19. `K0_functor.tex:793--850`: bind `\pi:=Q` and `\lambda:=\psi` so the
    nonunital quotient and scalar-section notation is closed.
20. `K0_functor.tex:814--822`: call `K_0(\phi)` a group homomorphism between
    Abelian groups.
21. `K0_functor.tex:860--866`: remove unused `q` from the standard-picture set
    builder.
22. `K0_functor.tex:930--934`: require infinite-dimensional `H` in the Calkin
    exact-sequence counterexample.
23. `K0_functor.tex:1032--1036`: take the norm closure of the increasing union
    in the C-star inductive limit.
24. `K0_functor.tex:1038--1042`: identify the compact-operator limit space as
    separable and infinite-dimensional.
25. `K0_functor.tex:1093--1104`: classify nonzero star-homomorphisms, name the
    displayed map `\phi`, and preserve that category in the following example.
26. `K0_functor.tex:1127--1130`: allow zero multiplicities by using
    nonnegative, rather than positive, integer matrix entries.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 16

The following 15 source-facing correction groups are adjudicated and applied
in `source/id-ID/extensions-id.tex`. The exact machine-verifiable ledger is
`provenance/SOURCE_CORRECTIONS_CH16.json`; it binds every inclusive source and
target line range, correction class, normalized snippet hash, and required
target anchor.

Mechanical, notation, and bibliographic repairs:

1. `extensions.tex:13`: insert the missing separation after `\begin{prop}`.
2. `extensions.tex:254--257`: restore the established Calkin-algebra macro in
   `\ofml Q(H^2)`.
3. `extensions.tex:256`: read the malformed “and isomorphism” as the intended
   “an isomorphism.”
4. `extensions.tex:312--314`: repair the visibly split Douglas theorem number
   `7.2 6` to `7.26`.
5. `extensions.tex:407`: replace the stale “after section 9.2” index locator
   by the stable local locator “mulai bagian Penjumlahan Ekstensi.”
6. `extensions.tex:444--449`: remove the extra parenthesis from
   `\psi|_{\ofml K)}` in the extension-equivalence diagram.
7. `extensions.tex:620--634`: repair both index-only spellings `Topelitz` to
   `Toeplitz`.

Mathematical, type, map-identity, and scope repairs:

8. `extensions.tex:42--58`: with the declared unitary `U:H\to K`, replace the
   ill-typed conjugations `UTU^*` by `U^*TU` in both essential and ordinary
   unitary equivalence.
9. `extensions.tex:61--63`: require the separable Hilbert spaces in
   Proposition `005134` to be infinite-dimensional; equality of essential
   spectra alone does not determine finite-dimensional multiplicities.
10. `extensions.tex:298--305`: identify `T`, not `\beta`, as the continuous
    right inverse/section, consistently with `\beta\circ T=I`.
11. `extensions.tex:344--345`: replace both malformed punctured-plane groups
    `\pi^1(\C\setminus0)` by `\pi_1(\C\setminus\{0\})`.
12. `extensions.tex:547--551`: give `\pi_2` codomain `A`, not the accidental
    font form `\ofml A`, in the pullback proof.
13. `extensions.tex:559--566`: name the implementing unitary `U` before using
    it in `\tau_2=\operatorname{ad}_U\tau_1`.
14. `extensions.tex:886--891`: declare `\phi` to be a unital completely
    positive linear map in Voiculescu's theorem; without this hypothesis the
    printed assertion is false.
15. `extensions.tex:909--924`: retain that `\tau` is unital and replace the
    claimed star-homomorphic lift by a unital completely positive linear lift.
    A star-homomorphic lift characterizes a split extension, not merely a
    semisplit one.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 15

The following nine source decisions are adjudicated and applied in
`source/id-ID/fredholm_theory-id.tex`. The exact machine-verifiable ledger is
`provenance/SOURCE_CORRECTIONS_CH15.json`; it binds every inclusive source and
target line range, correction class, normalized snippet hash, and required or
forbidden target anchor.

Mathematical source repairs:

1. `fredholm_theory.tex:10--32`: quantify the scalar in Fredholm Alternative I
   as fixed and nonzero; the stated finite-dimensional alternative fails for
   `lambda=0`.
2. `fredholm_theory.tex:43--66`: restrict the scalar in Fredholm Alternative II
   to the nonzero complex scalars.
3. `fredholm_theory.tex:72--81`: impose the same necessary nonzero-scalar
   restriction in Fredholm Alternative IIIa.
4. `fredholm_theory.tex:101--106`: remove the unwarranted commuting condition
   `SK=KS` from the Riesz--Schauder definition so that it agrees with the
   chapter's invertible-plus-compact characterization.
5. `fredholm_theory.tex:123--125`: name the ambient Banach space `B`, making the
   quotient-dual expression `(B/M)^*` defined.
6. `fredholm_theory.tex:150--157`: replace the false claim that a sum of
   subspaces need not be a subspace by the demonstrated fact that a sum of two
   closed subspaces need not be closed.
7. `fredholm_theory.tex:300--303`: add the infinite-dimensional hypothesis
   required for the Fredholm index map to be surjective onto the integers.

Mechanical and formal-scope repairs:

8. `fredholm_theory.tex:247--252`: remove the extra closing parenthesis from
   the Fredholm-index index hook.
9. `fredholm_theory.tex:268--270`: state the standard closed-range,
   finite-kernel, finite-cokernel convention before applying Fredholm theory to
   maps `V` to `W`; the earlier Calkin-algebra definition covers endomorphisms.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 14

The following nine source candidates are adjudicated and applied in
`source/id-ID/multiplier_algebras-id.tex`. The exact machine-verifiable ledger
is `provenance/SOURCE_CORRECTIONS_CH14.json`; it binds every inclusive source
and target range, correction class, normalized snippet hash, and required or
forbidden target anchor.

1. `multiplier_algebras.tex:75--79`: replace the undefined `f` in the
   antihomomorphism definition by the declared map `\phi`.
2. `multiplier_algebras.tex:102--104`: restore the missing space in
   `means,when`.
3. `multiplier_algebras.tex:208--210`: supply the missing sentence stop after
   the assertion about Hilbert `$A$`-modules.
4. `multiplier_algebras.tex:229--233`: replace the malformed
   `$C^*$=algebra` typography by the ordinary `$C^*$-algebra` compound.
5. `multiplier_algebras.tex:229--234`: reverse the impossible inclusion
   `\iota\colon V\to W` to `\iota\colon W\to V`, since `V=A` and the proper
   ideal `W=J_0` includes into `A`, not conversely.
6. `multiplier_algebras.tex:312--317`: render the erroneous past participle
   `has lead` with its intended past-tense meaning.
7. `multiplier_algebras.tex:413--420`: join the period-fragment pair so the
   notation sentence says that if `A` and `B` are nonempty subsets of an
   algebra, `AB` denotes the stated linear span.
8. `multiplier_algebras.tex:641--643`: supply the missing second comma around
   `if it exists` in the injectivity proposition.
9. `multiplier_algebras.tex:645--647`: supply the missing second comma around
   `if it exists` in the uniqueness proposition.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 13

The following six source-facing changes are adjudicated and applied in
`source/id-ID/GNS_construction-id.tex`. The exact machine-verifiable ledger is
`provenance/SOURCE_CORRECTIONS_CH13.json`, 10,653 bytes, SHA-256
`9fdcdc4fe5b8f3d621ace0ac0efad2ae684766efcb4341d38bbc2e923e652a05`.

1. `GNS_construction.tex:27--31`: remove the redundant repeated positivity
   quantifier while retaining the exact domain and order condition.
2. `GNS_construction.tex:43--47`: define a state on a possibly nonunital
   `$C^*$`-algebra as a positive norm-one functional; retain
   `τ(1_A)=1` as the equivalent unital criterion. This is required after the
   source's own Chapter 12 admits algebras without identities.
3. `GNS_construction.tex:66--68`: restrict the norm-at-the-identity
   characterization of positivity to a unital `$C^*$`-algebra, where `1_A`
   exists.
4. `GNS_construction.tex:146--149`: replace the exercise's doubled final
   period with one period.
5. `GNS_construction.tex:215--219`: complete the GNS notation sentence by
   naming the given algebra `A` and adding terminal punctuation.
6. `GNS_construction.tex:230--237`: repair `that is.` punctuation and remove
   intrusive parentheses without changing the claim that the direct-sum
   operations are well defined.

No upstream contact occurs during production. These entries remain candidates
for the one deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 11

The following six source candidates are adjudicated and applied in
`source/id-ID/Gelfand_Naimark-id.tex`. The exact machine-verifiable ledger is
`provenance/SOURCE_CORRECTIONS_CH11.json`; it binds the inclusive source and
target ranges, normalized snippets and hashes, required anchors, and current
target identity.

1. `Gelfand_Naimark.tex:83`: close the unmatched parenthesis in the idempotent
   equation.
2. `Gelfand_Naimark.tex:205`: punctuate the proof hint after its `C073147`
   reference before the following question.
3. `Gelfand_Naimark.tex:470`: render the intended plural “compact Hausdorff
   spaces.”
4. `Gelfand_Naimark.tex:480`: use `a_kz^k`, not `a_nz^n`, under the
   `k`-indexed sum in the Gelfand-transform identity.
5. `Gelfand_Naimark.tex:519`: remove the unmatched closing parenthesis after
   the bibliographic locator “exercise 18.45.”
6. `Gelfand_Naimark.tex:750`: remove the duplicated “is” in the spectrum
   hypothesis.

At the Chapter 12 cumulative boundary, the seven Chapter 11 reader occurrences
and two Chapter 11 index occurrences of `swadjoin` were reconciled to the
whole-edition form `swaadjoin`, already used from Chapter 1 onward. This is a
derived-record terminology correction, not an upstream source correction; its
evidence and treatment of the historical Chapter 11 release are recorded in
`provenance/SELF_ADJOINT_TERMINOLOGY_ADJUDICATION.md`.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 12

The following 29 decisions are adjudicated and applied in
`source/id-ID/no_identity-id.tex`. The exact machine-verifiable ledger is
`provenance/SOURCE_CORRECTIONS_CH12.json`; it binds every inclusive source and
target range, classification, normalized source/target snippet hash, required
and forbidden anchors, and the complete 29-record closure.

Mechanical, indexing, and cross-reference repairs:

1. `no_identity.tex:89--90`: index the defined object as a right, not left,
   identity relative to an ideal.
2. `no_identity.tex:226`: point the first local short-exact-sequence reference
   to the globally unique Chapter 12 label.
3. `no_identity.tex:240`: repair the second local reference in the same way.
4. `no_identity.tex:247`: repair the third local reference and use equation
   reference typography.
5. `no_identity.tex:431`: supply the missing preposition in the proof-hint
   opening.
6. `no_identity.tex:435--436`: supply the missing article before “C-star
   algebra.”
7. `no_identity.tex:448`: typeset the star as a superscript in the C-star norm.
8. `no_identity.tex:483`: close the enumerated instruction with a period.
9. `no_identity.tex:536--537`: repair the article in “given an algebra.”
10. `no_identity.tex:670`: insert the missing space after the proposition
    opener.
11. `no_identity.tex:689`: insert the missing space after the proposition
    opener.
12. `no_identity.tex:709--710`: close the unmatched explanatory parenthesis in
    the `Q_A` index entry.
13. `no_identity.tex:907`: insert protected spacing before the
    Jordan-decomposition reference.
14. `no_identity.tex:961--962`: insert the missing space after the proposition
    opener.
15. `no_identity.tex:1033--1035`: correct the spelling of “approximate” in the
    sequential approximate-identity index entry.

Mathematical source repairs:

16. `no_identity.tex:175--179`: restore the omitted domain and mapping arrow in
    the nonunital Gelfand-transform signature.
17. `no_identity.tex:505`: state the proposition's precise
    “not isomorphic” conclusion instead of an undefined equivalence.
18. `no_identity.tex:554--559`: remove “unitally” from the general nonunital
    Gelfand--Naimark II description.
19. `no_identity.tex:561--565`: remove the false unital qualifier from the
    theorem's isomorphism for a general commutative C-star algebra.
20. `no_identity.tex:887--893`: name the ambient C-star algebra `A` before item
    (iii) quantifies an element of `A`.
21. `no_identity.tex:945--947`: state the positivity inequality in the
    unitization, using `1_{\widetilde A}`, because a general C-star algebra has
    no `1_A`.

Reader-facing mathematical localization and navigation:

22. `no_identity.tex:323--324`: translate the conjunction embedded in the
    displayed map pair without changing either map.
23. `no_identity.tex:471--473`: translate the conjunction inside the
    `A^\sharp` set-builder formula.
24. `no_identity.tex:591--596`: translate the two conditional labels inside
    the piecewise display.
25. `no_identity.tex:611`: retain the official future printed locator for
    Proposition 14.3.1 until Chapter 14 supplies the live label.
26. `no_identity.tex:659--663`: repeat the variable `b` where Indonesian
    grammar requires an explicit subject.
27. `no_identity.tex:728--733`: repair the source article and translate the
    conjunction inside the Q-spectrum display.
28. `no_identity.tex:858--860`: render “nth root” idiomatically as *akar
    pangkat n* while preserving the quantified symbol.
29. `no_identity.tex:1062--1069`: retain the named algebra `A` explicitly in
    idiomatic Indonesian proposition and corollary prose.

Two target-only `\newline`/`\mbox` treatments in Propositions 12.2.10 and
12.6.13 keep the compound `homomorfisme-*` intact under modern TeX line
breaking. They are visual reflow, not source corrections; they preserve every
mathematical surface and remove the two Chapter 12 overfull lines observed in
the provisional render.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 5

The following source candidates are adjudicated and applied in
`source/id-ID/Hilbert_space_operators-id.tex`. The target retains the complete
ordered environment, label, citation, exercise, hint, index, defined-term, and
formula topology except for the six explicitly locked mathematical surfaces
listed below.

1. `Hilbert_space_operators.tex:42,44`: correct the misspelled index display
   word `isomorophisms` in the translated reader-facing entries.
2. `Hilbert_space_operators.tex:143`: restore the omitted predicate: the
   associated quadratic form is the zero function exactly when the operator is
   the zero operator.
3. `Hilbert_space_operators.tex:188--189`: in the bound for a sesquilinear
   functional on `H` and `K`, quantify `x in H` and `y in K`, not both in `H`.
4. `Hilbert_space_operators.tex:481`: encode scalar conjugation with the
   semantic macro `\conj\alpha`, not the closure macro `\clo\alpha`.
5. `Hilbert_space_operators.tex:490`: remove the trailing space from the raw
   defined-term argument while translating it as `aljabar-*`.
6. `Hilbert_space_operators.tex:536`: close the pronunciation parenthesis in
   the star-homomorphism definition.
7. `Hilbert_space_operators.tex:576`: scope the definition and notation for a
   unitary element to a unital star algebra, because the displayed condition
   uses the multiplicative identity.
8. `Hilbert_space_operators.tex:602`: close the reader-facing parenthesis in
   the star-subalgebra index entry.
9. `Hilbert_space_operators.tex:790--792`: use the established real-field
   macro `\R^2` in both occurrences, not the undefined literal `R^2`.
10. `Hilbert_space_operators.tex:838--840`: require the star algebra to be
    unital before asserting `0 \preceq p \preceq 1` for every projection.
11. `Hilbert_space_operators.tex:864--866`: avoid the not-yet-defined notation
    `A^+`; state directly that `a in A` is a positive element.
12. `Hilbert_space_operators.tex:1076`: restore the missing space after the
    comma, expressed naturally in Indonesian.
13. `Hilbert_space_operators.tex:1106--1107`: exclude the zero Hilbert space
    from the minimal-ideal claim; otherwise `FR(H)` is the zero ideal, whereas
    this chapter defines a minimal ideal to be nonzero.
14. Ordinary source-language defects at lines 221, 234, 249, 300, 536, 843,
    and 1076, and the stray comma at line 834, are repaired naturally in the
    Indonesian prose without changing mathematical surfaces.
15. `Hilbert_space_operators.tex:77--81`: require both Hilbert spaces to be
    nonzero before taking suprema over their unit spheres in the operator-norm
    formula and its proof hint.
16. `Hilbert_space_operators.tex:179--212`: require both Hilbert spaces to be
    nonzero where the norm of a bounded sesquilinear functional is identified
    with expressions involving unit vectors and nonzero vectors; this scope is
    carried into the two immediately following propositions that invoke that
    norm.
17. `Hilbert_space_operators.tex:307--310`: state the finite-dimensional
    spectral theorem for a complex inner-product space. A real planar rotation
    is normal but need not be unitarily equivalent to a scalar multiplication
    operator.
18. `Hilbert_space_operators.tex:370--375`: require `H` to be a complex Hilbert
    space before quantifying `alpha in C` and forming `alpha T`.
19. `Hilbert_space_operators.tex:620--635`: require a nonzero Hilbert space in
    the definitions and proposition for numerical range and numerical radius;
    otherwise the unit sphere is empty and the displayed supremum has no stated
    convention.
20. `Hilbert_space_operators.tex:962--968`: bind `u` and `v` to the same
    Hilbert space `H` on which `T` acts, so both tensor-composition formulas are
    well typed.
21. `Hilbert_space_operators.tex:970--971`: qualify the preview of the minimal
    finite-rank ideal by requiring a nonzero Hilbert space, consistently with
    the corrected proposition at lines 1106--1107 and the chapter's definition
    of a minimal ideal as nonzero.
22. `Hilbert_space_operators.tex:1116--1118`: restrict the claim that the
    finite-rank ideal is not closed to infinite-dimensional Hilbert spaces. In
    finite dimension it equals the full operator algebra and is closed.
23. `functional_analysis_op_algs_bib.bib`, entry `Erdman:2010`: replace the
    dead `ELMA_licensepage.html` URL in the derivative bibliography with the
    durable DOI for the current publisher record of the same work. On
    2026-08-22 the frozen URL and both title-specific links exposed by Erdman's
    official author page returned HTTP 404; DOI `10.1142/11896` resolved and
    its registered record identified John M. Erdman and the exact title. The
    target retains the source's 2010 citation year because the DOI record is
    for the later 2021 monograph; this is a link repair, not a silent edition
    substitution. The frozen upstream bibliography remains byte-identical.

The source's variation between `H\oplus K` and `H\times K` at lines 179--212
is retained rather than silently harmonized: the finite direct sum is
canonically the product here, and the source deliberately alternates the two
descriptions. The cumulative Chapter 1--5 reader renders the intentional
forward reference `chap_cpt_ops` as `\futurexref{7}{chap_cpt_ops}` until
Chapter 7 supplies the live endpoint.
## Chapter 6

The following source candidates are adjudicated and applied in
`source/id-ID/Banach_spaces-id.tex`. The target retains the complete ordered
environment, label, reference, citation, exercise, proof, hint, index,
defined-term, and formula topology except for the explicitly classified
corrections and reader-facing localization deltas locked by
`qa/check_ch06_translation.py`.

1. `Banach_spaces.tex:16,60--62,330,403,423,496,502,684,797,909,912,932,
   1055,1171`: repair ordinary source-language and punctuation defects---a
   stray comma, an unclosed parenthesis, misspellings, missing token
   boundaries, wrong or duplicated articles/conjunctions, an unclosed
   parenthetical, and missing terminal punctuation---naturally in Indonesian.
2. `Banach_spaces.tex:128`: preserve the exact later-source endpoint `000731`
   as `\futurexref{11.2.20}{000731}` until Chapter 11 enters the cumulative
   reader; the endpoint is Proposition 11.2.20 at
   `Gelfand_Naimark.tex:242`.
3. `Banach_spaces.tex:213--214`: for arbitrary subsets, replace `M={0}` and
   `F={0}` by `M\subseteq\{0\}` and `F\subseteq\{0\}` in the two annihilator
   biconditionals. The source statements otherwise fail for empty subsets.
4. `Banach_spaces.tex:275`: describe `w^*` convergence as weak-star
   convergence, not ordinary weak convergence.
5. `Banach_spaces.tex:303--305`: state Alaoglu's theorem for the closed unit
   ball of the dual `V^*`; the source's unspecified normed-space ball has no
   weak-star topology of the stated kind.
6. `Banach_spaces.tex:396`: use the defined sequence term `w_0`, not `w_o`.
7. `Banach_spaces.tex:407--410`: change the invertibility index category from
   `BAN_1` to `BAN_\infty`. A bounded linear bijection need not be invertible
   in the contraction category.
8. `Banach_spaces.tex:476`: call `C069431` the preceding example, matching its
   `exam` environment, rather than an exercise.
9. `Banach_spaces.tex:546--549`: normalize the lone un-emphasized proof-hint
   heading to the same emphasized semantic heading used by the other 27
   Chapter 6 hints.
10. `Banach_spaces.tex:661--665`: introduce the missing ambient Banach algebra
    `A` before forming the quotient algebra `A/J`.
11. `Banach_spaces.tex:924--925`: retain the discussion of `c` and
    `l_\infty`; the constant sequence belongs to both, and the displayed norm
    difference tends to `1` in both. The source's switch to `l_1` and value
    infinity is not well typed.
12. `Banach_spaces.tex:955`: introduce the Banach space `B` used throughout
    the Schauder-basis definition.
13. `Banach_spaces.tex:1205`: use the established Banach-subspace relation
    `\preccurlyeq`, not `\preceq`, which Chapter 5 uses for the projection
    order.
14. `Banach_spaces.tex:1253`: specify continuous **linear** maps as the
    morphisms of the duality functor.
15. `Banach_spaces.tex:1254`: restore the missing superscript marker in
    `B^*`.
16. `Banach_spaces.tex:1327`: name the ambient Banach space `B`, not `M`, in
    the pair `(B,M)`.
17. `Banach_spaces.tex:1384`: require the complete metric space in the local
    Baire statement to be nonempty.
18. `Banach_spaces.tex:1447`: take
    `\sup\{\abs{a^{**}(f)}\colon a\in A\}`. The source supremum without
    modulus is invalid over complex scalars and does not prove boundedness.
19. `Banach_spaces.tex:1490--1495`: close the piecewise definition with the
    invisible delimiter `\right.` rather than a visible unmatched right
    brace.
20. `Banach_spaces.tex:1566,1574`: give the SOT and uniform/operator-norm
    convergence index entries distinct sort keys instead of reusing the WOT
    key.

The source-to-target math audit separately classifies localization-only
changes inside mathematical text (`if` to `jika`, English ordinal suffixes,
and natural Indonesian word order for projection phrases). They are not source
corrections. The cumulative Chapter 1--6 reader now resolves the earlier
Chapter 4 Alaoglu reference normally; its Chapter 7 and Chapter 11 references
remain exact `futurexref` endpoints until those chapters enter the reader.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 7

The following source candidates are adjudicated and applied in
`source/id-ID/compact_operators-id.tex`. The target preserves the complete
ordered environment, label, reference, citation, exercise, proof, hint, index,
defined-term, and formula topology except for the explicitly classified
corrections and reader-facing localizations locked by
`qa/check_ch07_translation.py`.

1. `compact_operators.tex:22--26`: retain both proposition environments exactly
   as published, while repairing the first copy's “its is complete” wording
   naturally in Indonesian. The duplicate remains visible because deleting it
   would change source topology.
2. `compact_operators.tex:117`: supply the missing article in “k be
   square-integrable function,” expressed naturally in Indonesian.
3. `compact_operators.tex:127--129`: close the parenthetical reference to the
   earlier example.
4. `compact_operators.tex:137`: use `\ofml K(B)`, matching the Banach space
   introduced by the example, rather than the undefined `\ofml K(H)`.
5. `compact_operators.tex:162--165`: remove the duplicated “that” construction
   naturally in Indonesian without changing the assertion.
6. `compact_operators.tex:299`: remove the stray closing parenthesis following
   the definition of the final space.
7. `compact_operators.tex:397--400`: require `\alpha\ge 0` in the homogeneity
   formula. At this point the trace has been defined only for positive
   operators, so arbitrary `\alpha\in\K` would take `\alpha T` outside the
   stated domain.
8. `compact_operators.tex:422`: use `e^k=Uf^k`, not `e^k=Tf^k`; the preceding
   sentence introduces `U` as the unique unitary carrying one orthonormal basis
   to the other.
9. `compact_operators.tex:425--430`: replace both instances of “is” by “if” in
   the defining conditions for a cone and a proper cone.
10. `compact_operators.tex:436--437`: bind the separable Hilbert space as `H`
    before the example forms the operator algebra `\ofml B(H)`.
11. `compact_operators.tex:497`: insert the missing comma in
    `\{e_1, \dots, e_n\}`.

The opening reference to the end of Chapter 5 is intentional and remains
unchanged: Chapter 7 resumes the operator-theoretic work after the intervening
Banach-space foundations in Chapter 6. The cumulative reader now resolves the
earlier Chapter 5 reference `chap_cpt_ops` normally. The three genuine later
references remain exact, honest pending endpoints:
`\futurexref{12.3.16}{00152171}`,
`\futurexref{12.3.17}{00152181}`, and
`\futurexref{11.5.7}{X_sqroot_op}`. TeX-only `\allowbreak` opportunities in
the long citation-only polar-decomposition proof are a layout reflow, not a
source correction; they remove a measured 2.28432-point overfull line without
changing visible content.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 8

The following source candidates are adjudicated for
`source/id-ID/spectrum-id.tex`. The frozen upstream member remains unchanged.
The target preserves the complete active source order through `\endinput`, all
environments, labels, reference and citation endpoints, exercises, proof and
hint surfaces, index and defined-term hooks, and mathematical topology except
for the explicitly classified corrections below and reader-facing
localization.

1. `spectrum.tex:17`: restore the missing word boundary after the closing
   parenthesis in `of~$a$)such`, expressed naturally in Indonesian.
2. `spectrum.tex:178--181`: state the equivalence involving `1/\lambda` for
   `\lambda\ne0`. The surrounding hypothesis says that `a` is invertible, so
   zero is already outside its spectrum; division by an arbitrary complex
   scalar was not well defined.
3. `spectrum.tex:348`: remove the stray closing parenthesis after the reference
   to Proposition `C073134`.
4. `spectrum.tex:372`: open the parenthetical expression with `\bigl(` rather
   than the mismatched right-delimiter command `\bigr(`.
5. `spectrum.tex:396--412`: define the Volterra operator on `C([0,1])` by the
   same displayed formula used in Example `000319`, while retaining that
   example as a formula precedent. The referenced example acts on
   `L_2([0,1])`; the source's unqualified identification silently changes the
   operator's domain.
6. `spectrum.tex:443--450`: bind the self-adjoint operator as acting on a
   Hilbert space `H` before the statement forms `\ofml B(H)` and `T=S^*S`.
7. `spectrum.tex:509`: supply *Teorema Pemetaan Spektral* as the theorem
   environment's optional title (`\begin{thm}[...]`) rather than as an
   unintended mandatory body group after `\begin{thm}`.
8. `spectrum.tex:547`: define the diagonal-entry set as
   `A=\{a_k\colon k\in\N\}`. The published `A=\cup_{k=1}^\infty a_k` attempts
   to take a union of scalars and is not a valid set definition.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 9

The following 26 source candidates are adjudicated and applied in
`source/id-ID/topvecspaces-id.tex`. The exact machine-verifiable ledger is
`provenance/SOURCE_CORRECTIONS_CH09.json`; it binds every inclusive source-line
range, classification, normalized source/target snippet hash, required target
anchor, forbidden malformed anchor, and the 551-record nonblank ordinal map.

Mechanical source repairs:

1. `topvecspaces.tex:88`: replace “nonempty sets of a set” by the intended
   nonempty **subsets** of the set.
2. `topvecspaces.tex:147`: remove the duplicated “the” in the net statement.
3. `topvecspaces.tex:172`: restore the missing map arrow in
   `\K\times X\sto X\colon` for scalar multiplication.
4. `topvecspaces.tex:181--184`: use the grammatical plural “category of
   topological vector spaces.”
5. `topvecspaces.tex:219`: remove the duplicated “every neighborhood” phrase.
6. `topvecspaces.tex:230--232`: use the set-family macro `\sfml U`, not the
   function-family macro `\fml U`.
7. `topvecspaces.tex:375`: remove the comma that incorrectly separates the
   subject “between topological vector spaces” from “is continuous.”
8. `topvecspaces.tex:436--437`: state that `X/M` is Hausdorff, not “a
   Hausdorff.”
9. `topvecspaces.tex:584`: use the singular “a locally convex space.”
10. `topvecspaces.tex:617--620`: say that `d` is a metric **on `X`**, rather
    than on `X\times X`; its two arguments are already expressed by `d(x,y)`.
11. `topvecspaces.tex:630--632`: keep the ambient space consistently `X`, not
    the undefined `V`, in the translation-invariant-metric statement.
12. `topvecspaces.tex:638`: remove the duplicated article in “a a countable
    family.”
13. `topvecspaces.tex:668`: replace “The there exists” by “There exists.”
14. `topvecspaces.tex:721`: replace “a open subset” by “an open subset.”
15. `topvecspaces.tex:738`: use the natural-number macro `\N`, not the plain
    letter `N`.
16. `topvecspaces.tex:742`: separate the multi-index coordinates with a comma,
    `(α_1,\dots,α_n)`, rather than a period.
17. `topvecspaces.tex:763--765`: repair the malformed phrase “of `F` a has
    finite diameter” to state that each bounded subset of `F` has finite
    diameter.

Mathematical source repairs:

18. `topvecspaces.tex:277--278`: require `X` to be a topological **vector**
    space in the proposition relating closed singletons and Hausdorffness.
19. `topvecspaces.tex:311--312`: likewise retain the topological-vector-space
    hypothesis in the corollary deducing regularity from closed singletons.
20. `topvecspaces.tex:352--356`: in the filter-completeness proof choose
    `B\in\sfml F`, not an unrelated subset `B\subseteq A`; this is the member
    whose closure is then shown to meet the candidate limit.
21. `topvecspaces.tex:559--561`: choose the nonzero vector in the subspace
    `V`, not merely in the ambient `X`, so the separation argument applies to
    the stated restricted topology.
22. `topvecspaces.tex:564--566`: supply the required Hausdorff hypothesis for
    the proposition asserting that the topology is generated by a separating
    family of Minkowski functionals.
23. `topvecspaces.tex:578--581`: type each Minkowski functional as real-valued,
    `V\sto\R`, rather than scalar-field-valued `V\sto\K` in the complex case.
24. `topvecspaces.tex:588--590`: state the Hahn--Banach consequence for the
    continuous linear functional `f` on `M`; the published sentence instead
    introduces an unrelated continuous seminorm `p`.
25. `topvecspaces.tex:640--642`: require the coefficient sequence to satisfy
    `\alpha_k>0` for every `k\in\N`, as needed for the displayed invariant
    metric to separate points and generate the intended topology.
26. `topvecspaces.tex:749--751`: define the Schwartz seminorm as the function
    value `\sbsb p{m,k}(f)`, not as a bare repeated definition of the symbol
    `\sbsb p{m,k}`.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.

## Chapter 10

The following 16 source candidates are adjudicated and applied in
`source/id-ID/distributions-id.tex`. The exact machine-verifiable ledger is
`provenance/SOURCE_CORRECTIONS_CH10.json`; it binds every inclusive source and
target line range, correction class, normalized snippet hash, and required
target anchor.

Mechanical source repairs:

1. `distributions.tex:54`: replace “if this system” by the intended “of this
   system.”
2. `distributions.tex:98`: supply the missing verb in “we will [be]
   interested.”
3. `distributions.tex:119`: state directly that the topology on `X_i` is the
   restriction of `\sfml T_{i+1}`, rather than using the malformed
   restriction-of-sets wording.
4. `distributions.tex:341`: repair the number agreement in “every test
   functions.”
5. `distributions.tex:393`: supply the missing relation in “generated [by] the
   family.”

Semantic and TeX source repairs:

6. `distributions.tex:405`: replace raw less-than/greater-than delimiters by
   semantic angle-bracket commands in the distributional-pairing formula.
7. `distributions.tex:456`: call `fu` a functional rather than a function
   before establishing that it is a distribution.

Mathematical source repairs:

8. `distributions.tex:29`: quantify the universal-property condition over the
   directed index set `D`, not `\N`.
9. `distributions.tex:57--73`: replace the false product/direct-sum quotient
   hint by the standard direct-sum quotient construction
   `W=\bigoplus_{i\in D}V_i`, relation span `N`, quotient `L=W/N`, and
   canonical maps. An independent universal-property review passed.
10. `distributions.tex:121`: restore the omitted subscript in the connecting
    morphism `\phi_{ji}`.
11. `distributions.tex:252--255`: require `f` to be locally integrable with
    respect to the stated regular Borel measure.
12. `distributions.tex:509`: restore the missing backslash in the integration
    domain `\R`.
13. `distributions.tex:559`: apply the convolution theorem to the transform of
    `f\ast g`, not to the pointwise product `fg`.
14. `distributions.tex:566`: type a general scalar-valued function with
    codomain `\K`, rather than only `\R`.
15. `distributions.tex:766`: restore the missing backslash in the integration
    domain `\R`.
16. `distributions.tex:778`: use the same lowercase derivative order `p` in
    numerator and denominator.

No upstream contact occurs during production. These entries are held for the
single deduplicated post-corpus report only if that report is separately
authorized.
