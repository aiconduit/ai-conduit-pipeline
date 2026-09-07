import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  spring,
  Sequence,
  Easing,
  random,
} from 'remotion';
import React from 'react';

// ============================================================
// フォント読み込み (Noto Sans JP for 日本語)
// ============================================================
import {loadFont as loadNotoSans} from "@remotion/google-fonts/NotoSansJP";

const {fontFamily: jaFont} = loadNotoSans();

// ============================================================
// THEME OBJECT (原則8: 全てここから)
// ============================================================
const THEME = {
  colors: {
    anthropic: '#a78bfa',
    openai: '#10b981',
    accent: '#06b6d4',
    gold: '#f59e0b',
    bg: '#040408',
    surface: 'rgba(255,255,255,0.04)',
    border: 'rgba(255,255,255,0.08)',
  },
  fonts: {
    display: `${jaFont}, Inter, system-ui, sans-serif`,
    mono: 'JetBrains Mono, Menlo, monospace',
  },
};

// ============================================================
// LAYER 5: グレイン + ビネット (最上位レイヤー)
// ============================================================
const GrainVignette: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const grainOpacity = 0.035;
  // ランダムシードでグレインをアニメーション
  const seed = frame * 7919 % 9973;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', zIndex: 100}}>
      {/* ビネット */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,0.7) 100%)',
      }} />
      {/* グレイン (SVG noise) */}
      <svg style={{position: 'absolute', inset: 0, opacity: grainOpacity}} width="100%" height="100%">
        <filter id={`grain-${frame % 3}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" seed={seed} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#grain-${frame % 3})`} />
      </svg>
    </AbsoluteFill>
  );
};

// ============================================================
// LAYER 4: カラーグレード
// ============================================================
const ColorGrade: React.FC = () => (
  <AbsoluteFill style={{pointerEvents: 'none', zIndex: 90, mixBlendMode: 'color'}}>
    <div style={{
      position: 'absolute', inset: 0,
      background: 'linear-gradient(135deg, rgba(80,40,120,0.08) 0%, rgba(20,60,80,0.08) 100%)',
    }} />
  </AbsoluteFill>
);

