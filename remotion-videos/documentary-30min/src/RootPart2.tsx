import { Composition } from "remotion";
import { DocumentaryPart2 } from "./MainPart2";
import { VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import React from "react";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const totalFrames =
  f(SECTION_DURATION.s05_models) +
  f(SECTION_DURATION.s06_revenue) +
  f(SECTION_DURATION.s07_funding) +
  f(SECTION_DURATION.s08_business) -
  T * 3;

export const RemotionRoot: React.FC = () => (
  <Composition
    id="DocumentaryPart2"
    component={DocumentaryPart2}
    durationInFrames={totalFrames}
    fps={VIDEO_FPS}
    width={VIDEO_WIDTH}
    height={VIDEO_HEIGHT}
  />
);
