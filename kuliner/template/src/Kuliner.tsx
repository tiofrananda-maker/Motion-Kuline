import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import data from './data.json';
import './fonts';
import {C, FONT, SERIF, TEXT} from './theme';
import {enter, pop} from './anim';
import {GRADE} from './grade';

const S = data.segments as Record<string, {start: number; dur: number}>;
const f = (sec: number) => Math.round(sec * 30);

// Bayangan lembut berlapis pengganti latar: teks tetap jelas tanpa kotak
const SHADOW = '0 2px 3px rgba(0,0,0,0.6), 0 6px 22px rgba(0,0,0,0.5), 0 12px 48px rgba(0,0,0,0.3)';

// ---------- Teks kaya: kata di antara *...* jadi serif miring ----------
type Tok = {w: string; serif: boolean};
const parse = (text: string): Tok[] => {
  let inSerif = false;
  return text.split(' ').map((raw) => {
    let w = raw;
    if (w.startsWith('*')) {
      inSerif = true;
      w = w.slice(1);
    }
    const serif = inSerif;
    if (w.endsWith('*')) {
      inSerif = false;
      w = w.slice(0, -1);
    }
    return {w, serif};
  });
};
const serifStyle = (accent: string): React.CSSProperties => ({
  fontFamily: SERIF, fontStyle: 'italic', fontWeight: 400, fontSize: '1.12em', letterSpacing: '-0.01em', color: accent,
});

// ---------- Posisi berpindah-pindah (aman dari tombol IG di kanan bawah) ----------
type Pos = 'TL' | 'TR' | 'ML' | 'MR' | 'LL' | 'LR' | 'C';
const POS: Record<Pos, React.CSSProperties & {align: 'left' | 'right' | 'center'}> = {
  TL: {top: 290, left: 72, align: 'left'},
  TR: {top: 290, right: 72, align: 'right'},
  ML: {top: 760, left: 72, align: 'left'},
  MR: {top: 760, right: 72, align: 'right'},
  LL: {top: 1230, left: 72, align: 'left'},
  LR: {top: 1230, right: 150, align: 'right'},
  C: {top: 700, left: 72, right: 72, align: 'center'},
};

type Line =
  | {kind: 'main'; text: string; size?: number; color?: string; accent?: string; at?: number}
  | {kind: 'sub'; text: string; color?: string; size?: number; at?: number}
  | {kind: 'count'; a: number; b: number; unit: string; at?: number}
  | {kind: 'row'; label?: string; value?: string; at?: number}
  | {kind: 'strike'; label: string; at: number};

const Word: React.FC<{p: number; children: React.ReactNode; style?: React.CSSProperties}> = ({p, children, style}) => (
  <span style={{
    display: 'inline-block', opacity: p, ...style,
    filter: `blur(${interpolate(p, [0, 1], [8, 0])}px)`,
    transform: `translateY(${interpolate(p, [0, 1], [14, 0])}px)`,
  }}>{children}</span>
);

