# Chapter 12 terminology plan

Date: 2026-08-23  
Unit: `FAOA-2015-CH12` / `source/upstream/no_identity.tex`  
State: terminology plan only; no translation, backend, metadata, credit, or
publication change is authorized by this file.

## Scope and witnesses

This plan covers the complete 1,158-line Chapter 12 upstream source. It uses
only the already-local admitted Indonesian chapters, glossary/backend records,
and Chapter 11 terminology QA evidence. No new external search was performed.

| Witness | Bytes / lines | SHA-256 | Use |
|---|---:|---|---|
| `source/upstream/no_identity.tex` | 47,994 / 1,158 | `8da3ffa45bcc07cbe1897a09f309db51e1c5c38080459ffb1f6947bf45a20b6c` | complete Chapter 12 source and occurrence census |
| `backend/terminology.jsonl` | 122,910 / 300 | `814e7aba8c685f9678871223b80625c471c32748d669dd28af6c5b686bbe5671` | admitted preferred terms and scopes |
| `backend/terminology_qa.jsonl` | 9,232 / 7 | `0be61180b43ca8e314bc3323696a0836ed82f505153444373584d1ac640cc3c8` | accepted recognition-variant policy |
| `provenance/CH11_TERMINOLOGY_DECISIONS.md` | 7,558 / 144 | `95255750208191727b8a8b4341b8acf6be88b6ddb5cf34f18fb9add84ba6e678` | immediately preceding chapter decisions |
| `qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md` | 7,948 / 131 | `78195240227ca257ff9f0b5d5132e4afe0e20d46a166fad471305246818d9451` | already-local external terminology QA and its limits |
| `source/id-ID/categories-id.tex` | 29,254 / 570 | `39c4a0b345c49fc7a925331497dca37f5b7b296d77717ef1c97322dfeb96e2dd` | admitted order-language witness |
| `source/id-ID/normlinspaces-id.tex` | 94,040 / 1,913 | `c44f20890d5fb6b7445f0b2eeca8f477cc970d147d5c54aa4bc5df709f6b1f9d` | admitted nets/directed-sets witness |
| `source/id-ID/Banach_spaces-id.tex` | 82,940 / 1,569 | `ca32547e4b47af3444d454476beac71ad8870e88b436dc008e1cb5dbb6755e9c` | admitted exact-sequence witness |
| `source/id-ID/compact_operators-id.tex` | 22,735 / 517 | `8e68cf72e711ac95569883cf64a8f1f6a89ee43a1f85f5319fec6cb54b4f787a` | admitted cone/proper-cone witness |
| `source/id-ID/Hilbert_spaces-id.tex` | 62,947 / 1,351 | `b8e728e1f26a66ec2a420373e6104e3db4e5c954d7001acda1c13eb348322215` | admitted `unitalisasi` and direct-sum witness |

The Chapter 11 external QA directly supports only a narrower Indonesian
functional-analysis core (for example, `ruang Banach`, `ruang dual`, `norma
operator`, `operator kompak`, and weak-convergence forms). It does not attest
the specialized Chapter 12 vocabulary below. Those specialized decisions are
therefore based on mathematical meaning and edition-internal consistency, not
misrepresented as external field-frequency evidence.

Exact model-provenance wording and all author, component, source-maintainer,
human-direction, and maintenance credits must remain untouched at this
planning stage.

## Recommended titles

