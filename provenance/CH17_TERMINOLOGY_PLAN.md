# Rencana terminologi dan batas editorial Bab 17

Tanggal: 2026-08-24  
Unit: `FAOA-2015-CH17`  
Sumber: `source/upstream/K0_functor.tex`, rekaman 1--1.362

## Identitas dan dasar keputusan

Rencana ini mencakup keseluruhan sumber: 59.639 byte, 1.362 rekaman CRLF,
SHA-256
`e8ebcaa4e5dbc1cc9b907edb235465610f3bd61e0bfa1ce2f1b5b26e9abf8c6a`.
Delapan bagian aktifnya membangun relasi ekuivalensi proyeksi, semigrup kelas
proyeksi, konstruksi Grothendieck, funktor `K_0` untuk aljabar beridentitas dan
tak beridentitas, sifat eksak/stabilitas, limit induktif, dan diagram Bratteli.

Dasar konsistensi edisi adalah `backend/terminology.jsonl`, Bab 2 untuk
`funktor`, `funktor kovarian`, dan `funktor pelupa`; Bab 5 untuk `ekuivalen
secara uniter`; Bab 6 untuk `transformasi alami`; Bab 7 untuk `serupa`; Bab 10
untuk `barisan induktif`, `limit induktif`, dan `limit langsung`; Bab 12 untuk
`unitalisasi` dan `eksak terbelah`; Bab 15 untuk `lintasan`, `homotop`, dan
`aljabar Calkin`; serta Bab 16 untuk `semigrup` dan `multiplisitas`.

Istilah terakui berikut dipakai kembali tanpa variasi prosa: `aljabar-$C^*$`,
`beridentitas`, `tak beridentitas`, `proyeksi`, `uniter`, `swaadjoin`,
`isometri parsial`, `serupa`, `ekuivalen secara uniter`, `matriks diagonal`,
`matriks blok`, `jumlah langsung`, `representasi setia`,
`homomorfisme-$*\,$`, `barisan eksak`, `unitalisasi`, `eksak terbelah`,
`semigrup`, `funktor`, `funktor kovarian`, `funktor pelupa`, `transformasi
alami`, `lintasan`, `homotop`, `limit induktif`, `limit langsung`, `pembenaman`,
`aljabar Calkin`, dan `multiplisitas`.

Pemeriksaan terminologi Indonesia eksternal yang telah dicatat pada
`qa/CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md` mendukung kosakata inti
analisis fungsional, tetapi bukan bukti frekuensi bagi istilah khusus teori-K,
Grothendieck, atau Bratteli. Pilihan khusus di bawah didasarkan pada makna
matematis, morfologi bahasa Indonesia, dan konsistensi internal edisi; dokumen
ini tidak mengarang klaim konvensi lapangan eksternal.

## Judul terkendali

| Sumber | Bentuk id-ID pilihan | Catatan |
|---|---|---|
| `THE K_0-FUNCTOR` | `FUNKTOR K_0` | simbol `K_0` dipertahankan |
| `Equivalence Relations on Projections` | `Relasi Ekuivalensi pada Proyeksi` | bukan “kesetaraan” |
| `A Semigroup of Projections` | `Semigrup Proyeksi` | komutativitas ketat diperbaiki menurut ledger |
| `The Grothendieck Construction` | `Konstruksi Grothendieck` | nama diri dipertahankan |
| `The K_0-Group for Unital C*-Algebras` | `Grup K_0 untuk Aljabar-$C^*$ Beridentitas` | `unital` -> `beridentitas` |
| `K_0(A)---the Nonunital Case` | `K_0(A)---Kasus Tak Beridentitas` | bukan “tanpa unit” |
| `Exactness and Stability Properties of the K_0 Functor` | `Sifat Keeksakan dan Stabilitas Funktor K_0` | bentuk judul menghindari ambiguitas `half exact` |
| `Inductive Limits` | `Limit Induktif` | bentuk terakui Bab 10 |
| `Bratteli Diagrams` | `Diagram Bratteli` | nama diri dipertahankan |

## Istilah terkendali: proyeksi dan relasi ekuivalensi

