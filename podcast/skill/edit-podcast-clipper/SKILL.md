---
name: edit-podcast-clipper
description: Potong video podcast/talking head jadi klip TikTok/Reels gaya raymondchins (caption kinetik persis ucapan talent, B-roll video otomatis, kartu merah/abu, angka, flash/punch, SFX dari folder SOUND EFFEC). Pakai saat Tio bilang "editin podcast", "clip podcast", atau memberi folder footage podcast.
---

# Edit Podcast Clipper (workflow)

Gaya dan aturan: baca `podcast/ATURAN-PODCAST.md` dulu, wajib diikuti. **Aturan keras: caption = persis ucapan talent.**
Contoh yang sudah jadi (folder contoh/ tidak disertakan di repo publik): `podcast/contoh/cerbon/` (SFX ala CapCut selektif, video ramai-ramai, caption bawah), `podcast/contoh/abdan/` (gaya terbaru: premium, zoom dinamis, sumber download dengan teks bawaan dihapus) dan `podcast/contoh/tes/` (B-roll + kartu).
Kerja tanpa banyak tanya, laporkan singkat di akhir. Semua perintah dari folder proyek (PROYEK/<nama>).

## 0. Persiapan (sekali per komputer)
- `node -v` (>=18), `python --version` (>=3.10), `ffmpeg -version`. Windows: `winget install OpenJS.NodeJS.LTS`, `winget install Python.Python.3.12`, `winget install Gyan.FFmpeg`.
- `python -m pip install sherpa-onnx numpy pillow kaldi-native-fbank onnxruntime "opencv-python-headless<5"` (OpenCV 5 tidak punya pendeteksi wajah yang dipakai tools/face.py)

## 1. Siapkan proyek
- <nama> = folder `FOOTAGE/<nama>` yang Tio sebut (kalau tidak, folder FOOTAGE terbaru yang berisi video podcast).
- Salin `podcast/template/` ke `PROYEK/<nama>/`, lalu `npm install`.
- Sekali: `python tools/setup_asr.py turbo` dan `python tools/setup_asr.py small` (Whisper turbo + small + Dolphin + VAD). Atau salin `models/` dari proyek lain.
- Klip B-roll dari Tio (kalau ada) di `FOOTAGE/<nama>/broll/` → salin ke `public/broll/` (pakai lebih dulu dari stok).
- SFX: template sudah membawa `public/sfx/k/` (whoosh, hantaman, plus bunyi ala CapCut: key, kretik, tik, tanya, ding, boom, kaching, salah, scratch, kilau, tada). Kalau folder `SOUND EFFEC` berubah, jalankan `python tools/sfx_kenney.py "<path SOUND EFFEC>"`.

## 2. Transkrip PERSIS (aturan keras)
1. `python tools/words.py "<folder footage>"` → raw/words.json (teks + waktu per kata).
2. `python tools/crosscheck.py "<folder footage>"` → raw/crosscheck.txt (3 pendengar per segmen).
3. Pertama kali `python tools/fix.py "<folder footage>"` membuat `edit/transkrip.json`. Betulkan teks tiap segmen:
   ikuti bentuk ucapan (gue/aku, gak/nggak, cuy), angka sebagai angka, istilah Inggris ejaan asli. Whisper suka membakukan
   ("tidak" padahal "gak") dan berhalusinasi "terima kasih" di bagian hening.
4. Kata yang beda antar pendengar: `python tools/pilih.py "<file>" <mulai> <selesai> "versi a|versi b"` → pakai skor tertinggi. Selisih < 3 = catat untuk laporan.
5. `python tools/fix.py "<folder footage>"` lagi → waktu per kata dihitung ulang dari teks final.

## 3. Pilih bagian + tempo (edit/clip.json)
- Footage panjang: pilih bagian 30–90 detik yang punya hook kuat di awal dan selesai di kalimat utuh. Footage pendek: pakai semua.
- `"segments": [["<kunci>", mulai, selesai], ...]` (kunci = 4 digit terakhir nama file atau nama file). Buang ucapan berulang/salah ucap dengan memecah segmen.
- Format: potret 1080x1920 standar. Kalau Tio minta lanskap/YouTube, tulis `"format": "lanskap"` di clip.json SEBELUM build (hasil 1920x1080; split jadi kiri/kanan).
- `"speed": "auto"`, `"tighten": 0.22` (default). Talent pelan otomatis dipercepat lebih banyak (maks x1,3).
- Sumber hasil download yang sudah ada tulisan/caption: isi `edit/hapus_teks.json` lalu `python tools/hapus_teks.py "<video>" "<folder footage>/bersih/<nama>.mp4"` dan pakai folder `bersih` untuk build (lihat ATURAN bagian 9). Sumber resolusi rendah tanpa tulisan: jalankan tanpa kotak (upscale + tajamkan).
- `python tools/build.py "<folder footage>"` → public/base.webm, public/voice.wav, raw/timeline.txt (kata + detik hasil). Laporan per potongan menunjukkan speed yang dipakai.
- `python tools/face.py` → raw/face.json (posisi wajah per frame untuk zoom dinamis). Wajib setiap habis build.

