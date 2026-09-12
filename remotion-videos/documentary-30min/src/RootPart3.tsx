import { Composition } from "remotion";
import { DocumentaryPart3 } from "./MainPart3";
import { VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import React from "react";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;
const totalFrames =
  f(SECTION_DURATION.s17_partners_ms) + f(SECTION_DURATION.s18_partners_aws) +
  f(SECTION_DURATION.s19_safety_constitutional) + f(SECTION_DURATION.s20_safety_rlhf) +
  f(SECTION_DURATION.s21_fbi) + f(SECTION_DURATION.s22_future_agi) +
  f(SECTION_DURATION.s23_stargate) + f(SECTION_DURATION.s24_conclusion) - T * 7;

export const RemotionRoot: React.FC = () => (
  <Composition id="DocumentaryPart3" component={DocumentaryPart3}
    durationInFrames={totalFrames} fps={VIDEO_FPS} width={VIDEO_WIDTH} height={VIDEO_HEIGHT} />
);
