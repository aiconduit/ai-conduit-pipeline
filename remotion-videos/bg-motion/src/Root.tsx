import {Composition} from 'remotion';
import {MotionBackground} from './Background';
import React from 'react';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="MotionBackground"
    component={MotionBackground}
    durationInFrames={900}
    fps={30}
    width={1920}
    height={1080}
  />
);
