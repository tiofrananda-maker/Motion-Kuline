"""Kata meragukan? Biarkan model akustik memilih versi yang paling cocok dengan BUNYI-nya.
python tools/pilih.py <file_video> <mulai> <selesai> "versi satu|versi dua|versi tiga"
Contoh: python tools/pilih.py FOOTAGE/x/tes.mp4 27.7 34.4 "bayarannya berapa nanti|bayarannya yang gak seberapa nanti"
Skor makin mendekati 0 = makin cocok. Selisih < 3 = sama-sama mungkin -> dengar ulang / laporkan ke Tio.
Tulis angka dalam bentuk angka (10.000), alat ini mengubahnya ke ucapan sendiri."""
import sys, subprocess, numpy as np
from common import ROOT
from align import Aligner, spoken
import os
f, a, b, alts = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4].split('|')
al = Aligner(os.path.join(ROOT, 'models', 'sherpa-onnx-dolphin-small-ctc-multi-lang-int8-2025-04-02'))
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', f, '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
lp = al.logprobs(np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768)
def score(text):
    toks = [t for w in text.split() for p in spoken(w) for t in al.tokenize_word(p)]
    S = 2 * len(toks) + 1; ext = np.zeros(S, np.int64); ext[1::2] = toks; NEG = -1e9
    dp = np.full(S, NEG, np.float32); dp[0] = lp[0, 0]; dp[1] = lp[0, ext[1]]
    skip = np.zeros(S, bool); skip[3::2] = ext[3::2] != ext[1:-2:2]
    for t in range(1, lp.shape[0]):
        dp = np.max(np.stack([dp, np.concatenate([[NEG], dp[:-1]]), np.where(skip, np.concatenate([[NEG, NEG], dp[:-2]]), NEG)]), 0) + lp[t, ext]
    return float(max(dp[-1], dp[-2]))
print('Dolphin dengar:', al.greedy(lp))
for s, t in sorted(((score(t.strip()), t.strip()) for t in alts), reverse=True): print(f'{s:9.1f}  {t}')
