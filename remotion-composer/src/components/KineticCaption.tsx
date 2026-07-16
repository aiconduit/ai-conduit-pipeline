import { useCurrentFrame, useVideoConfig } from "remotion";
import { useJapaneseFont } from "./FontLoader";

interface CaptionBlock {
  start: number;
  end: number;
  text: string;
}

interface KineticCaptionProps {
  captions?: CaptionBlock[];
  fontSize?: number;
  color?: string;
  highlightColor?: string;
}

export const KineticCaption: React.FC<KineticCaptionProps> = ({
  captions = [],
  fontSize = 52,
  color = "#FFFFFF",
  highlightColor = "#22D3EE",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fontFamily = useJapaneseFont();
  
  const currentTimeSec = frame / fps;
  
  const currentCaption = captions.find(
    c => currentTimeSec >= c.start && currentTimeSec < c.end
  );

  if (!currentCaption) return null;

  return (
    <div style={{
      position: "absolute",
      bottom: "12%",
      left: "5%",
      right: "5%",
      textAlign: "center",
      fontFamily,
    }}>
      <div style={{
        display: "inline-block",
        backgroundColor: "rgba(0,0,0,0.75)",
        borderRadius: 8,
        padding: "8px 16px",
        maxWidth: "100%",
      }}>
        <span style={{
          color,
          fontSize: `${fontSize}px`,
          fontWeight: 900,
          lineHeight: 1.4,
          textShadow: "0 2px 8px rgba(0,0,0,0.9)",
          letterSpacing: "0.02em",
        }}>
          {currentCaption.text}
        </span>
      </div>
    </div>
  );
};
