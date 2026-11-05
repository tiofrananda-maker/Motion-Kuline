"""Path & kunci klip bersama. Semua path relatif ke folder proyek (induk tools/)."""
import os, re, glob, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_EXT = ('.mov', '.mp4', '.m4v', '.mkv')

def clip_key(path):
    """Kunci klip = 4 digit terakhir nama file (IMG_0915.MOV -> 0915), kalau tidak ada pakai nama file."""
    stem = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r'(\d{4})$', stem)
    return m.group(1) if m else stem

def footage_files(src):
    fs = [f for f in glob.glob(os.path.join(src, '**', '*'), recursive=True) if f.lower().endswith(VIDEO_EXT)]
    return {clip_key(f): f for f in sorted(fs)}

def cfg():
    p = os.path.join(ROOT, 'edit', 'config.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}

def duration(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
