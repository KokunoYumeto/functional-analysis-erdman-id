# O008 Indonesian Terminology QA — bounded external evidence

Date: 2026-08-22

Scope: one-time terminology check for the Indonesian functional-analysis
edition, especially `source/id-ID/topvecspaces-id.tex` and
`backend/terminology.jsonl`. This report does not edit either file.

## ArXiv gate and fallback decision

A bounded search was made for an Indonesian-language arXiv source in
functional analysis, topological vector spaces, operator theory, or
distribution theory. The exact-phrase searches were:

- `"analisis fungsional"`;
- `"ruang Banach"`;
- `"ruang vektor topologis"`;
- `"operator kompak"`;
- related searches for `Teorema Hahn-Banach`, `ruang Hilbert`, and `teori
  operator` restricted to arXiv.

The official arXiv search page for `all: "analisis fungsional"` returned “no
results”:

`https://arxiv.org/search/?query=%22analisis+fungsional%22&searchtype=all&abstracts=show&order=-announced_date_first&size=50`

The other exact-domain searches found no relevant Indonesian mathematical
paper. Some repeated direct arXiv/API requests were rate-limited with HTTP 429,
so this is deliberately a bounded negative finding, not a claim that no such
paper can ever exist. No suitable Indonesian arXiv paper with downloadable TeX
source was located; consequently the authorized institutional-PDF fallback was
used.

## Primary fallback witness

Solikhin, YD Sumanto, Abdul Aziz, Susilo Hariyanto, and R. Heri Soelistyo
Utomo, “Ruang Bernorma Lengkap atas Operator Linear Terbatas pada Ruang Fungsi
Terintegral Dunford,” *Journal of Fundamental Mathematics and Applications
(JFMA)* 3(1), 47–55 (2020), DOI `10.14710/jfma.v3i1.7874`.

- Official article page:
  `https://ejournal2.undip.ac.id/index.php/jfma/article/view/7874`
- Official PDF:
  `https://ejournal2.undip.ac.id/index.php/jfma/article/download/7874/4246`
- Publisher: Department of Mathematics, Universitas Diponegoro.
- Surface inspected: all 9 A4 pages (printed pages 47–55), both extracted text
  and a full-page visual contact sheet.
- The official article page identifies the journal as CC BY 4.0.

This is representative Indonesian functional-analysis usage: its subject is
bounded linear operators and completeness on Banach-valued/Dunford-integrable
function spaces. It is narrower than Erdman's Chapter 9 and therefore cannot
settle specialized terms such as *balanced*, *circled*, *filterbase*, or
*Minkowski functional*.

## Supplemental primary witnesses

Four bounded official institutional records were frozen because they directly
cover vocabulary absent from, or variable within, the fallback article:

1. Universitas Gadjah Mada dissertation metadata, “Representasi Linear Kontinu
   dari Grup Topologis ke dalam Ruang Vektor Topologis” (2015), record 89480:
   `https://etd.repository.ugm.ac.id/penelitian/detail/89480`. It independently
   uses **ruang vektor topologis**, **grup topologis**, and **representasi linear
   kontinu**.
2. Institut Teknologi Bandung official 2024 MA6131 curriculum:
   `https://six.itb.ac.id/pub/kur2024/matakuliah/50833`. It maps **Analisis
   Fungsional**, **Ruang Banach**, **Ruang Dual**, **Operator Linear**,
   **Operator Kompak**, **Operator-operator Fredholm**, and **Teori Spektral**
   to their English counterparts.
3. Institut Teknologi Bandung official 2024 MA5022 curriculum:
   `https://six.itb.ac.id/pub/kur2024/matakuliah/50585`. It explicitly maps
   **Operator Normal dan Adjoin dengan Diri Sendiri** to *Normal and
   Self-Adjoint Operator*, directly supporting preferred `adjoin` in this
   operator-theory sense.
4. Universitas Gadjah Mada thesis metadata, “Beberapa sifat operator normal
   pada ruang Hilbert” (2007), record 36096:
   `https://etd.repository.ugm.ac.id/penelitian/detail/36096`. Its Indonesian
   abstract explicitly calls the unique continuous linear operator $T^*$ the
   **operator pendamping**, supporting that phrase as a recognition variant.

## Frozen Chapter 10 presence check

A direct case-insensitive scan of frozen
`source/upstream/distributions.tex` for `weakly[ -]measurable|measur` found
zero occurrences of *weakly measurable* and 14 generic `measur`-stem
occurrences. The file is 42,703 bytes / 894 lines, SHA-256
`31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8`.
Therefore `terukur lemah` is not a Chapter 10 term awaiting instantiation. It
may be retained only as a non-instantiated future/domain recognition candidate,
and may be instantiated only if a later or separately authored source actually
introduces *weakly measurable*.

## Observed terminology

Counts below are exact case-insensitive counts in the `pdftotext -layout`
extraction and are only a reproducibility aid, not a corpus-frequency claim:

