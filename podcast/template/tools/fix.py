"""Pasang transkrip yang sudah DIBETULKAN Claude lalu hitung ulang waktu tiap kata (ATURAN KERAS: caption = ucapan).
python tools/fix.py <file_atau_folder_footage>
Pertama kali: membuat edit/transkrip.json dari raw/words.json  {kunci: ["teks segmen 0", "teks segmen 1", ...]}.
Betulkan teksnya (pakai raw/crosscheck.txt + dengar ulang), simpan, jalankan lagi -> raw/words.json diperbarui.
Jumlah segmen jangan diubah; kalau satu segmen kosong "" berarti tidak ada ucapan yang dipakai."""
import sys, os, json, subprocess
import numpy as np
from common import ROOT, footage_files, clip_key
from align import Aligner
src = sys.argv[1]
files = {clip_key(src): src} if os.path.isfile(src) else footage_files(src)
wp = os.path.join(ROOT, 'raw', 'words.json'); W = json.load(open(wp, encoding='utf-8'))
tp = os.path.join(ROOT, 'edit', 'transkrip.json')
if not os.path.exists(tp):
    os.makedirs(os.path.dirname(tp), exist_ok=True)
    json.dump({k: [s['t'] for s in v['segs']] for k, v in W.items() if k in files}, open(tp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(f'dibuat {tp} -- betulkan teksnya lalu jalankan lagi')
T = json.load(open(tp, encoding='utf-8'))
al = Aligner(os.path.join(ROOT, 'models', 'sherpa-onnx-dolphin-small-ctc-multi-lang-int8-2025-04-02'))
for k, texts in T.items():
    if k not in files or k not in W: continue
    segs = W[k]['segs']; assert len(texts) == len(segs), f'{k}: jumlah segmen harus {len(segs)}'
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', files[k], '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    n = 0
    for s, t in zip(segs, texts):
        if t == s['t'] and s.get('fixed'): continue
        sub = x[int(s['s'] * 16000):int(s['e'] * 16000)]; ws = t.split()
        words = [[wd, round(s['s'] + a, 2), round(s['s'] + b, 2)] for wd, a, b in al.align(sub, ws)] if ws else []
        for i in range(len(words)):
            nxt = words[i + 1][1] if i + 1 < len(words) else s['e']
            words[i][2] = round(min(max(words[i][2], nxt), words[i][1] + 0.6), 2)
        s.update(t=t, words=words, fixed=True); n += 1
    print(k, n, 'segmen dihitung ulang')
json.dump(W, open(wp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
