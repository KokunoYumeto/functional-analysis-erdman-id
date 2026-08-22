# FAOA-2015-CH08 classified source-to-target delta inventory

Date: 2026-08-22  
Scope: exact bounded comparison of `source/upstream/spectrum.tex`, active source
lines 1--603 through `\endinput`, and `source/id-ID/spectrum-id.tex`

## Frozen identities and active boundary

| Surface | Bytes | Lines/endings | SHA-256 |
|---|---:|---|---|
| Official source member | 25,716 | 611 CRLF | `ae68cf224c6218ecd501cc983428cf924a3c361c6324a6b40793b1e9ba44b4dd` |
| Active official source through `\endinput` | 25,698 | 603 logical lines | `2c4dea4be2cfb89eb507742b4052619c7cf09904d54921884f88be49b19ba05b` |
| Indonesian target | 26,947 | 603 LF | `1120da36ebd0793690ecb47b33b921c81376d1bf7d2f03d9821b79356dfd03bc` |
| Active target through `\endinput` | 26,946 | 603 logical lines | `596c74549f38600a8a96c251189f2c43d11980bc1df61b63dc7e9ccd82a745ae` |
| Cumulative Chapter 1--8 wrapper | 9,714 | 334 LF | `d0b4130b9fa6f85baef22f316ea914d5519bf30d6e82d8e6d824f2cf211c1998` |

All three files are BOM-free. The official member remains byte-identical to
authority. Its inactive suffix is exactly nine CRLF pairs (18 bytes, SHA-256
`2441ab53ba42405bf33990cd03799fe967666cb0d78de821577c7c876a9e4919`)
after the line-603 `\endinput` token. The target has only its terminal LF after
the corresponding token.

## Preserved topology and endpoint closure

- The two ordered sections and all 96 ordered environment pairs are preserved.
- Environment openings are 33 propositions, 14 examples, 14 proofs, ten
  enumerations, eight definitions, eight corollaries, four theorems, two
  exercises, two `bmatrix` environments, and one notation environment.
- The exact ordered endpoint surfaces retain 28 labels, 16 ordinary references,
  no equation references, no future references, and three citations.
- The exact ordered semantic hooks retain 73 index calls and 20 defined-term
  calls. Their translated arguments are locked independently from the source
  arguments, while all 73 MakeIndex operator shapes remain aligned.
- The ordered exercise/proof stream contains two exercises and 14 proofs:
  twelve proof hints, one proof comment, and one plain proof. The Volterra
  exercise retains its one inline hint.
- The source has 414 text-aware math surfaces: 399 inline-dollar and 15
  bracket-display surfaces. The target has 416: 401 inline-dollar and the same
  15 bracket displays.

## Exact sequence locks

Each value hashes the compact UTF-8 JSON serialization of the complete ordered
sequence named in the first column. These locks supplement the whole-file
identities and make drift attributable to a specific control surface.

| Sequence | SHA-256 |
|---|---|
| Environment topology, source and target | `7d217832d8b441446041532af74caf20c5e6d845fa00fe90661446b1ebd35942` |
| Source environment-opening shapes | `458f4910e0ecfdaafec03b97e5b35352f14f30b2cf504813fdaab6d2b7ae572c` |
| Target environment-opening shapes | `7d8e7a500e105a1345f3edf16aa9d1f1d9d8cc23850ba00704852878e14d82ed` |
| Labels | `71dbbacdf4eb2b677af586131a692bf7132a70180a169f334c56916b4938b52a` |
| Reference endpoints | `fc0e25bde96aae332891d08850d5e1e0bb43ad283d6c4d5c7f891f9141f03539` |
| Citations | `55f249e5229f4632822745345dc397259a08f9d23a8223f91c2bfd0e4e223e11` |
| Source index arguments | `235b8dcf5516d7b5f16cbbd53cd052602c5eb9cd640d7e7042ca8e863a860f5b` |
| Target index arguments | `26bdd910beb617890fcf686e2ed0b59a2c156b43435a23f1b362c60aa782a027` |
| Index operator shapes | `ff6654465870bdcc65274de183c2296532d682d6c8e5154f3050b0e070a0dcbf` |
| Source defined-term arguments | `15d207193adab175ea48fbdff7be5a2a9c27cbefd7423970063baac88b30854c` |
| Target defined-term arguments | `90d8b5078ee60646856c3df5a73f6174d47b7a9b3bf389213c96dd537f704cff` |
| Source proof openings | `3279057376cb78c3c97a3451c8faa6fa8c8f467a9b4fd24fe698078d8a1eb0d3` |
| Target proof openings | `e52c1460a55e4660fdd695832d58bff2cf6bbe10add13c53544e126a2e7ab192` |
| Proof-role stream | `fd88cb6369440d5a30f9d239980e6d4c38b367774197f30bfd42a7271e7e3c26` |
| Exercise/proof stream | `f338d8df11345524f2687c6b07893a1f77f0a979411835c38a281adbbc341f12` |
| Source math delimiter/key records | `3f7a97d5870b946f8724a47a1b4baad42c07e517edb9ac698c604953de07a324` |
| Target math delimiter/key records | `799ce89c673cc706533af74094e067423a0daaa641d05874d328fca3ac0d0b81` |
| Source math delimiters | `79d136b70b34e01f3b27f2bb97dbd563d9797681548e4d7cc648aec6ae369f3d` |
| Target math delimiters | `06db0da7abd427af582d5925213b5553b14ac1a7295f1bf0f31986951eb0a13f` |
| Cumulative-wrapper include order | `9c27175029f447770aee10a6fafe1b36adb1c47a5280c8f6d04a3e87bccf148c` |

## Complete math-edit classification

