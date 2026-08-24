# Rencana terminologi Bab 14

Tanggal: 2026-08-24  
Unit: `FAOA-2015-CH14`  
Sumber: `source/upstream/multiplier_algebras.tex`

## Batas dan dasar keputusan

Rencana ini berlaku untuk seluruh 687 rekaman sumber Bab 14. Identitas sumber
beku ialah 30.579 byte dengan SHA-256
`d9bf8cf31a6e18a779863dcb397863430fe2daac9031a86354ce2274b42def7c`.
Keputusan memakai istilah edisi yang telah diakui sampai Bab 13, makna
matematis setempat, dan pemeriksaan terminologi Indonesia yang sudah dilakukan
serta dicatat di `qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md`. Saksi
Indonesia tersebut cukup untuk bentuk inti seperti `ruang Hilbert`, `ruang
Banach`, `operator kompak`, `adjoin`, dan `aljabar-$C^*$`, tetapi tidak
menjadi bukti frekuensi untuk kosakata khusus modul Hilbert/aljabar pengali.
Istilah khusus di bawah ini karena itu dipilih secara jujur berdasarkan makna,
morfologi ilmiah Indonesia, dan konsistensi internal edisi.

## Judul

| Sumber | id-ID yang dipakai |
|---|---|
| `MULTIPLIER ALGEBRAS` | `ALJABAR PENGALI` |
| `Hilbert Modules` | `Modul Hilbert` |
| `Essential Ideals` | `Ideal Esensial` |
| `Compactifications and Unitizations` | `Kompaktifikasi dan Unitalisasi` |

## Istilah terkendali

| Istilah sumber | Bentuk id-ID pilihan | Varian pengenalan / catatan |
|---|---|---|
| Hilbert `$A$`-module | modul Hilbert-`$A$` | mengikuti morfologi TeX edisi; jangan membalik menjadi “modul `$A$` Hilbert” |
| `$A$`-module | modul-`$A$` | mempertahankan parameter aljabarnya |
| semi-inner product `$A$`-module | modul-`$A$` hasil kali dalam semu | mewarisi `hasil kali dalam semu` |
| inner product `$A$`-module | modul-`$A$` hasil kali dalam | — |
| pre-Hilbert `$A$`-module | modul pra-Hilbert-`$A$` | `modul pre-Hilbert` hanya varian pencarian |
| `$A$`-valued (semi-)inner product | hasil kali dalam (semu) bernilai-`$A$` | — |
| `$A$`-linear | linear-`$A$` | mempertahankan urutan bentuk sumber |
| Hilbert `$A$`-module morphism | morfisme modul Hilbert-`$A$` | mewarisi `morfisme` |
| adjointable | dapat diadjoinkan | sifat; `adjoin` tetap nomina |
| adjoint | adjoin | bentuk edisi yang sudah diakui; `adjoint` dan `operator pendamping` hanya varian pengenalan |
| opposite algebra | aljabar lawan | `aljabar oposisi` hanya varian pencarian |
| antihomomorphism | antihomomorfisme | — |
| anti-isomorphism | antiisomorfisme | memakai bentuk Bab 4 yang telah diakui |
| compact operator (module convention) | operator kompak | wajib mempertahankan peringatan bahwa anggota `\ofml K(V)` tidak harus kompak sebagai operator ruang Banach |
| principal ideal | ideal utama | mewarisi bentuk Bab 5 |
| essential ideal | ideal esensial | — |
| annihilator | anihilator | mewarisi bentuk Bab 6 |
| zero set | himpunan nol | — |
| compactification | kompaktifikasi | sudah muncul dalam materi yang diakui; bukan `pemadatan` |
| one-point compactification | kompaktifikasi satu titik | — |
| essential compactification | kompaktifikasi esensial | definisi mensyaratkan citra padat |
| unitization | unitalisasi | mewarisi Bab 12 |
| essential unitization | unitalisasi esensial | jangan meratakan menjadi unitalisasi sembarang |
| maximal essential unitization | unitalisasi esensial maksimal | urutan pengubah mempertahankan hierarki konsep |
| embedded / embedding | dibenamkan / pembenaman | mewarisi `pembenaman alami`; `penanaman` hanya varian pengenalan |
| nondegenerate | tak terdegenerasi | mewarisi istilah representasi Bab 13 |
| multiplier algebra | aljabar pengali | `multiplier` hanya varian pencarian |
| left multiplication operator | operator perkalian kiri | mewarisi Bab 12 |

## Penjagaan makna wajib

1. Konvensi modul kanan memakai hasil kali dalam yang linear pada variabel
   kedua dan linear konjugat pada variabel pertama. Semua kalimat dan rumus
   yang menjelaskan pembalikan konvensi harus tetap ada.
2. Definisi `adjointable` dimulai dari suatu fungsi, bukan dari operator linear
   terbatas. Sifat linear, linear-`A`, dan keterbatasannya merupakan konsekuensi
   proposisi berikutnya dan tidak boleh disisipkan ke dalam definisi.
3. `\Theta_{v,w}\colon W\to V`, sehingga keluarga yang benar ialah
   `\ofml K(W,V)`. Token indeks generik `\ofml K(V,W)` tidak mengubah arah ini.
4. Sebutan “operator kompak” untuk anggota `\ofml K(V)` adalah konvensi yang
   dikritik oleh sumber. Terjemahan harus mempertahankan contoh identitas yang
   tidak kompak dan tidak boleh menyatakan kekompakan operator Banach.
5. `essential`, `maximal`, dan `unital` adalah sifat berbeda. Pertahankan
   seluruh implikasi dan definisi, termasuk peringatan bahwa pemakaian istilah
   unitalisasi/kompaktifikasi untuk objek yang sudah beridentitas/kompak adalah
   konvensi nonstandar pengarang.
6. `embedding` pada aljabar ialah homomorfisme-`$*$` injektif; pada ruang
   topologis ialah homeomorfisme ke suatu subruang. Gunakan nomina yang sama
   tetapi jangan menyamakan jenis petanya.
7. `M(A)=\ofml L(A)` adalah aljabar semua operator yang dapat diadjoinkan pada
   modul Hilbert `$A$`; jangan menggantinya dengan aljabar operator kompak.
8. Semua label, rujukan, sitasi, indeks, rumus, dua latihan, dua petunjuk bukti,
   dan kekosongan jawaban/solusi hulu harus dipertahankan.

## Koreksi sumber yang harus tampak transparan

- Baris sumber 78: ganti variabel tak terdefinisi `f` dengan `\phi`.
- Baris 233: inklusi yang benar ialah `\iota\colon W\sto V`, yaitu
  `J_0\hookrightarrow A`, bukan `A\to J_0`.
- Perbaikan mekanis: spasi `means, when`, tanda hubung `C^*$-algebra`, titik
  sesudah kalimat baris 209, `has led`, penyatuan fragmen kalimat baris
  413–414, dan koma yang mengapit “jika ada” pada baris 641 serta 645.

Sumber Inggris beku tidak diubah. Setiap perbaikan pada turunan akan direkam
lagi dengan rentang sumber/target dan hash dalam ledger koreksi Bab 14.

## Kontrak admisi

Gunakan bentuk pilihan secara konsisten, simpan varian hanya untuk pencarian,
dan tambahkan ID istilah stabil pada rekonsiliasi backend. Jangan mengubah
kredit John M. Erdman, lisensi CC BY-SA 4.0, pemberitahuan perubahan,
non-endorsement, atau provenance model persis `OpenAI Codex gpt-5.6-sol,
Ultra`.