const Callout: React.FC<{pos: Pos; eyebrow?: string; lines: Line[]; dur: number; hold?: boolean}> = ({pos, eyebrow, lines, dur, hold}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {align, ...place} = POS[pos];
  const dir = align === 'right' ? 1 : -1;
  // keluar: memudar + sedikit naik + blur, 8 frame
  const out = hold ? 1 : interpolate(frame, [dur - 8, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const eb = enter(frame, fps, 0);
  const justify = align === 'right' ? 'flex-end' : align === 'center' ? 'center' : 'flex-start';
  return (
    <div style={{
      position: 'absolute', ...place, maxWidth: pos === 'C' ? undefined : 936, textAlign: align,
      display: 'flex', flexDirection: 'column', alignItems: justify,
      opacity: out, filter: `blur(${interpolate(out, [0, 1], [6, 0])}px)`, transform: `translateY(${interpolate(out, [0, 1], [-10, 0])}px)`,
      textShadow: SHADOW, color: C.putih,
    }}>
      {eyebrow ? (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 14, flexDirection: align === 'right' ? 'row-reverse' : 'row', marginBottom: 12,
          opacity: eb, transform: `translateX(${interpolate(eb, [0, 1], [24 * dir, 0])}px)`,
        }}>
          {/* garis aksen kecil sebagai elemen penanda */}
          <div style={{width: interpolate(eb, [0, 1], [0, 34]), height: 4, borderRadius: 2, background: C.kunyit, boxShadow: '0 2px 8px rgba(0,0,0,0.45)'}} />
          <div style={{fontFamily: TEXT, fontWeight: 700, fontSize: 30, letterSpacing: '0.16em', color: C.kunyit}}>{eyebrow}</div>
        </div>
      ) : null}
      {lines.map((l, i) => {
        const at = f(l.at ?? 0) + 3 + (l.at === undefined ? i * 4 : 0);
        if (l.kind === 'main') {
          const toks = parse(l.text);
          return (
            <div key={i} style={{display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', justifyContent: justify, gap: '0 0.26em', fontFamily: FONT, fontWeight: 700, fontSize: l.size ?? 68, lineHeight: 1.08, letterSpacing: '-0.03em', color: l.color ?? C.putih}}>
              {toks.map((t, j) => (
                <Word key={j} p={enter(frame, fps, at + j * 2.2)} style={t.serif ? serifStyle(l.accent ?? C.kunyit) : undefined}>{t.w}</Word>
              ))}
            </div>
          );
        }
        if (l.kind === 'sub') {
          const toks = parse(l.text);
          return (
            <Word key={i} p={enter(frame, fps, at)} style={{marginTop: 10, fontFamily: TEXT, fontWeight: l.size ? 600 : 500, fontSize: l.size ?? 36, letterSpacing: '-0.01em', color: l.color ?? C.krem}}>
              {toks.map((t, j) => (
                <span key={j} style={t.serif ? serifStyle(C.kunyit) : undefined}>{t.w}{j < toks.length - 1 ? ' ' : ''}</span>
              ))}
            </Word>
          );
        }
        if (l.kind === 'count') {
          const cnt = interpolate(frame, [at, at + 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: (x) => 1 - Math.pow(1 - x, 3)});
          const land = pop(frame, fps, at + 18);
          return (
            <Word key={i} p={enter(frame, fps, at)} style={{marginTop: 4, fontFamily: FONT, fontWeight: 800, fontSize: 100, lineHeight: 1, letterSpacing: '-0.04em', color: C.kunyit, fontVariantNumeric: 'tabular-nums'}}>
              <span style={{display: 'inline-block', transform: `scale(${interpolate(land, [0, 1], [0.96, 1])})`, transformOrigin: align}}>
                {Math.round(l.a * cnt)}–{Math.round(l.b * cnt)}
                <span style={{...serifStyle(C.putih), fontSize: 56, marginLeft: 14}}>menit</span>
              </span>
            </Word>
          );
        }
        if (l.kind === 'strike') {
          // daftar "tanpa ...": muncul lalu dicoret garis Cabai
          const rp = enter(frame, fps, at);
          const s = interpolate(frame, [at + 6, at + 13], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: (x) => 1 - Math.pow(1 - x, 3)});
          return (
            <div key={i} style={{position: 'relative', marginTop: 4, opacity: rp * interpolate(s, [0, 1], [1, 0.82]), transform: `translateX(${interpolate(rp, [0, 1], [18 * dir, 0])}px)`, filter: `blur(${interpolate(rp, [0, 1], [6, 0])}px)`}}>
              <span style={{fontFamily: TEXT, fontWeight: 600, fontSize: 44, letterSpacing: '-0.01em'}}>{l.label}</span>
              <div style={{position: 'absolute', left: -6, top: '54%', height: 5, borderRadius: 3, width: `calc(${s * 100}% + 12px)`, background: C.cabai, boxShadow: '0 2px 6px rgba(0,0,0,0.5)'}} />
            </div>
          );
        }
        const rp = enter(frame, fps, at);
        return (
          <div key={i} style={{
            display: 'flex', alignItems: 'baseline', gap: 18, marginTop: 8, opacity: rp,
            flexDirection: align === 'right' ? 'row-reverse' : 'row',
            transform: `translateX(${interpolate(rp, [0, 1], [18 * dir, 0])}px)`, filter: `blur(${interpolate(rp, [0, 1], [6, 0])}px)`,
          }}>
            {l.label ? <span style={{fontFamily: TEXT, fontWeight: 600, fontSize: 42, letterSpacing: '-0.01em'}}>{l.label}</span> : null}
            {l.value ? <span style={{fontFamily: FONT, fontWeight: 800, fontSize: 48, letterSpacing: '-0.02em', color: C.kunyit}}>{l.value}</span> : null}
          </div>
        );
      })}
    </div>
  );
};

// =====================================================================
// KONTEN PER VIDEO: ubah CHAPTERS, CUES, dan SFX di bawah sesuai brief.
// Komponen di atas (Callout, gaya teks, posisi) JANGAN diubah: itu aturan final.
// Contoh di bawah = video Ayam Panggang Mbah Dinem (versi final disetujui).
// =====================================================================

// ---------- Progress bar bab: WAJIB selalu tampil dari awal sampai akhir ----------
const g = S;
const ctaAlamat = g.cta.start + 8.5;
const CHAPTERS = [
  {label: 'KHAS KLATEN', from: 0, to: g.ajaib.start},
  {label: 'PROSES', from: g.ajaib.start, to: g.bestseller.start},
  {label: 'MENU', from: g.bestseller.start, to: g.tempat.start},
  {label: 'SUASANA', from: g.tempat.start, to: g.makan.start},
  {label: 'CICIP', from: g.makan.start, to: ctaAlamat},
  {label: 'LOKASI', from: ctaAlamat, to: data.total},
];
const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const p = enter(frame, fps, 0);
  const idx = Math.max(0, CHAPTERS.findIndex((c) => t >= c.from && t < c.to));
  const chapStart = f(CHAPTERS[idx].from);
  const lp = idx === 0 ? p : enter(frame, fps, chapStart);
  return (
    <div style={{position: 'absolute', top: 96, left: 72, right: 72, opacity: p}}>
      <div style={{display: 'flex', gap: 10}}>
        {CHAPTERS.map((c, i) => {
          const fill = interpolate(t, [c.from, c.to], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return (
            <div key={i} style={{flex: 1, height: 9, borderRadius: 9, background: 'rgba(255,255,255,0.42)', overflow: 'hidden', boxShadow: '0 2px 10px rgba(0,0,0,0.35)'}}>
              <div style={{width: `${fill * 100}%`, height: '100%', background: C.cabai}} />
            </div>
          );
        })}
      </div>
      <div style={{
        marginTop: 18, display: 'flex', alignItems: 'baseline', gap: 14, textShadow: SHADOW,
        opacity: lp, transform: `translateY(${interpolate(lp, [0, 1], [10, 0])}px)`,
      }}>
        <span style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 40, color: C.kunyit, lineHeight: 1}}>{String(idx + 1).padStart(2, '0')}</span>
        <span style={{fontFamily: TEXT, fontWeight: 700, fontSize: 30, letterSpacing: '0.16em', color: C.putih}}>{CHAPTERS[idx].label}</span>
      </div>
    </div>
  );
};

