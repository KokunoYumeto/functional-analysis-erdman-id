# Analisis Fungsional dan Aljabar Operator — Bahasa Indonesia

Repositori ini memuat edisi Bahasa Indonesia yang sedang dikerjakan dari buku
John M. Erdman, *Functional Analysis and Operator Algebras: An Introduction*
(versi 4 Oktober 2015).

## Baca edisi saat ini

[Buka PDF kumulatif Bab 1--13](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-13.pdf)

Bab 1 sampai Bab 13 telah diterjemahkan lengkap dan melewati pemeriksaan struktur,
matematika, residu bahasa, hak komponen, build bersih berulang yang menghasilkan
PDF identik, serta inspeksi visual seluruh 183 halaman. PDF ini merupakan batas
produksi ketiga belas, bukan edisi lengkap. [PDF Bab 1--12](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-12.pdf),
[PDF Bab 1--11](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-11.pdf),
[PDF Bab 1--10](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-10.pdf),
[PDF Bab 1--9](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-9.pdf),
[PDF Bab 1--8](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-8.pdf),
[PDF Bab 1--7](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-7.pdf),
[PDF Bab 1--6](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-6.pdf),
[PDF Bab 1--5](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf),
[PDF Bab 1--4](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf),
[PDF Bab 1--3](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-3.pdf),
[PDF Bab 1--2](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-2.pdf),
dan [PDF Unit 1](output/pdf/analisis-fungsional-dan-aljabar-operator-id-unit-1.pdf)
tetap tersedia sebagai artefak batas sebelumnya.

## Preservasi versi

Versi parsial `2026.08.24-ch13` dipertahankan secara mandiri di Zenodo dengan
[DOI 10.5281/zenodo.22074101](https://doi.org/10.5281/zenodo.22074101). Catatan
Zenodo tersebut secara eksplisit berstatus **edisi dalam pengerjaan, Bab 1--13
dari 17 bab**, bukan buku lengkap. Metadata publik dan ketiga berkasnya telah
dibaca ulang secara anonim dan cocok byte demi byte dengan artefak lokal.
Mirror GitHub juga telah diverifikasi pada commit
`08c69f1460d5b92182b78f47af1732b6f36948c4`.
[Versi Figshare
v4](https://doi.org/10.6084/m9.figshare.33314709.v4) masih merupakan penunjuk
historis Bab 1--10 dan bukan bukti untuk batas produksi saat ini.
CC0 di Figshare hanya berlaku untuk metadata dan penunjuk tautan, sedangkan
seluruh berkas substantif tetap berlisensi CC BY-SA 4.0.

## Cakupan

Edisi yang dipilih mencakup seluruh buku 17 bab, kata pengantar, bibliografi,
dan indeks. Bab 1–8 membentuk rute inti D20; Bab 9–17 merupakan lanjutan
analisis fungsional dan aljabar operator. Penandaan kurikuler tidak menghapus
isi sumber. Pekerjaan berikutnya dimulai pada Bab 14, aljabar pengali.

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

Lihat [BUILD.md](BUILD.md). Build memerlukan distribusi TeX dengan pdfLaTeX,
BibTeX, MakeIndex, `latexmk`, serta paket Xy-pic. Build modern sengaja boleh
mengalir ulang; nomor halaman bukan pengenal tetap.

## Aksesibilitas

PDF kumulatif Bab 1--13 memiliki metadata, bookmark, tautan silang, indeks,
warna tautan berkontras tinggi, dan pemetaan Unicode untuk seluruh 45 sumber
font. PDF ini belum merupakan PDF bertag. Reader HTML semantik dan aksesibel
adalah keluaran wajib edisi lengkap dan masih dalam pengerjaan. Tidak ada
klaim aksesibilitas yang melampaui keadaan ini.

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
spektral-kompak yang ditulis terpisah akan memiliki ID, atribusi, dan
provenansnya sendiri; materi tersebut tidak akan dinyatakan sebagai tulisan
Erdman.
