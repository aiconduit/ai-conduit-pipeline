import { Composition } from "remotion";
import { DocumentaryPart2 } from "./MainPart2";
import { VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import React from "react";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;
const totalFrames =
  f(SECTION_DURATION.s09_models_gpt) + f(SECTION_DURATION.s10_benchmark) +
  f(SECTION_DURATION.s11_revenue_anthropic) + f(SECTION_DURATION.s12_revenue_openai) +
  f(SECTION_DURATION.s13_funding) + f(SECTION_DURATION.s14_ipo_race) +
  f(SECTION_DURATION.s15_enterprise) + f(SECTION_DURATION.s16_consumer) - T * 7;

export const RemotionRoot: React.FC = () => (
  <Composition id="DocumentaryPart2" component={DocumentaryPart2}
    durationInFrames={totalFrames} fps={VIDEO_FPS} width={VIDEO_WIDTH} height={VIDEO_HEIGHT} />
);
