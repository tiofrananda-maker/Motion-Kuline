"""Caption VO (gaya referensi: huruf kecil, kecil, di tengah, muncul kata demi kata).
python tools/captions.py          -> buat edit/captions.json (kalau belum ada) lalu tulis src/data.json
python tools/captions.py ulang    -> buat ulang edit/captions.json dari timeline (setelah edl/build berubah)

edit/captions.json = daftar frasa [{"t": "pertama tusuk sosis", "s": 21.6, "e": 23.1, "w": [[kata, mulai, selesai], ...]}]
- "t" WAJIB persis ucapan VO. Betulkan kata yang salah dengar di "t" saja; waktu tetap dari "w".
  Jumlah kata sama -> waktu per kata dipakai; beda -> waktu dibagi rata sepanjang frasa.
- Hapus frasa = tidak ditampilkan. Gabung/pisah frasa boleh (atur "s"/"e").
edit/resep.json = teks tetap (nama akun, judul pembuka, ajakan komentar), lihat contoh di template."""
import json, os, re, sys
from common import ROOT, load
TW = load('raw/timeline_words.json')
R = load('edit/resep.json')
cp = os.path.join(ROOT, 'edit', 'captions.json')
MAXW, MAXC, GAP = 6, 34, 0.35

def phrases(words):
    out, cur = [], []
    for i, wd in enumerate(words):
        w, s, e = wd[:3]; baru = len(wd) > 3
        if cur and (baru or s - cur[-1][2] > GAP or len(cur) >= MAXW or len(' '.join(x[0] for x in cur + [[w]])) > MAXC):
            out.append(cur); cur = []
        cur.append([w, s, e])
        if re.search(r'[.,!?;:]$', w): out.append(cur); cur = []
    if cur: out.append(cur)
    # gabungkan frasa satu kata ke frasa sesudahnya kalau masih muat (hindari kata yatim)
    res = []
    for p in out:
        if res and len(res[-1]) == 1 and len(res[-1]) + len(p) <= MAXW + 1 and len(p[0]) == 3 and p[0][1] - res[-1][-1][2] < GAP * 2 and not re.search(r'[.!?]$', res[-1][0][0]):
            res[-1] = res[-1] + p
        else:
            res.append(p)
    return [{'t': ' '.join(x[0] for x in p), 's': p[0][1], 'e': p[-1][2], 'w': p} for p in res]

if not os.path.exists(cp) or (len(sys.argv) > 1 and sys.argv[1] == 'ulang'):
    json.dump(phrases(TW['words']), open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('dibuat', cp, '-> cek & betulkan teksnya (harus persis ucapan VO)')
caps = json.load(open(cp, encoding='utf-8'))
total = TW['total']

def clean(w):
    w = w.lower() if R.get('huruf_kecil', True) else w
    return re.sub(r'[.,!;:"]+$', '', w)   # tanda tanya dipertahankan seperti referensi

judul = R['judul']; cta = R['cta']
t_judul = judul.get('sampai', 2.4)
t_cta = cta.get('mulai')
segs = {x['id']: x for x in (load('edit/timeline.json', {}).get('segments', []))}
if t_cta is None and 'cta' in segs: t_cta = segs['cta']['start']     # ajakan muncul tepat di potongan segmen "cta"
if t_cta is None:
    key = cta['kata'].lower()
    hit = [c for c in caps if key in c['t'].lower().replace(' ', '') or key in c['t'].lower()]
    t_cta = hit[-1]['s'] if hit else max(0, total - 4)
out = []
for c in caps:
    if c['e'] <= t_judul + 0.05 or c['s'] >= t_cta - 0.05: continue   # judul & ajakan tampil tanpa caption
    toks = [clean(x) for x in c['t'].split()]
    if len(toks) == len(c['w']):
        ws = [[toks[i], c['w'][i][1], c['w'][i][2]] for i in range(len(toks))]
    else:
        n = sum(len(t) + 1 for t in toks); acc = c['s']; ws = []
        for t in toks:
            d = (c['e'] - c['s']) * (len(t) + 1) / n; ws.append([t, round(acc, 3), round(acc + d, 3)]); acc += d
    s = max(c['s'], t_judul + 0.1)
    out.append({'s': round(s, 3), 'e': round(min(c['e'] + 0.35, t_cta - 0.1), 3), 'w': ws})
# frasa berikut menggantikan frasa sebelumnya: tutup frasa tepat saat frasa baru mulai
for a, b in zip(out, out[1:]):
    a['e'] = round(min(a['e'], b['s']), 3)
data = {'total': total, 'handle': R.get('handle', ''), 'judul': {**judul, 'sampai': t_judul},
        'cta': {**cta, 'mulai': round(t_cta, 3)}, 'captions': out}
json.dump(data, open(os.path.join(ROOT, 'src', 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'frasa caption | judul 0 -', t_judul, '| ajakan mulai', round(t_cta, 2), '| total', total)