## 4. Caption, hook, cutaway, efek (edit/clip.json)
- `"captions"`: daftar frasa berurutan menutupi SEMUA kata ucapan (2–6 kata, `/` = ganti baris), gaya `**besar**`, `*serif*`, `_serif miring_`, `~miring~`, `^kuning^`. Satu kata ditonjolkan per frasa.
- `"hook": {"text": "BARIS SATU / BARIS DUA", "until_p": 2}`.
- `"cutaways"`: ganti visual tiap 2,5–4 detik (35–50% durasi), jenis dan kapan dipakai ada di ATURAN-PODCAST.md bagian 4. `p` = nomor frasa (mulai 0) atau `[dari, sampai]`.
  **Utamakan `"type": "video"`** (B-roll asli) dengan `"q": "kata kunci bahasa inggris"`, mis. `{"p": [1,2], "type": "video", "q": "content creator filming with smartphone"}`.
  **Dua layer:** `{"p": 5, "type": "split", "q": "..." | "src": "broll/x.mp4", "talent": "atas"}` = talent atas, B-roll bawah (`"talent": "bawah"` = dibalik). Campur dengan `video` penuh layar; split berurutan jadi montase. Klip potret beri `"y"`.
  Kartu teks untuk kalimat tanya/ketegangan, `stat` untuk angka, `logos` untuk merek (`"simple:<slug>"`). Gambar diam dan ikon garis hanya cadangan.
- `"fx"`: flash/punch/blur/wipe/defocus di awal frasa, maksimal 1 per ±5 detik. `defocus` di frasa 0 untuk pembuka (otomatis maks 0,5 detik).
- SFX: otomatis dan SELEKTIF (ATURAN bagian 7): bunyi ketik/kretik hanya di kata gaya yang paling ditekan, tanya di kalimat tanya, boom saat teriak. **Jangan beri bunyi di setiap kata.** Tambah `"sfx": "ding"|"kaching"|"salah"|"scratch"|"kilau"|"tada"` di frasa hanya untuk momen yang memang cocok.
- Pilih SFX sesuai talent dari SELURUH folder `SOUND EFFEC` (ATURAN bagian 7): ubah peran di `tools/sfx_kenney.py` proyek ini kalau bunyi bawaan kurang cocok, jalankan ulang, lalu compile.
- B-roll yang sudah pernah diunduh ada di `BROLL/` (lihat KREDIT.txt): pakai dulu kalau cocok sebelum mengunduh baru; klip baru yang dipakai salin juga ke `BROLL/`.
- Wajah talent di tengah/bawah frame (rombongan, kamera jauh): `"caption_pos": "bottom"`.
- Zoom dinamis dan tampilan premium otomatis (standar). Frasa yang memperlihatkan isi footage (demo, gambar) beri `"z": 1.0`; kata kunci beri `punch`.
- Lihat dulu frame footage (`python tools/thumbs.py "<folder>" strip <kunci>`): kalau footage punya tulisan/screenshot sendiri, jangan ditimpa (caption `"pos": "bottom"` atau `"top"`, jangan pasang stat di situ).
- `python tools/broll.py` → unduh klip untuk semua cutaway video/split yang punya `q` (butuh internet; set PEXELS_API_KEY kalau ada). LIHAT tiap klip;
  klip horizontal beri `"x"` (0–1) supaya objek masuk crop, `"start"` untuk bagian klip yang paling jelas. Tidak cocok → ganti `q` atau jadikan kartu.
- `python tools/compile.py` → src/data.json. **Wajib 100% dan tidak ada kata yang hilang.** Tidak perlu edit kode TSX.

## 5. Cek visual
- `node tools/stills.mjs out/cek <frame...>` (frame = detik × 30) untuk tiap cutaway, efek, dan 3 frame talent biasa. LIHAT hasilnya:
  caption terbaca dan tidak menutupi wajah, objek B-roll masuk crop dan jelas, angka tidak keluar layar, kartu tidak dobel dengan caption besar yang sama.

## 6. Render & ekspor
- `npx remotion render src/index.ts Podcast out/video.mp4 --crf=16 --audio-bitrate=256k --concurrency=4`
- `python tools/export.py out/video.mp4 "../../HASIL/<nama>" "<Nama>"` → SATU file `<Nama>_1080x1920.mp4` (atau `_1920x1080.mp4` kalau `"format": "lanskap"`) (H.264, 30 fps, AAC 48 kHz, -14 LUFS), siap IG/TikTok/FB (permintaan Tio 2026-10-16: cukup satu file).

## 7. Laporan ke Tio (singkat)
Path hasil, durasi sebelum/sesudah, speed per bagian, bunyi aksen yang dipasang, kata yang meragukan (detik di video hasil + versi), klip B-roll yang dipakai + kreditnya
(sebut jujur kalau klip hanya mendekati, mis. dolar bukan rupiah), dan keputusan yang diambil sendiri.
