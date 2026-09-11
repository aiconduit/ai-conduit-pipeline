import { Composition } from "remotion";
import { DocumentaryPart3 } from "./MainPart3";
import { VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import React from "react";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const totalFrames =
  f(SECTION_DURATION.s09_safety) +
  f(SECTION_DURATION.s10_partners) +
  f(SECTION_DURATION.s11_future) +
  f(SECTION_DURATION.s12_conclusion) -
  T * 3;

export const RemotionRoot: React.FC = () => (
  <Composition
    id="DocumentaryPart3"
    component={DocumentaryPart3}
    durationInFrames={totalFrames}
    fps={VIDEO_FPS}
    width={VIDEO_WIDTH}
    height={VIDEO_HEIGHT}
  />
);