| Sumber | Bentuk id-ID pilihan | Varian pengenalan / penjagaan |
|---|---|---|
| K-theory | teori-K | tanda hubung dipertahankan |
| K0-functor | funktor `K_0` | bukan fungsi numerik biasa |
| equivalence relation | relasi ekuivalensi | — |
| similar / similarity | serupa / keserupaan | bentuk terakui Bab 7 |
| unitarily equivalent | ekuivalen secara uniter | bentuk terakui Bab 5 |
| polar decomposition | dekomposisi polar | — |
| homotopic / homotopy | homotop / homotopi | predikat versus nomina |
| Murray--von Neumann equivalent | ekuivalen Murray--von Neumann | varian pengenalan: ekuivalen dalam pengertian Murray--von Neumann |
| Murray--von Neumann equivalence | ekuivalensi Murray--von Neumann | — |
| partial isometry | isometri parsial | bentuk terakui |
| implements the equivalence | merealisasikan ekuivalensi | jangan diterjemahkan sebagai implementasi perangkat lunak |
| isometry | isometri | elemen `s` dengan `s^*s=1` |
| nonunitary isometry | isometri tak uniter | contoh geser unilateral |
| diagonal matrix | matriks diagonal | — |
| block matrix | matriks blok | ukuran blok wajib utuh |
| conjugate transposition | transposisi konjugat | — |
| faithful representation | representasi setia | bentuk terakui |
| matrix algebra | aljabar matriks | simbol `M_n(A)` tetap |
| stabilized projection | proyeksi yang distabilkan | varian pengenalan: proyeksi stabilisasi |

## Istilah terkendali: semigrup dan Grothendieck

| Sumber | Bentuk id-ID pilihan | Varian pengenalan / penjagaan |
|---|---|---|
| semigroup | semigrup | bukan grup kecuali invers telah dibentuk |
| commutative semigroup | semigrup komutatif | pada `P_\infty` hanya modulo ekuivalensi |
| block/direct sum `p\oplus q` | jumlah blok / jumlah langsung `p\oplus q` | simbol dan urutan blok tetap |
| equivalence class | kelas ekuivalensi | subskrip `\fml D` tetap |
| Grothendieck construction | konstruksi Grothendieck | — |
| Grothendieck group | grup Grothendieck | — |
| Grothendieck map | pemetaan Grothendieck | komponen `\gamma_S` |
| cancellation property | sifat pembatalan | jangan disamakan dengan invers aditif |
| universal property | sifat universal | — |
| additive map | pemetaan aditif | — |
| Abelian group | grup Abelian | jangan gunakan `grup Abel` |
| group homomorphism | homomorfisme grup | berbeda dari homomorfisme-$*$ |
| Hint for proof | Petunjuk untuk bukti | bentuk terkendali untuk semua 16 petunjuk |
| forgetful functor | funktor pelupa | bentuk terakui Bab 2 |
| natural transformation | transformasi alami | bentuk terakui Bab 6; kenali `transformasi natural` |
| nonnegative integers | bilangan bulat tak negatif | sumber menulis `\mathbb Z^+=\{0,1,2,\ldots\}` |

## Istilah terkendali: funktor K0

| Sumber | Bentuk id-ID pilihan | Varian pengenalan / penjagaan |
|---|---|---|
| K0-group | grup `K_0` | — |
| stably equivalent | ekuivalen secara stabil | nomina: `ekuivalensi stabil` |
| stable equivalence | ekuivalensi stabil | jangan samakan dengan stabilitas matriks funktor |
| standard picture | gambaran standar | bukan gambar raster |
| point-norm topology | topologi norma-titik | pertahankan keluarga pseudometrik `d_a` |
| pseudometric | pseudometrik | — |
| homotopic star-homomorphisms | homomorfisme-$*\,$ yang homotop | lintasan kontinu norma-titik |
| homotopically equivalent algebras | aljabar yang ekuivalen secara homotopi | — |
| contractible | kontraktibel | untuk ruang dan aljabar; definisi objek berbeda |
| scalar mapping | pemetaan skalar | peta `s=\lambda\circ\pi` |
| scalar element | elemen skalar | syarat `s(x)=x` |
| split exact functor | funktor eksak terbelah | warisi `eksak terbelah` Bab 12 |
| half exact functor | funktor eksak separuh | kenali `funktor setengah eksak`; jangan sebut eksak penuh |
| preserves direct sums | mempertahankan jumlah langsung | — |
| stability property | sifat stabilitas | `K_0(A)\cong K_0(M_nA)` |
| quotient map | pemetaan hasil bagi | `Q`, dengan alias eksplisit `\pi:=Q` |
| canonical section | penampang kanonik | `\psi`, dengan alias eksplisit `\lambda:=\psi` |

## Istilah terkendali: limit induktif dan diagram Bratteli

