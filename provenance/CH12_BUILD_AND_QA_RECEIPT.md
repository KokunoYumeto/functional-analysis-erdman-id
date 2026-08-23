# FAOA-2015-CH12 build and QA receipt

Date: 2026-08-23  
Decision: **admitted**  
Course role: `advanced_continuation`

This receipt admits the complete Indonesian Chapter 12, *Bertahan tanpa
Identitas*, and the cumulative Chapter 1--12 reader. Translation, mathematics,
source topology, references, terminology, rights, deterministic build,
page-by-page visual layout, navigation, technical accessibility, privacy, and
the evidence required for modular-backend binding pass. This does not claim
that Chapters 13--17, semantic HTML, the O001 solved-mastery layer, or the
original compact-spectral/SVD bridge are complete; the whole edition remains
`in_progress`.

## Exact source and target identity

- Frozen source: `source/upstream/no_identity.tex`, 47,994 bytes / 1,158 CRLF
  records / SHA-256
  `8da3ffa45bcc07cbe1897a09f309db51e1c5c38080459ffb1f6947bf45a20b6c`.
- Admitted target: `source/id-ID/no_identity-id.tex`, 49,730 bytes / 1,173 LF
  records / SHA-256
  `da74193601c80828c8bebb59f20f82481c47627a746fc6c841602d538837d884`.
- Rebound Chapter 11 target after the whole-edition terminology reconciliation:
  `source/id-ID/Gelfand_Naimark-id.tex`, 32,558 bytes / 764 LF records /
  SHA-256
  `2756540bd5c58e405ee07e10b00d102fada7c21e806d59f072a8afbd24587bde`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch12.tex`, 10,275 bytes / 341 LF
  records / SHA-256
  `d84965e27ee26d71575838a42a8410cf5956b967d188d77a040c0f018fd007de`.
- Canonical reader:
  `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-12.pdf`,
  2,001,449 bytes / 179 US-Letter pages / SHA-256
  `476b1f1fd6ca82deddeeb9edac1b07286567ede5663a6df32906a36dd3ea5ab6`.

The target contains all six source sections in order: unitization of Banach
algebras; exact sequences and extensions; unitization of C-star algebras;
quasi-inverses; positive elements; and approximate identities. The source
inventory is `qa/CH12_SOURCE_INVENTORY.md`, 4,621 bytes / SHA-256
`4a1af34420ee87c94130da95b86badacf6522d577bf0cea60a3738d03c637cb6`.

## Structural, mathematical, and language replay

`qa/ch12-translation-report.json`, 2,223 bytes / SHA-256
`0bd7e7b328be5737e3611096beaee3e9c42c8b29ae2605e99e8c0a7e6541cc8b`,
passes with zero errors. It verifies:

- six ordered sections, 154 environment openings / 308 balanced environment
  tokens, 65 unique labels, 46 references, 17 citations, 102 index hooks, and
  42 defined-term hooks;
- 12 proofs, including eight explicit proof hints, two citation-only proof
  pointers, and two plain proofs;
- zero exercise, problem, answer, or solution environments, faithfully
  reflecting the source surface;
- all 927 source and 931 target mathematical surfaces, with eight classified
  edit blocks and no unexplained delta; and
- zero active placeholders, unintended English prose, mojibake signatures, or
  private-path residue.

The independent bilingual/mathematical rereview found no reader-facing defect
and confirmed the six-section mathematics, environment/reference/citation/index
topology, natural Indonesian prose, author credits, and exact model string. It
identified two evidence-ledger defects rather than translation defects: the
target line/anchor for correction 020 and the declared leading-whitespace
normalization. Both were corrected and the ledger/checker were replayed before
admission.

The 29 classified repairs and mathematical localizations are locked in
`provenance/SOURCE_CORRECTIONS_CH12.json`, 35,824 bytes / SHA-256
`10e253d32ef1677c8d1f2cb65e78d41bb1bb0818ba72a5e4ca0872044723805c`.
The cumulative human-readable ledger now includes Chapters 11 and 12 at
`provenance/SOURCE_CORRECTIONS.md`, 38,275 bytes / SHA-256
`127bb9406f45bf82fa92dbb251527bd1fee11b347a0f04c0d338e99d0f1e9c7d`.
No upstream contact occurred.

## Indonesian terminology gate and model provenance

The requested arXiv-first Indonesian terminology check had already been
completed and was verified rather than repeated. The bounded official arXiv
search found no suitable Indonesian functional-analysis TeX source; the
documented fallback directly inspected the official UNDIP article PDF and an
official ITB functional-analysis curriculum surface. Those sources support the
existing field-level vocabulary and do not attest a more authoritative
specialized compound for *self-adjoint*.

The cumulative corpus check did expose an internal glossary contradiction:
Chapter 1 and the admitted pre-Chapter-11 corpus use `swaadjoin`, while a later
glossary record incorrectly preferred `swadjoin`. The edition now consistently
prefers `swaadjoin`, with `swadjoin` and `adjoin-diri` retained as recognition
variants. The decision and historical-release treatment are recorded in
`provenance/SELF_ADJOINT_TERMINOLOGY_ADJUDICATION.md`, 2,322 bytes / SHA-256
`ad5b60165004920b1f3ff0d58fcbd50633df45336856171e09ea7cd7345fad21`.

The reader and durable provenance use the exact model identification
**OpenAI Codex gpt-5.6-sol, Ultra**. John M. Erdman's authorship, Michael
Barr's component notice, and all other source credits remain intact; the model
identification does not displace them.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex, and
  Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`; 15 exact task-local build
  inputs were hashed before the run and remained unchanged.
