# Motion Kuliner — template edit video Reels dengan Claude Code + Remotion

Tiga template video vertikal (1080×1920) yang dikerjakan Claude Code secara otomatis dari footage mentah:

| Template | Untuk | Prompt contoh |
|---|---|---|
| `kuliner/` | Reels review tempat makan (font ala Apple + serif miring, progress bar bab, grade hangat, SFX) | `editin kuliner, footage di FOOTAGE/Sate Pak Kumis` |
| `kuliner-2/` | Reels resep estetik (judul serif, caption kecil kata demi kata, ajakan comment, tanpa SFX) | `editin resep, footage di FOOTAGE/Corndog` |
| `podcast/` | Klip podcast / talking head (caption persis ucapan, zoom dinamis, B-roll, SFX selektif) | `editin podcast, footage di FOOTAGE/Podcast` |

## Cara pakai
1. Clone repo ini, buka Claude Code di folder repo. `CLAUDE.md` memilih template otomatis.
2. Buat `FOOTAGE/<nama video>/` berisi footage (kuliner: + brief PDF opsional; kuliner-2: + `vo.m4a` opsional; podcast: + `broll/` opsional).
3. Ketik prompt dari tabel di atas. Hasil muncul di `HASIL/<nama>/`.
4. Pertama kali, Claude memasang Node.js, Python, ffmpeg, dan model transkrip (sherpa-onnx Whisper). Butuh internet.

Opsional: salin folder `*/skill/*` ke `.claude/skills/` supaya muncul sebagai /perintah.

## Yang tidak disertakan
- Footage, video hasil, foto/logo brand, dan contoh proyek klien (privat).
- SFX template kuliner: lihat `kuliner/template/public/sfx/BACA.txt` untuk nama file yang perlu kamu isi.
- SFX podcast di `podcast/template/public/sfx/k/` berasal dari paket [Kenney](https://kenney.nl) (CC0), daftar di `SUMBER.txt`.
- B-roll diunduh otomatis oleh `podcast/template/tools/broll.py` (Pexels/Pixabay pakai API key milikmu sendiri lewat env `PEXELS_API_KEY` / `PIXABAY_API_KEY`).

## Font
Inter, DM Serif Display, Instrument Serif, dan Comfortaa dirilis di bawah SIL Open Font License 1.1 dan boleh didistribusikan ulang bersama template ini.

## Ubah aturan
Bilang `ubah aturan kuliner: …`, `ubah aturan kuliner 2: …`, atau `ubah aturan podcast: …`. Claude hanya mengubah template yang disebut.
