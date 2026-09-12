import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { useVideoConfig } from "remotion";
import React from "react";
import { VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import { GenericScene } from "./scenes/GenericScene";
import { ConclusionScene } from "./scenes/ConclusionScene";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const SCENES = {
  partners_ms: { title: "Microsoft連携", subtitle: "OpenAIの最大の武器", color: "#10b981", seed: 17, bullets: ["MicrosoftがAzure経由でGPTを世界展開","Microsoft株式保有額：$27B","Office・Teamsにフル統合","365 Copilotで企業ユーザー直撃"], narration: ["OpenAIとMicrosoftの連携は業界最大の提携です。","MicrosoftはAzure経由でGPTを全世界に提供しています。","Office・TeamsへのCopilot統合により、数億人のビジネスユーザーに届きます。","Microsoftの株式保有額は270億ドルに達しています。"], audioFile: "s17_partners_ms.mp3" },
  partners_aws: { title: "Amazon・Google連携", subtitle: "Anthropicの強力な後ろ盾", color: "#a78bfa", seed: 18, bullets: ["AmazonがAWS経由でClaudeを展開","Amazon投資額：$8B","Google・GCPでも利用可能","Microsoft vs Amazon・Google連合の代理戦争"], narration: ["AnthropicはAmazonと戦略的パートナーシップを締結しています。","AmazonはAWS経由でClaudeを展開し、80億ドルを投資しています。","GoogleもAnthropicに数十億ドルを投資しており、Google Cloudでも利用可能です。","AI覇権争いはMicrosoft陣営とAmazon・Google連合の代理戦争とも言えます。"], audioFile: "s18_partners_aws.mp3" },
  safety_const: { title: "Constitutional AI", subtitle: "Anthropicの独自技術", color: "#06b6d4", seed: 8, bullets: ["AIに原則を与えて自己評価させる手法","HHH原則：有益・無害・正直","全Claudeモデルの基盤技術","業界標準になりつつある安全手法"], narration: ["AnthropicはConstitutional AIを開発しました。","AIに原則を与えて自己評価させるという革新的な手法です。","有益で、無害で、正直にというHHH原則が全てのClaudeモデルの基盤です。","この手法は業界全体に影響を与えています。"], audioFile: "s19_safety_constitutional.mp3" },
  safety_rlhf: { title: "OpenAIの安全対策", subtitle: "RLHF & モデレーション", color: "#10b981", seed: 9, bullets: ["RLHF（人間のフィードバックから強化学習）","コンテンツモデレーション専門チーム","商業展開とのバランスが課題","Safety vs Capability のトレードオフ"], narration: ["OpenAIもRLHFで安全対策を実施しています。","コンテンツモデレーションの専門チームを持ちます。","しかし商業展開のスピードとのバランスが常に問われています。","安全性と能力のトレードオフは業界全体の課題です。"], audioFile: "s20_safety_rlhf.mp3" },
  fbi: { title: "FBI拒否事件", subtitle: "2026年2月の転換点", color: "#ef4444", seed: 19, bullets: ["FBIがDarioに「Claudeの安全制限解除」を要求","Darioは即座に拒否","「安全性は交渉の対象ではない」","業界に大きな衝撃を与えた決断"], narration: ["2026年2月、衝撃的な事件が起きました。","FBIがDario CEOに対し、Claudeの安全制限を解除するよう要求したのです。","Darioはこれを即座に拒否しました。","この決断はAnthropicの安全性への姿勢を世界に示す転換点となりました。"], audioFile: "s21_fbi.mp3" },
  future_agi: { title: "AGIへの競争", subtitle: "次の10年の覇権争い", color: "#f59e0b", seed: 20, bullets: ["OpenAI：「AGI時代へようこそ」GPT-6発表時の言葉","Anthropic：「AGIは2〜3年以内に来るかもしれない」","OpenAI Stargate：$5000億のデータセンター建設","どちらが先に汎用AIを達成するか"], stat: { label: "Stargate投資規模", value: "$500B", color: "#f59e0b" }, narration: ["2社が最終的に目指すものはAGI、汎用人工知能です。","OpenAIのGreg BrockmanはGPT-6発表を「AGI時代へようこそ」と締めくくりました。","OpenAIはStargateプロジェクトで5000億ドルのデータセンター建設を進めています。","AnthropicのDarioは「AGIは2〜3年以内に来るかもしれない」と発言しています。"], audioFile: "s22_future_agi.mp3" },
  stargate: { title: "Stargateプロジェクト", subtitle: "AIインフラへの$5000億投資", color: "#f59e0b", seed: 10, bullets: ["OpenAI・Microsoft・SoftBankが主導","$5000億（約75兆円）のデータセンター建設","米国全土にAIコンピューティング基盤を整備","Anthropicも独自のコンピュートを計画中"], stat: { label: "総投資規模", value: "$500B", color: "#f59e0b" }, narration: ["OpenAIはStargateプロジェクトを立ち上げました。","Microsoft・SoftBankと共同で5000億ドルを投資します。","米国全土にAIコンピューティング基盤を整備する壮大な計画です。","AnthropicもAmazonと共に独自のコンピュート投資を進めています。"], audioFile: "s23_stargate.mp3" },
};

export const DocumentaryPart3: React.FC = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s17_partners_ms)}><GenericScene data={SCENES.partners_ms} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s18_partners_aws)}><GenericScene data={SCENES.partners_aws} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s19_safety_constitutional)}><GenericScene data={SCENES.safety_const} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s20_safety_rlhf)}><GenericScene data={SCENES.safety_rlhf} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s21_fbi)}><GenericScene data={SCENES.fbi} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s22_future_agi)}><GenericScene data={SCENES.future_agi} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s23_stargate)}><GenericScene data={SCENES.stargate} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s24_conclusion)}><ConclusionScene /></TransitionSeries.Sequence>
  </TransitionSeries>
);
