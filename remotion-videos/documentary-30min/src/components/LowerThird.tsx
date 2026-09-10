import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import React from "react";
import { COLORS } from "../constants";
import { loadFont } from "@remotion/google-fonts/NotoSansJP";

const { fontFamily } = loadFont();

export const LowerThird: React.FC<{
  title: string;
  subtitle?: string;
  color?: string;
  showFrom?: number;
  showUntil?: number;
}> = ({ title, subtitle, color = COLORS.accent, showFrom = 0, showUntil = 999 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame < showFrom || frame > showUntil) return null;

  const sp = spring({ frame: frame - showFrom, fps, config: { damping: 14 } });
  const x = interpolate(sp, [0, 1], [-60, 0]);
  const opacity = interpolate(sp, [0, 1], [0, 1]);

  const fadeOut = frame > showUntil - fps * 0.5
    ? interpolate(frame, [showUntil - fps * 0.5, showUntil], [1, 0], { extrapolateRight: "clamp" })
    : 1;

  return (
    <AbsoluteFill style={{ pointerEvents: "none", zIndex: 85 }}>
      <div style={{
        position: "absolute", bottom: 140, left: 60,
        display: "flex", alignItems: "center", gap: 14,
        opacity: opacity * fadeOut,
        transform: `translateX(${x}px)`,
      }}>
        <div style={{ width: 4, height: subtitle ? 48 : 32, background: color, borderRadius: 2 }} />
        <div>
          <div style={{
            fontSize: 22, fontWeight: 700, color: "#fff",
            fontFamily, letterSpacing: 1,
          }}>{title}</div>
          {subtitle && (
            <div style={{
              fontSize: 15, color: COLORS.textMuted,
              fontFamily, letterSpacing: 2, marginTop: 2,
            }}>{subtitle}</div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
