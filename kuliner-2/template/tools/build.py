"""Potong footage sesuai edit/edl.json lalu siapkan bahan Remotion.
python tools/build.py <folder_footage>
Hasil: public/base.webm (video VP9, wajib untuk filter), public/mix.wav (VO -14 LUFS + suara asli),
edit/timeline.json, raw/timeline_words.json (waktu tiap kata VO di video jadi, untuk caption).
Sesudahnya jalankan tools/captions.py.

edl.json: {"segments":[{"id":"hook","audio":[[kunci,mulai,selesai]],"video":[[kunci,in,durasi|null,laju?]]}]}
- audio = potongan VO berurutan; panjang segmen = jumlah potongan audio. Kunci "vo" = file VO terpisah (vo.m4a),
  kunci klip = VO yang diucapkan di klip itu sendiri, kunci "-" = hening (mis. ["-",0,2.5] = 2,5 dtk tanpa VO).
- Segmen tanpa VO (semua "-"): suara asli klip (desis, kriuk, tuang) dipakai penuh = momen ASMR.
- video klip yang sama dengan audio otomatis sinkron (bibir pas). durasi null = bagi rata sisa waktu.
- laju opsional: 0.5 = gerak lambat setengah kecepatan (bagus untuk tuang saus, keju meleleh, minyak goreng).
- Grade dasar ringan di sini; filter utama ada di src/grade.ts (Remotion Effects)."""
import json, subprocess, os, sys, hashlib
from common import ROOT, footage_files, duration, load
files = footage_files(sys.argv[1])
OUT = os.path.join(ROOT, 'edit', 'parts'); os.makedirs(OUT, exist_ok=True)
PUB = os.path.join(ROOT, 'public'); os.makedirs(os.path.join(ROOT, 'raw'), exist_ok=True)
edl = load('edit/edl.json')
WORDS = load('raw/words.json', {})
HALL = ['terima kasih', 'selamat men', 'menonton']   # halusinasi Whisper di klip tanpa omongan
AMB, AMB_SPEECH = 1.6, 0.25                            # suara asli B-roll di bawah VO (~15 dB lebih pelan)
FPS = 30
GRADE = "eq=saturation=1.02:contrast=1.0"
D = {}; timeline = []; t0 = 0.0; vlist = []; alist = []; mlist = []; tw = []
def ff(*a): subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
def dur(k):
    if k not in D: D[k] = duration(files[k])
    return D[k]