// ---------- Poin penting (sesuai brief), waktu dalam detik komposisi ----------
type Cue = {name: string; from: number; to: number; pos: Pos; eyebrow?: string; lines: Line[]; hold?: boolean};
const TANPA = ['direbus', 'dikukus', 'diungkep', 'digoreng', 'dibakar', 'minyak', 'MSG'];
const CUES: Cue[] = [
  {name: 'Hook', from: 0.1, to: g.intro.start - 0.1, pos: 'TL', eyebrow: 'REVIEW KULINER', lines: [
    {kind: 'main', text: 'Ayam *Ajaib*', size: 116},
    {kind: 'sub', text: 'dipanggang dari mentah sampai matang', size: 38, at: 0.9},
  ]},
  {name: 'Nama', from: g.intro.start + 0.3, to: g.unik.start - 0.1, pos: 'TL', eyebrow: 'MBAH DINEM KUNINGAN', lines: [
    {kind: 'main', text: 'Ayam Panggang *Khas Klaten*', size: 66},
  ]},
  {name: 'Tungku', from: g.unik.start + 0.6, to: g.unik.start + 3.45, pos: 'MR', eyebrow: 'DIMASAK DI', lines: [
    {kind: 'main', text: 'tungku *gerabah*'},
  ]},
  {name: 'Bukan soto', from: g.unik.start + 3.55, to: g.ajaib.start - 0.1, pos: 'TL', eyebrow: 'BUKAN SOTO', lines: [
    {kind: 'main', text: 'ini ayam *panggang*'},
  ]},
  {name: 'Ajaib?', from: g.ajaib.start + 0.4, to: g.tanpa.start - 0.1, pos: 'LL', lines: [
    {kind: 'main', text: 'Kenapa disebut *ajaib?*', size: 60},
  ]},
  {name: 'Tanpa', from: g.tanpa.start + 0.2, to: g.tanpa.start + 7.6, pos: 'TL', eyebrow: 'TANPA', lines:
    TANPA.map((label, i) => ({kind: 'strike' as const, label, at: 0.3 + i * 0.55})),
  },
  {name: '100% panggang', from: g.tanpa.start + 7.7, to: g.bumbu.start - 0.05, pos: 'ML', eyebrow: '100% DIPANGGANG', lines: [
    {kind: 'main', text: 'dari mentah sampai *matang*', size: 58},
    {kind: 'count', a: 10, b: 15, unit: 'menit', at: 1.8},
  ]},
  {name: 'Bumbu', from: g.bumbu.start + 2.9, to: g.bumbu.start + 6.4, pos: 'LR', eyebrow: 'RESEP WARISAN', lines: [
    {kind: 'main', text: '*turun-temurun*'},
  ]},
  {name: 'Klaten', from: g.bumbu.start + 6.6, to: g.panggang2.start - 0.1, pos: 'TL', eyebrow: 'AYAM PANGGANG', lines: [
    {kind: 'main', text: 'khas *Klaten*', size: 92},
  ]},
  {name: 'Sehat', from: g.panggang2.start + 0.2, to: g.bestseller.start - 0.05, pos: 'LL', eyebrow: 'LEBIH SEHAT', lines: [
    {kind: 'row', label: 'Ayam kampung', at: 0.2},
    {kind: 'row', label: 'Lemak menetes di gerabah', at: 0.7},
    {kind: 'row', label: 'Rendah kolesterol', at: 1.2},
  ]},
  {name: '5-7 menit', from: g.panggang2.start + 1.7, to: g.bestseller.start - 0.05, pos: 'TR', eyebrow: 'PANGGANG KEDUA', lines: [
    {kind: 'count', a: 5, b: 7, unit: 'menit', at: 0.3},
  ]},
  {name: 'Harga', from: g.bestseller.start + 0.2, to: g.wedang.start - 0.1, pos: 'TL', eyebrow: 'MENU & HARGA', lines: [
    {kind: 'row', label: 'Ayam utuh', value: 'Rp130rb', at: 0.3},
    {kind: 'row', label: '½ ekor', value: 'Rp70rb', at: 0.75},
    {kind: 'row', label: '¼ ekor', value: 'Rp35rb', at: 1.2},
    {kind: 'sub', text: 'Favorit: bumbu *pedas manis*', size: 40, at: 3.0},
  ]},
  {name: 'Wedang', from: g.wedang.start + 1.4, to: g.menubaru.start - 0.1, pos: 'TL', eyebrow: 'WEDANG REMPAH', lines: [
    {kind: 'main', text: 'Wedang *Uwuh*'},
    {kind: 'row', value: 'Rp18rb', at: 0.8},
  ]},
  {name: 'Menu baru', from: g.menubaru.start + 0.1, to: g.tempat.start - 0.1, pos: 'TR', eyebrow: 'MENU BARU', lines: [
    {kind: 'main', text: '*Sayur Asem*', size: 64, accent: C.putih, at: 1.1},
    {kind: 'main', text: '*Telur Barendo*', size: 64, accent: C.putih, at: 2.5},
  ]},
  {name: 'Tempat', from: g.tempat.start + 0.3, to: g.tempat.start + 6.5, pos: 'TL', eyebrow: 'DINE-IN NYAMAN', lines: [
    {kind: 'main', text: 'Lesehan *luas*'},
    {kind: 'sub', text: 'bersih & estetik', at: 2.4},
    {kind: 'sub', text: 'cocok buat buka puasa bareng', at: 4.5},
  ]},
  {name: 'Lebaran', from: g.tempat.start + 6.6, to: g.info.start - 0.1, pos: 'LL', eyebrow: 'LEBARAN', lines: [
    {kind: 'main', text: 'tetap *buka*', size: 76},
    {kind: 'sub', text: 'makan rame-rame bareng keluarga', at: 0.8},
  ]},
  {name: 'Jam', from: g.info.start + 0.2, to: g.info.start + 4.5, pos: 'TL', eyebrow: 'JAM OPERASIONAL', lines: [
    {kind: 'main', text: '08.00–21.00 *WIB*', size: 74},
  ]},
  {name: 'Parkir', from: g.info.start + 2.7, to: g.info.start + 4.5, pos: 'LR', lines: [
    {kind: 'main', text: 'Parkiran *luas*', size: 64},
  ]},
  {name: 'Reservasi', from: g.info.start + 4.6, to: g.makan.start - 0.05, pos: 'TL', eyebrow: 'RESERVASI BUKA PUASA', lines: [
    {kind: 'main', text: '+62 8xx-xxxx-xxxx', size: 60},
  ]},
  {name: 'Juicy', from: g.makan.start + 1.9, to: g.makan.start + 4.35, pos: 'MR', eyebrow: 'DAGINGNYA', lines: [
    {kind: 'main', text: '*juicy*', size: 112},
  ]},
  {name: 'Besar', from: g.makan.start + 4.45, to: g.cta.start - 0.05, pos: 'TL', lines: [
    {kind: 'main', text: 'Besar *banget!*', size: 80},
  ]},
  {name: 'Rekomendasi', from: g.cta.start + 0.2, to: g.cta.start + 5.6, pos: 'LL', eyebrow: 'REKOMENDASI', lines: [
    {kind: 'main', text: 'buat buka *puasa*', at: 2.2},
    {kind: 'sub', text: 'reservasi · keluarga · teman', at: 3.8},
  ]},
  {name: 'Gas', from: g.cta.start + 5.7, to: ctaAlamat - 0.05, pos: 'TL', eyebrow: 'MAU LEBARAN?', lines: [
    {kind: 'main', text: 'Gas ke *Mbah Dinem!*', size: 70},
  ]},
  {name: 'Alamat', from: ctaAlamat, to: data.total, pos: 'TL', hold: true, eyebrow: 'ALAMAT', lines: [
    {kind: 'main', text: 'Ayam Panggang *Mbah Dinem*', size: 54, accent: C.putih},
    {kind: 'sub', text: '5G47+49H, Wanayasa, Kec. Beber', at: 0.5},
    {kind: 'sub', text: 'Kab. Cirebon, Jawa Barat 45172', at: 0.8},
    {kind: 'sub', text: 'Buka 08.00–21.00 WIB', color: C.putih, size: 38, at: 1.1},
  ]},
  {name: 'Penutup', from: g.outro.start + 0.4, to: data.total, pos: 'LL', hold: true, lines: [
    {kind: 'main', text: '*Simpan.*', size: 120, accent: C.putih},
    {kind: 'sub', text: 'Tag teman makanmu', size: 38, at: 0.6},
  ]},
];

