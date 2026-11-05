"""Potong + rapatkan + percepat footage podcast sesuai edit/clip.json, lalu siapkan bahan Remotion.
python tools/build.py <file_atau_folder_footage>

edit/clip.json (bagian yang dipakai di sini):
  "segments": [["tes", 0.0, 34.4], ["tes", 42.6, 61.0, 1.2]]   potongan sumber (kunci, mulai, selesai[, speed khusus]) berurutan
  "speed": "auto"     auto = tiap kalimat dipercepat sampai ~target suku kata/detik (talent pelan dipercepat lebih banyak,
                      yang sudah cepat dibiarkan). Angka (mis. 1.1) = semua sama. 1.0 = asli
  "target": 6.6       (auto) suku kata/detik yang dituju. Referensi raymondchins ~7.6; 6.6 masih natural untuk talent santai
  "max_speed": 1.3    (auto) batas atas supaya suara tidak terdengar aneh
  "tighten": 0.22     jeda hening (VAD) lebih dari ini (detik) dibuang. null = tidak dirapatkan
  "crop": {"tes": 0.5}  opsional, posisi tengah crop 0..1 kalau sumber horizontal (default: wajah otomatis)
  "music": "musik/lagu.mp3"  opsional, musik pelan di bawah suara (di-duck otomatis)
Hasil: public/base.webm (VP9), public/voice.wav, raw/timeline_words.json + raw/timeline.txt (kata + waktu output)."""
import json, subprocess, os, sys
import numpy as np
from common import ROOT, footage_files, clip_key
src = sys.argv[1]
files = {clip_key(src): src} if os.path.isfile(src) else footage_files(src)
clip = json.load(open(os.path.join(ROOT, 'edit', 'clip.json'), encoding='utf-8'))
W = json.load(open(os.path.join(ROOT, 'raw', 'words.json'), encoding='utf-8'))
OUT = os.path.join(ROOT, 'edit', 'parts'); os.makedirs(OUT, exist_ok=True)
PUB = os.path.join(ROOT, 'public')
FPS = 30; TIGHT = clip.get('tighten'); KEEP = 0.07
LAND = clip.get('format') == 'lanskap'           # "format": "lanskap" = 1920x1080 (16:9), default potret 1080x1920
OW, OH = (1920, 1080) if LAND else (1080, 1920)
def ff(*a): subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
def probe(f):
    o = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=width,height:stream_side_data=rotation:stream_tags=rotate', '-of', 'json', f]))['streams'][0]
    w, h = o['width'], o['height']
    rot = abs(int(o.get('tags', {}).get('rotate', 0) or next((s.get('rotation', 0) for s in o.get('side_data_list', [])), 0) or 0))
    return (h, w) if rot in (90, 270) else (w, h)

def face_x(f, a, b):
    """Posisi tengah wajah (0..1) dari beberapa frame, untuk crop sumber horizontal."""
    try:
        import cv2
    except ImportError:
        return 0.5
    det = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'); xs = []
    for t in np.linspace(a, b, 6):
        img = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', f, '-frames:v', '1', '-vf', 'scale=640:-2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        if not img: continue
        im = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_GRAYSCALE)
        fs = det.detectMultiScale(im, 1.1, 6, minSize=(40, 40))
        if len(fs): x, y, w, h = max(fs, key=lambda r: r[2] * r[3]); xs.append((x + w / 2) / im.shape[1])
    return float(np.median(xs)) if xs else 0.5

# 1) potongan yang disimpan: per kalimat (speed sendiri-sendiri), jeda hening dibuang
import re
from align import spoken
TARGET = float(clip.get('target') or 6.6); MAXSP = float(clip.get('max_speed') or 1.3)
def syl(w): return sum(max(1, len(re.findall(r'[aiueo]+', p))) for p in spoken(w))
def auto_speed(ws):
    if len(ws) < 3: return None
    rate = sum(syl(w[0]) for w in ws) / max(0.5, ws[-1][2] - ws[0][1])
    return round(min(MAXSP, max(1.0, TARGET / rate)) * 20) / 20
_gaps = {}
def gaps(k):
    """Bagian tanpa suara orang (Silero VAD halus), termasuk awal & akhir file."""
    if k in _gaps: return _gaps[k]
    import sherpa_onnx
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', files[k], '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    cfg = sherpa_onnx.VadModelConfig(); cfg.silero_vad.model = os.path.join(ROOT, 'models', 'silero_vad.onnx')
    cfg.silero_vad.min_silence_duration = 0.1; cfg.silero_vad.min_speech_duration = 0.1; cfg.silero_vad.threshold = 0.6; cfg.sample_rate = 16000
    v = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=7200); n = cfg.silero_vad.window_size
    for i in range(0, len(x), n): v.accept_waveform(x[i:i + n])
    v.flush(); sp = []
    while not v.empty(): f = v.front; sp.append((f.start / 16000, f.start / 16000 + len(f.samples) / 16000)); v.pop()
    g = [(0.0, sp[0][0])] if sp else []
    g += [(a[1], b[0]) for a, b in zip(sp, sp[1:])]
    if sp: g.append((sp[-1][1], len(x) / 16000))
    _gaps[k] = g; return g
