# Analisis Fungsional dan Aljabar Operator — Bahasa Indonesia

Repositori ini memuat edisi Bahasa Indonesia yang sedang dikerjakan dari buku
John M. Erdman, *Functional Analysis and Operator Algebras: An Introduction*
(versi 4 Oktober 2015).

## Baca edisi saat ini

[Buka PDF kumulatif Bab 1--5](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-5.pdf)

Bab 1 sampai Bab 5 telah diterjemahkan lengkap dan melewati pemeriksaan struktur,
matematika, residu bahasa, hak komponen, build bersih berulang yang menghasilkan
PDF identik, serta inspeksi visual seluruh 90 halaman. PDF ini merupakan batas
produksi kelima, bukan edisi lengkap. [PDF Bab 1--4](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-4.pdf),
[PDF Bab 1--3](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-3.pdf),
[PDF Bab 1--2](output/pdf/analisis-fungsional-dan-aljabar-operator-id-bab-1-2.pdf),
dan [PDF Unit 1](output/pdf/analisis-fungsional-dan-aljabar-operator-id-unit-1.pdf)
tetap tersedia sebagai artefak batas sebelumnya.

## Cakupan

Edisi yang dipilih mencakup seluruh buku 17 bab, kata pengantar, bibliografi,
dan indeks. Bab 1–8 membentuk rute inti D20; Bab 9–17 merupakan lanjutan
analisis fungsional dan aljabar operator. Penandaan kurikuler tidak menghapus
isi sumber. Pekerjaan berikutnya dimulai pada Bab 6, ruang Banach.

Sumber resmi:

- [halaman penulis](https://web.pdx.edu/~erdman/);
- [PDF resmi](https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_pdf.pdf);
- [arsip sumber resmi](https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_web.zip).

Identitas byte sumber, batas komponen, perubahan, dan hasil QA dicatat di
folder `provenance/`. Backend JSONL di folder `backend/` menggunakan ID yang
netral terhadap bahasa dan nomor halaman agar unit dapat dipetakan ke bahasa
lain tanpa mengekstrak ulang PDF.

## Build

Lihat [BUILD.md](BUILD.md). Build memerlukan distribusi TeX dengan pdfLaTeX,
BibTeX, MakeIndex, `latexmk`, serta paket Xy-pic. Build modern sengaja boleh
mengalir ulang; nomor halaman bukan pengenal tetap.

## Aksesibilitas

PDF kumulatif Bab 1--5 memiliki metadata, bookmark, tautan silang, indeks,
warna tautan berkontras tinggi, dan pemetaan Unicode untuk 38 dari 40 sumber
font. Dua font panah diagram lama belum memiliki peta Unicode, dan PDF ini belum
merupakan PDF bertag. Reader HTML semantik dan aksesibel adalah
keluaran wajib edisi lengkap dan masih dalam pengerjaan. Tidak ada klaim
aksesibilitas yang melampaui keadaan ini.

## Lisensi dan atribusi

Karya sumber John M. Erdman dan adaptasi Bahasa Indonesia ini dilisensikan
menurut [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Terjemahan dibuat oleh Codex atas arahan pengguna. Proyek ini tidak disponsori,
disetujui, atau didukung oleh John M. Erdman maupun Portland State University.

Komponen yang statusnya tidak cukup jelas tidak masuk ke reader. Berkas
`DIAGXY.TEX` dipertahankan byte-identik di bawah pemberitahuan distribusi
Michael Barr yang tertanam di dalamnya. Materi solusi, penguasaan, dan jembatan
spektral-kompak yang ditulis terpisah akan memiliki ID, atribusi, dan
provenansnya sendiri; materi tersebut tidak akan dinyatakan sebagai tulisan
Erdman.
