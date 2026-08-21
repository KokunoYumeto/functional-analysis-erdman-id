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
