# Final Companion PDF Visual and Accessibility Audit

Status: **pass**
Edition: complete id-ID source text plus separately provenanced O001 mastery
and compact-spectral/SVD bridge
PDF: `output/pdf/analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf`
Bytes: 2,838,207
SHA-256: `6d4bbf02959e5afb5fd34e1118f91f026c293b0056ec7a0ecdc5e95944df5d85`
Physical pages: 298 US Letter

## All-page visual inspection

Poppler rendered all 298 pages at 110 dpi to 935 by 1,210 pixel PNGs. The
render manifest is `provenance/FINAL_COMPANION_RENDER_MANIFEST.csv`, SHA-256
`0a421ee19fe0743c8ae04caaf1f2beac4e4d68c6d50779aa4226caf17c7f1826`.
Every contact sheet was inspected. All sheets except the bounded 265--276 sheet
are byte-identical to the preceding complete all-page inspection. That changed
sheet and physical pages 273--274 were re-inspected at original render
resolution after the final running-head correction.

No clipping, overlap, formula loss, broken glyph, truncated heading, or outer
edge ink was found. The minimum nonblank margins are 109 px left, 72 px top,
78 px right, and 60 px bottom. The blank pages reported by the raster audit are
structural versos: 28, 56, 86, 108, 122, 144, 154, 168, 172, 186, 198, 218,
224, 234, and 276. None hides reader content.

The provisional companion layout had inconsistent nested `chapter*` and
`section*` solution headings, two avoidable blank versos, a two-line widow,
and stale even-page running heads. The final layout makes all twelve source-
chapter solution groups section-level units inside Chapter 20, binds them in
the table of contents, and emits each running mark before its heading. The
result is 298 pages rather than 302. Full-resolution checks of every solution
transition through physical page 275 confirm consistent, legible headings.
Physical page 273 retains the Bab 13 running head and physical page 274 opens
Bab 14 with the Bab 14 running head. An independent bounded review plus this
post-correction check found no remaining visual defect.

Attribution, CC BY-SA 4.0 component rights, exact model provenance, source-
author separation, and non-endorsement are visibly stated at the bridge,
selected reader-work, all-solutions introduction, and solution-group surfaces.

## Navigation, security, and accessibility

`qa/FINAL_COMPANION_PDF_SECURITY_NAVIGATION_AUDIT.json` passes: 141 outline
entries, 3,116 resolved internal links, 2,612 named destinations, 53 font rows
all embedded/subset/Unicode-mapped, no encryption, JavaScript, launch action,
file attachment, embedded-file tree, rich media, or unresolved internal link.
The PDF catalog language is `id-ID`.

The PDF is honestly untagged and is not claimed to be the accessible surface.
The additive semantic companion at `output/html-companion/` provides native
MathML, stable anchors, responsive navigation, and the accessible text-diagram
surface; its exact build, machine, reproducibility, and visual-QA receipts bind
that remediation.
