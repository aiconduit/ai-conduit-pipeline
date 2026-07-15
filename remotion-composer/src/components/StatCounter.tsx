import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

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

  const scaleSpring = spring({ frame, fps, config: { damping: 12, stiffness: 100 } });
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div style={{
      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
      background: `linear-gradient(135deg, ${backgroundColor} 0%, #1a1a2e 100%)`,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      fontFamily: "system-ui, -apple-system, sans-serif",
    }}>
      <div style={{ opacity: titleOpacity, color: "rgba(255,255,255,0.6)", fontSize: "1.2rem", marginBottom: 40, letterSpacing: "0.2em", textTransform: "uppercase" }}>
        {title}
      </div>
      <div style={{ display: "flex", gap: 40, transform: `scale(${scaleSpring})` }}>
        {stats.map((stat, i) => {
          const count = Math.round(interpolate(frame, [10 + i * 5, 60 + i * 5], [0, stat.value], { extrapolateRight: "clamp", extrapolateLeft: "clamp" }));
          return (
            <div key={i} style={{
              textAlign: "center", backgroundColor: "rgba(255,255,255,0.05)",
              borderRadius: 16, padding: "32px 40px",
              border: `1px solid ${accentColor}33`,
              boxShadow: `0 0 30px ${accentColor}22`,
            }}>
              <div style={{ fontSize: "3.5rem", fontWeight: 900, color: stat.color || accentColor, lineHeight: 1 }}>
                {count.toLocaleString()}{stat.suffix || ""}
              </div>
              <div style={{ color: "rgba(255,255,255,0.6)", fontSize: "1rem", marginTop: 12, letterSpacing: "0.05em" }}>
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