| Exact source title and location | Preferred id-ID title | Recognition alternatives / note |
|---|---|---|
| `SURVIVAL WITHOUT IDENTITY` (line 1) | `BERTAHAN TANPA IDENTITAS` | Retains the source's playful metaphor without making `survival` a technical term. `KELANGSUNGAN TANPA IDENTITAS` is recognizable but too abstract. |
| `Unitization of Banach Algebras` (line 3) | `Unitalisasi Aljabar Banach` | `Penambahan identitas pada aljabar Banach` may be recognized as an explanatory paraphrase. |
| `Exact Sequences and Extensions` (line 198) | `Barisan Eksak dan Ekstensi` | `Ekstensi` is structural algebra terminology here; it is not the glossary's functional-extension sense. |
| `Unitization of $C^*$-algebras` (line 392) | `Unitalisasi Aljabar-$C^*$` | Preserve the edition's TeX form for `$C^*$`. |
| `Quasi-inverses` (line 658) | `Kuasi-Invers` | Recognize `invers kuasi`; avoid `invers semu`, which can suggest a generalized inverse. |
| `Positive Elements in $C^*$-algebras` (line 767) | `Elemen Positif dalam Aljabar-$C^*$` | Recognize `unsur positif`; retain `elemen` edition-wide. |
| `Approximate Identities` (line 1022) | `Identitas Aproksimatif` | Recognize `identitas hampiran`; the source itself separately gives `approximate unit` as a synonym. |

## Evidence keys

- **G** — exact admitted glossary/backend record: `backend/terminology.jsonl`.
- **A2** — admitted Chapter 2: `praurutan` and `urutan parsial` at
  `source/id-ID/categories-id.tex:111-125` (also backend index occurrences at
  `backend/index_terms.csv:206,209`).
- **A3** — admitted Chapter 3: `himpunan terarah` and `jaring` at
  `source/id-ID/normlinspaces-id.tex:1381-1402`.
- **A4** — admitted Chapter 4: the construction noun `unitalisasi` at
  `source/id-ID/Hilbert_spaces-id.tex:941-944`; admitted direct-sum uses at
  lines 124-125, 274-294, 1,138-1,151, and 1,217-1,222.
- **A6** — admitted Chapter 6 exact-sequence definition at
  `source/id-ID/Banach_spaces-id.tex:713-730`.
- **A7** — admitted Chapter 7 cone definition at
  `source/id-ID/compact_operators-id.tex:425-437`.
- **C11** — admitted Chapter 11 terminology decisions/backend records for
  `karakter`, `transformasi Gelfand`, `kalkulus fungsional`, `teorema spektral
  abstrak`, `kontraktif`, and the `$C^*$`/`$*$` compounds.
- **Q11** — already-local Chapter 11 external QA. It supports reuse of the
  edition's core forms and recognition-variant discipline, but not a new
  Chapter 12 specialized usage claim.
- **N12** — new Chapter 12 candidate. It is a proposed controlled form, not an
  already-admitted backend record.

## Inherited controlled terms

The locator column gives every line containing the exact English phrase
(case-insensitive) when the count is modest. For very common compounds it gives
the exact definition/theorem locations and a complete count, so a translator
can reproduce the census without mistaking index entries for new concepts.