// ---------- SFX (CC0 soundcn + whoosh/bonang sintetis) ----------
type Sfx = {t: number; src: string; v: number};
const sfx = (t: number, name: string, v = 0.35): Sfx => ({t, src: `sfx/${name}`, v});
const at = (name: string) => CUES.find((c) => c.name === name)!.from;
const ticks = (t0: number) => [0, 1, 2, 3, 4, 5].map((i) => sfx(t0 + i * 0.1, 'tick-001.mp3', 0.22));
const SFX: Sfx[] = [
  sfx(0.08, 'bonang.wav', 0.3), sfx(0.12, 'whoosh.wav', 0.3), sfx(0.25, 'impact-soft-medium-001.mp3', 0.4),
  // pergantian bab di progress bar
  ...CHAPTERS.slice(1).map((c) => sfx(c.from, 'hover-tick.mp3', 0.3)),
  sfx(at('Nama'), 'whoosh.wav', 0.28), sfx(at('Nama') + 0.15, 'card-slide-1.mp3', 0.3),
  sfx(at('Tungku'), 'card-slide-3.mp3', 0.3),
  sfx(at('Bukan soto'), 'switch-on.mp3', 0.3),
  sfx(at('Ajaib?'), 'click-soft.mp3', 0.45),
  ...TANPA.map((_, i) => sfx(at('Tanpa') + 0.3 + i * 0.55 + 0.32, 'click-soft.mp3', 0.4)),
  sfx(at('100% panggang'), 'whoosh.wav', 0.25), ...ticks(at('100% panggang') + 1.9),
  sfx(at('100% panggang') + 2.5, 'notification-pop.mp3', 0.3),
  sfx(at('Bumbu'), 'card-slide-5.mp3', 0.3),
  sfx(at('Klaten'), 'impact-wood-light-001.mp3', 0.4),
  ...[0.2, 0.7, 1.2].map((d) => sfx(at('Sehat') + d + 0.08, 'tick-001.mp3', 0.3)),
  ...ticks(at('5-7 menit') + 0.4), sfx(at('5-7 menit') + 1.0, 'notification-pop.mp3', 0.3),
  sfx(at('Harga'), 'card-slide-1.mp3', 0.28),
  ...[0.3, 0.75, 1.2].map((d) => sfx(at('Harga') + d + 0.1, 'coin-collect.mp3', 0.22)),
  sfx(at('Harga') + 3.1, 'notification-pop.mp3', 0.28),
  sfx(at('Wedang'), 'glass-002.mp3', 0.45), sfx(at('Wedang') + 0.9, 'coin-collect.mp3', 0.22),
  sfx(at('Menu baru'), 'switch-on.mp3', 0.3), sfx(at('Menu baru') + 1.15, 'notification-pop.mp3', 0.28), sfx(at('Menu baru') + 2.55, 'notification-pop.mp3', 0.28),
  sfx(at('Tempat'), 'whoosh.wav', 0.28), sfx(at('Tempat') + 0.1, 'card-slide-3.mp3', 0.25),
  sfx(at('Lebaran'), 'success-chime.mp3', 0.25),
  sfx(at('Jam'), 'card-slide-5.mp3', 0.28),
  sfx(at('Parkir'), 'click-soft.mp3', 0.4),
  sfx(at('Reservasi'), 'switch-on.mp3', 0.3),
  sfx(at('Juicy') + 0.1, 'notification-pop.mp3', 0.35),
  sfx(at('Besar'), 'impact-wood-light-001.mp3', 0.4),
  sfx(at('Rekomendasi'), 'card-slide-5.mp3', 0.28),
  sfx(at('Gas'), 'whoosh.wav', 0.3),
  sfx(at('Alamat'), 'card-slide-1.mp3', 0.3),
  sfx(at('Penutup'), 'bonang.wav', 0.22), sfx(at('Penutup') + 0.05, 'success-chime.mp3', 0.35),
];

export const Kuliner: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: C.arang}}>
      <Video src={staticFile('base.webm')} muted disallowFallbackToOffthreadVideo effects={GRADE} />
      <Audio src={staticFile('mix.wav')} />
      <Progress />
      {CUES.map((c) => (
        <Sequence key={c.name} name={c.name} from={f(c.from)} durationInFrames={f(c.to) - f(c.from)} premountFor={fps}>
          <Callout pos={c.pos} eyebrow={c.eyebrow} lines={c.lines} dur={f(c.to) - f(c.from)} hold={c.hold} />
        </Sequence>
      ))}
      {SFX.map((s, i) => (
        <Sequence key={`sfx${i}`} name={`sfx ${s.src}`} from={f(s.t)} durationInFrames={f(2.4)} layout="none">
          <Audio src={staticFile(s.src)} volume={s.v} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
