# Rencana terminologi dan batas editorial Bab 16

Tanggal: 2026-08-24  
Unit: `FAOA-2015-CH16`  
Sumber: `source/upstream/extensions.tex`, rekaman 1--1.000

## Identitas dan dasar keputusan

Rencana ini mencakup keseluruhan sumber: 42.614 byte, 1.000 rekaman CRLF,
SHA-256
`e4a1710bcf5773bf8193bd05f14a1ee82703212f3d123fb4669a4de76ae7e318`.
Empat bagian aktifnya adalah *Essentially Normal Operators*, *Toeplitz
Operators*, *Addition of Extensions*, dan *Completely Positive Maps*.
Judul produk tensor pada rekaman 676 dikomentari dalam sumber dan tidak
diaktifkan oleh terjemahan.

Dasar konsistensi edisi adalah `backend/terminology.jsonl`, Bab 2 untuk
`tarik balik`, `praurutan`, dan `urutan parsial`, Bab 5 untuk `ekuivalen secara
uniter`, Bab 12 untuk `ekstensi`, `eksak terbelah`, dan kosakata positif, serta
Bab 15 untuk `aljabar Calkin`, `operator Fredholm`, dan `indeks Fredholm`.
Istilah terakui berikut dipakai kembali tanpa variasi prosa: `ruang Hilbert`,
`operator kompak`, `perturbasi kompak`, `spektrum`, `nilai eigen`,
`swaadjoin`, `normal`, `uniter`, `basis ortonormal`, `proyeksi`, `jangkauan`,
`operator perkalian`, `aljabar-$C^*$`, `beridentitas`, `representasi`,
`homomorfisme-$*\,$`, `monomorfisme-$*\,$`, `barisan eksak`, `ekstensi`,
`tarik balik`, `konjugasi`, `semigrup`, `positif`, `kontraktif`, `praurutan`,
`urutan parsial`, `aljabar Calkin`, `operator Fredholm`, dan `indeks
Fredholm`.

Pemeriksaan terminologi Indonesia eksternal yang sudah ada pada
`qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md` mendukung kosakata inti
analisis fungsional, tetapi tidak menjadi bukti frekuensi bagi istilah khusus
BDF/Toeplitz/positivitas lengkap. Istilah khusus di bawah dipilih dari makna
matematis, morfologi bahasa Indonesia, dan konsistensi internal edisi; rencana
ini tidak mengarang klaim konvensi lapangan eksternal.

## Judul terkendali

| Sumber | Bentuk id-ID pilihan | Catatan |
|---|---|---|
| `EXTENSIONS` | `EKSTENSI` | objek aljabar/barisan eksak, bukan perpanjangan fungsional |
| `Essentially Normal Operators` | `Operator Normal secara Esensial` | kapitalisasi judul saja yang berubah |
| `Toeplitz Operators` | `Operator Toeplitz` | nama diri dipertahankan |
| `Addition of Extensions` | `Penjumlahan Ekstensi` | operasi pada `\ext A` |
| `Completely Positive Maps` | `Pemetaan Positif Lengkap` | `lengkap` adalah istilah teknis operator-aljabar |

## Istilah terkendali: spektrum esensial dan Toeplitz