- Two fully cleaned replays in the same fixed output directory produced
  byte-identical PDFs: 2,001,449 bytes / 179 US-Letter pages / SHA-256
  `476b1f1fd6ca82deddeeb9edac1b07286567ede5663a6df32906a36dd3ea5ab6`.
- Machine result: `qa/CH12_FINAL_BUILD_RESULT.json`, 887 bytes / SHA-256
  `8388eb15288bc6a1c91bb75b594faa93869197e1a89ac9b73e9662a743ef2b8e`.
- Both final logs and the retained fixed-path log are byte-identical: 58,542
  bytes / SHA-256
  `fa99ee3c6d778dc92b70ba9b0ab946e3aad4bf1b27f2aa481999d130efd19b34`.
- Blocking counts are zero: TeX/package errors, fatal or emergency stops,
  unresolved references or citations, rerun-required notices, multiply
  defined labels, missing characters, duplicate or nonexistent destinations,
  and BibTeX warnings.
- MakeIndex accepted 1,691 entries, rejected zero, wrote 2,050 index lines,
  and emitted zero warnings.

Four inherited underfull hboxes remain in the long front-matter source
URL/hash paragraph. The only overfull hboxes are the two already inspected
Chapter 11 lines, 7.30707 pt and 11.09703 pt; neither clips or crosses the page
edge. One underfull vbox marks the normal two-page bibliography transition.
The provisional Chapter 12 render had two undesirable `homomorfisme-*` line
breaks; two target-only `\newline`/`\mbox` reflow treatments keep the compounds
intact and remove both Chapter 12 overfull warnings without changing any math
surface.

## Complete visual and technical accessibility closure

All 179 pages were freshly rendered with Poppler at 110 dpi. The render set is
179 PNGs / 44,758,222 aggregate bytes, each 935 by 1,210 pixels. The exact
manifest is `provenance/CH12_RENDER_MANIFEST.csv`, 20,516 bytes / SHA-256
`2600580ca40a2fd17a6f7e1336c97b417769be125810b6907ac61a808127f1e7`;
the formal image audit is `qa/CH12_RENDER_AUDIT.json`, 3,874 bytes / SHA-256
`d6ceb8601b600fee7ae508060cfb9a4d5c780d634f7a9a6cfce1b24b1084a0c6`.

All 15 contact sheets were inspected. Every page inherited unchanged from the
provisional render was byte-identical; only physical pages 151 and 159 changed,
and both repaired pages were inspected again at full resolution. The complete
Chapter 12 surface, physical pages 147--159, was also inspected at full
resolution. No clipping, overlap, damaged glyph, stranded mathematical star,
broken diagram, unexpected blank, edge collision, header/footer defect, or
unreadable formula remains. Minimum nonblank clear margins are 109/72/93/60
pixels (left/top/right/bottom), and no page has ink in the outer five pixels.
The only blank pages are intentional versos 20, 48, 78, 100, 114, 136, 146,
and 160.

The independent object-level audit is
`qa/CH12_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 5,331 bytes / SHA-256
`a710ed99b4fd2627a1d27529a7ebbd05d8e51c24c549b1e0e5a2b2b48769fd0c`.
It verifies 77/77 resolved outline entries, 1,830 named destinations, 2,287
valid annotation-level internal links, eight public URI links over six unique
targets, and zero unsafe actions. All 45 font objects are embedded/subsetted
and carry ToUnicode maps. Text extraction yields 179 page segments with zero
replacement characters, NULs, or local paths. The PDF is unencrypted and has
no forms, widgets, attachments, embedded files, JavaScript, launch/remote-GoTo
actions, or additional actions.

The PDF remains honestly untagged and has no structure tree. It is therefore
not claimed as a standalone semantically accessible PDF. Semantic HTML and/or
a tagged derivative remains an edition-level requirement and is nonblocking
only for this verified chapter checkpoint.

## Rights, privacy, and backend admission boundary

The wrapper preserves Erdman attribution, the CC BY-SA 4.0 link, translation
and technical-change notices, ShareAlike, no additional restrictions, and
non-endorsement. `DIAGXY.TEX` remains byte-identical under Michael Barr's
notice. `TABLE.TEX`, badge artwork, and excluded quotations are not introduced.
No separately authored mastery support or compact-spectral/SVD bridge material
is represented as Erdman-authored content. Bounded privacy scans found no
credential, token, private-path, or unsafe-link residue.

The deterministic Chapter 12 backend operation preserves stable IDs, performs
the authorized Chapter 11 derived-record spelling reconciliation, and appends
the Chapter 12 semantic, segment, formula, index, terminology, correction,
artifact, relation, rights, and QA records. Because the receipt hash is an
input to final binding, aggregate backend identities are recorded only after
this receipt exists, avoiding a circular receipt hash.

Chapter 12 is admitted. The whole edition remains `in_progress`; after backend
binding and checkpoint publication, the source-order translation cursor
advances to `FAOA-2015-CH13`, `source/upstream/GNS_construction.tex`.
