"""Transkrip + waktu per kata: python tools/words.py <file_atau_folder_footage> [turbo|small]
Teks dari Whisper, waktu tiap kata dari Dolphin CTC (forced alignment).
Hasil: raw/words.json  {kunci: {file, dur, segs:[{s,e,t,words:[[kata,mulai,selesai],...]}]}}
Catatan: teks Whisper BELUM tentu persis ucapan talent (mis. 'gue' padahal 'gw', 'enggak' padahal 'nggak').
Claude wajib mendengar ulang lewat tools/check.py dan membetulkan kata di edit/captions.json."""
import sys, os, json, subprocess
import numpy as np, sherpa_onnx
from common import ROOT, footage_files, clip_key
from align import Aligner
src = sys.argv[1]; model = sys.argv[2] if len(sys.argv) > 2 else 'turbo'
M = os.path.join(ROOT, 'models'); d = os.path.join(M, f'sherpa-onnx-whisper-{model}')
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{d}/{model}-encoder.int8.onnx', decoder=f'{d}/{model}-decoder.int8.onnx',
    tokens=f'{d}/{model}-tokens.txt', language='id', task='transcribe', num_threads=4)
al = Aligner(os.path.join(M, 'sherpa-onnx-dolphin-small-ctc-multi-lang-int8-2025-04-02'))
cfg = sherpa_onnx.VadModelConfig(); cfg.silero_vad.model = os.path.join(M, 'silero_vad.onnx')
cfg.silero_vad.min_silence_duration = 0.3; cfg.silero_vad.min_speech_duration = 0.25; cfg.silero_vad.threshold = 0.5
cfg.silero_vad.max_speech_duration = 20; cfg.sample_rate = 16000
os.makedirs(os.path.join(ROOT, 'raw'), exist_ok=True)
outp = os.path.join(ROOT, 'raw', 'words.json')
out = json.load(open(outp, encoding='utf-8')) if os.path.exists(outp) else {}
files = {clip_key(src): src} if os.path.isfile(src) else footage_files(src)
PAD = 0.15
def dec(samples):
    st = rec.create_stream(); st.accept_waveform(16000, samples); rec.decode_stream(st); return st.result.text.strip()
for k, f in files.items():
    if k in out: continue
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=7200); w = cfg.silero_vad.window_size; segs = []
    for i in range(0, len(x), w): vad.accept_waveform(x[i:i + w])
    vad.flush()
    spans = []
    while not vad.empty():
        s = vad.front; spans.append((s.start / 16000, s.start / 16000 + len(s.samples) / 16000)); vad.pop()
    # potong span panjang (>12 dtk, mis. ada musik di belakang) di titik paling sepi tiap 6-12 dtk
    fr = x[:len(x) // 320 * 320].reshape(-1, 320); rms = np.sqrt((fr ** 2).mean(1)) + 1e-9
    pieces = []
    for a, b in spans:
        first = True
        while b - a > 12:
            i0, i1 = int((a + 6) * 50), int((a + 12) * 50)
            cut = (i0 + int(np.argmin(rms[i0:i1]))) / 50
            pieces.append((a, cut, first, False)); a = cut; first = False
        pieces.append((a, b, first, True))
    for a, b, pa, pb in pieces:
        a0 = max(0.0, a - (PAD if pa else 0)); b0 = min(len(x) / 16000, b + (PAD if pb else 0))
        sub = x[int(a0 * 16000):int(b0 * 16000)]
        if len(sub) < 16000 * 0.3: continue
        text = dec(sub)
        ws = text.split()
        words = [[wd, round(a0 + s1, 2), round(a0 + e1, 2)] for wd, s1, e1 in al.align(sub, ws)] if ws else []
        # selesai kata = awal kata berikutnya (maks +0.6 dtk), lebih natural untuk caption
        for i in range(len(words)):
            nxt = words[i + 1][1] if i + 1 < len(words) else b0
            words[i][2] = round(min(max(words[i][2], nxt), words[i][1] + 0.6), 2)
        segs.append({'s': round(a0, 2), 'e': round(b0, 2), 't': text, 'words': words})
    out[k] = {'file': os.path.basename(f), 'dur': round(len(x) / 16000, 2), 'segs': segs}
    print(k, len(segs), 'segmen,', sum(len(s['words']) for s in segs), 'kata', flush=True)
    json.dump(out, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('SELESAI', outp)
