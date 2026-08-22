# FAOA-2015-CH07 build and QA receipt

Date: 2026-08-22  
Decision: **admitted**  
Course role: `D20_core`

This receipt admits the complete Indonesian Chapter 7, *Operator Kompak*, and
the cumulative Chapter 1--7 reader. Translation, mathematics, structure,
references, build, visual layout, navigation, component rights, privacy, and
append-only backend gates pass. It does not claim that Chapters 8--17, the
semantic HTML reader, the O001 solved mastery layer, or the original
compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Source: `source/upstream/compact_operators.tex`, 21,755 bytes / 517
  CRLF-terminated lines / SHA-256
  `a1f55b061f526f3e536e5a812f073781777b6f990b662f4a1dba07475152d663`.
- Target: `source/id-ID/compact_operators-id.tex`, 22,735 bytes / 517 LF lines /
  SHA-256
  `8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch07.tex`, 9,691 bytes / 333
  LF lines / SHA-256
  `c639253fab59df7b51002058b414d8d64c92d77f12e95e88068decafd0d138b9`.
- Derivative bibliography: `source/id-ID/functional_analysis_op_algs_bib.bib`,
  17,409 bytes / SHA-256
  `72b33be29e0728654e4b623e454639927046f425fb81e5b13b8c05e1888fd6fa`.
- The admitted Chapter 1--6 targets and every locked backend byte prefix remain
  unchanged.

## Structural, mathematical, reference, and language replay

The locked checker preserves four ordered sections and all 72 balanced
environment pairs: 28 propositions, 17 examples, 11 definitions, nine proofs,
two theorems, two corollaries, two enumerations, and one exercise. It preserves
20 labels, 13 reference endpoints, eight citation calls, 91 index hooks, and 26
defined-term hooks. Seven proofs remain explicit hints and two remain
citation-only proof surfaces. Four references are local, six resolve to
admitted prior chapters, and three genuine later-source endpoints are rendered
honestly as `\futurexref{12.3.16}{00152171}`,
`\futurexref{12.3.17}{00152181}`, and
`\futurexref{11.5.7}{X_sqroot_op}`. The earlier Chapter 5 reference to Chapter
7 now resolves normally.

The source and target each contain 309 mathematical surfaces in the same
delimiter topology. All eight sequence-diff blocks are classified as a source
correction or natural Indonesian reordering; there is no unexplained formula
deletion, insertion, or reorder. The final checker is
`qa/check_ch07_translation.py`, 21,468 bytes / SHA-256
`392d2842c99fd1a54faaf671b2256ef41a896335edd2c2fe5d973f13d63e1363`.
Its durable classified inventory is
`qa/CH07_CLASSIFIED_DELTA_INVENTORY.md`, 4,327 bytes / SHA-256
`347fd91f87647be3bf0da78379ce3851f1d36535b622be43e642f675defaf4b4`.
Repeated runs return `pass`, with zero visible English, mojibake, private path,
or unclassified structural/math residue.

An independent bilingual rereview read every source and target line, every
environment, all 309 mathematical spans, all labels/references/citations,
every index and defined-term hook, and the complete exercise/hint surface. It
found only two low-severity consistency defects: isolated single-hyphen
`Hilbert-Schmidt` surfaces and one `ruang ukuran` rendering. Both were
normalized to controlled `Hilbert--Schmidt` and `ruang ukur` before the final
target was frozen; no remaining semantic or prose defect was found. The
durable rereview is `qa/CH07_INDEPENDENT_BILINGUAL_REVIEW.md`, 1,937 bytes /
SHA-256
`040622d37ec422c0e7d4e3f84d0cabb77d16d89b3145b82b61327e87f6cbe18f`.

Eleven bounded source corrections are applied and individually recorded. The
append-only cumulative ledger is `provenance/SOURCE_CORRECTIONS.md`, 23,661
bytes / SHA-256
`285f20b012926002bb9085dab91b06cee3e0808bf7881b598a276c643ad8eea7`.
Its admitted Chapter 1--6 prefix remains byte-identical at 20,716 bytes /
SHA-256
`7de8a5892b865af84c9f5d1d4c37ec6b3112b3e099685dae243108006dc94b01`;
the 2,945-byte Chapter 7 suffix has SHA-256
`9f262ed1003bf8824a0485c68caf117170458fb27651491a86d7b911797a4c6d`.
No upstream contact occurs during production.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex,
  and Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two independently cleaned builds in the same fixed output directory produced
  byte-identical PDFs: 1,530,677 bytes / 121 US-Letter pages / SHA-256
  `a7ddaef324bd356d258cb47195f524e027ba54a696cb8d38a8358bb8d0a2d7ff`.
- Latest final TeX log: 47,575 bytes / SHA-256
  `35cf19763a0e6b8336ad962f49940791d17dad89d4b55451e10dd65e8f923af5`.
