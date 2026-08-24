# FAOA-2015-CH17 build and QA receipt

Date: 2026-08-24  
Decision: **admitted**  
Whole-edition state: `in_progress`

This receipt admits the complete Indonesian Chapter 17, *Funktor K0*, and the
cumulative Chapters 1--17 PDF reader. It completes the source-order chapter
translation boundary. It does not claim that final front/back-matter
adaptation, the semantic accessible surface, the O001 mastery layer, or the
separately provenanced compact-spectral/SVD bridge are complete.

## Frozen unit and target

- Unit: `FAOA-2015-CH17`; source-order role: advanced continuation.
- Source: `source/upstream/K0_functor.tex`, 59,639 bytes / 1,362 CRLF records /
  SHA-256
  `e8ebcaa4e5dbc1cc9b907edb235465610f3bd61e0bfa1ce2f1b5b26e9abf8c6a`.
- Target: `source/id-ID/K0_functor-id.tex`, 61,673 bytes / 1,362 LF records /
  SHA-256
  `061ffd28907e2251fc8b01077888de3e11b3bce67fec1ba52b080c924a241059`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch17.tex`, 10,820 bytes / 346
  LF records / SHA-256
  `51b3f4d790e3d09ac6ac4c160284510e4827140ecaa5a961a46c880ae5c8bb39`.
- Canonical reader:
  `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-17.pdf`,
  2,432,395 bytes / 232 US-Letter pages / SHA-256
  `22fda5f25205f2a442c2b907db015fb4c93cb46cfcba6a1fa8814449469073f1`.

The official source ZIP/PDF authority and exact CC BY-SA 4.0 component
boundary remain frozen in `00_control/SOURCE_AUTHORITY.md`; no authority byte
was edited. The locked assembler `qa/assemble_ch17.py` is 10,774 bytes /
SHA-256
`8907030f81fb132176dad2f831cffbcba03a23b6f33eedffaa494e0b1c670a84`
and reproduces both target and cumulative master exactly.

## Translation, structure, and mathematics

The complete source inventory `qa/CH17_SOURCE_INVENTORY.md` is 13,441 bytes /
SHA-256
`96bd447b7629b428f51382a74bed5eb93425cb90b8d3ad1c371f202996f27e2f`.
The pretranslation mathematical review
`qa/CH17_PRETRANSLATION_MATH_REVIEW.md` is 17,583 bytes / SHA-256
`696b3610fc0799811492b77fe57affcb743aff38596a9fc6f8da39131d10a305`.
The locked checker report `qa/ch17-translation-report.json` is 15,667 bytes /
SHA-256
`1948b0b3298e70c3fd87df0075b32d6f5db439a44cdc4d1add89096af877697d`.
Its deterministic replays and two independent full-corpus reviews pass:

- eight ordered sections, 1,362-to-1,362 record topology, and 206 balanced
  environment openings/closings;
- 73 labels, 47 references, 12 active citations, 100 index hooks, 24
  defined-term hooks, and complete cumulative reference/bibliography closure;
- 63 propositions, 31 examples, 22 definitions, 22 proofs, 16 proof hints,
  seven notation blocks, two corollaries, one remark, and one exercise;
- 46 `bmatrix` blocks and 15 diagram surfaces with exact preserved topology;
- zero answer or solution environment, without inventing a missing source
  surface.

The authority has 1,047 parsed active math surfaces and the target has 1,048.
The one additional surface explicitly repairs the star-homomorphism category
at target record 1,104. Every other formula delta is classified by an exact
source-correction or localization range; the locked checker reports zero
unclassified differences. All 47 Chapter 17 reference occurrences resolve in
the cumulative 638-label master, and every citation key resolves.

The independent rereview is `qa/CH17_BILINGUAL_MATH_REVIEW.md`, 5,296 bytes /
SHA-256
`53fe4a4165cc3352fa7e29e5ff6f44e69e622d6bdd8dd85b6953ae38f4d3be21`.
It confirms natural id-ID prose, all formulas, matrices, diagrams, implication
directions, map types, labels/citations/references, controlled terms, and the
absence of active English instructional residue or mojibake.

Twenty-six explicit source-facing decisions are bound to exact ranges,
normalized snippets, anchors, and hashes in
`provenance/SOURCE_CORRECTIONS_CH17.json`, 53,256 bytes / SHA-256
`a2b84cfb272a22669920ee0ef4fd015929b353be651cc80700e370c91329257d`.
Among them, the target repairs the two reversed converse implications, the
codomain of `tau`, the unitary-path codomain, strict versus quotient
commutativity of block sum, the nonnegative-integer semigroup category,
projection-map category, split-section identity, nonunital aliases, norm
closure in an inductive limit, star-homomorphism classifications, and
nonnegative Bratteli multiplicities. The human-readable aggregate log is
`provenance/SOURCE_CORRECTIONS.md`, 49,970 bytes / SHA-256
`f2fb3821948f3fd1f7e09bf78921dc76220b5ea68175325f1403579377b72994`.
The frozen English authority remains byte-identical.

The terminology plan `provenance/CH17_TERMINOLOGY_PLAN.md` is 15,048 bytes /
SHA-256
`e57fe4efe837403e3f9fa130297403d48a9f9c7788647f671ef2d2dcf456b299`.
It locks distinctions among five equivalence relations, semigroup versus
group, star-homomorphism versus group homomorphism, half/split/full exactness,
inductive-limit norm closure, AF/CAR terminology, and Bratteli multiplicities.
The bounded Indonesian external terminology witness frozen at Chapter 11
remains the evidence boundary; no unsupported frequency claim is made.

## Deterministic build

The exact fixed build used `SOURCE_DATE_EPOCH=1444126743`. Two independent
clean replays produced byte-identical 2,432,395-byte PDFs with SHA-256
`22fda5f25205f2a442c2b907db015fb4c93cb46cfcba6a1fa8814449469073f1`.
All 20 hashed inputs remained unchanged after the visual and machine audits.
`qa/CH17_FINAL_BUILD_RESULT.json` is 1,719 bytes / SHA-256
`b88e5a0d12455ee78f04cb05fd2f27cb1f59f3ea25af1815a063ec561d8fd4e7`.
The locked build driver `qa/run_ch17_final_build.ps1` is 8,481 bytes /
SHA-256
`79dd08c455767f1c760ab8d6b0a102dd792002409ba6fe9a63d820dea95ed9d6`.

The final log contains zero TeX errors, undefined references/citations,
unresolved-reference summaries, rerun requests, multiply defined labels, or
missing characters. The two inherited Chapter 11 overfull boxes and three new
Chapter 17 boxes were rendered and inspected; no clipping or missing content
occurs. Raw machine-local build logs contain workstation paths and are
excluded from publication payloads.

## Visual, navigation, and accessibility evidence

All 232 pages were freshly rendered at 935x1210 pixels and inspected in three
independent non-overlapping ranges. The complete Chapter 17 surface, physical
pages 193--210, and the 300-dpi renders of its three overfull locations on
pages 195--197 pass. The bibliography occupies pages 211--212; the index
occupies pages 213--232. There is no clipping, overlap, damaged formula,
damaged diagram, black rectangle, or missing glyph. No page has ink in its
outer five-pixel border.

- Render manifest: `provenance/CH17_RENDER_MANIFEST.csv`, 26,569 bytes /
  SHA-256
  `2b3401c99ed6c81fe52f9094122fc48124b08df975dc323efd0a9410de2fcfd1`.
- Machine render audit: `qa/CH17_RENDER_AUDIT.json`, 4,943 bytes / SHA-256
  `d2c6d27efaabdd38995531c906a64c57509d99871e1486b3e12c1035a23f9549`.
- Human-visible audit:
  `qa/CH17_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 5,511 bytes / SHA-256
  `695585806d503baf87db26507ac646c95bb91afa9cad518f0e95ae980b6434c1`.

