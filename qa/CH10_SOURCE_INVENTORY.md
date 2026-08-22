# FAOA-2015-CH10 source inventory

Date: 2026-08-22  
State: **source frozen; terminology QA passed; complete translation admitted**
Unit: `FAOA-2015-CH10` / advanced continuation

## Exact source identity

- Path: `source/upstream/distributions.tex`.
- Upstream title: `DISTRIBUTIONS`.
- Controlled Indonesian title: `Distribusi`.
- Identity: 42,703 bytes / 894 CRLF-terminated physical records / ASCII / SHA-256
  `31f38daee49b9abfcd513a1c4a3f78414b122e469c6ac2d559c0b73ecbc082f8`.
- `\endinput` is physical line 894 and is terminated by the final CRLF; no
  source content follows it.
- This inventory does not modify, normalize, or silently repair the source.

The six source sections, in exact order, are:

1. `Inductive Limits` → `Limit Induktif` (lines 3--94);
2. `$LF$-spaces` → `Ruang-$LF$` (lines 95--190);
3. `Distributions` → `Distribusi` (lines 191--481);
4. `Convolution` → `Konvolusi` (lines 482--710);
5. `Distributional Solutions to Ordinary Differential Equations` →
   `Solusi Distribusional untuk Persamaan Diferensial Biasa` (lines 711--796);
6. `The Fourier Transform` → `Transformasi Fourier` (lines 797--894).

The ordered section-title digest, using compact UTF-8 JSON as in the Chapter 9
checker, is
`1f3abf10a9c69fcf38c0a7d578ec08611ef1df91418925410d374a2609f57566`.

## Locked structural and mathematical census

The Chapter 9 parser conventions give 125 balanced environment pairs. Begin
counts are: 31 `prop`, 25 `exam`, 19 `defn`, 18 `proof`, 11 `exer`, five
`equation`, four each of `array`, `enumerate`, and `notn`, and one each of
`cases`, `cau`, `rem`, and `thm`. The ordered begin/end topology SHA-256 is
`817980afcdd19bb25d0aa0385492d82459fb2ede5f888637540ae44e6c88422c`;
the begin-control-shape SHA-256 is
`d6f7c0a239a8376f65e7bac83d9d0cfb17e7ee128659aabd2d95b4d9d7064d0b`.

- Mathematical surfaces: 651 = 603 dollar-inline + 43 bracket-display + five
  `equation` environments. Ordered delimiter/math-key SHA-256:
  `c21e165b00044ae77c380422735550d2aa27fea0cd7098d6a261948009c90d10`.
- Labels: 18; ordered SHA-256
  `2a369eab5a3a169348344d7d9f222ea86ea5f23c0e844d234d7260ebd2725b84`.
- References: 20 = 13 `\ref` + seven `\eqref`; 15 resolve inside Chapter 10
  and five target earlier chapters. Ordered `(kind,key)` SHA-256:
  `cb8c2af05153f043e57b25e16bc462fec1fc778331926d64edd325a872477bae`.
  The earlier-chapter keys are `C015544`, `X_dir_sum_VEC`, `C021421`,
  `prop_quotient_top_strong`, and `mi_notn`.
- Citations: 29 calls over ten keys; ordered SHA-256
  `5c57f39e712f21a1c83d07fb1ae69728ee5dd970786a5936885af95013c1ad83`.
- Index hooks: 101 calls / 99 distinct arguments; ordered SHA-256
  `0d98fb5d935ac729e0ee1d69564037f26c2796c9340b9e73ecf1dcb960c10bb0`;
  MakeIndex-operator-shape SHA-256
  `e2f4f780d13dcb42328334d3d496fa777dd5466581064fd4e0da61c97db36b3d`.
- Defined-term calls: 35 / 32 distinct arguments; ordered SHA-256
  `4c6e7b7c4f05d692721ea22f3c580568817fb45837720255f5579915bed6e2bc`.
- Explicit list items: nine.

There are 11 explicit exercises. Five contain inline `\emph{Hint.}` blocks
(source lines 383, 425, 432, 441, and 670); none contains an upstream answer or
solution. The 18 proof environments comprise three explicit `Hint for proof`
blocks (lines 60, 299, and 764) and 15 citation-only proof pointers; there is
no complete plain proof environment. The ordered proof/exercise role digest is
969 UTF-8 bytes / SHA-256
`b688a5ca889ad50a8c5d96dae490ed8c3ac9840cdbfd4c6c42ec470454f2d5cd`.
Translation must keep each hint, citation-only proof, exercise, and absent-
solution state distinct.

