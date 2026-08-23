# Chapter 12 pretranslation mathematics and source review

## Scope and source identity

- Reviewed file only: `source/upstream/no_identity.tex`
- Source extent: 1,158 lines; 47,994 bytes
- Source SHA-256: `8DA3FFA45BCC07CBE1897A09F309DB51E1C5C38080459FFB1F6947BF45A20B6C`
- Review mode: static mathematical, cross-reference, index, citation, TeX, and translation-risk inspection before translation. No source or target text was edited, and no external bibliography or cited edition was consulted.

## Source topology

The chapter is organized into six substantive blocks, separated by unusually large runs of blank lines:

1. Lines 3--180: unitization of Banach algebras, modular ideals, characters, and the nonunital Gelfand transform.
2. Lines 198--373: exact sequences, extensions, direct sums, and strong equivalence.
3. Lines 392--639: unitization of `C^*`-algebras and the commutative Gelfand--Naimark theorem.
4. Lines 658--743: quasi-inverses, the circle operation, and the q-spectrum.
5. Lines 767--997: positive elements, ordered vector spaces, functional calculus, and order inequalities.
6. Lines 1022--1154: approximate identities, ideals and quotients, hereditary subalgebras, and inverse-closed subalgebras.

The large blank regions (especially lines 181--197, 375--391, 640--657, 744--766, and 998--1021) appear to be source-layout separators, not missing environments.

## Proven corrections / high-confidence defects

These can be corrected without resolving a mathematical convention or consulting an external source.

1. **Wrong index direction, lines 87--90.** The text defines `u` by `au-a\in J` and calls it a *right identity with respect to* `J`, but line 89 indexes it as `identity!left!with respect to an ideal`. Change that index entry to `identity!right!with respect to an ideal`. The later entry at line 95 correctly indexes the left identity.