for si, seg in enumerate(edl['segments']):
    pieces = []; pos = 0.0
    for it in seg['audio']:
        k, a, b = it[0], it[1], it[2]
        L = round((b - a) * FPS) / FPS; pieces.append((k, a, L, pos)); pos += L
    solo = all(p[0] == '-' for p in pieces)          # segmen ASMR: suara asli penuh
    segL = pos; vpos = 0.0; vids = []; syn = []
    for i, it in enumerate(seg['video']):
        k, vin, vd = it[0], it[1], it[2]; r = it[3] if len(it) > 3 else 1.0
        last = i == len(seg['video']) - 1
        d = (segL - vpos) if last else ((segL - vpos) / (len(seg['video']) - i) if vd is None else vd)
        d = round(d * FPS) / FPS; synced = False
        for (ak, aa, aL, apos) in pieces:
            if ak == k and apos - 0.01 <= vpos < apos + aL:
                vin = aa + (vpos - apos); synced = True; r = 1.0; break
        if vin + d * r > dur(k) - 0.01: vin = max(0, dur(k) - 0.01 - d * r)
        assert d * r <= dur(k) + 0.001, ('klip terlalu pendek', seg['id'], k, d, r, dur(k))
        vids.append((k, round(vin, 3), d, r)); syn.append(synced); vpos += d
    for j, (k, vin, d, r) in enumerate(vids):
        h = hashlib.md5(f'{files[k]}{vin}{d}{r}{GRADE}'.encode()).hexdigest()[:8]
        o = os.path.join(OUT, f'v{si:02d}_{j}_{h}.mp4')
        if not os.path.exists(o):
            vf = f"setpts=PTS/{r},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},{GRADE},setsar=1,format=yuv420p"
            ff('-ss', str(vin), '-i', files[k], '-t', f'{d * r:.4f}', '-an', '-vf', vf, '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-r', str(FPS), '-t', f'{d:.4f}', o)
        vlist.append(o)
    for j, (k, vin, d, r) in enumerate(vids):
        o = os.path.join(OUT, f'm{si:02d}_{j}.wav')
        if syn[j] or not (0.5 <= r <= 2):
            ff('-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', f'{d:.4f}', o); mlist.append(o); continue
        tempo = f'atempo={r},' if r != 1 else ''
        fade = f"afade=t=in:d=0.12,afade=t=out:st={max(0, d - 0.12):.3f}:d=0.12"
        if solo:
            af = f"highpass=f=60,{tempo}loudnorm=I=-19:TP=-2,{fade}"
        else:
            T = WORDS.get(k, {}).get('segs', [])
            sp = [(max(0, (x['s'] - vin) / r), (x['e'] - vin) / r) for x in T if x['e'] > vin and x['s'] < vin + d * r and not any(hh in x['t'].lower() for hh in HALL)]
            cond = '+'.join(f'between(t,{a:.2f},{b:.2f})' for a, b in sp) or '0'
            af = f"highpass=f=90,{tempo}volume='if({cond},{AMB_SPEECH},{AMB})':eval=frame,{fade}"
        ff('-ss', str(vin), '-i', files[k], '-t', f'{d * r:.4f}', '-vn', '-ac', '2', '-ar', '48000', '-af', af, '-t', f'{d:.4f}', o)
        mlist.append(o)
    for j, (k, a, L, apos) in enumerate(pieces):
        o = os.path.join(OUT, f'a{si:02d}_{j}.wav')
        if k == '-':
            ff('-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', f'{L:.4f}', o)
        else:
            ff('-ss', str(a), '-i', files[k], '-t', f'{L:.4f}', '-vn', '-ac', '2', '-ar', '48000', '-af', f"afade=t=in:d=0.02,afade=t=out:st={L - 0.04:.3f}:d=0.04", o)
            first = True
            for sg in WORDS.get(k, {}).get('segs', []):
                for w, s, e in sg['words']:
                    if a - 0.05 <= s < a + L - 0.05:
                        # potongan VO baru = awal frasa baru (caption tidak menyambung lintas potongan)
                        tw.append([w, round(t0 + apos + s - a, 3), round(t0 + apos + min(e, a + L) - a, 3)] + ([1] if first else []))
                        first = False
        alist.append(o)
    timeline.append({'id': seg['id'], 'start': round(t0, 3), 'dur': round(segL, 3), 'video': vids}); t0 += segL
def lst(name, items):
    p = os.path.join(OUT, name); open(p, 'w').write('\n'.join("file '%s'" % x.replace('\\', '/') for x in items)); return p
has_vo = any(it[0] != '-' for s in edl['segments'] for it in s['audio'])
ff('-f', 'concat', '-safe', '0', '-i', lst('v.txt', vlist), '-c', 'copy', os.path.join(OUT, 'video.mp4'))
ff('-f', 'concat', '-safe', '0', '-i', lst('a.txt', alist), *(['-af', 'loudnorm=I=-14:TP=-1.5:LRA=11'] if has_vo else []), '-ar', '48000', os.path.join(OUT, 'audio.wav'))
ff('-f', 'concat', '-safe', '0', '-i', lst('m.txt', mlist), '-ar', '48000', os.path.join(OUT, 'amb.wav'))
ff('-i', os.path.join(OUT, 'audio.wav'), '-i', os.path.join(OUT, 'amb.wav'), '-filter_complex', '[0][1]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.84', '-ar', '48000', os.path.join(PUB, 'mix.wav'))
# Chrome headless tidak bisa decode H.264 -> filter tidak jalan. Wajib VP9 WebM.
print('encode VP9 (beberapa menit)...', flush=True)
ff('-i', os.path.join(OUT, 'video.mp4'), '-an', '-c:v', 'libvpx-vp9', '-crf', '16', '-b:v', '0', '-deadline', 'good', '-cpu-used', '5', '-row-mt', '1', '-pix_fmt', 'yuv420p', os.path.join(PUB, 'base.webm'))
json.dump({'total': round(t0, 3), 'segments': timeline}, open(os.path.join(ROOT, 'edit', 'timeline.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump({'total': round(t0, 3), 'words': tw}, open(os.path.join(ROOT, 'raw', 'timeline_words.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('total', round(t0, 2), 'detik,', len(tw), 'kata VO. Lanjut: python tools/captions.py')
