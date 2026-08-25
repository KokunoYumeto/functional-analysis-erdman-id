# Final Integrated Edition — Build and QA Receipt

Date: 2026-08-25
Role: O008 / D20
Locale: `id-ID`
Status: **admitted and publicly preserved**

## Authority and scope

The source authority remains John M. Erdman's *Functional Analysis and
Operator Algebras: An Introduction*, version 4 October 2015. The frozen
official source ZIP is 262,556 bytes, SHA-256
`0c667cfa7420b61dda8f8cb4ed9d619db8abbd1b53d17eafe7d4a2e153342e53`; the
official 230-page PDF is 2,336,387 bytes, SHA-256
`f320b16af7448fbb43582c21569840fe657fccf6f31d97f176913fdd0e1eb823`;
and `authority/SOURCE_MANIFEST.csv` closes all 27 archive members under
SHA-256 `e222e326d8ff5fcd30b66b3b44642043295e1cb39920c58ff353eaafafd276d1`.

The Indonesian edition contains the preface, all 17 chapters in source order,
bibliography, and translated index. Chapters 1--8 are tagged D20 core and
9--17 advanced continuation without deleting source material. The final
reader adds, with separate authorship and provenance, solutions for all 52
explicit source exercises, checked solutions for ten selected central
reader-work results, and a 13-unit compact-spectral/SVD bridge. The bridge
covers Riesz--Schauder consequences, the compact self-adjoint spectral
theorem, singular values/SVD, finite-rank approximation error, and polar
decomposition without duplicating Chapter 15's Fredholm development.

## Exact admitted artifacts

- Integrated PDF:
  `output/pdf/analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf`,
  2,838,207 bytes, 298 US-Letter pages, SHA-256
  `6d4bbf02959e5afb5fd34e1118f91f026c293b0056ec7a0ecdc5e95944df5d85`.
- Generated master:
  `source/id-ID/functional-analysis-id-complete-with-companions.tex`,
  14,023 bytes, SHA-256
  `d50c78b69f342b8d22a817dcaf74746a992115d14077065f019a1ecd47152024`.
- Bridge source: `bridge/id-ID/compact-spectral-svd.tex`, 16,999 bytes,
  SHA-256 `201e343ddac2776e072f40f7d5f9c24a72f361d5ec973aff750a03c2bd95c31a`.
- Exercise inventory: `mastery/O001_EXERCISE_INVENTORY.jsonl`, 52 records,
  80,266 bytes, SHA-256
  `d98c1a91308b4b35dea61f157427efa80bd9b406ecd04a15a3572d44ddb6643a`.
- Reader-work inventory: `mastery/O001_READER_WORK_INVENTORY.jsonl`, ten
  records, 21,753 bytes, SHA-256
  `606505ede826bcc38666d590e8fb9586a89ed01048259a4f2e5a635eca747dad`.
- Semantic companion reader: `output/html-companion/`, 19 files / 1,343,144
  bytes including its manifest; inventory SHA-256
  `e9b8aa804bf619d7bfcc12a5767d5c6ef9836a1ac512c946fa925ef926e8f2fb`.
  Its manifested-site SHA-256 is
  `b2f953e6b4049f87ce583c45ca7f0f96eb496f7d678a85d0a1918a3c49d9cafe`;
  manifest SHA-256
  `e20683b5cb9ac6e6cd787d813476213ef8b5ddc2967ff0c6374b67b6419a7365`;
  route-map SHA-256
  `4a95bfba3957dc2d0fc73dc1a1ae4c47848e197a61a9d71365fd51d312388ee1`.

## Deterministic PDF and mathematical closure

`qa/run_final_companion_build.ps1` validates every component, regenerates the
master from the admitted source master, freezes 36 inputs, and performs two
clean fixed-path LaTeX replays under `SOURCE_DATE_EPOCH=1444126743`. Both
replays produced the exact PDF above. The final log has zero TeX errors,
undefined references/citations, unresolved summaries, rerun warnings,
multiply-defined labels, or missing characters. Six overfull boxes are
inherited from the admitted source reader; the companion adds zero.
`qa/FINAL_COMPANION_INPUT_SNAPSHOT.csv` is 4,113 bytes, SHA-256
`322799f519043092002ad61fbf3f38367cf15004f5d43304b976187c3769d869`.

