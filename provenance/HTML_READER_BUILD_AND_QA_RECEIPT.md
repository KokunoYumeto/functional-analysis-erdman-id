# Semantic HTML reader build and QA receipt

Date: 2026-08-24  
Boundary: complete translated source-text corpus, semantic HTML companion  
Admission decision: passed and admitted  
Whole-edition state: in progress; O001 mastery/solutions and the separately
provenanced compact-spectral/SVD bridge remain

## Scope and unchanged authority

This receipt admits the offline HTML reader at `output/html/` for the Indonesian
translation of John M. Erdman's *Functional Analysis and Operator Algebras: An
Introduction*, version 4 October 2015. It contains the preface, all 17 chapters,
bibliography, index, and an edition-information route. The source order and
mathematics are unchanged. Chapters 1--8 remain tagged as the D20 core and
Chapters 9--17 as the advanced continuation.

The HTML work did not alter either canonical source-text artifact:

- `source/id-ID/functional-analysis-id-complete-source.tex`: 11,176 bytes,
  SHA-256
  `7f06919a8ec9088a3bc812fab962a48b5f1b3b0d5d3bce80eb21055f65089041`;
- `output/pdf/analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf`:
  2,480,109 bytes / 238 pages, SHA-256
  `efa2358b3c3e6e8c47e0caee9a02f6afe78d15bea1b0f1822ea8449d801b2b10`;
- unchanged `source/id-ID/DIAGXY.TEX`: 41,908 bytes, SHA-256
  `3df2bc0a4d57650280fd92006c904fc876ebcbe989cee76ee7a73d9d3fa9eefb`.

The PDF remains honestly described as untagged. Semantic accessibility is
provided by this additive HTML companion; this receipt does not recast the PDF
as tagged or fully accessible.

## Deterministic build

The build uses Python 3.13.9, Pandoc 3.9.0.2 with native MathML, lxml 6.1.1,
MiKTeX-pdfTeX 4.27, and dvisvgm 3.6. The final public tree contains 105 files /
7,656,969 bytes. Its deterministic inventory SHA-256 is
`f04bb3f5ee883c794474b191faf0e724987ebc01c4711bac8f6dc5421e543f32`.
`output/html/MANIFEST.csv` is 11,616 bytes, SHA-256
`3a3a4a4cdd03d1cae2c49c316fc1f94fe36dad6aa9da79f3764930f011045576`.

Two clean corrected replays, `qa/html-replay-c-site/` and
`qa/html-replay-d-site/`, each produced the same 105 relative paths, byte
counts, and SHA-256 values with zero differences. The independently rebuilt
canonical `output/html/` tree also differs from neither replay at any path.
Both replay build reports are byte-identical; both replay machine-QA reports
are byte-identical.

The final build report is `qa/HTML_BUILD_RESULT.json`, 85,883 bytes, SHA-256
`82b3cbd022ea4aec5ba02a1e69840fbae15b00f67497d80313ce95b62bb87868`.
It records 22 routes, 1,867 semantic units, 2,196 segment anchors, 11,193 native
MathML nodes, 80 SVG diagrams, 2,104 index occurrences, 55 bibliography
entries, 571 rewritten cross-references, and 213 rewritten citations. It
records zero duplicate IDs, missing segment IDs, MathML fallbacks, Pandoc math
warnings, or unresolved references.

## Structure, accessibility, rights, and security QA

`qa/HTML_READER_QA.json` is 615 bytes, SHA-256
`50f35831a6db39d54b098b3d31ecef135dde9a8cc2facc1113c32c2bc7c5ab2b`.
The independent checker passed with zero findings over 105 files, 22 HTML
documents, 80 images and standalone SVGs, 11,193 MathML nodes, 12,805 internal
references, 4,838 route-map records, and three tables. Its bounded self-test
accepts the valid fixture and rejects all 21 representative defect classes.

Every MathML node carries its TeX annotation, an Indonesian formula label, and
`role="math"`. Every diagram carries an SVG title/description, image alternative
text, a visible Indonesian transcript, source/component provenance, and a
non-endorsement statement. The 80 records in
`html/accessibility/diagram_text.jsonl` are exact-ID unique and match the 80
final SVG and HTML surfaces. `DIAGXY.TEX` remains unchanged and is not embedded
in the reader; its Michael Barr notice remains controlling. `TABLE.TEX`, badge
art, `Wiener_quote.tex`, and uncleared quotation material remain excluded.

The substantive source and Indonesian adaptation remain CC BY-SA 4.0 with
attribution, change notice, ShareAlike, no additional restrictions, and no
implied endorsement. Accessible descriptions are identified as additions made
with OpenAI Codex gpt-5.6-sol, Ultra at the user's direction; Erdman's source
authorship remains primary.

External HTTP bibliography addresses are preserved as non-clickable visible
text. Optional HTTPS links use safe external-link relation tokens. The reader
contains no base element, unsafe active content, local filesystem path, raw
math fallback, image-only formula, unresolved internal link, or unbound ARIA
reference found by the checker.

The case-sensitive route map is `backend/html_routes.jsonl`, 852,785 bytes /
4,838 records, SHA-256
`36fb1838ae99ad850c8f4832c318d64d87f5aee1eb22415583f4ec8178a7c0f5`.
`exam_dual_C0` and `exam_dual_c0` are distinct inherited source labels and must
remain case-sensitive; neither is merged.

## Responsive visual QA

`qa/HTML_VISUAL_QA.json` records the all-route rendered review. All 22 routes
were measured at 1440 by 900 CSS pixels and 390 by 844 CSS pixels. Both passes
have zero document-level horizontal overflow, zero unconfined element failure,
and zero article-centering delta. Desktop content uses the full main region
with a centered 0.64-width reading measure and sticky book navigation. Mobile
content reflows to a centered 0.911-width reading column with static navigation.

All 80 final SVG images were loaded at the stricter mobile viewport and had
positive intrinsic and rendered dimensions with no viewport escape. Browser
console review recorded zero warnings or errors. Visual inspection covered the
home/status surface, mobile navigation and reading column, Chapter 6 diagram
and transcript, long Chapter 5 inline mathematics, and bibliography URL
wrapping.

The review found and corrected four presentation defects without changing the
translated source: low dark-mode status-panel contrast, black diagrams on a
dark panel, mobile overflow from long inline MathML in Chapters 3/5/17, and
mobile overflow from two preserved bibliography URLs. Final dark-mode contrast
is 11.410:1 for status text and 15.973:1 for diagram strokes. Long inline MathML
now scrolls within its own bounded inline box below 36rem, and retained HTTP
text wraps anywhere.

## Admission

The semantic HTML source-text reader is admitted at the identities above. The
locale-neutral backend binds the site, route map, assets, QA, rights, and
artifact hashes additively; its separate reconciliation receipt records the
final backend-manifest identity. Publication must use this exact admitted tree
and must describe the edition honestly as source-text translation plus semantic
HTML complete, with the O001 mastery/solutions layer and compact-spectral/SVD
bridge still pending.
