"""Cari + unduh klip B-roll stok (video pendek nyata, gaya referensi). Jalan di laptop (butuh internet).
python tools/broll.py                  -> isi semua cutaway "type": "video" / "split" di edit/clip.json yang punya "q" tapi belum punya "src"
python tools/broll.py "kata kunci"     -> cari satu, simpan ke public/broll/<kata-kunci>.mp4

Di clip.json cukup tulis kata kunci BAHASA INGGRIS:
  {"p": [3, 4], "type": "video", "q": "content creator filming with smartphone"}
Opsi per cutaway: "start" (detik mulai di klip), "rate" (kecepatan, default 0.85 = sedikit pelan), "bright" (default 0.7 = gelap sinematik).
Sumber (urut): Pexels Videos (env PEXELS_API_KEY, gratis di pexels.com/api) -> Pixabay (env PIXABAY_API_KEY) -> Mixkit -> Wikimedia Commons.
Semua bebas pakai komersial; kredit di public/broll/KREDIT.txt. Klip FOOTAGE\\<nama>\\broll\\ milik Tio selalu didahulukan.
Hasil diubah ke H.264 (sisi pendek 1080, rasio asli dipertahankan supaya bisa dipakai penuh layar maupun dua layer), maks 10 detik, tanpa suara."""
import json, os, re, subprocess, sys, urllib.parse, urllib.request
from common import ROOT
OUT = os.path.join(ROOT, 'public', 'broll'); os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (motion-podcast template)'}

def get(url, headers=None, raw=False):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=40) as r:
        b = r.read()
    return b if raw else json.loads(b.decode('utf-8'))

def pexels(q):
    key = os.environ.get('PEXELS_API_KEY')
    if not key: return []
    d = get(f'https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=10&orientation=portrait', {'Authorization': key})
    out = []
    for v in d.get('videos', []):
        fs = sorted([f for f in v['video_files'] if f.get('height') and 960 <= max(f['width'], f['height']) <= 2160], key=lambda f: -f['height'])
        if fs: out.append((fs[0]['link'], v['duration'], f"Video: {v['user']['name']} / Pexels ({v['url']})"))
    return out

def pixabay(q):
    key = os.environ.get('PIXABAY_API_KEY')
    if not key: return []
    d = get(f'https://pixabay.com/api/videos/?key={key}&q={urllib.parse.quote(q)}&per_page=10&safesearch=true')
    return [((h['videos'].get('large') or h['videos']['medium'])['url'], h['duration'], f"Video: {h['user']} / Pixabay ({h['pageURL']})")
            for h in d.get('hits', []) if (h['videos'].get('large') or h['videos'].get('medium', {})).get('url')]

def mixkit(q):
    html = get('https://mixkit.co/free-stock-video/' + urllib.parse.quote(re.sub(r'\s+', '-', q.lower().strip())) + '/', raw=True).decode('utf-8', 'ignore')
    urls = list(dict.fromkeys(re.findall(r'https://assets\.mixkit\.co/videos/\d+/\d+-(?:720|1080)\.mp4', html)))
    return [(u, 0, f'Video: Mixkit, Mixkit Stock Video Free License ({u})') for u in urls[:8]]

def wikimedia(q):
    d = get('https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=10'
            f'&gsrsearch={urllib.parse.quote(q + " filetype:video")}&prop=imageinfo&iiprop=url|extmetadata')
    out = []
    for p in (d.get('query', {}).get('pages', {}) or {}).values():
        ii = (p.get('imageinfo') or [{}])[0]; m = ii.get('extmetadata', {})
        art = re.sub('<[^>]+>', '', m.get('Artist', {}).get('value', '?'))
        out.append((ii.get('url'), 0, f"{p.get('title')} oleh {art}, {m.get('LicenseShortName', {}).get('value', '')} ({ii.get('descriptionurl')})"))
    return out

def find(q):
    for src in (pexels, pixabay, mixkit, wikimedia):
        try:
            res = [r for r in src(q) if r[0]]
        except Exception as e:
            print(f'  {src.__name__} gagal: {e}'); continue
        for url, dur, credit in res[:3]:
            try:
                b = get(url, raw=True)
                if len(b) > 200_000: return b, credit
            except Exception as e:
                print(f'  unduh gagal {url}: {e}')
    return None, None

def save(q, b, credit):
    slug = re.sub(r'[^a-z0-9]+', '-', q.lower()).strip('-')[:40]
    tmp = os.path.join(OUT, slug + '.src'); open(tmp, 'wb').write(b)
    dst = os.path.join(OUT, slug + '.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-t', '10', '-an', '-vf',
                    "scale='if(gt(iw,ih),-2,1080)':'if(gt(iw,ih),1080,-2)',fps=30,format=yuv420p",
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', dst], check=True)
    os.remove(tmp)
    with open(os.path.join(OUT, 'KREDIT.txt'), 'a', encoding='utf-8') as f: f.write(f'{slug}.mp4: {credit}\n')
    return 'broll/' + slug + '.mp4'

if len(sys.argv) > 1:
    q = ' '.join(sys.argv[1:]); b, cr = find(q)
    print(save(q, b, cr) if b else 'TIDAK KETEMU: ' + q); sys.exit()
cp = os.path.join(ROOT, 'edit', 'clip.json'); clip = json.load(open(cp, encoding='utf-8'))
n = 0
for c in clip.get('cutaways', []):
    if c.get('type') not in ('video', 'split') or not c.get('q') or (c.get('src') and os.path.exists(os.path.join(ROOT, 'public', c['src']))): continue
    b, cr = find(c['q'])
    if b: c['src'] = save(c['q'], b, cr); n += 1; print('OK', c['q'], '->', c['src'])
    else: print('TIDAK KETEMU', c['q'], '-> ganti kata kunci atau jadikan kartu teks')
json.dump(clip, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(n, 'klip diunduh. LIHAT tiap klip (cocok dengan omongan? tidak ada logo/watermark/teks?) sebelum render.')
