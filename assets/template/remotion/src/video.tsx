import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import data from './scenes.json';

type SceneData = (typeof data.scenes)[number];

const Grid: React.FC = () => (
  <AbsoluteFill
    style={{
      opacity: 0.13,
      backgroundImage:
        'linear-gradient(rgba(51,230,212,.2) 1px, transparent 1px), linear-gradient(90deg, rgba(51,230,212,.2) 1px, transparent 1px)',
      backgroundSize: '72px 72px',
    }}
  />
);

const Scene: React.FC<{scene: SceneData; index: number}> = ({scene, index}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 16, stiffness: 95}});
  const sweep = interpolate(frame, [0, 70], [-240, 980], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const pulse = 0.55 + Math.sin(frame / 13) * 0.16;
  return (
    <AbsoluteFill
      style={{
        padding: '168px 94px 150px',
        color: '#F7FBFF',
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif',
      }}
    >
      <div style={{fontSize: 30, letterSpacing: 5, color: '#33E6D4', fontWeight: 750}}>
        {scene.kicker}
      </div>
      <div
        style={{
          marginTop: 42,
          fontSize: scene.kind === 'skill' ? 88 : 76,
          fontWeight: 900,
          lineHeight: 1.18,
          whiteSpace: 'pre-line',
          transform: `translateY(${(1 - enter) * 46}px) scale(${0.93 + enter * 0.07})`,
          opacity: enter,
          textShadow: `0 0 34px rgba(51,230,212,${pulse})`,
        }}
      >
        {scene.headline}
      </div>
      <div
        style={{
          marginTop: 52,
          width: 820,
          border: '1px solid rgba(51,230,212,.48)',
          borderRadius: 30,
          background: 'rgba(4,14,29,.72)',
          padding: '38px 42px',
          fontSize: 38,
          lineHeight: 1.55,
          color: '#D8E8F5',
          boxShadow: '0 28px 80px rgba(0,0,0,.38)',
          opacity: interpolate(frame, [10, 28], [0, 1], {extrapolateRight: 'clamp'}),
        }}
      >
        {scene.body}
      </div>
      <div style={{position: 'absolute', left: 94, right: 94, bottom: 126, height: 7, borderRadius: 99, background: 'rgba(255,255,255,.12)'}}>
        <div style={{height: '100%', width: `${Math.min(100, (frame / Math.max(1, (scene.end - scene.start) * fps)) * 100)}%`, background: '#33E6D4', borderRadius: 99}} />
      </div>
      <div style={{position: 'absolute', right: 94, top: 162, fontSize: 25, color: 'rgba(255,255,255,.52)'}}>
        {String(index + 1).padStart(2, '0')} / {String(data.scenes.length).padStart(2, '0')}
      </div>
      <div style={{position: 'absolute', top: 0, bottom: 0, left: sweep, width: 180, transform: 'skewX(-18deg)', background: 'linear-gradient(90deg, transparent, rgba(51,230,212,.09), transparent)'}} />
    </AbsoluteFill>
  );
};

export const Video: React.FC = () => (
  <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 38%, #123C52 0%, #06111F 48%, #020711 100%)'}}>
    <Grid />
    <Audio src={staticFile('narration.wav')} />
    {data.scenes.map((scene, index) => (
      <Sequence
        key={`${scene.start}-${scene.headline}`}
        from={Math.round(scene.start * 30)}
        durationInFrames={Math.round((scene.end - scene.start) * 30)}
      >
        <Scene scene={scene} index={index} />
      </Sequence>
    ))}
  </AbsoluteFill>
);

