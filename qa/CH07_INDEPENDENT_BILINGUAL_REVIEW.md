# FAOA-2015-CH07 independent bilingual rereview

Date: 2026-08-22  
Decision: **pass after two minor consistency fixes**

An independent review context read the complete 517-line official source and
the complete 517-line Indonesian target, rather than sampling the chapter or
relying on the structural checker. The final reviewed identities are:

- source `source/upstream/compact_operators.tex`: 21,755 bytes / 517 CRLF
  lines / SHA-256
  `a1f55b061f526f3e536e5a812f073781777b6f990b662f4a1dba07475152d663`;
- target `source/id-ID/compact_operators-id.tex`: 22,735 bytes / 517 LF lines /
  SHA-256
  `8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a`.

The rereview checked all 72 environment pairs, 309 mathematical spans, 20
labels, 13 reference endpoints, eight citation calls, 91 index hooks, 26
defined-term hooks, seven hint proofs, two citation-only proofs, and the single
exercise in source order. It separately confirmed the exact pending mappings
`00152171` to 12.3.16, `00152181` to 12.3.17, and `X_sqroot_op` to 11.5.7.

Two low-severity findings were accepted before the final target was frozen:

1. normalize every reader, index, and defined-term surface to the controlled
   TeX spelling `Hilbert--Schmidt`, matching the section title and terminology
   record;
2. translate both occurrences of “measure space” consistently as `ruang ukur`,
   replacing the isolated `ruang ukuran` in the exercise.

After those fixes, the rereview found no remaining mathematical, semantic,
quantifier, negation, reference, citation, exercise, hint, or Indonesian prose
defect. It confirmed that both duplicated proposition environments remain,
all eleven accepted source corrections are correctly applied, and the opening
reference to Chapter 5 is intentional. The final locked machine replay is
`qa/check_ch07_translation.py`; its classified mathematical delta inventory is
`qa/CH07_CLASSIFIED_DELTA_INVENTORY.md`.
