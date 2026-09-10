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

// 各セクション秒数
export const SECTION_DURATION = {
  s01_intro: 120,
  s02_origin_openai: 180,
  s03_origin_anthropic: 180,
  s04_split: 180,
  s05_models: 180,
  s06_revenue: 180,
  s07_funding: 120,
  s08_business_model: 180,
  s09_safety: 180,
  s10_partners: 120,
  s11_future: 180,
  s12_conclusion: 180,
};

export const TRANSITION_FRAMES = 20;

export const EASING = {
  cinematic: Easing.bezier(0.22, 1, 0.36, 1),
  elastic: Easing.bezier(0.1, 0.9, 0.2, 1),
  exp: Easing.bezier(0.19, 1, 0.22, 1),
};
