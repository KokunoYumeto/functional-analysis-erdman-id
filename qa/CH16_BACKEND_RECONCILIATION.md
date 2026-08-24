# FAOA-2015-CH16 backend reconciliation

The Chapter 16 append preserves the exact admitted Chapter 1--15 byte prefix and binds the complete Extensions source/target topology.

- Target: `source/id-ID/extensions-id.tex` — 43804 bytes, SHA-256 `59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3`.
- Semantic units: 127; segments: 141; relations: 601.
- Formula maps: 701 covering 702 source and 700 target surfaces exactly once; index rows: 107.
- New terms: 21; term uses: 29; corrections: 15; exercise-support records: 0.
- `backend/CH16_PREFIX_LOCKS.json` locks the complete Chapter 1--15 prefix byte-for-byte.
- `backend/validate_ch16_backend.py` checks stable-ID uniqueness, relation endpoints, formula/index closure, manifest identity, and deterministic replay.
- Model provenance: `OpenAI Codex gpt-5.6-sol, Ultra`.

Generated identities:

- `artifacts.jsonl` — 92146 bytes, SHA-256 `463aa01410e11d1d1508a0614ca9427d8f09a6697c3767c3a0aaedb485b61862`
- `BACKEND_MANIFEST.csv` — 4552 bytes, SHA-256 `e707c21b95641997c72f63acf1ad4d61affe6c321f4d9f269e959cafbf0beff3`
- `CH16_PREFIX_LOCKS.json` — 1975 bytes, SHA-256 `881800f969c6ef99674f120ad29fa43dd1763ca53fa8615b76badd8254169871`
- `corrections.jsonl` — 233724 bytes, SHA-256 `420b1fda2575e259db4f94b866e27a5bb781cc782dc4cb7920497a037585b516`
- `exercise_support.jsonl` — 27135 bytes, SHA-256 `da1bd2f951ec0982cefce076ea5bd64a69c14613102ce1d7e17ed056a1763ffc`
- `formula_map.jsonl` — 6670181 bytes, SHA-256 `ae729d8948fbfc2aa8894633d71f1b2dc1ce95e021fd714f2a5be257e3695588`
- `index_terms.csv` — 499785 bytes, SHA-256 `691ed53a07998aaea922f3f2d61d316eb5178d065c165d233481fc26d3ef1847`
- `qa_events.jsonl` — 113597 bytes, SHA-256 `fbcdad8ec4567dd478704c8979a03fb9585d25aefb62a3d6a54c21299c344032`
- `relations.jsonl` — 2059296 bytes, SHA-256 `f4f32cd06df7e97db82a29f8b76887ea9bcb3a2954541bb477280ea2f0cfd69b`
- `segments.jsonl` — 1598607 bytes, SHA-256 `b38a228ded09e12a34e48c945a546e2bb592c9c3bcac81e9faf0676c0bfee93e`
- `semantic_units.jsonl` — 1431899 bytes, SHA-256 `403fc20586c45019f0693ece4beaa627e1b50f7447f6ea7a6dc8ed529f910319`
- `terminology.jsonl` — 163798 bytes, SHA-256 `bea26b0446b3709d8748dc043e7ec6aa17eda6d0df5cec3157f8003242f42683`
- `units.jsonl` — 23583 bytes, SHA-256 `d392ae51bc2722b9fafb6f4ade28e6f86c57e1b2810d12f4f028c68f7cbda9c3`
