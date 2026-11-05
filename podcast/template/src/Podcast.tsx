import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import raw from './data.json';
import './fonts';
import {C, SANS, SERIF, SHADOW, UI} from './theme';

// ---------- tipe data (dibuat tools/compile.py) ----------
type W = {w: string; st: 's' | 'B' | 'S' | 'si' | 'i'; y: boolean; t: number};
type Phrase = {lines: W[][]; start: number; end: number; pos?: 'top' | 'mid' | 'low' | 'bottom'; mode?: 'box'};
type Svg = {kind: 'simple' | 'lucide'; vb: string; paths?: string[]; hex?: string; inner?: string};
type Ic = {i: string; x: number; y: number; s?: number; svg?: Svg; color?: string};
type Cut = {
  type: 'card' | 'image' | 'video' | 'split' | 'person' | 'icons' | 'stat' | 'news' | 'logos';
  src?: string; start?: number; rate?: number; bright?: number; x?: number; y?: number; talent?: 'atas' | 'bawah' | 'kiri' | 'kanan';
  from: number; to: number;
  bg?: 'red' | 'gray' | 'split' | 'dark' | 'white'; img?: string; dim?: number; name?: string;
  icons?: Ic[]; value?: string; label?: string; color?: 'yellow' | 'white' | 'red';
  source?: string; title?: string; sub?: string;
};
type Fx = {type: 'flash' | 'blur' | 'punch' | 'wipe' | 'defocus'; at: number; to?: number};
type Data = {
  total: number; phrases: Phrase[]; cutaways: Cut[]; fx: Fx[];
  hook: {text: string; until: number} | null; sfx: {f: string; t: number; v: number}[]; cuts: number[];
  look?: 'premium'; shots?: {t: number; z: number}[]; face?: number[][]; format?: 'lanskap';
};
const data = raw as unknown as Data;
const PREMIUM = data.look === 'premium';
// format: potret 1080x1920 (standar) atau lanskap 1920x1080 ("format": "lanskap" di clip.json)
const LAND = data.format === 'lanskap';
const VW = LAND ? 1920 : 1080;
const VH = LAND ? 1080 : 1920;
const FPS = 30;
const ease = Easing.bezier(0.22, 1, 0.36, 1);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// ---------- gaya kata (acuan referensi) ----------
const STYLE: Record<W['st'], React.CSSProperties & {k: number}> = {
  s: {fontFamily: SANS, fontWeight: 700, fontSize: 60, letterSpacing: '-0.02em', k: 0.56},
  B: {fontFamily: SANS, fontWeight: 800, fontSize: 150, letterSpacing: '-0.045em', lineHeight: 0.95, k: 0.55},
  // *kata* = penekanan besar font Apple ringan (Tio 2026-10-16: tidak ada serif besar untuk poin penting)
  S: {fontFamily: SANS, fontWeight: 300, fontSize: 150, letterSpacing: '-0.04em', lineHeight: 0.95, k: 0.52},
  si: {fontFamily: SERIF, fontStyle: 'italic', fontWeight: 400, fontSize: 68, k: 0.4},
  i: {fontFamily: SANS, fontStyle: 'italic', fontWeight: 700, fontSize: 60, letterSpacing: '-0.02em', k: 0.55},
};
const MAXW = LAND ? 1500 : 940;
const lineWidth = (l: W[], scale = 1) =>
  l.reduce((a, w) => a + w.w.length * (STYLE[w.st].fontSize as number) * STYLE[w.st].k * scale + 14, 0);

// cutaway yang aktif di waktu t
const cutAt = (t: number) => data.cutaways.find((c) => t >= c.from && t < c.to);

// ---------- dua layer (split): talent di satu separuh layar, B-roll nyata di separuh lain ----------
// Potret: atas/bawah. Lanskap: kiri/kanan ("atas" dibaca "kiri", "bawah" dibaca "kanan").
// Split berurutan dengan posisi talent yang sama menyambung (talent diam, hanya klip B-roll yang berganti).
const SPLITS = data.cutaways.filter((c) => c.type === 'split');
const talentTop = (c: Cut) => ['atas', 'kiri'].includes(c.talent ?? 'atas');
const joined = (c: Cut, side: 'in' | 'out') =>
  SPLITS.some((o) => o !== c && talentTop(o) === talentTop(c) && Math.abs(side === 'in' ? o.to - c.from : o.from - c.to) < 0.05);
