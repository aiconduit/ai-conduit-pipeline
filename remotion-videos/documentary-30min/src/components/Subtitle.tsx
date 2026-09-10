import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import React from "react";
import { loadFont } from "@remotion/google-fonts/NotoSansJP";

const { fontFamily } = loadFont();

export interface CaptionEntry {
  startFrame: number;
  endFrame: number;
  text: string;
}

export const Subtitle: React.FC<{ captions: CaptionEntry[] }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const active = captions.find(c => frame >= c.startFrame && frame < c.endFrame);
  if (!active) return null;

  const fadeIn = interpolate(frame - active.startFrame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(active.endFrame - frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{ pointerEvents: "none", zIndex: 90 }}>
      <div style={{
        position: "absolute", bottom: 60,
        left: "8%", right: "8%", textAlign: "center", opacity,
      }}>
        <div style={{
          display: "inline-block",
          background: "rgba(0,0,0,0.78)",
          backdropFilter: "blur(8px)",
          borderRadius: 10, padding: "12px 28px",
          fontSize: 34, fontWeight: 400, color: "#fff",
          fontFamily,
          lineHeight: 1.55, maxWidth: "85%",
          textShadow: "0 2px 8px rgba(0,0,0,0.8)",
        }}>
          {active.text}
        </div>
      </div>
    </AbsoluteFill>
  );
};
