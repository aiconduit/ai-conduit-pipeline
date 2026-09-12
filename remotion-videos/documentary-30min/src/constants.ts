import { Easing } from "remotion";

export const VIDEO_WIDTH = 1920;
export const VIDEO_HEIGHT = 1080;
export const VIDEO_FPS = 30;

export const COLORS = {
  bg: "#040408",
  anthropic: "#a78bfa",
  openai: "#10b981",
  gold: "#f59e0b",
  accent: "#06b6d4",
  red: "#ef4444",
  text: "#ffffff",
  textMuted: "rgba(255,255,255,0.55)",
  textDim: "rgba(255,255,255,0.25)",
  surface: "rgba(255,255,255,0.05)",
  border: "rgba(255,255,255,0.08)",
};

// 24シーン × 60〜90秒 = 約30分
export const SECTION_DURATION = {
  s01_hook:          30,  // フック（冒頭30秒で掴む）
  s02_intro:         60,  // イントロ・概要
  s03_openai_birth:  75,  // OpenAI誕生
  s04_chatgpt:       60,  // ChatGPTの衝撃
  s05_anthropic_birth: 75, // Anthropic誕生
  s06_split_reason:  60,  // 決別の真相
  s07_safety_vs_growth: 60, // 安全性vs成長
  s08_models_claude: 60,  // Claudeモデル
  s09_models_gpt:    60,  // GPTモデル
  s10_benchmark:     60,  // ベンチマーク比較
  s11_revenue_anthropic: 75, // Anthropic収益
  s12_revenue_openai: 60, // OpenAI収益・損失
  s13_funding:       60,  // 資金調達
  s14_ipo_race:      60,  // IPOレース
  s15_enterprise:    60,  // エンタープライズ戦略
  s16_consumer:      60,  // コンシューマー戦略
  s17_partners_ms:   60,  // Microsoft連携
  s18_partners_aws:  60,  // Amazon・Google連携
  s19_safety_constitutional: 75, // Constitutional AI
  s20_safety_rlhf:   60,  // RLHF・OpenAI安全性
  s21_fbi:           45,  // FBI拒否事件
  s22_future_agi:    75,  // AGIへの競争
  s23_stargate:      60,  // Stargateプロジェクト
  s24_conclusion:    90,  // まとめ・結論
};

export const TRANSITION_FRAMES = 15;

export const EASING = {
  cinematic: Easing.bezier(0.22, 1, 0.36, 1),
  elastic: Easing.bezier(0.1, 0.9, 0.2, 1),
  exp: Easing.bezier(0.19, 1, 0.22, 1),
};
