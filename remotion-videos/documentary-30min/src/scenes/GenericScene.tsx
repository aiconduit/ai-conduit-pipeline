import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Easing,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/NotoSansJP";
import React from "react";
import { COLORS } from "../constants";
import { Background } from "../components/Background";
import { GrainVignette } from "../components/GrainVignette";
import { Subtitle, CaptionEntry } from "../components/Subtitle";
import { LowerThird } from "../components/LowerThird";
import { ProgressBar } from "../components/ProgressBar";

const { fontFamily } = loadFont();
const f = (fps: number, s: number) => Math.round(s * fps);

export interface SceneData {
  title: string;
  subtitle?: string;
  color: string;
  bullets: string[];
  stat?: { label: string; value: string; color: string };
  narration: string[];
  seed?: number;
}

export const GenericScene: React.FC<{ data: SceneData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  const exitO = interpolate(frame, [durationInFrames - f(fps, 0.7), durationInFrames], [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
  const titleSp = spring({ frame: Math.max(0, frame - f(fps, 0.2)), fps, config: { damping: 14 } });
  const breath = 1 + Math.sin(t * 0.7) * 0.003;

  // キャプションをナレーション文から自動生成
  const durPerChunk = durationInFrames / data.narration.length;
  const captions: CaptionEntry[] = data.narration.map((text, i) => ({
    startFrame: Math.round(i * durPerChunk + f(fps, 0.3)),
    endFrame: Math.round((i + 1) * durPerChunk - f(fps, 0.2)),
    text,
  }));

  return (
    <AbsoluteFill style={{ opacity: exitO }}>
      <Background primaryColor={data.color} secondaryColor={data.seed !== undefined && data.seed % 2 === 0 ? COLORS.openai : COLORS.anthropic} seed={data.seed ?? 1} />

      <AbsoluteFill style={{ padding: "60px 140px", justifyContent: "center" }}>
        {/* タイトル */}
        <div style={{
          opacity: interpolate(titleSp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleSp, [0, 1], [30, 0])}px) scale(${breath})`,
          marginBottom: 50,
        }}>
          <div style={{ fontSize: 13, color: COLORS.textDim, letterSpacing: 7, textTransform: "uppercase", fontFamily, marginBottom: 12 }}>
            AI最強2社の戦略比較
          </div>
          <div style={{ fontSize: 64, fontWeight: 900, color: "#fff", fontFamily, letterSpacing: -3, lineHeight: 1 }}>
            {data.title}
          </div>
          <div style={{
            width: interpolate(titleSp, [0, 1], [0, 300]), height: 3,
            background: `linear-gradient(to right, ${data.color}, transparent)`,
            borderRadius: 2, marginTop: 16,
          }} />
        </div>

        {/* 箇条書き */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {data.bullets.map((bullet, i) => {
            const bSp = spring({ frame: Math.max(0, frame - f(fps, 0.5 + i * 0.2)), fps, config: { damping: 14 } });
            return (
              <div key={i} style={{
                opacity: interpolate(bSp, [0, 1], [0, 1]),
                transform: `translateX(${interpolate(bSp, [0, 1], [-40, 0])}px)`,
                display: "flex", alignItems: "flex-start", gap: 16,
              }}>
                <div style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: data.color, marginTop: 12, flexShrink: 0,
                  boxShadow: `0 0 12px ${data.color}`,
                }} />
                <div style={{
                  fontSize: 28, color: COLORS.text, fontFamily, lineHeight: 1.5, fontWeight: 300,
                }}>{bullet}</div>
              </div>
            );
          })}
        </div>

        {/* 統計バッジ */}
        {data.stat && (() => {
          const sp = spring({ frame: Math.max(0, frame - f(fps, 1.5)), fps, config: { damping: 12 } });
          return (
            <div style={{
              opacity: interpolate(sp, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(sp, [0, 1], [20, 0])}px)`,
              marginTop: 36, padding: "20px 32px",
              background: `${data.stat.color}08`,
              border: `1px solid ${data.stat.color}30`, borderRadius: 16,
              display: "inline-flex", alignItems: "center", gap: 20,
            }}>
              <span style={{ fontSize: 48, fontWeight: 900, color: data.stat.color, fontFamily }}>
                {data.stat.value}
              </span>
              <span style={{ fontSize: 20, color: COLORS.textMuted, fontFamily }}>
                {data.stat.label}
              </span>
            </div>
          );
        })()}
      </AbsoluteFill>

      <LowerThird title={data.title} subtitle={data.subtitle} color={data.color}
        showFrom={f(fps, 0.2)} showUntil={durationInFrames - f(fps, 1)} />
      <Subtitle captions={captions} />
      <GrainVignette />
      <ProgressBar />
    </AbsoluteFill>
  );
};
