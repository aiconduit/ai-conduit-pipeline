import modal
import os
import subprocess
import base64

app = modal.App("remotion-documentary")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "chromium", "chromium-driver",
        "ffmpeg", "nodejs", "npm",
        "fonts-noto-cjk",  # 日本語フォント
        "git",
    )
    .run_commands(
        "npm install -g @remotion/cli@4.0.523",
    )
)

@app.function(
    cpu=8,
    memory=16384,
    timeout=3600,
    image=image,
    secrets=[modal.Secret.from_name("github-token")],
)
def render_documentary():
    import subprocess, os, base64

    # リポジトリをクローン
    token = os.environ.get("GITHUB_TOKEN", "")
    subprocess.run([
        "git", "clone", f"https://x-access-token:{token}@github.com/aiconduit/ai-conduit-pipeline.git",
        "/tmp/repo"
    ], check=True)

    os.chdir("/tmp/repo/remotion-videos/documentary-30min")

    # 依存関係インストール
    subprocess.run(["npm", "install"], check=True)

    # Remotionレンダリング
    result = subprocess.run([
        "npx", "remotion", "render",
        "src/index.tsx", "DocumentaryTest",
        "/tmp/output.mp4",
        "--codec", "h264",
        "--concurrency", "8",
    ], check=True, capture_output=True, text=True)

    print(result.stdout)

    # 動画を読み込んでbase64で返す
    with open("/tmp/output.mp4", "rb") as f:
        video_bytes = f.read()

    print(f"Video size: {len(video_bytes) / 1024 / 1024:.1f}MB")
    return video_bytes

@app.local_entrypoint()
def main():
    video_bytes = render_documentary.remote()
    with open("documentary_output.mp4", "wb") as f:
        f.write(video_bytes)
    print(f"✅ 保存完了: documentary_output.mp4 ({len(video_bytes)/1024/1024:.1f}MB)")
