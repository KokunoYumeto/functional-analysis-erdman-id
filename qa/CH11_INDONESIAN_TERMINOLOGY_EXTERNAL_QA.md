# O008 Chapter 11 — bounded Indonesian terminology QA

Date: 2026-08-23  
Unit: `FAOA-2015-CH11` / `source/id-ID/Gelfand_Naimark-id.tex`  
Purpose: one bounded external field-usage check before the Chapter 11 build.  
This report is evidence only. It does not edit the translation, backend,
controls, release metadata, or upstream material.

## Result

**Proceed.** No preferred Indonesian term in the Chapter 11 draft needs to be
changed on the bounded evidence below. The external witness confirms the
edition's established core forms (`ruang Banach`, `ruang dual`, `norma
operator`, `operator kompak`, `spektrum`, and the `lemah`/`konvergen` family)
and supplies useful recognition variants. It does not directly cover the
specialized Gelfand--Naimark vocabulary, so those terms are retained by
mathematical meaning and internal consistency rather than falsely presented as
externally attested.

The explicit provenance string to add at the next authorized edition/release
metadata boundary is **`OpenAI Codex gpt-5.6-sol, Ultra`**. Preserve Erdman's
authorship, all source/component credits, and human direction/maintenance
credits. This report does not make that metadata edit.

## ArXiv-first gate (official source only)

The bounded search was limited to three exact-phrase searches on the official
arXiv search service, retrieved 2026-08-23:

1. [`"analisis fungsional"`](https://arxiv.org/search/?query=%22analisis+fungsional%22&searchtype=all&abstracts=show&order=-announced_date_first&size=50) — the page reports **no results**.
2. [`"ruang Hilbert"`](https://arxiv.org/search/?query=%22ruang+Hilbert%22&searchtype=all&abstracts=show&order=-announced_date_first&size=50) — the page reports **no results**.
3. [`"operator kompak"`](https://arxiv.org/search/?query=%22operator+kompak%22&searchtype=all&abstracts=show&order=-announced_date_first&size=50) — the page reports **no results**.

A separate `"ruang Banach"` request was rate-limited (HTTP 429) and is not
counted as a result. These are bounded negative findings, not a claim that no
Indonesian arXiv paper can ever exist. No suitable Indonesian-language arXiv
record was located; consequently there was no arXiv identifier, source
package, or TeX archive to download and unpack. I do not invent a TeX witness.

## Authorized institutional fallback

The fallback is the official Universitas Diponegoro JFMA article:

* Solikhin, YD Sumanto, Abdul Aziz, Susilo Hariyanto, and R. Heri Soelistyo
  Utomo, “Ruang Bernorma Lengkap atas Operator Linear Terbatas pada Ruang
  Fungsi Terintegral Dunford,” *Journal of Fundamental Mathematics and
  Applications* 3(1), 47–55 (2020), DOI
  [`10.14710/jfma.v3i1.7874`](https://doi.org/10.14710/jfma.v3i1.7874).
* Official article record:
  <https://ejournal2.undip.ac.id/index.php/jfma/article/view/7874>
* Official PDF download:
  <https://ejournal2.undip.ac.id/index.php/jfma/article/download/7874/4246>
* The publisher page identifies the journal as CC BY 4.0. The page metadata
  says `Language: EN`, while the title, abstract, body, and terminology are
  Indonesian; this is therefore a useful Indonesian field-usage witness, not
  a claim that the journal metadata classifies it as Indonesian.

The live PDF was fetched in memory on 2026-08-23 and matched the already
preserved local witness exactly:

* 9 A4 pages; 1,007,587 bytes;
  SHA-256 `6bc61be69f974e1598ec168504aa7b1925cf55a75dfc15100139bfcd586b0ff8`.
* Local witness:
  `qa/terminology_evidence/undip-jfma-2020-dunford/jfma-v3n1-7874.pdf`.
* Layout-preserving text extraction inspected:
  `qa/terminology_evidence/undip-jfma-2020-dunford/jfma-v3n1-7874.txt`,
  24,923 bytes, SHA-256
  `2a74c776f17891e80d2b5da88e2d00233a8990c969bac0e36451a703dd9f8c91`.
* The full nine-page rendered contact sheet was also inspected:
  `qa/terminology_evidence/undip-jfma-2020-dunford/jfma-v3n1-7874-contact-sheet.png`,
  2,622,328 bytes, SHA-256
  `94545c3ad7770d39b69132c4c0fae37a6487e4aa0b1c77ef58073fe061ed20a9`.

The article is narrower than Chapter 11: it treats bounded linear operators,
Banach spaces, weak measurability, weak compactness, and operator norms, but
not characters, maximal-ideal spaces, the Gelfand transform, or functional
calculus. Specialized Chapter 11 decisions must therefore not be overstated
as directly observed in this fallback.

As a second, compact institutional cross-check, the official ITB MA6131
curriculum lists the paired forms **Analisis Fungsional**, **Ruang Banach**,
**Ruang Dual**, **Operator Linear**, **Operator Kompak**, **Operator-operator
Fredholm**, and **Teori Spektral** (with English mappings):
<https://six.itb.ac.id/pub/kur2024/matakuliah/50833>.
The frozen local HTML witness is
`qa/terminology_evidence/undip-jfma-2020-dunford/itb-ma6131-2024.html`,
6,739 bytes, SHA-256
`5f9de3cc9dbcf3429ce45464aa08831d958466f5b5db6249fa3fe0f3eda94fb3`.
This cross-check is used only for terminology, not as a source corpus.

## Direct term comparison

Counts are case-insensitive occurrences in the layout-preserving extraction;
they are reproducibility aids, not a corpus-frequency claim.

| External Indonesian form (count) | Current project/Chapter 11 form | Decision |
|---|---|---|
| `ruang bernorma` (18) | `ruang linear bernorma` for *normed linear space* | Retain the source-sensitive current form. Record `ruang bernorma` as a recognition variant; the shorter form is clearly used in the fallback. |
| `ruang Banach` (4) | `ruang Banach` | Exact agreement; retain. |
| `ruang dual` (3) | `ruang dual` | Exact agreement; retain. |
| `norma operator` (9) | `norma operator` | Exact agreement; retain. |
| `operator linear terbatas` (3) | `pemetaan linear terbatas` when the source says *bounded linear map* | Keep the source-sensitive map/operator distinction. Use `operator linear terbatas` only as a scoped recognition variant, not a global replacement. |
| `operator adjoint` (6) | preferred `adjoin`; the reader uses `swaadjoin` for *self-adjoint* | The imported spelling is a real field-recognition form. It does not justify changing the established `adjoin`/`swaadjoin` choices; `swadjoin` and `adjoin-diri` remain recognition variants. |
| `operator kompak` (1) | `operator kompak` | Agreement with the whole-edition glossary; retain. |
| `konvergen lemah` (5) | preferred `konvergen secara lemah` | Both are intelligible field forms. Retain the explicit current wording for edition-wide consistency; recognize the shorter form. |
| `terukur lemah` (3) | no instantiated Chapter 11 term | Keep only as a future/domain recognition candidate beside `terukur secara lemah`; do not add it to current prose without a source that introduces *weakly measurable*. |

The following Chapter 11 forms occur in the draft and were checked for
semantic and morphological consistency but are **not** directly attested by
this narrower witness: `karakter`, `ruang karakter`, `ruang ideal maksimal`,
`transformasi Gelfand`, `kuasinilpoten`, `semisederhana`, `kalkulus
fungsional`, `pemisah`, `aljabar-$C^*$`, `beridentitas`, `uniter`, `proyeksi`,
and `swaadjoin`. They are retained: replacing them based on this article would
be an unsupported extrapolation and could collapse distinct algebraic
concepts. A later cross-chapter check corrected the Chapter 11 spelling to the
already established reader form `swaadjoin`; see
`provenance/SELF_ADJOINT_TERMINOLOGY_ADJUDICATION.md`. The draft snapshot inspected was
`source/id-ID/Gelfand_Naimark-id.tex` (32,521 bytes, SHA-256
`3804b274a75e1aa9485d8a9fa50a44cfc805224344c659423aef95da21e1162d`); this is
an observation hash, not a claim that the in-progress target is final.

## Handoff and limits

* No translated sentence or backend record was changed by this QA pass.
* No author or upstream maintainer was contacted.
* The fallback PDF was inspected directly; it is not a substitute for an
  Indonesian TeX source, and no TeX terminology was inferred from nonexistent
  source files.
* Additive recognition variants may be recorded at the next normal backend
  reconciliation. They are not instructions for indiscriminate prose
  replacement.
* Resume the existing Chapter 11 production/build cursor after this report.
