# FAOA-2015-CH14 build and QA receipt

Date: 2026-08-24  
Decision: **admitted**  
Whole-edition state: `in_progress`

This receipt admits the complete Indonesian Chapter 14, *Aljabar Pengali*, and
the cumulative Chapters 1-14 reader. It does not claim that Chapters 15-17,
the final accessible surface, the O001 mastery layer, or the
compact-spectral/SVD bridge are complete.

## Frozen unit and target

- Unit: `FAOA-2015-CH14`; source-order role: advanced continuation.
- Source: `source/upstream/multiplier_algebras.tex`, 30,579 bytes / 687 CRLF
  records / SHA-256
  `d9bf8cf31a6e18a779863dcb397863430fe2daac9031a86354ce2274b42def7c`.
- Target: `source/id-ID/multiplier_algebras-id.tex`, 31,900 bytes / 687 LF
  records / SHA-256
  `2688ec9c2370371060aada680f5f95e9511ecb61cb99c2a126385f525a3c9142`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch14.tex`, 10,443 bytes / 343
  LF records / SHA-256
  `f04180a796707c6cb0c5f74082a8b4c25721d20ff3ea9235819939b11e1e50c9`.
- Canonical reader:
  `output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-14.pdf`,
  2,104,187 bytes / 193 US-Letter pages / SHA-256
  `3e82aca29ea623502e6ce5b2059238088d8e5b6f81d699463402aff16fe15b41`.

The official source ZIP/PDF authority and exact CC BY-SA 4.0 component
boundary remain those frozen in `00_control/SOURCE_AUTHORITY.md`; no authority
byte was edited.

## Translation, structure, and mathematics

`qa/CH14_SOURCE_INVENTORY.md` is 5,191 bytes / SHA-256
`7d8d6592087684260db482829233eef71f53cbab65289079134f06b706a42835`.
The locked checker report `qa/ch14-translation-report.json` is 3,882 bytes /
SHA-256
`3eda0f4973afac82a4627d0fd2f1878ca50df8f15730497555fb3695a4427e15`.
It was generated twice with byte-identical output and passes:

- three ordered sections;
- 70 balanced environment openings/closings, including 66 reader-semantic
  environments;
- 20 labels, 31 references, four citations, 79 index hooks, and 36
  defined-term hooks;
- complete cumulative resolution of all references and bibliography keys;
- two source exercises and three proof environments, including two proof
  hints, with no invented source answer or solution.

The source inventory has 650 top-level delimiter surfaces. The text-aware,
nonoverlapping extractor yields 644 ordered source surfaces and 644 ordered
target surfaces. Eight classified transformations exhaust their differences:
two source corrections, five exact surface reorderings required by Indonesian
grammar, and four localized in-formula prose mappings, with overlap among the
classified sets as documented by the checker. Every other mapped surface is
exact after the stated normalization. The independent review is
`qa/CH14_BILINGUAL_MATH_REVIEW.md`, 4,831 bytes / SHA-256
`375b48684106f6d4ad19c6f9bac9d7fe79c5f41b5a826fa6f01a39963a3cd043`.

Nine explicit source-facing changes are bound to exact line ranges, normalized
snippets, and hashes in `provenance/SOURCE_CORRECTIONS_CH14.json`, 15,994 bytes
/ SHA-256
`a58f45716a73667d7da25431b1c87a0c438e0f17c0592946283d672b5f29cb97`.
They include the undefined `f`/`\phi` identifier repair and the mathematical
reversal of the impossible inclusion `A\to J_0` to `J_0\hookrightarrow A`.
The aggregate source-correction log is 41,495 bytes / SHA-256
`43a42465760dbdc26ef53d51f9e1a37100251985742815493e8aa20e8686c117`.
The frozen English source remains byte-identical.

The terminology plan `provenance/CH14_TERMINOLOGY_PLAN.md` is 6,151 bytes /
SHA-256
`60116f0b282504d12b2a9313364f16c2cbec0f4544b715188ab06455e1ed05cf`.
It preserves admitted forms and controls the new scoped terms `modul
Hilbert-$A$`, `dapat diadjoinkan`, `aljabar lawan`, `ideal esensial`,
`kompaktifikasi`, and `aljabar pengali`. The only intentional English residue
is a cited publication title. No unsupported frequency claim is made.

## Deterministic build

The exact fixed build used `SOURCE_DATE_EPOCH=1444126743`. Two independent
clean `latexmk` replays produced byte-identical 2,104,187-byte PDFs with
SHA-256
`3e82aca29ea623502e6ce5b2059238088d8e5b6f81d699463402aff16fe15b41`.
All 17 hashed inputs remained unchanged. `qa/CH14_FINAL_BUILD_RESULT.json` is
1,148 bytes / SHA-256
`ab929c1604bfe36480a315ce8a93741f7a350e1042529b082a52bea312afea40`.

The final log contains zero TeX errors, undefined references/citations,
unresolved-reference summaries, rerun requests, multiply defined labels, or
missing characters. Chapter 14 adds no overfull box. Two pre-existing Chapter
11 overfull boxes and five underfull layout notices were rendered and
inspected; no clipping occurs. Raw machine-local build logs contain workstation
paths and are deliberately excluded from publication payloads.

## Visual, navigation, and accessibility evidence

All 193 pages were freshly rendered at 935x1210 pixels and inspected through
17 contact sheets. The complete Chapter 14 surface, physical pages 167-174,
was also inspected at full resolution. No page has ink in its outer five-pixel
border; there is no clipping, overlap, damaged formula, black rectangle, or
missing glyph. Ten blank front-matter or verso pages are intentional.

- Render manifest: `provenance/CH14_RENDER_MANIFEST.csv`, 22,105 bytes /
  SHA-256
  `3c1fc7b1c45d1689a8b8d87541831b9102839e6e66416b60f660be9bf204bb9d`.
- Machine render audit: `qa/CH14_RENDER_AUDIT.json`, 4,303 bytes / SHA-256
  `733a110197e4a2eca7cb60948e20c408e87b22a8f254fed4447753fe2bb13537`.
- Human-visible audit:
  `qa/CH14_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 3,242 bytes / SHA-256
  `b0fdf14ae176db50ade3829e323087053ac01a7097b37a6c47a240365b35247a`.

