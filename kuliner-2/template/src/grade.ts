import {whiteBalance} from '@remotion/effects/white-balance';
import {contrast} from '@remotion/effects/contrast';
import {exposure} from '@remotion/effects/exposure';
import {saturation} from '@remotion/effects/saturation';
import {tint} from '@remotion/effects/tint';
import {shadowsHighlights} from '@remotion/effects/shadows-highlights';

// Grade "resep estetik": terang lembut, hangat keemasan (cahaya jendela sore), kontras rendah,
// bayangan sedikit diangkat (kesan film/krem), sorotan ditahan supaya putih piring tidak pecah.
// Tanpa vignette (referensi rata terang sampai tepi).
export const GRADE = [
  exposure({stops: 0.06}),
  shadowsHighlights({shadows: 0.14, highlights: -0.22}),
  contrast({amount: 0.92}),
  whiteBalance({temperature: 0.16, tint: 0.02}),
  tint({color: '#E9B98C', amount: 0.06}),
  saturation({amount: 0.94}),
];
