---
name: edit-video-kuliner
description: Edit footage mentah review kuliner jadi Reels final sesuai brief PDF, dengan gaya final Tio (Remotion, filter resto, teks tanpa latar, serif miring + font Apple, progress bar bab, SFX). Pakai saat Tio bilang "editin", "editin sesuai brief", "editin kuliner", atau memberi folder footage kuliner (dengan atau tanpa brief, mentah atau sudah dipotong).
---

# Edit Video Kuliner (workflow final)

Gaya dan aturan: baca `kuliner/ATURAN-FINAL.md` dulu, wajib diikuti. Contoh hasil yang disetujui: `kuliner/contoh/mbah-dinem/` (tidak disertakan di repo publik; contoh isi ada di `kuliner/template/src/Kuliner.tsx`).
Kerja tanpa banyak tanya. Laporkan progres singkat. Semua perintah dijalankan dari folder proyek video (PROYEK/<nama>).

## 0. Persiapan (sekali per komputer, cek dulu sebelum pasang)
- `node -v` (>=18), `python --version` (>=3.10), `ffmpeg -version`, `ffprobe -version`.
  Windows kalau belum ada: `winget install OpenJS.NodeJS.LTS`, `winget install Python.Python.3.12`, `winget install Gyan.FFmpeg` (buka terminal baru setelahnya).
- `python -m pip install sherpa-onnx numpy pillow`
- Semua font sudah ikut di template (`public/fonts`), tidak perlu pasang font di Windows.

## 1. Siapkan proyek
- Tentukan <nama> dari folder footage (FOOTAGE/<nama>). Kalau Tio tidak menyebut, pakai folder FOOTAGE terbaru.
- Salin `kuliner/template/` ke `PROYEK/<nama>/` (jangan edit template langsung). Lalu di PROYEK/<nama>: `npm install`.
- Sekali saja di PROYEK/<nama>: `python tools/setup_asr.py turbo` (atau salin folder `models/` dari proyek lain biar tidak unduh ulang).

## 2. Baca brief PDF (kalau ada)
- Tidak ada PDF di folder footage: lewati langkah ini, ikuti ATURAN-FINAL bagian "Tanpa brief" (alur sendiri dari footage, info hanya yang terdengar/terlihat).
- Ekstrak teks (pdftotext / pustaka PDF / baca langsung). Catat ke `PROYEK/<nama>/brief.md`:
  poin wajib, value yang di-highlight, larangan, menu (baru), harga, jam buka, alamat persis, nomor kontak, info musiman, nama cabang, warna & font brand di PDF.
- Larangan brief berlaku untuk teks layar DAN potongan VO.

## 3. Kenali footage
- `python tools/transcribe.py "<folder footage>"` → raw/transcript.json (kunci klip = 4 digit terakhir nama file).
- `python tools/thumbs.py "<folder footage>"` → raw/thumbs/sheet*.jpg, lihat gambarnya untuk tahu isi tiap klip.
- Detail per detik untuk klip kandidat: `python tools/thumbs.py "<folder>" strip 0988 0989`.
- Cari kalimat VO yang memenuhi poin brief (cari kata: jam, buka, reservasi, alamat, menu baru, lebaran, puasa, tanpa, khas, resep, parkir).
- Whisper sering menulis "terima kasih / selamat menikmati" di klip tanpa omongan: itu halusinasi, bukan VO.

## 4. Susun edit (edit/edl.json)
- Tentukan dulu footage *mentah* atau *sudah dipotong Tio* (ATURAN-FINAL bagian "Tanpa brief / footage sudah dipotong"). Sudah dipotong: urutan dan potongan Tio dipertahankan, satu segmen per bab mengikuti urutan file/waktu, hanya rapikan sisa jeda.
- Urutan sesuai kuliner/ATURAN-FINAL.md (hook → nama → proses/value → menu → suasana → info → cicip → rekomendasi + alamat), lalu segmen `outro` 4–5 dtk (klip papan nama/pintu masuk, audio aslinya) untuk alamat + "Simpan.".
- Format: `{"segments":[{"id":"hook","audio":[["0919",31.55,35.95,"teks"]],"video":[["0920",1.2,2.2],["0928",17.6,null]]}]}`.
  Audio = potongan VO berurutan (menentukan panjang). Video klip yang sama dengan audio otomatis sinkron bibir. B-roll pilih yang relevan dengan kalimat.
- Sebelum dipakai, cek tiap potongan: `python tools/check.py "<folder>" 0919:10.35:12.25 ...`. Potong ucapan berulang / gagap (pakai dua potongan dari klip yang sama, lompati bagian dobel). Jangan memotong kata di tengah.
- Footage makan wajib banyak: sisipkan sebagai B-roll di segmen cicip dan rekomendasi.
- `python tools/build.py "<folder footage>"` → public/base.webm, public/mix.wav, src/data.json. (VP9 wajib: Chrome headless tidak decode H.264, tanpa itu filter mati diam-diam.)

## 5. Isi teks & SFX (src/Kuliner.tsx, hanya bagian KONTEN)
- Ubah `CHAPTERS` (5–6 bab, mencakup 0 sampai akhir), `CUES`, dan `SFX`. Jangan ubah komponen, gaya, filter (src/grade.ts), font.
- Waktu pakai `g.<id segmen>.start + detik`. Kata kunci ditulis `*kata*` → serif miring.
- Jenis baris: main, sub, count (angka naik), row (label + harga), strike (daftar dicoret).
- Hook wajib formula sans + serif miring, mis. `'Ayam *Ajaib*'`. Nama cabang + "khas …" di cue kedua.
- Alamat, jam, nomor: salin persis dari brief. Penutup: alamat (hold) + "*Simpan.*" + "Tag teman makanmu".
- Composition id tetap `Kuliner`. `npm run cek` harus bersih.

## 6. Cek visual
- Hitung frame tengah tiap cue (detik × 30), lalu `node tools/stills.mjs raw/cek <frame...>` dan LIHAT hasilnya.
- Periksa: progress bar ada di semua frame, teks tidak menutupi wajah/produk utama, tidak di kanan bawah, terbaca (pindahkan posisi atau ganti aksen serif ke putih kalau latar terang/ramai).

## 7. Render & ekspor
- `npx remotion render src/index.ts Kuliner out/video.mp4 --crf=16 --audio-bitrate=256k --concurrency=4` (lama, 15–20 menit untuk ~100 dtk).
- `python tools/export.py out/video.mp4 "../../HASIL/<nama>" "<Nama>"` → `_final_1080p.mp4` (upload IG) + `_preview_720p.mp4`.
- Buat lembar kontak hasil (ffmpeg fps=1/4, tile) dan lihat sekali lagi.

## 8. Laporan ke Tio (singkat)
Path hasil, durasi, poin brief yang masuk, keputusan yang diambil sendiri, dan hal yang perlu Tio cek (info yang tidak bisa diverifikasi, konflik brief vs VO). Ingatkan musik belum ada.
