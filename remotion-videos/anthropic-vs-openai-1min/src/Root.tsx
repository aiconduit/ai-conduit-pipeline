import {Composition} from 'remotion';
import {AnthropicVsOpenAI} from './AnthropicVsOpenAI';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AnthropicVsOpenAI"
        component={AnthropicVsOpenAI}
        durationInFrames={1800}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
