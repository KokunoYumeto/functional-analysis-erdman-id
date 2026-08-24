# FAOA-2015-CH15 build and QA receipt

Date: 2026-08-24  
Decision: **admitted**  
Whole-edition state: `in_progress`

This receipt admits the complete Indonesian Chapter 15, *Teori Fredholm*, and
the cumulative Chapters 1-15 reader. It does not claim that Chapters 16-17,
the final accessible surface, the O001 mastery layer, or the
compact-spectral/SVD bridge are complete.

## Frozen unit and target

- Unit: `FAOA-2015-CH15`; source-order role: advanced continuation.
- Source: `source/upstream/fredholm_theory.tex`, 16,977 bytes / 444 CRLF
  records / SHA-256
  `0ef2e5be3c716a099e8609a84528d77ad6387ec531c52f9890d4e34175c57d91`.
- Target: `source/id-ID/fredholm_theory-id.tex`, 17,672 bytes / 444 LF
  records / SHA-256
  `174b1ad2557f7dfa10e8171bd7482d907f858389b509f4d55de9cc785e2b43ba`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch15.tex`, 10,541 bytes / 344
  LF records / SHA-256
  `f2df36c70dcca86f44687efe450ea46a5611be2d1170a9ded16dbfbfcdb73a33`.
- Canonical reader:
  `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-15.pdf`,
  2,156,827 bytes / 200 US-Letter pages / SHA-256
  `5b8d5d5f44671f4695dea7f470d6ea7bb63fd2a0ff459aa8e8fb1a0c0faac7c7`.

The official source ZIP/PDF authority and exact CC BY-SA 4.0 component
boundary remain those frozen in `00_control/SOURCE_AUTHORITY.md`; no authority
byte was edited.

## Translation, structure, and mathematics

`qa/CH15_SOURCE_INVENTORY.md` is 5,246 bytes / SHA-256
`b27bb18855c4ca1fd819163fe68c5e452b51ce898aac7e4bdb54ff03eb989b57`.
The locked checker report `qa/ch15-translation-report.json` is 5,942 bytes /
SHA-256
`ae12ef71a0c4fa09895ac3bbb547da1b89e994f5b23a3551fddf324379f2d84d`.
Its deterministic replays and the independent bilingual rereview pass:

- four ordered sections;
- 60 balanced environment openings/closings, including 50 reader-semantic
  environments;
- 33 labels, 27 references, 17 citations, 46 index hooks, 11 defined-term
  hooks, and 12 manual equation tags;
- complete cumulative resolution of every reference and bibliography key;
- eight examples, 13 proof environments, and two proof hints;
- zero formal exercise, answer, or solution environments, without inventing
  any missing source surface.

The source has 203 ordered top-level math surfaces and the target has 204.
Twelve classified transformations exhaust the differences: one inserted
nonzero-scalar hypothesis in Alternative I; six localized conjunctions inside
the tagged systems; one localized ordinal; two nonzero-scalar replacements;
one deletion of the false `SK=KS` condition; and one insertion of the missing
ambient-space identifier `B`. Every other ordered surface is exact after the
stated normalization. The backend mapping must preserve the removed `SK=KS`
as an explicit source-only deletion rather than hiding it behind an unrelated
target formula.

The independent review is `qa/CH15_BILINGUAL_MATH_REVIEW.md`, 6,538 bytes /
SHA-256
`ae0d17272540c21ef730150199ccf66b8a98fa0897e923c3d433f0dc55a556ae`.
Its final typography rereview confirms that deleting the redundant Indonesian
word `suatu` from Proposition 15.2.3 changes no mathematical content or
identifier and eliminates the chapter's only overfull line.

Nine explicit source-facing decisions are bound to exact line ranges,
normalized snippets, and hashes in
`provenance/SOURCE_CORRECTIONS_CH15.json`, 21,257 bytes / SHA-256
`c33a8ab24250c376e63ce6fd45aeb42cdd4590a169f9a00efab705fac087e887`.
Seven are mathematical source repairs, one is a mechanical prose/index repair,
and one is a formal-scope clarification. They include the three necessary
nonzero-scalar hypotheses, removal of the false commuting condition, repair of
the closed-subspace-sum claim, definition of the ambient quotient space, the
standard cross-space Fredholm convention, and the infinite-dimensional
hypothesis for index surjectivity. The aggregate human-readable log is
`provenance/SOURCE_CORRECTIONS.md`, 43,492 bytes / SHA-256
`85fe4b1afc625359ab6e43dad3b76b2ae8989c23e831627a8ec8a0ff655f9add`.
The frozen English source remains byte-identical.

The terminology plan `provenance/CH15_TERMINOLOGY_PLAN.md` is 4,598 bytes /
SHA-256
`e790b352a689ce0169a133a7fce469eda1391bd61ba811b4abbb6b50ac25ed5c`.
It preserves the admitted forms and controls the Fredholm-specific terms
`operator Riesz--Schauder`, `kokernel`, `kodimensi`, `aljabar Calkin`,
`operator Fredholm`, `indeks Fredholm`, `lintasan`, `terhubung oleh lintasan`,
`homotop`, and `komponen lintasan`. No unsupported frequency claim is made.

## Deterministic build

The exact fixed build used `SOURCE_DATE_EPOCH=1444126743`. Two independent
clean `latexmk` replays produced byte-identical 2,156,827-byte PDFs with
SHA-256
`5b8d5d5f44671f4695dea7f470d6ea7bb63fd2a0ff459aa8e8fb1a0c0faac7c7`.
All 18 hashed inputs remained unchanged. `qa/CH15_FINAL_BUILD_RESULT.json` is
1,148 bytes / SHA-256
`545cc604baf5cb720d7205eac83865a16af5629edc0b392e7dc79fba6e1a6ffe`.

The final log contains zero TeX errors, undefined references/citations,
unresolved-reference summaries, rerun requests, multiply defined labels, or
missing characters. Chapter 15 adds no overfull box after the final reflow.
Two inherited Chapter 11 overfull boxes and five underfull layout notices were
rendered and inspected; no clipping occurs. Raw machine-local build logs
contain workstation paths and are deliberately excluded from publication
payloads.

## Visual, navigation, and accessibility evidence

All 200 pages were freshly rendered at 935x1210 pixels and inspected through
17 contact sheets. The complete Chapter 15 surface, physical pages 175-179,
was also inspected at full resolution; page 180 is an intentional blank verso.
No page has ink in its outer five-pixel border; there is no clipping, overlap,
damaged formula, black rectangle, or missing glyph.

- Render manifest: `provenance/CH15_RENDER_MANIFEST.csv`, 22,901 bytes /
  SHA-256
  `1b4aae6c68668641aa4f86eb6aba87720017df9676773b532dbcf7da06265567`.
- Machine render audit: `qa/CH15_RENDER_AUDIT.json`, 4,313 bytes / SHA-256
  `294705139b6c1a8dd46cbb725579b0114633a0ed58740d0b41d2214414717048`.
- Human-visible audit:
  `qa/CH15_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 3,648 bytes / SHA-256
  `90fcfd11e32a8406a6d5cb5d3cd4c6fcc71fe7a6afae159fe94985e0921bc3c9`.

