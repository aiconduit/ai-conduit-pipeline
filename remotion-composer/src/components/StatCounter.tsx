import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useJapaneseFont } from "./FontLoader";

interface StatItem {
  label: string;
  value: number;
  suffix?: string;
  color?: string;
}

interface StatCounterProps {
  title?: string;
  stats?: StatItem[];
  accentColor?: string;
  backgroundColor?: string;
}

export const StatCounter: React.FC<StatCounterProps> = ({
  title = "今月のGitHubトレンド",
  stats = [{ label: "Stars", value: 10000, suffix: "⭐" }],
  accentColor = "#22D3EE",
  backgroundColor = "#0B0F1A",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fontFamily = useJapaneseFont();

  const scaleSpring = spring({ frame, fps, config: { damping: 12, stiffness: 100 } });
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div style={{
      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
      background: `linear-gradient(135deg, ${backgroundColor} 0%, #1a1a2e 100%)`,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      fontFamily,
    }}>
      <div style={{ opacity: titleOpacity, color: "rgba(255,255,255,0.7)", fontSize: "1.1rem", marginBottom: 32, letterSpacing: "0.15em", textAlign: "center" }}>
        {title}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 24, transform: `scale(${scaleSpring})`, width: "80%" }}>
        {stats.map((stat, i) => {
          const count = Math.round(interpolate(frame, [10 + i * 5, 60 + i * 5], [0, stat.value], { extrapolateRight: "clamp", extrapolateLeft: "clamp" }));
          return (
            <div key={i} style={{
              textAlign: "center", backgroundColor: "rgba(255,255,255,0.06)",
              borderRadius: 16, padding: "24px 32px",
              border: `1px solid ${accentColor}44`,
              boxShadow: `0 0 30px ${accentColor}22`,
            }}>
              <div style={{ fontSize: "3rem", fontWeight: 900, color: stat.color || accentColor, lineHeight: 1 }}>
                {count.toLocaleString()}{stat.suffix || ""}
              </div>
              <div style={{ color: "rgba(255,255,255,0.6)", fontSize: "0.9rem", marginTop: 8 }}>
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
