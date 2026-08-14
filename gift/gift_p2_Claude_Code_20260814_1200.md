# Claude Code の自律エージェントでアプリ構築が自動になった - 実践テンプレート

## この動画で学んだこと
Claude Agent SDK を使えば、Anthropic の API キーさえ設定すれば、数行のコードとコマンドだけで自律エージェントが起動し、アプリの雛形生成やコード補完を自動化できます。

---

## すぐに使えるテンプレート
以下のファイルを **同じディレクトリに保存** して、コピー＆ペーストだけでそのまま実行できます。

### 1️⃣ `.env`  ― API キーを安全に管理
```dotenv
# .env
# Anthropic の API キーをここに貼り付けてください
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2️⃣ `requirements.txt`  ― 必要パッケージ
```text
# requirements.txt
python-dotenv==1.0.1
anthropic==0.3.5          # Claude API ライブラリ
claude-agent-sdk==0.2.0   # 本動画で紹介した自律エージェント SDK
```

### 3️⃣ `agent_demo.py`  ― 最小構成の自律エージェント
```python
# agent_demo.py
"""
Claude Agent SDK デモスクリプト
- .env から API キーを読み込み
- 簡単なプロンプトで自律エージェントを起動
- 生成されたコードを `generated_app/` ディレクトリに出力
"""

import os
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeAgent, AgentConfig, Task

# -------------------------------------------------
# 1. 環境変数のロード
# -------------------------------------------------
load_dotenv()  # .env ファイルを読み込む
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY が .env に設定されていません")

# -------------------------------------------------
# 2. エージェント設定
# -------------------------------------------------
config = AgentConfig(
    api_key=api_key,
    model="claude-3-5-sonnet-20240620",   # 最新モデルを使用
    max_iterations=10,                    # エージェントが最大 10 回ループ
    temperature=0.7,
)

# -------------------------------------------------
# 3. タスク定義
# -------------------------------------------------
task = Task(
    description=(
        "React + FastAPI のシンプルな Todo アプリの雛形を作成してください。\n"
        "以下のファイル構成を生成し、`generated_app/` ディレクトリに保存します。\n"
        "- backend/: FastAPI のエンドポイント\n"
        "- frontend/: React のコンポーネント\n"
        "- README.md: 起動手順"
    ),
    output_dir="generated_app",   # 出力先ディレクトリ
)

# -------------------------------------------------
# 4. エージェント起動
# -------------------------------------------------
def main():
    agent = ClaudeAgent(config)
    print("🚀 自律エージェントを起動します…")
    result = agent.run(task)
    print("\n✅ タスク完了！生成されたファイルは `generated_app/` にあります。")
    # 生成されたコードのサマリを表示（任意）
    print("\n--- 生成されたファイル一覧 ---")
    for path in result.generated_files:
        print(f"- {path}")

if __name__ == "__main__":
    main()
```

### 4️⃣ 起動コマンド  ― 端末で実行するだけ
```bash
# 1. 仮想環境を作成（任意ですが推奨）
python -m venv .venv
source .venv/bin/activate   # Windows の場合は .venv\Scripts\activate

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. エージェントを起動
python agent_demo.py
```

> **ポイント**  
> - `ANTHROPIC_API_KEY` は Anthropic のコンソールから取得した **シークレットキー** を貼り付けてください。  
> - `generated_app/` ディレクトリが自動で作成され、そこにコードが出力されます。  
> - `max_iterations` を増やすと、エージェントがより多くのステップを踏んで改善します（ただしトークン使用量が増えます）。

---

## 使い方
1. **API キーを取得**  
   Anthropic の公式サイトで API キーを作成し、`.env` の `ANTHROPIC_API_KEY` に貼り付けます。

2. **依存パッケージをインストール**  
   上記コマンドの `pip install -r requirements.txt` を実行。

3. **エージェントを起動**  
   `python agent_demo.py` を実行すると、エージェントが自動でコードを生成し `generated_app/` に出力します