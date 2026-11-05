"""Unduh model Whisper (sherpa-onnx) + VAD sekali saja ke folder models/. pip install sherpa-onnx numpy dulu."""
import os, sys, tarfile, urllib.request
from common import ROOT
M = os.path.join(ROOT, 'models'); os.makedirs(M, exist_ok=True)
BASE = 'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/'
model = sys.argv[1] if len(sys.argv) > 1 else 'turbo'
for name in [f'sherpa-onnx-whisper-{model}.tar.bz2', 'silero_vad.onnx']:
    dst = os.path.join(M, name)
    if os.path.exists(dst.replace('.tar.bz2', '')) or (name.endswith('.onnx') and os.path.exists(dst)):
        print('ada:', name); continue
    print('unduh', name); urllib.request.urlretrieve(BASE + name, dst)
    if name.endswith('.tar.bz2'):
        with tarfile.open(dst) as t: t.extractall(M)
        os.remove(dst)
print('siap')