| PDF form | Count | Current project form | Decision |
|---|---:|---|---|
| `ruang bernorma` | 18 | `ruang linear bernorma` for source term *normed linear space* | Both are established. Retain the source-sensitive current wording; add `ruang bernorma` as a glossary variant. No prose propagation required. |
| `ruang Banach` | 4 | `ruang Banach` | Exact match; retain. |
| `ruang dual` | 3 | `ruang dual` | Exact match; retain. |
| `norma operator` | 9 | `norma operator` | Exact match; retain. |
| `operator linear terbatas` | 3 | `pemetaan linear terbatas` for *bounded linear map* | Preserve the map/operator distinction dictated by the English source. Add `operator linear terbatas` only as a scoped operator-theory variant, not as a global replacement. |
| `operator adjoint` | 6 | `adjoin` | Retain `adjoin`: the frozen ITB MA5022 page explicitly supports it. Record `adjoint` and the independently frozen UGM `operator pendamping` as recognition/search variants. |
| `kompak lemah` | 2 | `kompak secara lemah` | Both forms occur in Indonesian academic usage. Retain the grammatically explicit current preferred form; add the shorter form as a variant. |
| `konvergen lemah` | 5 | `konvergen secara lemah` | Both forms occur in primary Indonesian academic sources. Retain the current form for edition-wide consistency; add the shorter form as a variant. |
| `barisan Cauchy` | 13 | `barisan Cauchy` | Exact match; retain. |
| `terukur lemah` | 3 | no edition term record | Retain only as a non-instantiated future/domain recognition candidate beside hypothetical preferred `terukur secara lemah`. It is explicitly absent from frozen Chapter 10 and may be instantiated only if a later or original source introduces *weakly measurable*. |
| `ruang linear` | 8 | `ruang linear` when the source deliberately says *linear space* | Exact semantic match; retain the project's deliberate distinction from `ruang vektor`. |

The UGM record exactly supports the Chapter 9 preferred term `ruang vektor
topologis`. The ITB record independently supports the edition's core forms for
functional analysis, Banach/dual spaces, linear and compact operators, Fredholm
operators, and spectral theory.

## Recommendation

No translated mathematical sentence needs changing on this evidence. The
current preferred terms are mathematically sound, natural, and internally
consistent. The additive glossary/backend refinement is limited to recognition
variants:

- `ruang bernorma` for `ruang linear bernorma`;
- `operator linear terbatas` scoped to operators, beside `pemetaan linear
  terbatas` for maps;
- `adjoint` and `operator pendamping` beside preferred `adjoin`;
- `kompak lemah` beside `kompak secara lemah`;
- `konvergen lemah` beside `konvergen secara lemah`;
- non-instantiated future/domain candidate `terukur lemah` beside hypothetical
  preferred `terukur secara lemah`; this is not present in frozen Chapter 10
  and is gated on a later or original source actually introducing *weakly
  measurable*.

These are search/interoperability variants, not permission for indiscriminate
replacement. Specialized Chapter 9 terms remain unchanged because the bounded
external witness does not actually use them.

## Frozen evidence identities

| File | Bytes | SHA-256 |
|---|---:|---|
| `jfma-v3n1-7874.pdf` | 1,007,587 | `6bc61be69f974e1598ec168504aa7b1925cf55a75dfc15100139bfcd586b0ff8` |
| `jfma-v3n1-7874.txt` | 24,923 | `2a74c776f17891e80d2b5da88e2d00233a8990c969bac0e36451a703dd9f8c91` |
| `jfma-v3n1-7874-contact-sheet.png` | 2,622,328 | `94545c3ad7770d39b69132c4c0fae37a6487e4aa0b1c77ef58073fe061ed20a9` |
| `undip-jfma-7874-article.html` | 49,084 | `bb8bfeb1e799b479288c1857406d480ecb00b82118a74728985a0d7a9aaf78b9` |
| `ugm-etd-89480-metadata.html` | 35,075 | `3499fe641f9127357395c1d1bcd8467f848804208803db31ec0eb9f720c0c9e2` |
| `itb-ma6131-2024.html` | 6,739 | `5f9de3cc9dbcf3429ce45464aa08831d958466f5b5db6249fa3fe0f3eda94fb3` |
| `itb-ma5022-2024-adjoin.html` | 7,943 | `cce7931eba1388395a504d83275f2846b7c3ac9031066bc27258c7abbc62724e` |
| `ugm-etd-36096-operator-pendamping.html` | 22,532 | `677165f202f8d7f32eb13f3ebe5b18052a20765ae32354209034d1ed8c3cf3f4` |

Compared live project inputs:

| File | Bytes | SHA-256 |
|---|---:|---|
| `source/id-ID/topvecspaces-id.tex` | 37,705 | `791868776a07f4c854f1c13d295da23a2559b88dcac48523fb0390e1e5330ee1` |
| `source/upstream/distributions.tex` | 42,703 | `31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8` |
| `backend/terminology.jsonl` | 98,578 | `98d69653ba962b1f88f84e9de28e13b9fa1c8f3fcbfbdc319e89b182f68a2144` |
