# FAOA-2015-CH04 build and QA receipt

Date: 2026-08-22  
Decision: **admitted**  
Course role: `D20_core`

This receipt admits the complete Indonesian Chapter 4, *Ruang Hilbert*, and the
cumulative Chapter 1--4 reader. Reader, translation, build, visual, rights,
privacy, and append-only backend gates pass. It does not claim that Chapters
5--17, the semantic HTML reader, the O001 solved mastery layer, or the original
compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Source: `source/upstream/Hilbert_spaces.tex`, 60,217 bytes / 1,340
  CRLF-terminated lines / SHA-256
  `80fd8fd190beefde7787139be67ce29b9d9cce2d68ff66489aa1e4a93b54c740`.
- Target: `source/id-ID/Hilbert_spaces-id.tex`, 62,947 bytes / 1,351 LF lines /
  SHA-256
  `b8e728e1f26a66ec2a420373e6104e3db4e5c954d7001acda1c13eb348322215`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch04.tex`, 9,348 bytes /
  SHA-256
  `598bd1f91096a2e0e19314995f44f79f246ca06cad6328ce9e996af074ceff6c`.
- The admitted Chapter 1--3 targets are unchanged.

## Structural, mathematical, and language replay

The source and target retain the same ordered topology: 144 balanced
environment pairs, 131 semantic anchors, 10 exercises, 11 explicit proof-hint
blocks, 44 labels, 12 citations, 177 index hooks, 59 defined-term hooks, and 11
diagram blocks. Fifty ordinary target references resolve in the admitted
closure: 27 are Chapter-4-local and 23 point to admitted prior chapters. Two
equation references are local. The one later source reference is rendered as
`\futurexref{6.2.9}{C067441}`, preserving its exact label and official printed
number without pretending Chapter 6 is present.

The deterministic checker finds 817 source and 817 target mathematical
surfaces. It records 802 exact normalized pairs; 807 pairs have equal
translation-neutral math keys. Bounded correction, localization, and
grammar-reordering classifications overlap where appropriate. There are no
unexplained formula deltas. The checker also locks all environment, label, reference, citation,
index-operator, defined-term, and diagram topology, including the explicitly
logged relocation of three misplaced `l_2` index hooks.

The final checker is `qa/check_ch04_translation.py`, 33,292 bytes / 832 lines /
SHA-256
`bcf98112417cf1a0405207d79a4f877f53fd25514ea72dfb985a347843118954`.
Two independent executions returned
`pass_reviewed_ch04_translation_locked` with zero placeholders and zero active
English residue. Final independent rereview found no remaining P1, P2, or P3
translation finding. Bounded scans also found no mojibake, replacement
character, local path, task identifier, credential, or reader-facing build
token.

Twenty-two source-backed corrections are applied and individually recorded.
They include malformed formulas, domains/codomains, coefficients, closures,
product and universal-pair variables, concatenation notation, index placement,
and bounded prose repairs. The cumulative ledger is
`provenance/SOURCE_CORRECTIONS.md`, 11,058 bytes / SHA-256
`8909a33f5ed5dd37065fb4c3afb08e4e0659d17ef1d1a2b8f1d7f307ed1eef2d`.
No upstream contact occurs during production.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex,
  and Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Repeated independently cleaned fixed-path runs produced byte-identical PDFs:
  1,249,703 bytes / 75 US-Letter pages / SHA-256
  `716e3524060f64e4728b4d3d8c1a2b906f377ec4e3b3a3cd1ef3e61759a3dd94`.
- Latest final TeX log: 34,083 bytes / SHA-256
  `e8ecc77de2c68e86372bff08f839667718084c4a2055b0a192ba7c82787020db`.
- Final log: zero TeX errors, unresolved references or citations,
  rerun-required warnings, multiply defined labels, overfull boxes, underfull
  vboxes, or missing characters. It retains two benign front-matter underfull
  hboxes and 31 legacy small-caps-italic substitutions; neither affects reader
  content.
- BibTeX reports zero warnings. MakeIndex accepts all 845 entries, rejects
  zero, and reports zero warnings.

The canonical reader is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf`. Its
build-tree copy is byte-identical. The catalog language is `id-ID`; Indonesian
title, subject, and keywords are present; 26 outline entries expose Chapters
1--4, their sections, bibliography, and index. The file has no encryption,
form, widget, JavaScript, executable action, or embedded attachment.

