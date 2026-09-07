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
  text: "#ffffff",
  textMuted: "rgba(255,255,255,0.5)",
  textDim: "rgba(255,255,255,0.25)",
  surface: "rgba(255,255,255,0.04)",
  border: "rgba(255,255,255,0.08)",
};

// 各セクション尺（秒）
export const SECTION_DURATION = {
  intro: 12,       // イントロ
  origin_openai: 30, // OpenAI誕生
  origin_anthropic: 30, // Anthropic誕生
  split: 30,       // 決別
  models: 30,      // モデル比較
  revenue: 30,     // 収益
  funding: 25,     // 資金調達
  business: 30,    // ビジネスモデル
  safety: 30,      // 安全性
  partners: 25,    // パートナー
  future: 30,      // 将来
  conclusion: 28,  // まとめ
};

export const VIDEO_FPS_CONST = VIDEO_FPS;

export const EASING = {
  cinematic: Easing.bezier(0.22, 1, 0.36, 1),
  elastic: Easing.bezier(0.1, 0.9, 0.2, 1),
  exp: Easing.bezier(0.19, 1, 0.22, 1),
};

export const TRANSITION_FRAMES = 20;