## Includes, assets, and build-facing macros

The chapter has zero `\input`, `\include`, `\includegraphics`, or `\epsfbox`
calls and no external image file. It contains one inline Xy-pic diagram,
`\xymatrix@+15pt@C+25pt`, at lines 37--43. The diagram must remain structurally
equivalent and needs a semantic text description in the accessible reader.
The source relies on the frozen book-master macro vocabulary, notably `\cat`,
`\vc`, `\bs`, `\sfml`, `\fml`, `\df`, `\sto`, `\underrightarrow`, `\locint`,
`\wt`, `\sbsb`, `\open`, `\lfs`, `\supp`, and `\wh`, plus the established
Xy-pic/`DIAGXY.TEX` dependency. There is no new component asset to license.

## Rights and citation hazards

The file inherits the frozen edition's CC BY-SA 4.0 substantive-work boundary;
it contains no separate component notice. Attribution, license link, change
notice, ShareAlike, and non-endorsement remain mandatory. No epigraph or
external long quotation occurs. The Treves warning at lines 162--165 is
authorial paraphrase, not a quoted extract.

The 15 citation-only proofs are pointers, not imported proof text. They must be
translated as pointers without silently supplying material from the cited
books. Citation keys and call counts are: `Rudin:1991` 12, `Treves:1967` four,
`HewittS:1965` three, `Conway:1990` two, `Grubb:2009` two, `Yosida:1965` two,
and one each of `Cerda:2010`, `HirschL:1999`, `Horvath:1966`, and
`McDonaldW:1999`. The Yosida locator at line 412 ends with an unspecified
“Theorem” and should be preserved but flagged, not guessed. No upstream contact
is authorized during production.

## Source-review candidates

These candidates were adjudicated during translation and are now applied. The
authoritative 16-record disposition is
`provenance/SOURCE_CORRECTIONS_CH10.json`:

- line 29: the universal property quantifies `i \in \N`, although the index set
  is the arbitrary directed set `D`; likely `i \in D`;
- line 54: “inductive limit if this system” likely means “of this system”;
- lines 57--73: the proposed `\prod V_i/\bigoplus V_i` construction appears too
  large for the categorical direct limit and its “eventually equal” argument is
  not valid for a general directed set; requires independent mathematical
  adjudication before any repair;
- line 98: “we will interested” lacks “be”;
- line 119: the topology-restriction statement is malformed and must state
  directly that the topology on `X_i` is the restriction of `\sfml T_{i+1}`;
- line 121: `\phi{ji}` likely intends `\phi_{ji}`;
- lines 252--255: Lebesgue-local integrability of `f` does not by itself ensure
  local integrability against an arbitrary regular Borel measure `\mu`, and
  the notation `L_\mu` suppresses the stated factor `f`; requires adjudication;
- line 341: “every test functions” should be singular;
- line 393: “generated the family” likely lacks “by”;
- line 405: `\left<...\right>` should be reviewed against semantic
  `\langle...\rangle` notation;
- line 456: `fu` is a functional, not a function, before the proposition proves
  that it is a distribution;
- lines 509 and 766: `\int_R` likely intends `\int_\R`;
- line 559: the convolution theorem is followed by `\wh{fg}=\hat f\hat g`;
  the left side likely intends the transform of `f\ast g`;
- line 566: a general scalar-valued function is typed `\R\to\R`, although the
  chapter otherwise allows scalar field `\K`; requires type adjudication;
- line 778: `d^P\delta/dx^p` has an uppercase `P` in the numerator.

## Controlled Indonesian terminology gate — passed

The frozen Chapter 1--9 terminology witness is `backend/terminology.jsonl`,
98,578 bytes / 255 records / SHA-256
`98d69653ba962b1f88f84e9de28e13b9fa1c8f3fcbfbdc319e89b182f68a2144`.
The additive Indonesian field-usage projection is
`backend/terminology_qa.jsonl`, 9,232 bytes / seven records / SHA-256
`0be61180b43ca8e314bc3323696a0836ed82f505153444373584d1ac640cc3c8`.
The full backend validator passes 16 JSONL files / 14,556 records / 1,423
index rows / 15,979 globally unique IDs / 9,428 checked relation endpoints;
the 31-row manifest SHA-256 is
`13b5cd1f5e5cfb59717bfd74e42048095bcfba95fcfb4981dfa2717c2da3621d`.
Inherited forms include `himpunan terarah`, `topologi lemah`,
`topologi-$w^*$`, `ruang konveks lokal`, `ruang Fr\'echet`, `fungsi uji`,
`multi-indeks`, `ruang Schwartz`, `terukur`, `tumpuan`, and `adjoin`.