## Visual and accessibility evidence

All 75 pages were freshly rendered at 144 dpi. Their 75-row manifest is 7,134
bytes / SHA-256
`9f8b88e46823e91920d27ade8f32af30ce347dccd0ab5d759afb2b07f0f64390`,
with zero missing, extra, duplicate, byte-size-mismatched, or hash-mismatched
pages. The page PNGs total 25,021,587 bytes. The all-page contact sheet is
2,535,154 bytes / SHA-256
`4712840f42f3fc988e90eeb80cdc5725ecc7db16383a339f5b98144008ecdc4d`.

The complete contact sheet and full-size physical pages 49, 50, 53--56,
58--67, and 75 were independently inspected, covering the Chapter 4 opening,
dense prose and mathematics, figures, exercises, all category-diagram pages,
the chapter close, bibliography, blank verso, and index boundaries. No
clipping, overlap, unreadable glyph, broken diagram, damaged link rectangle, or
margin violation was found. All 8,038 extracted word boxes on physical pages
49--64 lie within the page bounds. Intentional blank versos are physical pages
4, 20, 48, and 66.

The independent report is
`qa/CH04_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 5,549 bytes / SHA-256
`699009af48643839f1b2ab216d90c4e6f07cf4c3f92d60461d2ccfdae219a8a0`.
It records a visual/render **pass** and an honest accessibility limitation:
the PDF is untagged, and present ToUnicode maps for XY-pic arrow fonts are
empty while the CMEX map is incomplete. Prose extraction is intact, but this
PDF is not claimed to be fully accessible. Semantic accessible HTML, or a
later tagged PDF with corrected math/diagram Unicode, remains required.

## Rights and component closure

The wrapper supplies Erdman attribution, a CC BY-SA 4.0 link, a translation and
technical-change notice, ShareAlike terms, and non-endorsement. `DIAGXY.TEX`
remains byte-identical at 41,908 bytes / SHA-256
`3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb`
under Michael Barr's embedded notice. `TABLE.TEX`, badge artwork, and uncleared
quotation components are absent from the build closure. Separately authored
solutions, mastery support, and the compact-spectral/SVD bridge are not
represented as Erdman-authored content.

## Backend admission and deterministic replay

The Chapter 4 projection appends stable locale-neutral unit, semantic, segment,
formula, relation, exercise-support, index, terminology, correction, artifact,
and typed-QA records while retaining the admitted Chapter 1--3 bytes and IDs.
It adds 130 semantic units, 160 segments, 670 relations, 817 one-to-one formula
maps, 177 index rows, 10 exercise-support records and 11 proof-hint relations,
22 corrections, 53 bounded terminology records, 9 public artifacts, and 8 typed QA
events. The formula projection contains 802 normalized-exact pairs and locks
all reviewed localization, reordering, and source-correction classifications.

The private pretranslation inventory and terminology control remain durable
local coordination under `00_control`; they are not emitted as public artifact
paths. Public terminology provenance instead cites the admitted target,
`backend/index_terms.csv`, and this receipt, so a public checkout has no
dangling private evidence reference.

The canonical validator ran the complete generator twice with byte-identical
outputs. It validated 15 JSONL files / 6,900 records, 845 CSV index rows, 7,745
globally unique IDs, 3,972 relation endpoints, exact JSON and CSV round trips,
and a 24-row manifest. The final admitted replay binds this exact receipt hash
directly into the Chapter 4 unit, corrections, and QA events. Semantic units
and segments carry admitted/passed states and link through their parent unit;
artifacts carry the common admission receipt ID. These links bind them
transitively to the same evidence. The resulting
manifest hash is recorded in the durable state and publication handoff, rather
than circularly embedded in this receipt.

Chapter 4 is admitted. The whole edition remains `in_progress`, and the active
source-order cursor advances to `FAOA-2015-CH05`,
`source/upstream/Hilbert_space_operators.tex`.
