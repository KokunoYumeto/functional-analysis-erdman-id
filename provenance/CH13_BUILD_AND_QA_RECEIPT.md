# FAOA-2015-CH13 build and QA receipt

Date: 2026-08-24  
Decision: **admitted**  
Whole-edition state: `in_progress`

This receipt admits the complete Indonesian Chapter 13, *Konstruksi
Gelfand-Naimark-Segal*, and the cumulative Chapters 1–13 reader. It does not
claim that Chapters 14–17, the final accessible surface, the O001 mastery
layer, or the compact-spectral/SVD bridge are complete.

## Frozen unit and target

- Unit: `FAOA-2015-CH13`; source-order role: advanced continuation.
- Source: `source/upstream/GNS_construction.tex`, 11,965 bytes / 289 CRLF
  records / SHA-256
  `fcc774cecc607d9860540da7b757ae04a3c43afe9d9a17e8c881e077f02682c1`.
- Target: `source/id-ID/GNS_construction-id.tex`, 12,601 bytes / 289 LF
  records / SHA-256
  `4c95b339702180ef8f2ea42cfba9e19a60a1740ca7d25a0568a6290f0170371f`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch13.tex`, 10,345 bytes / 342
  LF records / SHA-256
  `d1734ea09a576c9e5c8f38bb9430a132e8cd38551c9b0c6cbd9bf65b4923c87e`.
- Canonical reader:
  `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-13.pdf`,
  2,031,973 bytes / 183 US-Letter pages / SHA-256
  `b7810718cb9a633c694aed126fc5c10786864650b076c2ad5bb7329191db3b65`.

The official source ZIP/PDF authority and exact CC BY-SA 4.0 component
boundary remain those frozen in `00_control/SOURCE_AUTHORITY.md`; no authority
byte was edited.

## Translation, structure, and mathematics

`qa/CH13_SOURCE_INVENTORY.md` is 3,366 bytes / SHA-256
`33d436f4bc86942aafe303278e9eb18a275bd04cd0e8a334258c1703548483fe`.
The locked checker report `qa/ch13-translation-report.json` is 2,514 bytes /
SHA-256
`68601ff9901558ab72f8f722a4f9360d75785531599a37babb999241998fd04b`.
It passes:

- three ordered sections;
- 32 balanced environment openings/closings: 10 propositions, seven
  definitions, five examples, two theorems, two corollaries, two proofs, one
  caution, one convention, one exercise, and one notation environment;
- seven labels, two references, seven citation occurrences, 28 index hooks,
  and 13 defined-term hooks;
- complete cumulative resolution of both references and all six bibliography
  keys;
- one source exercise, with no invented source hint, answer, or solution.

The source has 237 top-level math surfaces and the target 239. Four ordered
edit blocks exhaust the difference: positivity-quantifier consolidation, the
general norm-one state definition plus unital equivalent, and restoration of
the omitted algebra name. Every other math surface is exact after
line-ending-aware normalization. The independent review is
`qa/CH13_BILINGUAL_MATH_REVIEW.md`, 2,663 bytes / SHA-256
`8a1097eeb50df6c17d0e4b9c435ff75efbef1d2b4b9b66d5d7fa31a1e2c69997`.

Six explicit source-facing changes are bound to exact line ranges, normalized
snippets, and hashes in `provenance/SOURCE_CORRECTIONS_CH13.json`, 10,653 bytes
/ SHA-256
`9fdcdc4fe5b8f3d621ace0ac0efad2ae684766efcb4341d38bbc2e923e652a05`.
The aggregate source-correction log is 39,736 bytes / SHA-256
`508828263c3d06b6b8183a570f352589aa10b80035121d6ae3e59fae7d4b451d`.
The two substantive corrections make the definition and identity-norm
criterion valid for the nonunital context introduced in Chapter 12; they are
not silent changes to the frozen source.

The terminology record `provenance/CH13_TERMINOLOGY_PLAN.md` is 5,721 bytes /
SHA-256
`2e995b15fa954cf2f27e859f6226dca9e73208628ad8b86471977d1b6de31191`.
It preserves the admitted `padat`, `swaadjoin`, `jumlah langsung`, and related
forms and adds scoped GNS/state/representation terminology without claiming
external attestation that the bounded Indonesian witness does not provide.

## Deterministic build

The exact fixed build used `SOURCE_DATE_EPOCH=1444126743`. Two independent
clean `latexmk` replays produced byte-identical 2,031,973-byte PDFs with
SHA-256
`b7810718cb9a633c694aed126fc5c10786864650b076c2ad5bb7329191db3b65`.
All 16 hashed inputs remained unchanged. `qa/CH13_FINAL_BUILD_RESULT.json` is
1,148 bytes / SHA-256
`683e6be79a67fb4a728024c2986acf0b20e64ce92681b4cd9e50aea5aa29ddc0`.

The final log contains zero TeX errors, undefined references/citations,
unresolved-reference summaries, rerun requests, multiply defined labels, or
missing characters. Two pre-existing Chapter 11 overfull boxes and five
underfull URL/verso notices were rendered and inspected; no clipping occurs.
Raw machine-local build logs contain workstation paths and are deliberately
excluded from publication payloads.

## Visual, navigation, and accessibility evidence

All 183 pages were freshly rendered at 935×1210 pixels and inspected. No page
has ink in its outer five-pixel border; there is no clipping, overlap, damaged
formula, black rectangle, or missing glyph. Nine blank verso pages are
intentional. Chapter 13 reader pages 157–159 (physical pages 161–163) received
additional full-resolution inspection; physical page 164 is its blank verso.

- Render manifest: `provenance/CH13_RENDER_MANIFEST.csv`, 20,966 bytes /
  SHA-256
  `b7ab64c7ccaa059f972910f56d410ba5d133e960e3ed40aa8962bfe0f4bdd02a`.
- Machine render audit: `qa/CH13_RENDER_AUDIT.json`, 4,089 bytes / SHA-256
  `dc4f604c5ce8d54e6fdde61fc31c4a3a394470dded00fbc6f58934655694c16f`.
- Human-visible audit:
  `qa/CH13_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 2,959 bytes / SHA-256
  `f1d3d53562619ad55b635a42aa6cd19ca0ac1b61af5e1407b6ead0241c554bf7`.

