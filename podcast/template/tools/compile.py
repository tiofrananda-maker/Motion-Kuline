"""Gabungkan edit/clip.json + raw/timeline_words.json -> src/data.json (dipakai Remotion). Cepat, jalankan tiap ubah teks.
python tools/compile.py

CAPTION (clip.json "captions"): daftar frasa BERURUTAN, teks PERSIS seperti yang diucapkan talent.
  "ini satu / **pertanda**"         '/' = ganti baris
  tanda gaya (boleh lebih dari satu kata):  **tebal besar**  *serif besar*  _serif miring kecil_  ~sans miring~
  ^kata^ = warna kuning (bisa digabung: ^**GRIT**^)
  frasa juga boleh objek: {"t": "...", "pos": "top|mid|low|bottom", "mode": "box"}   bottom = di bawah tulisan bawaan footage
  "caption_pos": "bottom" di clip.json = posisi semua frasa (mis. wajah talent ada di tengah/bawah frame, video ramai-ramai)
CUTAWAY (clip.json "cutaways"): {"p": [3,5], "type": ..., ...}  p = dari frasa ke-3 sampai frasa ke-5 (mulai 0)
  type: video {src: "broll/x.mp4" | q: "kata kunci", start?, rate?, bright?, x?}  klip B-roll stok penuh layar (gelap sinematik), caption ke tengah
              x = posisi crop klip horizontal (0 kiri, 0.5 tengah, 1 kanan)
        split {src | q, talent?: atas|bawah, start?, rate?, bright?, x?, y?}  DUA LAYER: talent di separuh layar (default atas),
              B-roll nyata di separuh lain (geser masuk dari tepi). Caption di garis tengah. Split berurutan dengan posisi talent
              sama menyambung (talent diam, klip B-roll berganti). Klip horizontal paling pas; y = posisi crop vertikal.
        card  {bg: red|gray|split|dark, img?}       latar penuh, caption pindah ke tengah kartu
        image {img, dim?}                           gambar penuh (zoom pelan), caption tetap
        person {img, name}                          foto + nama serif miring merah di atas latar abu
        icons {icons: [{i: "lucide:bot"|"simple:openai", x, y, s?}], bg?: white}  ikon muncul satu-satu, caption jadi kotak
        stat  {value: "0,1%", color?: yellow|white}  angka besar di atas talent
        news  {source, title, sub?}                 kartu berita di atas talent, caption jadi kotak
        logos {icons: [...]}                         logo muncul di atas talent
FX (clip.json "fx"): {"p": 7, "type": flash|blur|punch|wipe}  di awal frasa ke-7
SFX ala CapCut, SELEKTIF (bukan tiap kata): maks satu bunyi per frasa sesuai tekanan suara talent. Kata gaya (tebal/kuning)
  yang paling ditekan = "kretik" (+ "tik" kalau kuning), frasa tanpa kata gaya = "key" hanya kalau ada kata yang jelas ditekan,
  kalimat tanya = "tanya", frasa teriak (>= 4 dB di atas median + nada tinggi) = "boom" otomatis. Frasa bisa minta bunyi aksen:
  {"t": "...", "sfx": "ding"|"boom"|"kaching"|"salah"|"scratch"|"kilau"|"tada"}. FX bisa ganti bunyi: {"p": 3, "type": "flash", "sfx": "boom"}
  "ketik": false / "boom_auto": false = matikan. Bahan: tools/sfx_kenney.py (paket Kenney di folder SOUND EFFEC).
FX "defocus" (p = frasa pembuka): talent kabur+gelap sebentar (maks 0,5 dtk, ubah dengan "dur") lalu fokus tajam (kesan mahal)
HOOK (clip.json "hook"): {"text": "TANDA KALIAN SUKSES...", "until_p": 1}  label merah di atas sampai akhir frasa 1
LOOK (clip.json "look": "premium" (standar) | "standar")  premium = grade sinematik, vignette + gradasi bawah, grain film halus, flash lebih lembut
FORMAT (clip.json "format": "potret" (standar, 1080x1920) | "lanskap" (1920x1080, YouTube/FB))  split di lanskap = kiri/kanan ("talent": "kiri"|"kanan")
ZOOM (clip.json "zoom": "dinamis" (standar) | "bergantian")  framing berganti per kalimat mengikuti wajah (jalankan tools/face.py dulu); frasa {"z": 1.0} = paksa lebar"""
import json, os, re, difflib
from common import ROOT
clip = json.load(open(os.path.join(ROOT, 'edit', 'clip.json'), encoding='utf-8'))
TL = json.load(open(os.path.join(ROOT, 'raw', 'timeline_words.json'), encoding='utf-8'))
words = TL['words']; total = TL['total']
SYN = {'gue': 'gw', 'gua': 'gw', 'gw': 'gw', 'aku': 'aku', 'nggak': 'gak', 'enggak': 'gak', 'ngga': 'gak', 'ga': 'gak', 'gak': 'gak',
       'tahu': 'tau', 'tau': 'tau', 'saja': 'aja', 'aja': 'aja', 'udah': 'udah', 'sudah': 'udah', 'dapat': 'dapet', 'dapet': 'dapet'}
