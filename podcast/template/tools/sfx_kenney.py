"""Bangun SFX per peran dari folder SOUND EFFEC (paket Kenney, CC0) -> public/sfx/k/<peran>-N.wav.
python tools/sfx_kenney.py "C:\\MOTION KULINER\\SOUND EFFEC"
Tiap peran = beberapa lapisan (file, kecepatan, gain dB, jeda, filter). Kecepatan < 1 = lebih berat/panjang (whoosh tebal).
Hasil disamakan kerasnya (RMS bagian terkeras), puncak dibatasi -1 dB, dan titik puncaknya digeser ke PK detik
supaya waktu di compile.py pas (contoh: whoosh "in" diputar 0,1 dtk sebelum cutaway, puncaknya tepat di potongan)."""
import os, subprocess, sys, wave
import numpy as np
from common import ROOT

SR = 48000
OUT = os.path.join(ROOT, 'public', 'sfx', 'k')

def L(f, rate=1.0, db=0, at=0.0, af=''):
    return (f, rate, db, at, af)

R = {  # peran: [varian: [lapisan]]
    'in':    [[L(f'casino-audio/card-shove-{i}.ogg', 0.55), L(f'casino-audio/card-shove-{i}.ogg', 1.0, -5, 0.08)] for i in (1, 2, 3, 4)],
    'out':   [[L(f'casino-audio/card-slide-{i}.ogg', 0.7)] for i in (1, 2, 3, 4)],
    'hit':   [[L(f'impact-sounds/impactPunch_heavy_{i:03d}.ogg'), L(f'impact-sounds/impactPunch_heavy_{i:03d}.ogg', 0.5, -2, 0, 'lowpass=f=300')] for i in (0, 1, 2)],
    'punch': [[L(f'impact-sounds/impactSoft_heavy_{i:03d}.ogg', 0.85)] for i in (0, 1, 2)],
    'blur':  [[L('casino-audio/card-shove-1.ogg', 0.4, 0, 0, 'lowpass=f=1800')]],
    'wipe':  [[L('casino-audio/card-shove-4.ogg', 0.45), L('casino-audio/card-shove-2.ogg', 0.8, -4, 0.12)]],
    'pop':   [[L('interface-sounds/drop_002.ogg')], [L('interface-sounds/drop_003.ogg')]],
    'tick':  [[L('interface-sounds/tick_002.ogg')], [L('interface-sounds/tick_004.ogg')]],
    'hook':  [[L('impact-sounds/impactPunch_medium_000.ogg'), L('impact-sounds/impactPunch_medium_000.ogg', 0.5, -3, 0, 'lowpass=f=250')]],
    'tok':   [[L('interface-sounds/pluck_001.ogg')], [L('interface-sounds/pluck_002.ogg')]],
    'rise':  [[L('digital-audio/phaserUp3.ogg')]],
    'page':  [[L('rpg-audio/bookFlip1.ogg')]],
    # --- bunyi yang akrab di CapCut/TikTok (dipakai compile.py, lihat ATURAN bagian SFX) ---
    'key':    [[L(f'ui-audio/{f}.ogg')] for f in ('switch26', 'switch28', 'click3', 'switch19', 'click5', 'switch30')],   # ketikan keyboard
    'kretik': [[L('ui-audio/switch22.ogg'), L('ui-audio/click2.ogg', 1.0, -4), L('ui-audio/switch13.ogg', 1.0, -3, 0.03)],
               [L('ui-audio/switch23.ogg'), L('ui-audio/click2.ogg', 0.9, -4), L('ui-audio/switch14.ogg', 1.0, -3, 0.028)]],  # "krtik" keyboard mekanik
    'tik':    [[L('interface-sounds/tick_001.ogg')], [L('interface-sounds/tick_002.ogg')]],
    'tanya':  [[L('interface-sounds/question_003.ogg')], [L('interface-sounds/question_001.ogg')]],      # nada naik "hm?"
    'ding':   [[L('interface-sounds/glass_001.ogg'), L('interface-sounds/glass_004.ogg', 1.0, -10)], [L('interface-sounds/confirmation_003.ogg')]],
    'boom':   [[L('sci-fi-sounds/lowFrequency_explosion_000.ogg', 0.9, 0, 0, 'highpass=f=40'), L('impact-sounds/impactPunch_heavy_000.ogg', 0.6, -2, 0, 'lowpass=f=900')]],  # "vine boom"
    'kaching': [[L('casino-audio/chips-handle-2.ogg'), L('rpg-audio/handleCoins2.ogg', 1.0, -3, 0.05)]],
    'salah':  [[L('interface-sounds/error_006.ogg')], [L('interface-sounds/error_008.ogg')]],          # buzzer salah
    'scratch': [[L('interface-sounds/scratch_005.ogg', 0.8)]],                                          # rekaman tergores
    'kilau':  [[L('digital-audio/powerUp5.ogg'), L('interface-sounds/glass_004.ogg', 1.0, -6, 0.05)]],    # kilau/sparkle
    'tada':   [[L('music-jingles/jingles_PIZZI00.ogg')], [L('music-jingles/jingles_SAX00.ogg')]],       # stinger lucu
}
PK = {'in': 0.10, 'out': 0.08, 'blur': 0.2, 'wipe': 0.3, 'rise': 0.25, 'page': 0.1, 'tok': 0.02, 'kilau': 0.08}   # detik sebelum puncak
RMS = {'in': -13, 'out': -15, 'hit': -12, 'punch': -14, 'blur': -14, 'wipe': -13, 'pop': -14, 'tick': -16,
       'hook': -13, 'tok': -14, 'rise': -16, 'page': -16,
       'key': -17, 'kretik': -16, 'tik': -17, 'tanya': -17, 'ding': -16, 'boom': -14, 'kaching': -16, 'salah': -16,
       'scratch': -15, 'kilau': -17, 'tada': -16}                                              # dBFS jendela 150 ms terkeras
