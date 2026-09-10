import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Sequence, Easing,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/NotoSansJP";
import React from "react";
import { COLORS, EASING } from "../constants";
import { Background } from "../components/Background";
import { GrainVignette } from "../components/GrainVignette";
import { Subtitle, CaptionEntry } from "../components/Subtitle";
import { ProgressBar } from "../components/ProgressBar";

const { fontFamily } = loadFont();
const f = (fps: number, s: number) => Math.round(s * fps);

export const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  const titleA = spring({ frame: Math.max(0, frame - f(fps, 0.3)), fps, config: { damping: 12 } });
  const titleO = spring({ frame: Math.max(0, frame - f(fps, 0.6)), fps, config: { damping: 12 } });
  const vsSp = spring({ frame: Math.max(0, frame - f(fps, 0.9)), fps, config: { damping: 10 } });
  const lineSp = spring({ frame: Math.max(0, frame - f(fps, 1.1)), fps, config: { damping: 14 } });
  const subSp = spring({ frame: Math.max(0, frame - f(fps, 1.3)), fps, config: { damping: 14 } });

  const exitO = interpolate(frame, [durationInFrames - f(fps, 0.7), durationInFrames], [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });

  const breathA = 1 + Math.sin(t * 1.2) * 0.008;
  const breathO = 1 + Math.sin(t * 1.1 + 0.5) * 0.008;
  const vsBreath = 1 + Math.sin(t * 0.8) * 0.015;

  const captions: CaptionEntry[] = [
    { startFrame: f(fps, 0.3), endFrame: f(fps, 3.5), text: "2026年、AIの世界を制する2つの巨人が存在します。" },
    { startFrame: f(fps, 4.0), endFrame: f(fps, 7.0), text: "OpenAI、そしてAnthropicです。" },
    { startFrame: f(fps, 7.5), endFrame: f(fps, 11.5), text: "2社合計で時価総額1兆8千億ドル。AI最強2社の戦略を徹底比較します。" },
  ];

  // 統計データ（フェードイン）
  const statsSp = spring({ frame: Math.max(0, frame - f(fps, 2.0)), fps, config: { damping: 12 } });

  return (
    <AbsoluteFill style={{ opacity: exitO }}>
      <Background primaryColor={COLORS.anthropic} secondaryColor={COLORS.openai} seed={0} />

      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
        {/* メインタイトル */}
        <div style={{ display: "flex", alignItems: "center", gap: 80, marginBottom: 40 }}>
          {/* Anthropic */}
          <div style={{
            opacity: titleA,
            transform: `translateX(${interpolate(titleA, [0, 1], [-80, 0])}px) scale(${titleA * 0.15 + 0.85})`,
            textAlign: "center",
          }}>
            <div style={{
              fontSize: 96, fontWeight: 900, color: COLORS.anthropic,
              fontFamily, letterSpacing: -4, lineHeight: 1,
              textShadow: `0 0 80px ${COLORS.anthropic}60`,
              transform: `scale(${breathA})`,
            }}>Anthropic</div>
            <div style={{
              opacity: interpolate(subSp, [0, 1], [0, 1]),
              fontSize: 20, color: COLORS.textMuted, fontFamily,
              letterSpacing: 2, marginTop: 10,
            }}>Claude Fable 5.1 · ARR $65B</div>
          </div>

          {/* VS */}
          <div style={{
            opacity: interpolate(vsSp, [0, 1], [0, 1]),
            transform: `scale(${vsBreath})`,
            fontSize: 56, fontWeight: 900, color: "rgba(255,255,255,0.1)", fontFamily,
          }}>VS</div>

          {/* OpenAI */}
          <div style={{
            opacity: titleO,
            transform: `translateX(${interpolate(titleO, [0, 1], [80, 0])}px) scale(${titleO * 0.15 + 0.85})`,
            textAlign: "center",
          }}>
            <div style={{
              fontSize: 96, fontWeight: 900, color: COLORS.openai,
              fontFamily, letterSpacing: -4, lineHeight: 1,
              textShadow: `0 0 80px ${COLORS.openai}60`,
              transform: `scale(${breathO})`,
            }}>OpenAI</div>
            <div style={{
              opacity: interpolate(subSp, [0, 1], [0, 1]),
              fontSize: 20, color: COLORS.textMuted, fontFamily,
              letterSpacing: 2, marginTop: 10,
            }}>GPT-6 Astra · ARR $40B</div>
          </div>
        </div>

        {/* ライン */}
        <div style={{
          width: interpolate(lineSp, [0, 1], [0, 900]),
          height: 2, borderRadius: 1,
          background: `linear-gradient(to right, ${COLORS.anthropic}, rgba(255,255,255,0.1), ${COLORS.openai})`,
          marginBottom: 36,
        }} />

        {/* サブタイトル */}
        <div style={{
          opacity: interpolate(subSp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(subSp, [0, 1], [20, 0])}px)`,
          fontSize: 22, fontWeight: 300, color: COLORS.textMuted,
          fontFamily, letterSpacing: 8, textTransform: "uppercase",
        }}>AI最強2社の戦略比較 · 2026年版</div>

        {/* 統計カード */}
        <div style={{
          opacity: interpolate(statsSp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(statsSp, [0, 1], [30, 0])}px)`,
          display: "flex", gap: 32, marginTop: 48,
        }}>
          {[
            { label: "時価総額", a: "$965B", o: "$852B" },
            { label: "ARR", a: "$65B", o: "$40B" },
            { label: "ユーザー", a: "企業80%", o: "9億人" },
          ].map((stat, i) => (
            <div key={i} style={{
              padding: "16px 28px", borderRadius: 12,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              textAlign: "center",
            }}>
              <div style={{ fontSize: 13, color: COLORS.textDim, fontFamily, letterSpacing: 4, marginBottom: 10 }}>
                {stat.label}
              </div>
              <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
                <span style={{ fontSize: 22, fontWeight: 700, color: COLORS.anthropic, fontFamily }}>{stat.a}</span>
                <span style={{ fontSize: 14, color: COLORS.textDim, fontFamily }}>vs</span>
                <span style={{ fontSize: 22, fontWeight: 700, color: COLORS.openai, fontFamily }}>{stat.o}</span>
              </div>
            </div>
          ))}
        </div>
      </AbsoluteFill>

      <Subtitle captions={captions} />
      <GrainVignette />
      <ProgressBar />
    </AbsoluteFill>
  );
};
