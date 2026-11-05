import {Composition} from 'remotion';
import {Resep} from './Resep';
import data from './data.json';
export const Root = () => (
  <Composition id="Resep" component={Resep} durationInFrames={Math.round(data.total * 30)} fps={30} width={1080} height={1920} />
);
