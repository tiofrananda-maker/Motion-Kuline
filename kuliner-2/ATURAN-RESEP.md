# Aturan Kuliner-2: Resep Estetik (acuan referensi Tio, 19 Okt 2026)

Acuan: reels resep "Corndog Hack" (akun tummyyammy) yang Tio kirim. **Hasil akhir wajib mirip persis referensi, dengan footage apa pun.**
Template ini terpisah dari `kuliner/` (review tempat makan). Jangan campur gaya keduanya.

## Format
- Reels 9:16, 1080x1920, 30 fps. Durasi 45–75 dtk (referensi 60 dtk). Ekspor 1080p -14 LUFS + preview 720p.
- Potongan hard cut saja. TANPA transisi, TANPA zoom digital, TANPA progress bar, TANPA SFX, TANPA kotak/latar teks.

## Struktur (urutan referensi)
1. **0–1,5 dtk: hero shot** hasil akhir tertata (sudut ±45°, tangan menabur garnish/menuang saus). VO hook berupa pertanyaan pendek ("Corndog cuma 4 bahan, emang bisa?"). Judul pembuka tampil.
2. **1,5–3 dtk: money shot** (keju ditarik, dibelah, saus meleleh), judul masih tampil sampai ±2,7 dtk.
3. **Cerita singkat** 1–2 kalimat (kenapa bikin ini) di atas shot plating/bahan.
4. **Bahan** disebut satu-satu, shot bahan tertata di meja (mangkuk kaca, talenan).
5. **Proses berurutan**, satu langkah = satu shot close-up tangan 2–4 dtk. VO memakai urutan "pertama… kemudian… terus… terakhir…".
6. Produk/bumbu sponsor (kalau ada): kemasan dipegang ke kamera 2–3 dtk, lalu dituang.
7. **Masak** (goreng/panggang) boleh gerak lambat 0,5x, angkat dengan capit.
8. **Plating & saus** (gerak lambat untuk tuangan).
9. **Hasil**: money shot lagi + VO tekstur ("crispy di luar, meleleh di dalam").
10. **Penutup**: kalimat manis + hero wide dengan semua sajian (dan produk). Ajakan komentar tampil dari potongan shot terakhir sampai akhir; VO mengucapkan ajakannya.
- Tempo potongan 1,5–3,5 dtk per shot, mengikuti kalimat VO. Shot yang dipilih: close-up, ruang tajam sempit (latar blur), cahaya hangat dari samping.
- Footage tidak lengkap: bagian yang tidak ada bahannya dilewati, jangan dipaksa. Hero/money shot wajib ada di awal; kalau tidak ada, pakai shot hasil akhir terbaik.

## Teks di layar (HANYA 4 elemen, ukuran sudah dikalibrasi ke referensi, jangan diubah)
| Elemen | Gaya | Posisi & waktu |
|---|---|---|
| Nama akun | Comfortaa SemiBold 31px, krem, huruf kecil | atas tengah (top 206), sepanjang video |
| Judul pembuka | eyebrow Inter Display Medium Italic 24px kapital ("4 INGREDIENTS, 1 GENIUS") + judul DM Serif Display 60px ("Corndog Hack") | tengah layar, 0 → ±2,7 dtk, hilang memudar 7 frame |
| Caption VO | Inter Italic 25px, **huruf kecil semua**, tanpa titik/koma (tanda tanya tetap) | tengah layar, kata muncul satu-satu (menumpuk), frasa baru menggantikan frasa lama |
| Ajakan komentar | "COMMENT" kecil / **"Kata"** DM Serif 75px dalam tanda kutip tebal / "AND GET THE RECIPE" | tengah layar, dari potongan segmen `cta` sampai akhir, muncul cepat 3 frame |
- Caption tidak tampil saat judul dan ajakan tampil (seperti referensi).
- Caption = **persis ucapan VO** (aturan keras). Maks 6 kata / 34 karakter per frasa, potong di jeda dan tanda baca.
- Eyebrow & ajakan boleh bahasa Inggris seperti referensi (judul resep pendek, 1–3 kata, kata kunci produk). Kata ajakan = nama menu singkat ("Corndog").
- Semua teks putih/krem dengan bayangan tipis. Tidak ada warna aksen.

## Grade (src/grade.ts)
Terang lembut, hangat keemasan (cahaya jendela sore), kontras rendah (0,92), bayangan diangkat (+0,14), sorotan ditahan (-0,22), saturasi 0,94, tint krem-peach 6%, tanpa vignette. Kesan: dapur rumahan estetik, bersih, hangat. Kalau footage sudah terang/hangat, kurangi temperature, jangan ditambah.

## Audio
- **VO narasi** santai bahasa sehari-hari ("doi", "satset", "nendang"), -14 LUFS. Sumber VO, pilih yang ada:
  1. File VO terpisah di folder footage (`vo.m4a`/`vo.mp3`/`vo.wav`), kunci `vo` di edl. (Paling mirip referensi.)
  2. Suara orang di klip itu sendiri (kunci klip).
  3. Tidak ada VO: video ASMR. Segmen pakai `["-",0,durasi]`, suara asli klip (desis, kriuk, tuang) penuh, tanpa caption; judul + ajakan tetap.
- Suara asli klip di bawah VO (~15 dB lebih pelan). Musik lembut: Tio tambah sendiri saat upload.

## Isi teks per video (edit/resep.json)
```json
{"handle": "akun_tio", "judul": {"atas": "4 ingredients, 1 genius", "teks": "Corndog Hack", "sampai": 2.7},
 "cta": {"atas": "comment", "kata": "Corndog", "bawah": "and get the recipe", "mulai": null}, "huruf_kecil": true}
```
- `handle` kosong = nama akun tidak tampil. `cta.mulai` null = otomatis di awal segmen `cta`.
- Judul diambil dari VO/footage (jumlah bahan, nama menu). Jangan mengarang klaim.
