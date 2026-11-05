---
name: edit-video-resep
description: Edit footage masak/resep jadi Reels gaya resep estetik (acuan Corndog Hack tummyyammy) - nama akun atas, judul serif pembuka, caption VO kecil huruf kecil kata demi kata, ajakan COMMENT di akhir, grade terang hangat. Pakai saat Tio bilang "editin resep", "kuliner 2", "template kuliner kedua", atau memberi footage proses masak.
---

# Edit Video Resep Estetik (kuliner-2)

Gaya dan aturan: baca `kuliner-2/ATURAN-RESEP.md` dulu, wajib diikuti. **Caption = persis ucapan VO.**
Kerja tanpa banyak tanya, laporkan singkat di akhir. Semua perintah dari folder proyek (PROYEK/<nama>).

## 0. Persiapan (sekali per komputer)
- `node -v` (>=18), `python --version` (>=3.10), `ffmpeg -version`. Windows: `winget install OpenJS.NodeJS.LTS`, `winget install Python.Python.3.12`, `winget install Gyan.FFmpeg`.
- `python -m pip install sherpa-onnx numpy pillow kaldi-native-fbank onnxruntime`

## 1. Siapkan proyek
- <nama> = folder `FOOTAGE/<nama>` yang Tio sebut (kalau tidak, folder FOOTAGE terbaru).
- Salin `kuliner-2/template/` ke `PROYEK/<nama>/`, lalu `npm install`. (Windows: ekstrak paket tar dengan `tar --force-local`.)
- Sekali: `python tools/setup_asr.py turbo` (Whisper + Dolphin untuk waktu per kata + VAD), atau salin `models/` dari proyek lain.

## 2. Kenali footage
- `python tools/thumbs.py "<folder>"` → raw/thumbs/sheet*.jpg; LIHAT untuk tahu isi tiap klip (hero, money shot, bahan, tiap langkah, masak, plating).
- Detail per detik: `python tools/thumbs.py "<folder>" strip 0921 0935`.
- `python tools/words.py "<folder>"` → raw/words.json (teks + waktu per kata semua klip dan file VO).
- Tentukan sumber VO (ATURAN bagian Audio): file `vo.*` → kunci `vo`; banyak voice note (.ogg/.m4a) → kunci = nama file masing-masing; omongan di klip → kunci klip; tidak ada → ASMR (`"-"`).
- Voice note: susun mengikuti ISI kalimat, bukan urutan nama/waktu file. Ujung voice note yang terpotong di tengah kata dibuang.
- Whisper suka menulis "terima kasih / selamat menikmati" di klip tanpa omongan: itu halusinasi.

## 3. Susun edit (edit/edl.json)
- Urutan mengikuti ATURAN bagian Struktur: hook (hero + money shot) → cerita → bahan → proses → masak → plating → hasil → `cta`.
- Format: `{"segments":[{"id":"hook","audio":[["vo",0.0,2.7]],"video":[["0950",1.0,1.5],["0960",3.2,null]]}, ... ,{"id":"cta","audio":[["vo",57.0,60.1]],"video":[["0978",0.5,null]]}]}`
  - audio = potongan VO berurutan (menentukan panjang segmen). `["-",0,2.5]` = 2,5 dtk tanpa VO (suara asli penuh).
  - video = `[klip, mulai, durasi|null, laju?]`; laju 0.5 = gerak lambat (tuangan, keju, minyak). null = bagi rata sisa.
  - Segmen terakhir WAJIB ber-id `cta` (shot hero wide penutup): ajakan komentar muncul tepat di potongannya.
- Satu langkah = satu shot 1,5–3,5 dtk, ganti shot mengikuti kalimat VO. Buang jeda panjang dan ucapan diulang (dua potongan dari klip yang sama). Jangan memotong kata.
- Cek potongan VO: `python tools/check.py "<folder>" vo:10.35:12.25 0921:1.15:7.65`.
- `python tools/build.py "<folder>"` → public/base.webm, public/mix.wav, raw/timeline_words.json.

## 4. Teks (edit/resep.json + edit/captions.json)
- Isi `edit/resep.json`: handle akun Tio, judul pembuka (eyebrow + judul serif 1–3 kata), kata ajakan. Lihat contoh di ATURAN.
- `python tools/captions.py` → membuat `edit/captions.json` (frasa dari VO) dan `src/data.json`.
- Baca `edit/captions.json`, dengarkan ulang yang ragu (`tools/check.py`), betulkan teks `"t"` supaya PERSIS ucapan (mis. "Korondok" → "Corndog"). Lalu `python tools/captions.py` lagi.
- edl/build berubah → `python tools/captions.py ulang` (frasa dibuat ulang; koreksi teks perlu diulang).
- Jangan ubah src/Resep.tsx, theme.ts, grade.ts, fonts kecuali Tio minta. `npx tsc --noEmit -p .` harus bersih.

## 5. Cek visual
- `node tools/stills.mjs raw/cek <frame...>` (frame = detik × 30): frame 30 (judul), beberapa caption, frame terakhir (ajakan). LIHAT hasilnya.
- Periksa: caption terbaca (latar terlalu putih → pilih shot lain di bagian itu), judul tidak menutupi bagian penting hero, potongan mengikuti VO.

## 6. Render & ekspor
- `npx remotion render src/index.ts Resep out/video.mp4 --crf=16 --audio-bitrate=256k --concurrency=2` (laptop Tio RAM 6 GB: concurrency di atas 2 kehabisan memori, ±20 menit per 60 dtk)
- `python tools/export.py out/video.mp4 "../../HASIL/<nama>" "<Nama>"` → `_final_1080p.mp4` + `_preview_720p.mp4`.
- Lembar kontak hasil (ffmpeg fps=1/3, tile) dan lihat sekali lagi.

## 7. Laporan ke Tio (singkat)
Path hasil, durasi, sumber VO yang dipakai, kata caption yang masih ragu, bagian struktur yang dilewati karena tidak ada footage. Ingatkan musik belum ada.