| Sumber | Bentuk id-ID pilihan | Varian pengenalan / penjagaan |
|---|---|---|
| inductive sequence | barisan induktif | bukan `sistem terarah` kecuali objek indeks lebih umum |
| inductive limit | limit induktif | bentuk terakui Bab 10 |
| direct limit | limit langsung | sinonim sumber; simbol sama |
| connecting morphism | morfisme penghubung | `\phi_j` |
| canonical morphism | morfisme kanonik | `\mu_j` menuju limit |
| approximately finite-dimensional C-star-algebra | aljabar-$C^*$ berdimensi hingga secara aproksimatif | perkenalkan singkatan `aljabar-AF` |
| AF-algebra | aljabar-AF | bukan “aljabar hampir hingga” |
| continuity property of K0 | sifat kekontinuan `K_0` | persamaan limit dipertahankan |
| dyadic rational numbers | bilangan rasional diadik | — |
| multiplicity | multiplisitas | bentuk terakui; nilainya dapat nol |
| Bratteli diagram | diagram Bratteli | jumlah sisi adalah data matematika |
| partial multiplicities | multiplisitas parsial | kutipan sumber dapat dipertahankan |
| Cantor set | himpunan Cantor | — |
| CAR-algebra | aljabar CAR | uraikan sekali: Relasi Antikomutasi Kanonik |
| Canonical Anticommutation Relations | Relasi Antikomutasi Kanonik | kapitalisasi pengenalan |
| Fibonacci algebra | aljabar Fibonacci | — |

## Batas makna yang wajib dijaga

1. **Lima relasi bukan sinonim.** `Serupa`, `ekuivalen secara uniter`,
   `ekuivalen Murray--von Neumann`, `homotop`, dan `ekuivalen secara stabil`
   mempunyai hipotesis serta ruang perantara berbeda. Simbol `\sim_s`,
   `\sim_u`, `\sim`, `\sim_h`, dan `\sim_{st}` tidak boleh dipertukarkan.
2. **Ekuivalensi Murray--von Neumann bukan kongruensi perkalian.** Display
   pembuka bersifat motivasional. Terjemahan tidak boleh menyebutnya bukti
   bahwa `pq\sim qp` dari aksioma ekuivalensi yang belum didefinisikan.
3. **`P_\infty(A)` dan `D(A)` memiliki tingkat keeksakan berbeda.** Jumlah
   blok pada proyeksi hanya komutatif hingga ekuivalensi; operasi pada kelas
   `D(A)` benar-benar terdefinisi baik dan komutatif.
4. **Semigrup bukan grup.** `D(\mathbb C)` merupakan semigrup aditif bilangan
   bulat tak negatif; grup baru muncul setelah konstruksi Grothendieck.
5. **Jenis pemetaan harus mengikuti objek.** Peta antarruang proyeksi adalah
   pemetaan, peta antarkelompok `K_0` adalah homomorfisme grup, dan hanya peta
   antaraljabar-$C^*$ yang dapat disebut homomorfisme-$*$.
6. **`unital`, `unitalization`, quotient, dan section berbeda.** Gunakan
   `beridentitas`, `unitalisasi`, `pemetaan hasil bagi`, dan `penampang`.
   Ikat `\pi:=Q` dan `\lambda:=\psi` secara eksplisit; jangan biarkan dua
   pasangan simbol tampak sebagai empat peta tanpa hubungan.
7. **Homotopi objek dan homotopi pemetaan berbeda.** Untuk elemen uniter,
   lintasan berada dalam grup uniter; untuk homomorfisme-$*$, kekontinuan
   diukur oleh topologi norma-titik.
8. **`half exact`, `split exact`, dan `exact` tidak bertingkat sebagai
   sinonim.** Gunakan `eksak separuh`, `eksak terbelah`, dan `eksak`; contoh
   kegagalan eksak penuh harus tetap tampak.
9. **Limit induktif aljabar-$C^*$ membutuhkan penutupan norma.** Gabungan
   meningkat yang belum tertutup bukan otomatis aljabar-$C^*$.
10. **AF menyatakan konstruksi limit, bukan sekadar dimensi kecil.** Bentuk
    panjang `berdimensi hingga secara aproksimatif` diperkenalkan sekali,
    lalu `aljabar-AF` dipakai konsisten.
11. **Multiplisitas dapat nol.** Matriks Bratteli berentri bilangan bulat tak
    negatif. Keberidentitasan membatasi hasil perkalian matriks, bukan membuat
    setiap entri positif.
12. **Diagram adalah data.** Setiap simpul, sisi paralel, arah panah, ukuran
    matriks, dan persamaan `\mathbf m\mathbf k=\mathbf n` atau
    `\le\mathbf n` harus tetap dapat dicocokkan dengan sumber.

## Koreksi sumber yang mengikat turunan

Keputusan berikut berasal dari review matematis lengkap
`qa/CH17_PRETRANSLATION_MATH_REVIEW.md`. Sumber beku tidak diubah.

1. Rekaman 12: hilangkan `be` berlebih pada maksud prosa “to roam”.
2. Rekaman 13--19: bingkai perhitungan stabilisasi sebagai heuristik, bukan
   konsekuensi formal relasi kongruensi.
3. Rekaman 44 dan 63--67: perbaiki artikel/konstruksi gramatikal dalam
   lokalisasi alami tanpa mengubah kuantor.
