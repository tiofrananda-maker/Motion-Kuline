import {interpolate, spring} from 'remotion';
// masuk: ease-out halus 300-500ms, keluar 200-300ms
export const enter = (frame: number, fps: number, delay = 0) =>
  spring({frame: frame - delay, fps, config: {damping: 200, stiffness: 140, mass: 0.6}});
export const fadeOut = (frame: number, dur: number, out = 8) =>
  interpolate(frame, [dur - out, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
export const pop = (frame: number, fps: number, delay = 0) =>
  spring({frame: frame - delay, fps, config: {damping: 12, stiffness: 180, mass: 0.6}});
export const wordIn = (p: number) => ({
  opacity: p,
  filter: `blur(${interpolate(p, [0, 1], [8, 0])}px)`,
  transform: `translateY(${interpolate(p, [0, 1], [12, 0])}px)`,
});