The text-aware sequence comparison has six edit blocks and no unclassified
block. SHA-256 values below hash the normalized math comparison keys, not the
surrounding prose.

| Edit | Source ordinal and surface | Target ordinal and surface | Key SHA-256, source to target | Classification |
|---|---|---|---|---|
| insert | -- | 64, `$A$` | -- to `559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd` | First half of a localization-only movement caused by Indonesian word order. |
| delete | 65, `$A$` | -- | `559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd` to -- | Second half of the same movement; the key is identical. |
| replace | 263, `$\rho(a^n) = \bigr(\rho(a)\bigr)^n$` | 263, `$\rho(a^n) = \bigl(\rho(a)\bigr)^n$` | `1e85269c7cb38a9b68c5065636e82e7cd91802198b3f58d78c82ba95347baf9e` to `fa12190e72acda477cd2b89e31ae73bf33a60772806f458db206df4ca49fb640` | Source correction 4: repair the mismatched scalable opening delimiter. |
| insert | -- | 280, `$Vf(x)=\int_0^x f(t)\,dt$` | -- to `39cfc53306fa41ef342a5ea7e7aeefa1dc418b211b2e42b17ede70b82d6d2c40` | Source correction 5 defines the operator on `C([0,1])`. |
| replace | 302, `$T$` | 303--304, `$H$`, `$T \in \ofml B(H)$` | `e632b7095b0bf32c260fa4c539e9fd7b852d0de454e9be26f24d0d6f91d069d3` to `44bd7ae60f478fae1061e11a7739f4b94d1daf917982d33b6fc8a01a63f89c21`, `eff40d5dd1f289f730e3fe14f1b2a76e0a574984395192cd41d8bfa9ae2285a0` | Source correction 6 binds the Hilbert space and operator before `T=S^*S`. |
| replace | 389, `$A = \cup_{k=1}^\infty a_k$` | 391, `$A = \{a_k\colon k\in\N\}$` | `a3fcee32896ef00e3d7c28198ff5f2a4b5091b1e95eca7b490d8bc9022c48961` to `451e6e653d28c123ad903a7c5e5e8e52d795a8487b1ea40ea13141291ca81bf2` | Source correction 8 defines the diagonal-entry set. |

Translation within a `\text{...}` or `\intertext{...}` payload is scrubbed from
the math comparison key while embedded math is retained. The complete delimiter
and key sequences are nevertheless locked by the digests above and by the
frozen file identities.

## Complete control-edit and prose-reflow classification

There is one environment-control shape edit. At environment-opening ordinal 84
(source and target line 509), the malformed source control
`\begin{thm}{Spectral Mapping Theorem}` has an immediate mandatory group. The
target uses the intended optional title
`\begin{thm}[Teorema Pemetaan Spektral]`. This is documented source correction
7. All other environment names, opening/closing order, and immediate argument
shapes are unchanged. Translated theorem, proposition, proof-hint, and
proof-comment option text is locked by the exact source and target sequence
digests.

Two final prose-only adjustments are ordinary Indonesian localization, not
source corrections and not mathematical or TeX-control edits:

1. Target line 399 naturally reorders the Volterra exercise opening as
   “pada ruang Banach ... definisikan operator integral melalui rumus”.
2. Target line 525 shortens “Jika `$T$` suatu operator invertibel” to the
   idiomatic “Jika `$T$` operator invertibel”.

The checker locks both exact prose anchors and requires zero active
`\allowbreak` calls in source and target.

## Eight documented source corrections

The Chapter 8 block of `provenance/SOURCE_CORRECTIONS.md` contains exactly eight
numbered adjudications and has SHA-256
`bb76200eee25a2a5e8305f7e62570ae4eab4a50c3785a11c78cdc4a4007c409c`.
The target anchors are:

1. Line 17 restores the missing boundary in `of~$a$)such` through natural
   Indonesian spacing.
2. Lines 178--180 restrict the reciprocal-spectrum equivalence to nonzero
   `\lambda`.
3. Line 348 removes the stray right parenthesis after reference `C073134`.
4. Line 372 changes the mismatched `\bigr(` to `\bigl(`.
5. Line 399 defines the Volterra operator on `C([0,1])` by
   `$Vf(x)=\int_0^x f(t)\,dt$`.
6. Line 443 binds Hilbert space `H` and `T \in \ofml B(H)` before using
   `T=S^*S`.
7. Line 509 makes *Teorema Pemetaan Spektral* an optional theorem title.
8. Line 547 replaces an invalid union of scalars by
   `$A=\{a_k\colon k\in\N\}$`.

The checker rejects regression to every documented source defect and requires
the exact correction-ledger block. No upstream contact occurs during
production.

## Terminology, residue, and rights closure

The target locks the 20 ordered `\df` surfaces and controlled terminology for
invertibility, unital algebras, spectra and resolvents, approximate point,
compression and residual spectra, self-adjoint operators, similarity, the
Volterra operator, unilateral shifts, and multiplication operators. It rejects
the enumerated English or inconsistent variants. Both the shared broad residue
scan and the Chapter 8 spectral vocabulary scan return zero active English
findings. Mojibake markers and active local/private paths are absent.

The cumulative wrapper locks the exact eight-member include order through
`\include{spectrum-id}`. It carries John M. Erdman's CC BY-SA 4.0 attribution,
the Indonesian derivative license, modification notice, and non-endorsement
statement. It uses unchanged `DIAGXY.TEX` and does not activate `TABLE.TEX` or
license-badge artwork.

Machine authority for this inventory is `qa/check_ch08_translation.py`. A pass
requires the exact source, active-source boundary, target, cumulative wrapper,
correction-ledger block, ordered control sequences, complete math record
sequences and classified edit blocks, terminology, residue, and rights closure
described above.
