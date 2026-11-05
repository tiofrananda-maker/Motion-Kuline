import {continueRender, delayRender, staticFile} from 'remotion';

// Semua font ikut di public/fonts supaya hasil render sama di laptop mana pun.
const faces: [string, string, FontFaceDescriptors][] = [
  ['DM Serif Display', 'fonts/dmserif-regular.woff2', {style: 'normal', weight: '400'}],
  ['DM Serif Display', 'fonts/dmserif-italic.woff2', {style: 'italic', weight: '400'}],
  ['Inter Display', 'fonts/InterDisplay-Italic.otf', {style: 'italic', weight: '400'}],
  ['Inter Display', 'fonts/InterDisplay-MediumItalic.otf', {style: 'italic', weight: '500'}],
  ['Inter Display', 'fonts/InterDisplay-Bold.otf', {style: 'normal', weight: '700'}],
  ['Inter', 'fonts/Inter-LightItalic.otf', {style: 'italic', weight: '300'}],
  ['Inter', 'fonts/Inter-Italic.otf', {style: 'italic', weight: '400'}],
  ['Inter', 'fonts/Inter-MediumItalic.otf', {style: 'italic', weight: '500'}],
  ['Inter', 'fonts/Inter-Regular.otf', {style: 'normal', weight: '400'}],
  ['Comfortaa', 'fonts/Comfortaa.ttf', {style: 'normal', weight: '300 700'}],
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
