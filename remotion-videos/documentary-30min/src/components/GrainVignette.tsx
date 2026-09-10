import { AbsoluteFill, useCurrentFrame } from "remotion";
import React from "react";

export const GrainVignette: React.FC<{ opacity?: number }> = ({ opacity = 0.035 }) => {
  const frame = useCurrentFrame();
  const seed = (frame * 7919) % 9973;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", zIndex: 100 }}>
      <div style={{
        position: "absolute", inset: 0,
        background: "radial-gradient(ellipse at 50% 50%, transparent 45%, rgba(0,0,0,0.65) 100%)",
      }} />
      <svg style={{ position: "absolute", inset: 0, opacity }} width="100%" height="100%">
        <filter id={`grain-${frame % 4}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" seed={seed} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#grain-${frame % 4})`} />
      </svg>
    </AbsoluteFill>
  );
};
