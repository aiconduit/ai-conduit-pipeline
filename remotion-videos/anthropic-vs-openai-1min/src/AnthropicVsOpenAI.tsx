import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  spring,
  Sequence,
  Easing,
} from 'remotion';
import React from 'react';

// カラーパレット
const ANTHROPIC_COLOR = '#a78bfa'; // パープル
const OPENAI_COLOR = '#10b981'; // グリーン
const BG_COLOR = '#0a0a0f';
const TEXT_COLOR = '#ffffff';

// セクション定義（1分 = 1800フレーム @ 30fps）
const SECTIONS = [
  {id: 'intro', start: 0, duration: 180, title: 'Anthropic vs OpenAI', subtitle: 'AI最強2社の比較'},
  {id: 'revenue', start: 180, duration: 360, title: '収益比較', subtitle: 'Anthropic $30B vs OpenAI $25B'},
  {id: 'models', start: 540, duration: 360, title: 'モデル比較', subtitle: 'Claude Fable 5.1 vs GPT-6 Astra'},
  {id: 'valuation', start: 900, duration: 360, title: '時価総額', subtitle: '$965B vs $852B'},
  {id: 'conclusion', start: 1260, duration: 540, title: 'まとめ', subtitle: 'どちらが勝者か？'},
];

// グラデーション背景
const Background: React.FC<{frame: number}> = ({frame}) => {
  const pulse = interpolate(
    Math.sin(frame * 0.02),
    [-1, 1],
    [0.3, 0.6]
  );
  return (
    <AbsoluteFill style={{background: BG_COLOR}}>
      {/* Anthropic側グロー */}
      <div style={{
        position: 'absolute',
        left: -200,
        top: '20%',
        width: 600,
        height: 600,
        borderRadius: '50%',
        background: `radial-gradient(circle, rgba(167,139,250,${pulse}) 0%, transparent 70%)`,
        filter: 'blur(80px)',
      }} />
      {/* OpenAI側グロー */}
      <div style={{
        position: 'absolute',
        right: -200,
        bottom: '20%',
        width: 600,
        height: 600,
        borderRadius: '50%',
        background: `radial-gradient(circle, rgba(16,185,129,${pulse}) 0%, transparent 70%)`,
        filter: 'blur(80px)',
      }} />
      {/* グリッドライン */}
      <svg style={{position: 'absolute', inset: 0, opacity: 0.04}} width="1920" height="1080">
        {Array.from({length: 20}).map((_, i) => (
          <line key={`v${i}`} x1={i * 96} y1={0} x2={i * 96} y2={1080} stroke="white" strokeWidth={1} />
        ))}
        {Array.from({length: 12}).map((_, i) => (
          <line key={`h${i}`} x1={0} y1={i * 90} x2={1920} y2={i * 90} stroke="white" strokeWidth={1} />
        ))}
      </svg>
    </AbsoluteFill>
  );
};

// イントロセクション
const IntroSection: React.FC<{frame: number; duration: number}> = ({frame, duration}) => {
  const titleOpacity = interpolate(frame, [0, 30], [0, 1], {extrapolateRight: 'clamp'});
  const titleY = interpolate(frame, [0, 30], [40, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const vsOpacity = interpolate(frame, [20, 50], [0, 1], {extrapolateRight: 'clamp'});
  const vsScale = interpolate(frame, [20, 50], [0.5, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.back(2))});

  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', flexDirection: 'column'}}>
      {/* Anthropicロゴテキスト */}
      <div style={{display: 'flex', alignItems: 'center', gap: 60, marginBottom: 40}}>
        <div style={{
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          textAlign: 'center',
        }}>
          <div style={{fontSize: 72, fontWeight: 900, color: ANTHROPIC_COLOR, fontFamily: 'Inter, sans-serif', letterSpacing: -2}}>
            Anthropic
          </div>
          <div style={{fontSize: 24, color: 'rgba(255,255,255,0.5)', fontFamily: 'Inter, sans-serif', marginTop: 8}}>
            Claude Fable 5.1
          </div>
        </div>

        {/* VS */}
        <div style={{
          opacity: vsOpacity,
          transform: `scale(${vsScale})`,
          fontSize: 80,
          fontWeight: 900,
          color: 'rgba(255,255,255,0.15)',
          fontFamily: 'Inter, sans-serif',
        }}>
          VS
        </div>

        <div style={{
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          textAlign: 'center',
        }}>
          <div style={{fontSize: 72, fontWeight: 900, color: OPENAI_COLOR, fontFamily: 'Inter, sans-serif', letterSpacing: -2}}>
            OpenAI
          </div>
          <div style={{fontSize: 24, color: 'rgba(255,255,255,0.5)', fontFamily: 'Inter, sans-serif', marginTop: 8}}>
            GPT-6 Astra
          </div>
        </div>
      </div>

      {/* サブタイトル */}
      <div style={{
        opacity: interpolate(frame, [40, 70], [0, 1], {extrapolateRight: 'clamp'}),
        fontSize: 32,
        color: 'rgba(255,255,255,0.6)',
        fontFamily: 'Inter, sans-serif',
        fontWeight: 300,
        letterSpacing: 4,
        textTransform: 'uppercase',
      }}>
        AI最強2社の戦略比較
      </div>

      {/* アクセントライン */}
      <div style={{
        width: interpolate(frame, [60, 90], [0, 600], {extrapolateRight: 'clamp'}),
        height: 2,
        background: `linear-gradient(to right, ${ANTHROPIC_COLOR}, transparent, ${OPENAI_COLOR})`,
        marginTop: 40,
        borderRadius: 1,
      }} />
    </AbsoluteFill>
  );
};

