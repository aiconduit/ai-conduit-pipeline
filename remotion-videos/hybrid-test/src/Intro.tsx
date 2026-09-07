import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  Sequence,
  Easing,
  spring,
  useVideoConfig,
} from 'remotion';
import React from 'react';

const ANTHROPIC_COLOR = '#a78bfa';
const OPENAI_COLOR = '#10b981';
const BG = '#0a0a0f';

// パーティクル背景
const Particles: React.FC<{frame: number}> = ({frame}) => {
  const particles = Array.from({length: 30}, (_, i) => ({
    x: (Math.sin(i * 2.4 + frame * 0.01) * 0.5 + 0.5) * 1920,
    y: (Math.cos(i * 1.7 + frame * 0.008) * 0.5 + 0.5) * 1080,
    size: (Math.sin(i * 3.1) * 0.5 + 0.5) * 4 + 1,
    opacity: (Math.sin(frame * 0.05 + i) * 0.5 + 0.5) * 0.3,
    color: i % 2 === 0 ? ANTHROPIC_COLOR : OPENAI_COLOR,
  }));

  return (
    <svg style={{position: 'absolute', inset: 0}} width={1920} height={1080}>
      {particles.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r={p.size} fill={p.color} opacity={p.opacity} />
      ))}
      {/* グロー */}
      <radialGradient id="glow-a" cx="25%" cy="50%" r="40%">
        <stop offset="0%" stopColor={ANTHROPIC_COLOR} stopOpacity={0.15} />
        <stop offset="100%" stopColor={ANTHROPIC_COLOR} stopOpacity={0} />
      </radialGradient>
      <radialGradient id="glow-o" cx="75%" cy="50%" r="40%">
        <stop offset="0%" stopColor={OPENAI_COLOR} stopOpacity={0.15} />
        <stop offset="100%" stopColor={OPENAI_COLOR} stopOpacity={0} />
      </radialGradient>
      <rect width={1920} height={1080} fill="url(#glow-a)" />
      <rect width={1920} height={1080} fill="url(#glow-o)" />
    </svg>
  );
};

// イントロシーン（0〜150フレーム = 5秒）
const IntroScene: React.FC<{frame: number}> = ({frame}) => {
  const titleA = spring({frame, fps: 30, from: -100, to: 0, config: {damping: 15}, delay: 10});
  const titleO = spring({frame, fps: 30, from: 100, to: 0, config: {damping: 15}, delay: 10});
  const vsOpacity = interpolate(frame, [20, 40], [0, 1], {extrapolateRight: 'clamp'});
  const vsScale = spring({frame: frame - 20, fps: 30, from: 0, to: 1, config: {damping: 12}});
  const lineWidth = interpolate(frame, [40, 80], [0, 800], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const subOpacity = interpolate(frame, [60, 90], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 0}}>
      {/* メインタイトル */}
      <div style={{display: 'flex', alignItems: 'center', gap: 80, marginBottom: 32}}>
        <div style={{transform: `translateX(${titleA}px)`, textAlign: 'center'}}>
          <div style={{fontSize: 96, fontWeight: 900, color: ANTHROPIC_COLOR, fontFamily: 'sans-serif', letterSpacing: -3, lineHeight: 1}}>
            Anthropic
          </div>
          <div style={{fontSize: 24, color: 'rgba(255,255,255,0.4)', fontFamily: 'sans-serif', marginTop: 8, letterSpacing: 2}}>
            Claude Fable 5.1
          </div>
        </div>

        <div style={{
          opacity: vsOpacity,
          transform: `scale(${vsScale})`,
          fontSize: 72,
          fontWeight: 900,
          color: 'rgba(255,255,255,0.12)',
          fontFamily: 'sans-serif',
          letterSpacing: -2,
        }}>
          VS
        </div>

        <div style={{transform: `translateX(${titleO}px)`, textAlign: 'center'}}>
          <div style={{fontSize: 96, fontWeight: 900, color: OPENAI_COLOR, fontFamily: 'sans-serif', letterSpacing: -3, lineHeight: 1}}>
            OpenAI
          </div>
          <div style={{fontSize: 24, color: 'rgba(255,255,255,0.4)', fontFamily: 'sans-serif', marginTop: 8, letterSpacing: 2}}>
            GPT-6 Astra
          </div>
        </div>
      </div>

      {/* アクセントライン */}
      <div style={{
        width: lineWidth,
        height: 2,
        background: `linear-gradient(to right, ${ANTHROPIC_COLOR}, rgba(255,255,255,0.1), ${OPENAI_COLOR})`,
        borderRadius: 1,
        marginBottom: 32,
      }} />

      {/* サブタイトル */}
      <div style={{
        opacity: subOpacity,
        fontSize: 28,
        fontWeight: 300,
        color: 'rgba(255,255,255,0.5)',
        fontFamily: 'sans-serif',
        letterSpacing: 6,
        textTransform: 'uppercase',
      }}>
        AI最強2社の戦略比較
      </div>
    </AbsoluteFill>
  );
};

