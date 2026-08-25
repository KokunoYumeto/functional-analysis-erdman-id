# Kontrak berkas solusi O001

Setiap bab latihan memiliki satu berkas `mastery/id-ID/solutions-chNN.tex`.
Berkas itu merupakan komponen asli terpisah berlisensi CC BY-SA 4.0; bukan
bagian dari teks Erdman. Jangan mengubah berkas sumber atau reader yang telah
diterima.

Header berkas harus menyatakan bab, provenans
`OpenAI Codex gpt-5.6-sol, Ultra, atas arahan pengguna`, CC BY-SA 4.0,
non-endorsement, dan jumlah solusi. Setelah satu judul bab, setiap solusi
mengikuti bentuk persis ini:

```tex
% O001-SOLUTION-ID: O001-FAOA-2015-CHxx-EX-nnn-SOLUTION
% SOURCE-EXERCISE-ID: FAOA-2015-CHxx-NODE-nnnn
% STATEMENT-TARGET-SHA256: <64 hex>
\begin{o001solution}
  {O001-FAOA-2015-CHxx-EX-nnn-SOLUTION}
  {FAOA-2015-CHxx-NODE-nnnn}
  {<64 hex>}
\begin{o001statement}
<isi lingkungan exer yang diterjemahkan, tanpa \begin{exer}/\end{exer}>
\end{o001statement}
\begin{o001answer}
<jawaban ringkas atau klaim akhir yang tepat>
\end{o001answer}
\begin{o001proof}
<argumen lengkap dalam Bahasa Indonesia>
\end{o001proof}
\end{o001solution}
```

Gunakan persis ID, urutan, pernyataan, dan hash dari
`mastery/O001_EXERCISE_INVENTORY.jsonl`. Petunjuk sumber boleh digunakan dan
harus diakui sebagai petunjuk sumber, tetapi jangan dinyatakan sebagai solusi
sumber. Pertahankan macro matematika edisi (`\K`, `\R`, `\vc`, `\ip`, dan
sebagainya), label, serta referensi yang diperlukan agar master pendamping
dapat memakai preamble edisi.

Syarat isi:

- `o001answer` harus cukup spesifik untuk pemeriksaan cepat, bukan sekadar
  “terbukti”;
- `o001proof` harus menunjukkan semua implikasi, kasus batas, konstruksi,
  konvergensi, atau estimasi yang dibutuhkan;
- hipotesis tidak boleh diperkuat diam-diam dan hasil yang lebih lanjut dalam
  urutan buku tidak boleh dipakai tanpa pembuktian lokal;
- jika latihan meminta contoh atau solusi eksplisit, berikan objeknya lalu
  verifikasi semua sifat;
- jika ada beberapa jawaban sah, nyatakan ruang kebebasannya;
- jangan memakai placeholder, “jelas”, “serupa”, atau rujukan eksternal sebagai
  pengganti langkah inti;
- akhiri dengan pemeriksaan langsung bila kesalahan tanda, domain, norma,
  adjoint, atau konvensi Fourier mudah terjadi.

Pemeriksaan integrasi akan menolak ID/hash yang hilang atau ganda, pernyataan
yang tidak cocok dengan inventaris, lingkungan tak seimbang, formula yang
tidak dapat dikompilasi, residu bahasa non-Indonesia, dan solusi yang belum
memakai status pemeriksaan eksplisit di backend.
