import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { useVideoConfig } from "remotion";
import React from "react";
import { VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import { HookScene } from "./scenes/HookScene";
import { GenericScene } from "./scenes/GenericScene";
import { WebScreenScene } from "./scenes/WebScreenScene";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const SCENES = {
  origin_openai: { title: "OpenAIの誕生", subtitle: "2015年 · 非営利→営利", color: "#10b981", seed: 1, bullets: ["2015年12月、Sam AltmanとElon Muskら共同創業","当初は非営利。AIを人類全体の利益のために開発","Microsoftから総額$130Bを調達","2022年11月、ChatGPTリリース"], stat: { label: "週間アクティブユーザー", value: "9億人", color: "#10b981" }, narration: ["OpenAIは2015年12月に設立されました。","Sam Altman、Elon Musk、Greg Brockmanら錚々たる顔ぶれが共同創業しました。","当初は非営利組織として設立されました。","2022年11月、ChatGPTをリリース。わずか5日で100万ユーザーを獲得しました。"], audioFile: "s03_origin_openai.mp3" },
  anthropic_birth: { title: "Anthropicの誕生", subtitle: "2021年 · 安全性を最優先", color: "#a78bfa", seed: 2, bullets: ["2021年1月、Dario Amodeiと8人のOpenAI研究者が退社","設立理念：AIを安全に、人類のために開発する","19ヶ月で$1B → $65B ARRへ、史上最速の成長","企業顧客が収益の80%を占める"], stat: { label: "ARR成長（19ヶ月）", value: "×65", color: "#a78bfa" }, narration: ["2020年末、OpenAIの内部で亀裂が生じていました。","Dario Amodeiは会社の方向性に疑問を持ち始めます。","2021年1月、DarioはAnthropicを設立します。","2026年現在、ARRは650億ドルに達しました。"], audioFile: "s05_anthropic_birth.mp3" },
  split: { title: "決別の真相", subtitle: "安全性 vs 商業主義", color: "#ef4444", seed: 3, bullets: ["Dario：「AIが強力になるほど安全性に注力すべき」","OpenAI：Microsoftとの連携で急速に商業展開","哲学の違いが2社の戦略を根本から分ける","2026年2月、DarioはFBIの安全制限解除要求を拒否"], stat: { label: "OpenAI 2025年損失", value: "$20.9B", color: "#ef4444" }, narration: ["なぜDarioはOpenAIを去ったのか。","Darioは「AIが非常に強力になりうると確信した」と語っています。","OpenAIは普及を優先、Anthropicは安全性を優先。","2026年2月、DarioはFBIからの制限解除要求を拒否しました。"], audioFile: "s06_split.mp3" },
  safety_vs_growth: { title: "2つの哲学", subtitle: "安全性 vs 成長速度", color: "#06b6d4", seed: 12, bullets: ["Anthropic：Constitutional AI・HHH原則","OpenAI：RLHF + 商業展開のバランス","どちらが正しいかは今も議論中","ユーザーは最終的に両方を使う"], narration: ["2社の根本的な違いは哲学にあります。","Anthropicは安全性を最優先。Constitutional AIという独自手法を開発しました。","OpenAIは普及速度を優先します。","この哲学の違いが製品・価格・対象市場の全てに影響しています。"], audioFile: "s07_safety_vs_growth.mp3" },
};

const WEB_SCENES = {
  anthropic_web: { title: "Anthropic公式サイト", subtitle: "anthropic.com", color: "#a78bfa", screenshotFile: "anthropic_home.png", caption: "ClaudeとAI安全研究を軸に急成長。シンプルで洗練されたブランド戦略。", narration: ["これがAnthropicの公式サイトです。","シンプルで洗練されたデザインが印象的です。","安全性を前面に打ち出したブランド戦略が伝わります。"], audioFile: "s02_intro.mp3" },
  chatgpt_web: { title: "ChatGPT画面", subtitle: "chatgpt.com", color: "#10b981", screenshotFile: "chatgpt.png", caption: "週間9億人が使う世界最大のAIサービス。シンプルなUIが普及を加速。", narration: ["これが週間9億人のユーザーが使うChatGPTです。","シンプルで直感的なUIが爆発的な普及を支えました。","誰でも使えるアクセシビリティがOpenAIの強みです。"], audioFile: "s04_chatgpt.mp3" },
  claude_web: { title: "Claude画面", subtitle: "claude.ai", color: "#a78bfa", screenshotFile: "claude_ai.png", caption: "長文理解・コーディング・分析に特化。企業ユーザーから高い評価。", narration: ["こちらはClaudeのインターフェースです。","長文の理解と精密な分析能力が際立っています。","企業のプロフェッショナルユーザーから特に高い評価を受けています。"], audioFile: "s08_models_claude.mp3" },
};

export const DocumentaryPart1: React.FC = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s01_hook)}><HookScene /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s02_intro)}><WebScreenScene data={WEB_SCENES.anthropic_web} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s03_openai_birth)}><GenericScene data={SCENES.origin_openai} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s04_chatgpt)}><WebScreenScene data={WEB_SCENES.chatgpt_web} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s05_anthropic_birth)}><GenericScene data={SCENES.anthropic_birth} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s06_split_reason)}><GenericScene data={SCENES.split} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s07_safety_vs_growth)}><GenericScene data={SCENES.safety_vs_growth} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s08_models_claude)}><WebScreenScene data={WEB_SCENES.claude_web} /></TransitionSeries.Sequence>
  </TransitionSeries>
);