| Sumber | Bentuk id-ID pilihan | Varian pengenalan / penjagaan |
|---|---|---|
| essential spectrum | spektrum esensial | simbol `\sigma_e(T)` tetap |
| accumulation point | titik akumulasi | — |
| finite/infinite multiplicity | multiplisitas hingga/tak hingga | jangan ganti dengan banyaknya vektor eigen |
| essentially unitarily equivalent | ekuivalen uniter secara esensial | gunakan bentuk ini konsisten; relasi biasa tetap `ekuivalen secara uniter` |
| compalent | kompalen | istilah rekaan sumber; definisinya tetap modulo kompak |
| essentially normal | normal secara esensial | — |
| commutator | komutator | tanda sumber `[T,T^*]=TT^*-T^*T` tetap |
| essentially self-adjoint | swaadjoin secara esensial | `swaadjoin` adalah bentuk terakui edisi |
| diagonalizable | dapat didiagonalkan | — |
| square integrable | terintegralkan kuadrat | konteks `L_2(\T)` |
| normalized arc-length measure | ukuran panjang busur ternormalisasi | — |
| Hardy space | ruang Hardy | — |
| Toeplitz operator | operator Toeplitz | — |
| symbol | simbol | khusus simbol operator Toeplitz |
| essentially bounded | terbatas secara esensial | sifat fungsi `L_\infty` |
| Hartman--Wintner spectral inclusion theorem | Teorema Inklusi Spektral Hartman--Wintner | — |
| semi-commutator | semikomutator | bukan komutator penuh |
| Toeplitz matrix | matriks Toeplitz | — |
| Toeplitz algebra | aljabar Toeplitz | — |
| Toeplitz extension | ekstensi Toeplitz | — |
| continuous section | penampang kontinu | peta yang dimaksud adalah `T`, bukan `\beta` |
| isometrical cross section | penampang silang isometrik | parafrase kutipan, jangan ubah peran peta |
| winding number | bilangan lilit | kenali `bilangan belitan`; prosa utama tidak berganti-ganti |
| fundamental group | grup fundamental | gunakan `\pi_1`, bukan `\pi^1` |
| punctured plane | bidang berlubang | objeknya `\C\setminus\{0\}` |
| Wold decomposition | dekomposisi Wold | — |
| proper isometry | isometri sejati | sumber menjelaskan “tak uniter”; jangan pakai arti *proper cone* |
| Coburn's theorem | Teorema Coburn | — |

## Istilah terkendali: ekstensi dan penjumlahannya

| Sumber | Bentuk id-ID pilihan | Varian pengenalan / penjagaan |
|---|---|---|
| extension of `K` by `A` | ekstensi `K` oleh `A` | pertahankan orientasi frasa sumber dan barisan eksaknya |
| equivalent extensions | ekstensi yang ekuivalen | `ekuivalensi ekstensi` untuk nomina |
| conjugation by `U` | konjugasi oleh `U` | `\ad_U(T)=UTU^*` pada arah yang didefinisikan |
| extension determined by `T` | ekstensi yang ditentukan oleh `T` | — |
| pullback | tarik balik | bentuk terakui Bab 2 |
| pullback along maps | tarik balik sepanjang pemetaan | `along` tidak menyatakan lintasan topologis |
| unitary equivalence of monomorphisms | ekuivalensi uniter monomorfisme | bentuk predikat: `ekuivalen secara uniter` |
| addition of extensions | penjumlahan ekstensi | operasi kelas dalam `\ext A` |
| commutative semigroup | semigrup komutatif | — |
| abstract Toeplitz operator | operator Toeplitz abstrak | — |
| abstract Toeplitz extension | ekstensi Toeplitz abstrak | dapat tidak injektif |
| split / semisplit | terbelah / semiterbelah | selalu nyatakan kategori atau jenis pengangkatannya bila perlu |
| additive identity / inverse | identitas aditif / invers aditif | — |
| Abelian group | grup Abel | `grup Abelian` hanya varian pengenalan |

## Istilah terkendali: pemetaan positif lengkap