MAXD = {'in': 0.85, 'out': 0.6, 'blur': 1.0, 'wipe': 0.95, 'boom': 1.1, 'ding': 0.7, 'tada': 0.8}   # potong ekor panjang (detik)

def load(src, f, rate, af):
    flt = f'asetrate={int(44100 * rate)},aresample={SR}' + (',' + af if af else '')
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(src, f), '-af', flt, '-ac', '2', '-ar', str(SR),
                        '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2)

def build(src, layers, role):
    parts = [(load(src, f, r, af) * 10 ** (db / 20), int(at * SR)) for f, r, db, at, af in layers]
    x = np.zeros((max(len(a) + o for a, o in parts), 2), np.float32)
    for a, o in parts: x[o:o + len(a)] += a
    e = np.sqrt(np.convolve((x ** 2).mean(1), np.ones(int(0.03 * SR)) / int(0.03 * SR), 'same'))
    on = np.argmax(e > e.max() * 0.05)                     # awal bunyi
    pk = PK.get(role, 0.0)
    i = max(on, np.argmax(e) - int(pk * SR)) if pk else on
    x = x[i:] if i >= 0 else x
    if pk and np.argmax(e) - on < pk * SR:                  # puncak terlalu dekat awal: tambah hening di depan
        x = np.vstack([np.zeros((int(pk * SR) - (np.argmax(e) - on), 2), np.float32), x])
    e = np.sqrt(np.convolve((x ** 2).mean(1), np.ones(int(0.03 * SR)) / int(0.03 * SR), 'same'))
    x = x[:min(len(x), len(e) - np.argmax(e[::-1] > e.max() * 0.03) + int(0.06 * SR))]   # buang ekor desis
    w = int(0.15 * SR); p = (x ** 2).mean(1)
    loud = np.sqrt(np.convolve(p, np.ones(w) / w, 'valid').max()) if len(p) > w else np.sqrt(p.mean())
    x *= 10 ** (RMS[role] / 20) / max(loud, 1e-6)
    f = int(0.004 * SR); x[:f] *= np.linspace(0, 1, f)[:, None]
    if role in MAXD: x = x[:int(MAXD[role] * SR)]
    t = int(min(0.25 if role in MAXD else 0.12, len(x) / SR / 4) * SR); x[-t:] *= np.linspace(1, 0, t)[:, None]
    return x

def save(x, path):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                        '-af', 'alimiter=limit=0.89:attack=1:release=40:level=disabled', '-c:a', 'pcm_s16le', path],
                       input=x.astype(np.float32).tobytes(), capture_output=True)
    if r.returncode: raise SystemExit(r.stderr.decode())

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', '..', 'SOUND EFFEC')
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.wav'): os.remove(os.path.join(OUT, f))
    lines = []
    for role, vs in R.items():
        for n, layers in enumerate(vs, 1):
            x = build(src, layers, role); name = f'{role}-{n}.wav'; save(x, os.path.join(OUT, name))
            lines.append(f'{name}: ' + ' + '.join(f'{l[0]} (x{l[1]})' for l in layers))
            print(f'{name:10s} {len(x) / SR:4.2f}s')
    open(os.path.join(OUT, 'SUMBER.txt'), 'w', encoding='utf-8').write(
        'SFX dari paket Kenney (kenney.nl), lisensi CC0, folder SOUND EFFEC milik Tio. Diolah oleh tools/sfx_kenney.py.\n' + '\n'.join(lines) + '\n')
