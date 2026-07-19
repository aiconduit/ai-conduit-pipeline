import asyncio
import edge_tts

async def main():
    text = "こんにちは。AI Conduitです。今日のGitHubトレンドを紹介します。"
    await edge_tts.Communicate(text, "ja-JP-KeitaNeural").save("/tmp/test.mp3")

asyncio.run(main())
