import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import React from "react";
import { COLORS } from "../constants";

export const Background: React.FC<{
  primaryColor?: string;
  secondaryColor?: string;
  seed?: number;
}> = ({ primaryColor = COLORS.anthropic, secondaryColor = COLORS.openai, seed = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const g1 = Math.sin(t * 0.3 + seed) * 0.5 + 0.5;
  const g2 = Math.sin(t * 0.25 + seed + 1.2) * 0.5 + 0.5;

  const wave1 = Array.from({ length: 24 }, (_, i) => {
    const x = (i / 23) * 1920;
    const y = 540 + Math.sin(i * 0.4 + t * 0.6) * 70 + Math.sin(i * 0.7 + t * 0.9) * 35;
    return `${x},${y}`;
  }).join(" ");

  const wave2 = Array.from({ length: 24 }, (_, i) => {
    const x = (i / 23) * 1920;
    const y = 540 + Math.sin(i * 0.5 + t * 0.5 + 1) * 55 + Math.sin(i * 0.3 + t * 0.8) * 28;
    return `${x},${y}`;
  }).join(" ");

  // パーティクル
  const particles = Array.from({ length: 35 }, (_, i) => ({
    x: ((Math.sin(i * 7.3 + t * 0.15) * 0.5 + 0.5 + i * 0.028) % 1) * 1920,
    y: ((Math.cos(i * 5.1 + t * 0.12) * 0.5 + 0.5) % 1) * 1080,
    r: (Math.sin(i * 3.7) * 0.5 + 0.5) * 2.5 + 0.5,
    o: (Math.sin(t * 0.8 + i * 1.1) * 0.5 + 0.5) * 0.3,
    c: i % 3 === 0 ? primaryColor : i % 3 === 1 ? secondaryColor : COLORS.accent,
  }));

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <svg style={{ position: "absolute", inset: 0 }} width={1920} height={1080}>
        <defs>
          <radialGradient id={`g1-${seed}`} cx="25%" cy="40%" r="50%">
            <stop offset="0%" stopColor={primaryColor} stopOpacity={0.15 * g1} />
            <stop offset="100%" stopColor={primaryColor} stopOpacity={0} />
          </radialGradient>
          <radialGradient id={`g2-${seed}`} cx="75%" cy="60%" r="50%">
            <stop offset="0%" stopColor={secondaryColor} stopOpacity={0.15 * g2} />
            <stop offset="100%" stopColor={secondaryColor} stopOpacity={0} />
          </radialGradient>
        </defs>
        <rect width={1920} height={1080} fill={`url(#g1-${seed})`} />
        <rect width={1920} height={1080} fill={`url(#g2-${seed})`} />
        {Array.from({ length: 20 }, (_, i) => (
          <line key={`v${i}`} x1={i * 96} y1={0} x2={i * 96} y2={1080}
            stroke="white" strokeWidth={0.4} opacity={0.025} />
        ))}
        {Array.from({ length: 12 }, (_, i) => (
          <line key={`h${i}`} x1={0} y1={i * 90} x2={1920} y2={i * 90}
            stroke="white" strokeWidth={0.4} opacity={0.025} />
        ))}
        <polyline points={wave1} fill="none" stroke={primaryColor} strokeWidth={1.2} opacity={0.2} />
        <polyline points={wave2} fill="none" stroke={secondaryColor} strokeWidth={1.2} opacity={0.2} />
        {particles.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={p.r} fill={p.c} opacity={p.o} />
        ))}
      </svg>
    </AbsoluteFill>
  );
};
