# ATURAN PODCAST CLIPPER (gaya referensi raymondchins)

Berlaku untuk semua video di `podcast\`. Jangan diubah kecuali Tio minta ("ubah aturan podcast: …").

## 1. ATURAN KERAS: caption = persis yang diucapkan talent
- Setiap kata yang diucapkan muncul di caption, urutannya sama, bentuknya sama. `gue` tetap `gue`, `gak` tetap `gak`, `cuy` tetap `cuy`. Tidak boleh diringkas, diparafrase, dibakukan, atau ditambah kata.
- Angka ditulis angka (`10.000`, `100 ribu`, `ke-11`), bahasa Inggris ditulis ejaan aslinya (`endorse`, `niche`, `followers`).
- Cara memastikan (wajib, berurutan):
  1. `tools/words.py` (Whisper turbo + waktu per kata),
  2. `tools/crosscheck.py` (bandingkan 3 pendengar: Whisper turbo, Whisper small, Dolphin),
  3. kata yang beda antar pendengar diuji dengan `tools/pilih.py` (model akustik memilih versi yang paling cocok dengan bunyi),
  4. teks final ditulis di `edit/transkrip.json`, lalu `tools/fix.py` menghitung ulang waktu tiap kata,
  5. `tools/compile.py` harus melapor **100%** dan tidak ada "kata ucapan yang tidak ada di caption".
- Kata yang tetap meragukan (selisih skor `pilih.py` < 3) disebut di laporan akhir ke Tio, lengkap dengan detiknya.
- Hati-hati: `pilih.py` condong ke teks yang lebih pendek dan ke ejaan baku (`senang`, `benar`). Varian gaul e/a (`seneng`, `bener`) dicek dengan analisis formant vokal (F1/F2), atau dipercaya kalau Whisper sendiri menulis bentuk gaul (Whisper cenderung membakukan, jadi kalau ia menulis gaul, itu bukti kuat memang diucapkan).
- Teks yang BUKAN caption (label hook, angka besar, judul kartu berita) boleh ringkasan, tapi isinya tidak boleh bertentangan dengan ucapan.

## 2. Caption kinetik
- Muncul kata per kata tepat saat diucapkan: blur 14px ke 0, naik 14px, ±7 frame. Frasa hilang 5 frame dengan blur.
- Tanpa kotak, bayangan lembut. Posisi normal ±65% tinggi layar (y≈1240). 1–2 baris, 2–6 kata per frasa.
- Campuran gaya dalam satu frasa (tulis di `clip.json` "captions"):
  - biasa: Inter Display Bold 60px (kata penghubung),
  - `**tebal besar**`: Inter Display ExtraBold 150px rapat (kata inti),
  - `*tipis besar*`: Inter Display Light 150px (kata emosi/penekanan). **Tidak ada serif besar** untuk poin penting, semua poin penting pakai font Apple (keputusan Tio 2026-10-16),
  - `_serif miring kecil_`: Instrument Serif Italic 68px (ekor kalimat). Tetap dipakai, jangan dihilangkan,
  - `~sans miring~`: Inter Display Bold Italic 60px,
  - `^kuning^` #F5E31A: maksimal 1 kata kunci per frasa.
- Satu frasa satu kata yang ditonjolkan (besar ATAU kuning). Jangan semua kata besar.
- Di atas kartu merah: teks abu terang. Di kartu abu/foto orang: teks merah #B5161B. Adegan ikon/berita: subtitle kotak hitam kecil (Inter Medium 46px).
- Kalau footage sudah punya tulisan sendiri (screenshot chat, dll.) caption pindah `"pos": "bottom"` atau `"top"`, jangan menimpa.
- Wajah talent ada di tengah/bawah frame (video ramai-ramai, kamera jauh): `"caption_pos": "bottom"` di clip.json supaya caption tidak menutupi wajah.

## 3. Hook
- Label merah di atas (Inter Display ExtraBold 74px, huruf besar, 1–2 baris, latar #B5161B) selama 2–3 frasa pertama.
- Isinya janji/pertanyaan dari inti video (mis. "ENDORSE PERTAMAKU / DIBAYAR BERAPA?").

## 4. Visual berganti tiap 2,5–4 detik (tidak full muka talent)
- Target: 35–50% durasi berupa cutaway. Muka talent maksimal ±5 detik tanpa perubahan (zoom bergantian otomatis di tiap jump cut ikut dihitung sebagai perubahan kecil).
- **Utamakan klip video B-roll asli** (keputusan Tio 2026-10-16: "jangan gambar, kayak video pendek gitu"). Ikon garis dan gambar diam hanya cadangan kalau tidak ada klip yang cocok.
- Jenis cutaway (`clip.json` "cutaways"):
  - `video` (utama): klip B-roll stok penuh layar 1,5–3 detik, gelap sinematik, zoom pelan, blur masuk. Untuk benda/aktivitas/situasi yang disebut (bikin konten, kamera, HP, uang, makan, kerja malam). Klip horizontal diberi `"x"` (0 kiri, 0.5 tengah, 1 kanan) supaya objek masuk crop 9:16; opsi lain `start`, `rate`, `bright`.
  - `split` (DUA LAYER, permintaan Tio 2026-10-16): layar dibagi dua, talent di separuh atas dan visual nyata (klip B-roll) di separuh bawah, atau dibalik dengan `"talent": "bawah"`. Dipakai saat ekspresi talent tetap penting sambil memperlihatkan yang ia sebut (contoh, daftar pilihan, reaksi penonton). Wajah otomatis ditaruh di tengah separuhnya (framing sedang), B-roll geser masuk dari tepi layar, caption di garis tengah. Split berurutan dengan posisi talent sama menyambung jadi montase (talent diam, klip bawah berganti), cocok untuk daftar "atau A, atau B, atau C". Klip horizontal paling pas; klip potret diberi `"y"` (0 atas, 1 bawah) supaya objek masuk jendela. Di format lanskap, dua layer jadi kiri/kanan (bagian 11). Opsi lain sama dengan `video`.
  - Campur `video` penuh layar dan `split` dalam satu video (variasi). Panduan: `split` untuk momen ≥1 detik di mana talent masih bicara tentang hal itu, `video` penuh layar untuk sorotan singkat yang perlu menonjol.
  - `card` merah/abu/gelap: kalimat tanya, pernyataan penting, ketegangan sebelum jawaban, pergantian topik.
  - `stat`: angka besar kuning naik (count-up) di atas talent, saat menyebut angka penting. Jangan dobel dengan caption besar kuning yang sama.
  - `logos`: logo aplikasi/merek muncul di samping talent + asterisk merah.
  - `person`: foto + nama serif miring merah, saat menyebut tokoh.
  - `news`: kartu berita putih + sumber, saat mengutip data/berita.
  - cadangan saja: `image` (gambar diam) dan `icons` (ikon garis).
- Klip dicari otomatis (`tools/broll.py`, kata kunci bahasa Inggris di `"q"`, butuh internet). Urutan sumber: folder `FOOTAGE\<nama>\broll\` milik Tio, lalu Pexels (kalau ada PEXELS_API_KEY), Pixabay (PIXABAY_API_KEY), Mixkit, Wikimedia. Kredit tercatat di `public/broll/KREDIT.txt`.
- Setiap klip DILIHAT dulu (`tools/stills.mjs`): cocok dengan omongan, objek masuk crop, tidak ada logo/watermark/teks. Tidak cocok → ganti `q`, atau pakai kartu teks/angka. Jangan pakai klip yang tidak nyambung.
- Klip yang sama tidak dipakai dua kali dalam satu video.

## 5. Transisi dan efek (maksimal 1 per ±5 detik)
- `flash` (overexposure putih): kejutan, angka/jawaban penting, titik balik.
- `punch` (zoom masuk cepat): penekanan emosi.
- `blur` (defocus): pindah topik.
- `wipe` (lingkaran merah): masuk/keluar kartu merah.
- Kamera "zoom dinamis" (standar, permintaan Tio 2026-10-16 "zoom in dimainkan"): framing berganti tiap kalimat (≥1,2 dtk) bergiliran lebar 1.00, dekat 1.24, sedang 1.10, paling dekat 1.30, lalu didorong pelan +4,5%. Wajah dilacak (`tools/face.py`) dan digeser ke sepertiga atas saat zoom dekat.
  - Saat footage menunjukkan sesuatu (demo layar, gambar, tulisan penting) paksa lebar: frasa `{"t": "...", "z": 1.0}`.
  - `punch` di kata kunci (Ketik, Praktek, angka) = zoom cepat +12% dengan sedikit motion blur.
  - Sumber resolusi rendah (mis. download TikTok 576x1024): zoom maksimal ±1.3 supaya tidak pecah.
- `defocus` (pembuka): talent kabur + gelap SEBENTAR (maks 0,5 detik, Tio 2026-10-16: "jangan kelamaan"), lalu fokus tajam dengan whoosh. Butuh lebih lama untuk menutupi teks bawaan sumber: `"dur": 1.2`.

## 6. Tempo
- `"speed": "auto"`: tiap kalimat dipercepat sampai ±6,6 suku kata/detik, maksimal x1,3. Talent yang pelan dipercepat lebih banyak, kalimat yang sudah cepat dibiarkan x1,0. Suara tetap natural (atempo, nada tidak berubah).
- `"tighten": 0.22`: jeda hening lebih dari 0,22 detik dibuang (deteksi suara Silero, awal kata tidak pernah terpotong).
- Ucapan berulang/salah ucap yang diulang talent boleh dibuang lewat `segments`, tapi kalimat yang dipakai tetap utuh.

## 7. Audio
- Suara talent -14 LUFS, highpass 70 Hz. Musik opsional (`"music"`), -26 LUFS, otomatis turun saat talent bicara.
- SFX dari folder `SOUND EFFEC` milik Tio (paket Kenney, CC0). `tools/sfx_kenney.py` mengolahnya sekali jadi `public/sfx/k/<peran>-N.wav` (whoosh diperlambat supaya tebal, hantaman dilapis bass, kerasnya disamakan). Template sudah membawa hasilnya.
- SFX dipasang otomatis oleh `compile.py` sesuai peran, gaya referensi = tiap pergantian visual ada bunyinya dan TERASA:
  - `in` whoosh tebal tepat di potongan masuk B-roll/kartu, `out` whoosh pendek saat kembali ke talent,
  - `hit` hantaman + bass di flash, `punch` hantaman lembut di punch, `blur` whoosh rendah, `wipe` whoosh besar,
  - `pop` angka/logo, `rise` naik sebelum angka, `hook` hantaman di detik 0.
- **Bunyi ala CapCut, SELEKTIF (aturan FIX Tio 2026-10-16: "jangan semua kata dikasih, menyesuaikan aja").** Kata biasa TANPA bunyi. Maksimal SATU bunyi per frasa, dipilih otomatis dari intonasi talent (`tools/intonasi.py` mengukur keras + nada tiap kata):
  - kata gaya (tebal/besar/kuning) yang paling ditekan → `kretik` (keyboard mekanik), kalau kuning ditambah `tik`,
  - frasa tanpa kata gaya → `key` (ketikan) hanya kalau talent jelas menekan satu kata; kalimat datar dibiarkan tanpa bunyi,
  - kalimat tanya → `tanya` (nada naik "hm?") di kata terakhir,
  - teriakan (≥4 dB lebih keras dari biasanya + nada tinggi) → `boom` (gaya vine boom) otomatis, menggantikan hit/punch di situ,
  - jarak antar bunyi ketik minimal 0,8 detik, dan dilewati kalau berdekatan (<0,3 detik) dengan SFX lain.
- **Seluruh folder `SOUND EFFEC` boleh dipakai** (Tio 2026-10-16: "ambil semua, Claude milih sendiri sesuai talent"). Peran di atas hanya bawaan. Tiap video, sesuaikan dengan karakter talent: talent santai/lucu → bunyi ringan (pop, pluck, jingle PIZZI/SAX), talent serius/premium → bunyi halus (glass, click, whoosh tipis), teriak/heboh → impact dan boom. Dengarkan pilihan lewat analisis (durasi, nada), tambah/ganti peran di `tools/sfx_kenney.py` khusus proyek itu, lalu `python tools/sfx_kenney.py "../../SOUND EFFEC"`. Aturan selektif tetap berlaku.
- Bunyi aksen manual, pakai seperlunya (±1 per 5 detik) di momen yang memang cocok: frasa `{"t": "...", "sfx": "ding"}`, diputar di kata tebal/kuning pertama.
  `ding` (enak, mantap, benar) · `kaching` (uang, harga, cuan) · `salah` (buzzer salah/gagal) · `scratch` (rekaman tergores: "eh tunggu", plot twist) · `kilau` (wow, bersih, glowing) · `tada` (stinger lucu) · `boom` (kaget) · `tanya` · `pop`.
  Efek juga bisa ganti bunyi: `{"p": 3, "type": "flash", "sfx": "boom"}`. Matikan otomatisnya: `"ketik": false`, `"boom_auto": false`.
- Keras: whoosh 2–5 dB di bawah suara talent, hantaman setara suara, ketik/kretik ±8–12 dB di bawah. Semua dicampur x0,7 supaya suara + SFX tidak pecah, `export.py` menormalkan lagi ke -14 LUFS. Suara talent tidak boleh tertutup.
- Tidak ada dua bunyi bertumpuk: kalau potongan berbarengan dengan flash/punch/wipe, whoosh-nya dilewati.

## 8. Tampilan premium ("podcast mahal", standar sejak 2026-10-16)
- Grade sinematik: contrast 1.12, saturate 0.86, brightness 0.95, sedikit hangat. Vignette lebih kuat dan gradasi gelap di bawah supaya caption terbaca.
- Grain film halus (bergerak), flash lebih lembut (bukan putih menyilaukan).
- Bersih: tidak ada stiker/emoji ramai, transisi utama = potong + zoom, efek maksimal 1 per ±5 detik.
- `"look": "standar"` di clip.json = gaya lama tanpa grain/grade sinematik.

## 9. Sumber yang sudah ada tulisannya (download TikTok/IG)
- Caption bawaan pembuat asli jangan sampai dobel dengan caption kita. Hapus dengan `tools/hapus_teks.py` (kotak + frame acuan bersih di `edit/hapus_teks.json`), tutup dengan kartu/defocus, atau biarkan kalau tulisan itu bagian isi (mis. perintah yang didemokan).
- Caption pembuat asli boleh dipakai sebagai petunjuk ejaan kata yang meragukan.
- Laporkan ke Tio bahwa hasil terbaik pakai file asli dari HP (tanpa tulisan, resolusi penuh).

## 10. Warna dan font
- Merah #B5161B, merah tua #7E0E12, abu kartu #E7E5E3, kuning #F5E31A, putih, hitam #0E0E10.
- Font ikut di `public/fonts` (Inter Display Light–ExtraBold, Inter, Instrument Serif), jadi hasil sama di laptop mana pun.
- Grade ringan: contrast 1.06, saturate 1.05, vignette lembut. Warna kulit tetap natural.

## 11. Format
- Standar potret 1080x1920, 30 fps, H.264, SATU file `<Nama>_1080x1920.mp4` di `HASIL\<nama>\` (IG/TikTok/FB).
- Sumber horizontal (podcast 16:9) di-crop 9:16 otomatis mengikuti wajah.
- **Lanskap** (permintaan Tio 2026-10-16, hanya kalau diminta): `"format": "lanskap"` di clip.json -> 1920x1080 (YouTube/FB), file `<Nama>_1920x1080.mp4`.
  Semua gaya sama (caption kinetik, premium, zoom dinamis, SFX). Caption di sepertiga bawah (ukuran x0,8), hook di atas tengah.
  Dua layer di lanskap = kiri/kanan: `"talent": "kiri"` (default, B-roll kanan) atau `"kanan"`. Sumber 720p di-upscale lanczos + tajamkan otomatis.
