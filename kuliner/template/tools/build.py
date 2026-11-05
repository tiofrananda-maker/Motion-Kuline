"""Potong footage sesuai edit/edl.json lalu siapkan bahan Remotion.
python tools/build.py <folder_footage>
Hasil: public/base.webm (video VP9, wajib untuk filter), public/mix.wav (VO -14 LUFS + suara asli pelan),
src/data.json (total & awal tiap segmen), edit/timeline.json.

edl.json: {"segments":[{"id":"hook","audio":[[klip,mulai,selesai,"teks"]],"video":[[klip,in,durasi|null]]}]}
- audio = potongan VO berurutan; panjang segmen = jumlah potongan audio.
- video klip yang sama dengan audio otomatis sinkron (bibir pas). durasi null = bagi rata sisa waktu.
- Grade warna dasar ringan di sini; filter utama ada di src/grade.ts (Remotion Effects)."""
import json, subprocess, os, sys, hashlib
from common import ROOT, footage_files, duration
files = footage_files(sys.argv[1])
OUT = os.path.join(ROOT, 'edit', 'parts'); os.makedirs(OUT, exist_ok=True)
PUB = os.path.join(ROOT, 'public')
edl = json.load(open(os.path.join(ROOT, 'edit', 'edl.json'), encoding='utf-8'))
trp = os.path.join(ROOT, 'raw', 'transcript.json')
TR = json.load(open(trp, encoding='utf-8')) if os.path.exists(trp) else {}
HALL = ['terima kasih', 'selamat men', 'menonton']   # halusinasi Whisper di klip tanpa omongan
AMB, AMB_SPEECH = 1.6, 0.25                            # suara asli B-roll di bawah VO (~15 dB lebih pelan)
FPS = 30
GRADE = "eq=saturation=1.10:contrast=1.03,colorbalance=rm=0.03:gm=0.0:bm=-0.03"
D = {}; timeline = []; t0 = 0.0; vlist = []; alist = []; mlist = []
def ff(*a): subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
for si, seg in enumerate(edl['segments']):
    pieces = []; pos = 0.0
    for (k, a, b, txt) in seg['audio']:
        L = round((b - a) * FPS) / FPS; pieces.append((k, a, L, pos, txt)); pos += L
    segL = pos; vpos = 0.0; vids = []; syn = []
    for i, (k, vin, vd) in enumerate(seg['video']):
        if k not in D: D[k] = duration(files[k])
        last = i == len(seg['video']) - 1
        d = (segL - vpos) if last else ((segL - vpos) / (len(seg['video']) - i) if vd is None else vd)
        d = round(d * FPS) / FPS; synced = False
        for (ak, aa, aL, apos, _) in pieces:
            if ak == k and apos - 0.01 <= vpos < apos + aL:
                vin = aa + (vpos - apos); synced = True; break
        if vin + d > D[k] - 0.01: vin = max(0, D[k] - 0.01 - d)
        assert d <= D[k] + 0.001, (seg['id'], k, d, D[k])
        vids.append((k, round(vin, 3), d)); syn.append(synced); vpos += d
    for j, (k, vin, d) in enumerate(vids):
        h = hashlib.md5(f'{files[k]}{vin}{d}{GRADE}'.encode()).hexdigest()[:8]
        o = os.path.join(OUT, f'v{si:02d}_{j}_{h}.mp4')
        if not os.path.exists(o):
            vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},{GRADE},setsar=1,format=yuv420p"
            ff('-ss', str(vin), '-i', files[k], '-t', f'{d:.4f}', '-an', '-vf', vf, '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-r', str(FPS), o)
        vlist.append(o)
    for j, (k, vin, d) in enumerate(vids):
        o = os.path.join(OUT, f'm{si:02d}_{j}.wav')
        if syn[j]:
            ff('-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', f'{d:.4f}', o)
        else:
            T = TR.get(k, {}).get('segs', [])
            sp = [(max(0, x['s'] - vin), x['e'] - vin) for x in T if x['e'] > vin and x['s'] < vin + d and not any(hh in x['t'].lower() for hh in HALL)]
            cond = '+'.join(f'between(t,{a:.2f},{b:.2f})' for a, b in sp) or '0'
            af = f"highpass=f=90,volume='if({cond},{AMB_SPEECH},{AMB})':eval=frame,afade=t=in:d=0.12,afade=t=out:st={max(0, d - 0.12):.3f}:d=0.12"
            ff('-ss', str(vin), '-i', files[k], '-t', f'{d:.4f}', '-vn', '-ac', '2', '-ar', '48000', '-af', af, o)
        mlist.append(o)
    for j, (k, a, L, apos, txt) in enumerate(pieces):
        o = os.path.join(OUT, f'a{si:02d}_{j}.wav')
        ff('-ss', str(a), '-i', files[k], '-t', f'{L:.4f}', '-vn', '-ac', '2', '-ar', '48000', '-af', f"afade=t=in:d=0.02,afade=t=out:st={L - 0.04:.3f}:d=0.04", o)
        alist.append(o)
    timeline.append({'id': seg['id'], 'start': round(t0, 3), 'dur': round(segL, 3), 'video': vids}); t0 += segL
def lst(name, items):
    p = os.path.join(OUT, name); open(p, 'w').write('\n'.join("file '%s'" % x.replace('\\', '/') for x in items)); return p
ff('-f', 'concat', '-safe', '0', '-i', lst('v.txt', vlist), '-c', 'copy', os.path.join(OUT, 'video.mp4'))
ff('-f', 'concat', '-safe', '0', '-i', lst('a.txt', alist), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', os.path.join(OUT, 'audio.wav'))
ff('-f', 'concat', '-safe', '0', '-i', lst('m.txt', mlist), '-ar', '48000', os.path.join(OUT, 'amb.wav'))
ff('-i', os.path.join(OUT, 'audio.wav'), '-i', os.path.join(OUT, 'amb.wav'), '-filter_complex', '[0][1]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.84', '-ar', '48000', os.path.join(PUB, 'mix.wav'))
# Chrome headless tidak bisa decode H.264 -> filter tidak jalan. Wajib VP9 WebM.
print('encode VP9 (beberapa menit)...', flush=True)
ff('-i', os.path.join(OUT, 'video.mp4'), '-an', '-c:v', 'libvpx-vp9', '-crf', '16', '-b:v', '0', '-deadline', 'good', '-cpu-used', '5', '-row-mt', '1', '-pix_fmt', 'yuv420p', os.path.join(PUB, 'base.webm'))
json.dump({'total': round(t0, 3), 'segments': timeline}, open(os.path.join(ROOT, 'edit', 'timeline.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump({'total': round(t0, 3), 'segments': {s['id']: {'start': s['start'], 'dur': s['dur']} for s in timeline}, 'captions': []},
          open(os.path.join(ROOT, 'src', 'data.json'), 'w'), indent=1)
print('total', round(t0, 2), 'detik')