// ============================================================
// LAYER 1: 背景メッシュ (底レイヤー)
// ============================================================
const BackgroundMesh: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const t = frame / fps;
  
  // 呼吸するグロー (原則6: sin波マイクロモーション)
  const glow1 = Math.sin(t * 0.4) * 0.5 + 0.5;
  const glow2 = Math.sin(t * 0.3 + 1.2) * 0.5 + 0.5;
  const glow3 = Math.sin(t * 0.25 + 2.4) * 0.5 + 0.5;

  // 波形ライン
  const wavePoints1 = Array.from({length: 24}, (_, i) => {
    const x = (i / 23) * 1920;
    const y = 540 + Math.sin(i * 0.4 + t * 0.8) * 80 + Math.sin(i * 0.7 + t * 1.1) * 40;
    return `${x},${y}`;
  }).join(' ');
  
  const wavePoints2 = Array.from({length: 24}, (_, i) => {
    const x = (i / 23) * 1920;
    const y = 540 + Math.sin(i * 0.5 + t * 0.6 + 1) * 60 + Math.sin(i * 0.3 + t * 0.9) * 30;
    return `${x},${y}`;
  }).join(' ');

  return (
    <AbsoluteFill style={{background: THEME.colors.bg, zIndex: 0}}>
      <svg style={{position: 'absolute', inset: 0}} width={1920} height={1080}>
        <defs>
          <radialGradient id="g1" cx="20%" cy="35%" r="45%">
            <stop offset="0%" stopColor={THEME.colors.anthropic} stopOpacity={0.18 * glow1} />
            <stop offset="100%" stopColor={THEME.colors.anthropic} stopOpacity={0} />
          </radialGradient>
          <radialGradient id="g2" cx="80%" cy="65%" r="45%">
            <stop offset="0%" stopColor={THEME.colors.openai} stopOpacity={0.18 * glow2} />
            <stop offset="100%" stopColor={THEME.colors.openai} stopOpacity={0} />
          </radialGradient>
          <radialGradient id="g3" cx="50%" cy="50%" r="35%">
            <stop offset="0%" stopColor={THEME.colors.accent} stopOpacity={0.08 * glow3} />
            <stop offset="100%" stopColor={THEME.colors.accent} stopOpacity={0} />
          </radialGradient>
        </defs>
        {/* グロー */}
        <rect width={1920} height={1080} fill="url(#g1)" />
        <rect width={1920} height={1080} fill="url(#g2)" />
        <rect width={1920} height={1080} fill="url(#g3)" />
        {/* グリッド */}
        {Array.from({length: 20}).map((_, i) => (
          <line key={`v${i}`} x1={i * 96} y1={0} x2={i * 96} y2={1080}
            stroke="white" strokeWidth={0.4} opacity={0.025 + Math.sin(t * 0.3 + i * 0.5) * 0.01} />
        ))}
        {Array.from({length: 12}).map((_, i) => (
          <line key={`h${i}`} x1={0} y1={i * 90} x2={1920} y2={i * 90}
            stroke="white" strokeWidth={0.4} opacity={0.025} />
        ))}
        {/* 波形 */}
        <polyline points={wavePoints1} fill="none" stroke={THEME.colors.anthropic} strokeWidth={1.2} opacity={0.2} />
        <polyline points={wavePoints2} fill="none" stroke={THEME.colors.openai} strokeWidth={1.2} opacity={0.2} />
        {/* パーティクル */}
        {Array.from({length: 40}).map((_, i) => {
          const px = ((Math.sin(i * 7.3 + t * 0.2) * 0.5 + 0.5 + i * 0.025) % 1) * 1920;
          const py = ((Math.cos(i * 5.1 + t * 0.15) * 0.5 + 0.5) % 1) * 1080;
          const pr = (Math.sin(i * 3.7) * 0.5 + 0.5) * 2.5 + 0.5;
          const po = (Math.sin(t * 0.8 + i * 1.1) * 0.5 + 0.5) * 0.35;
          const pc = i % 3 === 0 ? THEME.colors.anthropic : i % 3 === 1 ? THEME.colors.openai : THEME.colors.accent;
          return <circle key={i} cx={px} cy={py} r={pr} fill={pc} opacity={po} />;
        })}
      </svg>
    </AbsoluteFill>
  );
};

// ============================================================
// スプリングヘルパー (原則1: spring優先)
// ============================================================
const useSpring = (frame: number, fps: number, delay: number = 0, damping: number = 14) =>
  spring({frame: Math.max(0, frame - delay), fps, config: {damping, mass: 0.8}});

