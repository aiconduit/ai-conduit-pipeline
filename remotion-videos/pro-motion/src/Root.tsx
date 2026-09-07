import {Composition} from 'remotion';
import {ProMotion} from './ProMotion';
import React from 'react';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="ProMotion"
    component={ProMotion}
    durationInFrames={900}
    fps={30}
    width={1920}
    height={1080}
  />
);
