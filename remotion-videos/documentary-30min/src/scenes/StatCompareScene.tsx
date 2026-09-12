import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring, Easing, Audio, staticFile } from "remotion";
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

export interface StatItem {
  label: string;
  anthropic: string;
  openai: string;
  winner?: "anthropic" | "openai" | "tie";
}

export interface StatCompareData {
  title: string;
  subtitle?: string;
  stats: StatItem[];
  narration: string[];
  audioFile?: string;
  seed?: number;
}

export const StatCompareScene: React.FC<{ data: StatCompareData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const exitO = interpolate(frame, [durationInFrames - f(fps, 0.5), durationInFrames], [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });

  const titleSp = spring({ frame: Math.max(0, frame - f(fps, 0.1)), fps, config: { damping: 14 } });

  const durPerChunk = durationInFrames / Math.max(data.narration.length, 1);
  const captions: CaptionEntry[] = data.narration.map((text, i) => ({
    startFrame: Math.round(i * durPerChunk + f(fps, 0.2)),
    endFrame: Math.round((i + 1) * durPerChunk - f(fps, 0.1)),
    text,
  }));

  return (
    <AbsoluteFill style={{ opacity: exitO }}>
      <Background primaryColor={COLORS.anthropic} secondaryColor={COLORS.openai} seed={data.seed ?? 5} />

      {data.audioFile && <Audio src={staticFile(`audio/${data.audioFile}`)} volume={1} />}

      <AbsoluteFill style={{ padding: "50px 80px" }}>
        {/* ヘッダー */}
        <div style={{
          opacity: interpolate(titleSp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleSp, [0, 1], [-20, 0])}px)`,
          marginBottom: 40,
        }}>
          <div style={{ fontSize: 11, color: COLORS.textDim, letterSpacing: 6, fontFamily, marginBottom: 8 }}>DATA COMPARISON · 2026</div>
          <div style={{ fontSize: 54, fontWeight: 900, color: "#fff", fontFamily, letterSpacing: -2 }}>{data.title}</div>
        </div>

        {/* カラムヘッダー */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 20 }}>
          <div style={{ fontSize: 13, color: COLORS.textDim, fontFamily, letterSpacing: 4 }}>指標</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: COLORS.anthropic, fontFamily, textAlign: "center" }}>Anthropic</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: COLORS.openai, fontFamily, textAlign: "center" }}>OpenAI</div>
        </div>
        <div style={{ height: 1, background: "rgba(255,255,255,0.1)", marginBottom: 20 }} />

        {/* データ行 */}
        {data.stats.map((stat, i) => {
          const rowSp = spring({ frame: Math.max(0, frame - f(fps, 0.3 + i * 0.15)), fps, config: { damping: 14 } });
          const winnerColor = stat.winner === "anthropic" ? COLORS.anthropic : stat.winner === "openai" ? COLORS.openai : "transparent";
          return (
            <div key={i} style={{
              display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16,
              marginBottom: 16, padding: "16px 20px", borderRadius: 12,
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.06)",
              opacity: interpolate(rowSp, [0, 1], [0, 1]),
              transform: `translateX(${interpolate(rowSp, [0, 1], [-30, 0])}px)`,
            }}>
              <div style={{ fontSize: 18, color: COLORS.textMuted, fontFamily, alignSelf: "center" }}>{stat.label}</div>
              <div style={{
                fontSize: 26, fontWeight: 700, color: stat.winner === "anthropic" ? COLORS.anthropic : COLORS.text,
                fontFamily, textAlign: "center",
                textShadow: stat.winner === "anthropic" ? `0 0 20px ${COLORS.anthropic}60` : "none",
              }}>
                {stat.anthropic}
                {stat.winner === "anthropic" && <span style={{ fontSize: 14, marginLeft: 6 }}>👑</span>}
              </div>
              <div style={{
                fontSize: 26, fontWeight: 700, color: stat.winner === "openai" ? COLORS.openai : COLORS.text,
                fontFamily, textAlign: "center",
                textShadow: stat.winner === "openai" ? `0 0 20px ${COLORS.openai}60` : "none",
              }}>
                {stat.openai}
                {stat.winner === "openai" && <span style={{ fontSize: 14, marginLeft: 6 }}>👑</span>}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>

      <LowerThird title={data.title} subtitle={data.subtitle} color={COLORS.accent}
        showFrom={f(fps, 0.2)} showUntil={durationInFrames - f(fps, 0.5)} />
      <Subtitle captions={captions} />
      <GrainVignette />
      <ProgressBar />
    </AbsoluteFill>
  );
};
