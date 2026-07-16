import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useJapaneseFont } from "./FontLoader";

interface CinematicTitleProps {
  title?: string;
  subtitle?: string;
  accentColor?: string;
  backgroundColor?: string;
}

export const CinematicTitle: React.FC<CinematicTitleProps> = ({
  title = "今日のAIトレンド",
  subtitle = "GitHub Trending",
  accentColor = "#22D3EE",
  backgroundColor = "#111827",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fontFamily = useJapaneseFont();

  const titleY = spring({ frame, fps, from: 60, to: 0, durationInFrames: 40, config: { damping: 14, mass: 0.8 } });
  const titleOpacity = spring({ frame, fps, from: 0, to: 1, durationInFrames: 30 });
  const underlineWidth = interpolate(frame, [20, 50], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const subtitleOpacity = interpolate(frame, [40, 65], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{
      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
      background: `radial-gradient(ellipse at 50% 50%, ${accentColor}22 0%, ${backgroundColor} 70%)`,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      fontFamily,
    }}>
      <h1 style={{
        color: "white", fontSize: "3rem", fontWeight: 900,
        opacity: titleOpacity, transform: `translateY(${titleY}px)`,
        margin: "0 20px", letterSpacing: "0.02em", textAlign: "center",
        textShadow: `0 0 40px ${accentColor}88, 0 2px 8px rgba(0,0,0,0.8)`,
        position: "relative", lineHeight: 1.3,
      }}>
        {title}
      </h1>
      <div style={{
        width: `${underlineWidth}%`, maxWidth: 300, height: 3,
        background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
        borderRadius: 2, marginTop: 16, position: "relative",
      }} />
      <p style={{
        color: "rgba(255,255,255,0.75)", fontSize: "1.2rem", fontWeight: 400,
        opacity: subtitleOpacity, marginTop: 20,
        letterSpacing: "0.1em", textTransform: "uppercase",
        position: "relative",
      }}>
        {subtitle}
      </p>
    </div>
  );
};
