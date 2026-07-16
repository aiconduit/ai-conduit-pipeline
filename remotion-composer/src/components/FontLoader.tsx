import { loadFont } from "@remotion/google-fonts/NotoSansJP";

const { fontFamily } = loadFont("normal", {
  weights: ["700", "900"],
  subsets: ["latin", "japanese"],
  ignoreTooManyRequestsWarning: true,
});

export const JAPANESE_FONT_FAMILY = fontFamily;

export function useJapaneseFont() {
  return fontFamily;
}
