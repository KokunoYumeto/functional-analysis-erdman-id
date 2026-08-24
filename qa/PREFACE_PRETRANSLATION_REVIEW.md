# FAOA-2015-PREFACE pretranslation review

Date: 2026-08-24  
Decision: **admissible for contiguous id-ID production with the locked repairs and adaptations below**  
Production state: **review only; no target or wrapper edited**

## Review basis

This review covers the complete frozen `source/upstream/preface.tex`, 18,107
bytes / 351 CRLF records / SHA-256
`0976042bbb6ae3b8d1e5bb113a93d51169fada9d3e41f2d01435c76b6729edb9`.
It was checked against:

- `00_control/DURABLE_GOAL_AND_WORKFLOW.md`;
- `00_control/CURRENT_STATE.md` and `00_control/CURRENT_CURSOR.md`;
- `00_control/SOURCE_AUTHORITY.md`, 4,901 bytes / SHA-256
  `c3e4866e5134aacdb3b7a82a44d014bf9b9acee3827b1271d1ab75d190387d6a`;
- the official web and PDF masters;
- the current cumulative wrapper, SHA-256
  `51b3f4d790e3d09ac6ac4c160284510e4827140ecaa5a961a46c880ae5c8bb39`;
- `backend/terminology.jsonl`, 171,497 bytes / 407 records / SHA-256
  `2464af7ef8add6e5e01c95a73e967c64f47eacf20d4146e432e1378be890fb2a`;
- `backend/terminology_qa.jsonl`, 9,232 bytes / seven records / SHA-256
  `0be61180b43ca8e314bc3323696a0836ed82f505153444373584d1ac640cc3c8`;
- `backend/rights.jsonl`, 1,385 bytes / four records / SHA-256
  `fe2176f18b74e451f4589f72e015ccb3ac03fe20f51eaed989f7c36d244445b8`.

The exact topology and safe split are frozen in
`qa/PREFACE_SOURCE_INVENTORY.md`. The ordered proposed dispositions are frozen
in `provenance/SOURCE_CORRECTIONS_PREFACE.json`; none is yet applied.

## Narrative and curricular reading

The preface has five coherent roles that must remain visibly distinct:

1. Erdman's activity-oriented pedagogy and the invitation to verify results
   that have neither a proof nor a proof reference;
2. the two-course origin, modest prerequisites, and relation between
   finite-dimensional spectral theory and functional analysis/operator
   algebras;
3. the incomplete-sequel/scope statement and pointers to background notes;
4. the electronic-document and ShareAlike rationale, including the historical
   author contact statement;
5. four reference sections for Greek letters, Fraktur, standard number sets,
   and function notation.

Natural Indonesian prose should retain Erdman's first-person voice and humor
without translating English syntax mechanically. The activity invitations are
important reader-contract content, not disposable preamble. The statement that
some results are deliberately left for verification must also remain separate
from the later, independently authored O001 mastery/solution layer.

## High-confidence source repairs

The following are source defects or formal-scope defects, not stylistic
preferences:

1. **Lines 33--35 — missing complex-field scope.** The second and third pivotal
   observations use unitary diagonalization/equivalence. Chapter 1 identifies
   the relevant spectral theorem as the theorem for finite-dimensional
   **complex** inner-product spaces. The target must add `kompleks` to the
   ambient space for both observations; otherwise the statements are
   overbroad over real inner-product spaces.
2. **Line 49 — `advanced calculous`.** This is the typographical error
   `calculous` for `calculus`; translate the corrected meaning as `kalkulus
   lanjut`.
3. **Lines 187, 189, and 191 — zero included but called positive.** The sets
   `\R^+={x:x\ge0}`, `\Q^+={x:x\ge0}`, and `\Z^+={0,1,2,...}` are
   nonnegative under the displayed definitions. Preserve every formula and the
   plus notation, but call the three sets `bilangan ... tak negatif`. Keep
   `\N={1,2,3,...}` as the book's natural-number convention.
4. **Line 193 — missing punctuation before the gloss.** Insert the grammatical
   separator before “the first n natural numbers” in the Indonesian sentence;
   the set formula is unchanged.
5. **Line 308 — `in for`.** The definition must read semantically “surjective
   if for every ...”; the target must say `surjektif jika untuk setiap ...`.
6. **Lines 310--313 — unclosed parenthesis.** The parenthetical synonym for
   `bijective` opens before `or` and lacks its closing parenthesis. Close it
   after the translated `korespondensi satu-satu`.

No other high-confidence mathematical defect was found in the function
definition, image/preimage formulas, interval notation, or diagram equations.
The `disk`/`disc` spelling alternation is not a mathematical discrepancy; both
map consistently to `cakram` in Indonesian.

Posttranslation addendum: the independent bilingual comparison found that the
second defining condition at source line 236 typesets its mathematical `G` in
text mode. The applied target sets that occurrence as `$G$`; the additive
record is `FAOA-2015-PREFACE-CORR-014`, appended without renumbering the
thirteen stable pretranslation records.

## Mathematical and structural preservation rules

