# Complete-source PDF visual and accessibility audit

Date: 2026-08-24  
Reader boundary: translated preface, Chapters 1--17, bibliography, and index  
Result: **pass for this source-text checkpoint; honestly untagged**

## Exact reader and deterministic build

- Path: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf`
- Bytes: **2,480,109**
- SHA-256: `efa2358b3c3e6e8c47e0caee9a02f6afe78d15bea1b0f1822ea8449d801b2b10`
- Pages: **238**, US Letter, no rotation.
- Exact preface target: `source/id-ID/preface-id.tex`, 18,140 bytes,
  394 LF records, SHA-256
  `c622dc9d9c1af4e5b1a6112c84eeff7328c778e8ef8643fc267f6fc6e3e7d564`.
- Exact cumulative master:
  `source/id-ID/functional-analysis-id-complete-source.tex`, 11,176 bytes,
  353 LF records, SHA-256
  `7f06919a8ec9088a3bc812fab962a48b5f1b3b0d5d3bce80eb21055f65089041`.

Two clean fixed-path builds with `SOURCE_DATE_EPOCH=1444126743` produced
byte-identical PDFs. The pass-1 witness, fixed-path PDF, and canonical reader
have the exact byte count and hash above. All 19 inherited Chapter 17
chapter/dependency inputs matched the frozen Chapter 17 snapshot; the new
preface and complete-source master were separately identity-locked. All 21
inputs remained unchanged through both builds.

The final log has zero TeX errors, undefined references, undefined citations,
unresolved-reference summaries, rerun requests, multiply defined labels, or
missing-character warnings. It contains exactly six inherited overfull hboxes:
**2.90276 pt**, **7.30707 pt**, **11.09703 pt**, **21.73163 pt**,
**14.48387 pt**, and **3.32439 pt**. The preface adds none. Every implicated
surface was included in the all-page render inspection; no text, symbol,
matrix, diagram, or rule clips or overlaps the margin. Four underfull hboxes
and three underfull vboxes are harmless inherited URL/page-layout effects.
There are 150 inherited unavailable small-caps-italic requests and 28 inherited
PDF-string warnings for mathematical title tokens; visible text and outlines
remain readable.

The build result is `qa/COMPLETE_SOURCE_FINAL_BUILD_RESULT.json`, 1,913 bytes,
SHA-256
`db8f799e2a42d6921db50580d6bcb668a8d374f7192a7ce47b542435b3dbf1e3`.
The locked build driver is `qa/run_complete_source_final_build.ps1`, 9,404
bytes, SHA-256
`427f80a7b7a941308bf5cc98a88c7e47164afd4d0b1375ccc2dc68d29e568930`.

## Every-page render review

All 238 pages were freshly rendered at 110 dpi to 935x1210 PNGs. Twenty
ordered contact sheets, each covering at most 12 pages, were inspected from
physical page 1 through physical page 238. The new front matter was also
inspected at full render resolution: title, licensing/attribution, contents,
both preface prose pages, the complete 24-row Greek table, the complete 26-row
Fraktur table, number-set notation, function notation, and both diagrams.

- No clipped text, formula, matrix, commutative diagram, header, footer,
  bibliography entry, index column, link marker, or page number was observed.
- No overlapping text, black rectangle, missing glyph, damaged equation, or
  unreadable page was observed.
- The preface tables are full-width, centered, readable, and remain inside the
  page body; the final function page holds both diagrams and its closing text
  without orphaning or clipping.
- No page has ink in the outer five-pixel border. Minimum detected nonblank
  margins are 109 px left, 72 px top, 78 px right, and 60 px bottom.
- Blank physical pages 6, 28, 56, 86, 108, 122, 144, 154, 168, 172, 186, and
  198 are intentional front-matter or chapter-transition verso pages.

The render manifest covers all 238 PNGs:
`provenance/COMPLETE_SOURCE_RENDER_MANIFEST.csv`, 27,263 bytes, SHA-256
`2379f5eb5b3b5944be1f70500ea60bb236ec4e0e05f08f679952207d146399e3`.
The machine render audit is `qa/COMPLETE_SOURCE_RENDER_AUDIT.json`, 4,971
bytes, SHA-256
`92bb17327f1cbf4de707585f1356e29e5d7c086c309a931a08492f94685e3c85`.
The evidence generator is `qa/make_complete_source_render_evidence.py`, 6,537
bytes, SHA-256
`efcde5444441bca0593ddc2fd88cdd1607e783be156edb9a74cdcd06f452797b`.

## Navigation, fonts, and interactive-surface audit

The PDF metadata retains John M Erdman as author and records
`OpenAI Codex gpt-5.6-sol, Ultra` as creator. The catalog language is `id-ID`.

- 109 outline entries.
- 3,043 link annotations: 3,033 internal GoTo actions and 10 URI actions.
- 2,331 named destinations and **zero unresolved internal links**.
- 49 referenced font objects; every one is embedded, subset, and Unicode-mapped.
- Extractable and searchable text: 896,493 bytes, 238 page delimiters, zero
  replacement characters, zero recognized mojibake signatures, and zero local
  path leaks.
- No encryption, AcroForm, embedded-file name tree, file attachment,
  JavaScript, Launch action, RichMedia, movie, sound, or screen annotation.

The text/font result is `qa/COMPLETE_SOURCE_TEXT_FONT_AUDIT.json`, 1,387 bytes,
SHA-256
`dee4ef50646d5841845a61f0e0f18b23b37946bf848ca847aca73448f4d6520d`.
The navigation/security result is
`qa/COMPLETE_SOURCE_PDF_SECURITY_NAVIGATION_AUDIT.json`, 1,786 bytes,
SHA-256
`1a3a692d6302351d545f4238e60e5463c8f7856256e69006dfe320075d42e0b5`.

The PDF has no structure tree or marked-content catalog flag and is therefore
correctly reported as **untagged**, not falsely described as fully accessible.
It supplies working navigation and Unicode text extraction; the goal's semantic
accessible HTML remains a separate full-corpus production surface.
