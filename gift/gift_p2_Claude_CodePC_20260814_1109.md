# Claude Codeのリファレンス実装でPCを安全に保護できるようになった – 実践テンプレート

## この動画で学んだこと
macOS 用の仮想マシン上で Python 仮想環境を作り、マウス・キーボード操作用ライブラリをインストールすれば、Claude Code のリファレンス実装を安全に実行できることが分かります。

---

## すぐに使えるテンプレート

### 1️⃣ macOS 仮想マシンの作成（UTM を例に）

```bash
# ① UTM を Homebrew でインストール（macOS ホスト側）
brew install --cask utm

# ② UTM を起動し、以下の設定で macOS 仮想マシンを作成
#   - CPU: 4 コア以上
#   - メモリ: 8 GB 以上
#   - ストレージ: 64 GB 以上 (macOS インストーラ ISO をマウント)
#   - ネットワーク: NAT (ポートフォワーディングで 2222→22 を設定)
#   - 共有フォルダ: ホストの ~/ClaudeProject をゲストにマウント
```

> **ポイント**  
> - 仮想マシンはインターネットに直接接続しないよう、NAT とポートフォワーディングだけに留めます。  
> - 共有フォルダを使うと、ホストとゲスト間でコードをシームレスに同期できます。

### 2️⃣ 仮想マシン内での Python 環境構築

```bash
# ③ 仮想マシンに SSH 接続（ホスト側ターミナル）
ssh -p 2222 user@localhost   # 初回はパスワードでログイン

# ④ 必要なツールをインストール
brew install python@3.11   # Homebrew がインストールされていない場合は公式インストーラから

# ⑤ プロジェクトディレクトリを作成し、仮想環境を構築
mkdir -p ~/ClaudeProject
cd ~/ClaudeProject
python3 -m venv .venv

# ⑥ 仮想環境を有効化
source .venv/bin/activate

# ⑦ 必要なライブラリをインストール
pip install --upgrade pip
pip install pyautogui pynput requests tqdm
```

### 3️⃣ Claude Code リファレンス実装（サンプルスクリプト）

```python
# -*- coding: utf-8 -*-
"""
Claude Code リファレンス実装サンプル
- マウスとキーボード操作を自動化し、PC を安全に保護するデモです。
- 必要ライブラリ: pyautogui, pynput, requests
"""

import time
import json
import requests
import pyautogui
from pynput import keyboard

# -------------------------------------------------
# ① Claude API のエンドポイントとトークン（環境変数か .env に保存推奨）
# -------------------------------------------------
CLAUDE_API_URL = "https://api.anthropic.com/v1/complete"
CLAUDE_API_KEY = "YOUR_CLAUDE_API_KEY"   # ← ここに自分の API キーを貼り付け

# -------------------------------------------------
# ② ユーティリティ関数
# -------------------------------------------------
def send_prompt(prompt: str) -> str:
    """Claude にプロンプトを送信し、応答テキストを取得する"""
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    payload = {
        "model": "claude-2.1",
        "max_tokens_to_sample": 1024,
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "temperature": 0.0,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"]
    }
    response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
    return result["completion"].strip()

def safe_click(x: int, y: int, delay: float = 0.2):
    """指定座標を安全にクリック（クリック前に少し待つ）"""
    pyautogui.moveTo(x, y, duration=0.2)
    time.sleep(delay)
    pyautogui.click()
    print(f"Clicked ({x}, {y})")

def type_text(text: str, interval: float = 0.05):
    """文字列をキーボード入力として送信"""
    pyautogui.write(text, interval=interval)
    print(f"Typed: {text}")

# -------------------------------------------------
# ③ メインロジック
# -------------------------------------------------
def main():
    # 例: 「スクリーンショットを撮ってメールで送信したい」指示を Claude に投げる
    user_prompt = "スクリーンショットを撮って、デスクトップの my_screenshot.png に保存し、gmail で自分に送信するスクリプトを書いてください。"
    print("Sending prompt to Claude...")
    claude_response = send_prompt(user_prompt)
    print("Claude の応答:\n", claude_response)

    # 受け取ったコードを一時ファイルに保存して実行
    script_path = "generated_script.py"
    with open(script_path, "w", encoding="