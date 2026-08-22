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