keep = []
for seg in clip['segments']:
    k, a, b = seg[:3]
    allw = [w for s in W[k]['segs'] for w in s['words']]
    starts = [s['words'][0][1] - 0.08 for s in W[k]['segs'] if s['words']]
    bounds = sorted({a, b, *[x for x in starts if a + 0.3 < x < b - 0.3]})
    for x0, x1 in zip(bounds, bounds[1:]):
        ws = [w for w in allw if x0 <= w[1] < x1]
        if len(seg) > 3: sp = float(seg[3])
        elif str(clip.get('speed', 1)).lower() == 'auto': sp = auto_speed(ws) or 1.0
        else: sp = float(clip.get('speed') or 1.0)
        parts = [[x0, x1]]
        if TIGHT is not None:
            for g0, g1 in gaps(k):
                c0, c1 = g0 + KEEP, g1 - KEEP * 1.5
                if g1 - g0 <= TIGHT or c1 <= c0: continue
                # jangan memotong awal kata
                c1 = min([c1] + [w[1] - KEEP for w in ws if c0 < w[1] < c1])
                nxt = []
                for p0, p1 in parts:
                    if c1 <= p0 or c0 >= p1: nxt.append([p0, p1]); continue
                    if c0 > p0: nxt.append([p0, c0])
                    if c1 < p1: nxt.append([c1, p1])
                parts = nxt
        keep += [[k, p0, p1, sp] for p0, p1 in parts]
keep = [p for p in keep if p[2] - p[1] > 0.12]

# 2) potong video + audio, satukan
vlist, alist, tmap, t_out = [], [], [], 0.0
for i, (k, a, b, SP) in enumerate(keep):
    f = files[k]; w, h = probe(f); d = b - a
    if not LAND and w / h > 9 / 16 + 0.01:
        cx = (clip.get('crop') or {}).get(k)
        if cx is None:
            cx = face_x(f, a, b); clip.setdefault('crop', {})[k] = round(cx, 3)
        cw = h * 9 / 16; x0 = min(max(0, cx * w - cw / 2), w - cw)
        vf = f'crop={cw:.0f}:{h}:{x0:.0f}:0,scale=1080:1920'
    else:
        vf = f'scale={OW}:{OH}:force_original_aspect_ratio=increase:flags=lanczos,crop={OW}:{OH}' + (',unsharp=5:5:0.6:5:5:0' if w < OW and h < OH else '')
    vf += f',setpts=(PTS-STARTPTS)/{SP},fps={FPS},setsar=1,format=yuv420p'
    vo = os.path.join(OUT, f'v{i:03d}.mp4'); ao = os.path.join(OUT, f'a{i:03d}.wav')
    ff('-ss', f'{a:.3f}', '-t', f'{d:.3f}', '-i', f, '-an', '-vf', vf, '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', vo)
    ff('-ss', f'{a:.3f}', '-t', f'{d:.3f}', '-i', f, '-vn', '-ac', '2', '-ar', '48000', '-af',
       f'atempo={SP},afade=t=in:d=0.015,afade=t=out:st={max(0, d / SP - 0.03):.3f}:d=0.03', ao)
    L = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vo]))
    tmap.append((k, a, b, t_out, SP)); t_out += L
    vlist.append(vo); alist.append(ao)
def lst(name, items):
    p = os.path.join(OUT, name); open(p, 'w').write('\n'.join("file '%s'" % x.replace('\\', '/') for x in items)); return p
ff('-f', 'concat', '-safe', '0', '-i', lst('v.txt', vlist), '-c', 'copy', os.path.join(OUT, 'video.mp4'))
ff('-f', 'concat', '-safe', '0', '-i', lst('a.txt', alist), '-af', 'highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9', '-ar', '48000', os.path.join(OUT, 'voice.wav'))
music = clip.get('music')
if music and os.path.exists(os.path.join(ROOT, music)):
    # musik ~ -24 LUFS, turun lagi saat ada suara (sidechain), fade in/out
    ff('-i', os.path.join(OUT, 'voice.wav'), '-stream_loop', '-1', '-i', os.path.join(ROOT, music), '-filter_complex',
       f'[1]loudnorm=I=-26,atrim=0:{t_out:.2f},afade=t=in:d=1,afade=t=out:st={max(0, t_out - 1.5):.2f}:d=1.5[m];'
       '[0]asplit[v][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=400[md];'
       '[v][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89', '-ar', '48000', os.path.join(PUB, 'voice.wav'))
else:
    ff('-i', os.path.join(OUT, 'voice.wav'), '-c', 'copy', os.path.join(PUB, 'voice.wav'))
print('encode VP9...', flush=True)
ff('-i', os.path.join(OUT, 'video.mp4'), '-an', '-c:v', 'libvpx-vp9', '-crf', '20', '-b:v', '0', '-deadline', 'good', '-cpu-used', '5',
   '-row-mt', '1', '-pix_fmt', 'yuv420p', os.path.join(PUB, 'base.webm'))

# 3) kata dalam waktu output (dasar caption)
tw = []
for k, a, b, t0, SP in tmap:
    for s in W[k]['segs']:
        for w, s1, e1 in s['words']:
            if a - 0.02 <= s1 < b:
                tw.append([w, round(t0 + (s1 - a) / SP, 3), round(t0 + (min(e1, b) - a) / SP, 3)])
tw.sort(key=lambda x: x[1])
json.dump({'total': round(t_out, 3), 'cuts': [round(t[3], 3) for t in tmap], 'speeds': [t[4] for t in tmap], 'words': tw},
          open(os.path.join(ROOT, 'raw', 'timeline_words.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open(os.path.join(ROOT, 'raw', 'timeline.txt'), 'w', encoding='utf-8') as fo:
    for w, s1, e1 in tw: fo.write(f'{s1:7.2f}  {w}\n')
json.dump(clip, open(os.path.join(ROOT, 'edit', 'clip.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'total {t_out:.2f} dtk dari {sum(sg[2] - sg[1] for sg in clip["segments"]):.2f} dtk sumber, {len(keep)} potongan')
for k, a, b, t0, sp in tmap: print(f'  {k} {a:6.2f}-{b:6.2f}  x{sp:<4}  -> {t0:6.2f}')
