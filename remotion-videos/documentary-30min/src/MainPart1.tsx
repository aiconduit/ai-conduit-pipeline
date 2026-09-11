import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { useVideoConfig } from "remotion";
import React from "react";
import { VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import { IntroScene } from "./scenes/IntroScene";
import { GenericScene } from "./scenes/GenericScene";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const SCENE_DATA = {
  origin_openai: {
    title: "OpenAIの誕生", subtitle: "2015年 · 非営利→営利", color: "#10b981", seed: 1,
    bullets: ["2015年12月、Sam AltmanとElon Muskら共同創業","当初は非営利。AIを人類全体の利益のために開発","2022年11月、ChatGPTリリース → 5日で100万ユーザー","2026年8月時点で週間9億人が利用するAIサービスへ"],
    stat: { label: "週間アクティブユーザー", value: "9億人", color: "#10b981" },
    narration: ["OpenAIは2015年12月に設立されました。","Sam Altman、Elon Musk、Greg Brockmanら錚々たる顔ぶれが共同創業しました。","当初は非営利組織として、AIを人類全体の利益のために開発することを掲げました。","2019年にMicrosoftから10億ドルの投資を受け、営利組織へと転換しました。","そして2022年11月、ChatGPTをリリース。わずか5日で100万ユーザーを獲得しました。","2026年現在、ChatGPTは週間9億人のユーザーを抱える世界最大のAIサービスです。"],
    audioFile: "s02_origin_openai.mp3",
  },
  origin_anthropic: {
    title: "Anthropicの誕生", subtitle: "2021年 · 安全性を最優先", color: "#a78bfa", seed: 2,
    bullets: ["2021年1月、Dario Amodeiと8人のOpenAI研究者が退社","設立理念：AIを安全に、人類のために開発する","19ヶ月で$1B → $65B ARRへ、史上最速の成長","企業顧客が収益の80%を占める強固なビジネスモデル"],
    stat: { label: "ARR成長（19ヶ月）", value: "×65", color: "#a78bfa" },
    narration: ["2020年末、OpenAIの内部で亀裂が生じていました。","研究担当副社長のDario Amodeiは、会社の方向性に疑問を持ち始めます。","2021年1月、Darioは妹のDaniellaを含む8人のOpenAI研究者と共に退社し、Anthropicを設立します。","設立の理念は明確でした。AIを安全に、人類のために開発する。","2026年現在、AnthropicのARRは650億ドルに達し、19ヶ月で65倍という歴史的な成長を遂げました。","企業顧客が収益の80%を占める強固なビジネスモデルを確立しています。"],
    audioFile: "s03_origin_anthropic.mp3",
  },
  split: {
    title: "決別の真相", subtitle: "安全性 vs 商業主義", color: "#ef4444", seed: 3,
    bullets: ["Dario：「AIが強力になるほど安全性に注力すべき」","OpenAI：Microsoftとの連携でChatGPTを急速に商業展開","哲学の違いが2社の戦略を根本から分けることになる","2026年2月、DarioはFBIの安全制限解除要求を拒否"],
    stat: { label: "OpenAI 2025年損失", value: "$20.9B", color: "#ef4444" },
    narration: ["なぜDarioはOpenAIを去ったのか。その真相を掘り下げます。","Darioは後のインタビューで「AIが非常に強力になりうると確信した」と語っています。","だからこそ安全性に注力すべきだという考えがあったのです。","一方のOpenAIは、MicrosoftとのパートナーシップによりChatGPTを急速に商業展開していきました。","OpenAIは普及を優先、Anthropicは安全性を優先。この哲学の違いが、2社の戦略を根本から分けることになります。","2026年2月、DarioはFBIからClaudeの安全制限を解除するよう要求されましたが、これを拒否しました。"],
    audioFile: "s04_split.mp3",
  },
};

export const DocumentaryPart1: React.FC = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s01_intro)}>
      <IntroScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s02_origin_openai)}>
      <GenericScene data={SCENE_DATA.origin_openai} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s03_origin_anthropic)}>
      <GenericScene data={SCENE_DATA.origin_anthropic} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s04_split)}>
      <GenericScene data={SCENE_DATA.split} />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
