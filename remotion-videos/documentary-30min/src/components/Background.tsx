import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { noise2D } from "@remotion/noise";
import React from "react";
import { COLORS } from "../constants";

export const Background: React.FC<{seed?: number}> = ({seed = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;

  const g1 = Math.sin(t * 0.3 + seed) * 0.5 + 0.5;
  const g2 = Math.sin(t * 0.25 + seed + 1.2) * 0.5 + 0.5;

  return (
    <AbsoluteFill style={{background: COLORS.bg}}>
      <svg style={{position:"absolute",inset:0,width:"100%",height:"100%"}} viewBox="0 0 1920 1080">
        <defs>
          <radialGradient id={`g1-${seed}`} cx="25%" cy="40%" r="50%">
            <stop offset="0%" stopColor={COLORS.anthropic} stopOpacity={0.15 * g1} />
            <stop offset="100%" stopColor={COLORS.anthropic} stopOpacity={0} />
          </radialGradient>
          <radialGradient id={`g2-${seed}`} cx="75%" cy="60%" r="50%">
            <stop offset="0%" stopColor={COLORS.openai} stopOpacity={0.15 * g2} />
            <stop offset="100%" stopColor={COLORS.openai} stopOpacity={0} />
          </radialGradient>
        </defs>
        <rect width={1920} height={1080} fill={`url(#g1-${seed})`} />
        <rect width={1920} height={1080} fill={`url(#g2-${seed})`} />
        {/* グリッド */}
        {Array.from({length:20},(_,i)=>(
          <line key={`v${i}`} x1={i*96} y1={0} x2={i*96} y2={1080} stroke="white" strokeWidth={0.4} opacity={0.025}/>
        ))}
        {Array.from({length:12},(_,i)=>(
          <line key={`h${i}`} x1={0} y1={i*90} x2={1920} y2={i*90} stroke="white" strokeWidth={0.4} opacity={0.025}/>
        ))}
        {/* 波形 */}
        <polyline
          points={Array.from({length:24},(_,i)=>{
            const x=(i/23)*1920;
            const y=540+Math.sin(i*0.4+t*0.6)*70+Math.sin(i*0.7+t*0.9)*35;
            return `${x},${y}`;
          }).join(' ')}
          fill="none" stroke={COLORS.anthropic} strokeWidth={1.2} opacity={0.2}
        />
        <polyline
          points={Array.from({length:24},(_,i)=>{
            const x=(i/23)*1920;
            const y=540+Math.sin(i*0.5+t*0.5+1)*55+Math.sin(i*0.3+t*0.8)*28;
            return `${x},${y}`;
          }).join(' ')}
          fill="none" stroke={COLORS.openai} strokeWidth={1.2} opacity={0.2}
        />
      </svg>
    </AbsoluteFill>
  );
};
