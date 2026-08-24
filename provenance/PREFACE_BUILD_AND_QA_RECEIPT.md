# FAOA-2015-PREFACE build and QA receipt

Date: 2026-08-24  
Decision: **admitted**  
Whole-edition state: `in_progress`

This receipt admits the complete Indonesian preface and the cumulative
source-text reader containing the translated preface, all 17 admitted source
chapters, bibliography, and translated index topology. It completes the
reader's source-text translation boundary. It does not claim that the semantic
accessible HTML, separately authored O001 mastery/solution layer, or separately
authored compact-spectral/SVD bridge is complete.

## Exact authority and target

- Unit ID: `FAOA-2015-PREFACE`.
- Authority: `source/upstream/preface.tex`, 18,107 bytes / 351 CRLF records /
  ASCII / SHA-256
  `0976042bbb6ae3b8d1e5bb113a93d51169fada9d3e41f2d01435c76b6729edb9`.
- Target: `source/id-ID/preface-id.tex`, 18,140 bytes / 394 LF records /
  UTF-8 without BOM / SHA-256
  `c622dc9d9c1af4e5b1a6112c84eeff7328c778e8ef8643fc267f6fc6e3e7d564`.
- Complete-source master:
  `source/id-ID/functional-analysis-id-complete-source.tex`, 11,176 bytes /
  353 LF records / SHA-256
  `7f06919a8ec9088a3bc812fab962a48b5f1b3b0d5d3bce80eb21055f65089041`.
- Canonical reader:
  `output/pdf/analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf`,
  2,480,109 bytes / 238 US-Letter pages / SHA-256
  `efa2358b3c3e6e8c47e0caee9a02f6afe78d15bea1b0f1822ea8449d801b2b10`.

The master retains the exact 17-chapter include order and all 19 non-master
Chapter 17 build inputs byte-identically. It inserts the translated preface
between the table of contents and `\mainmatter`, preserves the bibliography
database and `\printindex`, and adds only `tabularx` as the table-layout
dependency needed by the replacement front-matter tables.

## Translation, mathematics, and topology

The deterministic translation checker passed **193 checks with zero
failures**. It proves:

- exact five-heading topology: preface plus Greek letters, Fraktur fonts,
  number-set notation, and function notation;
- ordered equality of all label, reference, equation-reference, and five
  citation keys;
- all 53 active index hooks plus the one preserved commented candidate;
- all 21 defined-term hooks and both source enumerations;
- exactly the two locally authored `center`/`tabularx` pairs needed to replace
  the excluded legacy table machinery;
- all 24 ordered Greek rows with the source's English name/pronunciation
  strings, all 26 ordered Fraktur rows with two headers, and all 20 number-set
  notation rows;
- both commutative-diagram topologies;
- 204 source dollar-math spans versus 205 target spans, where the sole added
  target span is the classified `PREFACE-C014` repair placing graph symbol
  `G` in math mode;
- exact preservation of all 19 inherited Chapter 17 non-master build inputs.

The checker is `qa/check_preface_translation.py`, 38,455 bytes / SHA-256
`dd56486b7c57449b65ab78e4f496c3cb2eaa3a25b2dbb2b6cfcc4a25b52bcb1e`.
Its deterministic report is `qa/preface-translation-report.json`, 69,035
bytes / SHA-256
`7091f4a505b6c69abbe706cdd4fe849c93f71406160ec97130302031b91b9c8b`.

Independent bilingual review covered every narrative paragraph, all 50 table
rows, all notation rows, citations, index hooks, label `C0009`, and both
diagrams. It resolved the complex-field scope, Halmos paraphrase, background
sentence attachment, `catatan` self-description, function synonyms,
`pracitra`/`citra invers`, `berkomutasi`/`diagram komutatif`, and source-mode
`G` repair. The final review is `qa/PREFACE_BILINGUAL_REVIEW.md`, 2,912 bytes /
SHA-256
`a58cdf3232204d91a8640934f3d464f3e832578438318cc543a4dc4cb72c12cd`.

All fourteen source decisions occur exactly once as markers and are
`applied_verified` in
`provenance/SOURCE_CORRECTIONS_PREFACE.json`, 12,159 bytes / SHA-256
`927a74c63cbbc625fb910bfd9a30915179e689d0b5eac64545d2aafcd0bb62ce`.
The aggregate human-readable correction log now contains the same bounded
preface decisions. No authority byte was modified.

## Deterministic build and all-page visual QA

The locked driver `qa/run_complete_source_final_build.ps1` verifies the
preface, master, and complete Chapter 17 dependency snapshot before building.
Two clean replays at the same fixed path with
`SOURCE_DATE_EPOCH=1444126743` produced byte-identical 2,480,109-byte PDFs
with the canonical hash above. All 21 inputs were unchanged.

