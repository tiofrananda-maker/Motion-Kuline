"""Cek isi potongan audio sebelum dipakai: python tools/check.py <folder_footage> 0919:10.35:12.25 0921:1.15:7.65 ..."""
import sys, os, subprocess
import numpy as np, sherpa_onnx
from common import ROOT, footage_files
files = footage_files(sys.argv[1]); d = os.path.join(ROOT, 'models', 'sherpa-onnx-whisper-turbo')
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{d}/turbo-encoder.int8.onnx', decoder=f'{d}/turbo-decoder.int8.onnx', tokens=f'{d}/turbo-tokens.txt', language='id', task='transcribe', num_threads=4)
for spec in sys.argv[2:]:
    k, s, e = spec.split(':')
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-ss', s, '-to', e, '-i', files[k], '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    st = rec.create_stream(); st.accept_waveform(16000, x); rec.decode_stream(st)
    print(spec, '=>', st.result.text.strip(), flush=True)
