import { useVideoConfig } from "remotion";
import { TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { linearTiming } from "@remotion/transitions";
import React from "react";
import { VIDEO_FPS, COLORS, SECTION_DURATION } from "./constants";
import { IntroScene } from "./scenes/IntroScene";
import { RevenueScene } from "./scenes/RevenueScene";
import { ConclusionScene } from "./scenes/ConclusionScene";
import { GenericScene, SceneData } from "./scenes/GenericScene";

const sec = (s: number) => Math.round(s * VIDEO_FPS);
const T = sec(20); // トランジション20フレーム

// 各シーンのデータ
const SCENE_DATA: Record<string, SceneData> = {
  origin_openai: {
    title: "OpenAIの誕生",
    subtitle: "2015年 · 非営利→営利",
    color: COLORS.openai,
    seed: 1,
    bullets: [
      "2015年12月、Sam AltmanとElon Muskら共同創業",
      "当初は非営利。AIを人類全体の利益のために開発",
      "2022年11月、ChatGPTリリース → 5日で100万ユーザー",
      "2026年8月時点で週間9億人が利用するAIサービスへ",
    ],
    stat: { label: "週間アクティブユーザー", value: "9億人", color: COLORS.openai },
    narration: [
      "OpenAIは2015年12月に設立されました。",
      "Sam Altman、Elon Musk、Greg Brockmanら錚々たる顔ぶれが共同創業しました。",
      "当初は非営利組織として、AIを人類全体の利益のために開発することを掲げました。",
      "2019年にMicrosoftから10億ドルの投資を受け、営利組織へと転換。",
      "そして2022年11月、ChatGPTをリリース。わずか5日で100万ユーザーを獲得しました。",
      "2026年現在、ChatGPTは週間9億人のユーザーを抱える世界最大のAIサービスです。",
    ],
  },
  origin_anthropic: {
    title: "Anthropicの誕生",
    subtitle: "2021年 · 安全性を最優先",
    color: COLORS.anthropic,
    seed: 2,
    bullets: [
      "2021年1月、Dario Amodeiと8人のOpenAI研究者が退社",
      "設立理念：AIを安全に、人類のために開発する",
      "19ヶ月で$1B → $65B ARRへ、史上最速の成長",
      "企業顧客が収益の80%を占める強固なビジネスモデル",
    ],
    stat: { label: "ARR成長（19ヶ月）", value: "×65", color: COLORS.anthropic },
    narration: [
      "2020年末、OpenAIの内部で亀裂が生じていました。",
      "研究担当副社長のDario Amodeiは、会社の方向性に疑問を持ち始めます。",
      "2021年1月、Darioは妹のDaniellaを含む8人のOpenAI研究者と共に退社し、Anthropicを設立します。",
      "設立の理念は明確でした。AIを安全に、人類のために開発する。",
      "2026年現在、AnthropicのARRは650億ドルに達し、19ヶ月で65倍という歴史的な成長を遂げました。",
      "企業顧客が収益の80%を占める強固なビジネスモデルを確立しています。",
    ],
  },
  split: {
    title: "決別の真相",
    subtitle: "安全性 vs 商業主義",
    color: COLORS.red,
    seed: 3,
    bullets: [
      "Dario：「AIが強力になるほど安全性に注力すべき」",
      "OpenAI：Microsoftとの連携でChatGPTを急速に商業展開",
      "哲学の違いが2社の戦略を根本から分けることになる",
      "2026年2月、DarioはFBIの安全制限解除要求を拒否",
    ],
    stat: { label: "OpenAI 2025年損失", value: "$20.9B", color: COLORS.red },
    narration: [
      "なぜDarioはOpenAIを去ったのか。その真相を掘り下げます。",
      "Darioは後のインタビューで「GPTモデルを作る過程で、AIが非常に強力になりうると確信した」と語っています。",
      "だからこそ安全性に注力すべきだという考えがあったのです。",
      "一方のOpenAIは、MicrosoftとのパートナーシップによりChatGPTを急速に商業展開していきました。",
      "OpenAIは普及を優先、Anthropicは安全性を優先。この哲学の違いが、2社の戦略を根本から分けることになります。",
      "2026年2月、DarioはFBIからClaudeの安全制限を解除するよう要求されましたが、これを拒否。政府案件を失ってでも原則を守りました。",
    ],
  },
  models: {
    title: "モデル比較",
    subtitle: "Claude Fable vs GPT-6 Astra",
    color: COLORS.gold,
    seed: 4,
    bullets: [
      "コーディング：Claude 72.7% vs GPT-6 67%（SWE-bench）",
      "長文理解・推論：Claudeが優位",
      "マルチモーダル・コスパ：GPT-6が優位",
      "APIの価格差：フラッグシップで1Mトークン50セント以下",
    ],
    stat: { label: "Claude Code 年間収益", value: "$2.5B", color: COLORS.gold },
    narration: [
      "2026年9月現在、2社の最新フラッグシップモデルを比較します。",
      "コーディング性能：SWE-benchでClaudeが72.7%、GPT-6が67%。",
      "長文理解でもClaudeが優位です。",
      "一方、マルチモーダルとミニモデルのコスパではGPT-6が上回っています。",
      "Claude Codeは年間収益25億ドルを達成し、開発者市場で急速に普及しています。",
      "多くの企業が両方を本番環境で使用しているのが現実です。",
    ],
  },
  funding: {
    title: "IPOレース",
    subtitle: "2026年 最大の資金調達",
    color: COLORS.gold,
    seed: 6,
    bullets: [
      "Anthropic：$965B時価総額でIPO申請（6月1日）→ 10月上場予定",
      "OpenAI：$852Bで$122Bを調達、S-1申請（6月8日）→ 9月上場予定",
      "Anthropic IPO目標：$2兆ドル以上",
      "2社合計で史上最大規模のIPOレースが展開",
    ],
    stat: { label: "2社合計時価総額", value: "$1.82T", color: COLORS.gold },
    narration: [
      "資金調達でも2社は熾烈な競争を繰り広げています。",
      "Anthropicは2026年5月に9650億ドルの時価総額でIPO申請。2兆ドル以上の上場時価総額を目指し、10月のIPOを予定しています。",
      "OpenAIは3月に8520億ドルで1220億ドルを調達。6月8日に極秘のS-1を申請し、2026年9月の上場を目指しています。",
      "両社合計で1兆8千億ドル近い時価総額が市場に登場することになります。",
      "これはソフトウェア史上最大規模のIPOレースです。",
    ],
  },
  business: {
    title: "ビジネスモデル",
    subtitle: "エンタープライズ vs コンシューマー",
    color: COLORS.anthropic,
    seed: 7,
    bullets: [
      "OpenAI：コンシューマー重視 → ChatGPT 9億人",
      "Anthropic：エンタープライズ重視 → 収益の80%が企業",
      "年間$100万超の企業顧客が7倍に増加",
      "高マージンのAPI収益がAnthropicの黒字化を支える",
    ],
    stat: { label: "Anthropic エンタープライズ比率", value: "80%", color: COLORS.anthropic },
    narration: [
      "2社のビジネスモデルは根本的に異なります。",
      "OpenAIはコンシューマー重視。ChatGPTの9億人ユーザーが象徴するように、一般消費者への普及を最優先します。",
      "一方Anthropicはエンタープライズ重視。収益の80%が企業顧客からです。",
      "年間100万ドル以上支払う企業顧客が7倍に増加しました。",
      "この違いは利益率に直結します。エンタープライズAPIはコンシューマー向けより高マージンです。",
      "Anthropicが初の黒字化を達成できた背景にはこのビジネスモデルの優位性があります。",
    ],
  },
  safety: {
    title: "安全性哲学",
    subtitle: "Constitutional AI vs RLHF",
    color: COLORS.accent,
    seed: 8,
    bullets: [
      "Anthropic：Constitutional AI（HHH原則：有益・無害・正直）",
      "AIに原則を与えて自己評価させる独自の手法",
      "OpenAI：RLHFによる安全対策 + 商業展開のバランス",
      "2026年2月：DarioがFBIの制限解除要求を拒否",
    ],
    narration: [
      "2社を最も分けるのは、AI安全性への哲学です。",
      "AnthropicはConstitutional AIを開発。AIに原則を与えて自己評価させる手法です。",
      "有益で、無害で、正直にというHHH原則が全モデルの基盤となっています。",
      "OpenAIもRLHFによる安全対策を実施していますが、商業展開とのバランスが常に問われます。",
      "2026年2月、DarioはFBIからClaudeの安全制限を解除するよう要求されましたが、これを拒否。",
      "AIが社会に組み込まれるにつれ、この哲学の違いはより重要になっていきます。",
    ],
  },
  partners: {
    title: "パートナー戦略",
    subtitle: "Microsoft vs Amazon・Google",
    color: COLORS.openai,
    seed: 9,
    bullets: [
      "OpenAI：MicrosoftがAzure経由で世界展開、$27Bの株式保有",
      "Anthropic：AmazonがAWS経由で展開、$8Bを投資",
      "Anthropic：GoogleもAnthropic株を数十億ドル保有",
      "AI覇権争いはMicrosoft vs Amazon・Google連合の代理戦争",
    ],
    narration: [
      "両社のパートナー戦略も対照的です。",
      "OpenAIはMicrosoftと深く結びついています。Microsoftは270億ドルの株式を保有し、Azure経由でGPTを全世界に提供します。",
      "AnthropicはAmazonと戦略的パートナーシップを締結。Amazonは80億ドルを投資しています。",
      "またGoogleも数十億ドルを投資しており、Google Cloudでも利用可能です。",
      "この構図を見ると、AI覇権争いはMicrosoft陣営とAmazon・Google連合の代理戦争とも言えます。",
    ],
  },
  future: {
    title: "今後の展望",
    subtitle: "AGIへの競争",
    color: COLORS.gold,
    seed: 10,
    bullets: [
      "OpenAI：Stargate Project → $5000億のデータセンター建設",
      "GPT-6リリース発表「AGI時代へようこそ」",
      "Anthropic：「AGIは2〜3年以内に来るかもしれない」",
      "両社ともに$1兆超の時価総額を目指してIPOへ",
    ],
    stat: { label: "Stargate投資規模", value: "$500B", color: COLORS.gold },
    narration: [
      "2社が最終的に目指すものは何か。AGI、つまり汎用人工知能です。",
      "OpenAIのGreg Brockmanは、GPT-6のリリース発表を「AGI時代へようこそ」という言葉で締めくくりました。",
      "OpenAIはStargateプロジェクトで5000億ドルのデータセンター建設を進めています。",
      "一方AnthropicのDarioは「AGIは2〜3年以内に来るかもしれない」と発言。",
      "しかしその開発は安全性を担保しながら進めるべきだという姿勢を崩しません。",
      "IPOレースも激化しており、Anthropicは10月、OpenAIは9月の上場を目指しています。",
    ],
  },
};

export const Documentary: React.FC = () => {
  const { fps } = useVideoConfig();

  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s01_intro)}>
        <IntroScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s02_origin_openai)}>
        <GenericScene data={SCENE_DATA.origin_openai} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s03_origin_anthropic)}>
        <GenericScene data={SCENE_DATA.origin_anthropic} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s04_split)}>
        <GenericScene data={SCENE_DATA.split} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s05_models)}>
        <GenericScene data={SCENE_DATA.models} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s06_revenue)}>
        <RevenueScene />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s07_funding)}>
        <GenericScene data={SCENE_DATA.funding} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s08_business_model)}>
        <GenericScene data={SCENE_DATA.business} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s09_safety)}>
        <GenericScene data={SCENE_DATA.safety} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s10_partners)}>
        <GenericScene data={SCENE_DATA.partners} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s11_future)}>
        <GenericScene data={SCENE_DATA.future} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

      <TransitionSeries.Sequence durationInFrames={sec(SECTION_DURATION.s12_conclusion)}>
        <ConclusionScene />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