// データビジュアライゼーション（収益グラフ）
const RevenueChart: React.FC<{frame: number}> = ({frame}) => {
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});
  const barA = interpolate(frame, [20, 80], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const barO = interpolate(frame, [40, 100], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const labelA = interpolate(frame, [80, 100], [0, 1], {extrapolateRight: 'clamp'});
  const labelO = interpolate(frame, [100, 120], [0, 1], {extrapolateRight: 'clamp'});
  const noteOpacity = interpolate(frame, [120, 140], [0, 1], {extrapolateRight: 'clamp'});

  const maxH = 400;

  return (
    <AbsoluteFill style={{padding: '60px 160px', justifyContent: 'center'}}>
      {/* タイトル */}
      <div style={{opacity: titleOpacity, marginBottom: 60}}>
        <div style={{fontSize: 14, color: 'rgba(255,255,255,0.25)', letterSpacing: 6, textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: 12}}>
          ANNUAL REVENUE RUN-RATE 2026
        </div>
        <div style={{fontSize: 56, fontWeight: 900, color: '#fff', fontFamily: 'sans-serif', letterSpacing: -2}}>
          収益比較
        </div>
      </div>

      {/* グラフエリア */}
      <div style={{display: 'flex', alignItems: 'flex-end', gap: 80, height: maxH + 80}}>
        {/* Anthropicバー */}
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16}}>
          <div style={{
            opacity: labelA,
            fontSize: 48,
            fontWeight: 900,
            color: ANTHROPIC_COLOR,
            fontFamily: 'sans-serif',
          }}>$30B</div>
          <div style={{
            width: 200,
            height: maxH * barA,
            background: `linear-gradient(to top, ${ANTHROPIC_COLOR}, ${ANTHROPIC_COLOR}66)`,
            borderRadius: '12px 12px 0 0',
            boxShadow: `0 0 40px ${ANTHROPIC_COLOR}44`,
            transition: 'height 0.1s',
          }} />
          <div style={{fontSize: 20, color: ANTHROPIC_COLOR, fontFamily: 'sans-serif', fontWeight: 600}}>Anthropic</div>
        </div>

        {/* OpenAIバー */}
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16}}>
          <div style={{
            opacity: labelO,
            fontSize: 48,
            fontWeight: 900,
            color: OPENAI_COLOR,
            fontFamily: 'sans-serif',
          }}>$25B</div>
          <div style={{
            width: 200,
            height: maxH * 0.83 * barO,
            background: `linear-gradient(to top, ${OPENAI_COLOR}, ${OPENAI_COLOR}66)`,
            borderRadius: '12px 12px 0 0',
            boxShadow: `0 0 40px ${OPENAI_COLOR}44`,
          }} />
          <div style={{fontSize: 20, color: OPENAI_COLOR, fontFamily: 'sans-serif', fontWeight: 600}}>OpenAI</div>
        </div>

        {/* 成長率インフォ */}
        <div style={{
          opacity: noteOpacity,
          marginLeft: 60,
          marginBottom: 80,
          padding: '24px 32px',
          background: `${ANTHROPIC_COLOR}11`,
          border: `1px solid ${ANTHROPIC_COLOR}33`,
          borderRadius: 16,
          maxWidth: 400,
        }}>
          <div style={{fontSize: 18, color: ANTHROPIC_COLOR, fontFamily: 'sans-serif', fontWeight: 600, marginBottom: 8}}>
            🚀 Anthropic 15ヶ月で33倍成長
          </div>
          <div style={{fontSize: 16, color: 'rgba(255,255,255,0.5)', fontFamily: 'sans-serif', lineHeight: 1.5}}>
            2025年初: $1B ARR
            → 2026年4月: $30B ARR
          </div>
        </div>
      </div>

      {/* ベースライン */}
      <div style={{height: 2, background: 'rgba(255,255,255,0.08)', marginTop: -2}} />
    </AbsoluteFill>
  );
};

// メインコンポーネント
export const HybridIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  return (
    <AbsoluteFill style={{background: BG}}>
      <Particles frame={frame} />

      {/* イントロ 0〜150 (5秒) */}
      <Sequence from={0} durationInFrames={150}>
        <IntroScene frame={frame} />
      </Sequence>

      {/* 収益グラフ 150〜330 (6秒) */}
      <Sequence from={150} durationInFrames={180}>
        <RevenueChart frame={frame - 150} />
      </Sequence>

      {/* プログレスバー */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: 3,
        background: 'rgba(255,255,255,0.05)',
      }}>
        <div style={{
          width: `${(frame / durationInFrames) * 100}%`,
          height: '100%',
          background: `linear-gradient(to right, ${ANTHROPIC_COLOR}, ${OPENAI_COLOR})`,
        }} />
      </div>
    </AbsoluteFill>
  );
};