// ============================================================
// シーン1: イントロ (0〜6秒)
// ============================================================
const IntroScene: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const dur = fps * 6;
  
  // 原則1: spring
  const titleASpring = useSpring(frame, fps, fps * 0.3, 12);
  const titleOSpring = useSpring(frame, fps, fps * 0.5, 12);
  const vsSpring = useSpring(frame, fps, fps * 0.7, 10);
  
  // 原則2: 複数プロパティ
  const titleAX = interpolate(titleASpring, [0, 1], [-80, 0]);
  const titleAO = interpolate(titleASpring, [0, 1], [0, 1]);
  const titleAS = interpolate(titleASpring, [0, 1], [0.85, 1]);
  
  const titleOX = interpolate(titleOSpring, [0, 1], [80, 0]);
  const titleOO = interpolate(titleOSpring, [0, 1], [0, 1]);
  const titleOS = interpolate(titleOSpring, [0, 1], [0.85, 1]);
  
  // 原則3: スタガード (3フレームオフセット)
  const sub1 = useSpring(frame, fps, fps * 0.9);
  const sub2 = useSpring(frame, fps, fps * 1.0);
  const lineW = interpolate(useSpring(frame, fps, fps * 0.85, 8), [0, 1], [0, 900]);
  
  // 原則6: 呼吸するVS
  const t = frame / fps;
  const vsBreath = Math.sin(t * 1.5) * 0.02 + 1;

  // 退場アニメーション
  const exitStart = dur - fps * 0.5;
  const exitO = interpolate(frame, [exitStart, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});

  return (
    <AbsoluteFill style={{opacity: exitO, justifyContent: 'center', alignItems: 'center', flexDirection: 'column'}}>
      {/* メインタイトル */}
      <div style={{display: 'flex', alignItems: 'center', gap: 80, marginBottom: 40}}>
        {/* Anthropic */}
        <div style={{
          opacity: titleAO,
          transform: `translateX(${titleAX}px) scale(${titleAS})`,
          textAlign: 'center',
        }}>
          <div style={{fontSize: 100, fontWeight: 900, color: THEME.colors.anthropic,
            fontFamily: THEME.fonts.display, letterSpacing: -4, lineHeight: 1,
            textShadow: `0 0 80px ${THEME.colors.anthropic}60`}}>
            Anthropic
          </div>
          {/* 原則3: スタガード */}
          <div style={{opacity: interpolate(sub1, [0,1], [0,1]), fontSize: 22,
            color: 'rgba(255,255,255,0.35)', fontFamily: THEME.fonts.display,
            letterSpacing: 3, marginTop: 10}}>
            Claude Fable 5.1
          </div>
        </div>

        {/* VS */}
        <div style={{
          opacity: interpolate(vsSpring, [0, 1], [0, 1]),
          transform: `scale(${vsBreath})`,
          fontSize: 56, fontWeight: 900, color: 'rgba(255,255,255,0.1)',
          fontFamily: THEME.fonts.display,
        }}>VS</div>

        {/* OpenAI */}
        <div style={{
          opacity: titleOO,
          transform: `translateX(${titleOX}px) scale(${titleOS})`,
          textAlign: 'center',
        }}>
          <div style={{fontSize: 100, fontWeight: 900, color: THEME.colors.openai,
            fontFamily: THEME.fonts.display, letterSpacing: -4, lineHeight: 1,
            textShadow: `0 0 80px ${THEME.colors.openai}60`}}>
            OpenAI
          </div>
          <div style={{opacity: interpolate(sub2, [0,1], [0,1]), fontSize: 22,
            color: 'rgba(255,255,255,0.35)', fontFamily: THEME.fonts.display,
            letterSpacing: 3, marginTop: 10}}>
            GPT-6 Astra
          </div>
        </div>
      </div>

      {/* アクセントライン */}
      <div style={{
        width: lineW, height: 2, borderRadius: 1,
        background: `linear-gradient(to right, ${THEME.colors.anthropic}, rgba(255,255,255,0.1), ${THEME.colors.openai})`,
        marginBottom: 36,
      }} />

      {/* サブタイトル */}
      <div style={{
        opacity: interpolate(sub1, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(sub1, [0, 1], [20, 0])}px)`,
        fontSize: 24, fontWeight: 300, color: 'rgba(255,255,255,0.4)',
        fontFamily: THEME.fonts.display, letterSpacing: 8, textTransform: 'uppercase',
      }}>
        AI最強2社の戦略比較
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// データバー (スタガード付き)
// ============================================================
const AnimatedBar: React.FC<{
  label: string; value: number; maxVal: number; color: string;
  frame: number; fps: number; delay: number; unit?: string;
}> = ({label, value, maxVal, color, frame, fps, delay, unit = '$'}) => {
  const sp = useSpring(frame, fps, delay, 10);
  const barW = interpolate(sp, [0, 1], [0, (value / maxVal) * 100]);
  const labelO = interpolate(sp, [0, 0.3], [0, 1], {extrapolateRight: 'clamp'});
  const numO = interpolate(sp, [0.5, 1], [0, 1], {extrapolateRight: 'clamp'});
  
  // 原則6: 呼吸
  const t = frame / fps;
  const breathScale = 1 + Math.sin(t * 1.2 + delay) * 0.005;

  return (
    <div style={{opacity: labelO, marginBottom: 28, transform: `scale(${breathScale})`}}>
      <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 10, alignItems: 'baseline'}}>
        <span style={{fontSize: 20, color: 'rgba(255,255,255,0.6)', fontFamily: THEME.fonts.display}}>
          {label}
        </span>
        <span style={{opacity: numO, fontSize: 32, fontWeight: 900, color, fontFamily: THEME.fonts.display,
          textShadow: `0 0 20px ${color}60`}}>
          {unit}{value}B
        </span>
      </div>
      <div style={{height: 10, background: 'rgba(255,255,255,0.06)', borderRadius: 5, overflow: 'hidden'}}>
        <div style={{
          width: `${barW}%`, height: '100%', borderRadius: 5,
          background: `linear-gradient(to right, ${color}, ${color}88)`,
          boxShadow: `0 0 20px ${color}60`,
        }} />
      </div>
    </div>
  );
};

// ============================================================
// シーン2: 収益比較 (6〜14秒)
// ============================================================
const RevenueScene: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const dur = fps * 8;
  const titleSp = useSpring(frame, fps, fps * 0.2, 14);
  
  // 退場
  const exitO = interpolate(frame, [dur - fps * 0.5, dur], [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});

  const t = frame / fps;
  // 原則6: タイトル呼吸
  const titleBreath = 1 + Math.sin(t * 0.8) * 0.003;

  return (
    <AbsoluteFill style={{opacity: exitO, padding: '60px 140px', justifyContent: 'center'}}>
      {/* タイトル */}
      <div style={{
        opacity: interpolate(titleSp, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(titleSp, [0, 1], [30, 0])}px) scale(${titleBreath})`,
        marginBottom: 60,
      }}>
        <div style={{fontSize: 13, color: 'rgba(255,255,255,0.2)', letterSpacing: 7,
          textTransform: 'uppercase', fontFamily: THEME.fonts.display, marginBottom: 12}}>
          Annual Revenue Run-Rate · 2026
        </div>
        <div style={{fontSize: 64, fontWeight: 900, color: '#fff', fontFamily: THEME.fonts.display,
          letterSpacing: -3}}>
          収益比較
        </div>
      </div>

      {/* バー（原則3: スタガード）*/}
      <AnimatedBar label="Anthropic ARR" value={30} maxVal={35}
        color={THEME.colors.anthropic} frame={frame} fps={fps} delay={fps * 0.4} />
      <AnimatedBar label="OpenAI ARR" value={25} maxVal={35}
        color={THEME.colors.openai} frame={frame} fps={fps} delay={fps * 0.6} />

      {/* インサイトカード */}
      {(() => {
        const cardSp = useSpring(frame, fps, fps * 1.2, 12);
        return (
          <div style={{
            opacity: interpolate(cardSp, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(cardSp, [0, 1], [20, 0])}px)`,
            marginTop: 40, padding: '20px 28px',
            background: `${THEME.colors.anthropic}10`,
            border: `1px solid ${THEME.colors.anthropic}25`,
            borderRadius: 14,
          }}>
            <span style={{fontSize: 18, color: THEME.colors.anthropic, fontFamily: THEME.fonts.display, fontWeight: 600}}>
              🚀 Anthropic: 15ヶ月で33倍成長（$1B → $30B）
            </span>
          </div>
        );
      })()}
    </AbsoluteFill>
  );
};

// ============================================================
// シーン3: 時価総額 (14〜22秒)
// ============================================================
const ValuationScene: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const dur = fps * 8;
  const titleSp = useSpring(frame, fps, fps * 0.2, 14);
  const barASp = useSpring(frame, fps, fps * 0.5, 10);
  const barOSp = useSpring(frame, fps, fps * 0.7, 10);
  
  const exitO = interpolate(frame, [dur - fps * 0.5, dur], [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});

  const t = frame / fps;
  const aH = interpolate(barASp, [0, 1], [0, 320]);
  const oH = interpolate(barOSp, [0, 1], [0, 280]);
  
  // 原則6: バーの呼吸
  const aBreath = 1 + Math.sin(t * 1.0) * 0.01;
  const oBreath = 1 + Math.sin(t * 1.1 + 0.5) * 0.01;

  return (
    <AbsoluteFill style={{opacity: exitO, padding: '60px 140px', justifyContent: 'center', alignItems: 'center', flexDirection: 'column'}}>
      <div style={{
        opacity: interpolate(titleSp, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(titleSp, [0, 1], [30, 0])}px)`,
        marginBottom: 80, textAlign: 'center',
      }}>
        <div style={{fontSize: 13, color: 'rgba(255,255,255,0.2)', letterSpacing: 7,
          textTransform: 'uppercase', fontFamily: THEME.fonts.display, marginBottom: 12}}>
          Valuation · 2026
        </div>
        <div style={{fontSize: 64, fontWeight: 900, color: '#fff', fontFamily: THEME.fonts.display, letterSpacing: -3}}>
          時価総額
        </div>
      </div>

      <div style={{display: 'flex', gap: 100, alignItems: 'flex-end'}}>
        {/* Anthropic */}
        <div style={{textAlign: 'center', transform: `scale(${aBreath})`, transformOrigin: 'bottom center'}}>
          <div style={{
            opacity: interpolate(barASp, [0.7, 1], [0, 1], {extrapolateRight: 'clamp'}),
            fontSize: 44, fontWeight: 900, color: THEME.colors.anthropic,
            fontFamily: THEME.fonts.display, marginBottom: 12,
            textShadow: `0 0 30px ${THEME.colors.anthropic}80`,
          }}>$965B</div>
          <div style={{
            width: 220, height: aH,
            background: `linear-gradient(to top, ${THEME.colors.anthropic}, ${THEME.colors.anthropic}44)`,
            borderRadius: '14px 14px 0 0',
            boxShadow: `0 0 60px ${THEME.colors.anthropic}44`,
          }} />
          <div style={{fontSize: 22, color: THEME.colors.anthropic, fontFamily: THEME.fonts.display,
            fontWeight: 700, marginTop: 16}}>Anthropic</div>
          <div style={{fontSize: 14, color: 'rgba(255,255,255,0.3)', fontFamily: THEME.fonts.display, marginTop: 4}}>
            🏆 時価総額1位
          </div>
        </div>

        {/* OpenAI */}
        <div style={{textAlign: 'center', transform: `scale(${oBreath})`, transformOrigin: 'bottom center'}}>
          <div style={{
            opacity: interpolate(barOSp, [0.7, 1], [0, 1], {extrapolateRight: 'clamp'}),
            fontSize: 44, fontWeight: 900, color: THEME.colors.openai,
            fontFamily: THEME.fonts.display, marginBottom: 12,
            textShadow: `0 0 30px ${THEME.colors.openai}80`,
          }}>$852B</div>
          <div style={{
            width: 220, height: oH,
            background: `linear-gradient(to top, ${THEME.colors.openai}, ${THEME.colors.openai}44)`,
            borderRadius: '14px 14px 0 0',
            boxShadow: `0 0 60px ${THEME.colors.openai}44`,
          }} />
          <div style={{fontSize: 22, color: THEME.colors.openai, fontFamily: THEME.fonts.display,
            fontWeight: 700, marginTop: 16}}>OpenAI</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// シーン4: まとめ (22〜30秒)
// ============================================================
const ConclusionScene: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const points = [
    {text: 'Anthropic収益が逆転・エンタープライズ首位', color: THEME.colors.anthropic},
    {text: 'OpenAIはユーザー規模で圧倒（9億人）', color: THEME.colors.openai},
    {text: '両社2026〜2027年にIPO予定', color: THEME.colors.gold},
    {text: 'AGIは2〜3年以内という見方が主流', color: THEME.colors.accent},
  ];

  const titleSp = useSpring(frame, fps, fps * 0.2, 14);
  const t = frame / fps;

  return (
    <AbsoluteFill style={{padding: '60px 140px', justifyContent: 'center'}}>
      <div style={{
        opacity: interpolate(titleSp, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(titleSp, [0, 1], [30, 0])}px)`,
        marginBottom: 50,
      }}>
        <div style={{fontSize: 64, fontWeight: 900, color: '#fff', fontFamily: THEME.fonts.display, letterSpacing: -3}}>
          まとめ
        </div>
      </div>

      {/* 原則3: スタガード */}
      {points.map((p, i) => {
        const sp = useSpring(frame, fps, fps * (0.5 + i * 0.15), 12);
        const breath = 1 + Math.sin(t * 0.9 + i * 0.7) * 0.005;
        return (
          <div key={i} style={{
            opacity: interpolate(sp, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(sp, [0, 1], [-40, 0])}px) scale(${breath})`,
            display: 'flex', alignItems: 'center', gap: 20, marginBottom: 24,
            padding: '18px 24px',
            background: `${p.color}0a`,
            border: `1px solid ${p.color}20`,
            borderRadius: 12,
          }}>
            <div style={{width: 8, height: 8, borderRadius: '50%', background: p.color,
              boxShadow: `0 0 12px ${p.color}`, flexShrink: 0}} />
            <div style={{fontSize: 24, color: '#fff', fontFamily: THEME.fonts.display, fontWeight: 400}}>
              {p.text}
            </div>
          </div>
        );
      })}

      {/* CTA */}
      {(() => {
        const ctaSp = useSpring(frame, fps, fps * 1.5, 12);
        const ctaBreath = 1 + Math.sin(t * 1.5) * 0.01;
        return (
          <div style={{
            opacity: interpolate(ctaSp, [0, 1], [0, 1]),
            transform: `scale(${ctaBreath})`,
            marginTop: 40, textAlign: 'center',
            fontSize: 18, color: 'rgba(255,255,255,0.25)',
            fontFamily: THEME.fonts.display, letterSpacing: 4,
          }}>
            @AI.Conduit — チャンネル登録お願いします
          </div>
        );
      })()}
    </AbsoluteFill>
  );
};

