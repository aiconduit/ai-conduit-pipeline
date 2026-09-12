import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring, Easing, Audio, staticFile } from "remotion";
import { loadFont } from "@remotion/google-fonts/NotoSansJP";
import React from "react";
import { COLORS } from "../constants";
import { GrainVignette } from "../components/GrainVignette";
import { Subtitle, CaptionEntry } from "../components/Subtitle";
import { ProgressBar } from "../components/ProgressBar";

const { fontFamily } = loadFont();
const f = (fps: number, s: number) => Math.round(s * fps);

export const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const exitO = interpolate(frame, [durationInFrames - f(fps, 0.5), durationInFrames], [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });

  const q1Sp = spring({ frame: Math.max(0, frame - f(fps, 0.1)), fps, config: { damping: 12 } });
  const q2Sp = spring({ frame: Math.max(0, frame - f(fps, 0.6)), fps, config: { damping: 12 } });
  const q3Sp = spring({ frame: Math.max(0, frame - f(fps, 1.2)), fps, config: { damping: 12 } });

  const captions: CaptionEntry[] = [
    { startFrame: f(fps, 0.1), endFrame: f(fps, 4), text: "2社のAI企業が世界を変えようとしています。" },
    { startFrame: f(fps, 4.5), endFrame: f(fps, 9), text: "でも、どちらが本当に勝つのか？" },
    { startFrame: f(fps, 10), endFrame: f(fps, 28), text: "数字が全てを語ります。30分で徹底解説。" },
  ];

  // パルスアニメーション
  const pulse = 1 + Math.sin(frame * 0.15) * 0.015;

  return (
    <AbsoluteFill style={{ opacity: exitO, background: COLORS.bg }}>
      {/* 動的背景 */}
      <AbsoluteFill>
        <svg width="100%" height="100%" style={{ position: "absolute" }}>
          <defs>
            <radialGradient id="hg1" cx="30%" cy="50%" r="60%">
              <stop offset="0%" stopColor={COLORS.anthropic} stopOpacity={0.2} />
              <stop offset="100%" stopColor={COLORS.anthropic} stopOpacity={0} />
            </radialGradient>
            <radialGradient id="hg2" cx="70%" cy="50%" r="60%">
              <stop offset="0%" stopColor={COLORS.openai} stopOpacity={0.2} />
              <stop offset="100%" stopColor={COLORS.openai} stopOpacity={0} />
            </radialGradient>
          </defs>
          <rect width="100%" height="100%" fill="url(#hg1)" />
          <rect width="100%" height="100%" fill="url(#hg2)" />
          {/* 中央の分割線 */}
          <line x1="960" y1="0" x2="960" y2="1080" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
        </svg>
      </AbsoluteFill>

      {/* メインコンテンツ */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 32 }}>
        {/* 疑問文1 */}
        <div style={{
          opacity: interpolate(q1Sp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(q1Sp, [0, 1], [-40, 0])}px)`,
          fontSize: 52, fontWeight: 900, color: "#fff", fontFamily, textAlign: "center",
          textShadow: "0 0 40px rgba(255,255,255,0.3)",
        }}>
          世界No.1 AIは<span style={{ color: COLORS.anthropic }}>Anthropic</span>か
        </div>

        {/* VS */}
        <div style={{
          opacity: interpolate(q2Sp, [0, 1], [0, 1]),
          fontSize: 32, color: COLORS.textDim, fontFamily, letterSpacing: 8,
        }}>それとも</div>

        {/* 疑問文2 */}
        <div style={{
          opacity: interpolate(q2Sp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(q2Sp, [0, 1], [40, 0])}px)`,
          fontSize: 52, fontWeight: 900, color: "#fff", fontFamily, textAlign: "center",
        }}>
          <span style={{ color: COLORS.openai }}>OpenAI</span>か？
        </div>

        {/* 数字 */}
        <div style={{
          opacity: interpolate(q3Sp, [0, 1], [0, 1]),
          transform: `scale(${interpolate(q3Sp, [0, 1], [0.8, 1]) * pulse})`,
          display: "flex", gap: 48, marginTop: 20,
        }}>
          {[
            { label: "Anthropic 時価総額", value: "$965B", color: COLORS.anthropic },
            { label: "OpenAI 時価総額", value: "$852B", color: COLORS.openai },
          ].map((stat, i) => (
            <div key={i} style={{
              textAlign: "center", padding: "20px 36px",
              background: `${stat.color}10`, border: `1px solid ${stat.color}30`,
              borderRadius: 16,
            }}>
              <div style={{ fontSize: 42, fontWeight: 900, color: stat.color, fontFamily }}>{stat.value}</div>
              <div style={{ fontSize: 14, color: COLORS.textMuted, fontFamily, marginTop: 6 }}>{stat.label}</div>
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