def norm(w):
    w = re.sub(r"[^\w]", '', w.lower()); return SYN.get(w, w)

def parse(text):
    """-> lines: [[{w, st, y}]]  st = s|B|S|si|i"""
    lines, cur = [], []; on = {'B': False, 'S': False, 'si': False, 'i': False, 'y': False}
    OPEN = [('^', 'y'), ('**', 'B'), ('*', 'S'), ('_', 'si'), ('~', 'i')]
    for tok in text.split():
        if tok == '/':
            lines.append(cur); cur = []; continue
        m = re.match(r'^(.*?)([.,!?…:;"\')]*)$', tok); w, tail = m.group(1), m.group(2)
        changed = True
        while changed:
            changed = False
            for mk, k in OPEN:
                if w.startswith(mk) and len(w) > len(mk): on[k] = True; w = w[len(mk):]; changed = True; break
        closes = []; changed = True
        while changed:
            changed = False
            for mk, k in OPEN:
                if w.endswith(mk) and len(w) > len(mk) and not (mk == '*' and w.endswith('**') and k == 'S' and on['B'] and not on['S']):
                    closes.append(k); w = w[:-len(mk)]; changed = True; break
        st = 'B' if on['B'] else 'S' if on['S'] else 'si' if on['si'] else 'i' if on['i'] else 's'
        cur.append({'w': w + tail, 'st': st, 'y': on['y']})
        for k in closes: on[k] = False
    if cur: lines.append(cur)
    return lines

# 1) frasa + cocokkan kata ke waktu ucapan
phr = []
for c in clip.get('captions', []):
    o = c if isinstance(c, dict) else {'t': c}
    if clip.get('caption_pos') and 'pos' not in o: o = {**o, 'pos': clip['caption_pos']}   # posisi caption semua frasa
    phr.append({**o, 'lines': parse(o['t'])})
cap_tokens = [(pi, li, wi, norm(w['w'])) for pi, p in enumerate(phr) for li, l in enumerate(p['lines']) for wi, w in enumerate(l)]
A = [t[3] for t in cap_tokens]; B = [norm(w[0]) for w in words]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
times = [None] * len(A)
for a, b, n in sm.get_matching_blocks():
    for j in range(n): times[a + j] = words[b + j][1]
# interpolasi yang tidak cocok
known = [i for i, t in enumerate(times) if t is not None]
for i in range(len(times)):
    if times[i] is None:
        prv = max([k for k in known if k < i], default=None); nxt = min([k for k in known if k > i], default=None)
        if prv is None and nxt is None: times[i] = 0.0
        elif prv is None: times[i] = max(0.0, times[nxt] - 0.25 * (nxt - i))
        elif nxt is None: times[i] = times[prv] + 0.25 * (i - prv)
        else: times[i] = times[prv] + (times[nxt] - times[prv]) * (i - prv) / (nxt - prv)
for (pi, li, wi, _), t in zip(cap_tokens, times):
    phr[pi]['lines'][li][wi]['t'] = round(t, 3)
match_ratio = sum(1 for t in sm.get_matching_blocks() for _ in range(t[2])) / max(1, len(B))
for i, p in enumerate(phr):
    ts = [w['t'] for l in p['lines'] for w in l]
    p['start'] = round(min(ts) - 0.06, 3)
