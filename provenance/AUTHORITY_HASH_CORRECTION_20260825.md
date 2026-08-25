# Authority ZIP Hash Correction — 2026-08-25

Status: corrected metadata only; no mathematical, translation, source, reader,
or license bytes changed.

The terminal completion audit recomputed the frozen official source ZIP
directly and replayed every row of `authority/SOURCE_MANIFEST.csv`. The ZIP is
262,556 bytes and its actual 64-character SHA-256 is:

`0c667cfa7420b61dda8f8cb4ed9d619db8abbd1b53d17eafe7d4a2e153342e53`

Several late handoff/build-receipt records had accidentally omitted the second
`b` in `...db8abbd1...`, yielding the invalid 63-character string
`0c667cfa7420b61dda8f8cb4ed9d619db8abd1b53d17eafe7d4a2e153342e53`.
Those metadata occurrences were corrected. Earlier authority records and the
backend already contained the valid 64-character value.

Independent replay after correction proved:

- official source ZIP: 262,556 bytes, SHA-256 as above;
- official PDF: 2,336,387 bytes, SHA-256
  `f320b16af7448fbb43582c21569840fe657fccf6f31d97f176913fdd0e1eb823`;
- source manifest: 27 exact members / 897,169 expanded bytes / SHA-256
  `e222e326d8ff5fcd30b66b3b44642043295e1cb39920c58ff353eaafafd276d1`;
- `DIAGXY.TEX`: byte-identical under its embedded notice;
- `TABLE.TEX`, badge art, and uncleared quotations: absent from the tracked
  derivative and release payload;
- final 298-page PDF: unchanged at SHA-256
  `6d4bbf02959e5afb5fd34e1118f91f026c293b0056ec7a0ecdc5e95944df5d85`.

The correction is released as a new version in the existing publication
lineages. It does not overwrite or conceal the prior version. The first
correction version contained correct reader/archive bytes but its packaged
anonymous verifier overrejected the explanatory occurrence of the old value;
the `r2` successor fixes that verifier and preserves the working tool with the
same unchanged 298-page PDF.
