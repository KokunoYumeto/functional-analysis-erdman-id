# Analisis Fungsional dan Aljabar Operator — Bahasa Indonesia

Repositori ini memuat edisi Bahasa Indonesia lengkap dari buku
John M. Erdman, *Functional Analysis and Operator Algebras: An Introduction*
(versi 4 Oktober 2015), beserta pendamping penguasaan berprovenans terpisah.

## Baca edisi lengkap

- **[Baca online — reader HTML teks sumber lengkap](https://kokunoyumeto.github.io/functional-analysis-erdman-id/)**
  memuat prakata, seluruh 17 bab, bibliografi, indeks, MathML semantik, dan
  diagram SVG berlabel dalam tata letak yang mengalir ulang di desktop maupun
  seluler.
- **[Buka pendamping penguasaan dan jembatan spektral](https://kokunoyumeto.github.io/functional-analysis-erdman-id/companion/)**
  memuat 52 solusi latihan sumber, 10 solusi hasil kerja pembaca, dan jembatan
  spektral-kompak/SVD 13 unit dengan provenans terpisah.
- [PDF edisi lengkap dengan pendamping penguasaan](output/pdf/analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf)
  adalah reader utama 298 halaman.
- [Reader HTML pendamping semantik](output/html-companion/index.html) memuat
  jembatan spektral-kompak/SVD, 52 solusi latihan sumber, dan 10 solusi hasil
  kerja pembaca dengan MathML, jangkar stabil, serta reflow desktop/seluler.
- [Reader HTML teks sumber](output/html/index.html) memuat prakata, seluruh 17
  bab, bibliografi, indeks, 11.193 rumus MathML, serta 80 diagram SVG berlabel.

Terjemahan, pendamping, PDF terintegrasi, kedua reader HTML, dan backend
modular kini lengkap. Dua build PDF bersih menghasilkan byte identik; seluruh
298 halaman dirender dan diperiksa. Reader pendamping juga direproduksi dua
kali tanpa selisih byte dan lolos pemeriksaan struktur, tautan, formula,
aksesibilitas, serta reflow. PDF dan reader checkpoint sebelumnya tetap
dipertahankan sebagai riwayat produksi, tetapi bukan lagi pintu masuk utama.

## Preservasi versi

Semua versi terbit dipertahankan dalam
[konsep Zenodo O008 yang sama](https://doi.org/10.5281/zenodo.22059739), tanpa
membuat konsep pesaing. Versi terkini
`2026.08.25-backend-artifact-reconciliation` tersedia dengan
[DOI 10.5281/zenodo.22088947](https://doi.org/10.5281/zenodo.22088947) dan
terikat pada commit GitHub
[`059bda086dfd6e6aa80f2077b2338c5d15039057`](https://github.com/KokunoYumeto/functional-analysis-erdman-id/tree/059bda086dfd6e6aa80f2077b2338c5d15039057).
Versi ini merekonsiliasi satu identitas artefak overlay backend dan mengikat
tiga saksi QA yang dihasilkan PowerShell pada byte CRLF persisnya di Git serta
arsip rilis. Seluruh 19 JSONL backend dasar, PDF 298 halaman, HTML, terjemahan,
solusi, jembatan, dan isi matematis tidak berubah. Versi koreksi metadata
otoritas sebelumnya `2026.08.25-authority-hash-correction-r2` tetap tersedia
dengan [DOI 10.5281/zenodo.22088677](https://doi.org/10.5281/zenodo.22088677).
Versi lengkap terintegrasi sebelumnya
`2026.08.25-final-integrated` tetap tersedia dengan
[DOI 10.5281/zenodo.22088404](https://doi.org/10.5281/zenodo.22088404).
Versi reader HTML `2026.08.24-html-reader` sebelumnya tetap tersedia dengan
[DOI 10.5281/zenodo.22086801](https://doi.org/10.5281/zenodo.22086801).
Versi teks sumber lengkap `2026.08.24-source-text` sebelumnya tetap tersedia
dengan [DOI 10.5281/zenodo.22082688](https://doi.org/10.5281/zenodo.22082688),
dan versi `2026.08.24-ch17` tetap tersedia dengan
[DOI 10.5281/zenodo.22077300](https://doi.org/10.5281/zenodo.22077300).
Setiap checkpoint menyatakan cakupan dan keterbatasannya secara eksplisit;
metadata publik serta semua berkas terbit dibaca ulang secara anonim dan
dicocokkan byte demi byte dengan artefak lokal. Mirror GitHub juga diverifikasi
pada setiap batas terbit.
[Versi Figshare
v4](https://doi.org/10.6084/m9.figshare.33314709.v4) masih merupakan penunjuk
historis Bab 1--10 dan bukan bukti untuk batas produksi saat ini.
CC0 di Figshare hanya berlaku untuk metadata dan penunjuk tautan, sedangkan
seluruh berkas substantif tetap berlisensi CC BY-SA 4.0.

## Cakupan

Edisi ini mencakup seluruh buku 17 bab, prakata, bibliografi,
dan indeks. Bab 1–8 membentuk rute inti D20; Bab 9–17 merupakan lanjutan
analisis fungsional dan aljabar operator. Penandaan kurikuler tidak menghapus
isi sumber. Pendamping menambahkan solusi lengkap bagi seluruh 52 latihan
eksplisit, sepuluh hasil kerja pembaca sentral, serta jembatan 13 unit mengenai
Riesz--Schauder, teorema spektral swaadjoin kompak, nilai singular/SVD, galat
aproksimasi peringkat hingga, dan dekomposisi polar. Semua tambahan memakai ID,
atribusi, lisensi komponen, dan provenans terpisah dari teks Erdman.

Sumber resmi:

- [halaman penulis](https://web.pdx.edu/~erdman/);
- [PDF resmi](https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_pdf.pdf);
- [arsip sumber resmi](https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_web.zip).

Identitas byte sumber, batas komponen, perubahan, dan hasil QA dicatat di
folder `provenance/`. Backend JSONL di folder `backend/` menggunakan ID yang
netral terhadap bahasa dan nomor halaman agar unit dapat dipetakan ke bahasa
lain tanpa mengekstrak ulang PDF.

QA terminologi Indonesia berbasis sumber primer dicatat dalam
[`qa/terminology_evidence/undip-jfma-2020-dunford/TERMINOLOGY_QA_REPORT.md`](qa/terminology_evidence/undip-jfma-2020-dunford/TERMINOLOGY_QA_REPORT.md).
Perbandingan itu tidak mengubah prosa Bab 1--9; bentuk-bentuk alternatif yang
terbukti hanya ditambahkan sebagai varian pencarian/interoperabilitas dalam
`backend/terminology_qa.jsonl`. Keputusan khusus Bab 10 mengenai istilah
*distribusi tempered* dan pemeriksaan istilah khusus Bab 11 dicatat terpisah di
`provenance/CH10_TERMINOLOGY_DECISIONS.md` dan
`provenance/CH11_TERMINOLOGY_DECISIONS.md`.

## Build

Lihat [BUILD.md](BUILD.md). Build PDF memerlukan distribusi TeX dengan
pdfLaTeX, BibTeX, MakeIndex, `latexmk`, serta paket Xy-pic. Build HTML
memerlukan Python, Pandoc dengan MathML, `lxml`, LaTeX, dan `dvisvgm`. Build
modern sengaja boleh mengalir ulang; nomor halaman bukan pengenal tetap.

## Aksesibilitas

PDF terintegrasi memiliki metadata `id-ID`, 141 entri kerangka, 3.116 tautan
internal yang seluruhnya terurai, dan pemetaan Unicode untuk seluruh 53 objek
font. PDF 298 halaman ini belum merupakan PDF bertag. Kedua reader HTML
semantik menyediakan struktur judul, navigasi, MathML, diagram berlabel,
transkrip diagram, jangkar stabil, dan reflow responsif sebagai permukaan
aksesibilitas. Tidak ada klaim bahwa PDF itu sendiri sudah bertag atau
sepenuhnya aksesibel.

## Lisensi dan atribusi

Karya sumber John M. Erdman dan adaptasi Bahasa Indonesia ini dilisensikan
menurut [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Terjemahan dan penyuntingan teknis dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra**,
atas arahan pengguna manusia. Provenans model dan pembagian kredit
dicatat di `provenance/TRANSLATION_MODEL_PROVENANCE.md`. Proyek ini tidak
disponsori, disetujui, atau didukung oleh John M. Erdman maupun Portland State
University.

Komponen yang statusnya tidak cukup jelas tidak masuk ke reader. Berkas
`DIAGXY.TEX` dipertahankan byte-identik di bawah pemberitahuan distribusi
Michael Barr yang tertanam di dalamnya. Materi solusi, penguasaan, dan jembatan
spektral-kompak yang ditulis terpisah memiliki ID, atribusi, dan provenansnya
sendiri; materi tersebut tidak dinyatakan sebagai tulisan Erdman.
