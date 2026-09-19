# O008 GitHub Pages recovery handoff — 2026-09-19

Status: complete, public, and anonymously verified.

The existing O008 GitHub Pages lineage now serves the complete Indonesian
reader at <https://kokunoyumeto.github.io/functional-analysis-erdman-id/>. The
root leads to the complete 17-chapter source-text reader; the separately
provenanced mastery companion remains available at
<https://kokunoyumeto.github.io/functional-analysis-erdman-id/companion/>.

The successful deployment is commit
`d0c47da0802742fdd7316acc86c82d9ce238b4a2`, tree
`c479cc0f4bd227336727a3b39b5d67d67ff0eb5c`, tagged
`o008-pages-2026.09.19-recovery` (annotated tag object
`08e57b69b581be281f72273595b1f7805e28ecfa`). Workflow run
[`35470384181`](https://github.com/KokunoYumeto/functional-analysis-erdman-id/actions/runs/35470384181)
and GitHub deployment `6545897535` both completed successfully.

Two local payload replays were byte-identical. The public manifest has 128 rows,
23,873 bytes, and SHA-256
`00b273ec3e2cf1b9074592f2124b02e577a033de1e5e4e7d004775ae5156e57e`.
Credential-free readback downloaded all 128 manifested files (9,031,362 bytes)
and matched every file to both the manifest and its tracked source. The Pages
root, canonical source-reader index, canonical companion index, and bridge
entry all returned exact HTTP 200 byte matches.

Browser QA passed at 1440×900 and 390×844 for the source reader and companion:
no reader-resource failures, no reader console errors, and no page-level
horizontal overflow. Chromium separately requested the GitHub user-site
`/favicon.ico`, outside this repository's project path; that host-level 404 did
not affect any reader route or asset.

The public README already leads visibly to both the primary Pages root and the
companion in its first reading section, so no reader or README rewrite was
needed. PDF, editable source, backend, CC BY-SA 4.0 attribution, component
rights, model provenance, and non-endorsement remain unchanged. No duplicate
repository or DOI was created, and no upstream issue or author contact occurred.

Machine-readable ingestion record:
`provenance/GITHUB_PAGES_RECOVERY_HANDOFF_20260919.json`.
