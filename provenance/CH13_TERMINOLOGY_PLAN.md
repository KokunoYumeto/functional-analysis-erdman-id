# Chapter 13 terminology decisions

Date: 2026-08-24  
Unit: `FAOA-2015-CH13` / `source/upstream/GNS_construction.tex`  
Status: applied to the complete provisional translation; backend admission pending

## Evidence boundary

The decisions cover all 289 source records and use the admitted edition
glossary, prior reader prose, and the bounded Indonesian terminology QA already
completed for Chapter 11. The external UNDIP/ITB witnesses attest the core
forms `ruang Hilbert`, `operator linear`, `operator adjoint`, and
functional-analysis vocabulary, but they do not attest the specialized
GNS/state/representation compounds below. Those compounds are therefore
chosen from their mathematical meaning, normal Indonesian morphology, and
whole-edition consistency—not presented as an external frequency claim.

| Witness | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `source/upstream/GNS_construction.tex` | 11,965 | `fcc774cecc607d9860540da7b757ae04a3c43afe9d9a17e8c881e077f02682c1` | complete frozen Chapter 13 source |
| `backend/terminology.jsonl` | 138,915 | `f6140d3c78be026175d6609524d5756c580c5127a08787f24216832b487ad667` | admitted preferred terms through Chapter 12 |
| `backend/terminology_qa.jsonl` | 9,232 | `0be61180b43ca8e314bc3323696a0836ed82f505153444373584d1ac640cc3c8` | recognition-variant policy |
| `qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md` | 8,181 | `7a815e6e5d5c1846706aa4c80f12ed43670d1a35205b6896065be3f395a53575` | bounded external Indonesian witness and limits |
| `provenance/SELF_ADJOINT_TERMINOLOGY_ADJUDICATION.md` | 2,322 | `ad5b60165004920b1f3ff0d58fcbd50633df45336856171e09ea7cd7345fad21` | whole-edition `swaadjoin` decision |

The requested arXiv-first check is not repeated: its bounded negative result,
the directly inspected institutional fallback, and exact model provenance are
already durable in the cited Chapter 11 report.

## Titles

| Source | Preferred id-ID |
|---|---|
| `THE GELFAND-NAIMARK-SEGAL CONSTRUCTION` | `KONSTRUKSI GELFAND-NAIMARK-SEGAL` |
| `Positive Linear Functionals` | `Fungsional Linear Positif` |
| `Representations` | `Representasi` |
| `The GNS-Construction and the Third Gelfand-Naimark Theorem` | `Konstruksi GNS dan Teorema Gelfand-Naimark Ketiga` |

## Inherited terms

| Source term | Preferred id-ID | Stable ID / evidence |
|---|---|---|
| Hermitian | Hermitian | `TERM-HERMITIAN` |
| self-adjoint | swaadjoin | `TERM-SELF-ADJOINT`; recognize `swadjoin`, `adjoin-diri` |
| positive | positif | `TERM-POSITIVE` |
| proper (cone) | proper | `TERM-PROPER-CONE`; do not use rejected `wajar` |
| partial ordering | urutan parsial | `TERM-PARTIAL-ORDERING` |
| direct sum | jumlah langsung | `TERM-DIRECT-SUM` |
| unitary | uniter | `TERM-UNITARY` |
| semi-inner product | hasil kali dalam semu | `TERM-SEMI-INNER-PRODUCT` |
| left ideal | ideal kiri | `TERM-LEFT-IDEAL` |
| dense | padat | admitted Chapter 3 definition and whole-reader usage; do not alternate with `rapat` |
| `$C^*$`-algebra | aljabar-`$C^*$` | `TERM-CSTAR-ALGEBRA` |
| `$*$`-homomorphism | homomorfisme-`$*$` | `TERM-STAR-HOMOMORPHISM` |

## New Chapter 13 controlled terms

| Source term | Preferred id-ID | Recognition variant / safeguard |
|---|---|---|
| positive linear functional | fungsional linear positif | keep word order; not “fungsi positif” |
| state | keadaan | recognize English `state`; stable ID disambiguates ordinary prose `keadaan` |
| vector state | keadaan vektor | state induced by a unit vector, not a generic vector condition |
| representation (of a `$C^*$`-algebra) | representasi | scope it to a `$*$`-homomorphism into `\mathfrak B(H)` |
| nondegenerate | tak terdegenerasi | qualifier of a representation; preserve density criterion |
| faithful | setia | preserve injectivity; never weaken to “andal” |
| cyclic | siklik | qualifier of a representation |
| cyclic vector | vektor siklik | preserve the density condition separately |
| left kernel | kernel kiri | distinguish from a two-sided kernel/ideal |
| Gelfand-Naimark-Segal construction | konstruksi Gelfand-Naimark-Segal | short form `konstruksi GNS` after first expansion |
| faithful representation | representasi setia | composition of the controlled terms |
| cyclic representation | representasi siklik | composition of the controlled terms |
| direct sum of representations | jumlah langsung representasi | reuse the existing construction ID plus a scoped representation concept |

## Mathematical and linguistic safeguards

1. `state` is a positive norm-one functional in the general, possibly
   nonunital, setting. The unital identity criterion is stated as an equivalent
   special case; this correction is separately provenanced.
2. `representation`, `faithful`, `nondegenerate`, and `cyclic` remain distinct:
   respectively a `$*$`-homomorphism, injectivity, density of `\pi(A)H`, and
   existence of one cyclic vector.
3. Preserve `\tau^\star` as the conjugate functional and `\tau^*` as the usual
   adjoint mapping; Indonesian prose may not collapse the notation.
4. Use `padat`, the admitted reader term for *dense*. `Rapat` is not introduced
   as an uncontrolled prose alternate.
5. Preserve the single exercise, all theorem labels, references, citations,
   index hooks, and the source distinction between the direct sums of spaces,
   operators, and representations.
6. Use `elemen` for mathematical elements, matching the edition, rather than
   varying with `unsur` inside this chapter.

At backend admission, reuse inherited IDs and add only the specialized records
actually instantiated by the final target. The model-provenance string remains
exactly `OpenAI Codex gpt-5.6-sol, Ultra`; source authorship and all component
credits remain primary.