The final log contains zero TeX errors, undefined references, undefined
citations, unresolved-reference summaries, rerun requests, multiply defined
labels, or missing characters. It contains exactly six inherited overfull
hboxes at 2.90276, 7.30707, 11.09703, 21.73163, 14.48387, and 3.32439 points;
the preface introduces none. The machine result is
`qa/COMPLETE_SOURCE_FINAL_BUILD_RESULT.json`, 1,913 bytes / SHA-256
`db8f799e2a42d6921db50580d6bcb668a8d374f7192a7ce47b542435b3dbf1e3`.

Every one of 238 pages was freshly rendered at 110 dpi and inspected in source
order. The title, license page, contents, both preface prose pages, 24-row
Greek table, 26-row Fraktur table, number notation, function page, both
diagrams, every chapter, bibliography, and all index columns are readable,
centered, page-filling, and unclipped. No page has ink in the outer five-pixel
border; minimum nonblank margins are 109 px left, 72 px top, 78 px right, and
60 px bottom. The twelve blank pages recorded in the audit are intentional
front-matter or chapter-transition versos.

The 238-row render manifest is
`provenance/COMPLETE_SOURCE_RENDER_MANIFEST.csv`, 27,263 bytes / SHA-256
`2379f5eb5b3b5944be1f70500ea60bb236ec4e0e05f08f679952207d146399e3`.
The render audit is `qa/COMPLETE_SOURCE_RENDER_AUDIT.json`, 4,971 bytes /
SHA-256
`92bb17327f1cbf4de707585f1356e29e5d7c086c309a931a08492f94685e3c85`.
The narrative audit is
`qa/COMPLETE_SOURCE_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 5,483 bytes /
SHA-256
`82c0205fa11a71a61db858cd31654c80408e30f5e492b410e619ee6f72605ace`.

## Navigation and accessibility truth

The PDF catalog language is `id-ID`. It has 109 outline entries, 3,043 link
annotations, 3,033 internal GoTo actions, 2,331 named destinations, and zero
unresolved internal links. All 49 font resources are embedded subsets with
Unicode maps. Extracted text is 896,493 bytes with 238 page delimiters, zero
replacement characters, zero recognized mojibake signatures, and zero private
local-path hits. There is no encryption, AcroForm, embedded file, attachment,
JavaScript, Launch action, or rich-media surface.

The PDF is honestly **untagged** and has no structure tree. This admitted PDF
is searchable and navigable, but it is not represented as the final semantic
accessible reader. That required HTML surface remains active work.

## Rights, provenance, and privacy

The wrapper preserves John M. Erdman's primary authorship, exact official
source links and hashes, CC BY-SA 4.0 license link, change notice,
ShareAlike, and non-endorsement. It records translation and technical editing
assistance as `OpenAI Codex gpt-5.6-sol, Ultra` at the user's direction without
displacing the author or component credits.

`DIAGXY.TEX` remains byte-identical under Michael Barr's embedded notice. The
reader does not include `TABLE.TEX`, badge artwork, `Wiener_quote.tex`, or the
direct Halmos quotation. The two table contents are reimplemented with ordinary
local LaTeX; the Halmos idea is paraphrased with attribution and citation. No
credential, token, private path, placeholder, or unsafe active content occurs
in the reader. No upstream contact occurred.

## Backend and admission decision

The preface backend preflight preserves the exact 27,633-record Chapter 1--17
aggregate as a byte prefix across all eleven aggregate files and adds 412
preface records. It covers one front-matter unit, nine semantic units, five
segments, 74 relations, 224 formula maps covering 223 source and 224 target
math surfaces, 53 index occurrences, 18 new terms and 21 term-use relations,
five citations, fourteen corrections, artifacts, and typed QA events. Global
stable IDs are unique, relation endpoints resolve, and JSONL/CSV round-trip is
deterministic.

This receipt is the non-circular admission witness. The final backend binding
will now add this receipt, final build, render, text/font, and
navigation/security artifacts; change the unit and admission event from
pending to admitted; replay exact Chapter 1--17 prefixes; and regenerate the
manifest and validation receipt. Final aggregate identities are therefore
recorded in durable state after this receipt exists, not inside the receipt
whose hash the backend binds.

`FAOA-2015-PREFACE` is admitted. The source-text reader—preface, all 17 source
chapters, bibliography, and index—is complete. The whole edition remains
`in_progress` while semantic accessibility, O001 mastery/solutions, and the
compact-spectral/SVD bridge remain.