for i, p in enumerate(phr):
    last = max(w['t'] for l in p['lines'] for w in l)
    nxt = phr[i + 1]['start'] if i + 1 < len(phr) else total
    p['end'] = round(min(nxt, last + 0.9) if nxt - last < 1.4 else last + 0.6, 3)
    p.pop('t', None)

def span(c):
    if 'p' in c:
        a, b = (c['p'], c['p']) if isinstance(c['p'], int) else c['p']
        return phr[a]['start'], phr[b]['end']
    return c['from'], c['to']

cuts = []
for c in clip.get('cutaways', []):
    s, e = span(c); cuts.append({**{k: v for k, v in c.items() if k != 'p'}, 'from': round(s, 3), 'to': round(e, 3)})
fx = []
for f in clip.get('fx', []):
    at = phr[f['p']]['start'] if 'p' in f else f['at']
    e = {**{k: v for k, v in f.items() if k != 'p'}, 'at': round(at, 3)}
    if f['type'] == 'defocus':   # blur pembuka singkat (Tio: "jangan kelamaan"), maks 0,5 dtk atau "dur"
        e['to'] = round(min(phr[f['p']]['end'] if 'p' in f else f['to'], at + f.get('dur', 0.5)), 3)
    fx.append(e)
hook = clip.get('hook')
if hook:
    hook = {**hook, 'until': round(phr[hook['until_p']]['end'], 3) if 'until_p' in hook else hook.get('until', 3)}

# 2) SFX otomatis (paket SOUND EFFEC Tio, sudah dinormalkan di public/sfx/k/<peran>-<n>.wav, lihat SUMBER.txt)
#    Gaya referensi: tiap pergantian visual ada bunyinya, cukup keras supaya terasa.
SFX = []
K = os.path.join(ROOT, 'public', 'sfx', 'k')
_n = {}
def role(r):
    fs = sorted(f for f in os.listdir(K) if f.startswith(r + '-')) if os.path.isdir(K) else []
    if not fs: return None
    _n[r] = _n.get(r, -1) + 1; return 'sfx/k/' + fs[_n[r] % len(fs)]
def sfx(r, t, v):
    f = role(r)
    if f: SFX.append({'f': f, 't': round(max(0, t), 3), 'v': v})
if hook: sfx('hook', 0.05, 0.75)
near_fx = lambda t: any(abs(f['at'] - t) < 0.35 for f in fx if f['type'] in ('flash', 'punch', 'wipe'))   # efek sudah punya bunyi sendiri
for c in cuts:
    ty = c['type']
    if ty in ('card', 'image', 'person', 'video', 'split') and not near_fx(c['from']): sfx('in', c['from'] - 0.1, 0.9)
    nxt_in = any(abs(o['from'] - c['to']) < 0.25 for o in cuts if o is not c)
    if ty in ('card', 'image', 'person', 'video', 'split', 'icons') and c['to'] < total - 0.3 and not nxt_in and not near_fx(c['to']): sfx('out', c['to'] - 0.08, 0.7)
    if ty == 'stat': sfx('rise', c['from'] - 0.25, 0.55); sfx('pop', c['from'] + 0.05, 0.85)
    if ty == 'logos':
        for k, ic in enumerate(c.get('icons', [])): sfx('pop', c['from'] + k * 0.27, 0.85)
    if ty == 'news': sfx('page', c['from'], 0.7)
    if ty == 'icons':
        for k, ic in enumerate(c.get('icons', [])): sfx('tick', c['from'] + 0.27 + k * 0.33, 0.55)
VOL = {'ding': 0.8, 'boom': 0.95, 'kaching': 0.7, 'salah': 0.75, 'scratch': 0.8, 'kilau': 0.7, 'tada': 0.7, 'tanya': 0.6,
       'pop': 0.85, 'in': 0.9, 'out': 0.7, 'hit': 0.85, 'punch': 0.75, 'tik': 0.6, 'kretik': 0.8, 'key': 0.45, 'rise': 0.55}
