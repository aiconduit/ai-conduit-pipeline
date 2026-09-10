import { Composition } from "remotion";
import { Documentary } from "./Main";
import { VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SECTION_DURATION } from "./constants";
import React from "react";

const sec = (s: number) => Math.round(s * VIDEO_FPS);
const T_FRAMES = 20; // トランジション

// 総フレーム数を計算
const totalSecs = Object.values(SECTION_DURATION).reduce((a, b) => a + b, 0);
const transitionSecs = (Object.keys(SECTION_DURATION).length - 1) * (T_FRAMES / VIDEO_FPS);
const TOTAL_FRAMES = Math.round((totalSecs - transitionSecs) * VIDEO_FPS);

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="DocumentaryTest"
      component={Documentary}
      durationInFrames={TOTAL_FRAMES}
      fps={VIDEO_FPS}
      width={VIDEO_WIDTH}
      height={VIDEO_HEIGHT}
    />
  );
};
