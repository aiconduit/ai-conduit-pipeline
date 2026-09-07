import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Sequence, Easing,
} from "remotion";
import React from "react";
import { COLORS } from "../constants";
import { Background } from "../components/Background";
import { GrainVignette } from "../components/GrainVignette";
import { Subtitle, CaptionEntry } from "../components/Subtitle";

const f = (fps: number, s: number) => Math.round(s * fps);

const TimelineItem: React.FC<{
  year: string; text: string; color: string;
  frame: number; fps: number; delay: number;
}> = ({year, text, color, frame, fps, delay}) => {
  const sp = spring({frame: Math.max(0, frame - f(fps, delay)), fps, config:{damping:14}});
  const t = frame / fps;
  const breath = 1 + Math.sin(t * 0.9 + delay) * 0.005;
  return (
    <div style={{
      opacity: interpolate(sp,[0,1],[0,1]),
      transform:`translateX(${interpolate(sp,[0,1],[-40,0])}px) scale(${breath})`,
      display:"flex", alignItems:"flex-start", gap:24, marginBottom:28,
    }}>
      <div style={{
        minWidth:80, fontSize:22, fontWeight:900, color,
        fontFamily:"Inter, sans-serif",
        textShadow:`0 0 20px ${color}60`,
      }}>{year}</div>
      <div style={{
        flex:1, fontSize:24, color:COLORS.textMuted,
        fontFamily:"Inter, sans-serif", lineHeight:1.4,
      }}>{text}</div>
    </div>
  );
};

export const OriginOpenAIScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = frame / fps;

  const exitStart = durationInFrames - f(fps, 0.7);
  const exitO = interpolate(frame, [exitStart, durationInFrames], [1, 0],
    {extrapolateLeft:"clamp", extrapolateRight:"clamp", easing: Easing.in(Easing.cubic)});

  const titleSp = spring({frame: Math.max(0, frame - f(fps,0.2)), fps, config:{damping:14}});
  const titleBreath = 1 + Math.sin(t * 0.7) * 0.003;

  const timeline = [
    {year:"2015", text:"Sam Altman・Elon Musk・Greg Brockmanらが共同創業"},
    {year:"2019", text:"Microsoftから10億ドル投資・営利転換"},
    {year:"2022", text:"ChatGPT公開・5日で100万ユーザー達成"},
    {year:"2024", text:"GPT-4・5と怒涛のリリース"},
    {year:"2026", text:"週間9億人ユーザー・AI最大サービスへ"},
  ];

  const captions: CaptionEntry[] = [
    {startFrame:f(fps,0.2), endFrame:f(fps,4), text:"OpenAIは2015年12月に設立されました。"},
    {startFrame:f(fps,4.5), endFrame:f(fps,9), text:"Sam AltmanやElon Muskら錚々たる顔ぶれが共同創業しました。"},
    {startFrame:f(fps,9.5), endFrame:f(fps,14), text:"2019年にMicrosoftから10億ドルの投資を受け営利転換。"},
    {startFrame:f(fps,14.5), endFrame:f(fps,19), text:"2022年11月、ChatGPTをリリース。わずか5日で100万ユーザー。"},
    {startFrame:f(fps,19.5), endFrame:f(fps,24), text:"これはAI史上最速の成長であり、世界を変えた瞬間でした。"},
    {startFrame:f(fps,24.5), endFrame:f(fps,29), text:"2026年現在、週間9億人のユーザーを抱える世界最大のAIサービスです。"},
  ];

  return (
    <AbsoluteFill style={{opacity:exitO}}>
      <Background seed={1} />
      <AbsoluteFill style={{padding:"60px 120px", justifyContent:"center"}}>
        {/* タイトル */}
        <div style={{
          opacity:interpolate(titleSp,[0,1],[0,1]),
          transform:`translateY(${interpolate(titleSp,[0,1],[30,0])}px) scale(${titleBreath})`,
          marginBottom:50,
        }}>
          <div style={{fontSize:13, color:COLORS.textDim, letterSpacing:7,
            textTransform:"uppercase", fontFamily:"Inter,sans-serif", marginBottom:12}}>
            Origin Story — 2015
          </div>
          <div style={{fontSize:64, fontWeight:900, color:COLORS.openai,
            fontFamily:"Inter,sans-serif", letterSpacing:-3,
            textShadow:`0 0 60px ${COLORS.openai}50`}}>
            OpenAIの誕生
          </div>
          <div style={{
            width:interpolate(titleSp,[0,1],[0,300]), height:3,
            background:`linear-gradient(to right, ${COLORS.openai}, transparent)`,
            borderRadius:2, marginTop:16,
          }} />
        </div>

        {/* タイムライン */}
        {timeline.map((item, i) => (
          <TimelineItem
            key={i}
            year={item.year}
            text={item.text}
            color={COLORS.openai}
            frame={frame}
            fps={fps}
            delay={0.5 + i * 0.18}
          />
        ))}
      </AbsoluteFill>
      <Subtitle captions={captions} />
      <GrainVignette />
    </AbsoluteFill>
  );
};
