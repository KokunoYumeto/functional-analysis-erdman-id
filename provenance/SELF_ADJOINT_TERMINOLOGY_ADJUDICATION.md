# Whole-edition adjudication: *self-adjoint*

Date: 2026-08-23  
Decision: prefer **`swaadjoin`**; recognize `swadjoin` and `adjoin-diri`.

This is a bounded consistency correction made during the Chapter 12 admission
gate. It does not claim that the external terminology witness directly attests
either Indonesian compound for *self-adjoint*.

## Evidence and decision

The established reader first defines *self-adjoint* as `swaadjoin` in
`source/id-ID/linalg-id.tex` and repeats that form throughout the admitted
corpus: 29 occurrences before Chapter 11 (5 in Chapter 1, 20 in Chapter 5, 2
in Chapter 6, 1 in Chapter 7, and 1 in Chapter 8). The glossary record
`TERM-SELF-ADJOINT` cited Chapter 1 as its evidence but incorrectly stored
`swadjoin`, contradicting the very witness it named. The Chapter 11 and draft
Chapter 12 translations inherited that record and introduced 7 and 18
occurrences of the shorter spelling respectively.

The bounded Indonesian external check in
`qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md` found `operator adjoint` in
the official UNDIP article, but not an Indonesian compound for
*self-adjoint*. It therefore supports `adjoin` as a recognizable base and does
not choose between `swaadjoin` and `swadjoin`. On mathematical meaning and
whole-edition consistency, the source-defined and majority form `swaadjoin`
is controlling. `swadjoin` remains a search/interoperability variant rather
than reader prose.

## Applied scope

- `backend/terminology.jsonl`: `TERM-SELF-ADJOINT.preferred` is `swaadjoin`;
  variants are `swadjoin` and `adjoin-diri`.
- The 7 Chapter 11 and 18 Chapter 12 reader occurrences were normalized to
  `swaadjoin`, including their index entries.
- The Chapter 11 external-QA and terminology-decision records and the Chapter
  12 terminology plan were corrected so that they no longer misstate the
  earlier reader convention.
- Earlier chapters already used `swaadjoin` and required no prose change.
- Backend occurrence projections and artifact hashes are regenerated at the
  Chapter 12 reconciliation boundary; prior public Chapter 11 bytes remain an
  honest historical checkpoint.

No upstream contact occurred. The source author, component credits, human
direction, CC BY-SA 4.0 terms, and model provenance
`OpenAI Codex gpt-5.6-sol, Ultra` are unaffected.