- Preserve the three-item and two-item enumerations in order.
- Preserve all number-set, interval, function, image, inverse-image, range,
  and restriction formulas byte-equivalently at the TeX-token level except
  ordinary whitespace/line wrapping and the explicitly recorded repairs.
- Preserve `C0009` as the source label. Because it follows a starred section
  and has no source inbound reference, add a unique hyperlink anchor without
  inventing a section number.
- Preserve all five citation keys exactly. Do not turn citation pointers into
  imported text or silently update the cited editions.
- Preserve all 53 active index hooks and their hierarchy while translating the
  reader-facing terms; keep the commented line-274 candidate commented unless
  a separate index decision is made.
- Preserve the 21 `\df` roles and their repeated distinctions: image of a
  point, image of a set, image/range of a function, and inverse image are not
  interchangeable backend concepts.
- Preserve both visible diagrams and their exact arrow/equality semantics.
  Add semantic text alternatives in the accessible surface.
- Retain the source's explicit page transitions where they remain useful, but
  allow ordinary reflow when a translated table requires it. Logical section
  and stable IDs, not physical page numbers, control identity.

## Locked rights adaptations

### Halmos surface

Lines 3--4 reproduce a short third-party Halmos quotation. The target must not
reproduce it. Instead it must state in original Indonesian prose that Halmos,
in the cited book, emphasized learning mathematics through mathematical
practice. Preserve `Paul Halmos`, the book title, and `\cite{Halmos:1982}`;
remove quotation marks and do not reconstruct the English sentence.

### Table machinery

The two reference tables are Erdman-selected substantive data, but their TeX
machinery comes from `TABLE.TEX`, whose redistribution rights are not
established. Rebuild both with ordinary locally authored LaTeX. Acceptance
requires three columns and 24 Greek rows for the first table, three columns and
26 Fraktur rows for the second, the same row order and glyphs, and zero custom
`TABLE.TEX` commands in the target. The Greek pronunciation column must remain
explicitly described as approximate English pronunciation rather than being
misrepresented as Indonesian phonology.

### Edition notices and dependencies

The wrapper's visible attribution, exact CC BY-SA 4.0 link, change notice,
ShareAlike statement, non-endorsement, source identities, and exact model
provenance `OpenAI Codex gpt-5.6-sol, Ultra` remain controlling. The preface's
historical ShareAlike discussion may be translated naturally, but it must not
downgrade or replace the exact wrapper notice. `DIAGXY.TEX` remains
byte-identical under Michael Barr's notice. Badge artwork, `Wiener_quote.tex`,
and `TABLE.TEX` remain absent.

## Terminology decisions that control production

The detailed mapping is in `provenance/PREFACE_TERMINOLOGY_PLAN.md`. The
highest-risk distinctions are:

- `function` -> `fungsi`; generic `map/mapping` -> `pemetaan`;
  `transformation` -> `transformasi`, while preserving the source statement
  that all three are synonymous in this book;
- `domain` -> `domain`; `codomain` -> `kodomain`; `input/target/output space`
  -> `ruang masukan/ruang sasaran/ruang keluaran`;
- `image` -> `citra`; `range` -> `jangkauan`; `inverse image` -> `pracitra`
  with `citra invers` retained as a recognition synonym;
- `restriction` -> `pembatasan`; `graph` -> `graf`;
- `one-to-one` -> `satu-satu`; `one-to-one correspondence` ->
  `korespondensi satu-satu`; `commute` -> `berkomutasi`; `commutative diagram`
  -> `diagram komutatif`;
- `positive` in the three zero-containing number sets -> `tak negatif`, while
  `positive` elsewhere retains `positif` when zero is not included by the
  stated definition.

## Source-to-target map and safe assembly

Use one target unit, provisionally `source/id-ID/preface-id.tex`, assembled in
the seven exhaustive source fragments `PREFACE-F01` through `PREFACE-F07` from
the inventory. Each source fragment maps to exactly one ordered target
fragment. Fragments may expand or contract in line count, but may not overlap,
reorder, or absorb another fragment's semantic content.

The wrapper integration is additive only:

1. keep `\frontmatter`, the translated title/license/source notice, and
   `\tableofcontents`;
2. include `preface-id` after the table of contents and before `\mainmatter`;
3. add a reader-visible `Prakata` navigation/TOC destination without assigning
   a source-nonexistent chapter number;
4. keep all 17 admitted chapter includes byte-identical and in the same order;
5. keep bibliography and index generation after `\backmatter`.

## Future admission gates

Translation may begin from this review, but admission requires all of the
following after the target exists:

- exact source/target fragment coverage and an applied correction ledger;
- balanced section/list/display/diagram topology;
- formula-token and label/citation/index/defined-term closure;
- explicit proof that both tables contain all 50 data rows and no excluded
  macro dependency;
- Indonesian residue, terminology, mathematical, rights, privacy, and
  non-endorsement checks;
- two byte-identical fixed-epoch builds, fresh all-page rendering, table and
  diagram visual inspection, navigation/font/security checks, and honest
  accessibility reporting;
- append-only backend records with stable front-matter/section/table/term/
  formula/index/asset IDs and resolved relation endpoints.

No upstream contact, Git operation, wrapper edit, target edit, backend edit, or
publication was performed in this pretranslation review.
