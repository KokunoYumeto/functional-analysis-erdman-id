# Rencana terminologi dan batas editorial Bab 15

Tanggal: 2026-08-24  
Unit: `FAOA-2015-CH15`  
Sumber: `source/upstream/fredholm_theory.tex`

## Identitas dan dasar

Rencana ini meliputi 444 rekaman sumber, 16.977 byte, SHA-256
`0ef2e5be3c716a099e8609a84528d77ad6387ec531c52f9890d4e34175c57d91`.
Istilah yang sudah diakui dipakai kembali tanpa variasi prosa: `operator
kompak`, `ruang Hilbert`, `ruang Banach`, `adjoin`, `swaadjoin`, `kernel`,
`kokernel`, `kodimensi`, `operator geser unilateral`, `barisan eksak`,
`pemetaan hasil bagi`, `semigrup`, `invertibel`, dan `komponen terhubung`.
Pemeriksaan terminologi Indonesia terdokumentasi pada
`qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md`; bukti itu mendukung bentuk
inti analisis fungsional, tetapi bukan klaim frekuensi untuk istilah Fredholm
khusus di bawah. Bentuk baru dipilih dari makna matematis dan konsistensi
morfologi edisi.

## Judul dan istilah terkendali

| Sumber | Bentuk id-ID pilihan | Catatan |
|---|---|---|
| `FREDHOLM THEORY` | `TEORI FREDHOLM` | — |
| `The Fredholm Alternative` | `Alternatif Fredholm` | pertahankan nomor I–VI |
| `continued` / `Concluded` | `lanjutan` / `penutup` | — |
| integral equation | persamaan integral | — |
| homogeneous / nonhomogeneous equation | persamaan homogen / tak homogen | `nonhomogen` hanya varian pencarian |
| complete continuity | kontinuitas lengkap | nama historis bagi kekompakan |
| Riesz--Schauder operator | operator Riesz--Schauder | — |
| cokernel | kokernel | ID edisi yang sudah diakui |
| codimension | kodimensi | ID edisi yang sudah diakui |
| nonclosed range | jangkauan tak tertutup | `range` bukan `rentang linear` dalam konteks ini |
| Calkin algebra | aljabar Calkin | — |
| Fredholm operator | operator Fredholm | — |
| compact perturbation | perturbasi kompak | — |
| Atkinson's theorem | Teorema Atkinson | — |
| Fredholm index | indeks Fredholm | — |
| finite-rank partial isometry | isometri parsial berperingkat hingga | — |
| path | lintasan | — |
| connected by a path | terhubung oleh lintasan | — |
| homotopic in `$X$` | homotop dalam `$X$` | `homotopi` tetap nomina |
| path component | komponen lintasan | — |

## Koreksi matematis yang mengikat turunan

1. Alternatif I–IIIa memakai `\lambda\ne0`. Pada I, tambahkan
   `\lambda\in\C\setminus\{0\}`; pada II dan IIIa, ganti domain skalar
   yang terlalu luas dengan himpunan tersebut. Semua tag persamaan tetap.
2. Proposisi sumber baris 123 menamai ruang Banach ambient sebagai `$B$`,
   sehingga `(B/M)^*` terdefinisi.
3. Jumlah dua subruang selalu subruang. Contoh baris 150–157 harus menyatakan
   bahwa jumlah dua subruang **tertutup** dapat tidak **tertutup**; dalam
   contoh, `M+N=H\oplus\operatorname{ran}T` padat tetapi tak tertutup.
4. Surjektivitas indeks ke `\Z` pada baris 300–303 mensyaratkan ruang Hilbert
   berdimensi tak hingga.
5. Hapus syarat salah `SK=KS` dari Definisi `004034`. Dalam bab ini,
   operator Riesz--Schauder berarti perturbasi kompak dari operator
   invertibel. Dengan definisi itu, Alternatif IIIb–VI dan pembuktian melalui
   indeks nol konsisten. Sumber beku tidak diubah dan perubahan dicatat
   terang-terangan dalam ledger koreksi.
6. Hapus satu kurung tutup berlebih dalam kait indeks sumber baris 249.

## Klarifikasi ruang lingkup

- Alternatif I tidak menentukan ruang fungsi bagi `f,g,h,j`. Turunan
  mempertahankan keterbatasan sumber ini dan mencatatnya; turunan tidak
  mengarang pilihan antara `C([0,1])` dan `L^2([0,1])`.
- Definisi awal operator Fredholm hanya berbicara tentang operator pada satu
  ruang Hilbert. Sebelum contoh pemetaan `V\to W` berdimensi hingga, tambahkan
  klarifikasi lokal: untuk pemetaan antar-ruang, dipakai konvensi standar
  bahwa pemetaan Fredholm memiliki jangkauan tertutup serta kernel dan
  kokernel berdimensi hingga. Ini membuat contoh dan rumus indeks formal,
  tanpa mengubah definisi hasil bagi Calkin bagi endomorfisme.
- Klasifikasi komponen lintasan dipahami dalam ruang Hilbert kompleks yang
  dimaksudkan bab. Jangan memperluasnya diam-diam ke kategori real atau
  topologi operator lain.

## Penjagaan struktur

Pertahankan 33 label unik, 27 rujukan, 17 sitasi, 46 kait indeks, 11 kait
`\df`, 12 tag persamaan manual, 13 bukti (termasuk dua petunjuk), delapan
contoh, dan ketiadaan latihan/jawaban/solusi. Jangan mengubah urutan Alternatif
I–VI atau menyatakan syarat komutasi yang telah dibuktikan salah. Kredit John
M. Erdman, CC BY-SA 4.0, pemberitahuan perubahan, non-endorsement, dan
provenance model persis `OpenAI Codex gpt-5.6-sol, Ultra` tetap utuh.
