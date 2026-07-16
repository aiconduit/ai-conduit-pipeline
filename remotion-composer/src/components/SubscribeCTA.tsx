import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useJapaneseFont } from "./FontLoader";

interface SubscribeCTAProps {
  handle?: string;
  message?: string;
  ctaText?: string;
  accentColor?: string;
  backgroundColor?: string;
}

export const SubscribeCTA: React.FC<SubscribeCTAProps> = ({
  handle = "@AI_Conduit",
  message = "毎日AIトレンドを紹介中",
  ctaText = "コメントに「conduit」でテンプレ無料プレゼント",
  accentColor = "#22D3EE",
  backgroundColor = "#0B0F1A",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fontFamily = useJapaneseFont();

  const slideUp = spring({ frame: Math.max(frame - 5, 0), fps, config: { damping: 14, stiffness: 100 } });
  const translateY = interpolate(slideUp, [0, 1], [80, 0]);
  const opacity = interpolate(frame, [5, 20], [0, 1], { extrapolateRight: "clamp" });
  const bellPulse = interpolate(Math.sin(frame * 0.15), [-1, 1], [1, 1.2]);

  return (
    <div style={{
      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
      background: `radial-gradient(ellipse at 50% 40%, ${accentColor}15 0%, ${backgroundColor} 65%)`,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      fontFamily,
    }}>
      <div style={{ color: accentColor, fontSize: "1.6rem", fontWeight: 700, marginBottom: 8, textAlign: "center" }}>
        {handle}
      </div>
      <div style={{ color: "rgba(255,255,255,0.7)", fontSize: "1rem", marginBottom: 40, textAlign: "center" }}>
        {message}
      </div>
      <div style={{
        transform: `translateY(${translateY}px)`, opacity,
        backgroundColor: "rgba(0,0,0,0.7)",
        border: `1px solid ${accentColor}66`,
        borderRadius: 999, padding: "14px 24px",
        display: "flex", alignItems: "center", gap: 12,
        boxShadow: `0 0 30px ${accentColor}33`,
        maxWidth: "85%",
      }}>
        <div style={{
          width: 36, height: 36, borderRadius: "50%",
          backgroundColor: accentColor, flexShrink: 0,
          display: "flex", alignItems: "center", justifyContent: "center",
          transform: `scale(${bellPulse})`,
          fontSize: "1.1rem",
        }}>
          🎁
        </div>
        <div style={{ color: "white", fontSize: "0.9rem", fontWeight: 600, lineHeight: 1.4 }}>
          {ctaText}
        </div>
      </div>
      <div style={{
        display: "flex", gap: 12, marginTop: 24,
        opacity: interpolate(frame, [20, 35], [0, 1], { extrapolateRight: "clamp" }),
      }}>
        {["❤️ いいね", "🔔 フォロー", "🔗 シェア"].map((btn, i) => (
          <div key={i} style={{
            backgroundColor: "rgba(255,255,255,0.1)",
            border: "1px solid rgba(255,255,255,0.2)",
            borderRadius: 999, padding: "8px 16px",
            color: "white", fontSize: "0.85rem",
          }}>
            {btn}
          </div>
        ))}
      </div>
    </div>
  );
};