// データバーコンポーネント
const DataBar: React.FC<{
  label: string;
  value: number;
  maxValue: number;
  color: string;
  unit: string;
  frame: number;
  delay: number;
}> = ({label, value, maxValue, color, unit, frame, delay}) => {
  const progress = interpolate(frame, [delay, delay + 60], [0, value / maxValue], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const opacity = interpolate(frame, [delay - 10, delay + 10], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <div style={{opacity, marginBottom: 32}}>
      <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 12}}>
        <span style={{fontSize: 24, fontFamily: 'Inter, sans-serif', color: 'rgba(255,255,255,0.7)', fontWeight: 400}}>
          {label}
        </span>
        <span style={{fontSize: 28, fontFamily: 'Inter, sans-serif', color, fontWeight: 700}}>
          {unit}{Math.round(value * progress / value * value)}B
        </span>
      </div>
      <div style={{height: 12, background: 'rgba(255,255,255,0.08)', borderRadius: 6, overflow: 'hidden'}}>
        <div style={{
          width: `${progress * 100}%`,
          height: '100%',
          background: `linear-gradient(to right, ${color}, ${color}aa)`,
          borderRadius: 6,
          boxShadow: `0 0 20px ${color}80`,
        }} />
      </div>
    </div>
  );
};

// 収益比較セクション
const RevenueSection: React.FC<{frame: number}> = ({frame}) => {
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{padding: '60px 120px', justifyContent: 'center'}}>
      <div style={{opacity: titleOpacity, marginBottom: 60}}>
        <div style={{fontSize: 16, color: 'rgba(255,255,255,0.3)', letterSpacing: 6, textTransform: 'uppercase', fontFamily: 'Inter, sans-serif', marginBottom: 16}}>
          REVENUE COMPARISON 2026
        </div>
        <div style={{fontSize: 64, fontWeight: 900, color: TEXT_COLOR, fontFamily: 'Inter, sans-serif', letterSpacing: -2}}>
          収益比較
        </div>
      </div>

      <DataBar label="Anthropic ARR" value={30} maxValue={35} color={ANTHROPIC_COLOR} unit="$" frame={frame} delay={20} />
      <DataBar label="OpenAI ARR" value={25} maxValue={35} color={OPENAI_COLOR} unit="$" frame={frame} delay={40} />

      {/* 成長率表示 */}
      <div style={{
        opacity: interpolate(frame, [100, 130], [0, 1], {extrapolateRight: 'clamp'}),
        marginTop: 40,
        padding: '24px 32px',
        background: `rgba(167,139,250,0.1)`,
        border: `1px solid ${ANTHROPIC_COLOR}40`,
        borderRadius: 16,
      }}>
        <div style={{fontSize: 20, color: ANTHROPIC_COLOR, fontFamily: 'Inter, sans-serif', fontWeight: 600}}>
          🚀 Anthropicの成長率：15ヶ月で33倍（$1B → $30B）
        </div>
      </div>
    </AbsoluteFill>
  );
};

