import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { useVideoConfig } from "remotion";
import React from "react";
import { VIDEO_FPS, SECTION_DURATION, TRANSITION_FRAMES } from "./constants";
import { GenericScene } from "./scenes/GenericScene";
import { RevenueScene } from "./scenes/RevenueScene";
import { WebScreenScene } from "./scenes/WebScreenScene";
import { StatCompareScene } from "./scenes/StatCompareScene";

const f = (s: number) => Math.round(s * VIDEO_FPS);
const T = TRANSITION_FRAMES;

const SCENES = {
  models_gpt: { title: "GPTモデル群", subtitle: "GPT-6 Astra · o3 · GPT-4o mini", color: "#10b981", seed: 14, bullets: ["GPT-6 Astra：2026年最新・マルチモーダル強化","o3：深い推論特化・数学・科学に強い","GPT-4o mini：コスパ最強ミニモデル","週間9億人が使うChatGPTを支える"], stat: { label: "ChatGPT MAU", value: "9億人", color: "#10b981" }, narration: ["OpenAIの最新モデルラインナップです。","GPT-6 Astraはマルチモーダル能力が大幅に強化されました。","o3は深い推論に特化し、数学や科学の問題解決に優れています。","これらが週間9億人のChatGPTユーザーを支えています。"], audioFile: "s09_models_gpt.mp3" },
  funding: { title: "資金調達競争", subtitle: "2026年 史上最大規模", color: "#f59e0b", seed: 6, bullets: ["Anthropic：$965B時価総額でIPO申請","OpenAI：$852Bで$122Bを調達","Anthropic目標：$2兆ドル以上の上場","2社合計で史上最大規模のIPO"], stat: { label: "2社合計時価総額", value: "$1.82T", color: "#f59e0b" }, narration: ["資金調達でも2社は熾烈な競争を繰り広げています。","Anthropicは時価総額9650億ドルでIPO申請しました。","OpenAIは8520億ドルで1220億ドルを調達しています。","2社合計で約1兆8千億ドルが市場に登場します。"], audioFile: "s13_funding.mp3" },
  ipo: { title: "IPOレース", subtitle: "2026年秋の大勝負", color: "#f59e0b", seed: 7, bullets: ["Anthropic：10月上場予定","OpenAI：9月上場予定（極秘S-1提出）","上場後の時価総額争いが焦点","投資家はどちらを選ぶか"], narration: ["IPOレースが激化しています。","OpenAIは9月、Anthropicは10月の上場を目指しています。","どちらの株が高く評価されるか、投資家の注目が集まっています。","AIセクター最大のIPOイベントとなります。"], audioFile: "s14_ipo_race.mp3" },
  enterprise: { title: "エンタープライズ戦略", subtitle: "Anthropicの勝ち筋", color: "#a78bfa", seed: 15, bullets: ["収益の80%が企業顧客から","年間$100万超の顧客が7倍に増加","Amazon・Googleとのパートナーシップ","高マージンAPIが黒字化を実現"], stat: { label: "エンタープライズ比率", value: "80%", color: "#a78bfa" }, narration: ["Anthropicの最大の強みはエンタープライズ戦略です。","収益の80%が企業顧客から来ています。","年間100万ドル以上支払う大企業顧客が7倍に増加しました。","このモデルが2026年の初黒字化を実現させました。"], audioFile: "s15_enterprise.mp3" },
  consumer: { title: "コンシューマー戦略", subtitle: "OpenAIの強み", color: "#10b981", seed: 16, bullets: ["ChatGPTは週間9億人が使う世界最大AIサービス","ChatGPT Plus：月$20で個人向け","ChatGPT Team・Enterprise：法人向け","ブランド力はAI業界で圧倒的No.1"], stat: { label: "週間アクティブユーザー", value: "9億人", color: "#10b981" }, narration: ["OpenAIの最大の強みはブランド力とユーザー数です。","ChatGPTは週間9億人のユーザーを抱える世界最大のAIサービスです。","一般消費者への普及率はAI業界で圧倒的No.1です。","月額20ドルのChatGPT Plusは個人ユーザーに広く普及しています。"], audioFile: "s16_consumer.mp3" },
};

const STAT_SCENES = {
  benchmark: { title: "ベンチマーク比較", subtitle: "2026年9月最新データ", stats: [{ label: "コーディング(SWE-bench)", anthropic: "72.7%", openai: "67.0%", winner: "anthropic" as const }, { label: "数学(MATH-500)", anthropic: "91.2%", openai: "94.5%", winner: "openai" as const }, { label: "長文理解", anthropic: "96.4%", openai: "93.1%", winner: "anthropic" as const }, { label: "マルチモーダル", anthropic: "88.5%", openai: "91.2%", winner: "openai" as const }], narration: ["2026年9月時点の最新ベンチマーク比較です。","コーディングと長文理解はClaudeが優位。","数学とマルチモーダルはGPT-6が優位。","用途によって使い分けるのが賢い選択です。"], audioFile: "s10_benchmark.mp3", seed: 4 },
  revenue_compare: { title: "収益比較", subtitle: "ARR & 利益率 2026", stats: [{ label: "ARR", anthropic: "$65B", openai: "$40B", winner: "anthropic" as const }, { label: "時価総額", anthropic: "$965B", openai: "$852B", winner: "anthropic" as const }, { label: "2025年損益", anthropic: "黒字化", openai: "-$20.9B", winner: "anthropic" as const }, { label: "MAU", anthropic: "数千万", openai: "9億人", winner: "openai" as const }], narration: ["収益面ではAnthropicが大きく上回っています。","ARRはAnthropicの650億ドルがOpenAIを大幅に超えます。","利益面でもAnthropicが2026年に初の黒字化を達成しました。","ただしユーザー数ではOpenAIが圧倒しています。"], audioFile: "s12_revenue_compare.mp3", seed: 6 },
};

const WEB_OPENAI = { title: "OpenAI公式サイト", subtitle: "openai.com", color: "#10b981", screenshotFile: "openai_home.png", caption: "ChatGPTを核に消費者・企業の両方を獲得。圧倒的なブランド認知度。", narration: ["こちらはOpenAIの公式サイトです。","ChatGPTを前面に押し出したマーケティング戦略が見て取れます。","世界で最も認知されたAIブランドとしての自信が伝わります。"], audioFile: "s09_models_gpt.mp3" };

export const DocumentaryPart2: React.FC = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s09_models_gpt)}><WebScreenScene data={WEB_OPENAI} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s10_benchmark)}><StatCompareScene data={STAT_SCENES.benchmark} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s11_revenue_anthropic)}><RevenueScene /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s12_revenue_openai)}><StatCompareScene data={STAT_SCENES.revenue_compare} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s13_funding)}><GenericScene data={SCENES.funding} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s14_ipo_race)}><GenericScene data={SCENES.ipo} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s15_enterprise)}><GenericScene data={SCENES.enterprise} /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: T })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={f(SECTION_DURATION.s16_consumer)}><GenericScene data={SCENES.consumer} /></TransitionSeries.Sequence>
  </TransitionSeries>
);
