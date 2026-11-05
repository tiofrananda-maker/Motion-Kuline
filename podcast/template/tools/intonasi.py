"""Ukur tekanan ucapan per kata dari public/voice.wav (dipakai compile.py untuk SFX ketik yang mengikuti intonasi talent).
Tekanan = gabungan keras suara (dB) dan tinggi nada (F0) kata itu dibanding kata lain di frasa yang sama (skor z)."""
import os, subprocess, numpy as np
from common import ROOT
SR = 16000

def _load():
    p = os.path.join(ROOT, 'public', 'voice.wav')
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32)

def _f0(x):
    """nada dasar (Hz) potongan suara dengan autokorelasi, 0 kalau tidak bersuara"""
    if len(x) < 640 or np.sqrt((x ** 2).mean()) < 0.01: return 0.0
    x = x - x.mean(); r = np.correlate(x, x, 'full')[len(x) - 1:]
    lo, hi = SR // 400, SR // 75
    k = lo + int(np.argmax(r[lo:hi])); return SR / k if r[k] > 0.3 * r[0] else 0.0

def tekanan(phrases):
    """phrases: [[(t_mulai, t_selesai), ...], ...] -> skor per kata dengan bentuk yang sama"""
    x = _load(); out = []
    for ws in phrases:
        db, f0 = [], []
        for a, b in ws:
            s = x[int(a * SR):int(min(b, a + 0.35) * SR)]
            db.append(20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-6) if len(s) else -60)
            fr = [_f0(s[i:i + 640]) for i in range(0, max(0, len(s) - 640), 320)]; fr = [f for f in fr if f]
            f0.append(np.median(fr) if fr else 0.0)
        db = np.array(db); f0 = np.array(f0)
        z = lambda v: (v - v.mean()) / (v.std() + 1e-6) if len(v) > 2 else np.zeros_like(v)
        fz = z(np.where(f0 > 0, f0, f0[f0 > 0].mean() if (f0 > 0).any() else 0))
        out.append(list(np.round(0.6 * z(db) + 0.4 * fz, 2)))
    return out

def keras(spans):
    """[(mulai, selesai), ...] -> [(keras dB (RMS 100 ms terkeras), nada F0 median Hz), ...] tiap rentang, untuk deteksi teriak"""
    x = _load(); out = []; w = int(0.1 * SR)
    for a, b in spans:
        s = x[int(a * SR):int(b * SR)]
        if len(s) < w: out.append((-60.0, 0.0)); continue
        p = np.convolve(s ** 2, np.ones(w) / w, 'valid')
        fr = [_f0(s[i:i + 640]) for i in range(0, len(s) - 640, 320)]; fr = [f for f in fr if f]
        out.append((float(10 * np.log10(p.max() + 1e-12)), float(np.median(fr)) if fr else 0.0))
    return out
