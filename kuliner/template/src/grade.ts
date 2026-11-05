import {vignette} from '@remotion/effects/vignette';
import {whiteBalance} from '@remotion/effects/white-balance';
import {vibrance} from '@remotion/effects/vibrance';
import {contrast} from '@remotion/effects/contrast';
import {exposure} from '@remotion/effects/exposure';
import {saturation} from '@remotion/effects/saturation';
import {tint} from '@remotion/effects/tint';
import {shadowsHighlights} from '@remotion/effects/shadows-highlights';

// Grade "resto besar": sedikit gelap, hangat ala kayu jati/sogan, sorotan ditahan
// supaya makanan dan kulit tetap segar, tepi digelapkan agar mata ke tengah.
export const GRADES = {
  A: [
    exposure({stops: -0.2}),
    shadowsHighlights({shadows: -0.12, highlights: -0.3}),
    contrast({amount: 1.1}),
    whiteBalance({temperature: 0.14, tint: 0.02}),
    saturation({amount: 1.04}),
    vignette({amount: 0.4, radius: 0.72, feather: 0.55}),
  ],
  B: [
    exposure({stops: -0.28}),
    shadowsHighlights({shadows: -0.1, highlights: -0.35}),
    contrast({amount: 1.12}),
    whiteBalance({temperature: 0.18, tint: 0.03}),
    tint({color: '#7A4A24', amount: 0.08}),
    vibrance({amount: 0.08}),
    vignette({amount: 0.5, radius: 0.68, feather: 0.6}),
  ],
  D: [
    exposure({stops: -0.3}),
    shadowsHighlights({shadows: -0.08, highlights: -0.4}),
    contrast({amount: 1.14}),
    whiteBalance({temperature: 0.22, tint: 0.03}),
    tint({color: '#7A4A24', amount: 0.1}),
    vignette({amount: 0.55, radius: 0.66, feather: 0.6}),
  ],
  C: [
    exposure({stops: -0.12}),
    shadowsHighlights({shadows: -0.06, highlights: -0.25}),
    contrast({amount: 1.08}),
    whiteBalance({temperature: 0.1}),
    vibrance({amount: 0.1}),
    vignette({amount: 0.32, radius: 0.75, feather: 0.55}),
  ],
};
// Dipakai di video final: B, sedikit lebih hangat
export const GRADE = [
  exposure({stops: -0.25}),
  shadowsHighlights({shadows: -0.1, highlights: -0.35}),
  contrast({amount: 1.12}),
  whiteBalance({temperature: 0.26, tint: 0.03}),
  tint({color: '#7A4A24', amount: 0.08}),
  vibrance({amount: 0.06}),
  vignette({amount: 0.5, radius: 0.68, feather: 0.6}),
];
