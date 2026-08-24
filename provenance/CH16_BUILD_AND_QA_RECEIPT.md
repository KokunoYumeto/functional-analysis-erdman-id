# FAOA-2015-CH16 build and QA receipt

Date: 2026-08-24  
Decision: **admitted**  
Whole-edition state: `in_progress`

This receipt admits the complete Indonesian Chapter 16, *Ekstensi*, and the
cumulative Chapters 1-16 reader. It does not claim that Chapter 17, the final
semantic accessible surface, the O001 mastery layer, or the separately
provenanced compact-spectral/SVD bridge are complete.

## Frozen unit and target

- Unit: `FAOA-2015-CH16`; source-order role: advanced continuation.
- Source: `source/upstream/extensions.tex`, 42,614 bytes / 1,000 CRLF records /
  SHA-256
  `e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318`.
- Target: `source/id-ID/extensions-id.tex`, 43,804 bytes / 1,000 LF records /
  SHA-256
  `59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch16.tex`, 10,679 bytes / 345
  LF records / SHA-256
  `6e528b0193d3179b58e44169430d043fa5399f7c860f09d832eb3ccd954a5388`.
- Canonical reader:
  `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-16.pdf`,
  2,278,823 bytes / 213 US-Letter pages / SHA-256
  `8af194778cd60630ec767cfb381e4798253aa5d2ee205d2e72489cf3b5d90ef5`.

The official source ZIP/PDF authority and exact CC BY-SA 4.0 component
boundary remain those frozen in `00_control/SOURCE_AUTHORITY.md`; no authority
byte was edited. The locked assembler `qa/assemble_ch16.py` is 8,908 bytes /
SHA-256
`fca4e703549412ce8cb7640b170eb3b6f44260ca685f2f243176fcf5b523c485`
and reproduces both target and cumulative master exactly.

## Translation, structure, and mathematics

The complete source inventory `qa/CH16_SOURCE_INVENTORY.md` is 9,031 bytes /
SHA-256
`899c11dce4eacaf5639512bbb02e649c2fa8ebab336a3d8d34bc4d058e9d9298`.
The locked checker report `qa/ch16-translation-report.json` is 9,133 bytes /
SHA-256
`bef72510042b339451afee90a5dc93c13b65abe1c562257677aa069494d98374`.
Its deterministic replays and the independent bilingual rereview pass:

- four ordered sections: essentially normal operators, Toeplitz operators,
  addition of extensions, and completely positive maps;
- 142 balanced environment openings/closings, including 124 reader-semantic
  environments;
- 36 labels, 28 references, 59 citations, 107 index hooks, 29 defined-term
  hooks, and one manual equation tag;
- complete cumulative resolution of every reference and bibliography key;
- 15 examples and 31 proof environments;
- zero formal exercise, hint, answer, or solution environments, without
  inventing a missing source surface.

The source has 702 ordered active top-level math surfaces and the target has
700. Fifteen classified transformations exhaust every difference: the two
typed unitary-conjugation repairs; one norm-bracing normalization; one
localized conjunction; the Calkin-algebra macro repair; correction of the
section map from `\beta` to `T`; two repairs of the punctured-plane fundamental
group; one diagram-parenthesis repair; one pullback-codomain repair; the
restructured and named unitary in the equivalence definition; two localized
ordinals; and removal of the false star-homomorphism requirement from the
semisplit-lift statement. There are zero unclassified math differences.

The independent rereview is `qa/CH16_BILINGUAL_MATH_REVIEW.md`, 8,789 bytes /
SHA-256
`61f190988b4e585442795b4bed72de8442d70f776631fc94dc4a502f3cac9b0f`.
It confirms natural id-ID prose, the complete source topology, all map
directions and hypotheses, exact labels/citations/references, no active English
instructional residue or mojibake, and consistent admitted terminology.

Fifteen explicit source-facing decisions are bound to exact line ranges,
normalized snippets, anchors, and hashes in
`provenance/SOURCE_CORRECTIONS_CH16.json`, 32,044 bytes / SHA-256
`9a224bf8833e3504009b696ae3afad4e74967add24c2bedcaf7f44d4d2666794`.
The decisions include:

1. both ill-typed `UTU^*` conjugations become `U^*TU` for the declared
   unitary `U:H\to K`;
2. Proposition `005134` gains the required infinite-dimensional scope;
3. the Calkin-algebra macro, source typo, continuous-section map, Douglas
   locator, punctured-plane fundamental group, stale index locator, diagram
   parenthesis, pullback codomain, missing unitary name, and two Toeplitz index
   spellings are repaired;
4. Voiculescu's theorem gains its required unital completely positive linear
   hypothesis; and
5. the semisplit criterion retains a unital `\tau` and uses a unital
   completely positive linear lift rather than a star-homomorphic lift, which
   would characterize a split extension.

The aggregate human-readable log is
`provenance/SOURCE_CORRECTIONS.md`, 46,189 bytes / SHA-256
`64b32dcff72e36ef4b5bd6d11293be1ae53f3568757d6687c06e8ecac60431ae`.
The frozen English authority remains byte-identical.

