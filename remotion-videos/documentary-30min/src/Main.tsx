import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { useVideoConfig } from "remotion";
import React from "react";
import { VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import { HookScene } from "./scenes/HookScene";
import { IntroScene } from "./scenes/IntroScene";
import { GenericScene } from "./scenes/GenericScene";
import { RevenueScene } from "./scenes/RevenueScene";
import { ConclusionScene } from "./scenes/ConclusionScene";
import { WebScreenScene } from "./scenes/WebScreenScene";
import { StatCompareScene } from "./scenes/StatCompareScene";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const SCENES = {
  origin_openai: {
    title: "OpenAIの誕生", subtitle: "2015年 · 非営利→営利", color: "#10b981", seed: 1,
    bullets: ["2015年12月、Sam AltmanとElon Muskら共同創業","当初は非営利。AIを人類全体の利益のために開発","Microsoftから総額$130Bを調達","2022年11月、ChatGPTリリース"],
    stat: { label: "週間アクティブユーザー", value: "9億人", color: "#10b981" },
    narration: ["OpenAIは2015年12月に設立されました。","Sam Altman、Elon Musk、Greg Brockmanら錚々たる顔ぶれが共同創業しました。","当初は非営利組織として、AIを人類全体の利益のために開発することを掲げました。","2022年11月、ChatGPTをリリース。わずか5日で100万ユーザーを獲得しました。"],
    audioFile: "s03_origin_openai.mp3",
  },
  chatgpt: {
    title: "ChatGPTの衝撃", subtitle: "2022年11月の革命", color: "#10b981", seed: 11,
    bullets: ["リリース5日で100万ユーザー","2ヶ月で1億ユーザー（史上最速）","検索エンジンを脅かす存在に","Microsoftがすぐに$10Bを追加投資"],
    stat: { label: "2ヶ月でのユーザー数", value: "1億人", color: "#10b981" },
    narration: ["ChatGPTの登場は世界を変えました。","リリースからわずか5日で100万ユーザーを獲得。","2ヶ月で1億ユーザーに達し、史上最速の成長を記録しました。","Googleは社内で「コードレッド」を宣言し、緊急対応を迫られました。"],
    audioFile: "s04_chatgpt.mp3",
  },
  anthropic_birth: {
    title: "Anthropicの誕生", subtitle: "2021年 · 安全性を最優先", color: "#a78bfa", seed: 2,
    bullets: ["2021年1月、Dario Amodeiと8人のOpenAI研究者が退社","設立理念：AIを安全に、人類のために開発する","19ヶ月で$1B → $65B ARRへ、史上最速の成長","企業顧客が収益の80%を占める"],
    stat: { label: "ARR成長（19ヶ月）", value: "×65", color: "#a78bfa" },
    narration: ["2020年末、OpenAIの内部で亀裂が生じていました。","研究担当副社長のDario Amodeiは、会社の方向性に疑問を持ち始めます。","2021年1月、DarioはAnthropicを設立します。","2026年現在、ARRは650億ドルに達し、19ヶ月で65倍という歴史的な成長を遂げました。"],
    audioFile: "s05_anthropic_birth.mp3",
  },
  split: {
    title: "決別の真相", subtitle: "安全性 vs 商業主義", color: "#ef4444", seed: 3,
    bullets: ["Dario：「AIが強力になるほど安全性に注力すべき」","OpenAI：Microsoftとの連携で急速に商業展開","哲学の違いが2社の戦略を根本から分ける","2026年2月、DarioはFBIの安全制限解除要求を拒否"],
    stat: { label: "OpenAI 2025年損失", value: "$20.9B", color: "#ef4444" },
    narration: ["なぜDarioはOpenAIを去ったのか。","Darioは「AIが非常に強力になりうると確信した」と語っています。","OpenAIは普及を優先、Anthropicは安全性を優先。","2026年2月、DarioはFBIからの制限解除要求を拒否しました。"],
    audioFile: "s06_split.mp3",
  },
  safety_vs_growth: {
    title: "2つの哲学", subtitle: "安全性 vs 成長速度", color: "#06b6d4", seed: 12,
    bullets: ["Anthropic：Constitutional AI・HHH原則","OpenAI：RLHF + 商業展開のバランス","どちらが正しいかは今も議論中","ユーザーは最終的に両方を使う"],
    narration: ["2社の根本的な違いは哲学にあります。","Anthropicは安全性を最優先。Constitutional AIという独自手法を開発しました。","OpenAIは普及速度を優先。より多くの人にAIを届けることを重視します。","この哲学の違いが、製品・価格・対象市場の全てに影響しています。"],
    audioFile: "s07_safety_vs_growth.mp3",
  },
  models_claude: {
    title: "Claudeモデル群", subtitle: "Fable 5.1 · Sonnet 5 · Haiku 4.5", color: "#a78bfa", seed: 13,
    bullets: ["Claude Fable 5.1：最高性能・複雑な推論に強い","Claude Sonnet 5：コスパ最強・最も人気","Claude Haiku 4.5：超高速・低コスト","コーディングSWE-bench：72.7%（業界1位）"],
    stat: { label: "SWE-bench スコア", value: "72.7%", color: "#a78bfa" },
    narration: ["Anthropicのモデルラインナップを紹介します。","フラッグシップのClaude Fable 5.1は複雑な推論と長文理解に特に優れています。","Claude Sonnet 5はコストパフォーマンスが最も高く、企業での採用が急増しています。","コーディングの指標SWE-benchでは業界トップの72.7%を達成しています。"],
    audioFile: "s08_models_claude.mp3",
  },
  models_gpt: {
    title: "GPTモデル群", subtitle: "GPT-6 Astra · GPT-4o · o3", color: "#10b981", seed: 14,
    bullets: ["GPT-6 Astra：2026年最新・マルチモーダル強化","o3：深い推論特化・数学・科学に強い","GPT-4o mini：コスパ最強ミニモデル","週間9億人が使うChatGPTを支える"],
    stat: { label: "ChatGPT MAU", value: "9億人", color: "#10b981" },
    narration: ["OpenAIの最新モデルラインナップです。","GPT-6 Astraはマルチモーダル能力が大幅に強化されました。","o3は深い推論に特化し、数学や科学の問題解決に優れています。","これらのモデルが週間9億人のChatGPTユーザーを支えています。"],
    audioFile: "s09_models_gpt.mp3",
  },
  funding: {
    title: "IPOレース", subtitle: "2026年 史上最大の資金調達", color: "#f59e0b", seed: 6,
    bullets: ["Anthropic：$965B時価総額でIPO申請→10月上場予定","OpenAI：$852Bで$122Bを調達→9月上場予定","Anthropic IPO目標：$2兆ドル以上","2社合計で史上最大規模のIPO"],
    stat: { label: "2社合計時価総額", value: "$1.82T", color: "#f59e0b" },
    narration: ["2026年、2社は史上最大規模のIPOレースを繰り広げています。","Anthropicは時価総額9650億ドルでIPO申請。2兆ドル以上の上場時価総額を目指します。","OpenAIは8520億ドルで1220億ドルを調達し、9月の上場を目指しています。","2社合計で約1兆8千億ドルが市場に登場することになります。"],
    audioFile: "s13_funding.mp3",
  },
  enterprise: {
    title: "エンタープライズ戦略", subtitle: "Anthropicの勝ち筋", color: "#a78bfa", seed: 15,
    bullets: ["収益の80%が企業顧客から","年間$100万超の顧客が7倍に増加","Amazon・Googleとのパートナーシップ","高マージンAPIが黒字化を実現"],
    stat: { label: "エンタープライズ比率", value: "80%", color: "#a78bfa" },
    narration: ["Anthropicの最大の強みはエンタープライズ戦略です。","収益の80%が企業顧客から来ています。","年間100万ドル以上支払う大企業顧客が7倍に増加しました。","このモデルが2026年の初黒字化を実現させました。"],
    audioFile: "s15_enterprise.mp3",
  },
  consumer: {
    title: "コンシューマー戦略", subtitle: "OpenAIの強み", color: "#10b981", seed: 16,
    bullets: ["ChatGPTは週間9億人が使う世界最大AIサービス","ChatGPT Plus：月$20で個人向け","ChatGPT Team・Enterprise：法人向け","ブランド力はAI業界で圧倒的No.1"],
    stat: { label: "週間アクティブユーザー", value: "9億人", color: "#10b981" },
    narration: ["OpenAIの最大の強みはブランド力とユーザー数です。","ChatGPTは週間9億人のユーザーを抱える世界最大のAIサービスです。","一般消費者への普及率はAI業界で圧倒的No.1です。","月額20ドルのChatGPT Plusは個人ユーザーに広く普及しています。"],
    audioFile: "s16_consumer.mp3",
  },
  partners_ms: {
    title: "Microsoft連携", subtitle: "OpenAIの最大の武器", color: "#10b981", seed: 17,
    bullets: ["MicrosoftがAzure経由でGPTを世界展開","Microsoft株式保有額：$27B","Office・Teamsにフル統合","365 Copilotで企業ユーザー直撃"],
    narration: ["OpenAIとMicrosoftの連携は業界最大の提携です。","MicrosoftはAzure経由でGPTを全世界に提供しています。","Office・TeamsへのCopilot統合により、数億人のビジネスユーザーに直接届きます。","Microsoftの株式保有額は270億ドルに達しています。"],
    audioFile: "s17_partners_ms.mp3",
  },
  partners_aws: {
    title: "Amazon・Google連携", subtitle: "Anthropicの強力な後ろ盾", color: "#a78bfa", seed: 18,
    bullets: ["AmazonがAWS経由でClaudeを展開","Amazon投資額：$8B","Google・GCPでも利用可能","Microsoft vs Amazon・Google連合の代理戦争"],
    narration: ["AnthropicはAmazonと戦略的パートナーシップを締結しています。","AmazonはAWS経由でClaudeを展開し、80億ドルを投資しています。","GoogleもAnthropicに数十億ドルを投資しており、Google Cloudでも利用可能です。","AI覇権争いはMicrosoft陣営とAmazon・Google連合の代理戦争とも言えます。"],
    audioFile: "s18_partners_aws.mp3",
  },
  fbi: {
    title: "FBI拒否事件", subtitle: "2026年2月の転換点", color: "#ef4444", seed: 19,
    bullets: ["FBIがDarioに「Claudeの安全制限解除」を要求","Darioは即座に拒否","「安全性は交渉の対象ではない」","業界に大きな衝撃を与えた決断"],
    narration: ["2026年2月、衝撃的な事件が起きました。","FBIがAnthropicのDario CEOに対し、Claudeの安全制限を解除するよう要求したのです。","Darioはこれを即座に拒否しました。","この決断はAnthropicの安全性への姿勢を世界に示す転換点となりました。"],
    audioFile: "s21_fbi.mp3",
  },
  future_agi: {
    title: "AGIへの競争", subtitle: "次の10年の覇権争い", color: "#f59e0b", seed: 20,
    bullets: ["OpenAI：「AGI時代へようこそ」GPT-6発表時の言葉","Anthropic：「AGIは2〜3年以内に来るかもしれない」","OpenAI Stargate：$5000億のデータセンター建設","どちらが先に汎用AIを達成するか"],
    stat: { label: "Stargate投資規模", value: "$500B", color: "#f59e0b" },
    narration: ["2社が最終的に目指すものはAGI、汎用人工知能です。","OpenAIのGreg BrockmanはGPT-6発表を「AGI時代へようこそ」という言葉で締めくくりました。","OpenAIはStargateプロジェクトで5000億ドルのデータセンター建設を進めています。","AnthropicのDarioは「AGIは2〜3年以内に来るかもしれない」と発言しています。"],
    audioFile: "s22_future_agi.mp3",
  },
};

const STAT_SCENES = {
  benchmark: {
    title: "ベンチマーク比較", subtitle: "2026年9月最新データ",
    stats: [
      { label: "コーディング(SWE-bench)", anthropic: "72.7%", openai: "67.0%", winner: "anthropic" as const },
      { label: "数学(MATH-500)", anthropic: "91.2%", openai: "94.5%", winner: "openai" as const },
      { label: "長文理解", anthropic: "96.4%", openai: "93.1%", winner: "anthropic" as const },
      { label: "マルチモーダル", anthropic: "88.5%", openai: "91.2%", winner: "openai" as const },
      { label: "推論(GPQA)", anthropic: "82.1%", openai: "87.3%", winner: "openai" as const },
    ],
    narration: ["2026年9月時点の最新ベンチマーク比較です。","コーディングと長文理解はClaudeが優位。","数学、マルチモーダル、深い推論はGPT-6が優位。","用途によって使い分けるのが賢い選択です。"],
    audioFile: "s10_benchmark.mp3",
    seed: 4,
  },
  revenue_compare: {
    title: "収益比較", subtitle: "ARR & 利益率 2026",
    stats: [
      { label: "ARR", anthropic: "$65B", openai: "$40B", winner: "anthropic" as const },
      { label: "時価総額", anthropic: "$965B", openai: "$852B", winner: "anthropic" as const },
      { label: "2025年損益", anthropic: "黒字化", openai: "-$20.9B", winner: "anthropic" as const },
      { label: "エンプロ比率", anthropic: "80%", openai: "40%", winner: "anthropic" as const },
      { label: "MAU", anthropic: "数千万", openai: "9億人", winner: "openai" as const },
    ],
    narration: ["収益面ではAnthropicが大きく上回っています。","ARRはAnthropicの650億ドルがOpenAIの400億ドルを大幅に超えます。","利益面でもAnthropicが2026年に初の黒字化を達成しました。","ただしユーザー数ではOpenAIが圧倒しています。"],
    audioFile: "s12_revenue_compare.mp3",
    seed: 6,
  },
};

const WEB_SCENES = {
  anthropic_web: {
    title: "Anthropic公式サイト", subtitle: "anthropic.com", color: "#a78bfa",
    screenshotFile: "anthropic_home.png",
    caption: "ClaudeとAI安全研究を軸に急成長。シンプルで洗練されたブランド戦略。",
    narration: ["これがAnthropicの公式サイトです。","シンプルで洗練されたデザインが印象的です。","安全性を前面に打ち出したブランド戦略が伝わります。"],
    audioFile: "s01_hook.mp3",
  },
  openai_web: {
    title: "OpenAI公式サイト", subtitle: "openai.com", color: "#10b981",
    screenshotFile: "openai_home.png",
    caption: "ChatGPTを核に消費者・企業の両方を獲得。圧倒的なブランド認知度。",
    narration: ["こちらはOpenAIの公式サイトです。","ChatGPTを前面に押し出したマーケティング戦略が見て取れます。","世界で最も認知されたAIブランドとしての自信が伝わります。"],
    audioFile: "s02_intro.mp3",
  },
  chatgpt_web: {
    title: "ChatGPT画面", subtitle: "chatgpt.com", color: "#10b981",
    screenshotFile: "chatgpt.png",
    caption: "週間9億人が使う世界最大のAIサービス。シンプルなUIが普及を加速。",
    narration: ["これが週間9億人のユーザーが使うChatGPTです。","シンプルで直感的なUIが爆発的な普及を支えました。","誰でも使えるアクセシビリティがOpenAIの強みです。"],
    audioFile: "s04_chatgpt.mp3",
    highlights: [{ x: 10, y: 70, w: 80, h: 20, label: "入力エリア" }],
  },
  claude_web: {
    title: "Claude画面", subtitle: "claude.ai", color: "#a78bfa",
    screenshotFile: "claude_ai.png",
    caption: "長文理解・コーディング・分析に特化。企業ユーザーから高い評価。",
    narration: ["こちらはClaudeのインターフェースです。","長文の理解と精密な分析能力が際立っています。","企業のプロフェッショナルユーザーから特に高い評価を受けています。"],
    audioFile: "s08_models_claude.mp3",
  },
};

export const Documentary: React.FC = () => (
  <TransitionSeries>
    {/* S01: フック */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s01_hook)}>
      <HookScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S02: イントロ（Anthropicサイト） */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s02_intro)}>
      <WebScreenScene data={WEB_SCENES.anthropic_web} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S03: OpenAI誕生 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s03_openai_birth)}>
      <GenericScene data={SCENES.origin_openai} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S04: ChatGPT（実際の画面） */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s04_chatgpt)}>
      <WebScreenScene data={WEB_SCENES.chatgpt_web} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S05: Anthropic誕生 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s05_anthropic_birth)}>
      <GenericScene data={SCENES.anthropic_birth} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S06: 決別 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s06_split_reason)}>
      <GenericScene data={SCENES.split} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S07: 2つの哲学 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s07_safety_vs_growth)}>
      <GenericScene data={SCENES.safety_vs_growth} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S08: Claudeモデル（実際の画面） */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s08_models_claude)}>
      <WebScreenScene data={WEB_SCENES.claude_web} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S09: GPTモデル（OpenAIサイト） */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s09_models_gpt)}>
      <WebScreenScene data={WEB_SCENES.openai_web} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S10: ベンチマーク比較 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s10_benchmark)}>
      <StatCompareScene data={STAT_SCENES.benchmark} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S11: Anthropic収益 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s11_revenue_anthropic)}>
      <RevenueScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S12: 収益比較 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s12_revenue_openai)}>
      <StatCompareScene data={STAT_SCENES.revenue_compare} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S13: 資金調達 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s13_funding)}>
      <GenericScene data={SCENES.funding} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S14: IPO */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s14_ipo_race)}>
      <GenericScene data={{ ...SCENES.funding, title: "IPOの行方", subtitle: "2026年秋の大勝負", audioFile: "s14_ipo_race.mp3" }} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S15: エンタープライズ */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s15_enterprise)}>
      <GenericScene data={SCENES.enterprise} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S16: コンシューマー */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s16_consumer)}>
      <GenericScene data={SCENES.consumer} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S17: Microsoft */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s17_partners_ms)}>
      <GenericScene data={SCENES.partners_ms} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S18: Amazon・Google */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s18_partners_aws)}>
      <GenericScene data={SCENES.partners_aws} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S19: Constitutional AI */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s19_safety_constitutional)}>
      <GenericScene data={{ title: "Constitutional AI", subtitle: "Anthropicの独自技術", color: "#06b6d4", seed: 8, bullets: ["AIに原則を与えて自己評価させる手法", "HHH原則：有益・無害・正直", "全Claudeモデルの基盤技術", "業界標準になりつつある安全手法"], narration: ["AnthropicはConstitutional AIを開発しました。","AIに原則を与えて自己評価させるという革新的な手法です。","有益で、無害で、正直にというHHH原則が全てのClaudeモデルの基盤です。","この手法は業界全体に影響を与えています。"], audioFile: "s19_safety_constitutional.mp3" }} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S20: RLHF */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s20_safety_rlhf)}>
      <GenericScene data={{ title: "OpenAIの安全対策", subtitle: "RLHF & モデレーション", color: "#10b981", seed: 9, bullets: ["RLHF（人間のフィードバックから強化学習）", "コンテンツモデレーション専門チーム", "商業展開とのバランスが課題", "Safety vs Capability のトレードオフ"], narration: ["OpenAIもRLHF（人間のフィードバックから強化学習）で安全対策を実施しています。","コンテンツモデレーションの専門チームを持ちます。","しかし商業展開のスピードとのバランスが常に問われています。","安全性と能力のトレードオフは業界全体の課題です。"], audioFile: "s20_safety_rlhf.mp3" }} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S21: FBI拒否 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s21_fbi)}>
      <GenericScene data={SCENES.fbi} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S22: AGI競争 */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s22_future_agi)}>
      <GenericScene data={SCENES.future_agi} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S23: Stargate */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s23_stargate)}>
      <GenericScene data={{ title: "Stargateプロジェクト", subtitle: "AIインフラへの$5000億投資", color: "#f59e0b", seed: 10, bullets: ["OpenAI・Microsoft・SoftBankが主導", "$5000億（約75兆円）のデータセンター建設", "米国全土にAIコンピューティング基盤を整備", "Anthropicも独自のコンピュートを計画中"], stat: { label: "総投資規模", value: "$500B", color: "#f59e0b" }, narration: ["OpenAIはStargateプロジェクトを立ち上げました。","Microsoft・SoftBankと共同で5000億ドルを投資します。","米国全土にAIコンピューティング基盤を整備する壮大な計画です。","AnthropicもAmazonと共に独自のコンピュート投資を進めています。"], audioFile: "s23_stargate.mp3" }} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />

    {/* S24: まとめ */}
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s24_conclusion)}>
      <ConclusionScene />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