The PDF has 90 outline entries, 2,568 link annotations, 2,021 named
destinations, zero unresolved internal links, embedded fonts, Unicode maps,
extractable text, and no encryption, forms, embedded files, rich media, or
JavaScript. It remains honestly untagged and has no structure tree. This
checkpoint is navigable but does not satisfy the goal's final semantic
accessible-reader requirement, which remains active for the full corpus.

## Rights, privacy, and backend boundary

The wrapper preserves John M. Erdman's authorship, component credits,
CC BY-SA 4.0, change notice, ShareAlike, non-endorsement, and exact model
provenance `OpenAI Codex gpt-5.6-sol, Ultra`. `DIAGXY.TEX` remains
byte-identical under Michael Barr's notice. `TABLE.TEX`, badge artwork, and
excluded quotation surfaces are not introduced. No separately authored
mastery or bridge content is represented as Erdman-authored.

Bounded scans of the Chapter 15 target, wrapper, and extracted final PDF text
found no credential, token, private path, placeholder, or unsafe-link residue.
No upstream contact occurred.

The backend preflight locks the exact admitted Chapters 1-14 prefix under its
current manifest and passes the complete Chapter 15 structural closure. The
deterministic Chapter 15 append will bind this receipt and final artifacts,
then pass global stable-ID uniqueness, relation-endpoint closure, complete
source-and-target formula coverage, manifest, prefix-lock, and round-trip
validation. Aggregate backend identities are intentionally recorded after
this receipt exists, avoiding a circular receipt hash.

Chapter 15 is admitted. The edition remains `in_progress`; after backend
binding and checkpoint publication, the cursor advances to `FAOA-2015-CH16`,
`source/upstream/extensions.tex`.