- Final log: zero TeX errors, unresolved references or citations,
  rerun-required warnings, multiply defined labels, overfull boxes, underfull
  vboxes, or missing characters. Four inherited front-matter underfull hboxes
  arise from long authority URLs and hashes; 84 legacy small-caps-italic font
  substitutions do not alter content.
- BibTeX uses 30 entries and reports zero warnings. MakeIndex accepts all 1,259
  entries, rejects zero, writes 1,546 lines, and reports zero warnings.

The canonical reader is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-7.pdf`; its
build-tree copy is byte-identical. The catalog language is `id-ID`; the PDF has
47 outline entries, 1,132 named destinations, 1,620 resolved internal links,
and eight URI annotations over six unique external targets. It has no
encryption, form, widget, JavaScript, launch action, embedded attachment, rich
media, or executable action. Its sole open action is an internal `GoTo` view.

## Visual and accessibility evidence

All 121 physical pages were freshly rendered at 150 dpi. The exact render set
contains 121 PNGs / 42,779,126 aggregate bytes, each 1,275 by 1,650 pixels.
The public render manifest is 23,608 bytes / SHA-256
`b2fa453d7b96b51826aadddf2e8151144d6deae1d093dfa34841ab589ef464ed`;
replay finds no missing, extra, duplicate, dimension-mismatched, or
hash-mismatched page. The all-page public contact sheet is 3,549,427 bytes /
SHA-256
`b52f348c29cdaa1cebd87c280ac0c01fad919e72a8f595ba2c48cb78ac283564`.

Every page was inspected through eleven detailed consecutive contact sheets
and the public all-page sheet. Full-size pages 96--107 received a second
inspection, covering the Chapter 7 opener, the long citation proof, trace-class
material, the Hilbert--Schmidt section, and the bibliography transition. No
clipping, overlap, off-center body block, damaged glyph, unreadable formula,
broken header, or margin violation was found. The citation proof reflows cleanly
after three invisible `\allowbreak` opportunities removed its measured
2.28432-point overfull line.

Bounding-box replay finds 57,431 words and zero boxes outside page bounds, with
minimum clearances of 72.000 points left, 71.254988 right, 49.278601 top, and
37.803801 bottom. The five zero-word pages are the intentional blank versos 20,
48, 78, 100, and 108. The formal report is
`qa/CH07_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 6,182 bytes / SHA-256
`c71c7b9bce1133d7c10bab8cf2e3bb4c310a8ceb701672ced87bbd6a412012f5`.

All 43 font resources are embedded subsets with Unicode maps. Extracted text
is 463,585 bytes / SHA-256
`aad0d057d0a8bd51bc9e39ea90da922b635c590b0c3746d8c82b7181fda6d6c1`
and contains no replacement character, mojibake signature, or local path. The
PDF remains honestly untagged: it lacks a structure tree, semantic
heading/list/equation/index roles, alternative-text framework, and guaranteed
screen-reader order. It is a visually usable, searchable, navigable reader,
not a fully accessible edition. Semantic HTML and/or a later tagged-PDF
derivative remains an edition-level deliverable and is nonblocking only for
this chapter boundary.

## Rights, component, and privacy closure

The wrapper supplies Erdman attribution, a CC BY-SA 4.0 link, translation and
technical-change notices, ShareAlike terms, and non-endorsement. `DIAGXY.TEX`
remains byte-identical to the frozen source copy at 41,908 bytes / SHA-256
`3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb`
under Michael Barr's embedded notice. `TABLE.TEX`, badge artwork, and uncleared
quotation components remain absent. Separately authored solutions, mastery
support, and the compact-spectral/SVD bridge are not represented as
Erdman-authored content.

A bounded scan of the prospective public Chapter 7 text, QA, provenance,
reader, and backend surfaces finds no credential, live local filesystem path,
unrelated-lane reference, or private control artifact. The checker's credential
terms are negative-test patterns only; `.gitignore` names private directories
solely to exclude them from publication.

## Backend admission and deterministic replay

The Chapter 7 projection appends stable locale-neutral unit, semantic, segment,
formula, relation, exercise-support, index, terminology, correction, artifact,
and typed-QA records while preserving every admitted Chapter 1--6 byte prefix
and ID. The chapter contributes 74 semantic units, 85 segments, 349 relations,
309 formula maps, 91 index rows, one exercise-support record with seven hint
links, 11 correction records, 17 new global terminology records representing
26 term occurrences, nine exact public artifact bindings, and eight typed QA
events.

The canonical validator runs the complete generator twice with byte-identical
outputs, validates exact JSON/CSV round trips, globally unique IDs, relation
endpoints, public artifact bytes, private-control exclusion, receipt binding,
and append-only closure of the prior Chapter 5 pending reference. The resulting
global counts and backend manifest hash are recorded in durable state and the
root handoff rather than circularly embedded in this receipt.

Chapter 7 is admitted. The whole edition remains `in_progress`, and the active
source-order cursor advances to `FAOA-2015-CH08`,
`source/upstream/spectrum.tex`.
