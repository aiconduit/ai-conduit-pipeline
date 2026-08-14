# Claude Codeのリファレンス実装でPCを安全に保護できるようになった – 実践テンプレート

## この動画で学んだこと
macOS 上の仮想マシン内で Python の仮想環境を作り、マウス・キーボード操作用ライブラリをインストールすれば、Claude Code のリファレンス実装を安全に実行できることが分かります。

## すぐに使えるテンプレート

### 1️⃣ macOS 仮想マシンの作成（UTM 例）

```bash
# ① UTM をインストール（Homebrew が入っている前提）
brew install --cask utm

# ② macOS Ventura（または好きなバージョン）の ISO を公式サイトから取得
# 例: https://developer.apple.com/download/all/

# ③ UTM を起動し、以下の設定で新規 VM を作成
#   - CPU: 4 コア
#   - メモリ: 8 GB
#   - ストレージ: 64 GB (QCOW2)
#   - ネットワーク: NAT（ポートフォワーディングで 2222 → 22）
#   - ISO: 取得した macOS インストーラ
#   - 起動 → macOS をインストール
```

> **ポイント**  
> - 仮想マシンの IP アドレスは `ifconfig` で確認し、ホストから `ssh -p 2222 <ユーザー>@localhost` で接続できるようにします。  
> - 以降のコマンドはすべて仮想マシン内で実行してください。

### 2️⃣ Python 仮想環境と必須ライブラリのセットアップ

```bash
# 仮想マシンにログイン（例: ssh -p 2222 user@localhost）
ssh -p 2222 user@localhost

# ① Python3 がインストールされていない場合は Homebrew でインストール
brew install python@3.12   # macOS のデフォルトは 3.11 ですが、最新版を推奨

# ② プロジェクトディレクトリを作成
mkdir -p ~/claude_code_demo && cd ~/claude_code_demo

# ③ 仮想環境を作成
python3 -m venv .venv

# ④ 仮想環境を有効化
source .venv/bin/activate

# ⑤ 必要なライブラリをインストール（requirements.txt から）
cat > requirements.txt <<'EOF'
# マウス・キーボード操作
pynput==1.7.6
pyautogui==0.9.54

# Claude API（公式 SDK がある場合）
anthropic==0.3.0
EOF

pip install -r requirements.txt
```

### 3️⃣ Claude Code リファレンス実装サンプル

> **※ 本サンプルは Claude の API キーが必要です。環境変数 `ANTHROPIC_API_KEY` に設定してください。**

```python
# safe_control.py
"""
Claude Code のリファレンス実装サンプル
- 仮想マシン内で実行することで、ホスト OS への直接的な影響を防止
- マウス・キーボード操作は pynput で実装
- Claude API から取得した指示を安全に実行
"""

import os
import json
import time
from typing import Any, Dict

# Claude API 用 SDK
from anthropic import Anthropic, Completion

# マウス・キーボード操作
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

# -------------------------------------------------
# 1. Claude へプロンプト送信
# -------------------------------------------------
def ask_claude(prompt: str) -> Dict[str, Any]:
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.completions.create(
        model="claude-3-5-sonnet-20241022",   # 例: 最新モデル名
        max_tokens=1024,
        temperature=0.0,
        prompt=prompt,
    )
    # Claude の返答は JSON 形式で返すことを想定
    return json.loads(response.completion)

# -------------------------------------------------
# 2. 受け取った指示を安全に実行
# -------------------------------------------------
def execute_action(action: Dict[str, Any]) -> None:
    """action の種類に応じてマウス・キーボード操作を実行"""
    typ = action.get("type")
    if typ == "move_mouse":
        x, y = action["x"], action["y"]
        mouse = MouseController()
        mouse.position = (x, y)
        print(f"[INFO] Mouse moved to ({x}, {y})")
    elif typ == "click":
        button = action.get("button", "left")
        mouse = MouseController()
        btn = Button.left if button == "left" else Button.right
        mouse.click(btn)
        print(f"[INFO] Mouse {button} click")
    elif typ == "type_text":
        text = action["text"]
        keyboard = KeyboardController()
        for ch in text:
            keyboard.press(ch)
            keyboard.release(ch)
            time.sleep(0.02)  # 人間らしい速度
        print