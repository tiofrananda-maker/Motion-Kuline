"""Transkrip semua klip: python tools/transcribe.py <folder_footage> [turbo|small]
Hasil: raw/transcript.json  {kunci: {dur, rms, segs:[{s,e,t}]}}
Catatan: Whisper suka berhalusinasi 'terima kasih / selamat menikmati' di klip tanpa omongan (cuma desis)."""
import sys, os, json, subprocess
import numpy as np, sherpa_onnx
from common import ROOT, footage_files
src = sys.argv[1]; model = sys.argv[2] if len(sys.argv) > 2 else 'turbo'
M = os.path.join(ROOT, 'models'); d = os.path.join(M, f'sherpa-onnx-whisper-{model}')
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{d}/{model}-encoder.int8.onnx', decoder=f'{d}/{model}-decoder.int8.onnx',
    tokens=f'{d}/{model}-tokens.txt', language='id', task='transcribe', num_threads=4)
cfg = sherpa_onnx.VadModelConfig(); cfg.silero_vad.model = os.path.join(M, 'silero_vad.onnx')
cfg.silero_vad.min_silence_duration = 0.25; cfg.silero_vad.min_speech_duration = 0.25; cfg.silero_vad.threshold = 0.5; cfg.sample_rate = 16000
os.makedirs(os.path.join(ROOT, 'raw'), exist_ok=True)
outp = os.path.join(ROOT, 'raw', 'transcript.json')
out = json.load(open(outp, encoding='utf-8')) if os.path.exists(outp) else {}
def dec(samples):
    st = rec.create_stream(); st.accept_waveform(16000, samples); rec.decode_stream(st); return st.result.text.strip()
for k, f in footage_files(src).items():
    if k in out: continue
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=180); w = cfg.silero_vad.window_size; segs = []
    for i in range(0, len(x), w): vad.accept_waveform(x[i:i + w])
    vad.flush()
    while not vad.empty():
        s = vad.front; st = s.start / 16000; smp = np.array(s.samples, dtype=np.float32)
        for j in range(0, len(smp), 16000 * 25):
            sub = smp[j:j + 16000 * 25]
            if len(sub) >= 16000 * 0.3:
                segs.append({'s': round(st + j / 16000, 2), 'e': round(st + (j + len(sub)) / 16000, 2), 't': dec(sub)})
        vad.pop()
    out[k] = {'file': os.path.basename(f), 'dur': round(len(x) / 16000, 2), 'rms': round(float(np.sqrt(np.mean(x ** 2))) if len(x) else 0, 4), 'segs': segs}
    print(k, ' | '.join(s['t'] for s in segs)[:160], flush=True)
    json.dump(out, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('SELESAI', outp)
