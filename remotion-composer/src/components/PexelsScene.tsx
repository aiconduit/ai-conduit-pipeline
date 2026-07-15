import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

interface PexelsSceneProps {
  videoUrl?: string;
  text?: string;
  textPosition?: "top" | "bottom" | "center";
  accentColor?: string;
  overlayOpacity?: number;
  gradient?: string;
}

export const PexelsScene: React.FC<PexelsSceneProps> = ({
  videoUrl,
  text,
  textPosition = "bottom",
  accentColor = "#22D3EE",
  overlayOpacity = 0.45,
  gradient,
}) => {
  const frame = useCurrentFrame();
  const textOpacity = interpolate(frame, [10, 25], [0, 1], {
    extrapolateRight: "clamp",
  });
  const bgPulse = interpolate(frame, [0, 30, 60], [0.8, 1, 0.9], {
    extrapolateRight: "clamp",
  });

  const positionStyle: React.CSSProperties =
    textPosition === "top"
      ? { top: "8%", bottom: "auto" }
      : textPosition === "center"
      ? { top: "50%", transform: "translateY(-50%)" }
      : { bottom: "10%", top: "auto" };

  // グラデーション背景(B-roll動画なしのフォールバック)
  const defaultGradient = gradient || `linear-gradient(135deg, #0B0F1A 0%, #1a1a2e 40%, ${accentColor}22 100%)`;

  return (
    <AbsoluteFill>
      {/* グラデーション背景 */}
      <div style={{
        width: "100%", height: "100%",
        background: defaultGradient,
        opacity: bgPulse,
      }} />

      {/* アニメーション背景パターン */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
        background: `radial-gradient(ellipse at 30% 70%, ${accentColor}18 0%, transparent 50%),
                     radial-gradient(ellipse at 70% 30%, ${accentColor}12 0%, transparent 50%)`,
      }} />

      {/* テキストオーバーレイ */}
      {text && (
        <div style={{
          position: "absolute", left: "6%", right: "6%",
          ...positionStyle,
          opacity: textOpacity,
          textAlign: "center",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}>
          <div style={{
            color: "white",
            fontSize: "2rem",
            fontWeight: 800,
            lineHeight: 1.4,
            textShadow: `0 2px 20px rgba(0,0,0,0.9), 0 0 40px ${accentColor}44`,
          }}>
            {text}
          </div>
          <div style={{
            width: 50, height: 3,
            background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
            borderRadius: 2,
            margin: "14px auto 0",
          }} />
        </div>
      )}
    </AbsoluteFill>
  );
};