// モデル比較セクション
const ModelSection: React.FC<{frame: number}> = ({frame}) => {
  const categories = [
    {name: 'コーディング', anthropic: 94, openai: 88},
    {name: '推論', anthropic: 91, openai: 93},
    {name: '数学', anthropic: 87, openai: 92},
    {name: '長文理解', anthropic: 95, openai: 86},
  ];

  return (
    <AbsoluteFill style={{padding: '60px 120px', justifyContent: 'center'}}>
      <div style={{
        opacity: interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
        marginBottom: 60,
      }}>
        <div style={{fontSize: 16, color: 'rgba(255,255,255,0.3)', letterSpacing: 6, textTransform: 'uppercase', fontFamily: 'Inter, sans-serif', marginBottom: 16}}>
          MODEL COMPARISON
        </div>
        <div style={{fontSize: 64, fontWeight: 900, color: TEXT_COLOR, fontFamily: 'Inter, sans-serif', letterSpacing: -2}}>
          モデル比較
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24}}>
        {categories.map((cat, i) => {
          const opacity = interpolate(frame, [20 + i * 20, 40 + i * 20], [0, 1], {extrapolateRight: 'clamp'});
          const winner = cat.anthropic > cat.openai ? 'anthropic' : 'openai';
          return (
            <div key={cat.name} style={{
              opacity,
              padding: 28,
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 16,
            }}>
              <div style={{fontSize: 20, color: 'rgba(255,255,255,0.6)', fontFamily: 'Inter, sans-serif', marginBottom: 20}}>
                {cat.name}
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: 40, fontWeight: 900, color: ANTHROPIC_COLOR, fontFamily: 'Inter, sans-serif'}}>
                    {cat.anthropic}
                  </div>
                  <div style={{fontSize: 14, color: 'rgba(255,255,255,0.4)', fontFamily: 'Inter, sans-serif'}}>Claude</div>
                </div>
                <div style={{fontSize: 24, color: 'rgba(255,255,255,0.2)', fontFamily: 'Inter, sans-serif'}}>vs</div>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: 40, fontWeight: 900, color: OPENAI_COLOR, fontFamily: 'Inter, sans-serif'}}>
                    {cat.openai}
                  </div>
                  <div style={{fontSize: 14, color: 'rgba(255,255,255,0.4)', fontFamily: 'Inter, sans-serif'}}>GPT-6</div>
                </div>
              </div>
              <div style={{
                marginTop: 12,
                fontSize: 14,
                color: winner === 'anthropic' ? ANTHROPIC_COLOR : OPENAI_COLOR,
                fontFamily: 'Inter, sans-serif',
                textAlign: 'center',
              }}>
                {winner === 'anthropic' ? '✅ Claude優位' : '✅ GPT-6優位'}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// 時価総額セクション
