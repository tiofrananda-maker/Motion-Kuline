import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import data from './data.json';
import './fonts';
import {C, LOGO, SANS, SERIF, SHADOW, TEXT} from './theme';
import {fade, fadeOut} from './anim';
import {GRADE} from './grade';

// =====================================================================
// GAYA TETAP (meniru referensi resep estetik). JANGAN diubah per video.
// Isi per video ada di edit/resep.json + edit/captions.json -> tools/captions.py -> src/data.json.
// Ukuran sudah dikalibrasi ke referensi (1080x1920).
// =====================================================================
const f = (sec: number) => Math.round(sec * 30);
const MID = 960; // semua teks utama berpusat di tengah layar, seperti referensi

type Cap = {s: number; e: number; w: [string, number, number][]};

// Nama akun kecil di atas tengah, sepanjang video
const Handle: React.FC = () =>
  data.handle ? (
    <div style={{position: 'absolute', top: 206, left: 0, right: 0, textAlign: 'center', fontFamily: LOGO, fontWeight: 600,
      fontSize: 31, letterSpacing: '0.01em', color: C.krem, opacity: 0.94, textShadow: SHADOW}}>{data.handle}</div>
  ) : null;

// Eyebrow: huruf kapital miring kecil (Inter Display Medium Italic)
const Eyebrow: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div style={{fontFamily: SANS, fontStyle: 'italic', fontWeight: 500, fontSize: 24, letterSpacing: '-0.01em',
    textTransform: 'uppercase', lineHeight: 1, color: C.putih, ...style}}>{children}</div>
);

// Judul pembuka: eyebrow + serif, diam di tengah, hilang memudar
const Judul: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const o = fadeOut(frame, dur, 7);
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: MID - 8, transform: 'translateY(-50%)', textAlign: 'center',
      display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: o, textShadow: SHADOW}}>
      <Eyebrow style={{marginBottom: 2}}>{data.judul.atas}</Eyebrow>
      <div style={{fontFamily: SERIF, fontWeight: 400, fontSize: 60, lineHeight: 1.0, letterSpacing: '-0.035em', color: C.putih}}>
        {data.judul.teks}
      </div>
    </div>
  );
};

// Caption VO: huruf kecil miring tipis, kata muncul satu-satu (menumpuk), frasa baru menggantikan
const Caption: React.FC<{c: Cap}> = ({c}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: 110, right: 110, top: MID, transform: 'translateY(-50%)', textAlign: 'center',
      fontFamily: TEXT, fontStyle: 'italic', fontWeight: 400, fontSize: 25, lineHeight: 1.3, letterSpacing: '-0.005em',
      color: C.putih, textShadow: SHADOW}}>
      {c.w.map(([w, s], i) => (
        <span key={i} style={{opacity: fade(frame, f(s - c.s), 3)}}>{w}{i < c.w.length - 1 ? ' ' : ''}</span>
      ))}
    </div>
  );
};

// Ajakan komentar di akhir: COMMENT / "Kata" / AND GET THE RECIPE
const Ajakan: React.FC = () => {
  const frame = useCurrentFrame();
  const o = fade(frame, 0, 3);
  const q: React.CSSProperties = {fontFamily: SANS, fontWeight: 700, fontSize: 62, lineHeight: 1, position: 'relative', top: -6, margin: '0 -1px'};
  return (
    <div style={{position: 'absolute', left: 40, right: 40, top: MID - 4, transform: 'translateY(-50%)', textAlign: 'center',
      display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: o, textShadow: SHADOW, color: C.putih}}>
      <Eyebrow style={{marginBottom: -10, position: 'relative', zIndex: 1}}>{data.cta.atas}</Eyebrow>
      <div style={{display: 'flex', alignItems: 'flex-start', justifyContent: 'center'}}>
        <span style={q}>"</span>
        <span style={{fontFamily: SERIF, fontWeight: 400, fontSize: 75, lineHeight: 1.0, letterSpacing: '-0.03em'}}>{data.cta.kata}</span>
        <span style={q}>"</span>
      </div>
      <Eyebrow style={{marginTop: 22}}>{data.cta.bawah}</Eyebrow>
    </div>
  );
};

export const Resep: React.FC = () => {
  const {fps} = useVideoConfig();
  const caps = data.captions as unknown as Cap[];
  const total = f(data.total);
  const ctaFrom = f(data.cta.mulai);
  return (
    <AbsoluteFill style={{background: C.gelap}}>
      <Video src={staticFile('base.webm')} muted disallowFallbackToOffthreadVideo effects={GRADE} />
      <Audio src={staticFile('mix.wav')} />
      <Handle />
      {data.judul.teks ? (
        <Sequence name="Judul" from={0} durationInFrames={f(data.judul.sampai)}>
          <Judul dur={f(data.judul.sampai)} />
        </Sequence>
      ) : null}
      {caps.map((c, i) => (
        <Sequence key={i} name={`cap ${c.w.map((x) => x[0]).join(' ')}`} from={f(c.s)} durationInFrames={Math.max(1, f(c.e) - f(c.s))} premountFor={fps}>
          <Caption c={c} />
        </Sequence>
      ))}
      {data.cta.kata ? (
        <Sequence name="Ajakan" from={ctaFrom} durationInFrames={Math.max(1, total - ctaFrom)}>
          <Ajakan />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};
