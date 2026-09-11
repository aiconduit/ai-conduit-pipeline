import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { useVideoConfig } from "remotion";
import React from "react";
import { VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import { ConclusionScene } from "./scenes/ConclusionScene";
import { GenericScene } from "./scenes/GenericScene";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const SCENE_DATA = {
  safety: {
    title: "安全性哲学", subtitle: "Constitutional AI vs RLHF", color: "#06b6d4", seed: 8,
    bullets: ["Anthropic：Constitutional AI（HHH原則：有益・無害・正直）","AIに原則を与えて自己評価させる独自の手法","OpenAI：RLHFによる安全対策 + 商業展開のバランス","2026年2月：DarioがFBIの制限解除要求を拒否"],
    narration: ["2社を最も分けるのは、AI安全性への哲学です。","AnthropicはConstitutional AIを開発。AIに原則を与えて自己評価させる手法です。","有益で、無害で、正直にというHHH原則が全モデルの基盤となっています。","OpenAIもRLHFによる安全対策を実施していますが、商業展開とのバランスが常に問われます。","2026年2月、DarioはFBIからClaudeの安全制限を解除するよう要求されましたが、これを拒否しました。","AIが社会に組み込まれるにつれ、この哲学の違いはより重要になっていきます。"],
    audioFile: "s09_safety.mp3",
  },
  partners: {
    title: "パートナー戦略", subtitle: "Microsoft vs Amazon・Google", color: "#10b981", seed: 9,
    bullets: ["OpenAI：MicrosoftがAzure経由で世界展開、$27Bの株式保有","Anthropic：AmazonがAWS経由で展開、$8Bを投資","Anthropic：GoogleもAnthropic株を数十億ドル保有","AI覇権争いはMicrosoft vs Amazon・Google連合の代理戦争"],
    narration: ["両社のパートナー戦略も対照的です。","OpenAIはMicrosoftと深く結びついています。Microsoftは270億ドルの株式を保有し、Azure経由でGPTを全世界に提供します。","AnthropicはAmazonと戦略的パートナーシップを締結。Amazonは80億ドルを投資しています。","またGoogleも数十億ドルを投資しており、Google Cloudでも利用可能です。","この構図を見ると、AI覇権争いはMicrosoft陣営とAmazon・Google連合の代理戦争とも言えます。"],
    audioFile: "s10_partners.mp3",
  },
  future: {
    title: "今後の展望", subtitle: "AGIへの競争", color: "#f59e0b", seed: 10,
    bullets: ["OpenAI：Stargate Project → $5000億のデータセンター建設","GPT-6リリース発表「AGI時代へようこそ」","Anthropic：「AGIは2〜3年以内に来るかもしれない」","両社ともに$1兆超の時価総額を目指してIPOへ"],
    stat: { label: "Stargate投資規模", value: "$500B", color: "#f59e0b" },
    narration: ["2社が最終的に目指すものは何か。AGI、つまり汎用人工知能です。","OpenAIのGreg Brockmanは、GPT-6のリリース発表を「AGI時代へようこそ」という言葉で締めくくりました。","OpenAIはStargateプロジェクトで5000億ドルのデータセンター建設を進めています。","一方AnthropicのDarioは「AGIは2〜3年以内に来るかもしれない」と発言しています。","しかしその開発は安全性を担保しながら進めるべきだという姿勢を崩しません。","IPOレースも激化しており、Anthropicは10月、OpenAIは9月の上場を目指しています。"],
    audioFile: "s11_future.mp3",
  },
};

export const DocumentaryPart3: React.FC = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s09_safety)}>
      <GenericScene data={SCENE_DATA.safety} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s10_partners)}>
      <GenericScene data={SCENE_DATA.partners} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s11_future)}>
      <GenericScene data={SCENE_DATA.future} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s12_conclusion)}>
      <ConclusionScene />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
