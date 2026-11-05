"""Hapus teks bawaan sumber (video hasil download yang sudah ada caption), lalu upscale ke 1080x1920 + tajamkan.
python tools/hapus_teks.py <video sumber> <video hasil>        kotak dibaca dari edit/hapus_teks.json:
  {"boxes": [[t0, t1, x, y, w, h, [frame acuan bersih, ...]], [t0, t1, x, y, w, h, "v"]]}
  koordinat dalam piksel SUMBER. Frame acuan = frame lain (framing sama) yang area kotaknya bersih; ditempel dengan
  pencocokan geser +-8 px dan tepi lembut. "v" = isi tegak lurus dari baris atas/bawah (untuk permukaan rata).
Kalau tidak ada kotak, hanya upscale + tajamkan (berguna untuk sumber resolusi rendah)."""
import json, os, subprocess, sys
import cv2, numpy as np
from common import ROOT
src, dst = sys.argv[1], sys.argv[2]
cfg = os.path.join(ROOT, 'edit', 'hapus_teks.json')
BOX = json.load(open(cfg))['boxes'] if os.path.exists(cfg) else []
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
W, H = int(cap.get(3)), int(cap.get(4))
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
def feather(w, h, r=10):
    m = np.zeros((h + 2 * r, w + 2 * r), np.float32); m[r:-r, r:-r] = 1
    return cv2.GaussianBlur(m, (0, 0), r / 2)[..., None]
out = []
for n, f in enumerate(frames):
    t = n / fps; g = f.copy()
    for t0, t1, x, y, w, h, refs in BOX:
        if not (t0 <= t <= t1): continue
        if refs == 'v':
            a = g[y - 2:y, x:x + w].astype(np.float32).mean(0); b = g[y + h:y + h + 2, x:x + w].astype(np.float32).mean(0)
            k = np.linspace(0, 1, h)[:, None, None]
            g[y:y + h, x:x + w] = np.clip(a * (1 - k) + b * k + np.random.normal(0, 1.5, (h, w, 3)), 0, 255).astype(np.uint8); continue
        P = 14; ring = np.ones((h + 2 * P, w + 2 * P), bool); ring[P:-P, P:-P] = False
        tgt = f[y - P:y + h + P, x - P:x + w + P].astype(np.float32)
        best = None
        for r in refs:
            for dy in range(-8, 9, 2):
                for dx in range(-8, 9, 2):
                    c = frames[r][y - P + dy:y + h + P + dy, x - P + dx:x + w + P + dx].astype(np.float32)
                    if c.shape != tgt.shape: continue
                    e = ((c - tgt) ** 2)[ring].mean()
                    if best is None or e < best[0]: best = (e, c)
        R = 10; fm = feather(w + 2 * (P - R), h + 2 * (P - R), R)
        g[y - P:y + h + P, x - P:x + w + P] = np.clip(best[1] * fm + tgt * (1 - fm), 0, 255).astype(np.uint8)
    out.append(g)
vf = 'scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920' + (',unsharp=5:5:0.7:5:5:0' if W < 1080 else '')
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                       '-i', src, '-map', '0:v', '-map', '1:a', '-vf', vf, '-c:v', 'libx264', '-crf', '14', '-preset', 'slow',
                       '-pix_fmt', 'yuv420p', '-c:a', 'copy', dst], stdin=subprocess.PIPE)
for g in out: ff.stdin.write(g.tobytes())
ff.stdin.close(); ff.wait(); print(len(out), 'frame ->', dst)