The PDF has 85 outline entries, 2,461 link annotations, embedded fonts,
ToUnicode maps, extractable text, and no encryption, forms, or JavaScript. It
remains honestly untagged and has no structure tree. This checkpoint is
navigable but does not satisfy the goal's final semantic accessible-reader
requirement, which remains active for the full corpus.

## Rights, privacy, and backend boundary

The wrapper preserves Erdman attribution, source links, CC BY-SA 4.0, change
notice, ShareAlike, non-endorsement, and exact model provenance
`OpenAI Codex gpt-5.6-sol, Ultra`. `DIAGXY.TEX` remains byte-identical under
Michael Barr's notice. `TABLE.TEX`, badge artwork, and excluded quotations are
not introduced. No separately authored mastery or bridge content is
represented as Erdman-authored.

Bounded scans of the Chapter 14 target, wrapper, and extracted final PDF text
found no credential, token, private-path, placeholder, or unsafe-link residue.
No upstream contact occurred.

The backend preflight independently locks the exact complete Chapters 1-13
prefix under SHA-256
`7eed0bb6a623e41e7015262b073e61469f3ba09f77e1aca604801acc977fa660`
and passes the complete Chapter 14 structural closure. The deterministic
Chapter 14 append will now bind this receipt and the final artifacts, then pass
global stable-ID uniqueness, relation-endpoint closure, manifest, prefix-lock,
and round-trip validation. Aggregate backend identities are intentionally
recorded after this receipt exists, avoiding a circular receipt hash.

Chapter 14 is admitted. The edition remains `in_progress`; after backend
binding and checkpoint publication, the cursor advances to `FAOA-2015-CH15`,
`source/upstream/fredholm_theory.tex`.
