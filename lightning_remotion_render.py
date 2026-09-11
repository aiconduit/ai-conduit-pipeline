#!/usr/bin/env python3
"""
Lightning AI Sandbox APIを使ってRemotionドキュメンタリーをレンダリングする
lightning-sdk の Sandbox 機能を使用
"""
import os, time, base64

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def main():
    from lightning_sdk.sandbox import Sandbox

    print("✅ lightning-sdk import成功")

    # Sandboxを作成（cpu-8 = 8コア）
    print("Sandbox作成中...")
    sandbox = Sandbox.create(name="remotion-render", instance_type="cpu-8")
    print(f"✅ Sandbox作成: {sandbox}")

    try:
        # 依存関係インストール
        print("Node.js・ffmpeg・Chromiumインストール中...")
        cmds = [
            "apt-get update -qq && apt-get install -y nodejs npm ffmpeg chromium fonts-noto-cjk -qq",
            "npm install -g @remotion/cli@4.0.523 --silent",
        ]
        for cmd in cmds:
            result = sandbox.run_command(cmd)
            print(f"  done: {result.output[-200:] if result.output else 'ok'}")

        # リポジトリをクローン
        print("リポジトリクローン中...")
        result = sandbox.run_command(
            f"git clone https://x-access-token:{GITHUB_TOKEN}@github.com/aiconduit/ai-conduit-pipeline.git /tmp/repo"
        )
        print(f"  clone: {result.output[-100:]}")

        # 依存関係インストール
        result = sandbox.run_command("cd /tmp/repo/remotion-videos/documentary-30min && npm install --silent")
        print(f"  npm install: done")

        # ナレーション生成
        print("ナレーション生成中...")
        result = sandbox.run_command(
            "cd /tmp/repo/remotion-videos/documentary-30min && "
            "pip install edge-tts -q && "
            "python3 scripts/gen_narration.py"
        )
        print(f"  narration: {result.output[-200:]}")

        # Remotionレンダリング
        print("Remotionレンダリング開始...")
        result = sandbox.run_command(
            "cd /tmp/repo/remotion-videos/documentary-30min && "
            "npx remotion render src/index.tsx DocumentaryTest /tmp/output.mp4 "
            "--codec h264 --concurrency 8 2>&1",
            timeout=7200
        )
        print(f"  render output: {result.output[-500:]}")

        # ファイルサイズ確認
        result = sandbox.run_command("ls -lh /tmp/output.mp4 && ffprobe -v quiet -show_entries format=duration -of csv=p=0 /tmp/output.mp4")
        print(f"  output: {result.output}")

        # GitHubにアップロード（artifactとして保存）
        result = sandbox.run_command("base64 /tmp/output.mp4 > /tmp/output_b64.txt && wc -c /tmp/output_b64.txt")
        print(f"  base64 size: {result.output}")

        # ファイルをダウンロード
        result = sandbox.run_command("cat /tmp/output_b64.txt")
        if result.output:
            video_bytes = base64.b64decode(result.output.strip())
            with open("documentary_output.mp4", "wb") as f:
                f.write(video_bytes)
            print(f"✅ 動画保存完了: {len(video_bytes)/1024/1024:.1f}MB")
        else:
            print("❌ ファイル取得失敗")

    finally:
        print("Sandbox削除中...")
        sandbox.delete()
        print("✅ Sandbox削除完了")

if __name__ == "__main__":
    main()
