import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import React from "react";
import { COLORS } from "../constants";

export const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const pct = (frame / durationInFrames) * 100;

  return (
    <AbsoluteFill style={{ pointerEvents: "none", zIndex: 80 }}>
      <div style={{
        position: "absolute", bottom: 0, left: 0, right: 0, height: 3,
        background: "rgba(255,255,255,0.06)",
      }}>
        <div style={{
          width: `${pct}%`, height: "100%",
          background: `linear-gradient(to right, ${COLORS.anthropic}, ${COLORS.openai})`,
        }} />
      </div>
    </AbsoluteFill>
  );
};
