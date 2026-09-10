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

// アニメーションするバーグラフ
const AnimBar: React.FC<{
  label: string; value: number; maxVal: number; color: string;
  unit: string; frame: number; fps: number; delay: number;
}> = ({ label, value, maxVal, color, unit, frame, fps, delay }) => {
  const sp = spring({ frame: Math.max(0, frame - f(fps, delay)), fps, config: { damping: 10 } });
  const t = frame / fps;
  const breath = 1 + Math.sin(t * 1.1 + delay) * 0.006;
  const pct = interpolate(sp, [0, 1], [0, (value / maxVal) * 100]);
  const numO = interpolate(sp, [0.5, 1], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div style={{ marginBottom: 36, transform: `scale(${breath})` }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12, alignItems: "baseline" }}>
        <span style={{ fontSize: 22, color: COLORS.textMuted, fontFamily }}>{label}</span>
        <span style={{
          opacity: numO, fontSize: 40, fontWeight: 900, color, fontFamily,
          textShadow: `0 0 24px ${color}70`,
        }}>{unit}{value}B</span>
      </div>
      <div style={{ height: 14, background: "rgba(255,255,255,0.06)", borderRadius: 7, overflow: "hidden" }}>
        <div style={{
          width: `${pct}%`, height: "100%", borderRadius: 7,
          background: `linear-gradient(to right, ${color}, ${color}88)`,
          boxShadow: `0 0 24px ${color}60`,
        }} />
      </div>
    </div>
  );
};

// 成長タイムライン
const GrowthTimeline: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const milestones = [
    { date: "2025年1月", value: "$1B", color: COLORS.textDim },
    { date: "2025年7月", value: "$3B", color: COLORS.textMuted },
    { date: "2026年4月", value: "$30B", color: COLORS.anthropic },
    { date: "2026年5月", value: "$47B", color: COLORS.anthropic },
    { date: "2026年7月", value: "$65B", color: COLORS.gold },
  ];

  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 24, marginTop: 32, height: 120 }}>
      {milestones.map((m, i) => {
        const sp = spring({ frame: Math.max(0, frame - f(fps, 0.8 + i * 0.15)), fps, config: { damping: 12 } });
        const h = interpolate(sp, [0, 1], [0, (i + 1) * 20 + 10]);
        return (
          <div key={i} style={{ textAlign: "center", flex: 1 }}>
            <div style={{
              opacity: interpolate(sp, [0.7, 1], [0, 1], { extrapolateRight: "clamp" }),
              fontSize: 14, fontWeight: 700, color: m.color, fontFamily, marginBottom: 6,
            }}>{m.value}</div>
            <div style={{
              height: h, background: `linear-gradient(to top, ${m.color}, ${m.color}44)`,
              borderRadius: "4px 4px 0 0",
              boxShadow: i >= 3 ? `0 0 20px ${m.color}60` : "none",
            }} />
            <div style={{
              opacity: interpolate(sp, [0.5, 1], [0, 1], { extrapolateRight: "clamp" }),
              fontSize: 11, color: COLORS.textDim, fontFamily, marginTop: 6,
            }}>{m.date}</div>
          </div>
        );
      })}
    </div>
  );
};

export const RevenueScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  const exitO = interpolate(frame, [durationInFrames - f(fps, 0.7), durationInFrames], [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
  const titleSp = spring({ frame: Math.max(0, frame - f(fps, 0.2)), fps, config: { damping: 14 } });
  const titleBreath = 1 + Math.sin(t * 0.8) * 0.003;

  const captions: CaptionEntry[] = [
    { startFrame: f(fps, 0.2), endFrame: f(fps, 5), text: "Anthropicの年間収益は19ヶ月で1億ドルから650億ドルへ急成長。" },
    { startFrame: f(fps, 5.5), endFrame: f(fps, 10), text: "ソフトウェア史上最速の成長率です。" },
    { startFrame: f(fps, 10.5), endFrame: f(fps, 15), text: "OpenAIも400億ドルと急成長していますが、Anthropicが首位です。" },
    { startFrame: f(fps, 15.5), endFrame: f(fps, 20), text: "しかしOpenAIは2025年に209億ドルの損失を計上。" },
    { startFrame: f(fps, 20.5), endFrame: f(fps, 25), text: "Anthropicは2026年、初の黒字化を達成しました。" },
    { startFrame: f(fps, 25.5), endFrame: f(fps, 29), text: "収益構造の効率性でも、Anthropicが大きく上回っています。" },
  ];

  return (
    <AbsoluteFill style={{ opacity: exitO }}>
      <Background primaryColor={COLORS.anthropic} secondaryColor={COLORS.openai} seed={5} />
      <AbsoluteFill style={{ padding: "60px 140px", justifyContent: "center" }}>
        <div style={{
          opacity: interpolate(titleSp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleSp, [0, 1], [30, 0])}px) scale(${titleBreath})`,
          marginBottom: 50,
        }}>
          <div style={{ fontSize: 13, color: COLORS.textDim, letterSpacing: 7, textTransform: "uppercase", fontFamily, marginBottom: 12 }}>
            Annual Revenue Run-Rate · 2026
          </div>
          <div style={{ fontSize: 60, fontWeight: 900, color: "#fff", fontFamily, letterSpacing: -3 }}>収益比較</div>
          <div style={{
            width: interpolate(titleSp, [0, 1], [0, 280]), height: 3,
            background: `linear-gradient(to right, ${COLORS.anthropic}, transparent)`,
            borderRadius: 2, marginTop: 16,
          }} />
        </div>

        <AnimBar label="Anthropic ARR（2026年7月）" value={65} maxVal={80} color={COLORS.anthropic} unit="$" frame={frame} fps={fps} delay={0.4} />
        <AnimBar label="OpenAI ARR（2026年8月）" value={40} maxVal={80} color={COLORS.openai} unit="$" frame={frame} fps={fps} delay={0.6} />

        <GrowthTimeline frame={frame} fps={fps} />

        {/* 黒字化バッジ */}
        {(() => {
          const sp = spring({ frame: Math.max(0, frame - f(fps, 1.8)), fps, config: { damping: 12 } });
          return (
            <div style={{
              opacity: interpolate(sp, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(sp, [0, 1], [20, 0])}px)`,
              marginTop: 24, padding: "16px 24px",
              background: `${COLORS.anthropic}10`,
              border: `1px solid ${COLORS.anthropic}30`, borderRadius: 14,
              display: "flex", gap: 24, alignItems: "center",
            }}>
              <span style={{ fontSize: 18, color: COLORS.anthropic, fontFamily, fontWeight: 700 }}>
                🏆 Anthropic: 2026年初の黒字化達成
              </span>
              <span style={{ fontSize: 16, color: COLORS.textMuted, fontFamily }}>
                vs OpenAI: 2025年に$20.9B損失
              </span>
            </div>
          );
        })()}
      </AbsoluteFill>
      <LowerThird title="収益比較" subtitle="ARR & 利益率" color={COLORS.anthropic} showFrom={f(fps, 0.2)} showUntil={durationInFrames - f(fps, 1)} />
      <Subtitle captions={captions} />
      <GrainVignette />
      <ProgressBar />
    </AbsoluteFill>
  );
};