The PDF has 81 outline entries, 2,343 link annotations, embedded subset fonts,
Unicode maps, extractable text, and no encryption/forms/JavaScript. It remains
honestly untagged and has no structure tree. This checkpoint is navigable but
does not satisfy the goal's final semantic accessible-reader requirement,
which remains active for the full corpus.

## Rights, privacy, and backend boundary

The wrapper preserves Erdman attribution, source links, CC BY-SA 4.0, change
notice, ShareAlike, non-endorsement, and exact model provenance
`OpenAI Codex gpt-5.6-sol, Ultra`. `DIAGXY.TEX` remains byte-identical under
Michael Barr's notice. `TABLE.TEX`, badge artwork, and excluded quotations are
not introduced. No separately authored mastery/bridge content is represented
as Erdman-authored.

Bounded scans of the target, wrapper, evidence, and PDF found no credential,
token, private-path, or unsafe-link residue. No upstream contact occurred.

The deterministic Chapter 13 backend append will preserve the complete
Chapter 1–12 prefix and add Chapter 13 semantic, segment, formula, index,
terminology, correction, exercise-support, artifact, relation, rights, and QA
records. Because this receipt's hash is itself a final-binding input, aggregate
backend identities are recorded only after the receipt exists, avoiding a
circular receipt hash.

Chapter 13 is admitted. The edition remains `in_progress`; after backend
binding and checkpoint publication, the cursor advances to `FAOA-2015-CH14`,
`source/upstream/multiplier_algebras.tex`.
