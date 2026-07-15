import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface SubscribeCTAProps {
  handle?: string;
  message?: string;
  ctaText?: string;
  accentColor?: string;
  backgroundColor?: string;
  commentKeyword?: string;
}

export const SubscribeCTA: React.FC<SubscribeCTAProps> = ({
  handle = "@AI_Conduit",
  message = "毎日AIトレンドを紹介中",
  ctaText = "コメントに「conduit」でテンプレ無料プレゼント🎁",
  accentColor = "#22D3EE",
  backgroundColor = "#0B0F1A",
  commentKeyword = "conduit",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideUp = spring({ frame: Math.max(frame - 5, 0), fps, config: { damping: 14, stiffness: 100 } });
  const translateY = interpolate(slideUp, [0, 1], [80, 0]);
  const opacity = interpolate(frame, [5, 20], [0, 1], { extrapolateRight: "clamp" });
  const bellPulse = interpolate(Math.sin(frame * 0.15), [-1, 1], [1, 1.2]);
  const bgOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div style={{
      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
      background: `radial-gradient(ellipse at 50% 40%, ${accentColor}15 0%, ${backgroundColor} 65%)`,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      fontFamily: "system-ui, -apple-system, sans-serif",
      opacity: bgOpacity,
    }}>
      {/* ハンドル */}
      <div style={{ color: accentColor, fontSize: "1.8rem", fontWeight: 700, letterSpacing: "0.05em", marginBottom: 8 }}>
        {handle}
      </div>
      {/* メッセージ */}
      <div style={{ color: "rgba(255,255,255,0.7)", fontSize: "1.1rem", marginBottom: 40 }}>
        {message}
      </div>
      {/* CTA バナー */}
      <div style={{
        transform: `translateY(${translateY}px)`, opacity,
        backgroundColor: "rgba(0,0,0,0.6)",
        backdropFilter: "blur(12px)",
        border: `1px solid ${accentColor}55`,
        borderRadius: 999, padding: "14px 28px",
        display: "flex", alignItems: "center", gap: 12,
        boxShadow: `0 0 30px ${accentColor}33`,
      }}>
        <div style={{
          width: 36, height: 36, borderRadius: "50%",
          backgroundColor: accentColor,
          display: "flex", alignItems: "center", justifyContent: "center",
          transform: `scale(${bellPulse})`,
          fontSize: "1.1rem",
        }}>
          🎁
        </div>
        <div style={{ color: "white", fontSize: "1rem", fontWeight: 600 }}>
          {ctaText}
        </div>
      </div>
      {/* フォロー・いいね ボタン風 */}
      <div style={{
        display: "flex", gap: 16, marginTop: 24,
        opacity: interpolate(frame, [20, 35], [0, 1], { extrapolateRight: "clamp" }),
      }}>
        {["❤️ いいね", "🔔 フォロー", "🔗 シェア"].map((btn, i) => (
          <div key={i} style={{
            backgroundColor: "rgba(255,255,255,0.1)",
            border: "1px solid rgba(255,255,255,0.2)",
            borderRadius: 999, padding: "8px 20px",
            color: "white", fontSize: "0.9rem",
          }}>
            {btn}
          </div>
        ))}
      </div>
    </div>
  );
};