const ValuationSection: React.FC<{frame: number}> = ({frame}) => {
  const anthropicScale = interpolate(frame, [20, 80], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.5))});
  const openaiScale = interpolate(frame, [40, 100], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.5))});

  return (
    <AbsoluteFill style={{padding: '60px 120px', justifyContent: 'center', alignItems: 'center', flexDirection: 'column'}}>
      <div style={{
        opacity: interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
        marginBottom: 80, textAlign: 'center',
      }}>
        <div style={{fontSize: 16, color: 'rgba(255,255,255,0.3)', letterSpacing: 6, textTransform: 'uppercase', fontFamily: 'Inter, sans-serif', marginBottom: 16}}>
          VALUATION 2026
        </div>
        <div style={{fontSize: 64, fontWeight: 900, color: TEXT_COLOR, fontFamily: 'Inter, sans-serif', letterSpacing: -2}}>
          時価総額
        </div>
      </div>

      <div style={{display: 'flex', gap: 80, alignItems: 'flex-end'}}>
        {/* Anthropic */}
        <div style={{textAlign: 'center', transform: `scale(${anthropicScale})`, transformOrigin: 'bottom center'}}>
          <div style={{
            width: 240,
            height: 280,
            background: `linear-gradient(to top, ${ANTHROPIC_COLOR}, ${ANTHROPIC_COLOR}44)`,
            borderRadius: '16px 16px 0 0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 0 60px ${ANTHROPIC_COLOR}60`,
          }}>
            <div style={{fontSize: 36, fontWeight: 900, color: 'white', fontFamily: 'Inter, sans-serif'}}>$965B</div>
          </div>
          <div style={{fontSize: 24, color: ANTHROPIC_COLOR, fontFamily: 'Inter, sans-serif', fontWeight: 700, marginTop: 16}}>
            Anthropic
          </div>
          <div style={{fontSize: 14, color: 'rgba(255,255,255,0.4)', fontFamily: 'Inter, sans-serif', marginTop: 4}}>
            🏆 時価総額1位
          </div>
        </div>

        {/* OpenAI */}
        <div style={{textAlign: 'center', transform: `scale(${openaiScale})`, transformOrigin: 'bottom center'}}>
          <div style={{
            width: 240,
            height: 240,
            background: `linear-gradient(to top, ${OPENAI_COLOR}, ${OPENAI_COLOR}44)`,
            borderRadius: '16px 16px 0 0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 0 60px ${OPENAI_COLOR}60`,
          }}>
            <div style={{fontSize: 36, fontWeight: 900, color: 'white', fontFamily: 'Inter, sans-serif'}}>$852B</div>
          </div>
          <div style={{fontSize: 24, color: OPENAI_COLOR, fontFamily: 'Inter, sans-serif', fontWeight: 700, marginTop: 16}}>
            OpenAI
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// まとめセクション
const ConclusionSection: React.FC<{frame: number}> = ({frame}) => {
  const points = [
    {text: 'Anthropicの収益成長率が圧倒的', color: ANTHROPIC_COLOR},
    {text: 'OpenAIはユーザー数で圧勝（9億人）', color: OPENAI_COLOR},
    {text: 'AnthropicがエンタープライズでOpenAIを逆転', color: ANTHROPIC_COLOR},
    {text: '両社とも2026〜2027年にIPO予定', color: '#f59e0b'},
  ];

  return (
    <AbsoluteFill style={{padding: '60px 120px', justifyContent: 'center'}}>
      <div style={{
        opacity: interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
        marginBottom: 60,
      }}>
        <div style={{fontSize: 64, fontWeight: 900, color: TEXT_COLOR, fontFamily: 'Inter, sans-serif', letterSpacing: -2}}>
          まとめ
        </div>
      </div>

      {points.map((point, i) => {
        const opacity = interpolate(frame, [20 + i * 25, 45 + i * 25], [0, 1], {extrapolateRight: 'clamp'});
        const x = interpolate(frame, [20 + i * 25, 45 + i * 25], [-40, 0], {extrapolateRight: 'clamp'});
        return (
          <div key={i} style={{
            opacity,
            transform: `translateX(${x}px)`,
            display: 'flex',
            alignItems: 'center',
            gap: 24,
            marginBottom: 28,
            padding: '20px 28px',
            background: `${point.color}10`,
            border: `1px solid ${point.color}30`,
            borderRadius: 12,
          }}>
            <div style={{width: 8, height: 8, borderRadius: '50%', background: point.color, flexShrink: 0}} />
            <div style={{fontSize: 26, color: TEXT_COLOR, fontFamily: 'Inter, sans-serif', fontWeight: 400}}>
              {point.text}
            </div>
          </div>
        );
      })}

      {/* CTA */}
      <div style={{
        opacity: interpolate(frame, [130, 160], [0, 1], {extrapolateRight: 'clamp'}),
        marginTop: 40,
        textAlign: 'center',
        fontSize: 22,
        color: 'rgba(255,255,255,0.4)',
        fontFamily: 'Inter, sans-serif',
        letterSpacing: 2,
      }}>
        @AI.Conduit — チャンネル登録お願いします
      </div>
    </AbsoluteFill>
  );
};

// プログレスバー
const ProgressBar: React.FC<{frame: number; totalFrames: number}> = ({frame, totalFrames}) => (
  <div style={{
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 3,
    background: 'rgba(255,255,255,0.05)',
  }}>
    <div style={{
      width: `${(frame / totalFrames) * 100}%`,
      height: '100%',
      background: `linear-gradient(to right, ${ANTHROPIC_COLOR}, ${OPENAI_COLOR})`,
    }} />
  </div>
);

// メインコンポーネント
export const AnthropicVsOpenAI: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  return (
    <AbsoluteFill style={{background: BG_COLOR, fontFamily: 'Inter, sans-serif'}}>
      <Background frame={frame} />

      <Sequence from={0} durationInFrames={180}>
        <IntroSection frame={frame} duration={180} />
      </Sequence>

      <Sequence from={180} durationInFrames={360}>
        <RevenueSection frame={frame - 180} />
      </Sequence>

      <Sequence from={540} durationInFrames={360}>
        <ModelSection frame={frame - 540} />
      </Sequence>

      <Sequence from={900} durationInFrames={360}>
        <ValuationSection frame={frame - 900} />
      </Sequence>

      <Sequence from={1260} durationInFrames={540}>
        <ConclusionSection frame={frame - 1260} />
      </Sequence>

      <ProgressBar frame={frame} totalFrames={durationInFrames} />
    </AbsoluteFill>
  );
};
