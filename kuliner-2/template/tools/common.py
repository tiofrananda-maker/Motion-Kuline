"""Path & kunci klip bersama. Semua path relatif ke folder proyek (induk tools/)."""
import os, re, glob, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_EXT = ('.mov', '.mp4', '.m4v', '.mkv')
AUDIO_EXT = ('.m4a', '.mp3', '.wav', '.aac', '.ogg', '.opus')   # rekaman VO terpisah (mis. vo.m4a -> kunci "vo")

def clip_key(path):
    """Kunci klip = 4 digit terakhir nama file (IMG_0915.MOV -> 0915), kalau tidak ada pakai nama file."""
    stem = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r'(\d{4})$', stem)
    return m.group(1) if m else stem

def footage_files(src):
    """Semua video + audio (VO terpisah) di folder footage: kunci -> path."""
    if os.path.isfile(src): return {clip_key(src): src}
    fs = [f for f in glob.glob(os.path.join(src, '**', '*'), recursive=True) if f.lower().endswith(VIDEO_EXT + AUDIO_EXT)]
    return {clip_key(f): f for f in sorted(fs)}

def video_files(src):
    return {k: f for k, f in footage_files(src).items() if f.lower().endswith(VIDEO_EXT)}

def load(path, default=None):
    p = os.path.join(ROOT, path)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default

def duration(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
