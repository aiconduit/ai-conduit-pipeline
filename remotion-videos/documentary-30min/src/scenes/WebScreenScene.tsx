import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring, Easing, Img, staticFile, Audio } from "remotion";
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

export interface WebScreenData {
  title: string;
  subtitle?: string;
  color: string;
  screenshotFile: string;  // public/assets/内のファイル名
  caption: string;         // 画面説明テキスト
  narration: string[];
  audioFile?: string;
  highlights?: { x: number; y: number; w: number; h: number; label: string }[];
}

export const WebScreenScene: React.FC<{ data: WebScreenData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const exitO = interpolate(frame, [durationInFrames - f(fps, 0.5), durationInFrames], [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });

  const titleSp = spring({ frame: Math.max(0, frame - f(fps, 0.2)), fps, config: { damping: 14 } });
  const screenSp = spring({ frame: Math.max(0, frame - f(fps, 0.4)), fps, config: { damping: 12 } });

  const durPerChunk = durationInFrames / Math.max(data.narration.length, 1);
  const captions: CaptionEntry[] = data.narration.map((text, i) => ({
    startFrame: Math.round(i * durPerChunk + f(fps, 0.2)),
    endFrame: Math.round((i + 1) * durPerChunk - f(fps, 0.1)),
    text,
  }));

  return (
    <AbsoluteFill style={ opacity: exitO }>
      <Background primaryColor={data.color} seed={3} />

      {data.audioFile && (
        <Audio src={staticFile(`audio/${data.audioFile}`}) volume={1} />
      )}

      <AbsoluteFill style={ display: "flex", flexDirection: "row", padding: "50px 60px", gap: 40 }>
        {/* 左：タイトルと説明 */}
        <div style={ flex: "0 0 420px", display: "flex", flexDirection: "column", justifyContent: "center" }>
          <div style={
            opacity: interpolate(titleSp, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(titleSp, [0, 1], [-30, 0])})px)`,
          }>
            <div style={ fontSize: 11, color: COLORS.textDim, letterSpacing: 6, textTransform: "uppercase", fontFamily, marginBottom: 10 }>
              実際の画面
            </div>
            <div style={ fontSize: 48, fontWeight: 900, color: "#fff", fontFamily, letterSpacing: -2, lineHeight: 1.1, marginBottom: 16 }>
              {data.title}
            </div>
            <div style={ width: interpolate(titleSp, [0, 1], [0, 200]), height: 3, background: `linear-gradient(to right, ${data.color}, transparent)`, borderRadius: 2, marginBottom: 24 } />
            <div style={ fontSize: 20, color: COLORS.textMuted, fontFamily, lineHeight: 1.7, fontWeight: 300 }>
              {data.caption}
            </div>
          </div>
        </div>

        {/* 右：スクリーンショット */}
        <div style={
          flex: 1,
          opacity: interpolate(screenSp, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(screenSp, [0, 1], [20, 0])})px) scale(${interpolate(screenSp, [0, 1], [0.95, 1])})`,
          borderRadius: 12,
          overflow: "hidden",
          boxShadow: `0 0 60px ${data.color}30, 0 20px 60px rgba(0,0,0,0.5)`,
          border: `1px solid ${data.color}30`,
          position: "relative",
        }>
          {/* ブラウザバー */}
          <div style={ background: "#1a1a2e", padding: "10px 16px", display: "flex", alignItems: "center", gap: 8 }>
            <div style={ width: 10, height: 10, borderRadius: "50%", background: "#ef4444" } />
            <div style={ width: 10, height: 10, borderRadius: "50%", background: "#f59e0b" } />
            <div style={ width: 10, height: 10, borderRadius: "50%", background: "#10b981" } />
            <div style={ flex: 1, background: "rgba(255,255,255,0.08)", borderRadius: 6, padding: "4px 12px", marginLeft: 8, fontSize: 11, color: COLORS.textDim, fontFamily }>
              {data.title.toLowerCase().replace(/\s/g, "")}.com
            </div>
          </div>
          <Img
            src={staticFile(`assets/${data.screenshotFile}`)}
            style={ width: "100%", height: "calc(100% - 38px)", objectFit: "cover", objectPosition: "top" }
          />
          {/* ハイライト */}
          {data.highlights?.map((h, i) => {
            const hSp = spring({ frame: Math.max(0, frame - f(fps, 1.0 + i * 0.3)), fps, config: { damping: 12 } });
            return (
              <div key={i} style={
                position: "absolute",
                left: `${h.x}%`, top: `${h.y + 5}%`,
                width: `${h.w}%`, height: `${h.h}%`,
                border: `2px solid ${data.color}`,
                borderRadius: 6,
                opacity: interpolate(hSp, [0, 1], [0, 1]),
                boxShadow: `0 0 20px ${data.color}60`,
              }>
                <div style={
                  position: "absolute", top: -24, left: 0,
                  background: data.color, borderRadius: "4px 4px 0 0",
                  padding: "2px 8px", fontSize: 11, color: "#000", fontFamily, fontWeight: 700,
                }>{h.label}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>

      <LowerThird title={data.title} subtitle={data.subtitle} color={data.color}
        showFrom={f(fps, 0.2)} showUntil={durationInFrames - f(fps, 0.5)} />
      <Subtitle captions={captions} />
      <GrainVignette />
      <ProgressBar />
    </AbsoluteFill>
  );
};
