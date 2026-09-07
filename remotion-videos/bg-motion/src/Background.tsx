import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import React from 'react';

const COLORS = {
  anthropic: '#a78bfa',
  openai: '#10b981',
  accent: '#06b6d4',
  bg: '#050510',
};

// 波形背景
const WaveBackground: React.FC<{frame: number}> = ({frame}) => {
  const t = frame * 0.02;
  const points1 = Array.from({length: 20}, (_, i) => {
    const x = (i / 19) * 1920;
    const y = 540 + Math.sin(i * 0.5 + t) * 120 + Math.sin(i * 0.3 + t * 1.3) * 60;
    return `${x},${y}`;
  }).join(' ');
  const points2 = Array.from({length: 20}, (_, i) => {
    const x = (i / 19) * 1920;
    const y = 540 + Math.sin(i * 0.4 + t * 0.8 + 1) * 100 + Math.sin(i * 0.6 + t * 1.1) * 50;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg style={{position: 'absolute', inset: 0}} width={1920} height={1080}>
      <defs>
        <radialGradient id="bg-glow-1" cx="25%" cy="40%" r="50%">
          <stop offset="0%" stopColor={COLORS.anthropic} stopOpacity={0.2} />
          <stop offset="100%" stopColor={COLORS.anthropic} stopOpacity={0} />
        </radialGradient>
        <radialGradient id="bg-glow-2" cx="75%" cy="60%" r="50%">
          <stop offset="0%" stopColor={COLORS.openai} stopOpacity={0.2} />
          <stop offset="100%" stopColor={COLORS.openai} stopOpacity={0} />
        </radialGradient>
        <radialGradient id="bg-glow-3" cx="50%" cy="50%" r="40%">
          <stop offset="0%" stopColor={COLORS.accent} stopOpacity={0.08} />
          <stop offset="100%" stopColor={COLORS.accent} stopOpacity={0} />
        </radialGradient>
      </defs>
      <rect width={1920} height={1080} fill={COLORS.bg} />
      <rect width={1920} height={1080} fill="url(#bg-glow-1)" />
      <rect width={1920} height={1080} fill="url(#bg-glow-2)" />
      <rect width={1920} height={1080} fill="url(#bg-glow-3)" />
      {/* グリッド */}
      {Array.from({length: 16}).map((_, i) => (
        <line key={`v${i}`} x1={i*128} y1={0} x2={i*128} y2={1080}
          stroke="white" strokeWidth={0.5} opacity={0.03} />
      ))}
      {Array.from({length: 9}).map((_, i) => (
        <line key={`h${i}`} x1={0} y1={i*135} x2={1920} y2={i*135}
          stroke="white" strokeWidth={0.5} opacity={0.03} />
      ))}
      {/* 波形 */}
      <polyline points={points1} fill="none" stroke={COLORS.anthropic} strokeWidth={1.5} opacity={0.25} />
      <polyline points={points2} fill="none" stroke={COLORS.openai} strokeWidth={1.5} opacity={0.25} />
    </svg>
  );
};

// パーティクル
const Particles: React.FC<{frame: number}> = ({frame}) => {
  const particles = Array.from({length: 50}, (_, i) => {
    const seed = i * 7.3;
    const x = ((Math.sin(seed) * 0.5 + 0.5 + frame * 0.0003 * (i % 3 === 0 ? 1 : -0.5)) % 1) * 1920;
    const y = ((Math.cos(seed * 1.3) * 0.5 + 0.5 + frame * 0.0002 * (i % 2 === 0 ? 1 : -1)) % 1) * 1080;
    const size = (Math.sin(seed * 2.1) * 0.5 + 0.5) * 3 + 0.5;
    const opacity = (Math.sin(frame * 0.04 + seed) * 0.5 + 0.5) * 0.4;
    const color = i % 3 === 0 ? COLORS.anthropic : i % 3 === 1 ? COLORS.openai : COLORS.accent;
    return {x, y, size, opacity, color};
  });

  return (
    <svg style={{position: 'absolute', inset: 0}} width={1920} height={1080}>
      {particles.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r={p.size} fill={p.color} opacity={p.opacity} />
      ))}
    </svg>
  );
};

// スキャンライン
const ScanLines: React.FC<{frame: number}> = ({frame}) => {
  const y = (frame * 4) % 1080;
  return (
    <svg style={{position: 'absolute', inset: 0, opacity: 0.03}} width={1920} height={1080}>
      <line x1={0} y1={y} x2={1920} y2={y} stroke="white" strokeWidth={2} />
    </svg>
  );
};

export const MotionBackground: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: COLORS.bg}}>
      <WaveBackground frame={frame} />
      <Particles frame={frame} />
      <ScanLines frame={frame} />
    </AbsoluteFill>
  );
};
