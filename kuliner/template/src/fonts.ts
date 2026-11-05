import {continueRender, delayRender, staticFile} from 'remotion';

// DM Serif Display = serif yang sama dengan brief brand Mbah Dinem,
// dipasangkan dengan Inter Display (pengganti SF Pro) untuk teks utama.
const W: Record<string, string> = {Regular: '400', Medium: '500', SemiBold: '600', Bold: '700', ExtraBold: '800'};
// Semua font ikut di public/fonts supaya hasil render sama di laptop mana pun (Windows tidak punya Inter bawaan).
const faces: [string, string, FontFaceDescriptors][] = [
  ['DM Serif Display', 'fonts/dmserif-italic.woff2', {style: 'italic', weight: '400'}],
  ['DM Serif Display', 'fonts/dmserif-regular.woff2', {style: 'normal', weight: '400'}],
  ...['Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold'].map((w) => ['Inter Display', `fonts/InterDisplay-${w}.otf`, {weight: W[w]}] as [string, string, FontFaceDescriptors]),
  ...['Regular', 'Medium', 'SemiBold', 'Bold'].map((w) => ['Inter', `fonts/Inter-${w}.otf`, {weight: W[w]}] as [string, string, FontFaceDescriptors]),
];
if (typeof document !== 'undefined') {
  const handle = delayRender('Memuat font');
  Promise.all(
    faces.map(([fam, file, desc]) => new FontFace(fam, `url(${staticFile(file)})`, desc).load()),
  )
    .then((loaded) => {
      loaded.forEach((f) => (document.fonts as unknown as {add: (x: FontFace) => void}).add(f));
      continueRender(handle);
    })
    .catch((err) => {
      console.error(err);
      continueRender(handle);
    });
}
