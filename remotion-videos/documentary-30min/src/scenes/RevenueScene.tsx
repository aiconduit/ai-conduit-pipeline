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

const Bar: React.FC<{
  label: string; value: number; maxVal: number; color: string;
  frame: number; fps: number; delay: number; unit?: string;
}> = ({label, value, maxVal, color, frame, fps, delay, unit="$"}) => {
  const sp = spring({frame: Math.max(0, frame - f(fps,delay)), fps, config:{damping:10}});
  const t = frame / fps;
  const breath = 1 + Math.sin(t * 1.1 + delay) * 0.006;
  return (
    <div style={{marginBottom:32, transform:`scale(${breath})`}}>
      <div style={{display:"flex", justifyContent:"space-between", marginBottom:12, alignItems:"baseline"}}>
        <span style={{fontSize:22, color:COLORS.textMuted, fontFamily:"Inter,sans-serif"}}>{label}</span>
        <span style={{
          opacity:interpolate(sp,[0.6,1],[0,1],{extrapolateRight:"clamp"}),
          fontSize:36, fontWeight:900, color,
          fontFamily:"Inter,sans-serif",
          textShadow:`0 0 20px ${color}70`,
        }}>{unit}{value}B</span>
      </div>
      <div style={{height:12, background:"rgba(255,255,255,0.06)", borderRadius:6, overflow:"hidden"}}>
        <div style={{
          width:`${interpolate(sp,[0,1],[0,(value/maxVal)*100])}%`,
          height:"100%", borderRadius:6,
          background:`linear-gradient(to right, ${color}, ${color}88)`,
          boxShadow:`0 0 20px ${color}60`,
        }} />
      </div>
    </div>
  );
};

export const RevenueScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = frame / fps;

  const exitStart = durationInFrames - f(fps,0.7);
  const exitO = interpolate(frame,[exitStart,durationInFrames],[1,0],
    {extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:Easing.in(Easing.cubic)});

  const titleSp = spring({frame:Math.max(0,frame-f(fps,0.2)),fps,config:{damping:14}});
  const titleBreath = 1 + Math.sin(t*0.8)*0.003;
  const noteSp = spring({frame:Math.max(0,frame-f(fps,1.5)),fps,config:{damping:12}});

  const captions: CaptionEntry[] = [
    {startFrame:f(fps,0.2), endFrame:f(fps,5), text:"Anthropicの年間収益は2026年4月に300億ドルへ急成長。"},
    {startFrame:f(fps,5.5), endFrame:f(fps,10), text:"わずか15ヶ月で33倍という驚異的な成長率です。"},
    {startFrame:f(fps,10.5), endFrame:f(fps,15), text:"OpenAIの収益は約250億ドルで依然リードしています。"},
    {startFrame:f(fps,15.5), endFrame:f(fps,20), text:"しかしAnthropicのエンタープライズシェアが逆転しました。"},
    {startFrame:f(fps,20.5), endFrame:f(fps,25), text:"エンタープライズ支出シェア: Anthropic 34.4% vs OpenAI 32.3%"},
    {startFrame:f(fps,25.5), endFrame:f(fps,29), text:"収益構造の効率性でもAnthropicが上回っています。"},
  ];

  return (
    <AbsoluteFill style={{opacity:exitO}}>
      <Background seed={5} />
      <AbsoluteFill style={{padding:"60px 160px", justifyContent:"center"}}>
        <div style={{
          opacity:interpolate(titleSp,[0,1],[0,1]),
          transform:`translateY(${interpolate(titleSp,[0,1],[30,0])}px) scale(${titleBreath})`,
          marginBottom:60,
        }}>
          <div style={{fontSize:13, color:COLORS.textDim, letterSpacing:7,
            textTransform:"uppercase", fontFamily:"Inter,sans-serif", marginBottom:12}}>
            Annual Revenue Run-Rate · 2026
          </div>
          <div style={{fontSize:64, fontWeight:900, color:"#fff",
            fontFamily:"Inter,sans-serif", letterSpacing:-3}}>収益比較</div>
          <div style={{
            width:interpolate(titleSp,[0,1],[0,280]),height:3,
            background:`linear-gradient(to right,${COLORS.anthropic},transparent)`,
            borderRadius:2, marginTop:16,
          }}/>
        </div>
        <Bar label="Anthropic ARR" value={30} maxVal={35} color={COLORS.anthropic} frame={frame} fps={fps} delay={0.4}/>
        <Bar label="OpenAI ARR" value={25} maxVal={35} color={COLORS.openai} frame={frame} fps={fps} delay={0.6}/>
        <div style={{
          opacity:interpolate(noteSp,[0,1],[0,1]),
          transform:`translateY(${interpolate(noteSp,[0,1],[20,0])}px)`,
          marginTop:32, padding:"18px 24px",
          background:`${COLORS.anthropic}10`,
          border:`1px solid ${COLORS.anthropic}25`, borderRadius:14,
        }}>
          <span style={{fontSize:20,color:COLORS.anthropic,fontFamily:"Inter,sans-serif",fontWeight:600}}>
            🚀 Anthropic: 15ヶ月で33倍成長（$1B → $30B）
          </span>
        </div>
      </AbsoluteFill>
      <Subtitle captions={captions}/>
      <GrainVignette/>
    </AbsoluteFill>
  );
};
