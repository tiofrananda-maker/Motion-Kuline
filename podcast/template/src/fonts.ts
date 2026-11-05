import {continueRender, delayRender, staticFile} from 'remotion';

// Semua font ikut di public/fonts supaya hasil render sama di laptop mana pun
// (Inter Display = pengganti SF Pro, Instrument Serif = serif tinggi ala referensi).
const faces: [string, string, FontFaceDescriptors][] = [
  ['Inter Display', 'fonts/InterDisplay-Light.otf', {weight: '300', style: 'normal'}],
  ['Inter Display', 'fonts/InterDisplay-SemiBold.otf', {weight: '600', style: 'normal'}],
  ['Inter Display', 'fonts/InterDisplay-Bold.otf', {weight: '700', style: 'normal'}],
  ['Inter Display', 'fonts/InterDisplay-ExtraBold.otf', {weight: '800', style: 'normal'}],
  ['Inter Display', 'fonts/InterDisplay-SemiBoldItalic.otf', {weight: '600', style: 'italic'}],
  ['Inter Display', 'fonts/InterDisplay-BoldItalic.otf', {weight: '700', style: 'italic'}],
  ['Inter', 'fonts/Inter-Medium.otf', {weight: '500', style: 'normal'}],
  ['Inter', 'fonts/Inter-SemiBold.otf', {weight: '600', style: 'normal'}],
  ['Instrument Serif', 'fonts/instrument-serif.woff2', {weight: '400', style: 'normal'}],
  ['Instrument Serif', 'fonts/instrument-serif-italic.woff2', {weight: '400', style: 'italic'}],
];
if (typeof document !== 'undefined') {
  const handle = delayRender('Memuat font');
  Promise.all(faces.map(([fam, file, desc]) => new FontFace(fam, `url(${staticFile(file)})`, desc).load()))
    .then((loaded) => {
      loaded.forEach((f) => (document.fonts as unknown as {add: (x: FontFace) => void}).add(f));
      continueRender(handle);
    })
    .catch((err) => {
      console.error(err);
      continueRender(handle);
    });
}