2. **Malformed Gelfand-transform signature, lines 175--179 (especially 177).** The display reads
   `\Gamma = \Gamma_A\colon \fml C_0(\Delta A)\colon a \mapsto ...`,
   omitting both the domain and the mapping arrow. The intended type is
   `\Gamma=\Gamma_A\colon A \sto \fml C_0(\Delta A)\colon a\mapsto\widehat a` (using the book's existing macros).

3. **Broken equation label, lines 219--247.** The short exact sequence is labelled `001500202i2` at line 219, but lines 226, 240, and 247 all refer to `001500202i`. Within this file there is no label `001500202i`. The repeated references make changing the label to `001500202i` the strongest correction candidate; alternatively all three references would have to acquire the trailing `2`.

4. **Incorrect `C^*` typesetting, line 448.** `$C*$-norm` prints an ordinary asterisk. It should be `$C^*$-norm`.

5. **Undefined equivalence terminology, line 505.** The section defines *strongly equivalent* extensions (lines 338--350), while line 505 says only that `\wt A` is “not equivalent” to `A\oplus\C`. The proposition itself says “not isomorphic” (line 428). Replace line 505 with either “not strongly equivalent to the direct sum extension” or the proposition's precise “not isomorphic to `A\oplus\C`.”

6. **False blanket use of “unital” in Gelfand--Naimark II, lines 554--565.** The theorem allows any commutative `C^*`-algebra, including a nonunital one, and maps it onto `\fml C_0(\Delta A)`, which is generally nonunital. Thus “isometric unital `*`-isomorphism” at line 564 cannot be correct in the stated generality. Delete “unital” there (and revise the parallel wording “isometrically unitally” at line 556), or restrict the theorem to unital `A` and replace `C_0` by `C`; the surrounding chapter clearly supports the former correction.

7. **Malformed index display text, lines 708--711.** Line 709 has `\index{q@$Q_A$ (quasi-invertible elements}`: the TeX group closes, but the human-readable parenthesis does not. Add `)` before `}`.

8. **Undeclared algebra variable, lines 887--893.** The proposition begins “If `c` is an element of a `C^*`-algebra” but item (iii) says `a\in A`; `A` has not been named. Change the opening to “If `c` is an element of a `C^*`-algebra `A`”.

9. **Missing unital hypothesis / nonexistent symbol, lines 945--947.** The proposition uses `\vc 1_A` although `A` is stated only to be a `C^*`-algebra. Either say “unital `C^*`-algebra `A`” or explicitly interpret the inequality in the unitization `\wt A`. As written, `1_A` need not exist.

10. **Index typo, lines 1029--1035.** `sequential!approxiamte identity` at line 1033 should be `sequential!approximate identity`.

11. **Mechanical prose/spacing defects.** These are safe editorial corrections: “The proof this result” -> “The proof of this result” (line 431); “unitization of `C^*`-algebra `A`” -> “unitization of a `C^*`-algebra `A`” (line 435); “given a algebra” -> “given an algebra” (line 536); “If `A` is a algebra” -> “If `A` is an algebra” (line 728); add the missing space after `\begin{prop}` at lines 670, 689, and 961. At line 907 insert spacing before the reference (`theorem}~\ref{001807}`).

## Questions requiring editorial or convention confirmation

These should not be silently “fixed” during translation.

1. **Meaning of “unital subalgebra,” lines 1133--1148.** The assertion that invertibility in `B` implies invertibility in `A`, and the inverse-closed converse, require the inclusion to preserve a common identity (and normally require `A` itself to be unital). If this book has already defined “unital subalgebra” to mean “contains the ambient identity,” the passage is sound. Otherwise the hypotheses must say so explicitly; a unital corner with a different unit is a counterexample to the unqualified formulation.

2. **Norm notation in the auxiliary lemma, lines 465--468.** The same symbol `\norm a` is used for the norm already present on `B` and the seminorm newly pulled back to `A`. It is mathematically readable but locally overloaded. Consider distinguishing the source norm or saying explicitly “define `p(a)=\|\phi(a)\|_B`.”

3. **Step numbering reference, lines 464--483.** The second case resets the enumerator to 8, so the lemma is item (9); line 482's “Use (9)” is therefore probably intentional. Preserve the explicit counter reset, and verify the rendered numbering before changing this reference.

4. **Map punctuation, lines 322--324.** `\pi_2\colon A\oplus B\sto B: (a,b)\mapsto b` uses a raw colon after `B`, unlike the source's usual `\colon`. This is a typography consistency candidate, not a mathematical error.

5. **External references cannot be closed within this file.** References at lines 64, 201, 207, 269, 334, 519--520, 558, 611, 707, and 864 target labels outside this source. Their existence and displayed object types must be checked in the complete build. No duplicate `\label` value was observed within this file.

## Formula and variable consistency watchlist

- Keep the three different unitization notations distinct: `A_e` for the Banach-algebra unitization (line 59), `\wt A` for the `C^*`-unitization (from line 420), and `A^\sharp` for the auxiliary left-multiplication realization (line 471). They are related but not typographical variants.
- In lines 442--456 the unital case deliberately adds a *new* identity and obtains `\wt A\cong A\oplus\C`; do not normalize this to the convention that a unital algebra is its own unitization.
- The split arrow at line 453 carries both `Q` and `\psi`; the prose at lines 454--455 defines the quotient map and its splitting. Both labels must survive translation.
- At lines 591--596, `\wt f` is a piecewise extension of `f` to `\wt X`; it is not the same use of a tilde as algebra unitization.
- Lines 659--663 reverse the visual order that readers may expect: “left quasi-inverse” means `ba=a+b`, while “right quasi-inverse” means `ab=a+b`. Preserve the order of factors.
- The q-spectrum at lines 728--742 is defined to contain `0` by construction. The comparison with the usual spectrum is asserted only for `\lambda\ne0`; do not strengthen it to equality in the unital case.
- In line 865, `C^*(\vc1,a)` may live in the unitization when `A` is nonunital; the proof prompt explicitly asks why the functional-calculus root returns to `A`. Translation should not replace it with `C^*(a)` without mathematical review.
- The positivity order is an order on the self-adjoint real vector-space part (made explicit at lines 850--852), even when formulas are written for elements of the ambient complex algebra.
- At lines 1052--1059 the scalar function `f(t)=t/(1-t)` “induces” a map on positive contractions through continuous functional calculus. Translate “induces” in a way that does not suggest direct scalar substitution without functional calculus.
- In line 1099, positivity of `a` is implicit in the meaningful inequality `x^*x\le a`; it need not be added as a separate assumption, though adding it would improve readability.

## Cross-reference, citation, and index risks

- The definite internal label failure is `001500202i2` versus `001500202i` (lines 219, 226, 240, 247), described above.
- Line 247 uses `\ref` for an equation while nearby occurrences use `\eqref`; after repairing the label, standardize to `\eqref` if equation references are meant to carry parentheses.
- Citation keys used are `Erdman:2007`, `Wegge-Olsen:1993`, `Davidson:1996`, `Murphy:1990`, `Fillmore:1996`, `Blackadar:2006`, `DoranB:1986`, and `HigsonR:2000`. Preserve keys byte-for-byte. The theorem/page claims at lines 122, 607, 910, 1081--1082, and 1103 require bibliography/edition verification in a later full-project pass.
- Preserve `\index` sort/display syntax, including `@`, `!`, and the leading `<` conventions. Translate only human-readable display/descriptive text when the index policy calls for it; do not translate control-like sort keys casually.
- Besides the two proven index defects (lines 89 and 709) and the spelling typo (line 1033), repeated index entries such as `cone!positive` are legitimate alternate access paths, not duplicates to delete.

## Nontrivial TeX constructs that must survive

- `xymatrix` diagrams and arrow syntax occur throughout lines 209--231, 271--290, 317--320, 344--348, 357--370, 422--425, 452--455, 501--503, 630--634, and 1114--1115. In particular, `\two/->` with the backtick modifier at line 453 is specialized XY-pic syntax.
- Numerous project macros carry semantics: `\vc`, `\fml`, `\ofml`, `\M`, `\cat`, `\sto`, `\df`, `\ns`, `\wt`, `\wh`, `\sbsb`, `\ssst`, `\cstariso`, `\inv`, `\ran`, `\conj`, `\breve`, and `\norm`. Do not replace them opportunistically during prose translation.
- There is a `lem` environment nested inside an `enumerate` inside a proof (lines 461--506), with `\setcounter{enumi}{8}`. Preserve nesting and counter state.
- Manual layout controls include `\vskip`, `\noindent`, `\hbox`, explicit thin spaces, `\,`, `\!`, and `%` line-ending suppression. Translation can change line wrapping but must not strand these controls or move index commands into math inadvertently.
- Piecewise notation at lines 591--596 uses an `array` inside `\left\{`; matrix examples occur at lines 925--929 and 994--996. Preserve row separators and brace balance.
- The definition text at lines 836--839 deliberately opens `\df{partial ordering` before intervening `\index` commands and closes it at “induced by}`. This unusual cross-line macro argument is balanced and should not be mechanically reordered.

## Translation traps

- The title “SURVIVAL WITHOUT IDENTITY” is mathematical wordplay about nonunital algebras. Translate “identity” as the algebraic identity element, not personal identity.
- Keep “identity,” “unit,” “unitization,” “approximate identity,” and “approximate unit” terminologically coordinated. The source treats the last two as synonyms but uses “identity” in other specialized phrases such as “right identity with respect to `J`.”
- The source explicitly reports incompatible conventions for “extension of `A` by `B`” versus “extension of `B` by `A`” (lines 240--251). Preserve the ambiguity and the author attributions; do not choose one orientation in translation.
- From line 253 onward, bare “ideal” in a `C^*`-algebra means a closed two-sided `*`-ideal. “Algebraic ideal” and “algebraic `*`-ideal” intentionally remove parts of that convention.
- The book uses a nonstandard convention in which the one-point compactification of an already compact space gains a new isolated point (lines 604--611). Preserve the caveat.
- Terms such as “positive,” “positive cone,” “proper cone,” “preordering,” “partial ordering,” “order isomorphism,” “hereditary,” and “inverse closed” form a tightly linked terminology chain; translate consistently across definitions and later propositions.
- “Character” means a nonzero multiplicative linear functional, `\Delta A` is its character space, and `\phi_\infty` is the distinguished added character. Avoid a literary rendering of “character.”
- “Range” (`\ran`) denotes the image of a map, while “spectrum,” “q-spectrum,” “spectral radius,” and “range of the Gelfand transform” are distinct notions.
- Authorial asides (“Everyone should go through all the details...”, lines 431--433; “See my remarks...”, lines 604--607) are source voice. Any modernization of gendered phrasing or first-person reference should be an explicit editorial policy decision, not an unnoticed translation change.

## Quotation and rights assessment

No substantial third-party quotation appears in this source. The TeX quotation marks around “almost” (line 736) and “same thing” (line 617) are brief scare quotes, while the literature discussion at lines 240--251 paraphrases attributed terminology. Rights risk from quoted prose is therefore low. Preserve all citations and avoid expanding the cited statements into reconstructed quotations. The author's first-person and pedagogical asides are original source prose and should be translated faithfully unless a separate editorial policy authorizes adaptation.

## Pretranslation disposition

Translation may proceed after the proven defects are either corrected upstream or recorded as intentional translator corrections. The two mathematically consequential gates are the nonunital Gelfand--Naimark wording (lines 554--565) and the missing unital hypothesis/unitization interpretation at lines 945--947. The common-identity convention at lines 1133--1148 should be confirmed from the book's global conventions before that passage is finalized.

## Corpus-wide adjudication before translation

A bounded whole-source label and convention check changes or closes three of
the preliminary questions above:

1. The local equation label must **remain** `001500202i2`.
   `source/upstream/Banach_spaces.tex:744` already defines the global label
   `001500202i`, so renaming the Chapter 12 label would create a duplicate and
   silently redirect the earlier Banach-space equation. The proven repair is
   instead to change the three Chapter 12 references at source lines 226, 240,
   and 247 from `001500202i` to `001500202i2`.
2. The unit convention at lines 1133--1148 is already explicit in
   `source/upstream/categories.tex:242-250`: a *unital subalgebra* contains the
   ambient algebra's multiplicative identity. The inverse-closed passage is
   therefore sound under the book's own definition and needs no mathematical
   change; the translation must preserve that established meaning.
3. The notation `1_A` is defined for a unital algebra in
   `source/upstream/categories.tex:229-234`. Consequently proposition
   `0018203` is ill-typed for a general nonunital `A`. The scope-preserving
   repair is to state
   `\\norm a\\,\\vc 1_{\\wt A} \\pm a \\ge \\vc 0` in the unitization
   `\\wt A`, rather than adding a unital hypothesis that would weaken the
   proposition and its later use.

The nonunital Gelfand--Naimark repair remains necessary: remove “unitally” and
“unital” from the prose and theorem while retaining the isometric
`*`-isomorphism onto `\\fml C_0(\\Delta A)`. These decisions are source
corrections, not license to change any other identifier or hypothesis.
