# GitHub Pages repair decision — 2026-08-25

Status: bounded delivery repair in progress; substantive corpus unchanged.

## Proven failure boundary

At repository commit `164d6eb403a995176ef9822a25d5a705c1dd4fc2`
(tree `5eb68a962f8fe7a3ea3bf12b75ca6a3af792f341`), the GitHub repository API
reported `has_pages: false`; the Pages endpoint and `gh-pages` ref returned
HTTP 404; no Pages workflow, deployment, or environment existed. Anonymous
requests to the repository Pages root, `output/html/index.html`, and
`output/html-companion/index.html` each returned the same 9,115-byte GitHub
404 response, SHA-256
`70d613e3acfba24fd2876fcbacaf639e1e111ef4d54baf70761c47673f37d6a3`.

The failure is routing only. The source-reader manifest replayed 104/104 rows;
its `MANIFEST.csv` is 11,616 bytes with SHA-256
`3a3a4a4cdd03d1cae2c49c316fc1f94fe36dad6aa9da79f3764930f011045576`.
The companion manifest replayed 18/18 rows; its `MANIFEST.csv` is 1,744 bytes
with SHA-256
`e20683b5cb9ac6e6cd787d813476213ef8b5ddc2967ff0c6374b67b6419a7365`.

## Selected mechanism

Use the existing repository's GitHub Pages lineage with `build_type=workflow`
and one custom Pages workflow pinned to exact official action commits. The
workflow builds a curated static artifact containing only:

- a small accessible root redirect/fallback to `output/html/index.html`;
- a `/companion/` redirect/fallback to `output/html-companion/index.html`;
- a `.nojekyll` static-delivery marker included in the manifested artifact;
- the admitted source reader under `output/html/`, byte-identically;
- the admitted companion under `output/html-companion/`, byte-identically;
- deterministic deployment metadata and an exact public-byte manifest.

This exposes every existing relative route—including the companion's links to
`../html/index.html`—without rewriting reader bytes, and avoids publishing the
repository's source, backend, build evidence, or credentials as website
content. Two independent local payload builds must be byte-identical. The
workflow validates all manifest rows, internal links and fragments, MathML,
SVG, rights/provenance markers, absence of scripts and private paths, and exact
source-to-payload bytes before deployment.

Workflow privileges are job-scoped: the build has read-only contents/Pages
access and checkout does not retain credentials; only the dedicated deploy job
receives `pages: write` and `id-token: write`. The repository Pages site is
enabled once through the authorized repository API with
`build_type=workflow`; the workflow itself does not attempt account-level
enablement.

## Rights and scope

This routing repair changes no mathematics or admitted reader content. Source
and adaptation rights remain CC BY-SA 4.0; separately authored companion
components retain their recorded provenance. The public metadata keeps source
credit, the model identity `OpenAI Codex gpt-5.6-sol, Ultra`, the direction of
the user, and non-endorsement. It creates no new repository or DOI and does not
justify a new Zenodo version. No upstream report or author contact is allowed.
