# FAOA-2015-CH10 build and QA receipt

Date: 2026-08-22  
Decision: **admitted**  
Course role: `advanced_continuation`

This receipt admits the complete Indonesian Chapter 10, *Distribusi*, and the
cumulative Chapter 1--10 reader. Translation, mathematics, structure,
references, terminology, build determinism, visual layout, navigation,
component rights, privacy, and append-only backend gates pass. It does not
claim that Chapters 11--17, the semantic HTML reader, the O001 solved mastery
layer, or the original compact-spectral/SVD bridge are complete.

## Exact source and target identity

- Frozen source: `source/upstream/distributions.tex`, 42,703 bytes / 894
  CRLF-terminated records / SHA-256
  `31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8`.
  Its sole `\endinput` is the final nonblank source record.
- Admitted target: `source/id-ID/distributions-id.tex`, 42,627 bytes / 876 LF
  records / SHA-256
  `6456f9def822da572e117f3ec368931f0bfb441840aa0785be1df6080bbb6840`.
- Cumulative master:
  `source/id-ID/functional-analysis-id-through-ch10.tex`, 9,866 bytes / 336
  LF records / SHA-256
  `5de05f7a154bea99d11924fc21dbbf7495c8642d5a3c58e48e0fdd053dd400b4`.
- The admitted Chapter 1--9 targets and every locked backend prefix remain
  unchanged.

The seven reviewed contiguous translation fragments are:

1. `part_0001_0094.tex`: 4,510 bytes / SHA-256
   `c84f091e9f5226aafa2f3b89507855fa7df92b278c1c2742fed5e18b8bb9c0b0`;
2. `part_0095_0190.tex`: 4,094 bytes / SHA-256
   `adfdcd3a4ee97faf5cc0261affe5b6d909ef5a1d37428c172462143d9d8f2a09`;
3. `part_0191_0386.tex`: 11,307 bytes / SHA-256
   `0d7b8127b464546247966249996f781fdf6fe4e477deee5599cda6d1538c5170`;
4. `part_0387_0481.tex`: 4,857 bytes / SHA-256
   `9477bccbba12c5e27b854b851b5ae08093c7b91f2c62e624b69cf9066c4a0cdd`;
5. `part_0482_0710.tex`: 9,841 bytes / SHA-256
   `de59e7c34e0f56c2085b8af4839f681efb62faf12d331bad9845f7ad719f39ff`;
6. `part_0711_0796.tex`: 3,705 bytes / SHA-256
   `226a0d26bdde4fa0d2ccb37426ae4db6189b1d655717e61c11989066b7b4db3b`;
7. `part_0797_0894.tex`: 4,313 bytes / SHA-256
   `65c18dd37bdb7fa77cc08c9d7c7081ac3d57b3c85d6ee6057404c578470874ae`.

The locked fragment checker and assembler reproduce the admitted target
exactly. Their identities are respectively 13,288 bytes / SHA-256
`a7b32ccf8fc6ef0188e00bbd1e6fad333ed1bf5a9ed064c02aeae660d06d523e`
and 6,142 bytes / SHA-256
`e6c9e117e95372f66001700ee22497f15564d008e1c40bc10a31baa09c0063bd`.

## Structural, mathematical, language, and terminology replay

The locked checker preserves the chapter and all six sections, 124 semantic
environment openings, 18 labels, 20 references, 29 citations, 101 index hooks,
35 defined-term hooks, 11 exercises, three proof hints, 15 citation-only proof
surfaces, and 648 target mathematical surfaces. All label, reference,
citation, index-operator, proof-role, and learning-support sequences retain
their source order. The 651-to-648 mathematical-surface delta is exactly the
classified repair of the false direct-limit construction; every remaining
non-exact formula is bound to localization or a recorded source correction.
No unclassified mathematical edit remains.

The final checker is `qa/check_ch10_translation.py`, 16,387 bytes / SHA-256
`fa247c00608997da81d65bdcadc0bfa916060a0bb8858c24e5f0a54ac5aa75db`.
Its deterministic report is `qa/ch10-translation-report.json`, 1,089 bytes /
SHA-256
`8b472e7b803cfb566e08c4ff3f1e464f7564520faf2f9115f3b57e7042c1218d`.
Repeated replay returns `pass`, with zero visible English residue other than
two cited English book titles, zero mojibake, zero private path, and zero
structural or unclassified mathematical error.

Sixteen corrections are locked in
`provenance/SOURCE_CORRECTIONS_CH10.json`, 11,858 bytes / SHA-256
`c5010ce91ae98d3c9b3637fe6a553f4df7d1ba524faa75b1f4fb42b0b036c948`:
nine mathematical repairs, five mechanical repairs, one semantic repair, and
one semantic TeX repair. They include a standard direct-sum quotient
construction for the inductive-limit hint, restored index/codomain/integral
notation, and the corrected convolution identity. The append-only Chapter
1--10 human-readable ledger is `provenance/SOURCE_CORRECTIONS.md`, 32,495
bytes / SHA-256
`8bd1be45b70a5e2395e67c20f192f89fc658f3d158d8ff7bb9b1e9cef77b947b`.
No upstream contact occurred.

The one-time Indonesian field-terminology gate remains passed. A focused
Chapter 10 check against the inspected ITB usage establishes *distribusi
tempered* as the preferred reader term while retaining *distribusi temperate*
only as the source's explicit alternative recognition form. The decision is
recorded in `provenance/CH10_TERMINOLOGY_DECISIONS.md`, 1,756 bytes / SHA-256
`03005aa60200768a05c700e7d9d8cfa969034204e37ecffbd8b67126c5c66329`.
The non-redistributable terminology witness remains local QA evidence and is
not included in any public payload. The public provenance retains the exact
model identification **OpenAI Codex gpt-5.6-sol, Ultra** and preserves all
source-author and human-contributor credits.

