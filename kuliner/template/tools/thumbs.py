"""Lembar kontak semua klip (1 frame/klip, label kunci+durasi): python tools/thumbs.py <folder_footage>
Hasil: raw/thumbs/sheetN.jpg. Untuk detail per detik: python tools/thumbs.py <folder_footage> strip 0988 0989"""
import sys, os, subprocess
from PIL import Image, ImageDraw
from common import ROOT, footage_files, duration
files = footage_files(sys.argv[1]); O = os.path.join(ROOT, 'raw', 'thumbs'); os.makedirs(O, exist_ok=True)
def frame(f, t, w, h):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', f, '-frames:v', '1', '-vf', f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert('RGB') if raw else Image.new('RGB', (w, h))
def label(im, txt):
    dr = ImageDraw.Draw(im); dr.rectangle((0, 0, 8 * len(txt) + 6, 16), fill=(0, 0, 0)); dr.text((3, 2), txt, fill=(255, 255, 0)); return im
if len(sys.argv) > 2 and sys.argv[2] == 'strip':
    rows = []
    for k in sys.argv[3:]:
        d = duration(files[k]); n = min(16, int(d) + 1)
        row = Image.new('RGB', (96 * 16, 170))
        for i in range(n): row.paste(label(frame(files[k], min(i, d - 0.1), 96, 170), f'{k} {i}s'), (i * 96, 0))
        rows.append(row)
    o = Image.new('RGB', (96 * 16, 170 * len(rows)))
    for i, r in enumerate(rows): o.paste(r, (0, i * 170))
    o.save(os.path.join(O, 'strip.jpg'), quality=80); print(os.path.join(O, 'strip.jpg'))
else:
    ks = list(files); W = 10
    for n in range(0, len(ks), 40):
        sub = ks[n:n + 40]; o = Image.new('RGB', (160 * W, 284 * ((len(sub) + W - 1) // W)))
        for i, k in enumerate(sub):
            d = duration(files[k]); o.paste(label(frame(files[k], d / 2, 160, 284), f'{k} {d:.0f}s'), ((i % W) * 160, (i // W) * 284))
        p = os.path.join(O, f'sheet{n // 40}.jpg'); o.save(p, quality=80); print(p)
