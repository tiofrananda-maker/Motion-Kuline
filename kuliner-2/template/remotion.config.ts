import {Config} from '@remotion/cli/config';
// Effects (filter) butuh WebGL
Config.setChromiumOpenGlRenderer('angle');
// Opsional: pakai Chrome tertentu, isi env REMOTION_BROWSER
if (process.env.REMOTION_BROWSER) Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
