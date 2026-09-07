import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Sequence, Easing,
} from "remotion";
import React from "react";
import { COLORS, EASING } from "../constants";
import { Background } from "../components/Background";
import { GrainVignette } from "../components/GrainVignette";
import { Subtitle, CaptionEntry } from "../components/Subtitle";

const f = (fps: number, s: number) => Math.round(s * fps);

export const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  // スプリング (원則1)
  const titleASp = spring({frame: Math.max(0, frame - f(fps,0.3)), fps, config:{damping:12}});
  const titleOSp = spring({frame: Math.max(0, frame - f(fps,0.6)), fps, config:{damping:12}});
  const vsSp = spring({frame: Math.max(0, frame - f(fps,0.9)), fps, config:{damping:10}});
  const lineSp = spring({frame: Math.max(0, frame - f(fps,1.1)), fps, config:{damping:14}});
  const subSp = spring({frame: Math.max(0, frame - f(fps,1.3)), fps, config:{damping:14}});

  // 退場
  const exitStart = durationInFrames - f(fps, 0.7);
  const exitO = interpolate(frame, [exitStart, durationInFrames], [1, 0],
    {extrapolateLeft:"clamp", extrapolateRight:"clamp", easing: Easing.in(Easing.cubic)});

  // 呼吸 (原則6)
  const t = frame / fps;
  const breathA = 1 + Math.sin(t * 1.2) * 0.008;
  const breathO = 1 + Math.sin(t * 1.1 + 0.5) * 0.008;
  const vsBreath = 1 + Math.sin(t * 0.8) * 0.015;

  // 字幕データ (フレーム同期)
  const captions: CaptionEntry[] = [
    {startFrame: f(fps,0.3), endFrame: f(fps,3), text: "2026年、AIの世界を制する2つの巨人が存在します。"},
    {startFrame: f(fps,3.5), endFrame: f(fps,6.5), text: "OpenAI、そしてAnthropicです。"},
    {startFrame: f(fps,7), endFrame: f(fps,10.5), text: "この動画では2社の戦略を徹底比較します。"},
  ];

  return (
    <AbsoluteFill style={{opacity: exitO}}>
      <Background seed={0} />

      {/* メインタイトル */}
      <AbsoluteFill style={{justifyContent:"center", alignItems:"center", flexDirection:"column"}}>
        <div style={{display:"flex", alignItems:"center", gap:80, marginBottom:40}}>
          {/* Anthropic */}
          <div style={{
            opacity: titleASp,
            transform: `translateX(${interpolate(titleASp,[0,1],[-80,0])}px) scale(${titleASp*0.15+0.85})`,
            textAlign:"center",
          }}>
            <div style={{
              fontSize:96, fontWeight:900, color:COLORS.anthropic,
              fontFamily:"Inter, sans-serif", letterSpacing:-4, lineHeight:1,
              textShadow:`0 0 80px ${COLORS.anthropic}60`,
              transform:`scale(${breathA})`,
            }}>Anthropic</div>
            <div style={{
              opacity: interpolate(subSp,[0,1],[0,1]),
              fontSize:22, color:COLORS.textMuted,
              fontFamily:"Inter, sans-serif", letterSpacing:3, marginTop:10,
            }}>Claude Fable 5.1</div>
          </div>

          {/* VS */}
          <div style={{
            opacity: interpolate(vsSp,[0,1],[0,1]),
            transform:`scale(${vsBreath})`,
            fontSize:56, fontWeight:900, color:"rgba(255,255,255,0.1)",
            fontFamily:"Inter, sans-serif",
          }}>VS</div>

          {/* OpenAI */}
          <div style={{
            opacity: titleOSp,
            transform: `translateX(${interpolate(titleOSp,[0,1],[80,0])}px) scale(${titleOSp*0.15+0.85})`,
            textAlign:"center",
          }}>
            <div style={{
              fontSize:96, fontWeight:900, color:COLORS.openai,
              fontFamily:"Inter, sans-serif", letterSpacing:-4, lineHeight:1,
              textShadow:`0 0 80px ${COLORS.openai}60`,
              transform:`scale(${breathO})`,
            }}>OpenAI</div>
            <div style={{
              opacity: interpolate(subSp,[0,1],[0,1]),
              fontSize:22, color:COLORS.textMuted,
              fontFamily:"Inter, sans-serif", letterSpacing:3, marginTop:10,
            }}>GPT-6 Astra</div>
          </div>
        </div>

        {/* ラインアニメーション */}
        <div style={{
          width: interpolate(lineSp,[0,1],[0,900]),
          height:2, borderRadius:1,
          background:`linear-gradient(to right, ${COLORS.anthropic}, rgba(255,255,255,0.1), ${COLORS.openai})`,
          marginBottom:36,
        }} />

        {/* サブタイトル */}
        <div style={{
          opacity: interpolate(subSp,[0,1],[0,1]),
          transform:`translateY(${interpolate(subSp,[0,1],[20,0])}px)`,
          fontSize:24, fontWeight:300, color:COLORS.textMuted,
          fontFamily:"Inter, sans-serif", letterSpacing:8, textTransform:"uppercase",
        }}>AI最強2社の戦略比較</div>
      </AbsoluteFill>

      {/* 字幕 */}
      <Subtitle captions={captions} />
      <GrainVignette />
    </AbsoluteFill>
  );
};
