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
import { ProgressBar } from "../components/ProgressBar";

const { fontFamily } = loadFont();
const f = (fps: number, s: number) => Math.round(s * fps);

export const ConclusionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  const exitO = interpolate(frame, [durationInFrames - f(fps, 0.7), durationInFrames], [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });

  const titleSp = spring({ frame: Math.max(0, frame - f(fps, 0.3)), fps, config: { damping: 12 } });
  const breath = 1 + Math.sin(t * 0.6) * 0.004;

  const captions: CaptionEntry[] = [
    { startFrame: f(fps, 0.5), endFrame: f(fps, 4), text: "AnthropicとOpenAI。どちらが勝つのか。" },
    { startFrame: f(fps, 4.5), endFrame: f(fps, 8), text: "答えは「どちらも勝者になり得る」です。" },
    { startFrame: f(fps, 8.5), endFrame: f(fps, 13), text: "OpenAIは9億人ユーザーとMicrosoftとの連携が強み。" },
    { startFrame: f(fps, 13.5), endFrame: f(fps, 18), text: "AnthropicはARR$65B、初の黒字化、エンタープライズ首位。" },
    { startFrame: f(fps, 18.5), endFrame: f(fps, 23), text: "この競争はテクノロジーの競争であり、哲学の競争でもあります。" },
    { startFrame: f(fps, 23.5), endFrame: f(fps, 27), text: "チャンネル登録とベルアイコンで最新情報をお見逃しなく！" },
  ];

  const verdicts = [
    { team: "Anthropic", color: COLORS.anthropic, points: ["ARR $65B（首位）", "初の黒字化", "エンタープライズ80%", "安全性哲学"] },
    { team: "OpenAI", color: COLORS.openai, points: ["9億人ユーザー", "ブランド力No.1", "マルチモーダル", "Microsoft連携"] },
  ];

  return (
    <AbsoluteFill style={{ opacity: exitO }}>
      <Background primaryColor={COLORS.accent} secondaryColor={COLORS.gold} seed={11} />

      <AbsoluteFill style={{ padding: "60px 140px", justifyContent: "center" }}>
        <div style={{
          opacity: interpolate(titleSp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleSp, [0, 1], [30, 0])}px) scale(${breath})`,
          textAlign: "center", marginBottom: 48,
        }}>
          <div style={{ fontSize: 13, color: COLORS.textDim, letterSpacing: 7, textTransform: "uppercase", fontFamily, marginBottom: 12 }}>
            VERDICT · 2026
          </div>
          <div style={{ fontSize: 72, fontWeight: 900, color: "#fff", fontFamily, letterSpacing: -4 }}>
            まとめ
          </div>
          <div style={{
            width: interpolate(titleSp, [0, 1], [0, 400]), height: 3, margin: "16px auto 0",
            background: `linear-gradient(to right, ${COLORS.anthropic}, ${COLORS.openai})`,
            borderRadius: 2,
          }} />
        </div>

        <div style={{ display: "flex", gap: 40 }}>
          {verdicts.map((v, vi) => {
            const vSp = spring({ frame: Math.max(0, frame - f(fps, 0.6 + vi * 0.3)), fps, config: { damping: 12 } });
            return (
              <div key={vi} style={{
                flex: 1, padding: "28px 32px",
                background: `${v.color}08`,
                border: `1px solid ${v.color}30`, borderRadius: 16,
                opacity: interpolate(vSp, [0, 1], [0, 1]),
                transform: `translateY(${interpolate(vSp, [0, 1], [30, 0])}px)`,
              }}>
                <div style={{
                  fontSize: 32, fontWeight: 900, color: v.color,
                  fontFamily, marginBottom: 20,
                  textShadow: `0 0 30px ${v.color}60`,
                }}>{v.team}</div>
                {v.points.map((p, pi) => {
                  const pSp = spring({ frame: Math.max(0, frame - f(fps, 0.8 + vi * 0.3 + pi * 0.1)), fps, config: { damping: 14 } });
                  return (
                    <div key={pi} style={{
                      display: "flex", alignItems: "center", gap: 12, marginBottom: 14,
                      opacity: interpolate(pSp, [0, 1], [0, 1]),
                      transform: `translateX(${interpolate(pSp, [0, 1], [-20, 0])}px)`,
                    }}>
                      <div style={{ width: 6, height: 6, borderRadius: "50%", background: v.color, flexShrink: 0 }} />
                      <span style={{ fontSize: 22, color: COLORS.text, fontFamily, fontWeight: 300 }}>{p}</span>
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>

        {/* CTAバッジ */}
        {(() => {
          const sp = spring({ frame: Math.max(0, frame - f(fps, 2.0)), fps, config: { damping: 12 } });
          return (
            <div style={{
              opacity: interpolate(sp, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(sp, [0, 1], [20, 0])}px)`,
              marginTop: 36, textAlign: "center",
              padding: "20px 32px",
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.1)", borderRadius: 16,
            }}>
              <span style={{
                fontSize: 24, color: COLORS.textMuted, fontFamily,
              }}>👍 いいねと保存 · 🔔 チャンネル登録 · 💬 コメントで教えてください</span>
            </div>
          );
        })()}
      </AbsoluteFill>

      <Subtitle captions={captions} />
      <GrainVignette />
      <ProgressBar />
    </AbsoluteFill>
  );
};