| Source phrase | Preferred id-ID | Variants to recognize | Consistency evidence | Exact Chapter 12 occurrence/location |
|---|---|---|---|---|
| Banach algebra | aljabar Banach | — | G: `TERM-BANACH-ALGEBRA`; Q11 | 29 lines: 3, 54-56, 58, 63, 66, 70, 73, 128, 131, 134, 138, 145, 148, 156, 163, 175, 207, 237, 517, 574, 681, 685, 689, 694, 698, 710, 722 |
| unital | beridentitas | unital | G: `TERM-UNITAL` at glossary line 130 | 36 lines: 14, 17, 62, 113, 171, 179, 334, 420, 426, 428, 440, 461, 482, 494, 518, 564, 570, 608, 621, 670, 694, 722, 736-737, 741, 843, 957, 961, 965, 971, 976, 1,133, 1,136, 1,142, 1,146, 1,151 |
| nonunital | tak beridentitas | nonunital; tanpa identitas | inverse of admitted `beridentitas`; N12 wording | lines 40-41 |
| `$C^*$-algebra | aljabar-$C^*$ | aljabar C-star (search only) | G: `TERM-CSTAR-ALGEBRA` at glossary line 189; C11 | 122 source lines; first definition-bearing occurrences 117, 200-204, 209-226; section title 392; positive-elements title/definition 767-780; approximate-identity definition 1,022-1,038 |
| `$*\,$-homomorphism` | homomorfisme-$*\,$ | homomorfisme bintang (search only) | G: `TERM-STAR-HOMOMORPHISM` at glossary line 129; C11 | 24 lines: 209, 218, 225, 230, 235, 272, 280, 285, 334, 353, 361, 398, 480, 551, 569-570, 576, 580, 583, 637, 935, 1,090-1,092 |
| ideal / left ideal / right ideal | ideal / ideal kiri / ideal kanan | — | G: `TERM-IDEAL` lines 142-144 | 50 lines contain `ideal(s)`; modular definitions are exactly lines 84-101; `$C^*$` convention is lines 253-267; approximate-identity consequences are lines 1,072-1,130 |
| spectrum | spektrum | — | G: `TERM-SPECTRUM` at glossary line 209 | lines 41-42, 62, 66, 70, 515, 541-542, 729-731, 941 |
| spectral radius / Spectral radius formula | radius spektral / Rumus Radius Spektral | jari-jari spektral; formula radius spektral | G: `TERM-SPECTRAL-RADIUS` at glossary line 214 | theorem title and only exact phrase: line 77; symbol/results at lines 73-81 |
| exact at / exact | eksak di / eksak | — | G: `TERM-EXACT-AT`, `TERM-EXACT` at glossary lines 166-167; A6 | exact phrase `exact at`: lines 216-217; exact-sequence block: 209-232 |
| short exact sequence | barisan eksak pendek | barisan eksak singkat | G: `TERM-SHORT-EXACT-SEQUENCE` at glossary line 168; A6 | lines 223-224; later diagrams/usages at 240-251, 316-327, 356-372, 1,085-1,087, 1,120-1,122 |
| direct sum | jumlah langsung | — | G: `TERM-DIRECT-SUM` at glossary line 4; A4 | lines 302-306, 315, 325-327, 330, 333-334, 360, 427 |
| self-adjoint | swaadjoin | swadjoin; adjoin-diri; `adjoint`/`operator pendamping` as search variants only | G: `TERM-SELF-ADJOINT` at glossary line 15; Q11 and the whole-edition adjudication accept recognition variants | 18 lines: 254, 259, 263, 540-542, 546, 768, 843, 869, 874, 876, 906, 919, 940, 945, 949, 1,073 |
| positive | positif | — | G: `TERM-POSITIVE` at glossary line 137; A7 | 33 lines: 767, 769-777, 823, 826-830, 839, 850, 854-855, 858, 865-866, 872-875, 897, 909, 930, 932, 965-966, 1,030 |
| cone | kerucut | — | G: `TERM-CONE` at glossary line 200; A7 | Chapter 12 definition/use block lines 772-840 and line 850 |
| proper (a cone) | proper | `sejati` only outside this cone-specific scope | G: cone-specific `TERM-PROPER-CONE` at glossary line 201; A7 lines 425-437 | cone sense lines 813-815, 825, 833, 838, 850; unrelated `proper ideal` sense lines 128, 134 |
| compatible | kompatibel | selaras | G: `TERM-COMPATIBLE` at glossary line 233 | lines 794, 802, 835 |
| directed set | himpunan terarah | — | G: `TERM-DIRECTED-SET` at glossary line 47; A3 | line 1,049; the defining set is displayed at 1,046-1,050 |
| net | jaring | barisan tergeneralisasi | G: `TERM-NET` at glossary line 46; A3 | lines 1,029, 1,032, 1,036 |
| character | karakter | —; never `fungsi karakteristik` | G: `TERM-CHARACTER` at glossary line 284; C11 | lines 140, 145, 150, 153, 156, 158-160, 175, 550, 559 |
| Gelfand transform | transformasi Gelfand | —; never transformasi Fourier | G: `TERM-GELFAND-TRANSFORM` at glossary line 292; C11 | lines 176, 530, 547, 551, 563 |
| contractive | kontraktif | — | C11 | lines 145, 178, 577, 580 |
| functional calculus / abstract spectral theorem | kalkulus fungsional / teorema spektral abstrak | — | C11 | line 865 / line 864 |

## New or scope-specialized Chapter 12 terms

These are proposed controlled forms. They should receive stable backend IDs
only during an authorized Chapter 12 admission/reconciliation, after the
translation has preserved the source distinctions.

| Source phrase | Preferred id-ID | Variants to recognize | Evidence | Exact Chapter 12 occurrence/location |
|---|---|---|---|---|
| unitization | unitalisasi | unitalization; penambahan identitas | A4; N12 | 26 lines: 3, 5, 22-23, 47, 51-52, 57-58, 148, 150, 158-159, 199, 202, 392-393, 396, 435, 511-512, 567, 608, 616, 742, 1,125 |
| modular left ideal | ideal kiri modular | ideal kiri bermodul (search only) | inherited `ideal kiri` + N12 | definition line 87 |
| right identity with respect to `J` | identitas kanan terhadap `J` | identitas kanan relatif terhadap `J` | inherited `identitas` + N12 | definition line 90; proof reuse lines 107-109 |
| modular right ideal | ideal kanan modular | ideal kanan bermodul (search only) | inherited `ideal kanan` + N12 | definition line 93 |
| left identity with respect to `J` | identitas kiri terhadap `J` | identitas kiri relatif terhadap `J` | inherited `identitas` + N12 | definition line 96; proof reuse line 108 |
| modular ideal | ideal modular | ideal bermodul (search only) | inherited `ideal` + N12 | 9 lines: 99, 117, 128, 131, 134-135, 139-140, 682 |
| split exact | eksak terbelah | eksak terbagi; barisan eksak terbelah | A6 lexical base + N12 | lines 228-230, 426, 454, 504 |
| extension (of `$C^*$`-algebras) | ekstensi | perluasan; extension (search only) | N12, structural scope | heading line 198; structural uses lines 204, 242-251, 325-327, 338-372, 427 |
| algebraic ideal | ideal aljabar | ideal aljabarik | inherited `ideal` + N12 | definition lines 260-263; later exact phrase at line 1,072 |
| algebraic `$*$`-ideal | ideal-$*$ aljabar | ideal aljabar-$*$; ideal aljabarik-$*$ | inherited `ideal-$*$` + N12 | definition lines 263-266 |
| (external) direct sum | jumlah langsung (eksternal) | jumlah langsung luar | G `TERM-DIRECT-SUM`; A4; N12 qualifier | definition lines 301-313 (exact phrase line 306) |
| direct sum extension | ekstensi jumlah langsung | ekstensi berbentuk jumlah langsung | structural `ekstensi` + G direct sum | lines 325-327, 360, 427 |
| strongly equivalent | ekuivalen kuat | setara kuat | N12 | lines 338-350, 360, 372 |
| left multiplication by `$a$` / left multiplication operator | perkalian kiri oleh `$a$` / operator perkalian kiri | pengalian kiri (search only) | edition `operator`; N12 | lines 409-417 and recall at 469-470 |
| one-point compactification | kompaktifikasi satu titik | kompaktifikasi satu-titik | admitted `kompaktifikasi` at A4 + N12 | lines 167, 588, 604, 610, 617 |
| left quasi-inverse | kuasi-invers kiri | invers kuasi kiri | N12 | lines 659, 666, 704 |
| right quasi-inverse | kuasi-invers kanan | invers kuasi kanan | N12 | lines 660-661 |
| quasi-inverse | kuasi-invers | invers kuasi; avoid `invers semu` | N12 | heading/definition/use lines 658-663, 666-667, 704 |
| quasi-invertible | kuasi-invertibel | dapat dikuasi-inverskan | morphology consistent with `kuasinilpoten`; N12 | lines 681, 709-710 |
| q-spectrum | spektrum-q | spektrum q | inherited `spektrum` + N12 | index/definition lines 729-733 |
| positive cone | kerucut positif | konus positif (search only) | G positive + G cone + A7 | lines 772, 774-777, 823, 826-828, 839, 850 |
| preordering | praurutan | praorder; preorder (search only) | A2 exact admitted form | lines 785-787 |
| partial ordering | urutan parsial | pengurutan parsial | A2 exact admitted form | lines 777, 783, 790, 792, 802, 834, 836-839 |
| respects the operations | menghormati operasi-operasi | selaras dengan operasi-operasi | N12; paired with admitted `kompatibel` | lines 793-800 (exact verb lines 795-796) |
| ordered vector space | ruang vektor terurut | ruang vektor berurutan | A2 order morphology + N12 | lines 802-806, 822-830, 839 |
| positive `$n^{\text{th}}$` root | akar pangkat `$n$` positif | akar ke-`$n$` positif | inherited `positif` + N12 | proposition lines 858-860 |
| Jordan decomposition | dekomposisi Jordan | penguraian Jordan | C11 theorem-name policy + N12 | theorem lines 869-878; reuse lines 906-910 |
| positive part / negative part | bagian positif / bagian negatif | komponen positif / komponen negatif | inherited `positif` + N12 | index lines 873-876; defining equation line 877; reuse 907-910, 919-920 |
| absolute value (in a `$C^*$`-algebra) | nilai mutlak | harga mutlak (search only) | N12 | definition/index lines 913-917; reuse lines 919-932 and 976-979 |
| approximate identity | identitas aproksimatif | identitas hampiran | morphology from admitted `spektrum titik aproksimatif`; N12 | definition lines 1,023-1,038; examples/results lines 1,040-1,043, 1,062-1,070 |
| approximate unit | unit aproksimatif | unit hampiran | source-declared synonym; N12 | definition synonym lines 1,026-1,030 only |
| increasing net | jaring menaik | jaring meningkat | G `TERM-NET`; A3 | definition lines 1,029-1,032 |
| sequential approximate identity | identitas aproksimatif sekuensial | barisan identitas aproksimatif | N12 | definition lines 1,032-1,037; existence line 1,069 |
| order isomorphism | isomorfisme urutan | isomorfisme orde | admitted `urutan parsial`; G `TERM-ISOMORPHISM`; N12 | lines 1,054-1,058 |
| hereditary (`$C^*$`-subalgebra/ideal) | herediter | turun-temurun (explanatory recognition only) | N12 | definition lines 1,094-1,097; ideal result lines 1,106-1,108 |
| inverse closed | tertutup terhadap invers | tertutup-invers | inherited `invers`; N12 | explanatory definition lines 1,133-1,140; proposition lines 1,142-1,144 |

## Ambiguous contexts and mandatory safeguards

1. **`extension` has two senses.** At lines 157-160 and 569-571 it means
   extending a character or homomorphism and should use `perpanjangan` /
   `memperpanjang`, consistent with glossary record `TERM-FUNCTIONAL-EXTENSION`
   (`backend/terminology.jsonl:52`). At lines 198-251, 325-372, and 427 it is a
   short-exact-sequence object and should use `ekstensi`. The generic glossary
   record's rejection of `perluasan` is scoped to extensions of functionals; it
   must not force `perpanjangan` onto the algebraic object.

2. **The orientation of an algebra extension is intentionally unsettled.**
   Lines 243-251 report incompatible author conventions for “extension of A by
   B” versus “of B by A.” Translate those phrases compositionally as `ekstensi
   A oleh B` and `ekstensi B oleh A`; do not silently choose a preferred
   orientation or rewrite the ordered triple/sequence/algebra distinction.

3. **`identity`, `unit`, and `unitization` are related, not interchangeable.**
   Use `identitas` for a multiplicative identity, `unit` only where the source
   explicitly supplies `approximate unit`, and `unitalisasi` for the
   construction. Preserve the source convention that even an already unital
   algebra receives a newly adjoined identity (lines 435-457 and 604-611).

4. **Two unitizations and two notations occur.** Banach-algebra unitization is
   denoted `$A_e$` at lines 46-60; `$C^*$`-algebra unitization is denoted
   `$\widetilde A$` at lines 420-513. Keep `$A\bowtie\mathbb C$`, `$A_e$`,
   `$A^\sharp$`, and `$\widetilde A$` distinct and unchanged.

5. **`proper` is scope-dependent.** For a proper cone (lines 813-850), use the
   admitted cone-specific `proper` (`TERM-PROPER-CONE`, glossary line 201), not
   generic `sejati` (`TERM-PROPER`, line 145) and not rejected `wajar`. For a
   proper ideal at lines 128 and 134, `ideal sejati` is appropriate.

6. **`order` is not globally `orde`.** The glossary's `TERM-ORDER` = `orde` is
   scoped to earlier topological-vector-space usage, while the admitted
   foundational relation is `urutan parsial`/`praurutan` (A2). In lines
   777-840 and 1,049-1,058 use the `urut` family: `urutan`, `terurut`,
   `mempertahankan urutan`, and `isomorfisme urutan`.

7. **`positive` is an order/spectrum property, not merely numerical sign.**
   Preserve the source definition `$\sigma(a)\subseteq[0,\infty)$` at lines
   768-780, distinguish a positive element from the positive cone, and retain
   the `$a\le b$` convention. Do not translate `positive part` as a generic
   “good part.”

8. **`q-spectrum` is defined independently.** Keep `spektrum-q` and
   `$\breve\sigma_A(a)$` distinct from ordinary `spektrum`/`$\sigma_A(a)$`.
   Lines 736-743 state only an “almost” relationship and must not be flattened
   into equality in every algebra.

9. **Map/operator distinctions remain source-sensitive.** `L_a` at lines
   409-417 is explicitly a bounded linear operator, while `$L\colon A\to
   \mathcal B(A)$` is called a map. Follow the Chapter 11 QA rule: use
   `operator` for operator objects and `pemetaan` for general maps; the accepted
   recognition variant `operator linear terbatas` is not a global replacement
   for `pemetaan linear terbatas`.

10. **Synonyms must remain visible where the source makes them explicit.** Keep
    both `identitas aproksimatif` and `unit aproksimatif` in the definition at
    lines 1,023-1,038. Do not globally alternate them later. Likewise,
    `compatible with` and `respects` at lines 793-800 are source-declared
    alternatives and should both be represented.

11. **Preserve established Chapter 11 distinctions.** `karakter` is not
    `fungsi karakteristik`; `transformasi Gelfand` is not `transformasi
    Fourier`; `swaadjoin` remains preferred over the recognition variants
    `swadjoin` and `adjoin-diri`; and theorem names retain proper names and
    source numbering.

12. **Source defects are not terminology decisions.** Apparent source issues
    such as cross-reference `001500202i` versus `001500202i2`, “given a
    algebra,” the missing word in “The proof this result,” and index wording
    must go through the separate source-correction admission process. This plan
    neither silently repairs nor translates them.

## Translation/admission handoff

- Apply the preferred forms consistently across all six sections; preserve all
  mathematical identifiers, labels, citation keys, diagrams, and notation.
- Treat recognition variants as search/QA aids, not permission to vary prose
  indiscriminately.
- During an authorized backend reconciliation, reuse existing stable IDs and
  create new IDs only for the N12 concepts that actually appear in the admitted
  translation.
- Run an exact bilingual occurrence census after translation, paying special
  attention to all 26 `unitization` lines, both senses of `extension`, all
  modular-ideal compounds, the positive/order block, and the complete
  approximate-identity definition.
- Make no model-provenance or author/credit change as a side effect of applying
  this terminology plan.
