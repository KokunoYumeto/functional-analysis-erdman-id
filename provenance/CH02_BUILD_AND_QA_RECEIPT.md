# FAOA-2015-CH02 build and QA receipt

Date: 2026-08-21  
Decision: **admitted**  
Course role: `D20_core`

This receipt admits the complete Indonesian Chapter 2, *Selingan Sangat
Singkat tentang Bahasa Kategori*, and the cumulative Chapter 1--2 reader. It
does not claim that later chapters, the semantic HTML reader, the O001 solved
mastery layer, or the original compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Source: `source/upstream/categories.tex`, 27,446 bytes / 574 lines / SHA-256
  `6f5115e4058902e99ab7157ad59ea95f0e0013e2f4272c05ff421933f7255775`.
- Admitted target: `source/id-ID/categories-id.tex`, 29,254 bytes / 570 lines /
  SHA-256
  `39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd`.
- Cumulative master: `source/id-ID/functional-analysis-id-through-ch02.tex`,
  9,437 bytes / SHA-256
  `1ca424e166df692e8bf69421a0a1720d5dfb2540c52053bb036be99ecdde9ecd`.
- The frozen Chapter 1 target and Unit 1 master were not modified.

## Structural and mathematical replay

The source and target retain the same ordered topology:

- 39 balanced environment pairs in identical order: 12 definitions, 17
  examples, 1 proposition, 1 caution, 1 notation block, 6 enumerations, and 1
  labelled equation;
- 35 semantic anchors, yielding 34 reader semantic units and 41 mapped
  segments;
- 12 labels in identical order, 4 citations in identical order, 137 index
  hooks, 63 defined-term hooks, and 18 list items;
- the local reference `C015127` resolves inside Chapter 2; the later Open
  Mapping Theorem label `C069414` is preserved as the typed future reference
  `\futurexref{6.3.4}{C069414}`;
- no explicit exercise, proof, or hint environment occurs in the chapter; the
  two inline learner exercises and the proposition intentionally left without
  proof are retained.

The deterministic math extractor finds 396 source and 397 target surfaces.
Sequence alignment gives 395 exact normalized matches. The only non-equal
groups are both logged source corrections:

1. `f(\vc 1_A)=1_B` becomes `f(\vc 1_A)=\vc 1_B`;
2. the missing diagonal-functor arrow action `\ftr D(f):=(f,f)` is supplied.

No unexplained mathematical delta remains.

## Translation and source-correction review

The complete source and target were read independently. Final review at the
admitted target hash found P1=0, P2=0, and P3=0. Active reader text contains no
unintended English prose, mojibake, replacement character, placeholder, local
path, task identifier, or credential surface. Terminology is reconciled with
Chapter 1, including `grup Abelian`, `pemetaan linear`, `ruang dual aljabar`,
and `adjoin`.

The edition transparently corrects the source's swapped small/locally-small
index hooks; false claim that the one-object monoid category is non-concrete;
unqualified element notation for an arbitrary product category; omitted arrow
action of the diagonal functor; inconsistent identity notation; and minor
source-language slips. Exact decisions and source loci are in
`provenance/SOURCE_CORRECTIONS.md`, 3,408 bytes / SHA-256
`26708cf62c00202ad224a5d5413069e7bd376497a96e3c7c30487b66214d5c16`.
Erdman's intentional Bourbaki convention for monomorphisms and epimorphisms is
preserved rather than silently normalized.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex,
  and Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two independently cleaned runs at the same fixed output path produced
  byte-identical PDFs: 795,305 bytes / 32 US-Letter pages / SHA-256
  `7a04eb72ef5445ee06e429e7552b8e14a02a993c916b4632cdb9219a928a3bdb`.
- Pass-one log: 29,743 bytes / SHA-256
  `ad20fecd7510b7cd0b28fede4d32434ee02e9e1c990fe6e3d6c85118c4007867`.
- Pass-two log: 29,743 bytes / SHA-256
  `820757ce340c6831d2a3720a33b7ec03007e65ed7c631ebc8676db5adbb400f2`.
  The logs differ only in the wall-clock minute printed in their first line;
  replacing that field gives the identical normalized SHA-256
  `661f7b702b4420f3d4c92b5999b408a85a1acc3b54c53e6141c0c79cee28e235`.
- Final log: zero TeX errors, unresolved references/citations, rerun-required
  warnings, multiply defined labels, or overfull boxes. It retains two benign
  front-matter underfull boxes and nine legacy small-caps-italic substitutions;
  neither affects reader content.

The canonical reader PDF is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-2.pdf` with the
same exact byte identity above. It has title/author metadata, `/Lang=id-ID`,
eight outline entries (four top-level entries and four section children),
links, and no encryption, JavaScript, forms, or AcroForm. It is honestly
untagged; the required accessible semantic HTML reader remains future edition
work.

## Visual, rights, privacy, and backend evidence

All 32 pages were freshly rendered at 144 dpi and inspected. No clipping,
overlap, broken formula, missing glyph, damaged link text, or index collision
was found. Physical pages 4, 20, and 28 are intentional blank versos. The 32
page PNGs total 9,468,166 bytes. Their 32-row replay manifest is 2,938 bytes /
SHA-256
`ac7f79b32125a554322faa242c656704f5643e78598c5973c68072ec28d8d670`,
with zero missing, extra, size-mismatched, or hash-mismatched pages. Four
contact sheets cover pages 1--8, 9--16, 17--24, and 25--32; changed front
matter, all Chapter 2 pages, bibliography, and index were additionally
inspected at full rendered size.

The wrapper supplies attribution, a CC BY-SA 4.0 link, change notice,
ShareAlike terms, and non-endorsement. `DIAGXY.TEX` remains byte-identical at
41,908 bytes / SHA-256
`3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb`.
`TABLE.TEX`, badge artwork, and uncleared quotation components are absent from
the build closure. Text, PDF-text, and metadata privacy scans pass.

Before admission binding, the canonical backend regenerated deterministically
and validated twice: 161 semantic units, 195 segments, 591 relations, 1,328
formula-map records, 324 index rows, and 6 Chapter 1 exercise-support records;
2,716 globally unique IDs; 1,226 checked relation endpoints; exact JSON/CSV
round trips; and unchanged Chapter 1 byte prefixes. The 21-row pre-admission
backend manifest was 1,879 bytes / SHA-256
`97d99d0d4f1c9250389e270707b5416c82e809f5d8138f55b9b4d87174d5c36b`.
The final backend reconciliation binds this receipt, target, cumulative PDF,
source corrections, QA events, and admission state; its final manifest hash is
recorded in the durable state and publication handoff to avoid a circular
self-hash inside this receipt.

Chapter 2 is admitted. The active source-order cursor advances to
`FAOA-2015-CH03`, `source/upstream/normlinspaces.tex`.