The terminology plan `provenance/CH16_TERMINOLOGY_PLAN.md` is 12,546 bytes /
SHA-256
`b1dcdefa587d9c9e9aeafc3d680d2facbb89dea43939f517a11c99e191bf879c`.
It preserves established forms including `swaadjoin`, `ekuivalen uniter secara
esensial`, `operator Toeplitz`, `aljabar Calkin`, `ekstensi`, `semiterbelah`,
`pemetaan positif lengkap`, `representasi tak terdegenerasi`, and `nuklir`.
The bounded Indonesian external terminology witness already frozen at Chapter
11 remains the evidence boundary; no unsupported usage-frequency claim is
made.

## Deterministic build

The exact fixed build used `SOURCE_DATE_EPOCH=1444126743`. Two independent
clean `latexmk` replays produced byte-identical 2,278,823-byte PDFs with
SHA-256
`8af194778cd60630ec767cfb381e4798253aa5d2ee205d2e72489cf3b5d90ef5`.
All 19 hashed inputs remained unchanged. `qa/CH16_FINAL_BUILD_RESULT.json` is
1,441 bytes / SHA-256
`fb38212312f2b17b68934398e563f82128035d6717a85aa6687f7a684b8ccaae`.
The locked build driver `qa/run_ch16_final_build.ps1` is 8,451 bytes /
SHA-256
`1971e9aec764a18e53875de3b3192ee6caec1a8fd4dcf607eb637d7fc8f83f25`.

The final log contains zero TeX errors, undefined references/citations,
unresolved-reference summaries, rerun requests, multiply defined labels, or
missing characters. Chapter 16 adds no overfull box. The two inherited Chapter
11 overfull boxes, 7.30707 pt and 11.09703 pt, four underfull hboxes, one
underfull vbox, font-shape fallbacks, and PDF-string warnings were rendered and
inspected; no clipping or missing content occurs. Raw machine-local build logs
contain workstation paths and are excluded from publication payloads.

## Visual, navigation, and accessibility evidence

All 213 pages were freshly rendered at 935x1210 pixels and inspected through
18 contact sheets. The complete Chapter 16 surface, physical pages 181-191,
was also inspected at full resolution; physical page 192 is an intentional
blank verso, the bibliography occupies pages 193-194, and the index occupies
pages 195-213. No page has ink in its outer five-pixel border; there is no
clipping, overlap, damaged formula or diagram, black rectangle, or missing
glyph. Chapter 16 is centered and fills the established reader page area.

- Render manifest: `provenance/CH16_RENDER_MANIFEST.csv`, 24,385 bytes /
  SHA-256
  `930d84c8b15c5b2c352538ee40e923cca5642cccd2229179a7366d28c310db1b`.
- Machine render audit: `qa/CH16_RENDER_AUDIT.json`, 4,529 bytes / SHA-256
  `1262a4702d243b693891ebe39c75d8ec7f60290a770f7dbfa15e241f93bc72ec`.
- Human-visible audit:
  `qa/CH16_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 4,842 bytes / SHA-256
  `f85efd706ae90890cc7d1d2f317fc6102d9c7e10c667a2c9caa9670705638f3d`.

The PDF has 95 outline entries, 2,796 link annotations, 2,141 named
destinations, zero unresolved internal links, 47 embedded font objects with
Unicode maps, extractable Indonesian text, and catalog language `id-ID`. It
has no encryption, form, embedded file, JavaScript, launch action, rich media,
movie, sound, or screen annotation. It remains honestly untagged and has no
structure tree. This checkpoint is navigable but does not satisfy the goal's
final semantic accessible-reader requirement, which remains active.

## Rights, privacy, and backend boundary

The wrapper preserves John M. Erdman's authorship, component credits,
CC BY-SA 4.0, change notice, ShareAlike, non-endorsement, and exact model
provenance `OpenAI Codex gpt-5.6-sol, Ultra`. `DIAGXY.TEX` remains
byte-identical under Michael Barr's notice. `TABLE.TEX`, badge artwork, and
excluded quotation surfaces are not introduced. No separately authored
mastery or bridge content is represented as Erdman-authored.

Bounded scans of the Chapter 16 target, wrapper, and extracted final PDF text
found no credential, token, private path, placeholder, or unsafe-link residue.
No upstream contact occurred.

The backend preflight locks the exact admitted Chapters 1-15 prefix under its
current manifest and passes the complete Chapter 16 structural closure. The
deterministic Chapter 16 append will bind this receipt and final artifacts,
then pass global stable-ID uniqueness, relation-endpoint closure, complete
source-and-target formula coverage, manifest, prefix-lock, and round-trip
validation. Aggregate backend identities are intentionally recorded after
this receipt exists, avoiding a circular receipt hash.

Chapter 16 is admitted. The edition remains `in_progress`; after backend
binding and checkpoint publication, the cursor advances to `FAOA-2015-CH17`,
`source/upstream/K0_functor.tex`.
