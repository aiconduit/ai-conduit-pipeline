import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { useVideoConfig } from "remotion";
import React from "react";
import { VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import { RevenueScene } from "./scenes/RevenueScene";
import { GenericScene } from "./scenes/GenericScene";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const SCENE_DATA = {
  models: {
    title: "モデル比較", subtitle: "Claude Fable vs GPT-6 Astra", color: "#f59e0b", seed: 4,
    bullets: ["コーディング：Claude 72.7% vs GPT-6 67%（SWE-bench）","長文理解・推論：Claudeが優位","マルチモーダル・コスパ：GPT-6が優位","APIの価格差：フラッグシップで1Mトークン50セント以下"],
    stat: { label: "Claude Code 年間収益", value: "$2.5B", color: "#f59e0b" },
    narration: ["2026年9月現在、2社の最新フラッグシップモデルを比較します。","コーディング性能：SWE-benchでClaudeが72.7%、GPT-6が67%です。","長文理解でもClaudeが優位です。","一方、マルチモーダルとミニモデルのコスパではGPT-6が上回っています。","Claude Codeは年間収益25億ドルを達成し、開発者市場で急速に普及しています。","多くの企業が両方を本番環境で使用しているのが現実です。"],
    audioFile: "s05_models.mp3",
  },
  funding: {
    title: "IPOレース", subtitle: "2026年 最大の資金調達", color: "#f59e0b", seed: 6,
    bullets: ["Anthropic：$965B時価総額でIPO申請（6月1日）→ 10月上場予定","OpenAI：$852Bで$122Bを調達、S-1申請（6月8日）→ 9月上場予定","Anthropic IPO目標：$2兆ドル以上","2社合計で史上最大規模のIPOレース"],
    stat: { label: "2社合計時価総額", value: "$1.82T", color: "#f59e0b" },
    narration: ["資金調達でも2社は熾烈な競争を繰り広げています。","Anthropicは2026年5月に9650億ドルの時価総額でIPO申請。2兆ドル以上の上場時価総額を目指し、10月のIPOを予定しています。","OpenAIは3月に8520億ドルで1220億ドルを調達。6月8日に極秘のS-1を申請し、2026年9月の上場を目指しています。","両社合計で1兆8千億ドル近い時価総額が市場に登場することになります。","これはソフトウェア史上最大規模のIPOレースです。"],
    audioFile: "s07_funding.mp3",
  },
  business: {
    title: "ビジネスモデル", subtitle: "エンタープライズ vs コンシューマー", color: "#a78bfa", seed: 7,
    bullets: ["OpenAI：コンシューマー重視 → ChatGPT 9億人","Anthropic：エンタープライズ重視 → 収益の80%が企業","年間$100万超の企業顧客が7倍に増加","高マージンのAPI収益がAnthropicの黒字化を支える"],
    stat: { label: "Anthropic エンタープライズ比率", value: "80%", color: "#a78bfa" },
    narration: ["2社のビジネスモデルは根本的に異なります。","OpenAIはコンシューマー重視。ChatGPTの9億人ユーザーが象徴するように、一般消費者への普及を最優先します。","一方Anthropicはエンタープライズ重視。収益の80%が企業顧客からです。","年間100万ドル以上支払う企業顧客が7倍に増加しました。","この違いは利益率に直結します。エンタープライズAPIはコンシューマー向けより高マージンです。","Anthropicが初の黒字化を達成できた背景にはこのビジネスモデルの優位性があります。"],
    audioFile: "s08_business.mp3",
  },
};

export const DocumentaryPart2: React.FC = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s05_models)}>
      <GenericScene data={SCENE_DATA.models} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s06_revenue)}>
      <RevenueScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s07_funding)}>
      <GenericScene data={SCENE_DATA.funding} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s08_business)}>
      <GenericScene data={SCENE_DATA.business} />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
