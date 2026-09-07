import { Composition } from "remotion";
import { DocumentaryMain } from "./Main";
import { VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import React from "react";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const totalDuration =
  f(SECTION_DURATION.intro) +
  f(SECTION_DURATION.origin_openai) +
  f(SECTION_DURATION.revenue) +
  f(SECTION_DURATION.conclusion) -
  TRANSITION_FRAMES * 3; // 3トランジション分

export const RemotionRoot: React.FC = () => (
  <Composition
    id="DocumentaryTest"
    component={DocumentaryMain}
    durationInFrames={totalDuration}
    fps={VIDEO_FPS}
    width={VIDEO_WIDTH}
    height={VIDEO_HEIGHT}
  />
);
