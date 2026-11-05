"""Forced alignment: Whisper text -> word timestamps using the Dolphin CTC model.

align(audio_f32_16k, text) -> [(word, start_s, end_s), ...]
"""
import re
import numpy as np
import onnxruntime as ort
import kaldi_native_fbank as knf


SATU = ['', 'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan', 'sepuluh', 'sebelas']
def terbilang(n):
    """Angka -> kata Indonesia (untuk alignment saja; caption tetap tampil angka)."""
    n = int(n)
    if n < 12: return SATU[n] or 'nol'
    if n < 20: return SATU[n - 10] + ' belas'
    if n < 100: return (SATU[n // 10] + ' puluh ' + SATU[n % 10]).strip()
    if n < 200: return ('seratus ' + (terbilang(n - 100) if n > 100 else '')).strip()
    if n < 1000: return (SATU[n // 100] + ' ratus ' + (terbilang(n % 100) if n % 100 else '')).strip()
    if n < 2000: return ('seribu ' + (terbilang(n - 1000) if n > 1000 else '')).strip()
    for v, nm in ((10**12, 'triliun'), (10**9, 'miliar'), (10**6, 'juta'), (1000, 'ribu')):
        if n >= v: return (terbilang(n // v) + ' ' + nm + ' ' + (terbilang(n % v) if n % v else '')).strip()

def spoken(w):
    """Bentuk ucapan dari kata tampil: '10.000' -> 'sepuluh ribu', 'ke-11' -> 'ke sebelas', '50%' -> 'lima puluh persen'."""
    w = w.lower().replace('%', ' persen').replace('-', ' ').replace('rp', ' ')
    out = []
    for p in w.split():
        m = re.fullmatch(r"[^\w]*(\d[\d.]*)(?:,(\d+))?([^\w]*)(\w*)", p)
        if m and m.group(1).replace('.', '').isdigit():
            out.append(terbilang(m.group(1).replace('.', '')))
            if m.group(2): out.append('koma ' + ' '.join(SATU[int(c)] or 'nol' for c in m.group(2)))
            if m.group(4): out.append(m.group(4))
        else:
            out.append(re.sub(r"[^\w']", '', p, flags=re.UNICODE))
    return [x for x in ' '.join(out).split() if x]


class Aligner:
    def __init__(self, model_dir):
        self.sess = ort.InferenceSession(f'{model_dir}/model.int8.onnx', providers=['CPUExecutionProvider'])
        meta = self.sess.get_modelmeta().custom_metadata_map
        self.mean = np.array([float(x) for x in meta['mean'].split(',')], np.float32)
        self.invstd = np.array([float(x) for x in meta['invstd'].split(',')], np.float32)
        self.vocab = {}
        self.id2tok = {}
        for line in open(f'{model_dir}/tokens.txt', encoding='utf-8'):
            p = line.rstrip('\n').rsplit(' ', 1)
            if len(p) == 2:
                self.vocab[p[0]] = int(p[1])
                self.id2tok[int(p[1])] = p[0]
        self.maxlen = max(len(t) for t in self.vocab)

    def feats(self, audio):
        o = knf.FbankOptions()
        o.frame_opts.dither = 0
        o.frame_opts.samp_freq = 16000
        o.mel_opts.num_bins = 80
        o.frame_opts.snip_edges = False
        fb = knf.OnlineFbank(o)
        fb.accept_waveform(16000, audio.tolist())
        fb.input_finished()
        x = np.stack([fb.get_frame(i) for i in range(fb.num_frames_ready)]).astype(np.float32)
        # per-utterance CMVN (matches the model's training-time normalisation well)
        return (x - x.mean(0)) / (x.std(0) + 1e-5)

    def logprobs(self, audio):
        x = self.feats(audio)[None]
        lp, n = self.sess.run(None, {'x': x, 'x_len': np.array([x.shape[1]], np.int64)})
        return lp[0][: int(n[0])]

    def greedy(self, lp):
        ids = lp.argmax(1)
        out, prev = [], -1
        for i in ids:
            if i != prev and i != 0:
                out.append(self.id2tok.get(int(i), ''))
            prev = i
        return ''.join(out).replace('▁', ' ').strip()

    def tokenize_word(self, w):
        """Greedy longest-match into model tokens, first piece prefixed with ▁."""
        s, out, first = w.lower(), [], True
        while s:
            for L in range(min(len(s), self.maxlen), 0, -1):
                piece = ('▁' if first else '') + s[:L]
                if piece in self.vocab:
                    out.append(self.vocab[piece]); s = s[L:]; first = False
                    break
            else:
                if first and '▁' in self.vocab:
                    out.append(self.vocab['▁']); first = False
                else:
                    s = s[1:]  # character not in vocab: skip
        return out

    def align(self, audio, words, frame_s=0.04):
        """words: list of display words. Returns list of (word, start, end)."""
        lp = self.logprobs(audio)
        T = lp.shape[0]
        toks, owner = [], []
        for wi, w in enumerate(words):
            for part in spoken(w) or [w]:
                for t in self.tokenize_word(part):
                    toks.append(t); owner.append(wi)
        if not toks or T < 2:
            return self._spread(words, 0, len(audio) / 16000)
        # CTC Viterbi over extended sequence (blank between tokens)
        S = 2 * len(toks) + 1
        ext = np.zeros(S, np.int64); ext[1::2] = toks
        NEG = -1e9
        dp = np.full((T, S), NEG, np.float32); bp = np.zeros((T, S), np.int8)
        dp[0, 0] = lp[0, 0]; dp[0, 1] = lp[0, ext[1]]
        skip_ok = np.zeros(S, bool)
        skip_ok[3::2] = ext[3::2] != ext[1:-2:2]
        for t in range(1, T):
            a = dp[t - 1]
            b = np.concatenate([[NEG], a[:-1]])
            c = np.concatenate([[NEG, NEG], a[:-2]])
            c = np.where(skip_ok, c, NEG)
            stack = np.stack([a, b, c])
            k = stack.argmax(0)
            dp[t] = stack[k, np.arange(S)] + lp[t, ext]
            bp[t] = k
        s = S - 1 if dp[-1, S - 1] >= dp[-1, S - 2] else S - 2
        path = []
        for t in range(T - 1, -1, -1):
            path.append(s); s -= int(bp[t, s])
        path.reverse()
        first = {}; last = {}
        for t, st in enumerate(path):
            if st % 2 == 1:
                wi = owner[st // 2]
                first.setdefault(wi, t); last[wi] = t
        out = []
        for wi, w in enumerate(words):
            if wi in first:
                out.append([w, first[wi] * frame_s, (last[wi] + 1) * frame_s])
            else:
                out.append([w, None, None])
        # fill missing by neighbours
        for i, o in enumerate(out):
            if o[1] is None:
                prev = next((out[j][2] for j in range(i - 1, -1, -1) if out[j][2] is not None), 0.0)
                o[1] = o[2] = prev
        return [tuple(o) for o in out]

    @staticmethod
    def _spread(words, s, e):
        n = max(len(words), 1); d = (e - s) / n
        return [(w, s + i * d, s + (i + 1) * d) for i, w in enumerate(words)]
