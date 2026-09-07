import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import React from "react";
import { COLORS } from "../constants";

export interface CaptionEntry {
  startFrame: number;
  endFrame: number;
  text: string;
}

export const Subtitle: React.FC<{captions: CaptionEntry[]}> = ({captions}) => {
  const frame = useCurrentFrame();
  const active = captions.find(c => frame >= c.startFrame && frame < c.endFrame);

  if (!active) return null;

  const fadeIn = interpolate(frame - active.startFrame, [0, 8], [0, 1], {extrapolateRight: "clamp"});
  const fadeOut = interpolate(active.endFrame - frame, [0, 8], [0, 1], {extrapolateRight: "clamp"});
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{pointerEvents:"none"}}>
      <div style={{
        position:"absolute",
        bottom:60,
        left:"10%",
        right:"10%",
        textAlign:"center",
        opacity,
      }}>
        <div style={{
          display:"inline-block",
          background:"rgba(0,0,0,0.75)",
          backdropFilter:"blur(8px)",
          borderRadius:8,
          padding:"12px 28px",
          fontSize:36,
          fontWeight:400,
          color:COLORS.text,
          fontFamily:'"Noto Sans JP", Inter, sans-serif',
          lineHeight:1.5,
          maxWidth:"80%",
          textShadow:"0 2px 8px rgba(0,0,0,0.8)",
        }}>
          {active.text}
        </div>
      </div>
    </AbsoluteFill>
  );
};