const splitK = (c: Cut, frame: number) => {
  const a = c.from * FPS;
  const b = c.to * FPS;
  const kin = joined(c, 'in') ? (frame >= a ? 1 : 0) : interpolate(frame, [a, a + 9], [0, 1], {...clamp, easing: ease});
  const kout = joined(c, 'out') ? (frame < b ? 1 : 0) : interpolate(frame, [b - 8, b], [1, 0], {...clamp, easing: Easing.inOut(Easing.cubic)});
  return Math.min(kin, kout);
};
const splitAt = (frame: number) => {
  let best = {k: 0, top: true};
  for (const c of SPLITS) {
    const k = splitK(c, frame);
    if (k > best.k) best = {k, top: talentTop(c)};
  }
  return best;
};

// ---------- kamera ----------
// Tanpa data.shots: zoom bergantian 1.00/1.10 tiap jump cut.
// Dengan data.shots (zoom "dinamis"): tiap shot punya framing sendiri (lebar/sedang/dekat), dorong pelan,
// dan wajah (data.face, hasil tools/face.py) digeser ke sepertiga atas saat zoom dekat.
const zoomGroups = (() => {
  const g: number[] = [0];
  for (const c of data.cuts) if (c - g[g.length - 1] >= 1.6) g.push(c);
  return g;
})();
const faceAt = (frame: number): [number, number] => {
  const f = data.face;
  if (!f || !f.length) return [0.5, 0.4];
  const i = Math.max(0, Math.min(f.length - 1, frame));
  return [f[i][0], f[i][1]];
};
const Camera: React.FC<{children: React.ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  let s: number;
  if (data.shots && data.shots.length) {
    let k = 0;
    for (let i = 0; i < data.shots.length; i++) if (t >= data.shots[i].t) k = i;
    const sh = data.shots[k];
    const t1 = data.shots[k + 1]?.t ?? data.total;
    s = sh.z + interpolate(t, [sh.t, t1], [0, 0.045], {...clamp, easing: Easing.inOut(Easing.sin)});
  } else {
    let gi = 0;
    for (let i = 0; i < zoomGroups.length; i++) if (t >= zoomGroups[i]) gi = i;
    const g0 = zoomGroups[gi];
    const g1 = zoomGroups[gi + 1] ?? data.total;
    s = (gi % 2 === 0 ? 1.0 : 1.1) + interpolate(t, [g0, g1], [0, 0.03], clamp);
  }
  const sp = splitAt(frame);
  s += sp.k * (1.06 - s); // saat dua layer: framing tetap sedang, wajah di tengah separuh layarnya
  let blur = 0;
  let bright = 1;
  for (const f of data.fx) {
    const d = frame - Math.round(f.at * FPS);
    if (f.type === 'punch' && d >= 0 && d < 40) {
      const sp = spring({frame: d, fps: FPS, config: {damping: 16, stiffness: 200, mass: 0.5}});
      s += (PREMIUM ? 0.12 : 0.09) * sp * interpolate(d, [30, 40], [1, 0], clamp);
      if (PREMIUM) blur = Math.max(blur, interpolate(d, [0, 2, 6], [0, 3, 0], clamp));
    }
    if (f.type === 'blur') blur = Math.max(blur, interpolate(d, [-6, 0, 8], [0, 18, 0], clamp));
    if (f.type === 'flash') bright = Math.max(bright, interpolate(d, [-4, 0, 9], [1, PREMIUM ? 1.7 : 2.4, 1], clamp));
    if (f.type === 'defocus' && f.to !== undefined) {
      // pembuka: talent kabur + gelap, lalu fokus tajam di akhir frasa (rack focus)
      const e = Math.round(f.to * FPS);
      if (frame <= e + 6) {
        const q = interpolate(frame, [e - 3, e + 5], [1, 0], {...clamp, easing: Easing.out(Easing.cubic)});
        blur = Math.max(blur, 26 * q);
        bright = Math.min(bright, 1 - 0.45 * q);
        s += 0.08 * q;
      }
    }
  }
  const [fx0, fy0] = faceAt(frame);
  const k = Math.max(0, Math.min(1, (s - 1) / 0.25));
  const dx = fx0 + (0.5 - fx0) * k;
  const dy = fy0 + (0.4 - fy0) * k;
  const lim = (s - 1) / 2;
  let tx = Math.max(-lim, Math.min(lim, dx - 0.5 - (fx0 - 0.5) * s));
  let ty = Math.max(-lim, Math.min(lim, dy - 0.5 - (fy0 - 0.5) * s));
  if (sp.k > 0 && LAND) tx += sp.k * ((sp.top ? 0.25 : 0.75) - (0.5 + tx + (fx0 - 0.5) * s));
  else if (sp.k > 0) ty += sp.k * ((sp.top ? 0.25 : 0.74) - (0.5 + ty + (fy0 - 0.5) * s));
  return (
    <AbsoluteFill style={{transform: `translate(${tx * VW}px, ${ty * VH}px) scale(${s})`, filter: `blur(${blur}px) brightness(${bright})`}}>{children}</AbsoluteFill>
  );
};

