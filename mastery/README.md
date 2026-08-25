# Lapisan penguasaan dan solusi O001

Folder ini memuat pendamping yang ditulis terpisah untuk edisi Bahasa
Indonesia buku John M. Erdman, *Functional Analysis and Operator Algebras: An
Introduction* (4 Oktober 2015). Pernyataan latihan tetap merupakan materi
sumber Erdman. Solusi, pemeriksaan penguasaan, dan penjelasan tambahan di sini
bukan tulisan Erdman dan tidak menyiratkan dukungan atau persetujuan beliau
atau Portland State University.

Materi pendamping ditulis dengan bantuan **OpenAI Codex gpt-5.6-sol, Ultra**
atas arahan pengguna. Materi ini dilisensikan CC BY-SA 4.0; atribusi, catatan
perubahan, ShareAlike, hak komponen, dan pemisahan provenans harus tetap
dipertahankan.

## Cakupan wajib

1. solusi yang diperiksa untuk seluruh 52 lingkungan latihan sumber;
2. dukungan penguasaan untuk sekumpulan hasil kerja-pembaca yang dipilih karena
   sentral secara matematis;
3. hubungan stabil dan dapat dibaca mesin dari latihan atau hasil sumber ke
   solusi asli, prasyarat, formula, petunjuk sumber, dan permukaan reader;
4. integrasi aditif tanpa mengubah byte reader teks-sumber atau reader HTML
   yang telah diterima.

ID solusi latihan memakai bentuk
`O001-FAOA-2015-CHxx-EX-nnn-SOLUTION`, persis seperti kontrak yang sudah
diantrekan dalam `backend/exercise_support.jsonl`. Setiap solusi harus memuat
ID latihan sumber, urutan sumber, pernyataan Bahasa Indonesia yang terikat pada
hash fragmen, provenans asli, status pemeriksaan, dan relasi hak. Hasil
kerja-pembaca terpilih memakai namespace `O001-FAOA-2015-CHxx-RW-nnn-*` agar
tidak disamakan dengan latihan eksplisit.

## Gerbang penerimaan

- inventaris 52/52, ID unik, dan urutan bab cocok dengan backend yang diterima;
- setiap pernyataan dan petunjuk sumber cocok byte demi byte dengan rentang
  target terjemahan dan hash yang telah dibekukan;
- argumen lengkap, tanpa mengandalkan hasil yang belum tersedia, dengan semua
  kasus batas dan hipotesis digunakan secara eksplisit;
- rumus dapat dikompilasi dan maknanya cocok dengan sumber;
- pemeriksaan matematis independen serta uji regresi yang sengaja menolak
  solusi salah representatif;
- atribusi, CC BY-SA 4.0, pemisahan penulis, dan non-endorsement tampak pada
  reader dan backend;
- build deterministik, QA visual/aksesibilitas, receipt, commit/push sempit,
  dan pembacaan ulang byte publik pada batas yang layak.

`O001_EXERCISE_INVENTORY.jsonl` adalah inventaris turunan deterministik; berkas
itu tidak berisi solusi. Solusi produksi disimpan berurutan per bab di
`id-ID/`, lalu diikat ke backend dan reader hanya setelah pemeriksaan lulus.