4. Rekaman 101--103: kodomain lintasan ialah `\ofml U(A)`, bukan `\mathbb T`.
5. Rekaman 367--369: jumlah blok asosiatif secara ketat tetapi komutatif hanya
   hingga ekuivalensi pada `P_\infty(A)`; `D(A)` yang menjadi semigrup
   komutatif.
6. Rekaman 390--401: `D(\mathbb C)` adalah semigrup bilangan bulat tak
   negatif, dan contoh `D(B(H))` memerlukan `H` terpisahkan berdimensi tak
   hingga.
7. Rekaman 447, 459, dan 547: pulihkan bentuk gramatikal “denoted,” “an
   Abelian group,” dan “group homomorphisms.”
8. Rekaman 655--657: peta pada keluarga proyeksi bukan homomorfisme-$*$.
9. Rekaman 741--752: identitas terakhir memakai `\psi'` yang baru
   didefinisikan.
10. Rekaman 793--850: ikat `\pi:=Q` dan `\lambda:=\psi` agar notasi
    unitalisasi tertutup.
11. Rekaman 814--822: `K_0(\phi)` adalah homomorfisme grup; perbaiki pula
    “unitization of as C-star-algebra” pada rekaman 848.
12. Rekaman 860--866: hapus variabel `q` yang tidak muncul dari deskripsi
    himpunan gambaran standar.
13. Rekaman 930--934: tambahkan hipotesis `H` berdimensi tak hingga.
14. Rekaman 1.032--1.042: ambil penutupan norma gabungan meningkat dan
    nyatakan ruang Hilbert contoh operator kompak terpisahkan berdimensi tak
    hingga.
15. Rekaman 1.093--1.104: klasifikasi konjugasi uniter berlaku bagi
    homomorfisme-$*$; namai petanya `\phi` dan pertahankan kategori itu pada
    contoh langsung sesudahnya.
16. Rekaman 1.127--1.130 serta 1.185--1.215: entri multiplisitas adalah
    bilangan bulat tak negatif.
17. Rekaman 144--145: balik arah implikasi agar benar-benar menyatakan
    kebalikan dari implikasi kedua pada Proposisi `0060221`.
18. Rekaman 175--177: balik arah implikasi agar benar-benar menyatakan
    kebalikan dari implikasi pertama pada Proposisi `0060221`.
19. Rekaman 651--652: kodomain `\tau` adalah semigrup dasar `\abs G`, karena
    nilainya `\nu(p)`, bukan elemen `K_0(A)`.
20. Rekaman 1.274: hapus `\textbf{}` kosong.

Rincian tersebut bersesuaian dengan kelompok ledger `CH17-C001` sampai
`CH17-C026`; beberapa butir ringkasan memuat lebih dari satu perbaikan
mekanis. Setiap perubahan harus dicatat dengan rekaman sumber, bentuk
sebelum/sesudah, alasan, dan lokasi target.

## Penjagaan struktur dan serah-terima produksi

Pertahankan tepat delapan bagian aktif, 206 lingkungan, 73 label unik, 47
rujukan, 12 sitasi aktif, 100 kait indeks, 24 kait `\df`, 1.051 permukaan
matematika sumber dan 1.052 permukaan target yang seluruh selisihnya
terklasifikasi, 22 bukti, 16 petunjuk bukti, 31 contoh, satu latihan, enam
komentar penunjuk bukti yang tetap nonaktif, dan ketiadaan jawaban serta
solusi. Pertahankan seluruh 15 diagram, 46 matriks blok, arah panah, jumlah
sisi, objek, simbol, dan pengenal.

Pemisahan produksi aman ialah rekaman 1--572 lalu 573--1.362. Sambungan berada
di batas bagian; tidak ada lingkungan, kalimat, rumus, diagram, label, rujukan,
atau sitasi yang terpotong. Bagian pertama memegang `\chapter`; bagian kedua
memegang `\endinput`.

Saat target lengkap dirakit, lakukan pemeriksaan istilah khusus terhadap lima
relasi ekuivalensi, `semigrup` versus `grup`, semua simbol unitalisasi,
homotopi elemen versus homotopi homomorfisme, `eksak separuh` versus `eksak
terbelah`, penutupan limit induktif, keluarga `AF/CAR/Bratteli`, dan semua
multiplisitas nol. Varian pengenalan membantu pencarian residu; varian itu
bukan izin untuk mengganti-ganti prosa.

Kredit John M. Erdman, CC BY-SA 4.0, pemberitahuan perubahan, ShareAlike,
non-endorsement, dan provenance model persis `OpenAI Codex gpt-5.6-sol,
Ultra` tetap utuh. Tidak ada kontak upstream selama produksi.