// ---------- tampilan premium: grain film halus ----------
const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{opacity: 0.09, mixBlendMode: 'overlay', pointerEvents: 'none'}}>
      <svg width={VW} height={VH}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={2} seed={frame % 10} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};

// ---------- caption kinetik kata per kata ----------
const Word: React.FC<{w: W; scale: number; color: string; shadow: boolean}> = ({w, scale, color, shadow}) => {
  const frame = useCurrentFrame();
  const d = frame - w.t * FPS;
  const p = interpolate(d, [0, 7], [0, 1], {...clamp, easing: ease});
  const {k: _k, ...st} = STYLE[w.st];
  return (
    <span
      style={{
        ...st,
        fontSize: (st.fontSize as number) * scale,
        color: w.y ? (color === C.merah ? C.hitam : C.kuning) : color,
        opacity: p,
        filter: `blur(${(1 - p) * 14}px)`,
        transform: `translateY(${(1 - p) * 14}px)`,
        display: 'inline-block',
        whiteSpace: 'pre',
        textShadow: shadow ? SHADOW : 'none',
      }}
    >
      {w.w}
    </span>
  );
};

const Caption: React.FC<{p: Phrase}> = ({p}) => {
  const frame = useCurrentFrame();
  const mid = (p.start + p.end) / 2;
  const cut = cutAt(mid);
  const onCard = cut && (cut.type === 'card' || cut.type === 'person');
  const box = p.mode === 'box' || (cut && (cut.type === 'icons' || cut.type === 'news'));
  const out = interpolate(frame, [p.end * FPS - 5, p.end * FPS], [1, 0], clamp);
  const outBlur = (1 - out) * 10;

  if (box) {
    // gaya subtitle kotak hitam (adegan ikon / berita)
    return (
      <AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', top: LAND ? 880 : 1340, opacity: out}}>
        {p.lines.filter((l) => frame >= l[0].t * FPS - 1).map((l, i) => (
          <div key={i} style={{background: 'rgba(12,12,12,.86)', padding: '6px 16px', marginTop: i ? 6 : 0, borderRadius: 4}}>
            {l.filter((w) => frame >= w.t * FPS - 1).map((w, j) => {
              const pp = interpolate(frame - w.t * FPS, [0, 3], [0.4, 1], clamp);
              return (
                <span key={j} style={{fontFamily: UI, fontWeight: 500, fontSize: 46, color: w.y ? C.kuning : C.putih, opacity: pp, whiteSpace: 'pre'}}>
                  {(j ? ' ' : '') + w.w}
                </span>
              );
            })}
          </div>
        ))}
      </AbsoluteFill>
    );
  }

  const base = LAND ? 0.8 : 1;
  const widest = Math.max(...p.lines.map((l) => lineWidth(l, base)));
  const scale = base * Math.min(1, MAXW / widest);
  const color = onCard ? (cut!.bg === 'gray' || cut!.type === 'person' ? C.merah : C.abu) : C.putih;
  const hasImg = onCard && !!cut!.img && cut!.type === 'card';
  const y = LAND
    ? hasImg ? 900 : cut?.type === 'split' && !p.pos ? 860 : onCard || (cut?.type === 'video' && !p.pos) ? 540 : p.pos === 'top' ? 300 : p.pos === 'mid' ? 540 : p.pos === 'bottom' ? 960 : 830
    : hasImg ? 470 : onCard || ((cut?.type === 'video' || cut?.type === 'split') && !p.pos) ? 960 : p.pos === 'top' ? 560 : p.pos === 'mid' ? 960 : p.pos === 'bottom' ? 1430 : 1240;
  return (
    <AbsoluteFill style={{opacity: out, filter: `blur(${outBlur}px)`}}>
      <div style={{position: 'absolute', left: 50, right: 50, top: y, transform: 'translateY(-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
        {p.lines.map((l, i) => (
          <div key={i} style={{display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: 14 * scale, flexWrap: 'nowrap', marginTop: i ? -4 * scale : 0}}>
            {l.map((w, j) => (
              <Word key={j} w={w} scale={scale} color={color} shadow={!onCard} />
            ))}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ---------- ikon (SVG di dalam data.json) ----------
const Icon: React.FC<{ic: Ic; size: number; tile?: boolean}> = ({ic, size, tile}) => {
  const svg = ic.svg;
  if (!svg) return null;
  if (svg.kind === 'simple') {
    const inner = (
      <svg viewBox={svg.vb} width={size * 0.62} height={size * 0.62}>
        {svg.paths!.map((d, i) => (
          <path key={i} d={d} fill={ic.color ?? (svg.hex === '#000000' ? '#111' : svg.hex)} />
        ))}
      </svg>
    );
    return tile === false ? inner : (
      <div style={{width: size, height: size, borderRadius: size * 0.24, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 10px 30px rgba(0,0,0,.25)'}}>{inner}</div>
    );
  }
  return (
    <svg viewBox={svg.vb} width={size} height={size} fill="none" stroke={ic.color ?? '#1B1B1D'} strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round"
      dangerouslySetInnerHTML={{__html: svg.inner!}} />
  );
};
const TiledIcon: React.FC<{ic: Ic; size: number}> = ({ic, size}) =>
  ic.svg?.kind === 'lucide' ? (
    <div style={{width: size, height: size, borderRadius: size * 0.24, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 10px 30px rgba(0,0,0,.25)'}}>
      <Icon ic={ic} size={size * 0.6} />
    </div>
  ) : <Icon ic={ic} size={size} />;

const Asterisk: React.FC<{x: number; y: number; size: number; d: number}> = ({x, y, size, d}) => {
  const p = spring({frame: d, fps: FPS, config: {damping: 12, stiffness: 160}});
  return (
    <svg viewBox="-50 -50 100 100" width={size} height={size} style={{position: 'absolute', left: x - size / 2, top: y - size / 2, transform: `scale(${p}) rotate(${d * 1.2}deg)`}}>
      {Array.from({length: 10}).map((_, i) => (
        <rect key={i} x={-4} y={-48} width={8} height={40} rx={4} fill="#E8452C" transform={`rotate(${i * 36})`} />
      ))}
    </svg>
  );
};

// ---------- cutaway ----------
const BG: Record<string, string> = {
  red: 'radial-gradient(circle at 50% 45%, #C81F24 0%, #A3151A 50%, #5C0A0D 100%)',
  gray: 'radial-gradient(circle at 50% 50%, #F4F3F1 0%, #DCDAD7 55%, #A8A5A1 100%)',
  dark: 'radial-gradient(circle at 50% 45%, #2B2A2E 0%, #141416 60%, #050506 100%)',
  white: 'radial-gradient(circle at 50% 50%, #FFFFFF 0%, #F1F1F1 45%, #9A9A9A 100%)',
};
const Cutaway: React.FC<{c: Cut}> = ({c}) => {
  const frame = useCurrentFrame(); // lokal (Sequence)
  const dur = (c.to - c.from) * FPS;
  const fin = interpolate(frame, [0, 6], [0, 1], {...clamp, easing: ease});
  const fout = interpolate(frame, [dur - 5, dur], [1, 0], clamp);
  const o = Math.min(fin, fout);
  const pop = (delay: number) => spring({frame: frame - delay, fps: FPS, config: {damping: 13, stiffness: 190, mass: 0.6}});

  if (c.type === 'card') {
    return (
      <AbsoluteFill style={{opacity: o, background: c.bg === 'split' ? `linear-gradient(${C.merah} 0 50%, ${C.abu} 50% 100%)` : BG[c.bg ?? 'red']}}>
        {c.img && (
          <Img src={staticFile(c.img)} style={{position: 'absolute', left: (VW - 860) / 2, width: 860, top: LAND ? 110 : 640, height: LAND ? 640 : 860, objectFit: 'cover', borderRadius: 18,
            boxShadow: '0 20px 60px rgba(0,0,0,.4)', transform: `scale(${interpolate(frame, [0, dur], [1.0, 1.05])})`}} />
        )}
      </AbsoluteFill>
    );
  }
  if (c.type === 'video') {
    // B-roll stok: gelap, hangat, sedikit pelan (gaya referensi), masuk dengan defocus
    const z = interpolate(frame, [0, dur], [1.06, 1.14]);
    const bl = interpolate(frame, [0, 7], [16, 0], clamp);
    return (
      <AbsoluteFill style={{opacity: o, background: '#000'}}>
        <AbsoluteFill style={{transform: `scale(${z})`, filter: `blur(${bl}px) brightness(${c.bright ?? 0.7}) contrast(1.12) saturate(0.8) sepia(0.12)`}}>
          <OffthreadVideo src={staticFile(c.src!)} muted startFrom={Math.round((c.start ?? 0) * FPS)} playbackRate={c.rate ?? 0.85}
            style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${(c.x ?? 0.5) * 100}% ${(c.y ?? 0.5) * 100}%`}} />
        </AbsoluteFill>
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 35%, rgba(0,0,0,.55) 100%)'}} />
      </AbsoluteFill>
    );
  }
  if (c.type === 'split') {
    // separuh layar B-roll (bawah kalau talent di atas, atas kalau talent di bawah; lanskap: kanan/kiri), geser masuk dari tepi layar
    const top = talentTop(c);
    const g = frame + Math.round(c.from * FPS);
    const k = splitK(c, g);
    const bl = joined(c, 'in') ? interpolate(frame, [0, 7], [16, 0], clamp) : 0;
    const z = interpolate(frame, [0, dur], [1.04, 1.1]);
    return (
      <>
        <div style={{position: 'absolute', overflow: 'hidden', background: '#000',
          ...(LAND ? {top: 0, height: 1080, left: top ? 960 : 0, width: 960} : {left: 0, width: 1080, top: top ? 960 : 0, height: 960}),
          transform: LAND ? `translateX(${(1 - k) * (top ? 960 : -960)}px)` : `translateY(${(1 - k) * (top ? 960 : -960)}px)`}}>
          <AbsoluteFill style={{transform: `scale(${z})`, filter: `blur(${bl}px) brightness(${c.bright ?? 0.85}) contrast(1.1) saturate(0.85) sepia(0.1)`}}>
            <OffthreadVideo src={staticFile(c.src!)} muted startFrom={Math.round((c.start ?? 0) * FPS)} playbackRate={c.rate ?? 0.85}
              style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${(c.x ?? 0.5) * 100}% ${(c.y ?? 0.5) * 100}%`}} />
          </AbsoluteFill>
          <AbsoluteFill style={{background: `linear-gradient(${LAND ? (top ? 'to right' : 'to left') : top ? 'to bottom' : 'to top'}, rgba(0,0,0,.45) 0%, rgba(0,0,0,0) 22%)`}} />
        </div>
        <div style={{position: 'absolute', background: 'rgba(0,0,0,.9)', opacity: k,
          ...(LAND ? {top: 0, height: 1080, left: 958, width: 4} : {left: 0, width: 1080, top: 958, height: 4})}} />
      </>
    );
  }
  if (c.type === 'image') {
    return (
      <AbsoluteFill style={{opacity: o, background: '#000'}}>
        <Img src={staticFile(c.img!)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${interpolate(frame, [0, dur], [1.04, 1.12])})`}} />
        <AbsoluteFill style={{background: `rgba(0,0,0,${c.dim ?? 0.35})`}} />
      </AbsoluteFill>
    );
  }
  if (c.type === 'person') {
    return (
      <AbsoluteFill style={{opacity: o, background: BG.gray}}>
        {c.img && <Img src={staticFile(c.img)} style={{position: 'absolute', bottom: 0, left: 0, width: '100%', height: '78%', objectFit: 'cover', objectPosition: 'top'}} />}
        <div style={{position: 'absolute', top: LAND ? 60 : 150, width: '100%', textAlign: 'center', fontFamily: SERIF, fontStyle: 'italic', fontSize: LAND ? 96 : 120, color: C.merah, letterSpacing: '-0.01em'}}>{c.name}</div>
      </AbsoluteFill>
    );
  }
  if (c.type === 'icons') {
    return (
      <AbsoluteFill style={{opacity: o, background: BG[c.bg ?? 'white']}}>
        {(c.icons ?? []).map((ic, k) => {
          const p = pop(8 + k * 10);
          const size = ic.s ?? 230;
          return (
            <div key={k} style={{position: 'absolute', left: ic.x * VW - size / 2, top: ic.y * VH - size / 2, transform: `scale(${p}) translateY(${(1 - p) * 30}px)`, opacity: Math.min(1, p * 2)}}>
              <Icon ic={ic} size={size} />
            </div>
          );
        })}
      </AbsoluteFill>
    );
  }
  if (c.type === 'stat') {
    const num = parseFloat((c.value ?? '').replace(/[^\d,]/g, '').replace(',', '.'));
    const p = interpolate(frame, [0, 16], [0, 1], {...clamp, easing: ease});
    const shown = isNaN(num) ? c.value : c.value!.replace(/[\d.,]+/, () => {
      const v = num * p;
      const dec = (c.value!.split(',')[1] ?? '').replace(/\D/g, '').length;
      return v.toLocaleString('id-ID', {minimumFractionDigits: dec, maximumFractionDigits: dec});
    });
    const sc = pop(0);
    return (
      <AbsoluteFill style={{opacity: o}}>
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, rgba(0,0,0,.45) 0%, rgba(0,0,0,0) 60%)'}} />
        <div style={{position: 'absolute', top: LAND ? 200 : 560, width: '100%', textAlign: 'center', transform: `scale(${0.7 + 0.3 * sc})`}}>
          <div style={{fontFamily: SANS, fontWeight: 800, fontSize: Math.min(250, 1700 / Math.max(1, (c.value ?? '').length)), letterSpacing: '-0.05em', lineHeight: 1, textShadow: SHADOW,
            color: c.color === 'white' ? C.putih : c.color === 'red' ? '#E8452C' : C.kuning}}>{shown}</div>
          {c.label && <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 70, color: C.putih, textShadow: SHADOW, marginTop: -6}}>{c.label}</div>}
        </div>
      </AbsoluteFill>
    );
  }
  if (c.type === 'news') {
    const p = pop(0);
    return (
      <AbsoluteFill style={{opacity: o}}>
        <div style={{position: 'absolute', left: LAND ? 360 : 70, right: LAND ? 360 : 70, top: LAND ? 300 : 700, background: '#fff', borderRadius: 10, padding: '22px 30px 26px', boxShadow: '0 20px 50px rgba(0,0,0,.35)',
          transform: `translateY(${(1 - p) * 60}px) scale(${0.94 + 0.06 * p})`}}>
          <div style={{display: 'inline-block', fontFamily: UI, fontWeight: 600, fontSize: 26, color: '#444', background: '#EEE', borderRadius: 6, padding: '3px 10px'}}>{c.source}</div>
          <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 58, lineHeight: 1.04, letterSpacing: '-0.03em', color: '#111', marginTop: 12}}>{c.title}</div>
          {c.sub && <div style={{fontFamily: UI, fontWeight: 500, fontSize: 26, color: '#666', marginTop: 10}}>{c.sub}</div>}
        </div>
        <Asterisk x={LAND ? 300 : 110} y={LAND ? 600 : 1010} size={140} d={frame - 6} />
      </AbsoluteFill>
    );
  }
  // logos
  return (
    <AbsoluteFill style={{opacity: o}}>
      {(c.icons ?? []).map((ic, k) => {
        const p = pop(k * 8);
        const size = ic.s ?? 190;
        return (
          <div key={k} style={{position: 'absolute', left: ic.x * VW - size / 2, top: ic.y * VH - size / 2, transform: `scale(${p}) rotate(${(1 - p) * -12}deg)`}}>
            <TiledIcon ic={ic} size={size} />
          </div>
        );
      })}
      <Asterisk x={0.83 * VW} y={0.43 * VH} size={150} d={frame - 10} />
    </AbsoluteFill>
  );
};

// ---------- transisi ----------
const Overlays: React.FC = () => {
  const frame = useCurrentFrame();
  let white = 0;
  let wipe = 0;
  for (const f of data.fx) {
    const d = frame - Math.round(f.at * FPS);
    if (f.type === 'flash') white = Math.max(white, interpolate(d, [-3, 0, 2, 12], [0, PREMIUM ? 0.7 : 0.92, PREMIUM ? 0.55 : 0.85, 0], clamp));
    if (f.type === 'wipe') wipe = Math.max(wipe, d < 0 ? interpolate(d, [-9, 0], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)}) : interpolate(d, [0, 7], [1, 0], clamp) * 2);
  }
  return (
    <>
      {white > 0 && <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, #fff 0%, #fff 55%, #FFE2C4 100%)', opacity: white}} />}
      {wipe > 0 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: Math.min(1, wipe)}}>
          <div style={{width: 2400, height: 2400, borderRadius: '50%', background: C.merah, transform: `scale(${Math.min(1, wipe)})`}} />
        </AbsoluteFill>
      )}
    </>
  );
};

const Hook: React.FC<{text: string; until: number}> = ({text, until}) => {
  const frame = useCurrentFrame();
  const p = spring({frame: frame - 2, fps: FPS, config: {damping: 14, stiffness: 170, mass: 0.6}});
  const o = interpolate(frame, [until * FPS - 6, until * FPS], [1, 0], clamp);
  return (
    <AbsoluteFill style={{alignItems: 'center', top: LAND ? 70 : 150, opacity: o, transform: `scale(${0.85 + 0.15 * p})`, transformOrigin: '50% 10%'}}>
      {text.split('/').map((l, i) => (
        <div key={i} style={{background: C.merah, color: C.putih, fontFamily: SANS, fontWeight: 800, fontSize: LAND ? 62 : 74, letterSpacing: '-0.03em', lineHeight: 1,
          padding: '6px 16px 8px', marginTop: i ? -2 : 0, textTransform: 'uppercase', opacity: Math.min(1, p * 1.5)}}>{l.trim()}</div>
      ))}
    </AbsoluteFill>
  );
};

export const Podcast: React.FC = () => {
  const {fps} = useVideoConfig();
  const seq = (from: number, to: number) => ({from: Math.round(from * fps), durationInFrames: Math.max(1, Math.round((to - from) * fps))});
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Camera>
        <AbsoluteFill style={{filter: PREMIUM ? 'contrast(1.12) saturate(0.86) brightness(0.95) sepia(0.06)' : 'contrast(1.06) saturate(1.05) brightness(0.98)'}}>
          <Video src={staticFile('base.webm')} muted />
        </AbsoluteFill>
      </Camera>
      {!PREMIUM && <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 55%, rgba(0,0,0,.38) 100%)'}} />}
      {data.cutaways.map((c, i) => (
        <Sequence key={i} {...seq(c.from, c.to)} layout="none">
          <Cutaway c={c} />
        </Sequence>
      ))}
      {PREMIUM && (
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, rgba(0,0,0,0) 45%, rgba(0,0,0,.5) 100%), linear-gradient(to top, rgba(0,0,0,.55) 0%, rgba(0,0,0,.28) 34%, rgba(0,0,0,0) 56%)'}} />
      )}
      {data.phrases.map((p, i) => (
        <Sequence key={i} {...seq(0, p.end + 0.05)} layout="none">
          {/* frame global dipakai untuk waktu kata, jadi Sequence mulai dari 0 */}
          <Visible from={p.start} to={p.end}>
            <Caption p={p} />
          </Visible>
        </Sequence>
      ))}
      {data.hook && <Hook text={data.hook.text} until={data.hook.until} />}
      <Overlays />
      {PREMIUM && <Grain />}
      {/* semua x0,7 = ruang ~3 dB supaya suara + SFX (mis. boom saat teriak) tidak pecah; export.py menormalkan lagi ke -14 LUFS */}
      <Audio src={staticFile('voice.wav')} volume={0.7} />
      {data.sfx.map((s, i) => (
        <Sequence key={i} from={Math.round(s.t * fps)} layout="none">
          <Audio src={staticFile(s.f)} volume={s.v * 0.7} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const Visible: React.FC<{from: number; to: number; children: React.ReactNode}> = ({from, to, children}) => {
  const frame = useCurrentFrame();
  return frame >= from * FPS - 1 && frame <= to * FPS ? <>{children}</> : null;
};