for f in fx:
    if 'sfx' in f:   # bunyi efek diganti sendiri, mis. {"type": "flash", "sfx": "boom"}; false = tanpa bunyi
        if f['sfx']: sfx(f['sfx'], f['at'], VOL.get(f['sfx'], 0.8))
        continue
    if f['type'] == 'flash': sfx('hit', f['at'], 0.85)
    if f['type'] == 'punch': sfx('punch', f['at'], 0.75)
    if f['type'] == 'blur': sfx('blur', f['at'] - 0.2, 0.8)
    if f['type'] == 'wipe': sfx('wipe', f['at'] - 0.3, 0.85)
    if f['type'] == 'defocus' and not any('/in-' in x['f'] and abs(x['t'] - (f['to'] - 0.1)) < 0.3 for x in SFX):
        sfx('in', f['to'] - 0.1, 0.9)   # cutaway di akhir defocus sudah punya whoosh sendiri
# SFX per frasa: {"t": "...", "sfx": "ding"} atau ["ding", "boom"], diputar di kata tebal/kuning pertama (atau awal frasa).
# Peran ala CapCut: ding, boom (vine boom), kaching, salah (buzzer), scratch, kilau, tada, tanya, pop, in (whoosh).
def accent(p):
    ww = [w for l in p['lines'] for w in l]
    return next((w['t'] for w in ww if w['y'] or w['st'] in ('B', 'S')), ww[0]['t'])
for p in phr:
    for r in ([p['sfx']] if isinstance(p.get('sfx'), str) else p.get('sfx') or []):
        sfx(r, accent(p) - 0.02, VOL.get(r, 0.8))