The 52 exercise solutions, ten reader-work solutions, and 13 bridge units pass
their exact ID/order/source-statement/provenance/rights/structure validators.
A bounded independent mathematical rereview was applied to the complete
companion after corrections; no unresolved mathematical blocker remains. The
known source inconsistency in Chapter 14 exercise 2 is not silently rewritten:
the admitted translation preserves the printed statement, while the separately
authored solution explains that a right action gives an antihomomorphism and
states the corrected equivalence. Its evidence is
`provenance/O001_SOURCE_ADJUDICATIONS.json`.

## PDF visual, navigation, security, and accessibility evidence

All 298 pages were rendered at 110 dpi. The render audit reports no ink within
the outer five pixels, minimum nonblank margins of 109 px left / 72 px top /
78 px right / 60 px bottom, and only the 15 expected structural blank versos.
The 298-row render manifest is 34,135 bytes, SHA-256
`0a421ee19fe0743c8ae04caaf1f2beac4e4d68c6d50779aa4226caf17c7f1826`.
Every contact sheet was inspected; the final Bab 13/Bab 14 transition was also
checked at full resolution. Physical page 273 retains the Bab 13 head and page
274 opens Bab 14 with the Bab 14 head. No clipping, overlap, formula loss,
broken glyph, or truncated heading remains.

The security/navigation audit passes with 141 outline entries, 3,116 resolved
internal links, 2,612 named destinations, and 53 font rows all embedded,
subset, and Unicode-mapped. The catalog language is `id-ID`; there is no
encryption, JavaScript, launch action, attachment, embedded-file tree, or rich
media. The PDF is honestly untagged. It is not claimed to be the accessible
surface; the two semantic HTML readers provide that remediation.

## HTML and backend closure

The canonical companion reader and two clean replays are byte-identical: 19
files / 1,343,144 bytes / inventory SHA-256
`e9b8aa804bf619d7bfcc12a5767d5c6ef9836a1ac512c946fa925ef926e8f2fb`.
Machine QA passes 15 documents, 2,288 MathML elements, 448 internal references,
126 source-reader links, 52 solutions, ten reader-work units, 13 bridge units,
294 route records, and zero findings. Browser QA covers every route at desktop
and mobile widths with no horizontal overflow; the reading column is centered
within the main content area and mobile content reflows to 342 px.

The additive backend preserves all 19 admitted base JSONLs byte-identically:
14,878,396 bytes under base manifest SHA-256
`06ad5f9c6931ef1838a8307c60b8b3b94a4c89a25d6ddc12dbfb2a3ddc591cfc`.
Its companion overlay records four components, four provenance records, 52
exercise solutions, ten reader-work solutions, 52 support-status overlays, 13
bridge units, two admitted surfaces, 294 HTML routes, 826 relations, and 70
artifacts. Strict validation and second-run byte replay pass with zero
findings. `backend/COMPANION_BACKEND_MANIFEST.csv` is 1,073 bytes, SHA-256
`9be0d071106f9ba38e00f50811a718c84102e4527ae507a8e51250bbd9bfb201`;
`qa/COMPANION_BACKEND_VALIDATION.json` is 4,524 bytes, SHA-256
`ee7ae54a5a069e22aabd9e2c76e16a5b8571736cf93a6298babd80730735312d`.
All 70 artifact records agree with their live bytes. Three PowerShell-generated
QA witnesses are explicitly marked `-text` so Git and release archives retain
their admitted CRLF streams exactly; anonymous GitHub and Zenodo verifiers
check each actual stream against its backend record.

## Rights, attribution, and contact boundary

Erdman's substantive source and the Indonesian adaptation remain CC BY-SA
4.0. Attribution, license link, change notice, ShareAlike, no additional
restrictions, and non-endorsement are explicit. `DIAGXY.TEX` remains
byte-identical under Michael Barr's embedded notice; `TABLE.TEX`, badge art,
and uncleared quotations are not redistributed. The O001 solutions,
reader-work solutions, and bridge are separately authored CC BY-SA 4.0
components and are not represented as Erdman-authored. Model provenance is
stated exactly as `OpenAI Codex gpt-5.6-sol, Ultra`, at the user's direction,
without displacing source-author credit. No upstream contact occurred.

The admitted integrated edition and reconciled backend are public in the
existing GitHub mirror and Zenodo concept. The release archive is bound to
Git commit `059bda086dfd6e6aa80f2077b2338c5d15039057`, tree
`77822a94a46d6422d9ed9c6b48e345229a4e7c05`; Zenodo record/DOI
`22088947` / `10.5281/zenodo.22088947`. Separate sanitized GitHub, package,
metadata, and Zenodo receipts record anonymous byte readback and final
coordinator handoff.
