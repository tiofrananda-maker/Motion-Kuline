"""Lacak posisi wajah per frame di public/base.webm -> raw/face.json (dipakai zoom "dinamis" supaya wajah tetap di tengah saat zoom dekat).
python tools/face.py"""
import json, os, subprocess
import cv2, numpy as np
from common import ROOT
src = os.path.join(ROOT, 'public', 'base.webm')
sw, sh = map(int, subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                          '-of', 'csv=p=0', src]).decode().split(',')[:2])
W, H = (480, 270) if sw > sh else (270, 480)   # potret atau lanskap
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'fps=30,scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W)
if not hasattr(cv2, 'CascadeClassifier'):
    raise SystemExit('OpenCV ini tidak punya pendeteksi wajah Haar. Jalankan: python -m pip install "opencv-python-headless<5"')
cc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
xy = []
for g in fr:
    f = cc.detectMultiScale(cv2.equalizeHist(g), 1.1, 5, minSize=(30, 30))
    if len(f):
        x, y, w, h = max(f, key=lambda r: r[2] * r[3]); xy.append([(x + w / 2) / W, (y + h / 2) / H])
    else: xy.append(None)
known = [i for i, v in enumerate(xy) if v]
if not known: xy = [[0.5, 0.4]] * len(xy)
else:
    for i in range(len(xy)):
        if xy[i] is None:
            j = min(known, key=lambda k: abs(k - i)); xy[i] = xy[j]
a = np.array(xy)
# haluskan, tapi jangan melintasi lompatan framing (jump cut sumber)
seg = [0] + [i for i in range(1, len(a)) if np.hypot(*(a[i] - a[i - 1])) > 0.06] + [len(a)]
out = a.copy()
for s0, s1 in zip(seg[:-1], seg[1:]):
    for i in range(s0, s1):
        lo, hi = max(s0, i - 6), min(s1, i + 7); out[i] = a[lo:hi].mean(0)
json.dump({'fps': 30, 'xy': [[round(x, 4), round(y, 4)] for x, y in out]}, open(os.path.join(ROOT, 'raw', 'face.json'), 'w'))
print(len(out), 'frame, wajah terdeteksi', len(known), ', lompatan framing', len(seg) - 2)
