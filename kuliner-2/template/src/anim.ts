import {interpolate} from 'remotion';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
// fade linear pendek seperti referensi (tanpa gerak/geser)
export const fade = (frame: number, from: number, len: number) => interpolate(frame, [from, from + len], [0, 1], clamp);
export const fadeOut = (frame: number, end: number, len: number) => interpolate(frame, [end - len, end], [1, 0], clamp);
