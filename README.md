# Analisis Fungsional dan Aljabar Operator: terjemahan Bahasa Indonesia buku John M. Erdman

Terjemahan Bahasa Indonesia yang lengkap dari *Functional Analysis and Operator Algebras: An Introduction* karya John M.
Erdman (versi 4 Oktober 2015): prakata, 17 bab, bibliografi, dan indeks, dengan pendamping penguasaan yang ditulis
terpisah (solusi seluruh 52 latihan, 10 hasil kerja pembaca, dan jembatan spektral-kompak/SVD 13 unit), sebagai PDF 298
halaman, dua pembaca HTML, dan backend modular.

[Baca daring](https://kokunoyumeto.github.io/functional-analysis-erdman-id/) · [Pendamping](https://kokunoyumeto.github.io/functional-analysis-erdman-id/companion/) · [PDF](output/pdf/analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf)

## Cara pembuatan

Terjemahan dan penyuntingan teknis dikerjakan oleh AI: OpenAI Codex gpt-5.6-sol, Ultra; pembagian kredit dicatat di
`provenance/TRANSLATION_MODEL_PROVENANCE.md`. Dua build PDF bersih menghasilkan byte identik, dan seluruh 298 halaman
dirender dan diperiksa. Pembaca pendamping direproduksi dua kali tanpa selisih byte dan lolos pemeriksaan struktur,
tautan, rumus, aksesibilitas, dan reflow. Istilah diperiksa terhadap sumber primer berbahasa Indonesia
([laporan](qa/terminology_evidence/undip-jfma-2020-dunford/TERMINOLOGY_QA_REPORT.md)); keputusan istilah Bab 10 dan 11
ada di `provenance/`.

## Status

Edisi lengkap: terjemahan, pendamping, PDF terintegrasi, kedua pembaca HTML, dan backend modular. Bab 1–8 membentuk
rute inti kursus D20 dalam [Program Matematika Indonesia](https://kokunoyumeto.github.io/program-matematika-indonesia/id/#course-D20);
Bab 9–17 merupakan lanjutannya. PDF memiliki metadata `id-ID`, kerangka, tautan internal, dan pemetaan Unicode untuk
semua font, tetapi belum bertag; pembaca HTML adalah permukaan aksesibilitas utama. Masih mungkin ada kesalahan.

## Isi

- [PDF edisi lengkap dengan pendamping](output/pdf/analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf) (298 halaman).
- [Pembaca HTML teks sumber](output/html/index.html): prakata, 17 bab, bibliografi, indeks, 11.193 rumus MathML, dan
  80 diagram SVG berlabel.
- [Pembaca HTML pendamping](output/html-companion/index.html): jembatan spektral-kompak/SVD, solusi latihan, dan hasil
  kerja pembaca.
- `source/`, `bridge/`, `mastery/`: sumber terjemahan dan pendamping; `backend/`: JSONL dengan ID yang netral terhadap
  bahasa dan nomor halaman; `provenance/` dan `qa/`: identitas sumber, batas komponen, perubahan, dan pemeriksaan.
- Build: [BUILD.md](BUILD.md) (pdfLaTeX, BibTeX, MakeIndex, `latexmk`, Xy-pic; untuk HTML: Python, Pandoc, `lxml`,
  LaTeX, `dvisvgm`).

## Sumber dan atribusi

- John M. Erdman, *Functional Analysis and Operator Algebras: An Introduction*:
  [halaman penulis](https://web.pdx.edu/~erdman/),
  [PDF resmi](https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_pdf.pdf),
  [arsip sumber resmi](https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_web.zip).
- `DIAGXY.TEX` dipertahankan byte-identik di bawah pemberitahuan distribusi Michael Barr yang tertanam di dalamnya.
- Materi solusi, penguasaan, dan jembatan ditulis terpisah dan tidak dinyatakan sebagai tulisan Erdman. Proyek ini
  tidak disponsori atau didukung oleh John M. Erdman maupun Portland State University.

## Lisensi

Karya sumber dan adaptasi Bahasa Indonesia ini tersedia menurut
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); komponen yang statusnya tidak cukup jelas tidak
dimasukkan. Lihat [LICENSE.md](LICENSE.md).