# TERIAK = intonasi: frasa yang jauh lebih keras (>= 4 dB di atas median) DAN nadanya tinggi (>= 1,4x median F0) otomatis
# dapat "boom" (vine boom) menggantikan bunyi hit/punch di situ. "boom_auto": false di clip.json = matikan.
if clip.get('boom_auto', True) and role('boom') and len(phr) >= 3:
    _n.pop('boom', None)
    from intonasi import keras
    kk = keras([(p['start'] + 0.06, p['end']) for p in phr])
    mdb = sorted(k[0] for k in kk)[len(kk) // 2]; f0s = sorted(k[1] for k in kk if k[1]); mf0 = f0s[len(f0s) // 2] if f0s else 0
    for p, (d, f0) in zip(phr, kk):
        t = accent(p)
        if d - mdb >= 4 and mf0 and f0 >= 1.4 * mf0 and not any(abs(x['t'] - t) < 0.3 and '/boom-' in x['f'] for x in SFX):
            SFX[:] = [x for x in SFX if not (abs(x['t'] - t) < 0.3 and x['f'].split('/')[-1].split('-')[0] in ('hit', 'punch'))]
            sfx('boom', t - 0.02, 0.95); print(f'teriak terdeteksi (+{d - mdb:.0f} dB, nada x{f0 / mf0:.1f}): boom di {t:.2f} dtk')
# SFX KETIK ala CapCut, SELEKTIF (aturan Tio 2026-10-16: "jangan semua kata dikasih, menyesuaikan aja").
# Kata biasa TANPA bunyi. Tiap frasa paling banyak SATU bunyi, dipilih dari tekanan ucapan talent (tools/intonasi.py):
#   kalimat tanya (?)            -> "tanya" (nada naik) di kata terakhir
#   ada kata tebal/besar/kuning  -> "kretik" (keyboard mekanik) di kata gaya yang paling ditekan, kuning + "tik"
#   tanpa kata gaya              -> "key" (ketikan) hanya kalau talent jelas menekan satu kata (skor >= 1,2)
# Dilewati kalau frasa sudah punya bunyi aksen ("sfx"), dekat SFX lain (< 0,3 dtk), atau < 0,8 dtk dari ketikan sebelumnya.
# "ketik": false di clip.json = matikan.
if clip.get('ketik', True) and role('key'):
    _n.pop('key', None)
    from intonasi import tekanan
    ws = [[w for l in p['lines'] for w in l] for p in phr]
    ends = [[(w['t'], (ww[i + 1]['t'] if i + 1 < len(ww) else p['end'])) for i, w in enumerate(ww)] for p, ww in zip(phr, ws)]
    emph = tekanan(ends)
    busy = [x['t'] for x in SFX]
    last = -9.0
    for p, ww, em in zip(phr, ws, emph):
        if not ww or p.get('sfx'): continue
        if ww[-1]['w'].endswith('?'): r, i = 'tanya', len(ww) - 1
        else:
            gaya = [i for i, w in enumerate(ww) if w['st'] in ('B', 'S') or w['y']]
            if gaya: r, i = 'kretik', max(gaya, key=lambda i: em[i])
            else:
                i = max(range(len(ww)), key=lambda i: em[i]); r = 'key' if em[i] >= 1.2 else None
        if not r: continue
        t = ww[i]['t']
        if t - last < 0.8 or any(abs(t - b) < 0.3 for b in busy): continue
        e = em[i]
        if r == 'tanya': sfx('tanya', t + 0.03, 0.6)
        elif r == 'kretik':
            sfx('kretik', t - 0.01, round(min(1.0, 0.8 + 0.1 * max(0, e)), 2))
            if ww[i]['y']: sfx('tik', t, 0.6)
        else: sfx('key', t - 0.01, round(min(0.95, 0.6 + 0.2 * e), 2))
        last = t

# 3) kamera "dinamis": framing berganti per kalimat (lebar/dekat/sedang/paling dekat), frasa boleh paksa {"z": 1.0}
shots = None
if clip.get('zoom', 'dinamis') == 'dinamis':   # standar sejak 2026-10-16; "bergantian" = gaya lama 1.00/1.10
    Z = [1.0, 1.24, 1.1, 1.3]; shots = []; n = 0
    for p in phr:
        z = p.get('z')
        if shots and z is None and p['start'] - shots[-1]['t'] < 1.2: continue
        if z is None: z = Z[n % len(Z)]; n += 1
        shots.append({'t': 0 if not shots else round(p['start'] - 0.04, 3), 'z': z})
data = {'total': total, 'phrases': phr, 'cutaways': cuts, 'fx': fx, 'hook': hook, 'sfx': SFX,
        'grade': clip.get('grade', 'soft'), 'cuts': TL.get('cuts', [])}
if clip.get('look', 'premium') == 'premium': data['look'] = 'premium'   # "standar" = tanpa grain/grade sinematik
if clip.get('format') == 'lanskap': data['format'] = 'lanskap'           # 1920x1080; default potret 1080x1920
if shots: data['shots'] = shots
fp = os.path.join(ROOT, 'raw', 'face.json')
if shots and os.path.exists(fp): data['face'] = json.load(open(fp))['xy']
json.dump(data, open(os.path.join(ROOT, 'src', 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(phr)} frasa, {len(cuts)} cutaway, {len(fx)} fx, total {total:.2f} dtk')
print(f'kecocokan caption vs ucapan: {match_ratio:.0%} kata ucapan tertutup caption')
miss = [B[b] for b in range(len(B)) if not any(blk[1] <= b < blk[1] + blk[2] for blk in sm.get_matching_blocks())]
if miss: print('kata ucapan yang tidak ada di caption (cek, mungkin salah dengar ASR):', ' '.join(miss[:60]))

# 3) ikon: "simple:tiktok" (logo merek, warna asli) atau "lucide:bot" (ikon garis). Disisipkan langsung ke data.
NM = os.path.join(ROOT, 'node_modules')
_hex = None
def icon(spec):
    global _hex
    kind, name = spec.split(':', 1)
    if kind == 'simple':
        if _hex is None:
            _hex = {d['slug']: d['hex'] for d in json.load(open(os.path.join(NM, 'simple-icons', 'data', 'simple-icons.json'), encoding='utf-8'))}
        svg = open(os.path.join(NM, 'simple-icons', 'icons', f'{name}.svg'), encoding='utf-8').read()
        path = re.findall(r'<path d="([^"]+)"', svg)
        return {'kind': 'simple', 'vb': '0 0 24 24', 'paths': path, 'hex': '#' + _hex.get(name, '111111')}
    svg = open(os.path.join(NM, 'lucide-static', 'icons', f'{name}.svg'), encoding='utf-8').read()
    inner = re.sub(r'(?s)^.*?<svg[^>]*>|</svg>\s*$', '', svg).strip()
    return {'kind': 'lucide', 'vb': '0 0 24 24', 'inner': inner}
for c in data['cutaways']:
    for ic in c.get('icons', []):
        try: ic['svg'] = icon(ic['i'])
        except Exception as e: print('ikon tidak ketemu:', ic['i'], e)
json.dump(data, open(os.path.join(ROOT, 'src', 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