New Chapter 10 preferences frozen for production are: `sistem
terarah`, `morfisme penghubung`, `limit induktif`, `limit langsung`, `topologi
kuat`, `barisan induktif ketat`, `limit induktif ketat`, `topologi limit
induktif`, `ruang-$LF$`, `terintegralkan secara lokal`, `distribusi`,
`distribusi regular`, `distribusi singular`, `ukuran Dirac`, `distribusi delta
Dirac`, `fungsi Heaviside`, `distribusi Heaviside`, `turunan distribusi`,
`operator diferensial`, `dipol`, `ukuran Lebesgue ternormalisasi`, `konvolusi`,
`transformasi Fourier`, `adjoin formal`, `solusi klasik`, `solusi lemah`,
`solusi distribusional`, `solusi diperumum`, and `distribusi tempered`.

The Chapter 10-specific form **`distribusi tempered`** is directly attested in
the official ITB Digital Library chapter PDF *Bab II: Ruang dan Operator LPS*,
section II.1.3, both as the section heading and in the defining prose. The
10-page PDF is frozen locally at
`qa/terminology_evidence/itb-distribusi-tempered-2018-bab2.pdf`, 283,518 bytes,
SHA-256
`830a241c8ace73290a4c613cc6478bb17698d835b781b1fec332fa09838ddf02`.
Page 2 was inspected visually and by text extraction. This evidence refines
the provisional calque `distribusi temper`; no admitted Chapter 1--9 prose is
affected. The upstream alternate *temperate distributions* remains the
recognition form `distribusi temperate` where the source explicitly presents
it as an alternative.

Adverbial *weakly* follows the established `secara lemah` pattern. Therefore
the controlled preference is **`terukur secara lemah`** for *weakly
measurable*. The witnessed shorter variant **`terukur lemah`** remains a
recognized variant, not the preferred reader form. Neither phrase occurs in
this Chapter 10 source; the record is reserved for cross-corpus consistency.
Attributive compounds remain `topologi lemah` and `solusi lemah`.

## Contiguous production fragments and admission

| Fragment | Inclusive source lines | Bytes | SHA-256 | Scope |
|---|---:|---:|---|---|
| CH10-F01 | 1--94 | 5,150 | `6cb7e8c7a4382345eaf5cac803b841cd883c326160284ef395649517515ce519` | title + inductive limits |
| CH10-F02 | 95--190 | 4,130 | `54f124c5596ecccf0bec86d33215d154e5c0633fda7006dece2c3552a5cbae70` | `$LF$`-spaces |
| CH10-F03 | 191--386 | 10,899 | `013a8b49f725ec140cb09dd09a9bdaa02bab0cd1848012347ee043f24f9fa86b` | distributions through the dipole exercise |
| CH10-F04 | 387--481 | 4,644 | `9ac3bd5059414d3ce1a24db50bf9b9a6d2e63cb3980dc28b210b0cc69ae7f399` | weak/weak-star topology, convergence, multiplication |
| CH10-F05 | 482--710 | 9,805 | `032590cb0067b40c948d952a6dcac7cef8ca8b1254b5d006ae825d67fb9d4cd8` | convolution |
| CH10-F06 | 711--796 | 3,749 | `cac89f13c29d536a966c9b6684bf7e273d296e6d00547e176bc00da75cea8769` | distributional ODE solutions |
| CH10-F07 | 797--894 | 4,326 | `f4036be8ec3face8cf220ba3bb6de88164e365863471aa31cb9cb767f6e2d5eb` | Fourier transform + `\endinput` |

The source fragments are byte-exact, nonoverlapping, exhaustive, and ordered;
their bytes sum to 42,703. All seven corresponding Indonesian target fragments
were translated, independently reread, and assembled into the admitted
42,627-byte target. Structural, mathematical, terminology, build, all-page
visual, rights, privacy, and backend gates pass in
`provenance/CH10_BUILD_AND_QA_RECEIPT.md`. The next executable source-order
boundary is Chapter 11, `source/upstream/Gelfand_Naimark.tex`.
