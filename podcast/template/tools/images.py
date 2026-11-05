"""Cari + unduh gambar cutaway otomatis (supaya video tidak full muka talent). Jalan di laptop (butuh internet).
python tools/images.py                 -> isi semua cutaway di edit/clip.json yang punya "q" tapi belum punya "img"
python tools/images.py "kata kunci"    -> cari satu, simpan ke public/img/<kata-kunci>.jpg, cetak path-nya

Di clip.json cukup tulis kata kunci BAHASA INGGRIS (hasil stok lebih banyak):
  {"p": [3, 4], "type": "image", "q": "content creator filming phone"}
  {"p": 6, "type": "card", "bg": "red", "q": "indonesian street food"}
  {"p": 9, "type": "person", "name": "Angela Duckworth", "q": "Angela Duckworth"}   (orang terkenal -> Wikimedia)
Sumber (urut): Pexels (kalau ada env PEXELS_API_KEY, gratis di pexels.com/api) -> Openverse -> Wikimedia Commons.
Semua sumber berlisensi bebas pakai; kredit dicatat di public/img/KREDIT.txt.
Gambar dari folder FOOTAGE\\<nama>\\gambar\\ selalu didahulukan: salin ke public/img lalu tulis "img": "img/<file>"."""
import json, os, re, sys, urllib.parse, urllib.request
from common import ROOT
IMG = os.path.join(ROOT, 'public', 'img'); os.makedirs(IMG, exist_ok=True)
UA = {'User-Agent': 'motion-podcast/1.0 (template edit video; kontak: pemilik laptop)'}
MINW = 700

def get(url, headers=None, raw=False):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=25) as r:
        b = r.read()
    return b if raw else json.loads(b.decode('utf-8'))

def pexels(q, portrait):
    key = os.environ.get('PEXELS_API_KEY')
    if not key: return []
    o = '&orientation=portrait' if portrait else ''
    d = get(f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=10{o}', {'Authorization': key})
    return [(p['src']['large2x'], p['width'], p['height'], f"Foto: {p['photographer']} / Pexels ({p['url']})") for p in d.get('photos', [])]

def openverse(q, portrait):
    a = '&aspect_ratio=tall' if portrait else ''
    d = get(f'https://api.openverse.org/v1/images/?q={urllib.parse.quote(q)}&license_type=commercial&page_size=12&mature=false{a}')
    return [(r['url'], r.get('width') or 0, r.get('height') or 0,
             f"{r.get('title') or 'gambar'} oleh {r.get('creator') or '?'}, lisensi {r.get('license', '').upper()} {r.get('license_version') or ''} ({r.get('foreign_landing_url')})")
            for r in d.get('results', [])]

def wikimedia(q, portrait):
    d = get('https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=12'
            f'&gsrsearch={urllib.parse.quote(q + " filetype:bitmap")}&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1400')
    out = []
    for p in (d.get('query', {}).get('pages', {}) or {}).values():
        ii = (p.get('imageinfo') or [{}])[0]
        meta = ii.get('extmetadata', {})
        art = re.sub('<[^>]+>', '', meta.get('Artist', {}).get('value', '?'))
        out.append((ii.get('thumburl') or ii.get('url'), ii.get('width', 0), ii.get('height', 0),
                    f"{p.get('title')} oleh {art}, {meta.get('LicenseShortName', {}).get('value', '')} ({ii.get('descriptionurl')})"))
    return out

def find(q, portrait=True, person=False):
    order = [wikimedia, pexels, openverse] if person else [pexels, openverse, wikimedia]
    for src in order:
        try:
            res = [r for r in src(q, portrait) if r[0] and r[1] >= MINW]
        except Exception as e:
            print(f'  {src.__name__} gagal: {e}'); continue
        if portrait:  # utamakan potret, lalu yang paling besar
            res.sort(key=lambda r: (-(r[2] >= r[1]), -r[1]))
        for url, w, h, credit in res[:4]:
            try:
                b = get(url, raw=True)
                if len(b) > 20000: return b, credit
            except Exception as e:
                print(f'  unduh gagal {url}: {e}')
    return None, None

def save(q, b, credit):
    name = re.sub(r'[^a-z0-9]+', '-', q.lower()).strip('-')[:40] + '.jpg'
    open(os.path.join(IMG, name), 'wb').write(b)
    with open(os.path.join(IMG, 'KREDIT.txt'), 'a', encoding='utf-8') as f: f.write(f'{name}: {credit}\n')
    return 'img/' + name

if len(sys.argv) > 1:
    q = ' '.join(sys.argv[1:]); b, cr = find(q)
    print(save(q, b, cr) if b else 'TIDAK KETEMU: ' + q)
    sys.exit()
cp = os.path.join(ROOT, 'edit', 'clip.json'); clip = json.load(open(cp, encoding='utf-8'))
n = 0
for c in clip.get('cutaways', []):
    if not c.get('q') or (c.get('img') and os.path.exists(os.path.join(ROOT, 'public', c['img']))): continue
    b, cr = find(c['q'], portrait=c['type'] in ('image', 'person'), person=c['type'] == 'person')
    if b:
        c['img'] = save(c['q'], b, cr); n += 1; print('OK', c['q'], '->', c['img'])
    else:
        print('TIDAK KETEMU', c['q'], '-> ganti jadi kartu teks/ikon/angka')
json.dump(clip, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(n, 'gambar diunduh. Cek tiap gambar (cocok dengan omongan? tidak ada watermark/teks aneh?) sebelum render.')