// ============================================================
// プログレスバー
// ============================================================
const ProgressBar: React.FC<{frame: number; total: number}> = ({frame, total}) => (
  <div style={{position: 'absolute', bottom: 0, left: 0, right: 0, height: 2,
    background: 'rgba(255,255,255,0.04)', zIndex: 80}}>
    <div style={{
      width: `${(frame / total) * 100}%`, height: '100%',
      background: `linear-gradient(to right, ${THEME.colors.anthropic}, ${THEME.colors.openai})`,
    }} />
  </div>
);

// ============================================================
// メインコンポーネント
// ============================================================
export const ProMotion: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  const scene1Dur = fps * 6;
  const scene2Dur = fps * 8;
  const scene3Dur = fps * 8;
  const scene4Dur = fps * 8;

  return (
    <AbsoluteFill>
      {/* Layer 1: 背景メッシュ */}
      <BackgroundMesh frame={frame} fps={fps} />

      {/* Layer 2-3: シーンコンテンツ */}
      <Sequence from={0} durationInFrames={scene1Dur}>
        <IntroScene frame={frame} fps={fps} />
      </Sequence>
      <Sequence from={scene1Dur} durationInFrames={scene2Dur}>
        <RevenueScene frame={frame - scene1Dur} fps={fps} />
      </Sequence>
      <Sequence from={scene1Dur + scene2Dur} durationInFrames={scene3Dur}>
        <ValuationScene frame={frame - scene1Dur - scene2Dur} fps={fps} />
      </Sequence>
      <Sequence from={scene1Dur + scene2Dur + scene3Dur} durationInFrames={scene4Dur}>
        <ConclusionScene frame={frame - scene1Dur - scene2Dur - scene3Dur} fps={fps} />
      </Sequence>

      {/* Layer 4: カラーグレード */}
      <ColorGrade />

      {/* Layer 5: グレイン + ビネット */}
      <GrainVignette frame={frame} fps={fps} />

      {/* プログレスバー */}
      <ProgressBar frame={frame} total={durationInFrames} />
    </AbsoluteFill>
  );
};
