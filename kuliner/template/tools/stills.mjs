// Cek tampilan cepat: node tools/stills.mjs <folderOutput> frame1 frame2 ...  (bundle sekali, banyak frame)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition, openBrowser} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
const [outDir, ...frames] = process.argv.slice(2);
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const browserExecutable = process.env.REMOTION_BROWSER ?? null;
const browser = await openBrowser('chrome', {browserExecutable, chromiumOptions: {gl: 'angle'}});
const composition = await selectComposition({serveUrl, id: 'Kuliner', puppeteerInstance: browser});
for (const fr of frames) {
  const output = path.join(outDir, `f_${fr}.jpg`);
  await renderStill({composition, serveUrl, frame: Number(fr), output, imageFormat: 'jpeg', jpegQuality: 85, puppeteerInstance: browser});
  console.log(output);
}
await browser.close({silent: true});
