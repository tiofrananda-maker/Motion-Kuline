# Aturan Final Video Kuliner (disetujui Tio, 15 Okt 2026)

Acuan visual: video Ayam Panggang Mbah Dinem v3 (contoh/mbah-dinem, tidak disertakan di repo publik). Semua video baru WAJIB mengikuti ini.

## Format
- Reels 9:16, 1080x1920, 30 fps. Ekspor IG 1080p (-14 LUFS) + preview 720p.
- Durasi mengikuti isi brief (Mbah Dinem: 1:42). Potong jeda dan ucapan yang diulang.

## Struktur cerita (urutan mengikuti brief)
1. Hook 3–5 dtk: kalimat paling menarik + judul pembuka.
2. Nama tempat + "khas …" (identitas dari brief).
3. Proses / keunikan / value utama brief.
4. Menu & harga, menu baru.
5. Suasana / dine-in / fasilitas (parkir dll).
6. Info: jam buka, reservasi + nomor kontak, info musiman (Lebaran, buka puasa).
7. Cicip: footage makan WAJIB banyak (sobek, gigit, seruput, minum), reaksi "juicy / besar banget".
8. Rekomendasi + ajakan, lalu alamat lengkap + "Simpan." di akhir.

## Progress bar bab (WAJIB, selalu tampil)
- Dari frame pertama sampai terakhir, di atas (top 96px, kiri-kanan 72px).
- Garis per bab (track putih 42%, isi Cabai #E4572E, tinggi 9px), di bawahnya nomor serif miring Kunyit + nama bab huruf kapital: "01 · KHAS KLATEN".
- 5–6 bab, contoh: KHAS …, PROSES, MENU, SUASANA, CICIP, LOKASI.

## Tipografi
- Font Apple: SF Pro Display/Text (render pakai Inter Display/Inter).
- Pasangan serif miring: DM Serif Display Italic (serif brand dari brief; padanan "New York" Apple).
- Judul pembuka = formula sans + serif miring: "Ayam *Ajaib*" (kata pertama sans tebal putih, kata kunci serif miring Kunyit), eyebrow kecil "REVIEW KULINER", sub satu baris.
- Kata kunci di tiap teks pakai serif miring (tulis *kata* di CUES).
- Eyebrow: huruf kapital 30px, spasi 0.16em, Kunyit, dengan garis aksen kecil di depannya.

## Teks di layar
- TANPA latar/kotak apa pun. Keterbacaan dari bayangan lembut berlapis.
- Hanya poin penting (bukan subtitle penuh).
- Posisi berpindah-pindah: TL, TR, ML, MR, LL, LR, C. Hindari wajah dan produk; hindari kanan bawah (tombol IG).
- Animasi: kata masuk satu-satu (blur→tajam, naik 14px), keluar memudar 8 frame. Angka dihitung naik (10–15 menit). Daftar "tanpa …" dicoret garis Cabai satu per satu. Harga baris demi baris.
- Warna: putih teks utama, Kunyit #F4A62A untuk harga/aksen, Krem #FFF8EF untuk sub, Cabai #E4572E untuk coretan/progress.

## Filter (FIX, jangan diubah)
Remotion Effects di src/grade.ts: exposure -0.25, shadows -0.1 / highlights -0.35, contrast 1.12, white balance +0.26 (hangat), tint sogan #7A4A24 8%, vibrance 0.06, vignette 0.5. Kesan: kuliner resto besar, agak gelap, hangat nuansa Jawa, makanan & wajah tetap segar.

## Audio & SFX
- VO = suara asli di klip, -14 LUFS. Suara asli B-roll (desis bakaran, suasana) dicampur ~15 dB di bawah VO.
- SFX tiap teks masuk (volume 0.22–0.45): whoosh, card-slide, tick, klik saat dicoret, koin di harga, gelas di minuman, pop di angka, chime + bonang di penutup, tick halus tiap ganti bab.
- Musik: tidak dari sini; Tio tambah sendiri saat upload.

## Tanpa brief / footage sudah dipotong (Tio 2026-10-16)
- **Tidak ada brief PDF**: Claude menyusun alur sendiri dengan struktur cerita di atas, isinya hanya dari footage (ucapan VO + yang terlihat: papan nama, menu, harga di kertas/spanduk). Bagian yang tidak ada bahannya dilewati, jangan dikarang. Nama tempat, alamat, jam, harga hanya ditulis kalau terdengar/terlihat jelas; yang ragu dilaporkan ke Tio. Tanpa brief tidak ada larangan khusus, tapi tetap tidak boleh klaim yang tidak ada di footage.
- **Kenali kondisi footage dulu** (lihat sheet thumbnail + transkrip):
  - *Mentah* (banyak klip pendek, ada take ulang/gagap, durasi total jauh di atas 60–90 dtk): pilih take terbaik, susun ulang sesuai struktur cerita.
  - *Sudah dipotong Tio* (satu/beberapa file yang sudah berurutan, potongan rapat, ada alur): JANGAN susun ulang. Pertahankan urutan dan potongan Tio, hanya rapikan (buang jeda/gagap yang tersisa), lalu tambahkan grade, teks, progress bar bab (bab ditentukan dari isi tiap bagian), SFX.
  - Campuran (sebagian sudah urut, ada klip tambahan): pakai urutan Tio sebagai tulang punggung, klip tambahan jadi B-roll.
- Laporkan di akhir: footage dianggap mentah atau sudah dipotong, dan alur yang dipakai.

## Patuh brief
- Semua poin wajib brief harus tampil (teks atau VO). Info (alamat, jam, nomor) disalin persis dari brief.
- Hal yang dilarang brief tidak boleh muncul di teks. Contoh: dilarang sebut penjualan → "best seller" di layar diganti "Favorit"; kalau VO-nya menyebut, tanyakan ke Tio.
- Jangan mengarang klaim yang tidak ada di brief/footage.