| Sumber | Bentuk id-ID pilihan | Varian pengenalan / penjagaan |
|---|---|---|
| positive map | pemetaan positif | `positif` berarti mempertahankan elemen positif |
| standard matrix units | unit matriks standar | bukan matriks identitas |
| n-positive | n-positif | pertahankan pangkat `\phi^{(n)}` |
| completely positive | positif lengkap | hindari pergantian prosa ke `sepenuhnya positif` |
| 2-positive | 2-positif | — |
| completely bounded | terbatas lengkap | — |
| completely bounded norm | norma terbatas lengkap | simbol `\|\phi\|_{\mathrm{cb}}` tetap |
| Kadison's inequality | Ketaksamaan Kadison | — |
| Stinespring's dilation theorem | Teorema Dilasi Stinespring | — |
| dilation | dilasi | ruang dan isometri dilasi tetap dibedakan |
| operator-valued map | pemetaan bernilai operator | — |
| preordering | praurutan | bentuk terakui; bukan `praorder` dalam prosa utama |
| completely positive lifting | pengangkatan positif lengkap | pengangkatan tidak harus multiplikatif |
| completely positive lifting property | sifat pengangkatan positif lengkap | — |
| nuclear | nuklir | sifat aljabar-$C^*$, bukan “inti” |
| algebraic tensor product | hasil kali tensor aljabar | simbol `\odot` tetap |
| C-star norm | norma-$C^*$ | — |

## Batas makna yang wajib dijaga

1. **`extension` bukan selalu `perpanjangan`.** Seluruh pemakaian teknis Bab
   16 adalah ekstensi aljabar/Busby/barisan eksak, sehingga bentuknya
   `ekstensi`. `Perpanjangan` tetap khusus bagi extension of a functional pada
   bab lain.
2. **Dua relasi uniter harus dibedakan.** Gunakan `ekuivalen secara uniter`
   untuk kesamaan tepat setelah konjugasi, dan `ekuivalen uniter secara
   esensial` untuk kesamaan modulo operator kompak. Setelah koreksi tipe,
   definisi pertama memakai `S=U^*TU` dan definisi kedua
   `S-U^*TU\in\ofml K(H)` ketika `U:H\to K`.
3. **`section` bersifat kategoris.** Dalam diagram Toeplitz, `T` merupakan
   penampang/invers kanan dari `\beta`; kata itu bukan “bagian” dokumen.
4. **Orientasi ekstensi tidak dinormalkan diam-diam.** Frasa “extension of
   `K` by `A`”, urutan `0\to K\to E\to A\to0`, dan pasangan `(E,\phi)`
   harus tetap dapat dicocokkan satu per satu.
5. **`pullback` dan `lifting` berbeda.** `Tarik balik` ialah objek universal;
   `pengangkatan` ialah peta menuju aljabar sebelum hasil bagi. Jangan gunakan
   satu istilah untuk keduanya.
6. **`unit`, `unital`, dan `matrix unit` berbeda.** `Beridentitas` menerjemahkan
   *unital*; `unit matriks standar` adalah elemen `e^{jk}`, bukan matriks
   identitas.
7. **Tingkat positivitas harus tetap berjenjang.** `Positif`, `2-positif`,
   `n-positif`, dan `positif lengkap` bukan sinonim. Semua superskrip
   `\phi^{(n)}`, matriks blok, dan kuantifikasi `n\in\N` dipertahankan.
8. **`completely positive` tidak berarti multiplikatif.** Pengangkatan dalam
   kriteria semiterbelah adalah pemetaan linear beridentitas positif lengkap,
   bukan homomorfisme-$*$. Perbedaan ini menentukan split versus semisplit.
9. **`range` bersifat peka objek.** Untuk operator gunakan `jangkauan`; dalam
   pernyataan `\sigma_e(T_\phi)=\ran\phi`, prosa dapat mengatakan `citra
   \phi`, tetapi simbol `\ran\phi` tidak diubah.
10. **`proper` bersifat peka konteks.** *Proper isometry* adalah `isometri
    sejati`; ini tidak mengubah istilah `proper` yang sengaja dipertahankan
    untuk kerucut proper pada Bab 12.
11. **`abstract Toeplitz extension` dapat tidak injektif.** Jangan menyebut
    setiap pemetaan itu anggota `\ext A`; kelas `\ext A` pada bagian ini
    memakai monomorfisme beridentitas.
