#!/usr/bin/env python3
"""
Kaggle Notebooks APIを使ってRemotionドキュメンタリーをレンダリングする
GPU: T4 x2 (無料)
"""
import os, time, json, requests, base64, zipfile, io

KAGGLE_USERNAME = os.environ["KAGGLE_USERNAME"]
KAGGLE_KEY = os.environ["KAGGLE_KEY"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

AUTH = (KAGGLE_USERNAME, KAGGLE_KEY)
BASE = "https://www.kaggle.com/api/v1"

# Kaggle Notebookのカーネルコード
KERNEL_CODE = f"""
import subprocess, os, base64

GITHUB_TOKEN = "{GITHUB_TOKEN}"

# 依存関係
subprocess.run(["apt-get", "install", "-y", "ffmpeg", "fonts-noto-cjk", "-qq"], check=True)
subprocess.run(["npm", "install", "-g", "@remotion/cli@4.0.523", "--silent"], check=True)

# リポジトリクローン
subprocess.run([
    "git", "clone",
    f"https://x-access-token:{{GITHUB_TOKEN}}@github.com/aiconduit/ai-conduit-pipeline.git",
    "/tmp/repo"
], check=True)

os.chdir("/tmp/repo/remotion-videos/documentary-30min")

# 依存関係
subprocess.run(["npm", "install", "--silent"], check=True)

# ナレーション生成
subprocess.run(["pip", "install", "edge-tts", "-q"], check=True)
subprocess.run(["python3", "scripts/gen_narration.py"], check=True)

# Remotionレンダリング（concurrency 4）
result = subprocess.run([
    "npx", "remotion", "render",
    "src/index.tsx", "DocumentaryTest",
    "/tmp/output.mp4",
    "--codec", "h264",
    "--concurrency", "4",
], capture_output=True, text=True)
print(result.stdout[-1000:])
print(result.stderr[-500:])

# ファイルサイズ確認
result2 = subprocess.run(["ls", "-lh", "/tmp/output.mp4"], capture_output=True, text=True)
print(result2.stdout)

# base64でエンコードして出力
with open("/tmp/output.mp4", "rb") as f:
    data = base64.b64encode(f.read()).decode()
print("OUTPUT_B64_START")
print(data)
print("OUTPUT_B64_END")
"""

def create_kernel():
    payload = {
        "id": f"{KAGGLE_USERNAME}/remotion-documentary-render",
        "title": "Remotion Documentary Render",
        "code": KERNEL_CODE,
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": True,
        "enable_internet": True,
        "dataset_data_sources": [],
        "competition_data_sources": [],
        "kernel_data_sources": [],
    }
    resp = requests.post(f"{BASE}/kernels/push", auth=AUTH, json=payload)
    print(f"Kernel push: {resp.status_code}")
    print(resp.text[:500])
    return resp.json()

def wait_for_kernel(kernel_slug, max_wait=7200):
    print(f"Kernel実行待機中: {kernel_slug}")
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(f"{BASE}/kernels/{kernel_slug}/status", auth=AUTH)
        data = resp.json()
        status = data.get("status", "unknown")
        print(f"  Status: {status} ({int(time.time()-start)}s)")
        if status in ["complete", "error", "cancel"]:
            return status
        time.sleep(30)
    return "timeout"

def get_output(kernel_slug):
    resp = requests.get(f"{BASE}/kernels/{kernel_slug}/output", auth=AUTH, stream=True)
    if resp.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        for name in z.namelist():
            print(f"  Output file: {name}")
            content = z.read(name).decode()
            if "OUTPUT_B64_START" in content:
                start = content.index("OUTPUT_B64_START") + len("OUTPUT_B64_START\n")
                end = content.index("OUTPUT_B64_END")
                b64_data = content[start:end].strip()
                video_bytes = base64.b64decode(b64_data)
                with open("documentary_output.mp4", "wb") as f:
                    f.write(video_bytes)
                print(f"✅ 動画保存: {len(video_bytes)/1024/1024:.1f}MB")
                return True
    print(f"Output取得失敗: {resp.status_code}")
    return False

def main():
    kernel_slug = f"{KAGGLE_USERNAME}/remotion-documentary-render"
    result = create_kernel()
    if "error" in str(result).lower():
        print("❌ Kernel作成失敗")
        return
    status = wait_for_kernel(kernel_slug)
    print(f"最終ステータス: {status}")
    if status == "complete":
        get_output(kernel_slug)
    else:
        print(f"❌ Kernel失敗: {status}")

if __name__ == "__main__":
    main()
