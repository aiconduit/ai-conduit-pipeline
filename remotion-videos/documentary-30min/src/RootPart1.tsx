import { Composition } from "remotion";
import { DocumentaryPart1 } from "./MainPart1";
import { VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import React from "react";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;
const totalFrames =
  f(SECTION_DURATION.s01_hook) + f(SECTION_DURATION.s02_intro) +
  f(SECTION_DURATION.s03_openai_birth) + f(SECTION_DURATION.s04_chatgpt) +
  f(SECTION_DURATION.s05_anthropic_birth) + f(SECTION_DURATION.s06_split_reason) +
  f(SECTION_DURATION.s07_safety_vs_growth) + f(SECTION_DURATION.s08_models_claude) - T * 7;

export const RemotionRoot: React.FC = () => (
  <Composition id="DocumentaryPart1" component={DocumentaryPart1}
    durationInFrames={totalFrames} fps={VIDEO_FPS} width={VIDEO_WIDTH} height={VIDEO_HEIGHT} />
);
