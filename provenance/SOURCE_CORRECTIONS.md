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
