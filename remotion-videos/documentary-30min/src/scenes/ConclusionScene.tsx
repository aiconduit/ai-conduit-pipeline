import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Easing,
} from "remotion";
import React from "react";
import { COLORS } from "../constants";
import { Background } from "../components/Background";
import { GrainVignette } from "../components/GrainVignette";
import { Subtitle, CaptionEntry } from "../components/Subtitle";

const f = (fps: number, s: number) => Math.round(s * fps);

export const ConclusionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = frame / fps;

  const exitStart = durationInFrames - f(fps,0.7);
  const exitO = interpolate(frame,[exitStart,durationInFrames],[1,0],
    {extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:Easing.in(Easing.cubic)});

  const titleSp = spring({frame:Math.max(0,frame-f(fps,0.2)),fps,config:{damping:14}});

  const points = [
    {text:"Anthropicの収益成長率が圧倒的（15ヶ月で33倍）", color:COLORS.anthropic},
    {text:"OpenAIはユーザー規模で圧倒（週9億人）", color:COLORS.openai},
    {text:"AnthropicがエンタープライズでOpenAIを逆転", color:COLORS.anthropic},
    {text:"両社2026〜2027年にIPO予定", color:COLORS.gold},
    {text:"AGIは2〜3年以内という見方が主流", color:COLORS.accent},
  ];

  const captions: CaptionEntry[] = [
    {startFrame:f(fps,0.2), endFrame:f(fps,5), text:"Anthropic vs OpenAI。どちらが勝つのか？"},
    {startFrame:f(fps,5.5), endFrame:f(fps,10), text:"答えは「どちらも勝者になり得る」です。"},
    {startFrame:f(fps,10.5), endFrame:f(fps,15), text:"OpenAIは規模、Anthropicは効率で競い合う構図です。"},
    {startFrame:f(fps,15.5), endFrame:f(fps,20), text:"安全性を重視するAnthropicは長期的に有利かもしれません。"},
    {startFrame:f(fps,20.5), endFrame:f(fps,24), text:"チャンネル登録とコメントをお待ちしています！"},
  ];

  return (
    <AbsoluteFill style={{opacity:exitO}}>
      <Background seed={11} />
      <AbsoluteFill style={{padding:"60px 140px", justifyContent:"center"}}>
        <div style={{
          opacity:interpolate(titleSp,[0,1],[0,1]),
          transform:`translateY(${interpolate(titleSp,[0,1],[30,0])}px)`,
          marginBottom:50,
        }}>
          <div style={{fontSize:64,fontWeight:900,color:"#fff",
            fontFamily:"Inter,sans-serif",letterSpacing:-3}}>まとめ</div>
          <div style={{
            width:interpolate(titleSp,[0,1],[0,200]),height:3,
            background:`linear-gradient(to right,${COLORS.accent},transparent)`,
            borderRadius:2,marginTop:16,
          }}/>
        </div>
        {points.map((p,i)=>{
          const sp = spring({frame:Math.max(0,frame-f(fps,0.5+i*0.15)),fps,config:{damping:12}});
          const breath = 1+Math.sin(t*0.9+i*0.7)*0.005;
          return (
            <div key={i} style={{
              opacity:interpolate(sp,[0,1],[0,1]),
              transform:`translateX(${interpolate(sp,[0,1],[-40,0])}px) scale(${breath})`,
              display:"flex", alignItems:"center", gap:20, marginBottom:22,
              padding:"16px 22px",
              background:`${p.color}0a`,
              border:`1px solid ${p.color}20`, borderRadius:12,
            }}>
              <div style={{width:8,height:8,borderRadius:"50%",background:p.color,
                boxShadow:`0 0 12px ${p.color}`,flexShrink:0}}/>
              <div style={{fontSize:24,color:"#fff",fontFamily:"Inter,sans-serif",fontWeight:400}}>{p.text}</div>
            </div>
          );
        })}
        {(()=>{
          const ctaSp = spring({frame:Math.max(0,frame-f(fps,1.5)),fps,config:{damping:12}});
          return (
            <div style={{
              opacity:interpolate(ctaSp,[0,1],[0,1]),
              marginTop:36,textAlign:"center",
              fontSize:18,color:COLORS.textDim,
              fontFamily:"Inter,sans-serif",letterSpacing:4,
            }}>@AI.Conduit — チャンネル登録お願いします</div>
          );
        })()}
      </AbsoluteFill>
      <Subtitle captions={captions}/>
      <GrainVignette/>
    </AbsoluteFill>
  );
};
