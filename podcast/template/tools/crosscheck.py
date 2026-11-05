"""ATURAN KERAS caption = persis ucapan. Bandingkan 3 pendengar per segmen supaya kata yang meragukan ketahuan:
python tools/crosscheck.py <file_atau_folder_footage> [kunci]
Cetak per segmen: T = Whisper turbo (dari words.json), S = Whisper small, D = Dolphin (CTC, cenderung fonetis).
Kata yang beda antar versi = WAJIB dicek (dengar ulang potongan itu, pilih yang paling cocok dengan bunyi).
Hasil juga ditulis ke raw/crosscheck.txt."""
import sys, os, json, subprocess
import numpy as np, sherpa_onnx
from common import ROOT, footage_files, clip_key
from align import Aligner
src = sys.argv[1]; only = sys.argv[2] if len(sys.argv) > 2 else None
M = os.path.join(ROOT, 'models'); d = os.path.join(M, 'sherpa-onnx-whisper-small')
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{d}/small-encoder.int8.onnx', decoder=f'{d}/small-decoder.int8.onnx',
    tokens=f'{d}/small-tokens.txt', language='id', task='transcribe', num_threads=4)
al = Aligner(os.path.join(M, 'sherpa-onnx-dolphin-small-ctc-multi-lang-int8-2025-04-02'))
W = json.load(open(os.path.join(ROOT, 'raw', 'words.json'), encoding='utf-8'))
files = {clip_key(src): src} if os.path.isfile(src) else footage_files(src)
out = []
for k, f in files.items():
    if only and k != only or k not in W: continue
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    for s in W[k]['segs']:
        sub = x[int(s['s'] * 16000):int(s['e'] * 16000)]
        st = rec.create_stream(); st.accept_waveform(16000, sub); rec.decode_stream(st)
        blk = f"[{k} {s['s']:.2f}-{s['e']:.2f}]\n T: {s['t']}\n S: {st.result.text.strip()}\n D: {al.greedy(al.logprobs(sub))}\n"
        print(blk, flush=True); out.append(blk)
open(os.path.join(ROOT, 'raw', 'crosscheck.txt'), 'w', encoding='utf-8').write('\n'.join(out))
