import {Composition} from 'remotion';
import {Podcast} from './Podcast';
import data from './data.json';
export const Root = () => (
  <Composition id="Podcast" component={Podcast} durationInFrames={Math.round(data.total * 30)} fps={30}
    width={(data as {format?: string}).format === 'lanskap' ? 1920 : 1080} height={(data as {format?: string}).format === 'lanskap' ? 1080 : 1920} />
);
