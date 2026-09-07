import {Composition} from 'remotion';
import {HybridIntro} from './Intro';
import React from 'react';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HybridIntro"
        component={HybridIntro}
        durationInFrames={330}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
