# MOTION KULINER — instruksi untuk Claude

Studio edit video berbasis Remotion. Bahasa: Indonesia. Ada tiga model video, pilih sesuai permintaan:

| User bilang | Model | Baca dan ikuti |
|---|---|---|
| "editin sesuai brief", "editin kuliner", footage review makanan (brief PDF opsional, mentah atau sudah dipotong) | **kuliner** (Reels review kuliner) | `kuliner/skill/edit-video-kuliner/SKILL.md` + `kuliner/ATURAN-FINAL.md` |
| "editin resep", "kuliner 2", footage proses masak/resep (bahan, langkah, goreng, plating) | **kuliner-2** (resep estetik) | `kuliner-2/skill/edit-video-resep/SKILL.md` + `kuliner-2/ATURAN-RESEP.md` |
| "editin podcast", "clip podcast", footage orang ngomong ke kamera / podcast | **podcast** (clipper) | `podcast/skill/edit-podcast-clipper/SKILL.md` + `podcast/ATURAN-PODCAST.md` |

Kalau ragu: review tempat makan/warung → kuliner; proses masak sendiri → kuliner-2; orang bicara ke kamera tanpa topik makanan → podcast.

Aturan umum:
1. Ikuti skill langkah demi langkah sampai video jadi. Aturan gaya WAJIB diikuti; jangan ubah gaya/filter/font kecuali diminta.
2. Podcast & kuliner-2: **caption harus persis ucapan talent/VO** (aturan keras). Podcast: SFX ala CapCut **selektif**, tidak di setiap kata (ATURAN-PODCAST bagian 7). Kuliner-2: tanpa SFX.
3. Jangan tanya panjang. Pilih default yang masuk akal, jalan terus, laporkan singkat di akhir.
4. "ubah aturan kuliner/kuliner 2/podcast: …" → perbarui file ATURAN + template model itu saja.

Struktur (folder yang tidak ada di repo dibuat sendiri oleh user):
- `FOOTAGE/<nama>/` → bahan video (satu folder per video; podcast boleh punya sub-folder `broll/`)
- `SOUND EFFEC/` → paket SFX (mis. Kenney, CC0); diolah lewat `podcast/template/tools/sfx_kenney.py`
- `BROLL/` → pustaka klip B-roll yang sudah diunduh (+ KREDIT.txt)
- `kuliner/`, `kuliner-2/`, `podcast/` → aturan, skill, template Remotion
- `PROYEK/<nama>/` → salinan template per video (dibuat Claude)
- `HASIL/<nama>/` → video final 1080p + preview 720p
