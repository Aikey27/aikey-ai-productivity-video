import React from 'react';
import {Composition} from 'remotion';
import {Video} from './video';
import scenes from './scenes.json';

export const Root: React.FC = () => {
  const duration = Math.ceil(Math.max(...scenes.scenes.map((scene) => scene.end)) * 30);
  return (
    <Composition
      id="Video"
      component={Video}
      durationInFrames={duration}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};

