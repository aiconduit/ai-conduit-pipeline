import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
} from "remotion";
import { TransitionSeries, linearTiming, springTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";
import { wipe } from "@remotion/transitions/wipe";
import React from "react";
import { VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import { IntroScene } from "./scenes/IntroScene";
import { OriginOpenAIScene } from "./scenes/OriginOpenAIScene";
import { RevenueScene } from "./scenes/RevenueScene";
import { ConclusionScene } from "./scenes/ConclusionScene";

const f = (s: number) => Math.round(s * VIDEO_FPS);

// プログレスバー
const ProgressBar: React.FC<{frame: number; total: number}> = ({frame, total}) => (
  <div style={{
    position:"absolute", bottom:0, left:0, right:0, height:3,
    background:"rgba(255,255,255,0.04)", zIndex:200,
  }}>
    <div style={{
      width:`${(frame/total)*100}%`, height:"100%",
      background:"linear-gradient(to right, #a78bfa, #10b981)",
    }}/>
  </div>
);

// ローワーサード（画面下部チャンネル名）
const LowerThird: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  if (frame > f(8) || frame < f(2)) return null;
  return (
    <div style={{
      position:"absolute", bottom:100, left:60,
      display:"flex", alignItems:"center", gap:16, zIndex:150,
    }}>
      <div style={{width:4, height:40, background:"#a78bfa", borderRadius:2}}/>
      <div>
        <div style={{fontSize:18, fontWeight:700, color:"#fff", fontFamily:"Inter,sans-serif", letterSpacing:2}}>
          @AI.Conduit
        </div>
        <div style={{fontSize:13, color:"rgba(255,255,255,0.4)", fontFamily:"Inter,sans-serif", letterSpacing:4}}>
          AI ANALYSIS
        </div>
      </div>
    </div>
  );
};

export const DocumentaryMain: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  return (
    <AbsoluteFill>
      <TransitionSeries>
        {/* イントロ */}
        <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.intro)}>
          <IntroScene />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({durationInFrames: TRANSITION_FRAMES})}
        />

        {/* OpenAI誕生 */}
        <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.origin_openai)}>
          <OriginOpenAIScene />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={slide({direction: "from-right"})}
          timing={springTiming({config: {damping: 200}, durationInFrames: TRANSITION_FRAMES})}
        />

        {/* 収益比較 */}
        <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.revenue)}>
          <RevenueScene />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={wipe({direction: "from-bottom-left"})}
          timing={springTiming({config: {damping: 200}, durationInFrames: TRANSITION_FRAMES})}
        />

        {/* まとめ */}
        <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.conclusion)}>
          <ConclusionScene />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      {/* ローワーサード */}
      <LowerThird frame={frame} fps={fps} />

      {/* プログレスバー */}
      <ProgressBar frame={frame} total={durationInFrames} />
    </AbsoluteFill>
  );
};
