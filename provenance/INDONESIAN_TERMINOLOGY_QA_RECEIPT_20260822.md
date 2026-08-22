# Indonesian terminology QA receipt — 2026-08-22

Unit boundary: O008 / `ERDMAN-FAOA-2015-ID`, after admission of Chapters 1--9
and before contiguous Chapter 10 production.

## Decision

The one-time Indonesian field-usage comparison passed. A bounded official
arXiv search found no suitable Indonesian functional-analysis source with an
available TeX source package. This is a bounded result, not a universal claim.
The authorized fallback was the nine-page Universitas Diponegoro JFMA article
by Solikhin et al., DOI `10.14710/jfma.v3i1.7874`, supplemented by exact
official UGM and ITB records for vocabulary not resolved by that article.

All nine PDF pages were inspected from the rendered contact sheet and the
layout-preserving text extraction. No admitted Indonesian mathematical
sentence requires alteration. The frozen Chapter 1--9 reader PDF and TeX
therefore remain byte-identical and do not require a rebuild or a new
Zenodo/Figshare reader version at this metadata-only boundary.

Accepted recognition variants are:

- `ruang bernorma` beside preferred `ruang linear bernorma`;
- scoped `operator linear terbatas` beside preferred `pemetaan linear
  terbatas` for the source term *bounded linear map*;
- `adjoint` and `operator pendamping` beside preferred `adjoin`;
- `kompak lemah` beside preferred `kompak secara lemah`;
- `konvergen lemah` beside preferred `konvergen secara lemah`.

`terukur lemah` is retained only as a non-instantiated future/domain
recognition candidate beside hypothetical preferred `terukur secara lemah`.
The frozen Chapter 10 source contains zero occurrences of *weakly measurable*;
the candidate may be instantiated only if a later or separately authored
source actually introduces that concept.

## Frozen evidence

- QA report: 9,317 bytes, SHA-256
  `c7618249a3d9f273044a408e44438e2db710d5b5f46856ea5280bf247583858d`.
- UNDIP PDF: 1,007,587 bytes / nine pages, SHA-256
  `6bc61be69f974e1598ec168504aa7b1925cf55a75dfc15100139bfcd586b0ff8`.
- UNDIP extracted text: 24,923 bytes, SHA-256
  `2a74c776f17891e80d2b5da88e2d00233a8990c969bac0e36451a703dd9f8c91`.
- Nine-page contact sheet: 2,622,328 bytes, SHA-256
  `94545c3ad7770d39b69132c4c0fae37a6487e4aa0b1c77ef58073fe061ed20a9`.
- Frozen UNDIP article page: 49,084 bytes, SHA-256
  `bb8bfeb1e799b479288c1857406d480ecb00b82118a74728985a0d7a9aaf78b9`.
- Frozen UGM topological-vector-space record: 35,075 bytes, SHA-256
  `3499fe641f9127357395c1d1bcd8467f848804208803db31ec0eb9f720c0c9e2`.
- Frozen ITB MA6131 record: 6,739 bytes, SHA-256
  `5f9de3cc9dbcf3429ce45464aa08831d958466f5b5db6249fa3fe0f3eda94fb3`.
- Frozen ITB MA5022 `adjoin` record: 7,943 bytes, SHA-256
  `cce7931eba1388395a504d83275f2846b7c3ac9031066bc27258c7abbc62724e`.
- Frozen UGM `operator pendamping` record: 22,532 bytes, SHA-256
  `677165f202f8d7f32eb13f3ebe5b18052a20765ae32354209034d1ed8c3cf3f4`.

## Backend and replay

The existing `backend/terminology.jsonl` remains byte-identical at 98,578
bytes / 255 records / SHA-256
`98d69653ba962b1f88f84e9de28e13b9fa1c8f3fcbfbdc319e89b182f68a2144`.
The additive `backend/terminology_qa.jsonl` contains seven records, 9,232 bytes,
SHA-256
`0be61180b43ca8e314bc3323696a0836ed82f505153444373584d1ac640cc3c8`.
It records the evidence, five accepted current variant groups containing six
spellings, and one explicitly non-instantiated future/domain candidate.

The complete validator performed two deterministic generator replays and
passed all frozen Chapter 1--9 prefix locks, exact JSON/CSV round trips,
evidence locks, stable IDs, and relation endpoints: 16 JSONL files / 14,556
records, 1,423 index rows, 15,979 globally unique IDs, 9,428 checked relation
endpoints, and a 31-row backend manifest with SHA-256
`13b5cd1f5e5cfb59717bfd74e42048095bcfba95fcfb4981dfa2717c2da3621d`.

## Production handoff

The Chapter 10 inventory is now translation-ready:

- `qa/CH10_SOURCE_INVENTORY.md`: 10,199 bytes, SHA-256
  `751ad13db185fe10491828440fb863e8ed2c083513692d38bd87275f58268f83`;
- `provenance/CH10_SOURCE_INVENTORY.json`: 15,690 bytes, SHA-256
  `b8d73079421a3d132a2e375cf2605297a9f4a68123e9394ab86cba035e8ab76d`.

The active contiguous boundary is `FAOA-2015-CH10-F01`, source lines 1--94,
5,150 bytes, SHA-256
`6cb7e8c7a4382345eaf5cac803b841cd883c326160284ef395649517515ce519`.

The explicit model provenance is **OpenAI Codex gpt-5.6-sol, Ultra**. John M.
Erdman, all source/component authors, and the human direction and maintenance
credits remain preserved. No upstream contact occurred.
