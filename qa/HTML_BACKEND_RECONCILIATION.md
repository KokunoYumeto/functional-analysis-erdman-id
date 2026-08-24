# Semantic HTML backend reconciliation

Date: 2026-08-24  
Result: pass  
Surface ID: `FAOA-2015-ID-HTML-SOURCE-TEXT`

The semantic HTML reader is bound additively over the admitted complete
source-text backend. The exact pre-HTML byte prefixes remain unchanged:

| Record set | Locked bytes | Locked records | Locked SHA-256 |
|---|---:|---:|---|
| `artifacts.jsonl` | 105,861 | 207 | `6d4eee148186e9f71deae438ef1f7525011d7e1f9bad5e40b9d09b140ffa9365` |
| `qa_events.jsonl` | 126,742 | 155 | `c0d8a88080caab5b439e728596cd06d40193c1fba168a80c26cea88395c3fa94` |
| `relations.jsonl` | 2,282,344 | 8,627 | `12f6888069cdf4a2efe331b0b4d9a641b7fcbc20c6aa1e2699920bf477a90255` |

The historical complete-source backend manifest remains identified by SHA-256
`413756e2e337e8c032c9fba14f07242c47c266503a582f40e537a0e94b4d105b`.
`backend/HTML_PREFIX_LOCKS.json`, 1,035 bytes, SHA-256
`5cd7b200349b2b05f7df0a0f56f8ff279f40649793e67d81d307c933dcf57d97`,
freezes that append boundary.

The HTML layer adds:

- one admitted HTML-surface record in `backend/html_surfaces.jsonl`, 1,401
  bytes, SHA-256
  `a7de54f540550144e06f26bd61310d1a639bb711b1e9f4cec884a72ee36f1a7a`;
- 80 accessible SVG asset records in `backend/html_assets.jsonl`, 99,948
  bytes, SHA-256
  `1ba1b4d4e98addfb6a3d661a556afdff04683b6d0a801102d9a0144dc711d1f4`;
- 10 bound artifact records, five passing QA events, and 97 resolved
  relations appended after the exact source-text prefixes;
- the auxiliary case-sensitive route map
  `backend/html_routes.jsonl`, 4,838 records / 852,785 bytes, SHA-256
  `36fb1838ae99ad850c8f4832c318d64d87f5aee1eb22415583f4ec8178a7c0f5`.

The route map is intentionally not an entity record set: 4,081 route IDs map
to canonical backend IDs, while the remainder are HTML-only anchors. Route IDs
are case-sensitive. In particular, `exam_dual_C0` and `exam_dual_c0` preserve
two distinct inherited source labels and must not be case-folded or merged.

The current backend manifest has 61 rows, 5,684 bytes, and SHA-256
`06ad5f9c6931ef1838a8307c60b8b3b94a4c89a25d6ddc12dbfb2a3ddc591cfc`.
`backend/generate_html_backend.py` reproduced the checked-in outputs exactly
with no mismatch. `backend/validate_html_backend.py` and the canonical
`backend/validate_backend.py` entrypoint each passed two deterministic
in-memory generator replays, global entity-ID uniqueness, all relation
endpoints, rights references, every artifact byte/hash, all 80 final SVG
bytes/hashes, and the 4,838 exact-case route IDs.

The machine-readable validation receipt is
`qa/HTML_BACKEND_VALIDATION.json`, 1,026 bytes, SHA-256
`4ef3c01335843fdd85f051921c269fd8bcfbc16f323c4424e56af554c1908bb5`.
It binds the HTML admission receipt SHA-256
`66fbf6a9c601b323fd30e3bcf2e4f22bfc2543a5c3c677eb73e9e520940d5314`
and the site inventory SHA-256
`f04bb3f5ee883c794474b191faf0e724987ebc01c4711bac8f6dc5421e543f32`.

The whole edition remains `in_progress`: the translated source text and
semantic HTML companion are admitted, while O001 mastery/solutions and the
separately provenanced compact-spectral/SVD bridge remain pending.
