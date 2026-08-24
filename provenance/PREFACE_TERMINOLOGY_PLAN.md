# FAOA-2015-PREFACE Indonesian terminology plan

Date: 2026-08-24  
State: **frozen for preface production; target not yet edited**  
Unit: `FAOA-2015-PREFACE`

## Evidence and precedence

This plan applies only to `source/upstream/preface.tex`, 18,107 bytes / 351
CRLF records / SHA-256
`0976042bbb6ae3b8d1e5bb113a93d51169fada9d3e41f2d01435c76b6729edb9`.
Its precedence is:

1. exact mathematical meaning and the frozen source notation;
2. the admitted Chapters 1--17 Indonesian usage;
3. `backend/terminology.jsonl`, 171,497 bytes / 407 records / SHA-256
   `2464af7ef8add6e5e01c95a73e967c64f47eacf20d4146e432e1378be890fb2a`;
4. the bounded field-usage witness in `backend/terminology_qa.jsonl`, 9,232
   bytes / seven records / SHA-256
   `0be61180b43ca8e314bc3323696a0836ed82f505153444373584d1ac640cc3c8`;
5. natural reader-facing id-ID prose.

The plan introduces no competing preferred form for an already admitted term.
Recognition variants may be indexed, but they do not displace the preferred
reader form.

## Narrative and curricular vocabulary

| Source term or phrase | Preferred id-ID form | Constraint |
|---|---|---|
| preface | prakata | reader heading `Prakata`; stable unit remains `PREFACE` |
| linear functional analysis | analisis fungsional linear | retain distinction from generic analysis |
| operator algebra(s) | aljabar operator | established title form |
| activity-oriented | berorientasi aktivitas | do not weaken the learner-work contract |
| pedagogical companion | pendamping pedagogis | natural prose may use `pendamping pembelajaran` where syntax requires |
| proposition / example / exercise / corollary | proposisi / contoh / latihan / akibat | matches theorem-environment names |
| proof / reference to a proof | bukti / rujukan ke bukti | do not imply that a citation-only pointer is a supplied proof |
| vector space / linear map | ruang vektor / pemetaan linear | established whole-edition forms |
| linear algebra / real analysis / topology | aljabar linear / analisis real / topologi | established forms |
| Lebesgue measure / Lebesgue integral | ukuran Lebesgue / integral Lebesgue | preserve proper name |
| open set / compact set / continuous function | himpunan terbuka / himpunan kompak / fungsi kontinu | established forms |
| finite-dimensional | berdimensi hingga | hyphenation follows Indonesian syntax |
| diagonalizable | dapat didiagonalkan | established form |
| unitarily diagonalizable | dapat didiagonalkan secara uniter | `uniter`, not `unitari` |
| normal operator | operator normal | established form |
| unitarily equivalent | ekuivalen secara uniter | established form |
| eigenvalue / multiplicity | nilai eigen / multiplisitas | established forms |
| projection | proyeksi | established form |
| inner-product space | ruang hasil kali dalam | established form |
| operator theory | teori operator | field name |
| complex variables | variabel kompleks | matches admitted Chapter 8 usage |
| algebraic topology | topologi aljabar | matches admitted Chapter 14 usage |
| homological algebra | aljabar homologis | `aljabar homologi` is a recognition variant |
| advanced calculus | kalkulus lanjut | corrects source `advanced calculous` |
| metric space / topological space | ruang metrik / ruang topologis | established forms |
| annotated reading/reference list | daftar bacaan dan rujukan beranotasi | preserve both functions |

The finite-dimensional unitary statements must say `ruang hasil kali dalam
kompleks berdimensi hingga`. This is a formal scope repair, not optional
terminology.

## Reference-table and number-set vocabulary