## Reproducible cumulative build

- Toolchain: MiKTeX 26.5, pdfTeX 1.40.29, latexmk 4.88, BibTeX, MakeIndex, and
  Xy-pic.
- Fixed environment: `SOURCE_DATE_EPOCH=1444126743`.
- Two fully cleaned replays in the same fixed output directory produced
  byte-identical PDFs: 1,796,056 bytes / 153 US-Letter pages / SHA-256
  `1f793d022efeafae1c69b4f36a9b992031f77bf343154e585dc95ba543d72ebc`.
  A diagnostic build in a different directory changed only the PDF trailer ID
  and is not used as evidence of byte identity.
- Final TeX log: 52,286 bytes / SHA-256
  `993caf6e1602de89155464ba9f3f2d735e6db1f14b4a242f6ddbe31f2f65fef3`.
- Blocking log counts are zero: TeX/package errors, unresolved references or
  citations, rerun notices, multiply defined labels, overfull boxes, vbox
  warnings, and missing characters. Four inherited underfull hboxes arise
  from long authority URL/hash material. The inherited small-caps-italic
  substitutions and the two math-shift bookmark notices do not alter visible
  text; the Chapter 10.2 bookmark is correctly `Ruang-LF`.
- BibTeX uses 36 entries with zero warnings. MakeIndex accepts 1,524 entries,
  rejects zero, makes 17,626 comparisons, writes 1,858 lines, and reports zero
  warnings.

The canonical reader is
`output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf`; its
fixed-path build copy is byte-identical.

## Visual and accessibility evidence

All 153 physical pages were rendered at 150 dpi. The exact render set contains
153 PNGs / 54,129,667 aggregate bytes, each 1,275 by 1,650 pixels. The public
render manifest is 29,798 bytes / SHA-256
`b1dd863b6b2441e0a49bf9fe3248b759c9889f0a74654fbe060d868f60cfb7ca`;
replay finds no missing, extra, duplicate, dimension-mismatched, or
hash-mismatched page. The public all-page contact sheet is 4,463,573 bytes /
SHA-256
`e5b14686ad4ce088d02ba819e3df14621936dd888b429b92a9506e53ce9d34f6`.

Every page was inspected through thirteen detailed consecutive contact sheets.
Physical pages 124--139 received a second full-resolution inspection covering
the Chapter 9 close, all of Chapter 10, the inductive-limit diagram, every
section and learning-support surface, the bibliography and index transitions,
and both intentional blank versos. No clipping, overlap, off-center body
block, damaged glyph, unreadable formula, broken diagram/header, unexpected
blank, or margin violation was found.

Bounding-box replay finds 72,104 words and zero boxes outside page bounds,
with minimum clearances of 72.000 points left, 71.254988 right, 49.278601 top,
and 37.803801 bottom. The seven zero-word pages are exactly the intentional
blank versos 20, 48, 78, 100, 114, 136, and 138. The formal report is
`qa/CH10_FINAL_PDF_VISUAL_ACCESSIBILITY_AUDIT.md`, 7,203 bytes / SHA-256
`5d5ff18e230a8fc1d2aace1b801b53487ebb409c5bdb3bc6e600056b73a75bea`.

The PDF has language `id-ID`, 64 outline entries, 1,516 named destinations,
2,005 resolved internal links, eight URI annotations over six unique external
targets, and zero unresolved internal links. It has no encryption, form,
widget, JavaScript, launch action, embedded attachment, rich media, or unsafe
action. All 45 font resources are embedded subsets with Unicode maps.
Extracted text is 584,818 bytes / SHA-256
`7d33802d1a3cd9d9249facbde20ad719ac1342fbbd08d9b3588f20a82c1595c9`
and contains no replacement character, mojibake signature, or local path.

The PDF remains honestly untagged and lacks a structure tree, semantic roles,
alternative-text framework, and guaranteed screen-reader order. It is a
visually usable, searchable, navigable reader, not the final accessible
edition. Semantic HTML and/or a later tagged-PDF derivative remains a required
edition-level deliverable and is nonblocking only for this chapter boundary.

## Rights, privacy, and backend closure

The wrapper supplies John M. Erdman attribution, a CC BY-SA 4.0 link,
translation and technical-change notices, ShareAlike terms, and
non-endorsement. `DIAGXY.TEX` remains byte-identical under Michael Barr's
embedded notice. `TABLE.TEX`, badge artwork, and uncleared quotation
components remain absent. Separately authored solutions, mastery support, and
the compact-spectral/SVD bridge are not represented as Erdman-authored
content. A bounded public-surface scan finds no credential, live local path,
unrelated-lane reference, or private control artifact.

The Chapter 10 backend projection appends 116 semantic units, 132 segments,
523 relations, 648 formula maps, 11 exercise-support records, 101 index rows,
28 new terminology records, 16 correction records, 11 exact artifact
bindings, and eight typed QA events. Every admitted Chapter 1--9 byte prefix
and stable ID remains unchanged. The complete generator is replayed twice;
byte-identical output, exact JSON/CSV round trips, globally unique IDs,
relation endpoints, formula source/target closure, public artifact bytes,
private-control exclusion, and the Chapter 1--9 prefix locks all pass. Final
aggregate counts and the backend manifest identity are recorded in durable
state after this receipt is bound, avoiding a circular receipt hash.

Chapter 10 is admitted. The whole edition remains `in_progress`, and the active
source-order cursor advances to `FAOA-2015-CH11`,
`source/upstream/Gelfand_Naimark.tex`.
