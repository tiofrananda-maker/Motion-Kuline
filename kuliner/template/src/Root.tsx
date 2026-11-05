import {Composition} from 'remotion';
import {Kuliner} from './Kuliner';
import data from './data.json';
export const Root = () => (
  <Composition id="Kuliner" component={Kuliner} durationInFrames={Math.round(data.total * 30)} fps={30} width={1080} height={1920} />
);