12. **Pilihan `H\oplus H\cong H` harus eksplisit tetapi tidak menjadi isi
    baru.** `\nu` dan `\rho` bergantung pada satu isomorfisme terpilih;
    proposisi well-definedness memastikan kelas hasil tidak bergantung pada
    pilihan tersebut.

## Koreksi sumber yang mengikat turunan

Keputusan berikut berasal dari review matematis lengkap
`qa/CH16_PRETRANSLATION_MATH_REVIEW.md`. Sumber beku tidak diubah.

1. Rekaman 13: pisahkan `\begin{prop}` dari kata pembuka.
2. Rekaman 42--58: dengan `U:H\to K`, gunakan `U^*TU` dalam kedua rumus
   ekuivalensi; `UTU^*` salah tipe.
3. Rekaman 61--63: nyatakan ruang-ruang Hilbert terpisahkan berdimensi tak
   hingga agar klasifikasi spektrum esensial mempunyai unitary pembanding.
4. Rekaman 254--257: pulihkan `\ofml Q(H^2)` dan salah ketik “an
   isomorphism”.
5. Rekaman 298--305: `T`, bukan `\beta`, adalah penampang/invers kanan karena
   `\beta\circ T=I`.
6. Rekaman 313: pulihkan nomor teorema Douglas `7.26`.
7. Rekaman 344--345: gunakan dua kali
   `\pi_1(\C\setminus\{0\})`.
8. Rekaman 407: ganti kait indeks basi “setelah bagian 9.2” dengan bentuk
   netral “mulai bagian Penjumlahan Ekstensi” (lokasi edisi: setelah 16.2).
9. Rekaman 446: hapus kurung `)` berlebih dari pembatasan `\psi|_{\ofml K}`.
10. Rekaman 549: kodomain `\pi_2` adalah `A`, bukan `\ofml A`.
11. Rekaman 563: namai operator uniter yang hilang sebagai `U`.
12. Rekaman 622 dan 633: perbaiki `Topelitz` menjadi `Toeplitz` dalam kait
    indeks.
13. Rekaman 886--891: `\phi` dalam Teorema Voiculescu harus merupakan
    pemetaan linear beridentitas positif lengkap.
14. Rekaman 914--924: `\tau` adalah monomorfisme-$*\,$ beridentitas dan
    `\widetilde\tau` adalah pengangkatan linear beridentitas positif lengkap,
    bukan pengangkatan homomorfik-$*$.

Butir 4 memuat dua perbaikan mekanis terpisah; keseluruhan keputusan tersebut
bersesuaian dengan kelompok ledger `CH16-C001` sampai `CH16-C015`. Setiap
perubahan harus dicatat dengan rekaman sumber, bentuk sebelum/sesudah, alasan,
dan lokasi target.

## Penjagaan struktur dan serah-terima produksi

Pertahankan tepat empat bagian aktif, 142 lingkungan, 36 label unik, 28
rujukan, 59 sitasi, 107 kait indeks, 29 kait `\df`, 702 permukaan matematika
aktif, 31 bukti, 15 contoh, satu tag manual `(1)`, dan ketiadaan latihan,
petunjuk, jawaban, serta solusi. Pertahankan semua diagram XY, arah panah,
objek, simbol, dan pengenal. Jangan mengaktifkan judul produk tensor yang
dikomentari.

Saat target lengkap dirakit, lakukan pemeriksaan istilah khusus untuk dua
bentuk ekuivalensi uniter, seluruh keluarga Toeplitz, `ekstensi` versus
`perpanjangan`, `tarik balik` versus `pengangkatan`, semua tingkat
positivitas, dan `semiterbelah` versus `terbelah`. Varian pengenalan membantu
pencarian residu; varian itu bukan izin untuk mengganti-ganti prosa.

Kredit John M. Erdman, CC BY-SA 4.0, pemberitahuan perubahan, ShareAlike,
non-endorsement, dan provenance model persis `OpenAI Codex gpt-5.6-sol,
Ultra` tetap utuh. Tidak ada kontak upstream selama produksi.
