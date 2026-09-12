import { Composition } from "remotion";
import { Documentary } from "./Main";
import { VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import React from "react";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const totalSecs = Object.values(SECTION_DURATION).reduce((a, b) => a + b, 0);
const nTransitions = Object.keys(SECTION_DURATION).length - 1;
const totalFrames = Math.round(totalSecs * VIDEO_FPS) - nTransitions * TRANSITION_FRAMES;

export const RemotionRoot: React.FC = () => (
  <Composition
    id="DocumentaryTest"
    component={Documentary}
    durationInFrames={totalFrames}
    fps={VIDEO_FPS}
    width={VIDEO_WIDTH}
    height={VIDEO_HEIGHT}
  />
);
