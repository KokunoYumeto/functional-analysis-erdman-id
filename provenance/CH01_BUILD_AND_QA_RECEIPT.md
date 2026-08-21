# Chapter 1 Build and QA Receipt

Receipt ID: `QA-CH01-ADMISSION-20260821`  
Date: 2026-08-21  
Unit: `FAOA-2015-CH01`  
Verdict: **admitted**

This receipt admits only the first translated unit, *Aljabar Linear dan Teorema
Spektral*. The complete 17-chapter Indonesian edition remains in progress.

## Exact inputs and output

| Surface | Bytes | SHA-256 |
|---|---:|---|
| `source/upstream/linalg.tex` | 58,673 | `a15cabf306adf5457cedce046f98b9474c72b38ab50197b0dc4288e942772096` |
| `source/id-ID/linalg-id.tex` | 60,798 | `4ab3098cab358f425190bfe6defa20d3ec7b2a81653e0e61bbfa67e497e2654d` |
| `source/id-ID/functional-analysis-id-unit1.tex` | 9,369 | `3d90738a7ba526d578330e56b04db5fc96a72ca29c270c930a030b9a90a39346` |
| `source/id-ID/DIAGXY.TEX` | 41,908 | `3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb` |
| `source/id-ID/functional_analysis_op_algs_bib.bib` | 17,438 | `54a08f8dfdbc43533a1b76a19caa47415d8376f39ce3971d8778087911cb4f82` |
| `output/pdf/analisis-fungsional-dan-aljabar-operator-id-unit-1.pdf` | 654,052 | `0a15bf4fb9567c994b031079d9878e540b83e8d04ee368f733cbefae33292ac6` |

The source chapter contains 1,261 lines; the admitted target contains 1,254.
The build database binds the final target at exactly 60,798 bytes. The target
PDF and retained clean-build witness are byte-identical.

## Reproducible build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex,
  and Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two independently cleaned fixed-path builds each produced 654,052 bytes and
  SHA-256 `0a15bf4fb9567c994b031079d9878e540b83e8d04ee368f733cbefae33292ac6`.
- Both final logs are 28,652 bytes and have SHA-256
  `5de7f0ffa1bf13a5ac51e2de6e942dbb1d6c4258c10d829ea5033d0eb50ed5a0`.
- Final log: zero TeX errors, zero unresolved references or citations, zero
  multiply defined labels, and zero overfull boxes.
- Retained warnings: two benign front-matter underfull boxes and nine uses of
  the legacy small-caps-italic fallback (`scit` to `scsl`). They do not clip or
  obscure reader content.

## Structural and mathematical replay

Source and target have the same ordered topology:

- 155 matched environment pairs;
- 49 labels, in identical order;
- 6 citations, in identical order;
- 187 index entries;
- 59 list items;
- 36 definitions, 40 propositions, 7 theorems, 3 corollaries, 3 notation
  blocks, 2 convention blocks, 1 lemma, 14 examples, 6 exercises, and 12 proof
  environments;
- 20 source cross-references represented as 18 resolving local `ref` surfaces
  plus 2 typed `futurexref` surfaces for later chapters; all local references
  resolve.

The deterministic formula extractor finds 932 source and 932 target math
surfaces. Sequence alignment proves 906 surfaces identical after whitespace
normalization; the remaining 26 source and 26 target surfaces are captured in
typed alignment groups and were individually covered by translation,
source-correction, or display-reflow review. Fifteen admitted changes are
listed in `SOURCE_CORRECTIONS.md`; no unexplained mathematical delta remains.

## Language, rights, privacy, and accessibility

- Active reader text has no unresolved English prose, mojibake, replacement
  characters, placeholder tokens, or unresolved-reference markers. Proper
  titles and bibliographic data remain in their cited source languages.
- Generated labels for the email address and index cross-references are
  localized as `Alamat surel`, `lihat`, and `lihat juga`.
- The wrapper supplies attribution, the CC BY-SA 4.0 license link, a change
  notice, ShareAlike terms, and explicit non-endorsement.
- `DIAGXY.TEX` is byte-identical to the upstream component and retains Michael
  Barr's embedded notice. `TABLE.TEX`, badge artwork, and uncleared quotation
  components are absent from the build closure.
- Text and binary publication-candidate scans found no local filesystem path,
  account name, credential, task identifier, or private coordination data.
- The 25-page US-Letter PDF has correct title/author metadata, `/Lang=id-ID`,
  bookmarks, links, and no encryption, JavaScript, or forms. It is not tagged;
  semantic accessible HTML remains a required later edition surface and is not
  overclaimed here.

## Visual and backend evidence

All 25 freshly rendered pages were inspected at 144 dpi. There is no clipping,
overlap, broken formula, missing diagram, or damaged glyph. Physical pages 4,
20, and 22 are intentional blank versos.

- Render manifest: 26 rows, 2,209 bytes, SHA-256
  `933316364ca7807d22766e6ffeda0bcdf43d1d04af26820ff80d9d01c698f754`;
  zero missing, extra, size-mismatched, or hash-mismatched files.
- Contact sheet: 4,301,230 bytes, SHA-256
  `976c691a7d21dfc2875201b82f94a8bd2a491225e7510856003fa4b4a1b69cf3`.
- Backend manifest: 19 rows, 1,693 bytes, SHA-256
  `d2feb13d6680f23d75d617194fef7cb56027c31075a4230c335f41bde4828fc6`.
- Backend validator: 1,799 globally unique records, 984 checked relation
  endpoints, 127 semantic subunits, 154 mapped reader segments, 187 mapped
  index terms, 932-to-932 formula coverage, and 6 explicit exercise-support
  records. Generator replay is byte-deterministic and all JSON/JSONL/CSV
  exports round-trip.

Chapter 1 therefore satisfies the bounded admission gate. Publication of this
unit does not imply completion of Chapters 2--17, the O001 solution layer, the
compact-spectral/SVD bridge, or the final semantic HTML reader.