| Source | Preferred id-ID | Note |
|---|---|---|
| Greek letters | huruf Yunani | index as `huruf!Yunani` and `Yunani!huruf` where hierarchy permits |
| upper case / lower case | huruf kapital / huruf kecil | applies to both reference tables |
| English name (approximate pronunciation) | nama dalam bahasa Inggris (perkiraan pelafalan) | preserve source strings as English approximations |
| Fraktur fonts | font Fraktur | retain `Fraktur` as proper typographic name |
| Roman equivalents | padanan huruf Roman | do not silently call the Fraktur glyphs Latin variables |
| script English letters | huruf Latin kaligrafis | natural blackboard recommendation |
| family of sets / operators | keluarga himpunan / operator | established mathematical `keluarga` |
| set of complex/real/rational numbers | himpunan bilangan kompleks/real/rasional | preserve `\C`, `\R`, `\Q` |
| integers / natural numbers | bilangan bulat / bilangan asli | preserve source convention `\N={1,2,...}` |
| n-tuple | n-tupel | matches admitted Chapters 3 and 17 |
| open unit disc/disk | cakram satuan terbuka | one Indonesian form for both English spellings |
| unit circle | lingkaran satuan | preserve both `\T` and `\Sp^1` |
| positive reals/rationals/integers in lines 187/189/191 | bilangan real/rasional/bulat tak negatif | required because the displayed sets contain zero |

Do not change `\R^+`, `\Q^+`, or `\Z^+`. The prose explicitly explains the
book's convention so readers can distinguish it from other conventions for a
superscript plus.

## Function vocabulary and concept boundaries

| Source defined term | Preferred id-ID | Recognition variant / boundary |
|---|---|---|
| function | fungsi | generic primary term |
| domain | domain | keep `\dom f` |
| input space | ruang masukan | synonym of domain in this source |
| codomain | kodomain | not the same as range |
| target space | ruang sasaran | synonym of codomain in this source |
| output space | ruang keluaran | synonym of codomain in this source |
| graph | graf | ordered-pair relation `G` |
| image of a point | citra suatu titik | element `f(x)` |
| transformation | transformasi | source says synonymous with function here |
| map / mapping | pemetaan | source says synonymous with function here |
| family of all functions | keluarga semua fungsi | preserve `\fml F(S,T)` |
| restriction | pembatasan | `restriksi` is recognition-only |
| image of a set | citra suatu himpunan | preserve `f^{\sto}(A)` and conventional `f(A)` |
| range | jangkauan | preserve `\ran f`; do not collapse into codomain |
| image of a function | citra suatu fungsi | source synonym for range |
| inverse image | pracitra | `citra invers` is the source-retained synonym |
| injective | injektif | established form |
| one-to-one | satu-satu | parenthetical synonym |
| surjective | surjektif | established form |
| onto | onto | recognition synonym; explain as reaching all of the codomain rather than forcing ambiguous bare `pada` |
| bijective | bijektif | established form |
| one-to-one correspondence | korespondensi satu-satu | close the source's missing parenthesis |
| diagram | diagram | visible and semantic surfaces both required |
| commute | berkomutasi | verb |
| commutative diagram | diagram komutatif | noun phrase |

The ordered triple is `tripel terurut`; `rule` in the informal account is
`aturan`; `relation` is `relasi`; `ordered pair` is `pasangan terurut`; `arrow`
is `panah`; composition is `komposisi`.

## Index and TeX policy

- Translate all 53 active index arguments while preserving their hierarchy,
  math sort keys, and duplicate conceptual routes. Keep the commented source
  candidate at line 274 commented.
- Preserve the 21 `\df` positions and distinguish point image, set image,
  function image/range, and inverse image.
- Preserve every source macro, formula, citation key, and label unless the
  correction ledger explicitly authorizes an adaptation.
- Rebuild the two reference tables without `TABLE.TEX`. Table headings and
  prose are translated; mathematical glyphs and all row ordering are retained.
- Preserve `DIAGXY.TEX` diagrams and add separate semantic descriptions. Do not
  translate node or arrow symbols.
- Preserve proper names and source titles: Paul Halmos, Brown, Douglas,
  Fillmore, Creative Commons, Portland State University, LaTeX, and Fraktur.

## Rights and attribution language

The Halmos idea is paraphrased, not quoted: retain the author, book title, and
`Halmos:1982` citation without quotation marks or reconstructed wording. Use
the exact license name `Creative Commons Attribution--ShareAlike 4.0
International (CC BY-SA 4.0)` where formal license identity is needed. Retain
the wrapper's attribution, change notice, ShareAlike, no-additional-restriction
boundary, non-endorsement, and exact model provenance
`OpenAI Codex gpt-5.6-sol, Ultra`.

No target, wrapper, backend, or admitted chapter was changed by this plan.