The PDF has 104 outline entries, 2,974 link annotations, 2,312 named
destinations, zero unresolved internal links, 48 embedded subset font objects
with Unicode maps, extractable Indonesian text, and catalog language `id-ID`.
It has no encryption, form, embedded file, JavaScript, launch action, rich
media, movie, sound, or screen annotation. It remains honestly untagged and
has no structure tree. This PDF checkpoint is navigable but does not satisfy
the goal's final semantic accessible-reader requirement, which remains active.

## Rights, privacy, and backend boundary

The wrapper preserves John M. Erdman's authorship, component credits,
CC BY-SA 4.0, change notice, ShareAlike, non-endorsement, and exact model
provenance `OpenAI Codex gpt-5.6-sol, Ultra`. `DIAGXY.TEX` remains
byte-identical under Michael Barr's notice. `TABLE.TEX`, badge artwork, and
excluded quotation surfaces are absent. No separately authored mastery or
bridge content is represented as Erdman-authored.

Bounded scans of the Chapter 17 target, wrapper, and extracted final PDF text
found no credential, token, private path, placeholder, or unsafe active
content. No upstream contact occurred.

The backend preflight locks the exact admitted Chapters 1--16 prefix under its
current manifest and passes the complete Chapter 17 structural closure. The
deterministic Chapter 17 append will bind this receipt and final artifacts,
then pass global stable-ID uniqueness, relation-endpoint closure, complete
source-and-target formula coverage, manifest, prefix-lock, and round-trip
validation. Aggregate backend identities are intentionally recorded after
this receipt exists, avoiding a circular receipt hash.

Chapter 17 is admitted. The source-order translation of all 17 chapters is now
complete. The edition remains `in_progress`; after backend binding and
checkpoint publication, the cursor advances to final front/back-matter
adaptation and the semantic accessible-reader surface.
