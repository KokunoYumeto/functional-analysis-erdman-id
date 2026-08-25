# Companion Backend Artifact Reconciliation — 2026-08-25

Status: reconciled; additive backend only; no source, translation, mathematics,
PDF, HTML, solution, or bridge byte changed.

The terminal completion audit reran `qa/validate_companion_backend.py` instead
of relying only on its earlier report. It correctly found that
`backend/companion_artifacts.jsonl` still described an earlier byte stream for
`qa/FINAL_COMPANION_COMPONENT_VALIDATION_CONSOLE.txt`. The live admitted
console is 4,330 bytes, SHA-256
`874ea2a4da664f01be45152bc9dbaa1e15333608d7badc82df7082226e523d29`;
the stale overlay record described 4,338 bytes under a different hash.

`backend/generate_companion_backend.py` was rerun against the admitted live
artifacts, followed by the strict validator, then the same generator/validator
sequence a second time. Both reconciled replays were byte-identical and the
validator reports zero findings. Only these generated records changed:

- `backend/companion_artifacts.jsonl`: 35,524 bytes, SHA-256
  `6256503166fb89d9de4959571602abcf9599b39f5edc902ac1851ef5bf1e7b30`;
- `backend/COMPANION_BACKEND_MANIFEST.csv`: 1,073 bytes, SHA-256
  `9be0d071106f9ba38e00f50811a718c84102e4527ae507a8e51250bbd9bfb201`;
- `qa/COMPANION_BACKEND_VALIDATION.json`: 4,524 bytes, SHA-256
  `ee7ae54a5a069e22aabd9e2c76e16a5b8571736cf93a6298babd80730735312d`.

All 19 base JSONL files remain byte-identical: 14,878,396 bytes under base
manifest SHA-256
`06ad5f9c6931ef1838a8307c60b8b3b94a4c89a25d6ddc12dbfb2a3ddc591cfc`.
The admitted overlay counts remain four components, four provenance records,
52 exercise solutions, ten reader-work solutions, 52 support overlays, 13
bridge units, two surfaces, 294 HTML routes, 826 relations, and 70 artifacts.

The strengthened public-byte verifier then exposed a separate Git line-ending
boundary: three admitted PowerShell-generated witnesses matched their backend
records on disk but Git's default text normalization stored LF variants. The
release now marks those three exact paths `-text` and binds their actual CRLF
bytes in Git, the compact archive, and both anonymous verifiers:

- `qa/FINAL_COMPANION_BUILD_RESULT.json`: 1,935 bytes, SHA-256
  `5719f9a726fb5a411a7b76879058ad7e14c155717130ad5e8c4672c941c591df`;
- `qa/FINAL_COMPANION_INPUT_SNAPSHOT.csv`: 4,113 bytes, SHA-256
  `322799f519043092002ad61fbf3f38367cf15004f5d43304b976187c3769d869`;
- `qa/FINAL_COMPANION_COMPONENT_VALIDATION_CONSOLE.txt`: 4,330 bytes,
  SHA-256
  `874ea2a4da664f01be45152bc9dbaa1e15333608d7badc82df7082226e523d29`.

This exact-byte binding changes only evidentiary line endings in the Git tree;
it does not change source, translation, formulas, PDF, HTML, solutions, or
bridge content.
